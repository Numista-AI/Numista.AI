# BATON NET-741 — GROK COS & ARGON — NET-647 R2.8.16 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-02 16:25 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.16_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/FAILFIX_PLAN_NET-647_R2.8.16_20261102.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 3 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments. Docs commits to `dev` only, never `p7-v8.9`.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Executive Context:
Plan R2.8.16 was constructed strictly and surgically by applying **ONLY MF-1 through MF-4** onto `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`, as ordered by Grok CoS in BATON NET-740 and Argon in `GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md`. All 28 A4 rows, A3.2 unit test rows, and A7 code blocks were preserved with zero structural drift.

### Summary of Completed Surgical Fixes (MF-1 through MF-4):
1. **MF-1 — Section 4 Rows 01, 02, 26, 28 Staged & Composite Fallbacks Synchronized (§4 L1188, L1189, L1213, L1215):**
   - **Row 01 (`26EA`):** Fallback reverse explicitly mapped to `reference_library/us_mint_official/2026_products/26ea_b.webp` (`164,146 B`, MD5: `62ad11e997ac0320b57091e3d108d3e0`, `STAGED Gate 4`).
   - **Row 02 & Row 26 (`26XE`):** Fallback reverse explicitly mapped to `reference_library/us_mint_official/2026_products/26xe_b.webp` (`245,878 B`, MD5: `3a77694c9a72e6db63811c8b001edbb5`, `STAGED Gate 4`).
   - **Row 28 (`23RH`):** Primaries updated to real GCS composite JPG bytes/MD5s:
     - Primary Obverse: `reference_library/2023_series/2023_american_women_quarters_five_honorees_composite.jpg` (`711,501 B`, MD5: `1e65934dcab1944ff7010883690ac67d`, `HTTP 200 LIVE`).
     - Primary Reverse: `reference_library/2023_series/2023_american_innovation_four_states_composite.jpg` (`584,055 B`, MD5: `beb40fba68bde1460c865c5d7d54d8a6`, `HTTP 200 LIVE`).
     - Fallbacks: `23rh_b.webp` (`226,854 B`, MD5: `8a2060d0ca...`, `STAGED Gate 4`) and `23rh_c.webp` (`161,734 B`, MD5: `08f5b5aaf6...`, `STAGED Gate 4`).

2. **MF-2 — Section 4.1.3 Storage Census Table Restored to Full 114 Rows (§4.1.3 L1237–L1365):**
   - Heading reconciled to single truthful count: Exactly **114 Total Reference Suite Paths** (**110 Live in GCS HTTP 200** + **4 Staged WebPs** scheduled for Gate 4 upload).
   - Stale narrative bullets (108 objects / 104 paths) fully purged.
   - Restored complete 114-row census table from R2.8.14.
   - Rows 111–114 explicitly list honest status `STAGED (Gate 4 Upload)` with measured local bytes and MD5 digests (`26ea_b.webp`: `164,146 B`, `26xe_b.webp`: `245,878 B`, `23rh_b.webp`: `226,854 B`, `23rh_c.webp`: `161,734 B`).

3. **MF-3 — Resolver Safety & Redundant Fallback Elimination (§3.1 L151–L206, §3.2 L223–L1145, §4 L1194–L1214):**
   - **Service Code (§3.1):** Removed `$notes` from `extractSku` (`final combined = '$prog $theme $title';`). Redundant self/cross fallbacks nulled out in `26SQRP`, `26RH`, `1962-LINCOLN-1C`, and `ATB`.
   - **Unit Tests (§3.2):** Replaced fallback asserts with `expect(pair.fallbackReverseUrl, isNull);`. Added Row 11 Reference Resolution test (`Row 11 Reference Resolution: 2026-HALF-D Catalog Lookup (Without User Photos)`).
   - **Terminal Verification:** Executed `flutter test ..\scratch\canonical_mint_asset_service_test.dart` from `numista_mobile`: **44/44 tests passed (0 failures, exit code 0)**. Verbatim console output embedded in §3.2.
   - **Section 4 Table:** Fallback Reverse column updated to `None` (null - duplicate eliminated) for Rows 07, 13–17, 18, 19, 20–24, and 27.

4. **MF-4 — Cross-Section Consistency, Section 8 Sync & Gate 6 Sync (§1 L15–L88, §4.1.1 L1220–L1233, §8 L1620–L1664, §9.2 L1723):**
   - **Section 4.1.1:** Reconciled Row 11 Half Dollar specification: preserves Founder Eric's microscope photos via `hasUserUploadedPhotos` guard, while documenting clean catalog lookup for `2026-HALF-D` with nullable fallback reverse.
   - **Section 8 (39/39 Matrix):** Header updated to `Resolution in R2.8.16`. Synchronized rows B26-1, B26-2, B26-6, B26-7, B26-12, B26-13, B26-15..B26-27 with Section 3 and Section 4.
   - **Section 9.2 (Gate 6):** Repository tip updated to active tip `origin/dev 01a03f90`.
   - **Section 1 (Deliberation Matrix):** Cites exact changed line numbers for all R2.8.16 fixes (R16-01 through R16-04). Plan footer terminates cleanly with `**END PLAN R2.8.16**`.

---

### Instructions for Grok CoS / Argon / SAG:
1. Review `FAILFIX_PLAN_NET-647_R2.8.16_20261102.md`.
2. Confirm all items scored $\ge 95/100$ PASS.
3. Upon consensus PASS ($\ge 95$), stage plan for Founder Eric's morning typed `YES`.

## Log
- 2026-11-02 4:25 PM EST | AG CoS v4 (`ba2bfdb2`) | Opened BATON_NET-741 for Grok CoS and Argon review of R2.8.16.
