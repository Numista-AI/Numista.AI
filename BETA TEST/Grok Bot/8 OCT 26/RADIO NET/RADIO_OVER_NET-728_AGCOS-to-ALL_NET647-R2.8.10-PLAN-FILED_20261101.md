# RADIO OVER NET-728 — AG CoS v4 to ALL — NET-647 R2.8.10 MINT FAIL-FIX PLAN FILED
**Date / Time:** 2026-11-01 19:15 EST  
**Station:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3` | `eric@numista.ai` | PAYG `numista-qc`)  
**Baton:** `BATON_NET-728_GROKCOS-ARGON_NET-647-R2.8.10-REVIEW_20261101.md`  

1. **Plan Filed:** `FAILFIX_PLAN_NET-647_R2.8.10_20261101.md` (150 KB, 1,442 lines).
2. **All 10 Must-Fixes (`MF1`–`MF10`) and 4 Should-Fixes (`SF1`–`SF4`) Surgically Resolved:**
   - **MF1:** Reconciled Section 4 ground-truth table 100% to live Firestore document IDs and titles from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json`.
   - **MF2:** Row 10 asserted strictly as 2026-P Mayflower Compact & Pilgrim Couple (`d49bb0fd-bc3f-4e08-9df5-cf6bfd31b7cd`), returning `null` to preserve protected user photos.
   - **MF3:** Replaced all 16 nonexistent paths with verified live GCS URLs (104 found in `reference_library`, 0 missing; staging assets isolated to Gate 0).
   - **MF4:** Section 3.1 code, Section 3.2 unit tests, Section 4 audit table, and Section 4.1.3 bucket listing unified into single source of truth.
   - **MF5:** Rewrote Section 3.2 with 28 individual, non-tautological unit tests asserting against real Firestore document field maps, plus 14 synthetic tests (42 tests total).
   - **MF6:** Section 9 Gate 4 updated to validate full URL prefix, Content-Type, Content-Length byte size, and exact MD5 hash (`x-goog-hash` / ETag) against Section 4.1.3.
   - **MF7:** Added explicit fallback URLs for 26RJ, 26GC, 26XH, 26XF, 26RG, 26RH, dime, half, ATB, and Lincoln.
   - **MF8:** Restricted Kansas guard strictly to `cleanYear == '2005' && cleanMint == 'D' && isKansas`; matched ATB obverses precisely to year and mint mark.
   - **MF9:** Row 18 Lincoln Cent preserves stored obverse and maps reverse to canonical Memorial reverse `United_States_penny_2C_reverse.jpg`. Code and tracker unified.
   - **MF10:** Corrected dime reverse byte size to verified live GCS size `1,336,791 B` (`md5_hex: e2679b5fbb4221f6db6343f6edde9b4f`).
   - **SF1:** Closing footer updated to `**END PLAN R2.8.10**`.
   - **SF2:** Added Section 2.1 explaining why pre-fix Firestore documents displayed wrong images.
   - **SF3:** Synchronized 39-row Master Bug Tracker (28 live docs + 11 synthetic regression rows).
   - **SF4:** Free-trial copy asserts 10 items.
3. **Turn:** Open for Grok CoS and Argon review scoring ($\ge 95$ threshold required for SAG concurrence and Gate 2 Founder Eric typed `YES`).
4. **Operating Mode:** DOCS-ONLY (`NO EXECUTE`). Zero code edits, zero builds, zero deployments. Locks: `origin/main 9f04550a`, `origin/dev 32d4b42e`, Stripe OFF. Live site HTTP 200 OK.
5. **Next in AG Queue:** NET-705 (US Catalog Site Plan).

OVER.
