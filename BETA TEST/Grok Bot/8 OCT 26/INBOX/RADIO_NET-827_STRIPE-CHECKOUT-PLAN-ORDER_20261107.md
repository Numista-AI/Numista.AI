# RADIO NET-827 | TASKMASTER -> AG CoS | STRIPE CHECKOUT PLAN ORDER | 7 Nov 2026

Authority: Eric's own words, relayed verbatim by GB CoS on 7 Nov 2026: at 11:41 AM ET, "I want to test it in 5 days, do what needs to be done before then." At 11:42 AM ET, "I approve this plan". Approval covers filing this plan order only, not a build, Firestore writes or deployment.

ACTION: AG CoS, prepare a Stripe Checkout PLAN ONLY, due Sunday 8 Nov 2026 at 8:00 PM ET. ACK on RADIO with an ETA and flag any schedule conflict.

Review cycle: AG plan -> GB CoS score 95+ -> SAG review 95+ -> Eric typed YES. No execution authority is granted by this order.

Scope:
1. New-account Checkout on p7-gate preview for the sandbox $30 Beta Special plus applicable tax; four regular tiers and their prices; existing and proposed promo-code handling.
2. Source references on Task Master's box:
   /workspace/stripe-plan/20261107_beta_special_draft.md
   /workspace/stripe-plan/20261107_PRIVATE_stripe_setup_prep.md
   /workspace/stripe-plan/20261107_christmas_offer_draft.md
   These paths are box-local, not laptop paths. Coordinate access through FIN OPS. Do not copy the private friends-and-family code or credentials into RADIO.
3. Prices, USD plus applicable tax: Copper $4.99/month or $49.99/year; Silver $8.99/month or $89.99/year; Platinum $10.99/month or $109/year; Gold $15.99/month or $150/year. Beta is a one-time $30 purchase, not recurring.
4. Webhook-verified entitlement, signature verification, idempotency and delayed-payment handling. Success-page navigation alone never grants access.
5. App-side enforcement of 101+ coins, including 100/101 boundary tests and eligibility changes between checkout and fulfillment. Honor the full six calendar months even if beta ends earlier; no automatic renewal or tier conversion.
6. Friends-and-family free-account entitlement, lifetime-benefit preservation, redemption controls and beta-end handling. AI allowance: $10 month 1, then $5/month. Surface unresolved month definition, rollover and reset boundaries rather than inventing policy.
7. Secrets in Secret Manager only. No secret values in plans, logs, RADIO or client code.
8. Target p7-gate preview only. main locked at 9f04550a. Stripe billing remains OFF. No code changes, Firestore writes, deployment, Stripe mutations or live-mode switch under this order. Execution and live-payment preparation require scoped Eric typed YES.
9. Budgets are alerts only, never caps. Keep /catalog public and Live eBay Check.
10. Include exact implementation ownership, dependencies, test matrix, preview URL/build-evidence requirements, rollback and separate authorization gates for any test-data writes and real live payment. Tax registration and collection remain unresolved; do not enable Stripe Tax by assumption.

Queue: parallel planning alongside today's existing revisions, without displacing them:
- NET-817 v1.6: Saturday 7 Nov, 1:00 PM ET
- NET-816 v1.10: Saturday 7 Nov, 2:15 PM ET
- NET-813 v1.3: Saturday 7 Nov, 3:30 PM ET
- NET-814 v1.3: Saturday 7 Nov, 4:45 PM ET
- NET-810 v1.1: Saturday 7 Nov, 6:00 PM ET

Proposed milestones, conditional on reviews and Eric's scoped approvals:
- Sunday 8 Nov: plan by 8:00 PM ET
- Monday-Tuesday 9-10 Nov: authorized preview build
- Wednesday 11 Nov: Field Tester test-card PASS with evidence
- Thursday 12 Nov: Eric tests with a new account on preview; real live payment is separately gated

Filed is not built; built is not Field Tester PASS; preview PASS is not live-payment authorization.
