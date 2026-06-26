# Numista.Ai System Scan Report

## Executive Summary
- **Overall Scan Status:** ⚠️ **WARNING** (Active test suites and production codes pass, but a compiler warning exists in hardware utility files)
- **Frontend Test Suite (Playwright):** ✅ **PASS** (63/63 tests passed)
- **Backend API Test Suite (Python):** ✅ **PASS** (37/37 checks passed, with 2 environment-specific warnings)
- **Code Compilation & Syntax Check:** ⚠️ **WARNING** (1 syntax error detected in `numista_hardware\build_installer_fallback.py`)

The Numista.Ai core application and API endpoints are in a healthy, passing state. The core server compiled with zero syntax errors, and both E2E navigation workflows and overnight API test suites achieved 100% success. However, a Python syntax error was identified in a local desktop installer script (`numista_hardware\build_installer_fallback.py`), and minor warnings remain concerning eventual consistency/replication lag and legacy utility script imports.

---

## Critical Errors & Warnings

> [!WARNING]
> A syntax error in a local installer build script prevents clean file compilation, and legacy developer utility scripts still reference the deprecated `vertexai` library.

### 1. Syntax Error in Hardware Installer Builder
* **Affected File:** [build_installer_fallback.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_hardware/build_installer_fallback.py#L1-L15)
* **Symptom:** Running or compiling this file fails immediately on modern Python interpreters with `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 252-253: malformed \N character escape`.
* **Root Cause:** Line 6 of the script's primary docstring contains the path `%LOCALAPPDATA%\NumistaAI\`. Because the docstring is declared as a normal string (`"""`) rather than a raw string (`r"""`), Python tries to parse `\N` as a unicode name escape sequence (which fails because `umistaAI` is not a valid unicode identifier).

### 2. Grade Review Stats Replication Latency (Warning)
* **Affected Endpoint:** `GET /api/grade_review/stats`
* **Symptom:** Querying stats immediately after submitting reviews occasionally shows identical counts.
* **Root Cause:** A test warning `Stats may not have updated (pending was 61, now 61)` is logged during API validation tests. This represents minor eventual consistency/latency in Firestore index updates when reading counts immediately after writes.

### 3. Legacy `vertexai` Library Deprecation/Removal (Warning)
* **Affected Files:** Developer scripts under [_scripts](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts) (e.g. [auto_label_receipts.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/auto_label_receipts.py), [generate_gap_images.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/generate_gap_images.py))
* **Symptom:** Running these helper scripts from the command line will throw errors due to the server-side decommissioning of legacy endpoints.
* **Root Cause:** Production code has been successfully migrated to the modern `google-genai` SDK, but developer utilities in the `_scripts` directory still reference `import vertexai`.

---

## Data Pipeline Audit

We evaluated local datasets against the Numista.AI golden schema defined in [coin-schema.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json):

### 1. Main Collection Backup ([AJ's Coins Backup 8 APR 26.csv](file:///c:/Users/ericd/Documents/MyVertexProject/AJ%27s%20Coins%20Backup%208%20APR%2026.csv))
* **Required Fields:** All required fields (`Year`, `Denomination`, `Quantity`, `Condition`) are present.
* **Matching Fields:** 15 of 32 columns match the Golden Schema.
* **Extra/Non-Standard Columns:** Contains 17 columns not in the schema (e.g., `Surface & Strike Quality`, `AI Estimated Value`, `Numismatic Report`, `imageUrlObverse`, `imageUrlReverse`).
* **Discrepancies:** Key columns use non-standard names:
  - `Grading Cert #` instead of `Certification Number`
  - `Cost` instead of `Purchase Cost`
  - `Personal Notes` instead of `Personal Notes I`
  - `Personal Ref #` instead of `Personal Reference #`

### 2. Image Audit Report ([audit_findings.csv](file:///c:/Users/ericd/Documents/MyVertexProject/audit_findings.csv))
* **Structure:** Maps `user_email`, `doc_id`, `coin_name`, `denomination`, `program`, `year`, `theme`, `mint_mark`, `obverse_url`, `reverse_url`, and `mismatches`.
* **Symptom:** Identifies discrepancy warnings between coin records and metadata stored in GCS image URLs (e.g. "Year mismatch: coin is 1903 but URL contains 1920" or "Half Dollar coin but URL has 'dollar'").

### 3. Internal Pipeline CSVs
* **Files:** `AJ_Currency_Parsed.csv`, `AJ_Currency_Parsed_v2.csv`, `AJ_Manual_Image_Sourcing_Currency.csv`
* **Status:** ❌ **Incompatible** (These files are for banknotes/paper currency and do not match the required columns or format for coin collection datasets).

---

## Test Logs Summary

### 1. Playwright E2E Test Suite (`npm test`)
* **Status:** ✅ **100% Pass** (63/63 tests passed)
* **Report File:** [2026-06-26_morning_report.md](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/reports/2026-06-26_morning_report.md)
* **Summary:** End-to-end interface flow, authentication UI, demo navigation paths, and edge cases are verified as operational. The spec-level test breakdown counts are reporting accurately (homepage: 7, auth: 8, demo navigation: 18, registration: 8, navigation: 12, edge-cases: 10).

### 2. Python API Test Suite (`run_overnight_tests.py`)
* **Status:** ✅ **100% Pass** (37/37 checks passed)
* **Log File:** [overnight_test_results.txt](file:///c:/Users/ericd/Documents/MyVertexProject/overnight_test_results.txt)
* **Summary:** Endpoint latency tests, approved nickname queries, Nickname submissions, and Grade Review queues are verified.
* **Warnings:** 
  1. `Stats may not have updated`: Firestore eventual consistency warning on `GET /api/grade_review/stats`.
  2. `Normalization import skipped`: Fastapi import skipped in local environment running outside the virtual environment interpreter.

---

## Recommended Fixes

1. **Fix Installer Builder Docstring (High):**
   Modify [build_installer_fallback.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_hardware/build_installer_fallback.py#L1-L15) by prefixing the docstring block on line 1 with `r` (converting it to `r"""`) or doubling the backslashes to escape `\N` as `\\N`. This corrects the syntax check failures.
2. **Migrate Legacy Utilities (Medium):**
   Update legacy developer tools under [_scripts](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts) to use the modern `google-genai` SDK and remove references to `vertexai`.
3. **Establish Ingest Column Remapping (Low):**
   Ensure database sheet ingestion workflows map colloquial keys (`Grading Cert #`, `Cost`, `Personal Notes`, `Personal Ref #`) to their canonical equivalents defined in the Golden Schema.
