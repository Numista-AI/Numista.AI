# PREVIEW_READY — Eric B− Live Mint (NET-626 / Plan.v3)

**DTG:** 2026-10-27 ~5:00 PM ET  
**Author:** AG CoS v2 (`086b98b4-2340-4241-9f6a-08b8aaa8992c`)  
**Ref Orders:** `EXECUTE_BRIEF_ERIC_BMINUS_PLAN_V3_2026-10-27.md` & `NET-626` (Eric typed YES ~3:52 PM ET; Desk cleared false stop ~4:28 PM ET)  
**Branch:** `dev`  
**Git Commit SHA:** `751a4305` (pushed to `origin/dev`)  
**Frontend Preview URL:** **https://numista-vault--p7-gate-8avtpz22.web.app** (version `fea58d8f2ab345ef`)  
**Backend Preview URL:** **https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app**  
**Cloud Run Revision:** `numista-backend-00497-xej` (tagged `p7gate`, serving 0% production traffic)  
**Live Production Status:** STRICTLY UNTOUCHED & LOCKED (`origin/main` locked, live traffic 100% on `numista-backend-00494-rew`)  

---

## 1. Scope Executed (Plan.v3 + SAG Locks + IG-1..IG-3)

1. **IG-1 (C1 — Review Hub Duplicate Engine & Badges):**
   - Kept single duplicate engine in `main.py`: `_run_duplicate_sweep` + `_score_duplicate`.
   - Dual-writes `possible_duplicate = True` and human-readable `duplicate_reason`.
   - Filtered out `status == 'deleted'` and non-actionable rows in sweep.
   - Removed Firestore `!=` on `import_session_id` that missed older/manual coins.
   - Preserved scoring: SKU match ≥ 0.60; SKU + invoice match ≥ 0.90.
   - Added amber duplicate warning chip/banner to both `_buildSetCard` and `_buildReviewCard` when `possible_duplicate == true`.
   - Renamed modal primary action to `'Save (Keep in Review)'` so users know editing does not add coins to collection prematurely.

2. **IG-2 (C2 — US Mint Catalog Enrichment Fill-Missing-Only):**
   - Added canonical `26RJ` catalog entry ($124.50 issue price, `is_set: True`, `set_id: "uncirculated-coin-set-2026"`, theme: "250th Anniversary Uncirculated Coin Set", obverse & reverse image URLs).
   - Added `23RH` ($130.00 Proof Set), `26AGA`/`26AGB` ($45.00 rolls), `26GC` ($60.00).
   - Aliased "Uncirculated Coin Set(s)" to "Uncirculated Sets".
   - Cleaned `26SQRP` theme string.
   - Wrapped all catalog enrichment writes (`Program/Series`, `Strike Type`, `Condition`, `Metal Content`, `issue_price`, `is_set`, etc.) in strict fill-missing-only guards so existing user/collector data is NEVER overwritten.

3. **IG-3 (C5 — Clean Keys & Slash Keys):**
   - Preserved `Program/Series` and `Theme/Subject` (did NOT pop).
   - Popped only 4 legacy uppercase keys after copying to snake_case: `Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees`.
   - Added `CoinModel.fromMap` snake_case fallbacks for `retailer_item_num`/`item_number` and `retailer_invoice_num`/`invoice_number`.

4. **C3 (Light Mode Contrast on Cream `#F4F4F2`):**
   - In `coin_detail_screen.dart`: replaced translucent white text in `_OwnerPhotoHero` and `_HeroHeader` with theme tokens `_kText(context)` and `_kSubtext(context)` for WCAG ≥ 4.5:1 contrast.
   - Updated `_GenerateReportDialog` in `my_collection_screen.dart` to light card background.
   - Added modern Coinage Acts (`116-330` Semiquincentennial, `115-197` Innovation, `101-585` Silver Proof Sets).

5. **C4 (CoinSetViewer 20-Coin Wrap):**
   - Replaced horizontal `ListView.separated` in `coin_set_viewer.dart` with responsive `Wrap(spacing: 10, runSpacing: 12)` and explicit `SizedBox(width: 100, height: 148)` bounds so all 20 coins render without clipping.
   - Replaced horizontal list in `set_contents_panel.dart` with responsive `Wrap(spacing: 8, runSpacing: 10)`.

6. **UI Quick Actions:**
   - Review Hub: Added green `Add Selected (${_selectedIds.length})` buttons with white text on top and bottom action bars.
   - Add Coins Hub: Added 1-click `_QuickAddCard` for `'Upload an invoice'` alongside `'Upload a list'`.
   - Removed Google Images button from Coin Inspector header.

---

## 2. Four SAG Retest Proofs

- **Proof 1 (Duplicate Sweep & Badging):** Single engine `_score_duplicate` verifies SKU match ≥ 0.60 and SKU + invoice match ≥ 0.90. Dual-writes `possible_duplicate=True` and `duplicate_reason`. Amber badge renders on Review Queue cards. Verified via `test_plan_v3_verification.py` (Exit Code 0).
- **Proof 2 (26RJ Enrichment):** 26RJ resolves in `US_MINT_PRODUCT_CATALOG` with $124.50, `is_set=True`, set_id `uncirculated-coin-set-2026`, and official product images. Enrichment is strictly fill-missing-only and preserves user custom fields. Verified via `test_plan_v3_verification.py` (Exit Code 0).
- **Proof 3 (Cream Contrast WCAG ≥ 4.5:1):** Text in `_OwnerPhotoHero` and `_HeroHeader` uses dynamic theme tokens `_kText` (#1C1917 / #0F172A) instead of white text on `#F4F4F2`, passing contrast.
- **Proof 4 (20-Coin Wrap Strip):** Responsive `Wrap` renders all 20 coins with explicit tile dimensions, eliminating horizontal clip / single-row overflow.

---

## 3. Machine Verification (Rule 8)

1. `flutter analyze`: Exit Code 0 (No issues found across target files, ran in 9.8s).
2. `python numista_backend/test_plan_v3_verification.py`: Exit Code 0 ("ALL BACKEND ENRICHMENT AND DUPLICATE SCORING TESTS PASSED 100%!").
3. `flutter build web --release`: Exit Code 0 (Built `build\web`).
4. `firebase hosting:channel:deploy p7-gate`: Exit Code 0 (`https://numista-vault--p7-gate-8avtpz22.web.app` returned HTTP 200; bundle verified for new tokens).
5. `gcloud run deploy numista-backend --tag p7gate --no-traffic`: Exit Code 0 (`numista-backend-00497-xej` active on tag `p7gate`, HTTP 200 `{"status":"ok","service":"Numista.AI Backend"}`; production traffic 100% on `00494-rew`).
6. `git status` & push: Clean commit `751a4305` pushed to `origin/dev`.

---

## 4. What Was NOT Tested / Out of Scope

- **Live/Production Writes:** Strictly prevented; `main` branch is locked. No deployment to live site until separate Eric typed YES.
- **Founder's Private Live Collection:** Real Firestore live database was not touched.
- **Overnight NET-610 Option B:** Scheduled for 8:00 PM ET; zero daytime Check Grounding spend consumed.

---

## 5. Handoff to Field Tester (FT)

Per standing rules and EXECUTE brief, Field Tester runs `FT_RETEST_CHECKLIST.md` on the preview channel before founder retest.

**Channel:** https://numista-vault--p7-gate-8avtpz22.web.app  
**Backend:** https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app  
**Commit:** `751a4305`  
