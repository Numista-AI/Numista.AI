# GB CoS score - NET-827 Stripe Checkout Preview Plan v1.2

**96/100 - PASS (threshold >=95). Send to SAG for independent review. Do not treat this as a SAG score. No build or deploy authorized.**

Reviewed: `docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md` (28,899 bytes, mtime 7:00:58 PM ET, sha256 `273a3268933f9bc1dba25812deecec6c761b3e8de58fa23b45844f1e409ed39d`). Scored 2026-11-08 ~7:16 PM ET by GB CoS (evening AG plan handoff watch). Delta review of v1.1 92 FAIL. PLAN-ONLY document review (not a Tier 1/2 build). Nothing was executed; no Firestore writes; Stripe remains OFF; `origin/main` remains locked at `9f04550a`. Code citations remain pinned at `56701f92` on `origin/p7-v8.9` (unchanged from the v1.1 review). Plan file is on the working tree at commit `1d23f1a7`.

## What closed from v1.1
1. **MF-1 closed** for the expired-year bug. `1798243199` is 25 Dec 2026 23:59:59 UTC (verified). The operative API sample uses `PromotionCode.create(..., expires_at=1798243199)`. The old `1766707199` (25 Dec 2025) is gone except as changelog history. `first_time_transaction` is not used.
2. **MF-2 closed.** `restrictions={'first_time_transaction': True}` is dropped. Section 3.2 says the Christmas special is usable by any customer (new or existing) from Thanksgiving through 25 Dec 2026, matching Eric's 7 Nov rule.
3. **MF-3 closed.** Annual-only is specified three ways: (1) server-side session gating sets `allow_promotion_codes` only when `interval == "year"` and disables it for monthly and Beta Special; (2) optional Dashboard `applies_to` if static annual products are later provisioned; (3) webhook defense-in-depth rejects a Christmas coupon when `metadata.billing_cycle != 'annual'` and refunds. This matches the v1.1 ask to enforce annual-only even though checkout builds ad-hoc `price_data`.
4. **NB-1 closed.** Section 2.1 example is now a 12 Nov 2026 14:00:00 UTC purchase expiring 12 May 2027 14:00:00 UTC, matching `relativedelta(months=6)`.
5. **NB-2 closed.** Phase 1 uses `@firestore.transactional` atomic check/claim, and an active processing lease (< 60s) raises HTTP 500 so Stripe keeps retrying.
6. **NB-3 closed.** `invoice.paid` is in the section 4.5 matrix as in-scope for recurring renewals.

Prior v1.0 must-fixes (term, F&F flags, idempotency retry intent, subscription event matrix, `pre_checkout_coin_count`) stay closed.

## Remaining must-fixes
None.

## Nonblocking polish (do not block SAG)
- The changelog and checklist say the campaign window is on both `Coupon.create` and `PromotionCode.create`, but the `Coupon.create` sample still has no `redeem_by`. Add `redeem_by=1798243199` there for defense in depth; `expires_at` on the promotion code is the field Checkout actually uses.
- Stripe has no `starts_at` on coupons or promotion codes. `active=True` with a comment is not an activation timestamp. Spell out preview vs live: the sandbox code may be active now so TC-08 can run this week; a live-mode PromotionCode must not be active before 26 Nov 2026 00:00:00 UTC (create it then, or create it with `active=False` and flip it at Thanksgiving).
- Changelog cites `applies_to={'products': ['prod_annual_tiers']}` while section 3.2 uses four `prod_*_annual` placeholders gated on Dashboard provisioning. Do not treat invented product IDs as existing; server-side gating is the real enforcement while sessions use `price_data`.
- Disabling all promotion codes on monthly sessions also blocks Friends & Family (TC-07) unless the tester picks annual. Prefer rejecting only the Christmas code when `interval != 'year'` so F&F still works on a monthly checkout.

SAG should independently score the entire exact current plan (must reach >=95), then Founder Eric typed YES is the preview gate. Plan only; no deploy authorized.
