# TRA-32 bare-route and site-utility retrospective

Date: 2026-11-06
Scope: Stop the existing unprefixed guide routes and `/privacy`, `/terms`, and `/contact` from returning 404 while preserving the generated-site source of truth, locked Chinese slogan, sitemap quality, and PR-only release boundary.

## Level 1 — Deliverable quality

- Added real English and Chinese privacy, terms, and contact pages through `scripts/site_i18n.py`. The copy stays short and explicit: no invented email, postal address, compatibility promise, safety certification, or third-party privacy guarantee; the verified contact route is GitHub Issues.
- Added generated 200 HTML redirect pages for `/privacy`, `/terms`, `/contact`, and every current English guide slug: `ai-retrofit`, `home-computers`, `kindle-displays`, `nest-mini-local-ai`, and `speaker-voice`. Each stub has `noindex,follow`, an English canonical, meta refresh, `location.replace`, query/fragment preservation, and a normal fallback link.
- Kept the thin redirect pages out of `sitemap.xml` while including all six canonical localized utility pages. Updated `url-mapping.json` and validation so generator output, redirect intent, and sitemap coverage cannot drift independently.
- Preserved the compact four-link footer and the exact locked slogan `二手硬件再就业指南`; the full validator's brand, footer, link, UTF-8, export, and sitemap contracts passed.
- Local HTTP acceptance covered the no-trailing-slash requests and final directory pages: all eight bare routes ended at HTTP 200, all six localized utility pages were real HTTP 200 pages, and all redirect targets were present in the 1,144-URL sitemap while the bare stubs were absent. The complete browser contract passed at desktop and 390 px.

## Level 2 — Process failures and corrections

- The first large patch encountered a context mismatch because the shared worktree changed after the initial clean-state check. Re-reading the diff instead of overwriting it preserved the in-scope implementation, then the missing mapping, sitemap, and redirect assertions were reviewed as one generated contract.
- A combined PowerShell preview-server wrapper was rejected by execution policy before starting a service. Starting one separately tracked loopback server session, running HTTP/browser checks against it, and stopping that exact session with Ctrl+C provided the same bounded acceptance without changing policy or leaving a process behind.
- The first full browser run reported the root mobile page with a Chinese footer while direct readback from the same server showed the generated root had an English footer and no redirect. A stability check plus one clean rerun passed the unchanged browser contract; the transient failure was not hidden or used to weaken the assertion.
- Serving `docs/<route>/index.html` means a bare no-slash request receives the static server's directory normalization before the 200 HTML landing page. Acceptance therefore checked both the requested no-slash URL's final HTTP 200 and the slash route's redirect metadata, rather than claiming an unavailable arbitrary HTTP 301 from GitHub Pages.
- Generated pages were rebuilt from the canonical Python source. No generated HTML was hand-edited, and PR, merge, Pages deployment, and public production acceptance remained separate gates.

## Level 3 — Reusable mechanism

1. Enumerate bare guide redirects from the same guide sources used to generate canonical locale pages; do not maintain a second handwritten slug list.
2. On GitHub Pages, use a 200 HTML landing page for arbitrary legacy routes: `noindex,follow`, canonical target, meta refresh, `location.replace`, preserved query/fragment, and an ordinary fallback link.
3. Generate the bare route through the same site shell when repository validators audit every HTML page. Mark it as a legacy output so it is written but not added to the canonical sitemap path list.
4. Add honest localized targets when the subject needs real content. Avoid inventing legal, privacy, ownership, or contact claims; identify third-party boundaries and only publish verified contact channels.
5. Lock the mapping in validation: every bare source file exists, every canonical target exists, redirect metadata and script match exactly, localized targets are real pages, and the sitemap includes targets but excludes thin stubs.
6. Test the no-trailing-slash request over a local static server, not only filesystem existence. Separately check the HTML redirect contract and run the repository's desktop/mobile browser suite.
7. Record local validation, commit, PR, Linear review state, merge, deployment, and public acceptance as distinct states. TRA-32 authorizes only the first four and explicitly forbids merge and Pages publication.

The reusable GitHub Pages redirect procedure was added to `skills/hardware-revival-research/SKILL.md`.
