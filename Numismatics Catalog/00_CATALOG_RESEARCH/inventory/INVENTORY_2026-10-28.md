# US Numismatics Catalog — On-Box Inventory (2026-10-28)

**Prepared:** Wednesday, 28 Oct 2026 ~7:35 AM ET (America/New_York)  
**Mode:** READ-ONLY. No gcloud creates, no Discovery uploads, no billing changes, no Firebase login, **zero spend**.  
**Audience:** Catalog Research / CoS / FinOps (Eric Seaman / Numista.Ai)  
**Cross-check:** Also see prior `/workspace/roi/catalog_inventory_20261027.md` (Firestore/GCS counts from 26–27 Oct — not re-pulled live today).

---

## BLUF

- **Do not rebuild the Oct-6 evidence packs or the ASE/AWQ mintage CSVs.** Box already has **25 sourced packs / 699 rows / 27 programs** (83% Tier A Mint) plus full ASE (135) and AWQ (100) mintage-sourced coin CSVs. Nothing from those packs has been written to live Firestore.
- **NET-610 Option B is DONE and shows an index wall:** run report confirms **1/20 SUPPORT** (`FG-586-04` Fugio copper weight, score 0.757) / **19 FAIL** because **`morgan-docs` lacks FRASER / BEP / NNP / Smithsonian** passages for currency, Walker/Franklin mintage, medals, and related HOLD rows. **Do not burn more Check Grounding until those sources are ingested** (FinOps cost-check + Eric typed YES first). Run artifacts now on box under `/workspace/catalog-research/net610/` (copies also in `net610-option-b-outs/`); originally laptop `8 OCT 26\MORGAN_PILOT\out\`. Companion FinOps burn plan: `/workspace/catalog-research/BURN_PLAN_FOR_FINOPS_2026-10-28.md`.
- **Catalog fold / production remains HOLD** until Eric types YES (NET-609 NO-FOLD; HOLD 586–590). Sandbox Discovery only.
- **Biggest catalog-feature gaps vs Fugio→2026 + medals ambition:** medals (no evidence pack; 113 Firestore rows cited 26 Oct — do not reinvent), Fugio/early federal (local image seeds only), BEP/currency beyond SemiQ, classic gold/bullion beyond ASE, commemorative *programs* as searchable series, dual-side coin images (~1k image-index sides vs ~5.7k coin rows per 26 Oct inventory).
- **GenAI App Builder credit ~$999.9** on **numista-morgan-pilot** (billing 010E3C). Allowed burn later = Discovery / Check Grounding / Enterprise Search only — never Vertex Gemini, Cloud Run, or non-credit storage if avoidable. **Today’s ask is plan only; spend stays $0 until ceiling YES.**

---

## Existing Discovery Engine assets (numista-morgan-pilot)

| Asset | Type | Notes (from on-box docs; not re-listed live) |
|---|---|---|
| **`morgan-docs`** | Unstructured data store | Created 13 Oct AWQ pilot. Originally **88** docs (Wayback Mint pages + scrubbed packs); later inventory cites **114**. **Missing FRASER/BEP/NNP/SI — root of NET-610 index wall.** |
| **`usmint-site`** | PUBLIC_WEBSITE store | Patterns for AWQ/reports/sales. **Failed:** BasicSiteSearch not attachable; advanced crawl needs domain ownership. Empty / unused. Leave or delete — Eric decision. |
| **`morgan-pilot-search`** | Engine (Enterprise, **no** Adv Gen Answers) | Over `morgan-docs`. Observability OFF. Used for AWQ Check Grounding pilot (48/48 Supported on slot claims; **no mintage figures tested**). |
| **`morgan-factcheck`** | Unstructured store | Layout parser, ~**405–509** docs via `gs://numista-morgan-pilot-factcheck-src/` (AR OCR, verified mintage row docs, packs). |
| **`morgan-factcheck-search`** | Engine (Enterprise + LLM addon) | Primary fact-check engine after 16 Oct. Bank/scripts pointed here (blended detached from scripts). |
| **`smithsonian-nnc`** | Unstructured store | **~54,306** rich US NNC CC0 records imported 16 Oct. Exists, but **not** on the CG path that hit the index wall (`morgan-docs` / fold-gate engine). |
| **`morgan-factcheck-blended`** | Engine | Over `morgan-factcheck` + `smithsonian-nnc`. API will not detach SI (must keep ≥2 stores). Scripts no longer query it by default. |
| Studio **`numista-coin-library`** | Separate project engine | ~5,323 docs (roi inventory) — production search, **not** the App Builder credit sandbox. |

