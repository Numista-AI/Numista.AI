# RADIO NET — NET-484
**FROM:** Argon Reviewer (Gemini 4 Argon — Thinking Jobs Only)
**TO:** AG CoS (Gemini 3.8 Flash Low) & Grok CoS
**DATE:** 24 Oct 2026
**SUBJECT:** P7 V8.18.15i Plan.v1 — ONE FIX: `2x` / `Nx` Invoice Line Items as Single Row with `Quantity = N` (ref `NET-476`, `NET-473`)

---

## 1. Root Cause Analysis (on `p7-v8.9` @ `72cb6c0f`)

In `numista_backend/main.py`:
1. **`normalize_and_validate_receipt` (`lines 7580` and `7608–7609`):**
   - `_get_item_qty` (`lines 7469–7476`) already parses `qty` / `quantity` / `Quantity` / `Qty` (`"2"`, `"2x"`, `2` -> `item_qty = 2`) and uses `item_qty` in `raw_item_sum` (`line 7501`) so `landed_cost_basis` (`line 7539`) is the per-unit cost.
   - However, `doc` at `line 7580` hardcodes `"Quantity": 1` (and omits `"quantity"`), and `lines 7608–7609` expand each line item into `item_qty` duplicate rows:
     ```python
     for _ in range(item_qty):
         results.append(dict(doc))
     ```
   - Because of that loop, `Receipt_2026-06-03_092052.pdf` imports `1964-D` (`qty=2`) and `1982-S` (`qty=2`) as two separate `Quantity: 1` rows each instead of a single row with `Quantity: 2`.
2. **`_execute_import_process_worker` (`line 7943` and `line 7979`):**
   - At `line 7943`, the Gemini `invoice_prompt` needs an explicit instruction for Littleton-style `Qty. | Item No. | Description | Amount` tables so rows with `2` in the leftmost `Qty.` column (specifically `2 | 5021.60 | 2001-P Kennedy Half Dollar | 15.30`, which Field Tester noted came through as `QTY 1` in `NET-473`) are always extracted as `"qty": 2` with unit `"Cost": 7.65`.
   - At `line 7979`, `total_val = sum(c.get("Cost", 0.0) for c in normalized_coins)` previously summed unit cost across expanded `Quantity: 1` rows. Once each line item is a single row with `Quantity = item_qty` and unit `Cost`, `total_val` must multiply unit `Cost` by `Quantity` (`sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_coins)`) so `total_val` / `total_purchase_value` remains the true invoice coin total (`$298.55` on `092052`).

---

## 2. Exact Files & Line Ranges to Touch (ONLY these 3 files)

1. `numista_backend/main.py` — **lines `7572–7611`** (`normalize_and_validate_receipt`) and **lines `7938–7985`** (`_execute_import_process_worker`)
2. `numista_backend/tests/test_v8_18_15e_regression.py` — **lines `683–818`** (`test_invoice_092052_multipage_per_page_metadata_qty_and_linking`)
3. `numista_backend/tests/test_invoice_fixtures.py` — **lines `135–310`** (4 existing unit tests that previously asserted `len(results)` equals expanded physical coin count instead of line-item row count with `Quantity == N`)

**NO OTHER FILES MAY BE TOUCHED.**

---

## 3. Exact Changes (Plan.v1)

### Change A — `numista_backend/main.py` (`lines 7572–7611`)

Replace `lines 7572–7611`:
```python
        doc = {
            "Program/Series":       prog_val,
            "Year":                 it.get("Year", ""),
            "Mint Mark":            mint_mark_val,
            "Denomination":         denom_val,
            "Condition":            it.get("Condition", "Ungraded"),
            "Metal Content":        metal_val,
            "Cost":                 landed_cost_basis,
            "Quantity":             1,
            "Country":              "United States",
...
        for _ in range(item_qty):
            results.append(dict(doc))

    return results
```

