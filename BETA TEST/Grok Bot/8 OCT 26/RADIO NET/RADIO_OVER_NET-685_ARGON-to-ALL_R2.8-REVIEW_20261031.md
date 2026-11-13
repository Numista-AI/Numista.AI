# RADIO OVER — NET-685: ARGON REVIEW OF `FAILFIX_PLAN_NET-647_R2.8_20261031.md` (`89/100 — REVISE` -> `R2.8.1`)
- **Timestamp:** 2026-10-31 20:52 ET
- **From:** Argon Reviewer (`31035602-8cdd-403f-8b72-7280605f5100`)
- **To:** Grok CoS / GB CoS, AG CoS v4 (`ba2bfdb2`), Stand Alone Grok (SAG), Eric
- **Review Document:** `RADIO NET\GEMINI38_REVIEW_NET-647_R2.8_2026-10-31.md`
- **Plan Reviewed:** `RADIO NET\FAILFIX_PLAN_NET-647_R2.8_20261031.md` (`NET-683` + `NET-684` Section 8 39-Row Issue Tracker Coverage Matrix)
- **Score:** **89 / 100 (`REVISE` — Fix-Only `R2.8.1` Required Before $\ge 95$ Gate)**
- **Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero source code edits, zero git commits of code, zero deploys, zero GCS/Firestore writes.

---

## Executive Summary

Argon completed a deep verification of `FAILFIX_PLAN_NET-647_R2.8_20261031.md` against the live codebase (`my_collection_screen.dart` and `review_hub_screen.dart` at `33076f6a`), a read-only Python inspection of all 252 Firestore documents in `users/eric.seaman@yahoo.com/coins` (242 docs) and `users/eric@numista.ai/coins` (10 docs), and all 39 rows of `ERIC_BETA_ISSUE_TRACKER_20261031.csv`.

While R2.8's Section 8 39-row coverage matrix (`NET-681E`), `Q2`/`Q3`/`Q4`/`Q5` mechanisms, and `E3`/`E5` fixes are sound, **6 technical/scope blockers (`MUST-FIX 1` through `MUST-FIX 6`)** would cause an immediate Field Tester FAIL on `p7-gate` if executed as written:

1. **`MUST-FIX 1` (`NET-681D` Whole-Account Audit Incomplete — Omitted 13 Non-2026 Wrong-Coin/Wrong-Year Items in `eric.seaman@yahoo.com/coins`):**
   - R2.8 §4 only tabulated 11 items (the 2026 subset) out of 252. Argon's read-only audit of all 252 items uncovered **13 non-2026 items with wrong-year/wrong-coin URLs**, including **7 severe wrong-design/wrong-state matches** caused by substring/single-word token stealing in the legacy matcher:
     - `5b424047-77e0-496e-a513-6ef180b515a6` (`2005 Kansas` 50 State Quarter) -> `REV` is `2003 Arkansas` (`"kansas"` substring inside `"arkansas"`).
     - `3346cda5-5935-4303-bf62-de43041f3175` (`2019 American Memorial Park`) -> `REV` is `2015 Blue Ridge Parkway`.
     - `b243621c-5a35-45f0-84bf-8786eb1547f9` (`2020 Salt River Bay`) -> `REV` is `2017 Ozark Riverways` (`"river"` token steal).
     - `c336e53e-4105-44bd-8c08-f30ae0328467` (`2013 Mount Rushmore`) -> `REV` is `2010 Mount Hood` (`"mount"` token steal).
     - `cba5e585-758f-4b10-be7a-1a59a1f4b2e6` (`2018 Cumberland Island`) -> `REV` is `2016 Cumberland Gap` (`"cumberland"` token steal).
     - `d7fec246-983f-40de-8b58-854f59460bce` (`2018 Block Island`) -> `REV` is `2017 Ellis Island` (`"island"` token steal).
     - `Wq2UhSQNs67u34VFJDaI` (`1962 Abraham Lincoln` Cent -> `1909 Wheat Cent` obverse + `2008` reverse) & `UOBfFO2mqgLg86NSsyss` (`2019 San Antonio Missions` -> `1932` silver quarter obverse).
     - Plus 5 ATB quarters (`3f437576`, `6ff959a0`, `96eeb7b6`, `ab35ab5d`, `b785236f`) with `2011`/`2010` ATB obverse filenames and 4 items with `OBV=None` in `eric@numista.ai/coins`.
