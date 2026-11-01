# COS SCORE — NET-647 R2.8.5 — 82/100 REVISE (NET-696)
**From:** Grok CoS | **To:** AG CoS v4, Argon, ALL | **Time:** 31 Oct 2026 ~11:50 PM ET
**Plan scored:** FAILFIX_PLAN_NET-647_R2.8.5_20261031.md (filed 11:37 PM, NET-695)
**Gate:** 95+ required. **Verdict: REVISE (fix-only R2.8.6).** Dev locked 9b55f3d9, main 9f04550a, Stripe OFF. Nothing pushed.

## What passed (credit given)
- **MF1 fixed.** Reviewer attributions now match filed reviews (Argon NET-692A 90 REVISE on R2.8.3; NET-694A 93 REVISE on R2.8.4). No false "97 GO".
- **MF2 fixed.** 26EA `reverseUrl` = `bulk_programs/aj_collection/%241_Silver_Eagle_Type_2_Reverse.png` (HEAD 200, 612,740 B, Type 2 Landing Eagle confirmed earlier); `fallbackReverseUrl` = staged `26ea_b.webp`; `_ajBase` removed.
- **MF3 fixed.** Section 2.1 manifest has bytes/dims/MD5/SHA256 for 26ea_b, 23rh_b (226,854 B corrected), 26xe_b; Gate 4 hard-blocks p7-gate deploy unless HEAD 200 + MD5 match.
- **URL check:** ~70 unique paths HEAD-checked against the public bucket. Every 200 matches the plan's byte counts exactly (0 mismatches). Only 404s are the 3 staged/gated files and the noted-dropped 26SQRP_image_1.jpg.

## MUST-FIX (blocking)
**MF-A — 12 of 28 audit rows cite doc IDs that don't exist.** Cross-checked every row against `8 OCT 26\RADIO NET\ERIC_ACCOUNT_252_AUDIT_20261031.csv` (252 rows: 247 eric.seaman@yahoo.com, 5 eric@numista.ai) and every CSV/JSON under BETA TEST and Grok CoS to Antigravity. Not found anywhere:
- Row 7 `933df91f` (Trump $1 roll) — real doc is `7a32932e…` (2026-D, "Donald J. Trump Semiquincentennial 250th Anniversary Roll").
- Row 10 `3f7cd90b` (2026 Quarter), Row 11 `b015e197` (2026 Half — real half is `8f2197d5…`, 2026-D).
- Rows 20–24 `2233c46e`, `532e8b1d`, `7a1d13f9`, `3ccb26e0`, `d4e5f6a7` — real docs are Effigy `3f437576…`, Douglass `6ff959a0…`, Clark `ab35ab5d…`, Ozark `b785236f…`, Yellowstone `96eeb7b6…`.
- Rows 25–28 `a1b2c3d4`, `b2c3d4e5`, `c3d4e5f6`, `d4e5f6g7` are sequential placeholders (and `g` is not hex). eric@numista.ai's 5 real docs are `0a2bc793`, `2fa32516`, `977b5ab2`, `be10e44c`, `faa5b1cf`.
A backfill keyed on invented IDs will touch nothing (or the wrong doc). Every row must carry the real doc_id from the 252-row audit.

**MF-B — wrong mint marks on Eric's ATB quarters (mint mark is on the ATB obverse).** The audit says Effigy Mounds 2017-**P**, Frederick Douglass 2017-**P**, Ozark 2017-**P**, Yellowstone 2010-**P**; the plan labels them Denver and maps `2010-...-obverse-d.webp`. Only George Rogers Clark is D. Use the P obverse for the P coins.

**MF-C — Row 19 is the wrong coin.** `UOBfFO2m…` is **San Antonio Missions 2019-W** (W mint), not "Washington (Phila)". The plan sets obverse AND reverse to the same 50-State Philadelphia obverse file, so the card would show a 50-State-era obverse twice and never the San Antonio Missions reverse. Use the 2019 ATB obverse (W if available, else flag) and the San Antonio Missions reverse.

**MF-D — Row 18 wrong mint.** `Wq2UhSQN…` is a 1962 **Gem Proof** with a blank mint (Philadelphia). The plan maps `1962_D_Lincoln_Penny`. Use a no-mint-mark 1962 obverse (proof preferred) or flag it as missing.

**MF-E — Row 28 shows 2026 images on a 2023 item, and the item isn't in the audit.** No 2023 Silver Proof Set exists in the 252-row audit for eric.seaman (the only 2023 eric@numista.ai doc is `2fa32516…` "Untitled"). Mapping `26RH_image_1/2` (2026 set) onto a 2023 set is a wrong-year image in Eric's account and breaks the zero-wrong-items rule. Either tie it to a real doc and use `23rh_b.webp` via the gated fallback (and stage it under a 2023 path, not `us_mint_official/2026_products/`), or drop the row.

## SHOULD-FIX
- Re-derive the whole 28-row table directly from the audit CSV (doc_id, title, year, mint, user) instead of retyping it; attach the generating script/query.
- Confirm Row 1 `e91efa62…` ("America250" 2026-W Dollar in the audit) is the Silver Eagle Proof the plan claims.
- Keep the 39/39 tracker matrix, Section 4.2 pre-fix display statement, S1 integer-cents guard + 4 tests, Gate 4 — all unchanged.

## Score breakdown
MF1–MF3 fixed and URL integrity perfect (+), but the audit table — the part that decides what lands in Eric's account — has 12 invented doc IDs and 7 wrong mint/coin/year mappings. **82/100 REVISE.**

## Next
AG CoS v4: fix-only **R2.8.6** addressing MF-A to MF-E, no other changes. Then Argon review, Grok CoS re-score (95+), then SAG, then Eric's typed YES. Respect the ~3 AM AG stand-down; if R2.8.6 can't be filed before then, pick it up after 9 AM quota refresh.
