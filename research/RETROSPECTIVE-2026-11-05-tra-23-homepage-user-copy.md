# TRA-23 user-perspective homepage copy retrospective

Date: 2026-11-05
Scope: Rewrite the generated Chinese and English homepage copy around visitor outcomes and decisions, while preserving the locked Chinese brand line, canonical facts, and branch-only delivery boundary.

## Level 1 — Deliverable quality

- Reframed the homepage from catalog and retrofit terminology to a visitor sequence: enter a device, see what it can become, understand the required change, and check fit and rollback before acting.
- Changed the primary CTA to the concrete outcome `看看能做什么 / See what it can do`; simplified the proof strip, AI guide entry, reviewed-route labels, safety questions, category entry, title, and description in both languages.
- Preserved the exact Chinese `二手硬件再就业指南` h1 and kicker required by TRA-21. The dynamic AI-route count and all compatibility, cost, risk, and reproduction boundaries remain evidence-derived or explicitly unknown.
- Added a bilingual homepage copy contract to `scripts/validate.py`, updated the browser contract's exact placeholder expectations, rebuilt the canonical generator outputs, and kept the generated diff to the English root, English localized homepage, and Chinese homepage.
- The complete repository validator passed. Real-browser acceptance passed at 1440 px and 390 px in both languages with zero horizontal overflow and zero console errors. The homepage search CTA carried `Nest Mini` to the directory URL and returned the two matching records.

## Level 2 — Process failures and corrections

- The first patch assumed a validation-loop shape that did not match the current file and was rejected without changing files. Re-reading the exact block before applying the smaller patch avoided a partial or misplaced assertion.
- The first resumed browser run correctly failed because the exact placeholder contract still named the old copy. Updating only the two bilingual expected strings preserved every layout, navigation, media, and behavior assertion; the full contract then had to pass before delivery.
- The next browser run exposed an English mobile subtitle wrapping beyond the existing one-line limit. Shortening it to `See what your device can do next.` kept the visitor outcome while satisfying the unchanged 390 px layout gate.
- A literal rewrite of the prior technical headings would still have made the catalog the subject. The copy-editing pass instead tested every section with “what does the visitor get or decide here?” and moved methodology language out of the main narrative.
- Stronger marketing wording could have implied universal compatibility or known cost. The final copy keeps the emotional promise at the hardware-reuse level and puts the decision gates immediately below it: exact model, amount of change, and rollback.
- Generated HTML was not edited by hand. The source generator was changed first, then a full build proved that only the three intended homepage outputs changed.

## Level 3 — Reusable mechanism

1. Start homepage copy with the visitor's owned object and desired outcome, not the product taxonomy or research method.
2. Map the page to four decisions: identify the device, see the possible outcome, understand the intervention, and check rollback. Give each section one decision only.
3. Turn CTA labels into the result the visitor receives. Keep evidence grades, repository states, and source taxonomy as supporting detail unless the user needs them to choose.
4. Marketing energy must stop at the evidence boundary. Never convert unknown fit, cost, risk, or reproduction into confidence language.
5. Protect approved brand copy and data-derived counts with exact assertions, then rebuild from the canonical generator.
6. Validate copy in a real browser at desktop and narrow widths. Check overflow, button wrapping, reading order, console errors, language switching, and the actual CTA destination.
7. Keep local implementation, commit, PR, merge, deployment, and public acceptance as separate gates. TRA-23 is committed, pushed, and submitted as open PR #8; merge, Pages deployment, and public acceptance remain unperformed.

The reusable homepage-copy procedure was added to `skills/hardware-revival-research/SKILL.md`.
