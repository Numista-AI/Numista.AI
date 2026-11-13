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

- 2026-10-14 19:41 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~7h10m). Correctly queued behind P7. AG on P7 V7 (NET-116). No Eric ping. See NET-117. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH V2 (NET-121) + P7 preview hold. AG critical path on LIVE-AUTH. No Eric ping (overnight). See NET-122. OVER.
- 2026-10-14 21:35 ET GROKCOS WATCH: still queued behind P7/LIVE-AUTH (Rule 8). No hourly re-flag (NET-122 <1h). See NET-125. OVER.

- 2026-10-14 22:08 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH (ERIC) + P7 preview hold (Rule 8). No Eric ping (overnight). See NET-126. OVER.
- 2026-10-14 23:15 ET GROKCOS WATCH: hourly re-flag. Queued behind P7 preview hold (Rule 8); NET-129 also queued. No Eric ping (overnight). See NET-130. OVER.

- 2026-10-15 02:12 ET GROKCOS WATCH: still queued AGCOS_OVER behind P7 (Rule 8). Hourly re-flag NET-136. Not a stall. Overnight quiet. OVER.


- 2026-10-15 19:45 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.7 (Rule 8). Not a stall. Overnight quiet. See NET-230. OVER.

- 2026-10-15 21:12 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 V8.8 (Rule 8). Not a stall. Overnight quiet. See NET-234. OVER.


- 2026-10-15 22:15 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-238. OVER.

- 2026-10-15 23:38 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-242. OVER.

- 2026-10-16 00:45 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-245. OVER.

- 2026-10-16 02:05 ET GROKCOS WATCH: hourly re-flag. Still AGCOS_OVER queued behind P7 (V8.8 PASS code, awaiting AM preview + UX/FT; Rule 8). Not a stall. Overnight quiet. See NET-248. OVER.

