# TRA-27 directory parameter SEO and GSC refresh retrospective

Date: 2026-11-05
Scope: Prevent bilingual directory search/category query states from becoming duplicate indexable pages, and replace the prior temporary KitAgain Search Console pull with a repeatable 7+7 repository workflow. Delivery stops at an open review PR; main merge and GitHub Pages deployment remain unauthorized and unperformed.

## Level 1 — Deliverable quality

- Added one generator-owned directory guard to every English and Chinese directory page. Requests containing `q` or `category` now render `noindex,follow` and replace the rendered canonical with the clean language directory root. Clean directory pages retain their generated self-canonical and no robots noindex, while real static pagination remains indexable.
- Kept the behavior narrow: the guard does not silently noindex the separately reviewed `ai`, evidence, or score facets. Existing cards, cross-page filtering, language alternates, sitemap routes, and public exports are unchanged.
- Added exact generator validation for both languages and every directory page. Targeted Playwright checks passed for clean, query, category, Chinese, English, and deep-page parameter URLs with zero page errors; the unchanged full directory browser contract also passed.
- Added `scripts/gsc_7d_compare.mjs` and `research/gsc/README.md`. The script reuses the existing `C:\work\.secrets\gsc-oauth-client.json` authorization and Codex/X79 proxy environment, calls `sites.list` before data pulls, requires the exact `sc-domain:kitagain.com` property, pages every API dimension, and never writes OAuth values or access tokens.
- Produced the sample snapshot `research/gsc/snapshots/2026-11-03-gsc-7d-vs-prev-7d.json`: current 2026-10-28 through 2026-11-03 versus previous 2026-10-21 through 2026-10-27. Each window contains seven date rows. The refresh observed 38 versus 39 clicks, 1,472 versus 1,461 impressions, and 2.58% versus 2.67% CTR; these are API observations, not evidence of deployment or an SEO outcome.
- Preserved the exact Chinese slogan `二手硬件再就业指南` in the generated h1, kicker, and header brand. The complete repository validator, Node syntax check, real GSC run, full Playwright directory contract, targeted metadata checks, secret-field scan, and `git diff --check` passed.
- Opened review-only PR #10: <https://github.com/liugod/awesome-hardware-revival/pull/10>. No main merge or GitHub Pages deployment was performed.

## Level 2 — Process failures and corrections

- The first broad repository search traversed generated assets and produced heavily truncated output. Narrowing subsequent searches to generator, validator, documentation, and exact GSC identifiers restored useful evidence without treating generated pages as source of truth.
- The first local preview launch used a background-process shape rejected by the execution policy. No files or external state changed. Running the HTTP server in a managed foreground session preserved deterministic cleanup and allowed the existing Playwright suite to run unchanged.
- The first targeted Chinese Playwright command piped literal Chinese through the Windows shell and turned the test literal into question marks. The page itself rendered the slogan correctly, but the comparison was invalid. Re-running with percent-encoded query text and Unicode escapes produced an encoding-independent pass.
- A first version of the GSC script made one request per dimension. Before committing, it was hardened to continue paging at the API row limit and to reject non-canonical or impossible ISO dates, preventing a future larger property from being silently truncated.
- Static canonical assertions alone would not prove query-dependent behavior because GitHub Pages serves the same file for every query string. The release gate therefore checks both generated source invariants and the final rendered DOM after the inline guard executes.

## Level 3 — Reusable mechanism

1. For static filter URLs, retain indexable clean pages and real pagination, but add `noindex,follow` only for the intended duplicate query states and canonicalize their rendered DOM to the clean language root.
2. Put parameter SEO in the canonical generator, not in hand-edited generated HTML. Validate every localized and paginated output, then test the DOM for a clean URL, each governed parameter, a localized URL, and a deep page.
3. Treat a GSC refresh as a credential-safe evidence pipeline: use an already-authorized local file, inherit the established proxy, list properties first, require the exact property, and never serialize tokens.
4. Compare adjacent inclusive windows with identical dimensions and an explicit reporting lag. Derive headline totals from date rows, because anonymized queries may be absent from query reports; store raw reports, window boundaries, lag, row limit, permission, totals, and deltas together.
5. Make API pagination and strict date validation part of the first durable version. A successful small sample does not prove a single-page implementation remains complete as traffic grows.
6. Keep implementation, API snapshot, PR, merge, Pages deployment, Google recrawl, indexing, and traffic effect as separate states. TRA-27 has reached open PR and local/API acceptance only.

The reusable directory-parameter and Search Console 7+7 procedures were added to the repository-local `skills/hardware-revival-research/SKILL.md`; user-scoped skills were not modified.
