# GB CoS SCORE — NET-806 / PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~5:00 PM ET (America/New_York)
- Repo checked read-only: p7-v8.9 @ 4c97c7f0; origin/dev @ b0b05808; origin/main @ 9f04550a
- Mode: SCORE ONLY; no execute, deploy, Firestore write, rules change, main change, or Stripe change
- **CoS: 86 / 100 FAIL** (pass >=95)
- Argon: see corresponding Argon review; not treated as repo evidence
- SAG: independent xAI grok-4.7 result filed separately
- Eric YES gate: BLOCKED pending revision and independent pass

## 1. Real-code verification

| Check | Result | Evidence |
|---|---|---|
| Call sites / contrast | **PASS** | All five call sites 2736,2761,2773,3044,3122 match real code. _kDark light background F4F4F2 + white title 918-921 verified. |
| Privacy / guest | **PASS** | Storage hidden until separate PIN design; guest hide-list covers purchase/cost/retailer/invoice/notes/storage/ownership actions. No AJ PII in plan. |
| Laws exception | **PASS WITH BOUNDARY** | Congress.gov-only Laws links, rel=noopener, no images, catalog wins, unchecked label, US-only and fail-closed all specified. |
| Rollback | **FAIL** | §9.3 still uses git revert --no-commit HEAD...9f04550a. Main is not an ancestor of p7-v8.9; 9f04550a..p7-v8.9 spans 2112 files (+282979/-11590). This is not a safe pre-execute rollback. |
| Firestore scope | **FAIL** | §8 permits Edit/Wishlist/Delete to trigger existing legacy mutation callbacks in the initial release. Those are writes and cannot be enabled under a plan that says all such actions wait for a separate YES. |
| Values | **PARTIAL** | CDN CPG retail and pending-only-on-missing are specified for public data. Private owner Purchase/Melt may remain behind Show values; AI Estimate must stay experimental and must never displace positive CDN retail in the primary value slot. |

## 2. Breakdown

- Founder UX requirements: 25/25
- Accuracy / citations: 17/20
- Privacy / public guest / PII: 18/20
- Retail / links / Laws: 12/15
- Rollback / writes / tests: 14/20
- **Total: 86/100 FAIL**

## 3. Blocking must-fixes

1. Replace HEAD...9f04550a with revert of the actual execute commit(s) to a recorded pre-execute p7-v8.9 SHA, plus named Hosting release restore if deployed. Keep main untouched.
2. Remove legacy mutation callbacks from the initial release. Edit/Wishlist/Delete/research-logging must be disabled/absent until Eric separately approves Firestore writes; specify read-only tests proving no write callback fires.
3. Bind Morgan notes and laws to checked catalog data or explicitly labeled unchecked output; add tests that arbitrary Congress API errors/timeouts produce the empty state and no unverified legal claim, and that AI/secondary values never displace positive CDN retail in the primary value slot.

## 4. PII and locks

No AJ PII found in the plan or supplied excerpts. origin/main remains 9f04550a; Stripe OFF. No execution or deployment performed.
