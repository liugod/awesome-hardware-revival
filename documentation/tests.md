# Verification map

## Existing coverage

| Use case | Rule and expected behavior | Evidence | Status / gate |
| --- | --- | --- | --- |
| Canonical catalog | Schema, unique IDs, evidence invariants, unknown costs, translations | `scripts/validate.py`, `data/catalog.schema.json` | Existing; CI-required |
| Full directory export | Every public entry has one evidence-capped score; JSON/CSV IDs and facts match | `scripts/scoring.py`, `scripts/validate.py` | Existing; CI-required |
| 200 project sources | 53 reviewed + 147 repository-unique E0 sources; no URL collision; E0 score stays 1; project-source JSON/CSV and pages match | `scripts/import_project_leads.py`, `scripts/validate.py` | Existing; CI-required |
| Static routes | One H1/canonical, reciprocal language links, internal links and anchors resolve | `scripts/validate.py` | Existing; CI-required |
| Hardware search | Model tags restore URL queries and return expected cards | `scripts/verify_hardware_tags.mjs` | Existing; guarded local/public browser check |
| Score directory | Search, evidence/kind/score filters, URL state, empty state, 200-source index, E0 detail, mobile overflow | `scripts/verify_directory_scores.mjs` | Existing; guarded local/public browser check |
| Public-file safety | No common token/private-key/private-machine-path pattern or replacement character | `scripts/validate.py` | Existing; CI-required |
| Deterministic build | Generated `docs/` and research files have no post-build diff | `.github/workflows/validate.yml` | Existing; CI-required |

## Proposed tests

| Test type | Case | Expected behavior |
| --- | --- | --- |
| Automated integration | Run browser acceptance in CI with a pinned Playwright version | Same filtering, sorting, URL, and mobile assertions on each pull request |
| Guarded live | Compare deployed JSON/CSV/HTML hashes with the exact `main` commit | Byte-identical release artifacts after Pages completes |
| Guarded live | Sample outbound sources with GET fallback and status classification | Redirects and access restrictions recorded without treating 403/429 as missing |
| Manual review | Keyboard-only and screen-reader pass for filters and score explanations | Logical focus, named controls, live result counts, no score-only meaning |
| Manual review | Exact-device safety/editorial review | No E1/E2/E3 upgrade without the required source scope and stop condition |

## Gaps

| Gap | Exposure | Priority |
| --- | --- | --- |
| Browser scripts are not currently CI-required | A JavaScript interaction regression could merge while static validation stays green | High |
| External URLs are not exhaustively checked on every release | A source may move or become restricted after editorial review | Medium |
| No physical hardware acceptance | Compatibility, recovery, power, and long-term stability remain unverified | Explicit product boundary |
| No automated visual-diff baseline | Layout regressions may require manual/browser inspection | Medium |
