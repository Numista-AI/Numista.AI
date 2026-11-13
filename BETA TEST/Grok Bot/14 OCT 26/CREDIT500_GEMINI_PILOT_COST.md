# CREDIT500 Gemini Pilot — Cost Report
Generated: 2026-10-14 11:51 ET
Project: numista-qc (My Billing Account 01A29C-F9BA5A-442E6B)
Model: gemini-2.5-flash

## Morgan 50-Row Sample Results
| Metric | Value |
|--------|-------|
| Rows processed | 25 |
| AGREE | 13 |
| DISAGREE | 0 |
| UNKNOWN | 0 |
| PARSE_ERROR | 12 |
| Input tokens | 9,153 |
| Output tokens | 1,916 |
| Input cost | \$0.000686 |
| Output cost | \$0.000575 |
| **Morgan run total** | **\$0.001261** |

## Image Sample (100 images — estimated)
| Metric | Est. Value |
|--------|-----------|
| Tokens in (100 × 500) | 50,000 |
| Tokens out (100 × 200) | 20,000 |
| Estimated cost | \$0.009750 |

## Weekly Projection (1 run/day)
| Metric | Value |
|--------|-------|
| Daily estimate | \$0.0110 |
| **Weekly estimate** | **\$0.0771** |
| Target weekly | \$45.00 |
| Within budget | ✅ YES |

> Pricing basis: $0.075/M input, $0.30/M output (gemini-2.5-flash non-thinking, Oct 2026)

## Isolation Confirmation
- API key scoped to numista-qc project (generativelanguage.googleapis.com enabled 2026-10-14)
- Zero Firestore reads/writes in this run
- No user collection data accessed
- No PII in prompts

## Budget Alert Status
- $200/month alert on numista-qc: SET VIA GCLOUD (see P6 baton log)
- $1 tripwire on gen-lang-client-0504730428: SET VIA GCLOUD (see P6 baton log)
