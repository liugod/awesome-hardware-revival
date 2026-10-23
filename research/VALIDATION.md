# Validation — current build

Date: 2026-10-24. This validates the catalog, project-source discovery layer, device atlas and website, not hardware compatibility.

## Local acceptance

- v1.15.0: all 547 public records use five independent revival-value dimensions: feasibility/ease 25%, low cost 15%, docs/community 20%, practical value 20%, and low bricking/security risk 20%. Weighted averages round to the nearest 0.5 star. E0–E3 is stored and filtered separately and does not enter or cap the score.
- v1.15.0: the nine half-star buckets are 1 = 0, 1.5 = 0, 2 = 0, 2.5 = 14, 3 = 511, 3.5 = 21, 4 = 1, 4.5 = 0, and 5 = 0. All 147 shallow repository candidates remain E0, `needs_review: true`, provisional, and visibly marked “待验证 / To verify”; no deep-review or compatibility claim was added.
- v1.15.0: `python -X utf8 scripts/validate.py` passed five-component coverage, weights totaling 100%, score recomputation, half-star steps, 547/547 coverage, 147 review-needed rows, 451 distinct primary-source URLs, JSON/CSV parity, all internal links, 1,177 HTML files, 1,122 sitemap URLs, and public-file safety.
- v1.15.0: local Chromium confirmed default stars-desc sorting on `/`, `/zh/directory/`, `/zh/project-sources/`, and `/zh/leads/`; reset restored the default without adding `sort` to the URL. Independent E0 + star filtering returned the expected 464 routes, the E2 filter returned 3, 147 markers appeared in both full indexes, and sampled project/device/E0 details each rendered five raw dimensions.
- v1.15.0: 390 px checks found no horizontal overflow on the homepage, unified directory, project-source index, or device/community list. The inspected captures are `research/validation-v1.15-directory-mobile.png`, `research/validation-v1.15-project-sources-mobile.png`, and `research/validation-v1.15.0-hardware-tags.png`.

- v1.14.0: exactly 200 repository-unique project sources are public: 53 existing E1/E2 reviewed projects plus 147 E0 GitHub discoveries selected from 159 cross-batch unique candidates. The discovery pass confirmed repository API access, `fork=false`, and a readable README entry point; it did not promote compatibility, installation, recovery, or hands-on claims.
- v1.14.0: the unified directory contains 547 records from 451 distinct primary-source URLs. All 547 have an explainable score and evidence cap; distribution is score 1 = 341, score 2 = 123, score 3 = 80, score 4 = 3, score 5 = 0. All 147 project-source discoveries remain E0 / 1.
- v1.14.0: `python -X utf8 scripts/validate.py` passed the 200-source denominator, project/repository deduplication, 547/547 scoring coverage, JSON/CSV parity, 1,177 generated HTML files, 1,122 unique sitemap URLs, internal links, bilingual pages and public-file safety scan.
- v1.14.0: Chromium rendered 547/547 scored cards, filtered exactly 147 E0 project sources and 53 reviewed projects, returned 3 project sources for `NAS` and 13 unified records for `Kindle`, preserved the mobile query, rendered project/device/E0-detail scores as 3/5, 2/5 and 1/5, and reported `innerWidth=scrollWidth=390` on both mobile indexes.
- v1.14.0: visual captures were inspected at `research/validation-v1.14-project-sources-mobile.png`, `research/validation-v1.14-directory-mobile.png`, and `research/validation-v1.14.0-hardware-tags.png`; the historical v1.13 screenshot remains byte-identical to its committed version.

- v1.13.0: `hardware-tags.json` covers all 53 reviewed projects; the 47 legacy field leads use curated bilingual tags and the 300 device-atlas entries plus exact-model reviews use their recorded device/model fields, giving all 400 public routes at least one hardware tag.
- v1.13.0: every reviewed-project card/detail page and every lead card/detail page renders separate clickable hardware tags. The project and lead indexes restore `q` from the URL and preserve it across language switches.
- v1.13.0: `python -X utf8 scripts/validate.py` passed schema, tag coverage/kinds/uniqueness, all 877 generated HTML pages, internal links and public data exports.
- v1.13.0: Chromium clicked `LX06` from Open-XiaoAI and showed 2 matching reviewed projects; clicked `GL-AR300M16-Ext` from its detail page and showed exactly 1 matching lead. The HP Laser detail page rendered six separate model tags at 390 px with `innerWidth=scrollWidth=390`.

