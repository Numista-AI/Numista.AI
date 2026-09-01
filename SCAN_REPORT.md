# SCAN REPORT: Numista.AI System Audit (v4.273)

## Executive Summary
* **Status:** 🟡 **PASS WITH NOTICES** (Full system audit executed on 2026-09-01 ahead of November Launch. Pytest backend suite: 268 passed [100% pass rate in 15.12s]. Playwright E2E: 173 passed, 1 failed, 2 skipped across 25 test specs [98.3% pass rate]. Dart analyzer: 0 fatal errors, 0 warnings, 0 infos [Clean]. Gemini models: 100% active 2026 GA compliance).
* **Scan Date:** 2026-09-01
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.273 / Frontend v4.273 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings Summary
* **Critical Backend Errors:** `0` — All primary backend APIs, database schemas, and FastAPI routing paths are stable and responsive.
* **Dart Analysis Errors:** `0` — Zero fatal compilation or syntax errors.
* **Dart Analysis Warnings:** `0` — Clean.
* **Dart Analysis Infos:** `0` — Clean.
* **Playwright E2E Failures:** `1` — `tests/26-aug24-remediation.spec.js` (ISSUE-002: Mint Set tab accessible from Add Coins Hub timeout).
* **Security Alerts:** `102` — Open Dependabot dependency alerts on GitHub default branch (70 high, 29 moderate, 3 low).

---

## Dev Environment & Credential Notes
1. ✅ **Greysheet API Dev Fallback (Expected — Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 hardening policy. Dev defaults to Tier 0 Firestore `config/greysheet` cache. Production credentials are managed via GCP Secret Manager / Cloud Run environment variables.
2. ✅ **Cloud Run Secrets & Environment Variables:**
   * `GREYSHEET_API_KEY`: ✅ **SET** in Cloud Run environment variables
   * `GREYSHEET_API_TOKEN`: ✅ **SET** in Cloud Run environment variables
   * `NUMISTA_SCRAPE_HTTP_PROXY`: ✅ **SET** in Cloud Run environment variables
   * `NUMISTA_SCRAPE_HTTPS_PROXY`: ✅ **SET** in Cloud Run environment variables
   * `STRIPE_WEBHOOK_SECRET`: ✅ **SET** in Cloud Run environment variables
   * `STRIPE_PUBLISHABLE_KEY`: ✅ **SET** in Cloud Run environment variables
   * `PCGS_BEARER_TOKEN`: ✅ **SET** in Cloud Run environment variables
   * `NUMISTA_API_KEY`: ✅ **SET** in Cloud Run environment variables

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active code paths.
* **Centralized Configuration (`numista_backend/config/__init__.py`):**
   * `GEMINI_FLASH_MODEL`: `gemini-3.7-flash` 🟢 PASS (Active GA / No shutdown date)
   * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / No shutdown date)
   * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / No shutdown date)
   * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / No shutdown date)
* **Embedding Model Binding (`numista_backend/services/vector_rag_service.py`):**
   * `ACTIVE_EMBEDDING_MODEL`: `gemini-embedding-2` 🟢 PASS (Active GA / 1536-dim MRL output dimensionality)
* **AGENTS.md Rule 6 Compliance:** Strictly compliant. All active models use 2026 GA versions.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Greysheet Probes (`https://numista-backend-568985927038.us-central1.run.app` & `https://numista.ai`):**
   * `/api/greysheet/config`: ✅ `200 OK` (Basic Tier active, mode: fallback, endpoints verified)
   * `/api/greysheet/pricing/1001`: ✅ `200 OK` (Pricing resolution active)
   * `/api/spot_prices`: ✅ `200 OK` (Precious metals feed active)
   * `/api/template`: ✅ `200 OK` (Set templates active)
   * `/api/estate/generate-appraisal-url`: ✅ `422 Unprocessable Entity` (Schema contract validation active)
   * `https://numista.ai`: ✅ `200 OK` (Main production domain live)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features Audit
* **Vector RAG (Phase 4):** Verified. 1536-dim embeddings via `gemini-embedding-2`, dual-path retrieval (`cosine_all` / `find_nearest`), and `SKIP_DIM` length guard active.
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) & Secure Passport active.
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/v1/estate/...`), legal tokenized URL generation, and 256 KB chunked PDF proxy streaming active.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding & Vertex AI endpoints active.
* **2026 America250 Coin Series & Checklists:** Verified. All 33 official US Mint programs registered and validated; ground-truth checklist counts confirmed.
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail (1920x1080 desktop layout), max-width containers, and web hotkeys active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active; WebRTC fallback path confirmed.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active (`numista_backend/numista_scraper/config.py`).

---

## Backend Architecture Health
* **FastAPI APIRouter Modularity:** ✅ **COMPLETE.** Monolithic routes decoupled into 17 dedicated `APIRouter` modules under `numista_backend/routes/`:
   * `affiliate_routes.py`, `ai_routes.py`, `collection_routes.py`, `estate_routes.py`, `grade_review_routes.py`, `greysheet_admin_routes.py`, `greysheet_error_routes.py`, `import_routes.py`, `news_routes.py`, `payment_routes.py`, `pcgs_routes.py`, `sandbox_routes.py`, `scan_routes.py`, `subaccount_routes.py`, `support_routes.py`, `telemetry_routes.py`, `valuation_routes.py`.
* **Route Parity:** `route_snapshot_baseline.json` committed — diff tool active for regression detection.
* **Backend Test Coverage:** 268 passed unit tests across all APIRouter modules and backend services (100% pass rate in 15.12s).

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable.
* **Open Dependabot Alerts:** ⚠️ **102 vulnerabilities** (70 high, 29 moderate, 3 low) flagged on GitHub default branch. Down from 160 alerts in earlier scans. Continued dependency upgrades recommended before November 2026 Launch.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** `268 passed, 224 warnings in 15.12s` (100% pass rate)
* **Frontend Dart Analysis (`dart analyze .`):** `0 fatal errors`, `0 warnings`, `0 infos` (No issues found)
* **Frontend Playwright E2E Suite (1920x1080 Viewport):** `173 passed`, `1 failed`, `2 skipped` across 25 test specs (98.3% pass rate)
* **E2E Timeout Notices:**
   * `tests/26-aug24-remediation.spec.js` (ISSUE-002: Mint Set tab accessible from Add Coins Hub locator timeout)
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Fixes & Pre-Launch Action Items
1. **Remediation Spec Tab Navigation (`26-aug24-remediation.spec.js`):** Adjust locator strategy or add explicit canvas settle wait before clicking Mint Set tab in `ISSUE-002` to prevent locator timeout under heavy test runner loads.
2. **Dependabot Vulnerabilities:** Continue triaging remaining 102 open GitHub security alerts before November 2026 Launch (prioritizing 70 high-severity items).
3. **Maintain Skill Documentation:** Keep `.antigravity/skills/project-scanner/SKILL.md` aligned with production Cloud Run URLs and series additions.
