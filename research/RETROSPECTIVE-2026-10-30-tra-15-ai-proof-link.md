# TRA-15 homepage AI proof-link retrospective

## Level 1: deliverable quality

- The generated AI-route count is now a link to the canonical `?ai=native` directory facet in both languages.
- The English public root correctly rewrites the target to `en/directory/?ai=native`; the localized English and Chinese roots retain their directory-relative targets.
- The deterministic rebuild changed only the generator and the three intended root indexes. No `q=AI` or Greenway reference was introduced.

## Level 2: process corrections

- Treating the count and the nearby “Browse every AI-related route” action as one semantic promise avoided creating a second search behavior.
- Diffing immediately after the full rebuild confirmed that the broad generator did not cause unrelated artifact churn.
- The browser-backed score verifier requires a local server on port 4185; a connection refusal is an environment precondition, not a content failure.

## Level 3: reusable mechanism

- Generated summary metrics that name a canonical class should link to the same structured facet as the corresponding call to action.
- Verify source markup, localized generated pages, and public-root path rewriting separately because their relative URLs differ.
- The repository skill already records the `?ai=native` versus keyword-query rule, so this follow-up adds no duplicate skill guidance.

This branch-only follow-up does not authorize push, merge, deployment, or public-site mutation.
