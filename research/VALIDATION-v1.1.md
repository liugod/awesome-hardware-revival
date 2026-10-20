# Validation — v1.1.0

Date: 2026-10-20. These checks concern the website and editorial translations, not physical hardware compatibility.

## Automated acceptance

- JSON schema, 53 unique IDs, 51 families, 13 categories and 12 deep dives passed.
- 53 source-checked English translations and 12 complete English analyses, plus 3 paired topic guides.
- 175 HTML pages passed title, H1, language, canonical and internal-link validation: 120 localized pages, one language entry and 54 historical pages.
- All 53 historical project pages map to their corresponding Chinese canonical. No HTTP 301 redirect is claimed.
- 121 unique sitemap URLs resolve to generated pages. Both project languages have matching reciprocal hreflang.
- English visible text has no silent Chinese paragraph fallback; the explicit Chinese language switch is allowed.
- English exports preserve model identifiers, categories, source URLs, evidence levels, risk codes, null costs and review dates. Both CSV exports match their respective JSON.
- A changed source record was deliberately simulated in memory: the build rejected its stale translation before writing.
- Two consecutive builds produced identical file hashes.
- Public-file checks found no credential patterns, private machine paths or UTF-8 replacement characters.

## Browser acceptance on localhost

- English query `Kindle` plus all five filters (e-reader, information display, AI-assisted, advanced, E2) produced only the WHOOP entry.
- Switching to Chinese and reloading preserved all filters and the one-entry result.
- The share button reported successful copying of the filtered URL.
- Both languages showed the empty state for a nonexistent query and returned to 53 entries after clear.
- Chinese search `printer` and English search `打印机` each returned the HP driver entry.
- Root URLs with historical Chinese use values retained the query through language selection and mapped to the stable use-case ID (information display: five entries).
- Matching-language project detail, full WHOOP analysis and the Kindle topic guide rendered.
- Project discussion links opened a clearly labeled community preparation page carrying `project=kindle-whoop`, then retained that ID in the contribution link.
- Desktop rendering and 390px viewport emulation were inspected. English homepage, Chinese topic and Chinese/English details had no measured horizontal overflow; the catalog had one card column and two filter columns. This is browser emulation, not a physical phone test.
- No browser error/warning log entries were captured during these checks.
- A high-level screenshot call stalled; later screenshots used bounded developer-protocol capture. This tooling problem is not counted as a website failure or a hardware test.

## Scope and release boundary

No independent forum, account system, domain purchase, DNS change or analytics service was activated. Community pages explicitly say the forum is not open. Existing GitHub issue forms are the current submission route.

Hardware evidence remains E1=50, E2=3, E3=0. Translation and website testing do not upgrade evidence. Costs remain unknown. Public deployment and file readback must be verified separately from these local checks.
