import { chromium } from "file:///C:/Users/liuji/AppData/Roaming/npm/node_modules/playwright/index.mjs";
import path from "node:path";

const base = process.env.KITAGAIN_PREVIEW || "http://127.0.0.1:4185";
const browser = await chromium.launch({ headless: true });
const checks = {};

try {
  const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
  await page.goto(`${base}/zh/`, { waitUntil: "networkidle" });
  checks.reviewedCards = await page.locator("#project-grid .project").count();
  checks.reviewedCardsWithTags = await page.locator("#project-grid .project:has(.hardware-tag)").count();
  checks.version = (await page.locator("footer").innerText()).includes("v1.13.0");
  const lx06 = page.locator('[data-id="open-xiaoai"] .hardware-tag', { hasText: "LX06" });
  await lx06.click();
  await page.waitForURL(/\?q=LX06/);
  checks.projectQuery = await page.locator("#q").inputValue();
  checks.projectVisible = await page.locator("#project-grid .project:not([hidden])").count();
  checks.openXiaoVisible = await page.locator('[data-id="open-xiaoai"]:not([hidden])').count();
  await page.locator('[data-id="open-xiaoai"]').screenshot({ path: path.join(process.cwd(), "research", "validation-v1.13-hardware-tags.png") });

  await page.goto(`${base}/zh/leads/atlas-x-gl-ar300m16-ext-wifi-pineapple/`, { waitUntil: "networkidle" });
  checks.leadDetailTags = await page.locator(".hardware-tag").allTextContents();
  await page.locator(".hardware-tag").first().click();
  await page.waitForURL(/\/zh\/leads\/\?q=/);
  checks.leadQuery = await page.locator("#lead-q").inputValue();
  checks.leadVisible = await page.locator("#lead-grid .project:not([hidden])").count();

  const mobile = await browser.newPage({ viewport: { width: 390, height: 844 }, isMobile: true, hasTouch: true });
  await mobile.goto(`${base}/zh/projects/printer-spl3/`, { waitUntil: "networkidle" });
  checks.mobileTags = await mobile.locator(".hardware-tag").allTextContents();
  checks.mobileWidth = await mobile.evaluate(() => ({ inner: innerWidth, scroll: document.documentElement.scrollWidth }));
  await mobile.close();

  if (checks.reviewedCards !== 53 || checks.reviewedCardsWithTags !== 53 || !checks.version) throw new Error("Reviewed-project tag coverage or version failed");
  if (checks.projectQuery !== "LX06" || checks.openXiaoVisible !== 1 || checks.projectVisible < 1) throw new Error("Project tag search failed");
  if (!checks.leadDetailTags.includes("GL-AR300M16-Ext") || checks.leadQuery !== "GL-AR300M16-Ext" || checks.leadVisible !== 1) throw new Error("Lead tag search failed");
  if (checks.mobileTags.length !== 6 || checks.mobileWidth.inner !== checks.mobileWidth.scroll) throw new Error("Mobile tag layout failed");
  console.log(JSON.stringify(checks, null, 2));
  await page.close();
} finally {
  await browser.close();
}
