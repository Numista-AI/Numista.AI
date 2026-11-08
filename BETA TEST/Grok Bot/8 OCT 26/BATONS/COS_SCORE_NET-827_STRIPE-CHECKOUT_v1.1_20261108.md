# GB CoS score - NET-827 Stripe Checkout Preview Plan v1.1

**92/100 - FAIL (threshold >=95). Revise to v1.2 and resubmit. Do not send to SAG yet.**

Reviewed: `docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md` (23,956 bytes, mtime 5:51:16 PM ET). Scored 2026-11-08 ~6:20 PM ET by GB CoS (evening AG plan handoff watch). Delta review of v1.0 86 FAIL. PLAN-ONLY document review (not a Tier 1/2 build). Nothing was executed; no Firestore writes; Stripe remains OFF; `origin/main` remains locked at `9f04550a`. Code citations were spot-checked at the plan's pin `56701f92` on `origin/p7-v8.9`.

## What closed from v1.0
1. **MF-1 closed.** No leftover `timedelta(days=182)`. Sections 2.1, 4.4, TC-01, and the checklist use six calendar months via `relativedelta(months=6)`.
2. **MF-3 closed.** F&F uses dedicated `is_friends_and_family`, `is_beta_tester`, and `beta_access_type: "friends_and_family"`. `is_lifetime_family_estate` is left to estate planning (`estate_planning_screen.dart:170` verified at the pin). $0 checkout fulfillment and Stripe `max_redemptions: 500` are specified. No promo-code secrets are printed.
3. **MF-4 closed** for the asked point (write-before-fulfillment with a `processing` state; mark `failed` and return HTTP 500 so Stripe retries). See polish below.
4. **MF-5 closed.** Annual vs monthly mapping uses `price_data` plus `TIER_PRICES_CENTS[tier][interval]` with `recurring.interval` `month`/`year`. Preview vs production event matrix lists checkout completed/async success/fail, `invoice.payment_failed`, `customer.subscription.updated`/`deleted`, and `checkout.session.expired` as in-scope; `charge.refunded` and `charge.dispute.created` are Phase 2. `invoice.paid` is correctly limited to recurring renewals in §4.4 (add it to the §4.5 table in polish).
5. **MF-6 closed.** `pre_checkout_coin_count` is in the §4.1 metadata payload and §5.2 still uses it.
6. **Nonblocking from v1.0 closed.** Canonical branch is `origin/p7-v8.9`; preview URL is `https://preview-catalog.numista.ai/#/` (`p7-gate` channel). §5.1 mojibake is gone. Free-tier 20 coins is cited to NET-372 and `tier_gatekeeper.py:42` (`TIER_COIN_LIMITS["free"] = 20` verified at the pin, lines 41-50). §8.1 distinguishes the Sunday plan-delivery gate from Eric's Thursday 12 Nov 5-day test target.

## Citations verified at `56701f92`
- `numista_backend/tier_gatekeeper.py:41-50` — `TIER_COIN_LIMITS["free"] = 20`; Copper/Silver/Platinum/Gold map to `pro`/`numismatist`/`dealer`/`estate`.
- `numista_backend/routes/payment_routes.py:32-80` — checkout session route; `:35` `Depends(get_current_user)`; `:58` `allow_promotion_codes=True`.
- `payment_routes.py:166-241` webhook; `:182` `construct_event`; `:229-232` 3-day grace; `:238` `lock_overflow_coins(..., TIER_COIN_LIMITS["free"])`.
- `numista_backend/main.py:160-162` — `/webhook` and `/api/stripe/webhook` are in `_PUBLIC_PATHS` (paths on 161-162).
- `estate_planning_screen.dart:170` — `is_lifetime_family_estate` (cited in the baton; plan body correctly leaves the flag untouched).

## Remaining must-fixes (all leftover from MF-2)
1. **Christmas `redeem_by` timestamp is the wrong year.** Prose says the window is 26 Nov 2026 00:00:00 UTC through 25 Dec 2026 23:59:59 UTC, but `redeem_by: 1766707199` is 25 Dec **2025** 23:59:59 UTC. The correct Unix time for 25 Dec 2026 23:59:59 UTC is `1798243199`. As written, a coupon created with that timestamp would already be expired. Put `redeem_by` (and how the code becomes active at 26 Nov 2026 00:00:00 UTC) on the actual `Coupon.create` / `PromotionCode.create` calls, not only in the surrounding sentence.
2. **`restrictions={'first_time_transaction': True}` contradicts Eric's 7 Nov rule** that the Christmas special is usable by anyone from Thanksgiving through 25 Dec. Drop that restriction unless Eric separately directs it.
3. **Annual-only enforcement is not implemented in the Stripe objects.** The plan says Christmas is 50% off the first year of yearly plans only, but `Coupon.create(percent_off=50.0, duration='once', ...)` has no `applies_to` (or equivalent), and checkout builds ad-hoc `price_data` so there are no annual Price IDs to attach. State how the coupon is limited to annual prices — create annual Price IDs and use `applies_to`, or reject the code server-side when `interval != 'year'` — without inventing Price IDs that do not exist.

## Nonblocking polish
- §2.1's example expires at 23:59:59 UTC, but the §4.4 code is `purchased_at + relativedelta(months=6)` (a 14:00 UTC purchase would expire at 14:00 UTC). Pick one and make the example match the code. Operative sections already agree on calendar-month add, so this is not a reopen of MF-1.
- Phase 1 is a get-then-set, not an atomic `create()` or Firestore transaction, despite the checklist saying "atomic check/claim". Two concurrent deliveries could both pass the read. Also, returning HTTP 200 for `in_progress` can stop Stripe retries if the first worker crashes inside the 60-second window; return 500 (or similar) so Stripe keeps retrying after the stale lock expires.
- Add `invoice.paid` to the §4.5 matrix as in-scope for recurring renewals, matching §4.4 (current code at `payment_routes.py:220` already groups it with subscription updates).

Resubmit as v1.2 with a changelog mapping these three must-fixes. Expect another quick delta review. Plan only; no deploy authorized.
