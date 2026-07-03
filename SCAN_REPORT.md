# Numista.Ai Project Scan Report
**Date:** 2026-07-03  
**Status:** PASS (with Warnings)

## Executive Summary
The Numista.Ai project has passed the core system check. The backend infrastructure is operational, main service endpoints are functional, and critical API integrations (Gemini, PCGS, Smithsonian) are correctly configured. No syntax errors or broken imports were detected in the primary code path. However, a significant discrepancy between the "Golden Schema" and local data files was identified.

## Critical Errors & Warnings

### ⚠️ Data Pipeline Discrepancy (Golden Schema)
- **Issue:** The `coin-schema.json` (Golden Schema) specifies `Quantity` and `Condition` as **required** fields.
- **Findings:** Sample data files, including `morgan_dollar_expanded.json` and `banknotes_expanded.json`, are **missing** these required fields.
- **Impact:** Ingestion pipelines or validation layers enforcing this schema will fail when processing these files.

### ℹ️ Optional Service Dependencies
- **Note:** `morgan_knowledge.py` and `vertex_search` are successfully integrated. The system correctly handles their absence if they were missing, but they are currently present and functional.

### ℹ️ Model Deprecation Sync
- **Status:** Backend is correctly synced with the Gemini 3.5/3.1 model roadmap. No legacy models (e.g., Gemini 3.0) were found in the active configuration.

## Test Logs Summary

### Python Backend Tests (pytest)
- **Executed:** 4 tests
- **Passed:** 4
- **Failed:** 0
- **Summary:** Basic valuation logic and parsing are stable.

### Frontend/UI Tests (Playwright)
- **Status:** **100% PASSED** (70/70 tests)
- **Completed Specs:**
  - `01-homepage.spec.js`: PASSED (7/7)
  - `02-auth-ui.spec.js`: PASSED (7/7)
  - `03-demo-navigation.spec.js`: PASSED (24/24)
  - `04-registration.spec.js`: PASSED (8/8)
  - `05-navigation.spec.js`: PASSED (12/12)
  - `06-edge-cases.spec.js`: PASSED (10/10)
  - `07-error-library.spec.js`: PASSED (2/2)
- **Summary:** Full frontend suite completed without regression. All core flows (Auth, Nav, Demo Mode) are stable.

## Recommended Fixes

1. **Schema Alignment:** Update all local `.json` and `.csv` coin datasets to include `Quantity` and `Condition` fields to ensure compliance with `coin-schema.json`.
2. **Expand Test Coverage:** The Python test suite is currently limited to valuation logic. Recommend adding integration tests for the FastAPI endpoints and GCS/Firestore interaction layers.
3. **Environment Documentation:** Ensure `.env.example` stays updated with the latest required keys as seen in the current `.env`.
