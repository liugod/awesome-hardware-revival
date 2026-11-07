# TRA-37 lead-to-project upgrades retrospective

## Level 1 — execution

- The three source records were retained as evidence-bearing lead entries while their public detail routes were promoted to `/en/projects/.../` and `/zh/projects/.../`.
- Each canonical page now contains the project overview, applicable-device boundary, prerequisites, executable stop conditions, risk and recovery guidance, source ledger, one topic-hub backlink, and four generated related projects.
- GitHub Pages cannot configure arbitrary HTTP 301 responses from repository content. The legacy routes therefore use the repository's established 200 HTML redirect contract: canonical target, `noindex,follow`, immediate meta refresh, JavaScript `location.replace`, query/fragment preservation, and a fallback link.
- The build and full validator passed, including 39,433 generated internal references. Edge checks covered all six localized legacy routes and the three canonical pages at desktop and 390 px widths.

## Level 2 — process and failure analysis

- Keeping source identity separate from presentation identity avoided duplicating or rewriting the research ledger. A small route-override map was enough to make directories, source cards, related-project links, exports, and sitemap output converge on the new canonical pages.
- The first sitemap implementation promoted the upgrade review date to the global content date, which rewrote every sitemap entry. Diff review caught that unrelated SEO churn. The corrected generator assigns the new review date only to the six canonical project URLs and preserves the existing date everywhere else.
- Reusing the redirect renderer initially changed the copy on unrelated historical redirects. A scoped `project` mode restored byte-stable output for the existing redirects while allowing localized copy for these six lead migrations.
- Browser automation through the requested computer-use surface was unavailable. A local Edge DevTools session against the generated `docs/` tree provided equivalent navigation, responsive-layout, module, canonical, robots, and query/fragment checks without touching production.

## Level 3 — reusable rules

1. Promote a researched lead by layering presentation data over the original source record; do not mutate the evidence identity merely to change its public route.
2. Put route overrides in the canonical generator and apply them consistently to exports, cards, related links, URL mappings, sitemap entries, and validators.
3. Keep legacy redirect stubs out of the sitemap and require canonical plus `noindex,follow`; preserve query strings and fragments in the client redirect.
4. Treat sitemap `lastmod` as route-specific metadata. A new record date must not imply that unrelated pages changed.
5. Diff generated output before acceptance so a valid build cannot hide broad copy or metadata churn.
6. State hands-on status explicitly and never turn upstream documentation into a KitAgain compatibility or testing claim.

The reusable redirect behavior is already captured by the existing `github-pages-generated-redirects` skill. The lead-promotion-specific rules above remain repository-local because they depend on this generator's source ledger, route map, and validation contracts; a separate overlapping skill would add maintenance without a second consumer yet.
