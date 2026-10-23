import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const ledgerPath = path.join(root, "data", "scoring-evidence.json");
const ledger = JSON.parse(fs.readFileSync(ledgerPath, "utf8"));
const entries = Array.isArray(ledger.entries) ? ledger.entries : Object.values(ledger.entries || {});
const urls = [...new Set(entries.flatMap((entry) =>
  Object.values(entry.components || {}).flatMap((component) => component?.sources || [])
))].sort();

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
            "user-agent": "KitAgain-v1.16-source-verifier",
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
const failures = results.filter((item) => !item.ok);
console.log(JSON.stringify({
  entries: entries.length,
  unique_sources: urls.length,
  passed: results.length - failures.length,
  failed: failures.length,
  failures,
}, null, 2));

if (failures.length) process.exitCode = 1;
