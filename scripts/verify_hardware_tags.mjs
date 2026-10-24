import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import fs from "node:fs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const config = JSON.parse(fs.readFileSync(path.join(process.cwd(), "site.config.json"), "utf8"));
const browser = await chromium.launch({ headless: true });
const checks = {};

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  const errors = [];
  page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
  page.on("pageerror", error => errors.push(error.message));

  await page.goto(`${base}/zh/about/`, { waitUntil: "networkidle" });
  checks.version = (await page.locator("#release").innerText()).includes(`v${config.version}`);

  await page.goto(`${base}/zh/directory/?kind=reviewed-project`, { waitUntil: "networkidle" });
  checks.reviewedCards = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.cardHardwareTags = await page.locator("#directory-grid .project .hardware-tag").count();

  await page.goto(`${base}/zh/projects/open-xiaoai/`, { waitUntil: "networkidle" });
  checks.projectDetailTags = await page.locator(".record-detail .hardware-tag").allTextContents();
  checks.projectAboutLink = await page.locator("main a.about-link").count();
  const lx06 = page.locator('.hardware-tag', { hasText: "LX06" }).first();
  await lx06.click();
  await page.waitForURL(url => ["/zh/directory/", "/zh/directory/index.html"].includes(url.pathname) && url.searchParams.get("q") === "LX06");
  checks.projectQuery = await page.locator("#directory-q").inputValue();
  checks.projectVisible = await page.locator("#directory-grid .project:not([hidden])").count();
  checks.openXiaoVisible = await page.locator('[data-id="open-xiaoai"]:not([hidden])').count();
  await page.locator('[data-id="open-xiaoai"]').screenshot({ path: path.join(process.cwd(), "research", `validation-v${config.version}-hardware-tags.png`) });

  await page.goto(`${base}/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/`, { waitUntil: "networkidle" });
  checks.leadDetailTags = await page.locator(".hardware-tag").allTextContents();
  await page.locator(".hardware-tag").first().click();
  await page.waitForURL(url => ["/zh/directory/", "/zh/directory/index.html"].includes(url.pathname) && Boolean(url.searchParams.get("q")));
  checks.leadQuery = await page.locator("#directory-q").inputValue();
  checks.leadVisible = await page.locator("#directory-grid .project:not([hidden])").count();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  mobile.on("console", message => { if (message.type() === "error") errors.push(`mobile: ${message.text()}`); });
  mobile.on("pageerror", error => errors.push(`mobile: ${error.message}`));
  await mobile.goto(`${base}/zh/projects/printer-spl3/`, { waitUntil: "networkidle" });
  checks.mobileTags = await mobile.locator(".hardware-tag").allTextContents();
  checks.mobileWidth = await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth }));
  checks.mobileAboutLink = await mobile.locator("main a.about-link").count();
  await mobile.close();

  if (checks.reviewedCards !== 53 || checks.cardHardwareTags !== 0 || !checks.version) throw new Error("Simplified reviewed-project card coverage or version failed");
  if (!checks.projectDetailTags.includes("LX06") || checks.projectAboutLink !== 1) throw new Error("Project detail hardware tags or About link failed");
  if (checks.projectQuery !== "LX06" || checks.openXiaoVisible !== 1 || checks.projectVisible < 1) throw new Error("Project tag directory search failed");
  if (!checks.leadDetailTags.includes("GL-AR300M16-Ext") || checks.leadQuery !== "GL-AR300M16-Ext" || checks.leadVisible !== 1) throw new Error("Lead tag search failed");
  if (checks.mobileTags.length !== 6 || checks.mobileWidth.scroll > checks.mobileWidth.inner || checks.mobileAboutLink !== 1) throw new Error("Mobile detail tag layout failed");
  if (errors.length) throw new Error(`Browser errors: ${errors.join(" | ")}`);
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