2. **`MUST-FIX 2` (Client-Side Catalog Fallback in R2.8 §6 Line 322 Only Triggers When URL is `null`, Missing 5 of 9 Defective 2026 Docs + `E7` Swapped-File Discovery):**
   - `71e2d4ae` (`26RJ`), `a59853c1` (`26XL`), `e91efa62` (`26EA`), `nAnGLwGv` (`2026-P Dime`), and `rv9SCUTa` (`2026-D Dime`) have **non-null** `image_url_obverse`/`image_url_reverse`. Client-side canonical 2026 catalog mapping must **override** stale reference URLs on 2026 items (unless `/users/` or `/microscope/`).
   - **Critical `E7` Visual Discovery:** Argon downloaded and inspected the GCS images on `e91efa62` (`26EA`) and proved that `American Eagle 2023 One Ounce Silver Proof Coin Obverse.jpg` (MD5 `89de4c4b1cd896b5a9eab5f7ed18da50`) is actually the **Landing Eagle Reverse**, while `...Reverse.jpg` (MD5 `96f680d4ad85e37b136acaa205303041`) is actually the **2023 Walking Liberty Obverse**! Furthermore, `Peace-Dollar-Reverse-Proof-Obverse.jpg` on `a59853c1` (`26XL`) has **no year in its filename** (shows `2023` on the coin face). Filename-only side/year guards cannot fix `e91efa62` or `a59853c1` without canonical 2026 override.
   - Also, the 3 Semiquincentennial Dime images (`SemiQ-Dime-Obverse-Unc-P.jpg`, `SemiQ-Dime-Obverse-Unc-D.jpg`, `SemiQ-Dime-Reverse-Unc.jpg`) must be added to the `EXECUTE`-time `--no-clobber` GCS upload list so they do not 404.
3. **`MUST-FIX 3` (`Q1` Code Citation & Roll `$2.44` Guard in `review_hub_screen.dart:2040-2058`):** Replace fabricated snippet with verbatim lines `2040-2058`, prioritize `data['unit_cost_cents']` / `data['unit_cost']`, and compute `((numCost * 100.0) / cleanQty).round()` (`ROUND_HALF_UP`).
4. **`MUST-FIX 4` (`E4a` Title-Case Key Lookup in `my_collection_screen.dart:3016-3022`):** Must include Title-Case `m['Purchase Cost']` and `m[_F.cost]` (`'Cost'`) + `m['paper_trail']['purchase_price']`.
5. **`MUST-FIX 5` (`E4b` Helper Name in `my_collection_screen.dart:1042` & `3000`):** Call existing `_conditionLabel(...)` at line 3000 instead of non-existent `_normalizeCondition(...)`.
6. **`MUST-FIX 6` (`_CollectionCardImage` Line Citation `6358-6360` & Year-Guard Regex Scope):** Cite lines `6358-6360` and restrict Year Guard regex `(?:^|[^0-9])(1[789]\d\d|20\d\d)(?:$|[^0-9])` to decoded filename basename after stripping `\d{3,4}x\d{3,4}` dimensions.

---

## Handoff & Next Steps

- **Full Review + Plan Staged in `For SAG`:** Copied `FAILFIX_PLAN_NET-647_R2.8_20261031.md` and `GEMINI38_REVIEW_NET-647_R2.8_2026-10-31.md` to `"C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\31 OCT 2026\For SAG\"`.
- **Turn:** **GROK COS / AG CoS v4 (`ba2bfdb2`)** for fix-only `R2.8.1` incorporating `MUST-FIX 1` through `MUST-FIX 6` $\rightarrow$ Argon + Grok CoS $\ge 95$ $\rightarrow$ SAG $\rightarrow$ Eric's typed `YES` $\rightarrow$ `EXECUTE` on `p7-v8.9`.
- **Locks Unchanged:** `origin/main` = `9f04550a`, `origin/dev` = `9b55f3d9`, Stripe OFF.

OVER.
