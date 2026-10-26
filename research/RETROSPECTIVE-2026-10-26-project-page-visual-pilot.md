# Project-page visual pilot retrospective

## Level 1 — Deliverable quality

OpenBeken, Onju Voice v2, and OpenWrt now use a bilingual, data-driven project-detail pilot with a two-column desktop hero, a single-column mobile layout, purpose copy, five status chips, a three-card decision snapshot, spec grids, risk emphasis, and an image or source-aware placeholder. The build changes only the six canonical pilot pages plus shared CSS and source/render logic. OpenBeken's finalized English title, description, canonical, hreflang, Open Graph title/description, and glance block remain byte-identical to `HEAD`; the hero image is never lazy-loaded, and the stylesheet query advances to `1.20.1` only on pilot pages.

## Level 2 — Process failure and correction

The inherited uncommitted renderer initially applied the new structure to every reviewed project and introduced new component names instead of the brief's existing classes. It also omitted the validator-required evidence-method link. The first mobile render placed the hero image before the project name, pushing purpose and chips below the useful first viewport on image-heavy pages. The correction was to gate canonical pilot pages by source-data IDs, restore the legacy renderer byte-for-byte for all other and historical pages, reuse `project-purpose`, `reader-snapshot`, `detail-score`, `spec-grid`, `lead-verdict`, `project-media`, `hardware-tags`, `detail-links`, and `resource-list`, restore the evidence link, and keep mobile copy before media.

## Level 3 — Reusable mechanism

Future generated-page pilots should use four independent gates: source-data scope, protected-content equality, generated-diff scope, and rendered acceptance. Store pilot IDs and exact overrides in tracked data; run the full generator; reject any non-pilot HTML drift; compare protected metadata and editorial fragments directly with `HEAD`; then test every pilot language at desktop and mobile widths for layout order, chip wrapping, horizontal overflow, image loading policy, and browser warnings. A global validator remains necessary because visual success does not prove repository contracts or export/link integrity.
