# COS_SCORE NET-647 R2.2: 93/100, REVISE (close; small fixes only)
GB CoS, Sat 31 Oct 2026 2:55 PM ET. Plan: FAILFIX_PLAN_NET-647_R2.2_20261031-1445.md. I checked the claims against the repo myself.

VERIFIED: the regression list matches FT_RESULT verbatim (10 PASS items). The 3 backend test files exist. pubspec = 8.18.15+81818. Integer cents + Decimal HALF_UP are sound. The string-based formatCurrency gives 32.49 for 64.97/2. The legacy hack is deleted. The backfill runs dry-run plus a CSV, only on pending items, and never touches coins/. The #9 400 'Invalid update field: Storage Location' is captured. There is a single write path, and the whitelist excludes money fields. The protocol correction is acknowledged.

## MUST-FIX for R2.3
1. WRONG-YEAR IMAGES. 26EA (2026 Silver Eagle) uses an image named 'American Eagle 2023 ... Obverse'. 26XE (2026 Morgan) uses '2025-Morgan-Unc-Obverse'. The date is on the obverse, so collectors would see the wrong year. Use 2026 images, or show a clearly labeled 'Representative image' only if no 2026 image exists, and list which SKUs.
2. NO CONTACT SHEET. Section 7.2 is a table, not a contact sheet. Render an actual 11-thumbnail PNG (SKU + name under each) into RADIO NET so CoS/FT can eyeball the unique side and year. Also: 26XL and 26XH share one file named 'Peace-Dollar-Reverse-Proof-Obverse.jpg'. Confirm it shows the obverse and its date.
3. LICENSE CLAIMS. 'Public Domain' is asserted for files in our own GCS buckets with no origin. For each, record the original source URL (usmint.gov or Wikimedia page). Mark it 'unknown' if not known, and do not claim PD.

## SHOULD-FIX
4. The mobile test count is wrong. numista_mobile/test has ~40 *_test.dart files, not 25. Report the real count from 'flutter test' output and require 0 failures, not a fixed number.

## Next
R2.3 is a FIX-ONLY revision (items 1-4, no new scope). Then a CoS re-score at >=95, then SAG on pricing/rounding, then Eric's typed YES. No code or deploy until then. Live and main stay locked.
