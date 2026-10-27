# ERIC B- LIVE MINT PLAN v3 — 2026-10-27
**Author:** AG CoS v2 | **Status:** PLAN.V3 FILED — PENDING REVIEW (round 3 of 4: Argon → GB → SAG → Eric typed YES → Desk EXECUTE)
**Supersedes:** Plan.v2 where noted. Everything in Plan.v2 not listed under "CHANGES" stays in force (I-01..I-16, PM-01..PM-07 targets, FT checklist `FT_RETEST_CHECKLIST_NET602_NET616.md`).
**Folds:** Argon GAP-1..4 (84) + GB-1..3 (82) + SAG locks (81 CONDITIONAL GO).
**LOCKS:** NO CODE, NO DEPLOY, NO CHERRY-PICK until chain passes. Preview only (`p7-gate`). Live/main only on Eric typed YES. origin/main LOCKED. NET-609 NO-FOLD.

## 0. SAG HARD LOCKS (all four must be explicit — they are)
- **(a)** Sweep fix limited to (i) missing-`import_session_id` inclusion and (ii) SKU/invoice scoring. No second engine.
- **(b)** Catalog is **fill-missing-only**. Never overwrite non-blank fields on an existing or edited coin. (Replaces Argon GAP-2 step 3 "authoritative overwrite".)
- **(c)** Four retest proofs (section 6).
- **(d)** Preview-only; any live write needs Eric typed YES.

## 1. CHANGES vs Plan.v2

