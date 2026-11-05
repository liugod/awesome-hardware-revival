# KitAgain Search Console 7+7 refresh

This repository uses a read-only, repeatable Search Console pull for `sc-domain:kitagain.com`. Each run compares the latest seven-day window with the immediately preceding seven-day window. By default, the latest window ends two UTC days before the run to allow for normal Search Console reporting lag.

The script first calls `sites.list` and fails unless the existing OAuth account can see the exact domain property. It then pulls the same query, page, query+page, and date dimensions for both windows, paging until each dimension is complete. Headline totals come from the date dimension because anonymized searches may be absent from query rows.

## Run on the existing Codex/X79 path

Use the already-authorized local credential file. Do not create a new OAuth client or copy credentials into this repository.

```powershell
$env:GSC_OAUTH_CLIENT_FILE = 'C:\work\.secrets\gsc-oauth-client.json'
node --use-env-proxy scripts\gsc_7d_compare.mjs
```

`--use-env-proxy` reuses the current Codex/X79 `HTTP_PROXY`, `HTTPS_PROXY`, and `NO_PROXY` environment. The script never prints or stores OAuth values or access tokens.

Snapshots are written to `research/gsc/snapshots/YYYY-MM-DD-gsc-7d-vs-prev-7d.json`, where the filename date is the inclusive end of the current window. Re-running the same end date deterministically refreshes that snapshot.

Optional controls:

```powershell
$env:GSC_END_DATE = '2026-11-03'      # inclusive current-window end
$env:GSC_DATE_LAG_DAYS = '2'          # used only when GSC_END_DATE is absent
$env:GSC_OUTPUT_DIR = 'research\gsc\snapshots'
$env:GSC_ROW_LIMIT = '25000'
node --use-env-proxy scripts\gsc_7d_compare.mjs
```

Keep `GSC_END_DATE` in `YYYY-MM-DD` form. Every generated JSON file records the exact periods, property permission, totals, deltas, raw dimension reports, and the reporting-lag setting needed for a like-for-like rerun.
