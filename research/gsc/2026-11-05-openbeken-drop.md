# OpenBeken search drop diagnosis — 2026-11-05

Source: `research/gsc/snapshots/2026-11-03-gsc-7d-vs-prev-7d.json`, comparing 2026-10-28..2026-11-03 with 2026-10-21..2026-10-27. The snapshot stores up to 25,000 rows for each dimension. Query and query+page rows can still omit anonymized searches, so they are not used to reconstruct missing click counts.

## What changed

- The English OpenBeken page moved from 6 clicks / 106 impressions / 5.66% CTR / average position 3.29 to 0 clicks / 12 impressions / 0% CTR / average position 9.75.
- The page did not disappear from the full raw page report. It only fell outside the shorter top-page view used in the planning summary.
- Visible query+page rows are too sparse to identify one lost query: the prior window exposes eight impressions across seven queries and the current window exposes four impressions across `open beken` and `openbeken`. The page totals are higher because Search Console withholds some query detail.
- The current English title, `OpenBeken Guide: BK7231 Tuya to Local MQTT | KitAgain`, was merged on 2026-11-05, after the latest GSC date in this comparison. This snapshot cannot measure that title or establish that it caused the drop.

## Technical and intent check

- URL remains `https://kitagain.com/en/projects/openbeken/`; there is no duplicate or newly created OpenBeken route.
- The generated page has one self-canonical, reciprocal EN/ZH hreflang, no page-level `noindex`, and the site robots file allows crawling and points to the sitemap.
- TRA-29/30 navigation is present: Home → Smart home → OpenBeken breadcrumb, BK7231T/BK7231N directory links, the AI retrofit hub link, and four related local-control projects.
- The current English title and opening lead already cover the observed/high-value intent cluster: OpenBeken, BK7231, Tuya, local MQTT, Home Assistant, exact board matching, backup, and recovery. There is no evidence for another English-title rewrite before the post-deployment window is observed.

## Likely cause and fix in TRA-31

The observed loss is most consistent with a short-window visibility/ranking contraction: impressions fell 89% and average position weakened by about 6.46 positions. The available data does not prove a canonical, robots, route, or internal-link fault, and it does not expose enough query detail to attribute the change to one keyword. Demand volatility, query mix, indexing volatility, and competition remain possible; none is claimed as confirmed.

TRA-31 therefore keeps the already intent-aligned English title and lead, adds an equally specific Chinese title/meta/lead for BK7231 Tuya → local MQTT/Home Assistant intent, and retains the existing AI-retrofit hub instead of inventing a new smart-plug section. The same PR also tightens the six second-batch pages identified by the weekly GSC review.

## Two-week CTR reminder

Recheck the same canonical page two weeks after this PR is later merged, deployed, and recrawled. If deployment occurs on 2026-11-05, use a window ending no earlier than 2026-11-19; otherwise shift the comparison forward. Compare clicks, impressions, CTR, average position, indexed canonical, and the visible query+page mix. Do not treat PR creation or green CI as indexing or traffic recovery.
