# ACK — DECISION Free Tier 10 Coins Lifetime & HOLD Preview Deploy at c547b7a0 (AG CoS v5)
Filed: 2026-11-10 12:25 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to:
1. `DECISION_NET-827_FREE-TIER-10-COINS-LIFETIME_RELEASES-HOLD_20261110-1139.md`
2. `HOLD_NET-816_PREVIEW-DEPLOY_c547b7a0_NOT-REISSUED_AWAIT-A1A2-FIX_20261110-1148.md`

## 1. NET-827 Free-Tier Limit Decision Acknowledged (10 Coins Lifetime)
- Received and acknowledged Eric's authoritative decision (`cu:420206129` Option A): **FREE plan = 10 coins lifetime at launch, not 20**.
- Supersedes previous interim ACK §4.
- Logged for inclusion in the NET-827 v1.2 plan revision (§5.1 corrected from 20 to 10 coins lifetime; `tier_gatekeeper.py` `TIER_COIN_LIMITS['free'] = 10` in subsequent build).
- Strict PLAN ONLY mode maintained; zero code modified now.

## 2. NET-816 Preview Deploy at c547b7a0 HELD
- Received confirmation of AG CoS v5's named BLOCKED record (`BLOCKED_BATON_NET-816_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1140.md`).
- Fully honored: `c547b7a0` preview deploy is **HELD and will NOT be retried**.
- Preview deploy will only occur against the subsequent A1/A2-fixed commit after that fail-fix plan passes CoS 95 + SAG 95 + Eric's new scoped typed YES.

## 3. Standing Governance Invariants
- `origin/main` strictly pinned at `9f04550a`. Zero merges or direct pushes.
- Production live hosting (`numista.ai`) strictly untouched.
- Stripe live mode remains strictly **OFF**; live keys not attached.
- Go-live addendum remains **NOT ACTIVE**.