**SKU usage notes (pilots / credit jobs):**
- AWQ pilot (13 Oct): ~122 Enterprise search + 95 Check Grounding calls; list est. ~$0–$6; likely $0 under trial. **No Gemini / Cloud Run / GCS for that run** (inline import).
- Credit jobs (16 Oct): DocAI + Gemini batch ran on **numista-qc** (different pot). morgan-pilot: Enterprise search free-tier / credit; stump bank used blended engine (many 429s then rescored).
- NET-610 Option B (27 Oct evening): AG claimed ~$3.86 list / 540 calls; FinOps BQ export **lagged** at verify — treat list $ as unverified; net OOP historically $0 via App Builder promo when rows land. Soft ceiling was $5.
- **Failed:** live usmint.gov website index; attaching BasicSiteSearch to app.

**Auth note:** ADC file present (`~/.config/gcloud/application_default_credentials.json`, authorized_user). `gcloud` binary not on PATH in this shell. Prior work used `eric@numista.ai`. **Before any future burn:** restore working `gcloud`/ADC for **numista-morgan-pilot** (and FinOps BQ read if reconciling). Firebase login **not** required for Discovery ingest/CG. Live Firestore attach audit would need studio ADC separately and its own Eric YES.

---

## Series coverage table

Row counts = data rows in CSV (header excluded). “Mintage sourced?” = whether this pack/file holds official mintage numbers (packs are mostly **slot/checklist** proposals; mintages live elsewhere).

