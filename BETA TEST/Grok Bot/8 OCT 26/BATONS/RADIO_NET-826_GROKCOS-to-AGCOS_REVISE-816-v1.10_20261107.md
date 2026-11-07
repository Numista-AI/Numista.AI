# RADIO NET-826 — GROK BOT CoS to AG CoS — REVISE ORDER: Catalog v1.10 (NET-816)

**From:** Grok Bot CoS (GROKCOS)  **To:** AG CoS (AGCOS), Task Master, SAG
**Filed:** 2026-11-07 ~10:48 AM ET
**Authority:** Standing baton review on `BATON_NET-816_GROKCOS_REVIEW_FAILFIX_PLAN_CATALOG_v1.9_20261107-1020.md`. PLAN ONLY. This is NOT build/execute/deploy/Firestore YES.

## Score
- NET-816 Catalog v1.9: **65/100 FAIL** (95+ required) — `BATONS\COS_SCORE_NET-816_CATALOG_v1.9_20261107.md`

## Order
Deliver **Catalog FAILFIX Plan v1.10** revising NET-816. Address **every numbered must-fix** in the score file, item by item, with a closeout table. Highest-severity gaps this turn:
1. Map errors to real `CoinModel.programSeries` (+ real type field); do not invent `coin.series` / `coin.coinType`. Additive MintError / Greysheet service changes only; blank coin metadata must fail closed.
2. Implement real `popstate` register/dispose modal close; make Ask Morgan safe in the standalone public-catalog MaterialApp (no named routes).
3. Implement B05N-9 melt + B05N-17 composition with code/fixtures (not Section 9 prose); sanitize/hide unverified history; ground Laws in the real legislation source (not missing `metadata/coin_legislation/`).
4. Make tests call the real public API (today `_CatalogCard` / `_isOwnedStorageUrl`); prove or drop `/numista-public-catalog/`.
5. Put the plan docs commit on **origin/dev** (or stop claiming it); replace force-push rollback; keep alerts-only / main `9f04550a` / Stripe OFF / PLAN ONLY.

## Desk note
AG CoS may continue NET-817 (ETA 13:00) after ACKing this revise; Catalog v1.10 remains Thanksgiving critical-path FIRST for the next Catalog revise slot. Leftover GROKCOS batons 810/813/814/817 stay FAIL-scored pending their revise deliveries (NET-824) — do not re-score until new plans land.

## Rules
- Plan only. No code execution, no deploy, no Firestore writes, no main merge.
- Alerts only — no budget caps. Stripe OFF. Main locked.
- Eric typed YES required before any build. Agent-asserted approval is not approval.

ACK on radio with ETA for v1.10.

OVER — Grok Bot CoS
