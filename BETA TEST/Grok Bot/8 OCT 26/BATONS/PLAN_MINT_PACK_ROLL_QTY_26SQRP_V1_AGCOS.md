# AGCOS PLAN.v1: US MINT PACK/ROLL QUANTITY EXPANSION (26SQRP) & UX POLISH
**Track:** P7-MINT-PACK-ROLL-QTY-26SQRP-V1  
**Author:** AG CoS  
**Date:** 2026-10-25  
**Target:** Dev / Preview (Holding live deploy until explicit Eric typed YES)  
**Ref Radio:** NET-501 (Grok CoS)  
**Ref Baton:** `BETA TEST\Grok Bot\8 OCT 26\BATONS\PLAN_MINT_PACK_ROLL_QTY_26SQRP_V1.md`  

---

## 1. Executive Summary & Goals
During Eric's live testing on 24 Oct (~7:40–7:53 PM ET), uploading `Receipt Semiquincentennial President D Coin Roll.pdf` (US Mint SKU `26SQRP`, a 25-coin roll) demonstrated that while invoice multi-line QTY rollups work (V8.18.15i), **Mint SKU pack/roll quantities are not expanded**:
1. Review Hub item showed `26SQRP`, `QTY: 1`, cost `$70.95` (should have `Quantity: 25`, unit cost `$61.00`).
2. Add Coins UI showed `Processing Files` indefinitely while badge displayed `Done — 1 coin`, preventing a clean exit without opening a new tab.
3. Review Hub sidebar nav displayed `Review ...` due to narrow sidebar flex truncation next to badge count.

This plan details the changes across catalog enrichment, import counting, and UI polish to achieve the Monday acceptance bar.

---

## 2. Scope & Boundaries
- **In Scope:**
  1. Add `pack_quantity` attribute to US Mint catalog schema and catalog items (specifically `26SQRP: 25`, extensible to rolls/bags).
  2. In `enrich_us_mint_item`, expand `Quantity = pack_quantity * max(1, ship_qty)` when line item quantity <= 1 or missing. Guard against duplicate expansion if invoice already specifies 25.
  3. Ensure catalog item unit price ($61.00) is preserved as unit cost rather than leaking full order shipping/handling total ($70.95).
  4. In `main.py:_execute_import_process_worker`, compute `summary["coins_identified"]` as the sum of coin quantities (`sum(c.get("Quantity", 1) ...)`), ensuring the Add Coins "Done" count accurately reflects total coins (25).
  5. In `add_coins.html`, update progress panel header to `&#9989; All Files Processed` upon completion, display proper coin count, and provide clear "Exit to App" / "Return to Collection" buttons.
  6. In `base_layout.dart`, fix sidebar nav row layout to prevent `Review Hub` from truncating to `Review ...`.
  7. Automated tests (pytest + flutter test) verifying 26SQRP pack expansion, unit price, multi-line invoice regression protection, and pure LF compliance.

- **Out of Scope (Explicit Non-Goals):**
  - Deduplicating intentional or accidental double uploads (Eric confirmed two separate uploads occurred).
  - Outflow/inventory decrement logic for sold/gifted coins (Eric sold 2 @ $5, gifted 2 -> 21 remaining is future scope).
  - Merging to `main` or deploying to live production (Cloud Run traffic shift) without Eric's explicit typed YES.

---

## 3. Detailed Technical Architecture & Code Changes

### A. US Mint Catalog & Enrichment (`numista_backend/services/us_mint_catalog_service.py`)
1. **Catalog Entry Update:**
   Update `US_MINT_PRODUCT_CATALOG["26SQRP"]`:
   ```python
   "pack_quantity": 25,
   ```
   Ensure catalog helper functions return `pack_quantity` when querying SKU.
2. **Enrichment Expansion (`enrich_us_mint_item`):**
   ```python
   pack_qty = catalog_item.get("pack_quantity")
   if pack_qty and isinstance(pack_qty, int) and pack_qty > 1:
       current_qty = item.get("Quantity") or item.get("quantity") or 1
       try:
           current_qty = int(current_qty)
       except (ValueError, TypeError):
           current_qty = 1
       # If ship quantity is 1 (or default <= 1), expand to pack_quantity.
       # If ship quantity is > 1 (e.g. 2 rolls), expand to pack_quantity * ship_qty.
       # Guard: if item['Quantity'] already equals pack_qty (or a multiple), do not re-multiply.
       if current_qty < pack_qty:
           item["Quantity"] = pack_qty * current_qty
   ```
3. **Unit Cost Guard:**
   Ensure unit cost on enriched coin is catalog price ($61.00) if raw line item price was polluted by shipping/handling order total ($70.95).

### B. Backend Import Summary (`numista_backend/main.py`)
In `_execute_import_process_worker`:
Update:
```python
# Instead of 1 count per document:
summary["coins_identified"] = sum(int(c.get("Quantity") or 1) for c in normalized_coins)
```
This ensures the response summary payload sent to `add_coins.html` carries `coins_identified: 25`.

### C. Add Coins Status & Exit UX (`numista_mobile/web/add_coins.html`)
1. In `updateProgress(data)`:
   When `data.status === 'done'`, update:
   `document.querySelector('#progress-panel h2').innerHTML = '&#9989; All Files Processed';`
2. Add explicit navigation button in summary panel:
   `Back to Collection` / `Exit to Dashboard` alongside `Review Queue`.
3. Ensure `#stat-coins` displays `data.summary.coins_identified` (25).

### D. Navigation Label Truncation (`numista_mobile/lib/screens/base_layout.dart`)
In `_buildNavItem`:
Adjust `Row` children containing `Text(title, overflow: TextOverflow.ellipsis)` and the badge container to avoid flex collapse that cuts off "Review Hub".

---

## 4. Verification & Testing Strategy
1. **Backend Unit & Integration Tests:**
   - `tests/test_us_mint_catalog.py`: Add test verifying `26SQRP` has `pack_quantity: 25`.
   - `tests/test_us_mint_invoice_enrichment.py`: Add test verifying enrichment of a `26SQRP` invoice item sets `Quantity = 25` and preserves unit price `$61.00`.
   - Regression test: Run existing multi-line invoice tests (`test_invoice_pipeline.py`) to confirm V8.18.15i functionality remains 100% intact.
2. **Frontend Layout & UX Tests:**
   - Run `flutter analyze` and `flutter test` on modified dart files.
3. **Line Ending Verification:**
   - Execute git LF check to guarantee 0 CRLF bytes across all modified files.

---

## 5. Deployment & Release Gate
- Commit and push to branch `dev` / `p7-v8.9`.
- Deploy to Dev/Preview environment for Field Tester verification using `Receipt Semiquincentennial President D Coin Roll.pdf`.
- Submit build for Argon / Gemini38 / Grok CoS review.
- **Strict Stop:** No production Cloud Run deployment until explicit typed YES from Eric.
