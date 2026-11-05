# TRA-30 homepage and guide-hub link retrospective

Date: 2026-11-05
Scope: Add bilingual homepage entries for every existing device guide, then complete topical reciprocal links among the Nest Mini, speaker/voice, AI-retrofit, Onju, and OpenBeken routes. Delivery stops at open review PR #12; main merge and GitHub Pages deployment remain unauthorized and unperformed.

## Level 1 — Deliverable quality

- Added one EN/ZH homepage `Find by device / 按设备找` section with five device-plus-action anchors: Nest Mini local AI, speaker/voice, Kindle displays, home computers, and AI retrofit. The six existing directory-category links remain available separately.
- Completed the topical matrix in both languages. Onju v2 and Onju Voice now link to each other plus the Nest Mini, speaker/voice, and AI-retrofit hubs; those hubs link back. OpenBeken links only to the broader AI/automation hub, and that hub links back, rather than forcing OpenBeken into unrelated Nest Mini or speaker routes.
- Kept the exact Chinese slogan `二手硬件再就业指南` unchanged in the generator, h1, kicker, header, title, and Open Graph checks. No unsupported compatibility, performance, cost, or hands-on claim was added.
- Extended `scripts/validate.py` with the complete EN/ZH matrix and homepage hub contract. Updated the existing browser contract to distinguish five guide entries from six directory categories and to validate both sets independently.
- Deterministic rebuilds produced only the intended homepage, six target pages per language, shared stylesheet, generator, validators, and repository-local skill changes. The complete repository validator passed, and the existing Playwright directory/homepage suite passed with 543 cards, five guide entries per homepage, six category entries, and no browser errors.
- Targeted Playwright acceptance verified all 12 EN/ZH matrix pages at desktop width, clicked the homepage Nest Mini entry, confirmed zero missing edges and zero console/page errors, and confirmed the Chinese homepage at 390 px retained the exact slogan with no homepage overflow.
- Opened review-only PR #12: <https://github.com/liugod/awesome-hardware-revival/pull/12>. Linear TRA-30 received one completion comment and moved from `In Progress` to `In Review`; its GitHub integration had already attached the PR automatically.

## Level 2 — Process failures and corrections

- The first repository search traversed too much generated/data output and was truncated. Subsequent inspection stayed on `scripts/site_i18n.py`, `scripts/validate.py`, `data/guides.json`, the generated target pages, and the repository-local workflow skill.
- The first combined patch failed atomically because one validator line differed by whitespace. Splitting homepage, project-template, guide-template, and validation changes into separate patches made each change reviewable and avoided partial edits.
- The first full validation correctly rejected the old homepage-copy contract after the device section heading changed. The contract was updated to the new exact bilingual copy instead of weakened or removed.
- The first browser run correctly rejected the old assumption that every `.category-entry` was one of six query-based directory categories. The browser contract now counts and validates five clean guide URLs separately from six query-based category URLs.
- Ad hoc matrix checks needed two harness corrections: DOM `Set` values do not preserve `.has()` across the Playwright serialization boundary, and generated `index.html` paths need normalization only for test comparison. Neither issue required changing site URLs.
- A Chinese assertion piped through Windows became question marks. Re-running with Unicode escapes confirmed the page's actual h1 and kicker were correct; shell-transformed text was not treated as page evidence.
- A supplemental 390 px audit found a pre-existing 396 px overflow on `speaker-voice`: the global mobile project-card rule removes horizontal padding while thumbnail negative margins remain. TRA-30's CSS diff is homepage-scoped, so the unrelated global card fix was not folded into this SEO ticket. A deduplicated, parented follow-up was created as Linear TRA-34.

## Level 3 — Reusable mechanism

1. Write the topical link matrix before editing. Separate required reciprocity from merely possible cross-linking, and keep infrastructure projects out of device-specific hubs when the relationship is not real.
2. Use device-plus-action anchor text. A project name alone does not tell a visitor whether the destination compares firmware, a board swap, a service bridge, or a stop route.
3. Keep homepage guide hubs and directory categories as different navigation contracts even if they share a visual component. Static and browser tests should validate their counts and URL shapes separately.
4. Implement bilingual edges in the canonical generator, rebuild both languages, and assert the entire matrix in generated output. Do not hand-edit generated HTML.
5. Exercise one real homepage click and normalize `index.html` versus directory paths only inside the browser assertion. The generated file path and the public canonical route are related but not identical test values.
6. Preserve exact locked copy with generator and rendered-output assertions. SEO work does not authorize rebranding or evidence upgrades.
7. Treat implementation, open PR, Linear review state, merge, Pages deployment, public indexing, and GSC effect as separate gates. TRA-30 reached open PR and review state only.
8. When a scoped acceptance pass exposes an unrelated defect, prove whether the current diff caused it, keep the current ticket narrow, and create a concrete follow-up with viewport, expected/actual dimensions, selector/rule evidence, and parent linkage.

The reusable bilingual hub-link procedure was added to `skills/hardware-revival-research/SKILL.md`; user-scoped skills were not modified.
