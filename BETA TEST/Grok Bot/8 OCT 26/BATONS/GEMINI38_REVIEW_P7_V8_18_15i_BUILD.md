# GEMINI38 REVIEW — P7 V8.18.15i BUILD (Commit `6ee3de89`)

**Date:** 24 Oct 2026 ~3:20 PM ET  
**Reviewer:** AG CoS (Gemini 3.8 Flash Low)  
**Ref Commit:** `6ee3de89` on `origin/p7-v8.9` (base: `72cb6c0f`)  
**Scope:** 3 files modified, pure LF, 0 CRLF bytes.

---

## Verbatim Code Check (Rule 6a Compliance)

Every cite below quotes the exact verbatim code lines from the git diff of `6ee3de89` against base `72cb6c0f`:

### 1. `numista_backend/main.py:7577-7610` (Change A — Single Row Output with Quantity)
```python
            "Condition":            it.get("Condition", "Ungraded"),
            "Metal Content":        metal_val,
            "Cost":                 landed_cost_basis,
            "Quantity":             item_qty,
            "quantity":             item_qty,
            "Country":              "United States",
            "Personal Notes":       (it.get("Personal Notes") or it.get("Original Description from source") or "").strip(),
            "source":               "PDF Invoice",
```
and:
```python
        except Exception:
            pass

        results.append(dict(doc))

    return results
```
**Verification:** Verbatim code confirms `Quantity` and `quantity` stamped with `item_qty`, and the loop `for _ in range(item_qty)` removed so `results.append(dict(doc))` executes exactly once.

---

### 2. `numista_backend/main.py:7940-7980` (Change B — Prompt Qty & Valuation Calculation)
```python
                    - "retailer": If document header or body indicates "United States Mint" or "www.usmint.gov", set to "United States Mint".
                    - "invoice_number": Extract invoice number, order number, or packing slip number.
                    - "invoice_date": Output in ISO 8601 YYYY-MM-DD format.
                    - "qty": Integer quantity from the leftmost Qty / Qty. column on EVERY row (default 1). Inspect each row's Qty. column carefully (e.g., 1 vs 2) and never default qty to 1 when the Qty. column shows 2 or more. Do NOT split a qty > 1 line item into multiple JSON objects; emit a single line_item object with "qty": N.
                    - "Cost": Sticker price / per-unit price of the line item before global fees. If the line shows an extended Amount for qty > 1 (e.g. Qty. 2 with Amount 15.30), divide Amount by qty so Cost is the per-unit price (7.65).
                    - "is_supply": Set to true ONLY if the item is a non-coin accessory/supply (e.g., coin album, display box, storage capsule, insurance, or grading fee).
                    Output ONLY valid JSON.
```
and:
```python
                    normalized_coins = normalize_and_validate_receipt(data, fname=fname, gcs_path=gcs_path, session_id=session_id)
                    total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_coins), 2)

                    hdr = data if isinstance(data, dict) else (data[0] if (isinstance(data, list) and data and isinstance(data[0], dict)) else {})
```
**Verification:** Prompt instructs Gemini to preserve leftmost Qty column without splitting rows. `total_val` calculates unit cost multiplied by item quantity, rounded to 2 decimal places.

---

