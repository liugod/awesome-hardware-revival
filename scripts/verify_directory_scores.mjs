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
const ratingDisplayMatches = (text, score, unratedText = "待评分") => score === null ? text === unratedText : scoreTextPattern.test(text);
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

const auditCardGrid = async (targetPage, grid) => targetPage.locator(`${grid} .project`).evaluateAll(cards => {
  const lineCount = element => {
    const style = getComputedStyle(element);
    const lineHeight = Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.2;
    return element.getBoundingClientRect().height / lineHeight;
  };
  const reports = cards.map((card, index) => {
    const children = [...card.children];
    const outcome = card.querySelector(":scope > p.card-outcome");
    const forbidden = card.querySelectorAll("img,.tags,.hardware-tags,.device,.limit,.card-end,.project-thumb,.rating-panel").length;
    const valid = children.length === 3 &&
      children[0].tagName === "H3" && children[0].querySelectorAll("a").length === 1 &&
      children[1].matches("p.card-outcome") && children[2].matches("div.card-meta") &&
      card.querySelectorAll(".card-rating").length === 1 && card.querySelectorAll(".evidence-tag").length === 1 &&
      forbidden === 0;
    return {
      index,
      valid,
      children: children.map(child => `${child.tagName.toLowerCase()}.${child.className}`),
      outcomeLines: outcome ? lineCount(outcome) : Infinity,
      forbidden
    };
  });
  return {
    count: reports.length,
    valid: reports.every(report => report.valid),
    maxOutcomeLines: Math.max(0, ...reports.map(report => report.outcomeLines)),
    failures: reports.filter(report => !report.valid || report.outcomeLines > 1.25).slice(0, 5)
  };
});

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));

  const checkDefaultSort = async ({ pathName, form, sort, score, grid }) => {
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
    await page.locator(sort).selectOption("title-asc");
    await page.locator(`${form} button[type="reset"]`).click();
    const resetScores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
    result.resetSort = await page.locator(sort).inputValue();
    result.resetSortInURL = new URL(page.url()).searchParams.get("sort");
    result.resetDescending = descendingRatedFirst(resetScores);
    return result;
  };

  checks.defaultSort = {
    directoryZh: await checkDefaultSort({ pathName: "/zh/directory/", form: "#directory-filters", sort: "#directory-sort", score: "#directory-score", grid: "#directory-grid" }),
    directoryEn: await checkDefaultSort({ pathName: "/en/directory/", form: "#directory-filters", sort: "#directory-sort", score: "#directory-score", grid: "#directory-grid" }),
    projectSources: await checkDefaultSort({ pathName: "/zh/project-sources/", form: "#project-source-filters", sort: "#project-source-sort", score: "#project-source-score", grid: "#project-source-grid" }),
    leads: await checkDefaultSort({ pathName: "/zh/leads/", form: "#lead-filters", sort: "#lead-sort", score: "#lead-score", grid: "#lead-grid" })
  };

  for (const [name, result] of Object.entries(checks.defaultSort)) {
    if (result.sort !== "score-desc" || result.sortInURL !== null || !result.descending) throw new Error(`${name} default star sorting failed`);
    if (!expectedHalfStars.every(value => result.halfStarOptions.includes(value))) throw new Error(`${name} half-star filter options failed`);
    if (result.resetSort !== "score-desc" || result.resetSortInURL !== null || !result.resetDescending) throw new Error(`${name} reset star sorting failed`);
  }

  const checkHomepage = async ({ pathName, placeholder, directoryPath }) => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    const result = await page.evaluate(expectedPlaceholder => {
      const subtitle = document.querySelector("main .home-subtitle");
      const style = subtitle ? getComputedStyle(subtitle) : null;
      const lineHeight = style ? (Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.2) : 1;
      const categories = [...document.querySelectorAll("main .popular-categories > .category-entry")];
      return {
        h1: document.querySelectorAll("main h1").length,
        searches: document.querySelectorAll('main input[type="search"]').length,
        placeholder: document.querySelector("#home-q")?.getAttribute("placeholder"),
        placeholderMatches: document.querySelector("#home-q")?.getAttribute("placeholder") === expectedPlaceholder,
        subtitleLines: subtitle ? subtitle.getBoundingClientRect().height / lineHeight : Infinity,
        categories: categories.length,
        categoriesValid: categories.every(entry => {
          const url = new URL(entry.href);
          return Boolean(entry.querySelector('[aria-hidden="true"]')) && Boolean(url.searchParams.get("category"));
        }),
        forbidden: document.querySelectorAll("main .field-note,main .facts-strip,main .featured,main .closing,main #filters,main #project-grid,main .primary,main .secondary").length
      };
    }, placeholder);
    result.version = (await page.locator("footer").innerText()).includes(`v${config.version}`);
    await page.locator("#home-q").fill("Kindle");
    await Promise.all([
      page.waitForURL(url => url.pathname === directoryPath && url.searchParams.get("q") === "Kindle"),
      page.locator("#home-q").press("Enter")
    ]);
    result.submittedQuery = await page.locator("#directory-q").inputValue();
    result.destination = new URL(page.url()).pathname;
    return result;
  };

  checks.home = {
    zh: await checkHomepage({ pathName: "/zh/", placeholder: "输入你的设备", directoryPath: "/zh/directory/" }),
    en: await checkHomepage({ pathName: "/", placeholder: "Enter your device", directoryPath: "/en/directory/" })
  };
  for (const [lang, result] of Object.entries(checks.home)) {
    if (result.h1 !== 1 || result.searches !== 1 || !result.placeholderMatches || result.subtitleLines > 1.25 || result.categories < 4 || !result.categoriesValid || result.forbidden !== 0 || !result.version || result.submittedQuery !== "Kindle") {
      throw new Error(`${lang} simplified homepage failed: ${JSON.stringify(result)}`);
    }
  }

  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  checks.cards = await page.locator("#directory-grid .project").count();
  checks.directoryCardContract = await auditCardGrid(page, "#directory-grid");
  checks.ratedCards = await page.locator('#directory-grid .project[data-rated="true"]:has(.card-rating:not(.unrated))').count();
  checks.unratedCards = await page.locator('#directory-grid .project[data-rated="false"]:has(.card-rating.unrated)').count();
  checks.version = (await page.locator("footer").innerText()).includes(`v${config.version}`);
  checks.directoryNeedsReview = await page.locator('#directory-grid .project[data-kind="project-source-lead"] .evidence-tag').count();
  checks.directoryNeedsReviewText = await page.locator('#directory-grid .project[data-kind="project-source-lead"] .evidence-tag').evaluateAll(tags => tags.every(tag => /(待验证|To verify)/.test(tag.textContent)));

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

  const auditRecordDetail = async (pathName, expectedTitle = null) => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    return page.evaluate(title => {
      const paragraphs = [...document.querySelectorAll("main p")].filter(paragraph => getComputedStyle(paragraph).display !== "none");
      const overlong = paragraphs.map(paragraph => {
        const style = getComputedStyle(paragraph);
        const lineHeight = Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.2;
        return { text: paragraph.textContent.trim().slice(0, 80), lines: paragraph.getBoundingClientRect().height / lineHeight };
      }).filter(item => item.lines > 3.15);
      return {
        wrap: Boolean(document.querySelector(".detail-wrap.record-detail")),
        h1: document.querySelectorAll("main h1").length,
        title: document.querySelector("main h1")?.textContent.trim(),
        titleMatches: title === null || document.querySelector("main h1")?.textContent.trim() === title,
        bullets: document.querySelectorAll("main .record-detail ul li").length,
        aboutLinks: document.querySelectorAll("main a.about-link").length,
        aboutHref: document.querySelector("main a.about-link")?.getAttribute("href") || "",
        rating: document.querySelector(".detail-rating strong")?.textContent.trim() || "",
        unrated: document.querySelectorAll(".detail-rating.unrated").length,
        legacyPanels: document.querySelectorAll(".rating-panel,.detail-rating dl").length,
        overlong
      };
    }, expectedTitle);
  };

  checks.projectDetail = await auditRecordDetail("/zh/projects/dietpi/", "DietPi");
  checks.leadDetail = await auditRecordDetail("/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/");

  await page.goto(`${base}/zh/project-sources/`, { waitUntil: "networkidle" });
  checks.projectSources = await page.locator("#project-source-grid .project").count();
  checks.projectSourceCardContract = await auditCardGrid(page, "#project-source-grid");
  checks.projectSourceNeedsReview = await page.locator('#project-source-grid .project[data-kind="project-source-lead"] .evidence-tag').count();
  checks.projectSourceNeedsReviewText = await page.locator('#project-source-grid .project[data-kind="project-source-lead"] .evidence-tag').evaluateAll(tags => tags.every(tag => /(待验证|To verify)/.test(tag.textContent)));
  const firstLeadHref = await page.locator('#project-source-grid .project[data-kind="project-source-lead"] h3 a').first().getAttribute("href");
  if (!firstLeadHref) throw new Error("Project-source index produced no E0 detail link");
  await page.locator("#project-source-evidence").selectOption("E0");
  checks.projectSourcesE0 = await page.locator("#project-source-grid .project:not([hidden])").count();
  await page.locator("#project-source-evidence").selectOption("");
  await page.locator("#project-source-q").fill("NAS");
  checks.projectSourcesNas = await page.locator("#project-source-grid .project:not([hidden])").count();
  checks.projectLeadDetail = await auditRecordDetail(new URL(firstLeadHref, page.url()).pathname);
  checks.projectLeadNeedsReview = await page.locator("main .needs-review").count();

  await page.goto(`${base}/zh/leads/`, { waitUntil: "networkidle" });
  checks.leadCardContract = await auditCardGrid(page, "#lead-grid");

  const unratedEntry = directory.entries.find(entry => entry.score.score === null);
  if (!unratedEntry) throw new Error("Expected at least one not-yet-rated entry");
  checks.englishUnratedDetail = await auditRecordDetail(new URL(unratedEntry.detail_url_en).pathname);
  checks.englishProjectDetail = await auditRecordDetail("/en/projects/dietpi/", "DietPi");

  const auditAbout = async pathName => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    return page.evaluate(() => {
      const text = document.querySelector("main")?.innerText || "";
      return {
        h1: document.querySelectorAll("main h1").length,
        anchors: ["evidence", "scoring", "contribute"].filter(id => document.getElementById(id)).length,
        weightRows: document.querySelectorAll("table.scoring-weights tbody tr").length,
        evidenceRange: text.includes("E0") && text.includes("E3"),
        halfStar: text.includes("0.5"),
        nullable: text.includes("null"),
        contribution: document.querySelectorAll('main a[href*="issues/new/choose"]').length
      };
    });
  };
  checks.about = {
    zh: await auditAbout("/zh/about/"),
    en: await auditAbout("/en/about/")
  };

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on("console", message => { if (message.type() === "error") errors.push(`mobile: ${message.text()}`); });
  mobile.on("pageerror", error => errors.push(`mobile: ${error.message}`));
  const mobileMeasure = async (pathName, grid = null) => {
    await mobile.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    return {
      width: await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth })),
      visible: grid ? await mobile.locator(`${grid} .project:not([hidden])`).count() : null,
      subtitleLines: await mobile.locator(".home-subtitle").count() ? await mobile.locator(".home-subtitle").evaluate(element => {
        const style = getComputedStyle(element);
        const lineHeight = Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.2;
        return element.getBoundingClientRect().height / lineHeight;
      }) : null,
      overlongParagraphs: await mobile.locator(".record-detail").count() ? await mobile.locator("main p").evaluateAll(paragraphs => paragraphs.filter(paragraph => {
        const style = getComputedStyle(paragraph);
        const lineHeight = Number.parseFloat(style.lineHeight) || Number.parseFloat(style.fontSize) * 1.2;
        return paragraph.getBoundingClientRect().height / lineHeight > 3.15;
      }).map(paragraph => paragraph.textContent.trim().slice(0, 80))) : []
    };
  };
  checks.mobile = {
    homeEn: await mobileMeasure("/"),
    homeZh: await mobileMeasure("/zh/"),
    directory: await mobileMeasure("/zh/directory/?q=Kindle", "#directory-grid"),
    projectSources: await mobileMeasure("/zh/project-sources/?q=NAS", "#project-source-grid"),
    leads: await mobileMeasure("/zh/leads/", "#lead-grid"),
    detailZh: await mobileMeasure("/zh/projects/dietpi/"),
    detailEn: await mobileMeasure("/en/projects/dietpi/"),
    aboutZh: await mobileMeasure("/zh/about/"),
    aboutEn: await mobileMeasure("/en/about/")
  };
  await mobile.goto(`${base}/zh/directory/?q=Kindle`, { waitUntil: "networkidle" });
  checks.mobileDirectoryCardContract = await auditCardGrid(mobile, "#directory-grid");
  await mobile.screenshot({ path: path.join(process.cwd(), "research", `validation-v${config.version}-directory-mobile.png`), fullPage: true });
  await mobile.goto(`${base}/zh/project-sources/?q=NAS`, { waitUntil: "networkidle" });
  await mobile.screenshot({ path: path.join(process.cwd(), "research", `validation-v${config.version}-project-sources-mobile.png`), fullPage: true });
  await mobile.close();

  if (checks.cards !== expected || checks.ratedCards !== expectedRated || checks.unratedCards !== expectedUnrated) throw new Error("Directory rated/unrated coverage failed");
  for (const [name, result] of Object.entries({ directory: checks.directoryCardContract, projectSources: checks.projectSourceCardContract, leads: checks.leadCardContract, mobileDirectory: checks.mobileDirectoryCardContract })) {
    if (!result.valid || result.maxOutcomeLines > 1.25) throw new Error(`${name} four-field card contract failed: ${JSON.stringify(result.failures)}`);
  }
  if (!checks.version) throw new Error("Version footer failed");
  if (checks.e2Visible !== expectedE2) throw new Error("E2 filter failed");
  if (checks.combinedE0ScoreVisible !== expectedE0AtThreshold || !checks.combinedE0ScoreValid) throw new Error("Independent evidence and star filters failed");
  if (checks.score4Visible !== expectedScore4 || checks.scoreURL !== "4" || checks.score5Visible !== expectedScore5) throw new Error("Star filter or URL state failed");
  if (checks.reviewedVisible !== directory.counts.reviewed_projects) throw new Error("Entry-kind filter failed");
  if (checks.projectLeadVisible !== directory.counts.project_source_leads) throw new Error("Project-source kind filter failed");
  if (checks.directoryNeedsReview !== directory.counts.project_source_leads || !checks.directoryNeedsReviewText || checks.projectSourceNeedsReview !== directory.counts.project_source_leads || !checks.projectSourceNeedsReviewText || checks.projectLeadNeedsReview !== 1) throw new Error("Needs-review marker coverage failed");
  if (checks.projectSources !== directory.counts.independent_project_sources || checks.projectSourcesE0 !== directory.counts.project_source_leads || checks.projectSourcesNas < 1) throw new Error("Project-source index/filter failed");
  if (checks.kindleVisible < 1 || checks.mobile.directory.visible !== checks.kindleVisible) throw new Error("Bilingual/device search persistence failed");
  if (checks.mobile.projectSources.visible !== checks.projectSourcesNas) throw new Error("Project-source mobile search persistence failed");
  if (checks.mobile.leads.visible !== directory.counts.device_or_community_routes) throw new Error("Mobile lead list coverage failed");
  for (const [name, result] of Object.entries(checks.mobile)) {
    if (result.width.scroll > result.width.inner) throw new Error(`Mobile ${name} overflow`);
    if (result.subtitleLines !== null && result.subtitleLines > 1.25) throw new Error(`Mobile ${name} subtitle exceeds one line`);
    if (result.overlongParagraphs.length) throw new Error(`Mobile ${name} detail paragraph exceeds three lines: ${result.overlongParagraphs[0]}`);
  }

  const projectEntry = directory.entries.find(entry => entry.entry_id === "project:dietpi");
  const leadEntry = directory.entries.find(entry => entry.entry_id === "lead:atlas-x-gl-ar300m16-ext-wifi-pineapple");
  const projectLeadId = firstLeadHref.split("/").filter(Boolean).at(-1);
  const projectLeadEntry = directory.entries.find(entry => entry.entry_id === `project-lead:${projectLeadId}`);
  if (!projectEntry || !leadEntry || !projectLeadEntry) throw new Error("Detail score fixtures missing from directory export");
  const detailResults = [checks.projectDetail, checks.leadDetail, checks.projectLeadDetail, checks.englishUnratedDetail, checks.englishProjectDetail];
  for (const result of detailResults) {
    if (!result.wrap || result.h1 !== 1 || !result.titleMatches || result.bullets < 1 || result.aboutLinks !== 1 || result.legacyPanels !== 0 || result.overlong.length) {
      throw new Error(`Simplified detail contract failed: ${JSON.stringify(result)}`);
    }
  }
  if (!ratingDisplayMatches(checks.projectDetail.rating, projectEntry.score.score) || checks.projectDetail.unrated !== Number(projectEntry.score.score === null)) throw new Error("Reviewed-project detail rating failed");
  if (!ratingDisplayMatches(checks.leadDetail.rating, leadEntry.score.score) || checks.leadDetail.unrated !== Number(leadEntry.score.score === null)) throw new Error("Device-route detail rating failed");
  if (!ratingDisplayMatches(checks.projectLeadDetail.rating, projectLeadEntry.score.score) || checks.projectLeadDetail.unrated !== Number(projectLeadEntry.score.score === null)) throw new Error("Project-lead detail rating failed");
  if (!ratingDisplayMatches(checks.englishUnratedDetail.rating, unratedEntry.score.score, "Not yet rated")) throw new Error("English not-yet-rated marker failed");
  for (const [lang, result] of Object.entries(checks.about)) {
    if (result.h1 !== 1 || result.anchors !== 3 || result.weightRows !== 5 || !result.evidenceRange || !result.halfStar || !result.nullable || result.contribution < 1) {
      throw new Error(`${lang} About content failed: ${JSON.stringify(result)}`);
    }
  }
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