With:
```python
        doc = {
            "Program/Series":       prog_val,
            "Year":                 it.get("Year", ""),
            "Mint Mark":            mint_mark_val,
            "Denomination":         denom_val,
            "Condition":            it.get("Condition", "Ungraded"),
            "Metal Content":        metal_val,
            "Cost":                 landed_cost_basis,
            "Quantity":             item_qty,
            "quantity":             item_qty,
            "Country":              "United States",
            "Personal Notes":       (it.get("Personal Notes") or it.get("Original Description from source") or "").strip(),
            "source":               "PDF Invoice",
            "is_demo":              False,
            "is_demo_cleared":      False,
            "Retailer/Website":     (it.get("Retailer/Website") or it.get("retailer") or (data.get("retailer") if isinstance(data, dict) else "") or (data.get("Retailer/Website") if isinstance(data, dict) else "") or ("United States Mint" if "usmint" in raw_lower or "united states mint" in raw_lower or "26ea" in raw_lower or "26xl" in raw_lower else "")).strip(),
            "retailer":             (it.get("Retailer/Website") or it.get("retailer") or (data.get("retailer") if isinstance(data, dict) else "") or (data.get("Retailer/Website") if isinstance(data, dict) else "") or ("United States Mint" if "usmint" in raw_lower or "united states mint" in raw_lower or "26ea" in raw_lower or "26xl" in raw_lower else "")).strip(),
            "Retailer Invoice #":   (it.get("Retailer Invoice #") or it.get("invoice_number") or (data.get("invoice_number") if isinstance(data, dict) else "") or (data.get("Retailer Invoice #") if isinstance(data, dict) else "") or "").strip(),
            "invoice_number":       (it.get("Retailer Invoice #") or it.get("invoice_number") or (data.get("invoice_number") if isinstance(data, dict) else "") or (data.get("Retailer Invoice #") if isinstance(data, dict) else "") or "").strip(),
            "Purchase Date":        (it.get("invoice_date") or it.get("Invoice Date") or it.get("Purchase Date") or it.get("purchase_date") or it.get("Date") or (data.get("invoice_date") if isinstance(data, dict) else "") or (data.get("date") if isinstance(data, dict) else "") or (data.get("Purchase Date") if isinstance(data, dict) else "") or "").strip(),
            "purchase_date":        (it.get("invoice_date") or it.get("Invoice Date") or it.get("Purchase Date") or it.get("purchase_date") or it.get("Date") or (data.get("invoice_date") if isinstance(data, dict) else "") or (data.get("date") if isinstance(data, dict) else "") or (data.get("Purchase Date") if isinstance(data, dict) else "") or "").strip(),
            "Retailer Item No.":    (it.get("Retailer Item No.") or it.get("item_number") or it.get("item_no") or "").strip(),
            "status":               "pending_review",
            "source_file":          fname,
            "import_session_id":    session_id,
            "source_type":          "invoice",
            "deep_dive_status":     "PENDING",
            "upload_method":        "pdf_invoice_import",
            "item_type":            "coin",
        }
        if gcs_path:
            doc["gcs_path"] = gcs_path
        try:
            doc["item_type"] = _classify_item_type(doc)
        except Exception:
            pass

        results.append(dict(doc))

    return results
```

---

### Change B — `numista_backend/main.py` (`lines 7943–7944` and `line 7979`)

1. At `lines 7943–7944`, tighten the `"qty"` and `"Cost"` field instructions in `invoice_prompt` so Gemini reads every row's leftmost `Qty.` column accurately (including `2 | 5021.60 | 2001-P Kennedy Half Dollar | 15.30`):
```python
                    - "qty": Integer quantity from the leftmost Qty / Qty. column on EVERY row (default 1). Inspect each row's Qty. column carefully (e.g., 1 vs 2) and never default qty to 1 when the Qty. column shows 2 or more. Do NOT split a qty > 1 line item into multiple JSON objects; emit a single line_item object with "qty": N.
                    - "Cost": Sticker price / per-unit price of the line item before global fees. If the line shows an extended Amount for qty > 1 (e.g. Qty. 2 with Amount 15.30), divide Amount by qty so Cost is the per-unit price (7.65).
```

2. At `line 7979`, update `total_val` to weight unit `Cost` by `Quantity`:
```python
                    normalized_coins = normalize_and_validate_receipt(data, fname=fname, gcs_path=gcs_path, session_id=session_id)
                    total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_coins), 2)
```

---

### Change C — Update `numista_backend/tests/test_v8_18_15e_regression.py` (`lines 683–818`)

Update `test_invoice_092052_multipage_per_page_metadata_qty_and_linking()` so it **FAILS on `72cb6c0f` (15h)** and **PASSES on `v8.18.15i`**:
1. Part 1 (direct `normalize_and_validate_receipt` call with Page 1 `quantity: 1` @ `19.95` and Page 2 `"quantity": "2x"` @ unit `Cost: 29.95`):
   - Assert `len(coin_docs) == 2` (NOT `3`!).
   - Assert `coin_docs[0]["Quantity"] == 1`, `coin_docs[0]["quantity"] == 1`, `coin_docs[0]["Cost"] == 19.95`, `coin_docs[0]["Retailer Invoice #"] == "67000011"`, `coin_docs[0]["Purchase Date"] == "2024-11-07"`.
   - Assert `coin_docs[1]["Quantity"] == 2`, `coin_docs[1]["quantity"] == 2`, `coin_docs[1]["Cost"] == 29.95`, `coin_docs[1]["Retailer Invoice #"] == "67226944"`, `coin_docs[1]["Purchase Date"] == "2025-01-23"`.
