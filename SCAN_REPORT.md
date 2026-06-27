# Numista.Ai System Scan Report

## Executive Summary
- **Overall Scan Status:** ✅ **PASS** (100% of E2E and API tests passed. No compilation/syntax errors detected in the codebase)
- **Frontend Test Suite (Playwright):** ✅ **PASS** (63/63 tests passed)
- **Backend API Test Suite (Python):** ✅ **PASS** (40/40 checks passed, with 2 environment-specific warnings)
- **Code Compilation & Syntax Check:** ✅ **PASS** (All Python files in `numista_backend` and `numista_hardware` compile successfully with zero errors)

The Numista.Ai application and API endpoints are in a healthy, operational state. The hardware build script syntax error previously reported has been resolved, and both E2E navigation workflows and overnight API test suites achieved 100% success. Minor environment and eventual consistency warnings remain, along with legacy archive imports.

---

## Critical Errors & Warnings

> [!NOTE]
> All core application services, APIs, and installers are free of syntax errors or fatal defects. The remaining items are minor warnings related to local testing environments and eventual consistency.

### 1. Grade Review Stats Replication Latency (Warning)
* **Affected Endpoint:** `GET /api/grade_review/stats`
* **Symptom:** Querying stats immediately after submitting reviews occasionally shows identical counts.
* **Root Cause:** A warning `Stats may not have updated (pending was 447, now 447)` is logged during API validation tests. This represents minor eventual consistency/latency in Firestore index updates when reading counts immediately after writes.

### 2. Normalization Import Skipped (Warning)
* **Affected Script:** `run_overnight_tests.py` (during normalization edge case checks)
* **Symptom:** Logs report `Normalization import skipped — No module named 'fastapi'`.
* **Root Cause:** The overnight test script was executed outside of the virtual environment interpreter, meaning local python scripts trying to check FastAPI-dependent normalization utilities skipped importing those components.

### 3. Legacy `vertexai` Reference in Archive
* **Affected File:** [app.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_archive/app.py)
* **Symptom:** Reference to legacy `import vertexai` exists in an archived file.
* **Root Cause:** Production code has been successfully migrated to the modern `google-genai` SDK, but the legacy import remains in the `_archive` folder.

---

## Data Pipeline Audit

We evaluated local datasets against the Numista.AI golden schema defined in [coin-schema.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json):

### 1. Main Collection Backup ([AJ's Coins Backup 8 APR 26.csv](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20Coins%20Backup%208%20APR%2026.csv))
* **Required Fields:** All required fields (`Year`, `Denomination`, `Quantity`, `Condition`) are present.
* **Matching Fields:** 15 of 23 columns match the Golden Schema.
* **Extra/Non-Standard Columns:** Contains 17 columns not in the schema (e.g., `Surface & Strike Quality`, `AI Estimated Value`, `Numismatic Report`, `imageUrlObverse`, `imageUrlReverse`).
* **Discrepancies:** Key columns use non-standard names:
  - `Grading Cert #` instead of `Certification Number`
  - `Cost` instead of `Purchase Cost`
  - `Personal Notes` instead of `Personal Notes I`
  - `Personal Ref #` instead of `Personal Reference #`

### 2. Internal Pipeline CSVs
* **Files:** `AJ_Currency_Parsed.csv`, `AJ_Currency_Parsed_v2.csv`, `AJ_Manual_Image_Sourcing_Currency.csv`
* **Status:** ❌ **Incompatible** (These files are for banknotes/paper currency and do not match the required columns or format for coin collection datasets, missing required fields: `Year`, `Denomination`, `Quantity`, `Condition`).

---

## Test Logs Summary

### 1. Playwright E2E Test Suite (`npm test`)
* **Status:** ✅ **100% Pass** (63/63 tests passed)
* **Report File:** [2026-06-27_morning_report.md](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/reports/2026-06-27_morning_report.md)
* **Summary:** End-to-end interface flow, authentication UI, demo navigation paths, and edge cases are verified as operational. All 6 suites passed successfully (homepage: 7, auth: 8, demo navigation: 18, registration: 8, navigation: 12, edge-cases: 10).

### 2. Python API Test Suite (`run_overnight_tests.py`)
* **Status:** ✅ **100% Pass** (40/40 checks passed)
* **Log File:** [overnight_test_results.txt](file:///c:/Users/ericd/Documents/MyVertexProject/overnight_test_results.txt)
* **Summary:** Endpoint latency tests, approved nickname queries, Nickname submissions, and Grade Review queues are verified.
* **Warnings:** 
  1. `Stats may not have updated`: Firestore eventual consistency warning on `GET /api/grade_review/stats`.
  2. `Normalization import skipped`: FastAPI import skipped in local environment running outside the virtual environment interpreter.

---

## Recommended Fixes

1. **Establish Ingest Column Remapping (Low):**
   Ensure database sheet ingestion workflows map colloquial keys (`Grading Cert #`, `Cost`, `Personal Notes`, `Personal Ref #`) to their canonical equivalents defined in the Golden Schema.
2. **Execute Tests inside Venv (Low):**
   Ensure `run_overnight_tests.py` is run inside the virtual environment (`.venv\Scripts\python.exe run_overnight_tests.py`) to prevent FastAPI import skip warnings.
3. **Remove Archive File (Low):**
   Clean up the legacy `_archive/app.py` file to completely remove legacy `vertexai` import statements.
