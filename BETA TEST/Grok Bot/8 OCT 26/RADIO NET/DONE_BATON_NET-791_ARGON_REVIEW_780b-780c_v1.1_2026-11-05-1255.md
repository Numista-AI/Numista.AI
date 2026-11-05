# BATON NET-791 - To: Argon - REVIEW ONLY: FAILFIX PLANS 780b v1.1 and 780c v1.1
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Argon (Gemini 3.8)  
**Date:** 5 November 2026, 12:55 PM ET  
**Reference:** `GB_COS_SCORE_NET-780.md` (780b scored 88 FAIL, 780c scored 80 FAIL -> v1.1 Target 95+)  
**Review Order:** Argon (Score 95+ required) -> Grok Bot CoS 95+ -> SAG -> Eric typed YES.  

---

## Files in docs/, INBOX, and BATONS:
1. `FAILFIX_PLAN_NET-780b_CARDS_v1.1.md`
2. `FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md`
3. `DONE_BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-05-1250.md`

---

## Tasks for Argon:
1. Quote ONLY from real files with real line numbers.
2. **Review 780b v1.1 against must-fixes MF-B1 through MF-B4:**
   - MF-B1: `kFallbackUsMintSkus` type, issue price getter/fallback, and import into `my_collection_screen.dart`.
   - MF-B2: Year resolution in 26EA documents, text fallback regex, and `hasUserUploadedPhotos` guard.
   - MF-B3: $95.00 issue price dropped unless cited from code/SKU; renders gold `"Valuation Pending"` chip.
   - MF-B4: Purchase price never shown as "Value" (rendered as "Cost" if shown).
   - Advisories: Mojibake `5A` to `5¢`, nickel regex verification, corrected test path `test/services/canonical_mint_asset_service_test.dart`.
   - Commit `3936ba5f` explanation: hourly auto-backup cron, 0 code lines changed.
3. **Review 780c v1.1 against must-fixes MF-C1 through MF-C6:**
   - MF-C1: Deletion of Section 3D (CSP bridge); closed CSP perimeter (zero external hosts).
   - MF-C2: Real counts across all 353 collection items and 3,202 catalog entries citing dated files `1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv` and `numista_backend/gcs_full_inventory.csv`.
   - MF-C3: Reference `docs/MISSING_IMAGES.csv` and phased acquisition plan ($0 cost).
   - MF-C4: Licensing metadata fields (`author`, `license`, `source_url`, `retrieval_date`), Commons reuse licenses ONLY, and UI attribution chip.
   - MF-C5: PII intake gate: named excluded folders, 109 laptop / 138 GCS quarantined paths, 0-hit proof, and zero user IDs in object paths/metadata.
   - MF-C6: Pinned bucket `gs://numista-catalog-assets` and exact CSP citation `numista_mobile/firebase.json:275-276`.
4. **Confirm Standing Locks:**
   - PLAN ONLY. Zero code modifications. Zero deployments.
   - `origin/main` locked at `9f04550a`.
   - Stripe locked OFF.
   - Zero Firestore writes / zero seeding.

---

**Output File:** `INBOX\ARGON_REVIEW_NET-780_FAILFIX_v1.1.md` with individual scores for 780b and 780c, any must-fixes, and verdict.  
**Mode:** REVIEW ONLY. Nothing executes. No deploys without Eric's typed YES.
