# Variables and secrets

| Name or setting | Used by | Scope | Source | Rotation | Risk |
| --- | --- | --- | --- | --- | --- |
| `base_url` | Builders, canonical links, sitemap | Public | `site.config.json` | Change with domain migration | Broken canonical/hreflang URLs if inconsistent |
| `repository_url` | Pages and contribution links | Public | `site.config.json` | Change with repository migration | Links point to wrong owner/repository |
| `community_url` | Navigation and contribution copy | Public | `site.config.json` | Change with community migration | Users reach wrong service |
| `version` | Assets, footer, exports | Public | `site.config.json` and versioned data | Bump for releases | Mixed generated versions if not synchronized |
| `KITAGAIN_PREVIEW` | Playwright acceptance scripts | Local/CI process | Optional environment variable | N/A | Testing the wrong origin if set incorrectly |
| GitHub CLI credentials | Optional read-only collection/publish operations | Workstation secret | External credential store | Provider policy | Repository/account compromise if exposed |
| `GITHUB_TOKEN` | GitHub Actions | CI secret | GitHub-provided | Per job | Workflow privilege; current validation needs read-only contents |

No secret is bundled in `docs/`, client JavaScript, source data, or the public export. `scripts/validate.py` scans public text for common credential and private-path patterns.

## Pre-release checklist

- Confirm all product/data versions match.
- Confirm five score weights total 100%, all totals use 0.5-star steps, evidence is independent, and exactly 147 project-source rows need review.
- Confirm no local credential, private key, token, machine path, or secret file is staged.
- Build and validate from canonical data.
- Review generated diff and public outbound URLs.
- Verify Actions, Pages, HTTPS files, browser interactions, and the exact deployed commit independently.
