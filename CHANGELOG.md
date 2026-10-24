# Changelog

## 1.19.0 - 2026-10-24

- Reduce both unified-directory pages to one title, one search field, and one compact filter row for device category, minimum stars, and evidence level.
- Remove the directory eyebrow, long introduction, explanatory tip, visible entry-type and sort controls, share/reset row, and four top action links while preserving fixed star-desc sorting and URL-backed primary filters.
- Replace the removed scoring tip with an accessible `ⓘ` link to the bilingual About scoring section; consolidate full JSON/CSV, the 200-source index, and scoring-method links on About.
- Keep all 547 records and complete exports unchanged, enforce first-card visibility with no overflow at 390 px, and rebuild the validated 1,124-URL sitemap for v1.19.0.

## 1.18.0 - 2026-10-24

- Compress every Chinese and English page footer to one line with only About, Data download, GitHub, and CC BY 4.0 links.
- Move the current version, catalog/device-atlas/project-source review dates, and no-hands-on-testing boundary to the bilingual About pages.
- Add a bilingual About download section covering the full directory, localized reviewed catalog, E0 project-source exports, and the scoring-evidence ledger.
- Keep all list cards limited to the name, one-line new job, stars or the unrated label, and evidence tag; add an all-page audit covering all 2,240 rendered cards.
- Preserve all 547 records and complete JSON/CSV exports, rebuild the 1,124-URL sitemap, and publish the display-only release as v1.18.0.

## 1.17.0 — 2026-10-24

- Simplify the bilingual homepage to one headline, one device search field, a one-line subtitle, and compact popular-category links.
- Reduce list cards to the device or project name, one-line new job, revival stars or the exact unrated label, and the independent evidence tag; keep complete facts on detail pages and in exports.
- Restructure detail pages around a heading and concise bullet points, and consolidate the evidence system, scoring algorithm, and contribution guidance on new Chinese and English About pages.
- Increase whitespace and type size, reduce the color palette, and preserve star-desc defaults, star/evidence filters, bilingual parity, and 390 px layouts without horizontal overflow.
- Keep all 547 records and the complete JSON/CSV exports unchanged apart from the release version; rebuild the sitemap with both About pages and publish the display-only release as v1.17.0.

## 1.16.0 — 2026-10-24

- Remove neutral 3-point placeholders: every unevidenced scoring dimension is now `null`, and the weighted average uses only evidenced dimensions with their original weights proportionally renormalized.
- Require at least three evidenced dimensions for a total; otherwise JSON/CSV totals stay null, cards use the exact bilingual labels `待评分 / Not yet rated`, and unrated entries sort after all rated entries.
- Re-research and rescore 49 Kindle/e-reader, router, old mini-PC/NAS, and smart-speaker routes using 156 unique source URLs recorded per dimension in a public scoring-evidence ledger.
- Publish 95 rated and 452 not-yet-rated entries. The rated half-star distribution is 1: 1, 1.5: 3, 2: 2, 2.5: 6, 3: 35, 3.5: 8, 4: 35, 4.5: 5, and 5: 0.
- Keep E0–E3 independent from stars and preserve all 147 E0 repository discoveries with `needs_review: true`; scoring research does not promote their compatibility evidence grade.
- Extend validation for nullable raw scores, the three-dimension threshold, renormalized arithmetic, effective weights, evidence-ledger/source parity, rated-first sorting, exact bilingual unrated markers, and JSON/CSV/public-copy parity.
- Rebuild the bilingual static site, exports, reports, and sitemap at v1.16.0. This release is committed locally only; no push or Pages deployment is part of this change set.

## 1.15.0 — 2026-10-24

- Replace the evidence-capped review-maturity score with independent five-dimension revival-value stars: feasibility/ease 25%, low cost 15%, docs/community 20%, practical value 20%, and low bricking/security risk 20%, rounded to the nearest 0.5 star.
- Keep E0–E3 as a separate, independently filterable evidence tag; it no longer enters or caps the star calculation.
- Preserve all 147 repository-level E0 candidates without deep review and add `needs_review: true` plus compact bilingual “待验证 / To verify” markers to their cards and detail pages.
- Store the five raw scores, weighted average, rounded total, per-dimension basis, evidence grade, and review-needed state in the unified JSON/CSV; add half-star filters and a nine-bucket distribution.
- Default the homepage, unified directory, project-source index, and device/community list to stars descending while retaining star and evidence controls, URL state, reset behavior, and concise cards.
- Rebuild all bilingual/static pages and exports at v1.15.0; validate 547/547 score coverage, 147 review-needed candidates, JSON/CSV parity, independent evidence/star filtering, default sorting, and mobile overflow.

## 1.14.0 — 2026-10-24

