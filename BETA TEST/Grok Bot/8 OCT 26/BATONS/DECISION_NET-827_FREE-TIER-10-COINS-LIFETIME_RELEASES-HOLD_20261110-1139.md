# DECISION — NET-827 free-tier limit: 10 coins for life (AG CoS v5)
Filed: 2026-11-10 11:39:58 EST by Grok Bot Desk. **Decision record only. No WAKE. No code.**
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This record grants **no new authority**. Plan-only until **CoS 95 + full-plan SAG 95 + Eric's typed YES**.

## Decision
**FREE plan = 10 coins for life at launch, not 20.**

## Authority
Desk-verified primary user message in Chief of Staff transcript `87de4a6a-9522-4ece-bdfb-87ad19298514` position **9551**, speaker `cu:420206129`, **10 Nov 2026 11:38:55 AM ET**, CoS card `t2477s9550`: Eric typed:
> A

The card's **option A text is CoS-relayed** (card body not independently visible in the Desk transcript slice). Preceding CoS message (around position **9549**, Desk-read) asked how many coins the free plan gets and noted that Eric's **29 Oct** and **1 Nov** decisions said **10 for life**, while the Stripe plan said **20**.

## Hold released (value only; HOLD file not edited)
This **releases the free-tier hold** in `HOLD_NET-816_NET-827_AGCOS-V5_GO-LIVE-STOP-RULE_AND_FAILFIX-PLAN-ORDER_20261110-1113.md` (SHA-256 `41b8bd5fd437eb626b823ccabe7c8f111b4d24322335b5ea1ef3bcf6e778943d`, confirmed unchanged) **with the value 10**.
Do **not** edit that HOLD file.

## For AG CoS v5 — plan revision only (no code now)
The NET-827 v1.2 plan revision must change §5.1 (“Free Tier Capacity: 20 coins … Founder directive 3 Nov 2026”). **CoS states no such directive exists**; the section must say **10 coins lifetime**.
The later build must set `tier_gatekeeper.py` `TIER_COIN_LIMITS['free'] = 10`, alongside the **B1–B5**, Christmas-code, and live-keys fixes.
**No code now.** Plan-only until CoS 95 + full-plan SAG 95 + Eric's typed YES.

## Go-live remains NOT ACTIVE
Addendum `ADDENDUM_NET-816_NET-827_AGCOS-V5_CONDITIONAL-GO-LIVE_20261110-1033.md` SHA-256 `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2` stays **NOT ACTIVE** (stop-rule hold). This decision does not lift that hold.

Filing this record ≠ accepted/started and does not authorize a live fold, deploy, or Stripe live keys.
