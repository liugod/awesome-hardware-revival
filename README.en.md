# Hardware Revival Field Guide

An evidence-aware directory for giving existing hardware a useful second life: smart speakers, phones, computers, routers, e-readers, cameras, robots, wearables and printers.

[English website](https://liugod.github.io/awesome-hardware-revival/en/) · [中文网站](https://liugod.github.io/awesome-hardware-revival/zh/) · [中文 README](README.md) · [English JSON](docs/data/catalog.en.json) · [English CSV](docs/data/catalog.en.csv) · [Research report (Chinese)](research/REPORT.zh-CN.md)

**Version 1.1.0, sources reviewed 2026-10-20.** 53 project/platform/tool entries across 13 categories and 51 project families. All 53 entries, 12 detailed analyses and 3 topic guides are available in Chinese and English. This is not a claim of 53 independently tested hardware builds. Translation does not constitute fresh upstream verification.

## What is included

- 10 AI functionality projects, 2 with documented AI-assisted development or setup, 1 AI-adjacent use case, 40 conventional open-source reuse foundations.
- 12 detailed case analyses covering prerequisites, outcomes, limitations, costs still unknown, disassembly, cloud dependencies, recovery and suggested acceptance steps.
- Source URLs, review timestamps, README hashes where available, maintenance status, root license observations and explicit unknowns.
- 6 separate candidates or exclusions. Related generations are grouped by `family`; prerequisites are not presented as finished hardware outcomes.

Evidence: **E1 (50)** = repository/deployment documentation reviewed. **E2 (3)** = specific original-author hardware claims or demonstration descriptions also reviewed. **E3 (0)** = independently reproduced case verified by this catalog. **No hands-on hardware testing was performed.** Four original X posts from two case families were read; embedded videos were not verified.

## Start with your device

Use the [site filters](https://liugod.github.io/awesome-hardware-revival/en/#catalog) for device, use, AI relationship, difficulty and evidence. Search in Chinese or English, including identifiers such as LX06, Kindle, Nest Mini or HP. Filter state is shareable and retained when switching languages.

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

`site.config.json` controls the base URL, repository URL and product version. Translations in `data/i18n/` are tied to source hashes; stale translations fail the build. See [translation and deployment maintenance](research/BILINGUAL-MAINTENANCE.md). The independent community is in preparation, not yet deployed.

Use the [issue forms](https://github.com/liugod/awesome-hardware-revival/issues/new/choose) to submit a project, correction, successful or failed reproduction. Include exact hardware/firmware, source versions, what worked, what failed and recovery evidence. See [CONTRIBUTING](CONTRIBUTING.md). No automated schedule has been created.

Original editorial text and catalog arrangement: **CC BY 4.0**. Original software: **MIT**. Third-party projects retain their own licenses and trademarks; linked firmware and upstream tutorials are not redistributed. See [LICENSE](LICENSE) and [LICENSE-CODE](LICENSE-CODE).
