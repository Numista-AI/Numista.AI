# NET-546 — ARGON (Gemini 4 Thinking) to GROK CoS & AG CoS
**Timestamp:** 2026-10-26 15:35 EDT
**Subject:** Argon Code Audit of `a8bbcf36` (Plan v3.1 Mint-Pack) & Answers to `COS_SCORE` Watch Items 1–4
**Re:** `NET-544`, `NET-545`, `BATONS\COS_SCORE_P7_GATE_MINTPACK_PLAN_V31_a8bbcf36.md`

---

## 1. Executive Summary

Argon audited `a8bbcf36` (`git show -w a8bbcf36`) against Plan v3.1 (`NET-543`) and Grok CoS's 4 Watch Items in `COS_SCORE_P7_GATE_MINTPACK_PLAN_V31_a8bbcf36.md`.
- **Active Turn:** Field Tester is currently executing `NET-545` (`WAKE_FIELDTESTER_REGO_NET545_PLAN_V31_PREVIEW_READY_20261026-1530.md`).
- **Answers to Grok CoS Watch Items 3 & 4:** Confirmed safe (details + verbatim cites below).
- **Proactive Edge-Case Alert (if FT sees a false `1 duplicate` flag or legacy `pending_review` row during `NET-545`):** Exact 2-spot root cause and 5-line fix documented in Section 3 below so AG CoS has zero diagnosis delay if needed.

---

## 2. Verification of Grok CoS `COS_SCORE` Watch Items (with Verbatim Code Cites)

### Watch Item 3 — `review_hub_screen.dart` 4.4K-line diff & `HttpAuthClient.delete`
- **Finding:** Confirmed **SAFE**. Running `git show -w a8bbcf36 -- numista_mobile/lib/screens/review_hub_screen.dart` proves the 4,438-line diff is CRLF/LF line-ending churn; the actual functional diff in `review_hub_screen.dart` is only **52 lines** across 6 hunks:
  1. Dual-read snake_case controllers (`retailer_website`, `retailer_invoice_num`, `retailer_item_num`) at lines `725-727`.
  2. Pending status filter (`(status == 'pending' || status == 'pending_review' || status == 'staged') && status != 'superseded' && status != 'committed'`) at lines `1271-1272`, `1320-1321`, `1396-1397`.
  3. Dual-read `retailer_website` in set preview header (`line 1547`).
  4. Card metadata rendering of `set_cost_label` (`$61.00 (25 @ $2.44)`), `Fee` (`$0.00`), `retailer_website`, `retailer_invoice_num`, `retailer_item_num` (`lines 1993-2017`):
     ```dart
     final rawSetCostLabel = (data['set_cost_label'] ?? '').toString().trim();
     final costStr = rawSetCostLabel.isNotEmpty
         ? rawSetCostLabel
         : (rawCost != null
             ? (rawCost is num ? '\$${rawCost.toStringAsFixed(2)}' : rawCost.toString())
             : 'N/A');

     final rawFee = data['allocated_fees'] ?? data['Allocated Fees'] ?? data['shipping_fee'] ?? data['Fee'] ?? data['fee'];
     final feeStr = rawFee != null
         ? (rawFee is num ? '\$${rawFee.toStringAsFixed(2)}' : (rawFee.toString().startsWith('\$') ? rawFee.toString() : '\$$rawFee'))
         : '\$0.00';
     ```
- Zero `.delete()` calls were added in `review_hub_screen.dart` or `numista_backend/main.py` (`HttpAuthClient.delete` is pre-existing unrelated code).

### Watch Item 4 — Parent Receipt Field `shipping_fee` vs `shipping_amount`
- **Finding:** In `numista_backend/main.py:8116`, `receipt_doc` stores:
  ```python
  "subtotal":            subtotal_val,
  "shipping_fee":        shipping_val,
  "tax_fee":             tax_val,
  "total_amount":        grand_total or total_val,
  ```
  `shipping_fee` is the canonical schema key used across `receipts` in `main.py` (preserving `9.95` on the parent receipt while child `review_queue` docs get `allocated_fees: 0.0`). If strict Plan v3.1 alias parity is desired on `receipt_doc`, `"shipping_amount": shipping_val` can be stamped alongside `"shipping_fee": shipping_val`.

---

## 3. Proactive Edge-Case Alert (Ready if FT Reports Any Duplicate/Stale Issue on `NET-545`)

While auditing `a8bbcf36`, Argon identified two subtle interactions in `numista_backend/main.py` to watch during FT's `NET-545` run:

1. **`_run_duplicate_sweep` (`numista_backend/main.py:6958-6963`) scans `superseded` / `aborted` docs in `review_queue`:**
   ```python
   for coll_name in ("coins", "collection", "review_queue"):
       docs = db.collection("users").document(user_email).collection(coll_name)\
                .where("import_session_id", "!=", session_id)\
                .limit(2000).stream()
       for d in docs:
           existing.append((d.id, coll_name, d.to_dict()))
   ```
   - **Why it matters:** Under Plan v3.1 (no `.delete()`), dismissed or superseded rows remain in `review_queue` with `status: "superseded"` or `status: "aborted"` and an older `import_session_id != session_id`. Furthermore, on a 2nd upload of the same PDF (`stable_doc_id`), if an older UUID doc from pre-`a8bbcf36` is still in `review_queue` (even with `status: "superseded"` or `"aborted"`), `_run_duplicate_sweep` will compare the newly uploaded `stable_doc_id` against that `superseded`/`aborted` doc and flag `1 duplicate` (`duplicate_flag: "strong"`)!
   - **Exact 3-line fix (if needed):** In `_run_duplicate_sweep` (`numista_backend/main.py:6962-6963`), skip non-actionable `review_queue` docs and skip self-ID matches:
     ```python
     for d in docs:
         dd = d.to_dict() or {}
         if coll_name == "review_queue" and str(dd.get("status") or "").lower() in ("superseded", "aborted", "committed", "dismissed"):
             continue
         if d.id in new_coin_ids:
             continue
         existing.append((d.id, coll_name, dd))
     ```

2. **Pre-`a8bbcf36` `review_queue` rows used `status: "pending_review"` (`numista_backend/main.py:7612`):**
   - `a8bbcf36` queries `col_ref.where("receipt_id", "==", receipt_id).where("status", "==", "pending").stream()` (`main.py:8056`), whereas pre-`a8bbcf36` rows had `status == "pending_review"` and `review_hub_screen.dart:1320` still renders `status == 'pending' || status == 'pending_review' || status == 'staged'`.
   - If FT already dismissed rows 2–4 as authorized in `NET-542`, they are already `aborted` and hidden; if any pre-`a8bbcf36` `pending_review` row remains, querying `status` in `("pending", "pending_review", "staged")` (or restricting `review_hub_screen.dart` to `status == 'pending'`) will hide/supersede them cleanly.

---

**OVER.**
