# SCAN REPORT: Numista.AI System Audit (v4.0)

## Executive Summary
* **Status:** ⚠️ **WARNING** (Unit/E2E test suites passed with 1 minor UI validation failure; Greysheet API is in fallback mode due to empty credentials).
* **Scan Timestamp:** 2026-07-13
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.0, Frontend v4.0

---

## Critical Errors & Warnings
1. **Empty Greysheet API Credentials:** `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` are empty in `numista_backend/.env` (lines 51-52).
2. **Old Endpoint Reference in Documentation:** Local skill instructions references the defunct/orphan Cloud Run service (`numista-backend-xwqkbwqvuq-uc.a.run.app`), which yields `404 Not Found`.
3. **Playwright test failure (T05):** `T05: Deals Screen renders a valid state` failed due to strict viewport screenshot length expectations (expecting > 50000 bytes, received less).
4. **Unused Dart Element in Frontend:** The Dart Analyzer reported 1 warning (`_buildArbitrageDealsCard` is unused in `lib/screens/home_dashboard.dart`).

---

## Greysheet API Health
* **Key Presence:** ❌ (Empty in `.env` file)
* **Endpoint Probe Results:**
  * **Old/Orphan URL (`xwqkbwqvuq`):**
    * `/api/greysheet/config`: ❌ `404 Not Found`
    * `/api/greysheet/pricing/429`: ❌ `404 Not Found`
  * **Active Production URL (`568985927038`):**
    * `/api/greysheet/config`: ✅ `200 OK`
      * Response: `{"status":"active","mode":"fallback","tier":"Basic","endpoints":...}`
    * `/api/greysheet/pricing/429`: ✅ `200 OK`
      * Response: Valid pricing payload returned using fallback credentials.
* **API Tier Detected:** `Basic` (GreyVal1 only, via fallback)
* **Fallback Rate Estimate:** `100%` (Backend relies entirely on hardcoded `DEFAULT_API_KEY` / `DEFAULT_API_TOKEN` for all external calls).

---

## Data Pipeline Audit
* **Proxy Configuration (`scrapers.py`):** Verified. `numista_backend/numista_scraper/scrapers.py` uses `get_scrape_proxy()` which correctly loads proxies from `NUMISTA_SCRAPE_HTTP_PROXY`/`NUMISTA_SCRAPE_HTTPS_PROXY` env vars.
* **Brain Watcher (`brain_watcher.py`):** Verified. `INBOX_DIR` is set strictly to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.
* **Model Check:** Verified. No usages of deprecated model IDs like `gemini-1.5-flash` found in the active codebase; all production files have been updated to `gemini-3.5-flash` or newer.

---

## Test Logs Summary
### 1. Backend python tests (`pytest`):
* **Total:** 11 tests
* **Passed:** 11 (100% pass rate)
* **Failed:** 0

### 2. Frontend Playwright tests:
* **Total:** 104 tests
* **Passed:** 103
* **Failed:** 1
  * **Failure Details:** `tests/09-deals-arbitrage.spec.js` -> `T05: Deals Screen renders a valid state`
  * **Cause:** The screenshot byte length was below the hard 50,000-byte threshold, despite the page loading correctly.

### 3. Flutter Dart Analyzer:
* **Status:** ⚠️ 1 issue found (unused element warning).
* **Warning Details:** `The declaration '_buildArbitrageDealsCard' isn't referenced - lib\screens\home_dashboard.dart:1414:10 - unused_element`

---

## Recommended Fixes
1. **Configure Greysheet Credentials:** Populate the `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` in the production environment variables to upgrade from `Basic` fallback tier to `Advanced` tier.
2. **Update Local Documentation:** Replace obsolete `numista-backend-xwqkbwqvuq-uc.a.run.app` references in `project-scanner` and developer documentation with the active production backend URL (`https://numista-backend-568985927038.us-central1.run.app`).
3. **Refactor Playwright T05 Assertion:** Relax the strict screenshot size check (`expect(buf.length).toBeGreaterThan(50000)`) in `09-deals-arbitrage.spec.js` to prevent false-positive failures on layout size fluctuations.
4. **Remove Unused Dart Code:** Clean up the unused widget function `_buildArbitrageDealsCard` in `numista_mobile/lib/screens/home_dashboard.dart` to resolve the analyzer warning.
