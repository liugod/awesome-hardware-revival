# TRA-38 RootMyTV CTR 与 TV 刷机意图内链复盘

Scope: From `origin/main` at TRA-37 merge `330df718`, align the bilingual RootMyTV page with “root my TV / is my TV rootable” intent, state evidence-bounded fit and risks, and lock visible links to the TV/TV-box hub and webOS Homebrew. Delivery stops at an open PR; merge and GitHub Pages deployment remain unauthorized.

## 一阶：交付结果

- Added bilingual source-controlled title, meta description, and opening answers for RootMyTV. The English title changed from `RootMyTV: compatibility and reproduction · KitAgain` to `Can I Root My LG TV? RootMyTV Compatibility | KitAgain`; the Chinese title changed from `RootMyTV：适配设备与复现条件 · 二手硬件再就业指南 · KitAgain` to `LG webOS 电视能 Root 吗？RootMyTV 适用版本 | 二手硬件再就业指南 · KitAgain`.
- Added a visible bilingual eligibility and risk section based on the upstream model-year/webOS TV Version thresholds. It states that older firmware may still fail, lists never-supported webOS generations, distinguishes webOS TV Version from Software Version, and retains downgrade, update-lockout, damage/warranty, and stale-firmware limits.
- Made the RootMyTV → webOS Homebrew link explicit while retaining the generated RootMyTV → TV/TV-box hub link. Static validation locks those two forward links plus the existing webOS Homebrew → RootMyTV and TV/TV-box hub → RootMyTV links.
- Preserved the exact Chinese slogan `二手硬件再就业指南`. Generated diffs are limited to the English and Chinese canonical RootMyTV pages plus the historical RootMyTV URL; webOS Homebrew and OpenBeken pages have no generated diff.

## 二阶：过程与纠偏

- The first repository-wide `node scripts/verify_directory_scores.mjs` run failed on a pre-existing homepage category-link contract: rendered links still used `?category=` while the script expected static category routes. This failure was unrelated to the RootMyTV page and was not used to expand TRA-38 into homepage/taxonomy repair.
- A first targeted browser harness embedded the Chinese expected title directly through a PowerShell pipeline and reported an equality mismatch even though the displayed strings looked identical. The corrected harness loaded expected bilingual strings from `data/project-page-visual.json`, avoiding command-pipeline encoding ambiguity.
- The final targeted browser run passed for English and Chinese at 1280 px and 390 px: exact title/meta/lead, visible hub and Homebrew links, reciprocal links, zero horizontal overflow, and zero console errors.
- `python -X utf8 scripts/build.py`, `python -X utf8 scripts/validate.py`, a second hash-compared deterministic rebuild, `git diff --check`, Python/JSON syntax checks, and skill quick validation passed.

## 三阶：可复用机制

- A rootability/exploit CTR page must answer the yes/no query immediately but derive eligibility from the upstream version matrix, not a guessed retail-model list. Model year, operating-system version, and vendor Software Version are separate fields; “older” remains uncertain rather than becoming “compatible.”
- Pair the exploit route with both the closest device-decision hub and the post-root application route, then lock forward and reciprocal edges in static validation so related-project ranking cannot silently remove the journey.
- Reused and extended `skills/hardware-revival-research/SKILL.md` with this patched-exploit/rootability pattern instead of creating an overlapping one-off skill.
