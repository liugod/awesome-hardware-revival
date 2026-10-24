import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const directory = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "directory.json"), "utf8"));
const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "site.config.json"), "utf8"));
const expected = directory.counts.entries;
const expectedScore4 = directory.entries.filter(entry => entry.score.score !== null && entry.score.score >= 4).length;
const expectedScore5 = directory.entries.filter(entry => entry.score.score !== null && entry.score.score >= 5).length;
const expectedRated = directory.counts.rated;
const expectedUnrated = directory.counts.not_yet_rated;
const expectedE2 = directory.counts.evidence_distribution.E2 || 0;
const expectedHalfStars = ["1.5", "2.5", "3.5", "4.5"];
const combinedThreshold = 1.5;
const expectedE0AtThreshold = directory.entries.filter(entry => entry.evidence_level === "E0" && entry.score.score !== null && entry.score.score >= combinedThreshold).length;
const scoreTextPattern = /[1-5](?:\.5)?\s*\/\s*5/;
const ratingDisplayMatches = (text, score) => score === null ? text === "待评分" : scoreTextPattern.test(text);
const browser = await chromium.launch({ headless: true });
const checks = {};

const descendingRatedFirst = scores => {
  let foundUnrated = false;
  let previous = Infinity;
  for (const score of scores) {
    if (score === null) {
      foundUnrated = true;
      continue;
    }
    if (foundUnrated || score > previous) return false;
    previous = score;
  }
  return true;
};

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));

  const checkDefaultSort = async ({ pathName, form, sort, score, grid, reset = false }) => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    const scores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
    const result = {
      sort: await page.locator(sort).inputValue(),
      sortInURL: new URL(page.url()).searchParams.get("sort"),
      descending: descendingRatedFirst(scores),
      count: scores.length,
      firstScores: scores.slice(0, 8),
      halfStarOptions: await page.locator(`${score} option`).evaluateAll(options => options.map(option => option.value).filter(value => value.endsWith(".5")))
    };
    if (reset) {
      await page.locator(sort).selectOption("title-asc");
      await page.locator(`${form} button[type="reset"]`).click();
      const resetScores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
      result.resetSort = await page.locator(sort).inputValue();
      result.resetSortInURL = new URL(page.url()).searchParams.get("sort");
      result.resetDescending = descendingRatedFirst(resetScores);
    }
    return result;
  };

  checks.defaultSort = {
    home: await checkDefaultSort({ pathName: "/", form: "#filters", sort: "#sort", score: "#score", grid: "#project-grid", reset: true }),
    directory: await checkDefaultSort({ pathName: "/zh/directory/", form: "#directory-filters", sort: "#directory-sort", score: "#directory-score", grid: "#directory-grid" }),
    projectSources: await checkDefaultSort({ pathName: "/zh/project-sources/", form: "#project-source-filters", sort: "#project-source-sort", score: "#project-source-score", grid: "#project-source-grid" }),
    leads: await checkDefaultSort({ pathName: "/zh/leads/", form: "#lead-filters", sort: "#lead-sort", score: "#lead-score", grid: "#lead-grid", reset: true })
  };

  for (const [name, result] of Object.entries(checks.defaultSort)) {
    if (result.sort !== "score-desc" || result.sortInURL !== null || !result.descending) throw new Error(`${name} default star sorting failed`);
    if (!expectedHalfStars.every(value => result.halfStarOptions.includes(value))) throw new Error(`${name} half-star filter options failed`);
    if ("resetSort" in result && (result.resetSort !== "score-desc" || result.resetSortInURL !== null || !result.resetDescending)) throw new Error(`${name} reset star sorting failed`);
  }

  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  checks.cards = await page.locator("#directory-grid .project").count();
  checks.ratedCards = await page.locator('#directory-grid .project[data-rated="true"]:has(.rating:not(.unrated))').count();
  checks.unratedCards = await page.locator('#directory-grid .project[data-rated="false"]:has(.rating.unrated)').count();
  checks.version = (await page.locator("footer").innerText()).includes(`v${config.version}`);
  checks.directoryNeedsReview = await page.locator('#directory-grid .project[data-kind="project-source-lead"] .needs-review').count();

  await page.locator("#directory-evidence").selectOption("E2");
  checks.e2Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-evidence").selectOption("E0");
  await page.locator("#directory-score").selectOption(String(combinedThreshold));
  checks.combinedE0ScoreVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.combinedE0ScoreValid = await page.locator("#directory-grid .project:not([hidden])").evaluateAll((cards, threshold) => cards.every(card => card.dataset.evidence === "E0" && card.dataset.score !== "" && Number(card.dataset.score) >= threshold), combinedThreshold);

  await page.locator("#directory-evidence").selectOption("");
  await page.locator("#directory-score").selectOption("4");
  checks.score4Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.scoreURL = new URL(page.url()).searchParams.get("score");
  await page.locator("#directory-score").selectOption("5");
  checks.score5Visible = await page.locator("#directory-grid .project:not([hidden])").count();

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
  checks.projectRatingComponents = await page.locator(".rating-panel dl > div").count();
  checks.projectRatingUnrated = await page.locator(".rating-panel .rating.unrated").count();
  await page.goto(`${base}/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/`, { waitUntil: "networkidle" });
  checks.leadRating = (await page.locator(".rating-panel .rating strong").innerText()).trim();
  checks.leadRatingComponents = await page.locator(".rating-panel dl > div").count();
  checks.leadRatingUnrated = await page.locator(".rating-panel .rating.unrated").count();

  await page.goto(`${base}/zh/project-sources/`, { waitUntil: "networkidle" });
  checks.projectSources = await page.locator("#project-source-grid .project").count();
  checks.projectSourceNeedsReview = await page.locator('#project-source-grid .project[data-kind="project-source-lead"] .needs-review').count();
  const firstLeadHref = await page.locator('#project-source-grid .project[data-kind="project-source-lead"] h3 a').first().getAttribute("href");
  if (!firstLeadHref) throw new Error("Project-source index produced no E0 detail link");
  await page.locator("#project-source-evidence").selectOption("E0");
  checks.projectSourcesE0 = await page.locator("#project-source-grid .project:not([hidden])").count();
  await page.locator("#project-source-evidence").selectOption("");
  await page.locator("#project-source-q").fill("NAS");
  checks.projectSourcesNas = await page.locator("#project-source-grid .project:not([hidden])").count();
  await page.goto(new URL(firstLeadHref, page.url()).href, { waitUntil: "networkidle" });
  checks.projectLeadRating = (await page.locator(".rating-panel .rating strong").innerText()).trim();
  checks.projectLeadRatingComponents = await page.locator(".rating-panel dl > div").count();
  checks.projectLeadRatingUnrated = await page.locator(".rating-panel .rating.unrated").count();
  checks.projectLeadNeedsReview = await page.locator(".needs-review").count();
  const unratedEntry = directory.entries.find(entry => entry.score.score === null);
  if (!unratedEntry) throw new Error("Expected at least one not-yet-rated entry");
  await page.goto(`${base}${new URL(unratedEntry.detail_url_en).pathname}`, { waitUntil: "networkidle" });
  checks.englishUnratedMarker = (await page.locator(".rating-panel .rating.unrated strong").innerText()).trim();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  const mobileMeasure = async (pathName, grid) => {
    await mobile.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    return {
      width: await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth })),
      visible: await mobile.locator(`${grid} .project:not([hidden])`).count()
    };
  };
  checks.mobile = {
    home: await mobileMeasure("/", "#project-grid"),
    directory: await mobileMeasure("/zh/directory/?q=Kindle", "#directory-grid"),
    projectSources: await mobileMeasure("/zh/project-sources/?q=NAS", "#project-source-grid"),
    leads: await mobileMeasure("/zh/leads/", "#lead-grid")
  };
  await mobile.goto(`${base}/zh/directory/?q=Kindle`, { waitUntil: "networkidle" });
  await mobile.screenshot({ path: path.join(process.cwd(), "research", "validation-v1.16-directory-mobile.png"), fullPage: true });
  await mobile.goto(`${base}/zh/project-sources/?q=NAS`, { waitUntil: "networkidle" });
  await mobile.screenshot({ path: path.join(process.cwd(), "research", "validation-v1.16-project-sources-mobile.png"), fullPage: true });
  await mobile.close();

  if (checks.cards !== expected || checks.ratedCards !== expectedRated || checks.unratedCards !== expectedUnrated) throw new Error("Directory rated/unrated coverage failed");
  if (!checks.version) throw new Error("Version footer failed");
  if (checks.e2Visible !== expectedE2) throw new Error("E2 filter failed");
  if (checks.combinedE0ScoreVisible !== expectedE0AtThreshold || !checks.combinedE0ScoreValid) throw new Error("Independent evidence and star filters failed");
  if (checks.score4Visible !== expectedScore4 || checks.scoreURL !== "4" || checks.score5Visible !== expectedScore5) throw new Error("Star filter or URL state failed");
  if (checks.reviewedVisible !== directory.counts.reviewed_projects) throw new Error("Entry-kind filter failed");
  if (checks.projectLeadVisible !== directory.counts.project_source_leads) throw new Error("Project-source kind filter failed");
  if (checks.directoryNeedsReview !== directory.counts.project_source_leads || checks.projectSourceNeedsReview !== directory.counts.project_source_leads || checks.projectLeadNeedsReview !== 1) throw new Error("Needs-review marker coverage failed");
  if (checks.projectSources !== directory.counts.independent_project_sources || checks.projectSourcesE0 !== directory.counts.project_source_leads || checks.projectSourcesNas < 1) throw new Error("Project-source index/filter failed");
  if (checks.kindleVisible < 1 || checks.mobile.directory.visible !== checks.kindleVisible) throw new Error("Bilingual/device search persistence failed");
  if (checks.mobile.projectSources.visible !== checks.projectSourcesNas) throw new Error("Project-source mobile search persistence failed");
  if (checks.mobile.home.visible !== directory.counts.reviewed_projects || checks.mobile.leads.visible !== directory.counts.device_or_community_routes) throw new Error("Mobile list coverage failed");
  for (const [name, result] of Object.entries(checks.mobile)) {
    if (result.width.inner !== result.width.scroll) throw new Error(`Mobile ${name} overflow`);
  }
  const projectEntry = directory.entries.find(entry => entry.entry_id === "project:xiaogpt");
  const leadEntry = directory.entries.find(entry => entry.entry_id === "lead:atlas-x-gl-ar300m16-ext-wifi-pineapple");
  const projectLeadId = firstLeadHref.split("/").filter(Boolean).at(-1);
  const projectLeadEntry = directory.entries.find(entry => entry.entry_id === `project-lead:${projectLeadId}`);
  if (!projectEntry || !leadEntry || !projectLeadEntry) throw new Error("Detail score fixtures missing from directory export");
  if (!ratingDisplayMatches(checks.projectRating, projectEntry.score.score) || checks.projectRatingUnrated !== Number(projectEntry.score.score === null)) throw new Error("Reviewed-project detail rating failed");
  if (!ratingDisplayMatches(checks.leadRating, leadEntry.score.score) || checks.leadRatingUnrated !== Number(leadEntry.score.score === null)) throw new Error("Device-route detail rating failed");
  if (!ratingDisplayMatches(checks.projectLeadRating, projectLeadEntry.score.score) || checks.projectLeadRatingUnrated !== Number(projectLeadEntry.score.score === null)) throw new Error("Project-lead detail rating failed");
  if (checks.englishUnratedMarker !== "Not yet rated") throw new Error("English not-yet-rated marker failed");
  if (![checks.projectRatingComponents, checks.leadRatingComponents, checks.projectLeadRatingComponents].every(value => value === 5)) throw new Error("Five-dimension detail panel failed");
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
