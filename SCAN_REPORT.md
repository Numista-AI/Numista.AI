# Numista.Ai System Scan Report - 2026-07-08

## Executive Summary: **FAIL**
The system check has identified critical environment configuration issues and data schema mismatches that prevent the core test suite from running and may lead to ingestion failures. While the codebase has successfully migrated to the latest Gemini 3.5 Flash SDK, the local development environment is unstable for testing.

---

## Critical Errors & Warnings

### 1. Missing Dependencies in Global Environment
- **Issue**: `ModuleNotFoundError: No module named 'feedparser'`
- **Impact**: Prevents `pytest` collection and execution in the default environment.
- **Context**: `feedparser` is required by `numista_backend/main.py` for RSS/feed processing. It is listed in `requirements.txt` but not installed in the global Python 3.14 environment.

### 2. Pytest Execution Failure (Venv)
- **Issue**: `ValueError: I/O operation on closed file`
- **Impact**: `pytest` fails to execute even when using the `.venv` where `feedparser` is present.
- **Context**: This may be an incompatibility with the experimental Python 3.14.2 interpreter or a race condition in the `pytest-9.1.1` capture mechanism.

### 3. Syntax Warnings in Dependencies
- **Issue**: `SyntaxWarning: 'continue' in a 'finally' block` in `botasaurus_driver`.
- **Impact**: High-level warning that may lead to unpredictable behavior in scraping tasks on newer Python versions.

---

## Data Pipeline Audit

### Schema Validation Results
| Dataset | Status | Findings |
| :--- | :--- | :--- |
| `banknotes_expanded.json` | **PASS** | Matches `coin-schema.json` (PascalCase). |
| `awq_coins_live.json` | **FAIL** | Uses camelCase/lowercase keys (`year`, `mint`, `denomination`) instead of required PascalCase (`Year`, `Mint Mark`, `Denomination`). |
| `coin-schema.json` | **VALID** | Canonical schema is up to date (2026-07-01). |

---

## Test Logs Summary
- **Tests Collected**: 0 (Collection Error)
- **Tests Passed**: 0
- **Tests Failed**: 0
- **Errors**: 1 (Collection)
- **Warnings**: 1 (Deprecation: VertexAI SDK)

> [!NOTE]
> `app_error.log` shows repeated deprecation warnings for the Vertex AI SDK. Although `main.py` uses `google-genai`, some legacy calls or client configurations (`vertexai=True`) are still triggering these.

---

## Recommended Fixes

1. **Environment Sync**: Install all requirements in the global environment or fix the `.venv` pathing issues to ensure `pytest` can collect tests without `ModuleNotFoundError`.
2. **Schema Normalization**: Run a migration script on `awq_coins_live.json` to normalize keys to PascalCase as defined in `coin-schema.json`.
3. **Python Version**: Consider downgrading the local development environment to a stable Python 3.12 or 3.13 if Python 3.14 continues to cause `pytest` I/O errors.
4. **SDK Cleanup**: Remove the `vertexai=True` flag from `genai.Client` if the project is fully migrated to the `google-genai` native SDK to suppress deprecation warnings.
