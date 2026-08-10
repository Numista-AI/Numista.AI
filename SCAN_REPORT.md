# SCAN REPORT: Numista.AI System Audit (v4.2)

## Executive Summary
* **Status:** 🟡 **WARNING** (System scan completed. Pytest unit suite: 34 passed, 1 collection error in `test_beta_estate_pipeline.py`. Playwright E2E: 120/120 active tests passed [2 skipped — expected]. Flutter analyze: 44 info notices [0 errors, 0 warnings]. Gemini models: 100% active 2026 GA compliance.)
* **Scan Date:** 2026-08-10
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.2, Frontend v4.2 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Dev Environment Notes
1. ✅ **Greysheet API Dev Fallback (Expected — Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 hardening policy. Dev defaults to Tier 0 Firestore `config/greysheet` cache. Production credentials managed via Cloud Run environment variables.

---

## Cloud Run Secret Presence Check
* `GREYSHEET_API_KEY`: ✅ **SET** in Cloud Run environment variables (verified live probe `200 OK`)
* `GREYSHEET_API_TOKEN`: ✅ **SET** in Cloud Run environment variables (verified live probe `200 OK`)

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
* **Greysheet Quota Probe (`https://numista-backend-568985927038.us-central1.run.app/api/greysheet/quota`):** ✅ `200 OK` (1612 calls used out of 50,000 hard cap threshold)
* **Greysheet Pricing Probe (`https://numista-backend-568985927038.us-central1.run.app/api/greysheet/pricing/429`):** ✅ `200 OK` (Returns full 1793 1/2c MS BN pricing table across all grades P1 to MS66, CAC & non-CAC)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Firestore fallback.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) & Secure Passport active. Inventory loading, multi-term search, and collection selection verified.
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/estate/...`) active.
* **Vertex AI & Search Grounding:** Verified. `/api/coin_search` endpoint registered and active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series & Uncirculated Set checklist templates active.
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail, max-width containers, and web hotkeys active.
* **Phase 2 Desktop Bulk Import:** Verified. Deduplication hub and valuation pipeline v2 active.
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity active.
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active.
* **Phase 3 Step 1 — Affiliate EPN Wishlist:** Verified. Shareable wishlist links, backend reservation router, and Firestore security rules active.
* **Phase 3 Step 2 — Stripe Billing & Attorney Portal:** Verified. Stripe billing integration and attorney portal signed URLs active.
* **Release Notes Automation:** Verified. Automated release notes via git commits and CI build step active.
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active.

---

## Backend Architecture Health
* **main.py Deconstruction:** ✅ **COMPLETE.** All backend routes migrated from monolithic `main.py` into dedicated `APIRouter` modules.
* **Route Parity:** `route_snapshot_baseline.json` committed — diff tool active for regression detection.
* **Backend Test Coverage:** 34 passed, 168 warnings, 1 collection error (`test_beta_estate_pipeline.py`).
* **Email Normalization:** ✅ User emails normalized to lowercase across auth and Firestore path getters.

---

## Security Audit
* **Dependabot Vulnerabilities (2026-08-08):** ✅ **22 CVEs RESOLVED** on `dev` via `requirements.txt` upgrades.
* **CodeQL Alert #69:** ✅ **RESOLVED.** Smithsonian domain check uses `urlparse` netloc.
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, secret hygiene enforced.
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` Cloud Run environment variable.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** 34 passed, 1 error (`test_beta_estate_pipeline.py` collection error)
* **Frontend Playwright E2E Suite:** 120/120 active tests passed · 2 skipped (local dev server guard — expected)
* **Frontend Flutter Analyze:** 44 info notices (deprecated parameter warnings) · 0 syntax errors · 0 compile errors
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Critical Errors & Warnings Summary
1. 🔴 **`tests/test_beta_estate_pipeline.py` ImportError**:
   ```
   ImportError: cannot import name 'downsample_image_to_300dpi_thumb' from 'services.passport_pdf_generator'
   ```
2. ℹ️ **Flutter Deprecated Parameter Notices (44 count)**:
   - `dataRowHeight` deprecated in `lib/screens/add_coins_hub.dart`
   - `activeColor` deprecated in `lib/screens/admin_feedback_screen.dart`, `lateral_transfer_screen.dart`, `program_manager_screen.dart`
   - `value` deprecated in `lib/screens/family_settings_screen.dart`, `beta_feedback_widget.dart`

---

## Recommended Fixes
1. **Fix `test_beta_estate_pipeline.py` Import**: Update `passport_pdf_generator.py` or `test_beta_estate_pipeline.py` to use the updated thumbnail function name.
2. **Clean up Flutter Deprecations**: Replace deprecated Flutter widgets/properties in `numista_mobile` (`dataRowHeight` → `dataRowMinHeight`/`dataRowMaxHeight`, `activeColor` → `activeThumbColor`).
3. **Merge `dev` → `main`**: Dependabot security patches are ready on `dev` awaiting deployment PR.
