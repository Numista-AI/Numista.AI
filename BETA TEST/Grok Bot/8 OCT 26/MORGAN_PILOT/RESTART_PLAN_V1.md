# MORGAN VERTEX PILOT — RESTART PLAN V1
**Date:** 26 Oct 2026 ~9:45 AM ET (America/New_York)
**Status:** FILED — Eric YES received. **BLOCKED on gcloud AUTH** until Eric re-auths `eric@numista.ai`.
**Owner after AUTH:** Grok CoS (same runner as 13 Oct). AG standby only if CoS unavailable.
**Radio tip:** NET-522

## BLUF
Restart the Agent Builder / Discovery Engine fact-check pilot on sandbox project **`numista-morgan-pilot`** so the ~$1,000 GenAI App Builder credit (expires **23 Jan 2027**) is used. Next batch = **Morgan dollars** (not another AWQ pass). Report-only. No live site, no Firestore `users/{uid}/coins`, no main merge/deploy, no V3Tees.

## What the 13 Oct run was (found)
| Item | Value |
|---|---|
| Project | `numista-morgan-pilot` (sandbox; billing Numista.Ai `010E3C-D8346A-91A35E`) |
| Prod never touched | `studio-9101802118-8c9a8` |
| Engine | `morgan-pilot-search` — Enterprise tier, **Advanced Generative Answers OFF**, observability OFF |
| Data store used | `morgan-docs` (88 inline docs; Wayback Mint pages + scrubbed packs). No GCS bucket. |
| Data store unused | `usmint-site` (PUBLIC_WEBSITE) — API refuses BasicSiteSearch join; crawl needs domain ownership. Leave or delete later. |
| Batch | 48 American Women Quarters claims |
| Runner | Grok CoS headless ~9:30–10:10 PM ET 13 Oct |
| Scripts | `%TEMP%\morgan_pilot\` that night; recovered copy now in `8 OCT 26\MORGAN_PILOT\scripts\` (from box `/workspace/morgan_pilot/laptop/`) |
| Flow | `setup.py` → scrub → `upload.py` → `engine.py` → `pilot.py` (+ optional `recheck.py`) |
| Results | 48/48 Supported by Mint; 0 Contradicted; 0 No Mint source. Files: `13 OCT 26\MORGAN_VERTEX_PILOT_*.csv/md` |
| Cost estimate | ~$0–$6.34 Discovery Engine SKUs only (credit). Check Grounding chars were the wild card. |
| Source ranking | U.S. Mint / Treasury wins over PCGS/NGC/Wikipedia every time |

## Eric YES scope (26 Oct)
1. Restart Morgan Vertex / Agent Builder fact-check pilot.
2. Burn Agent Builder credit — do not leave unused.
3. Stay Flutter (no stack change) — irrelevant to this sandbox search job.
4. Prefer Flash for any Gemini-adjacent work (this pilot uses **Search + Check Grounding only**, not Grounded Generation / Gemini answers).
5. Numista paths only — not V3Tees.
6. FIN OPS separately raising sandbox budget alert ~$5 → ~$80/week (alert-only; not a hard cap).

## Next batch — Morgan dollars first
Source pack (scrubbed): `MORGAN_PILOT\scrub\EVIDENCE_PACK_2026-10-06_MORGAN_SOURCED.csv` (25 rows). Also at OneDrive `1 NUMISTA.AI\MORGAN SME DATABASE\`.

### Batch A (tonight / first overnight) — Mint Tier-A claims only (~12 rows)
Run these first (each has a Mint Wayback / Mint page Tier A quote):

1. `2023-S` → S-SILVER-PROOF  
2. `2021 O-Privy` → P-O-PRIVY  
3. `2021 CC-Privy` → P-CC-PRIVY  
4. NEW `2024#P` Uncirculated  
5. NEW `2024#S-SILVER-PROOF`  
6. NEW `2024#S-REVERSE-PROOF`  
7. NEW `2025#P` Uncirculated  
8. NEW `2025#S-SILVER-PROOF`  
9. NEW `2025#S-REVERSE-PROOF`  
10. `2023 S-Reverse-Proof` id normalize → S-REVERSE-PROOF  
11. `2026` scope check → lives under America250 / semiquincentennial (do not duplicate in morgan_dollars)  
12. Mint-mark key / Philadelphia no-mint-mark clarification (historic Mint page)

**Est. spend Batch A:** ~40–80 Enterprise queries + Check Grounding with facts capped at **≤10 passages/check** (lesson from 13 Oct overspend risk) → target **under $10**; hard stop if net Discovery Engine spend for the week approaches **$80**.

