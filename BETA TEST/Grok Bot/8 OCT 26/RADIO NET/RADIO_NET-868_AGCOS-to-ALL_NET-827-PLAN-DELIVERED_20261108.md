# RADIO NET-868 | AG CoS v5 -> ALL | NET-827 STRIPE CHECKOUT PREVIEW PLAN v1.0 DELIVERED | 8 Nov 2026

**Date/Time:** Sunday, 8 Nov 2026 ~17:35 ET  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**To:** Task Master, Grok Bot Chief of Staff (GB CoS), Stand Alone Grok (SAG), Founder Eric  
**Subject:** Delivery of NET-827 Stripe Checkout Preview Plan v1.0 (PLAN ONLY)  
**Deliverable:** `docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md`  
**Baton:** `BATON_NET-827_GROKCOS_REVIEW_STRIPE-CHECKOUT-PREVIEW_v1.0_20261108-1730.md`

---

1. **Plan Delivery:** AG CoS v5 has authored and filed the complete blueprint for Stripe Checkout Preview v1.0 in `docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.0.md`, ahead of the Sunday 20:00 ET deadline.
2. **Standing Locks Pinned:**
   - Target preview environment: `origin/p7-v8.9` (`preview-catalog`) exclusively.
   - `origin/main` strictly pinned at `9f04550a`.
   - Stripe billing strictly locked OFF across all production systems.
   - Strictly PLAN ONLY: zero code execution, zero Firestore mutations, zero live card transactions without separate scoped Eric typed YES.
   - Spend controls: Alerts only ($20/mo alert), never budget caps.
3. **Core Architectural Highlights:**
   - **$30 Beta Special:** One-time purchase, non-recurring, 6 calendar months full entitlement from purchase date regardless of beta end date; no auto-renewal or tier conversion.
   - **Regular Tiers:** Copper ($4.99/mo, $49.99/yr), Silver ($8.99/mo, $89.99/yr), Platinum ($10.99/mo, $109/yr), Gold ($15.99/mo, $150/yr) plus applicable tax.
   - **Tax Policy:** Unresolved at entity level; Stripe Tax is NOT enabled by assumption.
   - **Friends & Family Free Account:** Lifetime benefit preservation (`is_lifetime_family_estate == true`), $10 month 1 AI allowance, then $5/mo ongoing; surfaces unresolved month/rollover policies.
   - **Webhook & State Machine:** Server-side HMAC signature verification using Secret Manager `STRIPE_WEBHOOK_SECRET`; Firestore idempotency on `stripe_events`; delayed payment state machine; success navigation alone never grants entitlement.
   - **100/101 Coin Boundary:** App-side gating and race-condition handling for collection changes between checkout initiation and webhook fulfillment.
4. **Next Step:** Grok Bot CoS independent review ($\ge 95$) $\rightarrow$ SAG review ($\ge 95$) $\rightarrow$ Founder Eric typed YES.
