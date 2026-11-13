# PLAN NET-827: Stripe Checkout Preview v1.1 (p7-gate Preview Gated)

**Document Version:** 1.1  
**Date:** Sunday, 8 November 2026 ~18:15 ET  
**Author:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)  
**Authority:** Founder Eric verbatim directives:  
- 7 Nov 2026, 11:41 AM ET: *"I want to test it in 5 days, do what needs to be done before then."*  
- 7 Nov 2026, 11:42 AM ET: *"I approve this plan"* (Approval covers filing this plan order only; NOT a build, Firestore writes, or live deployment).  
**Code Citations Pin:** Git commit `56701f92` on branch `origin/p7-v8.9`.  
**Review Cycle:** AG CoS Plan -> Grok Bot CoS Review ($\ge 95$) -> Stand Alone Grok (SAG) Independent Review ($\ge 95$) -> Founder Eric Scoped Typed YES.

---

## Document Changelog (v1.0 $\rightarrow$ v1.1)

| Must-Fix / Issue | Section Updated | Resolution in v1.1 |
|---|---|---|
| **MF-1: Beta Special Term Contradiction** | §2.1, §4.4, §7 (TC-01), §9 | Replaced fixed `182 days` with deterministic calendar-month addition (`relativedelta(months=6)` / calendar month math). E.g. purchased 12 Nov 2026 $\rightarrow$ expires 12 May 2027 23:59:59 UTC. Sections 2.1, 4.4, and TC-01 unified. |
| **MF-2: Promo Codes (Christmas & F&F)** | §3.1, §3.2, §3.3 | Fully specified Stripe objects for: (a) Christmas Special: 50% off first year (`percent_off: 50.0`, `duration: 'once'`), yearly subscriptions only, valid 26 Nov – 25 Dec 2026, non-stackable; (b) F&F / Beta Tester Code: 100% off (`percent_off: 100.0`), `max_redemptions: 500`, valid through beta end, \$10 AI month 1 then \$5/mo ongoing, at-cost AI top-ups. Zero secret strings printed in plan. |
| **MF-3: Separate F&F Entitlement Model** | §3.3, §4.4, §5.1 | Removed conflation with `is_lifetime_family_estate`. Defined dedicated fields `is_friends_and_family: true`, `is_beta_tester: true`, `beta_access_type: "friends_and_family"`. Specified \$0 checkout fulfillment and 500-cap atomic rejection. |
| **MF-4: Idempotency Ordering & Retry** | §4.2, §4.3 | Replaced write-after-fulfillment with robust Two-Phase Processing Ledger: Phase 1 atomic check/claim (`status: "processing"` with 60s stale lock recovery); Phase 2 batch fulfillment; Phase 3 mark `status: "completed"` on success or `status: "failed"` with HTTP 500 to trigger Stripe retry. |
| **MF-5: Subscription Path Specification** | §2.2, §4.1, §4.5 | Added explicit price mapping (`price_data` vs Price IDs), recurring interval (`month`/`year`). Added in-scope handlers for `checkout.session.completed`, `async_payment_succeeded`, `async_payment_failed`, `invoice.payment_failed`, `customer.subscription.updated`, `customer.subscription.deleted`, `checkout.session.expired`. Clarified `invoice.paid` applies only to recurring renewals, NOT one-time payments. Marked refund/dispute clawbacks as Phase 2. |
| **MF-6: Metadata Consistency** | §4.1, §5.2 | Added `pre_checkout_coin_count` to §4.1 session creation `metadata` dictionary, resolving §5.2 race-condition dependence. |
| **NB-1: Canonical Branch & Preview Target** | §1, §8.1 | Defined canonical branch as `origin/p7-v8.9` and preview deployment target as `https://preview-catalog.numista.ai/#/` (`p7-gate` channel). |
| **NB-2: Mojibake Fix** | §5.1 | Cleaned all garbled characters in boundary text into clean UTF-8. |
| **NB-3: Free Tier 20 Coins Source** | §5.1 | Cited NET-372 and `tier_gatekeeper.py:42` (`TIER_COIN_LIMITS["free"] = 20`) reinforced by Founder directive 3 Nov 2026. |
| **NB-4: Milestones vs 5-Day Window** | §8.1 | Explicitly distinguished Sunday 20:00 ET plan delivery from Founder Eric's 5-day testing target (Thursday, 12 Nov 2026). |

