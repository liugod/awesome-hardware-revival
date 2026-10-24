# Load-bearing flows

## Build and publish

- Actor: repository maintainer with permission to push `main`.
- Preconditions: canonical data and translations pass local validation; no credential is stored in the repository.
- Sequence: edit data → build static files → validate → review diff → commit/push → GitHub Actions validates → Pages deploys → independent HTTPS and browser readback.
- Authorization: GitHub controls repository writes and Pages configuration. Anonymous visitors have read-only access. The deny case is a contributor without repository write permission, whose push cannot update `main` or Pages.
- Side effects: Git commit, Actions runs, and replacement of the public static deployment.
- Trust crossings: workstation → GitHub; repository → Actions; Actions/Pages → public browser.

## Search, filter, sort, and share

- Actor: anonymous visitor.
- Preconditions: generated HTML, `assets/app.js`, and the route data attributes are available.
- Sequence: controls read card attributes → unmatched cards are hidden → cards may be reordered → selected state is written to the current URL with `history.replaceState` → optional clipboard copy.
- Authorization and writes: none. No server request carries filter state; no account or persistent server state exists.
- Deny/failure case: clipboard permission failure produces copy-the-address-bar guidance; disabled JavaScript leaves all content readable.

## Data download

- Actor: anonymous visitor.
- Sequence: visitor opens or downloads versioned static JSON/CSV generated from the same canonical records as the pages.
- Integrity rule: unified JSON/CSV IDs, five nullable raw scores, evidenced-dimension count, proportional effective weights, nullable weighted/rounded totals, per-dimension sources, independent evidence grades, review-needed state, display status, URLs, and entry counts must match in `scripts/validate.py`. Fewer than three evidenced dimensions must have no total. The separate project-source JSON/CSV preserves all 147 discovery rows and their audit outcomes (122 E0, 18 E1, 7 E2; 118 still review-needed); the site lists 143 of those alongside 53 reviewed repositories, while four rejected routes remain download-only.
- Side effects: client-side download only.

## Contribution and correction

- Actor: GitHub or community user.
- Sequence: KitAgain links to a GitHub issue form or community discussion; maintainers separately review exact model, source, failure, and recovery evidence before editing canonical data.
- Authorization: a public submission is not permission to change the directory and never upgrades evidence automatically.
- Trust crossing: KitAgain → GitHub/community; submitted text → maintainer review → repository.
