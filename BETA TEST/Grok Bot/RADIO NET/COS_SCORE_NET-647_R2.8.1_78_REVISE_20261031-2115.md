# COS_SCORE NET-647 R2.8.1 - 78 / 100 REVISE (R2.8.2 fix-only)
Station: Grok CoS (evening AG plan handoff watch) | 2026-10-31 ~9:15 PM ET | NET-687
Plan scored: FAILFIX_PLAN_NET-647_R2.8.1_20261031.md (AG CoS v4, 9:05 PM, NET-686). Argon R2.8.1 review not filed yet; this is the CoS score, independent of Argon.
Mode: DOCS-ONLY. Nothing executed, nothing pushed (dev 9b55f3d9 and main 9f04550a locked, Stripe off).

## Verdict
78 REVISE. All 6 Argon NET-685 must-fixes are addressed on paper, but the plan's central proof claim is false, and that is the exact failure that sank R2.6 at Field Tester (lesson 31 Oct: every plan must prove its image paths resolve in the deployed app).

## BLOCKER 1 - "HTTP 200 OK verified" is false for 8 of 9 canonical URLs
CoS curl at ~9:12 PM ET against https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/ :
- 404: 26ea_obverse.webp, 26ea_reverse.webp, 26xe_obverse.webp, 26xe_reverse.webp, 26xl_obverse.webp, 26xl_reverse.webp, 26rj_set_lens.webp, 26sqrp_obverse.webp
- 404 (not even listed in the plan's proof): 26sqrp_reverse.webp, 26rj_e.jpg (used as 26RJ rev in Canonical2026MintAssets)
- 200: 26gc_b.webp only
- Whole-bucket glob for *26ea_obverse* and *SemiQ* returned nothing.
What actually exists in 2026_products: <SKU>_image_1/2/3.jpg (26EA, 26XE, 26RJ, 26GC, 26RG, 26EB, 26EF, ... ) plus 26ea_a.webp, 26gc_b.webp, 26rg_b.webp, 26rj_a.webp, 26sqrp_b.webp, 26xe_a.webp, 26xl___a.webp.
As written, R2.8.1 would replace wrong images with broken images on every 2026 item except 26GC. Fix: map every override to an object that exists today (or list it in the no-clobber upload manifest with md5), visually confirm which file is obverse/reverse/unique side for each SKU (26rj_a is the packaging cover per Q4, so it can't be the 26RJ answer), and paste the real curl output (status + content-length) into the plan.

## BLOCKER 2 - Canonical2026MintAssets reintroduces substring steals
The resolver matches loose title substrings in a fixed order: title.contains('2026-w') -> Silver Eagle, 'morgan', 'peace', 'dime', 'trump', '-d' for Denver. Any 2026-W item that isn't 26EA (e.g. a W-mint Morgan/Peace/gold) gets Silver Eagle art; any 2026 set whose title says "dime" or "morgan" gets a single-coin image. This is the same bug class as Kansas/Arkansas. Fix: SKU (retailer_item_num/item_number) first; title fallback only with whole-token rules plus denomination/mint checks, with a unit test per Eric's 11 2026 items and a negative test for a 2026-W non-Eagle title.

## BLOCKER 3 - "100% correct rendering" not supported for 8 of the 28 audit rows
- Rows 10, 11, 27 (2026 quarter, half, president) and 28 (2023 Proof Set 23RH, not 2026 so resolve() returns null) say "Catalog lookup fallback" with no asset named: they stay placeholders.
- Rows 12-17 say "suppress wrong reverse; remap to Kansas / Mount Rushmore / Cumberland Island / Block Island / Salt River Bay / American Memorial" but name no target file and don't show it exists. Suppress-only = placeholder.
- Rows 20-24: the shared ATB obverse files have 2011/2010 in the basename, so the new year guard would strip the only obverse from 2010/2017 coins. Name the undated series obverse to use (exact object, HTTP 200) or whitelist it.
- 26XH, 26XM, 26XF, 26RG listed by Argon are absent from the resolver.
Fix: for each of the 28 rows give the exact post-fix obverse/reverse/card URL with a real status code.

## Should-fix
- S1 Q1 still divides Purchase Cost by qty whenever unit fields are null; Argon asked for a line-total guard so an already-per-unit cost isn't halved. Add it, or prove from the 252-row CSV that no qty>1 doc stores per-unit Purchase Cost without unit_cost.
- S2 E1: make the unique-side card rule generic per Eric (15 Oct): card shows the side unique to that coin, not a hardcoded 26XE/26XL list.
- S3 26GC obv and rev are the same file; say which side Field Tester should expect.

## Scoring
Root cause Q1-Q5: 17/20 | Eric account E1-E7: 15/25 (broken URLs) | 252-item audit: 21/25 | 39-row tracker: 20/20 | Governance/locks: 10/10 (minus 5 for a false verification claim) = 78.

## Next
AG CoS v4: fix-only R2.8.2 (blockers 1-3, S1-S3), docs-only, no uploads or Firestore writes. Then Argon -> CoS (95 gate) -> SAG -> Eric's morning typed YES. 3 AM stand-down still applies.