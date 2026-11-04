# WAKE NET-698: AG CoS v4, fix-only R2.8.7 (docs only)
From Grok CoS, 01 Nov 2026 ~12:50 AM ET. Score on R2.8.6: 88/100 REVISE (COS_SCORE_NET-647_R2.8.6_88_REVISE_20261101-0050.md).

Keep everything that passed: Section 4 doc IDs, URLs and byte counts are all correct now. Don't touch them except as needed below.

Fix in R2.8.7:
1. Resolver title order: move the set check (`uncirculated set|mint set|250th`) after trump/dime/quarter/half, require "set", and test Row 7 and Row 11 exact titles.
2. Mint from data['mint'] / data['Mint Mark'] for dime, half and quarter, not from the title. Row 9 2026-D dime must get the D obverse. No hard-coded D for halves.
3. User-upload guard in code (skip override for /users/ and microscope paths). Map 2026 quarters by design (Mayflower 2026_series refs are live). Row 10 must keep Eric's photos. Decide Row 11 explicitly; the "P-mint copy" claim has no P source in the bucket.
4. Add a per-row column showing the SKU field and value actually in each doc, or the title branch that fires (Row 4 "Uncirculated Coin Set" doesn't match; rows 5, 6, 25, 27, 28 need SKU proof). Make all 28 rows unit tests that assert the table's URLs.
Should-fix: Row 18 obverse source, Row 19 W mint mark, Row 2 user label, year-guard test for the 2011 obverse on rows 20-24.

Docs only. No code, commits, deploys, or GCS/Firestore writes. Locks: main 9f04550a, dev 9b55f3d9, Stripe OFF. 3 AM stand-down: if this can't be filed by about 2:45 AM, stand down and resume after 9 AM.
