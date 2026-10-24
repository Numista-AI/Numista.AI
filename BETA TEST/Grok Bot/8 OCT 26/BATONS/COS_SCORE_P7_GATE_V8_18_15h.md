# COS_SCORE P7 GATE V8.18.15h (72cb6c0f) - Grok CoS, 24 Oct 2026 ~8:30 AM ET
Source: NET-473 (Field Tester, grokbot, p7-gate preview numista-vault--p7-gate-8avtpz22.web.app). Shots reviewed: c2_02_hub_a.png, c2_03_hub_b.png.

VERDICT: PARTIAL - HOLD FOR ERIC DECISION. Not deploy-ready yet.

| Check | FT | CoS score |
|---|---|---|
| Review Hub commit | PASS | PASS |
| Manual duplicate | PASS | PASS |
| 092052 no 60s timeout | PASS | PASS (fix 2A works) |
| 092052 per-page invoice/date | PASS | PASS (page 2 rows show 67226944, e.g. 21st Century Set ST5114) |
| 092052 row count | PASS (+17) | PASS on count, pending FT recount (see below) |
| 092052 2x as QTY 2 | FAIL | SPEC QUESTION, not a code defect |

Why the 2x result is a spec question: the approved Argon plan NET-460 (assertion 4) says "Each qty=2 item expands to 2 docs in review_queue". The build does exactly that: 1964-D and 1982-S each arrive as two QTY-1 rows, and the total (12 page-1 coins + 5 page-2 = 17) is right, so no coin is lost (the original bug was 2x importing as only 1 coin). FT expected one row at QTY 2. Which one is right is a product call only Eric can make.

Recount needed: the Hub still holds leftover 092052 rows from the 15g gate (no Item #, page-1 invoice on page-2 coins, e.g. 2017-P Native American Dollar with 67000011). That mixes old and new rows. FT tagged 16 new by Item #, so please confirm item 5021.60 (2001-P Kennedy Half) has TWO new rows (17 total).

Side findings (log, not blocking this gate): Firestore 403 on runAggregationQuery; Settings 'Clear Entire Collection' shows 315 vs My Collection 316; melt/valuation $0 on new coins (related to QUEUE item 2). Unit cost shows small allocated shipping/tax (e.g. 1963-D $17.10 line -> $18.22), consistent ~6.5 pct on all rows.

NEXT: Baton to ERIC for one decision: (A) keep 2x lines as two separate QTY-1 records (current build, each coin its own record for grading, selling, Certificate of Transfer) - Grok CoS recommends A; or (B) one record at QTY 2 (needs a V8.18.15i one-fix). After Eric picks: A -> FT recount of 2001-P, then Eric typed deploy YES; B -> Argon plan + AG build.
No deploys, nothing on main, no data writes. Live traffic still numista-backend-00479-beg.
