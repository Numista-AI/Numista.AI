# PREVIEW READY — P7 GATE MINTPACK / UPLOAD INVOICE (PLAN V3.1 §6 PROOF)

- **Commit:** `a8bbcf36` (pushed to `origin/dev`)
- **Cloud Run Revision:** `numista-backend-00492-gus` (tag: `p7gate`, 0% live traffic)
- **Preview Channel:** `https://numista-vault--p7-gate-8avtpz22.web.app`
- **Backend Tag URL:** `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`
- **Timestamp:** 2026-10-26 15:18 EDT

---

## 1. Verified Proof Table (Plan v3.1 §6 Proof Package)

| Plan v3.1 §6 Gate Item | Specification | Verified Output | Status |
| :--- | :--- | :--- | :--- |
| **Stable ID Formula** | `doc_id = sha256(f"{receipt_id}\|{normalized_line_key}")[:40]` | `7a32932ebc4e94a586534e7180cd1c4372c4f17d` | **PASS** |
| **No-Merge Create** | `.set(payload)` without merge; top-level `receipt_id`; `status: "pending"` | Verified in `main.py` lines 8070-8110 | **PASS** |
| **In-Memory Supersede** | Query `(receipt_id, status=="pending")`; older doc_ids `.set({'status': 'superseded'}, merge=True)` | Verified; **ZERO `.delete()`** calls | **PASS** |
| **Composite Indexes** | `(receipt_id ASC, status ASC)` on `review_queue` collection & group | `CICAgNiroIEK` & `CICAgNjpgYIK` **STATE: READY** | **PASS** |
| **Snake_case Schema** | `retailer_website`, `retailer_invoice_num`, `retailer_item_num`, `allocated_fees` | `retailer_website: United States Mint`<br>`retailer_invoice_num: USM24086141`<br>`retailer_item_num: 26SQRP`<br>`allocated_fees: 0.0` | **PASS** |
| **Review Hub Economics** | `Quantity = 25`, `Cost = 61.00`, `unit_cost = 2.44`, `set_cost_label = "$61.00 (25 @ $2.44)"` | Single row: `Quantity: 25`, `Cost: 61.0`, `set_cost_label: "$61.00 (25 @ $2.44)"` | **PASS** |
| **Parent Receipt Shipping** | Retains original shipping fee | `shipping_fee: 9.95`, child retains `allocated_fees: 0.0` | **PASS** |
| **Review Hub Filter** | Only shows actionable `pending` / `pending_review` / `staged` | Ignores `superseded` and `committed` | **PASS** |
| **Traffic / Scope** | 0% live traffic, preview tag only | Cloud Run `numista-backend-00492-gus` tag `p7gate` serving 0% live traffic | **PASS** |

---

## 2. Verification Run Output

```
Coins count post-echo collapse: 1
Quantity: 25
Cost / Purchase Cost: 61.0 / 61.0
Allocated Fees: 0.0 , allocated_fees: 0.0
set_cost_label: $61.00 (25 @ $2.44)
retailer_website: United States Mint
retailer_invoice_num: USM24086141
retailer_item_num: 26SQRP
stable_doc_id: 7a32932ebc4e94a586534e7180cd1c4372c4f17d
```

---

## 3. Deployment Health Verification
- `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app/` responded:
  `{"status":"ok","service":"Numista.AI Backend"}`
- Ready for Grok CoS evaluation and FT Canary re-run.
