# $1,000 Agent Builder credit: 13-week plan (recommendations only)
Prepared 23 Oct 2026, 9:30 AM ET. Billing account Numista.Ai 010E3C-D8346A-91A35E, sandbox project numista-morgan-pilot. About $999.98 left, expires 23 Jan 2027.
Week-1 proofs are authorized (27 Oct). Every later step still needs Eric's typed YES.

## Status 27 Oct 2026 (updated ~10:30 AM ET)
- **Credit left:** $999.98 of $1,000 (live console ~10:08 AM ET 27 Oct). Expires 23 Jan 2027. Stop all runs by 22 Jan.
- **Week-1 proof runs: AUTHORIZED and EXECUTING.** Eric typed "YES proof runs" ~10:20 AM ET 27 Oct. Desk is running the ~$5.36 tiny proofs on numista-morgan-pilot only. Billing lags about a day, so we confirm each charge lands on the credit before scaling.
- **Eric's goal (27 Oct):** the most accurate, thorough database of coins, currency and medals used in the current and former US states and territories, with images, Fugio through 2026 releases. Every item a user might add should already be there. **No duplicate work:** review what's already in our buckets first. Only if credit is left after that, expand to popular foreign coins and notes.
- **Inventory done (read-only):** `/workspace/roi/catalog_inventory_20261027.md`. We already hold ~6,503 catalog rows (5,770 coins / 620 notes / 113 medals, 26 Oct live read). Spend goes to **gaps**, not to the "do not redo" series listed there.
- **Overnight 26–27 Oct:** about $0 used against a one-night $50 cap. That cap is not this plan.
- **Unchanged rules:** nothing is enabled, raised or scaled without Eric's typed YES. Alerts only, no caps. No live Firestore writes from morgan-pilot without a separate YES. Flash/Gemini stays on numista-qc (Developer credit).
- **Not paid by this credit:** image download/attach, GCS remap, Gemini vision/Flash labeling, image generation, Firestore attach. That is the **Developer (numista-qc) / GFS** track and needs its own YES. The app still reads the finished catalog from the live **studio** Firestore and buckets.

