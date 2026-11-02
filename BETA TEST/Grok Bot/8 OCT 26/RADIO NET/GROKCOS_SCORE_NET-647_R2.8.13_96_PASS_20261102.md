# GB CoS SCORE — NET-647 R2.8.13 Mint Fail-Fix Plan — 96 / 100 PASS
Reviewer: GB CoS (Grok Bot) | 2 Nov 2026 ~10:15 AM ET | Baton: BATON_NET-735 | Prior: R2.8.12 = 92 REVISE

## Independent checks (all run by GB CoS on EDS_Laptop)
1. MF-1 test file: scratch\canonical_mint_asset_service_test.dart EXISTS (mtime 1 Nov 9:07 PM ET). All 27 unique doc IDs in the pasted output (incl. Row 08 nAnGLwGvhfIOibf6kIft, Row 09 rv9SCUTahBuqJkkiJyga) appear in the test code AND in ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json. 0 missing. (Checked against the dump, not a live Firestore read.)
2. Re-ran `flutter test` on that file myself: 00:00 +43: All tests passed! — matches the plan.
3. Gate 4 Python snippet: extracted and ast.parse() -> OK. NameError/quoting bug fixed (SF-1 verified).
4. Section 7 "verbatim" blocks vs 32d4b42e: my_collection_screen 6320-6366, coin_image_service 535-571, review_hub_screen 2282-2289, main.py 8369-8376 = 0 diffs. my_collection_screen 3016-3023 differs only by the em-dash encoding in PowerShell output (not a real diff).
5. Commit 078fe42c (origin/p7-v8.9 tip): 32 files, ALL .md — docs only, no source.
6. Locks: origin/main = 9f04550a OK. origin/dev = 01a03f90 (NOT 32d4b42e). 01a03f90 = NET-734 stand-down radio doc only (+17 lines, 1 .md); code is the same as 32d4b42e.

## Must-fix
None.

## Should-fix (fold into the execute step, no new round)
- SF-A: The plan says dev tip is 32d4b42e (Section 7 header, Gate 6). The real tip is 01a03f90 (docs only). Change Gate 6 to say the "code tree is the same as 32d4b42e", or cite 01a03f90.
- SF-B: The test file is untracked in git and has its own inline copy of CanonicalMintAssetService (the service isn't on dev yet). Gate 5 has to run the same 43 cases against the real numista_mobile/lib/services/canonical_mint_asset_service.dart that's committed to p7-v8.9, not the scratch copy.
- SF-C: Before Gate 3, run a live Firestore spot-check of Rows 08/09/18/19 (the dump is dated 1 Nov 1:47 AM).

## Verdict
96 PASS -> next step is SAG, then Eric's YES. No code changed and nothing pushed by GB CoS.