---

## 1. Operational Constraints & Standing Locks

> [!IMPORTANT]
> **Strict Operational Boundaries (Always Enforced):**
> 1. **PLAN ONLY Mode:** Strictly zero code execution, zero production deployments, zero live Firestore mutations, zero Stripe live-mode mutations, and zero live card charges authorized under this document.
> 2. **Canonical Target Branch:** `origin/p7-v8.9` exclusively. Zero merges or pushes to `origin/main`.
> 3. **Canonical Preview Target:** `p7-gate` preview deployment (`https://preview-catalog.numista.ai/#/`).
> 4. **Repository Locks:** `origin/main` strictly pinned and locked at commit `9f04550a`.
> 5. **Stripe Production Status:** Stripe billing is strictly **LOCKED OFF** across all production environments.
> 6. **Spend Controls:** Standing rule: **Alerts only, NEVER budget caps** ($20/month alert configured; hard spending caps prohibited).
> 7. **Public Endpoints:** Public `/catalog` browsing and Live eBay Check must remain 100% public and ungated.
> 8. **Secrets Integrity:** All Stripe API keys and webhook signing secrets reside in Google Cloud Secret Manager only. Zero raw keys, test credentials, or private promo codes in plans, commit history, radio messages, or client bundles.

---

## 2. Product Architecture & Pricing Model

### 2.1 Sandbox $30 Beta Special
- **Nature:** One-time, non-recurring purchase ($30.00 USD plus applicable tax).
- **Checkout Mode:** Stripe Checkout `mode='payment'` (NOT `mode='subscription'`).
- **Entitlement Period:** Exactly **six (6) calendar months** calculated deterministically from the timestamp of webhook fulfillment:
  $$\text{ExpiresAt} = \text{PurchasedAt} + \text{relativedelta}(\text{months}=6)$$
  *(E.g., purchased 12 Nov 2026 at 14:00 UTC $\rightarrow$ expires 12 May 2027 at 23:59:59 UTC). This eliminates month-length variance (28/30/31 days).*
- **Beta-End Independence:** Full 6 calendar months honored even if the public beta test concludes earlier.
- **Renewal / Conversion Policy:** Zero automatic renewal; zero automatic tier conversion. At expiration, account gracefully transitions to free tier coin limits with overflow lock protections unless the user manually elects to purchase an ongoing subscription tier.

### 2.2 Standard Subscription Tiers (USD plus applicable tax)
When regular subscription tiers launch, ongoing plans operate via Stripe Checkout `mode='subscription'`:

| Tier | Monthly Price | Annual Price | Annual Savings | Coin Capacity | Daily DeepDive AI | Daily Invoice Scans |
|---|---|---|---|---|---|---|
| **Copper** | \$4.99 / mo | \$49.99 / yr | ~16% | 100 coins | 25 / day | 15 / day |
| **Silver** | \$8.99 / mo | \$89.99 / yr | ~17% | 250 coins | 50 / day | 30 / day |
| **Platinum** | \$10.99 / mo | \$109.00 / yr | ~17% | 500 coins | 100 / day | 50 / day |
| **Gold** | \$15.99 / mo | \$150.00 / yr | ~22% | 1,000 coins | 500 / day | 250 / day |

*Code Mapping Citation:* In [`numista_backend/tier_gatekeeper.py:41-50`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L41-L50), existing internal tier keys map directly: Copper $\rightarrow$ `pro`, Silver $\rightarrow$ `numismatist`, Platinum $\rightarrow$ `dealer`, Gold $\rightarrow$ `estate`.

### 2.3 Tax Policy
- Tax registration, multi-jurisdiction nexus, and tax collection policies remain **UNRESOLVED** at the business entity level.
- **Strict Rule:** Do NOT enable Stripe Tax (`automatic_tax: {'enabled': True}`) by assumption. Line items pass standard unit amounts until explicit tax nexus advice is delivered by FIN OPS.

---

## 3. Promotion Codes & Friends & Family Entitlements

### 3.1 Stripe Checkout Promo Code Support
- Checkout Session creation passes `allow_promotion_codes=True` ([`numista_backend/routes/payment_routes.py:58`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L58)).
- Enables server-validated customer-facing promotion codes and restricted coupons.

