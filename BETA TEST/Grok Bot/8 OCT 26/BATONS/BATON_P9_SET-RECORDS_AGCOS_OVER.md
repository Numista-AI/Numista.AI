# BATON P9 SET / PACKAGING RECORDS - PLAN ONLY (order 4: after P7, P8, P10)
Holder: AG CoS. Ref: NET-087. Beta notes: `1 NUMISTA.AI\BETA TEST\MY TESTING\14 OCT 2026\14 OCT Beta test, v2.docx`.

## Task: write PLAN_V1_SET_RECORDS.md (no schema change, no code)
Design a set/packaging record that links the coins inside it:
- Fields: maker/distributor (e.g. PCS Stamps & Coins / MBI, Danbury Mint, U.S. Mint), product/program name, product code (e.g. PCS 'PDO'), packaging type (3-coin slab, chest), certificate/COA, issue year, linked coin items (P/D/S slots).
- Fast entry: Eric must be able to log his 20 PCS Presidential 3-coin P/D/S sets quickly (pick the set template once, then per president add 3 linked coins, filling checklist slots and allowing duplicates per P7).
- Show how sets appear on the checklist, the PDF report, the collection count (tie into the P2 count logic) and the estate report.
- Migration/back-compat, Firestore rules, tests, rollout steps.
- Finish claims (e.g. 'business strike, not satin finish' and 'S = clad proof from Proof Set') are UNVERIFIED (Gemini text in the beta notes). Plan a Morgan check against U.S. Mint sources; mark UNKNOWN where it can't be cited. Fabricate nothing.

## Gate
Plan.v1 -> Gemini review -> GROKCOS score -> Eric typed YES -> only then build.

## Limits
Dev only. Cherry-pick only. No deploy without Eric's typed YES. NO data writes, no collection writes (Eric's or anyone's). Never fake data; U.S. Mint/Treasury beats PCGS/NGC. No PII or collection values in prompts or files.
## Log
- 2026-10-14 12:30 ET GROKCOS: issued, PLAN ONLY. OVER.
- 2026-10-14 14:30 ET GROKCOS WATCH: STALL FLAG. Unmoved ~2h since issue (~12:30 ET). Correctly queued behind P7 (TOP PRIORITY). No Eric ping - critical AG work (P7/P4/P5/P6) last moved 12:40 ET (~110m, under 2h). See NET-090. OVER.

- 2026-10-14 15:57 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~3h25m). Correctly queued behind P7. AG critical path active (15:49/15:52), so no Eric ping. See NET-100. OVER.
- 2026-10-14 17:40 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~5h10m). Correctly queued behind P7. AG on P7 V5. No Eric ping. See NET-110. OVER.

- 2026-10-14 19:41 ET GROKCOS WATCH: hourly re-flag. Unmoved since issue ~12:30 (~7h10m). Correctly queued behind P7. AG on P7 V7 (NET-116). No Eric ping. See NET-117. OVER.

- 2026-10-14 20:41 ET GROKCOS WATCH: hourly re-flag. Queued behind LIVE-AUTH V2 (NET-121) + P7 preview hold. AG critical path on LIVE-AUTH. No Eric ping (overnight). See NET-122. OVER.