### 3. `numista_backend/tests/test_v8_18_15e_regression.py:732-848` (Change C — Regression Test)
```python
    coin_docs = main.normalize_and_validate_receipt(raw_multipage_gemini)
    # Total returned should be 2 line item rows (1 from page 1, 1 from page 2 with Quantity: 2)
    assert len(coin_docs) == 2

    # Coin 0 (Page 1)
    assert coin_docs[0]["Retailer Invoice #"] == "67000011"
    assert coin_docs[0]["Purchase Date"] == "2024-11-07"
    assert coin_docs[0]["retailer"] == "Littleton Coin Company"
    assert coin_docs[0]["Cost"] == 19.95
    assert coin_docs[0]["Quantity"] == 1
    assert coin_docs[0]["quantity"] == 1

    # Coin 1 (Page 2, Quantity: 2)
    assert coin_docs[1]["Retailer Invoice #"] == "67226944"
    assert coin_docs[1]["Purchase Date"] == "2025-01-23"
    assert coin_docs[1]["retailer"] == "Littleton Coin Company"
    assert coin_docs[1]["Cost"] == 29.95
    assert coin_docs[1]["Quantity"] == 2
    assert coin_docs[1]["quantity"] == 2
```
and Part 2:
```python
    normalized_all = main.normalize_and_validate_receipt(full_2page_payload)
    assert len(normalized_all) == 14
    assert sum(int(d.get("Quantity") or 1) for d in normalized_all) == 17

    p1_rows = [d for d in normalized_all if d.get("Retailer Invoice #") == "67000011"]
    p2_rows = [d for d in normalized_all if d.get("Retailer Invoice #") == "67226944"]
    assert len(p1_rows) == 9
    assert len(p2_rows) == 5
    assert all(d.get("Purchase Date") == "2024-11-07" for d in p1_rows)
    assert all(d.get("Purchase Date") == "2025-01-23" for d in p2_rows)

    k64 = [d for d in normalized_all if d.get("Year") == "1964" and d.get("Mint Mark") == "D"]
    assert len(k64) == 1 and k64[0]["Quantity"] == 2 and k64[0]["quantity"] == 2 and k64[0]["Cost"] == 19.95

    k82 = [d for d in normalized_all if d.get("Year") == "1982" and d.get("Mint Mark") == "S"]
    assert len(k82) == 1 and k82[0]["Quantity"] == 2 and k82[0]["quantity"] == 2 and k82[0]["Cost"] == 29.95

    k01 = [d for d in normalized_all if d.get("Year") == "2001" and d.get("Mint Mark") == "P"]
    assert len(k01) == 1 and k01[0]["Quantity"] == 2 and k01[0]["quantity"] == 2 and k01[0]["Cost"] == 7.65

    total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_all), 2)
    assert total_val == 298.55
```
and linking:
```python
    assert link_res.get("linked") == 14
    assert link_res.get("unlinked") == 0
```
**Verification:** Verbatim code matches exact requirements from `NET-484` and `NET-488` Step 2.

---

### 4. `numista_backend/tests/test_invoice_fixtures.py:149-317` (Change D — Legacy Fixture Adaptations)
```python
    results = normalize_and_validate_receipt(data)
    assert len(results) == 2  # 1 ASE (qty 1) + 1 Morgan Dollar row (qty 2)
    assert results[0]["Program/Series"] == "American Silver Eagle"
    assert results[0]["retailer"] == "US Mint"
    assert results[0]["Quantity"] == 1
    assert results[1]["Program/Series"] == "Morgan Dollar"
    assert results[1]["Quantity"] == 2
```
and:
```python
    results = normalize_and_validate_receipt(raw_data)
    # Album skipped (1 item), Lincoln Cent (qty 3), Cent & Nickel Set (qty 1) = 2 row items
    assert len(results) == 2
    cents = [c for c in results if c["Program/Series"] == "Lincoln Cent"]
    assert len(cents) == 1
    assert cents[0]["Quantity"] == 3
    set_coin = [c for c in results if c["Program/Series"] == "Cent & Nickel Set"]
    assert len(set_coin) == 1
    assert set_coin[0]["Quantity"] == 1
    assert set_coin[0]["Denomination"] == "Cent"
    assert not any("album" in (c.get("Personal Notes") or "").lower() for c in results)
```
and:
```python
    # 1. Output must be exactly 13 row items (15 input minus 2 supply rows)
    assert len(results) == 13, f"Expected 13 output row items, got {len(results)}"
```
and:
```python
    # 4. Quantity sum across all items is 15 physical coins, with qty=2 Kennedy halves having Quantity == 2
    assert sum(c.get("Quantity", 1) for c in results) == 15
    halves = [c for c in results if c["Program/Series"] == "Kennedy Half Dollar"]
    assert len(halves) == 2, f"Expected 2 Kennedy half rows, got {len(halves)}"
    for h in halves:
        assert h["Quantity"] == 2
```
and:
```python
    results = normalize_and_validate_receipt(raw_usmint_invoice, fname="usmint_order_2026.pdf")
    assert len(results) == 1, f"Expected 1 row item for qty=3, got {len(results)}"
    coin = results[0]
    assert coin["retailer"] == "United States Mint"
    assert coin["invoice_number"] == "USM23436235"
    assert coin["purchase_date"] == "2026-03-15"
    assert coin["Program/Series"] == "American Silver Eagle"
    assert coin["Mint Mark"] == "W"
    assert coin["Cost"] == 85.00
    assert coin["Quantity"] == 3
```

---

## Conclusion & Verdict

Commit `6ee3de89` on `origin/p7-v8.9`:
- Strictly touches 3 backend files only (0 Flutter files, 0 Markdown files).
- Exact Red/Green proof verified (`3 == 2` -> `1 passed`).
- Full backend pytest suite: 614/614 passed (exit code 0).
- Pure LF line endings (0 CRLF bytes).
- All citations verbatim.

**Gemini Review Verdict:** **PASS (READY FOR ARGON REVIEW)**