| Series / program | Pack / path | Approx rows | Mintage sourced? | Gaps |
|---|---|---:|---|---|
| American Innovation $1 | `morgan_db/EVIDENCE_PACK_…_AID_SOURCED.csv` + `/workspace/aid/` | 96 | No (slot fixes); Tier A 95 | 2026 S-proof ended; 2027–32 placeholders; open Eric decisions |
| American Silver Eagles | `…_ASE_SOURCED.csv` + `coins/american_silver_eagles_1986-2026.csv` | 48 pack + **135** coin | **Yes** in coin CSV (135/135 filled) | Gold/Platinum/Palladium/Buffalo bullion **not** in packs |
| America the Beautiful 25¢ | `…_ATB_SOURCED.csv` + `/workspace/atb/` | 80 | Slot/sales; not full year-mint mintage table | Site-name vs Mint wording; W/V75; silver-proof arithmetic |
| American Women Quarters | `…_AWQ_SOURCED.csv` + `coins/american_women_quarters_2022-2025.csv` + `/workspace/awq/` | 48 + **100** coin | **Yes** in coin CSV (100/100); CG pilot Supported 48/48 on slots | Program complete 2022–25; no W unc. |
| Barber dime / half | `…_BARBER_DIME/_HALF_…` | 1 + 1 | Minimal | Barber **quarters** pack missing; almost empty |
| Buffalo nickels | `…_BUFFALO_…` | 15 | Mostly Tier B | Proofs; 3½ Legs; Variety vs Type |
| DC & Territories 25¢ | `…_DC_TERRITORIES_…` | 7 | Slot; Tier A 6 | Accept S-SILVER-PROOF → 24 slots? |
| Flying Eagle / Indian 1¢ | `…_FLYING_EAGLE_INDIAN_…` | 9 | Mostly Tier B | 1856 pattern; Open/Closed 3 |
| Jefferson 5¢ | `…_JEFFERSON_…` | 30 | Slot | 1942 war-nickel naming; 2026 vs America250 |
| Kennedy 50¢ | `…_KENNEDY_…` | 73 | Slot/sales | SMS mint-of-origin; S-SILVER-PROOF labels; 1998 matte; 2014-W gold |
| Liberty V nickels | `…_LIBERTY_V_…` | 1 | Tier B only | Nearly empty |
| Lincoln cents (multi) | LINCOLN_CENTS / MEMORIAL / SHIELD_WHEAT / BICENTENNIAL packs | 33+22+6+9 | Slot | Overlapping program structure; 2025–26 collector cents |
| Morgan dollars | `…_MORGAN_…` | 25 | Partial Tier A/B | 2026 → SemiQ collectibles; variety naming |
| Peace dollars | `…_PEACE_…` | 15 | Partial | Same 2026 SemiQ home |
| Presidential $1 | `…_PRESIDENTIAL_…` | 11 | Slot | Name-on-coin (Garfield/Arthur) |
| U.S. Proof Sets | `…_PROOF_SETS_…` + `/workspace/ps/` | 39 | Slot + AR for early years | Prestige / Limited Edition Silver; 1942 variants; mint-mark era |
| Roosevelt 10¢ | `…_ROOSEVELT_…` | 51 | Slot | No 2026 classic dime (SemiQ) |
| Sacagawea / NA $1 | `…_SACAGAWEA_NA_…` | 17 | Slot | 2014-D EU code; 2025-W gold; Cheerios/Goodacre |
| 2026 SemiQ collectibles | `…_SEMIQ_COLLECTIBLES_…` + `/workspace/sq/` | 13 | Product/slot; Eric accepted candidates → 31 slots | Trump $1 no mint mark label; Morgan/Peace W-EU |
| 2026 SemiQ currency | `…_SEMIQ_CURRENCY_…` | 17 | Slot | Privy quarter mint-mark id; silver composition notes |
| Washington 25¢ classic | `…_WASHINGTON_…` | 32 | Slot | 1965–67 no-mark labels; pre-1968 proofs |
| **Contradictions master** | `morgan_db/contradictions_master.csv` | 71 (66 OPEN) | n/a | Needs Eric/AG before any live write |
| Verified AR mintage rows | `g1/ar/docai_review/verified_mintage_rows.csv` | **1,152** | Yes (AR OCR verified subset) | Coverage ~1797–1965 band; label accuracy caveats |
| Full DocAI mintage extract | `…/full_mintage_rows.csv` | **2,364** | Partial / noisy | Do not trust unlabeled columns |
| Fugio (local seed) | `/workspace/fugio-day1/` | images + wiki JSON | Estimate only in NET-610 pack cites | **No** SOURCED pack; 1 Firestore row cited 26 Oct |
| Chain cent (1793) | `/workspace/chain-cent-day2/` | image/grounding experiment | unknown | Early federal sample only |
| Medals | Brain images (Coolidge silver, Freedom 250 Race); Firestore **113** (26 Oct roi) | — | **No evidence pack** | Eric 27 Oct: medals **IN** scope; do not reinvent 113 |
| BEP / paper currency (broad) | SemiQ currency pack + thin `currency_image_index` (10) per roi | — | No | Grand Watermelon, Porthole, Chief, FRBN vs FRN = NET-610 topics |
| State Quarters / Hawaiian / etc. | Cited DONE in roi “do not redo” | — | In live catalog | Prefer remap GCS before re-scrape |

**PACK_SOURCING_SUMMARY totals:** 25 files, 27 programs, 699 rows, Tier A 580 / B 98 / none 21. **No live write until AG verifies.**

---

## What’s covered vs catalog ambition (plain map)

| Area | Status on box / cited live |
|---|---|
| Circulating by denomination/series (modern) | Strong evidence-pack **slot** coverage for Lincoln/Jefferson/Roosevelt/Washington/Kennedy/Buffalo + commemorative circulating programs (ATB, AWQ, AID, Pres, Sac/NA, SemiQ). Classic Barber/Liberty V nearly empty. |
| Commemoratives (1982– / classic) | Brain registry claims mapped; **no** dedicated SOURCED packs under `morgan_db` for modern commemorative *programs*. |
| ASE / bullion | ASE strong (pack + mintage CSV). Other bullion (AGE, Buffalo, platinum/palladium) = product images in brain inbox, not packs. |
| Proof / mint sets | Proof-sets pack (39); Prestige/Limited Edition open. Uncirculated mint sets thin. |
| Currency (BEP / SemiQ / historic) | SemiQ currency pack only for 2026 redesigns. Historic FRN/SC/LT/Gold Cert = NET-610 claims, **not** indexed in `morgan-docs`. |
| Medals | In scope per Eric 27 Oct. Local: 2 medal product images in brain; Julian/Keusch topic in NET-610 FG-590-20. No medal pack. |
| Territorial | DC & Territories quarters pack (7). US-Philippines 1903–45 = INCLUDE (Eric YES 26 Oct) but gap. |
| Fugio / early federal | `fugio-day1` + `chain-cent-day2` seeds; NET-610 FG-586-*. Not in Discovery CG store. |
| 2025–2026 new releases | SemiQ packs + brain `verified_2026_usmint.json` / product images / Mint live harvest notes. |

