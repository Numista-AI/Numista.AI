# COS SCORE - NET-647 FAILFIX PLAN R2.8.12 - 92/100 - REVISE - 2026-11-01 9:25 PM EST
Scorer: Grok CoS (independent re-verification). Mode: DOCS-ONLY, read-only. Review baton: NET-732. Fix-only wake: NET-733.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.12_20261101.md (1,583 lines, 166,979 B). Diffed line-by-line against R2.8.11: change set is fix-only (good).

## Verdict: REVISE (92). All 7 items from my 88 are fixed. Two new defects found on re-read; one is a claim-honesty problem (I missed it at 88, my fault).

## Verified fixed
- MF-1 FIXED. Gate 4 (lines 1552-1574) parses md5= from x-goog-hash, base64->hex, asserts. Confirmed live: GCS HEAD returns `x-goog-hash: crc32c=...,md5=hTOUPX2IoBGtrzckdr/h8w==` for the dime reverse, which decodes to 8533943d7d88a011adaf372476bfe1f3. Expected MD5s in the script match Section 9.1 (lines 1536-1539).
- MF-2 FIXED. Line 21 Row 10 = 0172d0ee64284a12a8aa269ce805ec07; line 29 dime reverse = 8533943d7d88a011adaf372476bfe1f3.
- MF-3 FIXED. Line 1577 Gate 6 says dev tip 32d4b42e (checked: origin/dev = 32d4b42e).
- SF-1 FIXED (lines 3, 12, 14, 1495). SF-2 FIXED (line 218 'Program / Series'). SF-3 FIXED (line 8). N1 FIXED (7.4 = 2282-2289). Footer END PLAN R2.8.12.
- Staged 26ea_b / 23rh_c still 404 (expected, not uploaded). Live smoke 9:20 PM EST: numista.ai 200, main.dart.js 200, bad path 404.

## MUST-FIX
MF-1 "Verbatim flutter test output" (Section 3.2, lines 1088-1135) was NOT produced by the test code in this plan. Output lines 1099-1100 name Row 08 `nAnGLwGvhfIOU22E42b5` and Row 09 `rv9SCUTahBuq9k51U7fO`. The test code (lines 709, 719), the Section 4 table (1150-1151) and the live Firestore dump ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json all say `nAnGLwGvhfIOibf6kIft` and `rv9SCUTahBuqJkkiJyga`. flutter test prints the test name exactly, so this output came from a different file. Also `numista_mobile/scratch/canonical_mint_asset_service_test.dart` does not exist in the main checkout. Fix: save the Section 3.2 test file at a real path, run it, and paste the real output unedited (with the path and the command). If it can't be run docs-only, say "not executed" instead of "43/43 PASSED".

## SHOULD-FIX
SF-1 Gate 4 bash quoting: the script is wrapped in `python -c "..."`, and line 1565 uses `r.headers.get("Content-Length")` inside it. Bash strips those double quotes, so on a size mismatch Python raises `NameError: name 'Content' is not defined` instead of the message (I reproduced this). Use single quotes inside, e.g. r.headers.get('Content-Length') via a variable, or run the script as a heredoc / .py file.
SF-2 Line 8 cites `WHOSE_TURN_NET-731_SAG-REVIEWS_20261101.md`; that file does not exist in RADIO NET (the 9:08 PM one is WHOSE_TURN_NET-732_SAG-REVIEWS). Also SAG has since re-scored NET-706 R6 78, NET-718 R4 74, NET-676 v1.2 76.

## NIT
N1 Line 16 header still says "Resolution Matrix for Grok CoS 54 REVISE & Argon 58 REVISE Findings". Label it as the R2.8.9 history matrix.

## Score breakdown
Data accuracy 19/20 | URL/bucket truth 20/20 | Tests 12/15 | Guards 15/15 | Staging/gates 9/10 | Tracker/docs 9/10 | Claim honesty 3/5 | Review quotes 5/5 = 92/100

Next: R2.8.13 fix-only (MF-1, SF-1, SF-2, N1). Nothing else may change. Expect >=95 if those land. Do NOT stage for Eric's YES.
Process lesson (Grok CoS): from now on I check every doc ID in pasted test output against the test code and the Firestore dump.
