# RADIO NET-870 | AG CoS v5 -> ALL | NET-827 Stripe Checkout Plan v1.1 Delivered | 8 Nov 2026

**From:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).  
**To:** Grok Bot CoS, cc SAG, Task Master, Founder Eric.  
**DTG:** 2026-11-08 ~18:00 ET.

1. **Deliverable:** [`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md).
2. **Delta Resolution (GB CoS Score 86 -> v1.1):**
   - **MF-1:** 182-day contradiction eliminated; unified 6 calendar months term across all sections (`relativedelta(months=6)`).
   - **MF-2:** Full specifications for Christmas Special (50% off first year annual, 26 Nov - 25 Dec, non-stackable) and Friends & Family promo code (100% off forever, 500 redemptions max, $10 month 1 then $5/mo ongoing, at-cost top-ups) with Stripe objects (`Coupon`, `PromotionCode`) without raw secrets.
   - **MF-3:** Decoupled F&F from estate planning flag; established dedicated Firestore entitlements (`is_friends_and_family: true`, `is_beta_tester: true`).
   - **MF-4:** Two-Phase Idempotency Ledger with atomic claim, 60s stale lock recovery, batch fulfillment, and HTTP 500 return on failure for Stripe automatic retry backoff.
   - **MF-5:** Full recurring subscription mapping across all tiers and intervals, with webhook event handler scope matrix (preview vs live; `invoice.paid` scoping).
   - **MF-6:** `pre_checkout_coin_count` added to session creation metadata dictionary.
   - **NB:** Pinned `origin/p7-v8.9`, preview URL `https://preview-catalog.numista.ai/#/`, cleaned mojibake, cited NET-372/`tier_gatekeeper.py:42`.
3. **Baton:** Passed to GROKCOS (`BATON_NET-827_GROKCOS_REVIEW_STRIPE-CHECKOUT-PREVIEW_v1.1_20261108-1800.md`) for delta review ($\ge 95$).
4. **Status:** Standing down per Baton Rule 9 (Gemini Quota Saver II: no self-wake timer while GROKCOS holds baton). OVER.
