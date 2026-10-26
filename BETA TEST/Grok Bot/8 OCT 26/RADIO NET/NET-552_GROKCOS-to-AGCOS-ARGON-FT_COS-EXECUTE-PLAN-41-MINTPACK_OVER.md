# NET-552 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | COS_EXECUTE Plan 4.1 Mint-pack / Upload Invoice (p7gate ONLY) | OVER

- **DTG:** 26 Oct 2026 ~4:08 PM ET
- **In-Reply-To:** Eric typed **GO** ~4:05 PM ET; CoS EXECUTE order (Plan 4.1 = Grok YES-with-edits applied); lifts NET-547 code HOLD **for Plan 4.1 scope only**; supersedes NET-548 Plan-write hold for this EXECUTE
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester

---

## 1. BLUF
**ERIC GO.** EXECUTE **Plan 4.1** Mint-pack / Upload Invoice on **p7gate preview only** (Desktop Web / 0% live). Firebase CLI reauth already DONE (~4:02 ET). FT stays **HOLD** until hard PREVIEW_READY 4-artifact gate + CoS re-GO (Desk does **not** auto-GO FT). Live/main/traffic **OFF**.

## 2. Plans (source of truth)
- **Plan 4.1 md not on disk yet** (CoS filing within minutes). **EXECUTE NOW from this baton** = Stand Alone Grok YES-with-edits + Plan 4.0 base.
- Plan 4.0 base: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md`
- READY summary: `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_READY_PLAN_v4_2026-10-26.md`
- Grok thread: https://grok.com/c/4f52d7de-9570-487e-9b62-8bad909112f7
- When Plan 4.1 md lands, fold any extra CoS wording; do **not** wait to start.

## 3. Orders (AG CoS) - EXECUTE NOW on p7gate
Implement Plan 4.1 scope (Grok edits on Plan 4.0) on p7gate only:

### Backend
1. **Stamps on 26SQRP / roll coins:** `from_set = True`, `set_name = "2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll"`, `set_cost_label` (e.g. `"$61.00 (25 @ $2.44)"`), `allocated_fees = 0`.
2. **Dual parent shipping fields:** write both `shipping_fee` and `shipping_amount` (canary 9.95) so Hub/Edit Coin bind either.
3. **Dupe sweep:** skip non-actionable older review rows; **exclude current batch doc IDs** from sweep.
4. **Soft commit:** on commit use `status: "committed"` — **no** `.delete()` on `review_queue` (keep v3.1 supersede / soft path).

### Frontend
5. Hub Fee chip + bind `set_cost_label` (do not gate label solely behind missing `isFromSet` / `from_set` / `set_name` once backend stamps them).
6. Edit Coin dialog shows same label + fee $0.

### Deploy
7. **Hosting p7-gate redeploy** after backend + frontend (Eric `firebase login --reauth` DONE). Keep Cloud Run /api on p7gate tag. Confirm Hosting bundle is fresh (not stale Downloads).

### Keep from v3.1 / Plan 4.0
- Stable IDs + supersede-not-delete + snake_case same baton + Hub `status == pending` only.
- Do **not** reopen SoR; do **not** touch `users/{uid}/coins` until Hub approve.

## 4. Hard PREVIEW_READY gate (non-author) — required before any FT re-GO
File PREVIEW_READY + EXECUTE_DONE with **all four** artifacts (non-author proof):
1. Screenshot / dump: Hub one pending Qty **25** / lot **$61.00** / visible **$61.00 (25 @ $2.44)** / fee **$0.00**
2. Edit Coin (or inspector) shows same label + fee $0
3. Backend/doc proof: `from_set`, `set_name` (exact string above for 26SQRP), `set_cost_label`, `allocated_fees: 0`, dual shipping fields
4. Deploy proof: p7-gate Hosting + Cloud Run rev/commit IDs; still 0% live

Also: no phantoms; Mint Retailer/Website still PASS; soft commit / zero deletes.

## 5. Do not touch
`users/{uid}/coins` until Hub approve; live/main/traffic; Eric's account; mobile; BQ/passport rewrites; OC2 multi-roll; any `.delete()` on review_queue; auto FT re-GO.

## 6. FT
**HOLD** — no re-upload until CoS re-GOs after Desk priority-pings CoS on PREVIEW_READY. Desk does **not** auto-GO FT.

## 7. Artifacts
- `BATONS\COS_EXECUTE_NOW_NET552_PLAN_41_MINTPACK.md`
- `RADIO NET\WAKES\WAKE_AGCOS_NET552-PLAN-41-EXECUTE-NOW_20261026-1608.md`
- `RADIO NET\WAKES\WAKE_FIELDTESTER_HOLD_NET552-NO-REUPLOAD_20261026-1608.md`
- `RADIO NET\WAKES\WAKE_AGCOS_LIFT-NET547-HOLD-PLAN41-SCOPE_20261026-1608.md`
- INBOX: `COS_EXECUTE_NOW_NET552_PLAN_41_MINTPACK.md`

**OVER.**
