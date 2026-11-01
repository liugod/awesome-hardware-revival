# TRA-21 Chinese slogan restoration retrospective

Date: 2026-11-01
Scope: Restore the owner-approved Chinese KitAgain brand and homepage slogan, lock it in generated output, and deliver a review PR without merge or Pages deployment.

## Level 1 — Deliverable quality

- Replaced the retired Chinese brand and tagline with the exact approved wording `二手硬件再就业指南` in the README, both generators, generated page titles, Open Graph titles, header branding, and the Chinese homepage h1.
- Rebuilt the complete generated site. The retired wording count is zero in both `docs/` and `scripts/`, while the English homepage h1 remains unchanged.
- Added repository validation for the Chinese README heading plus the homepage h1, title, `og:title`, and header brand. Validation also rejects either retired Chinese phrase if it returns under `docs/` or `scripts/`.
- The full schema, export-parity, internal-link, UTF-8, and public-file validation passed. Real-browser checks at 1440 px and 390 px confirmed the rendered title, brand, and h1 with no horizontal overflow.
- Pushed implementation commit `864dfafc` and opened review-only PR #6: <https://github.com/liugod/awesome-hardware-revival/pull/6>. No merge or Pages deployment was performed.

## Level 2 — Process failures and corrections

- The first interpretation changed only the Chinese homepage h1. The ticket clarification showed that the true invariant covered every Chinese brand surface: title, Open Graph title, header brand, generator brand variables, README heading, and generated legacy pages. The correction moved from a page-level copy edit to a generator-level brand restoration.
- The first retired-copy assertion scanned the entire repository and failed on a historical changelog entry. Historical records should not be rewritten. The assertion was narrowed to the explicitly governed publication and generator scopes, `docs/` and `scripts/`.
- The Playwright skill's shell wrapper could not run because Windows Subsystem for Linux was unavailable. The same package was invoked through `npx.cmd`, preserving the required CLI workflow and browser evidence without installing or changing user-scoped skills.
- Playwright created a temporary snapshot directory. Its file was removed after inspection so it did not enter the commit or PR.

## Level 3 — Reusable mechanism

1. Treat owner-approved brand text as an immutable release input. Centralize it in the canonical generator and require explicit authorization before changing it.
2. Protect both source and output: assert exact README and homepage surfaces, then reject retired wording across the generated publication tree and generator scripts.
3. Rebuild generated pages from canonical sources instead of mass-editing HTML. A large generated diff is acceptable only when every changed page is explained by the same source-level invariant.
4. Keep a control language when changing localized brand copy. Here, the English homepage h1 was checked before delivery and remained byte-for-word unchanged.
5. Render-check long replacement copy at desktop and narrow widths. Exact text correctness is insufficient if the new brand causes header or hero overflow.
6. Keep review, merge, deployment, and public acceptance separate. TRA-21 ends at PR #6 until an authorized reviewer chooses the next gate.
7. Preserve this rule in the repository-local `hardware-revival-research` skill; do not modify user-scoped skill installations for a repository task.
