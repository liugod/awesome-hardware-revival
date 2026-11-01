# TRA-19 full-directory thumbnail retrospective

Date: 2026-11-01
Scope: Raise source-backed thumbnail coverage across the complete KitAgain directory in the dedicated TRA-19 worktree. The image-work session ended without a push, PR, merge, Pages deployment, or public acceptance.

## Level 1 — Deliverable quality

- Expanded the canonical image ledger from 31 visual entries, of which 27 were upstream source-backed and four were KitAgain illustrations, to 352 unique upstream source-backed entries.
- Raised source-backed coverage from 27/543 (5.0%) to 352/543 (64.8%). The remaining 191 listed records retain the localized neutral `图片待核 / Image pending review` placeholder.
- Coverage by listed directory kind is 43/53 reviewed projects, 101/143 project-source leads, and 208/347 device/community routes.
- Replaced all four prior KitAgain illustrations with upstream assets. No synthetic device likeness remains in the ledger.
- Generalized thumbnail lookup from reviewed-project `project_id` values to unified directory `entry_id` values while leaving homepage and project-detail image behavior limited to reviewed projects.
- Stored source page, direct image URL, bilingual alt/caption text, decoded dimensions/format, original-download hash, normalized hash, and conservative `not-separately-stated` image-rights status for newly acquired assets.
- Kept every listed card visually complete: 352 real thumbnails plus 191 explicit placeholders, in both languages and every static directory page.

## Level 2 — Process failures and corrections

- The first cross-kind discovery pass joined GitHub leads by `content_id` (`PS-*`) instead of repository ID. This falsely reported 123 missing candidates. Joining by the stable suffix of `entry_id` corrected the audit.
- The original GitHub discovery loop made two sequential API calls per repository and took several minutes. Bounded concurrency reduced the same audit to a practical duration without changing source selection rules.
- Node `fetch` did not inherit the workstation proxy and produced systematic `ECONNRESET` failures for `raw.githubusercontent.com`. A curl fallback using the environment proxy recovered the real assets; network failure was not reclassified as absence.
- ESPHome pages advertised one shared social card before the device image. Hash deduplication exposed 97 false duplicates; rejecting the site-wide social card allowed device-specific page images to win.
- The initial 320×180 / 5 KB gate rejected valid small upstream device thumbnails. The final gate accepts decodable images at 180×150, 50,000 pixels, and 2 KB while still rejecting thin banners, tiny controls, badges, and icons.
- A full desktop evidence screenshot exposed three false positives that structural tests could not: a Ko-fi support button, an Armbian site wordmark, and a Tasmota site logo. They were added to the discovery deny rules and removed from the ledger.
- Re-running acquisition after a transient source failure initially risked dropping previously validated images. The apply step now preserves prior validated assets unless a candidate is explicitly denied, while still replacing refreshed entries deterministically.
- Shared roundup pages, anti-bot challenge pages, and exact-model pages with no representative media were left as placeholders instead of reusing one generic image across many records.

## Level 3 — Reusable mechanism

1. Address every directory visual by unified `entry_id`, with `project_id` retained only for reviewed-project detail and homepage behavior.
2. Separate candidate discovery, binary acquisition/validation, and canonical ledger application so remote instability cannot silently corrupt public data.
3. Require bounded download size, real image decoding, minimum dimensions, normalized WebP output, original and normalized SHA-256, and duplicate-hash rejection.
4. Rank source-page Open Graph and device images ahead of generic assets, but maintain explicit filters for badges, donation buttons, social cards, challenge art, controls, and unrelated site logos.
5. Preserve a neutral placeholder when provenance or representation is weak. Coverage should measure unique accepted images, not candidate URLs or repeated generic banners.
6. Make the merge idempotent and resilient to transient network failures: preserve previously validated entries, but allow an explicit visual-review deny list to remove false positives.
7. Validate ledger counts by directory kind, generated-file parity, every internal link, cross-page imported image URLs, real browser decode, desktop/mobile overflow, and visual evidence screenshots.

This mechanism is recorded in `skills/hardware-revival-research/SKILL.md` under the full-directory image-enrichment guidance.

## Validation evidence

- `python -X utf8 scripts/build.py` — rebuilt 1,138 localized pages plus historical outputs.
- `python -X utf8 scripts/validate.py` — passed schema, internal links, exported-data parity, image hashes/files, coverage summary, and public-file scan.
- `research/tra-19-directory-image-missing.json` — records the final 191 placeholders after acquisition and visual-review corrections, with a per-entry reason and aggregate reason counts.
- `node scripts/verify_directory_scores.mjs` — passed 543 directory cards, 352 images, 191 placeholders, homepage thumbnails, cross-page XiaoGPT image/link normalization, lazy-image decode, and zero 390 px overflow.
- `research/validation-v1.20.0-directory-mobile.png` — visually inspected; real images and placeholders render correctly at 390 px.
- `research/validation-v1.20.0-directory-desktop-tra19.png` — visually inspected; the Kindle result set has aligned media, correct placeholders, and no horizontal overflow.
- `node --check` for modified JavaScript and `git diff --check` — passed.
