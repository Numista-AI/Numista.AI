# FT Gate: P7 V7 add-coins (preview p7-v7-gate), 15 Oct 2026, grokbot@numista.ai only

**Bottom line:** FAIL. The checklist "Add Selected Coins" path is broken because the backend rejects requests from the preview address (a CORS error). Manual entry passes. No writes to Eric's collections. The test coin was deleted and the count is back to 311.

| Path | Result | Notes |
|---|---|---|
| 1 Checklist, Add Selected Coins | FAIL | America250 checklist, Jefferson Nickel P and D ticked. Red banner: "Network error adding coins: ClientException: Failed to fetch, uri=.../api/checklist/add_coins". Nothing was added and the count stayed at 311. There was also no confirm dialog. |
| 2 Manual entry form | PASS | 1958 Washington Quarter PF67 at $10, qty 1. "Coin added to My Collection!" The count went 311 to 312 (+1, no duplicate) and the row is correct. Deleted afterward, back to 311. |
| + add another copy | NOT TESTED | It only exists on checklist rows, which are blocked. |

## Fix list
1. Add the origin https://numista-vault--p7-v7-gate-o3flke1i.web.app (or the *.web.app preview pattern) to the backend's allowed origins (CORS). That covers checklist/add_coins, user/ui_variant, news/feed, dismissed_news, spot_prices and mint-releases/upcoming.
2. Firestore runAggregationQuery returns 403 on the preview.
3. 404s on /assets/assets/mint_mark_diagrams/*.png (a doubled "assets" segment in the path, 8 files).
4. Live also blocks /api/spot_prices with CORS (from the 13 Oct smoke).
5. Re-gate path 1 and add-another-copy after fix 1.

Screenshots shot_01 to shot_09: dashboard, ticked, error, form, toast, 312, row, delete, final.
