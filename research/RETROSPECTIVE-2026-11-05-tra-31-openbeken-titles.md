# TRA-31 OpenBeken diagnosis and second-batch SEO retrospective

Date: 2026-11-05
Scope: Diagnose the OpenBeken GSC contraction and add bilingual intent-aligned title/meta coverage for ESPurna, Dafang Hacks, Armbian Allwinner, Kindle model/firmware, Kindle displays, and webOS Homebrew without changing the locked Chinese slogan.

## Level 1 — Deliverable quality

- Added `research/gsc/2026-11-05-openbeken-drop.md` from the repository snapshot. It records 6/106 at position 3.29 versus 0/12 at position 9.75, explains the anonymized query boundary, and separates a top-N summary omission from the full page report.
- Confirmed the OpenBeken route, self-canonical, robots posture, hreflang, breadcrumb, AI-retrofit hub link, hardware-tag links, and related local-control links. The current English title postdates the measured window, so it was retained instead of being rewritten without evidence.
- Added a Chinese OpenBeken title, description, and opening lead for BK7231/Tuya → local MQTT/Home Assistant intent. Added bilingual source-controlled SEO and opening leads for ESPurna, Dafang Hacks, Armbian Allwinner, and webOS Homebrew, plus bilingual SEO fields for the Kindle article and display guide.
- Extended the generator and validator so article/guide SEO data produces exact title, meta description, and Open Graph fields. Validation locks all TRA-31 targets in both languages and keeps `二手硬件再就业指南` in every custom Chinese title.
- Rebuilt generated output and passed `python -X utf8 scripts/validate.py`. This is local acceptance only; PR review, GitHub CI, merge, Pages deployment, recrawl, and CTR recovery remain separate states.

## Level 2 — Process failures and corrections

- The planning summary said OpenBeken fell out of the top 50, but the fuller repository snapshot still contained the page with 12 impressions. Reading the complete page report corrected the diagnosis before copy was changed.
- Query+page rows accounted for only a small fraction of page impressions. Treating those rows as complete would have invented a query explanation, so the report uses page totals and labels the visible query sample as incomplete.
- The measurement window ended on 2026-11-03, while the current English OpenBeken title and TRA-29/30 links were merged on 2026-11-05. The implementation therefore avoids attributing the earlier drop to later code and avoids unnecessary English-title churn.
- The six targets span reviewed projects, one E0 repository lead, an article, and a guide. Reusing only the project override path would have forced unrelated data shapes together; the implementation keeps project/lead overrides in `project-page-visual.json` and stores article/guide SEO beside their canonical localized content.

## Level 3 — Reusable mechanism

1. Start with the complete page report, then compare any top-N planning summary; record whether a page is absent, merely below the summary cutoff, or still present with reduced visibility.
2. Use page totals for click/impression diagnosis and treat query rows as a partial sample whenever anonymization prevents reconciliation.
3. Place every release event on the same timeline as the GSC window. Do not claim that a post-window change caused or fixed pre-window metrics.
4. Audit the route, canonical, robots, sitemap/hreflang, and internal-link graph before changing copy. Preserve an already aligned title until a post-deployment window can evaluate it.
5. Store bilingual SEO in the canonical source appropriate to each page type, inherit Open Graph by default, rebuild, and assert exact generated output for both languages.
6. Keep an E0 lead's uncertainty in the description and visible opening even when sharpening search intent; traffic opportunity does not upgrade evidence.
7. Start the two-week CTR check after merge, deployment, and recrawl. PR creation and green CI are not publication or indexing evidence.

The page-drop diagnostic rules were added to `skills/hardware-revival-research/SKILL.md`.
