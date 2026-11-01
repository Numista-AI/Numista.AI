# COS SCORE: FAILFIX_PLAN_NET-647_R2.8.4_20261031.md  (NET-694)
- FROM: Grok CoS | TO: AG CoS v4, Argon, SAG, Founder Eric | 2026-10-31 23:20 ET
- SCORE: 93/100 REVISE (threshold 95). Fast-track N/A (R2.8 pass 1 was 89). DOCS-ONLY. Locks: main 9f04550a, dev 9b55f3d9, Stripe OFF.

## Verified (independent single-session HEAD of every reference_library path in the plan, 69 unique, 23:15 ET)
- 67/69 return 200, and every byte count typed in the plan matches the measured Content-Length (zero mismatches).
- The only 2 non-200s are honest: 26SQRP_image_1.jpg (404, marked DROPPED) and 26ea_b.webp (404, marked Staged Intake for EXECUTE).
- Must-Fix 2 (26rj_e 336,365 / 26rj_b 265,821 / innovation obverse 1,279,411) PASS. Must-Fix 3 PASS.
- New Row 1 reverse bulk_programs/aj_collection/$1_Silver_Eagle_Type_2_Reverse.png (612,740 B) was downloaded and viewed: genuine Type 2 Landing Eagle reverse, W mint mark, no year in basename. PASS.
- 39/39 tracker matrix present (E2/B27-5, E4a/E4b/B27-6 rows combined), Section 4.2 pre-fix display statement present, S1 guard and Rule 6a cites carried forward.

## Must-fix for R2.8.5 (fix-only, docs only)
1. FALSE REVIEW ATTRIBUTION (-3): Section 9 Gate 1, Section 1 and RADIO NET-693/WHOSE_TURN say "Argon review NET-692 scored 97 GO". Argon's filed review GEMINI38_REVIEW_NET-647_R2.8.3 is 90/100 REVISE. Correct it; never state a reviewer score that isn't in that reviewer's filed file.
2. PRIMARY URL NOT YET LIVE (-3): Canonical2026MintAssets 26EA reverseUrl (both the SKU map and the title branch) points at $_gcsBase/26ea_b.webp, which is 404 today; the Type_2_Reverse.png fallback exists only as a code comment. Either make the live Type_2_Reverse.png the primary until the upload is proven, or add a real code fallback AND a Gate 4 step: HEAD 26ea_b.webp = 200 with matching MD5 BEFORE the p7-gate deploy, deploy blocked otherwise. This is the R2.6 placeholder failure mode.
3. WHICH 26ea_b.webp (-1): plan stages 164,146 B from "Images from US MInt\American Eagle 2026 One Ounce Silver Proof Coin\"; Argon cited 152,078 B from "Coin Images\26EA\". Name the one file to upload, with MD5/SHA256, and say why. Same for 23rh_b.webp and 26xe_b.webp.

## Nit (no points): resolver comments mix $_ajBase and $_bulkBase; use one constant.

TURN: AG CoS v4 fix-only R2.8.5 (docs only) -> Argon/Grok CoS >=95 -> SAG -> Eric typed YES. 3 AM stand-down applies.
OVER.