- Publish exactly 200 repository-unique project sources: 53 existing E1/E2 reviewed projects plus 147 new E0 GitHub discoveries spanning NAS/home servers, Kindle/e-readers, mobile, cameras, audio, IoT, robots, wearables, gaming and peripherals.
- Verify every discovery through the GitHub API and README entry point, exclude forks, 404s, profile repositories, obvious mirrors and read-only migrations, and keep all 147 at E0 without compatibility or installation claims.
- Add an evidence-capped 1–5 review-maturity score to all 547 public records. E0/E1/E2/E3 are capped at 2/3/4/5; the score is explicitly not popularity, quality, safety or success probability.
- Add bilingual 200-source and 547-entry indexes, 147 bilingual discovery detail pages, score/kind/category/search filters, and downloadable project-source plus unified JSON/CSV exports.
- Rebuild the sitemap and 1,177 static HTML files; validate 547/547 score coverage, 451 distinct primary-source URLs, JSON/CSV parity, internal links, public-file safety and browser interactions.
- Add release architecture, flow, permission, variable, test and SEO documentation, and update the reusable research skill with repository deduplication and evidence-capped scoring gates.

## 1.13.0 — 2026-10-23

- Add an evidence-bounded hardware-tag ledger covering all 53 reviewed projects and all 347 device/community leads.
- Render every exact model, device name, or supported hardware family as a separate, prominent tag on cards and detail pages in both languages.
- Make hardware tags clickable: each tag opens the relevant catalog or lead index with the device/model query applied and preserved in the URL.
- Include tag text in search while keeping exact models, device families, and hardware platforms distinct; no model is inferred beyond the existing reviewed scope.
- Validate complete tag coverage, bilingual labels, unique tags, rendered detail-page tags, public data export, and shareable lead searches.

## 1.12.0 — 2026-10-23

- Add 12 attributable upstream visuals for UBports, Termux, OpenMediaVault, RootMyTV, KOReader, Tasmota, Xiaomi Dafang Hacks, Frigate, Rockbox, Retro iPod Spotify, AsteroidOS and the HP Laser macOS driver; 31 of 53 reviewed projects now have distinct images.
- Prefer interface screenshots, wiring diagrams and actual output photos that help readers understand the resulting use, while retaining the original page, direct asset URL, alt text, caption and conservative media-license status.
- Rewrite reviewed-project cards and detail pages around visitor decisions: what the project gives you, which hardware must match, when to stop, what to prepare, what can go wrong and how each source link helps.
- Replace generic source-ledger rows with annotated bilingual resource cards and make the 12 deep-dive case pages use plain, action-oriented headings.
- Keep all compatibility, evidence and no-hands-on-testing boundaries while moving editorial process details below the practical answer.

## 1.11.0 — 2026-10-22

- Add distinct visual assets to 19 reviewed projects: 15 upstream device photos, hardware diagrams or interface screenshots, and 4 project-specific KitAgain illustrations.
- Prefer exact project/device imagery and use illustrations only where the upstream repository has no suitable visual; label every illustration as not an actual device photo.
- Publish bilingual alt text, captions, source pages, direct source-file URLs and conservative image-license status in `project-images.json`.
- Render responsive project thumbnails and full detail-page figures with `cover` or `contain` behavior chosen per asset, using optimized local WebP copies instead of hotlinks.
- Validate image IDs, files, attribution, captions and rendered bilingual pages.

## 1.10.0 — 2026-10-22

- Review 30 exact-model upstream sources across ESPHome, Tasmota and ophub/Armbian, while keeping the public denominator at 400 routes.
- Add model-specific hardware, installation, expected-result, revision-boundary and recovery fields in Chinese and English.
- Split the device layer into 30 E1 source-reviewed routes and 317 E0 leads; E1 still means source review rather than KitAgain hardware testing.
- Surface the reviewed-device counts and representative E1 pages on the homepage and device atlas.
- Export `device-reviews.json` and validate its upstream revisions, bilingual decision fields and rendered source links.

## 1.9.0 — 2026-10-22

- Expand the combined public directory from 100 to 400 devices and reuse routes: 53 reviewed entries plus 347 E0 device/community leads.
- Add a 300-entry device atlas covering ESPHome, Tasmota, postmarketOS, Chinese OpenWrt/router discussions, Chinese Armbian/TV-box documentation and one readable X lead corroborated by project repositories.
- Generate bilingual decision pages for every device with a clear goal, practical readiness, model boundary, evidence gap, annotated sources, next check and stop condition.
- Add device/model/source search and source filtering to the bilingual atlas index while keeping every entry readable without JavaScript.
- Preserve source-access limits and keep E0 device records separate from reviewed E1/E2 projects; no new hardware testing or blanket compatibility claim is made.

## 1.8.0 — 2026-10-21

