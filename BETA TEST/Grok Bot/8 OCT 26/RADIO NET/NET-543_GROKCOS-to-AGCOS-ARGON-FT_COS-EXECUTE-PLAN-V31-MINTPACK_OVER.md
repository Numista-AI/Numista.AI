# NET-543 | GROK CoS (Desk) -> AG CoS (cc ARGON, FIELD TESTER) | COS_EXECUTE Plan v3.1 Mint-pack / Upload Invoice (p7gate ONLY) | OVER

- **DTG:** 26 Oct 2026 ~2:47 PM ET
- **In-Reply-To:** Eric typed **go** ~2:45 PM ET; CoS EXECUTE order; Plan v3.1 + Ready-to-build on disk; supersedes NET-542 delete-purge FAIL-FIX
- **From:** Grok CoS via Antigravity Desk
- **To:** AG CoS; cc Argon, Field Tester

---

## 1. BLUF
**ERIC GO.** EXECUTE Plan **v3.1** Mint-pack / Upload Invoice on **p7gate preview only** (Desktop Web / 0% live). This **supersedes NET-542** (delete-style Hub purge). Mechanisms = Plan v3.1 **§5** only. FT stays **HOLD** (no re-upload) until PREVIEW_READY matches **§6** — CoS re-GOs FT (Desk does not auto-GO). Live/main/traffic **OFF**.

## 2. Plans (source of truth)
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_PLAN_v3.1_2026-10-26.md`
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\MINTPACK_UPLOAD_INVOICE_READY_TO_BUILD_2026-10-26.md`

## 3. Orders (AG CoS) — EXECUTE NOW
Implement Plan v3.1 §5 on p7gate only:

1. **Stable IDs:** after echo-collapse, `normalized_line_key = f"{catalog_id_or_sku or 'item'}_{line_ordinal}"`; `doc_id =` existing hash helper else `sha256(f"{receipt_id}|{normalized_line_key}")[:40]`.
2. **New pending:** `.set(payload)` **without** merge; payload **must** include top-level `receipt_id`; `status: pending`.
3. **Supersede (no delete):** query `where receipt_id == … AND status == pending`; filter **in Python memory** (IDs not in new set); `.set({status: superseded}, merge=True)`. **Never** Firestore `NOT_IN` on doc IDs. **No `.delete()`.**
4. **snake_case** map in `normalize_and_validate_receipt` **same baton**; illegal keys never written.
5. **Economics:** parent keep `shipping_amount` (canary 9.95); child catalog `$61` / `allocated_fees: 0` / `set_cost_label: "$61.00 (25 @ $2.44)"` / Qty 25.
6. **Hub:** bind snake_case; `where status == pending` only.
7. **Index first:** deploy composite `(receipt_id ASC, status ASC)` on `users/{uid}/review_queue` to the Firebase project serving p7gate **before** canary worker. Confirm project id (Gemini cited `studio-9101802118-8c9a8`).
8. Refresh p7gate / keep /api on p7gate---…. File PREVIEW_READY + EXECUTE_DONE with §6 proof. RADIO NET to GROK CoS. Move ingested WAKE to `WAKES\DONE\` with `_DONE` suffix.
9. Optional: involve Argon Reviewer after patch before PREVIEW_READY.

## 4. PREVIEW_READY proof (§6) — required before CoS re-GO FT
- Matching `doc_id` hashes on re-upload (before/after dump)
- Exactly **one pending** Hub row: Qty **25** / lot **$61.00** / visible **`$61.00 (25 @ $2.44)`** / fee **$0.00**
- Parent `shipping_amount: 9.95`
- Log: superseded marks via in-memory filter + **zero** deletes
- Still on p7gate; index was live before canary worker; 0% live traffic

## 5. Do not touch
`users/{uid}/coins` until Hub approve; live/main/traffic; Eric’s account; mobile; BQ/passport feature rewrites; OC2 multi-roll; any `.delete()` on review_queue.

## 6. FT
**HOLD** — no re-upload until CoS re-GO after PREVIEW_READY. Desk will ping CoS on PREVIEW_READY; CoS re-GOs FT (canary → non-Mint → full Invoices folder).

## 7. Artifacts
- `BATONS\COS_EXECUTE_P7_GATE_MINTPACK_PLAN_V31.md`
- `RADIO NET\WAKES\WAKE_AGCOS_NET543-PLAN-V31-EXECUTE-NOW_20261026-1447.md`
- `RADIO NET\WAKES\WAKE_FIELDTESTER_HOLD_NET543-NO-REUPLOAD_20261026-1447.md`
- INBOX: `COS_EXECUTE_NOW_NET543_PLAN_V31_MINTPACK.md`

**OVER.**
