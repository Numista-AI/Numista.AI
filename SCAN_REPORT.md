# Numista.Ai System Scan Report

## Executive Summary
- **Overall Scan Status:** ❌ **FAIL**
- **Frontend Test Suite (Playwright):** ✅ **PASS** (63/63 tests passed, taking 10.3 minutes)
- **Backend API Test Suite (Python):** ❌ **FAIL** (30/34 checks passed, 3 critical failures, 5 normalization mismatches)

Despite the web interface passing all end-to-end automated navigation, authorization, and UI resilience checks, the backend API is experiencing critical runtime crashes on key grade-review endpoints, and utility scripts contain syntax and library deprecation issues.

---

## Critical Errors & Warnings

### 1. Backend API 500 Internal Server Errors (Grade Review)
* **Affected Endpoints:** 
  * `GET /api/grade_review/stats`
  * `GET /api/grade_review/queue`
* **Symptom:** Both endpoints return HTTP 500 on the live server.
* **Root Cause:** In [main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L1344) and [main.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/main.py#L1675), the code attempts to parse the document's confidence score using:
  ```python
  conf = float(d.get('confidence_score', 1.0))
  ```
  In Firestore, many coin documents contain `'confidence_score': null` (None). Since the field is present, `d.get()` returns `None` instead of the default value `1.0`. Calling `float(None)` raises a `TypeError` and crashes the request.

### 2. Vertex AI Model 404 Error
* **Affected File:** [mappingController.js](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/mappingController.js#L26)
* **Symptom:** Gemini mappings fail with a 404 client error:
  `ClientError: [VertexAI.ClientError]: got status: 404 Not Found. {"error":{"code":404,"message":"Publisher Model .../models/gemini-3-flash-preview was not found..."}}`
* **Root Cause:** The script initializes the model with an invalid/non-existent model ID:
  ```javascript
  const modelId = 'gemini-3-flash-preview';
  ```

### 3. Syntax Error in Firestore Debug Utility
* **Affected File:** [_scripts/debug_firestore.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/debug_firestore.py#L44-L45)
* **Symptom:** Script compilation fails.
* **Root Cause:** Line 44 has an unterminated string literal because the print statement is split across lines:
  ```python
  print("
  ✅ Firestore Client: Initialized successfully.")
  ```

### 4. Vertex AI Python SDK Deprecation Warning
* **Affected Files:** All legacy scripts in `numista_backend/_scripts/` (e.g., `auto_annotate_checklist_dataset.py`, `build_image_index.py`, `coin_image_pipeline.py`)
* **Symptom:** Critical warning logs.
* **Warning Message:**
  `UserWarning: This feature is deprecated as of June 24, 2025 and will be removed on June 24, 2026. For details, see https://cloud.google.com/vertex-ai/generative-ai/docs/deprecations/genai-vertexai-sdk.`
* **Context:** Tomorrow (June 24, 2026), the legacy `vertexai` library will be fully removed/shut down by Google Cloud. All scripts using this SDK will fail to execute.

---

## Data Pipeline Audit

We evaluated local datasets against the Numista.AI golden schema defined in [coin-schema.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json):

### 1. Main Collection Backup (`AJ's Coins Backup 8 APR 26.csv`)
* **Matching Fields:** 15 of 32 columns match the Golden Schema.
* **Required Fields:** All required fields (`Year`, `Denomination`, `Quantity`, `Condition`) are present.
* **Non-Standard Columns:** Contains 17 columns not present in the Golden Schema (e.g. `Surface & Strike Quality`, `AI Estimated Value`, `Numismatic Report`, `imageUrlObverse`, `imageUrlReverse`).
* **Discrepancies:** Key columns use non-standard names:
  * `Grading Cert #` instead of `Certification Number`
  * `Cost` instead of `Purchase Cost`
  * `Personal Notes` instead of `Personal Notes I`
  * `Personal Ref #` instead of `Personal Reference #`

### 2. Internal Pipeline CSVs (`AJ_Currency_Parsed.csv`, `AJ_Currency_Parsed_v2.csv`, `AJ_Manual_Image_Sourcing_Currency.csv`)
* **Status:** ❌ **Incompatible**
* **Findings:** None of these files contain the required fields for coin datasets because they represent currency/banknote parsing steps rather than coin collection records.

---

## Test Logs Summary

### 1. Playwright E2E Test Suite (`npm test`)
* **Status:** ✅ **100% Pass** (63/63 tests passed)
* **Log File:** `numista_tests/reports/test-results.json`
* **Summary:** Front-end authentication flows, sidebar navigation, demo mock endpoints, and UI edge cases are fully resilient.

### 2. Python API Test Suite (`run_overnight_tests.py`)
* **Status:** ❌ **Fail** (30/34 checks passed)
* **Log File:** `overnight_test_results.txt`
* **Normalization Failures:** 5 condition mapping checks failed due to mismatches between test expectations and `CONDITION_MAP` keys:
  * `BU`/`bu` mapped to `Uncirculated` (Expected: `MS-63`)
  * `proof69`/`PR69` mapped to `Proof-69` (Expected: `PF-69`)
  * `Ch Proof 63` mapped to `Proof-63` (Expected: `PF-63`)

---

## Recommended Fixes

1. **Fix Grade Review Float conversion (Critical):**
   Modify lines 1344 and 1675 in `numista_backend/main.py` to handle `None` values safely:
   ```python
   conf = float(d.get('confidence_score') if d.get('confidence_score') is not None else 1.0)
   ```
2. **Update Mapping Controller Model ID (High):**
   In `numista_backend/mappingController.js`, update `modelId` to a valid production model:
   ```javascript
   const modelId = 'gemini-1.5-flash'; // or gemini-2.5-flash / gemini-3.5-flash
   ```
3. **Migrate Legacy Python Scripts (High):**
   Update all scripts under `numista_backend/_scripts/` to use the new `google-genai` client instead of the legacy `vertexai` library before the shutdown on June 24, 2026.
4. **Fix Firestore Debug Syntax Error (Low):**
   Correct the split string print statement in `numista_backend/_scripts/debug_firestore.py` onto a single line.
5. **Standardize CSV Columns Mapping (Medium):**
   Update CSV ingestors and parsers to map legacy columns (like `Cost` and `Grading Cert #`) to their official names (`Purchase Cost` and `Certification Number`) as defined in the Golden Schema.
