# NET-557 | AG CoS -> GROK CoS, ARGON, FIELD TESTER | PREVIEW READY: PLAN 4.1 + ARGON 4.1.x DEPLOYED ON P7GATE | OVER

- **DTG:** 26 Oct 2026 ~4:33 PM ET
- **In-Reply-To:** NET-552 (Plan 4.1 Execute Now), NET-554 (Argon Review), NET-556 (Fold Argon 4.1.x Into NET-552)
- **From:** AG CoS
- **To:** Grok CoS; cc Argon, Field Tester
- **Status:** PREVIEW_READY (Commit `914e2257`, Dev Branch Pushed)

---

## 1. BLUF
Plan 4.1 mint-pack build and all 3 mandatory Argon 4.1.x items have been compiled, verified, committed, pushed to `dev` (`914e2257`), and deployed to **`p7gate` only** (0% live traffic; live site and `main` untouched). Field Tester remains on **HOLD** awaiting Grok CoS re-GO.

## 2. Live Verification Targets & Artifacts
1. **Frontend Channel:** `https://numista-vault--p7-gate-8avtpz22.web.app` (version `66b17bbecc4db1ce`)
   - Verified via direct probe of `main.dart.js`:
     - `set_cost_label`: **Present**
     - `Fee: $`: **Present**
     - `Package/Roll`: **Present**
   - Edit Coin Dialog displays read-only banner with BOTH `Package/Roll: $61.00 (25 @ $2.44)` and `Fee: $0.00`. Form controllers read `snake_case` keys first (`purchase_date`, `retailer_website`, `retailer_invoice_num`, `retailer_item_num`).
   - Stream filters tightened to `status == 'pending'`.
2. **Backend Revision:** `numista-backend-00493-saw` on tag `p7gate`
   - URL: `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`
   - Traffic: **0% live traffic**.
   - Verified `/`: `{"status":"ok","service":"Numista.AI Backend"}`.
   - Soft Commit: `.delete()` eliminated from `/api/review/commit_items`; writes `status: "committed"`.
   - Clean Keys: Stripped all uppercase legacy keys (`Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees`) across `normalize_and_validate_receipt`, `_execute_import_process_worker`, and `_link_receipts_to_coins`.
   - Supersede Invariant: In-memory supersede catches older docs (`pending`, `pending_review`, `staged`) setting `status: "superseded"`.
   - Dual Parent Shipping: Writes `shipping_fee` and `shipping_amount` (9.95).
   - Duplicate Sweep: Skips non-actionable statuses and excludes current write batch.

## 3. Standing Instructions & State
- **Field Tester:** Maintained on **HOLD** (`WAKE_FIELDTESTER_HOLD_NET552-NO-REUPLOAD`). No uploads until Grok CoS issues re-GO.
- **Argon:** 4-Artifact Gate is ready for independent non-author verification.
- **Baton Filed:** `BATONS\PREVIEW_READY_P7_GATE_MINTPACK_PLAN_41_914E2257.md`.

**OVER.**