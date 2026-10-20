# Bilingual content and deployment

## One source of facts

`data/catalog.json` is the shared source. `data/i18n/en.json` translates editorial text by project ID. Its SHA-256 is calculated over the full Chinese project record using sorted JSON keys, compact separators and UTF-8. Any source change blocks the build until the corresponding translation is reviewed. Do not blindly refresh the hash.

`data/deep-dives.json` and `data/i18n/deep-dives.en.json` contain the 12 complete analyses. `data/i18n/revisions.json` records both hashes and the review scope. Compare models, firmware, numerical claims, exclusions, costs and recovery conditions before recording a new review. Translation review never changes `checked_at` or upgrades hardware evidence.

`data/guides.json` pairs both languages for the three topic guides. Edit both versions together, retain source-project links and do not introduce unsupported compatibility claims.

The site uses stable use-case IDs. Older shared URLs with Chinese use labels are accepted and mapped to those IDs. Project IDs, category IDs, evidence levels and source URLs remain shared. English JSON/CSV is generated, not manually maintained.

## Build and acceptance

Run `python scripts/build.py` and `python scripts/validate.py`. Validation checks schema, 53 IDs in both languages, shared facts, both CSV exports, 175 HTML pages, language links, canonicals, all internal links, historical mappings, sitemap URLs, English text fallbacks and public-file hygiene.

Also verify rendered UI: search, five combined filters, clear, no results, share, reload, matching-page language switches, topic links and community context. Check narrow and desktop layouts. Hardware acceptance lists remain proposed, unexecuted tests.

## Custom domain preparation

The current deployment remains on the existing GitHub Pages project URL. No domain has been purchased or DNS changed.

1. Select and verify the brand/domain, registration and renewal cost, ownership and history.
2. Preserve the current release and record all old URLs from `docs/data/url-mapping.json`.
3. Verify ownership and configure the custom domain for this repository only, not unrelated sites.
4. Update `site.config.json` and README links, rebuild, then check DNS, TLS and the actual Pages behavior.
5. Verify every old project route and the public JSON/CSV. A static HTML canonical, meta refresh or JavaScript navigation is not an HTTP 301.
6. Validate both languages' canonical/hreflang/sitemap against public URLs. Confirm indexed URLs separately when search-console access is available.

The old `/projects/{id}.html` files remain complete Chinese pages with canonical links to `/zh/projects/{id}/`. They do not force a redirect. The root offers a language choice and keeps old search parameters when the user selects a language.

## Forum boundary

The `/zh/community/` and `/en/community/` pages are preparation pages, explicitly labeled. Existing GitHub issue forms remain the real submission channel. A project ID travels to the contribution page for the submitter to include in the form.

Do not activate `community_url` until hosting, a domain, working email, a moderator, actual registration/post/reply tests and a backup restoration test are ready. Main-site accounts and SSO are not prerequisites. Never create fictitious user activity or reproduction reports.

## Measurement

No analytics backend, search-console property or user tracking was configured in v1.1.0. Search impressions, traffic and conversion remain unknown. Select a measurement service and privacy approach explicitly before adding scripts; this release does not claim live operating metrics.
