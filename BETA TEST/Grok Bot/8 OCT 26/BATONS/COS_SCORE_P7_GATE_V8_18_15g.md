# COS_SCORE_P7_GATE_V8_18_15g - Grok CoS gate score (23 Oct 2026, ~6:05 PM ET)
Build: V8.18.15g, commit 597e74a7 (p7-v8.9). Preview: numista-vault--p7-gate-8avtpz22.web.app (grokbot only).
Inputs: NET-454 (Argon PASS), NET-456 (preview ready), NET-457 (Field Tester), NET-458 (UX Designer).

## Verdict
- 15g's ONE fix (Review Hub commit 500 / ModuleNotFoundError numista_backend): **PASS on preview.** FT committed 1963-D Dime: "Added 1 coin.", no 500, 314->315.
- Manual duplicate: **PASS.** "Added 1 coin, flagged as possible duplicate", 315->316.
- 092052 multi-page invoice: **FAIL (known, queued).** FT: 60s timeout banner after "Done - 17 coins", all QTY 1, page-2 rows stamped page-1 invoice 67000011 / 2024-11-07, Hub +16 not 17. UX: no timeout this run (17 identified, 17 flagged dup, $298.55) - timeout is intermittent.
- **NOT deploy-ready.** No live-deploy YES ask to Eric yet. No deploys, nothing to main, no data writes by CoS.
- grokbot 314->316 = FT's 2 test coins (1963-D Roosevelt Dime, 2026-D Dime "FT-TEST 15g dup"). Not a leak. Cleanup held.

## New findings (added to queue)
1. "Upload a list" appears dead (UX). **NOT a P7 regression by code:** handler at p7-v8.9 add_coins_hub.dart:819-825 is byte-identical to origin/main (live) add_coins_hub.dart:329-335: `setState(() => _showMoreWays = true); _tabController.animateTo(0);`. It never opened a file picker on live either; it expands "More ways" and jumps to tab 0 (Upload). If already on tab 0 / already expanded, nothing visible happens -> UX/affordance bug, pre-existing. git log -L on L821-825 shows only P7 reflow commits (2aa65b50, c0965740, b3d63b78, ba37c03e), no behavior change. Runtime not re-verified by CoS.
2. Committed row stays in Review Hub after commit; badge jumped 39->56 (FT).
3. My Collection melt "$0.00 (offline)" (FT).
4. Firestore 403 on runAggregationQuery (FT) - likely rules on an aggregate count query.
5. My Collection "Date" column mostly blank; no reliable date-added (UX).
6. 18 console errors on My Collection (UX).
7. Review Hub "Add All (72)" mixes older pending rows from other imports; no per-import select (UX).
Carried: no "View Collection" button after import; Home vs My Collection melt mismatch ($2,186.57 vs $5,559.19).
