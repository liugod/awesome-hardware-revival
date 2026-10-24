# Community drafts and GSC readiness retrospective

## Level 1 — Deliverable quality

Ten rated routes now have separate, Chinese-first community tutorial drafts with short English summaries, exact KitAgain detail links, direct upstream tutorial sources, stop conditions, and an explicit non-hands-on boundary. The drafts and the owner-facing Search Console checklist remain outside the build and Git index. The sitemap audit covered every one of the 1,116 listed URLs rather than relying on samples; XML structure, limits, live status, robots directives, noindex, canonical, and language alternates were checked independently.

## Level 2 — Process failure and correction

The existing HTML passed the repository validator because that validator required `x-default` to point to the site root on every page. A reciprocal hreflang audit exposed the hidden defect: 1,114 non-home localized pages declared the unrelated homepage as an alternate, while the homepage could not return-link to each detail-page cluster. The correction was to make each cluster's English page its fallback and to change the regression assertion from a global constant to equality with the English alternate. The draft workflow also made the ignore rule the first tracked change, so parallel authors could not accidentally stage unpublished content.

## Level 3 — Reusable mechanism

Treat unpublished writing and public release as separate ledgers. For each community draft, use the sequence audience → prerequisites → sourced steps → stop conditions → evidence boundary → short English summary, then verify source responses and prove both ignore status and absence from the Git index. For search readiness, combine an XML/schema check, an exhaustive redirect-disabled HTTP scan, page-level noindex and self-canonical checks, reciprocal hreflang graph validation, robots readback, deterministic rebuild, exact-commit CI/Pages confirmation, and a second exhaustive live scan after deployment.
