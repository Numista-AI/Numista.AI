# Catalog + image inventory brief — do not duplicate before Agent Builder spend

**Filed:** 27 Oct 2026 ~10:25 AM ET (America/New_York)  
**Mode:** READ-ONLY synthesis of local `/workspace` artifacts. No APIs enabled, no deletes/deploys/purchases, no paid calls.  
**Eric order (27 Oct):** US (current + former territories/states) coins, currency, medals with images, Fugio→2026; spend ~$999.98 Agent Builder on that first; foreign only if credit remains; **do not duplicate** what is already in Google Cloud buckets. Medals are **in scope** (27 Oct supersedes older “no medals / medals last only” sprint posture for *future* gap-fill — existing 113 medal rows still must not be reinvented).

---

## Answer first

### What we already have (newest live catalog read = **26 Oct 2026 evening ET**, not re-pulled live today)

| Store | Project | Count | Notes / date |
|---|---|---|---|
| Firestore `definitive_reference` | **studio** | **6,503** docs | **coin 5,770 / banknote 620 / medal 113**; ~100 series; years ~1737–2030. Source: `/workspace/roi/roi_report.md` catalog section (26 Oct evening). **Not re-counted from a local dump today.** |
| Firestore `coins_reference` | studio | 6,302 | Near-mirror of definitive |
| Firestore `coin_image_index` | studio | **1,003** | Obverse-heavy (**601 obv / 404 rev**). Local CSV mirror `/workspace/qc_slot/src/_scripts/image_index_full.csv` = **1,005** rows / **1,003** unique `doc_key` — these are **per-side image docs**, not proven dual-matched coin pairs |
| Firestore `currency_image_index` | studio | **10** | Thin: CSA T-64/T-66, FR 226/237, FR 91 error, fractional FR 1226 |
| Firestore `reference_library` | studio | 6,019 | Image metadata |
| Firestore `global_programs` | studio | **34** | Modern circulating + ASE/proofs; **no** colonial/CSA program docs |
| Firestore `brain_knowledge_base` | studio | 1,876 | RAG chunks |
| Discovery Research Bot | **numista-morgan-pilot** | 3 engines | dataStores: morgan-docs 114, morgan-factcheck 439, smithsonian-nnc ≥50k (list truncated), usmint-site |
| Discovery Numista Coin Search | studio | 1 engine | `numista-coin-library` **5,323** docs |

**Biggest gaps (catalog rows / series skeleton — from 26 Oct inventory + 26–27 Oct gap plans):**

1. **Fugio / Confederation** — only **1** `definitive_reference` row (under Pattern Coinage); local seed exists at `/workspace/fugio-day1` (18 files, including sundial/rings images).  
2. **Pre-Federal & colonial empires** — ~**34** pre-federal rows; British/French/Spanish colonial nearly empty; Continental Currency ~8.  
3. **CSA + early federal paper** — `currency_image_index` = 10; CSA keyword hits ~9 inside Obsolete Banknotes; dedicated federal note families not built out.  
4. **Early federal coin types** — sparse counts cited 26 Oct: Flowing Hair 10, Capped Bust 7, Seated Liberty 33, Standing Liberty Quarters 2, Shield Nickels 2; half cents / large cents fragmented; pre-1933 gold thin.  
5. **Image attach on existing holdings** — ~1,003 coin image-index entries vs ~5,770 coin catalog rows; many empty design fields. See Rank-0 note below.

**Image coverage (local corroboration vs live claim):**

| Claim (26 Oct / Rank-0 drafts) | Local file check (27 Oct) | Verdict |
|---|---|---|
| ~1,000 matched obverse/reverse | `image_index_full.csv` ≈ 1,005 **side** rows (601 obv / 404 rev) | **Cannot** treat as ~1,000 dual-matched coins |
| ~4,800 rows lack dual-sided verified images | Arithmetic 5,770 − ~1,000 ≈ 4,770–4,800 appears only in narrative drafts | **UNVERIFIED** — Morgan FACTCHECK 27 Oct explicitly flags this; **no** `definitive_reference` dump under `/workspace/morgan_db` to recount |
| GCS reference + uploads images exist | `gcs_full_inventory.csv` (**dated 23 Oct 2026**) = **11,069** objects | Real blob inventory; **not** the same as “attached to catalog rows” |

**Medals:** 113 in `definitive_reference` (draft Rank-7 also cites **68 Congressional / 43 Presidential**). Split **UNVERIFIED** locally (same FinOps pull needed). Eric 27 Oct: medals remain in scope for the full US DB ambition; **do not reinvent** the 113 already held — expand only after a live attach audit flags real holes.

**Philippines:** INCLUDE under US administration 1903–1945 (Eric YES 26 Oct); post-1946 Republic OUT. Still a gap-fill target (Rank 5), not a “DONE” holding.

---

## Bucket / project names found in files (do not invent)

