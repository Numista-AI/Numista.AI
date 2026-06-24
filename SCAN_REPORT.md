# Numista.Ai System Scan Report

## Executive Summary
- **Overall Scan Status:** ✅ **PASS**
- **Frontend Test Suite (Playwright):** ✅ **PASS** (63/63 tests passed, taking 10.1 minutes)
- **Backend API Test Suite (Python):** ✅ **PASS** (48/48 checks passed, with 1 replication latency warning)
- **Code Compilation & Syntax Check:** ✅ **PASS** (141/141 active files compiled successfully)

The Numista.Ai system is functionally healthy. The critical backend API crashes (such as `TypeError` in grade review float conversion) and invalid Gemini model identifiers have been successfully resolved. Both the frontend E2E navigation suite and the backend overnight verification suite are fully operational and passing. Some minor warnings remain regarding data replication lag, local script library deprecation, and reporting utility logic.

---

## Critical Errors & Warnings

> [!NOTE]
> No critical blocker errors were found in the active production codebase. All previously reported runtime crashes have been verified as resolved.

### 1. Grade Review Stats replication latency (Warning)
* **Affected Endpoint:** `GET /api/grade_review/stats`
* **Symptom:** Scripts checking stats immediately after submitting a review receive un-updated counts.
* **Root Cause:** A warning `Stats may not have updated (pending was 61, now 61)` occurs during API testing. This points to standard Firestore query replication lag or server-side latency when reading counts immediately after writes.

### 2. Legacy `vertexai` library deprecation/removal (Warning)
* **Affected Files:** legacy scripts under [_scripts](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts) (e.g. [auto_annotate_checklist_dataset.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/auto_annotate_checklist_dataset.py), [coin_image_pipeline.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/coin_image_pipeline.py))
* **Symptom:** Running these scripts from command line will fail starting today (June 24, 2026).
* **Root Cause:** The legacy `vertexai` library has reached its final deprecation date and will fail to execute because of server-side removals. Active production code has already migrated to `google-genai` and `@google/genai`, but these utility files still import `vertexai`.

### 3. Playwright test report generator table bug (Warning)
* **Affected File:** [generate_report.js:L130-141](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/generate_report.js#L130-L141)
* **Symptom:** The summary table in the morning report lists `0` tests run for each individual spec file, although the overall metric count is correct (63).
* **Root Cause:** In [generate_report.js](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/generate_report.js), the report generator loop walks `suite.specs` directly at the top level, but Playwright nests spec results inside nested suites (`suite.suites`).

---

## Data Pipeline Audit

We evaluated local datasets against the Numista.AI golden schema defined in [coin-schema.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json):

### 1. Main Collection Backup ([AJ's Coins Backup 8 APR 26.csv](file:///c:/Users/ericd/Documents/MyVertexProject/AJ's%20Coins%20Backup%208%20APR%2026.csv))
* **Required Fields:** All required fields (`Year`, `Denomination`, `Quantity`, `Condition`) are present.
* **Matching Fields:** 15 of 32 columns match the Golden Schema.
* **Extra/Non-Standard Columns:** Contains 17 columns not in the schema (e.g. `Surface & Strike Quality`, `AI Estimated Value`, `Numismatic Report`, `imageUrlObverse`, `imageUrlReverse`).
* **Discrepancies:** Key columns use non-standard names:
  * `Grading Cert #` instead of `Certification Number`
  * `Cost` instead of `Purchase Cost`
  * `Personal Notes` instead of `Personal Notes I`
  * `Personal Ref #` instead of `Personal Reference #`

### 2. Internal Pipeline CSVs
* **Files:** `AJ_Currency_Parsed.csv`, `AJ_Currency_Parsed_v2.csv`, `AJ_Manual_Image_Sourcing_Currency.csv`
* **Status:** ❌ **Incompatible** (None of these files contain the required fields for coin datasets, representing banknotes/currency rather than coins).

---

## Test Logs Summary

### 1. Playwright E2E Test Suite (`npm test`)
* **Status:** ✅ **100% Pass** (63/63 tests passed)
* **Report File:** [2026-06-24_morning_report.md](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/reports/2026-06-24_morning_report.md)
* **Summary:** End-to-end authentication, navigation, and core interface screens are functioning correctly.

### 2. Python API Test Suite (`run_overnight_tests.py`)
* **Status:** ✅ **100% Pass** (48/48 checks passed)
* **Log File:** [overnight_test_results.txt](file:///c:/Users/ericd/Documents/MyVertexProject/overnight_test_results.txt)
* **Summary:** Health checks, binder scans, template downloads, community nicknames submission and voting, and grade reviews are fully operational. Normalization functions successfully map edge-case conditions (e.g. `BU` mapped to `MS-63`, `PR69` mapped to `PF-69`) under the virtual environment interpreter.

---

## Recommended Fixes

1. **Fix Playwright Report Generator (Medium):**
   Modify lines 130–141 in [generate_report.js](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/generate_report.js#L130-L141) to recursively traverse nested suites when counting spec tests.
2. **Migrate Legacy Python Utilities (Medium):**
   Update legacy tools in [_scripts](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts) to use the new `google-genai` client, removing any reference to `vertexai`.
3. **Map CSV Column Names on Ingest (Low):**
   Integrate a column re-mapper in the CSV parser to map legacy labels (`Grading Cert #`, `Cost`, `Personal Notes`) to their corresponding schema-defined counterparts (`Certification Number`, `Purchase Cost`, `Personal Notes I`).
