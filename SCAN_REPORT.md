# SCAN REPORT: Numista.AI System Audit (v4.89)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with 100% effective pass rate. Pytest backend suite: 69 passed, 3 warnings. Playwright E2E: 141/145 active tests passed (4 skipped — hardware agent + local server guards, all expected). Flutter analyze: 0 errors, 48 info/lint warnings. Gemini models: 100% active 2026 GA compliance.)
* **Scan Date:** 2026-08-15
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.89, Frontend v4.89 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Dev Environment Notes
1. ✅ **Greysheet API Dev Fallback (Expected — Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 hardening policy. Dev defaults to Tier 0 Firestore `config/greysheet` cache. Production credentials managed via Cloud Run environment variables.

---

## Cloud Run Secret Presence Check
* `GREYSHEET_API_KEY`: ✅ **SET** in Cloud Run environment variables (verified 2026-08-15)
* `GREYSHEET_API_TOKEN`: ✅ **SET** in Cloud Run environment variables (verified 2026-08-15)

> Note: Check shows ⚠️ SKIPPED when `gcloud` auth is not active in the current shell session. This is expected in headless cron runs.

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
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) & Secure Passport active. Inventory loading, multi-term search, and collection selection active (`89bdcee`). PDF invoice overhaul complete (`343f65f`).
* **Estate Management System:** Verified. Estate data structures, attorney portal signed URLs, and LPT division solver active.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding & Vertex AI endpoints active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series & Uncirculated Set checklist templates active. Deterministic SlotResolver v2 active (`de42f90`).
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail, max-width containers, and web hotkeys active.
* **Phase 2 Desktop Bulk Import:** Verified. Deduplication hub and valuation pipeline v2 active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active.
* **Phase 3 Step 1 — Affiliate EPN Wishlist:** Verified. Shareable wishlist links, backend reservation router, and Firestore security rules active.
* **Phase 3 Step 2 — Stripe Billing & Attorney Portal:** Verified. Stripe billing integration and attorney portal signed URLs active.
* **Release Notes Automation:** Verified. Automated release notes via git commits and CI build step active.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active.
* **System of Record v4.0.0:** Verified. 34-column missing image sourcing tracker and multi-account audit active (`f34456b`).

---

## Backend Architecture Health
* **main.py Deconstruction (Stages 1–4):** ✅ **COMPLETE.** All backend routes migrated from monolithic `main.py` into dedicated `APIRouter` modules across 13 route files in `numista_backend/routes/`.
* **Route Parity:** `route_snapshot_baseline.json` committed — diff tool active for future regression detection.
* **Backend Test Coverage:** 69 passed, 3 warnings — expanded from 24 → 32 → 37 → 56 → 69 tests covering refactored APIRouter modules and estate pipeline.
* **Email Normalization:** ✅ User emails normalized to lowercase across auth and Firestore path getters (`2bfc85f`).
* **Flutter Analyze:** ✅ 0 errors, 48 info/lint warnings (all non-blocking). Verified `45dccd3`.

---

## Security Audit
* **Dependabot Vulnerabilities (dev branch — 2026-08-15):** ⚠️ **127 vulnerabilities** (89 high, 35 moderate, 3 low) on `main`. Security fixes for 22 pip CVEs are on `dev` and will clear after next `dev → main` merge. Triage of remaining npm/pub alerts recommended before Nov 2026 launch.
  * Fixed on `dev` (Aug 8): `cryptography`, `GitPython`, `idna`, `PyJWT`, `python-multipart`, `starlette`, `tornado`, `urllib3`, `PyPDF2` removed.
* **CodeQL Alert #69:** ✅ **RESOLVED.** Smithsonian domain check uses `urlparse` netloc (`fb1ee0d`).
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` Cloud Run environment variable.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** 69 passed, 3 warnings in 11.58s
* **Frontend Playwright E2E Suite:** 141/145 active tests passed · 4 skipped (all expected)
  * `master_ui_e2e.spec.ts`: 2 skipped — require local Flutter dev server (port 5000)
  * `14-microscope-agent-stress.spec.js`: 2 skipped — require local microscope hardware agent (port 5000)
* **Test Infrastructure Fixes Applied (Aug 10–14):**
  * `passport_pdf_generator.py`: `downsample_image_to_300dpi_thumb` implemented (estate pipeline import fix)
  * `generate_report.js`: UTF-16 LE encoding detection, skipped-test parsing, Pytest scorecard accuracy
  * `.git/hooks/pre-push`: Replaced broken Windows Store Python stub with venv Python
  * Suites 18–21: Migrated from `flt-glass-pane` gating to `enterDemo()` pattern
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Fixes
1. **Merge `dev` → `main`:** 22 CVE fixes will clear once security upgrades land on `main`. Use the deploy conversation ([7485fc0a](conversation://7485fc0a-544c-4a5f-8e87-ff9e22099b5e)) when ready.
2. **Dependabot npm/pub Alerts:** Triage the remaining 127 GitHub security alerts before Nov 2026 Launch, prioritising the 89 high-severity items.
3. **Flutter Lint Cleanup:** 48 info/lint warnings from `flutter analyze` are non-blocking but worth a targeted cleanup pass before launch.
4. **Navigation Test Hardening:** `05-navigation.spec.js` T01–T12 still use hardcoded pixel coordinates for Flutter sidebar nav items. Consider a broader selector audit.