- Add a traceable repository-owner identity link to every reviewed project page, covering all 53 catalog entries without treating repository ownership as proof of sole authorship.
- Keep author social profiles as a separate, stricter layer with attribution method and review date; add verified Onju and HP Laser author profiles.
- Remove the squeezelite-esp32 maintainer profiles from the unrelated core Squeezelite entry to avoid presenting a neighboring project as the listed project's authorship.
- Validate both repository-owner coverage and the attribution metadata for every manually curated author profile.

## 1.7.0 — 2026-10-21

- Expand the public directory to 100 unique projects and leads: 53 reviewed catalog entries plus 47 E0 field leads.
- Add 37 bilingual decision sheets sourced from Hackaday.io, Instructables, Home Assistant Community, Armbian Community Forum and Vintage Computer Federation Forum.
- Cover old laptops, phones, tablets, TV boxes, displays, cameras, keyboards, pagers, audio meters, 3D printers, routers and game hardware without treating a search result as compatibility proof.
- Preserve working, partial, failed, stale and research-only states separately; every new page states practical readiness, device fit, unsupported assumptions, user value, source contents and a stop condition.
- Show the combined 100-entry count on both homepages while keeping the reviewed catalog and E0 lead totals separate.

## 1.6.0 — 2026-10-21

- Rewrite both homepages around visitor outcomes: find a device, see what it can become, check fit and know when to stop.
- Add a bilingual ESP32 / ESP8266 hardware-revival guide covering local smart-device control, electronic shelf labels, LED lighting, old stereos, BLE proxies and legacy radio/infrared bridges.
- Put a prominent plain-language purpose statement on every project page.
- Add an independently maintained core-author and official-account layer; publish only profiles whose attribution can be traced to a project or author source.

## 1.5.0 — 2026-10-21

- Add a decision sheet to every E0 lead: current stage, practical readiness, known device fit, unsupported or unverified cases, user value and a continue/stop recommendation.
- Replace bare source URLs with annotated resource cards that explain what each project page, forum thread, device directory, code repository or demonstration contains.
- Adopt “垃圾佬复活站” as the playful Chinese-facing name while retaining KitAgain for the English brand, domain and repository identity.
- Expand lead validation so every bilingual decision field and annotated source is required and published.

## 1.4.0 — 2026-10-21

- Add a bilingual public Field Leads layer for 10 projects and reuse patterns found on forums, author sites, Codeberg, GitLab, Hackaday and Instructables.
- Give every E0 lead an independent page with its source platform, known facts, review gap, next verification step and safety boundary.
- Preserve failed and incomplete prototypes as evidence instead of hiding them, while separating upstream incompleteness from incomplete KitAgain review.
- Add Field Leads to navigation, home discovery, canonical/hreflang validation, sitemap and public JSON exports.

## 1.3.0 — 2026-10-21

- Publish two source-backed bilingual field guides: checking Kindle model/firmware before modification, and choosing a role for an old PC.
- Link both guides from each homepage with matching language pages, source links, related projects, canonical URLs and sitemap entries.
- Keep each guide's source-review date separate from the catalog's older project-review date; no hardware tests are claimed.

## 1.2.1 — 2026-10-21

- Show the complete English catalog at the root URL, with the existing Chinese switch; keep `/en/` as a readable alias canonicalized to `/`.
- Link the live community forum from the site navigation and bilingual community/contribution pages, while describing its remaining setup accurately.
- Keep the root as the English canonical homepage and omit the `/en/` alias from the sitemap.

## 1.2.0 — 2026-10-21

- Adopt KitAgain branding and the purchased kitagain.com domain.
- Move bilingual canonical URLs, sitemap and repository links to the custom domain.
- Preserve historical project URLs and evidence boundaries. Community activation is tracked separately.

## 1.1.0 — 2026-10-20

- Full Chinese and English sites: 53 project entries, 12 complete case analyses and 3 device-led topic guides.
- Stable use-case filter IDs, bilingual keyword search and language switching that preserves filters and fragment links.
- Source-hash tracking for translations, matching language URLs, self-canonicals, reciprocal hreflang and a rebuilt sitemap.
- English JSON/CSV exports with shared model, evidence, source and cost facts preserved.
- All 53 historical project URLs and the method URL remain readable; these are canonicalized HTML pages, not HTTP 301 redirects.
- Bilingual methodology, contribution and community-preparation pages; no forum, new domain, accounts or tracking service activated.
- Product version and future domain base URL centralized in `site.config.json`.

## 1.0.0 — 2026-10-20

- Initial editorial catalog: 53 entries, 13 device categories, 51 families, 12 detailed analyses.
- Original-author X text reviewed for Onju and the HP Laser driver; explicit source and hardware-testing limits.
- Static searchable site, shareable filters, individual pages, JSON/CSV exports and sitemap.
- Contribution forms, source methodology, candidates, schema and validation.

Publication and browser acceptance results are recorded in `research/VALIDATION.md`.
