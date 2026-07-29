# SCAN REPORT: Numista.AI System Audit (v4.1)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with 98% test pass rate across unit and E2E test suites. Pytest backend suite: 16 passed, 3 warnings in 5.36s. Playwright E2E: 118/120 passed [2 skipped gracefully]. Gemini models: 100% active 2026 GA compliance).
* **Scan Date:** 2026-07-29
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.1, Frontend v4.1 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings
1. ℹ️ **Greysheet API Dev Fallback Active:** Local `.env` unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN`, defaulting to Tier 0 fallback mode and Firestore `config/greysheet` cache.

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active code paths.
* **Centralized Configuration (`numista_backend/config.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.6-flash` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / No shutdown date)
* **AGENTS.md Rule 6 Compliance:** Strictly compliant.

---

## Greysheet API & Core Features Audit
* **Greysheet Probes (`https://numista-backend-568985927038.us-central1.run.app`):** ✅ `200 OK`
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes & Secure Passport active.
* **Estate Management System:** Verified. Army Property Management estate data structures active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series & checklists active.

---

## Test Summary
* **Backend Pytest Unit Suite:** 16 passed, 3 warnings in 5.36s
* **Frontend Playwright E2E Suite:** 118/120 passed (2 skipped)

---

## Recommended Fixes
1. **Production Secret Management:** Ensure `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` environment variables are populated in Cloud Run settings prior to Beta deployment on 1 AUG 26.
2. **Maintain Skill Documentation:** Keep `project-scanner/SKILL.md` aligned with production Cloud Run URL.
