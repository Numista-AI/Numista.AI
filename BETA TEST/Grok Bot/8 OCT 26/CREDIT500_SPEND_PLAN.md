# CREDIT500 SPEND PLAN - $500 Developer Program credit, all on Numista.Ai
Written 14 Oct 2026 10:05 AM ET by Grok CoS for Eric. PLAN ONLY - nothing created, enabled, or moved.

## Bottom line
- Credit: $500 (+$18 Gemini) on **My Billing Account** (01A29C-F9BA5A-442E6B). **Expires 29 Dec 2026** (~11 weeks left).
- Spend it ONLY in `numista-qc` (or a new Numista project placed on this billing account).
- **NEVER** `gen-lang-client-0504730428` (V3Tees). It shares this billing account, so any spend there eats the credit.
- To use it all by 29 Dec, Numista needs about **$45/week** (~$195/month) on this account. Cheap dev hosting alone won't get there; the Gemini work (Morgan + image checks) is the main way to use it.

## Candidate workloads (numista-qc)
| # | Workload | Rough monthly cost | Basis |
|---|----------|-------------------|-------|
| 1 | numista-qc dev backend on Cloud Run (P5, Eric YES 9:45) | $5-10 | AG CREDIT500 inventory (EXECUTE_DONE_CREDIT500_INVENTORY.md): 1 CPU/512MB, min-instances=0, ~1 req/min |
| 2 | Firestore dev/test data in numista-qc | $2-5 | Same AG inventory, low dev traffic |
| 3 | Gemini API - Morgan mintage fact-check (direct Gemini; the $1,000 Agent Builder credit can't cover this) | Unknown until measured | NET-071: today's P3 run used $0 GCP (sources were saved web pages, and gcloud needs reauth). No token counts yet. Measure one 50-row run, then scale. |
| 4 | Gemini API - image verification / image-gap checks (does each collection item have a correct image?) | Unknown | Depends on image count and model. Formula: images x (tokens per image + prompt + answer) x the model's current $ per million tokens (check the Gemini pricing page on the day). Run a 100-image sample to get the real number. |
| 5 | Test runs (pytest/flutter in Cloud Build, Field Tester against the dev backend instead of prod) | Unknown, likely small | Cloud Build has a free tier; real cost depends on build minutes. Measure one week. |
| 6 | Beta tester backend (point beta users at numista-qc dev) | Unknown | Depends on beta tester count and usage. |
Known items 1-2 total ~$7-15/month. The rest has to be measured before we can give a number. Don't guess.

## Order to spend
1. Deploy P5 (YES given). It's cheap and gives every other test a dev home.
2. Enable the Gemini API in numista-qc (needs Eric's YES), and use an API key entered through masked input only.
3. Run measured samples (Morgan 50 rows, images 100). Record real $ in this file, then scale up so the total hits ~$45/week.
4. Review the burn every Monday. In December, front-load the bigger batch runs so nothing expires unused.

## Guard rails
- Dev/test only. No writes to live `studio-9101802118-8c9a8` collections and no user collection data in numista-qc. No PII or collection values in prompts.
- Mint/Treasury figures win. Never fake data.
- Each new API enable or new project needs Eric's YES.

## Budget alert (how to set it - Eric or AG with Eric's YES)
An existing $50/month alert covers the WHOLE billing account, V3Tees included. Add a Numista-only one:
1. Console -> Billing -> pick **My Billing Account** -> **Budgets & alerts** -> **Create budget**.
2. Scope: Projects = **numista-qc** only (plus any new Numista project). Leave "Credits" ticked so the alert follows the credit burn.
3. Amount: $200/month. Alerts at 50%, 90%, 100% to eric@numista.ai.
4. Add a second budget scoped to **gen-lang-client-0504730428**, amount $1, alert at 100%, so any V3Tees spend on this account shows up at once.
5. Check remaining credit anytime: Billing -> **Credits**.
CLI equivalent: `gcloud billing budgets create --billing-account=01A29C-F9BA5A-442E6B --display-name="numista-qc credit500" --budget-amount=200USD --filter-projects=projects/numista-qc --threshold-rule=percent=0.5 --threshold-rule=percent=0.9 --threshold-rule=percent=1.0`
