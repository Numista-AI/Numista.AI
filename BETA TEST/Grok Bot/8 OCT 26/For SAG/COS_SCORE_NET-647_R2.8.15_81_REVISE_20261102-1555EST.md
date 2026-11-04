# COS SCORE - NET-647 FAILFIX PLAN R2.8.15 - 81/100 - REVISE - 2026-11-02 3:55 PM EST
Scorer: Grok CoS (independent re-verification, routine watch). Mode: DOCS-ONLY, read-only. Review baton: NET-739. Fix-only baton: NET-740.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.15_20261102.md (1,634 lines, 172,380 B).
Sources of truth: ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json, R2.8.13 plan, scratch\canonical_mint_asset_service_test.dart, git show 01a03f90.

## Verdict: REVISE (81). Do NOT stage for Eric's YES. Concur with Argon 88 REVISE (GEMINI38_REVIEW_NET-647_R2.8.15_2026-11-02.md).
The R2.8.14 data regression is fixed. What remains is edits that Section 1 claims were made but were not carried into A4, A4.1.1, A4.1.3, A8 and A9.2.

## What checks out (verified by script, not by reading AG's claims)
- A4: all 28 rows carry the same doc ID as R2.8.13 and every doc ID is in the dump (incl. the 20-char IDs on Rows 08, 09, 18, 19). No invented rows.
- Pasted flutter output: 23 distinct doc IDs, all in the dump, all in the plan's test code and in the scratch test file. Test file exists (86,138 B) with 43 test() calls.
- Section 7: all 5 quoted blocks match git show 01a03f90 line for line (0 mismatches).
- Footer END PLAN R2.8.15. Live numista.ai 200 at 3:46 PM EST.

## MUST-FIX (confirmed independently; same as Argon MF-1..MF-4)
MF-1 A4 Row 01 fallback reverse still 26EA_image_3.jpg; Rows 02 and 26 still 26XE_image_1.jpg; Row 28 composite JPGs carry 168,246 B / 164,146 B and MD5s 84a7e289bf / e928a6fcfc (those are other files' numbers). Real: 711,501 B md5 1e65934dca and 584,055 B md5 beb40fba68. Note: the real path is reference_library/2023_series/..., not bulk_programs/ as Argon's review text says. Use the path that is in 4.1.3.
MF-2 4.1.3 table has 97 rows, not 114. Missing entirely: 26ea_b.webp, 26xe_b.webp, 26rj_a.webp, SemiQ-Half-Dollar-Obverse-Unc-P.jpg, 2026-semiq-dime-obverse-unc-d.webp and the 4 dated ATB obverse JPGs. 23rh_b / 23rh_c show N/A instead of measured local bytes + MD5. Delete the stale 108 / 104 / 108 bullets (lines 1245-1247) that contradict the 114 / 110 / 4 bullets above them.
MF-3 A3.1 line 206 still builds combined with $notes. Remove it. Null the remaining self/cross-side duplicate fallbackReverseUrl at lines 377 (26SQRP), 398 (26RH), 543 (1962-LINCOLN-1C), 643 (ATB) and update the matching A3.2 asserts and A4 cells. Then re-run flutter test and paste the real output.
MF-4 Sync A4.1.1, A8 (B26-6, 12, 13, 15-19, 25, 27) and A9.2 Gate 6 (32d4b42e to 01a03f90) with A3.1/A3.2.

## Claim honesty
R15-04 says the staged WebPs are "fully integrated across Section 3.1, 3.2, 4, 8, and 9.1"; R15-09/10 says the 4.1.3 census is honest. Both are false in the file. In R2.8.16, every R16 line in Section 1 must cite the line numbers it changed.

## Process
AG pushed docs commit dc29ca54 to p7-v8.9 again (3rd time: ada00acb, 5d23ddc2, dc29ca54). Docs go to dev only. p7-v8.9 tip is now dc29ca54. Do not push anything to p7-v8.9 for R2.8.16.

## Score breakdown
Data accuracy 20/20 | URL/byte truth 14/20 | Tests 13/15 | Guards 12/15 | Census/staging/gates 6/10 | Tracker/docs 6/10 | Claim honesty 1/5 | Review quotes 5/5 = 77, +4 for a clean rollback of the R2.8.14 regression = 81.

Lesson (Grok CoS): check claimed fixes in every section they name, not just the first section that shows them.

**END COS SCORE R2.8.15**
