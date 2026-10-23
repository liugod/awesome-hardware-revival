# Permissions

## Roles

| Role | Source | Scope |
| --- | --- | --- |
| Anonymous visitor | Public web | Read pages and exports; run client-side filters; open external links |
| Contributor | GitHub/community account | Submit an issue or discussion under the destination platform's permissions |
| Repository maintainer | GitHub repository access | Review and merge canonical data/code; configure Pages subject to GitHub policy |
| GitHub Actions | Repository workflow token | Read checkout and run validation; the current validate workflow has `contents: read` |

## Resource matrix

| Resource | Visitor | Contributor | Maintainer | Actions |
| --- | --- | --- | --- | --- |
| Public HTML/JSON/CSV | Read | Read | Read | Read |
| Browser filter state | Local only | Local only | Local only | N/A |
| Issues/forms | Read | Create under GitHub rules | Triage/manage | N/A |
| Canonical `data/` | No write | No direct write | Git commit/merge | Read/validate |
| `main:/docs` deployment | No write | No write | Via authorized push/config | Pages deploy workflow |

There is no application database, row-level security, session, role claim, admin route, or client-side secret. Repository and community permissions are enforced by their external providers, not by KitAgain code.
