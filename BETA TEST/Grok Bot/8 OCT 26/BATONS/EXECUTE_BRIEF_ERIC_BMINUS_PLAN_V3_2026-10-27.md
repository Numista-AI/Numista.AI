# EXECUTE BRIEF — Eric B− Live Mint Plan.v3 (NET-626)

**Authorization:** Eric typed YES 2026-10-27 ~3:52 PM ET  
**Target:** preview `p7-gate` ONLY. origin/main LOCKED. No live/main cherry-pick without a later typed YES.  
**Chain scores:** Argon 94 GO | GB 93 READY FOR SAG | SAG 92 GO  
**Plan:** `ERIC_BMINUS_LIVE_MINT_PLAN_v3_2026-10-27.md` (inherits Plan.v2 I-01..I-16, PM-01..PM-07, FT checklist)

## MUST fold before writing code (IG-1..IG-3)

### IG-1 (C1 — Review Hub badge)
- Dual-write `possible_duplicate=True` + human-readable `duplicate_reason` with existing `duplicate_flag` / `duplicate_score` in `_run_duplicate_sweep` writes (~main.py:7015-7028).
- Skip `status == "deleted"` docs in sweep candidates (~6973-6978).
- Keep single engine: drop Firestore `!=` on `import_session_id` that skipped missing-field coins; SKU ≥0.60 and SKU+invoice ≥0.90 scoring in `_score_duplicate`.

### IG-2 (C2 — enrich fill-missing-only)
- In `enrich_us_mint_item` (~us_mint_catalog_service.py:308-354): fill-missing-only copy `is_set`, `set_id`, `item_type`, `image_url_obverse`, `image_url_reverse`, `issue_price` from catalog_match onto item.
- Also fill `item_number` / `retailer_item_num` when blank (do not rely only on `"Retailer Item No."` which is popped at main.py:8127).
- Wrap Strike Type / Condition / Metal Content (~323-325) in fill-missing-only guards.
- ADD catalog row `26RJ` (issue_price 124.50, is_set True, set_id uncirculated-coin-set-2026, exact theme & image URLs per Plan.v3).
- Treat LLM “Uncirculated Coin Set” as placeholder/alias to “Uncirculated Sets”.

### IG-3 (C5 — slash keys)
- Do **NOT** pop `Program/Series` or `Theme/Subject`.
- Pop only the 4 legacy keys after snake_case copies: `Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees` (main.py:8125-8128).
- Add CoinModel.fromMap snake_case fallbacks for `retailer_item_num`/`item_number` and `retailer_invoice_num`/`invoice_number` (coin_model.dart ~193-194).

## Also execute from Plan.v3 C1–C5 / inherited I/PM
- C3: `_OwnerPhotoHero` contrast on `#F4F4F2` cream
- C4: replace horizontal ListView in CoinSetViewer with responsive Wrap (all 20 coins)
- Inherited I-01..I-16 / PM-01..PM-07 / FT_RETEST_CHECKLIST gates

## Gates after PREVIEW_READY
1. Field Tester runs `FT_RETEST_CHECKLIST` / FOUNDER_REVIEW_LOOP — FIXED or FAIL each item.
2. Four SAG proofs required (dup badge + 26RJ enrich + contrast shot + 20-coin strip + Firestore dump; roll + single-coin dupe).
3. Only after FT PASS → prompt Eric to retest same paths.
4. Live/main: **hold** until Eric types YES again after retest.

## Out of scope this EXECUTE
- NET-610 Option B CG overnight (8 PM Desk) — separate track, do not burn daytime CG.
- Catalog merge HOLD stack 586+588+589+590 — untouched.
- No Plan.v4 rewrite.

## Radio
NET-626 EXECUTE. Report PREVIEW_READY with Hosting URL + Run ID + commit SHA.