### 3.2 Christmas Special Promo Code (Founder Directive 7 Nov 2026)
- **Offer:** 50% discount on the first year of any annual subscription tier.
- **Eligibility:** Valid across all four tiers (Copper, Silver, Platinum, Gold) for annual billing only (`interval='year'`).
- **Redemption Window:** Active starting 26 Nov 2026 00:00:00 UTC through 25 Dec 2026 23:59:59 UTC (`redeem_by: 1766707199`).
- **Stripe Object Configuration:**
  - `stripe.Coupon.create(percent_off=50.0, duration='once', name='Christmas 2026 50% Off Annual')`
  - `stripe.PromotionCode.create(coupon=coupon_id, active=True, restrictions={'first_time_transaction': True})`
- **Non-Stacking Enforcement:**
  - Stripe Checkout natively enforces exactly one promotion code per session.
  - Christmas coupon restricts to `mode='subscription'` and annual interval, rendering it inapplicable to the one-time \$30 Beta Special.
  - Cannot stack with F&F code because multiple coupons cannot be applied simultaneously.

### 3.3 Friends and Family (F&F) / Beta Tester Free Accounts
- **Offer:** 100% discount / complimentary full access during beta for designated friends and family.
- **Redemption Cap:** Exactly 500 redemptions max across the campaign.
- **Stripe Object Configuration:**
  - `stripe.Coupon.create(percent_off=100.0, duration='forever', name='Friends & Family Beta')`
  - `stripe.PromotionCode.create(coupon=coupon_id, max_redemptions=500, active=True)`
  - *Redemption Enforcement:* Stripe's server-side promotion code engine atomically rejects any checkout attempt once the 500th redemption has completed.
- **Dedicated Entitlement Flags (Independent of Estate Planning):**
  - F&F accounts write distinct flags to `users/{uid}`:
    - `is_friends_and_family: true`
    - `is_beta_tester: true`
    - `beta_access_type: "friends_and_family"`
    - `ai_allowance_monthly_usd: 5.0`
  - *Separation Note:* Does NOT touch `is_lifetime_family_estate` (which is reserved for Estate VIPs).
- **AI Token Allowances & At-Cost Top-Ups:**
  - Month 1: \$10.00 complimentary AI token credit.
  - Ongoing Months: \$5.00 / month ongoing AI allowance.
  - Top-Ups: At-cost AI token pack purchases enabled when monthly allowance is exhausted.
- **Unresolved Policy Questions (Surfaced for Founder Decision):**
  1. *Month Definition:* Whether a "month" is 30 rolling days from redemption or aligns with the 1st of the calendar month (UTC).
  2. *Rollover Policy:* Unused balance does not accumulate/roll over by default; expires at monthly boundary unless Eric directs otherwise.

---

## 4. Backend & Webhook Architecture (`numista_backend`)

### 4.1 Checkout Session Creation Endpoint
- **Route:** `POST /api/stripe/create-checkout-session` ([`numista_backend/routes/payment_routes.py:32-80`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L32-L80)).
- **Authentication:** Mandatory Firebase ID token validated via `get_current_user` dependency ([`payment_routes.py:35`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L35)).
- **Session Dispatch Logic:**
  ```python
  current_coins = get_coin_count(user_uid)
  
  if req.tier == "beta_special":
      mode = "payment"
      unit_amount = 3000  # $30.00 USD in cents
      product_name = "Numista.AI 6-Month Beta Special"
      product_desc = "6 Months Full Access & 100-Coin Collection Capacity"
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
      # Subscription pricing mapping:
      # Copper:   $4.99/mo ($499)  or $49.99/yr ($4999)
      # Silver:   $8.99/mo ($899)  or $89.99/yr ($8999)
      # Platinum: $10.99/mo ($1099) or $109.00/yr ($10900)
      # Gold:     $15.99/mo ($1599) or $150.00/yr ($15000)
      interval = "year" if req.billing_cycle == "annual" else "month"
      unit_amount = TIER_PRICES_CENTS[req.tier][interval]
      line_items = [{
          'price_data': {
              'currency': 'usd',
              'product_data': {'name': f"Numista.AI {req.tier.capitalize()} Subscription"},
              'unit_amount': unit_amount,
              'recurring': {'interval': interval},
          },
          'quantity': 1,
      }]
  ```
