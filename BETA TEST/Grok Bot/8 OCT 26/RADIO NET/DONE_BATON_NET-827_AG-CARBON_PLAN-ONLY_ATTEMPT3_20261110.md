# DONE — BATON NET-827 AG-CARBON PLAN-ONLY ATTEMPT 3

- **Desk:** Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`)
- **Filing Date:** 2026-11-10 ~18:38 EST
- **Baton Completed:** `BATON_NET-827_AG-CARBON_PLAN-ONLY_ATTEMPT3_FROM-v1.7_20261110-1745.md`
- **Track Status:** NET-827 fail-fix track attempt 3 of 10; AG Carbon writer try 1 of 4 (Eric 4/10 rule).
- **Target Deliverable:** `PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.8_AG-CARBON_20261110.md`
- **File Metrics:**
  - Path: `1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\Carbon\PLAN_NET-827_FAILFIX-B1B5_STRIPE-CHECKOUT-PREVIEW_v1.8_AG-CARBON_20261110.md` (and exact mirror at `1 NUMISTA.AI\BETA TEST\MY TESTING\10 NOV 2026\`)
  - Size: **65,130 bytes**
  - SHA-256: **`BCC3F2D33B4799F2D4F8D4B17E0CAC226BDC223184248D3E75DE6E9C452A2E38`**

---

## 1. Material Defect Closures (Targeting Score >= 95 / 100)

### N1: Preview Backend Full Isolation
- All Firestore and GCS client initialisations across the backend are strictly routed through `env_guard.py`:
  - `main.py:349` (`db = firestore.Client(...)`) replaced with guarded client `build_firestore_client(load_data_config())` via `routes.deps.get_db()`.
  - `main.py:352` (`gcs_client = gcs.Client(...)`) replaced with guarded `get_gcs_client()`, and `USER_CONTENT_BUCKET` is guarded to require a dedicated non-production bucket name in preview mode.
  - `routes/subaccount_routes.py:26` (`firestore.Client(project="studio-9101802118-8c9a8")`) hard-coded client removed; replaced with guarded `deps.get_db()`.
  - `routes/export_routes.py` explicitly specified to use guarded `deps.get_db()`.
  - `main.py` collection routes (`/api/collection/count`, `/api/collection/clear`) and all coin manipulation paths brought into scope and enforce entitlement/lock check.
  - **PV-4 Check Enhanced:** Added read-only `gcloud projects get-iam-policy` check verifying that the preview Cloud Run service account holds **zero** roles on production project `studio-9101802118-8c9a8`.

### N2: Preview App Direct Firestore Isolation
- **Option (b) Adopted:** Because `numista_mobile` has fixed production Firebase config (`firebase_options.dart`), **synthetic preview testers (`ft-preview-01` to `04`) NEVER sign in to the client app on `p7-gate` directly**.
- All preview verification tests run exclusively via automated/scripted HTTP calls against the preview backend Cloud Run URL using Firebase Auth ID tokens.
- Manual in-app upgrade path for synthetic testers removed from Section 8.
- Added **PV-4.5 Check & Cleanup:** Gated script queries production Firestore for any documents under synthetic UIDs or emails to confirm zero prod documents exist, and deletes any stray test documents under explicit Eric YES before PV-6.

### N3: App Locked Enforcement & Legacy Email Coin Support
- **Firestore Security Rules:** Added `isNotLocked()` helper to `numista_mobile/firestore.rules` denying client `read`, `update`, and `delete` if `resource.data.locked_pending_upgrade == true`. Create operations exceeding limit fail closed. (Explicit Eric YES-gated deployment with documented rollback).
- **Backend Coin Access:** Both `users/{uid}/coins` AND legacy `users/{email}/coins` (as well as currency, wishlist subcollections) are fully checked by `lock_overflow_coins` and `unlock_user_coins`.
- **CSV Export:** Evaluates and exports coins from BOTH `users/{uid}/coins` and `users/{email}/coins`.

---

## 2. Advisories Closed (A1–A6)
- **A1:** Grant transaction skips writing `stripe_payments/{payment_intent_id}` inside checkout session grant when `payment_intent` is None (relying on `invoice.paid` for subscriptions).
- **A2:** `lock_overflow_coins` sorts coins safely by handling missing `created_at` (treating missing timestamp as epoch 0), and fails closed instead of swallowing errors.
- **A3:** `decide_grant` takes `session_created` timestamp to verify Christmas window at fulfillment.
- **A4:** Explicitly defines `beta_special_until` format as ISO-8601 string parsed to timezone-aware UTC datetime (or float epoch seconds) for comparison.
- **A5:** CSV injection protection prefixes cells starting with `=`, `+`, `-`, `@`, `\t` (tab), or `\r` (carriage return) with `'`.
- **A6:** Header and track attempt accurately counted as attempt 3 of 10, Carbon writer try 1 of 4.

---

## 3. Limits & Next Gates
- **PLAN ONLY:** Zero code execution, zero commits of code, zero Firestore/Stripe/Cloud Run writes.
- HOLDs `74611e05` and `41b8bd5f` remain in full force.
- `origin/main` strictly pinned at `9f04550a`.
- **Next Gate:** Designated Grok CoS 95 score, then full-plan SAG 95, then Eric's typed YES.
