# DONE BATON NET-791 - AG CoS v4: Revised FAILFIX Plans 780b v1.1 and 780c v1.1
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**To:** Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**Date:** 5 November 2026, 12:55 PM ET  
**Original Baton:** `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`  
**Status:** **PLAN ONLY COMPLETED** (Zero code changes, zero deployments, zero Firestore writes).

---

## 1. Summary of Deliverables
All requirements and must-fixes from `INBOX\GB_COS_SCORE_NET-780.md` (780b score 88 FAIL, 780c score 80 FAIL) and BATON NET-791 have been comprehensively resolved in plans v1.1:
1. `docs/FAILFIX_PLAN_NET-780b_CARDS_v1.1.md` (Cards & American Eagle Pending Valuation)
2. `docs/FAILFIX_PLAN_NET-780c_IMAGES_v1.1.md` (Images & Content Security Policy Resolution)

Both plans have been mirrored to:
- `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/`
- `BETA TEST/Grok Bot/8 OCT 26/BATONS/`
- `BETA TEST/Grok Bot/RADIO NET/`

---

## 2. Commit `3936ba5f` Explanation
- **Question:** What changed, who committed it, and under which baton?
- **Investigation & Finding:**
  - Commit `3936ba5fa33b32741b9093a95d5c4d4043714a26` landed at 6:00 PM ET on 4 Nov 2026 on branch `p7-v8.9`.
  - Author: `Numista Deployer <deploy@numista.ai>`.
  - Commit Message: `chore: auto-backup 2026-11-04 18:00`.
  - Files touched: Exactly 0 lines of source code touched. Captured repository documentation and active batons as part of the scheduled hourly automated backup cron.
  - Verification: `git diff 3936ba5f~1 3936ba5f -- numista_mobile/lib/` returns 0 changes.

---

## 3. NET-780b v1.1 Must-Fix Verification
- **MF-B1 (`kFallbackUsMintSkus` type & import):** Added `kFallbackUsMintSkus` issue price getter or `['issue_price']` with `_parseNumber`, and added the required import of `add_coins_hub.dart` into `my_collection_screen.dart`.
- **MF-B2 (26EA Year resolution & text fallback):** Read `numista_mobile/assets/guest_demo_coins.json` read-only, quoted verbatim keys demonstrating absence of `Title`/`title`, added regex extraction of year from text/subject (`RegExp(r'\b(1[7-9]\d{2}|20\d{2})\b')`), and added `hasUserUploadedPhotos` guard so stock images never overwrite user photos.
- **MF-B3 ($95.00 issue price dropped):** Dropped unsupported $95.00 issue price assumption. When no official issue price is present in SKU data, renders gold-styled `"Valuation Pending"` chip instead of an invented valuation.
- **MF-B4 (Never show purchase price as "Value"):** Strictly decoupled purchase cost from valuation. If user entered purchase price, labeled explicitly as `"Cost: $XX.XX"`, never as `"Value"`.
- **Advisories:** Fixed mojibake `5A` to `5¢`, verified nickel assets, corrected test path to `test/services/canonical_mint_asset_service_test.dart`.

---

## 4. NET-780c v1.1 Must-Fix Verification
- **MF-C1 (Closed CSP / Deleted Section 3D):** Deleted Section 3D completely. CSP remains 100% closed; zero external image hosts added.
- **MF-C2 (Real inventory counts):** Cited dated files `1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv` (8,945 files / 420 folders) and `numista_backend/gcs_full_inventory.csv` (11,069 objects). Itemized counts across all 353 collection cards and 3,202 catalog entries.
- **MF-C3 (Missing images list & acquisition):** Referenced `docs/MISSING_IMAGES.csv` (3,202 items) and phased acquisition plan ($0 cost).
- **MF-C4 (Licensing metadata):** Standardized metadata fields (`author`, `license`, `source_url`, `retrieval_date`), limited strictly to PD/CC0/CC-BY/CC-BY-SA, with attribution chip rendered in UI.
- **MF-C5 (Strict PII gate):** Named all excluded folders (`AJ's Coins/`, `Scans AJ June 2026/`, `AJ_Photos/`, `RECEIPTS/`, `INVOICES/`, `PACKING_SLIPS/`, `User_Uploads/`, `Row 10 Eric's microscope photos/`), documented 109 quarantined laptop files and 138 quarantined GCS upload files, and proved 0-hit intake manifest.
- **MF-C6 (CSP citation & single bucket):** Pinned to `numista_mobile/firebase.json:275-276` and single mirror bucket `gs://numista-catalog-assets`.

---

## 5. Next Steps
Handing off to Argon for re-review via `BATON_NET-791_ARGON_REVIEW_780b-780c_v1.1_2026-11-05-1255.md`.
AG CoS v4 advances immediately to `BATON_NET-798` (Unified Coin Details View Plan + EGM Gate).
