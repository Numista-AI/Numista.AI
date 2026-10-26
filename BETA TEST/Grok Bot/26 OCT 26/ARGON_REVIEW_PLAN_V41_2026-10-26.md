# DESK COPY / RENAME for CoS naming (NET-555)
**Source:** Argon NET-554 structured review filed as `ARGON_REVIEW_PLAN_V4_2026-10-26.md` (~4:13–4:16 ET)  
**Why:** CoS required deliverable name `ARGON_REVIEW_PLAN_V41_…` (Plan 4.1 object). Content below is **Argon-authored** — Desk only renamed/copied.  
**Verdict (Argon):** YES WITH 3 MANDATORY 4.1.x SURGICAL ADDITIONS — fold into NET-552 EXECUTE (WAKE_AGCOS fold already LIVE). Not a hard STOP of EXECUTE unless CoS says otherwise.  
**Desk DTG:** 26 Oct 2026 ~4:18 PM ET

---
# ARGON STRUCTURED REVIEW — `MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md` & `v4.1` (with 4.1.x Patch Items)

**Date:** 2026-10-26 16:13 EDT  
**Reviewer:** Numista.Ai Argon (Gemini 4 Argon — Thinking Jobs Only)  
**Target Plans:**
- `MINTPACK_UPLOAD_INVOICE_PLAN_v4_2026-10-26.md` (and `MINTPACK_UPLOAD_INVOICE_READY_PLAN_v4_2026-10-26.md`)
- `MINTPACK_UPLOAD_INVOICE_PLAN_v4.1_2026-10-26.md` (`NET-552` / `NET-553` — `COS_EXECUTE` active; non-conflicting Argon items to be folded into **4.1.x** patch)

---

## Executive Verdict: **YES WITH 3 MANDATORY 4.1.x SURGICAL ADDITIONS**

Plan 4.1 (`NET-552` / `NET-553`) accurately identifies the stale `p7-gate` Firebase Hosting bundle (`version 6827e011bc9e8619`, deployed at 11:55 AM before `a8bbcf36`), the `_run_duplicate_sweep` bug on non-`pending` `review_queue` docs, and the `commit_items` `.delete()` replacement.

However, verbatim code audit of `numista_backend/main.py` and `numista_mobile/lib/screens/review_hub_screen.dart` at commit `a8bbcf36` uncovered **three concrete gaps in Plan 4.0 / 4.1** that **will cause either `NET-547` Acceptance Gate #4 (Edit Coin dialog) or Gate #5 (pure `snake_case` / zero illegal keys) to FAIL** unless folded into AG CoS's **4.1.x** build now:

