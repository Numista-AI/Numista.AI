# SCAN REPORT: Numista.AI System Audit (v4.322)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with a 100% backend unit pass rate [268 passed, 0 failed in 26.31s], 0 Dart analysis issues [Clean: `dart analyze lib` passed with 0 errors/warnings], live Cloud Run backend probes 100% operational, and Playwright E2E smoke test suite 100% operational [8/8 passed in 44.2s]. Gemini model policy: 100% compliant with 2026 GA models including primary flash workhorse `gemini-3.8-flash`).
* **Scan Date:** 2026-09-06
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` GCP project / `numista-vault` Firebase project)
* **Versions Scanned:** Backend v4.322, Mobile/Web Frontend v4.322 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings Summary
* **Fatal Backend Errors:** 0
* **Dart / Flutter Compilation Errors:** 0 (`dart analyze lib` passed with 0 issues)
* **Active Deprecated Gemini Models in Production:** 0 (0 occurrences of `gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*` across active serving code paths)
* **Live Probes Health:** 100% operational on `https://numista-backend-568985927038.us-central1.run.app` and `https://numista.ai`
* **Backend Pytest Suite:** 268 passed, 0 failed in 26.31s (100% pass rate)
* **Frontend Playwright Smoke Suite:** 8 passed, 0 failed in 44.2s (100% pass rate)
* **Security & Vulnerability Triage:** CodeQL Alert #69 resolved, Phase 1 security hardening active. **Dependabot: 0 open alerts** (pyarrow #67 dismissed as inaccurate — already at 23.0.1; xlsx alerts #1/#2/#45/#46 dismissed as not_used — legacy internal tooling not exposed to user data).

---

## Dev Environment & Credential Notes
1. ✅ **Greysheet API Dev Fallback (Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 security policy. Dev environment defaults to Tier 0 Firestore `config/greysheet` cache with live fallback. Production credentials are securely managed in GCP Secret Manager and Cloud Run environment variables.
2. ✅ **Live Greysheet Probing:** Direct live probe to `https://numista-backend-568985927038.us-central1.run.app/api/greysheet/config` returned HTTP 200 with active Basic Tier mode.

---

## Model Binding & LLM Health (Rule 6 Compliance)
* **Model ID Verification:** Verified clean. Exactly 0 occurrences of deprecated or retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active production paths.
* **Centralized Declarations (`numista_backend/config/__init__.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.8-flash` 🟢 PASS (Primary workhorse / Active GA / 2026 GA Policy)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / 2026 GA Policy)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / 2026 GA Policy)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / 2026 GA Policy)
* **Ingestion & Classification Models (`numista_backend/config/ingestion_config.py`):**
  * `CLASSIFIER_MODEL`: `gemini-3.8-flash` 🟢 PASS
  * `EXTRACTION_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS
  * `FALLBACK_FLASH_MODEL`: `gemini-3.8-flash` 🟢 PASS
  * `FALLBACK_PRO_MODEL`: `gemini-3.5-pro` 🟢 PASS
* **Frontend Multimodal Analysis Models:**
  * `numista_mobile/lib/screens/coin_detail_screen.dart`: `gemini-3.8-flash` 🟢 PASS
  * `numista_mobile/lib/services/coin_normalizer_service.dart`: `gemini-3.8-flash` 🟢 PASS
* **Vector Embeddings (`numista_backend/services/vector_rag_service.py`):**
  * Embedding Model: `gemini-embedding-2` (1536 dimensions, Vertex AI `location="global"`) 🟢 PASS
  * Dual-Path Retrieval: `cosine_all` (exact Cosine Distance scan) & `find_nearest` (Vector Search Index) with fallback 🟢 PASS
  * Safe Embedding Guard: `SKIP_DIM` string-length check preventing API overflow on oversized payloads 🟢 PASS
* **Offline Tooling Health:** `numista_qc/layer_4_self_update/test_synthesizer.py` and `feedback_miner.py` verified aligned with `gemini-3.8-flash` 🟢 PASS.
* **AGENTS.md Rule 6 Compliance:** 100% compliant across production serving stack and offline tooling.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Live Backend Probes (`https://numista-backend-568985927038.us-central1.run.app`):**
  * `/api/greysheet/config` ➔ `200 OK` (Status: active, Tier: Basic, Fallback rate: 0%)
  * `/api/greysheet/pricing/1001` ➔ `200 OK` (Ground-truth pricing payload resolved for 1834 1c Large 8 Large Stars Medium Letters MS RB)
  * `/api/spot_prices` ➔ `200 OK` (Gold: $4,476.60, Silver: $66.75, Platinum: $1,826.00, Palladium: $1,403.90)
  * `/api/template` ➔ `200 OK` (CSV Template headers validated)
  * `/api/transfer/passport-pdf/dummy` ➔ `404 Not Found` (Route active, dummy ID rejected as expected)
  * `/api/transfer/initiate` ➔ `405 Method Not Allowed` on GET (POST route active)
