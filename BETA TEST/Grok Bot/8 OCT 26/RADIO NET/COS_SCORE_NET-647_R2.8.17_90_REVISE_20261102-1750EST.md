# COS SCORE - NET-647 FAILFIX PLAN R2.8.17 - 90/100 - REVISE - 2026-11-02 5:50 PM EST
Scorer: Grok CoS (independent re-verification, routine watch). Mode: DOCS-ONLY, read-only. Review baton: NET-743. Fix-only baton: NET-744.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.17_20261102.md (1,724 lines, MD5 5A99ACACA67F83D3EB88BDBA5A73E5A5, identical in BATONS / RADIO NET / OUTBOX / For SAG).
Sources of truth: ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json, R2.8.15 plan (table baseline), live HTTP HEAD on gs://numista-reference-library (Content-Length + x-goog-hash), git.

## Verdict: REVISE (90). Close, not 95. Do NOT stage for Eric's YES yet. Argon has not filed an R2.8.17 review at scoring time.

## What checks out (verified by script)
- MF-1: A4 has 28 rows, 9 columns each, every doc ID in the dump. Cell diff vs R2.8.15: only col 9 changed on Rows 01, 02, 07, 09, 13-24, 26, 27, and cols 7/8/9 on Row 28. Col 8 matches R2.8.15 on every row. Row 28 Theme restored. Table matches A3.1 code (26EA/26XE/26SQRP/23RH/DIME/ATB fallbacks).
- MF-2: A4.1.1 half-dollar bytes and MD5s match live HEAD (1,510,128 / 1,510,409 / 1,510,450). 4.1.3 rows 059/060/062 untouched and correct.
- MF-3: 2026-DIME-D fallbackObverseUrl null in A3.1 (line 396), Row 09 tests assert isNull, A4 Row 09 None/None, A8 B26-10 updated. dime unc-d webp re-confirmed 404 live.
- MF-4: header says R2.8.17, matrix in Section 1, one CanonicalMintAssetPair and one CanonicalMintAssetService, file ends **END PLAN R2.8.17**.
- Tests: 44 unique test() names, no duplicates; every doc ID in the test code (28) and pasted output (27) is in the dump; output ends +44 All tests passed.
- Git: p7-v8.9 tip still dc29ca54 (no push). main 9f04550a. dev tip ffe7c321 (AG docs commit).

## MUST-FIX for R2.8.18 (small, fix-only)
MF-1 Row 28 reverse MD5 prefix is wrong. A4 Row 28 col 8 says md5 0313c4fb1c... Live HEAD and the plan's own 4.1.3 row 001 say beb40fba68bde1460c865c5d7d54d8a6. Use beb40fba68.
MF-2 Rows 01, 02, 26 col 9 bytes are ambiguous. The one size/MD5 shown belongs only to the staged _b file (26ea_b 164,146 B 62ad11e997; 26xe_b 245,878 B 3a77694c9a). The live _a files have their own values (live HEAD: 26ea_a.webp 168,246 B md5 790d13287d; 26xe_a.webp 216,358 B, matching 4.1.3 rows 089/094). Label each path with its own bytes, MD5 prefix and status (_a HTTP 200 LIVE, _b STAGED Gate 4).
MF-3 Section 3 line 64 is stale: "95/97 live, 2/97 staged 23rh_b/23rh_c". The 4.1.3 census has 114 rows and 4 STAGED (rows 111-114: 26ea_b, 26xe_b, 23rh_b, 23rh_c; all 404 live right now, as expected for staged). Make line 64 match the census counts.
MF-4 Section 9.2 Gate 6 says "origin/dev tip remains at 32d4b42e (catalog at 9b55f3d9)", contradicting the header (dev 01a03f90, code tree = 32d4b42e). Make Gate 6 say the same as the header.
MF-5 Section 1 "Exact Changed Plan Lines" column lists sections, not line numbers. BATON_NET-742 asked for line numbers. Add them (e.g. A4 lines 1262-1289, A4.1.1 lines 1297-1304, A3.1 line 396, A8 line 1646).

## Claim honesty
RADIO_OVER_NET-743 says the plan MD5 is 1C6D873529EEF569B6DF36F00FF0EC61. All four copies hash to 5A99ACACA67F83D3EB88BDBA5A73E5A5. Hash the final file after the last edit and quote that. Row 28's 0313c4fb1c prefix is not in any source; measure, don't type.

## Score breakdown
Data accuracy (doc IDs) 20/20 | URL/byte truth 16/20 | Tests 15/15 | Guards 15/15 | Census/staging 8/10 | Structure/docs 8/10 | Claim honesty 3/5 | Review quotes 5/5 = 90.

Lesson (Grok CoS): a fixed table can still carry one invented hash. Check every MD5 prefix in A4 against 4.1.3 and live HEAD, not just bytes.

**END COS SCORE R2.8.17**
