# TRA-15 AI filter and Onju safety retrospective

## Level 1: deliverable quality

- Replaced the homepage and AI-guide `?q=AI` substring links with the explicit `?ai=native` facet. The old query rendered 104 mixed records; the new facet renders exactly the 10 reviewed projects whose canonical `ai_relation` is `native`.
- Added the same AI facet to the bilingual directory UI and URL state. It participates in the existing all-page lazy load, composes with device, score, and evidence filters, and remains usable without horizontal overflow at 390 px.
- Rewrote Onju v2 stop conditions as decisions a user can make before purchase or disassembly: exact second-generation hardware, loss of stock Google/Cast behavior, safe powered-off access and first flash, and willingness to maintain the external voice stack.
- Rewrote rollback as a bounded physical procedure: photograph and retain parts, then reinstall the original board only if it remains undamaged. Added bilingual fit/non-fit guidance and removed the unlinked Recovery guide label from Onju v2.
- Repository validation passed for schema, exports, 1100+ generated pages, internal links, bilingual parity, UTF-8 and public-file scanning. Browser validation passed existing directory/card/mobile contracts plus the TRA-15 104-to-10 comparison and Onju content assertions.

## Level 2: process corrections

- `TRA-15` was not a GitHub issue and the worktree was not Linear-linked. Reading the explicit Linear ticket before editing prevented the branch title from becoming an invented specification and kept all P1 items out of scope.
- The first recovery-link implementation hid unlinked labels on every project and produced broad unrelated diffs. It was narrowed to Onju v2 so the safety fix did not silently redesign other records.
- The first full browser command failed because the existing verifier assumes a local server on port 4185. Starting the documented static server separated an environment precondition from a product defect.
- Adding a fourth primary filter correctly invalidated hard-coded three-control and two-mobile-row browser assertions. The contract was updated to the intended four controls and three narrow-screen rows while retaining width and first-card-position gates.
- Updating canonical JSON without its CSV mirror triggered the parity validator. Synchronizing the Onju risk field before the final build restored source/export consistency.

## Level 3: reusable mechanism

- Semantic landing-page promises must link to structured facets backed by canonical fields, never to keyword searches that happen to resemble the label.
- A new static-directory facet requires one complete chain: card `data-*` value, visible control, URL read/write, active-filter detection, cross-page matching, localized generated markup, CSS row contract, static count assertions, and browser reload/mobile acceptance.
- Safety copy for hardware modification should always answer four user questions: exact hardware boundary, irreversible feature losses, pre-action stop conditions, and a recovery path that distinguishes software rollback from physical repair.
- Keep generator/source data authoritative, rebuild `docs/`, compare pre/post result counts, and audit the diff for unrelated generated churn before committing.

No deployment or public-site mutation was authorized in this branch-only task. The intended post-release URLs are `https://kitagain.com/en/directory/?ai=native`, `https://kitagain.com/zh/directory/?ai=native`, and the existing bilingual Onju v2 detail routes.
