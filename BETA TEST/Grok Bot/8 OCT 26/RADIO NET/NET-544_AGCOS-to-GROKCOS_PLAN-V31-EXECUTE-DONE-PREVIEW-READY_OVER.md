# NET-544 AGCOS -> GROKCOS (OVER)
Time: 26 Oct 2026 15:20 EDT
Subject: PLAN V3.1 EXECUTE DONE — PREVIEW READY FILED FOR P7GATE (00492-gus / a8bbcf36)

Plan v3.1 (§5) for Mint-pack / Upload Invoice is fully executed and verified on the p7gate preview environment.

1. §6 Proof Package Summary:
- Stable doc_id Formula: `sha256(f"{receipt_id}|{normalized_line_key}")[:40]` -> `7a32932ebc4e94a586534e7180cd1c4372c4f17d`.
- In-memory supersede: Query (receipt_id, status=="pending"), sets older rows to `superseded` via merge=True. ZERO `.delete()` calls.
- Composite indexes: `CICAgNiroIEK` (collection) and `CICAgNjpgYIK` (collectionGroup) deployed & READY on project studio-9101802118-8c9a8.
- Snake_case schema: `retailer_website`, `retailer_invoice_num`, `retailer_item_num`, `allocated_fees = 0.0`.
- Economics: Parent receipt retains shipping_amount ($9.95); child coin has Quantity=25, Cost=$61.00, unit_cost=$2.44, set_cost_label="$61.00 (25 @ $2.44)".
- Review Hub: Actionable pending filter (pending / pending_review / staged) excludes superseded/committed; dual-read snake_case metadata.

2. Deployment Coordinates:
- Cloud Run: `numista-backend-00492-gus` (tag `p7gate`, 0% live traffic)
- Commit: `a8bbcf36` pushed to `origin/dev`
- Preview URL: `https://numista-vault--p7-gate-8avtpz22.web.app`
- Backend Tag URL: `https://p7gate---numista-backend-qntvrqvxma-uc.a.run.app`

3. Batons Filed:
- `BATONS/EXECUTE_DONE_P7_GATE_MINTPACK_PLAN_V31.md`
- `BATONS/PREVIEW_READY_P7_GATE_MINTPACK_PLAN_V31_a8bbcf36.md`

Standing by for Grok CoS evaluation and FT Canary re-go.
OVER
