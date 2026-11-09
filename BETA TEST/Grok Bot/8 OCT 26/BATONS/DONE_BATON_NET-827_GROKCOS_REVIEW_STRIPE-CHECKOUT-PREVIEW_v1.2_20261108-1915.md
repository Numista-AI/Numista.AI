# BATON: NET-827 GROKCOS REVIEW STRIPE CHECKOUT PREVIEW v1.2
**Filed:** Sunday, 8 Nov 2026 19:15 ET  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**To:** Grok Bot Chief of Staff (GB CoS)  
**Track:** NET-827 (Stripe Checkout Preview v1.2)  
**Deliverable Document:** [`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md)  
**Authority Reference:** Founder Eric directives 7 Nov 2026 (11:41 AM & 11:42 AM ET), `RADIO_NET-827_STRIPE-CHECKOUT-PLAN-ORDER_20261107.md`, `RADIO_NET-871_GROKCOS-to-AGCOS_NET-827-v1.1-92-FAIL-REVISE_20261108.md`, `BATONS\COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.1_20261108.md`.

---

### Request for Delta Review (v1.1 -> v1.2)
AG CoS v5 has revised and delivered **`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.2.md`** resolving all 3 Must-Fixes and all 3 non-blocking polish items from Grok Bot CoS review (score 92):

1. **MF-1 (Christmas `redeem_by` Unix Timestamp Correction):**
   - Corrected `redeem_by` from `1766707199` (2025) to `1798243199` (25 Dec 2026 23:59:59 UTC).
   - Specified campaign window (Thanksgiving 26 Nov 2026 00:00:00 UTC through Christmas 25 Dec 2026 23:59:59 UTC) directly on `Coupon.create` and `PromotionCode.create` API calls (§3.2).
2. **MF-2 (Dropped `first_time_transaction` Restriction):**
   - Dropped `restrictions={'first_time_transaction': True}` completely. Aligned with Founder Eric's 7 Nov directive that the Christmas Special is usable by anyone from Thanksgiving through 25 Dec 2026.
3. **MF-3 (Annual-Only Enforcement Specification):**
   - Fully specified three-tier enforcement:
     (1) Server-side checkout session gating in `payment_routes.py:58`: `allow_promotion_codes = True` enabled only when `billing_cycle == 'annual'` (`interval == 'year'`); monthly subscription and Beta Special checkout sessions disable promo codes or reject Christmas promo code with HTTP 400.
     (2) Stripe Product architecture: static annual products use `Coupon.create(..., applies_to={'products': ['prod_annual_tiers']})`.
     (3) Webhook defense-in-depth: `checkout.session.completed` verifies `billing_cycle == 'annual'` before honoring discount.
4. **NB-1 (Aligned Expiration Example with Code):**
   - Aligned §2.1 example with §4.4 `relativedelta(months=6)`: a purchase on 12 Nov 2026 at 14:00:00 UTC expires on 12 May 2027 at 14:00:00 UTC (exact time of day preserved).
5. **NB-2 (Atomic Firestore Transaction & HTTP 500 on Active Lease):**
   - Phase 1 implemented via `@firestore.transactional` atomic check/claim. If a lease is currently `processing` and active (< 60s), raises HTTP 500 (instead of returning 200) to ensure Stripe webhook retry backoff continues if a processing worker fails.
6. **NB-3 (`invoice.paid` in Scope Matrix):**
   - Added `invoice.paid` to the §4.5 event matrix as in-scope for recurring subscription renewals (matching §4.4 and `payment_routes.py:220`).

Review score threshold: $\ge 95/100$ to proceed to Stand Alone Grok (SAG) review.

---

## Log
- 2026-11-08 ~17:55 ET GB CoS: scored 86/100 FAIL, six must-fixes. See COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.0_20261108.md and RADIO_NET-869. Passed to AGCOS (REVISE, OVER).
- 2026-11-08 ~18:00 ET AG CoS v5: Delivered PLAN v1.1 fixing all 6 must-fixes. Baton passed to GROKCOS for delta review (OVER).
- 2026-11-08 ~18:20 ET GB CoS: scored 92/100 FAIL, three must-fixes (Christmas promo details). See COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.1_20261108.md and RADIO_NET-871. Passed to AGCOS (REVISE, OVER).
- 2026-11-08 ~19:15 ET AG CoS v5: Delivered PLAN v1.2 fixing all 3 must-fixes and 3 polish items. Baton passed to GROKCOS for delta review (OVER).
