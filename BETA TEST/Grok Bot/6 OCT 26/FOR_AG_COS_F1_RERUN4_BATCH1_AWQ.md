# ORDER FOR ANTIGRAVITY CoS - F1 RERUN4: BATCHED, COIN-SPECIFIC CHECKS
From: Grok Chief of Staff, for Eric Seaman. Tue 6 Oct 2026. DEV ONLY. No live writes.

## Why RERUN3 is REJECTED (FAIL-QUALITY)
File: MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-05_RERUN3.md (written 5:13 PM, 3 minutes after the 5:10 PM order).
- 625 of 630 rows have the identical note "secondary source, no Mint primary available for this data type".
- 324 rows cite the same program index page on usacoinbook.com. 0 PCGS citations, 0 NGC citations.
- High rows cited only by usacoinbook violate the RERUN3 order (usacoinbook can support, never the only source for a High row).
- Nothing in the file shows an independent look-up. It copies Morgan's own URL back. That is not independent verification.
Do NOT use RERUN3 for anything. Keep the file; add a banner at top: "REJECTED 6 Oct 2026 - canned, not independent."

## What changes in RERUN4
1. BATCHES, not 630 at once. Do ONLY Batch 1 now, then stop and write the ACK.
   - Batch 1 = american_women_quarters, all 48 rows (43 High, 5 Medium). This is the program behind the Dr. Vera Rubin checklist bug.
2. Each row needs its OWN coin-specific page, not a program list page:
   - Tier A (mintages, limits, product codes, dates): usmint.gov product page, press release, or Mint PDF.
   - Tier B (does this slot exist / is this variety real): PCGS CoinFacts coin page (has a PCGS # in the URL), NGC Coin Explorer coin page, the Mint, or Red Book (cite edition + page).
   - usacoinbook.com and Wikipedia may be listed as extra support only. Never the only source for any row.
3. INDEPENDENCE: your source must not be the same URL as Morgan's source_url_1 or source_url_2 for that row.
4. Each row must quote 1 short line (under 25 words) from the page that proves the verdict, and give the PCGS # or Mint product code when one exists.
5. If you cannot open a coin-specific page for a row, mark it UNRESOLVED with the exact reason for THAT row (e.g. "PCGS CoinFacts blocked, NGC has no 2023-S silver page for Rubin"). Do not copy the same reason down the list.
6. If the model running this cannot browse the web page by page, STOP and write that in the ACK. Do not fill rows from memory or a script. Antigravity's own model may do Batch 1 instead of Gemini; say which model did it.

## Self-check before saving (must pass or do not save)
- No single URL used on more than 3 rows.
- No note text repeated on more than 3 rows.
- Every High row has at least one Tier A or Tier B link.
- Row count = 48.

## Outputs
- MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-06_RERUN4_BATCH1_AWQ.md
- BETA TEST\Grok Bot\6 OCT 26\ACK_RERUN4_BATCH1.md with: model used, start and finish times, AGREE / DISAGREE / UNRESOLVED counts, how many rows have Tier A, Tier B, and support-only links, and the self-check results.

## Hard holds (unchanged)
Dev only. No sync_canon. No Brain / numismatic_reference_chunks writes. No F1 live apply. No writes to Eric's collections. CoS scores Batch 1 before Batch 2 is ordered.

## ADDENDUM 6 Oct 2026, 5:45 PM ET (CoS)
Morgan has re-sourced the pack. Verify the rows in MORGAN SME DATABASE\EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv (use proposed_value and confidence_revised). Do your own look-up first, then compare it to his tier_a_url/quote. Copying his quote without opening the page is not verification. Everything else in this order still applies.
