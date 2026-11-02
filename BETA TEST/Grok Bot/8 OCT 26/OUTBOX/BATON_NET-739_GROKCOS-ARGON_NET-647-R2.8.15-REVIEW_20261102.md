# BATON NET-739 — GROK COS & ARGON — NET-647 R2.8.15 MINT FAIL-FIX PLAN REVIEW
**Date / Time:** 2026-11-02 15:25 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/FAILFIX_PLAN_NET-647_R2.8.15_20261102.md)  
**Status:** ACTIVE REVIEW BATON (Scoring threshold: >= 95 PASS required for Gate 3 Founder Eric typed YES)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Executive Context:
Plan R2.8.15 was constructed strictly by applying surgical delta fixes onto the authentic, ground-truth **R2.8.13 baseline**, completely rejecting and eliminating the generative drift that occurred in R2.8.14.

### Reconciliation Highlights across All 14 Deliberation Items (R15-01 through R15-14):
1. **R15-01 (Row 11 Non-Destructive Protection):** Row 11 (`8f2197d5d03a428db24486b4ee375a5e`) contains authentic user microscope scans in GCS bucket `numista-uploads-studio-.../users/eric@numista.ai/...`. The `hasUserUploadedPhotos` guard in `resolveFromMap` now explicitly checks `numista-uploads-studio-` and `/users/`. `resolveFromMap` returns `null`, non-destructively preserving user photos without overwriting. Row 11 is marked `PRESERVED` in Section 4. Clean resolver mapping is separately unit tested via synthetic cases.
2. **R15-02 (Nullable Fallbacks & Byte-Identity Nullification):** `fallbackObverseUrl` and `fallbackReverseUrl` are now nullable (`String?`). Redundant byte-identical self-fallbacks on Roosevelt Dime P obverse, Dime D reverse, Mayflower P obverse/reverse, and Kennedy Half reverse have been eliminated and set strictly to `null`.
3. **R15-03 (West Point Guard):** Explicit check `rawMint.contains('WEST POINT') || rawMint == 'W' ? 'W' : ...` runs before checking for `'S'`, eliminating any substring misclassification.
4. **R15-04 (26EA & 26XE Reverse Fallbacks):** `26EA` fallbackReverseUrl points to staged `26ea_b.webp` and `26XE` fallbackReverseUrl points to staged `26xe_b.webp`. All 4 staged WebPs are now fully integrated across Section 3.1, 3.2, 4, 8, and 9.1.
5. **R15-05 (23RH Silver Proof Set Composites & WebPs):** Primary obverse and reverse utilize the authentic 2023 10-coin composite images (`2023_american_women_quarters_five_honorees_composite.jpg` and `2023_american_innovation_four_states_composite.jpg`); fallbacks point to staged `23rh_b.webp` and `23rh_c.webp`.
6. **R15-06 (Mayflower Quarter Cross-Mint Elimination):** Eliminated Denver unc obverse fallback from Philadelphia Mayflower. P has `null` fallbacks. D has P obverse fallback and `null` reverse fallback.
7. **R15-07 (Half Dollar Defaults):** Kennedy Half Dollar with omitted mint mark defaults strictly to `P` (`2026-HALF-P`). Primary obverse is `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`.
8. **R15-08 (100% Authentic Row Lineage):** Section 4 table contains 100% authentic 28 rows matching `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` and R2.8.13. All synthetic row titles from R2.8.14 are eliminated.
9. **R15-09 / R15-10 (Asset Census Transparency):** Section 4.1.3 table heading and description honestly state: `110 Live in GCS (HTTP 200 OK verified; bytes + x-goog-hash MD5 measured live) + 4 Local Staged WebPs (bytes + local MD5 measured; uploaded to GCS in Gate 4 after Founder Eric's typed YES)`.
10. **R15-11 (Section 6 Fixture Byte Fidelity):** All intake manifest fixture byte counts restored to exact measured repository and GCS sizes (`168,246 B`, `164,146 B`, `216,358 B`, `245,878 B`, `239,954 B`, `244,540 B`, `226,854 B`, `161,734 B`, `1,224,042 B`, `1,224,376 B`, `1,336,791 B`).
11. **R15-12 (Verbatim Rule 6(a) Repository Citations from `origin/dev 01a03f90`):** Section 7 verbatim code blocks verified against active repository tip `origin/dev 01a03f90` (identical tree to `32d4b42e`). All non-existent pseudo-code methods from R2.8.14 purged. Section 7.5 explicitly labeled `[PROPOSED EXTENSION — NOT YET IN REPO]`.
12. **R15-13 (39/39 Tracker Synchronization):** B26-12, B26-13, and B26-27 updated in Section 8 to mirror Section 3.1 and 3.2.
13. **R15-14 (Unit Test Execution & Gate 6 Citation):** Section 3.2 unit test suite executed cleanly via `flutter test ..\scratch\canonical_mint_asset_service_test.dart`: **43/43 tests passed (0 failures, exit code 0)**. Verbatim console output embedded in Section 3.2. Gate 6 cites `origin/dev 01a03f90`. Plan terminates strictly with `**END PLAN R2.8.15**`.

---

### Instructions for Grok CoS / Argon / SAG:
1. Review `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`.
2. Confirm all items scored $\ge 95/100$ PASS.
3. Upon consensus PASS ($\ge 95$), stage plan for Founder Eric's morning typed `YES`.

## Log
- 2026-11-02 3:25 PM EST | AG CoS v4 (`ba2bfdb2`) | Opened BATON_NET-739 for Grok CoS and Argon review of R2.8.15.
