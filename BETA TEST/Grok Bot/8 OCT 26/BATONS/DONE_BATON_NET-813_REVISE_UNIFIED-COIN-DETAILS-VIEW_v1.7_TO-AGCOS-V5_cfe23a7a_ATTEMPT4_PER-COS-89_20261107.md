# BATON NET-813 — Revise Unified Coin Details View to v1.7
- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Status:** OPEN
- **Attempt:** 4/4 (last try)
- **Score basis:** COS-89 on v1.6
- **DTG:** 2026-11-07 ~8:55 PM ET (America/New_York)
- **Radio:** `RADIO_NET-849_GROKCOS-to-AGCOS_REVISE-813-v1.7_20261107.md`
- **Scorecard:** `COS_SCORE_NET-813_UNIFIED-COIN-DETAILS_v1.6_20261107.md`

Revise `PLAN_UNIFIED-COIN-DETAILS-VIEW` to **v1.7** as a narrow delta on v1.6. Keep the closed call-site quotes, `_cachedCoinsDocs` wire-up, laws block, nav-in-State, `assets/config/`, Test 5, and Test 9.

Must-fixes: (1) §2.6 `:925` verbatim `const TextStyle(color: Colors.white60, fontSize: 12)`; (2) public open site `:466`/`:810` not `:315`; (3) Test 14 two succeeding Next steps + parent-index asserts; (4) Test 13 advance FakeClock after pump during in-flight laws fetch; (5) Test 11 widget uses `harness.firestoreService`; (6) Test 12 same owner fixture for guest redaction; (7) record commit `2dbb525e` in §12.

PLAN ONLY. Pin `4d17ca5e`. Main locked `9f04550a`. Stripe OFF. No Eric ping.
