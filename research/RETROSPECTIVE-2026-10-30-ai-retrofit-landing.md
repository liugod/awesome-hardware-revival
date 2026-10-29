# AI retrofit landing retrospective

Date: 2026-10-30  
Scope: branch `liugod/kitagain-ai-retrofit-20261030` only; no Pages, deployment, or merge to `main`.

## Level 1 — Deliverable

The bilingual homepage now leads with a concrete job: search the exact old-device model and evaluate an AI retrofit route. The visual language comes from a repair bench rather than a generic AI product page, while the page retains the existing search form, category navigation, canonical/hreflang generation, and static architecture.

Route cards are generated from `data/catalog.json` through the existing localized data path. The displayed AI-function route count is computed from the catalog. The page does not claim local model execution, universal compatibility, known cost, or KitAgain hands-on reproduction.

Acceptance covered the deterministic build, repository validator, diff hygiene, directory browser checks, English desktop rendering, Chinese 390 px rendering, content order, and horizontal overflow. Production acceptance is intentionally out of scope because Pages and deployment were prohibited.

## Level 2 — Process and correction

The first build passed generation but failed the repository validator because the new, more specific search placeholder changed an existing homepage contract. The correct response was to retain the established placeholder and keep the more specific guidance in adjacent copy, rather than weakening or rewriting the validator.

The reconnect audit found a second missed contract: the longer hero subtitle wrapped at the validator's 1180 px and 390 px viewports. The fix shortened the task sentence and moved the two-column-to-one-column breakpoint to 1200 px. The unchanged browser test then passed in both languages and viewports. A prior summary had incorrectly reported this test as passing; explicit exit-code readback corrected that evidence gap before commit.

The implementation stayed inside the canonical generator plus homepage-scoped CSS. Generated pages were rebuilt instead of edited directly. Visual QA caught no reversed mobile order or overflow; the desktop and mobile compositions both kept the repair-chain illustration subordinate to the search task.

## Level 3 — Reusable mechanism

An evidence-bound AI retrofit landing should be assembled in this order: exact-model search, source-derived route examples, explicit evidence/unknown boundaries, stop conditions, then broader device navigation. Counts and route facts come from canonical data; freehand copy is limited to navigation and decision guidance.

This reusable pattern was added to `skills/hardware-revival-research/SKILL.md`. It also records the authorization boundary that branch work does not imply Pages, deployment, push, or merge permission.
