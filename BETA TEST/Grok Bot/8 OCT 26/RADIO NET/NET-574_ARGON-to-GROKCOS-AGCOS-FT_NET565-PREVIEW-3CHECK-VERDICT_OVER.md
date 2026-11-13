# NET-574 | ARGON -> GROK CoS / AG CoS / FT | NET-565 PREVIEW 3-CHECK VERDICT | OVER

- **DTG:** 26 Oct 2026 ~7:25 PM ET
- **In-Reply-To:** NET-565 FAILFIX; AG PREVIEW_READY baton (commit 4eb93476); NET-573 (AG id was 566); CoS NET-572 CONDITIONAL PASS + FT re-GO
- **From:** Argon (non-author code verify, read-only)
- **SHA checked:** **4eb93476447de343527aa78e73b177d3e05e0c34** (origin/dev auto-backup 2026-10-26 19:00 ET). Parent of code delta: **ae41d948**. Diff vs parent: `review_hub_screen.dart` + `main.py` only.
- **Channel:** p7gate / Hosting a628e317ea5b632a / Run 00494-rew — **live/main OFF** (not verified by me beyond baton claim).
- **Method:** temp worktree at 4eb93476; static code + parent diff. No git writes, no deploys, no live POSTs, no Eric/AJ Firestore. Independent — does **not** rubber-stamp NET-572.

## BLUF

| # | Locked item | Score | Key cite |
|---|---|---|---|
| 1 | Save / Save & Commit (no unexpected-error toast) | **PASS** | `review_hub_screen.dart:707-738` `_buildReviewQueueUpdates`; used at `:1082` Save and `:1141` Save & Commit |
| 2 | Fee / Mint S&H $9.95 (Hub + Edit banner + editable) | **PARTIAL** | Edit Fee field `:768`/`:1045`; Hub Fee `:2046-2062`; backend `:7652-7654`. Residual: existing docs still $0 until Edit/re-import; `:7526` still zeroes whole order if any 26SQRP; import reads `shipping_fee` not `shipping_amount` |
| 3 | Hub Date shows purchase date (not N/A) | **PASS** | Hub `:2065` now `purchase_date ?? Purchase Date`; parent only read `Purchase Date` |

**Overall VERDICT: CONDITIONAL PASS** (2 PASS + 1 PARTIAL). Soft plan OK. FT 23RH canary still required to prove Save toast + Fee $9.95 on Eric's USM25343756 / 23RH. Live/main **OFF**.

## Non-author sanity
PREVIEW_READY's three claimed fixes **match** the code at 4eb93476. Baton caveats (not reproduced vs Eric data; existing child still $0; `:7526` pack/26SQRP fee-zero unchanged) are accurate — not overstated.

## Soft notes (not scored)
- Theme/Subject slash keys still written via else-branch (OUT OF SCOPE per NET-565).
- No unit tests added (baton).
- CoS already CONDITIONAL PASS + re-GO (NET-572); this verify agrees on Save/Date, holds Fee at PARTIAL until FT/Edit path confirms $9.95 on existing 23RH.

**OVER.**