# COS_SCORE NET-647 R2.3: 88/100, REVISE
GB CoS, Sat 31 Oct 2026 4:55 PM ET. Plan: FAILFIX_PLAN_NET-647_R2.3_20261031-1645.md (+ NET-664). Fast-track does NOT apply (R2 pass 1 = 84). Full cycle stays in force.
I opened the contact sheet PNG myself and looked at every thumbnail. The plan's text is contradicted by its own image.

## VERIFIED (good)
- Fix-only: sections 2-6 and 8 match R2.2. No new scope.
- Pricing unchanged and correct: Decimal ROUND_HALF_UP, unit_cost_cents 3249 for 64.97/2. The string-based formatCurrency gives 32.49 / 2.44 / 84.50 / 100.01. The qty==25 hack is deleted. Money fields stay out of bulk_update.
- Backfill: dry-run CSV by default, pending items only, never touches coins/. --apply is gated.
- Version stays 8.18.15+81818. Only build/web/version.json is stamped.
- Test gate (SF#4 RESOLVED): I counted 40 *_test.dart files in numista_mobile\test. The gate is flutter test with exit 0 and 0 failures, plus the actual count reported. Good.
- The contact sheet is real: 1280x1330, 11 thumbnails, SKU and name under each.
- Licensing is mostly fixed: 26XE and 26RJ are marked Unknown with no PD claimed.

## MUST-FIX for R2.4 (fix-only)
1. 26XL / 26XH / 26XM are MISLABELED as representative 2023 images. The thumbnails clearly show the dual date "1776~2026" with Liberty Bell privy marks. These are the genuine 2026 Semiquincentennial obverses. The plan's claim that the date is 2023 (sec 7.2, NET-664 item 3) is false. Relabel all three as Genuine 2026 obverse and fix the provenance to the actual 2026 source (not "Product 23XF"). Separately: is one shared image acceptable for both 26XL (Reverse Proof) and 26XH (Enhanced Unc)? It is acceptable only if labeled as finish-agnostic design. Better: use each product's own still.
2. 26EA SHOWS THE WRONG SIDE. The thumbnail is the eagle REVERSE ("ONE DOLLAR - 1 OZ FINE SILVER"), but it is labeled "Obverse (Walking Liberty)". The filename says "2023 ... Obverse", so the file is mislabeled. Eric's rule: the image must show the side unique to that coin. Replace it with a Walking Liberty obverse, ideally 2026, and re-verify it visually.
3. 26XE: a 2025-dated Morgan on a 2026 SKU. The date is on the face collectors look at, so even with a "Representative" badge this is misleading, and it breaks Eric's correct-coin rule. The other Morgan (26XM) already shows 2026, so reuse a 2026 Morgan obverse, or show a neutral placeholder plus the badge. Do NOT show a 2025 date. Also, the image has a burned-in "United States Mint image" caption, yet provenance says "Unknown / internal scan". Pick one, prove it, and crop the overlay.
4. Policy for any remaining representative image: only a design without a visible wrong date is allowed. A wrong year on the dated face is a FAIL. The badge must say exactly which year is shown.
5. Re-render the contact sheet after the fixes. Include a zoom row of the date area for every obverse SKU so CoS/FT can read the year.

## MINOR
6. NET-664 links the PNG at BETA TEST\Grok Bot\RADIO NET\ and leaves out "8 OCT 26". The plan lists both paths; the canonical one is ...\8 OCT 26\RADIO NET\. Fix the link (alt path exists: True).
7. The "EXIF (c)2026 United States Mint" claim on a supposed 2023 still was itself a tell. Statements about an image must come from looking at the image.

## Lesson (logged)
Read the image, not the filename. 4 of the 11 labels were wrong, and only visual inspection caught it.

## Next
R2.4 is FIX-ONLY (items 1-6, images and labels only; pricing is frozen as approved). Then Argon, then a CoS re-score >=95, then SAG on pricing/rounding, then Eric's typed YES. No code, commit or deploy. Live and main stay locked (main 9f04550a, dev 9b55f3d9, Stripe OFF). No SAG packet issued (score < 95).
