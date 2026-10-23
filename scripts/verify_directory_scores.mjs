import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const directory = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "directory.json"), "utf8"));
const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "site.config.json"), "utf8"));
const expected = directory.counts.entries;
const expectedScore4 = directory.entries.filter(entry => entry.score.score >= 4).length;
const browser = await chromium.launch({ headless: true });
const checks = {};

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  checks.cards = await page.locator("#directory-grid .project").count();
  checks.cardsWithScores = await page.locator("#directory-grid .project:has(.rating)").count();
  checks.version = (await page.locator("footer").innerText()).includes(`v${config.version}`);

  await page.locator("#directory-evidence").selectOption("E2");
  checks.e2Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-evidence").selectOption("");
  await page.locator("#directory-score").selectOption("4");
  checks.score4Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.scoreURL = new URL(page.url()).searchParams.get("score");
  await page.locator("#directory-score").selectOption("5");
  checks.score5Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.emptyVisible = await page.locator("#directory-empty:not([hidden])").count();

  await page.locator("#directory-score").selectOption("");
  await page.locator("#directory-kind").selectOption("reviewed-project");
  checks.reviewedVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-kind").selectOption("project-source-lead");
  checks.projectLeadVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-kind").selectOption("");
  await page.locator("#directory-q").fill("Kindle");
  checks.kindleVisible = await page.locator("#directory-grid .project:not([hidden])").count();

  await page.goto(`${base}/zh/projects/xiaogpt/`, { waitUntil: "networkidle" });
  checks.projectRating = (await page.locator(".rating-panel .rating strong").innerText()).trim();
  await page.goto(`${base}/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/`, { waitUntil: "networkidle" });
  checks.leadRating = (await page.locator(".rating-panel .rating strong").innerText()).trim();

  await page.goto(`${base}/zh/project-sources/`, { waitUntil: "networkidle" });
  checks.projectSources = await page.locator("#project-source-grid .project").count();
  await page.locator("#project-source-evidence").selectOption("E0");
  checks.projectSourcesE0 = await page.locator("#project-source-grid .project:not([hidden])").count();
  await page.locator("#project-source-evidence").selectOption("");
  await page.locator("#project-source-q").fill("NAS");
  checks.projectSourcesNas = await page.locator("#project-source-grid .project:not([hidden])").count();
  const firstLeadHref = await page.locator('#project-source-grid .project[data-kind="project-source-lead"]:not([hidden]) h3 a').first().getAttribute("href");
  if (!firstLeadHref) throw new Error("Project-source NAS search produced no E0 detail link");
  await page.goto(new URL(firstLeadHref, page.url()).href, { waitUntil: "networkidle" });
  checks.projectLeadRating = (await page.locator(".rating-panel .rating strong").innerText()).trim();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await mobile.goto(`${base}/zh/directory/?q=Kindle`, { waitUntil: "networkidle" });
  checks.mobileWidth = await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth }));
  checks.mobileVisible = await mobile.locator("#directory-grid .project:not([hidden])").count();
  await mobile.screenshot({ path: path.join(process.cwd(), "research", "validation-v1.14-directory-mobile.png"), fullPage: true });
  await mobile.goto(`${base}/zh/project-sources/?q=NAS`, { waitUntil: "networkidle" });
  checks.projectSourceMobileWidth = await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth }));
  checks.projectSourceMobileVisible = await mobile.locator("#project-source-grid .project:not([hidden])").count();
  await mobile.screenshot({ path: path.join(process.cwd(), "research", "validation-v1.14-project-sources-mobile.png"), fullPage: true });
  await mobile.close();

  if (checks.cards !== expected || checks.cardsWithScores !== expected) throw new Error("Directory or score coverage failed");
  if (!checks.version) throw new Error("Version footer failed");
  if (checks.e2Visible !== 3) throw new Error("E2 filter failed");
  if (checks.score4Visible !== expectedScore4 || checks.scoreURL !== "4") throw new Error("Score filter or URL state failed");
  if (checks.score5Visible !== 0 || checks.emptyVisible !== 1) throw new Error("Evidence-capped empty state failed");
  if (checks.reviewedVisible !== directory.counts.reviewed_projects) throw new Error("Entry-kind filter failed");
  if (checks.projectLeadVisible !== directory.counts.project_source_leads) throw new Error("Project-source kind filter failed");
  if (checks.projectSources !== directory.counts.independent_project_sources || checks.projectSourcesE0 !== directory.counts.project_source_leads || checks.projectSourcesNas < 1) throw new Error("Project-source index/filter failed");
  if (checks.kindleVisible < 1 || checks.mobileVisible !== checks.kindleVisible) throw new Error("Bilingual/device search persistence failed");
  if (checks.mobileWidth.inner !== checks.mobileWidth.scroll) throw new Error("Mobile directory overflow");
  if (checks.projectSourceMobileVisible !== checks.projectSourcesNas || checks.projectSourceMobileWidth.inner !== checks.projectSourceMobileWidth.scroll) throw new Error("Mobile project-source search/overflow failed");
  if (!/^\d\/5$/.test(checks.projectRating) || !/^\d\/5$/.test(checks.leadRating) || checks.projectLeadRating !== "1/5") throw new Error("Detail score panel failed");
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
