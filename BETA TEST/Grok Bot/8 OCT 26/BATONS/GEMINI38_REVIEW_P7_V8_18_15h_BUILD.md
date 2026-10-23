# GEMINI38_REVIEW: P7 V8.18.15h BUILD

**Commit:** `72cb6c0ff2358251999ff227fd5209bb43928749`  
**Branch:** `p7-v8.9`  
**Reviewer:** AG CoS (`72de93b5-a5a0-41fa-8094-c21bfd4fcfbd`)  
**Addressed To:** Argon Reviewer (`31035602-8cdd-403f-8b72-7280605f5100`) per NET-452  
**Date:** 2026-10-23 ~19:20 ET  

---

## 1. Verbatim Code Line Citations (Eric 13 Oct Rule 6a)

### A. Direct ID Matching & Used ID Tracking in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7054-7069
        coin_id_map = {c_id: c_data for c_id, c_data in coin_data}
        used_coin_ids = set()

        for item in line_items:
            item_type = str(item.get("item_type", "coin")).lower()
            if item_type not in ("coin", "bullion", "round", "medal", "token"):
                continue

            matched_coin_id = None
            match_tier = "none"

            direct_id = str(item.get("id") or "").strip()
            if direct_id and direct_id in coin_id_map and direct_id not in used_coin_ids:
                matched_coin_id = direct_id
                match_tier = "exact"
```

### B. Per-Item Retailer and Invoice Metadata in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7071-7073
            retailer = str(item.get("Retailer/Website") or item.get("retailer") or rec.get("retailer", "")).lower().strip()
            inv_no   = str(item.get("Retailer Invoice #") or item.get("invoice_number") or rec.get("invoice_number", "")).lower().strip()
            item_no  = str(item.get("Retailer Item No.", "")).lower().strip()
```

### C. Stamping Per-Item Paper Trail without Clobbering in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7143-7151
                paper_trail = {
                    "source": "receipt_link",
                    "receipt_id": rec.get("id"),
                    "session_id": session_id,
                    "match_tier": match_tier,
                    "retailer": item.get("retailer") or rec.get("retailer"),
                    "invoice_number": item.get("invoice_number") or rec.get("invoice_number"),
                    "invoice_date": purchase_date,
                    "total_price": purchase_price_raw,
```

### D. Multi-Page Child Item Metadata Stamping in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7715-7729
            for sub_r in r_list:
                if isinstance(sub_r, dict):
                    page_inv = sub_r.get("invoice_number")
                    page_date = sub_r.get("invoice_date")
                    page_ret = sub_r.get("retailer")
                    for sub_item in sub_r.get("line_items", []):
                        if isinstance(sub_item, dict):
                            if page_inv and not sub_item.get("invoice_number"):
                                sub_item["invoice_number"] = page_inv
                            if page_date and not sub_item.get("invoice_date"):
                                sub_item["invoice_date"] = page_date
                            if page_ret and not sub_item.get("retailer"):
                                sub_item["retailer"] = page_ret
                    items = sub_r.get("line_items", [])
                    all_items.extend(items)
```

### E. Quantity Parsing and Unit Cost Division in `numista_backend/main.py`
```python
# File: numista_backend/main.py:7749-7764
            qty = _get_item_qty(item)
            cost_raw = (
                item.get("cost") or
                item.get("price") or
                item.get("unit_price") or
                item.get("Total Price") or
                item.get("Purchase Price") or
                0.0
            )
            try:
                tot_amt = float(re.sub(r"[^\d.]", "", str(cost_raw))) if cost_raw else 0.0
            except (ValueError, TypeError):
                tot_amt = 0.0
            unit_cost = round(tot_amt / qty, 2) if (qty > 1 and tot_amt > 0) else tot_amt

            cleaned_items.append({
                "description": item.get("description", ""),
                "quantity": qty,
                "cost": unit_cost,
```

### F. Client-Side Polling Timeout Extension and Progress Guard in `numista_mobile/web/add_coins.html`
```javascript
// File: numista_mobile/web/add_coins.html:1032-1069
  let lastProgressTime = Date.now();
  let lastProcessedCount = 0;
  const MAX_POLL_MS = 180000; // 180s timeout for multi-page documents
  pollInterval = setInterval(async () => {
    try {
      const elapsed = Date.now() - startTime;
...
      if ((data.processed_files || 0) > lastProcessedCount) {
        lastProcessedCount = data.processed_files || 0;
        lastProgressTime = Date.now();
      }
      if (data.status === 'linking') {
        lastProgressTime = Date.now();
      }

      // Check timeout only if overall cap reached and no recent activity in 60s
      if (elapsed >= MAX_POLL_MS && (Date.now() - lastProgressTime >= 60000)) {
        clearInterval(pollInterval);
        showError('Processing timed out. Please check your Review Queue or try uploading again.', true);
        document.getElementById('progress-label').textContent = 'Timed out';
        return;
      }
```

### G. App Version Bump
```dart
// File: numista_mobile/lib/constants.dart:28
const String kAppVersion = 'v8.18.15h';
```
```yaml
# File: numista_mobile/pubspec.yaml:19
version: 8.18.15+81818
```

---

## 2. Review Findings

1. **Surgical Scope:** Exactly 5 files modified (3 backend/test, 2 frontend/version). 0 unrelated changes.
2. **Line Endings:** Clean LF verified (0 CRLF bytes).
3. **Automated Test Results:**
   - Backend regression tests: 7/7 passed.
   - Flutter tests: 645/645 passed.
   - Flutter analyze: 0 errors.
4. **Safety & Invariants:**
   - No data deletion or live traffic modifications.
   - No merges to `main`.
   - Isolated to `p7-v8.9` branch.
