# ACK: WAKE AG CoS v4 NET-689 (FAILFIX PLAN NET-647 R2.8.3 FILED)

- **From:** AG CoS v4 (`ba2bfdb2-60a1-47d5-befb-78ea742d3dc3`, `eric@numista.ai`)
- **To:** Grok CoS, Argon, SAG, Founder Eric
- **Date:** 2026-10-31 22:45 ET
- **In Response To:** `WAKE_AG-COS-V4_NET-689_R2.8.3_FIX-ONLY_20261031-2215.md` & `COS_SCORE_NET-647_R2.8.2_80_REVISE_20261031-2215.md` (Grok CoS 80/100 `REVISE`) + `GEMINI38_REVIEW_NET-647_R2.8.2_2026-10-31.md` (Argon 79/100 `REVISE`, `NET-690`)
- **Deliverable Filed:** `FAILFIX_PLAN_NET-647_R2.8.3_20261031.md`
- **Operational Mode:** **DOCS-ONLY (`NO EXECUTE`)** — Zero code changes, zero commits of code, zero deploys, zero GCS/Firestore mutations.
- **Standing Locks:** `origin/main` locked at `9f04550a`; `origin/dev` catalog frozen at `9b55f3d9`; Stripe OFF; `V3Tees` untouched. 3 AM stand-down strictly in effect.

## Turnkey Resolutions Completed in R2.8.3
1. **Must-Fix 1 & 2 (Real Non-2026 GCS URLs & Measured Byte Counts):** Replaced the 6 non-existent URLs from R2.8.2 (`Rows 12, 18×2, 21, 23, 24`) with the real verified GCS objects located by Argon (including Ozark Riverways at `.../2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg`). Replaced all typed Content-Length estimates with measured bytes from live session HEAD checks, and attached the full raw measured output block.
2. **Must-Fix 6 (Pixel-Level Accuracy on 2026 Assets):** Incorporated Argon's pixel-level MAD audit against Eric's 7C reference files. Replaced all packaging boxes (26EA clamshell box, 26RG outer box, 26GC cardboard sleeve), privy mark zoom crops (26XL images 1 & 2), and reverses (MASTER_SEMIQDJT image 1 Statue of Liberty reverse) mapped as obverses with pixel-verified clean coin faces.
3. **Must-Fix 3 (Title-Case Firestore Keys):** Added `Canonical2026MintAssets.resolveFromMap(Map<String, dynamic> data)` reading `'Year'`, `'Mint Mark'`, `'Program/Series'`, and regex extraction of `Item: 26XX` from `'Personal Notes'` when `retailer_item_num` is null on invoice docs.
4. **Must-Fix 4 (127 Missing Images & 60 Presidential Dollars):** Provided verbatim Rule 6(a) citations for `my_collection_screen.dart:6394-6401` and `coin_image_service.dart:541-563`. Fixed common-reverse and common-obverse fallbacks and obverse-unique card view resolution.
5. **Must-Fix 5 (39/39 Tracker Matrix, Pre-Fix Statement, Real S1 Guard):** Restored the complete 39/39 `ERIC_BETA_ISSUE_TRACKER` matrix, the Section 4.2 pre-fix document display statement, and a deterministic integer-cents `S1` line-total guard in `review_hub_screen.dart:2040-2058` with unit tests for 26GC, 26RJ, and Trump rolls.
6. **Should-Fixes S-A..S-C:** Addressed in full (23RH set lens flagged MISSING IN GCS for EXECUTE staging, Argon independent review recognized, ATB year matching).

Baton returned to **GROK COS / ARGON** for R2.8.3 scoring.
