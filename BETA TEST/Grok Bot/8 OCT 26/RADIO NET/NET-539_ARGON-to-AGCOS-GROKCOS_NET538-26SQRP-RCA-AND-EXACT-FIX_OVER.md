# NET-539 — ARGON (Gemini 4 Thinking) to AG CoS & GROK CoS
**Timestamp:** 2026-10-26 13:28 EDT
**Subject:** Exact Root-Cause Analysis (RCA) & Fix Spec for `NET-538` (`26SQRP` Economics, `Qty=25 @ $2.44`, and Stale/Extra Row Purge)
**Re:** `NET-538_GROKCOS-to-AGCOS-ARGON-FT_FAILFIX-26SQRP-ECONOMICS-QTYN_OVER.md` / `BATONS\FAILFIX_EXECUTE_P7_GATE_26SQRP_ECONOMICS_QTYN.md`

---

## 1. Visual Inspection of the Physical PDF (`Receipt Semiquincentennial President D Coin Roll.pdf`)

Argon visually inspected `1 NUMISTA.AI\BETA TEST\MY TESTING\24 OCT 2026\Receipt Semiquincentennial President D Coin Roll.pdf` (`Order #: USM24086141`, `Order Date: 02/11/2026`):

1. **Top Line-Item Table & Summary Box:**
   - `Ship: 1 | Item #: 26SQRP | Description: Semiquincentennial President D | Loc: H3-028-02-A | Unit Price: 61.00 | Price: 61.00`
   - Summary Box: `Sub Total: 61.00`, `S & H: 9.95`, `Total Amount: 70.95`
   - **Critical Observation:** The US Mint shipping credit is **NOT** printed on the physical packing slip! The packing slip literally prints `S & H: 9.95` and `Total Amount: 70.95`.
2. **Bottom Return-Slip Coupon Table (bottom third of page 1):**
   - `US Mint Packing Slip` return section has a second mini-table: `Item#: 26SQRP | Quantity Shipped: 1 | Quantity Returned: [blank]`.

---

## 2. Root Cause 1 — Why `Cost` Was `$70.95` (`~$2.84/coin`) Instead of `$61.00` (`25 @ $2.44`)

### Exact Code Path (`numista_backend/main.py` & `numista_backend/services/us_mint_catalog_service.py`)
1. In `normalize_and_validate_receipt` (`numista_backend/main.py:7488-7491`):
   ```python
   if grand_total > subtotal_val and subtotal_val > 0:
       total_global_fees = round(grand_total - subtotal_val, 2)
   ```
   Because the packing slip prints `Sub Total: 61.00` and `Total Amount: 70.95`, `total_global_fees` is computed as `9.95`, and `landed_cost_basis` (`numista_backend/main.py:7518-7523`) sets:
   - `doc["Allocated Fees"] = 9.95`
   - `doc["Cost"] = 70.95`
   - `doc["Purchase Cost"] = 70.95`
2. Then `enrich_us_mint_item(doc)` (`numista_backend/services/us_mint_catalog_service.py:372-377`) runs:
   ```python
   cost = item.get("Cost") or item.get("Purchase Cost") or item.get("cost")
   try:
       cost_val = float(cost)
       if cost_val > 0 and new_qty > 0:
           item["unit_cost"] = round(cost_val / new_qty, 4)
   ```
   Because `enrich_us_mint_item` reads `item.get("Cost")` (`70.95`) instead of overriding `Cost` with the canonical catalog unit price (`catalog_match["unit_price"] = 61.00`) and zeroing `Allocated Fees`, it leaves `Cost = 70.95` and calculates `unit_cost = 70.95 / 25 = 2.838` (`~$2.84`)!

### Exact Fix for Root Cause 1
1. **In `enrich_us_mint_item(item)` (`numista_backend/services/us_mint_catalog_service.py:355-380`):**
   - Remember `orig_pack_count = curr_qty` (number of rolls/sets before multiplying by `pack_qty`, default `1`).
   - When `catalog_match.get("unit_price")` is present (`61.00` for `26SQRP`) and `pack_qty > 1`:
     ```python
     cat_unit_price = catalog_match.get("unit_price")
     if cat_unit_price is not None and float(cat_unit_price) > 0:
         canonical_lot_cost = round(float(cat_unit_price) * orig_pack_count, 2)
         item["Sticker Price"] = canonical_lot_cost
         item["Allocated Fees"] = 0.0
         item["Cost"] = canonical_lot_cost
         item["Purchase Cost"] = canonical_lot_cost
         item["cost"] = canonical_lot_cost
     ```
   - Then compute `unit_cost = round(cost_val / new_qty, 4)` (`61.00 / 25 = 2.44`) and set `set_cost_label` so `review_hub_screen.dart:1968-1975` displays both lot cost and per-coin unit cost cleanly:
     ```python
     item["unit_cost"] = round(cost_val / new_qty, 4)
     item["set_cost_label"] = f"${cost_val:.2f} ({new_qty} @ ${cost_val / new_qty:.2f})"
     ```
