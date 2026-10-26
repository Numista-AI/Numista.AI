# BATON | PREVIEW READY: P7-GATE MINTPACK PLAN 4.1 + ARGON 4.1.x

- **DTG:** 2026-10-26 ~4:33 PM ET
- **Status:** PREVIEW_READY
- **Git Commit:** `914e2257f0322f333110fd13ffa8981ca882e591` (pushed to `origin/dev`)
- **Frontend Target:** `https://numista-vault--p7-gate-8avtpz22.web.app` (version `66b17bbecc4db1ce`)
- **Backend Target:** `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app` (revision `numista-backend-00493-saw`, 0% traffic)

---

## Non-Author 4-Artifact Gate Evidence (Plan 4.1 §6 / NET-556)

1. **Frontend Deployed & Verified:**
   - Hosted JS (`https://numista-vault--p7-gate-8avtpz22.web.app/main.dart.js`) verified via Python string probe:
     - `set_cost_label found: True`
     - `Fee: $ found: True`
     - `Package/Roll found: True`
   - Form field controllers read pure snake_case keys (`purchase_date`, `retailer_website`, `retailer_invoice_num`, `retailer_item_num`).
   - Read-only banner in Edit Coin dialog displays BOTH `Package/Roll: $61.00 (25 @ $2.44)` and `Fee: $0.00`.
   - Stream filters tightened strictly to `status == 'pending'`.

2. **Backend Deployed & Verified:**
   - Tag: `p7gate`
   - Revision: `numista-backend-00493-saw` (serving 0% production traffic).
   - Root health check (`/`): `{"status":"ok","service":"Numista.AI Backend"}`.
   - Commit endpoint `/api/review/commit_items`: Replaced `.delete()` with soft-commit `.set(status: "committed", committed_at: firestore.SERVER_TIMESTAMP)`. Zero hard deletions.
   - Duplicate sweep: Excludes `new_coin_ids` and skips `review_queue` rows with non-actionable status (`superseded`, `aborted`, `committed`, `dismissed`).
   - Clean keys: Removed legacy illegal uppercase keys (`Retailer/Website`, `Retailer Invoice #`, `Retailer Item No.`, `Allocated Fees`) across all three write paths (`normalize_and_validate_receipt`, `_execute_import_process_worker`, and `_link_receipts_to_coins`). Pure `snake_case` written.
   - In-memory supersede: Supersedes older rows matching `receipt_id` with `pending`, `pending_review`, or `staged` to `status: "superseded"`.
   - Parent shipping fee: Dual-written as `shipping_fee = 9.95` and `shipping_amount = 9.95`.

3. **Field Tester Status:**
   - **HOLD MAINTAINED.** Field Tester remains on HOLD with NO re-upload permitted until Grok CoS issues re-GO.
