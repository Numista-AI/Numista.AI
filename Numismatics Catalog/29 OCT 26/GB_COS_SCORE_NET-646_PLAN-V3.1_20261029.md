# GB CoS Score: NET-646 Plan v3.1
Scored by: Grok Bot (Chief of Staff) | 7:09 PM ET, 29 Oct 2026 | Docs only, repo read-only at HEAD 9b55f3d9
Inputs: US_NUMISMATICS_CATALOG_IMPLEMENTATION_PLAN_V3.1.md + NET-646_V3.0_APPENDIX_WRITE_AUDIT.md (§11 additions)

## Score: 93 / 100 (NO-GO, pass mark 95). Trend: v2.9 88, v3.0 89, v3.1 93.

## v3.0 blockers
| # | Blocker | Status |
|---|---|---|
| A | Webhook / entitlement freeze | CLOSED. Tier is read at request time; webhook state comes from Stripe with status, marker in the same txn, 500 retry, daily reconcile, and email/key in metadata. |
| B | Forged count_weight_q on currency/world_items | CLOSED. _noServerKeysChanged on all three; delete clamps to 0..4 and floors at 0. |
| C | Free/guest ungroup bypass | CLOSED for the lifetime cap: lifetime_charged_q shortfall is charged at ungroup, and only server-linked set coins earn 1/4. |
| D | 500-doc limit | CLOSED. Batches of 150 with a resumable op record. |
| E | Writer guard holes | CLOSED in design. Library-level patch, .add wrapped, merge-set callers (main.py:1544/3757/1991, verified) moved to update(), client allowlist test. The repo has no async Firestore clients, so the patch scope is complete. |

## Checkout exploit claim: CONFIRMED in repo
- payment_routes.py:49-50: tier = req.tier.lower(); unit_amount = 2900 if estate/family_estate else 499 (inline price_data, L60-68). Any other string, including "sovereign" or "power_user", is charged $4.99/mo, and estate/family_estate $29/yr.
- payment_schemas.py: tier is a free str with no validation.
- payment_routes.py:73 metadata target_tier = client tier; L221-222 the webhook writes stripe_tier from it unvalidated.
- Plan §4.1/4.2 fix is correct: validate SOLD_TIERS, use env price ids only, fail closed, tier from the subscription price id. Not exploitable today because Stripe is not live.

## Remaining blockers
1. **Set fields stay client-editable after P3.** §6 says P3 update "stays as P1", where is_set/set_id/parent_set_id are client-writable, but §R1 text says "At P3 the server alone writes them." A client can clear set_id on a set coin, then funnel-group it again; group assumes 4→1 and subtracts 3 each time, so active_quarters drifts to 0 and capped paid tiers get unlimited room. Fix: add the three set fields to the P3 update deny, and have group/ungroup use the stored count_weight_q delta rather than assuming 4/1.
2. **Top-up purchases can be dropped.** The webhook skips any event older than stripe_event_hwm. A top-up checkout (payment mode) that arrives after a newer subscription event is ignored, so credits are paid for but never granted. Fix: exempt one-time payment events from the hwm check and rely on the event marker alone.

## Minor (not blocking)
- Restore on a read_only (cancelled) account is not specified. Recommend allow, since it only re-adds the user's own item.
- A.7 says 222 client constructions incl. scripts; my count of non-test .py is 149. Both point to P0 listing.
- First-month AI cap = full plan price means zero margin in month 1. Eric chose this; noted only.

## Founder-decision check
All 6:50 PM answers as stated by Claude (guest 5 items/20q, AI caps, first month = plan price, cancel read-only, basic CSV, Stripe gated on AI caps, estate→Gold, AJ named unlimited, Morgan counts, ungroup adds to lifetime) are reflected. Pending items are not penalized. No new invented decisions found. Wishlist rate limits are labelled as engineering defaults.

## Verdict
NO-GO at 93. Two small, specific edits (blockers 1-2) should clear 95. Do not execute.
