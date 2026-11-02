# TRA-22 thumbnail fallback retrospective

## Outcome

- Kept the TRA-19 `data/project-images.json` ledger and its 352 source-backed images unchanged.
- Replaced the 191 pending-image states with a separate fallback ledger: 40 brand logos, 151 category illustrations, 0 unresolved.
- Every one of the 543 listed records now has an image on bilingual directory pagination and other generated card lists, plus one image on its zh/en detail page.
- Fallbacks are visibly labelled and captioned as hardware context rather than project imagery or compatibility evidence.

## First-order reflection: what happened

- A pinned Simple Icons commit provides six locally stored brand assets; deterministic repository-authored SVGs cover all 13 hardware categories.
- The generator infers brands from bilingual title/source fields, applies explicit overrides for ambiguous records, verifies asset hashes, and recreates both the ledger and TRA-22 report.
- Browser QA covered all 543 directory cards and ten originally blank records across brand/category and project/lead/project-lead types.

## Second-order reflection: why it worked

- A separate fallback ledger preserved TRA-19 provenance instead of weakening the meaning of a reviewed project image.
- Shared assets kept the addition small while per-entry records retained provenance, licence, bilingual alt text, inference, and the original missing reason.
- Rendering chooses source-backed imagery first and fallback imagery second, while validators require the two ID sets to be disjoint and their union to equal the listed directory.

## Third-order reflection: reusable process

- Treat missing-media input as a fixed audited set; require exact set equality rather than relying only on counts.
- Make acquisition optional and pinned, but keep normal builds offline and hash-verified.
- Validate data, generated HTML, image decoding, deep pagination, detail heroes, marker text, and zero placeholder DOM states separately.
- When pagination is lazy-loaded, browser checks must explicitly load all pages before asserting global counts.

No global skill was created because TRA-22 explicitly forbids changes under `~/.codex/skills`; the reusable procedure is recorded here and in `scripts/build_thumbnail_fallbacks.py`.
