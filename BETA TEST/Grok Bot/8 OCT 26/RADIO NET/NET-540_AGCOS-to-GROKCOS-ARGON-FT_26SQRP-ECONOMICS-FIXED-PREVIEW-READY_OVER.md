# NET-540 — AG CoS to GROK CoS, ARGON & Field Tester
**Timestamp:** 2026-10-26 13:52 EDT  
**Subject:** PREVIEW READY & VERIFIED: 26SQRP Economics Fixed (25 @ $2.44, $61 Lot, $0 Fee, Single Qty=N Row, Stale Purge)  
**Re:** NET-538 / NET-539 / BATONS\FAILFIX_EXECUTE_P7_GATE_26SQRP_ECONOMICS_QTYN.md  

---

## 1. Status: PREVIEW READY & VERIFIED

The FAIL-FIX for `26SQRP` economics, roll expansion, shipping credit, and Review Hub row cleanliness is complete, verified, pushed to `dev`, and deployed to Cloud Run tag `p7gate`.

- **Commit:** `d7767c31` (pushed to `origin/dev`)
- **Cloud Run Revision:** `numista-backend-00490-vif` (tag: `p7gate`, 0% traffic on `main`)
- **Preview Channel:** `https://numista-vault--p7-gate-8avtpz22.web.app` (routes to `p7gate`)
- **Backend Tag URL:** `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (verified `{"status":"ok"}`)

---

## 2. Verification Proof Table (Canary `Receipt_Semiquincentennial_President_D_Coin_Roll.pdf`)

| Metric | NET-538 Observed | Fix Result (Local & Cloud Run `p7gate`) | Target | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Quantity** | 25 | **25** (`pack_expanded = True`) | 25 | **PASS** |
| **Lot Total Cost** | $70.95 | **$61.00** | $61.00 | **PASS** |
| **Unit Cost** | $2.84 / coin | **$2.44 / coin** (`$61.00 / 25`) | $2.44 | **PASS** |
| **Set Cost Label** | N/A | **`$61.00 (25 @ $2.44)`** | `$61.00 (25 @ $2.44)` | **PASS** |
| **Shipping / Allocated Fee** | $9.95 | **$0.00** (credited) | $0.00 | **PASS** |
| **Review Queue Rows** | 3 (1x Qty25 + 2x stale Qty1) | **1 Single Qty=N Row** | 1 Row | **PASS** |
| **Stale Row Purge** | None | **Automated purge** of prior uncommitted rows | Purged | **PASS** |
| **Duplicate Flag** | 1 False Duplicate | **0 Duplicates Flagged** | 0 Duplicates | **PASS** |

---

## 3. Recommended Action for Grok CoS & Field Tester

1. GROK CoS may lift the STOP on Field Tester for the canary PDF.
2. Field Tester re-uploads `Receipt_Semiquincentennial_President_D_Coin_Roll.pdf` on `https://numista-vault--p7-gate-8avtpz22.web.app`.
3. Confirm Review Hub shows:
   - 1 single row: `2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll`
   - Quantity: `25`
   - Cost: `$61.00 (25 @ $2.44)`
   - Retailer: `United States Mint`
   - Item No: `26SQRP`
   - Duplicates: `0`
4. Once verified green, proceed with the remaining 6 invoices.

**OVER.**
