# SCAN REPORT: Numista.AI System Audit (v4.399)

## Executive Summary
* **Status:** 🟢 **PASS WITH WARNINGS** (System audit completed with a 100% backend unit pass rate [362 passed, 0 failed in 17.16s], 0 Dart compilation errors and 5 non-fatal info/deprecation warnings [clean analyzer: `dart analyze lib` exit 0], 396/396 Flutter unit tests passed [100% pass rate in 15.0s], live Cloud Run backend probes 100% operational across all routes [7/7 healthy], and Playwright smoke tests 100% operational [8/8 passed in 43.8s; master suite was not run this session]. Test Isolation: E2E tests target `grokbot@numista.ai` [QC bot account] with zero production Firestore mutation. Gemini model policy: 100% compliant with 2026 GA models including primary flash workhorse `gemini-3.8-flash` and `gemini-embedding-2`).
* **Scan Date:** 2026-09-30
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` GCP project / `numista-vault` Firebase project)
* **Versions Scanned:** Backend v4.399, Mobile/Web Frontend v4.399 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Critical Errors & Warnings Summary
* **Fatal Backend Errors:** 0
* **Dart / Flutter Compilation Errors & Warnings:** 0 errors, 5 non-fatal warnings/infos (`dart analyze lib` exit 0; deprecation & string interpolation info in `ai_chat_screen.dart`)
* **Active Deprecated Gemini Models in Production:** 0 (0 occurrences of `gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*` across all production and maintenance code paths; 100% 2026 GA compliance)
* **Live Probes Health:** 100% operational on `https://numista-backend-568985927038.us-central1.run.app` and `https://numista.ai` (7/7 endpoints healthy)
* **Backend Pytest Suite:** 362 passed, 0 failed in 17.16s (100% pass rate; matches `numista_tests/reports/pytest-output.txt`)
* **Frontend Playwright Smoke Suite:** 8 passed, 0 failed in 43.8s (`auth.setup.js`, `01-homepage.spec.js`; master suite was not run this session)
* **Flutter Unit Suite:** 396 passed, 0 failed in 15.0s (100% pass rate; 0 failures)
* **Front Door & Session Reliability (v4.399):** Verified active (Resolved sign-in dead ends across public entrypoints, zero-read Firestore isolation in demo mode, XML sitemap validation, and CORS/Bearer auth on `/generate_estate_report` [REQ-023D / REQ-020]).
* **Paper Trail Receipt Scanning & Streaming (v4.397–v4.398):** Verified active (Resolved blank page on View Scan by dynamic detection and streaming of PDF, JPG, and PNG scans; support for gs://, HTTPS, and relative receipt paths [REQ-019]).
* **Lateral Transfer & Record Sale Bounds (v4.395–v4.398):** Verified active (Sell-direct validation, Mode 3 payload alignment, and public front-door zero-write vault [REQ-018 / REQ-018A / REQ-023C]).
* **Pre-Deploy Security & Data Loss Prevention (v4.392–v4.393):** Verified active (Blob retention when coins link to receipts [MF-1], owner-folder path validation on receipt deletions, catalog 26SQRD removal [MF-2], and cost override orig_i indexing).
* **Security & Auth Token Hardening (v4.390–v4.391):** Verified active (Bearer auth on receipt list/view/stream, identify_coin_photo, appraisal-pdf export, and pre-validation of cost split overrides [REQ_015 / REQ_016]).
* **Sets Management & Owner Photos (v4.375–v4.376):** Verified active (Owner photos on sets and atomic group/ungroup capability via `SetGroupingService`).
* **Hosting Hardening & Route Allowlist (v4.376):** Verified active (Strict route allowlist and standalone custom `404.html` fallback).
* **Upcoming US Mint Releases & Valuation Fallback (v4.361–v4.370):** Verified active (Automated test suites, migration seed hardening, and official US Mint Issue Price fallback with `ai_value_status` field).
* **26RJ Catalog & Ghost Repair Status:** Verified active (26RJ 20-coin count, 8 Firestore `coin_image_index` URLs aligned, ghost children eliminated, anti-hallucination guardrail active in `main.py`).
* **Checklist Stale PDF Hotfix Status:** Verified active (`HOTFIX PDF_STALE` and `PDF_STALE_AFTER_CHECKOFF` enforce server-side cache bypass and atomic FutureBuilder invalidation).
* **Security & Vulnerability Triage:** CodeQL Alert #69 resolved, Phase 1 security hardening active. **Dependabot: 0 open alerts** on default branch.

---

## Dev Environment & Credential Notes
1. ✅ **Greysheet API Dev Fallback (Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 security policy. Dev environment defaults to Tier 0 Firestore `config/greysheet` cache with live fallback. Production credentials are securely managed in GCP Secret Manager and Cloud Run environment variables.
2. ✅ **Live Greysheet Probing:** Direct live probe to `https://numista-backend-568985927038.us-central1.run.app/api/greysheet/config` returned HTTP 200 with active Basic Tier mode.

---

## Model Binding & LLM Health (Rule 6 Compliance)
* **Model ID Verification:** Verified clean. Exactly 0 occurrences of deprecated or retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active production paths and maintenance scripts.
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
* **AGENTS.md Rule 6 Compliance:** 100% compliant across production serving stack, offline tooling, and maintenance scripts.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Live Backend Probes (`https://numista-backend-568985927038.us-central1.run.app`):**
  * `/api/greysheet/config` ➔ `200 OK` (Status: active, Tier: Basic, Fallback rate: 0%)
  * `/api/greysheet/pricing/1001` ➔ `200 OK` (Ground-truth pricing payload resolved from Firestore cache for 1834 1c Large 8 Large Stars Medium Letters MS RB)
  * `/api/spot_prices` ➔ `200 OK` (Gold: $4,213.20, Silver: $61.01, Platinum: $1,730.30, Palladium: $1,223.50)
  * `/api/template` ➔ `200 OK` (CSV Template headers validated)
  * `/api/transfer/passport-pdf/dummy` ➔ `404 Not Found` (Route active, dummy ID rejected as expected)
  * `/api/transfer/initiate` ➔ `422 Unprocessable Entity` on empty POST (FastAPI schema validation active)
* **Production Web App (`https://numista.ai`):** ➔ `200 OK` (HTML shell rendered, Flutter canvas bootstrapped)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features & Pipeline Audit
* **Front Door & Session Reliability (v4.399):**
  * Resolved sign-in dead ends across `/pricing`, `/features`, `/roadmap`, demo mode, and account creation.
  * Demo Mode Isolation: Enforced zero Firestore network reads in guest demo mode (`vault_service.dart`).
  * SEO & Discovery: Restored and validated canonical XML sitemap (`/sitemap.xml`) referencing clean URLs.
  * Estate Reporting: Enforced Bearer auth and CORS options preflight headers on `/generate_estate_report`.
* **Paper Trail Receipt Scanning & Streaming (v4.397–v4.398):**
  * Fixed blank white screen bug on View Scan by dynamic detection and streaming of PDF, JPG, and PNG scans (REQ-019).
  * Backend multi-candidate file resolver handles gs:// URIs, HTTPS URLs, and relative storage paths.
* **Sell & Lateral Transfer System (v4.395–v4.398):**
  * Validated Mode 3 Record Sale payload parameters (`sale_price`, `buyer_email`, `notes`) and bounds checks (REQ-018 / REQ-018A).
  * Direct sale and undo sale endpoints hardened with auth token verification.
* **Pre-Deploy Security & Data Loss Prevention (v4.392–v4.393):**
  * Receipt blob retention: Prevents storage orphan leaks and premature deletion when active coin records still link to `receipt_id` (MF-1).
  * Storage path security: Strict owner-folder verification on GCS blob deletions (`receipts/{user_id}/...`) preventing cross-user path traversal.
  * Catalog cleanup: Removed nonexistent product code `26SQRD` and corrected `26SQRP` mint mark attribute (MF-2).
  * Index consistency: Indexed cost split overrides by `orig_i` in `commit_group_photo` to prevent price shift bugs on partial batch errors.
* **Auth & Endpoint Security Hardening (v4.390–v4.391):**
  * Bearer token enforcement on receipt viewing, receipt streaming, and `/api/identify_coin_photo`.
  * Authentication enforcement on `/api/export/appraisal-pdf`.
  * Pre-validation of cost split overrides with atomic commit transactions.
* **Hosting Hardening & Route Allowlist (v4.376):**
  * `numista_mobile/firebase.json`: Strict rewrites allowlist for API routes and valid frontend routes (`/`, `/wishlist`, `/collection`, etc.); eliminated catchall `**` rewrite.
  * `numista_mobile/web/404.html`: Custom branded static 404 page for direct URL misses.
  * `numista_mobile/lib/screens/not_found_screen.dart`: Branded in-app 404 fallback with quick navigation buttons.
* **Sets Management & Grouping Service (v4.375–v4.376):**
  * `numista_mobile/lib/services/set_grouping_service.dart`: Support for grouping loose coins into coin sets and atomic ungrouping with owner photo cleanup.
  * Set owner photo uploads and interactive image viewers integrated in `my_collection_screen.dart`.
* **Upcoming US Mint Releases & Valuation Fallback System (v4.361–v4.370):**
  * `services/usmint_releases_scraper.py`: Dual-source scraper with delta detection, changelog tracking, and official `get_mint_issue_price()` fallback.
  * `screens/upcoming_releases_screen.dart`: Release catalog with hero card, filters, sorting, and status badges.
  * `services/upcoming_releases_service.dart`: API fetch + SharedPreferences caching + fallback data.
  * Valuation Fallback Hardening: Removed .50 hardcoded valuation fallback from `main.py`; replaced with US Mint Issue Price and `ai_value_status` field.
* **Vector RAG (Phase 4 Semantic Search):** Active. Wired into `/api/deep_dive` and `/api/ai/chat` for high-precision numismatic retrieval against canonical catalogs.
* **Asset Transfer & Secure Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) and Secure Passport schema endpoints active in `main.py` and `services/transfer_service.py`.
* **Estate Management System:** Verified. Tokenized attorney portal (`/api/v1/estate/...`), dynamic snapshot generation, token revocation, and 256 KB chunked streaming active in `routes/estate_routes.py` and `routes/attorney_routes.py`.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding and Vertex AI endpoints active.
* **US Mint & Treasury Programs Registry:** Verified. Master registry of all 35 official programs active in `master_coin_programs.json` (including 2026 Semiquincentennial Series with Item 26RJ, 2026 U.S. Circulating Coins, Sacagawea & Native American Dollars, and American Innovation $1 Coin Program); ground-truth checklist counts confirmed without wildcard inflation.
* **26RJ Catalog & Ghost Children Repair (v4.337):**
  * Fixed 8 Firestore `coin_image_index` docs (marine-corps-250th URLs -> `26rj_c.jpg` / `26rj_e.jpg`).
  * Fixed `coin_set_index/uncirculated-coin-set-2026`: coin_count 22 -> 20, moved 2 packaging cards to cards field.
  * Corrected parent doc image URLs and stamped product_code `26RJ`.
  * Added anti-hallucination guardrail to `main.py` FOR SETS prompt (`26RJ != USMC`).
  * Added `repair_26rj_ghosts.py` with dual-path audit and 35 unit tests (all passing).
* **Checklist Ownership & PDF Fixes (v4.329–v4.330):**
  * `HOTFIX PDF_STALE`: Server-side `.get(GetOptions(source: Source.server))` bypasses stale Flutter widget closures.
  * `PDF_STALE_AFTER_CHECKOFF`: Shared `_invalidateAndRefetchCoins()` helper invalidates local cache and triggers atomic FutureBuilder refetch.
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
* **Frontend Dart Analysis:** `dart analyze lib` executed with 0 compilation errors and 5 non-fatal deprecation/interpolation warnings.

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable.
* **Dependabot Vulnerability Management:** ✅ 0 open alerts on default branch.

---

## Test Logs & Isolation Summary
* **Backend Pytest Suite:** `362 passed, 0 failed in 17.16s` (100% pass rate; matches `numista_tests/reports/pytest-output.txt`).
* **Frontend Dart Analyzer:** `Analyzing lib... 5 issues found (0 errors, 5 non-fatal info/deprecation warnings)` (Exit code 0).
* **Frontend Playwright Smoke Suite:** `8/8 passed in 43.8s (auth.setup + 01-homepage only)` (`Master suite: NOT RUN this session`).
* **Frontend Flutter Unit Suite:** `396 passed, 0 failed in 15.0s` (100% pass rate; 0 failures).
* **Layer 3 Data Health Probes:** `7/7 endpoints healthy` (Homepage: 200 OK, Greysheet Config: 200 OK, Pricing: 200 OK, Spot Prices: 200 OK, Template: 200 OK, Passport PDF: 404 sentinel, Transfer Initiate: 422 validation sentinel).
* **Test Isolation Policy & Confirmation:** ✅ Test Isolation: E2E tests target `grokbot@numista.ai` (QC bot account). Authenticated successfully with `uid=eIGZgYb49eeCR4Bsa5ABtHr94L63`. Zero forbidden accounts used (`ericdcman@gmail.com`, `eric.seaman@yahoo.com`, `jseaman1204@gmail.com`). Zero production Firestore mutation.

---

## Recommended Pre-Launch Action Items
1. **Dart Deprecation Cleanups:** Address 5 non-fatal deprecations/lint infos in `screens/ai_chat_screen.dart` (`withOpacity` -> `.withValues()`, `activeColor` -> `activeThumbColor`).
2. **Pytest Deprecation Cleanups:** Address upstream FastAPI/asyncio deprecation warnings in test environments (`asyncio.iscoroutinefunction` slated for removal in Python 3.16).
3. **Skill Maintenance:** Keep `.agents/skills/project-scanner/SKILL.md` aligned with current backend Cloud Run endpoints and newly registered coin programs.
