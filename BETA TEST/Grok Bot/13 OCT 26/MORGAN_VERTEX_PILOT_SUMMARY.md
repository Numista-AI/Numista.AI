# MORGAN VERTEX PILOT: RESULTS SUMMARY (run 13 Oct 2026, about 9:30 to 10:10 PM ET)
Run by Grok CoS (headless) on project `numista-morgan-pilot`. **Report only.** No live Numista.Ai data, Firestore, production project, catalog or Morgan database files were changed.

## Bottom line
- **All 48 AWQ rows: Supported by a U.S. Mint source.** 0 Contradicted, 0 "No Mint source".
- Every quote in the results file is word-for-word text that the Check Grounding API returned (this was checked by script: 0 non-matching quotes).
- **Website crawl of usmint.gov did NOT work** (details below). We used the plan's fallback: the saved Wayback copies of the Mint pages, uploaded as documents.
- **Cost:** queries are about $0.49 at list price, most likely $0 under the free trial. Check Grounding could be anywhere from about $0.0001 to about **$5.85**, depending on how Google meters it (details below). Everything is on Discovery Engine (credit) SKUs. **Please look at Billing > Reports in the morning.**

## Verdict counts
| Verdict | Rows |
|---|---|
| Supported | 48 |
| Contradicted | 0 |
| No Mint source | 0 |

The 48 rows break down like this:
- **Rows 1–39 (odd numbers): REMOVE the West Point (W) uncirculated slot**, 20 rows. For each honoree, the Mint's rolls-and-bags page supports "minted at Philadelphia (P), Denver (D) and San Francisco (S)." We also checked the opposite claim, "struck at West Point with a W mint mark," against the same Mint passages. It was **never supported**: scores ran from 0.01 to 0.24 with zero citations. Caveat: a grounding check can't prove that something doesn't exist. This result means "no Mint evidence of a W, and Mint pages list only P, D and S," which matches Morgan's own note.
- **Rows 2–40 (even numbers): ADD the S Silver Proof (99.9% silver) slot**, 20 rows. Each is supported by that year's Mint Silver Proof Set page (22WS, 23WS, 24WS or 25WS): the honoree is in the set, the coins are 99.9 percent silver, and the mint and mint mark are San Francisco - S.
- **Row 41** ("S Uncirculated" label) and **row 42** ("S Proof (clad)" label): Supported (the Mint rolls page and the 2023 Proof Set 23WP page).
- **Rows 43–47** (names and slug: Stacey Park Milbern, Rev. Dr. Pauli Murray, Patsy Takemoto Mink, Edith Kanakaʻole, Zitkala-Ša): Supported by the Mint coin pages and rolls pages, including the coin inscriptions.
- **Row 48** (100 total slots): Supported. The 2022 and 2024 Mint press releases cover the four-year program with five designs a year, the rolls pages cover P, D and S, and the proof and silver proof set pages cover S.

Support scores ran from 0.845 (row 44) to 0.991 (row 35).

## Rows that needed a second check (transparency)
On the first pass, 17 rows were not fully cited. They were re-checked **using the same Mint passages the search had already returned** (no new searches):
- **15 silver rows** (2, 4, 6, 8, 10, and 22–40): the sentence "…is struck at the San Francisco Mint (S)" scored 0.35–0.53. We reworded it to the Mint's own spec wording, "The mint and mint mark of the {year} AWQ Silver Proof Set is San Francisco - S," and it then scored 0.97–0.99. The 2023 rows passed on the first try because the 2023 page literally says "Struck at the U.S. Mint facility in San Francisco."
- **Row 3 (Dr. Sally Ride, 2022)** scored 0.49 at first. The saved Mint page (product 22WRC) lists "Mint and Mint Mark: Philadelphia – P Denver – D", and S appears only as "3-Roll Set (P, D, S)." We split the claim into those two facts, and it scored 0.98. **Something for Eric to note:** this Mint page lists only P and D in its mint field, with S in the 3-roll set. Other honorees' pages list P, D and S in the mint field.
- **Row 5 (Wilma Mankiller)** passed the first time, but its citations came from other honorees' pages. We re-checked it against only the Mankiller Mint page (a 2023 catalog.usmint.gov capture), and it scored 0.97.
The first-pass scores are kept in `MORGAN_VERTEX_PILOT_DETAILS.csv` (column row_first_pass_score).

