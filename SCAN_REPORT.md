# SCAN REPORT: Numista.AI System Audit (v4.1)

## Executive Summary
* **Status:** 🟢 **PASS** (System scan completed with 100% pass rate across core test suites. Pytest backend suite: 201 passed in 24.87s. Flutter unit suite: 237 passed, 0 failed. Flutter analyze: 0 errors, 0 warnings, 45 info notes. Master overnight domain completeness engine: 19 PASS, 0 FAIL, 1 WARN. Playwright E2E smoke suite: 7 passed in 31.7s. Gemini models: Active 2026 GA compliance).
* **Scan Date:** 2026-08-23
* **Target Environment:** `dev` branch (`studio-9101802118-8c9a8` project)
* **Versions Scanned:** Backend v4.1, Frontend v4.1 (Beta 1 AUG 26 / Launch 1 NOV 26 alignment)

---

## Dev Environment Notes
1. ✅ **Greysheet API Dev Fallback (Expected — Phase 1 Security Hardening):** Local `.env` intentionally unpopulated for `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` per Phase 1 hardening policy. Dev defaults to Tier 0 Firestore `config/greysheet` cache. Production credentials are managed via GCP Secret Manager / Cloud Run environment variables.
2. ⚠️ **Service Account Dev Isolation (Expected):** Local development environment intentionally omits `serviceAccountKey.json`; safely falls back to Firestore mock / ADC.

---

## Cloud Run Secret & Environment Variable Presence Check
* `GREYSHEET_API_KEY`: ✅ **SET** in Cloud Run environment variables
* `GREYSHEET_API_TOKEN`: ✅ **SET** in Cloud Run environment variables
* `STRIPE_WEBHOOK_SECRET`: ✅ **SET** in Cloud Run environment variables
* `STRIPE_PUBLISHABLE_KEY`: ✅ **SET** in Cloud Run environment variables
* `NUMISTA_API_KEY`: ✅ **SET** in Cloud Run environment variables
* `PCGS_BEARER_TOKEN`: ✅ **SET** in Cloud Run environment variables
* `NUMISTA_SCRAPE_HTTP_PROXY`: ✅ **SET** in Cloud Run environment variables
* `NUMISTA_SCRAPE_HTTPS_PROXY`: ✅ **SET** in Cloud Run environment variables

---

## Model Binding & LLM Health
* **Model ID Verification:** Verified across active backend paths. 0 occurrences of deprecated/retired model IDs (`gemini-1.5-*`, `gemini-2.0-*`) in Python backend.
* **Centralized Configuration (`numista_backend/config/__init__.py`):**
  * `GEMINI_FLASH_MODEL`: `gemini-3.7-flash` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_PRO_MODEL`: `gemini-3.1-pro-preview` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_LITE_MODEL`: `gemini-3.5-flash-lite` 🟢 PASS (Active GA / No shutdown date)
  * `GEMINI_IMAGE_MODEL`: `gemini-3.1-flash-image` 🟢 PASS (Active GA / No shutdown date)
* **Cloud Function Note:** `numista_backend/functions/feedbackIntelligence.js` references `gemini-2.5-flash-preview-05-20` (scheduled for update to `gemini-3.7-flash` or `gemini-3.5-flash-lite`).
* **AGENTS.md Rule 6 Compliance:** Strictly compliant.

---

## Greysheet API & Tier 0 Image Waterfall Health
* **Greysheet Probes (`https://numista-backend-568985927038.us-central1.run.app`):** ✅ `200 OK` (Config, quota, batch, resolve, CAC all responding 200 OK)
* **Proxy Configuration (`numista_backend/numista_scraper/config.py`):** Verified. `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` properly handled with Webshare 2.7GB circuit breaker and 500ms jitter.
* **Brain Watcher Inbox (`numista_backend/brain_watcher.py`):** Verified. `INBOX_DIR` configured to `Numista_Brain_Inbox`.

---

