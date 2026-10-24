# Bilingual content and deployment

## One source of facts

`data/catalog.json` is the shared source. `data/i18n/en.json` translates editorial text by project ID. Its SHA-256 is calculated over the full Chinese project record using sorted JSON keys, compact separators and UTF-8. Any source change blocks the build until the corresponding translation is reviewed. Do not blindly refresh the hash.

`data/deep-dives.json` and `data/i18n/deep-dives.en.json` contain the 12 complete analyses. `data/i18n/revisions.json` records both hashes and the review scope. Compare models, firmware, numerical claims, exclusions, costs and recovery conditions before recording a new review. Translation review never changes `checked_at` or upgrades hardware evidence.

`data/guides.json` pairs both languages for the three topic guides. Edit both versions together, retain source-project links and do not introduce unsupported compatibility claims.

The site uses stable use-case IDs. Older shared URLs with Chinese use labels are accepted and mapped to those IDs. Project IDs, category IDs, evidence levels and source URLs remain shared. English JSON/CSV is generated, not manually maintained.

## Build and acceptance

Run `python -X utf8 scripts/build.py` and `python -X utf8 scripts/validate.py`. Validation checks schema, 53 reviewed IDs in both languages, all 547 directory rows, shared facts, JSON/CSV parity, 1,179 HTML pages, language links, canonicals, internal links, historical mappings, 1,124 sitemap URLs, English text fallbacks, and public-file hygiene.

Also verify the rendered UI: the single-search homepage and category links; compact four-field cards; default star-desc order; the directory's category, score and evidence filters; no-results and reload behavior; matching-page language switches; record-detail bullets and About links. Confirm the directory has no visible entry-type or sort control, and that its scoring info icon reaches About. Check desktop plus a 390 px viewport for horizontal overflow and first-card visibility. Hardware acceptance lists remain proposed, unexecuted tests.

## Custom domain maintenance

GitHub Pages serves `main:/docs` at `https://kitagain.com/` with HTTPS. Treat the repository Pages settings, DNS, canonical URLs, and the `CNAME` file as one release surface.

1. Preserve the current release and the historical mappings in `docs/data/url-mapping.json`.
2. Change the custom domain only with repository-owner approval; update `site.config.json`, `CNAME`, and public documentation together.
3. Rebuild, then verify DNS, TLS, Pages status, canonical/hreflang, sitemap URLs, and actual browser behavior.
4. Verify representative historical project routes plus the public JSON/CSV. A static HTML canonical, meta refresh, or JavaScript navigation is not an HTTP 301.
5. Confirm indexed URLs separately when search-console access is available.

The old `/projects/{id}.html` files remain complete Chinese pages with canonical links to `/zh/projects/{id}/`; they do not force a redirect. The root is the simplified English search landing, `/en/` retains the matching English copy, and `/zh/` is the Chinese landing.

## Forum boundary

The independent forum is online, while its language interface, categories, moderation, and posting workflows continue to mature. The main catalog remains readable without registration, and GitHub issue forms remain the formal submission and correction channel.

Keep `community_url` changes separate from main-site releases. Do not claim registration, posting, moderation, email, backup restoration, or SSO readiness without independent tests. Never create fictitious user activity or reproduction reports.

## Measurement

No analytics backend, search-console property or user tracking was configured in v1.1.0. Search impressions, traffic and conversion remain unknown. Select a measurement service and privacy approach explicitly before adding scripts; this release does not claim live operating metrics.