### GCP projects named in artifacts
- **studio** (Firestore catalog + most GCS + Discovery coin search) — `/workspace/roi/roi_report.md`
- **numista-morgan-pilot** (Agent Builder / Research Bot / factcheck src) — roi_report + `/workspace/roi/agent_builder_credit_plan.md`
- **numista-qc** (Developer / Flash / DocAI Mint AR) — roi_report; **different credit pot**

### GCS buckets named in `gcs_full_inventory.csv` (23 Oct) and/or roi_report (26 Oct)
| Bucket | Source | Snapshot notes |
|---|---|---|
| `numista-reference-library` | inventory CSV + roi_report | CSV: **6,817** objects (6,600 “Reference Library” + 217 Presidential $1). Path prefixes: `reference_library/wikimedia_uscoin` 2274, `rare_uscoin` 2202, `balabaskar_coins` 1444, `bulk_programs` 858, `2026_series` 25 |
| `numista-uploads-studio-9101802118-8c9a8` | inventory CSV + roi_report | CSV: **4,252** objects (unclassified images 3167, user coin 483, user currency 483, docs 88, …). Roi: ~8.32 GB |
| `us_mint_coin_images` | roi_report only | ~554 MB / ~454 objs (mostly 2026 Mint product shots) — **not** in the 23 Oct CSV |
| `coin_paper_currency_test` | roi_report | **empty (0)** |
| `numista-morgan-pilot-factcheck-src` | roi_report | ~74 MB Mint Annual Report text extracts (morgan-pilot) |

### Other named stores (not GCS buckets)
- Firestore collections listed in the table above  
- Discovery dataStores: `morgan-docs`, `morgan-factcheck`, `smithsonian-nnc`, `usmint-site`, `numista-coin-library`  
- Cloud SQL `numista-coin-db` / DB `numista_data` — **row counts not read** (ACL = Eric home IP only)  
- Local: `/workspace/g1` mintage CSVs (1,152 rows, 1797–1965); `/workspace/morgan_db` evidence packs (~699 sourced rows); `/workspace/fugio-day1`

---

## Explicit “do not redo” list

From `RECONCILED_TONIGHT_2026-10-26.md` + priority checklist + roi_report (strong holdings / DONE posture):

**Programs / series already strong — do not re-scaffold or re-scrape as if empty:**
- Washington · Lincoln · Jefferson · Roosevelt · Buffalo · AID (American Innovation)  
- ASE · Morgan · Presidential + Sacagawea/NA (Pres-SAC)  
- **Fifty State Quarters (A6) — DONE**  
- OTB/ATB · Modern + classic commemoratives (as held) · Patterns (as held)  
- Obsolete notes slice (as held) · **Hawaiian Kingdom (H1) — DONE**  
- Medals holdings already in catalog (**113**) — do not invent duplicate Cong/Pres rows; expand only if live FinOps flags holes  
- `global_programs` (34) already listed in checklist — AID, ASE, ATB, AWQ, Barber (D/H/Q), Buffalo, DC/Territories, Eisenhower, 50 State, Flying Eagle/Indian, Franklin, Jefferson, Kennedy, Liberty V, Walking Liberty, Lincoln (wheat/memorial/shield/bicentennial), Mercury, Morgan, Peace, Presidential, Roosevelt, Sacagawea/NA, SBA, Proof sets, Washington classic, SemiQ currency + collectibles  

**Also leave untouched until evidence-pack / variety work (not empty-series rebuild):**
- Evidence packs already under `/workspace/morgan_db` for the Oct-6 SOURCED modern programs  
- Existing GCS blobs in `numista-reference-library` and uploads — **prefer attach/remap before new scrapes** (Eric: review every coin/note/medal already in buckets)

**Parked / out of scope for this credit burn:**
- Full National Bank Note charter census · full Judd patterns · private / Civil War tokens  
- Post-1946 Philippine Republic  
- Live Firestore / Brain / deploy (still OFF until Eric/CoS authorize)

---

## Gaps → Agent Builder credit vs Developer / GFS

**Credit reality** (`agent_builder_credit_plan.md`, console ~10:08 AM ET 27 Oct): **~$999.98** left of $1,000 GenAI App Builder trial on billing account Numista.Ai / project **numista-morgan-pilot**, expires **23 Jan 2027**. Covers **Vertex AI Search & Conversation / Discovery / Agent Search SKUs only** (queries, layout parser, OCR-for-Doc-Understanding in that SKU group, ranking, grounded generation on *own* data). Does **not** cover plain Gemini/Flash, standalone Document AI outside that path, Cloud Storage, or image generation.

