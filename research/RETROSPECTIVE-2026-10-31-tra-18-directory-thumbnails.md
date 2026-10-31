# TRA-18 directory thumbnails retrospective

Date: 2026-10-31
Scope: KitAgain directory list cards and homepage reviewed-route cards only. No deployment, merge, push, or catalog-fact changes.

## Level 1 — Deliverable quality

- Added source-reviewed thumbnails to directory cards for all 31 entries in `data/project-images.json`.
- Added one explicit, localized `图片待核 / Image pending review` placeholder to the other 512 directory records. The placeholder is neutral and does not imply a sourced device image.
- Added ledger-backed thumbnails to the three homepage reviewed-route cards: XiaoGPT, Onju Voice v2, and wire-pod.
- Reused each image record's bilingual alt text and `cover`/`contain` fit choice. No new compatibility, evidence, license, or hands-on claim was introduced.
- Kept media opt-in at the directory surface, so project-source, lead-index, guide-related, and article-related cards retain their prior structure.
- Used a 176 px side media column on desktop and 112 px at 390 px. The complete directory remains readable without horizontal overflow.

## Level 2 — Process failures and corrections

- The inherited partial implementation covered real images but left image-less directory records as text-only cards, which did not satisfy TRA-18's thumbnail-or-placeholder acceptance rule. A provenance-explicit placeholder closed the gap without fabricating visuals.
- The inherited retrospective confused 53 reviewed projects with 53 image-ledger entries. Reading `data/project-images.json` established the correct count of 31; validation now asserts 31 real images plus 512 placeholders instead of relying on prose.
- Adding `has-media` changed the article class string. A brittle validator first skipped directory cards because it expected `class="project"`, then a too-broad fix matched `project-media-placeholder`. A class-token boundary regex now detects only actual `project` cards.
- The first coverage assertion counted both real images and placeholders because both use the `project-thumb` base class. Real images are now counted by their anchor structure, while placeholders have a separate exact class count.
- Full-page screenshots initially left below-fold lazy images visually blank. The browser check now scrolls each visible real image into view and awaits `HTMLImageElement.decode()` before capturing evidence.
- Cross-page global search imports cards from static pagination. The runtime resolves both imported link `href` and image `src` values against the source page, and the browser test verifies XiaoGPT from `/en/directory/page/2/?q=xiaogpt`.

## Level 3 — Reusable mechanism

1. Treat the tracked image ledger as the only allowlist for real thumbnails; never turn a missing image into an inferred or synthetic device likeness.
2. If acceptance requires every card to have a visual position, use one clearly labeled neutral placeholder and assert real-image and placeholder counts separately.
3. Gate media rendering at the requested surface so a shared card generator cannot silently alter unrelated indexes or article cards.
4. Generate correct page-local relative paths, then normalize both links and media when static cards are imported across pagination.
5. Match HTML class tokens by boundaries in validators; exact whole-class strings and unrestricted prefixes both become brittle when modifier classes appear.
6. Separate structure checks from behavior and evidence: static counts/alt/ARIA, browser filtering and deep-page imports, then image decoding and visual inspection at desktop/mobile widths.

The reusable mechanism is recorded in `skills/hardware-revival-research/SKILL.md` under the directory-thumbnail guidance.

## Validation evidence

- `python -X utf8 scripts/build.py` — generated the bilingual site and all 10 directory pages per language.
- `python -X utf8 scripts/validate.py` — passed schema, 1,138 localized pages, internal links, public-file scan, and directory media coverage.
- `node --check docs/assets/app.js` and `node --check scripts/verify_directory_scores.mjs` — passed.
- `node scripts/verify_directory_scores.mjs` — passed 543 directory cards, 31 real images, 512 placeholders, three homepage thumbnails per language, Kindle global search = 13, deep-page XiaoGPT image/link normalization, and 390 px overflow checks.
- `research/validation-v1.20.0-directory-mobile.png` — inspected after decoding visible lazy images; real images and placeholders both render correctly.
- `git diff --check` — passed.
