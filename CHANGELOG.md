# Changelog

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
