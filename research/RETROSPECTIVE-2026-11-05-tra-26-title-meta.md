# TRA-26 title, meta, lead, and internal-link retrospective

Date: 2026-11-05
Scope: Improve English search snippets and opening summaries for six GSC-priority routes, then strengthen the Nest Mini decision-guide link graph without changing the locked Chinese brand line.

## Level 1 — Deliverable quality

- Added source-controlled English SEO and lead overrides for CoreELEC, FBInk, AirSane, dorita980, Kiosk Satellite, and OpenBeken. Titles are 45–60 characters and descriptions are 120–160 characters, with the searched project and job stated directly.
- Kept evidence classes intact. AirSane, dorita980, and Kiosk Satellite remain E0 discovery pages whose leads explicitly preserve unverified model, installation, recovery, sensor, or long-running behavior. CoreELEC, FBInk, and OpenBeken retain their reviewed-source hardware and recovery boundaries.
- Replaced OpenBeken's longer title and generic opening with a shorter BK7231/local-MQTT title and a lead covering exact chip/board matching, flash/calibration backups, and recovery before initial flashing.
- Added a contextual link from the Nest Mini guide back to the AI retrofit hub and links from the Onju Voice and Onju v2 records to the Nest Mini decision guide. The existing AI retrofit and speaker/voice hub links to the guide are now protected by validation.
- Rebuilt generated HTML and passed the complete repository validator. The exact Chinese slogan `二手硬件再就业指南` remains protected by its existing generator and validation contracts.

## Level 2 — Process failures and corrections

- A broad first text search produced excessive generated-output matches, and two Windows `rg` regex attempts failed because quoting removed the intended character classes. Narrowing searches to canonical data files and using parsed JSON records gave a smaller, reliable evidence surface.
- The six targets were not one page type: CoreELEC, FBInk, and OpenBeken use reviewed project rendering, while AirSane, dorita980, and Kiosk Satellite use project-source rendering. A page-specific override layer was therefore safer than changing canonical catalog summaries or editing generated HTML.
- The Nest Mini guide and two hubs already had useful links. Instead of duplicating hub calls to action, the implementation filled the missing contextual paths: guide back to hub and exact Onju records to guide.
- OpenBeken already had finalized SEO fragments from an earlier scoped edit. The recovery pass preserved its verified facts and flashing warning while tightening the title and moving the same decision boundary into the visible lead.

## Level 3 — Reusable mechanism

1. Start from the GSC query, canonical route, and evidence class; do not infer a route from the project name alone.
2. Keep SEO copy page-specific and source-controlled. Do not rewrite exported research summaries merely to improve snippets.
3. Use a compact contract: searched name/job in a 45–60 character title, a 120–160 character factual description, and a lead that covers outcome, hardware boundary, and pre-action check.
4. Let Open Graph inherit title and description unless a distinct social message is intentional; validate both rendered forms.
5. On E0 pages, use words such as “evaluate” and state what KitAgain has not verified. Search performance does not authorize an evidence upgrade.
6. Improve internal links by connecting the decision guide, its topical hubs, and the exact project records. Avoid unrelated or repeated keyword anchors.
7. Build from the generator, assert the exact generated title/meta/OG/lead and link paths, run the full validator, then rebuild and compare the working diff for determinism.
8. Keep implementation, PR, merge, Pages deployment, observed indexing, and GSC click recovery as separate acceptance stages.

This reusable GSC page-pass procedure was added to `skills/hardware-revival-research/SKILL.md`.
