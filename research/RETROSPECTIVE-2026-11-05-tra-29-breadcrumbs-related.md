# TRA-29 breadcrumb and related-project navigation retrospective

Date: 2026-11-05
Scope: Add visible breadcrumbs, matching schema.org `BreadcrumbList` JSON-LD, and build-time related projects to every bilingual reviewed-project, repository project-lead, and device/community lead detail page. Delivery stops at open review PR #11; merging `main` and GitHub Pages deployment remain unauthorized and unperformed.

## Level 1 — Deliverable quality

- Added one generator-owned three-item trail to all requested detail templates: language home, the existing device guide hub when one accurately maps to the category (speaker, computer, or e-reader), otherwise the localized directory category, then the current canonical page.
- Generated the visible breadcrumb and JSON-LD from the same inputs. Every structured item carries an explicit position, localized name, and canonical absolute URL; the visible category link resolves to the same target.
- Added four related projects per page. Selection is computed during the build from an exact category match, a bounded technology vocabulary, shared device/hardware terms, and same-family priority. The current record is excluded, only generated bilingual project or listed project-lead targets are eligible, and localized anchors describe the action/device rather than exposing a bare slug.
- Applied the shared mechanism to 53 reviewed projects, 143 listed project-leads, and 347 device/community leads in both languages, plus the 53 generated historical project compatibility URLs. The change regenerated 1,139 detail HTML files without changing homepage or directory templates.
- Extended repository validation to parse every `BreadcrumbList`, require exactly one visible trail and related block, enforce four unique related links, resolve every target locally, and compare English/Chinese target sets. The complete build and validator passed; a second build produced the identical docs diff hash `6def8924743287df9e5f9fabc177dceaebe4a21b`.
- Preserved the exact locked Chinese slogan `二手硬件再就业指南`; the slogan had no diff. `git diff --check` passed.
- Opened review-only PR #11: <https://github.com/liugod/awesome-hardware-revival/pull/11>. Linear TRA-29 contains one completion comment with the PR URL and is in `In Review`. No main merge or Pages deployment was performed.

## Level 2 — Process failures and corrections

- The initial broad file and memory read produced heavily truncated output. Subsequent inspection was narrowed to the canonical generator, validator, exact template ranges, and the relevant memory registry lines.
- The task text used both “project-lead” and an “atlas lead” acceptance sample. Repository inspection showed these are distinct generated routes (`project-leads/` and `leads/atlas-*`), so the implementation was expanded within the stated project/lead-template scope to cover both instead of guessing that one name represented both kinds.
- The first related-project tie-break used localized anchor text, which produced different fourth choices in English and Chinese. It was replaced with a language-neutral kind-and-ID tie-break, and full-site validation now rejects any bilingual target-set divergence.
- The first browser-render attempt reached the local preview but the computer-use browser host returned `browser access host is unavailable`. No screenshot, console, or visual-overflow result was fabricated. Static generation, parsed HTML/JSON-LD, link resolution, deterministic rebuild, and CI are separate gates; browser-render acceptance remains unexecuted locally.
- A PR attachment appeared automatically in Linear after PR creation. The completion flow read back the ticket first, avoided creating a duplicate attachment, posted exactly one short completion comment, and moved only from the existing started state to the deterministic review state.

## Level 3 — Reusable mechanism

1. Treat “project,” “repository project-lead,” and “device/community lead” as separate route families until the generator proves otherwise; acceptance samples can reveal a broader intended template surface than one shorthand noun.
2. Generate the visible breadcrumb and `BreadcrumbList` from one canonical trail object. Link to an existing accurate guide hub only when it exists; otherwise use the real directory category rather than inventing a static category page.
3. Build related links only from candidates with generated pages in every required language. Score explicit category, hardware/device tokens, and a bounded technology vocabulary; use a language-neutral deterministic tie-break and action/device anchor text.
4. Validate semantics across the entire generated surface: JSON-LD type and positions, localized labels, canonical URLs, visible trail, related-item count, duplicate exclusion, local target existence, same-language targets, and bilingual selection symmetry.
5. Keep local static acceptance, browser rendering, PR review, CI, merge, Pages deployment, public structured-data testing, and SEO impact as distinct states. A blocked browser-control layer does not invalidate static evidence, but it also cannot be reported as visual acceptance.

The reusable generator and validation procedure was added to the repository-local `skills/hardware-revival-research/SKILL.md`; user-scoped skills were not modified.
