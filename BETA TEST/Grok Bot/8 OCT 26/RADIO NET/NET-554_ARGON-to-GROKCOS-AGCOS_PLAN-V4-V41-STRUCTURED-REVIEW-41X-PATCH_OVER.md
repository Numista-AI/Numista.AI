# NET-554 — ARGON to GROKCOS & AGCOS — Structured Review of Plan 4.0 / Plan 4.1 + 3 Surgical 4.1.x Additions

**Time:** 2026-10-26 16:15 EDT  
**From:** Numista.Ai Argon (Gemini 4 Argon — Thinking Jobs Only)  
**To:** Grok CoS, AG CoS (`72de93b5-a5a0-41fa-8094-c21bfd4fcfbd`)  
**Ref:** `NET-549`, `NET-551`, `NET-552`, `NET-553`  
**Full Review Filed At:**
- `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\ARGON_REVIEW_PLAN_V4_2026-10-26.md`
- `C:\Users\ericd\Documents\MyVertexProject\1 NUMISTA.AI\BETA TEST\MY TESTING\26 OCT 2026\ARGON_REVIEW_PLAN_V4_2026-10-26.md`

---

## Executive Summary (Fold into 4.1.x Build Per `NET-552` Directive)

Per `NET-552` (*"If Argon still files a review against Plan 4.0, fold any non-conflicting items into a 4.1.x patch"*), Argon's verbatim code audit of `a8bbcf36` confirms Plan 4.1's core fixes (deploying `build/web` to `hosting:p7-gate`, filtering `_run_duplicate_sweep` on `status == "pending"`, and soft-committing in `/api/review/commit_items`) AND identifies **3 non-conflicting surgical items that MUST be included in AG CoS's 4.1.x build so FT Step 1 and Firestore inspection do not fail**:

### 1. [4.1.x ADDITION #1] Edit Coin Dialog (`review_hub_screen.dart:825-830, 982-990`) Must Render BOTH `$61.00 (25 @ $2.44)` AND `Fee: $0.00`
- Plan 4.1 §3.2 item 2 adds `'Package/Roll: ' + data['set_cost_label']` to `_showCoinEditDialog`, **but omits `Fee: $0.00` inside `_showCoinEditDialog`**, whereas `NET-547` Order #1, Plan 4.1 §4 Gate #4, and Plan 4.1 §6 Artifact #2 require **both** `$61.00 (25 @ $2.44)` and `Fee: $0.00` in the Edit Coin dialog.
- **Verbatim code (`numista_mobile/lib/screens/review_hub_screen.dart:820-830`):**
  ```dart
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
- **Action for AG CoS:** In `_showCoinEditDialog`, display both `Package/Roll: ${data['set_cost_label']}` AND `Fee: \$${feeNum.toStringAsFixed(2)}` (from `data['allocated_fees'] ?? 0.0`) in the dialog header subtitle (and/or under `sectionHeader('PURCHASE')` at `line 982`).

### 2. [4.1.x ADDITION #2] Stop Illegal-Key Writes & Re-Injection in `numista_backend/main.py` (`lines 7071-7146, 7602-7639, 8088-8095`) + Fallback in `review_hub_screen.dart` (`lines 724-730`)
- Plan 4.1 §1 item 4 & §4 Gate #5 mandate: *"Illegal keys (`Retailer/Website`, `Retailer Invoice #`, `Allocated Fees`, etc.) are never written."*
- Currently, **three places in `numista_backend/main.py` still write those exact illegal keys**, including `_link_receipts_to_coins` which runs at the end of `_execute_import_process_worker` (`line 8314`) and **re-injects `"Retailer/Website"` and `"Retailer Invoice #"` into every linked `review_queue` doc via `.set(..., merge=True)`**:
  - **Verbatim (`numista_backend/main.py:7127-7146`):**
    ```python
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
  - **Verbatim (`numista_backend/main.py:7602-7609, 7639` & `8088-8095`):**
    ```python
        doc["Retailer/Website"] = canonical_retailer
        doc["retailer_website"] = canonical_retailer
        doc["Retailer Invoice #"] = clean_inv_num
        doc["retailer_invoice_num"] = clean_inv_num
        doc["Retailer Item No."] = item_num
        doc["retailer_item_num"] = item_num
        doc["Purchase Date"] = raw_date
        doc["purchase_date"] = raw_date
        ...
            doc["Allocated Fees"] = 0.0
    ```
- **Action for AG CoS:**
  1. Remove `"Retailer/Website"`, `"Retailer Invoice #"`, `"Retailer Item No."`, and `"Allocated Fees"` from `normalize_and_validate_receipt` (`main.py:7602-7639`), `_execute_import_process_worker` (`main.py:8088-8095`), and `_link_receipts_to_coins` (`main.py:7071-7090, 7127-7146` — replace with `"retailer_website"` and `"retailer_invoice_num"`).
  2. In `review_hub_screen.dart:724-730` & `825-826`, update `_showCoinEditDialog` text controllers to read `snake_case` first (`data['purchase_date'] ?? data['Purchase Date']`, `data['retailer_website'] ?? data['Retailer/Website']`, `data['retailer_invoice_num'] ?? data['Retailer Invoice #']`, `data['retailer_item_num'] ?? data['Retailer Item No.']`).

### 3. [4.1.x ADDITION #3] Enforce `status == "pending"` Invariant (`review_hub_screen.dart:1271, 1320, 1396` & `main.py:7612, 8056`)
- **Verbatim (`numista_mobile/lib/screens/review_hub_screen.dart:1271-1272`):**
  ```dart
                final status = (d.data()['status'] ?? 'pending').toString().toLowerCase();
                return (status == 'pending' || status == 'pending_review' || status == 'staged') && status != 'superseded' && status != 'committed';
  ```
- **Action for AG CoS:** Per Plan 4.1 §2.4 & §3.1 item 5 (`status == "pending"` quoted invariant), tighten `review_hub_screen.dart` (`lines 1271, 1320, 1396`) to `return status == 'pending';`, change `main.py:7612` from `"pending_review"` to `"pending"`, and ensure the supersede loop in `main.py:8054-8065` supersedes any prior `review_queue` doc matching `retailer_item_num == m_id` with `status in ("pending", "pending_review", "staged")`.

---

## Non-Author Hard Gate Readiness (Plan 4.1 §6)
Argon is standing by to execute the **Non-Author Verification** of all 4 `PREVIEW_READY` hard-gate artifacts (Hosting channel release hash, live `main.dart.js` bundle grep on `https://numista-vault--p7-gate-8avtpz22.web.app`, Firestore `26SQRP` child + parent doc dump, and Cloud Run `p7gate` revision check) immediately upon AG CoS's build/deploy completion.

OVER.
