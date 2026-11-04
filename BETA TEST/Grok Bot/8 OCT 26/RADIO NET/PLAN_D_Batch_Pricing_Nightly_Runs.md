# PLAN D: Cheaper pricing for nightly catalog runs (batch / Flex)
Owners: Catalog Research (jobs) and FIN OPS (money) | Status: DRAFT v1 | Timing: POST-LAUNCH CANDIDATE. Eric decides whether any zero-cost setup can happen before 27 Nov.
Guide source: p.9 says Deferred and Batch run "work that can wait" and "You pay up to half the inference cost." We checked this against Google's current public docs (below) instead of trusting the guide.

## What Google's docs say today (checked 4 Nov 2026)
- Batch inference: "50% discounted rate compared to real-time." Up to 200,000 requests per job; 1 GB input file limit. Jobs can wait in a queue for up to 72 hours, and most finish within 24 hours of starting. Unfinished jobs are cancelled after 24 hours and you pay only for completed requests. No SLA. Does not support explicit caching or RAG.
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/capabilities/batch-inference
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deploy/batch-inference
- Price page: "Gemini models are available in batch mode at 50% discount."
  https://cloud.google.com/gemini-enterprise-agent-platform/generative-ai/pricing
- Flex PayGo: 50% off standard; answers can take up to 30 minutes; global endpoint only; 3,000 requests per minute per model; only Gemini 3.8 Flash and earlier (not newer models such as Gemini 4 Argon). Enabled with a request header.
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/flex-paygo
  https://docs.cloud.google.com/gemini-enterprise-agent-platform/models/deploy/consumption-options
- Deferred execution pricing: "Coming soon," "select workloads," "up to half." Not available to plan on yet.
  https://cloud.google.com/blog/products/ai-machine-learning/flexible-billing-and-cost-controls-for-agents-on-google-cloud
- Caching: on Gemini 2.5, the cache discount and the batch discount don't stack; on Gemini 3+, they stack to 95% off cached input.

## The key problem: timing
Batch doesn't promise a finish time: it can queue up to 72 hours and run up to 24. That conflicts with the 3 AM stop and the 6:30 AM report. Flex PayGo (30 minutes at most per answer) fits the night window much better. Proposal:
- Flex PayGo for the nightly jobs that must be done by 6:30 AM, if their model supports it.
- Batch only for work that can arrive "sometime in the next day or two" (for example, bulk re-tagging or summaries), and is reported when it lands.

## Goal
Pay about half price on eligible nightly catalog AI calls without breaking the $50 cap, the 3 AM stop or the 6:30 AM report.

## Scope
- Nightly catalog jobs that no user is waiting on (list to come from Plan C's "BATCH CANDIDATE" labels).
- A one-night test on a small slice, after launch.

## Out of scope
- Morgan's live chat and anything a user waits on.
- Jobs using RAG or explicit caching (batch doesn't support them).
- Provisioned Throughput purchases or any commitment. Any money commitment.
- Firestore writes from batch results without Eric's separate YES.

## Steps
1. From Plan C, list the nightly jobs, their models and their nightly cost.
2. Sort them: must finish by 6:30 AM → Flex candidate; can wait a day → batch candidate; uses RAG/caching or a newer model → not eligible.
3. Catalog Research writes a small test: one job, ~100 requests, on a test copy. Results go to a review file, not into the live catalog.
4. FIN OPS sets a hard stop: if the night's spend reaches $50, or it's 3 AM, the job is cancelled (Google bills only completed requests).
5. Compare cost and quality (Plan B style spot checks) with the standard run.
6. Report in the 6:30 AM report. GB CoS brings the result to Eric.

## Success criteria
- Test night: same quality, about 40–50% lower cost on the test slice, under $50, stopped by 3 AM, and in the 6:30 AM report.
- Batch jobs: done or cancelled cleanly, with no late surprise charges.

## Rollback
Remove the Flex header, or go back to the standard calls. Cancel any open batch job; only completed work is billed.

## Cost estimate
- Setup: probably $0 in Google fees (it's a setting or job type, no subscription). Engineering time only. UNVERIFIED.
- Test night: a small slice of the normal nightly spend, under $5. UNVERIFIED.
- Savings: up to 50% of eligible nightly AI spend. The eligible share is UNKNOWN until Plan C is done.

## Risks
- Late results breaking the 6:30 AM report (batch). Use Flex for anything that is due by morning.
- Flex throttling ("higher throttling") or slow answers; the job may not finish. Hard stop at 3 AM.
- Model limits: Flex is not available on Gemini 4 Argon or newer.
- "Coming soon" Deferred pricing could change. We don't plan on it.
- PII: nightly jobs use catalog data only. No user, AJ or storage-location data goes into batch files in Cloud Storage. Batch input files must be deleted after the run.

## Review chain
Catalog Research/FIN OPS draft → Argon → GB CoS score 95+ → SAG → Eric's typed YES → test night. Any Firestore write needs a separate YES.

## Open questions for Eric
1. Keep this fully after launch (27 Nov)? Or allow the zero-cost setup and a single test night before launch?
2. Is Flex for the overnight run and batch only for "can wait a day" work the right split?


## Eric decisions (4 Nov 2026, 10:36 AM ET)
- Allow $0 setup plus ONE test night before 27 Nov (within the $50 cap, 3 AM stop; Firestore writes still need a separate YES).
- Split: Flex PayGo overnight, batch only for work that can wait a day: YES.
