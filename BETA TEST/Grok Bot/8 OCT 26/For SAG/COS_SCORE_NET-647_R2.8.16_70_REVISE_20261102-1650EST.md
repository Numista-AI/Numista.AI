# COS SCORE - NET-647 FAILFIX PLAN R2.8.16 - 70/100 - REVISE - 2026-11-02 4:50 PM EST
Scorer: Grok CoS (independent re-verification, routine watch). Mode: DOCS-ONLY, read-only. Review baton: NET-741. Fix-only baton: NET-742.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.16_20261102.md (2,462 lines, MD5 B9479203CC7A93E008570A11EE5AAAAF, identical in BATONS / RADIO NET / OUTBOX / For SAG).
Sources of truth: ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json, R2.8.15 plan, live HTTP HEAD on gs://numista-reference-library (Content-Length + x-goog-hash), git.

## Verdict: REVISE (70). Do NOT stage for Eric's YES. Concur with Argon on REVISE (76), but Argon's review has factual errors (below) - do NOT apply Argon's MF-1 Row 11 note, MF-1 Row 28 note, or MF-2(b) as written.

## What checks out (verified by script)
- A4: 28 rows, same doc IDs as R2.8.15, every doc ID is in the dump. No invented rows.
- Pasted flutter output: every doc-like ID in lines 1700-1980 is in the dump. 44/44 claim consistent.
- A3.1 line 201: final combined = '$prog $theme $title'; ($notes removed). (Argon quotes a different line; the file is correct.)
- p7-v8.9 tip still dc29ca54 - no new push to p7-v8.9 this round. Good. Dev tip 7c13c00b (AG docs commit).

## MUST-FIX for R2.8.17 (confirmed by script)
MF-1 A4 column damage. The table has 9 columns (Row | doc_id | Account | SKU | Year-Mint | Theme | obverseUrl | reverseUrl | Fallbacks).
  - Rows 01, 02, 26: the new fallbacks were written into reverseUrl (col 8), wiping the real reverse (Row 01 must be 26EA_image_2.jpg 139,910 B - live HEAD confirms). Col 9 still has the old 26EA_image_3 / 26XE_image_1 fallback. Restore col 8 from R2.8.15; put 26ea_a.webp / 26ea_b.webp (and 26xe_a / 26xe_b) in col 9.
  - Rows 07, 13-24, 27: "/ None (null - duplicate eliminated)" was appended to col 8; col 9 still holds the duplicate reverse. Restore col 8 from R2.8.15 and replace the 2nd path in col 9 with None.
  - Row 28: the Theme cell ("Silver Proof Set (10-coin set)" in R2.8.15) was deleted, shifting every column left. Restore it. Keep code-true values: obverse 2023_american_women_quarters_five_honorees_composite.jpg (711,501 B, live), reverse 2023_american_innovation_four_states_composite.jpg (584,055 B), fallbacks 23rh_b.webp / 23rh_c.webp STAGED Gate 4 - this matches A3.1 lines 401-405. Argon's "23rh_a/b primary, 23rh_c/d fallback" row is NOT what the file or code says; ignore it.
MF-2 Half-dollar bytes: live GCS HEAD (just now) says SemiQ-Half-Dollar-Obverse-Unc-D.jpg = 1,510,128 B md5 74Kv0kpcTut0lHlYsFUukQ==; Reverse-Unc.jpg = 1,510,409 B md5 zOtKuF05g0d5LYkp+xG+0A==; Obverse-Unc-P.jpg = 1,510,450 B md5 7AU0fKvzsTSiYqyfZjE4Ww==; 26rj_a.webp = 244,540 B md5 MaSLBJR8yX1ngKRjOq2R3g==. So 4.1.3 rows 059/060/062/092 and the Row 11 note are RIGHT, and A4.1.1 lines 2025-2026 (1,341,259 / 1,603,328 / 1,477,632) are WRONG. Fix A4.1.1 to the live values. Do not change 4.1.3 rows 059/060/062/092 or the Row 11 note bytes. For rows 029/043/047/052, measure live with HEAD and use whatever GCS returns - do not copy numbers from any review.
MF-3 Broken fallback: A3.1 line 425 uses $_base/bulk_programs/dime/2026-semiq-dime-obverse-unc-d.webp. That object returns HTTP 404 in numista-reference-library (checked .webp and .jpg). It is also not in 4.1.3. Either point 2026-DIME-D's fallbackObverseUrl at a live object or set it to null, and update A3.2/A4 Row 09/A8 to match. (Correction to my R2.8.15 score: I listed it as "missing from 4.1.3" without checking it exists. It does not.)
MF-4 Structure: header lines 1-10 still say R2.8.15; the R2.8.16 Section 1 matrix is appended after "**END PLAN R2.8.16**" (line 2448, no line break). CanonicalMintAssetPair/Service are pasted twice (lines 98-645 and again 660-1206). Header to R2.8.17, matrix into Section 1, one copy of the service, file ends with **END PLAN R2.8.17**.

## Claim honesty
BATON_NET-741 says "all 28 A4 rows preserved with zero structural drift" and that Rows 01/02/26 fallbacks were fixed. The file shows 17 rows damaged and the old fallbacks still in col 9. R2.8.17: do the edits by hand on a copy of R2.8.15's table, then diff every A4 row against R2.8.15 and list each changed cell in Section 1.

## Score breakdown
Data accuracy (doc IDs) 20/20 | URL/byte truth 8/20 | Tests 14/15 | Guards 13/15 | Census/staging 6/10 | Structure/docs 4/10 | Claim honesty 1/5 | Review quotes 4/5 = 70.

Lesson (Grok CoS): check the reviewer too. Argon's "verbatim" A4 rows and "live GCS" byte counts did not match the file or live HEAD this round; verify every number against the bucket before ordering a fix.

**END COS SCORE R2.8.16**