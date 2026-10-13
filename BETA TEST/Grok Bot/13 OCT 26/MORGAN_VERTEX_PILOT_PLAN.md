# MORGAN VERTEX PILOT PLAN (13 Oct 2026)
Written by Grok CoS. Status: PLAN ONLY. Nothing signed in, enabled or spent.

## Bottom line
- Goal: use the $1,000 Agent Builder credit to fact-check the 48 accepted American Women Quarters (AWQ) rows, with a cited source for every answer.
- Expected spend: under $5 of credit for the whole pilot, $0 on your card.
- Your part: one sign-in session of about 10 minutes (steps at the bottom). The rest runs overnight.

## What the credit pays for (checked against Google's pricing page, Oct 2026)
"Vertex AI Search" was renamed "Agent Search" in April 2026. It's the same product and still bills under the Discovery Engine API.
| Item | Price | Covered by credit? |
|---|---|---|
| Search queries, Enterprise edition (includes basic AI answers) | $4.00 per 1,000 | Yes |
| Advanced Generative Answers add-on | +$4.00 per 1,000 | Yes, but we WON'T turn it on |
| Index storage | 10 GiB free per month, then about $5 per GiB per month | Yes. We need about 5 MB, so it's free |
| Check Grounding API | $0.00075 per 1,000 characters | Yes, and it costs pennies |
| Grounded Generation API | $2.50 per 1,000 calls PLUS the Gemini model's own charge | NOT USED. The Gemini part bills as Vertex AI, not Agent Builder, so it could hit your card |
There's also a free trial of 10,000 queries per month, so the pilot's queries may cost $0.

## What gets loaded (no values, no PII)
1. Morgan's sourced files from `OneDrive\Documents\1 NUMISTA.AI\MORGAN SME DATABASE`, which is about 4 MB across 154 items:
   - Main file: `EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv` (48 rows, U.S. Mint "Tier A" quotes and URLs).
   - Plus the `sources\` folder and the other *_SOURCED packs, for context.
   - Before anything is uploaded, a scrub copy is made on the box. It removes any price, value or collection column, and anything personal such as emails, names of users or account IDs. Only the scrub copy goes up.
2. Public U.S. Mint pages, through **website indexing** of `www.usmint.gov/coins/coin-medal-programs/american-women-quarters/*` and the Mint's annual report pages. No upload is needed. Note: usmint.gov blocked our own fetches on 6 Oct. If Google's crawler is also blocked, we fall back to uploading the saved Wayback copies of those pages as documents.

## How the files get in without a storage bucket
- Website pages: indexed by Google directly, with no bucket.
- Morgan files: sent straight to the data store through the Discovery Engine API's inline document upload, each file under 10 MB. This also avoids a bucket.
- If Google insists on a bucket, the worst case is 5 MB in Cloud Storage for a day, which costs less than $0.01 and would be billed to your card. I'll delete it the same night.

## Steps (overnight, done by Grok CoS once your sign-in is done)
1. Create two data stores in the sandbox project `numista-morgan-pilot`: "morgan-docs" (uploaded files) and "usmint-site" (website). Join them in one Search app, Enterprise edition, with Advanced answers OFF.
2. Load the scrubbed files and start the website crawl, which takes a few hours.
3. For each of the 48 AWQ rows, ask one search question, for example "2022 Maya Angelou quarter mint marks". That's 48 to 150 queries in total.
4. Check each row's claim against the returned passages with the Check Grounding API, which gives a score plus the citations.
5. Rank the sources: a U.S. Mint page beats PCGS/NGC/usacoinbook/Wikipedia, every time. If only a non-Mint source supports a row, it's flagged "Needs Mint source".
6. Output on the laptop: `13 OCT 26\MORGAN_VERTEX_PILOT_RESULTS.csv` with columns row, claim, verdict (Supported / Contradicted / No Mint source), score, cited URL, quote. A plain-English summary is included.
7. Billing check the next morning (see below), then a report to you.

## Estimated credit spend
| Item | Amount | Cost |
|---|---|---|
| Queries | about 150, including retries | $0.60, or $0 inside the free trial |
| Check Grounding | about 48 x 20,000 characters | under $0.01 |
| Storage | about 5 MB | $0 (free tier) |
| Website crawl/index | small site slice | $0 (within the free 10 GiB) |
| **Total** | | **under $1; budget cap $5** |
Note: a $5 pilot won't make a dent in $1,000. To show real use before asking for more, the follow-on step is to put ALL of Morgan's programs through the same check, and later run Morgan's live answers through Check Grounding. Each of those needs your YES.

## Billing check (Reports grouped by SKU)
1. Console > Billing > Reports.
2. Set the project to `numista-morgan-pilot`, the time range to the last 7 days, and Group by to **SKU**.
3. Every line should be "Vertex AI Search: …" or Discovery Engine, and each should show a matching **Promotions/credits** line that cancels it out, so the net is $0.
4. Any line from Cloud Storage, Vertex AI (Gemini), Compute or Cloud Run means STOP and use the kill switch.
5. A budget alert is also set: $1 on *net cost* for this project, emailed to you.

## Kill switch (any one of these is enough)
- Fastest: Console > Billing > Account management > find `numista-morgan-pilot` > **Disable billing**. All spending stops right away.
- Cleaner: delete the Search app and both data stores (AI Applications > Apps).
- Full stop: Console > IAM & Admin > Settings > **Shut down** the project (it can be undone for 30 days).
The production Numista.Ai project is never touched in any of these.

## Rules kept
- A separate sandbox project, never production.
- Credit SKUs only, with Grounded Generation and Advanced Answers OFF.
- No collection values or PII are uploaded.
- U.S. Mint beats PCGS/NGC.
- No new rows are changed on the live site. Results are a report only, and any fix goes through the normal baton and Deploy YES.

---
## ERIC'S ONE-TIME STEPS (about 10 minutes, on the laptop)
1. Go to https://console.cloud.google.com and sign in with the Google account that holds the Google for Startups credit.
2. Top bar project picker > **New Project**. Name it `numista-morgan-pilot`, leave Location as is, and click Create. **Do not pick the production Numista.Ai project.**
3. Console > **Billing** > confirm the billing account that shows the $1,000 Agent Builder credit under *Credits*, then link it to `numista-morgan-pilot` (Billing > Account management > Link a project).
4. Search bar: type **Discovery Engine API** and click **Enable**. Then search **AI Applications** (Agent Builder), open it, and click **Continue/Activate API** to accept the terms. Don't build anything; I'll do that.
5. Billing > **Budgets & alerts** > Create budget: project `numista-morgan-pilot`, amount $5, alerts at 20% and 100%.
6. Give Grok CoS access by either (a) leaving the console signed in on the laptop tonight, or (b) running `gcloud auth login` once if I give you that command. Tell me which you prefer.
7. Type "pilot ready" to me.
