# Catalog Research → FIN OPS: Discovery burn plan (cost-check)
**Filed:** 28 Oct 2026 ~7:30 AM ET (America/New_York)  
**Author:** Catalog Research  
**Project:** numista-morgan-pilot only · Billing Numista.Ai 010E3C  
**Credit:** GenAI App Builder ~**$999.88 of $1,000** left (FIN OPS BQ 28 Oct ~7:30 AM ET; promo e87a9b98…; ~$0.119872 Vertex AI Search drawn on morgan-pilot, net OOP $0). Option B Ranking ~$0.092 landed; AG $3.86 SKU math still not fully in export — hard reconcile Wed 28 Oct 1 PM ET. Exp **23 Jan 2027**.  
**Standing:** **Ceiling $0 until Eric typed YES.** No live Firestore/Brain/catalog fold. No Vertex Gemini / Cloud Run / studio-qc Gemini on this credit.

---

## BLUF
1. **Do not run more Check Grounding yet.** NET-610 Option B (27 Oct ~8:51 PM): **1/20 SUPPORT**, **19 FAIL = index wall** (`morgan-docs` lacked the primary passages for FRASER / BEP / NNP / Smithsonian-class cites).
2. **Next spend ask (when Eric YES):** **Phase I — Index-wall unblock (ingest + engine wiring)**, then a **small CG re-gate** of the 19 FAIL rows only.
3. **After that:** resume gap burn order 1→10 from `/workspace/roi/agent_builder_burn_recut_20261027.md` (Fugio first for catalog expansion).
4. **Already held (do not redo):** studio `definitive_reference` **6,503** (5,770 coin / 620 note / 113 medal); Oct-6 evidence packs **699** rows; strong modern series list in inventory. Prefer remapping ~11k GCS blobs over new scrapes (images = Developer/GFS, not this credit).

---

## What already exists (morgan-pilot Discovery)
| Asset | Approx size | Role |
|---|---|---|
| dataStore `morgan-docs` | ~114 docs (pilot era; may be higher post Week-1) | Unstructured; used for AWQ pilot + fold-gate |
| dataStore `morgan-factcheck` | ~439 | Factcheck corpus |
| dataStore `smithsonian-nnc` | ≥50,000 (list truncated) | **Already present** — may need engine attach, not full re-ingest |
| dataStore `usmint-site` | website (empty / not attachable as BasicSiteSearch) | Leave; no crawl without domain ownership |
| engines | `morgan-pilot-search`, `morgan-factcheck-search`, (+ blended quirk) | Use **search** engines for catalog; avoid Google Search grounding ($35/1k) |
| GCS `numista-morgan-pilot-factcheck-src` | ~74 MB Mint AR text extracts | Source material for FRASER/Mint AR path |

Sources for inventory: `/workspace/roi/catalog_inventory_20261027.md`, `roi_report.md`, `agent_builder_credit_plan.md`, NET-610 packs under `/workspace/eric-bminus-27oct/net610/`.

---

## Phase I — Index-wall unblock (PROPOSED next YES)
**Goal:** Put Tier-A passages into the store(s) the CG engine actually searches, so HOLD 586–590 redesigned queries can support.

### I-A. Source ingest (Discovery SKUs only)
| Source | Why (NET-610 FAIL map) | Ingest approach | Est. list $ | Uncertainty |
|---|---|---|---|---|
| **FRASER** Mint Annual Reports / sales figs | FG-590 Walker 548k, Franklin 2,876,381; early mintages | Prefer **inline import** of already-extracted text under `factcheck-src` + `/workspace/g1` (1,152 mintage rows 1797–1965). Layout Parser only for **new** PDF pages not already text-extracted | **~$0–15** if mostly reuse extracts; **up to ~$30** if ~3,000 new Layout Parser pages | Page count for *new* PDFs **TBD** — do not invent; sample 50–100 pp first |
| **BEP** / USCurrency.gov fact sheets | FG-588 currency (Watermelon, Porthole, Chief, FRBN) | HTML/PDF copies → unstructured docs into `morgan-docs` or new `bep-docs` store | **~$1–5** (small set) | Exact page/doc count TBD from evidence-pack URL list |
| **NNP** (Newman Numismatic Portal) | FG-586 Fugio (Buell, Rust, Crosby/Newman); FG-590-18 mintmark order | Public pages / permitted extracts only → unstructured | **~$2–10** | Rights/ToS: public cite only; no mass scrape beyond pack needs |
| **Smithsonian NNC** | FG-588 notes already cite NNC | **Prefer attach existing `smithsonian-nnc` store to CG engine** rather than re-ingest ≥50k | **~$0** attach; query $ only when used | Confirm store still healthy; blended-engine quirk needs ≥2 stores |

