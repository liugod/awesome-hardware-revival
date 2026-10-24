# KitAgain · Hardware Revival Field Guide

An evidence-aware directory for giving existing hardware a useful second life: smart speakers, phones, computers, routers, e-readers, cameras, robots, wearables and printers.

[English website](https://kitagain.com/) · [中文网站](https://kitagain.com/zh/) · [200 project sources](https://kitagain.com/en/project-sources/) · [full directory](https://kitagain.com/en/directory/) · [About and methodology](https://kitagain.com/en/about/) · [Community forum](https://community.kitagain.com/) · [中文 README](README.md) · [Research report (Chinese)](research/REPORT.zh-CN.md)

**Version 1.20.0; evidence-enrichment release dated 2026-10-24.** The data still retains exactly **200 independent project sources**, 347 device/community routes, and **547 records** from 451 distinct primary-source URLs. The 95 entries already rated in v1.19 were each checked for a used-device price and the required modding spend. Only four had reliable evidence for both classes and received a recalculated cost score; 91 keep cost as `null`. Batch 2 investigated 100 TV-box, old-phone/tablet, smart-home, e-reader, and router routes: 96 reached the three-evidenced-dimension threshold and four remain unrated.

The homepage has one headline, one device search field, a one-line subtitle, and popular device categories. The unified directory also removes its explanation, tip panel, top download links, entry-type filter, and sort control. List cards still show only the name, the device's new job, stars or the unrated label, and the independent evidence grade. Complete compatibility, risk, source, and other fields remain on detail pages and in the JSON/CSV downloads.

The five revival-value dimensions remain feasibility/ease 25%, low cost 15%, docs/community activity 20%, practical value 20%, and low bricking/security risk 20%. A dimension without a verifiable source is stored as `null`, never filled with a neutral 3. A total is published only with at least three evidenced dimensions; their original weights are proportionally renormalized before averaging and rounding to the nearest 0.5 star. In the complete data, **191 / 547 entries are rated and 356 display “待评分 / Not yet rated”.** Four audit rejections are delisted from pages but retained in JSON/CSV, so public lists show 188 rated and 355 unrated entries. Rated entries sort first by stars descending. Full-data distribution: 1: 1; 1.5: 3; 2: 2; 2.5: 12; 3: 56; 3.5: 53; 4: 58; 4.5: 5; 5: 1.

The two scoring batches record **149 routes**: 49 Kindle/e-reader, router, old mini-PC/NAS, and smart-speaker routes in batch 1, plus 100 priority-device routes in this release. Per-dimension grounds are in [`scoring-evidence.json`](data/scoring-evidence.json), with the raw second-batch attempts also preserved in [`scoring-evidence-batch2-v120.json`](data/scoring-evidence-batch2-v120.json). E0–E3 remains independent from stars. A separate deep audit selected 30 of the 147 repository discoveries: 18 moved to E1, seven to E2, one stayed E0, and four non-actionable hardware-revival routes were delisted from display while remaining in data. There are now 118 `needs_review: true` / “To verify” records.

Device detail pages still retain separate hardware-name or model tags that link back to a matching search. Tags distinguish exact models, source-bounded device families and hardware platforms without presenting guessed models as facts. Thirty-one reviewed projects have distinct visuals: 27 attributable upstream assets and 4 clearly labelled project-specific illustrations.

Detail pages use a heading and short bullet points to lead with the decision: what the route gives you, which hardware must match, when to stop, what can go wrong, and what each original link is useful for. A small About link now carries the evidence-level, scoring-method, and contribution guidance.

Image provenance and captions are published in [`project-images.json`](data/project-images.json). A repository license is not assumed to license every image: upstream assets retain their source page and file URL, while illustrations explicitly state that they are not actual device photos.

## What is included

- 10 AI functionality projects, 2 with documented AI-assisted development or setup, 1 AI-adjacent use case, 40 conventional open-source reuse foundations.
- 12 detailed case analyses covering prerequisites, outcomes, limitations, costs still unknown, disassembly, cloud dependencies, recovery and suggested acceptance steps.
- Source URLs, review timestamps, README hashes where available, maintenance status, root license observations and explicit unknowns.
- 147 retained repository discoveries (122 E0, 18 E1, and 7 E2 after the 30-entry audit), 30 E1 exact-model source reviews, 317 public E0 device/community leads, and 2 separate exclusions. The project-source data, 347-route device/community layer, and 53-entry reviewed catalog remain separate; E1 routes are source reviews rather than compatibility certifications or KitAgain hardware outcomes.
- Project pages lead with a plain-language purpose statement. All 53 reviewed entries expose the repository-owner profile as a traceability link without treating ownership as sole-authorship proof. Separately curated author social profiles require attributable project, repository or author-page evidence; the public coverage ledger is [`author-identity-coverage.json`](docs/data/author-identity-coverage.json).

Reviewed-catalog evidence: **E1 (50)** = repository/deployment documentation reviewed. **E2 (3)** = specific original-author hardware claims or demonstration descriptions also reviewed. **E3 (0)** = independently reproduced case verified by this catalog. After the deep audit, the project-discovery layer contains **E0 (122), E1 (18), and E2 (7)**, while the device/community layer contains **E1 (30)** and **E0 (317)** routes. Across all 547 records this is E0 439, E1 98, and E2 10. **No hands-on hardware testing was performed.** Full exports include [project-source JSON](data/project-leads.json) / [CSV](data/project-leads.csv), [unified scored JSON](data/directory.json) / [CSV](data/directory.csv), the [cost ledger](data/cost-evidence-v120.json), [30-entry E0 audit](data/e0-audit-v120.json), and [scoring evidence](data/scoring-evidence.json).

## Start with your device

Use the [full directory](https://kitagain.com/en/directory/) to search device names, models, projects, or sources in Chinese or English, including identifiers such as LX06, Kindle, Nest Mini, or HP. Filter by device category, minimum stars, or evidence; the directory stays in star-desc order and keeps filter state in the URL.

Installing an app, replacing firmware, replacing a motherboard and replacing a cloud service are different routes. Model, board revision, firmware and region matter. An archived mirror may have moved; a non-archived repository does not prove compatibility. Cost remains `null` unless both a used-device range and a complete required parts/tools range have reliable dated sources.

Representative cases: [Onju Voice](https://github.com/justLV/onju-voice) replaces a Nest Mini PCB; [HP Laser macOS driver](https://github.com/Kuberwastaken/hp-laser-1008a-macos) has an author-documented Claude-assisted development process; [Kindle for WHOOP](https://github.com/kaibuildsai/kindle-for-whoop) includes AI-assisted setup documentation and a limited PW2 hardware report.

## Build and contribute

Requires Python 3.10+. The site build uses only the standard library; validation uses `jsonschema`.

```sh
python -m pip install -r requirements-dev.txt
python scripts/build.py
python scripts/validate.py
python -m http.server 4185 --bind 127.0.0.1 --directory docs
```

GitHub Pages serves `main:/docs`. The build produces static, indexable detail pages and a sitemap; JavaScript only adds filtering. No accounts, backend, trackers or external script dependencies.

The v1.20 build contains 1,116 canonical sitemap URLs, one English root homepage, and 54 retained legacy URLs, for 1,171 static HTML files. The public data retains all 547 records; four deep-audit rejections have no list/detail presentation. Every listed route rated 4 stars or higher has a source-linked bilingual action guide covering what is needed, rough steps, and when to stop.

`site.config.json` controls the base URL, repository URL, community URL and product version. Translations in `data/i18n/` are tied to source hashes; stale translations fail the build. See [translation and deployment maintenance](research/BILINGUAL-MAINTENANCE.md). The [independent forum](https://community.kitagain.com/) is online; its Chinese interface, categories and moderation workflows are still being prepared. Use GitHub Issues for formal catalog corrections.

Use the [issue forms](https://github.com/liugod/awesome-hardware-revival/issues/new/choose) to submit a project, correction, successful or failed reproduction. Include exact hardware/firmware, source versions, what worked, what failed and recovery evidence. See [CONTRIBUTING](CONTRIBUTING.md). No automated schedule has been created.

Original editorial text and catalog arrangement: **CC BY 4.0**. Original software: **MIT**. Third-party projects retain their own licenses and trademarks; linked firmware and upstream tutorials are not redistributed. See [LICENSE](LICENSE) and [LICENSE-CODE](LICENSE-CODE).
