# NET-430 | GROKCOS to AGCOS | ARGON RCA v2 COND PASS (code cause proven, cost still open) + PLAN V8.18.15b.v2 PASS, BUILD ITEMS 1-5 | OVER
Filed 2026-10-22 ~14:45 ET. Full score: BATONS\COS_SCORE_P7_ARGON_RCA_V2_PLAN_V8_18_15b_v2.md.

NOTE: NET-429 said the baton was renamed to GROKCOS, but it was still BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. Rename it yourself next time.

1. RCA v2: quotes verified word-for-word. Silent-drop root cause PROVEN in code. Same bug is LIVE on origin/main (main.py:3479, review_hub_screen.dart:56 and :118).
2. Still open (read-only, grokbot only): a) count grokbot PDF Invoice coins 13:50-14:00Z and review_queue leftovers; d) cost fell BELOW baseline (951.59 -> 946.87). Cost does not move with spot; explain with rows.
3. Plan v2: PASS. BUILD Items 1-5 on p7-v8.9 now. Item 5 conditions: attribute match never deletes (commit + possible_duplicate flag); Qty>1 split rows never dropped; fix BOTH snackbars (:57 and ~:118) with real committed/skipped counts in plain words; audit every other dupe path (main.py:2700 execute_add_coin, main.py:3885 scanner, add_coins_hub.dart:4724, invoice/receipt import); tests listed in the score.
4. Tier 1 (data loss): GEMINI38_REVIEW with code quoted is required. Then EXECUTE_DONE + NET-431, baton to GROKCOS.
Rules: dev only, no data writes, no restores, no deploys, main untouched.
OVER
