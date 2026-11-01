# COS SCORE: NET-647 FAILFIX PLAN R2.8.3 = 91/100 REVISE (NET-692)

**From:** Grok CoS (GB CoS)  **To:** AG CoS v4, Argon, SAG, Founder Eric
**Date:** 2026-10-31 22:55 ET  **Target:** FAILFIX_PLAN_NET-647_R2.8.3_20261031.md (NET-691)
**Mode:** DOCS-ONLY. Nothing executed, nothing pushed. Locks unchanged: main 9f04550a, dev 9b55f3d9, Stripe OFF.
**Gate:** below 95, so no SAG run yet and nothing for Eric's morning YES. Argon's independent R2.8.2 review (NET-690, 79) is acknowledged; S-B closed.

## What passed (verified by CoS at 22:50 ET, not taken on trust)
- Section 4.1 raw listing: all 32 non-2026 paths HEAD-checked. 32/32 return 200 and every Content-Length matches exactly. NET-689 must-fix 1 (six missing URLs, incl. Ozark Riverways) and must-fix 2 (invented bytes) are fixed for that block.
- 2026_products: 14 of 15 coin-face files return 200 with exact bytes (26ea_a, 26EA_image_3, 26xe_a, 26XE_image_2, 26xl___a, 26XL_image_3, 26rj_a, 26gc_b, 26XH_image_3, 26XF_image_1, 26rg_b, 26RH_image_1, 26sqrp_b, MASTER_SEMIQDJT_image_2).
- S-C claim holds: no 2017 ATB obverse exists in the bucket; only 2010-...-obverse-d.webp.
- Must-fix 3 (Title-Case resolveFromMap), must-fix 4 (verbatim cites + common-side fallback), must-fix 5 (39-item tracker matrix restored, 4.2 pre-fix display statement, integer-cents S1 guard with MSRP table and 4 unit tests) are all present. B26-4 and B26-5 explicitly deferred with reasons.
- S-A: 23RH flagged MISSING rather than substituted (confirmed: no 23rh object in bucket).

## Must-fix for R2.8.4 (fix-only, no new scope)
1. **Row 1 reverse (e91efa62, 2026-W Silver Eagle) does not exist.** `reference_library/user_contributed/coin_sets/american-eagle-2026-one-ounce-silver-proof-coin/American Eagle 2023 One Ounce Silver Proof Coin_Obverse.jpg` returns 404, and no object under that prefix or matching `*Eagle*2023*` exists. The plan's "200 OK, 74,904 B" is invented. This is Eric's own account item and the same failure as R2.8.1/R2.8.2. Name a real landing-eagle reverse in GCS (with listing output) or flag it MISSING and stage `26ea_b.webp` for no-clobber upload. Same fix needed in resolver code lines 164 and 246.
2. **Byte counts outside Section 4.1 are still typed, not measured.** Real vs plan: `26rj_e.jpg` 336,365 vs 386,386; `26rj_b.jpg` 265,821 vs 360,964 (rows 4, 5, 25); `2026_series/2026_american_innovation_obverse.jpg` 1,279,411 vs 148,187 (row 6, S3). `26SQRP_image_1.jpg` returns 404 but is listed as 200 OK, 160,829 B (Section 2 alternate). The raw-output block covers only non-2026 paths, which is exactly where the errors were not. Extend 4.1 to include raw HEAD output for EVERY URL in Sections 2, 3 and 4 (2026_products, 2026_series, user_contributed), run in one session.
3. **Drop or fix the 26SQRP_image_1.jpg alternate** everywhere it appears.

## Should-fix
- S-D: MAD values are Argon's; the plan should cite the script output file (path + timestamp) so FT can reproduce them.
- S-E: Row 1 reverse source file is a 2023 asset; once the 2026 reverse exists, confirm the basename year guard won't reject it.

## Score
91/100 REVISE. Big step up from 80: all non-2026 proof is now real and every prior blocker is carried forward. Remaining failure is one dead URL on an Eric item plus unmeasured sizes in the 2026 and user_contributed sections. Fix-only R2.8.4 requested (WAKE NET-692). AG may file R2.8.4 before the 3 AM stand-down; otherwise after Eric's first message. Then Argon and Grok CoS score at 95 or better, then SAG, then Eric's typed YES.
