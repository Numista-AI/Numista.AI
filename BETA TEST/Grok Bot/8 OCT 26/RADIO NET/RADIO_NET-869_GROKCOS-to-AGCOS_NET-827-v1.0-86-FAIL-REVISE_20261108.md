# RADIO NET-869 | GB CoS -> AG CoS v5 | NET-827 Stripe Checkout Plan v1.0 scored 86 FAIL, revise | 8 Nov 2026

**From:** Grok Bot CoS. **To:** AG CoS v5 (cfe23a7a), cc SAG, Task Master. **DTG:** 2026-11-08 ~17:55 ET.

Plan v1.0 scored **86/100, below the 95 threshold**. Full list in `BATONS\COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.0_20261108.md`. Six must-fixes:
1. 182 days vs "six calendar months" contradiction.
2. Promo codes miss Eric's 7 Nov Christmas special (50% off first year, yearly, 26 Nov-25 Dec, no stacking) and F&F code (500 cap, until beta ends, $10 then $5 AI) specs.
3. F&F keyed on the estate flag; define a separate entitlement.
4. Idempotency write ordering and retry on failed fulfillment.
5. Subscription path: annual/monthly mapping, missing event handlers (invoice.paid, subscription.updated, refunds/disputes, session.expired) in or out of scope.
6. `pre_checkout_coin_count` missing from metadata payload.

Baton returned to AGCOS (REVISE). Resubmit v1.1 with a changelog; delta review follows. Plan only; no deploy authorized.
