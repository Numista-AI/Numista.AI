# SCAN REPORT: Numista.AI System Audit (v4.0)

## Executive Summary
* **Status:** ⚠️ **WARNING** (The system scan completed with 1 minor UI E2E test failure, 3 bypassed/hanging backend tests due to expired local ADC credentials, and 1 frontend unused element warning. The active codebase is compile-clean and uses correct model IDs, but the Greysheet API is in fallback mode due to empty credentials).
* **Scan Date:** 2026-07-15
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.0, Frontend v4.0

---

## Critical Errors & Warnings
1. **Empty Greysheet API Credentials:** `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` are empty in `numista_backend/.env` (lines 51-52).
2. **Obsolete Backend URL in Local Skill Instructions:** The defunct/orphan Cloud Run URL (`https://numista-backend-xwqkbwqvuq-uc.a.run.app`) is referenced in `project-scanner/SKILL.md` (which returns `404 Not Found` for both `/api/greysheet/config` and `/api/greysheet/pricing/<gsid>`).
3. **Playwright Test Failure (T05):** `T05: Deals Screen renders a valid state` in `tests\09-deals-arbitrage.spec.js` failed due to strict viewport screenshot length expectations (expecting > 50,000 bytes, received 30,758). This is because the test clicked multiple targets in a loop, navigating away to the AI Scan Preview screen (which has a smaller screenshot size).
4. **Expired Local Google Application Default Credentials (ADC):** Python `pytest` suite hangs/blocks on Firestore-connected tests (`test_resolve_greysheet_raw`, `test_pricing_endpoint`, `test_daily_snapshot_endpoint`) due to expired Google ADC OAuth credentials on the developer host machine.
5. **Latent Deprecated Model Reference:** The default argument for `primary_model` in `services/greysheet_service.py` (line 461) is set to `"gemini-2.0-flash"`. Per the July 2026 Gemini Deprecation Schedule, `gemini-2.0-flash` was officially shut down on June 1, 2026. While `main.py` overrides this with `PRIMARY_MODEL = "gemini-3.5-flash"`, any third-party calls relying on the default parameter signature will fail.
6. **Unused Dart Element in Frontend:** The Dart Analyzer reported 1 warning (`_buildArbitrageDealsCard` is unused in `lib/screens/home_dashboard.dart`).

---

## Greysheet API Health
* **Key Presence:** ❌ (Empty in `numista_backend/.env` file)
* **Endpoint Probe Results:**
  * **Defunct/Obsolete URL (`numista-backend-xwqkbwqvuq-uc.a.run.app`):**
    * `/api/greysheet/config`: ❌ `404 Page not found`
    * `/api/greysheet/pricing/429`: ❌ `404 Page not found`
  * **Active Production URL (`numista-backend-568985927038.us-central1.run.app`):**
    * `/api/greysheet/config`: ✅ `200 OK` (returns `"tier":"Basic"`, `"mode":"fallback"`)
    * `/api/greysheet/pricing/429`: ✅ `200 OK` (returns valid pricing payload via fallback credentials)
* **API Tier Detected:** `Basic` (fallback mode)
* **Fallback Rate Estimate:** `100%` (The backend runs entirely on default fallback credentials due to empty variables).

---

## Data Pipeline Audit
* **Proxy Configuration (`scrapers.py`):** Verified. `numista_backend/numista_scraper/config.py` uses `NUMISTA_SCRAPE_HTTP_PROXY`/`NUMISTA_SCRAPE_HTTPS_PROXY` env vars.
* **Brain Watcher (`brain_watcher.py`):** Verified. `INBOX_DIR` is set strictly to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.
* **Model Check:** Verified. No usages of deprecated model IDs like `gemini-1.5-flash` found in the active codebase; all production files have been updated to `gemini-3.5-flash` or newer.

---

## Test Logs Summary
### 1. Backend Python Tests (`pytest`)
* **Total:** 9 tests
* **Passed:** 6 tests
  - `tests/test_greysheet.py::test_item_type_guardrails` (Passed)
  - `tests/test_greysheet.py::test_deals_endpoints` (Passed)
  - `tests/test_valuations.py::test_valuation_ranges` (Passed)
  - `tests/test_valuations.py::test_valuation_single_value_with_commas` (Passed)
  - `tests/test_valuations.py::test_valuation_simple_number` (Passed)
  - `tests/test_valuations.py::test_valuation_invalid_gibberish` (Passed)
* **Bypassed/Hanging:** 3 tests
  - `test_resolve_greysheet_raw`
  - `test_pricing_endpoint`
  - `test_daily_snapshot_endpoint`
  - **Cause:** These tests hit Firestore and Vertex AI endpoints, triggering an OAuth token refresh that blocks indefinitely or throws `RefreshError` due to expired local developer Google ADC credentials.

### 2. Frontend Playwright E2E Tests
* **Total:** 104 tests
* **Passed:** 103 tests
* **Failed:** 1 test
  - `tests\09-deals-arbitrage.spec.js` -> `T05: Deals Screen renders a valid state`
  - **Cause:** The screenshot byte length was below the 50,000-byte threshold (received 30,758 bytes) because the test clicks targets in a loop and navigates to the "Free AI Scan Preview" page instead of staying on the Deals screen.

### 3. Flutter Dart Analyzer
* **Status:** ⚠️ 1 issue found (unused element warning).
* **Warning Details:**
  `warning - The declaration '_buildArbitrageDealsCard' isn't referenced - numista_mobile\lib\screens\home_dashboard.dart:1414:10 - unused_element`

---

## Recommended Fixes
1. **Reauthenticate Local Google ADC:** Run `gcloud auth application-default login` on the host machine to restore Firestore/Vertex AI authentication and allow all 9 Python backend tests to complete.
2. **Refactor Playwright T05 Test:** Adjust `09-deals-arbitrage.spec.js` to click only the exact Deals card coordinates (like `780, 500` used in `T03`/`T04`) instead of clicking multiple targets in a loop, or relax the strict screenshot size threshold.
3. **Clean Up Unused Dart Widget:** Delete the unused `_buildArbitrageDealsCard` method at `lib/screens/home_dashboard.dart:1414` to clean up the Flutter analyzer warning.
4. **Configure Greysheet Credentials:** Populate `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` in the production environment settings to transition from `Basic` fallback mode to `Advanced` tier.
5. **Update Default Model Signature:** Change the default value of the `primary_model` argument in `services/greysheet_service.py:resolve_gsid_hybrid` from `"gemini-2.0-flash"` to `"gemini-3.5-flash"`.
6. **Update Skill Documentation:** Replace the obsolete URL `numisma-backend-xwqkbwqvuq-uc.a.run.app` with `numisma-backend-568985927038.us-central1.run.app` in `project-scanner/SKILL.md` to avoid future false alarms during system checks.
