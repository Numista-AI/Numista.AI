# FT Gate: P7 V8.8 (preview p7-v88-gate, NET-269), 16 Oct 2026, grokbot@numista.ai only

**Bottom line:** FAIL, with 2 must-fix bugs in manual entry. First, Qty 3 adds only 1 to Total Coins. Second, Retailer and Invoice # drop their first character. The checklist add now works end to end. Total Coins was 311 at the start and 311 at the end, and all 4 test coins were deleted. No writes to Eric's collections.

| # | Item | Result | Notes |
|---|---|---|---|
| 1a | Confirm card before save | PASS (minor) | "Add Selected Coins? Save 2 coin(s) from '2026 America250 - Numismatic Collectibles' to your collection?" It shows the count and program but does not list the coins. |
| 1b | Cancel sends nothing | PASS | No add_coins request. Count stayed 311. |
| 1c | Confirm adds | PASS (minor) | add_coins returned 200. Toast "Successfully added 2 coins!", count 311 to 313, marked owned (7/19). The first Save click did nothing; the second worked. Deleted, back to 311. |
| 2a | Blank Year blocked | PASS (minor) | "Please enter the year on the coin, like 1921." The red text stays after the Year is filled in. |
| 2b | No dropped characters | FAIL | Retailer saved as "estShop" and Invoice as "NV-001". Other fields were OK. |
| 2c | Year persists | PASS | |
| 2d | Qty 3 saves 3 | FAIL | Coin details show Quantity 3, but Total Coins went up by only 1. |
| 2e | Blank Qty saves 1 | PASS | Count +1. The coin view doesn't show a Quantity field. |
| 2f | Retailer, Invoice and Notes save | PARTIAL | Retailer and Invoice save. Notes ("FT test") are not visible anywhere in the coin view. |
| 3 | Plain errors | PASS (minor) | Messages are plain English and name the field or coin. Two silent failures: the dead first Save click and the dropped letters show no message. |
| 4a | Demo guard | PASS (minor) | Read-only banner, and saving is blocked with "Couldn't save your 1999 coin — Your session expired or sign-in is required." It should say "demo" instead of "session expired". |
| 4b | PIN boxes at 389px | PASS | All 6 boxes and the keypad fit. |
| 4c | Phone layout at 389px | FAIL (minor) | Dashboard, Add menu and manual form are clean, and no $ amounts wrap. Clipped: checklist status chips ("Philadelphia I…"), and on My Collection the MELT VALUE header, Coins tab, Table/Cards toggle and card badges. |
| 5 | Console | PARTIAL | 3 errors after reload. No /assets/assets 404s. Firestore 403 RunAggregationQuery on coins_reference appears intermittently. Errors: Uncaught Error main.dart.js:4304; /api/news/feed CORS error and 401 from the preview origin; BetaChecklistSync and EPN Firestore permission-denied. |

## Fix list (by priority)
1. Manual entry, Qty N must add N to Total Coins (count bug).
2. Retailer and Invoice # fields drop the first typed character.
3. Notes not shown in the coin view (confirm they save).
4. First Save click on the checklist confirm card is ignored.
5. Confirm card should list the coins, not just the count.
6. Clear the Year error once it's filled. The manual form also doesn't reset after a save, which invites a double save.
7. Demo-mode message should say it's a demo, not "session expired".
8. Fix 389px clipping on checklist chips and the My Collection header and tabs.
9. Firestore permission-denied on coins_reference aggregation, BetaChecklistSync and EPN; news/feed CORS on preview; Uncaught Error main.dart.js:4304.
10. The "What should I call you?" modal comes back on every reload, and Skip and Esc don't close it. A stale "Coin added" toast stays pinned.
