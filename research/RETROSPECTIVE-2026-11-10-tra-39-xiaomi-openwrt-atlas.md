# TRA-39 Xiaomi OpenWrt 路由器型号聚合与 canonical 复盘

Scope: From `origin/main` at TRA-38 merge `f4ca5b816ab2e6f9966a5e627329cafc0f6db1e6`, add bilingual Xiaomi/Redmi OpenWrt model-atlas routes, connect them to the router hub and network directory, add family navigation to existing model leads, and consolidate only a narrow zero-click set. Delivery stops at an open PR; main merge and GitHub Pages deployment remain unauthorized.

## 一阶：交付结果

- Added `/en/guides/xiaomi-openwrt-routers/` and `/zh/guides/xiaomi-openwrt-routers/` from tracked source data. Each page lists 29 existing Xiaomi/Redmi router leads; no model article or compatibility claim was invented.
- Added reciprocal bilingual entry points from the router guide and `directory/network`, plus a prominent family entry on all 29 listed model pages. AX9000, Mi Router 3G, and AX3000T are covered by explicit validation and browser checks.
- Kept AX9000, both AC2100 names, Mi Router 3G, Mi Router 3 Pro, and AX3000T self-canonical. The first four protection decisions follow observed clicks or naming ambiguity; AX3000T retains its route because the current snapshot contains strong positions despite zero clicks.
- Canonicalized only AX1800, AX3600, AX6000, Mi Router 3G v2, Mi Router 4, and Mi Router 4C to the localized aggregate. These pages remain present and indexable, have no `noindex`, retain all atlas data, and are omitted from the sitemap as noncanonical leaves.
- Preserved `二手硬件再就业指南`; no atlas data page was deleted and no broad Xiaomi `noindex` rule was added.

## 二阶：过程与纠偏

- The first validator edit used a chained subset assertion that accidentally required every watchlist entry to exist in the device atlas. It was corrected to require only the explicit Xiaomi model set to exist in both sources.
- The next validator run exposed a stale generated-page count; the contract was updated by exactly two localized aggregate pages. A separate sitemap count accounts for two aggregate URLs and the twelve localized noncanonical leaf exclusions.
- The first generator pass inserted an empty line into every directory page because an optional family block always emitted a newline. The rendering expression was changed so only the two network directory pages differ, eliminating unrelated generated noise.
- Final checks passed: Python compilation, deterministic double build, full static validation, 39,606 generated internal references, `git diff --check`, and targeted Playwright at 1280 px and 390 px for both languages. The browser run verified 29 model links, self/aggregate canonicals, no `noindex`, hub/directory/sample lead links, zero horizontal overflow, and zero console errors.

## 三阶：可复用机制

- Treat family membership, canonical consolidation, and protected self-canonicals as three source-controlled concepts. Brand-prefix matching is acceptable for discovery, not for canonical policy.
- A zero-click page is not automatically disposable: preserve clicked pages across both comparison windows, protect ambiguous names, and retain strong-position pages even before they receive clicks. Prefer a small reviewed allowlist over a batch rule.
- Canonical consolidation is not a redirect or `noindex` campaign. Keep the leaf readable and linked, point canonical/hreflang to the localized aggregate, remove the noncanonical URL from the sitemap, and prove the aggregate is self-canonical and indexable.
- Reused and extended `skills/hardware-revival-research/SKILL.md` with the thin family-atlas pattern rather than creating an overlapping one-off skill.
