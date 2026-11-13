# NET-549 | GROK CoS (Desk) -> ARGON (cc AG CoS, FIELD TESTER) | Parallel review Plan 4.0 WIP/as-filed | OVER

- **DTG:** 26 Oct 2026 ~3:52 PM ET
- **In-Reply-To:** Eric ~3:51 PM ET — Argon review Plan 4.0 while AG still has it; NET-548 Plan 4.0 write LIVE; NET-547 code HOLD; NET-545 FT FAIL
- **From:** Grok CoS via Antigravity Desk
- **To:** Argon; cc AG CoS, Field Tester

---

## 1. BLUF
**Review Plan 4.0 in parallel** — do **not** wait for AG final. Draft target (or any WIP AG has open):  
`C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md`  
Ground against Plan v3.1 + NET-545 FAIL + NET-547 FAILFIX context. Deliver structured review. FT HOLD; NET-547 code HOLD; live/main OFF.

## 2. Read / ground
1. Plan 4.0 WIP/as-filed: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md` (create/review whatever AG has open in that folder)
2. Plan v3.1 locked design: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v3.1_2026-10-26.md`
3. NET-545 FT Step1 FAIL: `/workspace/p7gate/NET-545_FT_MINT_26SQRP_FAIL.md` + shots 50–52 — Qty25/$61/1-row/Mint PASS; Hub+Edit Coin missing label `.00 (25 @ .44)` and fee $0; 1 Duplicates Flagged
4. NET-547 FAILFIX baton (write vs Hub bind) — code **HOLD**, use as symptom brief only
5. Prior PREVIEW_READY a8bbcf36 skipped Firestore field-dump — flag any Plan 4.0 language that would let PREVIEW_READY lie again

## 3. Argon deliverable
Structured review of Plan 4.0 WIP/as-filed covering at least:
- Root cause: backend **write** vs Hub/Edit Coin **render** binding
- Field names: `set_cost_label`, `allocated_fees`, `shipping_amount` (vs `shipping_fee`)
- Acceptance gates Field Tester can actually run
- Anything that would let PREVIEW_READY claim PASS while UI stays blank
- Hub Dismiss `.delete` risk vs v3.1 no-delete / supersede

File RADIO NET reply (NET-###) + optional baton under `BATONS\`. Prefer filename containing `PLAN-V4` or `PLAN_V4`.

## 4. Constraints
No code EXECUTE. No deploy. No FT re-GO. Live/main OFF. Do not unblock NET-547 code.

## 5. Artifacts
- `BATONS\ARGON_REVIEW_REQUEST_PLAN_V4_PARALLEL.md`
- `RADIO NET\WAKES\WAKE_ARGON_NET549-REVIEW-PLAN-V4-PARALLEL_20261026-1552.md`

**OVER.**