### C1 — Duplicates: fix `_run_duplicate_sweep`/`_score_duplicate` (GB-1, SAG §1; DROPS Argon GAP-1 pre-fetch loop)
Verified verbatim on dev (re-read 15:33):
```
main.py:6967:         docs = db.collection("users").document(user_email).collection(coll_name)\
main.py:6968:                  .where("import_session_id", "!=", session_id)\
main.py:6969:                  .limit(2000).stream()
main.py:8347:         dup_result  = _run_duplicate_sweep(user_email, session_id, new_coin_ids)
main.py:8350:         summary["duplicates_flagged"]  = dup_result["strong"] + dup_result["possible"]
main.py:6918:     new_prog = _val(new_coin, "Program/Series", "program_series", "series", "CoinName")
main.py:6948:     return min(score, 1.0)
```
Root causes: (1) Firestore `!=` only returns docs where the field exists, so coins lacking `import_session_id` (manual adds, older imports, Eric's first 26RJ) are never candidates. (2) `_score_duplicate` (6903-6948) never compares SKU or invoice.
Fix (minimal, in place):
1. Replace the `!=` query with an unfiltered stream per collection (existing `limit(2000)`), keep the existing `excluded_ids` self-exclusion (6971) and review_queue non-actionable skip (6974-6977). Drop docs whose `import_session_id == session_id` in Python.
2. In `_score_duplicate`, add before `return`: same SKU (`retailer_item_num`/`item_number`/`Retailer Item No.`/`product_code`) → `score = max(score, 0.60)` (possible, `separate_order_copy`); same SKU AND same invoice (`retailer_invoice_num`/`invoice_number`/`Retailer Invoice #`) → `max(score, 0.90)` (strong, `same_invoice`). Case-insensitive via existing `_val`.
3. Keep Argon GAP-1 step 4: `/api/review/commit` (main.py:3560-3561) reads snake_case fallbacks (currently reads only `Retailer Invoice #` / `Retailer Item No.`). Also fix the `where('Retailer Invoice #'...)` queries at 3567-3570 to try snake_case fields.
4. Surface flag in Review Hub (Plan.v2 I-08 amber badge, `review_hub_screen.dart` ~2145-2165) and importer card (`add_coins.html:1127` already reads `s.duplicates_flagged`).
5. Systemic: test set (26RJ), roll, single coin.
**Not done:** no new pre-fetch loop; no change to `summary` init (8350 already assigns it).

### C2 — Catalog: ADD `26RJ` (GB-2, Argon GAP-2, SAG fill-missing-only)
`us_mint_catalog_service.py` has 0 hits for 26RJ (GB grep). Add entry with exact strings: `program_series "Uncirculated Sets"`, `theme_subject "250th Anniversary Uncirculated Coin Set"` (matches `coin_image_service.dart:148`), `denomination "Set"`, `mint_mark "P & D"`, `condition/strike_type "Uncirculated"`, `is_set True`, `set_id "uncirculated-coin-set-2026"`, `item_type "set"`, obverse/reverse image URLs (`.../uncirculated-coin-set-2026/26rj_a.jpg`, `_e.jpg`), **`issue_price 124.50`** (Mint receipt wins; $36.40 is the 20-coin aggregate face value computed at `main.py:10844-10865`, not the price). Also add 23RH, 26AGA/26AGB, and **audit every SKU on both test invoices + 1351hrs receipts** for catalog presence (systemic).
- `normalize_and_validate_receipt` (`main.py:7607-7638`): add `"Theme/Subject"` and `"Strike Type"` to `doc` (verified absent by Argon and GB).
- `enrich_us_mint_item` (`us_mint_catalog_service.py:315-338`): **fill blanks only** (and "Invoice Import"/"USA" placeholders already handled at 316-317). Never overwrite a non-blank collector field. Mint figures (issue price) win on a fill.
- Backfill of Eric's 4 existing test coins: **preview/dev only**, touches only blank or "Invoice Import" fields, dry-run diff first, logged. Any live-data write = Eric typed YES.

### C3 — Contrast (GAP-3 + SAG pixel proof)
`coin_detail_screen.dart:4217` `color: Colors.white.withAlpha(200)` and `:4240` `Colors.white.withAlpha(120)` in `_OwnerPhotoHero` → `_kText(context)` / `_kSubtext(context)`, plus `_HeroHeader` (917-928) from Plan.v2. Proof = screenshot with measured contrast ≥ 4.5:1 on `#F4F4F2`, not code review.

### C4 — Set strip (GAP-4, GB-3, SAG)
`coin_set_viewer.dart:217-229` (`SizedBox(height: 148)` + horizontal `ListView.separated`) → responsive `Wrap(spacing:10, runSpacing:12)` so all coins show without clipping. Also apply to `set_contents_panel.dart` per Plan.v2. Dialog sizing at `coin_detail_screen.dart:132-133` and `my_collection_screen.dart:3502-3506` per Plan.v2 plus maximize toggle. Proof = full-strip screenshot showing **all 20 coins** for 26RJ.

### C5 — Slash-key hygiene (SAG residual)
Audit the commit/import writers for keys containing `/` or `#` (e.g. `Program/Series`, `Theme/Subject`, `Retailer Invoice #`). `main.py:8125-8128` already pops `Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees` before write; confirm no other slash key reaches Firestore and that snake_case equivalents are populated first (otherwise C1 loses its SKU signal). Add a unit test asserting no residual slash keys on `coin_doc`.

## 2. REQUIRED VERIFICATION (Rule 8: commands, not adjectives)
- `pytest` new tests: sweep flags coin lacking `import_session_id`; sweep scores same-SKU ≥0.60 and SKU+invoice ≥0.90; `enrich_us_mint_item` leaves non-blank fields untouched; no slash keys.
- `flutter analyze` + widget tests for `_OwnerPhotoHero` and `CoinSetViewer` (20 coins, no overflow).
- **Firestore dump (preview project) of sweep inputs + counter** before/after second 26RJ upload (SAG proof #1).
- Screenshots: contrast on cream; full 20-coin strip.

## 3. FT FAIL-THE-BUILD GATES (GB list)
1. Second-invoice 26RJ → Duplicates Flagged ≥ 1 on importer **and** flag visible in Review Hub.
2. 26RJ shows image, Theme, value, 20-COIN SET strip with all 20 visible.
3. Footlocker/storage text readable on cream.
4. Dupe test also passes for a roll and a single coin.

## 4. PLAN.V2 ITEMS UNCHANGED
I-01..I-16 and PM-01..PM-07 fixes (fee preserved at `us_mint_catalog_service.py:380`/`main.py:7653-7654`, mint-mark override at 328, edit-stays-in-review, select-all, Google Images removal, estate prompt decouple, legislation text, etc.) remain as in Plan.v2. Plan.v2 line 278 mis-labelled `main.py:7640-7675`; corrected here: `normalize_and_validate_receipt` is 7607-7638 range and `_execute_import_process_worker` begins at 7694.

## 5. GATES / ROLLOUT
Preview `p7-gate` only → FT retest per checklist → Eric typed YES → cherry-pick approved commits onto a branch from main → PR. Desk EXECUTE only after Argon → GB → SAG on v3 and Eric YES. Overnight NET-610 Option B CG (≤$5) is a separate queued track (NET-621/622) and does not touch this plan.

## 6. SAG FOUR RETEST PROOFS
(1) dupes: Firestore dump + counter ≥1; (2) set enrichment: 26RJ populated image/theme/124.50/is_set/set_id, audit of all other test SKUs; (3) contrast screenshot with measured ratio; (4) full 20-coin strip screenshot.
