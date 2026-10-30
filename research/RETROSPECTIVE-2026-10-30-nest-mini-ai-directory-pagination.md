# Nest Mini local AI and directory pagination retrospective

Date: 2026-10-30
Scope: branch `liugod/kitagain-ai-retrofit-20261030`; PR only, with no Pages deployment or merge.

## Level 1 — Deliverable

The bilingual AI-retrofit hub now separates reviewed routes with identified upstream repositories from GitHub-index-only leads that still require exact-model, installation, and recovery review. The homepage topic strip links to that hub, and the hub links to a bilingual Nest Mini decision guide.

The Nest Mini guide answers the decision before presenting instructions: Onju is a second-generation Nest Mini board replacement, not an OEM-firmware jailbreak; the ESP32-S3 is an audio/control endpoint, not an on-chip LLM host; and the real choices are the Onju v2 conversation/agent pipeline, an ESPHome-to-Home Assistant Assist satellite, or stopping. It preserves unknown cost and performance, names the shared-I2S limitation, and records that KitAgain has not performed a hands-on build.

The 543 displayed directory records are split into ten indexable pages per language, each with its own canonical, hreflang cluster, pagination navigation, and sitemap entry. Search and filters remain global: they fetch the other static pages only when a filter is active, retain URL state, and normalize imported card links against the page they came from.

## Level 2 — Process and corrections

The first static validation correctly rejected the change because the existing page-count and complete-card audit assumed one giant directory page. The validator was updated to assert aggregate coverage across every generated page rather than weakening the card contract.

The second validation exposed incorrect relative links on deep pagination pages. The generator now emits page-depth-correct card links. Browser testing then found a second link-context problem: cards fetched from another page retained source-relative URLs when imported into the current document. The client now resolves every imported card link against its source page before inserting it.

The existing browser acceptance initially raced the new asynchronous cross-page loading and also kept an `AI` query active while testing evidence filters. The checks now wait for observable result counts, clear intersecting filters, and distinguish the 60-card unfiltered page from the 543-card global filtered dataset. This preserved the old search/filter behavior while proving the new pagination behavior.

## Level 3 — Reusable mechanism

For evidence-bound decision content, lead with architecture and stop conditions: identify the exact hardware generation, distinguish software bridging from firmware replacement and board replacement, show where compute actually runs, then compare build, ecosystem, and stop routes. Repository wording such as “jailbreak” must not override the documented physical architecture.

For a static directory that still needs global filtering, keep initial HTML genuinely paginated for indexability and payload size. Load remaining static pages only after a non-empty filter is applied, import their cards, resolve links against each source page, and hide pagination while presenting the global result set. Validate aggregate uniqueness and coverage statically, then test asynchronous URL state, reloads, deep-page search, link targets, and narrow-screen overflow in a real browser.

These mechanisms were added to `skills/hardware-revival-research/SKILL.md` for future KitAgain work.
