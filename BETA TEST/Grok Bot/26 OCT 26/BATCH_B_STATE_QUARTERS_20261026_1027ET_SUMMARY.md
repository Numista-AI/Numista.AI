# MORGAN VERTEX PILOT — BATCH B STATE QUARTERS (after Washington/Mint ingest)
**DTG:** 26 Oct 2026 ~10:27 AM ET (America/New_York)
**Runner:** Grok CoS executor (EDS_Laptop). Project **numista-morgan-pilot** only.
**Report only.** No live numista.ai, no Firestore users/coins, no prod studio, no deploy.

## BLUF
Ingested **14** U.S. Mint Wayback State Quarters pages/Excels as source_type=us_mint into morgan-docs (100 → **114** docs). Ran Batch B (12 rows).
**Verdicts: Supported 12 | Unsupported 0 | Contradicted 0 | No Mint source 0.**

## Verdict table
| Row | Slot | Verdict | supportScore | mintF |
|---|---|---|---|---|
| 1 | state_quarters#program_scope | Supported | 0.695458 | 14 |
| 2 | state_quarters#obverse_inscriptions | Supported | 0.815785 | 33 |
| 3 | state_quarters#production_window | Supported | 0.993596 | 14 |
| 4 | state_quarters_1999#Delaware | Supported | 0.973199 | 9 |
| 5 | state_quarters_1999#Connecticut | Supported | 0.902419 | 9 |
| 6 | state_quarters_2000#Virginia | Supported | 0.962844 | 9 |
| 7 | state_quarters#facilities_PD | Supported | 0.871174 | 9 |
| 8 | state_quarters_2008#order | Supported | 0.646154 | 13 |
| 9 | state_quarters_2008#Oklahoma | Supported | 0.962651 | 9 |
| 10 | state_quarters_1999#order | Supported | 0.884402 | 12 |
| 11 | state_quarters_2002#Mississippi | Supported | 0.971355 | 9 |
| 12 | state_quarters#2009_territories_followon | Supported | 0.66667 | 11 |

## Counts
| Verdict | N |
|---|---|
| Supported | 12 |
| Unsupported | 0 |
| Contradicted | 0 |
| No Mint source | 0 |

## Ingest (14 docs)
- page-stateq-50sq_designs_201002 — U.S. Mint 50 State Quarters Program — designs by year
  - https://web.archive.org/web/20100204054242/http://www.usmint.gov/mint_programs/50sq_program/?action=designs_50sq
- page-stateq-50sq_learn_201807 — 50 State Quarters Program (U.S. Mint learn page)
  - https://web.archive.org/web/20180705203015/https://www.usmint.gov/learn/coin-and-medal-programs/50-state-quarters
- page-stateq-50sq_schedule_200901 — 50 State Quarters Program release schedule
  - https://web.archive.org/web/20090101120000/http://www.usmint.gov/mint_programs/50sq_program/?action=schedule
- page-stateq-coin_production_index_201210 — U.S. Mint Coin Production Figures index (links 50 State Quarters 1999-2008)
  - https://web.archive.org/web/20121011075339/http://www.usmint.gov/about_the_mint/coin_production/index.cfm?action=production_figures&allCoinsYear=2012
- page-stateq-prod_excel_1999 — 1999 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063656id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/1999_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2000 — 2000 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063635id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2000_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2001 — 2001 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063809id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2001_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2002 — 2002 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063904id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2002_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2003 — 2003 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063820id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2003_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2004 — 2004 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063833id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2004_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2005 — 2005 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063815id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2005_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2006 — 2006 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063627id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2006_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2007 — 2007 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063643id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2007_50_State_Quarters_Program_Production.xls
- page-stateq-prod_excel_2008 — 2008 50 State Quarters Program Production (U.S. Mint Excel)
  - https://web.archive.org/web/20121021063920id_/http://www.usmint.gov/about_the_mint/coin_production/Excels/2008_50_State_Quarters_Program_Production.xls

## Usage (this batch)
| Item | Value |
|---|---|
| Search queries | 24 |
| Check Grounding calls | 24 |
| Fact chars sent | 316446 |
| MAXF | 10 |
| Docs in morgan-docs | 114 |

## Optional note (Morgan Batch A)
Rows 5 & 11 from Morgan Batch A rerun remain Unsupported (2024 S-proof; 2026 America250) — not blocking; not rechecked this run.

## Files
- MORGAN_PILOT/out/BATCH_B_STATE_QUARTERS_20261026_1027ET_RESULTS.csv
- MORGAN_PILOT/out/BATCH_B_STATE_QUARTERS_20261026_1027ET_DETAILS.csv
- MORGAN_PILOT/out/BATCH_B_STATE_QUARTERS_20261026_1027ET_SUMMARY.md
- MORGAN_PILOT/out/STATE_QUARTERS_MINT_INGEST_MANIFEST.json
- Raw row JSON: MORGAN_PILOT/scripts/run/row01.json … row12.json

## Hard rules honored
numista-morgan-pilot ONLY. No Advanced Answers / Grounded Generation. No prod studio writes. No users/{uid}/coins. No live deploy. Official/archived Mint pages + Mint production Excels only. Mint tier only as evidence (morgan_pack excluded).

OVER
