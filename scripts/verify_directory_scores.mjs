import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const directory = JSON.parse(fs.readFileSync(path.join(process.cwd(), "data", "directory.json"), "utf8"));
const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "site.config.json"), "utf8"));
const listedEntries = directory.entries.filter(entry => entry.display_status !== "delisted");
const expected = listedEntries.length;
const expectedScore4 = listedEntries.filter(entry => entry.score.score !== null && entry.score.score >= 4).length;
const expectedScore5 = listedEntries.filter(entry => entry.score.score !== null && entry.score.score >= 5).length;
const expectedNetwork = listedEntries.filter(entry => entry.category === "network").length;
const expectedRated = listedEntries.filter(entry => entry.score.score !== null).length;
const expectedUnrated = listedEntries.filter(entry => entry.score.score === null).length;
const expectedE2 = listedEntries.filter(entry => entry.evidence_level === "E2").length;
const expectedHalfStars = ["1.5", "2.5", "3.5", "4.5"];
const combinedThreshold = 1.5;
const expectedE0AtThreshold = listedEntries.filter(entry => entry.evidence_level === "E0" && entry.score.score !== null && entry.score.score >= combinedThreshold).length;
const listedProjectLeads = listedEntries.filter(entry => entry.kind === "project-source-lead");
const listedNeedsReview = listedProjectLeads.filter(entry => entry.needs_review).length;
const listedProjectSources = directory.counts.reviewed_projects + listedProjectLeads.length;
const listedProjectSourcesE0 = listedProjectLeads.filter(entry => entry.evidence_level === "E0").length;
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
    const outcomeStyle = outcome ? getComputedStyle(outcome) : null;
    const forbidden = card.querySelectorAll("img,.tags,.hardware-tags,.device,.limit,.card-end,.project-thumb,.rating-panel").length;
    const valid = children.length === 3 &&
      children[0].tagName === "H3" && children[0].querySelectorAll("a").length === 1 &&
      children[1].matches("p.card-outcome") && children[2].matches("div.card-meta") &&
      children[2].children.length === 2 &&
      card.querySelectorAll(".card-rating").length === 1 && card.querySelectorAll(".evidence-tag").length === 1 &&
      outcomeStyle?.whiteSpace === "nowrap" && outcomeStyle?.overflowX === "hidden" && outcomeStyle?.textOverflow === "ellipsis" &&
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

const auditFooter = async (targetPage, lang) => targetPage.locator("footer .footer-links").evaluate((footer, { expectedLang, repositoryURL }) => {
  const labels = expectedLang === "zh" ? ["关于", "数据下载", "GitHub", "CC BY 4.0"] : ["About", "Data download", "GitHub", "CC BY 4.0"];
  const links = [...footer.querySelectorAll(":scope > a")];
  const children = [...footer.children];
  const normalized = footer.innerText.replace(/\s+/g, " ").trim();
  const linkLabels = links.map(link => link.textContent.trim());
  const aboutPath = new URL(links[0]?.href || location.href).pathname;
  const downloadURL = new URL(links[1]?.href || location.href);
  const expectedAboutPaths = [`/${expectedLang}/about/`, `/${expectedLang}/about/index.html`];
  const tops = links.map(link => Math.round(link.getBoundingClientRect().top));
  const forbiddenMetadata = /v\d+\.\d+\.\d+|\d{4}-\d{2}-\d{2}|未进行实机测试|No hands-on hardware tests|not physically tested/i.test(normalized);
  const structure = children.length === 7 && children.every((child, index) => index % 2 === 0 ? child.tagName === "A" : child.tagName === "SPAN");
  const valid = normalized === labels.join(" · ") && JSON.stringify(linkLabels) === JSON.stringify(labels) &&
    expectedAboutPaths.includes(aboutPath) && expectedAboutPaths.includes(downloadURL.pathname) && downloadURL.hash === "#downloads" &&
    (links[2]?.href || "").replace(/\/$/, "") === repositoryURL.replace(/\/$/, "") && links[3]?.href === "https://creativecommons.org/licenses/by/4.0/" &&
    structure && !forbiddenMetadata && new Set(tops).size === 1 && footer.scrollWidth <= footer.clientWidth;
  return { valid, normalized, linkLabels, aboutPath, download: `${downloadURL.pathname}${downloadURL.hash}`, structure, forbiddenMetadata, singleLine: new Set(tops).size === 1, width: { client: footer.clientWidth, scroll: footer.scrollWidth } };
}, { expectedLang: lang, repositoryURL: config.repository_url });

