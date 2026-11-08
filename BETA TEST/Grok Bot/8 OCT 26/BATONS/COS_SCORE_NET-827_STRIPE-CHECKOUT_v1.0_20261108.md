# GB CoS score - NET-827 Stripe Checkout Preview Plan v1.0

**86/100 - FAIL (threshold >=95). Revise to v1.1 and resubmit. Do not send to SAG yet.**

Reviewed: `docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md` (14,869 bytes). Scored 2026-11-08 ~5:55 PM ET by GB CoS. PLAN-ONLY document review (not a Tier 1/2 build, so no GEMINI38 review required). Nothing was executed, no repo or Firestore access. Code line citations (payment_routes.py, tier_gatekeeper.py, main.py, estate_planning_screen.dart) were NOT independently verified in this pass; v1.1 should pin a commit SHA for them and a fresh reviewer will spot-check.

## Strengths
Standing locks are clear (plan only, main pinned at 9f04550a, Stripe off, alerts not caps). Secret Manager only. Webhook signature + stripe_events idempotency + "navigation never grants access" are well stated. Tax shown as unresolved. Test matrix TC-01..07 is concrete.

## Must-fixes
1. **Beta Special term contradiction.** Plan says "six calendar months" and codes `timedelta(days=182)`. 182 days is not six calendar months. Pick one (calendar-month add is recommended) and make sections 2.1, 4.4, TC-01 and the checklist agree.
2. **Promo codes do not match Eric's 7 Nov decisions.** Plan only sets `allow_promotion_codes=True`. Missing: (a) Christmas special = 50% off first year, yearly plans only, all tiers, usable 26 Nov through 25 Dec, not stackable with beta special or F&F code (coupon duration, applies_to / restrictions, redemption window, how non-stacking is enforced); (b) F&F / Beta Tester code = free accounts for friends and family only, max 500 redemptions, valid until beta testing ends, $10 AI first month then $5/mo, plus ability to buy at-cost AI tokens. State how Stripe objects (coupon, promotion code, max_redemptions, expires_at, restrictions) implement each, or mark the piece as unresolved for Eric. Do not print code values in the plan.
3. **F&F mechanism conflated.** Plan keys F&F on `is_lifetime_family_estate` (an estate-planning flag). F&F beta accounts are a different population. Define a separate entitlement flag/source or justify reuse, and say how a free (gratis) account interacts with Checkout and with the 500 cap.
4. **Idempotency ordering undefined.** Say whether the stripe_events doc is written before or after fulfillment, and what happens if fulfillment fails after the ledger write (event must be retryable). Use a transaction or write-after-success with a processing state.
5. **Subscription path under-specified.** Annual vs monthly price mapping, recurring interval, how `price_data` vs Stripe Price IDs are used, and handlers for `invoice.paid`, `customer.subscription.updated`, refunds/disputes (`charge.refunded`, `charge.dispute.created`) and `checkout.session.expired` are missing. At least list them as in or out of scope for preview. `invoice.paid` is listed for async one-time payments, where it does not apply.
6. **Metadata inconsistency.** Section 5.2 relies on `pre_checkout_coin_count` but the 4.1 metadata payload omits it.

## Nonblocking
- Target is named `p7-gate` in the baton and `origin/p7-v8.9` / `preview-catalog` in the plan; state the single canonical branch and preview URL.
- Section 5.1 contains garbled characters (mojibake) in the boundary bullets.
- Section 8 milestones are proposals; note the 20:00 ET deadline vs Eric's 5-day test window explicitly.
- Free tier 20 coins: cite the source decision.

Resubmit as v1.1 with a changelog mapping each must-fix. Expect a quick delta review.
