import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const directory = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "directory.json"), "utf8"));
const fallbacks = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "thumbnail-fallbacks.json"), "utf8"));
const fallbackById = new Map(fallbacks.entries.map(entry => [entry.entry_id, entry]));
const directoryById = new Map(directory.entries.map(entry => [entry.entry_id, entry]));
const sampleIds = [
  "lead:atlas-enshi-xiaomi-ax1800",
  "lead:atlas-esphome-shelly-1pm",
  "lead:atlas-pmos-clockworkpi-uconsole-raspberry-pi",
  "lead:reuse-sony-reader-with-pico",
  "project:lineageos",
  "project:coreelec",
  "project-lead:brlaser",
  "project-lead:cleanflight",
  "lead:rebble-services",
  "project:wyoming-satellite"
];

for (const entryId of sampleIds) {
  if (!fallbackById.has(entryId) || !directoryById.has(entryId)) throw new Error(`Missing spot-check fixture: ${entryId}`);
}

const browser = await chromium.launch({ headless: true });
try {
  const directoryPage = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await directoryPage.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  await directoryPage.locator("#directory-q").fill("AI");
  await directoryPage.waitForFunction(total => document.querySelectorAll("#directory-grid .project").length === total, directory.counts.listed_entries);

  const detailPage = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const results = [];
  for (const entryId of sampleIds) {
    const record = directoryById.get(entryId);
    const fallback = fallbackById.get(entryId);
    const detailPath = new URL(record.detail_url_zh).pathname;
    await directoryPage.locator("#directory-q").fill(record.title_zh);
    await directoryPage.waitForFunction(title => {
      const target = [...document.querySelectorAll("#directory-grid .project")].find(item => item.dataset.title === title);
      target?.scrollIntoView({ block: "center" });
      return Boolean(target && !target.hidden && target.querySelector("img")?.complete && target.querySelector("img")?.naturalWidth > 0);
    }, record.title_zh);
    const card = await directoryPage.evaluate(title => {
      const target = [...document.querySelectorAll("#directory-grid .project")].find(item => item.dataset.title === title);
      const image = target?.querySelector(":scope > .project-thumb img");
      const media = target?.querySelector(":scope > .project-thumb");
      return {
        found: Boolean(target),
        loaded: Boolean(image?.complete && image.naturalWidth > 0),
        alt: image?.alt || "",
        kind: media?.dataset.imageKind || "",
        marked: Boolean(media?.classList.contains("fallback-image") && media.querySelector(".fallback-badge")),
        placeholders: target?.querySelectorAll(".project-thumb-placeholder").length ?? -1
      };
    }, record.title_zh);

    await detailPage.goto(`${base}${detailPath}`, { waitUntil: "networkidle" });
    const detail = await detailPage.evaluate(() => {
      const media = document.querySelector("main .project-media");
      const image = media?.querySelector("img");
      return {
        loaded: Boolean(image?.complete && image.naturalWidth > 0),
        alt: image?.alt || "",
        kind: media?.dataset.imageKind || "",
        marked: Boolean(media?.classList.contains("fallback-image") && media.querySelector(".fallback-badge")),
        caption: media?.querySelector("figcaption")?.textContent.trim() || "",
        placeholders: document.querySelectorAll(".project-media-placeholder,.project-thumb-placeholder").length
      };
    });
    const pass = card.found && card.loaded && card.marked && card.placeholders === 0 && card.kind === fallback.source_kind &&
      detail.loaded && detail.marked && detail.placeholders === 0 && detail.kind === fallback.source_kind &&
      card.alt === fallback.alt_zh && detail.alt === fallback.alt_zh && detail.caption.includes("备用视觉");
    results.push({ entry_id: entryId, title: record.title_zh, source_kind: fallback.source_kind, detail_path: detailPath, card_loaded: card.loaded, detail_loaded: detail.loaded, marked_as_fallback: card.marked && detail.marked, placeholders: card.placeholders + detail.placeholders, result: pass ? "PASS" : "FAIL" });
  }
  if (results.some(result => result.result !== "PASS")) throw new Error(JSON.stringify(results, null, 2));
  console.log(JSON.stringify({ count: results.length, results }, null, 2));
} finally {
  await browser.close();
}
