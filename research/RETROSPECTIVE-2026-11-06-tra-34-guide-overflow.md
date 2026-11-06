# TRA-34 guide project-card overflow retrospective

Date: 2026-11-06
Scope: Remove the 390 px horizontal overflow from bilingual guide project cards without changing TRA-30 links, marketing copy, or the locked Chinese slogan. Delivery stops at an open review PR; main merge and GitHub Pages deployment remain unauthorized.

## Level 1 — Deliverable quality

- Reproduced `/en/guides/speaker-voice/` at 390×844 before editing: `innerWidth=390`, `scrollWidth=396`, the first card spanned x=16..374 with 0 px horizontal padding, and its thumbnail spanned x=-6..396 because both inline margins were -22 px.
- Scoped the mobile rule to `.prose .project-thumb` and changed the thumbnail margins to 0. After the change, the same route measured `innerWidth=scrollWidth=390`; card and thumbnail both span x=16..374.
- Audited all guide routes that use this project-card pattern: speaker/voice, Kindle/displays, and home/computers in both English and Chinese. All six measured 390 px document width at a 390×844 viewport, with thumbnail bounds inside x=16..374.
- Rebuilt the generated site and passed `python -X utf8 scripts/validate.py`, including 35,475 generated internal references plus schema, CSV/JSON parity, public-file, and catalog-evidence checks.
- Confirmed the only product change is `docs/assets/style.css`; generated guide HTML, `scripts/site_i18n.py`, TRA-30 link content, and the exact slogan `二手硬件再就业指南` are unchanged.

## Level 2 — Process failures and corrections

- A broad first CSS search included generated one-line HTML and produced truncated output. Narrowing inspection to exact stylesheet selectors and the mobile rule exposed the active cascade without mixing in card content.
- The first attempt to start a background preview with `Start-Process` was rejected by the execution policy. Running the local HTTP server in a managed terminal session kept the process visible, controllable, and easy to stop.
- The first multi-route Playwright command supplied statements where `run-code` expects a function. Wrapping the audit in `async (page) => { ... }` produced one deterministic six-route report.
- Lazy thumbnail images initially appeared unloaded because the audit did not scroll them into view. Scrolling the first card and awaiting `img.decode()` separated image-loading timing from the actual width contract.
- The full validator exceeded the 30-second command-yield window. Keeping the same session and polling it to the final exit code avoided treating a still-running check as a pass or failure.
- Task-specific untracked validation files appeared and changed during execution outside this patch. They were not staged or attributed to this implementation; tracked generated screenshot drift was restored from a worktree whose blob matched `HEAD`.

## Level 3 — Reusable mechanism

1. Measure the document, card, and overflowing child together at the exact failing viewport. Record `innerWidth`, `scrollWidth`, element bounds, card padding, and child margins before changing CSS.
2. Read the active cascade after all later stylesheet rules. A legacy negative margin that once matched card padding becomes an overflow source when a later redesign removes that padding.
3. Scope the correction to the affected content surface. For guide cards, `.prose .project-thumb` avoids changing directory cards or unrelated media while preserving the shared thumbnail component.
4. Re-run the exact failing route, then enumerate every bilingual page using the same rendered pattern. Require both document equality (`scrollWidth === innerWidth`) and child bounds within the viewport.
5. Keep layout repair separate from copy, SEO, and link-graph work. Verify protected source and generated surfaces have no diff before handoff.
6. Treat local browser acceptance, repository validation, PR/CI, merge, Pages deployment, and public acceptance as separate gates.

The reusable narrow-screen guide-card overflow procedure was added to `skills/hardware-revival-research/SKILL.md`.
