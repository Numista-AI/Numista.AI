# Grok CoS Score: FAILFIX_PLAN_NET-647_R2.8.6 = 88/100 REVISE (NET-698)
Scored 01 Nov 2026 ~12:50 AM ET by Grok CoS. Docs-only review. Nothing written to code, git, GCS or Firestore. Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF.

## What passed (credit kept)
- MF-A fixed. All 28 Section 4 doc IDs exist in ERIC_ACCOUNT_252_AUDIT_20261031.csv, and year, mint and user match for every row.
- MF-B fixed. Rows 13-17 keep their stored P obverses (2,133,544 / 1,340,722 / 1,867,830 / 2,309,513 / 2,309,513 B, all 200). Rows 20-22 and 24 use the 2011 undated P obverse (712,711 B). Row 23 uses the 2010 D obverse (166,278 B). The bucket listing has no 2010 or 2017 P obverse, so the 2011 P choice is reasonable.
- MF-C fixed. Row 19 San Antonio Missions reverse is 2,116,020 B, 200.
- MF-D fixed. Row 18 reverse is the Memorial reverse (608,070 B) with no 1962-D substitution.
- MF-E fixed. 23rh_b.webp is staged under 2023_products, not 2026_products.
- Every URL in every table, the 4.1 log and the resolver code was HEAD-checked by CoS. Every byte count matches live Content-Length. The only 404s are the expected staged or dropped files: 26ea_b.webp (fallback only, primary is live), 26xe_b.webp (staged), 23rh_b.webp (Row 28 primary, staged, covered by Gate 4 MD5), 26SQRP_image_1 and the american-eagle user_contributed file (both dropped).
- Reviewer scores quoted in the plan match the filed reviews (CoS 82, Argon 82 on R2.8.5; Argon 90 and 93 earlier). No self-review.
- Tracker matrix covers all 39 tracker IDs (compound IDs split into E2, E4a, E4b and so on, but nothing dropped).

## Why REVISE: the resolver code contradicts the Section 4 table
The URLs are right now, but if the Section 3.1 resolver code runs as written, several real rows in Eric's account would render differently from what the table promises. This is the same failure as R2.6 (reviews checked the table, not what the app will actually show).

### MUST-FIX 1: title fallback catches "250th" before coin type
`RegExp(r'\b(uncirculated set|mint set|250th)\b')` is checked before the trump, dime, quarter and half branches. Row 7 (7a32932e, "Donald J. Trump Semiquincentennial 250th Anniversary Roll") and Row 11 (8f2197d5, "250th Anniversary of American Independence", a half dollar) would both get the 26RJ Uncirculated Set images whenever no SKU is present. Move the set check after the coin-type checks, require a set word ("set") rather than "250th", and add unit tests using these exact CSV titles.

### MUST-FIX 2: mint comes from the title, not the doc's mint field
The dime branch uses `cleanTitle.contains('denver') || cleanTitle.contains('-d')`. Titles in the CSV don't carry the mint, so Row 9 (rv9SCUTa, 2026-D dime) would get the P obverse, contradicting the table. The half-dollar branch is hard-coded to the D obverse, so any 2026-P half would show D. Read mint from data['mint'] / data['Mint Mark'] first for every branch, and add P and D tests for dime and half.

### MUST-FIX 3: no user-upload guard, and every 2026 quarter maps to one design
The resolver has no check for /users/ or microscope paths, yet Section 4.2 says user uploads stay untouched. `\bquarter\b` sends every 2026 quarter to the Declaration of Independence images, so Row 10 (0172d0ee, Mayflower, Eric's own microscope photos, PASS) would be overwritten with the wrong design. Add the guard in code (skip override when the stored URL is a user upload), map quarters by design (the Mayflower 2026_series references are live, 1,446,894 / 1,627,560 B), and add a negative test for Row 10.
Row 11 also needs an explicit call: its stored images are user-account files (users/eric@numista.ai/coins/b22f8905.../obverse.jpg 1,510,450 B and reverse.jpg 1,510,409 B). The plan calls the obverse a "P-mint copy", but no P half obverse exists in bulk_programs/half_dollar, so that claim is unproven. Either keep the user files (default under Eric's rule) or prove by pixel compare that they're stock copies before replacing.

### MUST-FIX 4: prove which branch fires for each of the 28 rows
Row 4's title ("...Uncirculated Coin Set") doesn't match `uncirculated set`. Rows 5, 6, 25, 27 and 28 are untitled or don't match any regex, so they depend entirely on an SKU the plan never shows is in those docs. Add a column to Section 4 giving, for each row, the SKU field and value actually present in the doc (or the exact title branch that fires), and turn all 28 rows into unit tests that assert the table's obverse and reverse URLs.

## Should-fix
- Row 18: name the source file for the 1962 no-mint-mark proof obverse, or say plainly it stays as stored until intake.
- Row 19 (2019-W): the P obverse shows the wrong mint mark. Keep it flagged in the UI copy and FT checklist, or use a mint-neutral obverse.
- Row 2 user: the Section 4 table says eric.seaman@yahoo.com but the 4.1.1 log says eric@numista.ai (the doc exists under both). Make them agree, and say both accounts get the fix.
- Confirm the basename year guard doesn't suppress the 2011 undated obverse on rows 20-24 (2017 and 2010 coins), with a test.

## Next
TURN: AG CoS v4 for fix-only R2.8.7 (docs only, WAKE NET-698). Then Argon and Grok CoS need 95 or better, then SAG, then Eric's typed morning YES, then execute on p7-v8.9 only. 3 AM stand-down applies; if R2.8.7 can't be filed by about 2:45 AM, stand down and pick it up after 9 AM.
