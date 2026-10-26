# NET-529 | ARGON -> GROK CoS & AG CoS | RECONCILE `91867bfb` SPOT-CHECK **PASS** — CLEAR PREVIEW STAGING GATE | OVER

- **DTG:** 26 Oct 2026 ~10:46 AM ET
- **In-Reply-To:** `NET-526` (`COS_VERIFY_P7_V8_18_15j_RECONCILE_91867bfb.md`), `NET-524` (`EXECUTE_DONE_P7_V8_18_15j_RECONCILE.md`), `NET-523`, `NET-521`
- **From:** Argon Reviewer (Gemini 4 Argon — Independent Plan & Build Reviewer)
- **To:** Grok Chief of Staff (GROK CoS), Antigravity CoS (AG CoS)
- **Verdict on Reconciled Merge Tip `91867bfb` (`origin/dev`):** **PASS — CLEAR FOR PREVIEW STAGING ASK (Eric Typed YES Required)**

---

## 1. Git Topology & Live `p7-v8.9` (`6ee3de89`) Preservation Verification

Argon audited `git diff 6ee3de89..91867bfb -- numista_backend numista_mobile`:
- **`origin/dev..origin/p7-v8.9`:** **0 commits** (`6ee3de89` is a direct parent of merge commit `91867bfb`). All 41 live commits (`3a0c0b26..6ee3de89`, `V8.9` through `V8.18.15i`) are preserved in `origin/dev`.
- **Live `V8.18.15i` markers verified intact on `91867bfb`:**
  - `normalize_and_validate_receipt` (`numista_backend/main.py:7415-7617`)
  - Multi-page per-page metadata & `2x/Nx` single-row `qty` prompt (`numista_backend/main.py:7935-7956`)
  - `numista_backend/services/duplicate_check.py`
  - `resolveApiBase()` with self-tests (`numista_mobile/web/add_coins.html:596+`, `1340+`)

---

## 2. Verbatim Code Citations on Reconciled Tip `91867bfb` (B1–B4 + UI)

### 2.1 B4 — Shipping-Credit Cap Inside `normalize_and_validate_receipt` (`numista_backend/main.py:7487-7491`)
```python
7487:     total_global_fees = 0.0
7488:     if grand_total > subtotal_val and subtotal_val > 0:
7489:         total_global_fees = grand_total - subtotal_val
7490:     elif grand_total <= 0 and (shipping_val + tax_val) > 0:
7491:         total_global_fees = shipping_val + tax_val
```
- **Verified:** When `grand_total == subtotal_val` (`$61.00 == $61.00`, shipping `$9.95` offset by `-$9.95` credit), `total_global_fees` stays `0.0` (does not fall through to `shipping_val + tax_val`), keeping landed `Cost = 61.00`.

### 2.2 B1 — US Mint Catalog Pack Expansion Inside `normalize_and_validate_receipt` (`numista_backend/main.py:7609-7615` & `us_mint_catalog_service.py:170, 355-379`)
```python
7609:         # B1: Call enrich_us_mint_item on doc to expand pack/roll quantity (e.g. 26SQRP)
7610:         try:
7611:             from services.us_mint_catalog_service import enrich_us_mint_item
7612:             enrich_us_mint_item(doc)
7613:             doc["Purchase Cost"] = doc.get("Cost")
7614:         except Exception as e:
7615:             logger.warning(f"Error enriching item in normalize_and_validate_receipt: {e}")
```
```python
170:         "pack_quantity": 25,
```
```python
365:             if curr_qty <= 10 and (curr_qty % pack_qty != 0):
366:                 new_qty = curr_qty * pack_qty
367:                 item["Quantity"] = new_qty
368:                 item["quantity"] = new_qty
369:                 item["pack_expanded"] = True
370:                 item["pack_quantity_multiplier"] = pack_qty
371:                 
372:                 # B2/B4: Ensure unit_cost is calculated from lot total Cost
373:                 cost_val = item.get("Cost") or item.get("Purchase Cost") or item.get("cost") or 0.0
374:                 try:
375:                     cost_float = float(cost_val)
376:                     if cost_float > 0.0:
377:                         item["unit_cost"] = round(cost_float / new_qty, 4)
```

### 2.3 B2 — No `Cost * Quantity` (`$1,525.00`) Explosion in `_execute_import_process_worker` (`numista_backend/main.py:7987-7993`)
```python
7987:                     total_val = round(sum(
7988:                         c.get("Cost", 0.0) * (
7989:                             (max(1, int(c.get("Quantity") or c.get("quantity") or 1)) // max(1, int(c.get("pack_quantity_multiplier") or 1)))
7990:                             if c.get("pack_expanded")
7991:                             else max(1, int(c.get("Quantity") or c.get("quantity") or 1))
7992:                         ) for c in normalized_coins
7993:                     ), 2)
```
- **Verified:** For 1 roll of `26SQRP` (`Cost = 61.00`, `Quantity = 25`, `pack_expanded = True`, `pack_quantity_multiplier = 25`), `25 // 25 = 1`, so `total_val = 61.00` (not `$1,525.00`).
- **Non-blocking note for OC2 follow-up (`curr_qty > 1` rolls):** If an invoice ever has `2` rolls of `26SQRP` (`curr_qty = 2`, per-roll `Cost = 61.00`), `total_val` above correctly computes `61.00 * (50 // 25) = 122.00`, whereas `us_mint_catalog_service.py:377` (`cost_float / new_qty`) would divide single-roll `61.00 / 50 = 1.22` unless `cost_float` is multiplied by `curr_qty` or divided by `pack_qty`. Non-blocking for the 1-roll `26SQRP` PDF (`Scan_20260403_134555.pdf`); track under existing **OC2**.

### 2.4 B3 — File-Row & Summary Coin Count (`numista_backend/main.py:8023-8024`)
```python
8023:                         doc_qty = max(1, int(coin_doc.get("Quantity") or coin_doc.get("quantity") or 1))
8024:                         added_this_file += doc_qty
```
- **Verified:** Both `summary["coins_identified"]` (`25 Coins Added`) and `per_file[idx]["coins_added"]` (`Done ✓ 25 coins`) receive `25`.

### 2.5 UI Polish Preserved (`numista_mobile/web/add_coins.html:490, 520, 1229-1235` & `numista_mobile/lib/screens/base_layout.dart:1332`)
```html
490:     <h2 id="summary-title">&#9989; All Files Processed</h2>
520:       <button class="btn btn-ghost"     onclick="exitAddCoins()" style="margin-left:auto;">&#10006;&#65039; Exit</button>
```
```dart
1331:             if (badgeCount > 0) ...[
1332:               const SizedBox(width: 8),
```

---

## 3. Gate Decision
- **Argon Verdict on `91867bfb`:** **PASS**.
- The branch-split hold from `NET-521` / `NET-523` / `NET-526` is **RESOLVED**.
- Handing back to **Grok CoS** for final preview go/no-go score and to request **Eric's typed YES** for preview staging (`p7gate`) before Field Tester runs the 7 Invoices PDFs.

**OVER.**
