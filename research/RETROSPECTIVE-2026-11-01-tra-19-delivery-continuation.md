# TRA-19 delivery continuation retrospective

Date: 2026-11-01
Scope: Audit and deliver the completed local TRA-19 image work without repeating acquisition, merging `main`, deploying Pages, or claiming public acceptance.

## Level 1 — Deliverable quality

- Preserved the previous session's 352 source-backed images and 191 placeholders; no remote image acquisition was repeated.
- Rebuilt and revalidated the bilingual static output, including all 543 listed directory cards, deep-page image loading, lazy decoding, and 390 px overflow checks.
- Added `research/tra-19-directory-image-missing.json`, an exact 191-entry missing-image report derived from the final ledger after manual visual corrections.
- Removed one duplicate Python import found during handoff review and kept the worktree clean after two commits.
- Pushed commit `49ef9ffa` and opened review-only PR #5: <https://github.com/liugod/awesome-hardware-revival/pull/5>.

## Level 2 — Process failures and corrections

- The first browser verification attempt failed with `ERR_CONNECTION_REFUSED` because the local preview server was not running. Starting a loopback-only server on port 4185 and stopping its exact PID after the run produced a valid browser result.
- Static validation reports 547 underlying directory records while the browser shows 543 cards. The difference is intentional: four records are delisted, so image coverage must use `listed_entries`, not total records.
- The raw acquisition audit contained 196 unaccepted pipeline records, but five later visual-review replacements were already present in the final ledger. Treating the acquisition audit as the final missing list would therefore have overstated placeholders by five.
- PowerShell's default `Get-Content` display rendered UTF-8 punctuation as mojibake. UTF-8-aware Python reads confirmed the tracked files themselves were correctly encoded.

## Level 3 — Reusable mechanism

1. For a continued uncommitted task, read the prior retrospective and `git status` before any mutation, then verify the exact branch, remote, existing PR state, and base divergence.
2. Do not rerun expensive or unstable acquisition when a prior session already produced validated binaries; rerun only deterministic application, build, static checks, and browser acceptance.
3. Compute delivery metrics and missing-item reports from the final canonical ledger and listed public IDs. Intermediate acquisition statuses are evidence, not the final public state.
4. When a browser script assumes a preview service, start a loopback-only temporary server, retain its exact PID, and stop only that process in a `finally` path.
5. Keep commit/push, PR creation, merge, deployment, and public acceptance as distinct gates. TRA-19 ended at the review PR gate.
6. Record reusable full-directory enrichment guidance in `skills/hardware-revival-research/SKILL.md`, including final-ledger missing-report derivation.
