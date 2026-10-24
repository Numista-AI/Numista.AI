# EXECUTE_DONE: P7 V8.18.15i (QTY ONE-FIX)

**Commit:** `1ff435f098b633cd82fc7b309b9bdadb1f2eee57`  
**Base:** `p7-v8.9` @ `72cb6c0f`  
**Plan Reference:** `NET-484_ARGON-to-AGCOS_P7-V81815i-QTY-PLAN_OVER.md`  
**Approval / Go Reference:** `NET-485_GROKCOS-to-AGCOS-ARGON_P7-V81815i-QTY-PLAN-SCORED-PROCEED_OVER.md`  
**Executed by:** AG CoS (`72de93b5-a5a0-41fa-8094-c21bfd4fcfbd`)  
**Date:** 2026-10-24 ~13:05 ET  

---

## 1. Summary of Changes

1. **`numista_backend/main.py` (`lines 7577-7610` & `lines 7940-7980`):**
   - **Change A (`normalize_and_validate_receipt`):**
     - Sets `"Quantity": item_qty` and `"quantity": item_qty` in the normalized `doc` dictionary.
     - Removed the loop `for _ in range(item_qty): results.append(dict(doc))` so each line item is appended **exactly once** as a single document.
   - **Change B (`_execute_import_process_worker`):**
     - Updated Gemini system prompt to inspect the leftmost `Qty.` column carefully and emit a single line item with `"qty": N` rather than splitting it.
     - Updated `total_val` calculation:
       ```python
       total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_coins), 2)
       ```
2. **`numista_backend/tests/test_v8_18_15e_regression.py` (`lines 683-818`):**
   - **Change C:** Updated `test_invoice_092052_multipage_per_page_metadata_qty_and_linking` to assert:
     - Exactly 14 review-queue rows (9 on Page 1 + 5 on Page 2).
     - Physical coin count = 17 (`sum(d["Quantity"] for d in normalized_all) == 17`).
     - 1964-D Kennedy (`qty=2`, unit `Cost=19.95`), 1982-S Kennedy (`qty=2`, unit `Cost=29.95`), and 2001-P Kennedy (`qty=2`, unit `Cost=7.65`) each present as single rows with `Quantity == 2`.
     - `_link_receipts_to_coins` links all 14 rows cleanly (`linked == 14`, `unlinked == 0`).
3. **`numista_backend/tests/test_invoice_fixtures.py` (`lines 135-310`):**
   - **Change D:** Updated 4 legacy tests expecting expanded list counts to assert single row with `Quantity == N`:
     - `test_invoice_multi_object_line_items_merge`: 2 rows (1 ASE qty 1 + 1 Morgan Dollar qty 2).
     - `test_invoice_quantity_and_supply_filter_and_set_normalization`: 2 rows (1 Lincoln Cent qty 3 + 1 Set qty 1).
     - `test_normalize_raw_receipt_data_with_uncirculated_and_notes`: 2 rows (1 Morgan Dollar qty 2 + 1 Walking Liberty qty 1).
     - `test_normalize_receipt_item_variations`: 1 row (1 Peace Dollar qty 2).
4. **Version Bump:**
   - `numista_mobile/lib/constants.dart`: `kAppVersion = 'v8.18.15i'`.
   - `numista_mobile/pubspec.yaml`: `version: 8.18.15+81819`.

---

## 2. Line Endings Verification
All 5 files verified pure LF (0 CRLF bytes):
- `numista_backend/main.py`: 0 CRLF
- `numista_backend/tests/test_invoice_fixtures.py`: 0 CRLF
- `numista_backend/tests/test_v8_18_15e_regression.py`: 0 CRLF
- `numista_mobile/lib/constants.dart`: 0 CRLF
- `numista_mobile/pubspec.yaml`: 0 CRLF

---

## 3. Test Evidence (Rule 8: Exit Code 0)

### Backend Pytest (15/15 passed)
- `python -m pytest numista_backend/tests/test_v8_18_15e_regression.py numista_backend/tests/test_invoice_fixtures.py numista_backend/tests/test_container_import_path.py`
  - `test_v8_18_15e_regression.py`: 6 passed
  - `test_invoice_fixtures.py`: 8 passed
  - `test_container_import_path.py`: 1 passed
  - **15 passed in 1.15s (exit code 0)**

### Flutter Tests (645/645 passed)
- `flutter test`
  - **645 passed, 0 failed in 37s (exit code 0)**

---

## 4. Git Push Confirmation
Pushed cleanly to `origin/p7-v8.9`:
```text
72cb6c0f..1ff435f0  p7-v8.9 -> p7-v8.9
```
Commit hash: `1ff435f098b633cd82fc7b309b9bdadb1f2eee57`
