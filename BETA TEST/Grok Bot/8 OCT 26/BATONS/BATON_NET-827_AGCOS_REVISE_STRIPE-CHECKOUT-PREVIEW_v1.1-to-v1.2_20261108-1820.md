# BATON: NET-827 GROKCOS REVIEW STRIPE CHECKOUT PREVIEW v1.1
**Filed:** Sunday, 8 Nov 2026 18:00 ET  
**From:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**To:** Grok Bot Chief of Staff (GB CoS)  
**Track:** NET-827 (Stripe Checkout Preview v1.1)  
**Deliverable Document:** [`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md)  
**Authority Reference:** Founder Eric directives 7 Nov 2026 (11:41 AM & 11:42 AM ET), `RADIO_NET-827_STRIPE-CHECKOUT-PLAN-ORDER_20261107.md`, `RADIO_NET-869_GROKCOS-to-AGCOS_NET-827-v1.0-86-FAIL-REVISE_20261108.md`, `BATONS\COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.0_20261108.md`.

---

### Request for Delta Review (v1.0 -> v1.1)
AG CoS v5 has revised and delivered **`docs/PLAN_NET-827_STRIPE_CHECKOUT_PREVIEW_v1.1.md`** resolving all 6 Must-Fixes from Grok Bot CoS review (score 86):

1. **MF-1 (182-day contradiction resolved):** Removed all 182-day references; unified Beta Special term across all sections as exactly 6 calendar months via calendar-month addition (`relativedelta(months=6)`).
2. **MF-2 (Promotions fully specified):**
   - Christmas Special: 50% off first year annual, window 2026-11-26 00:00:00 to 2026-12-25 23:59:59 UTC, `duration: "once"`, `applies_to: annual_price_ids`, non-stackable (`allow_promotion_codes: true` enforces max 1 code).
   - Friends & Family Beta Tester: 100% off forever (`percent_off: 100.0`, `duration: "forever"`), `max_redemptions: 500`, active until beta ends (`is_beta_tester: true`). Entitlements: $10 AI credit month 1, $5/mo ongoing, at-cost top-ups.
   - PII/Secrets: Zero raw secret codes printed; designated Secret Manager lookup.
3. **MF-3 (Decoupled F&F from Estate):** Established dedicated Firestore flags (`is_friends_and_family: true`, `is_beta_tester: true`, `beta_access_type: "friends_and_family"`). Preserved `is_lifetime_family_estate` strictly for estate planning (`estate_planning_screen.dart:170`).
4. **MF-4 (Two-Phase Idempotency Ledger & Failure Recovery):**
   - Phase 1: Atomic `create()` on `stripe_events/{event_id}` with status `processing` and 60-second stale lease recovery.
   - Phase 2: Batch user entitlement update.
   - Phase 3: Update `stripe_events/{event_id}` to `completed` or `failed`. If Phase 2/3 fails, transaction rolls back or raises HTTP 500, enabling Stripe automatic retry backoff.
5. **MF-5 (Subscription Path & Event Matrix):**
   - Recurring Stripe Price IDs mapped across all tiers with billing intervals (`month`, `year`).
   - Webhook scope matrix: Explicitly marked `invoice.paid` for subscription renewals; explicitly marked out-of-scope/deferred handlers (`customer.subscription.updated`, `customer.subscription.deleted`, `charge.refunded`, `charge.dispute.created`, `checkout.session.expired`).
6. **MF-6 (Metadata Payload):** Added `pre_checkout_coin_count` to §4.1 session creation `metadata` dictionary alongside user_id, tier, interval, and environment tags.
7. **Non-Blocking Cleanups:** Pinned canonical branch `origin/p7-v8.9`, preview URL `https://preview-catalog.numista.ai/#/`, cleaned mojibake, cited NET-372/`tier_gatekeeper.py:42` for 20-coin free tier, and cited commit `56701f92`.

Review score threshold: $\ge 95/100$ to proceed to Stand Alone Grok (SAG) review.

---

## Log
- 2026-11-08 ~17:55 ET GB CoS: scored 86/100 FAIL, six must-fixes. See COS_SCORE_NET-827_STRIPE-CHECKOUT_v1.0_20261108.md and RADIO_NET-869. Passed to AGCOS (REVISE, OVER).
- 2026-11-08 ~18:00 ET AG CoS v5: Delivered PLAN v1.1 fixing all 6 must-fixes. Baton passed to GROKCOS for delta review (OVER).
