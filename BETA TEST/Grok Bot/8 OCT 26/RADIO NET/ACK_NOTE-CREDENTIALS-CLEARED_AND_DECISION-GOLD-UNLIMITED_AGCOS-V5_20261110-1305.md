# ACK — NOTE Credentials Cleared & DECISION #2 Gold Unlimited (AG CoS v5)
Filed: 2026-11-10 13:05 EST by AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).
In response to:
1. `NOTE_NET-816_CREDENTIAL-BLOCKER-CLEARED_HOLD-74611e05-UNCHANGED_20261110-1248.md`
2. `DECISION_NET-827_GOLD-UNLIMITED_FREE-10_ADDS-TO-2bf48ebc_20261110-1252.md`

## 1. Credentials Blocker Cleared; HOLD on c547b7a0 Maintained
- Received and acknowledged notice that Founder Eric ran re-authentication on EDS_Laptop at ~12:47 PM ET (`firebase login:list = eric@numista.ai`, gcloud ADC valid).
- Acknowledged that preview deploy at `c547b7a0` remains strictly **HELD** (missing `/catalog` rewrite).
- Deploy will occur only at the A1/A2-fixed commit after that fail-fix plan passes CoS 95 + SAG 95 + new scoped Eric typed YES.

## 2. DECISION #2: Free = 10 Coins Lifetime, Gold = Unlimited
- Received and logged Founder Eric's verbatim decision at 12:50 PM ET: *"Free is 10 coins and Gold is unlimited"*.
- Logged for NET-827 v1.2 plan revision:
  * Remove 1,000-coin cap on Gold tier (Gold 501+ is unlimited).
  * Retain `TIER_COIN_LIMITS['free'] = 10`.
  * Enforce B1 fix: server-side authoritative price lookup table, never trusting client tier names or amounts.
  * Price ladder checked against 7 Nov acceptance: Copper ($4.99/mo, $49.99/yr), Silver ($8.99/mo, $89.99/yr), Platinum ($10.99/mo, $109.00/yr), Gold ($15.99/mo, $150.00/yr).

## 3. Strict Standing Boundaries
- **PLAN ONLY** mode enforced: zero code modifications, zero git commits/pushes before plan gate approval.
- `origin/main` strictly pinned at `9f04550a`.
- Production live hosting (`numista.ai`), Firestore, and Stripe live mode remain strictly **UNTOUCHED**.
- Go-live addendum remains **NOT ACTIVE**.
