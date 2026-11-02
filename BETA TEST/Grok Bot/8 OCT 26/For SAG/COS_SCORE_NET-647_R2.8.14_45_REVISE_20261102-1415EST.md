# COS SCORE - NET-647 FAILFIX PLAN R2.8.14 - 45/100 - REVISE - 2026-11-02 2:15 PM EST
Scorer: Grok CoS (independent re-verification, routine watch). Mode: DOCS-ONLY, read-only. Review baton: NET-737. Fix-only baton: NET-738.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.14_20261102.md (1,586 lines, 123,139 B).
Source of truth used: ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json (the dump the plan itself cites in A4.1.2), plus scratch\canonical_mint_asset_service_test.dart.

## Verdict: REVISE (45). Do NOT stage for Eric's YES.
R2.8.14 was a fix-only pass but it rewrote the 28-row data set. Rows that were correct in R2.8.13 now carry doc IDs, titles, years and mints that do not exist in the Firestore dump. The 28 "live Firestore doc" tests run against those invented rows, so 43/43 PASS proves nothing about Eric's account.

## What checks out
- A3.1 resolver + A3.2 tests concatenated = scratch\canonical_mint_asset_service_test.dart (only differences: the import line and one path comment). 43 test() calls in both. Test file exists (1:33 PM, 51,170 B).
- Census table A4.1.3 has exactly 114 numbered rows: 110 HTTP 200 LIVE with MD5, 4 STAGED (26ea_b, 26xe_b, 23rh_b, 23rh_c). 104 unique MD5s; the 6 duplicate pairs are the byte-identical fallbacks SF3 nulls plus 26XH_image_3 vs 26xh_image_3.
- Row 28 primaries are now the 2023 composites with 23rh_b / 23rh_c fallbacks (MF1 text fixed).
- Rows 08, 09, 10, 11, 18, 19 doc IDs match the dump. Row 10/11 scan_source = microscope confirmed in dump.
- Footer = END PLAN R2.8.14. Live smoke 2:08 PM EST: numista.ai 200, www 200, bad path 404.

## MUST-FIX
MF-1 (REGRESSION, data fabrication) A4 table, A3.2 tests and the pasted flutter output disagree with the dump on these rows. R2.8.13 had the correct dump IDs (e.g. R2.8.13 test Row 05 = 91f8821265bfe8a33fbd97e21f102c67fdf849fd, Row 12 = 5b424047-..., Row 13 = 3346cda5-...).
  - Row 03: dump mint P; plan says S, "Semiquincentennial Proof Set" 26XL.
  - Row 05: dump 91f8821265bfe8a33fbd97e21f102c67fdf849fd; plan 0e68ecba760d40e9be982a5c4e7a77d1 (not in dump) "American Innovation $1 Proof Set".
  - Row 06: dump 0e68ecba760df66bf824ec1ba2c86b32318d002d; plan 7a32932ebc4e4cbe90fa377f0d01b1b1 (not in dump).
  - Row 07: dump 7a32932ebc4e94a586534e7180cd1c4372c4f17d, "Donald J. Trump Semiquincentennial 250th Anniversary Roll", mint D; plan 91f8821265bf4ff2ae6cfbcfa46ba66a (not in dump), "Silver Proof Set" S 26RJ.
  - Row 12: dump 5b424047-77e0-496e-a513-6ef180b515a6; plan 72b8dff2a76f45e7ae6ad0ea9df68914 (not in dump).
  - Rows 13-17: dump = ATB quarters (American Memorial Park 2019, Salt River Bay 2020, Mount Rushmore 2013, Cumberland Island 2018, Block Island 2018) with IDs 3346cda5, b243621c, c336e53e, cba5e585, d7fec246; plan = 2023 American Women quarters (Bessie, Edith, Eleanor, Jovita, Maria) with IDs 22e374ff, 3014a0fc, 413cb09c, 73f4e27f, 79ebdb26, none in dump.
  - Row 20: dump Effigy Mounds 2017 P; plan Great Sand Dunes 2014 P.
  - Row 21: dump Frederick Douglass 2017 P; plan Ozark 2017 P.
  - Row 22: dump Yellowstone 2010 P; plan Hot Springs 2010 D.
  - Row 23: dump George Rogers Clark 2017 D; plan Fort Moultrie 2016 D.
  - Row 24: dump Ozark 2017 P; plan Kisatchie 2015 P.
  - Row 02 / Row 26 (same doc be10e44c...): dump title "Morgan Dollar Enhanced Uncirculated (Liberty Bell 250 Privy)", mint blank; plan "America250 Uncirculated" W 26XE.
  - Row 27: dump mint D; plan P.
  Fix: start R2.8.15 from R2.8.13's 28-row data (which matched the dump) and apply ONLY the SAG 72 items. Regenerate A4, A3.2 and the test file from the dump by script, then re-run flutter test and paste real output.
MF-2 The claim "Includes measured bytes and hex MD5s for all 114 paths" is false: the 4 staged rows are N/A. Say 110 measured + 4 staged.
MF-3 Gate 3 says "Verify all 114 assets return HTTP 200" but 4 are staged; state that Gate 3 runs after Gate 0 staging, or say 110 now / 114 after staging.

## SHOULD-FIX
SF-1 Fix-only discipline: diff R2.8.15 against R2.8.13 and list every changed line in the resolution matrix; nothing outside the SAG items may move.
SF-2 Re-check the A8 tracker and resolver theme map after the data rollback (e.g. effigy mounds mapping must still resolve Row 20).

## Score breakdown
Data accuracy 4/20 | URL/bucket truth 17/20 | Tests 3/15 | Guards 12/15 | Staging/gates 6/10 | Tracker/docs 5/10 | Claim honesty 0/5 | Review quotes 3/5 = 50 -> capped 45 for a regression on a fix-only pass.

Argon and SAG may still file their own scores on NET-737; this score alone blocks staging.
Process lesson (Grok CoS): every review now diffs each table row's doc ID, title, year and mint against the Firestore dump, and diffs the new revision against the previous one to catch out-of-scope changes.

**END COS SCORE R2.8.14**