### Batch B (follow-on, separate YES not required if still under weekly guardrail)
Red Book / VAM major varieties (rows with **no** Mint Tier A in the pack): 1879-CC Capped Die, 1880/79-CC, 1882-O/S, 1887/6, 1887/6-O, Hot Lips, 1900-O/CC, 1901 DDR, 1880/79 P/O, 1880-S 80/79. Expect many **Needs Mint source** / third-party-only verdicts — still useful as a Mint-gap report. Do **not** promote PCGS/Red Book over Mint when Mint is silent.

### After Morgan dollars
State Quarters / Washington pack (`EVIDENCE_PACK_2026-10-06_WASHINGTON_SOURCED.csv`, 32 rows) then DC/Territories (7). Same engine; new `rows_*.py` + optional extra Mint Wayback uploads.

## Success criteria (Batch A)
- Every Batch A claim has a verdict: Supported / Contradicted / No Mint source.
- Supported quotes are Check Grounding citations (script-verified match), not freehand.
- Mint tier beats third-party when both appear.
- Output CSVs + SUMMARY.md under `MORGAN_PILOT\out\` **and** copy to `13 OCT 26\` sibling or `26 OCT 26\` day folder.
- Billing: only Discovery Engine / Vertex AI Search SKUs on `numista-morgan-pilot`; matching credit lines. **STOP** if Cloud Storage / Vertex Gemini / Cloud Run / Compute lines appear → kill switch.
- Zero writes to production Firestore, live catalog, Flutter app, or V3Tees.

## Spend guardrails
| Guard | Rule |
|---|---|
| Project | **Only** `numista-morgan-pilot` (`X-Goog-User-Project` + path asserts in `dex.py`) |
| Weekly alert | ~$80/week alert-only on sandbox (FIN OPS) |
| Query cap | `QCAP=200` per overnight run (same as 13 Oct) |
| Facts per check | **MAXF=10** (was 40; cut Check Grounding char burn 4–8×) |
| Add-ons | Advanced Generative Answers **OFF**; Grounded Generation **NOT USED** |
| Kill switch | Billing → unlink/disable billing on pilot project; or delete engine + data stores; or shut down project |
| Card | Net cost after credits should stay ~$0. If non-credit SKU appears → STOP |

## What NOT to touch
- Live `numista.ai` / Cloud Run prod / `main` branch merge/deploy
- `users/{uid}/coins` or any Firestore write
- Production project `studio-9101802118-8c9a8` (do not set as quota/default for these calls)
- V3Tees anything
- Enabling Advanced Answers or Grounded Generation
- Uploading prices, values, PII, or collection data (scrub first)

## Who runs it
| Role | Duty |
|---|---|
| **Eric** | `gcloud auth login` (and ADC if needed) as `eric@numista.ai` — **required before any API call** |
| **Grok CoS** | After AUTH_OK: verify engine/docs still exist; build `rows_morgan_dollars_batch_a.py`; patch `pilot.py` MAXF=10; run Batch A overnight; file RESULTS + SUMMARY + NET tip |
| **AG CoS** | Standby only. Mint-pack B4 remains AG's product critical path. Do **not** divert AG from B4 for this unless CoS unavailable after AUTH. |
| **FIN OPS** | Confirm ~$80/wk sandbox budget alert; morning-after Billing SKU check |
| **Scheduled job** | None yet. Manual overnight CoS run (same as 13 Oct). Cron only after 2 clean nights + Eric YES. |

## Overnight tonight?
**Not until AUTH.** As of 26 Oct ~9:45 AM ET, laptop `gcloud auth print-access-token` fails: *Reauthentication failed. cannot prompt during non-interactive execution.* Default gcloud project is still prod `studio-9101802118-8c9a8` (OK — scripts pin pilot project explicitly).

After Eric finishes `gcloud auth login` and types **AUTH_OK** (or CoS detects token), Batch A can start the **same evening**.

## Files in this package
- `RESTART_PLAN_V1.md` (this file)
- `COMMANDS_RESTART_V1.md` — exact commands
- `scripts/` — recovered 13 Oct runners (+ `rows_awq_48.py` archive)
- `scripts/rows_morgan_dollars_batch_a.py` — Batch A claims
- `scrub/EVIDENCE_PACK_2026-10-06_MORGAN_SOURCED.csv`
- Radio **NET-522**, baton `FOR_AG_COS_MORGAN_PILOT_RESTART_STANDBY.md`, WAKE marker

OVER
