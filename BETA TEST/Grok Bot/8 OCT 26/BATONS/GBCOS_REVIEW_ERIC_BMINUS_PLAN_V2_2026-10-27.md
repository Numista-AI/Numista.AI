# GB CoS REVIEW - Eric B- Live Mint Plan.v2 (NET-615 / NET-616 / NET-617, Round 2 of max 4)
- Reviewer: Grok Bot Chief of Staff (GB) | DTG: 2026-10-27 15:25 ET
- Inputs: ERIC_BMINUS_LIVE_MINT_PLAN_v2_2026-10-27.md; ARGON_REVIEW_ERIC_BMINUS_PLAN_V2_2026-10-27.md (84/100 CONDITIONAL GO)
- Code base checked: dev @ a6f4d22d

## Verdict: CONCUR CONDITIONAL GO (GB 82/100) - NOT executable as written. Fold Argon GAP-1..GAP-4 WITH the GB corrections below into Plan.v3 after Stand Alone Grok feedback. NO CODE yet.

## GB spot-check of Argon citations (verbatim, dev)
- main.py:7708-7713 summary init = coins_identified / receipts_parsed / total_purchase_value / unlinked_receipts (no duplicates_flagged) -> CONFIRMED
- main.py:8125-8128 coin_doc.pop("Retailer Invoice #") / pop("Retailer Item No.") -> CONFIRMED
- main.py:3560-3561 inv_no = data.get('Retailer Invoice #') / item_no = data.get('Retailer Item No.') -> CONFIRMED (snake_case never read)
- main.py:7607-7638 doc = {...} has no "Theme/Subject" and no "Strike Type" key -> CONFIRMED (GAP-2 part 1 correct)
- us_mint_catalog_service.py:315-317 Program/Series only overwritten when blank/"Invoice Import"/"USA" -> CONFIRMED
- add_coins.html:1127 s.duplicates_flagged || 0 -> CONFIRMED
- coin_detail_screen.dart:4217 color: Colors.white.withAlpha(200) on coin.storageLocation -> CONFIRMED (GAP-3)
- coin_set_viewer.dart:217-222 SizedBox(height: 148) + horizontal ListView.separated -> CONFIRMED (GAP-4)

## GB CORRECTIONS to Argon (Rule 6a - must go into Plan.v3)
### GB-1 (corrects GAP-1): duplicates_flagged IS set - the sweep is what misses.
- main.py:8347  dup_result  = _run_duplicate_sweep(user_email, session_id, new_coin_ids)
- main.py:8350  summary["duplicates_flagged"]  = dup_result["strong"] + dup_result["possible"]
- Both lines are inside _execute_import_process_worker (def at 7694; next top-level def is 8368). So Argon's "never increments it" is wrong, and Argon's proposed NEW pre-fetch loop at 7715 would duplicate the existing sweep. DO NOT add a second dupe engine.
- Real root causes (fix these in _run_duplicate_sweep / _score_duplicate instead):
  a) main.py:6967-6969 `.where("import_session_id", "!=", session_id)` - Firestore != only returns docs where the field EXISTS. Any existing coin without import_session_id (manual adds, older imports, backfilled coins like Eric's first 26RJ) is never loaded as a comparison candidate.
  b) main.py:6903-6948 _score_duplicate never compares SKU / item number or invoice number. Score = Program/Series 0.40 + Year 0.30 + Mint Mark 0.10 + Condition 0.10 + date 0.05 + cost 0.05. The new 26RJ had blank Program/Series and Theme (GAP-2), so it could not reach the 0.60 "possible" floor. Add: same retailer_item_num/item_number/Retailer Item No./product_code -> at least 0.60 (possible, "separate_order_copy"); same SKU + same invoice -> 0.90+ (strong, "same_invoice").
  c) Keep Argon GAP-1 step 4 (/api/review/commit main.py:3560-3561 read snake_case fallbacks) - CONFIRMED needed.
- Systemic (Eric rule): the same sweep serves every import path; FT must test a second-invoice dupe for a set (26RJ), a roll, and a single coin.

### GB-2 (adds to GAP-2): 26RJ is NOT in US_MINT_PRODUCT_CATALOG at all.
- grep "26RJ|26rj" in numista_backend/services/us_mint_catalog_service.py -> 0 hits on dev. Argon's step 2 is therefore an ADD, not an edit. Plan.v3 must say so, and must audit every SKU on Eric's two test invoices (and the receipts in the 1351hrs packet) for catalog presence - systemic, not 26RJ-only.
- Argon's authoritative-overwrite (step 3) must be limited to exact SKU catalog hits; never overwrite user-edited fields on already-committed coins (backfill touches only blank/"Invoice Import" fields). Mint figures win (issue_price 124.50 from the Mint receipt).
- Backfill for Eric's 4 test coins = dev/preview only; any live-data write needs Eric typed YES (live data writes are OFF).

### GB-3: GAP-3 and GAP-4 accepted as written. For GAP-4 prefer the responsive Wrap (no hidden coins, fewer clicks - matches Eric's click-cut goal) over arrows.

## Requirements carried for Plan.v3
1. All GB v1 requirements stand (real file:line verbatim, systemic, Mint wins, invoice upload must keep working, FT line per issue in FT_RETEST_CHECKLIST_NET602_NET616.md, preview only).
2. FT FAIL-the-build gates must include: second-invoice 26RJ shows Duplicates Flagged >= 1 and the flag appears in Review Hub; 26RJ shows image, Theme, value, 20-COIN SET strip with all 20 coins visible; Footlocker text readable.
3. Live/main only on Eric typed YES; cherry-pick approved commits onto a branch from main.

Next: Stand Alone Grok feedback (Eric relays the packet) -> AG CoS v2 writes Plan.v3 folding Argon GAP-1..4 + GB-1..3 + SAG -> Argon -> GB -> SAG (round 3 of 4).
