# NET-014 GROKCOS to AGCOS (12 Oct 2026 ~8:05 PM ET)
V2 scores filed. All three ITERATE; T1 live smoke PASS.

- T2 Morgan Gate 0 V2 (9769dac5): ITERATE. See COS_SCORE_MORGAN_GATE0_BUILD_V2.md. Main item: get_coin_details strip list (main.py:2705-2707) misses the real field names "AI Estimated Value", "Purchase Cost", "purchase_cost", "Melt Value", "Price Paid", so values reach the AI on a plain question. One shared filter + real-shape test. 474/474 pytest confirmed on my run.
- T3 UX V2 (9fc13333): ITERATE, 2 small. PIN focus never re-requested on tap (login_screen.dart:610, no requestFocus); fontSize 12 at :1017 and 11 at :1037 slip past the 1000-line test window.
- T3b Alt site V2 (9fc13333): ITERATE. P0: numista_mobile/firestore.rules:105-106 lets the owner write users/{email} itself, where tier, stripe_tier, beta_tester live; the :77 profile guard matches no document. This is live today. Also :109-111 still overrides the coin is_demo guards (coins not excluded), and the emulator suite was not run (tests :95/:141/:159 would fail). See COS_SCORE_REQ032B_BUILD_V2.md.
- T1 REQ_031 live: PASS (COS_SCORE_REQ031_LIVE_SMOKE.md). Follow-up: main.py:5506 `except Exception` turns the 401 into a 500; check every endpoint for the same pattern.
- Still open: stale duplicate BATONS\BATON_T1_REQ031_AGCOS_WILCO.md - please delete (rule 1).

All four batons now AGCOS OVER. Dev only. No deploy without Eric's typed YES. OVER
