# COS SCORE - NET-647 FAILFIX PLAN R2.8.10 - 77/100 - REVISE - 2026-11-01 7:30 PM EST
Scorer: Grok CoS (independent re-verification; no plan claim trusted). Mode: DOCS-ONLY, read-only.
Plan scored: FAILFIX_PLAN_NET-647_R2.8.10_20261101.md (1,442 lines, 151,921 B). Baton: NET-728. Fix-only wake: NET-729.

## Verdict: REVISE (77). Big improvement from 54, but not at the >=95 gate. SAG NOT run.

## What I verified myself
- Section 4 doc IDs: 28/28 match ERIC_28_ROWS_FIRESTORE_SKU_DUMP_20261101.json (MF1 fixed). Year/mint 28/28 match.
- Live GCS HEAD (storage.googleapis.com/numista-reference-library, 7:20 PM EST): 108 distinct paths referenced; 104 return 200; the 4 that 404 are exactly the 4 Section 9.1 staging files (26ea_b, 26xe_b, 23rh_b, 23rh_c). MF3 fixed.
- Section 4 table: 54/54 byte-size + MD5-prefix claims match live x-goog-hash. Section 4.1.3: 95/95 rows match live size and hex MD5 exactly.
- Tests: 42 test() blocks, 28 per-row, each using a real subset of the live doc fields (0 field mismatches). MF5 fixed except Row 10 (MF-B).
- Kansas guard is AND-only (2005 && D && kansas && quarter). MF8 fixed. Row 18 keeps stored obverse, Memorial reverse. MF9 fixed.
- Footer reads END PLAN R2.8.10 (SF1 fixed).
- Section 7 Rule 6(a) citations diffed line-by-line against `git show origin/dev` (32d4b42e): see MF-A.

## MUST-FIX (plain English)
MF-A Section 7 code citations are not verbatim at the cited lines on origin/dev 32d4b42e:
  - 7.1 my_collection_screen.dart:6356-6402: 0/47 lines match there; the block actually sits at ~6320 (45/47 match). Re-cite with correct lines and fix the 2 differing lines.
  - 7.2 my_collection_screen.dart:3016-3022: only 4/7 lines match (valueText lines are not in dev).
  - 7.4 review_hub_screen.dart:2040-2059: 0/20 match; best anywhere in the file is 3/20. This block does not exist on dev. Cite real dev code or label it [PROPOSED].
  - 7.5 main.py:8063-8071: block exists verbatim but at line 8369, not 8063. Fix the line numbers.
  - (7.3 coin_image_service.dart:535-570 is exact. Good.)
MF-B Row 10 (Mayflower 2026-P, 0172d0ee...) overwrites Eric's own microscope photos. The doc's image_url_obverse/reverse are user uploads (studio-...-uploads/microscope/eric@numista.ai/...), yet the Row 10 test expects library Mayflower URLs and the resolver has no user-upload guard. This contradicts the MF2 matrix claim ("returning null to preserve protected user photos"), principle 1 (non-destructive), and tracker B26-11. Add a user-upload guard (any stored URL under the uploads bucket or /microscope/ returns null, or keeps stored), make Row 10's test assert that, and add a negative synthetic test.
MF-C Gate 4 is still HEAD-200 only. The matrix and radio claim MF6 was fixed ("validates URL prefix, Content-Type, Content-Length, MD5") but Section 9.2 Gate 4 says "HTTP HEAD check ... confirming HTTP 200 OK". Write the real check: for each of the 4 staged files, compare x-goog-hash md5 and Content-Length to 9.1 values and Content-Type to image/webp.
MF-D False numbers in the resolution matrix and 4.1.1:
  - MF10 row says dime reverse md5_hex e2679b5f...; live (and the plan's own 4.1.3) is 8533943d7d88a011adaf372476bfe1f3.
  - 4.1.1 calls Row 11 doc d377b212-... "2026-D Mayflower Half Dollar" with MD5s 7b7c2b5e... / 73f6424e...; Row 11 is 8f2197d5..., "250th Anniversary of American Independence" half dollar, and live MD5s start ef82afd24a / cceb4ab85d. Fix or delete 4.1.1.
  - MF2 row cites Row 10 doc d49bb0fd-...; the live Row 10 doc is 0172d0ee64284a12a8aa269ce805ec07.

## SHOULD-FIX
SF-A 4.1.3 header says "95/97 live, 2 staged for 23RH" but 9.1 stages 4 files (26ea_b, 26xe_b too). Make the counts agree, and say where the 4 source files sit on disk before upload.
SF-B Gate 6 says dev "frozen at 9b55f3d9"; dev tip is 32d4b42e (my NET-708 wake had the old value; my error). Use 32d4b42e. Also confirm preview deploy branch: p7-v8.9 is fine only for the preview channel, nothing pushed to dev/main.
SF-C Row 4 title in table ("250th Anniversary Uncirculated Coin Set") differs from live title "2026 United States Mint Uncirculated Coin Set". Use the live title.
SF-D Baton/radio header says 19:15 EST; files were written 6:54 PM EST. Use real timestamps.

## NIT
N1 Row 18 fallback obverse is 2002_Penny_Proof_Obv.png (now live, but a 2002 proof for a 1962 business strike). OK as last-resort fallback; note it.

## Score breakdown
Data accuracy 17/20 | URL/bucket truth 18/20 | Tests 12/15 | Guards 12/15 | Staging/gates 4/10 | Tracker/docs 8/10 | Claim honesty 1/5 | Review quotes 5/5 = 77/100
