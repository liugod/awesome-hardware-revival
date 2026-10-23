# SEO and public routes

## Approach

Every indexable route is static HTML with a unique title, description, canonical URL, Open Graph metadata, and reciprocal Chinese/English `hreflang`. The English root is canonical at `/`; `/en/` remains a readable alias and is intentionally omitted from the sitemap.

| Route | Indexable | Data boundary |
| --- | --- | --- |
| `/` and `/zh/` | Yes | Public editorial summaries and navigation |
| `/{lang}/directory/` | Yes | Full public route index; no private or account data |
| `/{lang}/project-sources/` | Yes | 200 repository-unique project sources with explicit reviewed/E0 split |
| `/{lang}/project-leads/{id}/` | Yes | GitHub metadata/README discovery boundary; `needs_review: true`; nullable independent scoring; no compatibility claim |
| `/{lang}/projects/{id}/` | Yes | Reviewed project facts and public source links |
| `/{lang}/leads/{slug}/` | Yes | Explicit E0/E1 lead boundary and public sources |
| Guides/articles/research/scoring | Yes | Public editorial and methodology content |
| `/en/` | Readable alias | Canonical is `/`; excluded from sitemap |
| `/projects/{id}.html` | Historical readable HTML | Canonical points to `/zh/projects/{id}/` |
| `/data/*.json`, `/data/*.csv` | Downloadable | Public exports; not added to the HTML sitemap |

`scripts/site_i18n.py` generates the sitemap from emitted canonical routes and uses the latest catalog, atlas, project-source, or scoring-ledger content date as `lastmod`; validation requires one date per canonical URL. `docs/robots.txt` advertises it. User query parameters only filter an existing index and are not emitted as separate canonical pages, preventing combinatorial duplicate URLs.

Dynamic metadata is not accepted from the browser. All values are escaped at build time; source URLs are validated as HTTP(S). There is no bot-specific rendering or private-data path.
