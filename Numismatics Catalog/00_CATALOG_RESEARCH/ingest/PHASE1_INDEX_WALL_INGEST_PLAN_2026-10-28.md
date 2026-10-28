# Phase I — Index-wall ingest + wire (prep for Eric YES)
**Filed:** 28 Oct 2026 ~7:35 AM ET · Catalog Research  
**Local home:** `C:\Users\ericd\Documents\MyVertexProject\Numismatics Catalog\00_CATALOG_RESEARCH\ingest\`  
**Box mirror:** `/workspace/catalog-research/PHASE1_INDEX_WALL_INGEST_PLAN_2026-10-28.md`  
**FinOps cost-check:** CLEARED — `/workspace/roi/burn_plan_phase1_costcheck_20261028.md`  
**Status:** **NO SPEND until Eric typed YES** with ceiling. No catalog/Brain/Firestore fold.

## Eric YES wording (FinOps-cleared)
```
YES Phase I index-wall ingest+wire ≤ $30 on numista-morgan-pilot Discovery SKUs only (reuse extracts first; Layout Parser only after 50–100 page sample; Adv Answers OFF; attach smithsonian-nnc OK; no Gemini; no catalog fold)
```

## Why
NET-610 Option B (27 Oct ~8:51 PM): **1/20 SUPPORT** (FG-586-04 Fugio Treasury weight), **19 FAIL = index wall**.  
`morgan-docs` today ≈ Morgan Dollars / State Quarters / 2026 Mint (Mint-site ingest only). Tight queries cannot invent FRASER/BEP/NNP/Smithsonian passages.

## Non-goals
- No Check Grounding in this YES (that is Phase I-C, separate ≤ $0.50 Option A later)
- No Advanced Generative Answers
- No Vertex Gemini / Cloud Run / Document AI on morgan-pilot
- No growing GCS to burn GFS promo; prefer **inline import** (AWQ pilot pattern)
- No production merge

## Existing assets to reuse first
| Asset | Path / note |
|---|---|
| Mint AR text extracts | GCS `numista-morgan-pilot-factcheck-src` (~74 MB) |
| Local mintage rows | `/workspace/g1` (~1,152 rows, 1797–1965) |
| NET-610 evidence pack | `...\Numismatics Catalog\MORGAN_PILOT\out\` + BATONS HOLD 586–590 pack |
| Option B outs | `MORGAN_PILOT\out\OPTION_B_RUN_REPORT_NET610.json` (+ box `catalog-research/net610-option-b-outs/`) |
| Mint ingest scripts (pattern only) | `MORGAN_PILOT\scripts\ingest_morgan_mint_batch_a.py`, `ingest_state_quarters_batch_b.py` |
| Smithsonian store | Discovery `smithsonian-nnc` (≥50k) — **attach, do not re-ingest** |
| Engines | Prefer `morgan-pilot-search` / `morgan-factcheck-search` (blended needs ≥2 stores) |

## Work packages (execute order after YES)

### WP0 — Preflight (read-only, $0)
1. Confirm `gcloud` project `numista-morgan-pilot`, App Builder promo path.
2. List current `morgan-docs` doc count + engines attached.
3. Confirm `smithsonian-nnc` healthy; note which engines already see it.
4. Inventory `factcheck-src` + `/workspace/g1` coverage vs FAIL rows FG-590-16/17 (Walker 548k, Franklin 2,876,381).

### WP1 — FRASER / Mint Annual Reports → unstructured docs
**Unblocks:** FG-590-16, FG-590-17, FG-590-19 (packaging), parts of FG-589-15  
1. **Reuse** existing Mint AR extracts / g1 text — inline import into `morgan-docs` (or sibling `fraser-mint-ar` store then attach).  
2. Only if gaps remain: Layout Parser on **50–100 page sample** of FRASER PDFs → FinOps spot-check → then bulk under remaining ceiling.  
3. Tag docs with `source=fraser|mint_ar`, year, table refs when known.

### WP2 — BEP / USCurrency / FR Act materials
**Unblocks:** FG-588-06 Watermelon, FG-588-10 FRBN vs FRN  
1. Capture BEP fact sheets + statutory pages cited in NET-610 pack (public HTML/PDF).  
2. Inline import small set (est. handful of docs).  
3. No mass crawl.

### WP3 — NNP / colonial / Fugio authorities
**Unblocks:** FG-586-01..03, FG-586-05, FG-588-09, FG-590-18  
1. Public NNP / ANS / Crosby / Journals of Congress passages cited in evidence pack only.  
2. Rights: public cite extracts; no wholesale site scrape beyond pack URLs.  
3. Inline import.

### WP4 — govinfo / Coinage Acts / US-PH statutes
**Unblocks:** FG-589-11 gold denominations, FG-589-12 fineness, FG-589-13/14 as available  
1. Act of 1792 / 1849 / 1903 / Act 1564 pages from pack URLs.  
2. Inline import.

### WP5 — Smithsonian attach (not re-ingest)
**Unblocks:** FG-588-07 Porthole, FG-588-08 Chief  
1. Attach existing `smithsonian-nnc` to the search engine used for later CG.  
2. Confirm blended-engine quirk handled (≥2 stores if blended).  
3. Est. **$0** incremental.

### WP6 — Wire + smoke (still no CG burn of 19)
1. Adv Answers **OFF**; observability/trace OFF.  
2. 2–3 Enterprise Search smoke queries only (cheap) proving FRASER/BEP/NNP hits return.  
3. Stop. Report doc counts + sample hits to FinOps + CoS.  
4. **Do not** run Phase I-C until separate YES.

## FAIL → source map (19)
| ID | Topic | Primary ingest bucket |
|---|---|---|
| FG-586-01 | Fugio AMERICAN CONGRESS | Journals/Crosby (WP3) |
| FG-586-02 | New Haven / Rust | NNP/Heritage-class cite (WP3) |
| FG-586-03 | Abel Buell | NNP/ANS (WP3) |
| FG-586-05 | Rank-0 image gap / device | Journals Jul 6 1787 (WP3) |
| FG-588-06 | Watermelon 1890 | BEP (WP2) |
| FG-588-07 | Porthole $5 | smithsonian-nnc attach (WP5) |
| FG-588-08 | Chief Running Antelope | smithsonian-nnc attach (WP5) |
| FG-588-09 | Hibernia / 1767 Sou | Crosby/NNP (WP3) |
| FG-588-10 | FRBN vs FRN | FR Act / BEP / FRASER (WP2) |
| FG-589-11 | Gold denominations | govinfo Coinage Acts (WP4) |
| FG-589-12 | US-PH fineness | govinfo 1903 / Act 1564 (WP4) |
| FG-589-13 | Manila M timeline | NNP/ANS Perez (WP3) |
| FG-589-14 | Melecio Figueroa | BSP/public (WP3/4) |
| FG-589-15 | 1793/1794 deliveries | Mint records / FRASER (WP1) |
| FG-590-16 | 1921-S Walker 548,000 | Mint AR 1922 (WP1) |
| FG-590-17 | 1955 Franklin 2,876,381 | Mint AR 1956 (WP1) |
| FG-590-18 | 1917 mintmark order | NARA/NNP (WP3) |
| FG-590-19 | Proof/Mint set packaging | Mint catalogs / AR (WP1) |
| FG-590-20 | National/Assay medals | Julian/Keusch — Tier B; optional late |

**Already SUPPORT (do not re-burn):** FG-586-04 Fugio Treasury weight (0.757).

## Cost ceiling discipline
- Hard ceiling **≤ $30** list on Discovery SKUs.  
- Reuse-first target **$0–15**.  
- Layout Parser only after 50–100 page sample + FinOps ping if sample implies bulk would near ceiling.  
- Stop at 80% of ceiling without new Eric YES.

## Deliverables when DONE (still sandbox)
1. Ingest manifest JSON (doc ids, sources, counts) under `Numismatics Catalog\00_CATALOG_RESEARCH\ingest\`  
2. Engine attach confirmation (smithsonian-nnc + new docs)  
3. Smoke-query log (2–3 hits)  
4. Desk EXECUTE_DONE baton + FinOps actuals note  
5. **Ask** for Phase I-C YES separately (Option A ≤ $0.50)

## Desk baton ask
Please file on BATONS / INBOX / RADIO pointing at this plan + local folder  
`C:\Users\ericd\Documents\MyVertexProject\Numismatics Catalog`  
when Eric YES lands. Catalog Research + Desk execute; FinOps watches SKUs.

## Auth preflight (from 28 Oct inventory pass)
- ADC present as `eric@numista.ai` on the box at inventory time.
- **`gcloud` may be missing from PATH** in some shells — restore CLI / ensure Discovery API access on **numista-morgan-pilot** before WP1 ingest.
- Firebase login **not** required for Discovery ingest.
- Live studio Firestore attach remains a **separate** YES + studio ADC path (not Phase I).
