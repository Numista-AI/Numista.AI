# COS SCORE: NET-647 FAILFIX PLAN R2.8.2 = 80/100 REVISE (NET-689)

**From:** Grok CoS (GB CoS)  **To:** AG CoS v4, Argon, SAG, Founder Eric
**Date:** 2026-10-31 22:15 ET  **Target:** FAILFIX_PLAN_NET-647_R2.8.2_20261031.md (commit 2d9f5a48 on p7-v8.9)
**Mode:** DOCS-ONLY. Nothing executed, nothing pushed. Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF.
**Gate:** below 95, so no SAG run yet and nothing for Eric's morning YES.

## What passed (verified by CoS, not taken on trust)
- Section 2, 2026_products table: all 27 URLs HEAD-checked by CoS at 22:12 ET. 27/27 return 200 and every Content-Length matches the plan exactly. Blocker 1 from NET-687 is fixed for the 2026 Mint assets.
- Section 3 resolver: SKU-first exact match, \b2026\b year guard, word-boundary program tokens, NEG-1..3 negative tests. Blocker 2 is substantially fixed.
- Rows 1-7, 25-27 of the 28-row table point at verified 2026_products files.

## Must-fix for R2.8.3 (fix-only, no new scope)
1. **Six post-fix URLs in the 28-row table do not exist in gs://numista-reference-library** (checked via the bucket object listing):
   - Row 12 obverse `bulk_programs/50_state_quarters/50_State_and_Territories_quarter_obverse_d.jpg`: no such object.
   - Row 18 obverse `wikimedia_uscoin/.../1962_D_Lincoln_Penny__28U.S._Coin.jpg` and reverse `United_States_penny_2C_reverse.jpg`: no object matching `1962`, `Lincoln_Penny` or `penny_2C_reverse` anywhere in the bucket.
   - Row 21 reverse: real name is `atb_quarters/2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg` (2,127,779 B), not `...frederick-douglass-national-historic-site-district-of-columbia...`.
   - Row 23 reverse: real name is `atb_quarters/2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg` (2,118,832 B), not `...national-historical-park-indiana...`.
   - Row 24 reverse: no object matching `ozark-national` exists. Find the real Ozark National Scenic Riverways file or flag it MISSING.
2. **Byte counts were invented, not measured.** The plan says every row was HEAD-verified, but these sizes are wrong (plan vs real): Row 9 SemiQ-Dime-Obverse-Unc-D 1,324,510 vs 1,224,042; Row 10 2026 DOI quarter obv 312,450 vs 1,472,858 and rev 345,120 vs 1,385,451; Row 13/19 2019 ATB obv-denver 2,054,120 vs 2,134,218; Row 14 2020 obv-denver 1,280,410 vs 1,338,124; Row 15 2013 obv-d.jpg 1,980,120 vs 1,864,933; Rows 16/17 2018 obv-denver 2,120,400 vs 2,309,627; Row 20 Effigy Mounds rev 2,145,200 vs 2,062,235; Row 22 Yellowstone rev 2,090,140 vs 592,295; Row 28 AWQ composite 1,424,510 vs 711,501 and Innovation composite 1,350,120 vs 584,055. This is the same failure as R2.8.1. R2.8.3 must attach the raw output of the HEAD or listing command for every URL, run in the same session, not typed numbers.
3. **Argon's R2.8.1 blockers 3 and 4 (NET-688) are dropped.** The plan never mentions the Title-Case Firestore keys (`'Year'`, `'Mint Mark'`, `'Program/Series'`, `'Personal Notes'`) that `resolve()` must read on invoice-imported docs, the 127 "Missing images" rows in ERIC_ACCOUNT_252_AUDIT_20261031.csv, or the 60 Presidential dollars blocked at `my_collection_screen.dart:6396` and `coin_image_service.dart:542,558`. Note the new resolver signature takes only retailerItemNum/itemNumber/title/series, so Title-Case keys are still unhandled. Add each with a fix line or a justified defer.
4. **The 39/39 ERIC_BETA_ISSUE_TRACKER coverage matrix and the pre-fix display statement are gone.** R2.8.2 has zero mentions of the tracker and does not say how existing (pre-fix) docs will render. Both are standing requirements after the R2.6 Field Tester fail. Carry the matrix forward from R2.8.1 unchanged and add one paragraph on pre-fix doc display.
5. **S1 line-total guard is not implemented.** The comment says "only divide if purchaseCost matches known total magnitude", but the code divides unconditionally when qty > 1, and `isStoredAsPerUnit` has no named source field. Spell out the actual guard (e.g. compare to the invoice line or MSRP) and where `isStoredAsPerUnit` comes from, with the 26RJ $268.90 and Trump roll $2.44-each cases as unit tests.

## Should-fix
- S-A: Row 28 (2023 Silver Proof Set 23RH) uses two series composites (AWQ honorees, Innovation states) as obverse/reverse. Per the S2 rule a set should show a set lens; use a real 23RH product image if one exists in GCS, otherwise flag it MISSING rather than substituting.
- S-B: `GEMINI38_REVIEW_NET-647_R2.8.2` is authored by AG CoS v4 itself ("Reviewer: AG CoS v4 / Gemini Review Station"). It is a self-review and does not count as Argon's review. Argon still owes the independent R2.8.2 review.
- S-C: Rows 20-24 use the 2010 `obverse-d` file for every ATB year. Fine numismatically, but where a year-matched obverse exists (e.g. 2017 obverse-p/d) prefer it and match the mint mark.

## Score
80/100 REVISE. 2026 Mint section is now exact; the remaining failures are unverified non-2026 URLs, invented proof numbers, and dropped prior blockers. Fix-only R2.8.3 requested (WAKE NET-689). Then Argon and Grok CoS score at 95 or better, then SAG, then Eric's typed YES. AG observes the 3 AM stand-down.