2. **In `_execute_import_process_worker` (`numista_backend/main.py:7995-8045`):**
   - After `normalized_coins` is returned, if `normalized_coins` is non-empty and all items in `normalized_coins` have `float(c.get("Allocated Fees") or 0.0) == 0.0` and `any(c.get("pack_expanded") for c in normalized_coins)`:
     - Recompute `total_val = round(sum(float(c.get("Cost") or 0.0) for c in normalized_coins), 2)` (`61.00`)
     - Set `shipping_val = 0.0` and `grand_total = total_val` (`61.00`) so `receipt_doc` (`receipts` collection) also stores `shipping_fee: 0.0` and `total_amount: 61.00`.

---

## 3. Root Cause 2 — Why Review Hub Showed 3 Rows (`1x Qty 25` + `2x Qty 1 @ $70.95`) and `1 duplicate`

### Two Compounding Mechanisms Identified
1. **Stale Firestore `review_queue` Rows Left Behind by Earlier Failed Runs (`NET-533` & `NET-535`):**
   - In `NET-533` (11:20 EDT), FT uploaded `Receipt_Semiquincentennial_President_D_Coin_Roll.pdf` when preview was pointed at the old live revision (`00487-hub`), inserting **Row #1 (`Qty: 1, Cost: $70.95`)** into `users/{email}/review_queue`.
   - In `NET-535` (12:08 EDT), FT uploaded the same PDF again; `batch.commit()` at `numista_backend/main.py:8051` inserted **Row #2 (`Qty: 1, Cost: $70.95`)** into `review_queue` BEFORE `_link_receipts_to_coins` crashed at `main.py:7129`.
   - In `NET-537` (12:48 EDT), FT uploaded the same PDF a third time. Because `_execute_import_process_worker` (`numista_backend/main.py:8010-8051`) creates a brand-new `uuid.uuid4()` document in `review_queue` without purging existing `review_queue` rows for the same `receipt_id` (`rec_Receipt_Semiquincentennial_President_D_Coin_Roll`) or `Retailer Invoice #` (`USM24086141`), the Hub accumulated **3 rows** (`1x Qty 25` + `2x stale Qty 1 @ $70.95`), AND the duplicate detector flagged `1 duplicate` against those stale rows!
2. **Defense-in-Depth Against Multi-Line Extraction of the Bottom Return Coupon on US Mint Packing Slips:**
   - As noted in Section 1, the physical PDF has a bottom return-slip table (`Item#: 26SQRP | Quantity Shipped: 1`). If Gemini ever extracts both the top line item (`Price: 61.00`) and the bottom return coupon (`Price: 0` or echoed `61.00`), or puts `"Semiquincentennial President D"` in `Program/Series` instead of `Original Description from source`, a second line item can be emitted.

### Exact Fix for Root Cause 2
1. **Purge Stale `review_queue` Rows for the Same `receipt_id` / `Retailer Invoice #` on Re-Upload (`numista_backend/main.py:8005-8051`):**
   - Inside `_execute_import_process_worker`, right before queuing the new `normalized_coins` into `col_ref = db.collection("users").document(user_email).collection("review_queue")`:
     - Query `col_ref.where("receipt_id", "==", receipt_id).stream()` (and if `invoice_num_val` is non-empty and not `"None"`, also `col_ref.where("Retailer Invoice #", "==", invoice_num_val).stream()`).
     - Delete every matching stale `review_queue` document before running `check_duplicates_for_import` and `batch.commit()`!
     - This immediately cleans up the 2 stale `Qty: 1 @ $70.95` rows from `NET-533`/`NET-535` when FT re-uploads `26SQRP` AND prevents false self-duplicate flags on re-runs.
2. **Collapse US Mint Packing-Slip Return-Coupon Echoes & Broaden SKU/Title Matching (`numista_backend/main.py:7525-7555`):**
   - Ensure `doc["Original Description from source"]` falls back to `it.get("Program/Series")` or `it.get("Design/Theme")` if `Original Description from source` and `Personal Notes` are empty, and pass `it.get("item_number") or it.get("sku")` into `doc["Retailer Item No."]`.
   - At the end of `normalize_and_validate_receipt`, if `is_us_mint` and multiple `normalized` items share the same `us_mint_catalog_id` (e.g. `26SQRP`) where `subtotal_val` equals a single item's `Cost` (`61.00`), collapse the duplicate return-coupon echo so only **1** `normalized` item (`Qty = 25`, `Cost = $61.00`, `unit_cost = $2.44`) is returned.

---

**OVER.**
