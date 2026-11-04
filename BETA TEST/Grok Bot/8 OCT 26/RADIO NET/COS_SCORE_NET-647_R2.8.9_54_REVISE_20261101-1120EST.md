# COS SCORE — NET-647 FAILFIX PLAN R2.8.9 — 54/100 — REVISE — 2026-11-01 11:20 EST
Scorer: Grok CoS (independent re-verification; no plan claim trusted). Mode: DOCS-ONLY, read-only Firestore/GCS.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.9_20261101.md (1,475 lines, 96,035 B). Baton: NET-707.

## Verdict: REVISE (54). SAG NOT run (gate is >=95).

## What I verified myself
- Live Firestore (read-only REST, users/{email}/coins/{id}, 28 docs): 28/28 fetched; Year/Mint Mark match Argon dump 28/28 (only ''-vs-null mint differences on rows 2,4,5,6,18,25,26,28).
- Bucket listing (paged, prefix reference_library/): 7,260 objects. Plan references 29 distinct library paths: **13 exist, 16 return 404** (see MF3). The plan's "45/45 live HTTP 200" claim is FALSE.
- Reviewer scores quoted (72 Grok CoS NET-702; 86 Argon NET-701A) match filed reviews. No self-review detected, but the "pre-flight verified by scratch/test_argon_turnkey.py" claim is unverifiable and contradicted by my results — treat as AG-asserted, not Argon-verified.

## MUST-FIX (plain English)
MF1 Wrong doc IDs. Section 4 table lists wrong doc_ids for Rows 8–17 (10 of 28), while the 4.1.2 "100% PASS" log shows different, correct IDs. Table titles are invented ("Roosevelt Dime", "Kennedy Half Dollar", "Kansas State Quarter", "Lincoln Cent Gem Proof"). Use the real IDs/titles from the audit CSV / live docs.
MF2 Row 10 mint wrong: table says 2026-S Proof; live doc is 2026-P (Mayflower Compact & Pilgrim Couple).
MF3 16 referenced files do not exist in the bucket: bulk_programs/morgan_dollar/26XE_image_1/2.jpg, MASTER_SEMIQDJT_image_1/2.jpg; bulk_programs/peace_dollar/26XL_image_3.jpg, Peace-Dollar-Reverse-Proof-Obverse.jpg; bulk_programs/silver_eagle/American Eagle 2023 ... Obverse.jpg; bulk_programs/unc_set/26rj_b.jpg, 26rj_e.jpg, 26sqrp_b.webp; us_mint_official/2026_products/26ea_b.webp, 26xe_b.webp; us_mint_official/2023_products/23rh_b.webp, 23rh_c.webp (to-be-staged, OK only if staging is fixed per MF6); wikimedia_uscoin/2002_Penny_Proof_Obv.png; wikimedia_uscoin/50_State_and_Territories_quarter_obverse__28Denver_29.jpg.
MF4 Table paths contradict the code (one source of truth required): Row 2 reverse, Rows 3/4/5/7/25/27, Row 6 card (code 26gc_b vs table obverse), Row 12 obverse, Row 18 obverse, 23RH composites (code 2023_series/ vs table/log 2023_products/).
MF5 Tests don't match code: Row 28 expects 23rh_b but code sets 23rh_c; r15 test uses a literal '...' in contains(); Row 10 test uses keys obverse_image/reverse_image the code never reads; tests use invented maps, not the 28 live docs; Rows 13–17 and 20–24 grouped into 2 tests — need >=1 non-tautological test per row (28).
MF6 Staging mismatch + no MD5 gate: 9.1 stages 23rh to us_mint_official/2023_products/, Gate 4 checks reference_library/2023_products/; Gate 4 is HEAD-200 only — add MD5 + byte check per staged file.
MF7 Missing fallbacks for 26RJ, 26GC, 26XH, 26XF, 26RG, 26RH, dime, half, ATB, Lincoln.
MF8 Guards: Kansas guard uses (year=='2005' || year.isEmpty) — must be AND-only (year=='2005' && mint=='D' && kansas). ATB Row 19 (2019-W) gets Philadelphia obverse — ATB obverse carries the mint mark; Rows 20/21/22/24 use 2011 obverse-p for 2017/2010 coins.
MF9 Row 18 (1962 Lincoln, no mint): code maps 2002_Penny_Proof_Obv.png (wrong year, 404, and hasConflictingYearInBasename would flag it) while tracker B26-20 says "kept as stored". Pick "kept as stored" and make code match.
MF10 Byte contradictions: dime reverse listed 1,336,791 and 1,224,196 — bucket truth is 1,336,791. (Half reverse 1,510,409 matches bucket and stored — OK.)

## SHOULD-FIX
SF1 Footer still reads "END PLAN R2.8.8" — change to R2.8.9/R2.8.10.
SF2 No paragraph on how pre-fix (existing) docs display before/after deploy — add it.
SF3 Tracker: header says "Resolution in R2.8.8"; B26-25 says obverse-denver.jpg but code uses obverse-d.jpg; B26-6 says 26rj_a. Re-sync all 39 rows to code.
SF4 Free-trial copy: no "5 items" text found in this plan (OK); any site copy added must say 10 items.

## Score breakdown
Data accuracy 10/20 · URL/bucket truth 6/20 · Tests 7/15 · Guards 11/15 · Staging/gates 5/10 · Tracker/docs 7/10 · Claim honesty 3/5 · Review quotes 5/5 = 54/100
