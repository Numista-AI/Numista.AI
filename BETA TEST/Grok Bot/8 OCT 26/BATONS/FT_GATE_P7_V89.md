# FT Gate: P7 V8.9 (preview p7-v89-gate, commit 3a0c0b26), 16 Oct 2026, grokbot@numista.ai only

**Bottom line:** FAIL. Most NET-272 fixes landed: the Qty total, the first Save click, plain errors, demo wording, the keypad and the £ sign. Three things still fail: Retailer still drops its first letter, Notes and Qty aren't shown in the coin view, and the checklist progress jumps by 4 for 2 coins. Also open: grokbot Total Coins reads 312, vs 311 at the end of V8.8, and no stray test coin could be found. No writes to Eric's collections.

| # | Item | Result | Notes |
|---|---|---|---|
| 1a | Checklist confirm card lists coins | NOT VERIFIED | The exact card text wasn't captured in either run. Re-check next gate. |
| 1b | Cancel sends nothing | PASS | Count unchanged. Network shows a single add_coins request (200). |
| 1c | First Save click | PASS | Count +2 exactly; deleted afterward. |
| 1d | Checklist progress | FAIL (new) | Went from 1/39 to 5/39 after adding only 2 coins (Circulating Currency). |
| 2a | Blank Year blocked, red text clears | PASS (minor) | The Year error clears on typing. The Denomination and Series errors do not, and stale errors stay after the form resets. |
| 2b | First letter kept | FAIL | Retailer "TestShop" saved as "estShop". Invoice and Notes weren't checked (tool click error). |
| 2c | Qty 3 saves 3 | PASS | Count 313 to 316. |
| 2d | Blank Qty saves 1 | PASS | |
| 2e | Notes in coin view | FAIL | "FT test" isn't shown; Quantity isn't shown either. |
| 3 | Plain errors | PASS | "Please enter the denomination, like Quarter Dollar." "Please enter the series name, like Morgan Silver Dollar." |
| 4 | Keypad not inverted | PASS | 1-2-3 on top. |
| 5 | £ garbling | PASS | None found. NEW: the login icons (feature bullets, PIN backspace) render as empty boxes, so the icon font isn't loading. |
| 6 | Demo message | PASS | "Demo mode — create a free account to save coins." |
| 7 | Console | PARTIAL | 3 errors: Uncaught Error main.dart.js:4304; /api/news/feed CORS and 401. EPN and BetaChecklistSync Firestore permission-denied. |
| 8 | My Collection vs Dashboard count | PASS (minor) | Both 312. Ask Morgan's greeting says 311 while its header says 312. |

## Fix list
1. Retailer (and check every text field) drops the first typed character.
2. Show Notes and Quantity in the coin view.
3. Checklist progress counts jump (+4 for 2 coins).
4. Denomination and Series error text should clear on input, and errors should be cleared on form reset.
5. Load the icon font on the login screen (empty boxes).
6. Ask Morgan's greeting count is stale (311 vs 312).
7. Add a date-added sort or column to the Coins table so test coins can be found. Then reconcile grokbot's 312 vs 311.
8. Console: main.dart.js:4304 Uncaught Error; news/feed CORS on preview; Firestore permission-denied for EPN and BetaChecklistSync.
9. Next gate: capture the confirm-card text, and check Invoice and Notes first letters.