## Answer first (revised 27 Oct)
- **Next YES after the proofs pass:** **"YES fold-gate verify"** — a cheap (~$4) Check Grounding pass on Morgan's NET-586/588/589 corrections, so the overnight drafts are clean before we scale anything.
- Then, in order: (a) Mint/Treasury-first verification of **gaps only** (Fugio/Confederation, colonial and Continental, CSA and early federal paper, early federal coin types, US-Philippines 1903–45); (b) AJ's ~4.5K records, grounded checks, read-only; (c) invoice/receipt layout proof; (d) Mint/Treasury library; (e) Stump Morgan; (f) Morgan answers in a staged CSV only; (g) law corpus; (h) load test and ranking last.
- **Rough split of ~$981:** about **$387 on US gap-fill directly** (gap verify $264 + gap conflict re-checks $79 + Mint/Treasury library $40 + fold-gate $4), plus **$168 Morgan answers** (staged, gap items first) and **$50 law corpus** that support it. About **$178 on other must-do work** (AJ checks $108, receipt $3.75, Stump ~$49, prototype/load/ranking $17). Week-1 proofs $5.36. About **$192 held for foreign** (Weeks 10–12), which runs only if the US gaps are finished; otherwise it goes to more US gap verify (so US gap-fill can reach ~$579). Buffer ~$19.
- **Cut:** no scaling of catalog volume until fold-gate verify passes. No Google Search grounding ($35 per 1,000). Gemini tokens inside grounded generation are flagged as the wrong pot (they'd bill like numista-qc Developer work), so we use the search answer call.
- Medals: the 113 we hold are not rebuilt. New medal work only if a live attach audit finds real holes. The ~4,800 image-gap figure is still **unverified**.

## What the credit covers (checked 23 Oct 2026)
Sources: cloud.google.com/generative-ai-app-builder/pricing; cloud.google.com/products/agent-builder ("$1,000 ... one time credit per billing account ... for select SKUs"); cloud.google.com/skus/sku-groups/vertex-ai-search-and-conversation.

| Charge (SKU group "Vertex AI Search and Conversation") | Published price | Free allowance | Credit covers? |
|---|---|---|---|
| Enterprise search query (includes basic AI answers) | $4.00 / 1,000 | 10,000 queries / account / month | Yes (in SKU group) |
| Standard search query | $1.50 / 1,000 | same 10,000 | Yes |
| Advanced Generative Answers (add-on per query) | +$4.00 / 1,000 | **None** (free trial excludes it) | Yes |
| Layout Parser (document reading + chunking) | $10.00 / 1,000 pages | none listed | Yes (SKU 5F3F-A230-7FDA) |
| OCR for document understanding | $1.50 / 1,000 pages | first 1,000 pages/month free | Yes |
| Data index (storage) | $5.00 / GB / month | 10 GiB / month free | Yes |
| Grounded Generation on own data | $2.50 / 1,000 requests | none | Yes (SKU C42C-2852-B25D) |
| Grounded Generation on Google Search | $35 / 1,000 | none | Yes, but costly; not recommended |
| Ranking API | $1.00 / 1,000 | none | Yes |
| Check grounding | $0.00075 / 1,000 | none | Yes (about free) |
| Gemini tokens used *inside* grounded generation | "charged at the selected Gemini model's price" | n/a | **Probably not** (billed as Gemini/Vertex AI). Flag. |

Flag: Google doesn't publish an exact list of the SKUs this credit covers. The table above is based on the official SKU group, plus our 17 and 20 Oct billing, which showed the morgan-pilot $0.01 counted against "GenAI App Builder trial credit". The Week 1 proof runs are there to confirm it charge by charge.

## Workstreams: estimated weekly cost (list prices, math shown)
Assumptions (flagged): Enterprise edition with advanced answers on, so each query costs $4 + $4 = $8 per 1,000. To be safe I charge the full query price even though the free 10k/month will absorb some of it (up to about $40 a month less). Page and item counts are estimates until the proof runs.

1. **Catalog verification (legal-tender US coins and currency, Mint/Treasury figures win).** About 3 queries per item (mintage, specs/data, image source). Cost per item = 3 × $8/1,000 = **$0.024**. At 2,000 items a week: 6,000 queries × $8/1,000 = **$48/week**. *Assumption:* we don't yet know how many distinct items are in users' collections plus the US legal-tender list. If it's smaller, the catalog work finishes early (fine).
   - Tiny proof run: 50 items (150 queries) = **$1.20**. Check against the 48 AWQ rows already done: score right/wrong/not-found, and confirm the charge lands on the credit.
2. **Mint and Treasury document library (layout parser).** Mint annual reports, mintage PDFs, Treasury currency reports. *Assumption:* about 3,000 pages total. 3,000 × $10/1,000 = **$30 one-time**, spread as $15 over 2 weeks. Storage should stay under the free 10 GiB.
   - Tiny proof run: 100 pages = **$1.00**. Confirm tables (mintage columns) come out readable, which was our weak spot with the 16 Oct OCR (11/17 values right).
3. **Stump Morgan answer engine and question bank.** Bank is 1,169 questions today. Full run = 1,169 × $8/1,000 = **$9.35**. At 2,000 questions = **$16**. One run every 1-2 weeks.
   - Tiny proof run: 100 questions = **$0.80**, comparing advanced vs basic answers on the same questions (the 16 Oct baseline: 1,084 correct / 25 stumped / 0 wrong / 60 errors).
4. **"Research Bot" search prototype (sandbox numista-morgan-pilot only, no live site; formerly labeled Ask Morgan — in-app Morgan unchanged).** Test traffic of about 500 queries a week × $8/1,000 = **$4/week**, plus ranking at $1/1,000 (pennies).
   - Tiny proof run: 50 queries = **$0.40**.
5. **Invoice/receipt PDF reading test (must-keep).** Sample receipts only, copied into the sandbox. Nothing from live Firestore. Layout parser 300 pages × $10/1,000 = $3.00, plus grounded extraction 300 × $2.50/1,000 = $0.75, total **$3.75**. The Gemini tokens in that step are probably *not* covered (a few cents on Flash).
   - Tiny proof run: 20 pages = **$0.20**. Compare against today's Gemini receipt reading (main.py) for accuracy. Note: Argon's 22 Oct findings say the duplicate-delete bugs are in commit logic, not reading, so this test doesn't fix those.

## Added workstreams (revision 23 Oct)
6. **Coinage-law corpus:** Federal Register, the U.S. Code Title 31 coinage sections, and Mint/Treasury reports beyond the first 3,000 pages, read with the layout parser. *Assumption:* about 5,000 more pages. 5,000 × $10/1,000 = **$50**. Proof run: 50 pages = $0.50.
7. **Morgan answers per catalog item:** one search "answer" call with advanced answers per item, producing a description and FAQ. Each one is staged in a review CSV in the sandbox and **never written to the live site or Firestore**. 20,000 × $8/1,000 = **$160**. I chose the search answer call over the Grounded Generation API on purpose: Grounded Generation bills its Gemini tokens separately, and those tokens likely aren't covered by this credit. Proof run: 20 items = $0.16.
8. **Grounded checks of AJ's ~4.5K coin records:** 3 queries per record (mintage, specs, program) on a read-only copy of the records. 4,500 × 3 × $8/1,000 = **$108**. Check-grounding scores cost about $0.00075/1,000, so they're effectively free. *Flag:* we need a read-only export of AJ's records; nothing would be read from or written to live Firestore. Proof run: 25 records = $0.60.
9. **Prototype load test:** 2,000 Standard-edition queries × $1.50/1,000 = $3, plus 2,000 Enterprise queries × $4/1,000 = $8, which compares the two editions. I've budgeted **$8**, the Enterprise half. The Standard half and any queries left inside the free allowance aren't counted. Sandbox only.
10. **Ranking experiments:** re-rank catalog search results with the Ranking API. 5,000 calls × $1/1,000 = **$5**. *Flag:* the Recommendations product is built for media and retail, so I don't recommend it here.
(The bigger Stump Morgan bank is covered by the larger Stump runs in the table.)

## 13-week table (revised 27 Oct: gaps first, no redo)
Spend targets the gaps in the 27 Oct inventory. Series on the inventory's "do not redo" list (Washington, Lincoln, Jefferson, Roosevelt, Buffalo, AID, ASE, Morgan, Presidential/Sacagawea, 50 State, ATB, Hawaiian, held medals, and the rest) get **no** new verify queries except conflict re-checks. Week numbers stay, but each catalog line is tied to a named gap.

| Wk | Week of | Work (letters = CoS priority) | Est. cost | Running total | YES needed |
|---|---|---|---|---|---|
| 1 | 26 Oct | **AUTHORIZED / EXECUTING** (Eric YES ~10:20 AM ET 27 Oct): tiny proof runs, workstreams 1–10 | $5.36 | $5.36 | done: "YES proof runs" |
| 2 | 2 Nov | Fold-gate verify: Check Grounding + re-query of Morgan NET-586/588/589 corrections, ~500 queries ($4.00); Mint/Treasury library 1,500 pp, gap-type reports first ($15) | $19.00 | $24.36 | **YES fold-gate verify**; YES library |
| 3 | 9 Nov | (a) Gap verify 2,000 items: Fugio/Confederation + colonial + Continental ($48); library 1,500 pp ($15) | $63.00 | $87.36 | YES gap verify (only after fold-gate passes) |
| 4 | 16 Nov | (a) Gap verify 2,500: CSA + early federal paper ($60); (b) AJ checks 1,500 ($36) | $96.00 | $183.36 | YES AJ checks (read-only export) |
| 5 | 23 Nov | (a) Gap verify 2,500: early federal coin types, half/large cents, pre-1933 gold ($60); (b) AJ 1,500 ($36); (c) receipt test ($3.75) | $99.75 | $283.11 | YES receipt test |
| 6 | 30 Nov | (a) Gap verify 2,000: US-Philippines 1903–45 + thin evidence packs (Mercury, Walker, Franklin, Ike, SBA, Barber Q) ($48); (b) AJ 1,500 ($36); (d) law-adjacent Mint/Treasury extra pp 1,000 ($10) | $94.00 | $377.11 | — |
| 7 | 7 Dec | (a) Gap verify 2,000: medal holes ONLY if live attach audit flags them, else remaining note/coin holes ($48); (e) Stump 1,169 ($9.35); prototype ($4) | $61.35 | $438.46 | YES prototype |
| 8 | 14 Dec | (a) Gap conflicts re-check 1,500 ($36); (f) Morgan answers 3,000, staged CSV only ($24); (g) law corpus 2,500 pp ($25) | $85.00 | $523.46 | YES Morgan answers (staged); YES law corpus |
| 9 | 21 Dec | (f) Morgan answers 4,000 for gap items ($32); (g) law corpus 2,500 pp ($25); (e) Stump bank to 2,000 ($16) | $73.00 | $596.46 | YES new bank questions |
| 10 | 28 Dec | **Foreign lane only if US gaps are finished:** popular foreign coins/notes verify 2,500 ($60); (f) Morgan answers 3,000 ($24) | $84.00 | $680.46 | YES foreign (only if US done) |
| 11 | 4 Jan | Foreign (or leftover US) verify 3,000 ($72); (f) Morgan answers 4,000 ($32); (e) Stump 3,000 ($24) | $128.00 | $808.46 | — |
| 12 | 11 Jan | Foreign/US verify 2,500 ($60); (f) Morgan answers 4,000 ($32); (h) ranking ($5); (h) load test ($8) | $105.00 | $913.46 | YES ranking; YES load test |
| 13 | 18 Jan | (f) Morgan answers final 3,000 ($24); final gap conflict re-check 1,800 ($43.20); write-up; **stop everything by 22 Jan** | $67.20 | $980.66 | optional YES to shut down sandbox engines |

The plan totals about $981, leaving about $19 as a buffer. Weeks 10–12 "foreign" lines run only after an Eric YES confirming the US gaps are done; if they aren't, that money goes to more US gap verify. If the free 10k searches a month absorb some cost (up to ~$40 a month), I'll propose a top-up of real gap work in Weeks 11–12 for a YES. Weekly billing check against this table; stop and ask if any week runs more than 25% over.

**Images:** every gap row found here is staged as data only. Getting images onto those rows (prefer the ~11,069 objects already in GCS before any new scrape) is the Developer/GFS track, not this credit.

## Risks
- **Wrong pot:** Flash/Gemini on numista-qc is paid from the Developer credit. Never bill it to morgan-pilot.
- **Card leakage:** Gemini tokens inside grounded generation, Document AI outside Agent Search, and anything in other projects are not paid by this credit. Keep all this work in numista-morgan-pilot and use Agent Search's built-in features only.
- **Credit scope not published SKU-by-SKU:** we confirm in billing after Week 1 before scaling. Billing data lags by about a day.
- **Overspend:** the morgan-pilot budget (updated 26 Oct) is about $80 a week ($350 a month). It only sends alerts and leaves credits out of the count (EXCLUDE_ALL_CREDITS). It's not a cap (per Eric's rule, no caps). Recommend weekly billing checks against this table, and stop and ask if any week runs more than 25% over.
- **Expiry:** anything unused on 23 Jan is lost. Once it's spent, Google bills the card at the same rates, so stop all runs by 22 Jan.
- **Engine quirk:** morgan-factcheck-blended can't drop the Smithsonian store (the API needs 2 or more stores). Use morgan-factcheck-search for catalog and Stump runs.
- **Data safety:** no live site, Firestore or V3Tees access. Receipt samples are copies only.
- **Estimates:** page and item counts are assumptions. The real cost could be lower (free tier) or higher (more pages).
