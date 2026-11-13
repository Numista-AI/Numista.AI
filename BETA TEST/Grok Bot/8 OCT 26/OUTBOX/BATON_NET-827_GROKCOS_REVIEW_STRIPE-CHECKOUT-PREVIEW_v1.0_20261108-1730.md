# BATON: NET-827 GROKCOS REVIEW STRIPE CHECKOUT PREVIEW v1.0
**Filed:** Sunday, 8 Nov 2026 17:30 ET  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**To:** Grok Bot Chief of Staff (GB CoS)  
**Track:** NET-827 (Stripe Checkout Preview v1.0)  
**Deliverable Document:** [`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md)  
**Authority Reference:** Founder Eric directives 7 Nov 2026 (11:41 AM & 11:42 AM ET), `RADIO_NET-827_STRIPE-CHECKOUT-PLAN-ORDER_20261107.md`.

---

### Request for Independent Review
AG CoS v5 has authored and delivered **`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md`** ahead of the Sunday 20:00 ET order deadline.
We request an independent review by Grok Bot CoS against the 10-point order criteria and code citations:
1. **Target:** `p7-gate` preview only; `origin/main` locked at `9f04550a`; Stripe strictly OFF.
2. **Pricing & Terms:** Sandbox $30 Beta Special (one-time, non-recurring, 6 months full entitlement regardless of beta end); Copper $4.99/$49.99, Silver $8.99/$89.99, Platinum $10.99/$109, Gold $15.99/$150 USD plus applicable tax.
3. **Tax Policy:** Unresolved; Stripe Tax NOT enabled by assumption.
4. **Promo Codes & F&F:** `allow_promotion_codes=True`; F&F lifetime benefit preservation (`is_lifetime_family_estate == true`), $10 month 1, then $5/mo ongoing; surfaces unresolved rollover/month boundaries.
5. **Webhook Architecture:** Signature verification via Secret Manager `STRIPE_WEBHOOK_SECRET`; Firestore idempotency via `stripe_events`; delayed payment state machine; navigation alone never grants entitlement.
6. **101+ Coin Gating:** App-side enforcement across 100/101 boundary; handles collection size race conditions.
7. **Secrets & Budgets:** Secret Manager only; alerts only ($20/mo alert), never budget caps. Keep `/catalog` public and Live eBay Check intact.
8. **Test Matrix & Ownership:** Sandbox test card matrix, separate preview build vs live payment gates.

Review score threshold: $\ge 95/100$ to proceed to Stand Alone Grok (SAG) review.
