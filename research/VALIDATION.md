# Validation — current build

Date: 2026-10-22. This validates the catalog, device atlas and website, not hardware compatibility.

## Local acceptance

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
- Site: https://liugod.github.io/awesome-hardware-revival/
- Initial content commit: `39e5b423fae4c9d3203d73c5d1e65cbd9e6172ca`.
- GitHub `Validate catalog and site` workflow passed on that commit; Pages was enabled from `main:/docs`.
- Independent GitHub Contents API readback matched local README, catalog JSON and index HTML byte-for-byte.
- Independent public HTTPS GETs matched local index HTML, JSON, CSV, sitemap and HP detail HTML byte-for-byte on 2026-10-20 at 10:40:56 UTC.
- Catalog JSON SHA-256: `0d5cf367ff0f0d560d519fa5600145aa771b367fce80c71f7b4d1d18264670ad`.
- Catalog CSV SHA-256: `f857e898708342db54bbebcd049e6fc1b879fb871fef8e34ab2971cae180c5d9`.
- Chrome opened the public HTTPS page and rendered its title, navigation, counts and project entries. Public-page screenshot captured.
- Browser download automation timed out. The CSV URL itself was independently retrieved and hash-verified; successful browser download-manager completion is **not** claimed. Full interaction tests above were performed on the local build; deployed files were then independently matched to that build.

## Limits

No hardware was flashed, disassembled, driven or tested. Suggested hardware acceptance steps in case studies are unexecuted. No independent E3 reproduction has been verified. X text was read, embedded video was not verified. Not every outbound URL was exhaustively crawled; each catalog record distinguishes reviewed primary content from other supporting links.