- v1.12.0: 31 of 53 reviewed projects have distinct images: 27 attributable upstream assets and 4 clearly labelled KitAgain illustrations. The 12 new upstream assets cover UBports, Termux, OpenMediaVault, RootMyTV, KOReader, Tasmota, Xiaomi Dafang Hacks, Frigate, Rockbox, Retro iPod Spotify, AsteroidOS and the HP Laser macOS driver.
- v1.12.0: every reviewed-project detail page now opens with a reader decision block for outcome, hardware fit and stop condition; source links are rendered as annotated resource cards in both languages.
- v1.12.0: `python -X utf8 scripts/validate.py` passed schema, 53 unique project IDs, 30 E1 model reviews, 317 E0 leads, all generated internal links, bilingual exports and the public-file scan.
- v1.12.0: Chromium rendered the Chinese Tasmota page and English HP Laser page with their upstream images and revised copy. At a 390 × 844 mobile viewport, the Chinese page reported `innerWidth=390` and `scrollWidth=390`; the three decision cards stacked to 358 px each. The desktop homepage rendered 53 project cards and 31 image-bearing cards with no horizontal overflow.

- v1.11.0: 19 distinct project images are mapped to catalog IDs: 15 upstream project assets and 4 KitAgain project-specific illustrations.
- v1.11.0: every upstream image retains a source page and direct file URL without assuming the repository license covers media; every illustration is explicitly labelled as not an actual device photo.
- v1.11.0: the build uses optimized local WebP copies, bilingual alt text and captions, and per-image `cover` or `contain` behavior.
- v1.11.0: Chromium rendered the Onju Voice upstream-device photo and XiaoGPT labelled illustration. At a 390 × 844 mobile viewport, `innerWidth` and document `scrollWidth` were both 390; the homepage reported 53/53 formal projects and found 19 image-bearing project cards.

- v1.10.0: the public denominator remains 400: 53 reviewed catalog entries, 30 E1 exact-model device-source reviews and 317 E0 device/community leads.
- v1.10.0: all 30 model reviews carry a 40-character upstream blob revision, a direct model-specific source, and bilingual hardware, installation, expected-result, boundary and recovery fields.
- v1.10.0: the reviewed batch covers 15 ESPHome devices, 10 Tasmota devices and 5 ophub/Armbian TV boxes; no review is promoted to E3 or described as KitAgain hardware testing.
- v1.10.0: rendered cards and detail pages distinguish E1 source-reviewed devices from E0 leads and expose every reviewed source in the public resource list.

- v1.9.0: the combined public total is exactly 400: 53 reviewed catalog entries plus 347 E0 leads, including 300 device-atlas records with unique IDs and slugs.
- v1.9.0: the device atlas contains 100 ESPHome, 100 Tasmota, 50 ophub/Armbian TV-box, 30 Chinese OpenWrt/router, 19 postmarketOS and 1 X-plus-GitHub route.
- v1.9.0: all 300 new entries include a purpose, practical readiness, device boundary, evidence gap, next check, stop condition and annotated source access state in both languages.
- v1.9.0: the build emits 822 localized pages, one complete English root and 54 historical URLs, for 877 static HTML pages.
- v1.9.0: the rendered Chinese atlas showed 347/347 entries; searching `AX3000T` returned exactly one Xiaomi Mi Router AX3000T result, whose Chinese and English detail pages exposed the goal, readiness, device boundary, evidence gap, next check, stop condition and annotated source.
- v1.9.0: the English AX3000T detail page rendered at 390 × 844 with `innerWidth=390` and `scrollWidth=390`, so no horizontal overflow was observed in the emulated mobile viewport.

- v1.8.0: all 53 reviewed project pages include a repository-owner identity link; validation treats it as traceability rather than sole-authorship proof.
- v1.8.0: 4 projects have separately curated author social profiles with attribution method and review date. The public coverage ledger contains 53 unique project rows.
- v1.8.0: the Squeezelite page no longer attributes maintainers from the separate squeezelite-esp32 project.
- v1.8.0: Chromium rendered the Chinese Onju Voice detail page at 1280 × 900 and the English XiaoGPT page at 390 × 844. The identity section remained readable in both captures: `research/acceptance-v1.8-onju-zh.png` and `research/acceptance-v1.8-xiaogpt-mobile.png`.

- JSON Schema with URI and date-time formats passed.
- 53 unique IDs, 51 families, 13 categories and 12 complete deep dives.
- JSON/CSV parity, candidate separation, unknown-cost nulls and evidence invariants passed.
- 55 static HTML pages: one H1 and canonical each; all generated internal file links and anchors resolve.
- Public text scan found no credential patterns, private machine paths or UTF-8 replacement characters.
- Chrome rendered the index and HP driver detail page.
- Search `Kindle` returned 8 entries; adding AI-assisted returned 1.
- Combining device=e-reader, use=information screen, difficulty=high, evidence=E2 retained the WHOOP entry; reload preserved filters.
- Nonexistent search displayed the zero-result state; reset restored 53.
- Share button copied the active filter URL.
- 390 × 844 browser viewport: two-column filter controls, one-column entries and readable detail page; DOM measurements showed no horizontal overflow. This is viewport emulation, not a physical phone test.