1. **[4.1.x ADDITION #1 — Edit Coin Dialog Missing `Fee: $0.00` (`review_hub_screen.dart:825-830, 982-990`)]:** Plan 4.0/4.1 §3.2 item 2 adds `'Package/Roll: ' + data['set_cost_label']` to `_showCoinEditDialog`, **but omits `Fee: $0.00` (`allocated_fees`) inside the Edit Coin dialog**, even though `NET-547` Order #1, Plan 4.1 §4 Gate #4, and Plan 4.1 §6 Artifact #2 explicitly require **both** `$61.00 (25 @ $2.44)` **and** `Fee: $0.00` on the Edit Coin dialog.
2. **[4.1.x ADDITION #2 — Hidden Illegal-Key Re-Injection in `_link_receipts_to_coins` (`main.py:7127-7146`) & `normalize_and_validate_receipt` (`main.py:7602-7639`, `8088-8095`)]:** Plan 4.1 §1 item 4 mandates: *"Illegal keys (`Retailer/Website`, `Retailer Invoice #`, `Allocated Fees`, etc.) are never written."* Yet Plan 4.1 §3.1 (`line 89`) still writes `doc["Allocated Fees"] = 0.00`, `main.py:7602-7609, 8089-8093` still writes `"Retailer/Website"`, `"Retailer Invoice #"`, `"Retailer Item No."`, `"Allocated Fees"`, and worse, `_link_receipts_to_coins` (`main.py:7127-7146`) runs at the end of `_execute_import_process_worker` (`line 8314`) and **re-injects `"Retailer/Website"` and `"Retailer Invoice #"` into every linked `review_queue` doc via `.set(..., merge=True)`**!
3. **[4.1.x ADDITION #3 — Hub Actionable Read Filter (`review_hub_screen.dart:1271, 1320, 1396`) & Initial Status (`main.py:7612`)]:** Plan 4.1 §2.4 & §3.1 item 5 mandate `status == "pending"` only, whereas `review_hub_screen.dart` (`lines 1271, 1320, 1396`) currently accepts `status == 'pending' || status == 'pending_review' || status == 'staged'`, and `main.py:7612` initializes `"status": "pending_review"` (and `main.py:8056` only supersedes `status == "pending"`, leaving any `pending_review` docs unsuperseded).

---

## Detailed Review by `NET-549` / `NET-551` Focus Area (with Verbatim Code Cites per Rule 6a)

### 1. Root Cause: Backend Write vs. Hub / Edit Coin Render Binding

- **Backend Write (`numista_backend/main.py:7631-7640`):** Commit `a8bbcf36` (`p7gate` `00492-gus`) **did** compute and write `set_cost_label` and `allocated_fees` on the `26SQRP` child doc:
  ```python
  # numista_backend/main.py:7631-7640
          if qty_val > 1 and cost_val > 0:
              unit_val = round(cost_val / qty_val, 2)
              doc["unit_cost"] = unit_val
              doc["set_cost_label"] = f"${cost_val:.2f} ({qty_val} @ ${unit_val:.2f})"
              doc["Purchase Cost"] = cost_val
              doc["Cost"] = cost_val
          if "allocated_fees" not in doc:
              doc["allocated_fees"] = 0.0
              doc["Allocated Fees"] = 0.0
  ```
- **Hub Card Render (`numista_mobile/lib/screens/review_hub_screen.dart:1993-2016`):** Commit `a8bbcf36` **did** add `set_cost_label` to the `'Cost'` meta item and added `_buildMetaItem('Fee', feeStr, Icons.local_shipping_outlined)` in git:
  ```dart
  // numista_mobile/lib/screens/review_hub_screen.dart:1993-2016
                            Builder(builder: (context) {
                              final label = data['set_cost_label']?.toString() ?? '';
                              final rawCost = data['Purchase Cost'] ?? data['Cost'] ?? data['cost'];
                              final costStr = label.isNotEmpty
                                  ? label
                                  : (rawCost != null && rawCost.toString().isNotEmpty ? '\$$rawCost' : '—');
                              return _buildMetaItem('Cost', costStr, Icons.sell_outlined);
                            }),
                            const SizedBox(width: 24),
                            Builder(builder: (context) {
                              final rawFee = data['allocated_fees'] ?? data['Allocated Fees'] ?? 0.0;
                              final feeNum = rawFee is num ? rawFee.toDouble() : (double.tryParse(rawFee.toString()) ?? 0.0);
                              final feeStr = '\$${feeNum.toStringAsFixed(2)}';
                              return _buildMetaItem('Fee', feeStr, Icons.local_shipping_outlined);
                            }),
  ```
  **Why the Hub Card was blank in `NET-545`:** As confirmed in `NET-546` and Plan 4.1 §2.1, AG CoS never ran `flutter build web` + `firebase deploy --only hosting:p7-gate` after `a8bbcf36`. The live `p7-gate` channel (`https://numista-vault--p7-gate-8avtpz22.web.app`) was still serving the 11:55 AM (`NET-535`) bundle (`version 6827e011bc9e8619`).
- **Edit Coin Dialog Render (`numista_mobile/lib/screens/review_hub_screen.dart:723-730, 820-830, 982-1001`):** Even in `a8bbcf36`, `_showCoinEditDialog` was **never updated** to show `set_cost_label` OR `Fee: $0.00`:
  ```dart
  // numista_mobile/lib/screens/review_hub_screen.dart:723
      'Purchase Cost': TextEditingController(text: (data['Purchase Cost'] ?? data['Cost'] ?? '').toString()),
  ```
  ```dart
  // numista_mobile/lib/screens/review_hub_screen.dart:820-830
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Edit Coin Details', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                          if ((data['Retailer Item No.'] ?? '').toString().isNotEmpty)
                            Text('Mint ID: ${data['Retailer Item No.']}', style: const TextStyle(color: Color(0xFFD4AF37), fontSize: 12)),
                        ],
                      ),
                    ),
  ```
  ```dart
  // numista_mobile/lib/screens/review_hub_screen.dart:982-989
                      sectionHeader('PURCHASE'),
                      Row(children: [
                        Expanded(child: field('Purchase Cost', 'Purchase Cost', Icons.attach_money,
                            keyboardType: const TextInputType.numberWithOptions(decimal: true))),
                        const SizedBox(width: 12),
                        Expanded(child: field('Quantity', 'Quantity (QTY)', Icons.numbers,
                            keyboardType: TextInputType.number)),
                      ]),
  ```
  - **4.1.x Fix Required in `_showCoinEditDialog` (`review_hub_screen.dart`):**
    1. In the header column (`lines 825-829`), check `data['retailer_item_num'] ?? data['Retailer Item No.']` for Mint ID, and when `(data['set_cost_label'] ?? '').toString().isNotEmpty`, render both the package breakdown and the allocated fee in the subtitle (and/or under `sectionHeader('PURCHASE')` at `line 982`):
       - Subtitle / read-only banner under `PURCHASE`: show `'Package/Roll: ${data['set_cost_label']}  •  Fee: \$${feeNum.toStringAsFixed(2)}'` (so both `$61.00 (25 @ $2.44)` and `Fee: $0.00` are unmistakably visible in the Edit Coin dialog for FT Step 1).

---

### 2. Field Names: `set_cost_label`, `allocated_fees`, `shipping_amount` (vs `shipping_fee`), and Illegal Keys

- **`shipping_amount` vs `shipping_fee` on Parent Receipt (`numista_backend/main.py:8097-8126`):**
  ```python
  # numista_backend/main.py:8097-8105
                      raw_ship = item_data.get("shipping_fee") or item_data.get("shipping_handling") or item_data.get("Shipping") or 0.0
                      try:
                          ship_val = float(re.sub(r'[^\d.-]', '', str(raw_ship))) if raw_ship else 0.0
                      except Exception:
                          ship_val = 0.0
                      raw_total = item_data.get("total_invoice_cost") or item_data.get("Total") or (float(cost_val or 0.0) + ship_val)
  ```
  ```python
  # numista_backend/main.py:8118-8125
                          "shipping_amount": ship_val,
                          "total_amount": tot_val,
                          "subtotal": float(cost_val or 0.0),
                          "matched_coin_ids": [coin_id],
  ```
  - Parent receipt doc writes `"shipping_amount": ship_val` (`0.0` for `26SQRP`). Plan 4.1 §3.1 item 1 also adds `"shipping_fee": 0.0` on the child doc alongside `"allocated_fees": 0.00`, which is safe and backwards-compatible.
- **CRITICAL 4.1.x Fix — Eliminate Illegal Keys Across All Three Write Sites in `numista_backend/main.py`:**
  - **Write Site A (`normalize_and_validate_receipt`, `numista_backend/main.py:7602-7639`):**
    ```python
    # numista_backend/main.py:7602-7609
        doc["Retailer/Website"] = canonical_retailer
        doc["retailer_website"] = canonical_retailer
        doc["Retailer Invoice #"] = clean_inv_num
        doc["retailer_invoice_num"] = clean_inv_num
        doc["Retailer Item No."] = item_num
        doc["retailer_item_num"] = item_num
        doc["Purchase Date"] = raw_date
        doc["purchase_date"] = raw_date
    ```
    and `line 7639`:
    ```python
            doc["Allocated Fees"] = 0.0
    ```
    **Must remove** `"Retailer/Website"`, `"Retailer Invoice #"`, `"Retailer Item No."`, and `"Allocated Fees"` from `doc` (keep `retailer_website`, `retailer_invoice_num`, `retailer_item_num`, `purchase_date`, `allocated_fees`). Also remove `doc["Allocated Fees"] = 0.00` from Plan 4.1 §3.1 snippet (`line 89`).
  - **Write Site B (`_execute_import_process_worker`, `numista_backend/main.py:8088-8095`):**
    ```python
    # numista_backend/main.py:8088-8095
                    item_data["retailer_website"] = item_data.get("retailer_website") or item_data.get("Retailer/Website") or "US Mint"
                    item_data["Retailer/Website"] = item_data["retailer_website"]
                    if item_data.get("retailer_invoice_num") or item_data.get("Retailer Invoice #"):
                        inv_val = item_data.get("retailer_invoice_num") or item_data.get("Retailer Invoice #")
                        item_data["retailer_invoice_num"] = inv_val
                        item_data["Retailer Invoice #"] = inv_val
                    if "allocated_fees" not in item_data:
                        item_data["allocated_fees"] = 0.0
    ```
    **Must remove** `item_data["Retailer/Website"] = ...` and `item_data["Retailer Invoice #"] = ...` (and explicitly `item_data.pop("Retailer/Website", None)`, `item_data.pop("Retailer Invoice #", None)`, `item_data.pop("Retailer Item No.", None)`, `item_data.pop("Allocated Fees", None)` before `review_ref.set(item_data)`).
  - **Write Site C (`_link_receipts_to_coins`, `numista_backend/main.py:7071-7090` & `7127-7146`):**
    ```python
    # numista_backend/main.py:7127-7146
                for matched_coin_id in matched_ids:
                    db.collection("users").document(user_email)\
                      .collection("review_queue").document(matched_coin_id)\
                      .set({
                          "matched_receipt_id": r_id,
                          "receipt_matched": True,
                          "receipt_items_matched": matched_item_descs,
                          "receipt_confidence": 0.95,
                          "receipt_date": purchase_date,
                          "receipt_total": r_data.get("total_amount"),
                          "receipt_retailer": r_data.get("retailer"),
                          "Purchase Date": purchase_date,
                          "purchase_date": purchase_date,
                          "Retailer/Website": item_retailer,
                          "retailer": item_retailer,
                          "Retailer Invoice #": item_inv_no,
                          "invoice_number": item_inv_no,
                      }, merge=True)
    ```
    **Must replace** `"Retailer/Website": item_retailer` and `"Retailer Invoice #": item_inv_no` in `_link_receipts_to_coins` (`lines 7071-7090` and `7127-7146`) with `"retailer_website": item_retailer` and `"retailer_invoice_num": item_inv_no`! Otherwise `_link_receipts_to_coins` (called at `main.py:8314`) overwrites the clean `review_queue` doc and re-injects the illegal keys `"Retailer/Website"` and `"Retailer Invoice #"`.
  - **Frontend Reader Compatibility (`numista_mobile/lib/screens/review_hub_screen.dart:724-730, 825-826`):**
    Ensure `_showCoinEditDialog` reads `data['retailer_website'] ?? data['Retailer/Website']`, `data['retailer_invoice_num'] ?? data['Retailer Invoice #']`, `data['retailer_item_num'] ?? data['Retailer Item No.']`, and `data['purchase_date'] ?? data['Purchase Date']`:
    ```dart
    // numista_mobile/lib/screens/review_hub_screen.dart:724-730 (currently only reads legacy keys!)
          'Purchase Date': TextEditingController(text: (data['Purchase Date'] ?? '').toString()),
          'Retailer/Website': TextEditingController(text: (data['Retailer/Website'] ?? '').toString()),
          'Retailer Invoice #': TextEditingController(text: (data['Retailer Invoice #'] ?? '').toString()),
          'Retailer Item No.': TextEditingController(text: (data['Retailer Item No.'] ?? '').toString()),
    ```
    **4.1.x Fix:** Update those 4 lines in `review_hub_screen.dart:724-730` (and `line 825-826`) to fall back from `snake_case` first (`data['purchase_date'] ?? data['Purchase Date']`, `data['retailer_website'] ?? data['Retailer/Website']`, `data['retailer_invoice_num'] ?? data['Retailer Invoice #']`, `data['retailer_item_num'] ?? data['Retailer Item No.']`) so removing the illegal keys in Firestore does not blank out the Edit Coin dialog text controllers!

---

### 3. Duplicate Sweep & Hub Pending Filter Invariant (`status == "pending"`)

- **`_run_duplicate_sweep` (`numista_backend/main.py:6958-6963`):**
  ```python
  # numista_backend/main.py:6958-6963
      for coll_name in ("coins", "collection", "review_queue"):
          docs = db.collection("users").document(user_email).collection(coll_name)\
                   .where("import_session_id", "!=", session_id)\
                   .limit(2000).stream()
          for d in docs:
              existing.append((d.id, coll_name, d.to_dict()))
  ```
  - Plan 4.1 §3.1 item 3 (`if coll_name == "review_queue" and d_dict.get("status") != "pending": continue` + `if d.id in new_coin_ids: continue`) completely fixes `1 Duplicates Flagged`.
- **Idempotent Supersede & Initial Status (`numista_backend/main.py:7612` & `8054-8065`):**
  ```python
  # numista_backend/main.py:7612
      doc["status"] = "pending_review"
  ```
  ```python
  # numista_backend/main.py:8054-8060
                      stale_q = db.collection("users").document(user_email).collection("review_queue")\
                                  .where("retailer_item_num", "==", m_id)\
                                  .where("status", "==", "pending").stream()
  ```
  - **4.1.x Fix:** Set `doc["status"] = "pending"` in `main.py:7612`, and in `main.py:8054-8065` supersede any existing `review_queue` doc for `retailer_item_num == m_id` (or legacy `"Retailer Item No." == m_id`) whose `status` is in `("pending", "pending_review", "staged")`.
- **Hub Actionable Read Filter (`numista_mobile/lib/screens/review_hub_screen.dart:1271-1272, 1320-1321, 1396-1397`):**
  ```dart
  // numista_mobile/lib/screens/review_hub_screen.dart:1271-1272
                final status = (d.data()['status'] ?? 'pending').toString().toLowerCase();
                return (status == 'pending' || status == 'pending_review' || status == 'staged') && status != 'superseded' && status != 'committed';
  ```
  - **4.1.x Fix:** Per Plan 4.1 §2.4 & §3.1 item 5 (`status == "pending"` quoted invariant), tighten `lines 1271-1272, 1320-1321, 1396-1397` to `return status == 'pending';`.

---

### 4. Hub Dismiss / Commit `.delete()` Audit vs. v3.1 No-Delete / Supersede

- **`/api/review/delete_items` (`numista_backend/main.py:3844-3852`):**
  ```python
  # numista_backend/main.py:3844-3852
          for item_id in req.item_ids:
              doc_ref = queue_ref.document(item_id)
              batch.update(doc_ref, {
                  "status": "aborted",
                  "abort_reason": "user_dismissed_in_hub",
                  "aborted_at": firestore.SERVER_TIMESTAMP,
              })
  ```
  Already compliant (soft-update to `"status": "aborted"`).
- **`/api/review/commit_items` (`numista_backend/main.py:3616-3620`):**
  ```python
  # numista_backend/main.py:3616-3620
              vault_ref = user_ref.collection("coins").document(doc_id)
              batch.set(vault_ref, data)
              batch.delete(queue_ref.document(doc_id))
  ```
  Plan 4.1 §3.1 item 4 replaces `batch.delete(queue_ref.document(doc_id))` with `batch.set(queue_ref.document(doc_id), {"status": "committed", "committed_at": firestore.SERVER_TIMESTAMP}, merge=True)`. That removes the last `.delete()` on `review_queue` in the entire codebase.

---

### 5. Acceptance Gates & Non-Author `PREVIEW_READY` Verification (Plan 4.1 §4 & §6)

- The 6 binary acceptance criteria in Plan 4.1 §4 are directly executable by Field Tester (`26SQRP_MintPack.pdf` upload -> `1 Items Imported`, `0 Duplicates Flagged` -> Hub Card shows `Cost: $61.00 (25 @ $2.44)` & `Fee: $0.00` -> Edit Coin dialog shows `$61.00 (25 @ $2.44)` & `Fee: $0.00` -> Firestore child/parent doc verification -> 5 invoice runs).
- Per Plan 4.1 §6 (`PREVIEW_READY` Hard Gate — **Non-Author Verification**), Argon stands ready to execute the independent verification of all 4 artifacts (Hosting release hash, live `main.dart.js` bundle grep on `https://numista-vault--p7-gate-8avtpz22.web.app`, Firestore `26SQRP` child + parent doc dump, and Cloud Run `p7gate` revision check) the moment AG CoS completes the 4.1 / 4.1.x build and deploy.

