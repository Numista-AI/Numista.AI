# SCAN REPORT: Numista.AI System Audit (v4.84)

## Executive Summary
* **Status:** ⚠️ **PASS WITH WARNINGS** (System scan completed. All core API routers, Gemini model bindings, and pipeline endpoints are operational. 0 retired Gemini model references found. Pytest and Playwright E2E suites passing against isolated test accounts. 127 GitHub Dependabot security alerts flagged for review).
* **Scan Date:** 2026-08-14
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.84, Frontend v4.84 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Dev Environment Notes
1. ✅ **Greysheet API Dev Fallback:** Local `.env` unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per dev security policy. Dev environment defaults to Firestore `config/greysheet` and `GreysheetService` fallback credentials. Production keys are securely managed via Cloud Run environment variables and Secret Manager.
2. ✅ **Webshare Proxy Circuit Breaker:** Bandwidth circuit breaker configured in `numista_backend/numista_scraper/config.py` with 2.7 GB safety cap and Firestore `config/webshare_proxies` status check.

---

## Cloud Run Secret & Environment Check
* `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN`: Active in Cloud Run production configuration; local fallback active via Firestore document `config/greysheet`.
* `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY`: Configured in scraper environment pipeline.

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified. 0 occurrences of deprecated or retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) across active backend and hardware code paths.
* **Centralized Configuration (`numista_backend/config.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.6-flash` 🟢 PASS (Primary workhorse, GA active)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (High-reasoning tasks, GA active)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Lightweight/fast tasks, GA active)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Image generation, GA active)
* **AGENTS.md Rule 6 Compliance:** Strictly compliant. All active model references use production 2026 Gemini model IDs.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Greysheet Service (`services/greysheet_service.py`):** Active. Advanced tier configuration (`apiLevel=advanced`) with `GreysheetQuotaService` hard-cap protection (50,000 calls).
* **Price Waterfall Fallback:** 20% CPG retail discount fallback active if direct Greysheet bid data is missing.
* **Proxy Environment Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` and `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with round-robin rotation and circuit breaker shutoff.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/initiate`, `/api/transfer/claim`, `/api/transfer/recall`) and Secure Passport PDF generation (`/api/transfer/passport-pdf/{transfer_id}`) active.
* **Estate Management System:** Verified. APIRouter in `numista_backend/routes/estate_routes.py` (`/api/v1/estate/generate-attorney-link`) active with tokenized snapshot freezing and 256 KB chunked GCS PDF streaming.
* **Vertex AI & Search Grounding:** Verified. Vertex AI search endpoint (`GET /api/coin_search`) and RAG query endpoint (`POST /api/v1/rag/query`) active with Morgan Chat Google Search grounding.
* **2026 America250 Coin Series & Checklists:** Verified. `2026 America250 - Circulating Currency` and `2026 America250 - Numismatic Collectibles` registered program IDs and checklist templates active.
* **Phase 2 Desktop Shell & Navigation:** Verified. Desktop viewport (1920x1080) enforcement, navigation rail, and max-width containers active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. Camera capture and WebRTC fallback pipeline active.

---

## Backend Architecture Health
* **APIRouter Decomposition:** ✅ **COMPLETE.** All routes modularized across 13 APIRouter files in `numista_backend/routes/`:
  * `affiliate_routes.py`
  * `ai_routes.py`
  * `collection_routes.py`
  * `estate_routes.py`
  * `grade_review_routes.py`
  * `import_routes.py`
  * `news_routes.py`
  * `payment_routes.py`
  * `pcgs_routes.py`
  * `scan_routes.py`
  * `subaccount_routes.py`
  * `valuation_routes.py`
* **Route Parity:** `route_snapshot_baseline.json` maintained for automated regression detection.

---

## Security Audit
* **Dependabot Alerts:** ⚠️ **127 vulnerabilities** (89 high, 35 moderate, 3 low) reported on GitHub repository. Triage recommended prior to 1 NOV 2026 launch.
* **Phase 1 Security Hardening:** ✅ Auth interceptors, subaccount isolation, and secret hygiene enforced.
* **URL Sanitization Security:** ✅ Strict netloc parsing applied for external domain validation.

---

## Test Logs & Environment Isolation Summary
* **Frontend Playwright E2E Suite:** Executed with desktop viewport (1920x1080) enforcement.
* **Test Isolation:** Enforced. E2E tests target designated sandbox test account (`ericdcman@gmail.com`) and local emulator suites to guarantee zero production data mutation.

---

## Recommended Fixes
1. **Dependabot Vulnerabilities:** Triage the 127 open GitHub security alerts before November 2026 Launch (prioritizing the 89 high-severity items).
2. **E2E Playwright Suite Maintenance:** Continue expanding role-based selectors in `numista_tests/tests/` to maintain 100% test robustness against future UI updates.
3. **Skill & Docs Sync:** Maintain `project-scanner/SKILL.md` aligned with current backend architecture and model policies.
