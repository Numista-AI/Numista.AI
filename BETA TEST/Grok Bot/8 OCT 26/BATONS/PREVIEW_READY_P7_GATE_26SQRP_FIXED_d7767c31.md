# PREVIEW READY — P7 GATE 26SQRP ECONOMICS & QTY=N FAIL-FIX

- **Commit:** `d7767c31` (pushed to `origin/dev`)
- **Cloud Run Revision:** `numista-backend-00490-vif` (tag: `p7gate`, 0% live traffic)
- **Preview Channel:** `https://numista-vault--p7-gate-8avtpz22.web.app`
- **Backend Tag URL:** `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`
- **Timestamp:** 2026-10-26 13:50 EDT

---

## 1. Verified Proof Table (Canary `Receipt_Semiquincentennial_President_D_Coin_Roll.pdf`)

| Metric | Prior Observed (NET-538 FAIL) | New Result (Verified Local & Cloud Run) | Status |
| :--- | :--- | :--- | :--- |
| **Quantity** | 25 | **25** (`pack_expanded = True`) | **PASS** |
| **Lot Total Cost** | $70.95 | **$61.00** | **PASS** |
| **Unit Cost** | $2.84 / coin | **$2.44 / coin** (`61.00 / 25`) | **PASS** |
| **Set Cost Label** | N/A | **`$61.00 (25 @ $2.44)`** | **PASS** |
| **Shipping / Allocated Fees** | $9.95 | **$0.00** (credited) | **PASS** |
| **Review Queue Rows** | 3 (1x Qty25 + 2x stale Qty1) | **1 Single Qty=N Row** | **PASS** |
| **Stale Row Purge** | None | **Automated purge** of prior runs matching receipt/invoice | **PASS** |
| **Duplicate Flag** | 1 False Duplicate Flagged | **0 Duplicates Flagged** | **PASS** |

---

## 2. Root Cause & Solution Summary

1. **Shipping Credit Override:**
   - In `us_mint_catalog_service.py:enrich_us_mint_item`, when catalog match has `issue_price` or `unit_price` (`$61.00` for `26SQRP`), canonical lot cost overrides any fee additions, zeroing `Allocated Fees` to `0.0`, setting `Cost = 61.00`, `Purchase Cost = 61.00`, and calculating `unit_cost = 2.44`.
   - In `main.py:normalize_and_validate_receipt`, US Mint orders for roll products zero global fees and shipping fee so landed cost strictly equals the catalog lot price.
2. **Single Row & Stale Row Purge:**
   - On re-uploading an invoice, `_execute_import_process_worker` queries and purges previous pending `review_queue` rows for the same `receipt_id` and `Retailer Invoice #` (`USM24086141`), preventing accumulation of stale rows and false self-duplicate triggers.
   - Defense-in-depth coupon deduplication collapses duplicate SKU echoes from physical US Mint return coupons.

---

## 3. Deployment & Health Verification
- `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app/` responded:
  `{"status":"ok","service":"Numista.AI Backend"}`
- Ready for Field Tester to re-upload canary PDF on the preview channel.
