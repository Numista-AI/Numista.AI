# Code Review - P7 V8.18.15j Build

Changes have been successfully implemented and pushed to `dev`.

## `numista_backend/main.py`
```python
                    # B4: Cap shipping offset to avoid phantom landed cost
                    total_global_fees = 0.0
                    if grand_total > subtotal_val and subtotal_val > 0:
                        total_global_fees = grand_total - subtotal_val
                    elif (shipping_val + tax_val) > 0:
                        total_global_fees = shipping_val + tax_val
```

```python
                        if not is_supply:
                            doc["item_type"] = _classify_item_type(doc)

                        # B1: Call enrich_us_mint_item on doc to expand pack/roll quantity
                        doc["Original Description from source"] = it.get("Original Description from source", "")
                        doc["Retailer Item No."] = it.get("Retailer Item No.", "")
                        doc["Quantity"] = it.get("Quantity") or it.get("quantity") or 1
                        try:
                            from services.us_mint_catalog_service import enrich_us_mint_item
                            enrich_us_mint_item(doc)
                        except Exception as e:
                            logger.warning(f"Error enriching item in import worker: {e}")

                        doc_ref = col_ref.document(str(uuid.uuid4()))
                        batch.set(doc_ref, doc)
                        new_coin_ids.append(doc_ref.id)
                        
                        # B3: added_this_file += Quantity so the Done checkmark matches coins identified
                        doc_qty = max(1, int(doc.get("Quantity") or doc.get("quantity") or 1))
                        added_this_file += doc_qty
```

## `numista_mobile/lib/screens/base_layout.dart`
```dart
            if (badgeCount > 0) ...[
              const SizedBox(width: 8),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
```

## `numista_mobile/web/add_coins.html`
```html
<div class="card" id="summary-panel">
  <div class="card-header">
    <h2>&#9989; All Files Processed</h2>
    <span id="summary-date" style="font-size:0.82rem;color:var(--text-dim);"></span>
  </div>
```
```html
    <div class="summary-actions">
      <button class="btn btn-primary"   onclick="goToReviewQueue()">&#128203; Go to Review Queue</button>
      <button class="btn btn-secondary" onclick="showPaperTrail()">&#129534; View Paper Trail</button>
      <button class="btn btn-ghost"     onclick="resetImport()">&#11014;&#65039; Import More</button>
      <button class="btn btn-ghost"     onclick="window.parent.postMessage({type:'NAVIGATE', route:'/'}, '*');">&#10060; Exit</button>
    </div>
```

## `numista_backend/tests/test_us_mint_invoice_enrichment.py`
Added unit tests for 26SQRP 1 roll -> 25 coins, idempotency, and unit cost logic. Tests passed successfully.
