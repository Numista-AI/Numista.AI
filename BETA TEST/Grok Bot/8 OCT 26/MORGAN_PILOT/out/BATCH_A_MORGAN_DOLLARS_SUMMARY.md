# MORGAN VERTEX PILOT — BATCH A RESULTS (Morgan dollars)
**DTG:** 26 Oct 2026 ~9:47 AM ET (America/New_York)
**Runner:** Grok CoS executor (EDS_Laptop). Project **numista-morgan-pilot** only.
**Report only.** No live numista.ai, no Firestore users/coins, no prod studio-9101802118-8c9a8, no deploy.

## BLUF
Batch A ran after Eric AUTH_OK. **12/12 claims completed.** Engine + datastore probe OK (88 docs, Enterprise, Advanced Answers OFF).
**Verdicts: Supported 0 | Unsupported 9 | No Mint source 3.**

Root cause (expected from RESTART_PLAN): datastore `morgan-docs` still holds the **13 Oct AWQ Mint Wayback pages**, not Morgan-dollar product pages. `morgan_pack` CSV rows (including MORGAN_SOURCED) are loaded for context but **excluded as evidence** by design. Search therefore returns AWQ Mint passages for Morgan queries; Check Grounding correctly refuses citations (support scores 0.002-0.50, no citationIndices).

Credit was still burned on Discovery Engine Search + Check Grounding (Agent Builder path). **No deploy required or performed.**

## Verdict table
| Row | Slot | Verdict | supportScore | mintF |
|---|---|---|---|---|
| 1 | morgan_dollars_2023_s_2023#S | Unsupported | 0.029741 | 21 |
| 2 | morgan_dollars_2021_o_privy_2021#O-Privy | No Mint source |  | 0 |
| 3 | morgan_dollars_2021_cc_privy_2021#CC-Privy | No Mint source |  | 0 |
| 4 | NEW:morgan_dollars_2024#P | Unsupported | 0.043797 | 23 |
| 5 | NEW:morgan_dollars_2024#S-SILVER-PROOF | Unsupported | 0.498971 | 12 |
| 6 | NEW:morgan_dollars_2024#S-REVERSE-PROOF | Unsupported | 0.006031 | 11 |
| 7 | NEW:morgan_dollars_2025#P | Unsupported | 0.002465 | 3 |
| 8 | NEW:morgan_dollars_2025#S-SILVER-PROOF | Unsupported | 0.043789 | 13 |
| 9 | NEW:morgan_dollars_2025#S-REVERSE-PROOF | Unsupported | 0.015452 | 13 |
| 10 | ADDED:morgan_dollars_2023_s_reverse_proof_2023#S-Revers | Unsupported | 0.00589 | 13 |
| 11 | ADDED:morgan_dollars_2026 (scope check) | No Mint source |  | 0 |
| 12 | ADDED:program#mint_mark_locations | Unsupported | 0.034014 | 10 |

## Counts
| Verdict | N |
|---|---|
| Supported | 0 |
| Unsupported (Mint facts retrieved, no citation match) | 9 |
| No Mint source | 3 |

No Mint source rows: **2** (2021 O-Privy), **3** (2021 CC-Privy), **11** (2026 America250 scope).

## Usage (this run)
| Item | Value |
|---|---|
| Search queries | 24 (2 per claim x 12; under QCAP=200) |
| Check Grounding calls | 10 |
| Fact chars sent | 206578 |
| MAXF | 10 |
| Probe | engine 200; docs 88; probe_search 5 hits (AWQ-topic) |

Est. list cost: small (Enterprise queries + grounding chars). **Morning Billing Reports project numista-morgan-pilot Group by SKU** (FIN OPS). Kill switch if Cloud Storage / Gemini / Compute / Cloud Run appear.

## Auth
- Active account: `eric@numista.ai` — gcloud auth print-access-token OK (scripts use user token via dex.py).
- Default gcloud project left as `studio-9101802118-8c9a8` (untouched); all API calls pinned to pilot via path + X-Goog-User-Project.
- ADC (application-default) still fails reauth non-interactively — not required for this pilot runner.

## Next (credit burn continues)
1. **Upload Morgan-dollar Mint Wayback / product pages** as source_type=us_mint (incremental import; no bucket) — 2021 privy, 2023-2025 proof/unc/reverse-proof, 2026 America250, historic mint-mark pages. Then re-run Batch A.
2. Batch B Red Book/VAM (expect many Needs Mint source) — optional under weekly ~$80 guardrail.
3. After Morgan dollars green: **State Quarters / Washington** pack.

## Files
- MORGAN_PILOT/out/BATCH_A_MORGAN_DOLLARS_RESULTS.csv
- MORGAN_PILOT/out/BATCH_A_MORGAN_DOLLARS_DETAILS.csv
- MORGAN_PILOT/out/BATCH_A_MORGAN_DOLLARS_SUMMARY.md (this file)
- Raw row JSON: MORGAN_PILOT/scripts/run/row01.json … row12.json
- Copy: 26 OCT 26/MORGAN_BATCH_A_*

## Hard rules honored
No Advanced Answers, no Grounded Generation, no prod project calls, no Firestore writes, no main/live deploy. Eric: **no Deploy needed** for this pilot.

OVER
