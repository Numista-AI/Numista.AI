# NET-473 FT-to-GROKCOS: P7 V8.18.15h gate result — OUT
Field Tester, 24 Oct 2026 ~8:20 AM ET. grokbot only, app UI. Argon PASS NET-469 confirmed. Preview only (not live).

BLUF: Review Hub commit PASS. Manual duplicate PASS. Invoice 092052 PARTIAL FAIL — no timeout and per-page invoice/date FIXED, but 2x items still import as QTY 1 (or split QTY-1 rows). Do not approve live deploy.

| Check | Result | Evidence |
|---|---|---|
| Review Hub commit | PASS | 1963-D Dime: "Added 1 coin.", no 500, 316->317 |
| Manual duplicate | PASS | "Added 1 coin, flagged as possible duplicate", 317->318 |
| 092052 — no 60s timeout | PASS | Done in ~70s, "(118s remaining)" mid-run, no timeout banner |
| 092052 — 17 rows | PASS (hub +17) | Hub 98->114; I tagged 16 new by Item # |
| 092052 — own page inv/date | PASS | p1: 67000011 / 2024-11-07; p2: 67226944 / 2025-01-23 |
| 092052 — 2x as QTY 2 | FAIL | 1964-D and 1982-S each as two QTY-1 rows; 2001-P seen as QTY 1 |

Counts: START 316 coins / 98 Hub; END 318 / 114. Added: 1963-D Roosevelt Dime (~8:14), 2026-D Dime FT-TEST 15h dup (~8:20). 17 invoice rows left uncommitted in Hub. No deletions (holding).
Side: Firestore 403 on runAggregationQuery; Settings "Clear Entire Collection" said 315 while My Collection said 316; melt/valuation $0 on new coins.
Shots: NET-473_shots\
