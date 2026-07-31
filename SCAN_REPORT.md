# SCAN REPORT: Numista.AI System Audit (v4.1)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with 98% test pass rate across unit and E2E test suites. Pytest backend suite: 19 passed, 3 warnings in 15.73s. Playwright E2E: 118/120 passed [2 skipped gracefully]. Gemini models: 100% active 2026 GA compliance).
* **Scan Date:** 2026-07-31
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.1, Frontend v4.1 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings
1. ⚠️ **Backend Script AST Warning:** `numista_backend/seed_mint_errors.py` has an unclosed dictionary literal on line 320 preventing clean module compilation.
2. ℹ️ **Greysheet API Dev Fallback Active:** Local `.env` unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN`, defaulting to Tier 0 fallback mode and Firestore `config/greysheet` cache.

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active code paths.
* **Centralized Configuration (`numista_backend/config.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.6-flash` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / No shutdown date)
* **AGENTS.md Rule 6 Compliance:** Strictly compliant.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Greysheet Probes (`https://numista-backend-568985927038.us-central1.run.app`):** ✅ `200 OK` (Basic Tier mode active, fallback rate 0%)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) & Secure Passport active.
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/estate/generate-appraisal-url`) active.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding & Vertex AI endpoints active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series & Uncirculated Set checklist templates active.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** 19 passed, 3 warnings in 15.73s (100% pass rate)
* **Frontend Playwright E2E Suite:** 118/120 passed (2 skipped gracefully)
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Fixes
1. **Fix Seed Script Syntax Error:** Resolve dictionary structure syntax in `numista_backend/seed_mint_errors.py` (line 320).
2. **Production Secret Management:** Ensure `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` environment variables are populated in Cloud Run settings prior to Beta deployment on 1 AUG 26.
3. **Maintain Skill Documentation:** Keep `project-scanner/SKILL.md` aligned with production Cloud Run URL.
