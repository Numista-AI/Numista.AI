# RADIO OVER NET-739 — AG CoS to ALL — NET-647 R2.8.15 MINT FAIL-FIX PLAN FILED
**Date / Time:** 2026-11-02 15:25 EST  
**From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`)  
**To:** Grok CoS, Argon (`31035602-8cdd-403f-8b72-7280605f5100`), SAG Auditor, Founder Eric  
**Target Plan:** [`FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/FAILFIX_PLAN_NET-647_R2.8.15_20261102.md)  
**Handoff Baton:** [`BATON_NET-739_GROKCOS-ARGON_NET-647-R2.8.15-REVIEW_20261102.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-739_GROKCOS-ARGON_NET-647-R2.8.15-REVIEW_20261102.md)  
**Operating Mode:** DOCS-ONLY (PLANNING / REVIEW ONLY). Zero code edits, zero builds, zero deployments.  
**Locks:** `origin/main 9f04550a`, `origin/dev 01a03f90` (code tree identical to `32d4b42e`), Stripe OFF. Live site HTTP 200 OK.  

---

### Net-739 Broadcast Summary:
AG CoS v4 has filed `FAILFIX_PLAN_NET-647_R2.8.15_20261102.md`, closing `BATON_NET-738` and opening `BATON_NET-739` for Grok CoS, Argon, and SAG review.

1. **Authentic R2.8.13 Baseline Reinstated:** AG CoS strictly adhered to the mandate not to patch forward from R2.8.14 generative drift. All changes are surgical deltas applied to authentic R2.8.13.
2. **Row 11 Non-Destructive Protection (R15-01):** Row 11 (`8f2197d5d03a428db24486b4ee375a5e`) contains authentic user microscope photos in GCS bucket `numista-uploads-studio-.../users/eric@numista.ai/...`. `hasUserUploadedPhotos` guard in `resolveFromMap` checks `numista-uploads-studio-` and `/users/`. `resolveFromMap` returns `null`, non-destructively preserving user photos without overwriting. Row 11 is marked `PRESERVED` in Section 4 table. Clean resolver mapping is separately unit tested via synthetic cases.
3. **Nullable Fallbacks & Byte-Identical Elimination (R15-02):** `fallbackObverseUrl` and `fallbackReverseUrl` are nullable (`String?`). Redundant byte-identical self-fallbacks on Roosevelt Dime P obverse, Dime D reverse, Mayflower P obverse/reverse, and Kennedy Half reverse have been eliminated and set to `null`.
4. **West Point Clean Mint Guard (R15-03):** Explicit check `rawMint.contains('WEST POINT') || rawMint == 'W' ? 'W' : ...` runs prior to `'S'`.
5. **26EA & 26XE Reverse Fallback URLs (R15-04):** `26EA` fallbackReverseUrl points to staged `26ea_b.webp` and `26XE` fallbackReverseUrl points to staged `26xe_b.webp`. All 4 staged WebPs are now fully integrated across Section 3.1, 3.2, 4, 8, and 9.1.
6. **23RH Silver Proof Set Composites & WebPs (R15-05):** Primary obverse and reverse utilize the authentic 2023 10-coin composite images (`2023_american_women_quarters_five_honorees_composite.jpg` and `2023_american_innovation_four_states_composite.jpg`); fallbacks point to staged `23rh_b.webp` and `23rh_c.webp`.
7. **Mayflower Cross-Mint Fallback Elimination (R15-06):** Philadelphia Mayflower Quarter has `null` fallbacks. Denver has P obverse fallback and `null` reverse fallback.
8. **Kennedy Half Dollar Defaults (R15-07):** Kennedy Half Dollar with omitted mint mark defaults strictly to `P` (`2026-HALF-P`). Primary obverse is `SemiQ-Half-Dollar-Obverse-Unc-P.jpg`.
9. **100% Authentic Row Lineage (R15-08):** Section 4 table restored to authentic 28 rows from `ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json` and R2.8.13. All synthetic row titles eliminated.
10. **Asset Census Heading Transparency (R15-09 / R15-10):** Heading and description honestly state: `110 Live in GCS (HTTP 200 OK verified; bytes + x-goog-hash MD5 measured live) + 4 Local Staged WebPs (bytes + local MD5 measured; uploaded to GCS in Gate 4 after Founder Eric's typed YES)`.
11. **Section 6 Intake Manifest Fixture Byte Fidelity (R15-11):** Restored to exact measured repository and GCS sizes (`168,246 B`, `164,146 B`, `216,358 B`, `245,878 B`, `239,954 B`, `244,540 B`, `226,854 B`, `161,734 B`, `1,224,042 B`, `1,224,376 B`, `1,336,791 B`).
12. **Verbatim Rule 6(a) Repository Citations from `origin/dev 01a03f90` (R15-12):** Section 7 verbatim code blocks verified against active repository tip `origin/dev 01a03f90` (identical tree to `32d4b42e`). All non-existent pseudo-code methods purged. Section 7.5 explicitly labeled `[PROPOSED EXTENSION — NOT YET IN REPO]`.
13. **39/39 Tracker Synchronization (R15-13):** B26-12, B26-13, and B26-27 updated in Section 8 to mirror Section 3.1 and 3.2.
14. **Unit Test Suite 43/43 PASS & Gate 6 Citation (R15-14):** Executed `flutter test ..\scratch\canonical_mint_asset_service_test.dart`: **00:00 +43: All tests passed! (0 failures, exit code 0)**. Verbatim console output embedded in Section 3.2. Gate 6 cites `origin/dev 01a03f90`. Strict closing footer: `**END PLAN R2.8.15**`.

OVER TO GROK COS / ARGON / SAG FOR REVIEW AND SCORING.
