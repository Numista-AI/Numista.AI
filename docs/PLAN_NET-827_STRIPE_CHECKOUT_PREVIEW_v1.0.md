# PLAN NET-827: Stripe Checkout Preview v1.0 (p7-gate Preview Gated)

**Document Version:** 1.0  
**Date:** Sunday, 8 November 2026  
**Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Authority:** Founder Eric verbatim directives:  
- 7 Nov 2026, 11:41 AM ET: *"I want to test it in 5 days, do what needs to be done before then."*  
- 7 Nov 2026, 11:42 AM ET: *"I approve this plan"* (Approval covers filing this plan order only; NOT a build, Firestore writes, or live deployment).  
**Review Cycle:** AG CoS Plan -> Grok Bot CoS Review ($\ge 95$) -> Stand Alone Grok (SAG) Independent Review ($\ge 95$) -> Founder Eric Scoped Typed YES.

---

## 1. Operational Constraints & Standing Locks

> [!IMPORTANT]
> **Strict Operational Boundaries (Always Enforced):**
> 1. **PLAN ONLY Mode:** Strictly zero code execution, zero production deployments, zero live Firestore mutations, zero Stripe live-mode mutations, and zero live card charges authorized under this document.
> 2. **Target Environment:** `p7-gate` preview branch (`origin/p7-v8.9` / `preview-catalog`) exclusively. Zero code merged to `main`.
> 3. **Repository Locks:** `origin/main` strictly pinned and locked at commit `9f04550a`.
> 4. **Stripe Production Status:** Stripe billing is strictly **LOCKED OFF** across all production environments.
> 5. **Spend Controls:** Standing rule: **Alerts only, NEVER budget caps** ($20/month alert configured; hard spending caps prohibited).
> 6. **Public Endpoints:** Public `/catalog` browsing and Live eBay Check must remain 100% public and ungated.
> 7. **Secrets Integrity:** All Stripe API keys and webhook signing secrets reside in Google Cloud Secret Manager only. Zero raw keys, test credentials, or private promo codes in plans, commit history, radio messages, or client bundles.

---

## 2. Product Architecture & Pricing Model

### 2.1 Sandbox $30 Beta Special
- **Nature:** One-time, non-recurring purchase ($30.00 USD plus applicable tax).
- **Checkout Mode:** Stripe Checkout `mode='payment'` (NOT `mode='subscription'`).
- **Entitlement Period:** Exactly **six (6) calendar months** (182 days) from the timestamp of webhook fulfillment.
- **Beta-End Independence:** Full 6 calendar months honored even if the public beta test concludes earlier.
- **Renewal / Conversion Policy:** Zero automatic renewal; zero automatic tier conversion. At expiration, account gracefully transitions to free tier coin limits with overflow lock protections unless the user manually elects to purchase an ongoing subscription tier.

### 2.2 Standard Subscription Tiers (USD plus applicable tax)
When launched post-beta, regular ongoing tiers operate via Stripe Checkout `mode='subscription'`:

| Tier | Monthly Price | Annual Price | Annual Savings | Coin Capacity | Daily DeepDive AI | Daily Invoice Scans |
|---|---|---|---|---|---|---|
| **Copper** | \$4.99 / mo | \$49.99 / yr | ~16% | 100 coins | 25 / day | 15 / day |
| **Silver** | \$8.99 / mo | \$89.99 / yr | ~17% | 250 coins | 50 / day | 30 / day |
| **Platinum** | \$10.99 / mo | \$109.00 / yr | ~17% | 500 coins | 100 / day | 50 / day |
| **Gold** | \$15.99 / mo | \$150.00 / yr | ~22% | 1,000 coins | 500 / day | 250 / day |

*Note: Existing internal tier aliases (`pro`, `numismatist`, `dealer`, `estate`) in [`numista_backend/tier_gatekeeper.py:41-50`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L41-L50) map directly to the market tiers (Copper $\rightarrow$ `pro`, Silver $\rightarrow$ `numismatist`, Platinum $\rightarrow$ `dealer`, Gold $\rightarrow$ `estate`).*

### 2.3 Tax Policy
- Tax registration, multi-jurisdiction nexus, and tax collection policies remain **UNRESOLVED** at the business entity level.
- **Strict Rule:** Do NOT enable Stripe Tax (`automatic_tax: {'enabled': True}`) by assumption. Line items pass standard amounts until explicit tax nexus advice is delivered by FIN OPS.

---

## 3. Promotion Codes & Friends & Family Entitlements

### 3.1 Promo Code Handling in Stripe Checkout
- Checkout Session creation sets `allow_promotion_codes=True` ([`numista_backend/routes/payment_routes.py:58`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L58)).
- Enables both customer-facing promotional codes and customer-specific coupon codes configured in the Stripe dashboard.

