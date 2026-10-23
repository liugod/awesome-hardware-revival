# Architecture

## Product

KitAgain is a bilingual, evidence-graded directory for reusing existing hardware. Canonical editorial facts live in `data/`; Python builders emit a static site into `docs/`; GitHub Pages serves `main:/docs` at `https://kitagain.com/`. The public model keeps 200 unique project repositories (53 reviewed, 147 E0 discoveries) separate from 347 device/community routes.

The public site has no backend, account system, analytics, database, runtime AI, or write API. JavaScript only filters and sorts HTML that is already present.

## Stack and data flow

1. Editors update canonical JSON and reviewed translations. `project-leads.json` is the E0 repository-discovery ledger; it is not merged into the reviewed catalog.
2. `scripts/build.py` compiles reports, exports, legacy pages, and invokes `scripts/site_i18n.py`.
3. `scripts/scoring.py` derives five-dimension revival-value stars, kept independent from E0–E3, and emits the unified JSON/CSV export.
4. `scripts/validate.py` checks schema, evidence invariants, translations, generated pages, internal links, exports, and public-file safety.
5. GitHub Actions repeats build and validation, then Pages publishes `docs/` from `main`.

## Trust boundaries

- Upstream project sites and repositories → editorial data: upstream text is evidence to review, not trusted compatibility or executable input.
- Canonical data → static generator: builders escape displayed text and allow only validated HTTP(S) source URLs.
- Repository → GitHub Actions/Pages: only commits accepted on `main` become public after CI and Pages deployment.
- Browser → external source links: visitors leave KitAgain when opening an upstream link; KitAgain does not proxy, authenticate, or modify that service.
- Browser filters → URL: query parameters affect only local display state and do not trigger a server write.

## Known risks and assumptions

- Revival stars compare feasibility/ease, expected cost, docs/community activity, practical value, and bricking/security risk. E0–E3 separately describes evidence depth and never enters or caps the stars (`scripts/scoring.py`). Unknown-neutral values are calculation placeholders, not verified average performance; all 147 metadata-only repository discoveries remain E0 and `needs_review: true`.
- Upstream compatibility, releases, licenses, and URLs can drift after the recorded check time (`data/catalog.json`, device and lead data).
- Generated files must stay synchronized with canonical inputs; CI detects drift in `docs/` and generated research reports (`.github/workflows/validate.yml`).
- GitHub Pages availability does not prove browser interactions, downloads, or hardware outcomes; those are separate acceptance gates (`research/VALIDATION.md`).
- No scheduled work exists, so there is no `cron.md`.
- No transactional or automated email exists, so there is no `emails.md`.
- No embedded agent, webhook, or runtime automation exists, so there is no `automation.md`.

## Related documents

- [flows.md](flows.md)
- [permissions.md](permissions.md)
- [variables.md](variables.md)
- [tests.md](tests.md)
- [seo.md](seo.md)
