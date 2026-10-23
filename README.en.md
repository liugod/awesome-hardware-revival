# KitAgain · Hardware Revival Field Guide

An evidence-aware directory for giving existing hardware a useful second life: smart speakers, phones, computers, routers, e-readers, cameras, robots, wearables and printers.

[English website](https://kitagain.com/) · [中文网站](https://kitagain.com/zh/) · [200 project sources](https://kitagain.com/en/project-sources/) · [full directory](https://kitagain.com/en/directory/) · [scoring method](https://kitagain.com/en/scoring/) · [Community forum](https://community.kitagain.com/) · [中文 README](README.md) · [Research report (Chinese)](research/REPORT.zh-CN.md)

**Version 1.15.0; five-dimension revival stars updated 2026-10-24.** The Chinese-facing name is “垃圾佬复活站”; the English brand, domain and repository remain KitAgain. The site has exactly **200 independent project sources deduplicated by repository URL**: 53 E1/E2 reviewed project/platform/tool entries plus 147 E0 discoveries checked through the GitHub API and README entry point. Another 347 device/community routes contain 30 E1 exact-model source reviews and 317 E0 leads. The [unified directory](https://kitagain.com/en/directory/) therefore contains **547 public records** from 451 distinct primary-source URLs. Project sources, reviewed projects, and device routes remain separate denominators; multiple device models from one upstream are not presented as independent projects.

All 547 records have explainable 1–5 revival-value stars with five raw dimensions: feasibility/ease 25%, low cost 15%, docs/community activity 20%, practical value 20%, and low bricking/security risk 20%. The weighted average is rounded to the nearest 0.5 star. E0–E3 is an independent evidence tag and neither enters nor caps the stars; lists default to stars descending. Current half-star distribution: 1: 0; 1.5: 0; 2: 0; 2.5: 14; 3: 511; 3.5: 21; 4: 1; 4.5: 0; 5: 0. All 147 repository discoveries remain E0 and carry `needs_review: true` / “To verify”. They were not deeply reviewed; missing dimensions use disclosed neutral placeholders rather than invented compatibility, safety, or cost findings.

Every existing device route still displays separate hardware-name or model tags that link back to a matching search. Tags distinguish exact models, source-bounded device families and hardware platforms without presenting guessed models as facts. Thirty-one reviewed projects have distinct visuals: 27 attributable upstream assets and 4 clearly labelled project-specific illustrations.

Project pages now start with the reader's decision: what the route gives you, which hardware must match, when to stop, what can go wrong and what each original link is useful for. Evidence, maintenance and licensing boundaries remain available below the practical answer.

Image provenance and captions are published in [`project-images.json`](data/project-images.json). A repository license is not assumed to license every image: upstream assets retain their source page and file URL, while illustrations explicitly state that they are not actual device photos.

## What is included

- 10 AI functionality projects, 2 with documented AI-assisted development or setup, 1 AI-adjacent use case, 40 conventional open-source reuse foundations.
- 12 detailed case analyses covering prerequisites, outcomes, limitations, costs still unknown, disassembly, cloud dependencies, recovery and suggested acceptance steps.
- Source URLs, review timestamps, README hashes where available, maintenance status, root license observations and explicit unknowns.
- 147 repository-unique E0 project discoveries, 30 E1 exact-model source reviews, 317 public E0 device/community leads, and 2 separate exclusions. The 200-source project index, 347-route device/community layer, and 53-entry reviewed catalog remain separate; E1 routes are source reviews rather than compatibility certifications or KitAgain hardware outcomes.
- Project pages lead with a plain-language purpose statement. All 53 reviewed entries expose the repository-owner profile as a traceability link without treating ownership as sole-authorship proof. Separately curated author social profiles require attributable project, repository or author-page evidence; the public coverage ledger is [`author-identity-coverage.json`](docs/data/author-identity-coverage.json).

Reviewed-catalog evidence: **E1 (50)** = repository/deployment documentation reviewed. **E2 (3)** = specific original-author hardware claims or demonstration descriptions also reviewed. **E3 (0)** = independently reproduced case verified by this catalog. The project-discovery layer contains **E0 (147)** repositories, while the device/community layer contains **E1 (30)** and **E0 (317)** routes. **No hands-on hardware testing was performed.** Full exports: [project-source JSON](data/project-leads.json) / [CSV](data/project-leads.csv), and [unified scored JSON](data/directory.json) / [CSV](data/directory.csv), which stores total stars, weighted average, all five raw scores, their basis, independent evidence grade, and review-needed state.

## Start with your device

Use the [site filters](https://kitagain.com/#catalog) for device, use, AI relationship, difficulty and evidence. Search in Chinese or English, including identifiers such as LX06, Kindle, Nest Mini or HP. Filter state is shareable and retained when switching languages.

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
