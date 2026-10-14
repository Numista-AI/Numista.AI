# EXECUTE_DONE — P6 CREDIT500 Gemini Pilot REDO (V2 via Vertex AI ADC)
**Date:** 2026-10-14 ~15:29 ET
**Completed by:** AG CoS (Antigravity / Gemini 3.8)
**Ref:** BATON_P6_CREDIT500-GEMINI-PILOT, NET-088, NET-091

## What Changed from V1
- V1 used Gemini REST API with API key (scored PARTIAL by Grok CoS in NET-088)
- V2 uses **Vertex AI SDK** via ADC (eric@numista.ai) — NO API key in any file
- JSON parse fixed: `re.search(r'\{.*\}', text, re.DOTALL)` for nested JSON
- Also enabled `aiplatform.googleapis.com` on numista-qc (was not enabled — caused all prior Vertex AI errors)

## Results (V2)
| Metric | V1 | V2 |
|--------|----|----|
| Model | gemini-2.5-flash via REST | gemini-2.5-flash via Vertex AI ADC |
| Rows processed | 25 | 25 |
| AGREE | 13 | **19** |
| DISAGREE | 0 | 0 |
| UNKNOWN | 0 | 0 |
| PARSE_ERROR | 12 | **6** |
| Tokens in | ~5,200 | 10,588 |
| Tokens out | ~650 | 1,171 |
| Cost | $0.001261 | $0.001145 |

## AGREE rows (19/25 = 76% parse rate, 100% of parseable rows)
All 19 parseable rows returned AGREE. No DISAGREE or UNKNOWN.

## Remaining PARSE_ERROR rows (6)
Rows 10, 11, 19, 22, 23, 25 — these are "meta" rows (program#years, program#mint_mark_locations, etc.) that lack coin-level evidence context. The model returns truncated or malformed JSON for these meta-field rows. Recommendation: filter out meta rows before sending to Gemini (they aren't coin-slot fact-checks).

## API Enable Note
Enabled `aiplatform.googleapis.com` on numista-qc project (required for Vertex AI LLM calls via ADC). Within Eric's YES scope for numista-qc. NOT enabled on gen-lang-client-0504730428 (V3Tees).

## Image Sample Status
Image pilot (100 images) not yet run. Requires catalog/reference image path. Meta rows show no evidence quote → image path lookup needed. Will request from Eric if needed.

## Isolation Confirmation
- Used Vertex AI via ADC only — no API key in any file, log, or prompt
- No Firestore reads/writes; no collection access; no PII in prompts
- Budget alerts remain active (both projects)

## Output Files
- `BETA TEST\Grok Bot\14 OCT 26\CREDIT500_GEMINI_PILOT_MORGAN50_V2.csv` — 25 rows, 19 AGREE / 6 PARSE_ERROR

## Log
- 2026-10-14 ~15:27 ET AG CoS: Enabled aiplatform.googleapis.com on numista-qc
- 2026-10-14 ~15:29 ET AG CoS: V2 run complete — 19 AGREE, 0 DISAGREE, 6 PARSE_ERROR (all on meta rows)
