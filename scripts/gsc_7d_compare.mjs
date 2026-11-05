import fs from "node:fs";
import https from "node:https";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const SITE_URL = "sc-domain:kitagain.com";
const DEFAULT_CREDENTIAL_FILE = "C:\\work\\.secrets\\gsc-oauth-client.json";
const ROW_LIMIT = Number(process.env.GSC_ROW_LIMIT || 25000);
const DATE_LAG_DAYS = Number(process.env.GSC_DATE_LAG_DAYS || 2);
const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const OUTPUT_DIR = path.resolve(process.env.GSC_OUTPUT_DIR || path.join(ROOT, "research", "gsc", "snapshots"));

function isoDate(date) {
  return date.toISOString().slice(0, 10);
}

function addUtcDays(value, days) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) throw new Error(`Invalid ISO date: ${value}`);
  const date = new Date(`${value}T00:00:00Z`);
  if (Number.isNaN(date.valueOf()) || isoDate(date) !== value) throw new Error(`Invalid ISO date: ${value}`);
  date.setUTCDate(date.getUTCDate() + days);
  return isoDate(date);
}

function defaultEndDate() {
  const date = new Date();
  date.setUTCDate(date.getUTCDate() - DATE_LAG_DAYS);
  return isoDate(date);
}

function readCredentials() {
  const credentialFile = process.env.GSC_OAUTH_CLIENT_FILE || DEFAULT_CREDENTIAL_FILE;
  if (!fs.existsSync(credentialFile)) {
    throw new Error(`Existing OAuth file not found: ${credentialFile}. Set GSC_OAUTH_CLIENT_FILE to the already-authorized local file; do not create new OAuth for this flow.`);
  }
  const credentials = JSON.parse(fs.readFileSync(credentialFile, "utf8").replace(/^\uFEFF/, ""));
  for (const key of ["client_id", "client_secret", "refresh_token"]) {
    if (!credentials[key]) throw new Error(`Existing OAuth file is missing ${key}.`);
  }
  return credentials;
}

function request(url, options = {}) {
  return new Promise((resolve, reject) => {
    const body = options.body || "";
    const req = https.request(url, {
      method: options.method || "GET",
      headers: {
        ...(options.headers || {}),
        ...(body ? { "content-length": Buffer.byteLength(body) } : {}),
      },
    }, (res) => {
      let data = "";
      res.on("data", (chunk) => { data += chunk; });
      res.on("end", () => {
        let parsed = data;
        try { parsed = data ? JSON.parse(data) : {}; } catch {}
        if ((res.statusCode || 500) >= 400) {
          const error = new Error(`HTTP ${res.statusCode} from ${url}`);
          error.response = parsed;
          reject(error);
          return;
        }
        resolve(parsed);
      });
    });
    req.on("error", reject);
    if (body) req.write(body);
    req.end();
  });
}

