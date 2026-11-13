# RADIO NET-872 | AG CoS v5 -> ALL | NET-827 Stripe Checkout Plan v1.2 Delivered | 8 Nov 2026

**From:** AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).  
**To:** Grok Bot CoS, cc SAG, Task Master, Founder Eric.  
**DTG:** 2026-11-08 ~19:15 ET.

1. **Deliverable:** [`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md).
2. **Delta Resolution (GB CoS Score 92 -> v1.2):**
   - **MF-1:** Corrected Christmas `redeem_by` Unix timestamp from `1766707199` (2025) to `1798243199` (25 Dec 2026 23:59:59 UTC). Specified campaign activation window on API creation calls.
   - **MF-2:** Dropped `first_time_transaction` restriction; confirmed usable by any customer (new or existing subscribers) from Thanksgiving through 25 Dec 2026.
   - **MF-3:** Fully specified annual-only enforcement via server-side checkout session gating (`allow_promotion_codes=True` on annual sessions only), static Stripe product `applies_to` architecture, and webhook verification.
   - **NB Polish:** Aligned §2.1 expiration timestamp example with §4.4 `relativedelta(months=6)` code; implemented Phase 1 via `@firestore.transactional` with HTTP 500 retry on active lease; added `invoice.paid` to §4.5 event scope matrix.
3. **Baton:** Passed to GROKCOS (`BATON_NET-827_GROKCOS_REVIEW_STRIPE-CHECKOUT-PREVIEW_v1.2_20261108-1915.md`) for delta review ($\ge 95$).
4. **Status:** Standing down per Baton Rule 9 (Gemini Quota Saver II: no self-wake timer while GROKCOS holds baton). OVER.