## Contradictions (Mint figure vs our row)
None. Note that the 48 AWQ rows are about mint marks, slots, names and the slug. **None of them is a mintage figure**, so no Mint mintage numbers were tested in this pilot.

## What was created (all in numista-morgan-pilot, global location)
- Data store **`morgan-docs`** (unstructured, CONTENT_REQUIRED), holding **88 documents** sent by inline import. No bucket was used.
  - 58 U.S. Mint page copies (mostly Wayback captures, plus a few saved live fetches whose URL was taken from the page's Item Number).
  - 3 non-Mint pages (PCGS, NGC, Littleton). They were only allowed to count as "No Mint source" support, and in the end they weren't needed.
  - 27 scrubbed Morgan packs (all 25 `*_SOURCED.csv` packs, `coins\american_women_quarters_2022-2025.csv`, and `sources\sources_silver_eagles_women_quarters.md`). These were loaded for context only and **excluded as evidence**, because Morgan's own claims can't verify themselves.
- Data store **`usmint-site`** (PUBLIC_WEBSITE), with 4 include patterns:
  - `www.usmint.gov/coins/coin-medal-programs/american-women-quarters/*`
  - `www.usmint.gov/about/reports*`
  - `www.usmint.gov/content/dam/usmint/reports/*`
  - `www.usmint.gov/about/production-sales-figures/*` (added by Grok, beyond the plan)
  - **It is not connected to the app** (see "What failed"). It's empty and costs nothing. Left in place.
- Search app (engine) **`morgan-pilot-search`**: Enterprise tier, **no add-ons (Advanced Generative Answers OFF)**, data store `morgan-docs`. The engine's "observability" setting came ON by default, so Grok turned it OFF to avoid any Trace or Logging side charges.
- **No Cloud Storage bucket** was created (`gcloud storage ls` shows none). Grounded Generation was never called. No Gemini or Vertex model calls, no Cloud Run, no Compute, and no answer or summary calls.
- gcloud's global config is unchanged (the default project and quota project are still production, untouched). Every call used `numista-morgan-pilot` explicitly with the `X-Goog-User-Project` header.

## What failed or was limited
1. **Website indexing of usmint.gov:** the API refused to add the website store to the app, with this error: *"BasicSiteSearch data stores are not currently supported. Please remove the following data stores: …/dataStores/usmint-site."* Advanced website indexing (the kind that crawls) requires verified ownership of the domain, which we can't do for usmint.gov. **No crawl will happen.** We used the Wayback fallback.
2. **Per-SKU billing data is not available by API.** There's no BigQuery billing export. The Cloud Billing Budget API isn't enabled on the pilot: gcloud offered to enable it, and Grok declined. The Cloud Billing API doesn't return costs. So **Eric needs to check Console > Billing > Reports** (project numista-morgan-pilot, Group by SKU). Usage data can take up to 24 hours to appear.
3. Auto-review paused the document upload once, because it read it as sending files to an outside endpoint. It went ahead after the approval request. The destination was this sandbox's own Discovery Engine data store.
4. Some of the saved "Mint" copies came from rerun6 live fetches that had no URL header, so their URLs were rebuilt from the page's Item Number. The two press releases are cited as "usmint.gov press release (saved copy)" without an exact URL.

## Usage and estimated credit
| Item | Usage | Estimated cost |
|---|---|---|
| Search queries (Enterprise) | **122** (10 of them were test or probe queries; cap of 200 respected) | $0.49 at list price ($4 per 1,000). **$0** if covered by the 10,000-per-month free trial |
| Check Grounding | **95 calls**, **7,797,932 characters** sent (about 16,000 of those are the claims; the rest are Mint passages used as facts) | **Up to $5.85** if billed per 1,000 characters of all input, as the plan assumed. About $0.0001 if billed per call. Google's pricing page lists "$0.00075 / 1,000 count" without naming the unit |
| Index storage | 88 docs, about 2.2 MB of text | $0 (under the 10 GiB free tier) |
| Website index | 0 pages | $0 |
| **Total** | | **Most likely about $0 to $0.50; worst case about $6.34.** All Discovery Engine (Agent Builder credit) SKUs |

Note: the plan's estimate ("48 × 20,000 chars = under $0.01") was low. At $0.00075 per 1,000 characters, 960,000 characters is about $0.72. We actually sent about 40 to 80 thousand characters of Mint passages per check. If it's billed per character, the **$5 budget alert could fire** (it would still be credit, not Eric's card, as long as only Discovery Engine lines appear). Next time we can cap the facts at about 10 per check and cut this cost by 4 to 8 times.

## Billing and services check
- `gcloud billing projects describe numista-morgan-pilot`: billingEnabled true, on billing account 010E3C-D8346A-91A35E ("Numista.Ai").
- Per-SKU cost: **not available by API** (see above). **Billing was NOT unlinked**, because no non-credit SKU line was visible and nothing in this run uses Cloud Storage, Gemini, Compute or Cloud Run.
- Services enabled on numista-morgan-pilot: analyticshub, apptopology, bigquery, bigqueryconnection, bigquerydatapolicy, bigquerydatatransfer, bigquerymigration, bigqueryreservation, bigquerystorage, cloudapis, cloudtrace, dataform, dataplex, datastore, **discoveryengine**, logging, monitoring, servicemanagement, serviceusage, sql-component, storage-api, storage-component, storage, telemetry. Everything except discoveryengine is a Google default for a new project, and none was enabled by Grok tonight.

## Scrub (done on the box before upload)
- Removed: 313 Mint retail prices (shown as "[price removed]"), 5 "Welcome, [signed-in name]" banners, 2 promo codes, and 131 mentions of Eric's name in Morgan's notes (shown as "[owner]"). The Mint artist "Eric David Custer" was kept.
- No emails were found in the uploaded files. There were no price, value or collection columns in the packs. The `current_value` column (a catalog slot label, not money) was renamed `catalog_entry_now`.
- Not uploaded: the 19 empty PCGS files, `rerun6_pages\_REJECTED_FABRICATED\`, the Gemini review files, the contradictions files, the brain-inbox material and the README.

## Files
- `13 OCT 26\MORGAN_VERTEX_PILOT_RESULTS.csv`: 48 rows (row, claim, verdict, score, cited_url, quote). Where a row has more than one sub-claim, the quotes and URLs are joined with " || ".
- `13 OCT 26\MORGAN_VERTEX_PILOT_DETAILS.csv`: 100 sub-claims, with their scores, the full cited chunk, the first-pass scores, the W-claim scores and the queries.
- Raw API responses, saved on the laptop at `%TEMP%\morgan_pilot\run\` (one JSON per row) and `api_calls.log.jsonl`. No token is stored anywhere.

## For Eric in the morning
1. **Billing > Reports** for numista-morgan-pilot, grouped by SKU, last 7 days. Expect only Vertex AI Search or Discovery Engine lines, each with a matching credit line. Note what the Check Grounding line actually charges (somewhere between $0 and about $5.85).
2. If the $5 budget email arrives, it's most likely the Check Grounding characters. Look at the net cost after credits.
3. Decide whether to keep or delete the unused `usmint-site` store. A real usmint.gov crawl isn't possible without owning the domain.
4. Row 3 (Dr. Sally Ride): the Mint page lists P and D in the mint field and S only in the 3-roll set. Fine for REMOVE-W, but note it.
5. The next step that would actually use the credit: run the same check on the other programs. The **mintage-number** packs (ASE, Morgan, Proof Sets, etc.) are where Mint-versus-PCGS contradictions are likely to show up. That needs Eric's YES.
