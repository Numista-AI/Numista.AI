# BATON P10 PRESIDENTIAL LABELS + CHECKLIST RENDER AUDIT (order 3: after P7, P8)
Holder: AG CoS. Ref: NET-087. Evidence: `1 NUMISTA.AI\BETA TEST\MY TESTING\14 OCT 2026\14 OCT Beta test, v2.docx` and `Presidential_Dollars_Collection_Progress.14 OCT 26, post purchase.pdf` (same folder).

## Problem
Eric reports his downloaded Presidential checklist labels William Henry Harrison as 'Benjamin Harrison'. Grok CoS note: the 12:06 PDF in the folder shows 2009 William Henry Harrison and 2012 Benjamin Harrison correctly, so the mismatch may be in a different export, the on-screen view, or the slot mapping (a W.H. Harrison coin landing in the B. Harrison slot). Find it.

## Task (dev only, diagnose then fix in code)
- SYSTEMIC: every Coin Program - compare names/labels across checklist PDF, on-screen checklist, scanner/AI result labels and master_coin_programs.json, against U.S. Mint program lists. Output a mismatch CSV (program, slot, each surface's label, Mint label).
- Pay special attention to same-surname pairs (Harrison, Adams, Johnson, Roosevelt, Bush, Cleveland 1st/2nd term).
- PDF render: the S Proof column shows ticks, X marks and blanks, and the header says 12/120. Determine whether these are the real PDF output (render a fresh PDF from the grokbot test account and compare) or Eric's own markup. If real, explain each mark and whether 12/120 is the correct count.
- Fix code/labels on dev with tests.

## Limits
Dev only. Cherry-pick only. No deploy without Eric's typed YES. NO data writes, no collection writes (Eric's or anyone's). Never fake data; U.S. Mint/Treasury beats PCGS/NGC. No PII or collection values in prompts or files.
## Log
- 2026-10-14 12:30 ET GROKCOS: issued. OVER.
- 2026-10-14 14:30 ET GROKCOS WATCH: STALL FLAG. Unmoved ~2h since issue (~12:30 ET). Correctly queued behind P7 (TOP PRIORITY). No Eric ping - critical AG work (P7/P4/P5/P6) last moved 12:40 ET (~110m, under 2h). See NET-090. OVER.

- 2026-10-14 15:57 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~3h25m). Correctly queued behind P7. AG critical path active (15:49/15:52), so no Eric ping. See NET-100. OVER.
- 2026-10-14 17:40 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~5h10m). Correctly queued behind P7. AG on P7 V5. No Eric ping. See NET-110. OVER.