const auditDirectoryShell = async (targetPage, lang) => targetPage.locator(".directory-page").evaluate((page, expectedLang) => {
  const isVisible = element => Boolean(element && (element.offsetWidth || element.offsetHeight || element.getClientRects().length));
  const heading = page.querySelector(".directory-head");
  const form = page.querySelector("#directory-filters");
  const visibleSelects = [...form.querySelectorAll("select")].filter(isVisible);
  const info = form.querySelector("a.directory-info");
  const filterTops = [...visibleSelects, info].filter(isVisible).map(control => Math.round(control.getBoundingClientRect().top));
  const infoURL = new URL(info?.href || location.href);
  const expectedAboutPaths = [`/${expectedLang}/about/`, `/${expectedLang}/about/index.html`];
  return {
    headingOnly: heading?.children.length === 1 && heading.firstElementChild?.tagName === "H1",
    searchCount: [...form.querySelectorAll('input[type="search"]')].filter(isVisible).length,
    visibleSelectIds: visibleSelects.map(select => select.id),
    filterRows: new Set(filterTops).size,
    removedKind: !form.querySelector("#directory-kind"),
    removedSort: !form.querySelector("#directory-sort"),
    info: info?.textContent.trim() === "ⓘ" && expectedAboutPaths.includes(infoURL.pathname) && infoURL.hash === "#scoring" && Boolean(info.getAttribute("aria-label")),
    forbidden: page.querySelectorAll(".directory-head .eyebrow,.directory-head .intro,.directory-head .actions,.boundary,#directory-share,#directory-share-status").length,
    downloadLinks: page.querySelectorAll('.directory-head a[download],a[href*="data/directory."]').length,
    width: { client: form.clientWidth, scroll: form.scrollWidth }
  };
}, lang);

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

  const checkFixedDirectorySort = async ({ pathName, score, grid }) => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    const scores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
    const result = {
      sort: "score-desc",
      sortInURL: new URL(page.url()).searchParams.get("sort"),
      descending: descendingRatedFirst(scores),
      count: scores.length,
      firstScores: scores.slice(0, 8),
      halfStarOptions: await page.locator(`${score} option`).evaluateAll(options => options.map(option => option.value).filter(value => value.endsWith(".5")))
    };
    await page.locator(score).selectOption("4");
    await page.waitForURL(url => url.searchParams.get("score") === "4");
    await page.reload({ waitUntil: "networkidle" });
    await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedScore4);
    const filteredScores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
    result.filteredURL = new URL(page.url()).searchParams.get("score");
    result.filteredDescending = descendingRatedFirst(filteredScores);
    await page.locator(score).selectOption("");
    await page.waitForURL(url => url.searchParams.get("score") === null);
    await page.reload({ waitUntil: "networkidle" });
    const resetScores = await page.locator(`${grid} .project:not([hidden])`).evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
    result.resetSort = "score-desc";
    result.resetSortInURL = new URL(page.url()).searchParams.get("sort");
    result.resetDescending = descendingRatedFirst(resetScores);
    return result;
  };

  checks.defaultSort = {
    directoryZh: await checkFixedDirectorySort({ pathName: "/zh/directory/", score: "#directory-score", grid: "#directory-grid" }),
    directoryEn: await checkFixedDirectorySort({ pathName: "/en/directory/", score: "#directory-score", grid: "#directory-grid" }),
    projectSources: await checkDefaultSort({ pathName: "/zh/project-sources/", form: "#project-source-filters", sort: "#project-source-sort", score: "#project-source-score", grid: "#project-source-grid" }),
    leads: await checkDefaultSort({ pathName: "/zh/leads/", form: "#lead-filters", sort: "#lead-sort", score: "#lead-score", grid: "#lead-grid" })
  };

  for (const [name, result] of Object.entries(checks.defaultSort)) {
    if (result.sort !== "score-desc" || result.sortInURL !== null || !result.descending) throw new Error(`${name} default star sorting failed`);
    if (!expectedHalfStars.every(value => result.halfStarOptions.includes(value))) throw new Error(`${name} half-star filter options failed`);
    if (name.startsWith("directory") && (result.filteredURL !== "4" || !result.filteredDescending)) throw new Error(`${name} fixed sorting after filter/reload failed`);
    if (result.resetSort !== "score-desc" || result.resetSortInURL !== null || !result.resetDescending) throw new Error(`${name} reset star sorting failed`);
  }

  const checkHomepage = async ({ pathName, placeholder, directoryPath, lang }) => {
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
    result.footer = await auditFooter(page, lang);
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
    zh: await checkHomepage({ pathName: "/zh/", placeholder: "输入你的设备", directoryPath: "/zh/directory/", lang: "zh" }),
    en: await checkHomepage({ pathName: "/", placeholder: "Enter your device", directoryPath: "/en/directory/", lang: "en" })
  };
  for (const [lang, result] of Object.entries(checks.home)) {
    if (result.h1 !== 1 || result.searches !== 1 || !result.placeholderMatches || result.subtitleLines > 1.25 || result.categories < 4 || !result.categoriesValid || result.forbidden !== 0 || !result.footer.valid || result.submittedQuery !== "Kindle") {
      throw new Error(`${lang} simplified homepage failed: ${JSON.stringify(result)}`);
    }
  }

  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  await page.locator("#directory-q").fill("AI");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project").length === total, expected);
  checks.cards = await page.locator("#directory-grid .project").count();
  checks.directoryCardContract = await auditCardGrid(page, "#directory-grid");
  checks.ratedCards = await page.locator('#directory-grid .project[data-rated="true"]:has(.card-rating:not(.unrated))').count();
  checks.unratedCards = await page.locator('#directory-grid .project[data-rated="false"]:has(.card-rating.unrated)').count();
  checks.directoryFooter = await auditFooter(page, "zh");
  checks.directoryShell = { zh: await auditDirectoryShell(page, "zh") };
  await page.goto(`${base}/en/directory/`, { waitUntil: "networkidle" });
  checks.directoryShell.en = await auditDirectoryShell(page, "en");
  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  await page.locator("#directory-q").fill("AI");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project").length === total, expected);
  checks.directoryNeedsReview = await page.locator('#directory-grid .project[data-kind="project-source-lead"][data-needs-review="true"] .evidence-tag').count();
  checks.directoryNeedsReviewText = await page.locator('#directory-grid .project[data-kind="project-source-lead"][data-needs-review="true"] .evidence-tag').evaluateAll(tags => tags.every(tag => /(待验证|To verify)/.test(tag.textContent)));

  await page.locator("#directory-q").fill("");
  await page.locator("#directory-evidence").selectOption("E2");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedE2);
  checks.e2Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-evidence").selectOption("E0");
  await page.locator("#directory-score").selectOption(String(combinedThreshold));
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedE0AtThreshold);
  checks.combinedE0ScoreVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.combinedE0ScoreValid = await page.locator("#directory-grid .project:not([hidden])").evaluateAll((cards, threshold) => cards.every(card => card.dataset.evidence === "E0" && card.dataset.score !== "" && Number(card.dataset.score) >= threshold), combinedThreshold);

  await page.locator("#directory-evidence").selectOption("");
  await page.locator("#directory-score").selectOption("4");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedScore4);
  checks.score4Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.scoreURL = new URL(page.url()).searchParams.get("score");
  await page.locator("#directory-score").selectOption("5");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedScore5);
  checks.score5Visible = await page.locator("#directory-grid .project:not([hidden])").count();
  await page.locator("#directory-score").selectOption("");
  await page.locator("#directory-category").selectOption("network");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project:not([hidden])").length === total, expectedNetwork);
  checks.networkVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.networkValid = await page.locator("#directory-grid .project:not([hidden])").evaluateAll(cards => cards.every(card => card.dataset.category === "network"));
  checks.networkURL = new URL(page.url()).searchParams.get("category");

  await page.goto(`${base}/zh/directory/?kind=reviewed-project&sort=title-asc`, { waitUntil: "networkidle" });
  const retiredScores = await page.locator("#directory-grid .project:not([hidden])").evaluateAll(cards => cards.map(card => card.dataset.score === "" ? null : Number(card.dataset.score)));
  checks.retiredDirectoryParams = {
    kind: new URL(page.url()).searchParams.get("kind"),
    sort: new URL(page.url()).searchParams.get("sort"),
    visible: retiredScores.length,
    descending: descendingRatedFirst(retiredScores)
  };
  await page.goto(`${base}/zh/directory/`, { waitUntil: "networkidle" });
  await page.locator("#directory-q").fill("Kindle");
  await page.waitForFunction(total => document.querySelectorAll("#directory-grid .project").length === total, expected);
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
        actionGuide: document.querySelectorAll(".action-guide").length,
        actionGuideBlocks: document.querySelectorAll(".action-guide > ul > li").length,
        actionGuideLinks: document.querySelectorAll(".action-guide a[href^='https://']").length,
        overlong
      };
    }, expectedTitle);
  };

  checks.projectDetail = await auditRecordDetail("/zh/projects/dietpi/", "DietPi");
  checks.leadDetail = await auditRecordDetail("/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/");

  await page.goto(`${base}/zh/project-sources/`, { waitUntil: "networkidle" });
  checks.projectSources = await page.locator("#project-source-grid .project").count();
  checks.projectSourceCardContract = await auditCardGrid(page, "#project-source-grid");
  checks.projectSourceNeedsReview = await page.locator('#project-source-grid .project[data-kind="project-source-lead"][data-needs-review="true"] .evidence-tag').count();
  checks.projectSourceNeedsReviewText = await page.locator('#project-source-grid .project[data-kind="project-source-lead"][data-needs-review="true"] .evidence-tag').evaluateAll(tags => tags.every(tag => /(待验证|To verify)/.test(tag.textContent)));
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

  const auditAbout = async (pathName, lang) => {
    await page.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    const result = await page.evaluate(({ version, expectedLang }) => {
      const text = document.querySelector("main")?.innerText || "";
      const release = document.querySelector("#release")?.innerText || "";
      const downloads = [...document.querySelectorAll("#downloads a[download]")].map(link => link.getAttribute("href"));
      return {
        h1: document.querySelectorAll("main h1").length,
        anchors: ["release", "evidence", "scoring", "contribute", "downloads"].filter(id => document.getElementById(id)).length,
        weightRows: document.querySelectorAll("table.scoring-weights tbody tr").length,
        evidenceRange: text.includes("E0") && text.includes("E3"),
        halfStar: text.includes("0.5"),
        nullable: text.includes("null"),
        contribution: document.querySelectorAll('main a[href*="issues/new/choose"]').length,
        release: release.includes(`v${version}`) && release.includes(expectedLang === "zh" ? "未进行实机测试" : "No hands-on hardware tests"),
        downloads,
        downloadPairs: ["directory.json", "directory.csv", expectedLang === "zh" ? "catalog.json" : "catalog.en.json", expectedLang === "zh" ? "catalog.csv" : "catalog.en.csv", "project-leads.json", "project-leads.csv", "scoring-evidence.json", "scoring-evidence-batch2-v120.json", "cost-evidence-v120.json", "action-guides-v120.json", "e0-audit-v120.json"].every(name => downloads.some(href => href.endsWith(name))),
        directoryLinks: Boolean(document.querySelector('#downloads a[href="../project-sources/"]')) && Boolean(document.querySelector('#downloads a[href="#scoring"]'))
      };
    }, { version: config.version, expectedLang: lang });
    result.footer = await auditFooter(page, lang);
    return result;
  };
  checks.about = {
    zh: await auditAbout("/zh/about/", "zh"),
    en: await auditAbout("/en/about/", "en")
  };

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on("console", message => { if (message.type() === "error") errors.push(`mobile: ${message.text()}`); });
  mobile.on("pageerror", error => errors.push(`mobile: ${error.message}`));
  const mobileMeasure = async (pathName, grid = null) => {
    await mobile.goto(`${base}${pathName}`, { waitUntil: "networkidle" });
    const lang = pathName.startsWith("/zh/") ? "zh" : "en";
    const hasDirectory = await mobile.locator(".directory-page").count();
    const directoryShell = hasDirectory ? await auditDirectoryShell(mobile, lang) : null;
    const firstCardTop = grid && await mobile.locator(`${grid} .project:not([hidden])`).count()
      ? await mobile.locator(`${grid} .project:not([hidden])`).first().evaluate(card => card.getBoundingClientRect().top)
      : null;
    return {
      width: await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth })),
      footer: await auditFooter(mobile, lang),
      directoryShell,
      firstCardTop,
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
    directoryZh: await mobileMeasure("/zh/directory/?q=Kindle", "#directory-grid"),
    directoryEn: await mobileMeasure("/en/directory/?q=Kindle", "#directory-grid"),
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
  if (!checks.directoryFooter.valid) throw new Error(`Directory footer failed: ${JSON.stringify(checks.directoryFooter)}`);
  for (const [lang, shell] of Object.entries(checks.directoryShell)) {
    if (!shell.headingOnly || shell.searchCount !== 1 || JSON.stringify(shell.visibleSelectIds) !== JSON.stringify(["directory-category", "directory-ai", "directory-score", "directory-evidence"]) || shell.filterRows !== 1 || !shell.removedKind || !shell.removedSort || !shell.info || shell.forbidden !== 0 || shell.downloadLinks !== 0 || shell.width.scroll > shell.width.client) {
      throw new Error(`${lang} directory shell simplification failed: ${JSON.stringify(shell)}`);
    }
  }
  if (checks.e2Visible !== expectedE2) throw new Error("E2 filter failed");
  if (checks.combinedE0ScoreVisible !== expectedE0AtThreshold || !checks.combinedE0ScoreValid) throw new Error("Independent evidence and star filters failed");
  if (checks.score4Visible !== expectedScore4 || checks.scoreURL !== "4" || checks.score5Visible !== expectedScore5) throw new Error("Star filter or URL state failed");
  if (checks.networkVisible !== expectedNetwork || !checks.networkValid || checks.networkURL !== "network") throw new Error("Device-category filter or URL state failed");
  if (checks.retiredDirectoryParams.kind !== null || checks.retiredDirectoryParams.sort !== null || checks.retiredDirectoryParams.visible !== Math.min(60, expected) || !checks.retiredDirectoryParams.descending) throw new Error("Retired directory controls still affect the simplified index");
  if (checks.directoryNeedsReview !== listedNeedsReview || !checks.directoryNeedsReviewText || checks.projectSourceNeedsReview !== listedNeedsReview || !checks.projectSourceNeedsReviewText) throw new Error("Needs-review marker coverage failed");
  if (checks.projectSources !== listedProjectSources || checks.projectSourcesE0 !== listedProjectSourcesE0 || checks.projectSourcesNas < 1) throw new Error("Project-source index/filter failed");
  if (checks.kindleVisible < 1 || checks.mobile.directoryZh.visible !== checks.kindleVisible || checks.mobile.directoryEn.visible !== checks.kindleVisible) throw new Error("Bilingual/device search persistence failed");
  if (checks.mobile.projectSources.visible !== checks.projectSourcesNas) throw new Error("Project-source mobile search persistence failed");
  if (checks.mobile.leads.visible !== directory.counts.device_or_community_routes) throw new Error("Mobile lead list coverage failed");
  for (const [name, result] of Object.entries(checks.mobile)) {
    if (result.width.scroll > result.width.inner) throw new Error(`Mobile ${name} overflow`);
    if (!result.footer.valid) throw new Error(`Mobile ${name} footer failed: ${JSON.stringify(result.footer)}`);
    if (result.subtitleLines !== null && result.subtitleLines > 1.25) throw new Error(`Mobile ${name} subtitle exceeds one line`);
    if (result.overlongParagraphs.length) throw new Error(`Mobile ${name} detail paragraph exceeds three lines: ${result.overlongParagraphs[0]}`);
  }
  for (const [lang, result] of Object.entries({ zh: checks.mobile.directoryZh, en: checks.mobile.directoryEn })) {
    if (!result.directoryShell || result.directoryShell.filterRows > 3 || result.directoryShell.width.scroll > result.directoryShell.width.client || result.firstCardTop === null || result.firstCardTop > 560) {
      throw new Error(`Mobile ${lang} directory controls or first-card visibility failed: ${JSON.stringify(result)}`);
    }
  }

  const projectEntry = directory.entries.find(entry => entry.entry_id === "project:dietpi");
  const leadEntry = directory.entries.find(entry => entry.entry_id === "lead:atlas-x-gl-ar300m16-ext-wifi-pineapple");
  const projectLeadId = firstLeadHref.split("/").filter(Boolean).at(-1);
  const projectLeadEntry = directory.entries.find(entry => entry.entry_id === `project-lead:${projectLeadId}`);
  if (!projectEntry || !leadEntry || !projectLeadEntry) throw new Error("Detail score fixtures missing from directory export");
  if (checks.projectLeadNeedsReview !== Number(projectLeadEntry.needs_review)) throw new Error("Project-lead detail review marker failed");
  const detailResults = [checks.projectDetail, checks.leadDetail, checks.projectLeadDetail, checks.englishUnratedDetail, checks.englishProjectDetail];
  for (const result of detailResults) {
    if (!result.wrap || result.h1 !== 1 || !result.titleMatches || result.bullets < 1 || result.aboutLinks !== 1 || result.legacyPanels !== 0 || result.overlong.length) {
      throw new Error(`Simplified detail contract failed: ${JSON.stringify(result)}`);
    }
  }
  if (!ratingDisplayMatches(checks.projectDetail.rating, projectEntry.score.score) || checks.projectDetail.unrated !== Number(projectEntry.score.score === null)) throw new Error("Reviewed-project detail rating failed");
  if (!ratingDisplayMatches(checks.leadDetail.rating, leadEntry.score.score) || checks.leadDetail.unrated !== Number(leadEntry.score.score === null)) throw new Error("Device-route detail rating failed");
  if (!ratingDisplayMatches(checks.projectLeadDetail.rating, projectLeadEntry.score.score) || checks.projectLeadDetail.unrated !== Number(projectLeadEntry.score.score === null)) throw new Error("Project-lead detail rating failed");
  for (const [result, entry] of [[checks.projectDetail, projectEntry], [checks.leadDetail, leadEntry], [checks.projectLeadDetail, projectLeadEntry]]) {
    const expectedGuide = entry.score.score !== null && entry.score.score >= 4;
    if (result.actionGuide !== Number(expectedGuide) || (expectedGuide && (result.actionGuideBlocks !== 3 || result.actionGuideLinks < 3))) throw new Error("Detail action-guide contract failed");
  }
  if (!ratingDisplayMatches(checks.englishUnratedDetail.rating, unratedEntry.score.score, "Not yet rated")) throw new Error("English not-yet-rated marker failed");
  for (const [lang, result] of Object.entries(checks.about)) {
    if (result.h1 !== 1 || result.anchors !== 5 || result.weightRows !== 5 || !result.evidenceRange || !result.halfStar || !result.nullable || result.contribution < 1 || !result.release || !result.downloadPairs || !result.directoryLinks || result.downloads.length !== 11 || !result.footer.valid) {
      throw new Error(`${lang} About content failed: ${JSON.stringify(result)}`);
    }
  }
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