| Work | Who pays | Why |
|---|---|---|
| Mint/Treasury PDF library (layout parser + OCR) for mintages / type facts | **Agent Builder** (morgan-pilot) | Layout Parser / OCR SKUs in credit group |
| Catalog verification queries (mintage, specs, image *source* attribution) via Research Bot / Enterprise search | **Agent Builder** | Search query SKUs |
| Gap research for Fugio, colonial empires, CSA/federal paper type sets, early federal types, US-Philippines 1903–45, thin evidence packs (Mercury, Walker, Franklin, Ike, SBA, Barber Q) | **Agent Builder** | Discover + verify against Mint/Treasury/primary docs; staged drafts only |
| Staged Morgan descriptions / FAQ per catalog item (sandbox CSV, no live write) | **Agent Builder** | Search answer calls |
| **Image download, generation, Gemini vision, Flash labeling, bucket upload, Firestore attach** | **Developer / GFS (numista-qc / studio)** — **not** Agent Builder | Outside credit SKU group |
| Prefer existing GCS before new image acquisition | Ops / GFS | Eric no-duplicate rule; ~6.8k ref-lib + ~4.2k uploads objects already present (23 Oct CSV) |

**27 Oct standing order:** burn every Agent Builder dollar on US catalog gap verify/parse **before** foreign. Foreign only if credit remains after US Fugio→2026 coins/notes/medals work. Nothing runs without Eric typed YES (first gate historically: `YES proof runs` ~$5).

---

## Rank-0 ~4,800 image-gap — can local files alone confirm it?

### **No.**

- Live `definitive_reference` **6,503 / 5,770 / 620 / 113** and `coin_image_index` **1,003** come from the **26 Oct evening FinOps console/Firestore read** recorded in `roi_report.md` — there is **no** full `definitive_reference` JSON/CSV dump under `/workspace/morgan_db` to re-tally today.  
- Local `image_index_full.csv` confirms ~**1,005 side-level** image docs, **not** “~1,000 coins with both sides verified.”  
- `backup_coins_13aug2026.json` = **4,992** coin-ish rows (12 Aug 2026) — different snapshot; **not** proof of 5,770 or of a 4,800 gap.  
- Morgan `FACTCHECK_NET581_RANK0_RANK1_2026-10-27.md` and `EOD_UNRESOLVED_NET581_2026-10-27.md` both mark **~4,800 UNVERIFIED** and ask FinOps for a live image-attachment pull before any public/museum narrative.  
- Do **not** use ~4,800 in spend or marketing copy until that live pull.

Rough *narrative* arithmetic (5,770 − ~1,000 ≈ 4,770) is how the draft got the number; it is **not** a verified dual-side attach census.

---

## Overnight / NET notes (local)

- Primary overnight gap program on disk: **NET-581** drafts + factchecks under `/workspace/morgan_db/audit/gap_plans/` (26–27 Oct). Ranks 0–7 fact-checked **PASS WITH CORRECTIONS**; **Merge HOLD**; catalog/Brain OFF.  
- **No `NET-566` artifact** found under `/workspace` (maxdepth search 27 Oct).  
- `/workspace/mint-gap/` (23 Oct) is Flutter/Mint-releases scraper code, **not** a catalog row inventory.  
- User-collection image gaps (`jseaman_image_gaps.csv`, 4,048 rows) and `currency_gaps_for_grok.csv` (226 user-currency missing OBV/REV) are **user holdings**, not the master `definitive_reference` gap list — do not confuse with catalog build work.

---

## Sources (newest preferred)

| File | Date | Role |
|---|---|---|
| `/workspace/roi/roi_report.md` § Catalog inventory | 26 Oct evening | Live Firestore/GCS/Discovery counts |
| `/workspace/morgan_db/audit/gap_plans/RECONCILED_TONIGHT_2026-10-26.md` | 26 Oct ~18:00 | DONE vs gap ranks |
| `/workspace/morgan_db/audit/gap_plans/PRIORITY_GAP_CHECKLIST_FUGIO_TO_2026_2026-10-26.md` | 26 Oct | Full Fugio→2026 checklist |
| `/workspace/morgan_db/audit/gap_plans/FACTCHECK_NET581_RANK0_RANK1_2026-10-27.md` | 27 Oct ~10:15 | Rank-0 counts **UNVERIFIED** |
| `/workspace/morgan_db/audit/gap_plans/EOD_UNRESOLVED_NET581_2026-10-27.md` | 27 Oct ~10:20 | Blocking FinOps re-pull |
| `/workspace/img474/app/gcs_full_inventory.csv` | **23 Oct** | Bucket object inventory (stale vs 26 Oct live sizes) |
| `/workspace/qc_slot/src/_scripts/image_index_full.csv` | local mirror | 1,005 side image rows |
| `/workspace/roi/agent_builder_credit_plan.md` | refreshed 27 Oct | Credit SKU boundary |

---

## Status

Brief ready for CoS / Eric. **No spend, no enable, no deploy.** Next useful FinOps action (needs Eric/console or gcloud): live `definitive_reference` image-attachment recount + medals 68/43 split verify before treating Rank-0 ~4,800 as fact.
