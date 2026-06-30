# Numista.Ai System Scan Report

## Executive Summary
- **Overall Scan Status:** ✅ **PASS**
- **Code Compilation & Syntax Check:** ✅ **PASS** (No hard compilation syntax errors found; Python and JavaScript boundaries verified)
- **Backend API Test Suite (Pytest):** ✅ **PASS** (4/4 tests passed)
- **Frontend Test Suite (Playwright):** ✅ **PASS** (70/70 tests passed)

---

## Critical Errors & Warnings

> [!NOTE]
> All primary business APIs, RAG boundaries, and libraries run correctly. The legacy `vertexai` library has been successfully migrated to the new `google-genai` SDK.

### 1. Python Syntax Warnings
The AST parsing tool identified minor syntax warnings in helper/utility scripts:
* **File:** [ingest_coin_set.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/ingest_coin_set.py#L20)
  * **Line 20:** `SyntaxWarning: "\$" is an invalid escape sequence. Did you mean "\\$"?`
* **File:** [sync_local_images_to_gcs.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/sync_local_images_to_gcs.py#L16)
  * **Line 16:** `SyntaxWarning: "\ " is an invalid escape sequence. Did you mean "\\ "?`

### 2. Byte Order Mark (BOM) Presence
* **File:** [import_knowledge_base.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/import_knowledge_base.py)
  * Contains a leading UTF-8 Byte Order Mark (`\ufeff`) that can cause parser/AST compilation issues under certain Python environment encodings.

### 3. Library Deprecation Warning (Third-Party)
* **File:** `.venv\Lib\site-packages\google\genai\types.py` (Line 43)
  * `DeprecationWarning: '_UnionGenericAlias' is deprecated and slated for removal in Python 3.17`
  * *Note: This is an internal warning from the google-genai library on Python 3.14. No immediate action is required as it will be resolved by future SDK library updates.*

---

## Data Pipeline Audit
The JSON data schema audits verified that the local references match structural expectations:

| Dataset | Format | Compliance | Sample Keys |
| :--- | :--- | :--- | :--- |
| [coin-schema.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/coin-schema.json) | JSON Schema | ✅ Valid | `properties`, `required`, `type`, `title` |
| [awq_coins_live.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/awq_coins_live.json) | Array of 36 objects | ✅ Compliant | `doc_id`, `year`, `mint`, `program`, `theme` |
| [banknotes_expanded.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/banknotes_expanded.json) | Array of 550 objects | ✅ Compliant | `year`, `denomination`, `mint_mark`, `variety`, `note` |
| [master_coin_programs.json](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/master_coin_programs.json) | Array of 33 objects | ✅ Compliant | `name`, `years`, `mint_mark_locations`, `category` |

---

## Test Logs Summary

### 1. Pytest Unit Tests
We executed the backend python tests under the target local virtual environment:
```powershell
$env:PYTHONPATH="."
.\.venv\Scripts\pytest tests
```
* **Status:** ✅ **100% Pass** (4 passed, 1 warning in 6.33s)
* **Results:**
```text
============================= test session starts =============================
platform win32 -- Python 3.14.2, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\ericd\Documents\MyVertexProject\numista_backend
plugins: anyio-4.13.0
collected 4 items

tests\test_valuations.py ....                                            [100%]
======================== 4 passed, 1 warning in 6.33s =========================
```

### 2. Playwright End-to-End Tests
We executed the frontend test suites targeting the system interface:
```powershell
npx playwright test
```
* **Status:** ✅ **100% Pass** (70/70 tests passed in 12.7m)
* **Results:**
```text
Running 70 tests using 1 worker
...
  ok 66 [chromium] › tests\06-edge-cases.spec.js:91:3 › T07: Page does not crash when clicking outside all buttons (7.2s)
  ok 67 [chromium] › tests\06-edge-cases.spec.js:106:3 › T08: Scrolling the homepage does not break render (7.0s)
  ok 68 [chromium] › tests\06-edge-cases.spec.js:120:3 › T09: Sign Out from demo returns to login (13.3s)
  ok 69 [chromium] › tests\06-edge-cases.spec.js:131:3 › T10: Add New Coins page in demo shows appropriate blocked state (14.4s)
  ok 70 [chromium] › tests\07-error-library.spec.js:25:3 › T01: Error Library loads reference data without permission errors (14.4s)

70 passed (12.7m)
```
* **Latest Report:** [2026-06-30_morning_report.md](file:///c:/Users/ericd/Documents/MyVertexProject/numista_tests/reports/2026-06-30_morning_report.md)

---

## Recommended Fixes

1. **Resolve String Escape Warnings:**
   Prepend string literals with `r` (raw strings) or escape the backslashes (`\\`) in:
   * [ingest_coin_set.py:L20](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/ingest_coin_set.py#L20)
   * [sync_local_images_to_gcs.py:L16](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/sync_local_images_to_gcs.py#L16)
2. **Remove BOM:**
   Resave [import_knowledge_base.py](file:///c:/Users/ericd/Documents/MyVertexProject/numista_backend/_scripts/import_knowledge_base.py) using a standard UTF-8 signature without BOM to avoid compile errors on legacy parse targets.
3. **Configure Pytest Configuration Scope:**
   Create a `pytest.ini` in `numista_backend/` to define explicitly:
   ```ini
   [pytest]
   testpaths = tests
   ```
   This prevents Pytest from scanning the entire `.venv` node if run without directory arguments.