**SKU rules for I-A:** Enterprise Search / Layout Parser / OCR-in-SKU-group / Data index (stay under **10 GiB free**). **Avoid** creating billable GCS if inline import works (AWQ pilot pattern). **Never** Gemini on morgan-pilot for this credit.

### I-B. Engine wiring
- Point the fold-gate / catalog CG path at: `morgan-docs` (+ FRASER/BEP/NNP docs) **and** `smithsonian-nnc` (and/or `morgan-factcheck` if Mint AR text already there).
- Do **not** enable Advanced Generative Answers unless FinOps/Eric YES that SKU (drove most of fold-gate $).
- Observability/trace OFF (prior pilot practice).

### I-C. CG re-gate (only after I-A/I-B)
| Item | Detail |
|---|---|
| Rows | 19 FAIL from Option B (+ optional re-check of the 1 SUPPORT) |
| Shape | Prefer **CG + Enterprise search only** (Option A style) unless Eric YES’s fold-gate-with-Adv-Answers again |
| Est. | **Option A:** ~$0–0.10 CG + search within free/low band · **Option B-like:** ~$3.50–$5 (prior YES ceiling) |
| Fold | Still **HOLD** — staged CSV only; Mint-vs-trade caveats (Franklin 2,876,381 vs 2,498,181; Walker 548k vs 542k) need independent Fact Checker agree before any fold ask |

**Proposed ceiling language for Eric (when ready):**  
`YES Phase I index-wall ingest ≤ $X on numista-morgan-pilot Discovery SKUs only`  
then separately:  
`YES Phase I-C CG re-gate ≤ $Y` (recommend start **Option A / no Adv Answers** unless quality needs B).

---

## Phase II — Gap burn order (unchanged; each step own YES)
After Phase I re-gate quality is acceptable (CoS/Fact Checker), resume:

| # | Workstream | Est. list $ |
|---|---|---|
| 1 | Mint/Treasury layout library (remaining pages) | ~$15–30 |
| 2 | Fugio + Confederation | ~$10–20 |
| 3 | Colonial / pre-federal | ~$40–60 |
| 4 | CSA + early federal paper | ~$40–60 |
| 5 | Early federal / pre-1933 gold | ~$60–80 |
| 6 | US-Philippines 1903–45 | ~$25–40 |
| 7 | Thin modern packs (Mercury/Walker/Franklin/Ike/SBA/Barber Q) | ~$30–50 |
| 8 | AJ ~4.5K grounded checks (read-only export) | ~$108 |
| 9–10 | Staged answers / stump / ranking | remainder; buffer ~$19; stop by 22 Jan |

Foreign only after US Fugio→2026 + medal holes done.

---

## Explicit non-goals for this plan
- No production catalog fold / Brain write / deploy  
- No Google Search grounding  
- No Gemini/Flash on morgan-pilot  
- No image download/attach (Developer/GFS)  
- No competing with today’s Mint FAIL-FIX (1MC Hatch 9–10 AM) for daytime AG quota  

---

## Ask of FIN OPS
1. Cost-check Phase I SKU math (especially Layout Parser vs reuse of `factcheck-src`; Data index vs free tier; Adv Answers off by default).  
2. Confirm remaining GenAI App Builder $ after Wed 1 PM reconcile (Week-1 + fold-gate + Option B).  
3. Recommend a **single Phase I ceiling** (ingest-only first vs ingest+CG combo) for Eric YES wording.  
4. Confirm: attaching existing `smithsonian-nnc` does not create unexpected SKUs.

**Catalog Research will not spend until Eric typed YES on a FinOps-cleared ceiling.**

## FIN OPS credit brief lock (28 Oct ~7:30 AM ET)
- **Burn these on morgan-pilot:** Check Grounding Character Count, Ranking, Enterprise Search API, Data Index (App Builder promo).
- **Do not on morgan-pilot for this credit:** Vertex Gemini, Cloud Run, Document AI, studio/numista-qc Gemini.
- **GCS on morgan:** different promo (89b36f30… / GFS-side) — keep incidental; don’t grow storage to burn the wrong pot.
- **Tonight ceiling:** $0 / HOLD until Eric types YES with a $ ceiling. Last YES = NET-610 Option B $5 DONE.
