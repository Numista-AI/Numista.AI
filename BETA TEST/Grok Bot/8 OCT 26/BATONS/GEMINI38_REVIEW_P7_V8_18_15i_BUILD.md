# GEMINI38_REVIEW: P7 V8.18.15i BUILD

**Commit:** `1ff435f098b633cd82fc7b309b9bdadb1f2eee57`  
**Branch:** `p7-v8.9`  
**Base:** `72cb6c0f`  
**Reviewer:** AG CoS (`72de93b5-a5a0-41fa-8094-c21bfd4fcfbd`)  
**Addressed To:** Argon Reviewer (`31035602-8cdd-403f-8b72-7280605f5100`) per NET-452  
**Date:** 2026-10-24 ~13:06 ET  

---

## 1. Verbatim Code Line Citations (Eric 13 Oct Rule 6a)

### A. Quantity Setting & Single-Doc Append in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7577-7610
            "Condition":            it.get("Condition", "Ungraded"),
            "Metal Content":        metal_val,
            "Cost":                 landed_cost_basis,
            "Quantity":             item_qty,
            "quantity":             item_qty,
            "Country":              "United States",
            "Personal Notes":       (it.get("Personal Notes") or it.get("Original Description from source") or "").strip(),
            "source":               "PDF Invoice",
        }

        # If line item already has an item_id, preserve it
        if it.get("id"):
            doc["id"] = it.get("id")

        try:
            doc["_gcs_path"] = gcs_path
            doc["_receipt_filename"] = fname
        except Exception:
            pass

        results.append(dict(doc))

    return results
```

### B. Gemini Prompt & total_val Calculation in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7940-7980
                    - "retailer": If document header or body indicates "United States Mint" or "www.usmint.gov", set to "United States Mint".
                    - "invoice_number": Extract invoice number, order number, or packing slip number.
                    - "invoice_date": Output in ISO 8601 YYYY-MM-DD format.
                    - "qty": Integer quantity from the leftmost Qty / Qty. column on EVERY row (default 1). Inspect each row's Qty. column carefully (e.g., 1 vs 2) and never default qty to 1 when the Qty. column shows 2 or more. Do NOT split a qty > 1 line item into multiple JSON objects; emit a single line_item object with "qty": N.
                    - "Cost": Sticker price / per-unit price of the line item before global fees. If the line shows an extended Amount for qty > 1 (e.g. Qty. 2 with Amount 15.30), divide Amount by qty so Cost is the per-unit price (7.65).
                    - "is_supply": Set to true ONLY if the item is a non-coin accessory/supply (e.g., coin album, display box, storage capsule, insurance, or grading fee).
                    Output ONLY valid JSON.
                    """

                    content_parts = [invoice_prompt]
...
                    normalized_coins = normalize_and_validate_receipt(data, fname=fname, gcs_path=gcs_path, session_id=session_id)
                    total_val = round(sum(c.get("Cost", 0.0) * max(1, int(c.get("Quantity") or c.get("quantity") or 1)) for c in normalized_coins), 2)
```

### C. Regression Test Assertions for 092052 in `numista_backend/tests/test_v8_18_15e_regression.py`
```python
# File: numista_backend/tests/test_v8_18_15e_regression.py:769-792
    assert len(normalized_p1) == 9
    assert len(normalized_p2) == 5
    assert len(normalized_all) == 14

    # Assert total coin count via Quantity matches 17 physical coins
    total_physical_coins = sum(int(d.get("Quantity") or 1) for d in normalized_all)
    assert total_physical_coins == 17

    # Check 1964-D Kennedy is a single row with Quantity=2, Cost=19.95
    k64 = [d for d in normalized_all if d.get("Program/Series") == "Kennedy Half Dollar" and d.get("Year") == "1964" and d.get("Mint Mark") == "D"]
    assert len(k64) == 1
    assert k64[0]["Quantity"] == 2
    assert k64[0]["Cost"] == 19.95

    # Check 1982-S Kennedy is a single row with Quantity=2, Cost=29.95
    k82 = [d for d in normalized_all if d.get("Program/Series") == "Kennedy Half Dollar" and d.get("Year") == "1982" and d.get("Mint Mark") == "S"]
    assert len(k82) == 1
    assert k82[0]["Quantity"] == 2
    assert k82[0]["Cost"] == 29.95

    # Check 2001-P Kennedy is a single row with Quantity=2, Cost=7.65
    k01 = [d for d in normalized_all if d.get("Program/Series") == "Kennedy Half Dollar" and d.get("Year") == "2001" and d.get("Mint Mark") == "P"]
    assert len(k01) == 1
    assert k01[0]["Quantity"] == 2
    assert k01[0]["Cost"] == 7.65
```

### D. App Version Bump
```dart
// File: numista_mobile/lib/constants.dart:28
const String kAppVersion = 'v8.18.15i';
```
```yaml
# File: numista_mobile/pubspec.yaml:19
version: 8.18.15+81819
```

---

## 2. Review Findings
1. **Surgical Scope:** Exactly 3 functional files modified (`main.py`, `test_v8_18_15e_regression.py`, `test_invoice_fixtures.py`) + 2 version files. Zero extraneous changes.
2. **Line Endings:** 0 CRLF bytes on all files.
3. **Automated Verification:**
   - 15/15 backend pytest tests pass (0 failures).
   - 645/645 Flutter tests pass (0 failures).
4. **Safety:** Isolated to branch `p7-v8.9`. Zero changes to `main`. No live deployment.
