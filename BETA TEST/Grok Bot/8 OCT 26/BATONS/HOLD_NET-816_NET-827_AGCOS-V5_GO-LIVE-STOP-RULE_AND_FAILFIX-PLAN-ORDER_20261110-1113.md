# HOLD / FAIL-FIX PLAN ORDER — NET-816 + NET-827 (AG CoS v5)
From: GB CoS via Desk. CoS order timestamp: **10 Nov 2026 11:15 AM ET** (America/New_York).
Filed: 2026-11-10 11:13:11 EST by Grok Bot Desk. **Notice only. No WAKE.** Desk does not deploy, run git/Firebase/Stripe, or start work.
To: AG CoS v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
This notice grants **no new authority**. Every fix goes through the normal plan gate (**CoS 95 + SAG 95 + Eric YES**).

## 1) STOP-RULE HOLD — go-live stays NOT ACTIVE
Hold on `ADDENDUM_NET-816_NET-827_AGCOS-V5_CONDITIONAL-GO-LIVE_20261110-1033.md` (SHA-256 `c2b6ac93b844a51d22be23ba428b3d098ad3f2e087e004b3aa6d63919755b4c2`).
**Go-live stays NOT ACTIVE regardless of Field Tester score.**
Basis: Code Reviewer go-live review `C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\10 NOV 26\CODE_REVIEW_GO-LIVE_NET-816_NET-827_c547b7a0_20261110.md` (CoS-cited SHA starting `3e2c1670` ending `864ff`; Desk read-only laptop check: file exists, full SHA-256 `3e2c16709736ab5a5cf834ed9aba9df66704465d7b86f24baf4cf56a0ad864ff` — prefix/suffix match) found **wrong-access** and **wrong-charge** blockers.
**Do NOT** fold to main, deploy live, or attach live Stripe keys.
Lifting this hold needs a **new CoS written confirmation** after fixes pass the gate **and** Eric's YES.

## 2) NET-816 p7-gate PREVIEW deploy still authorized
Eric YES card `t2455s9467`; baton `BATON_NET-816_AGCOS-V5_PREVIEW-DEPLOY_CATALOG-CHUNK1_v2.2_p7-gate_20261110-1007.md` SHA-256 `c65658e0e2783477e0d07b271dcf6cee1e5d939764ccd5ae4f257539e7fcdf0c`.
**Continue.** File **DONE** with preview URL and built commit (plus the other evidence required in that baton).

## 3) NET-816 FAIL-FIX — PLAN ONLY (no code), due before any live fold
- **A1 BLOCKER:** `firebase.json` has no `/catalog` rewrite at `c547b7a0`, so numista.ai/catalog and #/catalog would break.
- **A2 MAJOR:** Half dime fix uses Morgan-dollar weight for 90% silver half dime melt — about **10× too high** on the collection dashboard.

## 4) NET-827 v1.2 build stays QUEUED
Queued behind the Catalog field test; Stripe **test mode only**. Baton `BATON_NET-827_AGCOS-V5_QUEUED-PREVIEW-BUILD_STRIPE-CHECKOUT-PREVIEW_v1.2_p7-gate_20261110-1031.md` SHA-256 `6693232a39993ddb3e4b678d439a0cd37a91217a148f0fcb8e6d4ed0ec2c1175`.
A revised build plan must close:
- **B1:** Price set from tier name and webhook grants whatever tier was sent, so power_user/sovereign unlock for $4.99 (`payment_routes.py`:52–53, 75, 223–224).
- **B2:** Subscription/invoice events can't find the user but are marked processed, so cancel leaves paid access and `invoice.paid` can reset tier to pro.
- **B3:** Promo codes allowed on every session; `amount_total` and `payment_status` never checked.
- **B4:** No idempotency key; dedupe not transactional.
- **B5:** Refunds and disputes ignored.
Christmas code created **inactive** and rejected server-side before **26 Nov 2026 00:00 UTC**, never on monthly. Live keys from Secret Manager only, with a test/live mode check.

## FREE-TIER COIN LIMIT HOLD
Plan and code say **20**; Eric's 29 Oct and 1 Nov decisions say **10** (**CoS-stated**). Eric is deciding now. **Change nothing** until CoS confirms.

Filing this notice ≠ accepted/started and does not lift or start any production step.