async function accessToken(credentials) {
  const body = new URLSearchParams({
    client_id: credentials.client_id,
    client_secret: credentials.client_secret,
    refresh_token: credentials.refresh_token,
    grant_type: "refresh_token",
  }).toString();
  const token = await request("https://oauth2.googleapis.com/token", {
    method: "POST",
    headers: { "content-type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!token.access_token) throw new Error("Google OAuth refresh returned no access token.");
  return token.access_token;
}

function authHeaders(token) {
  return { authorization: `Bearer ${token}`, "content-type": "application/json" };
}

async function verifyProperty(token) {
  const sites = await request("https://www.googleapis.com/webmasters/v3/sites", {
    headers: authHeaders(token),
  });
  const matches = (sites.siteEntry || []).filter((site) => site.siteUrl === SITE_URL);
  if (matches.length !== 1) {
    throw new Error(`Required property ${SITE_URL} was not returned exactly once by sites.list.`);
  }
  return matches[0].permissionLevel || "unknown";
}

async function searchAnalytics(token, period, dimensions) {
  const site = encodeURIComponent(SITE_URL);
  const rows = [];
  let metadata = {};
  let pageCount = 0;
  while (true) {
    const response = await request(`https://www.googleapis.com/webmasters/v3/sites/${site}/searchAnalytics/query`, {
      method: "POST",
      headers: authHeaders(token),
      body: JSON.stringify({
        startDate: period.startDate,
        endDate: period.endDate,
        dimensions,
        rowLimit: ROW_LIMIT,
        startRow: rows.length,
      }),
    });
    pageCount += 1;
    if (pageCount === 1) metadata = Object.fromEntries(Object.entries(response).filter(([key]) => key !== "rows"));
    const pageRows = response.rows || [];
    rows.push(...pageRows);
    if (pageRows.length < ROW_LIMIT) break;
  }
  return { ...metadata, rows, fetch: { pageCount, rowCount: rows.length } };
}

function totals(rows = []) {
  const aggregate = rows.reduce((result, row) => {
    result.clicks += row.clicks || 0;
    result.impressions += row.impressions || 0;
    result.positionWeight += (row.position || 0) * (row.impressions || 0);
    return result;
  }, { clicks: 0, impressions: 0, positionWeight: 0 });
  return {
    clicks: aggregate.clicks,
    impressions: aggregate.impressions,
    ctr: aggregate.impressions ? aggregate.clicks / aggregate.impressions : 0,
    position: aggregate.impressions ? aggregate.positionWeight / aggregate.impressions : null,
  };
}

function delta(current, previous) {
  const absolute = current - previous;
  return {
    absolute,
    percent: previous === 0 ? null : absolute / previous,
  };
}

async function periodReport(token, period) {
  const [byQuery, byPage, byQueryPage, byDate] = await Promise.all([
    searchAnalytics(token, period, ["query"]),
    searchAnalytics(token, period, ["page"]),
    searchAnalytics(token, period, ["query", "page"]),
    searchAnalytics(token, period, ["date"]),
  ]);
  return { byQuery, byPage, byQueryPage, byDate };
}

async function main() {
  if (!Number.isInteger(DATE_LAG_DAYS) || DATE_LAG_DAYS < 0) throw new Error("GSC_DATE_LAG_DAYS must be a non-negative integer.");
  if (!Number.isInteger(ROW_LIMIT) || ROW_LIMIT < 1 || ROW_LIMIT > 25000) throw new Error("GSC_ROW_LIMIT must be between 1 and 25000.");
  const currentEnd = process.env.GSC_END_DATE || defaultEndDate();
  const current = { startDate: addUtcDays(currentEnd, -6), endDate: currentEnd };
  const previous = { startDate: addUtcDays(currentEnd, -13), endDate: addUtcDays(currentEnd, -7) };
  const credentials = readCredentials();
  const token = await accessToken(credentials);

  // Property discovery is a required gate: do not assume an OAuth account can read KitAgain.
  const permissionLevel = await verifyProperty(token);
  const [currentReports, previousReports] = await Promise.all([
    periodReport(token, current),
    periodReport(token, previous),
  ]);
  const currentTotals = totals(currentReports.byDate.rows);
  const previousTotals = totals(previousReports.byDate.rows);
  const comparison = {
    clicks: delta(currentTotals.clicks, previousTotals.clicks),
    impressions: delta(currentTotals.impressions, previousTotals.impressions),
    ctr: delta(currentTotals.ctr, previousTotals.ctr),
    position: currentTotals.position === null || previousTotals.position === null
      ? { absolute: null, percent: null }
      : delta(currentTotals.position, previousTotals.position),
  };

  const output = {
    schemaVersion: 1,
    generatedAt: new Date().toISOString(),
    siteUrl: SITE_URL,
    propertyPermission: permissionLevel,
    dateLagDays: DATE_LAG_DAYS,
    rowLimit: ROW_LIMIT,
    periods: { current, previous },
    metrics: { current: currentTotals, previous: previousTotals },
    comparison,
    reports: { current: currentReports, previous: previousReports },
    notes: [
      "Each date range is inclusive and contains seven UTC dates.",
      "The current window ends two days before the run by default to accommodate normal Search Console reporting lag.",
      "Query rows may omit anonymized searches; headline totals are derived from the date dimension.",
      "OAuth credentials and access tokens are read locally and are never written to this snapshot.",
    ],
  };

  fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  const outputPath = path.join(OUTPUT_DIR, `${current.endDate}-gsc-7d-vs-prev-7d.json`);
  fs.writeFileSync(outputPath, `${JSON.stringify(output, null, 2)}\n`, "utf8");
  console.log(JSON.stringify({
    siteUrl: SITE_URL,
    outputPath,
    periods: output.periods,
    metrics: output.metrics,
    comparison: output.comparison,
  }, null, 2));
}

main().catch((error) => {
  console.error("KitAgain GSC 7+7 refresh failed.");
  console.error(error.response || error.message);
  process.exit(1);
});
