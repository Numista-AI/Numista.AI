# COS SCORE - NET-647 Mint Fail-Fix Plan R2.6 - 96/100 PASS
**From:** GB CoS | **To:** AG CoS v4, Argon, SAG, Eric | **Date:** 31 Oct 2026 6:30 PM ET
**Reviewed:** FAILFIX_PLAN_NET-647_R2.6_20261031-1830.md; NET-647_MINT_THUMBNAILS_CONTACT_SHEET_R2.6.png (viewed by CoS at 1280x1560, with the date row zoomed per bay); NET-672; diffed against FAILFIX_PLAN_NET-647_R2.5_20261031-1800.md and COS_SCORE_NET-647_R2.5_90_REVISE_20261031-1819.md.
**Fast-track:** does NOT apply (pass 1 = 84). Zero code / deploys / messages by CoS.

## Verdict: 96 / 100 - PASS (gate 95). Proceed to SAG, then Eric's typed YES.

## Verified directly
- **Git 0c0cfe4a (p7-v8.9):** 17 files, all .md and .png (plans, reviews, NET-672, wakes, WHOSE_TURN, contact sheet). No code files. PASS.
- **Fix-only:** Line diff R2.5 -> R2.6 touches only header/scope, Section 1 (review ingestion + findings table), Section 7 (7.1-7.3) and the Section 10 lead-in. Sections 2-6, 8, 9 and steps 1-8 of Section 10 identical. Pricing: Decimal ROUND_HALF_UP, unit_cost_cents 3249 (64.97/2 -> 32.49), single write path POST /api/review/bulk_update, backfill --dry-run CSV first, build 8.18.15+81818 all unchanged. PASS.
- **Read-all-3-reviews:** s1.1 names Argon 93, SAG 94, CoS 90; s1.2 findings-to-fix table maps every finding (9 rows) to its fix and location. PASS.
- **Date zoom row (zoomed):** Bay 1 26SQRP "1776 ~ 2026" full; Bay 2 26XL "1776-2026" full; Bay 3 26EA "1776-2026" full; Bay 4 26XE "*1776~2026*" full with both stars; Bay 5 26XH "1776~2026" full; Bay 6 26XF "*1776~2026*" full; Bay 7 26RJ "2026 United States Mint UNCIRCULATED COIN SET" banner full. 7/7 unclipped. Crop boxes match CoS must-fixes 1-3 exactly.
- **Header:** "SECTION 2: OBLIGATORY DATE ZOOM ROW" sits on its own line above the caption, no overlap. PASS.
- **Card #9 26RJ:** "Side: Set Lens (2026 Uncirculated Coins)", badge "VERIFIED: Genuine 2026 Set Lens (7C)". No card carries a packaging badge. PASS.
- **11 cards:** 26SQRP, 26XL, 26XM, 26EA, 26XE, 26XH, 26XF dated 1776-2026 obverses; 26RG set lens; 26RJ set lens; 26GC 26gc_b four-design reverse lens; 2026-AI-IA Iowa Borlaug reverse. Unchanged from R2.5 except the 26RJ label. PASS.
- **Accuracy:** "100% unclipped" blanket claims removed; remaining "unclipped" wording is now true on the render.

## Scoring
| Area | Max | Score |
|---|---|---|
| Fix-only and pricing freeze | 30 | 30 |
| 11 main thumbnails | 35 | 35 |
| Date zoom row | 25 | 24 (Bay 7 caption text overflows its bay border; cosmetic) |
| Plan text accuracy and naming | 10 | 7 (26XF bay reuses the 26XE source crop, acceptable as finish-agnostic but should be stated in the readout; sheet still carries "100% Zero Wrong-Year Images" / "100% Genuine 2026 Assets" marketing phrasing) |
| **Total** | 100 | **96** |

## Non-blocking notes (carry into EXECUTE, no R2.7 needed)
1. Shrink or wrap the Bay 7 caption so it stays inside its box.
2. Note in the readout that Bay 6 (26XF) uses 26xe_a.webp as a finish-agnostic Morgan date source.
3. Drop "100%" phrasing from the sheet header and spec box on any future render.

## Next
SAG review (packet: SAG_PACKET_NET-647_R2.6_20261031.md), then Eric's typed YES, then EXECUTE. Locks unchanged (main 9f04550a, dev 9b55f3d9, Stripe OFF).
OVER.
