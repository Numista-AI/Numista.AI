# Numista.Ai System Scan Report - 2026-07-10

## Executive Summary: **FAIL** (Backend Degraded / Test Regressions)
The system check has identified that the local codebase has successfully resolved all **Dart Analyzer warnings (0 issues found)**, and local database integrity is verified (11,928 total records). However, the live Cloud Run backend container (`numista-backend-xwqkbwqvuq-uc.a.run.app`) does not have the latest code version deployed. Consequently, critical endpoints returned **404 Not Found**, causing 10 out of 104 Playwright tests to fail. The core frontend navigation and read-only suites (01–07) pass cleanly (94/104 tests passed).

---

## Critical Errors & Warnings

### 1. Production Backend HTTP 404 (Missing Deployed Routes)
- **Issue**: The active Cloud Run container returns **404 Not Found** for all newly implemented Greysheet, Deals, and Portfolio API routes.
- **Context**: 
  - Local `main.py` contains endpoints for `/api/greysheet/config`, `/api/greysheet/batch`, `/api/greysheet/cac`, `/api/portfolio/snapshot`, and `/api/ebay/search`.
  - The live backend at `https://numista-backend-xwqkbwqvuq-uc.a.run.app` returns 404 for all these URLs, showing that the container has not been built/deployed with the current local changes.

### 2. Python Test Suite Execution Blocked by Environment Compatibility
- **Issue**: Running the Python `pytest` suite locally failed with `ValueError: I/O operation on closed file.`
- **Context**:
  - The local virtual environment runs **Python 3.14.2**, which has capture/buffering compatibility issues with the installed version of `pytest` (9.1.1).
  - This is an environment/runner compatibility issue rather than a failure of the backend python test logic itself.

---

## Greysheet API Health

- **Key Presence**: ❌ **Missing** from local `numista_backend/.env` (no `GREYSHEET_API_KEY` or `GREYSHEET_API_TOKEN` variables exist in the file).
- **Endpoint Probe Results**:
  - `GET /api/greysheet/config` -> ❌ **404 Not Found**
  - `POST /api/greysheet/batch` -> ❌ **404 Not Found**
  - `POST /api/greysheet/resolve` -> ❌ **404 Not Found**
  - `GET /api/greysheet/cac` -> ❌ **404 Not Found**
  - `GET /api/greysheet/pricing/429` -> ❌ **404 Not Found**
- **API Tier Detected**: **Basic** (due to missing production keys, falling back to CPG Retail price guide / basic resolution).
- **Fallback Rate Estimate**: **100%** (the backend resolves all bids via the fallback formula `cpg_retail * 0.80` due to the lack of wholesale API keys).

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
| `08-greysheet-valuation.spec.js` | 12 | ❌ **FAIL** (T11, T12) | Config and batch endpoints return 404 on the live Cloud Run backend. |
| `09-deals-arbitrage.spec.js` | 8 | ❌ **FAIL** (T05, T06) | EPN affiliate `/api/ebay/search` returns 404; Deals screen fails state assertion. |
| `10-greysheet-coin-detail.spec.js` | 14 | ❌ **FAIL** (T04, T10, T11, T12, T13, T14) | Pricing, config, batch, resolve, cac, and portfolio snapshot endpoints return 404 on the live Cloud Run backend. |

---

## Recommended Fixes

1. **Deploy Backend Changes**: Deploy the local `numista_backend` code to the production Cloud Run container so that the new `/api/greysheet/*` and `/api/portfolio/*` routes are registered on the live backend.
2. **Configure Greysheet API Credentials**: Add valid production keys for `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` to `numista_backend/.env` and the Cloud Run configuration to activate the **Advanced** tier and bypass the fallback logic.
3. **Resolve Pytest Runner Compatibility**: Run the Python backend test suite on a fully supported stable version of Python (e.g., Python 3.11 or 3.12) to avoid internal `pytest` I/O conflicts with Python 3.14.2.
