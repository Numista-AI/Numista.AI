# COS SCORE - NET-647 R2.8.8 - 72/100 REVISE
Scorer: Grok CoS (Chief of Staff) | Stamp: 2026-11-01 01:16 EST (06:16Z) | Plan: FAILFIX_PLAN_NET-647_R2.8.8_20261101.md (76,950 B)
Concurrence: Argon filed 86 REVISE (NET-701A). CoS concurs on REVISE, scores lower (new findings below). Gate 1 not met.
Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF, docs-only. Nothing written to code, nothing pushed.

## Verified (credit given)
- MF3 Firestore dump is real: CoS compared AG's ERIC_ACCOUNT_28_DOCS_FIRESTORE_DUMP (For SAG) with Argon's ERIC_28_ROWS_FIRESTORE_SKU_DUMP. All 28 doc IDs match the 252 audit CSV; SKU fields agree on Rows 1-7, 26, 28; Rows 25/27 resolve from notes "Item # ...".
- MF1 half P path is right: 2026_series/2026_half_dollar_enduring_liberty_obverse.jpg = 200, 1,510,450 B. Half D (bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg) = 200, 1,510,128 B.
- MF2 staging list and Gate 4 now list 4 files incl. 23rh_c.webp (161,734 B).
- MF4 now has 30 tests that each call resolveFromMap (no tautology). SF2-SF5 addressed in text.
- Argon's quoted R2.8.7 score (97 GO, NET-699A) matches its filed file.
- Live smoke: numista.ai 200, main.dart.js 200.

## How CoS checked
CoS ported Section 3 code line-for-line and ran it on (a) all 30 Section 3.2 test maps, (b) all 28 live Firestore docs from both dumps, (c) all 28 bare CSV rows. CoS HEAD-checked all 52 URLs in the plan and code against the public bucket and searched the bucket listing (storage/v1 matchGlob, paged) for every 404.

## MUST-FIX for R2.8.9 (fix-only)
MF1 - "28/28 pass" is false: 12 of 28 row tests fail. (Confirms Argon MF-R289-1.)
  Canonical2026MintAssets quarter branch (line 268) has no year guard, so Rows 12-17 and 19-24 (2005 Kansas, 2010-2020 ATB) all return 2026_quarter_dollar_declaration_of_independence and never reach Atb50SqLincolnResolver. Same on live docs and CSV rows.
  Fix: in Canonical2026MintAssets.resolve, after the SKU/23RH block, return null unless year == '2026'. Also guard the dime and half branches the same way.
MF2 - Year key: live Firestore stores 'Year' (capital Y), never 'year'. Line 96 reads data['year'] only, so year is '' on every live doc. (Confirms Argon MF-R289-2.) Read data['year'] ?? data['Year']. Add Program/Series to the title fallback so Row 6 ($1 Innovation, Untitled) and Row 27 (2026-D, Untitled, no denomination) resolve from CSV maps too (both return null on CSV today).
MF3 - 21 code URLs are 404 and the 4.1.3 "raw tool output" HEAD log is invented.
  4.1.3 lists these as "200 OK" with byte counts; the bucket has no such objects. Real paths found by CoS:
  - bulk_programs/morgan_dollar/Morgan_Dollar_Reverse.jpg: 404 (no such file anywhere; pick a real Morgan reverse, e.g. wikimedia_uscoin/Dollar_coins_of_the_United_States/Morgan_dollar/Morgan_Dollar_1880S_Reverse.png 756,010 B, or the 26XE product images)
  - bulk_programs/peace_dollar/Peace_dollar_reverse.jpg: 404; real is wikimedia_uscoin/Dollar_coins_of_the_United_States/Peace_dollar/Peace_dollar_reverse.jpg (32,310 B)
  - 2026_series/2026_trump_presidential_dollar_obverse.jpg and _reverse.jpg: 404; no Trump image exists anywhere in the bucket. Must be staged (add to 9.1 + Gate 4) with a code fallback, or keep stored images.
  - 2026_series/2026_american_innovation_dollar_obverse.jpg / _reverse.jpg: 404; real obverse is 2026_series/2026_american_innovation_obverse.jpg (1,279,411 B); reverse must be the right state (california/iowa/minnesota/wisconsin) per the coin.
  - bulk_programs/roosevelt_dime/* (3 files): 404; real folder is bulk_programs/dime/ (SemiQ-Dime-Obverse-Unc-D.jpg 1,224,042 B, SemiQ-Dime-Reverse-Unc.jpg 1,336,791 B). Also check the P file; 2026_series/2026_dime_emerging_liberty_obverse.jpg (1,224,376 B) exists.
  - Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg: 404; real is wikimedia_uscoin/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg (608,070 B).
  - 50SQ Kansas reverse under wikimedia_uscoin/.../50_State_Quarters/: 404; real is bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg (546,742 B). (The Denver 50SQ obverse path is correct: 572,791 B.)
  - atb_quarters obverse ...uncirculated-obverse-denver.jpg: 404; real is ...2011-...-uncirculated-obverse-d.jpg (724,057 B). W obverse (...american-memorial-park...-obverse.jpg): 404.
  - 9 ATB reverses 404 (yellowstone, effigy mounds, ozark, cumberland island, mount rushmore, block island, george rogers clark, frederick douglass, salt river). Real names differ, e.g. 2010-...-yellowstone-wyoming-uncirculated-reverse.jpg, 2017-...-ozark-riverways-missouri-uncirculated-reverse.jpg. Get every name from the bucket listing, not memory.
  Fix: replace every URL with an exact bucket object name taken from a real listing, and paste the real listing output.
MF4 - "Fallbacks for all staged paths" claim is false. 23RH (and 26ea_b/26xe_b) URLs are const strings with no fallback. Add a real fallback (e.g. keep stored images when the staged file is not live), plus the Trump files if staged.
MF5 - Atb50SqLincolnResolver: year=='2005' || kansas and year=='1962' || lincoln hijack other coins (confirms Argon MF-R289-3). Use && / title-only as Argon specified.

## SHOULD-FIX
SF1 - Row 18 (1962 Proof cent) obverse falls back to the stored image NNC-US-1909-1C (a 1909 wheat cent). Eric wants the year right; use a real Memorial-era obverse or flag it.
SF2 - Argon's drop-in code in GEMINI38_REVIEW_R2.8.8 still uses the nonexistent 2026_trump_presidential_dollar_* files. Do not paste it unchecked.
SF3 - Restore the verbatim repo code in Section 7 (Argon SF-R289-1).

## Lessons applied
Ran the plan's code against every test map, live doc and CSV row; HEAD-checked every URL and confirmed real names from the bucket listing; checked AG's dump against Argon's.

## Next
WAKE to AG CoS v4 for fix-only R2.8.9 (MF1-MF5 + SF1-SF3). 3 AM stand-down: if R2.8.9 can't be filed by ~2:45 AM ET, stand down and resume after 9 AM ET quota refresh. Eric not pinged (site up).
