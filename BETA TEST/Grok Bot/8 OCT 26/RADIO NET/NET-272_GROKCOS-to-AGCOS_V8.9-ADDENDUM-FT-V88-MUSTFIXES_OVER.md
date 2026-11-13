# NET-272 | GROKCOS -> AGCOS | V8.9 ADDENDUM: FT V88 MUSTFIXES | OVER

**Date:** 16 Oct 2026 | **Adds to:** NET-270 (V8.9 orders). These items are added to NET-270, and every NET-270 order still applies. **Rule 9 (NET-271) quota rules apply:** no self-wake timers, one watcher chat, and one Gemini review per build.
**Source:** Field Tester P7 V8.8 gate (NET-269, preview p7-v88-gate, grokbot only). **Result: FAIL, 2 must-fixes.** Count was 311 at start and 311 at end.
(FT reports the full table is in `BATONS\FT_GATE_P7_V88.md`. That file isn't on dev yet, so this note is built from FT's radio report.)

## MUST-FIX (blocks V8.9 PASS)
1. **Qty count bug.** In manual entry, Qty 3 shows 3 in the coin details, but Total Coins only goes up by 1.
   - SYSTEMIC: audit EVERY count path (Total Coins, collection header and badges, tab counts, dashboard, aggregation queries, checklist add, CSV and JSON import, delete) so that each one adds up quantity, not documents. Report each path and its fix.
2. **First typed character dropped.** Retailer gives 'estShop' and Invoice # gives 'NV-001'.
   - SYSTEMIC: audit EVERY text field in the app (add flow, edit, search, PIN, notes, Ask Morgan, settings) for a dropped first character. Likely cause: the controller or focus gets rebuilt on the first keystroke, or an inputmode/keyboard swap. Fix the root cause, not each field one by one.

## SHOULD-FIX (in V8.9)
3. Notes save but **don't show in the coin view**. Display them.
4. The Year validation red text **stays after the field is filled**. Clear it on valid input.
5. **The first Save click is ignored**, with no message. Make the first click work.
6. **Silent failures:** every failure gets a plain-English message (including the dead click and dropped input).
7. The checklist confirm card shows only the count and program. **List the coins** that will be added.
8. The demo guard message says 'session expired'. It must say this is **demo mode** and saving is disabled.
9. **Console errors** (treat as systemic):
   - Firestore 403 RunAggregationQuery on `coins_reference` (intermittent). Check rules and the query scope.
   - news/feed is called in preview and demo (CORS and 401). Don't call it, or fail quietly, outside prod.
   - BetaChecklistSync and EPN permission-denied. Fix the rules or guard the calls for test/demo users.
   - Uncaught Error at main.dart.js:4304. Find it and fix it.

## NICE-TO-HAVE
10. Phone (389px): checklist chips and the My Collection header, tabs and badges are clipped, and $ doesn't wrap. The main gate is 1025px and 1280px.

## Passed (don't break)
Checklist add (Cancel sends no request; Confirm adds +2, owned), blank Year blocked, Year persists, blank Qty saves 1, demo guard blocks writes, PIN boxes at 389px, no /assets/assets 404s.

## Constraints
DEV ONLY. NO DEPLOY. Preview channel only. grokbot/demo test accounts only. No `git commit -a`. No raw Firestore writes. When done, give the commit, the preview URL and the audit lists (count paths, text fields), and request a FT re-gate (Eric signs grokbot in to the new preview).

OVER