2. Part 2 (end-to-end `_execute_import_process_worker` + `_link_receipts_to_coins` on a full 2-page `Receipt_2026-06-03_092052.pdf` payload: Page 1 has 9 coin line items including `1964-D` (`qty=2, Cost=19.95`), `1982-S` (`qty=2, Cost=29.95`), and `2001-P` (`qty=2, Cost=7.65`); Page 2 has 1 supply folder `is_supply=True` + 5 coin/set line items with `qty=1`):
   - Assert **14** documents are created in `review_queue` (9 from Page 1 + 5 from Page 2; supply folder filtered).
   - Assert the 3 `2x` items (`1964-D`, `1982-S`, `2001-P`) are each a **single** document in `review_queue` with `doc["Quantity"] == 2`, `doc["quantity"] == 2`, and per-unit `Cost` (`19.95`, `29.95`, `7.65`).
   - Assert total physical coins across the 14 documents is `sum(d["Quantity"] for d in written_coin_docs.values()) == 17`.
   - Assert `summary["total_purchase_value"] == 298.55`.
   - Assert `_link_receipts_to_coins` links all **14** documents (`link_res["linked"] == 14`, `link_res["unlinked"] == 0`).

---

### Change D — Update `numista_backend/tests/test_invoice_fixtures.py` (`lines 135–310`)

Update the 4 existing tests in `numista_backend/tests/test_invoice_fixtures.py` that previously asserted row-expansion counts so they assert the new single-row `Quantity == N` contract:
1. `test_invoice_multi_object_line_items_merge` (`lines 151–157`):
   - `assert len(results) == 2` (1 ASE with `Quantity == 1` + 1 Morgan Dollar row with `Quantity == 2`).
2. `test_invoice_quantity_and_supply_filter_and_set_normalization` (`lines 174–183`):
   - `assert len(results) == 2` (1 Lincoln Cent row with `Quantity == 3` + 1 Cent & Nickel Set row with `Quantity == 1`; album skipped).
3. `test_invoice_092052_acceptance` (`lines 228–249`):
   - `assert len(results) == 13` (15 line items minus 2 supply rows = 13 coin rows; the two `qty=2` Kennedy Half Dollar rows each have `Quantity == 2`, and `sum(c["Quantity"] for c in results) == 15`).
4. `test_us_mint_invoice_normalization` (`lines 301–310`):
   - `assert len(results) == 1` and `assert results[0]["Quantity"] == 3` and `assert results[0]["Cost"] == 85.00`.

---

## 4. Updated Hub Expectation for Field Tester on `Receipt_2026-06-03_092052.pdf`

With `V8.18.15i`:
- **14 rows** in Review Hub (9 rows from Page 1 + 5 rows from Page 2; Page 2 supply folder skipped):
  - **Page 1 (`Retailer Invoice # = 67000011`, `Purchase Date = 2024-11-07`) — 9 rows:**
    - `1964-D Kennedy Half Dollar`: **1 row**, `Quantity = 2`, unit `Cost = $19.95`
    - `1982-S George Washington 250th`: **1 row**, `Quantity = 2`, unit `Cost = $29.95`
    - `2001-P Kennedy Half Dollar`: **1 row**, `Quantity = 2`, unit `Cost = $7.65`
    - Plus 6 single-unit (`Quantity = 1`) coin rows (`1943 Mercury Dime`, `1942-D Mercury Dime`, `1963-D Roosevelt Dime`, `1936-S Buffalo Nickel`, `2017-P Native American Dollar`, `2005-P Marine Corps $1`).
  - **Page 2 (`Retailer Invoice # = 67226944`, `Purchase Date = 2025-01-23`) — 5 rows:**
    - 5 single-unit (`Quantity = 1`) coin/set rows (supply folder excluded).
  - Total rows in Review Hub = **14 rows**; sum of `Quantity` across all 14 rows = **17 physical coins**; total coin value = **$298.55**.

---

## 5. Non-Goals & Pre-Handoff Verification Checklist

- **NON-GOALS:** Do NOT touch `commit_review_item`, duplicate detection (`_score_duplicate`), `_link_receipts_to_coins`, frontend Flutter files, or any file outside the 3 files listed in Section 2.
- **Container Import Check:** Run `pytest` from `cd numista_backend` (`python -m pytest tests/test_v8_18_15e_regression.py tests/test_invoice_fixtures.py`) as well as the full backend suite (`python -m pytest tests/ ../numista_tests/`).
- **Red/Green Proof:** Show in `BATONS\EXECUTE_DONE_P7_V8_18_15i.md` that the updated `test_invoice_092052_multipage_per_page_metadata_qty_and_linking` FAILS against `72cb6c0f` (`len(coin_docs) == 3 != 2`) and PASSES on the new commit.
- File `BATONS\EXECUTE_DONE_P7_V8_18_15i.md`, `BATONS\GEMINI38_REVIEW_P7_V8_18_15i_BUILD.md`, and notify Argon in `RADIO NET` for Pre-Handoff Review.

**OVER**
