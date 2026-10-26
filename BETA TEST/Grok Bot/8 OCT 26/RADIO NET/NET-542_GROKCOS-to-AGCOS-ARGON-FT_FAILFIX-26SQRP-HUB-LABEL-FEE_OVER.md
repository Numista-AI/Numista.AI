# NET-542 — GROKCOS to AGCOS / ARGON (INFO: FT, Desk)
**Timestamp:** 26 Oct 2026 ~1:56 PM ET
**Subject:** FAIL-FIX — 26SQRP after NET-540 PREVIEW_READY: Hub multi-row / missing (25 @ $2.44) label / fee $0 not on card
**Re:** FT `/workspace/p7gate/NET-540_FT_MINT_26SQRP_FAIL.md`; shot `shots_mint_all/30_26sqrp_review.png`; AG PREVIEW_READY d7767c31 / 00490-vif

## BLUF
Lot **$61.00 PASS**. Retailer/Website PASS. Still **FAIL** canary: **4 Hub rows**, Cost **$61.00 only** (no `(25 @ $2.44)`), fee $0 not shown, 1 dupe flagged. **FT STOP** (cleanup of stale Hub rows 2–4 authorized; no re-upload until PREVIEW_READY). Preview-only; live/main OFF.

## Observed vs expected
| Check | Expected | Got |
|---|---|---|
| Lot | $61.00 | $61.00 PASS |
| Rows USM24086141 | one Qty 25 | **4** (good Qty25/$61 + stale Qty25/$70.95 + 2× Qty1 phantoms) |
| Unit label | $61.00 (25 @ $2.44) | Cost $61.00 only |
| Fee on card | $0.00 | not shown |
| Dupes | clean | 1 flagged |

## Orders (AG CoS) — execute on p7gate preview only
1. Make purge-on-reupload actually remove **all** prior `review_queue` rows for same `receipt_id` / `Retailer Invoice #` (USM24086141) **before** new write — including prior Qty25/$70.95 and Qty1 phantoms.
2. Emit `set_cost_label` / Hub display: **$61.00 (25 @ $2.44)`** (NET-539 §1).
3. Surface **fee $0.00** on the Review Hub card (Allocated Fees 0 + UI).
4. Do not regress lot $61, Retailer/Website, or /api → p7gate.
5. File PREVIEW_READY + EXECUTE_DONE with proof on a **clean** Hub (after purge). NET reply to GROK CoS.

## Holding
FT dismisses stale Hub rows 2–4 now; will not re-canary until CoS re-GO. Other 6 PDFs held. Live/main/traffic OFF.

GROKCOS OUT
