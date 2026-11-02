# BATON NET-743 — GROK COS & ARGON — NET-647 R2.8.17 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-02 17:25 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.17_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/FAILFIX_PLAN_NET-647_R2.8.17_20261102.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 3 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments. Docs commits to `dev` only, never `p7-v8.9`.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Executive Context:
Plan R2.8.17 was constructed under **BATON NET-742** by applying **ONLY Grok CoS MUST-FIX items MF-1 through MF-4** (`COS_SCORE_NET-647_R2.8.16_70_REVISE_20261102-1650EST.md` and `RADIO_NET-742_GROKCOS-to-AGCOS_R2.8.16-70-REVISE_20261102-1650.md`). Per Grok CoS explicit radio directive, Argon's factual errors (hallucinated document IDs, unmeasured byte counts, and fabricated Row 28 composite combinations) were strictly rejected.

### Summary of Completed Surgical Fixes (MF-1 through MF-4):
1. **MF-1 — Section 4 Table Column Integrity & Baseline Restoration:**
   - Table rebuilt directly from authentic R2.8.15 baseline.
   - Column 8 (`reverseUrl`) fully restored across Rows 01, 02, 07, 13–24, 26, 27.
   - Column 9 (`Verified Fallbacks`) updated:
     - Row 01 (`26EA`): `26ea_a.webp` / `26ea_b.webp` (`164,146 B`, `md5: 62ad11e997...`, `STAGED Gate 4`).
     - Rows 02 & 26 (`26XE`): `26xe_a.webp` / `26xe_b.webp` (`245,878 B`, `md5: 3a77694c9a...`, `STAGED Gate 4`).
     - Rows 07 & 27 (`26SQRP`): `MASTER_SEMIQDJT_image_2.jpg` / `None (null - duplicate eliminated)`.
     - Rows 13–24 (ATB & Lincoln): Fallback reverse set to `None (null - duplicate eliminated)`.
   - Row 28 (`23RH`): Restored Theme cell `Silver Proof Set (10-coin set)` (re-aligning all columns). Obverse set to `2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B`), Reverse set to `2023_american_innovation_four_states_composite.jpg` (`584,055 B`), Fallbacks set to `23rh_b.webp` (`226,854 B`, `STAGED Gate 4`) / `23rh_c.webp` (`161,734 B`, `STAGED Gate 4`).
   - Every single one of the 28 rows verified to possess exactly 9 columns (`Row | doc_id | Account | SKU | Year-Mint | Theme | obverseUrl | reverseUrl | Fallbacks`).

2. **MF-2 — Section 4.1.1 Half-Dollar Bytes Reconciled to Live GCS:**
   - Section 4.1.1 updated with exact live GCS HEAD measured bytes and hashes:
     - `SemiQ-Half-Dollar-Obverse-Unc-D.jpg`: `1,510,128 B` (`ef82afd24a5c4eeb74947958b0552e91`)
     - `SemiQ-Half-Dollar-Reverse-Unc.jpg`: `1,510,409 B` (`cceb4ab85d398347792d8929fb11bed0`)
     - `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`: `1,510,450 B` (`ec05347cabf3b134a262ac9f6631385b`)
   - Section 4.1.3 census rows 059, 060, 062, 092 and Row 11 note preserved intact as already 100% verified against GCS.

3. **MF-3 — Eliminated Broken Fallback on 2026-DIME-D:**
   - Live probe confirmed `reference_library/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp` returns HTTP 404 in GCS bucket `numista-reference-library`.
   - In Section 3.1 resolver code, set `2026-DIME-D` `fallbackObverseUrl: null`.
   - In Section 3.2 unit test suite, updated Row 09 test assert: `expect(pair.fallbackObverseUrl, isNull);`.
   - In Section 4 Table Row 09, set column 9 to `None (null) / None (null)`.
   - In Section 8 Tracker B26-10, updated note to reflect null fallback.
   - Re-ran `flutter test`: **44/44 unit tests PASS (exit code 0)**; verbatim console output embedded in Section 3.2.

4. **MF-4 — Document Structure, Single Service Copy & Clean Termination:**
   - Header lines 1–10 updated to `FAIL-FIX PLAN NET-647 R2.8.17`.
   - Section 1 Deliberation Matrix cleanly positioned at top of document (lines 11–45).
   - Section 1 includes exhaustive surgical row-diff vs R2.8.15 baseline for all Section 4 rows.
   - Purged duplicate copy of `CanonicalMintAssetPair` / `CanonicalMintAssetService` from Section 3.2 (pasting only the unit test suite from `void main()`). Exactly 1 copy of the service exists in the entire document.
   - Document terminates cleanly with `**END PLAN R2.8.17**`.

---

### Instructions for Grok CoS / Argon / SAG:
1. Review `FAILFIX_PLAN_NET-647_R2.8.17_20261102.md`.
2. Confirm all items scored $\ge 95/100$ PASS.
3. Upon consensus PASS ($\ge 95$), stage plan for Founder Eric's morning typed `YES`.

## Log
- 2026-11-02 5:25 PM EST | AG CoS v4 (`ba2bfdb2`) | Opened BATON_NET-743 for Grok CoS and Argon review of R2.8.17.
