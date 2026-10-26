# COS EXECUTE — Plan v3.1 Mint-pack / Upload Invoice (p7gate ONLY)
**NET:** NET-543  
**Filed:** 26 Oct 2026 ~2:47 PM ET by GROKCOS / Antigravity Desk  
**Eric:** typed **go** ~2:45 PM ET  
**Supersedes:** NET-542 delete-style FAIL-FIX  

## Source
- Plan: `MINTPACK_UPLOAD_INVOICE_PLAN_v3.1_2026-10-26.md`
- Ready: `MINTPACK_UPLOAD_INVOICE_READY_TO_BUILD_2026-10-26.md`
- Preview: https://numista-vault--p7-gate-8avtpz22.web.app

## Implement (§5 only)
Stable `doc_id` + `normalized_line_key` with `or 'item'`; new pending `.set` without merge + top-level `receipt_id`; supersede via query + **in-memory** id filter + `status:superseded` (no `.delete()`); snake_case same baton; parent shipping / child `` / fees 0 / `set_cost_label`; Hub pending-only snake_case bind; deploy composite index `(receipt_id, status)` **before** canary (confirm p7gate Firebase project; Gemini cited `studio-9101802118-8c9a8`).

## PREVIEW_READY (§6)
Matching hashes on re-upload; one pending Qty25 / $61 / visible `$61.00 (25 @ $2.44)` / fee $0.00; parent shipping 9.95; superseded log; zero deletes; still p7gate.

## Forbidden
coins until Hub approve; live/main/traffic; Eric account; mobile; BQ/passport rewrites; OC2; `.delete()`.

FT HOLD until CoS re-GO. Argon Reviewer optional after patch.
