# KitAgain · Hardware Revival Field Guide

An evidence-aware directory for giving existing hardware a useful second life: smart speakers, phones, computers, routers, e-readers, cameras, robots, wearables and printers.

[English website](https://kitagain.com/) · [中文网站](https://kitagain.com/zh/) · [200 project sources](https://kitagain.com/en/project-sources/) · [full directory](https://kitagain.com/en/directory/) · [About and methodology](https://kitagain.com/en/about/) · [Community forum](https://community.kitagain.com/) · [中文 README](README.md) · [Research report (Chinese)](research/REPORT.zh-CN.md)

**Version 1.18.0; site-wide footer simplification released 2026-10-24.** This release changes presentation only and does not delete or reduce catalog data. Every Chinese and English page now has a one-line footer containing only About, Data download, GitHub, and CC BY 4.0. The version, three review dates, and no-hands-on-testing boundary moved to the bilingual [About page](https://kitagain.com/en/about/), with complete JSON/CSV exports in its [Data download section](https://kitagain.com/en/about/#downloads). The site still has exactly **200 independent project sources**, 347 device/community routes, and **547 public records** from 451 distinct primary-source URLs in the [unified directory](https://kitagain.com/en/directory/).

The homepage now has one headline, one device search field, a one-line subtitle, and popular device categories. List cards show only the name, the device's new job, stars or the unrated label, and the independent evidence grade. Complete compatibility, risk, source, and other fields remain on detail pages and in the JSON/CSV downloads; the evidence system, scoring algorithm, and contribution guide are consolidated on the bilingual [About page](https://kitagain.com/en/about/). Default star-desc sorting, star/evidence filters, and mobile support are unchanged.

The five revival-value dimensions remain feasibility/ease 25%, low cost 15%, docs/community activity 20%, practical value 20%, and low bricking/security risk 20%. A dimension without a verifiable source is stored as `null`, never filled with a neutral 3. A total is published only with at least three evidenced dimensions; their original weights are proportionally renormalized before averaging and rounding to the nearest 0.5 star. **95 / 547 entries are rated; 452 display “待评分 / Not yet rated”.** Rated entries sort first by stars descending, followed by unrated entries. Current rated distribution: 1: 1; 1.5: 3; 2: 2; 2.5: 6; 3: 35; 3.5: 8; 4: 35; 4.5: 5; 5: 0.

Batch 1 re-researched and rescored **49** Kindle/e-reader, router, old mini-PC/NAS, and smart-speaker routes. Per-dimension grounds and 156 unique source URLs are recorded in [`scoring-evidence.json`](data/scoring-evidence.json). E0–E3 remains an independent evidence tag and neither enters nor caps the stars. All 147 repository discoveries remain E0 and `needs_review: true` / “To verify”; scoring evidence does not automatically upgrade compatibility evidence.

Device detail pages still retain separate hardware-name or model tags that link back to a matching search. Tags distinguish exact models, source-bounded device families and hardware platforms without presenting guessed models as facts. Thirty-one reviewed projects have distinct visuals: 27 attributable upstream assets and 4 clearly labelled project-specific illustrations.

Detail pages use a heading and short bullet points to lead with the decision: what the route gives you, which hardware must match, when to stop, what can go wrong, and what each original link is useful for. A small About link now carries the evidence-level, scoring-method, and contribution guidance.

Image provenance and captions are published in [`project-images.json`](data/project-images.json). A repository license is not assumed to license every image: upstream assets retain their source page and file URL, while illustrations explicitly state that they are not actual device photos.

## What is included

- 10 AI functionality projects, 2 with documented AI-assisted development or setup, 1 AI-adjacent use case, 40 conventional open-source reuse foundations.
- 12 detailed case analyses covering prerequisites, outcomes, limitations, costs still unknown, disassembly, cloud dependencies, recovery and suggested acceptance steps.
- Source URLs, review timestamps, README hashes where available, maintenance status, root license observations and explicit unknowns.
- 147 repository-unique E0 project discoveries, 30 E1 exact-model source reviews, 317 public E0 device/community leads, and 2 separate exclusions. The 200-source project index, 347-route device/community layer, and 53-entry reviewed catalog remain separate; E1 routes are source reviews rather than compatibility certifications or KitAgain hardware outcomes.
- Project pages lead with a plain-language purpose statement. All 53 reviewed entries expose the repository-owner profile as a traceability link without treating ownership as sole-authorship proof. Separately curated author social profiles require attributable project, repository or author-page evidence; the public coverage ledger is [`author-identity-coverage.json`](docs/data/author-identity-coverage.json).

Reviewed-catalog evidence: **E1 (50)** = repository/deployment documentation reviewed. **E2 (3)** = specific original-author hardware claims or demonstration descriptions also reviewed. **E3 (0)** = independently reproduced case verified by this catalog. The project-discovery layer contains **E0 (147)** repositories, while the device/community layer contains **E1 (30)** and **E0 (317)** routes. **No hands-on hardware testing was performed.** Full exports: [project-source JSON](data/project-leads.json) / [CSV](data/project-leads.csv), [unified scored JSON](data/directory.json) / [CSV](data/directory.csv), and the [scoring evidence ledger](data/scoring-evidence.json). The unified export stores nullable totals and raw dimensions, effective weights, per-dimension grounds and source URLs, the independent evidence grade, and review-needed state.

## Start with your device

Use the [full directory](https://kitagain.com/en/directory/) to search device names, models, projects, or sources in Chinese or English, including identifiers such as LX06, Kindle, Nest Mini, or HP. Filter by device category, evidence, minimum stars, or entry type; star-desc remains the default, and filter state is shareable.

Installing an app, replacing firmware, replacing a motherboard and replacing a cloud service are different routes. Model, board revision, firmware and region matter. An archived mirror may have moved; a non-archived repository does not prove compatibility. Costs are `null`/`UNKNOWN`, never fabricated as zero.

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

`site.config.json` controls the base URL, repository URL, community URL and product version. Translations in `data/i18n/` are tied to source hashes; stale translations fail the build. See [translation and deployment maintenance](research/BILINGUAL-MAINTENANCE.md). The [independent forum](https://community.kitagain.com/) is online; its Chinese interface, categories and moderation workflows are still being prepared. Use GitHub Issues for formal catalog corrections.

Use the [issue forms](https://github.com/liugod/awesome-hardware-revival/issues/new/choose) to submit a project, correction, successful or failed reproduction. Include exact hardware/firmware, source versions, what worked, what failed and recovery evidence. See [CONTRIBUTING](CONTRIBUTING.md). No automated schedule has been created.

Original editorial text and catalog arrangement: **CC BY 4.0**. Original software: **MIT**. Third-party projects retain their own licenses and trademarks; linked firmware and upstream tutorials are not redistributed. See [LICENSE](LICENSE) and [LICENSE-CODE](LICENSE-CODE).
