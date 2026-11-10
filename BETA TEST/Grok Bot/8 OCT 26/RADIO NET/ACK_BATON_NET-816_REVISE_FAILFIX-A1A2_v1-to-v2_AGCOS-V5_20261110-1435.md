# ACK — BATON NET-816 FAIL-FIX A1/A2 PLAN REVISE v1 -> v2 (AG CoS v5)
Filed: 2026-11-10 14:35 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to: `BATON_NET-816_AGCOS-V5_REVISE_FAILFIX-A1A2_v1-to-v2_CoS79_20261110-1400.md` & `COS_SCORE_NET-816_FAILFIX-A1A2_v1_79_REVISE_20261110.md` (Score 79/100 REVISE).

## 1. Score & Feedback Acknowledged
- Acknowledged score 79/100 (Attempt 1/10 on track; writer AG CoS v5 attempt 1/4).
- Material deductions D1 through D6 accepted in full:
  * **D1:** Close line-201 generic silver Morgan fallback for sub-dollar silver.
  * **D2:** Base dollar fallback on face value 1.00 or combined text (`morgan`/`peace`/`dollar`), not denom alone.
  * **D3:** Add regression tests (a)–(d) in `catalog_chunk1_face_value_and_card_test.dart`.
  * **D4:** Define bounded Field Tester check with pass/fail criteria.
  * **D5:** Specify `#/catalog` handling.
  * **D6:** Specify base commit/branch (`p7-v8.9` at `c547b7a0`), built SHA requirement, and rollback procedures for code and hosting channel.

## 2. Status & Invariants
- v1 plan bytes preserved. v2 plan being authored in new file:
  `PLAN_NET-816_FAILFIX-A1A2_CATALOG-REWRITE_AND_HALF-DIME-MELT_v2_AGCOS-V5_20261110.md`.
- **PLAN ONLY:** Zero code modified now. Zero git commits or pushes.
- Gating invariants maintained: `origin/main` pinned at `9f04550a`; live hosting, Firestore, and Stripe live mode remain strictly **UNTOUCHED**.
