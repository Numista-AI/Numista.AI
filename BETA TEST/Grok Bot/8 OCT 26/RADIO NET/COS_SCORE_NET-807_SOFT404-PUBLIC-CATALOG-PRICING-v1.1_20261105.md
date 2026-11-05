# GB CoS SCORE — NET-807 / PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v1.1

- Scorer: Grok Bot Chief of Staff · 2026-11-05 ~5:00 PM ET (America/New_York)
- Repo checked read-only: p7-v8.9 @ 4c97c7f0; origin/dev @ b0b05808; origin/main @ 9f04550a
- Mode: SCORE ONLY; no execute, deploy, Firestore write, rules change, main change, or Stripe change
- **CoS: 76 / 100 FAIL** (pass >=95)
- Argon: see corresponding Argon review; not treated as repo evidence
- SAG: independent xAI grok-4.7 result filed separately
- Eric YES gate: BLOCKED pending revision and independent pass

## 1. Real-code verification

| Check | Result | Evidence |
|---|---|---|
| Catalog premise / options | **PASS** | Reuses dev CatalogBrowseScreen, no duplicate screen; all A/B/C require Eric typed choice + YES. |
| Census | **PASS** | Actual handoff master = 3202 (2965 coins,181 notes,56 medals), matching CSV. Proposed corrected marketing removes 5142 and unsourced claims. |
| AuthGate / links | **PARTIAL** | Correctly identifies authenticated users bypass publicRoute in real auth_gate.dart:105-148 before publicRoute at 157; InkWell footer confirmed. Must put publicRoute ahead of BaseLayout while retaining auth-stream wait. |
| Static OG | **FAIL** | One SPA index.html cannot provide route-specific titles/OG for /, /catalog, /pricing and thousands of coin URLs. Proposed bucket OG image is unverified and no per-route generation/hosting implementation is specified. |
| Rollback / egress | **FAIL** | Still pins rollback to 9f04550a; main lacks the catalog code. Inherits nonexistent IAM-only stop-public-egress instead of Hosting-disable human shutoff. |
| Public fields / images | **FAIL** | Plan asserts gs://numista-reference-library and catalog-assets without verified provisioning; existing public catalog JSON has no cpgRetail or ai_replica keys. Migration must not invent prices or primary images. |

## 2. Breakdown

- Ground truth / census / marketing: 17/20
- Options / launch fit: 20/20
- Routing / AuthGate / static HTML: 14/20
- Public privacy / prices / images: 15/20
- Rollback / spend / implementability: 10/20
- **Total: 76/100 FAIL**

## 3. Blocking must-fixes

1. Use current pre-execute p7-v8.9/dev SHAs with git revert, preserve dev catalog routing, and name prior Hosting release restoration. Replace inherited IAM-only stop with human Hosting disable/channel deletion until a real Hosting-aware control exists.
2. Specify actual per-route static HTML generation and hosting rewrites for /, /catalog, /pricing and any coin URLs; test raw response bodies for distinct canonical/title/OG. Use only an existing/provisioned same-party OG asset with a placeholder if absent.
3. Move publicRoute before the signed-in BaseLayout branch (while waiting on the existing auth stream) and test signed-in plus signed-out /pricing.
4. Correct master source path to the handoff input; define a fail-closed migration from catalog_public_v1.json that omits missing cpgRetail and primary images rather than inventing them. Require Foreign Coins/source-link removal from dev before any Option A release.

## 4. PII and locks

No AJ PII found in the plan or supplied excerpts. origin/main remains 9f04550a; Stripe OFF. No execution or deployment performed.
