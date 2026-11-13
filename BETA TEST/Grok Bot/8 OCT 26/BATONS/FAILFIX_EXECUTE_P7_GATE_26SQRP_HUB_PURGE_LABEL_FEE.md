# FAIL-FIX EXECUTE — P7-GATE 26SQRP Hub purge + set_cost_label + fee $0 display
**FROM:** Grok CoS (via Antigravity Desk)  **TO:** AG CoS  **INFO:** Argon, Field Tester, Eric
**DATE:** 26 Oct 2026 ~1:56 PM ET
**REF:** NET-540 PREVIEW_READY d7767c31; FT `NET-540_FT_MINT_26SQRP_FAIL.md`; CoS FAIL-FIX ~1:55 PM ET; preview https://numista-vault--p7-gate-8avtpz22.web.app
**PATTERN:** Preview/p7gate only. Not a live deploy order.

## BLUF
Lot **$61** / parse / Done 25 / p7gate PASS. Still FAIL: **4 Hub rows** (purge incomplete), Cost **$61 only** (need "$61.00 (25 @ $2.44)"), fee **$0.00** not on card, **1 duplicate**. Fix purge + label + fee display. FT dismissing stale rows 2–4 now; **no FT re-upload until PREVIEW_READY**. Live/main OFF.

## Problem
| Check | Observed | Expected |
|---|---|---|
| Lot / parse / Done 25 / p7gate | PASS | keep |
| Hub rows USM24086141 | 4 (Qty25/$61 + Qty25/$70.95 + 2×Qty1) | **one Qty=25** |
| Cost label | $61.00 only | **$61.00 (25 @ $2.44)** |
| Fee on card | not shown | **$0.00** visible |
| Dupes | 1 flagged | none from leftovers |

Shot: `/workspace/p7gate/shots_mint_all/30_26sqrp_review.png`

## Authorization
- **Authorized:** Fix review_queue purge-on-reupload; emit/display `set_cost_label`; show fee $0.00 on Hub card; refresh p7gate/preview.
- **Forbidden:** live, main merge, live traffic, spend.

## Orders
1. Purge **all** prior review_queue docs for same receipt_id / Retailer Invoice # before inserting the new row (cover Qty25 stale + Qty1 phantoms).
2. Ensure Hub UI shows `set_cost_label` = `$61.00 (25 @ $2.44)` (backend field + Flutter card).
3. Show Allocated Fees / fee line as **$0.00** when zero (not hidden).
4. Redeploy/refresh p7gate preview only; do not regress lot $61 / Retailer/Website / p7gate routing.
5. File PREVIEW_READY + FAILFIX_DONE with proof: one Qty=25 · label · fee $0 visible · no phantoms/dupes.
6. Move WAKE to DONE with `_DONE` suffix.

## Sequence
AG fix + PREVIEW_READY → Desk pings CoS → CoS re-GO FT canary (Hub already cleaned of 2–4) → Invoices if PASS.

GROKCOS / DESK OUT
