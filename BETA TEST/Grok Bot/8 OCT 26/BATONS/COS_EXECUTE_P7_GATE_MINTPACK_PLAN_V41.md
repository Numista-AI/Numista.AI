# COS EXECUTE — Plan v4.1 Mint-pack / Upload Invoice (p7gate ONLY)
**NET:** NET-552  
**Filed:** 26 Oct 2026 ~4:07 PM ET by GROKCOS  
**Eric:** typed **GO** ~4:05 PM ET on Plan 4.1  
**Supersedes:** NET-547 HOLD / Plan 4.0 draft (AG); Grok YES-with-edits applied in 4.1  

## Source
- Plan: `MINTPACK_UPLOAD_INVOICE_PLAN_v4.1_2026-10-26.md`
- Ready: `MINTPACK_UPLOAD_INVOICE_READY_PLAN_v4.1_2026-10-26.md`
- Grok review: `GROK_REVIEW_PLAN_V4_2026-10-26.md`
- Preview: https://numista-vault--p7-gate-8avtpz22.web.app
- Thread: https://grok.com/c/4f52d7de-9570-487e-9b62-8bad909112f7

## Implement (p7gate only)
Backend: `from_set=True`; `set_name` exact `2026 Semiquincentennial Presidential $1 Coin 25-Coin Roll`; `set_cost_label="$61.00 (25 @ $2.44)"`; `allocated_fees=0`; parent dual-write `shipping_fee`+`shipping_amount`; dupe sweep skip non-actionable before similarity + exclude current-batch doc IDs; soft commit `status:committed` (no `.delete()`); Hub `status == "pending"` only.

Frontend + Hosting: Fee chip + set_cost_label bind; redeploy Hosting `p7-gate` (Eric firebase reauth DONE ~4:02). Cloud Run `--tag=p7gate` 0%.

## PREVIEW_READY (hard — 4 artifacts by non-author)
1) Hosting hash matches frontend commit  
2) Live main.dart.js grep Fee / set_cost_label / subtitle  
3) Firestore child+parent dump (full set_name, label, fees 0, dual shipping keys)  
4) Cloud Run p7gate revision/tag  

## Forbidden
coins until Hub approve; live/main/traffic; Eric account; `.delete()`.

FT HOLD until CoS re-GO after PREVIEW_READY.
