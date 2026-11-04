# PLAN C: Read-only audit of which AI model each call uses
Owner: FIN OPS | Status: DRAFT v1 | Timing: PRE-LAUNCH (audit only). Any model switch is a separate, post-launch plan.
Source: Google guide p.7–8 (Flash-Lite for high-volume or simple work, Flash for production, Pro only for hard reasoning), p.3 ("tokenomics"), p.9 (prompt caching).

## Goal
Produce one table showing, for every Morgan and catalog AI call: which Gemini/Vertex model it uses, roughly how often, roughly what it costs, and whether it could move to Flash or Flash-Lite.

## Scope
- Reading code and config on the dev branch (search for model names).
- Reading the existing billing export and Vertex usage pages.
- Writing one report file.

## Out of scope (the audit changes nothing)
- No changes to code, config, models, prompts, keys or billing.
- No deploys and no Firestore reads of user records. No Firestore writes.
- No test calls that cost money.

## Steps
1. List every place a model is named: Morgan chat, coin identification, image analysis, valuation, catalog builder/nightly jobs, and anything else found. Record the file and line.
2. For each, note the model name and version, whether it's text or image, and whether a user is waiting on it (live) or it can wait (nightly).
3. Match calls to cost using the billing export: requests per day and dollars per day, last 14 days. Mark anything that can't be matched as UNVERIFIED.
4. Label each call:
   - KEEP: hard reasoning, or quality matters most.
   - TRY FLASH: routine answers.
   - TRY FLASH-LITE: classification, tagging, simple extraction.
   - BATCH CANDIDATE: can wait (feeds Plan D).
   - CACHE CANDIDATE: a big, fixed prompt sent many times (p.9).
5. Estimate the savings for each candidate using Google's public price page (https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing), marked UNVERIFIED until tested.
6. Report to GB CoS. Any switch becomes its own plan with a quality test (Plan B's golden set) before and after.

## Report format
| Call | File:line | Model | Live or nightly | Calls/day | $/day | Label | Est. saving | Notes |

## Success criteria
- Every model call found in the code is in the table, or listed as "not found in billing."
- Top 5 candidates ranked by estimated savings.
- Nothing in any system changed (FIN OPS confirms in the report).

## Rollback
Nothing to roll back; it's read-only. Delete the report if not wanted.

## Cost estimate
About $0 (reading code and billing). UNVERIFIED: if the billing export needs a BigQuery query, a few cents.

## Risks
- Missing calls hidden in config or environment settings. Search both, and compare against billing.
- Cheaper models can be less accurate. That's why no switch happens without its own plan and the golden-set test.
- PII: the report lists code locations and dollar totals only. No prompts, answers, user names or collection data are copied. Nothing about AJ.
- Seeing secrets: the auditor will see where keys are referenced. Never copy key values into the report or chat.

## Review chain
FIN OPS draft → Argon → GB CoS score 95+ → SAG → Eric's typed YES → audit runs → report back. A switch needs a new plan and a new YES.

## Open questions for Eric
None beyond approving the audit.
