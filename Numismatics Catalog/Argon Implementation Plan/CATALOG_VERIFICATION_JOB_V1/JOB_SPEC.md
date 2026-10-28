# CATALOG VERIFICATION JOB V1 — Ready for Catalog Research to Approve and Run

**Prepared by:** Argon (AG) · **Date:** 2026-10-28 evening · **Status:** PREPARED — NOT RUN. Nothing in this package has spent credit.
**Branch:** `dev` · **Related:** NET-642 (catalog plan), NET-640 (Catalog Research Phase I), `MORGAN_PILOT\RESTART_PLAN_V1.md`
**Eric's instruction (28 Oct, ~6:53 PM ET):** "prepare an ingestion job for Catalog Research to approve and run."

## 1. Purpose
Turn the catalog's draft facts (mintage, composition, weight/diameter, facility/mint mark) into **verdicted claims** using the existing Search + Check Grounding pipeline on the sandbox, so every published `us_numismatics_catalog` row carries a script-verified Tier-A citation. Also the intended way to use the $1,000 GenAI App Builder credit (expires 23 Jan 2027).

## 2. Facts established tonight (so nobody re-learns them)
| Item | Finding |
|---|---|
| Credit | "Trial credit for GenAI App Builder", $999.88 of $1,000 remaining, net pricing, ends 23 Jan 2027. Eric's understanding: **Vertex AI Search + Agent Builder usage only**. |
| Billing link | `numista-morgan-pilot` and prod `studio-9101802118-8c9a8` are both on billing account `010E3C-D8346A-91A35E` ("Numista.Ai"), the account that holds the credit. |
| Engines (global) | `morgan-pilot-search`, `morgan-pilot-blended`, `morgan-factcheck-search`, `morgan-factcheck-blended` — all Enterprise tier. |
| Data stores | `morgan-docs`, `morgan-factcheck`, `smithsonian-nnc` (NO_CONTENT), `usmint-site` (PUBLIC_WEBSITE, unusable). |
| Answer API | **Not available** — engines lack the LLM add-on (`FAILED_PRECONDITION`). Do NOT enable it (RESTART_PLAN_V1 rule). Use Search + Check Grounding only. |
| Smoke test | 24 Search queries (8 catalog rows x 3 questions) against `morgan-pilot-blended` returned 5 hits each; est. cost ~$0.10, possibly absorbed by the 10,000/month free tier. Raw hits only, not verdicts. |
| Gemini calls | A Gemini token call would likely bill the card, not the credit. **Not used.** |

## 3. Inputs in this package
- `claims_phase1_fixture.csv` — 28 claims generated from the 8 dev-fixture catalog rows (`numista_backend/data/catalog_dev_fixture.json`). Columns: `claim_id, nac_code, field, claim_text, required_source_tier, verdict, citation_quote, source_doc`. The last three are for the runner to fill.
- **The fixture facts are placeholders from the mockup, not verified.** They are claims to be tested; a `Contradicted` verdict is a useful result.
- `required_source_tier` is a first guess; Catalog Research should override per row.

## 4. Proposed batches (sized to existing guardrails)
| Batch | Claims | Source of claims | Notes |
|---|---|---|---|
| **A** | 28 | `claims_phase1_fixture.csv` | Smoke batch. Compare verdicts to the 13 Oct AWQ run (48/48 Supported). |
| **B** | ~25 | `EVIDENCE_PACK_2026-10-06_MORGAN_SOURCED.csv` (already scrubbed) | Same as RESTART_PLAN Batch A/B; no duplicate work if Morgan Batch A already ran. |
| **C** | ~32 + 7 | `..._WASHINGTON_SOURCED.csv` (32 rows), then DC/Territories (7) | Needs extra Mint Wayback uploads for State Quarters pages already in `MORGAN_PILOT\mint_pages_state_quarters\`. |
| **D** | up to ~100 | Phase 1A series list (ASE, ATB, PEACE, AID, etc.) | Needs new Tier-A source pages first (US Mint product pages, Annual Reports). |

Total ~190-200 claims = the existing `QCAP=200` per overnight run. At the **worst-case observed rate** from 13 Oct (~$6.34 / 48 claims ≈ $0.13 per claim), 200 claims ≈ **$26**, i.e. the stated $25 goal, if Check Grounding is the dominant cost. At the best-case rate it is near $0. Real net spend must be read from Billing by SKU after Batch A before scaling.

## 5. Guardrails (inherited, unchanged — Catalog Research owns them)
- Project **only** `numista-morgan-pilot` (`X-Goog-User-Project` + path asserts in `dex.py`). Never `studio-9101802118-8c9a8`.
- `MAXF = 10` facts per Check Grounding call; `QCAP = 200` per run.
- Advanced Generative Answers **OFF**; Grounded Generation **NOT USED**; no Gemini calls.
- Scrub first: no prices, values, PII or collection data in uploaded docs.
- **STOP / kill switch** if Billing shows Cloud Storage, Vertex AI Gemini, Compute or Cloud Run lines (see `COMMANDS_RESTART_V1.md`).
- Source ranking: U.S. Mint / Treasury / BEP beats PCGS / NGC / Wikipedia. Never promote a third-party source over Tier A when Tier A is silent: verdict is `No Mint source`.
- Zero writes to Firestore, the live catalog, or the Flutter app. Verdicts land in CSV files only; Argon imports `Supported` rows later through a separate reviewed step.

## 6. Approval gates (nothing runs until these)
1. **Eric typed YES** for Check Grounding (NET-640 option A) — this was a held item, and the YES in chat on 28 Oct was for "Search and Answer verification", which is not the same thing. A fresh typed YES naming Check Grounding is required.
2. Fold HOLD 586 / 588 / 589 / 590 stays HOLD; this job does not need it lifted.
3. FIN OPS confirms the sandbox budget alert (~$80/week, alert-only).
4. Grok CoS (or Catalog Research) runner: auth is now fresh on the laptop (`gcloud auth login` and ADC both completed 28 Oct ~6:50 PM ET). Grok Bot quota returns ~7:00 AM ET 29 Oct.

## 7. Run steps (for the runner; same as `COMMANDS_RESTART_V1.md`)
1. Sanity: engine and docs exist (step 1 there).
2. `copy rows_catalog_batch_a.py rows.py` after converting `claims_phase1_fixture.csv` to the `rows.py` shape the runner expects (Argon can do this on request once the 13 Oct `rows_awq_48.py` template is available — it is not in this checkout).
3. Probe one query, then run Batch A. Stop. Morning Billing check by SKU.
4. If clean, proceed to B, then C, then D; each batch is its own morning check.

## 8. Success criteria
- Every claim has a verdict: Supported / Contradicted / No Mint source.
- Supported quotes are Check Grounding citations (script-verified), not freehand.
- Billing shows only Discovery Engine / Vertex AI Search SKUs with matching credit lines.
- Output: `RESULTS.csv`, `DETAILS.csv`, `SUMMARY.md` under `MORGAN_PILOT\out\`.

## 9. Open items
- The 13 Oct runner scripts (`setup.py, dex.py, upload.py, engine.py, pilot.py`) are not in this checkout (`MORGAN_PILOT\scripts` is empty except `run\`). They live on the Grok box (`/workspace/morgan_pilot/laptop/`).
- Whether Search-only queries draw from the credit at all (free tier may absorb them): verify with the 29 Oct "Remaining value" figure.

OVER