- **Metadata Payload (Complete & Consistent):**
  ```python
  metadata = {
      "user_uid": user_uid,
      "target_tier": req.tier.lower(),
      "billing_cycle": req.billing_cycle, # 'monthly' | 'annual' | 'one_time'
      "pre_checkout_coin_count": str(current_coins),
      "app_version": "preview-p7",
  }
  ```
- **Redirect URLs:**
  - Success: `https://preview-catalog.numista.ai/#/settings?stripe=success&session_id={CHECKOUT_SESSION_ID}`
  - Cancel: `https://preview-catalog.numista.ai/#/settings?stripe=cancel`

### 4.2 Webhook Signature & Two-Phase Idempotency Ledger
- **Route:** `POST /api/stripe/webhook` ([`numista_backend/routes/payment_routes.py:166-241`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L166-L241)).
- **Public Allowlist:** Paths `/webhook` and `/api/stripe/webhook` allowlisted in `_PUBLIC_PATHS` ([`numista_backend/main.py:160-162`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L160-L162)).
- **Signature Verification:** Verified via `stripe.Webhook.construct_event(payload, sig_header, webhook_secret)` ([`payment_routes.py:182`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L182)).
- **Two-Phase Idempotency Protocol:**
  ```python
  event_id = event["id"]
  event_ref = db.collection("stripe_events").document(event_id)
  
  # Phase 1: Atomic Claim / Duplicate Check
  event_doc = event_ref.get()
  if event_doc.exists:
      doc_data = event_doc.to_dict() or {}
      if doc_data.get("status") == "completed":
          logger.info(f"[Stripe Webhook] Duplicate event {event_id} already completed; skipped.")
          return {"status": "skipped_duplicate", "event_id": event_id}
      elif doc_data.get("status") == "processing":
          # Check for stale lock (> 60 seconds old)
          claimed_at = doc_data.get("claimed_at")
          if claimed_at and (datetime.now(timezone.utc) - claimed_at).total_seconds() < 60:
              return {"status": "in_progress", "event_id": event_id}
  
  # Set processing state
  event_ref.set({
      "status": "processing",
      "claimed_at": datetime.now(timezone.utc),
      "event_type": event.get("type"),
  })
  
  try:
      # Phase 2: Execute Fulfillment Logic
      process_stripe_fulfillment(event)
      
      # Phase 3: Mark Completed
      event_ref.set({
          "status": "completed",
          "processed_at": datetime.now(timezone.utc).isoformat(),
          "event_type": event.get("type"),
      }, merge=True)
      return {"status": "success", "event_id": event_id}
  except Exception as e:
      logger.exception(f"[Stripe Webhook] Fulfillment failed for event {event_id}")
      # Mark failed to permit Stripe retry, and raise HTTP 500 so Stripe re-delivers
      event_ref.set({
          "status": "failed",
          "failed_at": datetime.now(timezone.utc).isoformat(),
          "error": str(e),
      }, merge=True)
      raise HTTPException(status_code=500, detail="Webhook fulfillment failed; retry scheduled")
  ```

### 4.3 Delayed Payments & State Machine
- **Strict Rule:** Success page navigation alone **NEVER** grants access.
- For asynchronous payment methods (ACH, SEPA, Boleto):
  - In `checkout.session.completed`, if `payment_status == 'unpaid'`, entitlement is held in `pending_payment` status.
  - Entitlement activation occurs strictly upon `checkout.session.async_payment_succeeded`.
  - Payment failure triggers `checkout.session.async_payment_failed` and clears pending status.

### 4.4 Fulfillment Event Handlers
1. **`checkout.session.completed` (`payment_status == 'paid'` or `amount_total == 0` for F&F):**
   - For `target_tier == 'beta_special'`:
     - `stripe_tier`: `"beta_special"`
     - `subscription_status`: `"active"`
     - `beta_special_purchased_at`: `datetime.now(timezone.utc).isoformat()`
     - `beta_special_expires_at`: `(datetime.now(timezone.utc) + relativedelta(months=6)).isoformat()`
     - Call `unlock_user_coins(target_id)` up to 100-coin limit.
   - For F&F redemption (`amount_total == 0` with F&F coupon):
     - `is_friends_and_family`: `true`
     - `is_beta_tester`: `true`
     - `subscription_status`: `"active"`
     - `ai_allowance_monthly_usd`: `5.0`
     - Initial month AI credit: \$10.00.
