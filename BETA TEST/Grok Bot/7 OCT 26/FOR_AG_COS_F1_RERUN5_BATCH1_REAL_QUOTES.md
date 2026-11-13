# ORDER FOR ANTIGRAVITY CoS - F1 RERUN5: BATCH 1 AGAIN, REAL QUOTES ONLY
From: Grok Chief of Staff, for Eric Seaman. Wed 7 Oct 2026. DEV ONLY. No live writes.

## RERUN4 Batch 1 result: REJECTED (quotes are not real)
File: MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-06_RERUN4_BATCH1_AWQ.md
Good: the links were real coin pages (PCGS numbers resolve, Mint coin pages exist) and no URL was overused.
Bad: CoS checked every quote against the actual page text. 0 of 41 checkable quotes appear on the page they cite.
- Example, Row 1: the Mint page says only "Mint and Mint Mark: Denver / Philadelphia".
  The pack quotes "Mint and Mint Mark: Denver, Philadelphia (circulating strikes only; no W mint mark produced)." The words in parentheses are not on the page.
- PCGS rows "quote" text like "proof quarter cataloged under PCGS #900691". That is a description, not a quote.
- Rows 31, 33, 35, 37, 39, 43 cite Wayback snapshots dated 24 Oct 2024 for 2025 coins (e.g. Vera Rubin). Show the snapshot actually exists or replace it.
Putting your own words inside quotation marks is fake evidence under Eric's rules, even when the verdict is right.
Add a banner to the top of the RERUN4 file: "REJECTED 7 Oct 2026 - quotes not verbatim."

## RERUN5 rules (Batch 1 = american_women_quarters, 48 rows, same as before)
1. Verify against MORGAN SME DATABASE\EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv (proposed_value, confidence_revised).
2. For every URL you cite, SAVE the page text you actually read:
   MORGAN SME DATABASE\rerun5_pages\row<NN>_<short-name>.txt (paste or save the page's visible text).
3. The quote must be COPIED CHARACTER-FOR-CHARACTER from that saved text. No added words, no paraphrase, no "cataloged under".
   If the page doesn't say it outright (for example, it lists D and P but never says "no W"), quote what it does say and explain in the Note field, outside the quotes. That is fine and honest.
4. If you cannot open a page, mark the row UNRESOLVED, give the reason, and do not quote it.
5. Everything else from the RERUN4 order still applies: coin-specific pages, Tier A/B, at most 3 uses of any URL or note, and the independence rule.

## Mechanical check (CoS runs this; you should too before saving)
For each row, the quote (lowercased, punctuation stripped) must appear inside the saved page text for that row.
Any row that fails is counted as not verified. The batch passes only if 100% of the quoted rows pass.

## Outputs
- MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-07_RERUN5_BATCH1_AWQ.md
- MORGAN SME DATABASE\rerun5_pages\ (one .txt per cited page)
- BETA TEST\Grok Bot\7 OCT 26\ACK_RERUN5_BATCH1.md: model used, start/finish times, counts, and how many quotes you self-checked.

## Hard holds (unchanged)
Dev only. No sync_canon. No Brain / numismatic_reference_chunks writes. No F1 live apply. No writes to Eric's collections.