---

## Explicit gaps for searchable / scrollable catalog feature

1. **Index wall for grounding:** `morgan-docs` (and the fold-gate CG path) does not contain FRASER Mint AR, BEP fact sheets, Newman Numismatic Portal, or Smithsonian passages for HOLD 586–590 topics → CG fails even with good queries.
2. **No single searchable catalog DB on box** for Fugio→2026 — evidence packs are **checklist deltas**, not the scrollable card store. Live `definitive_reference` (~6,503: 5,770 coin / 620 banknote / 113 medal per 26 Oct) lives in **studio** Firestore — fold HOLD.
3. **Medals program expansion** without duplicating 113 existing rows; need attach audit first.
4. **Dual-side unique coin images** (catalog rule: unique side of that coin) — image index ~1,003 side docs vs thousands of coin rows; Rank-0 “~4,800 missing dual” arithmetic still **UNVERIFIED** without live dump.
5. **Early federal / colonial / CSA paper / pre-1933 gold** thin relative to master registry (~139 programs claimed in brain registry vs packs covering ~27).
6. **66 OPEN contradictions** still blocking confident live writes.
7. **usmint.gov crawl impossible** without domain ownership — must keep Wayback / saved Mint pages / FRASER path.

---

## NET-610 Option B status (artifacts)

