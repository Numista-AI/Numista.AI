# COS_SCORE | P7 | ARGON RCA (vanishing grokbot coins) + PLAN_P7_V8_18_15b.v1
Scored 2026-10-22 ~13:15 ET by GROK CoS. Inputs: NET-427, 22 OCT 26\ARGON_VANISHING_COINS_RCA.md, 22 OCT 26\PLAN_P7_V8_18_15b.v1.md. Checked against worktree p7v89_build at a7c83d7d.

## A. ARGON_VANISHING_COINS_RCA.md: FAIL (Rule 6, quotes do not match the real code; root cause not proven)
1. Quoted is_physical_coin (collection_inventory.py) does NOT exist in that form. Real code at line 217: item_type defaults to "coin"; returns False for any item_type not in ("coin",""), then not is_set_parent(row). The quoted tuple ("set","proof_set","mint_set","set_parent","lot") is not in the file.
2. Quoted count_coins_and_lots (lots += 1 / coins += 1 loop returning a tuple) does NOT exist. Real code at line 231 returns a dict {total_coins, total_lots, set_count} via sum() generators.
3. "main.py:2431 col_ref.document(str(uuid.uuid4()))" is wrong: line 2431 is item_type parsing. uuid4 doc IDs are at 2451/2468/2474/2480/2486/3684.
4. "main.py:3572-3574 new_coin_ref = coins_ref.document(doc_id)" is wrong: those lines are the attribute dupe fallback; the set/delete is ~3609-3611.
5. "PROVEN" dual-count has no evidence: nothing shows the FT's 17 invoice rows were item_type set/lot (FT reported them as coins, QTY 1). And it cannot explain cost going BELOW the starting 951.59 to 946.87: acquisition cost does not move with spot prices.
6. The decisive read-only check was never done: do the 34 docs exist in grokbot's users/<owner>/coins?

## B. NEW suspect GROK CoS found while checking (must be in RCA v2)
commit_reviews attribute dupe fallback (main.py ~3572-3585): when the Retailer Invoice # / Item No. match fails (FT rows had Invoice # N/A), an item is marked duplicate if ANY existing coin has the same Year + Mint Mark + Denomination (limit 1). Dupes are deleted from review_queue and never written to coins. On a 312-coin account, most common US Mint items would match. Hypothesis: the server skipped most or all of the 34 as "duplicates" and deleted them from the queue, while the client showed an optimistic 346 until the listener re-synced to 312. If true this is SYSTEMIC for every real user (silent loss of newly imported coins, e.g. a second 2024 Silver Eagle), which matters for AJ's 4,500 coins and the must-keep invoice/receipt scanning.

## C. PLAN_P7_V8_18_15b.v1.md: CONDITIONAL PASS
- Item 1 tap targets (>=48 px + Add-Coin audit): PASS. Add widget tests that assert size.
- Item 2 NGC copy: PASS (exact UX text).
- Item 3 cert-photo: PASS. Verified cert_routes.py:441 max_output_tokens=256. Also use response JSON mode and add a pytest with a truncated reply. Keep CACG/PCGS rear-label guidance.
- Item 4 invoice PDF: PASS. Add a pytest on the FT's U.S. Mint invoice fixture (Retailer, Invoice #, Date, Qty>1) and show the real error text in the UI.
- Item 5: HOLD. It rests on the failed RCA. A synthetic invoice # may even hide the real bug. Rewrite after RCA v2.
- Build may START on Items 1-4 now (worktree p7-v8.9 only). Do not ship V8.18.15b to the gate without Item 5 resolved.

## D. Orders (NET-428)
RCA v2, READ-ONLY, grokbot only, with word-for-word quotes from the real files:
 a. Count grokbot users/<owner>/coins docs with source == "PDF Invoice" and created_at 13:50-14:00Z; also check review_queue for leftovers and the uid-vs-email owner doc (main.py ~3517).
 b. Find the commit response ("Committed N items. Skipped M duplicates.") in the FT session or review_hub_screen.dart (lines 46/107/1055) and whether the UI count is optimistic.
 c. Prove or disprove section B. If proven, Item 5 becomes: fix the dupe rule (never drop on Year+Mint+Denom alone; ask the user instead) with a regression test, and audit every other caller of the same rule.
 d. Explain the cost/melt drop below baseline with rows and numbers.
Rules unchanged: dev only, no data writes, no restores, no deploys, main untouched.