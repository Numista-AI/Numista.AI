# BATON NET-737 — GROK COS & ARGON — NET-647 R2.8.14 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-02 13:45 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.14_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/RADIO%20NET/FAILFIX_PLAN_NET-647_R2.8.14_20261102.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 0 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Instructions for Grok CoS / Argon / SAG:
1. Verify all 6 MUST-FIX and 7 SHOULD-FIX items from `BATON_NET-736` and `SAG_REVIEW_NET-647-R2.8.13_72_REVISE.md`:
   - **MF1 (Row 28 Swap):** §4 table primary = 2023 composite JPGs (`2023_american_women_quarters_five_honorees_composite.jpg` & `2023_american_innovation_four_states_composite.jpg`); fallbacks = staged `23rh_b.webp` / `23rh_c.webp`. 100% aligned with §3.1 and test Row 28.
   - **MF2 (Path Census Single Source of Truth):** Exactly **114 Total Reference Suite Paths** (**110 Live in GCS HTTP 200** + **4 Staged WebPs** under Gate 0). Consistent throughout §1, §3.1, §4, §4.1.3, §8, and §9. Includes measured bytes and hex MD5s for all 114 paths (including `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`, `2013-S`, `2018-D`, `2019-D`, `2020-D` ATB obverses, and `26rj_a.webp`).
   - **MF3 (User-Upload Guard & Row 10/11 Preservation):** `hasUserUploadedPhotos` guard matches `numista-uploads-studio-`, `/users/`, `scan_source: microscope`, `studio-9101802118-8c9a8-uploads`, `/microscope/`, `/user_uploads/`, and inspects all image fields. Rows 10 and 11 both return `null`, preserving user microscope hardware scans non-destructively. In §4 table, both are marked **PRESERVED**.
   - **MF4 (§8 Tracker Synchronization):** §8 tracker matches §3.1 code for B26-1, 2, 6, 13, 15–19, 22–26.
   - **MF5 (extractSku Theme Matching):** `Personal Notes` purged from theme matching (`combined = '$prog $theme $title'`). Notes only scanned for explicit 4-char SKU tokens.
   - **MF6 (Mayflower P & Half Dollar Defaults):** Mayflower P fallback obverse set to `null` (no cross-mint D fallback). Half dollar with no mint mark defaults strictly to `2026-HALF-P` SKU and P obverse image.
   - **SF1 (Footer):** Strictly `**END PLAN R2.8.14**`.
   - **SF2 (Unit Test Count):** Exactly **43 Tests Total** (28 Live Docs + 15 Synthetic Cases). Real terminal output from `flutter test ..\scratch\canonical_mint_asset_service_test.dart` embedded showing 43/43 PASS exit code 0.
   - **SF3 (Byte-Identical Fallbacks Nullified):** Proved byte-identity via MD5s and set redundant fallbacks to `null` (dime P obverse, dime reverse, half reverse, Mayflower reverse, half dollar obverse).
   - **SF4 (West Point Guard):** Explicit check prevents "WEST POINT" being classified as `S`.
   - **SF5 (Code vs Test Unity):** Tests execute self-contained standalone Dart resolver class identical to §3.1.
   - **SF6 (Gate 6 Reference):** Corrected to `origin/dev 01a03f90`.
   - **SF7 (Live Firestore Read-Only Verification):** Real read-only terminal verification output for Docs 08, 09, 10, 11, 18, 19 embedded in §4.1.2.
   - **SF8 (Security Rule 2 Compliance):** Section 7.5 details and implements the redaction mechanism for receipt/invoice scans before storage.
2. File score and radio broadcast.
3. Upon all parties $\ge 95/100$ PASS, stage plan for Founder Eric's typed `YES`.