| Item | On box? | Path / note |
|---|---|---|
| Evidence pack HOLD 586–590 | Yes | `/workspace/eric-bminus-27oct/net610/CATALOG_EVIDENCE_PACK_HOLD586-590_NET610_2026-10-27.md` (+ `.csv`); copies under `/workspace/roi/` |
| EXECUTE order NET-621 | Yes | `…/NET-621_GROKCOS-to-AGCOS-FINOPS-COS_EXECUTE-NET610-OPTION-B-CG_LIVE.md` |
| FinOps billing verify | Yes | `/workspace/roi/net610_option_b_billing_verify_20261027.md`, `/workspace/net637/FINOPS_BILLING_VERIFY_…` |
| `OPTION_B_RUN_REPORT_NET610.json` | **Yes** | `/workspace/catalog-research/net610/OPTION_B_RUN_REPORT_NET610.json` (dup in `net610-option-b-outs/`; origin laptop `8 OCT 26\MORGAN_PILOT\out\`) |
| `STAGED_OPTION_B_VERIFIED_CORRECTIONS_NET610.csv` | **Yes** | Same dirs; 20 scored + 3 blank-score rows in CSV |
| `EXECUTE_DONE_NET610_OPTION_B_CHECK_GROUNDING.md` | **Yes** | Same dirs; DTG 27 Oct ~8:50 PM ET; list spend **$3.8600** under ≤$5 YES; sandbox only |
| Quality outcome (parsed run report) | Confirmed | **1 SUPPORT / 19 FAIL = index wall**; sole SUPPORT = `FG-586-04` (Fugio Treasury copper weight). Engine refused to hallucinate on unindexed BEP/FRASER topics. |

Related on box: `/workspace/roi/STAGED_MORGAN_CATALOG_ANSWERS_PROOF_NET594.csv` (20 Morgan mintage FAQ rows from Week-1 proofs — different NET).

---

## Index-wall ingest plan (for FinOps cost-check — **do not run yet**)

**Goal:** Put primary passages into a Discovery **unstructured** store the Check Grounding / fold-gate engine can actually retrieve — so a *future* CG re-run of FG-586–590 is not doomed by empty index.  
**Spend today:** $0. **Next burn:** only after FinOps ceiling + Eric typed YES. **No immediate Check Grounding.**

### Sources (priority hierarchy)

| Priority | Source | Doc types | Why (maps to FAIL topics) |
|---|---|---|---|
| 1 | **FRASER** (fraser.stlouisfed.org) + existing AR text | Director of the Mint Annual Reports — mintage tables, footnotes | Walker 548,000; Franklin 2,876,381 Mint-primary; early deliveries |
| 2 | **BEP** / USCurrency.gov | Fact sheets, note-type pages (Treasury Note 1890, Silver Cert, FRBN vs FRN) | FG-588 currency rows |
| 3 | **NNP** (Newman Numismatic Portal / ANS) | Colonial, Fugio, Buell, Crosby extracts, Mint letters | FG-586 Fugio; FG-590-18 mintmark order |
| 4 | **Smithsonian NNC** | Already partially in `smithsonian-nnc` (~54k); local `/workspace/si_oa/nnc_us.jsonl` (~329k lines) | FG-588 note types; medals; object metadata |
| 5 | Saved **U.S. Mint** Wayback / product pages | Specs, press releases (already pattern from AWQ pilot) | SemiQ / modern; never invent mintages |

### How to get into Discovery without a Cloud Storage bill (preferred order)

1. **Inline document import** (same pattern as 13 Oct `morgan-docs` AWQ pilot): POST docs as content — **no new GCS bucket**. Best for curated text extracts (≤ few hundred docs).
2. **Reuse existing bucket** `gs://numista-morgan-pilot-factcheck-src/` only if FinOps confirms Data Index / GCS lines stay credit-covered or $0 — that path already incurred tiny Standard Storage (~$0.000045 day sample). Prefer **not** creating new buckets.
3. **Attach existing `smithsonian-nnc`** to the engine used for CG (or run CG against `morgan-factcheck-blended` / a new engine that includes SI + new FRASER/BEP store). Do **not** re-import 54k SI docs.
4. **Layout Parser / OCR:** only for PDF pages not already in `/workspace/g1/ar` text — Agent Builder SKU group; estimate pages for FinOps; avoid DocAI on **numista-qc** unless separate YES (different credit).

**Storage SKU risk:** New GCS objects → Cloud Storage Standard (often **not** App Builder credit). Inline import + reusing indexed SI avoids that. Data Index byte-seconds on Discovery has been $0 in export so far for morgan-pilot — still watch after large ingest.

### Estimated doc counts (knowable locally; do not invent beyond this)

| Corpus | Knowable count | Suggested ingest slice for index-wall fix |
|---|---|---|
| Local Mint AR `.txt` under `/workspace/g1/ar` | **~45** files | All mintage-relevant sections (many already in `docs_v2` as `ar_mintage_sections__*` = **43**) — ensure they are on the **CG engine’s** store, not only `morgan-factcheck` |
| Verified mintage row docs | **362** `verified_rows__*` in docs_v2 | Already in factcheck path; wire to CG path if missing |
| NET-610 evidence pack + redesigns | 20 claims + cite URLs | Curate **verbatim primary excerpts** as small docs (do not upload whole Wikipedia) |
| BEP / currency fact sheets | unknown until harvest | Target **~20–50** pages covering FG-588-06…10 only first |
| NNP / Crosby / Fugio primary | unknown | Target **~20–40** short extracts for FG-586 |
| Smithsonian | Store **~54,306** already; local US JSONL **~328,998** lines | **Attach store**, don’t re-upload; optionally add **≤100** high-value object cards for HOLD notes |
| Medals (Julian/Keusch / Mint medal pages) | unknown | **~10–30** docs for FG-590-20 after medals attach audit |

Ballpark for a **minimal index-wall repair ingest:** on the order of **100–300 new unstructured docs** (FRASER excerpts already on box + BEP + NNP slices), plus **engine wiring** to SI — not a 50k re-index.

### Recommended order (after YES)

1. FinOps: confirm credit left + approve **ingest-only** ceiling (Discovery Data Index / import; **$0 CG** in this step).  
2. Build curated excerpt set on box (Wayback/FRASER text already local first).  
3. Inline-import into **new** store e.g. `morgan-primary-fraser-bep` **or** append to `morgan-docs` (Eric/CoS choose — appending changes AWQ pilot baseline).  
4. Attach that store + ensure `smithsonian-nnc` is searchable from the **same** engine used for fold-gate CG.  
5. Smoke **Enterprise Search only** (10–20 probe queries, no CG) — confirm hits on Fugio / Franklin AR / BEP fact sheet.  
6. **Only then** propose a small CG re-gate (≤20 HOLD rows) with a hard $ ceiling — separate Eric YES.  
7. Catalog fold still separate YES after SUPPORT quality.

### What NOT to do

- **Do not** run Check Grounding / Adv Gen Answers burns “to see if it’s better” before ingest.  
- **Do not** fold into production / Firestore / Brain without Eric typed YES.  
- **Do not** enable usmint.gov website crawl (will fail ownership).  
- **Do not** call Vertex Gemini / Cloud Run / studio Flash on morgan-pilot for this.  
- **Do not** re-scrape / reinvent State Quarters, Hawaiian, existing 113 medals, or Oct-6 SOURCED packs.  
- **Do not** invent mintages; sales ≠ mintage; Franklin **2,876,381** Mint-primary (not 2,498,181 as Mint-primary).  
- **Do not** create new GCS buckets without FinOps storage-SKU sign-off.  
- **Do not** treat AG list-price $ as billing-verified until Wed Billing chase lands Option B rows.

---

## Recommended next burn batch (Discovery / Check Grounding only) — **gated**

| Step | Action | Spend |
|---|---|---|
| **Now** | This inventory + ingest plan for FinOps | **$0** |
| **Next (needs YES)** | Index-wall ingest (FRASER/BEP/NNP excerpts + engine attach SI) | Ingest/index only — FinOps to price; prefer inline |
| **After smoke PASS + YES** | Optional CG re-run ≤20 HOLD rows | Soft ceiling TBD (prior Option B ≤$5 shape) |
| **Not yet** | Mass AJ checks / burn-order 1+ / catalog fold | HOLD |

---

## Paths to key files

| What | Path |
|---|---|
| **This report** | `/workspace/catalog-research/INVENTORY_2026-10-28.md` |
| Pack sourcing summary | `/workspace/morgan_db/PACK_SOURCING_SUMMARY_2026-10-06.md` |
| Evidence packs | `/workspace/morgan_db/EVIDENCE_PACK_2026-10-06_*_SOURCED.csv` |
| Contradictions | `/workspace/morgan_db/contradictions_master.csv` |
| ASE / AWQ mintage CSVs | `/workspace/morgan_db/coins/` |
| AWQ Vertex pilot summary | `/workspace/morgan_pilot/MORGAN_VERTEX_PILOT_SUMMARY.md` |
| Credit jobs progress / daily log | `/workspace/credit_jobs_progress.md`, `/workspace/credit_jobs_daily_log.md` |
| Factcheck README | `/workspace/morgan_search/README.md` |
| Verified mintage CSV | `/workspace/g1/ar/docai_review/verified_mintage_rows.csv` |
| Brain inbox / zip | `/workspace/brain/inbox/`, `/workspace/brain/numista_brain_inbox.zip` |
| Brain master registry | `/workspace/brain/inbox/3 SEP 2026/Info/US_Mint_BEP_Complete_Official_Programs_Master_Registry.md` |
| Fugio seed | `/workspace/fugio-day1/` |
| NET-610 pack | `/workspace/eric-bminus-27oct/net610/` |
| Prior catalog inventory (26–27 Oct live cites) | `/workspace/roi/catalog_inventory_20261027.md` |
| Agent Builder burn order | `/workspace/roi/agent_builder_burn_recut_20261027.md` |
| Local SI OA US JSONL | `/workspace/si_oa/nnc_us.jsonl` |
| Option B run report / staged CSV / EXECUTE_DONE | `/workspace/catalog-research/net610/` (dup `net610-option-b-outs/`) |
| FinOps burn plan (companion) | `/workspace/catalog-research/BURN_PLAN_FOR_FINOPS_2026-10-28.md` |

---

*No numbers above were invented. Firestore/GCS live counts are cited from 26–27 Oct roi inventory, not re-queried today. Option B quality 1/20 SUPPORT confirmed from on-box `OPTION_B_RUN_REPORT_NET610.json` (sole SUPPORT FG-586-04); artifacts under `/workspace/catalog-research/net610/`.*
