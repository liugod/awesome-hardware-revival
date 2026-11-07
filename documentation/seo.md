# SEO and public routes

## Approach

Every indexable route is static HTML with a unique title, description, canonical URL, Open Graph metadata, and reciprocal Chinese/English `hreflang`. The English root is canonical at `/`; `/en/` remains a readable alias and is intentionally omitted from the sitemap.

| Route | Indexable | Data boundary |
| --- | --- | --- |
| `/` and `/zh/` | Yes | Public editorial summaries and navigation |
| `/{lang}/directory/` and `/page/{n}/` | Yes | Paginated public route index; filters load the complete public set on demand; no private or account data |
| `/{lang}/directory/{category}/` and `/page/{n}/` | Yes | Paginated static category indexes for the public taxonomy; empty or unsupported categories are not emitted |
| `/{lang}/project-sources/` | Yes | 200 repository-unique project sources with explicit reviewed/E0 split |
| `/{lang}/project-leads/{id}/` | Yes | GitHub metadata/README discovery boundary; `needs_review: true`; nullable independent scoring; no compatibility claim |
| `/{lang}/projects/{id}/` | Yes | Reviewed project facts and public source links |
| `/{lang}/leads/{slug}/` | Yes | Explicit E0/E1 lead boundary and public sources |
| Guides/articles/research/scoring | Yes | Public editorial and methodology content |
| `/en/` | Readable alias | Canonical is `/`; excluded from sitemap |
| `/projects/{id}.html` | Historical readable HTML | Canonical points to `/zh/projects/{id}/` |
| `/data/*.json`, `/data/*.csv` | Downloadable | Public exports; not added to the HTML sitemap |

`scripts/site_i18n.py` generates the sitemap from emitted canonical routes and uses the latest catalog, atlas, project-source, or scoring-ledger content date as `lastmod`; validation requires one date per canonical URL. `docs/robots.txt` advertises it. The static category taxonomy is `audio`, `camera`, `computer`, `ereader`, `gaming`, `mobile`, `network`, `peripheral`, `smarthome`, `speaker`, and `tv`; each non-empty category and its pagination are emitted as indexable canonical routes.

User query parameters only filter an existing index and are not emitted as separate canonical pages. Directory requests containing `q` or `category` add `noindex,follow` at render time. A recognized `category` value on the language directory root points its canonical to the matching static category route; a `q`-only or unsupported-category request points to the clean directory root. Query parameters on a static category route point back to that clean category route. Clean directory, category, and pagination pages remain indexable, so filtered views do not create a duplicate-URL surface or orphan the underlying records.

Editorial metadata is not accepted from the browser. Titles, descriptions, Open Graph values, canonicals, and alternates are escaped at build time; the directory's query-parameter guard may only replace its generated canonical with the generated clean directory URL and add `noindex,follow`. Source URLs are validated as HTTP(S). There is no bot-specific rendering or private-data path.