2. **`customer.subscription.updated` / `invoice.paid` (Recurring subscriptions only):**
   - Updates `stripe_tier` to the newly active tier.
   - Resets `grace_period_until = None` and sets `subscription_status = "active"`.
3. **`invoice.payment_failed`:**
   - Initiates 3-day grace period: `grace_period_until = now() + 3 days` ([`payment_routes.py:229-232`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L229-L232)).
4. **`customer.subscription.deleted`:**
   - Reverts `stripe_tier` to `"free"`.
   - Calls `lock_overflow_coins(target_id, TIER_COIN_LIMITS["free"])` ([`payment_routes.py:238`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/routes/payment_routes.py#L238)).
5. **`checkout.session.expired`:**
   - Logs session abandonment telemetry; cleans up any transient reservations.

### 4.5 Scope Matrix: Preview vs Production

| Event Name | In Scope for Preview Gate? | Action Taken |
|---|---|---|
| `checkout.session.completed` | **YES** | Activates Beta Special, Subscription, or F&F entitlement |
| `checkout.session.async_payment_succeeded` | **YES** | Activates deferred payment entitlement |
| `checkout.session.async_payment_failed` | **YES** | Clears pending state |
| `invoice.payment_failed` | **YES** | Activates 3-day grace period |
| `customer.subscription.updated` | **YES** | Updates tier and coin limits on plan change |
| `customer.subscription.deleted` | **YES** | Reverts to free tier; locks overflow coins |
| `checkout.session.expired` | **YES** | Telemetry logging |
| `charge.refunded` | **NO (Phase 2)** | Logged as warning; manual review flag in Firestore |
| `charge.dispute.created` | **NO (Phase 2)** | Logged as warning; manual review flag in Firestore |

---

## 5. App-Side Gating & 101+ Coin Boundary Enforcement

### 5.1 The 100/101 Coin Boundary
- **Free Tier Capacity:** 20 coins (established in NET-372, [`numista_backend/tier_gatekeeper.py:42`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/tier_gatekeeper.py#L42), reinforced by Founder directive 3 Nov 2026).
- **Beta Special & Copper Capacity:** 100 coins.
- **101+ Coins Policy:** Users with 101 or more coins require Silver tier (250) or higher.
- **Client Boundary Behavior:**
  - 1–100 coins: Qualified for $30 Beta Special or Copper tier.
  - 101+ coins: Upgrade banner displays coin capacity warning and routes user to Silver tier.

### 5.2 Collection Count Fluctuations & Race Conditions
- *Scenario:* User initiates Checkout with 99 coins, but adds 3 coins in a separate session while checkout is active, reaching 102 coins before webhook fulfills.
- *Resolution Protocol:*
  1. The server stores `pre_checkout_coin_count` in checkout session metadata (§4.1).
  2. Webhook fulfillment activates the purchased tier (`beta_special` / 100-coin limit).
  3. App `tier_gatekeeper` evaluates `coin_count > tier_limit`.
  4. If `coin_count` (102) exceeds the newly purchased limit (100), the app gracefully places the 2 overflow coins in read-only / locked state with a non-blocking banner: *"You have 102 coins. Your 100-coin Beta Special is active; 2 coins are locked until upgraded to Silver."* Zero data loss, zero destructive edits.

---

## 6. Secrets Management & Secret Manager Configuration

All credentials reside in Google Cloud Secret Manager. Injected into Cloud Run execution environments via environment variable mapping:

| Environment Variable | Secret Manager Secret Name | Target Environment |
|---|---|---|
| `STRIPE_PUBLISHABLE_KEY` | `stripe_publishable_key_test` | Preview (`p7-gate`) |
| `STRIPE_SECRET_KEY` | `stripe_secret_key_test` | Preview (`p7-gate`) |
| `STRIPE_WEBHOOK_SECRET` | `stripe_webhook_secret_test` | Preview (`p7-gate`) |

- **Standing Rule:** Live keys (`pk_live_...`, `sk_live_...`, `whsec_live_...`) are strictly prohibited from preview environments.
- Zero secrets committed to Git, logged in console outputs, or exposed to browser bundles.

---

## 7. Verification & Field Test Matrix

All tests must be executed with official Stripe Sandbox Test Cards on the preview URL (`https://preview-catalog.numista.ai/#/`):

| Test Case | Scenario / Test Card | Expected HTTP / Redirect | Expected Firestore State |
|---|---|---|---|
| **TC-01** | Successful Beta Special Purchase (`4242...4242`) | HTTP 200 $\rightarrow$ Stripe Checkout $\rightarrow$ `success_url` | `stripe_tier: 'beta_special'`, `subscription_status: 'active'`, `beta_special_expires_at: purchased_at + 6 calendar months` |
| **TC-02** | 3D-Secure Authentication (`4000...3020`) | 3DS challenge prompt $\rightarrow$ Success | Webhook activates entitlement only after challenge completion |
| **TC-03** | Declined Card (`4000...0002`) | Stripe card error shown in Checkout | Zero Firestore mutations; user remains on existing tier |
| **TC-04** | Webhook Idempotency (Replayed Event ID) | HTTP 200 with `skipped_duplicate` | Single event record in `stripe_events`; no duplicate side-effects |
| **TC-05** | Delayed Payment (ACH / Test Async) | `checkout.session.completed` (`unpaid`) | `subscription_status: 'pending_payment'`; access withheld until async success |
| **TC-06** | 100/101 Coin Boundary Enforcement | Account with 100 coins vs 101 coins | 100 coins unlocked; 101st coin triggers lock overflow banner |
| **TC-07** | F&F Promo Code Redemption (100% off, \$0 total) | Checkout completed with \$0 charge | `is_friends_and_family: true`, `is_beta_tester: true`, \$10 initial AI allowance; 500-cap decremented |
| **TC-08** | Christmas Promo Code (50% off annual) | Annual plan checkout with 50% discount | `stripe_tier: '<tier>'`, discounted first-year invoice; non-stackable |

---

## 8. Implementation Ownership, Milestones & Scoped Gates

### 8.1 Execution Milestones
- **Gate 1 (Plan Approval):** Sunday 8 Nov 2026: AG CoS delivers plan $\rightarrow$ GB CoS ($\ge 95$) $\rightarrow$ SAG ($\ge 95$) $\rightarrow$ Founder Eric typed YES.
- **Gate 2 (Preview Build):** Monday 9 Nov – Tuesday 10 Nov: Preview implementation on branch `origin/p7-v8.9` under scoped Eric authorization.
- **Gate 3 (Field Tester Sandbox PASS):** Wednesday 11 Nov: Field Tester executes TC-01 through TC-08 with Stripe test cards and files verification logs.
- **Gate 4 (Founder 5-Day Target Verification):** Thursday 12 Nov: Founder Eric tests new-account checkout flow on `https://preview-catalog.numista.ai/#/` per 7 Nov directive (*"test it in 5 days"*).
- **Gate 5 (Live Payment Authorization):** Real production live-mode switch requires a separate, independent, typed authorization from Founder Eric.

---

## 9. Verification Checklist Before Review Submission
- [x] Target branch is `origin/p7-v8.9` exclusively (`origin/main` locked at `9f04550a`).
- [x] Stripe billing strictly OFF across all live systems.
- [x] Beta Special term unified across all sections as exactly 6 calendar months (`relativedelta(months=6)`).
- [x] Christmas Special (50% off annual, 26 Nov–25 Dec) and F&F 500-cap promo code objects specified without printing secret strings.
- [x] F&F entitlement decoupled from estate planning into dedicated `is_friends_and_family: true` flag.
- [x] Two-Phase Idempotency Ledger specified with atomic check/claim, retry on failure, and stale lock recovery.
- [x] Full subscription event handler scope matrix defined; `invoice.paid` correctly scoped to recurring subscriptions only.
- [x] `pre_checkout_coin_count` included in metadata payload.
- [x] Tax collection surfaced as unresolved (Stripe Tax NOT assumed).
- [x] Secret Manager specified; zero secret values in plan.
- [x] Alerts only, never budget caps ($20/mo alert).