### 3.2 Friends and Family (F&F) Free Accounts
- **Account Identification:** Flag-driven entitlements in Firestore `users/{uid}` via `is_lifetime_family_estate == true` ([`numista_mobile/lib/screens/estate_planning_screen.dart:170`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/estate_planning_screen.dart#L170)).
- **Lifetime Benefit Preservation:** Permanent exemption from subscription paywalls and expiration downgrades.
- **AI Allowance Structure:**
  - Month 1: \$10.00 AI token allowance.
  - Ongoing Months: \$5.00 / month AI token allowance.
- **Unresolved Boundaries (Surfaced for Founder Policy Decision - Not Invented by Agent):**
  1. *Month Definition:* Whether a "month" is defined as a fixed 30-day window from redemption timestamp or aligns with the 1st of the calendar month (UTC).
  2. *Rollover Policy:* Whether unused dollar balance rolls over to the following month (standard industry practice is non-cumulative/no rollover; default recommendation: expire at monthly boundary).
  3. *Reset Timestamp:* Exact synchronization schedule (e.g. 00:00:00 UTC on the 1st vs rolling cron per user).

---

## 4. Backend & Webhook Architecture (`numista_backend`)

### 4.1 Checkout Session Creation Endpoint
- **Route:** `POST /api/stripe/create-checkout-session` ([`numista_backend/routes/payment_routes.py:32-80`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L32-L80)).
- **Authentication:** Mandatory Firebase ID token validated via `get_current_user` dependency ([`payment_routes.py:35`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L35)).
- **Session Dispatch:**
  ```python
  # Distinguish one-time Beta Special from recurring subscription tiers
  if req.tier == "beta_special":
      mode = "payment"
      unit_amount = 3000  # $30.00 in cents
      product_name = "Numista.AI 6-Month Beta Special"
      product_desc = "6 Months Unlimited Catalog & 100-Coin Collection Suite"
      line_items = [{
          'price_data': {
              'currency': 'usd',
              'product_data': {'name': product_name, 'description': product_desc},
              'unit_amount': unit_amount,
          },
          'quantity': 1,
      }]
  else:
      mode = "subscription"
      # Regular tier pricing mapping per Section 2.2
  ```
- **Metadata Payload:**
  ```python
  metadata = {
      "user_uid": user_uid,
      "target_tier": req.tier.lower(),
      "billing_cycle": req.billing_cycle, # 'monthly' | 'annual' | 'one_time'
      "app_version": "preview-p7",
  }
  ```
- **Redirect URLs:**
  - Success: `https://<preview-domain>/#/settings?stripe=success&session_id={CHECKOUT_SESSION_ID}`
  - Cancel: `https://<preview-domain>/#/settings?stripe=cancel`

### 4.2 Webhook Signature & Event Processing
- **Route:** `POST /api/stripe/webhook` ([`numista_backend/routes/payment_routes.py:166-241`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L166-L241)).
- **Public Middleware Allowlist:** Mount paths `/webhook` and `/api/stripe/webhook` are allowlisted in `_PUBLIC_PATHS` ([`numista_backend/main.py:160-162`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L160-L162)).
- **Signature Verification:**
  - Verified via `stripe.Webhook.construct_event(payload, sig_header, webhook_secret)` ([`payment_routes.py:182`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L182)).
  - Missing secret in production raises HTTP 400.
- **Firestore Idempotency Ledger:**
  - Collection: `stripe_events`
  - Document ID: Stripe `event['id']` ([`payment_routes.py:199-203`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L199-L203)).
  - Existing document check: Skips duplicate execution immediately (`{"status": "skipped_duplicate"}`).

### 4.3 Delayed Payments & State Machine
- **Strict Rule:** Success page navigation alone **NEVER** grants access.
- For asynchronous payment methods (ACH, SEPA, bank transfer, Boleto):
  - In `checkout.session.completed`, if `payment_status == 'unpaid'`, entitlement is held in `pending_payment` status.
  - Entitlement activation occurs strictly upon `checkout.session.async_payment_succeeded` or `invoice.paid`.
  - Failure/cancellation routes to `checkout.session.async_payment_failed`.

### 4.4 Fulfillment Event Handlers
1. **`checkout.session.completed` (with `payment_status == 'paid'`):**
   - For `target_tier == 'beta_special'`:
     - `stripe_tier`: `"beta_special"`
     - `subscription_status`: `"active"`
     - `beta_special_purchased_at`: `datetime.now(timezone.utc).isoformat()`
     - `beta_special_expires_at`: `(datetime.now(timezone.utc) + timedelta(days=182)).isoformat()`
     - Call `unlock_user_coins(target_id)` to restore access to coins up to limit.
2. **`invoice.payment_failed`:**
   - Initiates 3-day grace period: `grace_period_until = now() + 3 days` ([`payment_routes.py:229-232`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L229-L232)).
3. **`customer.subscription.deleted`:**
   - Reverts `stripe_tier` to `"free"`.
   - Calls `lock_overflow_coins(target_id, TIER_COIN_LIMITS["free"])` ([`payment_routes.py:238`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L238)).

---

## 5. App-Side Gating & 101+ Coin Boundary Enforcement

### 5.1 The 100/101 Boundary
- Standard Free Tier coin limit: **20 coins** ([`numista_backend/tier_gatekeeper.py:42`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L42)).
- Beta Special & Copper Tier limit: **100 coins**.
- Users with 101+ coins require Silver tier (250) or higher.
- **Client Boundary Display:**
  - 1–100 coins: Qualified for \$30 Beta Special or Copper tier.
  - 101+ coins: Clear upgrade prompt explaining coin capacity tiering.

### 5.2 Collection Count Invalidation & Race Conditions
- *Scenario:* User initiates Checkout with 99 coins, but while the Checkout tab is active, adds 3 coins via background sync or another browser session, reaching 102 coins.
- *Resolution:*
  1. The server stores `pre_checkout_coin_count` in checkout session metadata.
  2. Webhook fulfillment grants the purchased tier (`beta_special` / 100-coin limit).
  3. The app-side `tier_gatekeeper` evaluates `coin_count > tier_limit`.
  4. If `coin_count` (102) exceeds the newly purchased limit (100), the app gracefully places the 2 overflow coins in read-only / locked state with a non-blocking banner: *"You have 102 coins. Your 100-coin plan is active; 2 coins are locked until upgraded to Silver."* Zero data loss, zero destructive edits.

---

## 6. Secrets Management & Secret Manager Configuration

All credentials reside in Google Cloud Secret Manager. Values are injected into Cloud Run execution environments via environment variable references:

| Environment Variable | Secret Manager Secret Name | Target Environment |
|---|---|---|
| `STRIPE_PUBLISHABLE_KEY` | `stripe_publishable_key_test` | Preview (`p7-gate`) |
| `STRIPE_SECRET_KEY` | `stripe_secret_key_test` | Preview (`p7-gate`) |
| `STRIPE_WEBHOOK_SECRET` | `stripe_webhook_secret_test` | Preview (`p7-gate`) |

- **Standing Rule:** Live keys (`pk_live_...`, `sk_live_...`, `whsec_live_...`) are strictly prohibited from preview environments.
- Zero secrets committed to Git, logged in console outputs, or exposed to browser bundles.

---

## 7. Verification & Field Test Matrix

All tests must be executed with official Stripe Sandbox Test Cards in the preview environment:

| Test Case | Scenario / Card | Expected HTTP / Redirect | Expected Firestore State |
|---|---|---|---|
| **TC-01** | Successful Beta Special Purchase (`4242...4242`) | HTTP 200 $\rightarrow$ Stripe Checkout $\rightarrow$ `success_url` | `stripe_tier: 'beta_special'`, `subscription_status: 'active'`, `beta_special_expires_at: +182d` |
| **TC-02** | 3D-Secure Authentication (`4000...3020`) | 3DS challenge prompt $\rightarrow$ Success | Webhook activates entitlement only after challenge completion |
| **TC-03** | Declined Card (`4000...0002`) | Stripe card error shown in Checkout | Zero Firestore mutations; user remains on existing tier |
| **TC-04** | Webhook Idempotency (Replayed Event ID) | HTTP 200 with `skipped_duplicate` | Single event record in `stripe_events`; no duplicate side-effects |
| **TC-05** | Delayed Payment (ACH / Test Async) | `checkout.session.completed` (`unpaid`) | `subscription_status: 'pending_payment'`; access withheld until async success |
| **TC-06** | 100/101 Coin Boundary Enforcement | Account with 100 coins vs 101 coins | 100 coins unlocked; 101st coin triggers lock overflow banner |
| **TC-07** | F&F Account Preservation | Account with `is_lifetime_family_estate == true` | Expiration cron bypasses account; lifetime tier preserved |

---

## 8. Implementation Ownership, Milestones & Scoped Gates

### 8.1 Proposed Execution Milestones (Post-Approval)
- **Gate 1 (Plan Approval):** Sunday 8 Nov 2026: AG CoS delivers plan $\rightarrow$ GB CoS ($\ge 95$) $\rightarrow$ SAG ($\ge 95$) $\rightarrow$ Founder Eric typed YES.
- **Gate 2 (Preview Build):** Monday 9 Nov – Tuesday 10 Nov: Preview implementation on branch `p7-v8.9` under scoped Eric authorization.
- **Gate 3 (Field Tester Sandbox PASS):** Wednesday 11 Nov: Field Tester executes TC-01 through TC-07 with Stripe test cards and files verification logs.
- **Gate 4 (Founder Verification):** Thursday 12 Nov: Eric verifies new-account checkout flow on `p7-gate` preview.
- **Gate 5 (Live Payment Authorization):** Real production live-mode switch requires a separate, independent, typed authorization from Founder Eric.

---

### Verification Checklist Before Review Submission
- [x] Target branch is `origin/p7-v8.9` exclusively (`origin/main` locked at `9f04550a`).
- [x] Stripe billing strictly OFF across all live systems.
- [x] Prices matching NET-827 order: Beta Special \$30 (one-time), Copper \$4.99/\$49.99, Silver \$8.99/\$89.99, Platinum \$10.99/\$109, Gold \$15.99/\$150.
- [x] Tax collection surfaced as unresolved (Stripe Tax NOT assumed).
- [x] F&F token allowance and rollover surfaced as unresolved policy questions.
- [x] Webhook-verified entitlement required; navigation alone never grants access.
- [x] Secret Manager specified; zero secret values in plan.
- [x] Alerts only, never budget caps (\$20/mo alert).
