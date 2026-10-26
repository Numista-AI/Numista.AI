# MORGAN VERTEX PILOT — BATCH A RERUN (after Morgan Mint ingest)
**DTG:** 26 Oct 2026 ~10:07 AM ET (America/New_York)
**Runner:** Grok CoS executor (EDS_Laptop). Project **numista-morgan-pilot** only.
**Report only.** No live numista.ai, no Firestore users/coins, no prod studio, no deploy.

## BLUF
Ingested **12** U.S. Mint Wayback product/press pages as source_type=us_mint into morgan-docs (88 → **100** docs). Re-ran Batch A (12 rows).
**Verdicts: Supported 10 | Unsupported 2 | Contradicted 0 | No Mint source 0.**
Prior run (AWQ-only corpus): Supported 0 / Unsupported 9 / No Mint 3. Credit burned via Search + Check Grounding only.

## Verdict table
| Row | Slot | Verdict | supportScore | mintF |
|---|---|---|---|---|
| 1 | morgan_dollars_2023_s_2023#S | Supported | 0.974827 | 39 |
| 2 | morgan_dollars_2021_o_privy_2021#O-Privy | Supported | 0.797093 | 29 |
| 3 | morgan_dollars_2021_cc_privy_2021#CC-Privy | Supported | 0.764283 | 28 |
| 4 | NEW:morgan_dollars_2024#P | Supported | 0.982496 | 34 |
| 5 | NEW:morgan_dollars_2024#S-SILVER-PROOF | Unsupported | 0.486145 | 35 |
| 6 | NEW:morgan_dollars_2024#S-REVERSE-PROOF | Supported | 0.992043 | 29 |
| 7 | NEW:morgan_dollars_2025#P | Supported | 0.991714 | 38 |
| 8 | NEW:morgan_dollars_2025#S-SILVER-PROOF | Supported | 0.816612 | 29 |
| 9 | NEW:morgan_dollars_2025#S-REVERSE-PROOF | Supported | 0.985320 | 28 |
| 10 | ADDED:morgan_dollars_2023_s_reverse_proof_2023#S-Reverse-Proof | Supported | 0.978430 | 23 |
| 11 | ADDED:morgan_dollars_2026 (scope check) | Unsupported | 0.540807 | 29 |
| 12 | ADDED:program#mint_mark_locations | Supported | 0.687988 | 41 |

## Counts
| Verdict | N |
|---|---|
| Supported | 10 |
| Unsupported | 2 |
| Contradicted | 0 |
| No Mint source | 0 |

## Remaining gaps (Unsupported)
- **Row 5** NEW:morgan_dollars_2024#S-SILVER-PROOF score=0.48614514 — Mint facts retrieved but Check Grounding did not cite (threshold 0.6 / citationIndices). Claim may need tighter wording or a more specific product page.
- **Row 11** ADDED:morgan_dollars_2026 (scope check) score=0.5408074 — Mint facts retrieved but Check Grounding did not cite (threshold 0.6 / citationIndices). Claim may need tighter wording or a more specific product page.

## Ingest (12 URLs)
- page-morgan-2023_morgan_peace_proof_press — United States Mint Opens Sales for the 2023 Morgan and Peace Proof Silver Dollars
  - https://web.archive.org/web/20230810134920/https://www.usmint.gov/news/press-releases/united-states-mint-opens-sales-for-the-2023-morgan-and-peace-proof-silver-dollars-on-august-9
- page-morgan-2021_morgan_dollar_program — 2021 Morgan Dollar (program page)
  - https://web.archive.org/web/20210709183332/https://www.usmint.gov/coins/coin-medal-programs/morgan-peace-dollar-anniversary-coins/2021-morgan-dollar
- page-morgan-2021_morgan_peace_preorder_press — United States Mint Offering 2021 Morgan and Peace Dollars in Three Pre-Order Windows
  - https://web.archive.org/web/20210525060415/https://www.usmint.gov/news/press-releases/united-states-mint-offering-2021-morgan-and-peace-dollars-in-three-pre-order-windows
