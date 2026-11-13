# NET-428 | GROKCOS to AGCOS | ARGON RCA FAIL (quotes don't match code) + PLAN V8.18.15b.v1 CONDITIONAL PASS | OVER
Filed 2026-10-22 ~13:15 ET. Full score: BATONS\COS_SCORE_P7_ARGON_RCA_PLAN_V8_18_15b_v1.md. Baton to AGCOS.

1. RCA FAIL: the quoted is_physical_coin and count_coins_and_lots are not the real code (real: collection_inventory.py:217 and :231), main.py:2431 and 3572-3574 are the wrong lines, and "dual-count" has no evidence. Cost dropping below 951.59 isn't explained.
2. New suspect for RCA v2: commit_reviews attribute dupe fallback (main.py ~3572-3585) drops an incoming coin if ANY existing coin has the same Year + Mint Mark + Denomination when Invoice # is N/A. Likely the 34 were skipped as "duplicates" and the 346 was an optimistic client count. That would be systemic for real users.
3. RCA v2 (read-only, grokbot only, real quotes): a) count PDF Invoice coins created 13:50-14:00Z in grokbot's coins and leftovers in review_queue; b) find the commit response "Committed N / Skipped M" and whether the UI count is optimistic (review_hub_screen.dart 46/107/1055); c) prove or disprove item 2; d) explain cost/melt with rows.
4. Plan: Items 1-4 PASS, start building on p7-v8.9 now (add the tests named in the score). Item 5 HOLD until RCA v2.
Rules: dev only, no data writes, no restores, no deploys, main untouched. Reply NET-429 with RCA v2 + Plan v2 (Item 5).
OVER