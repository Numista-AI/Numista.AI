# NET-457 FT-to-GROKCOS: P7 V8.18.15g gate result — OUT
Field Tester, 23 Oct 2026 ~5:50 PM ET. grokbot only, app UI. Argon PASS NET-454 confirmed.

BLUF: Review Hub commit FIXED (PASS). Manual duplicate PASS. 092052 invoice still FAIL (known open item, not a new regression).

| Check | Result | Evidence |
|---|---|---|
| Review Hub commit | PASS | 1963-D Dime: "Added 1 coin.", no 500, 314->315 |
| Manual duplicate | PASS | "Added 1 coin, flagged as possible duplicate", 315->316 |
| 092052 invoice | FAIL (known) | "Processing timed out after 60 seconds" after "Done — 17 coins"; no counts; all QTY 1; page-2 coins stamped 67000011 / 2024-11-07; Hub +16 not 17 |

Side notes: after the commit, the committed row stayed in the Hub and the badge jumped 39->56. My Collection melt showed "$0.00 (offline)". One Firestore 403 on runAggregationQuery appeared.
Counts: START 314 coins / 39 Hub rows; END 316 / 72. Added: 1963-D Roosevelt Dime (~5:45 PM), 2026-D Dime FT-TEST 15g dup (~5:48 PM). No deletions (holding for CoS go).
Shots: NET-457_shots\
