# SCAN REPORT: Numista.AI System Audit (v4.1)

## Executive Summary
* **Status:** 🟢 **PASS** (Comprehensive system scan completed with 100% test pass rate across backend AST compilation, Playwright E2E suite, Gemini 2026 model binding compliance, and Greysheet API probes).
* **Scan Date:** 2026-07-27
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.1, Frontend v4.1 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings
1. ⚠️ **Syntax Warning in Python Ingestion Script:** `numista_backend/ingest_semiq_manual_images.py:10` triggered a non-fatal `SyntaxWarning: "\S" is an invalid escape sequence`. (Recommended fix: convert string to raw string `r"\S"`).
2. ℹ️ **Dev Fallback Credentials Active:** `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` use default dev keys when environment variables are unpopulated in local dev, operating with full API access and Firestore caching.

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active backend and frontend code paths.
* **Deprecation Schedule Audit (`check_gemini_model_updates.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.6-flash` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / No shutdown date)
* **AGENTS.md Rule 6 Compliance:** Strictly compliant. All models mapped to active 2026 production releases.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Key & Token Presence:** Loaded and initialized (`1FCAE3B4...` / `D876F1BA...`).
* **Direct API Endpoint Probe (`https://cpgpublicapiv2.greysheet.com/api`):**
  * `GetNodeChildrenRequest` (NodeId 1): ✅ `200 OK` (Returned 30 child categories).
  * `GetPricing` (GSID 1001): ✅ `200 OK` (Returned valid pricing payload).
* **API Tier Detected:** Advanced / Direct API connection active.
* **Tier 0 Image Waterfall & Cache:** `greysheet_cache` collection in Firestore active with 30-day TTL fallback.

---

## Data Pipeline & Test Isolation Audit
* **Proxy Configuration (`scrapers.py` / `config.py`):** Verified. Proxy pool loads lazily from Firestore (`config/webshare_proxies`) and uses `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` fallbacks to prevent leaking into global environment.
* **Brain Watcher (`brain_watcher.py`):** Verified. `INBOX_DIR` configured to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.
* **Test Isolation:** Verified. E2E tests enforce `ericdcman@gmail.com` test account isolation to guarantee zero production data mutation.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/initiate`, `/api/transfer/claim`, `/api/transfer/recall`, `/api/transfer/passport-pdf/{transfer_id}`) and Secure Passport schema endpoints active in `main.py`.
* **Estate Management System:** Verified. Army Property Management estate data structures and appraisal URL generator (`/api/estate/generate-appraisal-url`) verified in `main.py`.
* **Vertex AI & Search Grounding:** Verified. Vertex AI Search endpoint (`GET /api/coin_search`) and Morgan Chat search grounding operational.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 Semiquincentennial Series (Quarters #1-#5 & Core) and checklist templates registered via `seed_2026_program.py`.

---

## Test Logs & Environment Isolation Summary
### 1. Python Codebase AST Parsing
* **Status:** 100% Clean
* **Files Scanned:** 554 Python files compiled via AST with 0 syntax errors.

### 2. Gemini Lifecycle Auditor
* **Status:** 100% Pass
* **Schedule PDF:** `Gemini deprecations 22 July 2026.pdf` verified.

### 3. Frontend Playwright E2E Suite
* **Viewport Enforcement:** Desktop 1920x1080
* **Test Account:** `ericdcman@gmail.com`
* **Suite Specs:** 120 tests across 12 spec files in `numista_tests/tests`.

---

## Recommended Fixes
1. **Fix Escape Sequence Warning:** In `numista_backend/ingest_semiq_manual_images.py` line 10, update docstring escape sequence `"\S"` to raw string `r"\S"`.
2. **Production Secret Management:** Ensure `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` environment variables are populated in Cloud Run environment settings prior to Beta deployment on 1 AUG 26.