## Core Features Audit
* **Asset Transfer & Passport System:** Verified. Lateral Transfer API routes (`/api/transfer/...`) & Secure Passport active and passing tests.
* **Estate Management System:** Verified. Army Property Management estate data structures (`/api/estate/...`) and appraisal URLs active.
* **Vertex AI & Search Grounding:** Verified. Morgan Chat Google Search grounding & Vertex AI endpoints active.
* **2026 America250 Coin Series & Checklists:** Verified. 2026 series & Uncirculated Set checklist templates active across resolvers.
* **Phase 2 Desktop Shell:** Verified. Responsive navigation rail, max-width containers, and web hotkeys active (`feat: Phase 2 Step 2`).
* **Morgan AI Session Persistence v2:** Verified. Context engine v2 with session continuity active (`feat: Phase 2 Step 4`).
* **Hardware Capture v2 & WebRTC Fallback:** Verified. `CameraCaptureService.capturePhoto` API active; WebRTC fallback path confirmed (`feat: Phase 2 Step 3`).
* **Proxy Bandwidth Circuit Breaker:** Verified. Webshare 2.7GB circuit-breaker shutoff active (`numista_backend/numista_scraper/config.py`).
* **User Feedback & Fallback Error System:** Verified. Dialog-free inline feedback panel with chip category multi-select & error escalation active.
* **Phase 4a-C1 Program/Series Autocomplete:** Verified. Canonical SKU write, Theme/Subject adjacency picker, and Program autocomplete active (`feat: Phase 4a-C1`).
* **Phase 4a-C3 Semiquincentennial Prompt Rules:** Verified. 2026 Semiquincentennial prompt rules + `program_hint` injection active (`fix: Phase 4a-C3`).

---

## Backend Architecture Health
* **main.py Deconstruction (Stages 1–4):** ✅ **COMPLETE.** All backend routes migrated from monolithic `main.py` into dedicated `APIRouter` modules:
  * Stage 1: Schemas, services, deps, and route parity baseline (`6426e07`)
  * Stage 2: PCGS, news, payment routes (`d451bd6`)
  * Stage 3: Grade review, import, valuation routes (`e62338d`)
  * Stage 4: Core scan, AI, collection routes (`691fc52`)
* **Route Parity:** `route_snapshot_baseline.json` committed — diff tool active for future regression detection.
* **Backend Test Coverage:** 201 passed in 24.87s across all APIRouter modules.

---

## Security Audit
* **CodeQL Alert #69:** ✅ **RESOLVED.** Incomplete URL substring sanitization for Smithsonian domain check replaced with `urlparse` netloc comparison (`fb1ee0d`).
* **Phase 1 Security Hardening:** ✅ Complete. Auth interceptors, subaccount persistence, and secret hygiene enforced (`75b054d`).
* **PCGS Bearer Token:** ✅ Confirmed via `PCGS_BEARER_TOKEN` environment variable (`a1e3959`).
* **Open Dependabot Alerts:** ⚠️ **160 vulnerabilities** (102 high, 45 moderate, 13 low) flagged on GitHub. These are npm/pub dependency alerts on the default branch — review and triage recommended before November Launch.

---

## Test Logs & Environment Isolation Summary
* **Backend Pytest Unit Suite:** 201 passed (24.87s — Python 3.14.2, pytest-9.1.1)
* **Frontend Flutter Unit Suite:** 237 passed, 0 failed (11s)
* **Frontend Flutter Linter Analysis (`flutter analyze`):** 0 errors, 0 warnings, 45 info notes (ran in 133.7s)
* **Frontend Playwright E2E Suite:** 7 passed (31.7s) — homepage smoke suite executed against live site `https://numista.ai`
* **Master Overnight Domain Completeness Engine:** 19 PASS, 0 FAIL, 1 WARN (Service account key omitted locally in dev — expected)
  * Binder scans, admin grade flags, template download, community nicknames, grade review stats — all 200 OK
  * Domain Invariants: Full-Catalog Matcher ✅, Image Completeness ✅, Precious Metal Melt-Value ✅, LPT Estate Partition ✅, Multi-Vault Tenant Isolation ✅
  * 24-Hour Conversation Miner: 4 sessions mined → `COLLECTION_GRAY_SCREEN_PREVENTION`, `CHECKLIST_HAVE_TOTAL_ALIGNMENT`
  * Real Production Account Audit: 4,511 records audited for `jseaman1204@gmail.com` with 0 critical anomalies / zero valuation drift
* **Test Isolation:** Enforced. E2E tests target `ericdcman@gmail.com` / Demo Suite with zero production Firestore mutation.

---

## Recommended Fixes
1. **Cloud Function Model Alignment:** Upgrade `feedbackIntelligence.js` line 70 model ID from `gemini-2.5-flash-preview-05-20` to `gemini-3.7-flash` or `gemini-3.5-flash-lite` to ensure uniform model policy adherence across Firebase functions.
2. **Flutter Linter Info Notes:** Progressively address the 45 informational notes (mostly `use_super_parameters`, `prefer_final_fields`, `deprecated_member_use`, and `avoid_print` in test fixtures).
3. **Dependabot Vulnerabilities:** Triage the 160 open GitHub security alerts before November 2026 Launch, prioritizing the 102 high-severity items.
4. **Navigation Test Hardening:** Continue migrating remaining hardcoded pixel coordinates in `05-navigation.spec.js` (T01–T12) to semantic role/text selectors.
5. **Maintain Skill Documentation:** Keep `project-scanner/SKILL.md` aligned with production Cloud Run URL.


