# FIN OPS cost-check: Catalog Research Phase I burn plan
**When:** 28 Oct 2026 ~7:35 AM ET  
**Source plan:** `/workspace/catalog-research/BURN_PLAN_FOR_FINOPS_2026-10-28.md`  
**Status:** CLEARED for Eric YES ask — **no spend until typed YES**

## Credit remaining (pre–1 PM hard reconcile)
- BQ (export through ~27 Oct 10 PM ET): App Builder promo `e87a9b98…` drew **−$0.119872** on Vertex AI Search (CG + Ranking) → **~$999.88 of $1,000** left.
- Wed 28 Oct **1:00 PM ET** routine will hard-verify Week-1 / fold-gate / Option B vs console. Plan using ~$999.88 until then.

## SKU math (Phase I)
| Item | List rate (prior plan + Google pricing page) | Plan estimate | FinOps note |
|---|---|---|---|
| Layout Parser | $10 / 1,000 pages | $0–15 reuse; up to ~$30 if ~3,000 new pages | **Dominant cost.** Reuse `factcheck-src` / g1 first. Sample **50–100 pages** before any bulk LP. |
| Data index | $5 / GiB-mo; **10 GiB free** | ~$0 if stay under free | Keep under 10 GiB; prefer inline import (AWQ pattern). |
| Enterprise Search | $0 inside free 10k/mo band often | ~$0–few $ for wiring tests | OK on credit group. |
| Check Grounding | ~$0.00075 / 1k chars (near free) | Phase I-C only | **Not in Phase I ingest YES.** |
| Ranking | billed when used (Option B saw ~$0.09) | Phase I-C / later | Keep off ingest YES. |
| Advanced Generative Answers | +~$4 / 1k queries | **$0 — OFF** | Free trial excludes; prior fold-gate cost driver. **Do not enable.** |
| Vertex Gemini / Cloud Run / DocAI | n/a | **Forbidden** on morgan for this credit | |

**Phase I ingest band:** Catalog Research’s **$0–15 / up to $30** is consistent with LP math. Uncertainty is real page counts — do not treat $30 as a target; it’s a hard ceiling.

## smithsonian-nnc attach
- Store already exists (≥50k). **Attach to CG/search engine ≈ $0 incremental** (no re-ingest).
- Later queries bill Search/CG under App Builder when used — fine.
- Known quirk: blended engines need ≥2 stores; prefer `morgan-*-search` engines for catalog. No unexpected SKU expected from attach alone.

## Recommendation
1. **Split YES:** ingest+wire first; CG re-gate second. Do **not** combo into one ceiling.
2. **Single Phase I ceiling wording for Eric:**
   > `YES Phase I index-wall ingest+wire ≤ $30 on numista-morgan-pilot Discovery SKUs only (reuse extracts first; Layout Parser only after 50–100 page sample; Adv Answers OFF; attach smithsonian-nnc OK; no Gemini; no catalog fold)`
3. Later (after ingest done + FinOps spot-check):  
   > `YES Phase I-C CG re-gate Option A ≤ $0.50` (19 FAIL; no Adv Answers; fold still HOLD)
4. Phase II burn-order items each need their own YES after re-gate quality OK.

## OOP / alerts
- Expect **$0 net OOP** under App Builder promo if SKUs stay in Vertex AI Search group.
- morgan-pilot budget alert **$350/mo** (alerts only). Phase I ≤$30 is well under.
