# TRA-35 bilingual device-hub retrospective

Date: 2026-11-07
Scope: Add English and Chinese `tv-box`, `router`, and `smart-plug` guide hubs with intent-focused metadata, visible and structured breadcrumbs, representative reciprocal links, homepage discovery, and sitemap coverage. Delivery stops at an open review PR; merging `main` and GitHub Pages deployment remain unauthorized.

## Level 1 — Deliverable quality

- Added three source-controlled guide records in `data/guides.json`. Each language has a distinct intent title, description, H1, introduction, decision sections, and at least six reviewed project or lead entries with device-plus-action anchors.
- Generated six localized canonical hub pages, plus the static-host bare-route fallbacks, from `scripts/site_i18n.py`. The localized hubs have one H1, visible breadcrumbs, matching `BreadcrumbList` JSON-LD, reciprocal hreflang, self-canonicals, no `noindex`, and sitemap entries.
- Added all three hubs to the English and Chinese homepage `Find by device / 按设备找` section without removing the five existing guide entries or the separate directory-category navigation.
- Added bilingual reciprocal links for TV box ↔ RootMyTV and HK1 Box, router ↔ Xiaomi AX9000, and smart plug ↔ OpenBeken and Sonoff S31. The hub lists point to the same representative records.
- Preserved the exact Chinese slogan `二手硬件再就业指南` in the canonical homepage and generated brand surfaces. Copy keeps exact-model, hardware-revision, recovery, mains-safety, and not-tested boundaries; no compatibility, certification, performance, or hands-on result was invented.
- Extended static validation and the existing Playwright contract for hub metadata, H1, breadcrumbs, cards, indexability, reciprocal links, homepage entry count, sitemap coverage, and 390 px overflow.

## Level 2 — Process failures and corrections

- PowerShell initially displayed the UTF-8 acceptance file as mojibake. The two supplied files were compared by SHA-256, and the readable Linear issue/comment plus explicit UTF-8 reads were used for semantic verification instead of treating console encoding damage as source text.
- The first full validator continued beyond the tool session's output window, so its final exit code was unavailable. It was rerun as one hidden process with stdout, stderr, and exit code captured in an isolated temporary directory; no partial or missing output was reported as a pass.
- An ad hoc HTML audit assumed a card class and backlink spelling that did not match the generator's actual output. The repository validator and exact generated routes remained authoritative; supplemental checks were corrected to the real `index.html` link shape rather than changing valid site URLs.
- TRA-34 was rechecked against `origin/main` before editing or PR work. The branch started exactly at merge commit `d629dc8f`, so the required mobile-overflow prerequisite was present rather than inferred from a related branch.
- `TRA-35-acceptance.md` was treated as a read-only handoff checklist and kept outside the implementation commit. No Greenway, trad.link, global user skill, merge, Pages, or production operation entered scope.

## Level 3 — Reusable mechanism

1. Resolve the exact device-hub matrix first: slug, user decision, source-backed entries, localized anchors, representative reciprocal targets, and minimum accepted count.
2. Put hub copy and membership in `data/guides.json`; keep page rendering, breadcrumb schema, homepage navigation, sitemap, bare-route fallbacks, and backlinks in `scripts/site_i18n.py`. Rebuild generated `docs/` rather than editing it directly.
3. Make title/meta/H1 answer the same decision without duplicating wording mechanically. Preserve evidence level and unknown-state boundaries inside the hub copy, especially for changing hardware revisions and mains-powered devices.
4. Generate visible breadcrumbs and `BreadcrumbList` from one trail. Validate the current canonical URL, localized labels, positions, and the homepage device-guide anchor together.
5. Assert both directions of every representative edge in both languages. A hub forward link is not enough when acceptance calls for a reciprocal route.
6. Keep homepage guide links and query-driven directory categories as separate contracts. Count and test both sets independently in static and browser checks.
7. Run the full build, static validator, deterministic rebuild check, link/browser contract, and 390 px overflow checks before commit. Treat local generation, open PR, CI, merge, Pages, public HTTP, indexing, and GSC movement as separate gates.

The reusable device-hub procedure is recorded in `skills/hardware-revival-research/SKILL.md`; user-global skills were not modified.
