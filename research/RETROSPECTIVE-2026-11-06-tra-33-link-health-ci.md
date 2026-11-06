# TRA-33 internal-link health CI retrospective

Date: 2026-11-06
Scope: generated `docs/` link validation and inbound reporting on branch `liugod/tra-33-kitagain-link-ci`; PR and CI only, with no merge or Pages deployment.

## Level 1 — Deliverable quality

- Extended the existing generated-site validator rather than adding a second CI path. The current pull-request workflow already rebuilds `docs/` and runs `python -X utf8 scripts/validate.py`, so the new gate is active without workflow duplication.
- Normalized relative, root-relative, protocol-relative, and same-origin absolute references. Missing targets, paths escaping `docs/`, and missing HTML fragments are accumulated into a clear source-to-target error list and fail with a non-zero exit.
- Counted inbound navigation from `<a href>` only and deduplicated repeated links from the same source page. The `<3` report is sorted by count and route and remains informational.
- Limited the report to indexable content surfaces: localized projects, project leads, discovery leads, guides, articles, directory pages, project-source/research/scoring hubs, and the home routes. Pure utility pages are not treated as content-orphan candidates.
- Excluded TRA-32 `noindex` bare-route redirect stubs from both report targets and inbound-source counts. Their canonical targets and redirect metadata remain covered by the existing hard assertions.
- Preserved the locked Chinese slogan and all sitemap, i18n, redirect, export, and generated-page contracts.

## Level 2 — Process failures and corrections

- The old validator already checked many relative references, but it skipped same-origin absolute URLs because every URL with a scheme was treated as external. Centralizing URL resolution closed that gap without changing external-link behavior.
- Reusing the parser's generic reference list for inbound counts would have counted canonical, hreflang, stylesheet, script, image, and form references as navigation. A separate anchor list keeps inbound counts meaningful.
- Raw link totals can be inflated by repeated cards or multiple links within one page. Storing a set of referring pages makes the reported number an inbound-page count rather than a markup-occurrence count.
- Redirect fallback links would otherwise add artificial inbound credit to canonical English targets. Skipping redirect stubs as referring pages keeps the report focused on real discovery paths while the redirect validator still requires each target to exist.
- A temporary deliberate missing target was introduced only in generated output, produced one actionable broken-link record and exit code 1, and was removed before the final clean build.

## Level 3 — Reusable mechanism

1. Build first, then validate the complete generated tree; source-template inspection alone cannot prove emitted routes resolve.
2. Use one resolver for all generated references and one narrower navigation stream for inbound analysis.
3. Treat distinct referring pages as the inbound unit, exclude self-links, and sort low-inbound results by count then route.
4. Separate hard correctness from editorial triage: missing targets and fragments fail; low inbound counts report unless policy explicitly says otherwise.
5. Model intentional redirect stubs explicitly. Exclude them from orphan analytics, but never exempt their canonical targets, fallback links, or redirect metadata from validation.
6. Exercise both sides of the gate before delivery: normal tree passes, a temporary bad link fails, restored tree passes again.

This mechanism is recorded in `skills/hardware-revival-research/SKILL.md` under generated-site internal-link health.

## Validation evidence

- `python -X utf8 scripts/build.py` — rebuilt the complete generated site.
- `python -X utf8 scripts/validate.py` — normal tree passed after checking 35,475 generated internal references and reported 10 content pages below three distinct inbound sources.
- Deliberate broken-link proof — `/en/` to a temporary missing target produced one explicit error and exit code 1.
- Final clean validation, generated diff check, and GitHub Actions result are recorded in the PR.