- page-morgan-2024_morgan_peace_unc_press — United States Mint Opens Sales for the 2024 Morgan and Peace Uncirculated Silver Dollars
  - https://web.archive.org/web/20240713042030/https://www.usmint.gov/news/press-releases/united-states-mint-opens-sales-for-the-2024-morgan-and-peace-uncirculated-silver-dollars-on-july-11
- page-morgan-2024_morgan_peace_program_landing — Morgan and Peace Silver Dollar Coins (program landing)
  - https://web.archive.org/web/20261004090710/https://www.usmint.gov/coins/coin-programs/morgan-and-peace-silver-dollar-coins/
- page-morgan-2024_morgan_peace_reverse_proof_press — 2024 Morgan and Peace Dollar Reverse Proof Two-Coin Set Now Available
  - https://web.archive.org/web/20241206144121/https://www.usmint.gov/news/press-releases/united-states-mint-2024-morgan-and-peace-dollar-reverse-proof-two-coin-set-now-available
- page-morgan-2025_morgan_peace_unc_press — 2025 Morgan and Peace Uncirculated Silver Dollars Available
  - https://web.archive.org/web/20250907103931/https://www.usmint.gov/news/press-releases/2025-morgan-and-peace-uncirculated-silver-dollars-available-on-july-10
- page-morgan-2025_morgan_peace_proof_press — 2025 Morgan and Peace Dollar Proof Coins Available
  - https://web.archive.org/web/20250906083100/https://www.usmint.gov/news/press-releases/2025-morgan-and-peace-dollar-proof-coins-available-on-september-11
- page-morgan-2025_morgan_peace_reverse_proof_press — Morgan and Peace Dollar 2025 Reverse Proof Two-Coin Set Available
  - https://web.archive.org/web/20251218150313/https://www.usmint.gov/news/press-releases/morgan-and-peace-dollar-2025-reverse-proof-two-coin-set-available-on-december-11
- page-morgan-2023_morgan_peace_reverse_proof_press — 2023 Morgan & Peace Dollar Reverse Proof Two-Coin Set (S) Available
  - https://web.archive.org/web/20231110005655/https://www.usmint.gov/news/press-releases/2023-morgan-peace-dollar-reverse-proof-two-coin-set-s-available-november-9-at-noon
- page-morgan-2026_morgan_enhanced_unc_26XE — Morgan Silver Dollar 2026 Enhanced Uncirculated Coin (26XE)
  - https://web.archive.org/web/20261004090713/https://www.usmint.gov/morgan-silver-dollar-2026-enhanced-uncirculated-coin-26XE.html
- page-morgan-historic_coin_production_facilities — Historic Coin Production Facilities (mint marks)
  - https://web.archive.org/web/20210424145952/https://www.usmint.gov/learn/history/historic-coin-production

## Usage (this rerun)
| Item | Value |
|---|---|
| Search queries | 24 |
| Check Grounding calls | 16 |
| Fact chars sent | 342652 |
| MAXF | 10 |
| Docs in morgan-docs | 100 |

## State Quarters readiness
**Conditional YES.** Morgan Batch A is largely green (10/12 Supported). Safe to start State Quarters / Washington Mint-page ingest + Batch under the same ~/wk alert, while optionally patching rows 5 and 11 (2024 S-proof mintage wording; 2026 America250 claim) with better product pages / claim trim. Do **not** wait on perfect 12/12 to burn Agent Builder credit on the next pack.

## Files
- MORGAN_PILOT/out/BATCH_A_RERUN_20261026_1007ET_RESULTS.csv
- MORGAN_PILOT/out/BATCH_A_RERUN_20261026_1007ET_DETAILS.csv
- MORGAN_PILOT/out/BATCH_A_RERUN_20261026_1007ET_SUMMARY.md (this file)
- MORGAN_PILOT/out/MORGAN_MINT_INGEST_MANIFEST.json
- Raw row JSON: MORGAN_PILOT/scripts/run/row01.json … row12.json
- First run preserved: MORGAN_PILOT/out/run_BATCH_A_FIRST_20261026/

## Hard rules honored
numista-morgan-pilot ONLY. No Advanced Answers / Grounded Generation. No prod studio writes. No users/{uid}/coins. No live deploy. Official/archived Mint pages only (no medals). Mint tier only as evidence (morgan_pack excluded).

OVER
