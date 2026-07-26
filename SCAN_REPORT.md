# SCAN REPORT: Numista.AI System Audit (v4.0)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with 100% test pass rate across unit test and E2E suites. All 16 Python backend unit tests passed, 120 Playwright E2E tests passed, 661 Python files compiled cleanly with 0 errors, Flutter Dart analyzer returned 0 issues, Gemini model IDs strictly adhere to 2026 production standards (`gemini-3.6-flash` / `gemini-3.5-flash`), and Greysheet API endpoints returned HTTP 200 OK).
* **Scan Date:** 2026-07-26
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.0, Frontend v4.0

---

## Critical Errors & Warnings
1. **Fallback Greysheet Credentials:** `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` are using default dev fallback keys (`1FCAE3B4-966A-4F25-AFA1-BE242C26856B`), operating the backend in **Basic** tier mode rather than **Advanced** tier.

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across the entire repository.
* **Production Model Alignment:** Primary models across backend services, scripts, and Flutter frontend (`config.py`, `main.py`, `brain_processor.py`, `vertex_client.py`) are `gemini-3.6-flash`, `gemini-3.5-flash`, and `gemini-3.1-pro-preview` in strict compliance with AGENTS.md Rule 6.
* **Model Usage Counts Across Codebase:**
  - `gemini-3.5-flash`: 56 usages
  - `gemini-3.6-flash`: 2 usages
  - `gemini-3.1-pro-preview`: 4 usages
  - `gemini-3.5-flash-lite`: 3 usages
  - `gemini-3.1-flash-image`: 2 usages

---

## Greysheet API Health
* **Key Presence:** ⚠️ (Loaded via dev fallback key / Firestore config)
* **Endpoint Probe Results (`https://numista-backend-568985927038.us-central1.run.app`):**
  * `/api/greysheet/config`: ✅ `200 OK` (`{"status":"active","mode":"fallback","tier":"Basic"}`)
  * `/api/greysheet/pricing/101`: ✅ `200 OK` (returns valid pricing payload for GSID 101)
  * `/api/greysheet/cac`: ✅ `200 OK` (`{"status":"active","cac_premium_multiplier":1.2}`)
  * `/api/portfolio/snapshot/daily`: ℹ️ `405 Method Not Allowed` (POST-only trigger endpoint)
* **API Tier Detected:** `Basic` (GreyVal1 fallback)
* **Fallback Rate Estimate:** `100%` (Backend uses standard fallback credentials when production environment tokens are omitted)

---

## Data Pipeline & Test Isolation Audit
* **Proxy Configuration (`scrapers.py` / `config.py`):** Verified. `numista_backend/numista_scraper/config.py` uses `NUMISTA_SCRAPE_HTTP_PROXY` and `NUMISTA_SCRAPE_HTTPS_PROXY` environment variables to isolate scraper traffic from global `HTTP_PROXY`.
* **Brain Watcher (`brain_watcher.py`):** Verified. `INBOX_DIR` is set strictly to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.
* **Test Isolation:** Verified. Automated E2E tests run against designated test accounts and local emulator suites to guarantee zero production data mutation.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) and Secure Passport schema endpoints passed unit test suite (`test_transfer.py`).
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/estate/...`) and ownership handshakes confirmed operational.
* **Vertex AI & Search Grounding:** Verified. Vertex AI Data Store connection and Morgan Chat Google Search grounding configurations active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series registration and Uncirculated Set / checklist templates validated.

---

## Test Logs Summary
### 1. Backend Python Unit Tests (`pytest`)
* **Total:** 16 tests
* **Passed:** 16 / 16 tests (100% pass rate in 23.41s)
  - `tests/test_deal_spotter.py`: 3/3 passed
  - `tests/test_greysheet.py`: 5/5 passed
  - `tests/test_ingestion.py`: 2/2 passed
  - `tests/test_transfer.py`: 2/2 passed
  - `tests/test_valuations.py`: 4/4 passed

### 2. Python Codebase Compilation
* **Status:** 100% Clean
* **Files Compiled:** 661 Python files compiled without any syntax or import errors.

### 3. Frontend Playwright E2E Tests
* **Total Specs:** 120 tests across 12 spec files in `numista_tests/tests`
* **Passed:** 120 / 120 passed (100% pass rate in 54.8s)
* **Skipped / Failed:** 0

### 4. Flutter Dart Analyzer
* **Status:** 0 Issues Found (ran in 10.2s).
* **Details:** `numista_mobile` cleanly analyzed with 0 errors, 0 warnings, 0 lints.

---

## Recommended Fixes
1. **Configure Production Greysheet Credentials:** Add production `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` environment variables to Cloud Run service settings to unlock **Advanced** bid/ask pricing tier.
2. **Maintain Skill Documentation:** Keep `project-scanner/SKILL.md` aligned with the production Cloud Run URL (`numista-backend-568985927038.us-central1.run.app`).
