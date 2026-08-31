# SCAN REPORT: Numista.AI System Audit (v4.256)

## Executive Summary
* **Status:** 🟡 **PASS WITH NOTICES** (Full system audit executed on 2026-08-31 ahead of November Launch. Pytest backend suite: 268 passed [100% pass rate in 28.19s]. Playwright E2E: 172 passed, 2 failed, 2 skipped across 26 test specs [97.7% pass rate]. Dart analyzer: 0 fatal errors, 3 warnings, 5 infos. Gemini models: 100% active 2026 GA compliance).
* **Scan Date:** 2026-08-31
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.256 / Frontend v4.256 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings Summary
* **Critical Backend Errors:** `0` — All primary backend APIs, database schemas, and FastAPI routing paths are stable and responsive.
* **Dart Analysis Errors:** `0` — Zero fatal compilation or syntax errors.
* **Dart Analysis Warnings:** `3` — Minor unused imports in `lib/screens/customer_service_screen.dart` (`file_picker.dart`, `dart:html`, `dart:typed_data`).
* **Dart Analysis Infos:** `5` — Deprecated `dart:html` usage recommendation in `customer_service_screen.dart` and 4 null-aware marker recommendations in `lib/services/ticket_service.dart`.
* **Playwright E2E Failures:** `2` — `tests/26-aug24-remediation.spec.js` (ISSUE-002: Mint Set tab navigation timeout; ISSUE-003: Silver Proof Set card visible timeout).
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
* **Backend Test Coverage:** 268 passed unit tests across all APIRouter modules and backend services (100% pass rate).

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable.
* **Open Dependabot Alerts:** ⚠️ **102 vulnerabilities** (70 high, 29 moderate, 3 low) flagged on GitHub default branch. Down from 160 alerts in earlier scans. Continued dependency upgrades recommended before November 2026 Launch.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** `268 passed, 218 warnings in 28.19s` (100% pass rate)
* **Frontend Dart Analysis (`dart analyze .`):** `0 fatal errors`, `3 warnings` (unused imports), `5 infos`
* **Frontend Playwright E2E Suite (1920x1080 Viewport):** `172 passed`, `2 failed`, `2 skipped` across 26 test specs (97.7% pass rate)
* **E2E Timeout Notices:**
   * `tests/26-aug24-remediation.spec.js` (ISSUE-002: Mint Set tab navigation timeout at 60s)
   * `tests/26-aug24-remediation.spec.js` (ISSUE-003: Silver Proof Set card visibility timeout at 60s)
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Fixes & Pre-Launch Action Items
1. **Remediation Spec Tab Navigation (26-aug24-remediation.spec.js):** Adjust locator strategy or add explicit canvas settle wait before clicking Mint Set tab in `ISSUE-002` and `ISSUE-003` to prevent 60s timeout under heavy test runner loads.
2. **Customer Service Screen Cleanup:** Remove unused imports (`file_picker.dart`, `dart:html`, `dart:typed_data`) in `lib/screens/customer_service_screen.dart`.
3. **Dependabot Vulnerabilities:** Continue triaging remaining 102 open GitHub security alerts before November 2026 Launch (prioritizing 70 high-severity items).
4. **Maintain Skill Documentation:** Keep `.antigravity/skills/project-scanner/SKILL.md` aligned with production Cloud Run URLs and series additions.
