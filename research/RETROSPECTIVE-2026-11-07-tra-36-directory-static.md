# TRA-36 static category-directory retrospective

Date: 2026-11-07
Scope: Generate indexable English and Chinese static category directories under `/en|zh/directory/<category>/`, include their pagination in the sitemap, preserve query-state noindex behavior, and connect homepage and detail breadcrumbs to clean category URLs. Delivery stops at an open review PR; merge and Pages deployment remain unauthorized.

## Level 1 — Deliverable quality

- Added one explicit public taxonomy allowlist in the canonical bilingual generator: `audio`, `camera`, `computer`, `ereader`, `gaming`, `mobile`, `network`, `peripheral`, `smarthome`, `speaker`, and `tv`.
- Generated every non-empty category in both languages, including category-local pagination where needed. Each clean page has one H1, a self-canonical, reciprocal hreflang, no noindex directive, category-pure cards, and sitemap coverage.
- Reused the global directory's rated-first ordering, card component, evidence markers, images, and filter shell. Card and asset paths are calculated from the generated page depth rather than corrected afterward with string replacement.
- Changed the homepage's six category entries and valid project, project-lead, and atlas-lead breadcrumbs to clean static category URLs. Unsupported internal labels remain readable but fall back to the clean directory root instead of creating an unapproved taxonomy route or a broken link.
- Preserved query pages as non-index targets. A recognized `?category=` on the language directory root receives `noindex,follow` and the matching static-category canonical; `?q=` or unsupported category values canonicalize to the clean directory root; filters on a static category page canonicalize to that category root.
- Extended static and browser contracts for the exact category set, non-empty/pure cards, pagination, sitemap membership, homepage links, parameter SEO, clean category navigation, detail breadcrumbs, HTTP 200, desktop behavior, console errors, and 390 px overflow.
- Browser evidence confirmed English and Chinese `network`, `tv`, `ereader`, `smarthome`, and `speaker` routes returned 200 with non-empty lists; the observed first-page card counts were 53, 56, 28, 60, and 8 respectively in each language.

## Level 2 — Process failures and corrections

- Before material work, the execution contract was read back with the exact scope, acceptance criteria, branch-name exception, and explicit no-merge/no-deploy/no-external-send gates. A transient GitHub GraphQL EOF required one state-update retry, so the final state was independently read back instead of inferred from the failed request.
- The first static validator failure exposed a generated scoring-link regression from `../about/` to `../about/index.html`. The generator was corrected to keep the existing clean directory URL, then the complete validator was rerun instead of weakening the assertion.
- The default preview port already had an older Python server. A second server could bind on Windows, so the first browser attempts read stale pages even though the current generated files were correct. The task-owned preview session was stopped without touching the pre-existing process; acceptance was rerun on a verified free port with `KITAGAIN_PREVIEW` set explicitly.
- The browser contract first checked homepage category links using assumptions that could not distinguish the stale server. Diagnostics were added to report the actual source hrefs, then the final assertion was kept on resolved clean paths and the approved six slugs.
- The structured breadcrumb URL was already clean, but the visible link still ended in `index.html`. Browser acceptance caught the mismatch; the generator now removes the suffix so visible and JSON-LD trails agree.
- Full static validation was allowed to finish in the same process on every long run. No second validator was started while the first audited more than a thousand generated pages.

## Level 3 — Reusable mechanism

1. Freeze a public category allowlist independently from internal data labels. Count listed records first, skip empty categories, and fall unsupported categories back to the clean directory rather than inventing routes.
2. Build global and category pages from one sorted typed-record collection. Render each card using the current output path so content and asset prefixes are correct at every pagination depth.
3. Give each page set its own page count and fetch root. A fixed route category is page state, not a filter; only search, score, evidence, AI, or a different category selection should trigger cross-page behavior.
4. Make category selection navigate to clean static routes. Keep legacy parameter states readable but `noindex,follow`, with recognized category canonicals mapped to the static target and query-only states mapped to the appropriate clean root.
5. Generate homepage category links, visible breadcrumbs, BreadcrumbList URLs, category pages, and sitemap URLs from the same route contract. Validate unsupported categories separately so link health never depends on accidental data labels.
6. Lock exact category-set, non-empty, purity, pagination, canonical, hreflang, sitemap, and internal-link assertions in the repository validator. Render-test the five acceptance categories in both languages, the legacy parameter DOM metadata, at least one project and atlas lead breadcrumb, category navigation, and 390 px overflow.
7. Bind browser acceptance to a verified free preview port and explicit base URL. A listening default port is not evidence that it serves the current worktree.
8. Treat local build, static validation, browser acceptance, commit, push, PR, CI, merge, Pages, and indexing as separate states.

The reusable static-taxonomy procedure is recorded in `skills/hardware-revival-research/SKILL.md`; no user-global skill or external system was modified.
