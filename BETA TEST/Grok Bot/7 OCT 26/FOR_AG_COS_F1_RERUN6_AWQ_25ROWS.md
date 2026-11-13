# CoS GRADE + ORDER - F1 RERUN5 Batch 1 (AWQ) -> RERUN6 (25 rows only)
From: Grok Chief of Staff, for Eric Seaman. Wed 7 Oct 2026. DEV ONLY. No live writes.

## Grade: PARTIAL PASS (23 of 48 rows accepted)
CoS checked every quote against the saved page for THAT row (not all pages pooled together).

ACCEPTED (23 rows), with Morgan and AG independently agreeing on a real, saved Mint page:
- Rows 1,3,5,...,39 (the 20 W-UNC REMOVE rows). The saved Mint rolls/bags pages are genuine and their spec line reads
  "Mint and Mint Mark: Philadelphia – P Denver – D San Francisco – S". No W. Verdict stands.
  Two fixes for next time: quote the WHOLE line, not "Philadelphia –", and the notes saying "exclusively at Denver and Philadelphia" are wrong because San Francisco is listed too.
- Rows 44, 45, 46 (Pauli Murray, Patsy Takemoto Mink, Edith Kanakaʻole names). The quote is in that row's saved page.

NOT ACCEPTED (25 rows):
- Rows 2-40 even (the 20 S-SILVER-PROOF rows). 19 of the 20 saved PCGS page files are 0 bytes. The quotes are just honoree names (e.g. "Wilma Mankiller") or "PCGS #: 900690", which doesn't prove a 99.9% silver S proof exists.
- Rows 41, 42, 43, 48. No saved page for the row.
- Rows 47 and 48. Wrong values checked. Morgan proposes:
  - Row 47: "american_women_quarters_zitkala_sa_2024 (or keep id but fix slug/design_slug)". The pack verified "Dr. Mary Edwards Walker".
  - Row 48: "100 (unchanged if 20 W rows removed and 20 S-SILVER-PROOF rows added)". The pack verified "Dr. Sally Ride".
  Re-read each row's proposed_value from MORGAN SME DATABASE\EVIDENCE_PACK_2026-10-06_AWQ_SOURCED.csv.

## RERUN6 = only those 25 rows
1. S-SILVER-PROOF rows: use the U.S. Mint American Women Quarters SILVER PROOF SET pages (product codes 22WS, 23WS, 24WS, 25WS), via Wayback.
   Save each page's text ONCE as MORGAN SME DATABASE\rerun6_pages\<code>.txt; rows for the same year may share it.
   Quote the line that says 99.9% silver, and separately the line naming the honoree (two short quotes are fine).
   If a PCGS page is used too, the saved file must contain the page text. 0-byte files count as no source.
2. Rows 41/42: quote the spec line that shows S for the uncirculated rolls (row 41) and the S clad proof set page (row 42, 22WP-25WP).
3. Row 43: save the Stacey Park Milbern coin or rolls page and quote her name from it.
4. Rows 47/48: verify Morgan's REAL proposed values (above). Row 48 is arithmetic: show the math from the slot list.
5. All RERUN5 rules still apply: verbatim quotes, per-row saved pages, UNRESOLVED if you can't open a page.

## Outputs
- MORGAN SME DATABASE\GEMINI38_REVIEW_EVIDENCE_PACK_2026-10-07_RERUN6_AWQ_25ROWS.md
- MORGAN SME DATABASE\rerun6_pages\
- BETA TEST\Grok Bot\7 OCT 26\ACK_RERUN6.md (also list, by row number, which saved file holds each quote)

## Hard holds (unchanged)
Dev only. No sync_canon. No Brain / numismatic_reference_chunks writes. No F1 live apply, including for the 23 accepted rows, until all 48 rows pass and Eric gives his YES. No writes to Eric's collections.