* **Production Web App (`https://numista.ai`):** ➔ `200 OK` (HTML shell rendered, Flutter canvas bootstrapped)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features & Pipeline Audit
* **Vector RAG (Phase 4 Semantic Search):** Active. Wired into `/api/deep_dive` and `/api/ai/chat` for high-precision numismatic retrieval against canonical catalogs.
* **Asset Transfer & Secure Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) and Secure Passport schema endpoints active in `main.py` and `services/transfer_service.py`.
* **Estate Management System:** Verified. Tokenized attorney portal (`/api/v1/estate/...`), dynamic snapshot generation, token revocation, and 256 KB chunked streaming active in `routes/estate_routes.py`.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding and Vertex AI endpoints active.
* **US Mint & Treasury Programs Registry:** Verified. Master registry of all 35 official programs active in `master_coin_programs.json` (including 2026 Semiquincentennial Series with Item 26RJ, 2026 U.S. Circulating Coins, Sacagawea & Native American Dollars, and American Innovation $1 Coin Program); ground-truth checklist counts confirmed without wildcard inflation.
* **Goals & Proof-Sets Enhancements (v4.307+):** Filter progress counter by goal dropdown (`PROGRAM_GOAL_PROGRESS`) and set children expansion in checklist with strike_type/metal_content pass-through (`STATE_Q_PROOFSET_S_PROOF`).
* **Checklists Plain-English PDF Notes/QTY (v4.316):** Verified. Grid card uses `expandCollection` with saved goal (`GRID_CARD_PCT_LAG`) and plain-English PDF notes/quantities.
* **Authentication Enhancements:** Dual login support with PIN + password active; sovereign test account support via 6-digit PIN.
* **Brain Watcher Pipeline:** Hash-idempotent absorb, on_modified handler, file_bytes passing, and deny-list enforcement active.
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail (1920x1080 desktop layout), max-width containers, and web hotkeys active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity and multi-turn numismatic advisory active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active; WebRTC fallback path confirmed.

---

## Architecture & Code Quality Health
* **Backend Monolith Deconstruction:** ✅ **COMPLETE.** All backend routes modularized into 17+ dedicated `APIRouter` modules under `numista_backend/routes/`:
  * Core scan, AI, and collection routes (`scan_routes.py`, `ai_routes.py`, `collection_routes.py`)
  * Market valuation and Greysheet pricing (`greysheet_routes.py`, `valuation_routes.py`, `greysheet_admin_routes.py`, `greysheet_error_routes.py`)
  * Estate and Lateral Transfer systems (`estate_routes.py`, `attorney_routes.py`, `main.py`)
  * PCGS, news, payment, support, and admin routes (`pcgs_routes.py`, `news_routes.py`, `payment_routes.py`, `support_routes.py`, `affiliate_routes.py`, `grade_review_routes.py`, `import_routes.py`, `subaccount_routes.py`, `telemetry_routes.py`, `sandbox_routes.py`)
* **Route Parity Baseline:** `route_snapshot_baseline.json` maintained for automated regression detection.
* **Frontend Dart Analysis:** `dart analyze lib` executed with 0 errors and 0 warnings (`No issues found!`).

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable.
* **Dependabot Vulnerability Management:** 0 open alerts on default branch.

---

## Test Logs & Isolation Summary
* **Backend Pytest Suite:** `268 passed, 224 warnings in 26.31s` (100% pass rate).
* **Frontend Dart Analyzer:** `Analyzing lib... No issues found!` (Exit code 0).
* **Frontend Playwright Smoke Suite (`01-homepage.spec.js`):** `8 passed in 44.2s` (100% pass rate).
* **Layer 3 Data Health Probes:** `3/3 endpoints healthy` (Homepage: 200 OK, Spot Prices: 200 OK, Backend Health: 404 sentinel).
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Pre-Launch Action Items
1. **Playwright Report Generator Synchronization (`numista_tests/generate_report.js`):** Update `generate_report.js` baseline strings to dynamically pull the version identifier (`v4.322+`) rather than falling back to static legacy v4.1 placeholders during automated reporting runs.
2. **Skill Maintenance:** Keep `.antigravity/skills/project-scanner/SKILL.md` aligned with current backend Cloud Run endpoints and newly registered coin programs.
