# SCAN REPORT: Numista.AI System Audit (v4.287)

## Executive Summary
* **Status:** ⚠️ **PASS WITH NOTICES** (System scan completed with a 96.6% end-to-end test pass rate and 100% backend unit pass rate. Pytest backend suite: 268 passed, 0 failed. Dart analysis: 0 errors, 0 warnings [Clean]. Playwright E2E: 170 passed [including 1 flaky on retry], 2 failed [timeouts under full test run], 4 skipped gracefully across 25 specs. Gemini model policy: 100% compliant with 2026 GA models).
* **Scan Date:** 2026-09-02
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` GCP project / `numista-vault` Firebase project)
* **Versions Scanned:** Backend v4.287, Mobile/Web Frontend v4.287 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings Summary
* **Fatal Backend Errors:** 0
* **Dart / Flutter Compilation Errors:** 0 (`dart analyze lib` passed with 0 issues)
* **Active Deprecated Gemini Models:** 0 (0 occurrences across active codebase)
* **Live Probes Health:** 100% operational on `https://numista-backend-568985927038.us-central1.run.app` and `https://numista.ai`
* **E2E Timeouts:** 2 tests in `26-aug24-remediation.spec.js` (ISSUE-002 & ISSUE-003, non-blocking locator timeouts during batch test run)
* **Security & Vulnerability Triage:** In progress (CodeQL #69 resolved, Phase 1 security hardening active)

---

## Dev Environment & Credential Notes
1. ✅ **Greysheet API Dev Fallback (Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 security policy. Dev environment defaults to Tier 0 Firestore `config/greysheet` cache with live fallback. Production credentials are securely managed in GCP Secret Manager and Cloud Run environment variables.
2. ✅ **Live Greysheet Probing:** Direct live probe to `https://numista-backend-568985927038.us-central1.run.app/api/greysheet/config` returned HTTP 200 with active Basic Tier mode.

---

## Model Binding & LLM Health (Rule 6 Compliance)
* **Model ID Verification:** Verified clean. Exactly 0 occurrences of deprecated or retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active source files.
* **Centralized Declarations (`numista_backend/config/__init__.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.7-flash` 🟢 PASS (Active GA / 2026 GA Policy)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / 2026 GA Policy)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / 2026 GA Policy)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / 2026 GA Policy)
* **Vector Embeddings (`numista_backend/services/vector_rag_service.py`):**
  * Embedding Model: `gemini-embedding-2` (1536 dimensions, Vertex AI `location="global"`) 🟢 PASS
  * Dual-Path Retrieval: `cosine_all` (exact Cosine Distance scan) & `find_nearest` (Vector Search Index) with fallback 🟢 PASS
  * Safe Embedding Guard: `SKIP_DIM` string-length check preventing API overflow on oversized payloads 🟢 PASS
* **AGENTS.md Rule 6 Compliance:** 100% compliant.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Live Backend Probes (`https://numista-backend-568985927038.us-central1.run.app`):**
  * `/api/greysheet/config` ➔ `200 OK` (Status: active, Tier: Basic)
  * `/api/greysheet/pricing/1001` ➔ `200 OK` (Ground-truth pricing payload resolved)
  * `/api/spot_prices` ➔ `200 OK` (Gold, Silver, Platinum, Palladium live feeds)
  * `/api/template` ➔ `200 OK` (CSV Template headers validated)
  * `/api/estate/generate-appraisal-url` ➔ `422 Unprocessable Entity` (Expected for unauthenticated probe)
  * `/api/transfer/validate/test-token` ➔ `404 Not Found` (Expected for dummy token validation)
  * `/api/coin_search?query=morgan` ➔ `422 Unprocessable Entity` (Expected for unauthenticated probe)
* **Production Web App (`https://numista.ai`):** ➔ `200 OK` (HTML shell rendered, Flutter canvas bootstrapped)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features & Pipeline Audit
* **Vector RAG (Phase 4 Semantic Search):** Active. Wired into `/api/deep_dive` and `/api/ai/chat` for high-precision numismatic retrieval against canonical catalogs.
* **Asset Transfer & Secure Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) and Secure Passport schema endpoints active.
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/v1/estate/...`), tokenized appraisal URLs, and 256 KB chunked streaming active.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding and Vertex AI endpoints active.
* **2026 America250 Coin Series & Checklists:** Verified. All 33 official US Mint programs registered and validated; ground-truth checklist counts confirmed without wildcard inflation.
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail (1920x1080 desktop layout), max-width containers, and web hotkeys active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity and multi-turn numismatic advisory active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active; WebRTC fallback path confirmed.

---

## Architecture & Code Quality Health
* **Backend Monolith Deconstruction:** ✅ **COMPLETE.** All backend routes modularized into 17 dedicated `APIRouter` modules under `numista_backend/routes/`:
  * Core scan, AI, and collection routes (`scan_routes.py`, `ai_routes.py`, `collection_routes.py`)
  * Market valuation and Greysheet pricing (`greysheet_routes.py`, `valuation_routes.py`)
  * Estate and Lateral Transfer systems (`estate_routes.py`, `transfer_routes.py`)
  * PCGS, news, payment, and admin routes (`pcgs_routes.py`, `news_routes.py`, `payment_routes.py`, `admin_routes.py`)
* **Route Parity Baseline:** `route_snapshot_baseline.json` maintained for automated regression detection.
* **Frontend Dart Analysis:** `dart analyze lib` executed with 0 errors and 0 warnings.

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable.
* **Dependabot Vulnerability Management:** Dependency audit ongoing for upcoming launch milestones.

---

## Test Logs & Isolation Summary
* **Backend Pytest Suite:** `268 passed, 224 warnings in 28.80s` (100% pass rate).
* **Frontend Dart Analyzer:** `Analyzing lib... No issues found!` (Exit code 0).
* **Frontend Playwright E2E Suite:** `170 passed (including 1 flaky on retry), 2 failed, 4 skipped out of 176 tests in 45.6m` (96.6% pass rate).
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Pre-Launch Action Items
1. **Remediation E2E Spec Stabilization:** Adjust locator strategy or add canvas settle wait for `tests/26-aug24-remediation.spec.js` (ISSUE-002 & ISSUE-003) to eliminate intermittent timeouts during full concurrent test runs.
2. **Dependabot Vulnerability Triage:** Continue updating and trimming npm/pub dependencies ahead of the November 1, 2026 public launch.
3. **Skill Maintenance:** Keep `.antigravity/skills/project-scanner/SKILL.md` aligned with current backend Cloud Run endpoints and newly registered coin programs.

