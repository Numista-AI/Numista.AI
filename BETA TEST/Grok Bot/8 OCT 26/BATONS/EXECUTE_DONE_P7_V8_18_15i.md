# EXECUTE DONE — P7 V8.18.15i (QTY One-Fix)

**Date:** 24 Oct 2026 ~3:20 PM ET  
**Author:** AG CoS (Gemini 3.8 Flash Low)  
**Ref Commit:** `6ee3de89` on `origin/p7-v8.9` (base: `72cb6c0f`)  
**Direct Handoff Context:** Responding to `NET-488` (FAIL-FIX), `NET-489` (CoS CONCURS), `NET-490` (FILE-WAKE / Rule 10 adoption)

---

## 1. Scope Check — 3 Files Only vs `72cb6c0f`

Strict compliance with `NET-484` §2 and `NET-488` Step 1:
```
$ git diff --name-only 72cb6c0f
numista_backend/main.py
numista_backend/tests/test_invoice_fixtures.py
numista_backend/tests/test_v8_18_15e_regression.py
```
Numstat:
```
6   6   numista_backend/main.py
24  17  numista_backend/tests/test_invoice_fixtures.py
99  58  numista_backend/tests/test_v8_18_15e_regression.py
```
Reverted the 2 Flutter version files (`constants.dart`, `pubspec.yaml`) and uncommitted modified files (`RELEASE_NOTES.md`, `home_dashboard.dart`) cleanly back to `72cb6c0f`. Zero Flutter or markdown files touched in code commit `6ee3de89`.

CRLF byte verification across all 3 files:
```
numista_backend/main.py CRLF: False (0 CRLF bytes)
numista_backend/tests/test_invoice_fixtures.py CRLF: False (0 CRLF bytes)
numista_backend/tests/test_v8_18_15e_regression.py CRLF: False (0 CRLF bytes)
```

---

## 2. Red / Green Proof on `test_invoice_092052_multipage_per_page_metadata_qty_and_linking`

### Red Run (main.py reverted to `72cb6c0f`):
```
pytest tests/test_v8_18_15e_regression.py -k test_invoice_092052_multipage_per_page_metadata_qty_and_linking
================================== FAILURES ===================================
_______ test_invoice_092052_multipage_per_page_metadata_qty_and_linking _______
    coin_docs = main.normalize_and_validate_receipt(raw_multipage_gemini)
    # Total returned should be 2 line item rows (1 from page 1, 1 from page 2 with Quantity: 2)
>   assert len(coin_docs) == 2
E   AssertionError: assert 3 == 2
E    +  where 3 = len([{'Program/Series': '', 'Year': '', 'Mint Mark': '', 'Denomination': 'Dollar', ...}, {'Program/Series': '', 'Year': ''...'', 'Denomination': 'Dollar', ...}, {'Program/Series': '', 'Year': '', 'Mint Mark': '', 'Denomination': 'Dollar', ...}])

tests\test_v8_18_15e_regression.py:736: AssertionError
=========================== short test summary info ===========================
FAILED tests/test_v8_18_15e_regression.py::test_invoice_092052_multipage_per_page_metadata_qty_and_linking
=============== 1 failed, 5 deselected, 250 warnings in 12.82s ================
```

### Green Run (with V8.18.15i fix in `main.py`):
```
pytest tests/test_v8_18_15e_regression.py -k test_invoice_092052_multipage_per_page_metadata_qty_and_linking
============================= test session starts =============================
collected 6 items / 5 deselected / 1 selected

tests\test_v8_18_15e_regression.py .                                     [100%]
=============== 1 passed, 5 deselected, 250 warnings in 14.66s ================
```

---

## 3. Test Suites & Target Function Proof

### Target Invoice Test Suite (from `numista_backend` container working directory):
`python -m pytest tests/test_v8_18_15e_regression.py tests/test_invoice_fixtures.py tests/test_container_import_path.py`
```
collected 16 items
tests\test_v8_18_15e_regression.py ......                                [ 37%]
tests\test_invoice_fixtures.py .........                                 [ 93%]
tests\test_container_import_path.py .                                    [100%]

====================== 16 passed, 250 warnings in 48.87s ======================
```

### Full Backend Pytest Suite:
`python -m pytest numista_backend/tests/`
```
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\ericd\AppData\Local\Temp\p7v89_build\numista_backend
configfile: pytest.ini
collected 614 items

===================== 614 passed, 258 warnings in 56.24s ======================
```
**Exit Code 0: 614 passed, 0 failed.**

### Exact Names of Updated Tests in `test_invoice_fixtures.py`:
1. `test_invoice_multi_object_line_items_merge` (asserts `len == 2`, `Quantity == 1` for ASE, `Quantity == 2` for Morgan Dollar)
2. `test_invoice_quantity_and_supply_filter_and_set_normalization` (asserts `len == 2`, `Quantity == 3` for Lincoln Cent, `Quantity == 1` for Set)
3. `test_invoice_092052_acceptance` (asserts `len == 13`, `sum(Quantity) == 15`, `halves len == 2`, each half `Quantity == 2`)
4. `test_us_mint_invoice_normalization` (asserts `len == 1`, `Quantity == 3`)

---

## 4. Exact Implementation Summary

- **`numista_backend/main.py:7577-7610` (Change A):**
  Stamps `"Quantity": item_qty` and `"quantity": item_qty` onto the normalized doc. Replaced `for _ in range(item_qty): results.append(dict(doc))` with a single `results.append(dict(doc))`.
- **`numista_backend/main.py:7940-7980` (Change B):**
  Updated Gemini prompt instruction for `qty` to inspect the leftmost column, never default to 1 when column shows >=2, and output a single JSON object. Updated `total_val` calculation to multiply unit `Cost` by `max(1, Quantity)`.
- **`numista_backend/tests/test_v8_18_15e_regression.py:732-848` (Change C):**
  Part 1 asserts `len == 2`, Page 1 `Quantity: 1`, Page 2 `Quantity: 2`.
  Part 2 simulates full 2-page `092052` payload (14 rows, 17 physical coins):
  - `assert len(normalized_all) == 14`
  - `assert sum(int(d.get("Quantity") or 1) for d in normalized_all) == 17`
  - 9 Page 1 rows (`67000011`, `2024-11-07`)
  - 5 Page 2 rows (`67226944`, `2025-01-23`)
  - `1964-D` (`len == 1`, `Quantity == 2`, `Cost == 19.95`)
  - `1982-S` (`len == 1`, `Quantity == 2`, `Cost == 29.95`)
  - `2001-P` (`len == 1`, `Quantity == 2`, `Cost == 7.65`)
  - `assert total_val == 298.55`
  - Linking simulation: `linked == 14`, `unlinked == 0`.
- **`numista_backend/tests/test_invoice_fixtures.py:149-317` (Change D):**
  4 fixtures updated to assert single rows with `Quantity == N`.
