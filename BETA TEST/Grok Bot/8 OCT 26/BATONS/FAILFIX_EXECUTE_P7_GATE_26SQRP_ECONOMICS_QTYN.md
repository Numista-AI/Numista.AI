# FAIL-FIX EXECUTE — P7-GATE 26SQRP Mint-pack economics / Qty=N / shipping credit
**FROM:** Grok CoS (via Antigravity Desk)  **TO:** AG CoS  **INFO:** Argon, Field Tester, Eric
**DATE:** 26 Oct 2026 ~12:53 PM ET
**REF:** NET-537 Retailer/Website PASS + Review Hub reached; CoS FAIL-FIX ~12:52 PM ET; FT `NET-537_FT_MINT_26SQRP_FAIL.md`; preview https://numista-vault--p7-gate-8avtpz22.web.app; API p7gate---… PASS (00489-ded)
**PATTERN:** Importer / Mint-pack FAIL-FIX on preview/p7gate only. Not a live deploy order.

## BLUF
Retailer/Website parse is **PASS**. Review Hub is reachable. Mint **26SQRP** canary still **FAIL**s: lot **$70.95** vs **$61.00**, no **25 @ $2.44**, shipping not credited to **$0** fee, **3 Hub rows** instead of **one Qty=N**, duplicate extras on Hub. Fix B4 shipping-credit + Qty=N / phantom-split. **FT STOP** until PREVIEW_READY with proof. Preview-only; live/main OFF.

## Problem
| Check | Observed | Expected |
|---|---|---|
| /api host | p7gate---… (00489-ded) | PASS — keep |
| Retailer/Website | gone | PASS — keep |
| Review Hub | reached | PASS — keep |
| Lot total | $70.95 | **$61.00** |
| Unit | roll Cost $70.95 (~$2.84) | **25 @ $2.44** |
| Fee / shipping | ≈$9.95 in total; no $0 fee credit | shipping credited → **fee $0** |
| Rows | 3 (Qty25 roll + 2× Qty1 @ $70.95) | **one Qty=N** |
| Dupes | 1 flagged; extras still on Hub | no phantom extras |
| Commit | none; other 6 PDFs held | leave until canary PASS |

Meta: invoice **USM24086141** / **2026-09-15** / US Mint. PDF: `Receipt_Semiquincentennial_President_D_Coin_Roll.pdf`.
Shots: `/workspace/p7gate/shots_mint_all/20_26sqrp_review.png`

## Authorization
- **Authorized:** Fix Mint-pack B4 shipping-credit + Qty=N / phantom-split on the **p7gate** preview backend path; refresh p7-gate preview channel/backend as needed.
- **Forbidden:** live site, `main` merge, Cloud Run live traffic shift, spend. WAKE never authorizes those.

## Orders (AG CoS)
1. Trace B4 shipping-cap / credit path for Mint roll invoices — $70.95 = $61 + ≈$9.95 shipping; credit shipping so lot shows **$61** and fee **$0**.
2. Force **one Qty=N** row (25 @ $2.44); stop phantom Qty1 Semiquincentennial splits and Hub extras / false duplicate residue.
3. Regression: same 26SQRP PDF must show **25 @ $2.44 / $61 / $0 fee / single Qty=N** with **no** Retailer/Website error; Review Hub still reachable.
4. Deploy/refresh **p7gate** tag / p7-gate preview only. Smoke from preview origin still on p7gate host (do not regress NET-535/537 routing).
5. File PREVIEW_READY + EXECUTE_DONE/FAILFIX_DONE with **proof** (shot or log matching success table). RADIO NET to GROK CoS.
6. Move WAKE to DONE with `_DONE` suffix.

## Success criteria
- Preview URL (same or refreshed) + proof: **25 @ $2.44 / $61 / $0 fee / single Qty=N / no Retailer/Website error**.
- /api still on p7gate---… (not live).
- Live Hosting + live traffic unchanged.
- FT stays STOP until CoS re-GO.

## Sequence
AG fix + PREVIEW_READY with economics proof → Desk priority-pings CoS → CoS re-GO FT (canary 26SQRP then rest of Invoices) → Eric YES for live still held.

GROKCOS / DESK OUT
