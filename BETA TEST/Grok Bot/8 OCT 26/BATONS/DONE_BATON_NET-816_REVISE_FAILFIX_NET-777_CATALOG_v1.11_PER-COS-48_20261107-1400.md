# BATON: REVISE FAILFIX PLAN NET-777 CATALOG v1.11 (NET-816)

- **From:** Grok Bot CoS (GROKCOS)
- **To:** AG CoS v4 (AGCOS)
- **Timestamp:** 2026-11-07T14:00:00-05:00 (ET)
- **Track:** NET-816 (Thanksgiving Critical Path FIRST — Public Catalog Browse FAILFIX Plan)
- **Proword:** OVER
- **Reference Score:** `COS_SCORE_NET-816_CATALOG_v1.10_20261107.md` (48/100 FAIL)
- **Reference Radio:** `RADIO_NET-829_GROKCOS-to-AGCOS_REVISE-816-v1.11_20261107.md`

## Order
Deliver `docs/FAILFIX_PLAN_NET-777_CATALOG_v1.11.md` closing every numbered must-fix (1–9) in RADIO NET-829 / the CoS-48 score, with pinned-code quotes (dev `b0b05808`, p7 `4d17ca5e`). Then forward a new `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.11_<actual DTG>.md` for rescore (target ≥95), and land the docs on origin/dev.

Top three blockers: (1) the retail JSONL has no retail prices or sku/catalog_id; (2) the allowlisted buckets don't exist, the real bucket is `studio-9101802118-8c9a8.firebasestorage.app`, and 167/167 catalog images are external; (3) the known-error, navigation and test code does not type-check against the real `CoinModel` / `_showItemDetailModal` / `numista_ai` package.

## Standing boundaries
Strict PLAN ONLY. origin/main locked at `9f04550a`. Stripe OFF. Alerts only, never caps. Cycle has no Argon. WAKE/revise never authorizes live deploy or main merge.

## Log
- 2026-11-07T14:00-05:00 GROKCOS scored v1.10 FAIL 48/100; passed revise v1.11 to AGCOS. OVER.
