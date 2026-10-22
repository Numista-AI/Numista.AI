# COS_SCORE | P7 | ARGON RCA v2 (vanishing grokbot coins) + PLAN_P7_V8_18_15b.v2
Scored 2026-10-22 ~14:45 ET by GROK CoS. Inputs: NET-429, 22 OCT 26\ARGON_VANISHING_COINS_RCA.md (v2), 22 OCT 26\PLAN_P7_V8_18_15b.v2.md. Checked against worktree p7v89_build at a7c83d7d and origin/main.

## A. RCA v2: CONDITIONAL PASS (code root cause proven; data proof and cost still open)
1. PASS: quotes are now word-for-word. main.py:3558-3590 (invoice check, attribute fallback, `if is_dupe: batch.delete(queue_ref...)`), main.py:3623-3628 (returns committed/skipped), review_hub_screen.dart:54-62 (snackbar uses _selectedIds.length, ignores body), collection_inventory.py:217-248 all match the real files.
2. PASS: the silent-drop mechanism is real code: blank Invoice # falls through to Year + Mint Mark + Denomination (limit 1); a match deletes the queue doc and never writes the coin.
3. LIVE RISK: the same fallback is on origin/main (main.py:3479) and the same optimistic snackbar is on main (review_hub_screen.dart:56 and :118). Real users can silently lose imported coins today.
4. OPEN (order a): no grokbot data check was done. Still need read-only counts: grokbot coins with source "PDF Invoice" created 13:50-14:00Z (expect 0 if all 34 skipped) and review_queue leftovers. "Cloud Run logs show 0 DELETE calls" has no quoted log lines.
5. FAIL (order d): "Cost moved with spot prices" is wrong. Acquisition cost does not move with spot. Cost fell 951.59 -> 946.87 (-4.72), BELOW the pre-import baseline, while the RCA says no coin docs changed. Explain with rows (which coin(s) account for 4.72, or a display/rounding/listener cause), quoted.
6. Second optimistic path: review_hub_screen.dart ~:118 "Successfully committed ${highConfIds.length} items with 100% AI Confidence!" must get the same fix.

## B. PLAN V8.18.15b.v2: PASS with conditions (Items 1-5 unlocked for BUILD on p7-v8.9)
- Items 1-4: PASS as in prior score (widget tests for >=48 px, exact NGC copy, cert-photo tokens 1024 + JSON mode + truncated-reply pytest, U.S. Mint invoice fixture pytest + real error UI).
- Item 5: PASS with conditions:
  a. Attribute match (Year+Mint+Denom) must NEVER delete. Commit the coin and mark it `possible_duplicate` (or return it for the user to confirm). No silent drop anywhere.
  b. Invoice # + Item No. definite-dupe rule: must not drop the 2nd..Nth copy when Qty > 1 is split into rows (ties to Item 4). Add a test.
  c. Client: both snackbars (:57 and ~:118) show the server's committed and skipped numbers, in plain words for older users, e.g. "Added 17 coins. 17 looked like coins you already have; check them in Review." No "duplicates" jargon without a next step.
  d. Systemic audit (Eric rule): list every other dupe path and say drop vs flag: main.py:2700-2709 execute_add_coin (looks like flag-only, confirm), main.py:3885+ duplicate scanner, add_coins_hub.dart:4724 "Duplicates Skipped", and the invoice/receipt import path.
  e. Tests: backend pytest for same Year/Mint/Denom with no invoice # (both saved), Qty>1 split rows (all saved), true re-import of same invoice+item (skipped and reported); widget test for the snackbar text.
- GEMINI38_REVIEW with quoted code is REQUIRED on the build (Tier 1: data-loss path).

## C. Orders (NET-430)
1. BUILD Items 1-5 on p7-v8.9 now. Dev only.
2. In parallel, finish RCA v2 items A4 and A5 READ-ONLY (grokbot only).
3. When built: EXECUTE_DONE + GEMINI38_REVIEW (code quoted) + NET-431, baton to GROKCOS.
Rules: dev only, no data writes, no restores, no deploys, main untouched. Hotfix to main only by cherry-pick on Eric's typed YES.
