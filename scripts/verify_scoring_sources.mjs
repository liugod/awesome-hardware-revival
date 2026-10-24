import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const config = JSON.parse(fs.readFileSync(path.join(root, "site.config.json"), "utf8"));
const readOptional = (name) => {
  const file = path.join(root, "data", name);
  return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, "utf8")) : null;
};
const asEntries = (ledger) => Array.isArray(ledger?.entries) ? ledger.entries : Object.values(ledger?.entries || {});
const scoringLedger = readOptional("scoring-evidence.json");
const batchLedger = readOptional("scoring-evidence-batch2-v120.json");
const costLedger = readOptional("cost-evidence-v120.json");
const auditLedger = readOptional("e0-audit-v120.json");
const guideLedger = readOptional("action-guides-v120.json");
const browserFallbackUrls = new Set([
  ...(costLedger?.source_validation?.browser_fallback_urls || []),
  ...(auditLedger?.source_validation?.browser_fallback_urls || []),
]);
const scoringEntries = asEntries(scoringLedger);
const sources = [];
for (const entry of [...scoringEntries, ...asEntries(batchLedger)]) {
  for (const component of Object.values(entry.components || {})) sources.push(...(component?.sources || []));
}
for (const entry of asEntries(costLedger)) {
  sources.push(...(entry.used_price_sources || entry.used_price?.sources || []));
  sources.push(...(entry.modding_cost_sources || entry.modding_cost?.sources || []));
  sources.push(...(entry.assessment_sources || []));
}
sources.push(...(costLedger?.methodology?.fx_reference?.sources || []));
for (const entry of asEntries(auditLedger)) {
  sources.push(...(entry.sources || entry.audit_sources || []));
  for (const source of entry.evidence_sources || []) sources.push(typeof source === "string" ? source : source.url);
  sources.push(...(entry.tutorial_sources || []));
  for (const key of ["installation", "compatibility", "recovery"]) sources.push(...(entry[key]?.source_urls || []));
  for (const item of Object.values(entry.action_guide || {})) sources.push(...(item?.sources || item?.source_urls || []));
}
for (const entry of asEntries(guideLedger)) {
  for (const key of ["what_you_need", "rough_steps", "when_to_stop"]) sources.push(...(entry[key]?.sources || []));
}
const urls = [...new Set(sources.filter(Boolean))].sort();
if (urls.some((url) => typeof url !== "string" || !url.startsWith("https://"))) {
  throw new Error("Every research source must be an HTTPS URL");
}

const results = [];
let cursor = 0;
const pause = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

async function worker() {
  while (cursor < urls.length) {
    const url = urls[cursor++];
    for (let attempt = 1; attempt <= 3; attempt++) {
      try {
        const response = await fetch(url, {
          redirect: "follow",
          headers: {
            "accept": "text/html,application/xhtml+xml,text/plain,application/json;q=0.9,*/*;q=0.8",
            "user-agent": `KitAgain-v${config.version}-source-verifier`,
          },
          signal: AbortSignal.timeout(30_000),
        });
        await response.body?.cancel();
        if (response.ok || (response.status < 500 && response.status !== 429) || attempt === 3) {
          results.push({ url, status: response.status, ok: response.ok, final_url: response.url, attempts: attempt });
          break;
        }
      } catch (error) {
        if (attempt === 3) {
          results.push({ url, status: null, ok: false, error: String(error?.message || error), attempts: attempt });
          break;
        }
      }
      await pause(250 * attempt);
    }
  }
}

await Promise.all(Array.from({ length: Math.min(6, urls.length || 1) }, worker));
results.sort((a, b) => a.url.localeCompare(b.url));
const automatedPassed = results.filter((item) => item.ok);
const fallbackEligibleStatuses = new Set([null, 401, 403, 429, 451]);
const browserFallbackVerified = results.filter(
  (item) => !item.ok
    && browserFallbackUrls.has(item.url)
    && fallbackEligibleStatuses.has(item.status),
);
const failures = results.filter(
  (item) => !item.ok && !browserFallbackVerified.includes(item),
);
const unusedFallbacks = [...browserFallbackUrls].filter(
  (url) => !urls.includes(url),
);
console.log(JSON.stringify({
  scoring_entries: scoringEntries.length,
  batch2_entries: asEntries(batchLedger).length,
  cost_entries: asEntries(costLedger).length,
  audit_entries: asEntries(auditLedger).length,
  action_guides: asEntries(guideLedger).length,
  unique_sources: urls.length,
  automated_passed: automatedPassed.length,
  browser_fallback_verified: browserFallbackVerified.length,
  verified_total: automatedPassed.length + browserFallbackVerified.length,
  unresolved: failures.length,
  unused_browser_fallbacks: unusedFallbacks,
  unresolved_sources: failures,
}, null, 2));

if (failures.length || unusedFallbacks.length) process.exitCode = 1;
