# v1.20 action-guide retrospective

## Level 1 — Deliverable quality

The action-guide gate now has exact coverage for all 63 listed routes rated 4 stars or higher. Every guide has three bilingual blocks, every block carries an instructional, compatibility, security, or recovery source, forbidden history-style URLs are removed, and delisted routes receive no guide. The three Android kiosk routes that failed content review now use concrete upstream prerequisites, commands, configuration paths, verification states, and stop conditions.

## Level 2 — Process failure and correction

The first generator satisfied shape and source-count checks but converted scoring bases into instructions. This produced title-swapped boilerplate and, for software-only routes, risked implying hardware or firmware work that upstream did not require. A second review found the same failure pattern in 20 OpenWrt stop blocks: shared safety prose asserted stock-layout, bootloader, partition-backup, and calibration details even though those entries had no scored risk evidence. The correction was to treat structural validity and instructional usefulness as separate gates: normalize and compare each block after removing titles, prohibit scoring-meta language, use only the exact Firmware Selector profile and its Info boundary for those router stops, and add manual canonical guides when an entry's real documentation contains a more specific setup path than its scoring ledger.

## Level 3 — Reusable mechanism

For future enrichment rounds, first classify a route as firmware, operating-system image, application/service, hardware modification, or cloud replacement. Build each block only from the matching upstream setup/compatibility/recovery documentation; never borrow a flashing or backup pattern across classes. Reject commit, release-history, changelog, search-result, and marketplace URLs as tutorials. Validate exact rated/listed coverage, bilingual rendering, block-level source presence, normalized duplicate text, and absence on delisted entries before release.