## Publication acceptance

- Public repository: https://github.com/liugod/awesome-hardware-revival
- Canonical site: https://kitagain.com/; repository homepage metadata also points to this URL. Pages reports `built`, CNAME `kitagain.com`, source `main:/docs`.
- v1.15.0 content commit: `a750c74462d0a08691d1884bb459e8acad35444f`.
- GitHub `Validate catalog and site` run [40001085706](https://github.com/liugod/awesome-hardware-revival/actions/runs/40001085706) and `pages-build-deployment` run [40001085276](https://github.com/liugod/awesome-hardware-revival/actions/runs/40001085276) both completed successfully for that commit. Pages API readback reported `built`, CNAME `kitagain.com`, HTTPS enforced, and source `main:/docs`.
- Cache-busted HTTPS readback returned 200 and matched local SHA-256 byte-for-byte for 15 artifacts: root, Chinese and English homepages, Chinese directory/project-source/device-route indexes, both scoring pages, unified JSON/CSV, project-source JSON/CSV, sitemap, JavaScript, and CSS.
- v1.15.0 release hashes: `project-leads.json` `7cfbdbc4acc3ae9f9cfca7f819cc73732eade334274f54350e36fbfa93fa1b2c`; `project-leads.csv` `8dbbbe60f04c4740b238b70f396111b99f6ad47e9bdc68781f2412554c5ce287`; `directory.json` `db6dfcf9c03a8f5bd612fef6c29b1db2bade501aa4ab5c38696140911e7fa75f`; `directory.csv` `88a2e95481adc3ef983e1f16a896235d26d8e3ac14070018418cdc224a0e8549`; `sitemap.xml` `d2bd94630a753bfbf92d7b87adff494e54317673bdb6fd5d618af2276e6b88d8`.
- Live JSON/CSV readback confirmed version 1.15.0, scoring schema 2.0.0, 547/547 scores with five dimensions, the published nine-bucket distribution, exactly 147 `needs_review` rows in both exports, and 1,122 unique sitemap URLs with 1,122 `lastmod` values.
- Public Chromium confirmed default stars-desc order on the homepage, unified directory, 200-source index, and 347-route index; reset preserved that default without a `sort` query. Independent E0 + star filtering returned 464 valid rows, E2 returned 3, both full indexes rendered 147 compact review markers, sampled details rendered five dimensions, and all four 390 px layouts had `innerWidth=scrollWidth=390`.
- v1.14.0 content commit: `e44488910ed4d3188d6b475701e5b745e73604e0`.
- GitHub `Validate catalog and site` run [39993882577](https://github.com/liugod/awesome-hardware-revival/actions/runs/39993882577) and `pages-build-deployment` run [39993881925](https://github.com/liugod/awesome-hardware-revival/actions/runs/39993881925) both completed successfully for that commit.
- GitHub Contents API readback matched local Git blobs for README, project-source JSON, unified JSON/CSV, root HTML, Chinese 200-source index and sitemap.
- Independent HTTPS GETs returned 200 and matched local SHA-256 byte-for-byte for the root page, Chinese project-source and unified-directory pages, project-source JSON/CSV, unified JSON/CSV and sitemap.
- Release hashes: `project-leads.json` `1dd9fbadfacee001eb764c97ce7e9f274ade4a68dc56409c317ebbe190366676`; `project-leads.csv` `bacbaedb4da425143987c53f0ee988a4b112e54a9bf13aaa32cd2044284a974a`; `directory.json` `0adc1ad1e5421c0e59970f4ae974a18e87a411233fd108fe8a78ab529e6393cd`; `directory.csv` `597d003506b5cd79ee915639d4add3c2e649493bef9c920d14c5e75cc60a4173`; `sitemap.xml` `21859b95165d85d91557c6cc4b32addc469462313706c525276ffab99cf4f2ef`.
- Public Chromium readback rendered 547 scored directory cards, 147 E0 project-source cards, 200 project-source index cards, 3 `NAS` results, the E0 detail score `1/5`, the English `200 independent project sources` heading, and 390 px pages with no horizontal overflow.

The initial 2026-10-20 publication used commit `39e5b423fae4c9d3203d73c5d1e65cbd9e6172ca` and the pre-custom-domain GitHub Pages URL. Those earlier catalog JSON/CSV hashes are historical release evidence, not current v1.14.0 hashes.

## Limits

No hardware was flashed, disassembled, driven or tested. Suggested hardware acceptance steps in case studies are unexecuted. No independent E3 reproduction has been verified. X text was read, embedded video was not verified. Not every outbound URL was exhaustively crawled; each catalog record distinguishes reviewed primary content from other supporting links.
