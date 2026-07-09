# Numista.Ai System Scan Report - 2026-07-09

## Executive Summary: **FAIL** (Backend Degraded / Test Regressions)
The system check has identified critical routing errors on the production backend container and missing Greysheet API credentials that lead to degraded valuation features. While the frontend and core app navigation function correctly (suites 01–07 passing, 94/104 tests passed), the v4.0.0 Greysheet and Deals test suites (08–10) are failing (10/104 tests failed) due to a mismatch between test expectations and backend FastAPI routes/credentials.

---

## Critical Errors & Warnings

### 1. Production Backend HTTP 404 & Mismatched Routes
- **Issue**: Production Cloud Run URL (`numista-backend-xwqkbwqvuq-uc.a.run.app`) returns **404 Not Found** or other error responses for critical Greysheet/Deals endpoints.
- **Context**:
  - The routes `/api/greysheet/config`, `/api/greysheet/batch`, `/api/greysheet/cac`, and `/api/ebay/search` do not exist in the backend `main.py` routing file.
  - The daily snapshot endpoint in `main.py` is registered as a `POST /api/portfolio/snapshot/daily` route, but the test suite expects `GET /api/portfolio/snapshot`.
  - The resolver endpoint `/api/greysheet/resolve` and coin detail/pricing endpoint `/api/greysheet/pricing/{gsid}` fail due to credentials or configuration mismatches when queried under test conditions.

### 2. Dart Analyzer Warnings (30 Issues)
- **Issue**: `flutter analyze` failed with exit code 1 due to code health warnings.
- **Context**:
  - **11 Warnings**: Includes unused imports (`dart:typed_data` in `microscope_scan_screen.dart`), unused local variables (`margin` in `deals_screen.dart`), unused fields (`_fmt` in `my_collection_screen.dart`), and a subtype implementation of a sealed class (`DocumentSnapshot` in `guest_seed_service.dart`).
  - **19 Info Messages**: Deprecated Flutter member usages (e.g., `withOpacity` should be replaced with `.withValues()`, `activeColor` should be replaced with `activeThumbColor`/`activeTrackColor`), and `avoid_print` statements in production files.

### 3. Production Deployment Authentication Sync
- **Issue**: GCloud service account verification returned authentication errors.
- **Context**: The active session requires a re-authentication via `gcloud auth login` to check the live cloud storage bucket configurations and sync deployment parameters.

---

## Greysheet API Health

- **Key Presence**: ❌ **Missing** from local `.env` and Cloud Run service config (defaults to fallback development credentials starting with `1FCAE3B4` / `D876F1BA`).
- **Endpoint Probe Results**:
  - `GET /api/greysheet/config` -> ❌ **404 Not Found**
  - `GET /api/greysheet/pricing/429` -> ❌ **404 Not Found**
  - Direct request to `https://cpgpublicapiv2.greysheet.com/api/GetPricingRequest` -> ⚠️ **Degraded** (returns CPG Retail price guide, but `GreyVal` wholesale values are empty/null).
- **API Tier Detected**: **Basic/Restricted** (no wholesale data returned).
- **Fallback Rate Estimate**: **100%** (the backend resolves all bids via the fallback formula `cpg_retail * 0.80` due to the lack of wholesale API data).

---

## Test Logs Summary

- **Total Tests**: 104
- **Passed**: 94 ✅
- **Failed**: 10 ❌

### Current Suite Status

| Suite | Tests | Expected Status | Root Cause of Failure |
| :--- | :--- | :--- | :--- |
| `01-homepage.spec.js` | 7 | ✅ PASS | Core homepage resolves and loads Flutter canvas cleanly. |
| `02-auth-ui.spec.js` | 8 | ✅ PASS | Basic user login, signup tabs, and validation render. |
| `03-demo-navigation.spec.js` | 24 | ✅ PASS | Read-only demo navigation sidebar routes load successfully. |
| `04-registration.spec.js` | 8 | ✅ PASS | Registration fields and flow render. |
| `05-navigation.spec.js` | 12 | ✅ PASS | Standard user dashboard and portfolio routes. |
| `06-edge-cases.spec.js` | 10 | ✅ PASS | Form errors and network timeouts handled gracefully. |
| `07-error-library.spec.js` | 1 | ✅ PASS | Sanity checks for application error logger. |
| `08-greysheet-valuation.spec.js` | 12 | ❌ **FAIL** (T11, T12) | Endpoints `/api/greysheet/config` and `/api/greysheet/batch` return 404. |
| `09-deals-arbitrage.spec.js` | 8 | ❌ **FAIL** (T05, T06) | Endpoint `/api/ebay/search` returns 404 (not defined in `main.py`); Deals screen fails state assertion. |
| `10-greysheet-coin-detail.spec.js` | 14 | ❌ **FAIL** (T04, T10, T11, T12, T13, T14) | Config/batch/cac/snapshot endpoints fail or return 404; snapshot expects GET but backend implements POST; resolve/pricing endpoints fail due to configuration. |

---

## Recommended Fixes

1. **FastAPI Route Sync**: Update `main.py` to register the missing endpoints (`/api/greysheet/config`, `/api/greysheet/batch`, `/api/greysheet/cac`, and `/api/ebay/search`), or update the test suite scripts to match the actual routes implemented (`/api/greysheet/batch-resolve` and `/api/portfolio/snapshot/daily` POST).
2. **Greysheet Credentials**: Provision valid production API tokens for `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` to transition the integration from the fallback `Basic` mode to the `Advanced` wholesale tier.
3. **Dart Code Health Cleanup**: Address the 30 analyzer warnings in the mobile workspace (specifically removing unused variables and updating the deprecated `withOpacity` and `activeColor` methods).
4. **Deploy Sync**: Re-authenticate the active local shell session to synchronize settings with GCP and Cloud Run.
