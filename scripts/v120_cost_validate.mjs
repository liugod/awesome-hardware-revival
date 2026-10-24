import fs from "node:fs";

const path = "data/cost-evidence-v120.json";
const raw = fs.readFileSync(path);
const text = new TextDecoder("utf-8", { fatal: true }).decode(raw);
const data = JSON.parse(text);
const entries = data.entries;

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

assert(raw.subarray(0, 3).toString("hex") !== "efbbbf", "UTF-8 BOM is not allowed");
assert(data.actual_entries === 95 && entries.length === 95, "expected exactly 95 records");
assert(new Set(entries.map((entry) => entry.entry_id)).size === 95, "entry IDs must be unique");
assert(data.filled === entries.filter((entry) => entry.cost_score !== null).length, "filled mismatch");
assert(data.lacking_source === entries.filter((entry) => entry.cost_score === null).length, "lacking_source mismatch");
assert(data.filled + data.lacking_source === 95, "top-level counts must sum to 95");
assert(!text.includes("?".repeat(3)) && !text.includes("\ufffd"), "mojibake marker found");

const required = [
  "entry_id",
  "checked_at",
  "used_price_range",
  "modding_cost_range",
  "used_price_sources",
  "modding_cost_sources",
  "cost_score",
  "null_reason_zh",
  "null_reason_en",
];

for (const entry of entries) {
  for (const key of required) assert(Object.hasOwn(entry, key), `${entry.entry_id}: missing ${key}`);
  assert(entry.checked_at === "2026-10-24", `${entry.entry_id}: wrong checked_at`);
  const bothClasses =
    entry.used_price_range !== null &&
    entry.modding_cost_range !== null &&
    entry.used_price_sources.length > 0 &&
    entry.modding_cost_sources.length > 0;
  assert((entry.cost_score !== null) === bothClasses, `${entry.entry_id}: cost-score evidence gate failed`);
  if (entry.cost_score === null) {
    assert(Boolean(entry.null_reason_zh) && Boolean(entry.null_reason_en), `${entry.entry_id}: missing null reason`);
  } else {
    assert(entry.null_reason_zh === null && entry.null_reason_en === null, `${entry.entry_id}: unexpected null reason`);
  }
  for (const [rangeKey, sourceKey] of [
    ["used_price_range", "used_price_sources"],
    ["modding_cost_range", "modding_cost_sources"],
  ]) {
    const range = entry[rangeKey];
    if (range === null) continue;
    assert(range.low <= range.high, `${entry.entry_id}: invalid ${rangeKey}`);
    if (rangeKey === "modding_cost_range") {
      assert(Array.isArray(range.items), `${entry.entry_id}: modding_cost_range.items must be an array`);
    }
    assert(
      JSON.stringify(range.source_urls) === JSON.stringify(entry[sourceKey]),
      `${entry.entry_id}: ${rangeKey} sources differ from ${sourceKey}`,
    );
  }
}

const urls = [
  ...new Set([
    ...data.methodology.fx_reference.sources,
    ...entries.flatMap((entry) => [
      ...entry.used_price_sources,
      ...entry.modding_cost_sources,
      ...(entry.assessment_sources ?? []),
    ]),
  ]),
];
for (const url of urls) {
  assert(typeof url === "string" && url.startsWith("https://") && !/\s/.test(url), `invalid URL: ${url}`);
}

if (!process.argv.includes("--urls")) {
  console.log(
    JSON.stringify({
      schema: "PASS",
      utf8: "PASS",
      actual_entries: data.actual_entries,
      filled: data.filled,
      lacking_source: data.lacking_source,
      unique_urls: urls.length,
    }),
  );
  process.exit(0);
}

let cursor = 0;
const results = new Array(urls.length);
async function worker() {
  while (true) {
    const index = cursor++;
    if (index >= urls.length) return;
    const url = urls[index];
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), 30_000);
    try {
      const response = await fetch(url, {
        redirect: "follow",
        signal: controller.signal,
        headers: {
          "user-agent": "Mozilla/5.0 (compatible; KitAgainEvidenceBot/1.0; +https://kitagain.com)",
        },
      });
      results[index] = {
        url,
        status: response.status,
        ok: response.status >= 200 && response.status < 400,
        final_url: response.url,
      };
      await response.body?.cancel();
    } catch (error) {
      results[index] = {
        url,
        status: null,
        ok: false,
        error: `${error.name}: ${error.message}`,
      };
    } finally {
      clearTimeout(timeout);
    }
  }
}

await Promise.all(Array.from({ length: 10 }, worker));
const failures = results.filter((result) => !result.ok);
const browserFallback = new Set(data.source_validation?.browser_fallback_urls ?? []);
const fallbackEligibleStatuses = new Set([null, 401, 403, 429, 451]);
const fallbackVerified = failures.filter(
  (result) => browserFallback.has(result.url) && fallbackEligibleStatuses.has(result.status),
);
const unresolved = failures.filter((result) => !fallbackVerified.includes(result));
const uncitedFallbacks = [...browserFallback].filter((url) => !urls.includes(url));
const statusCounts = {};
for (const result of results) {
  const key = String(result.status ?? "ERR");
  statusCounts[key] = (statusCounts[key] ?? 0) + 1;
}
console.log(
  JSON.stringify(
    {
      schema: "PASS",
      utf8: "PASS",
      checked: results.length,
      automated_passed: results.length - failures.length,
      browser_fallback_verified: fallbackVerified.length,
      verified_total: results.length - unresolved.length,
      unresolved: unresolved.length,
      uncited_browser_fallbacks: uncitedFallbacks,
      status_counts: statusCounts,
      automated_failures: failures,
      unresolved_failures: unresolved,
    },
    null,
    2,
  ),
);
if (unresolved.length || uncitedFallbacks.length) process.exitCode = 1;
