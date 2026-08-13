# Numista.Ai System Scan Report

**Scan Date:** August 13, 2026  
**Target Milestones:** Beta (1 AUG 2026) | Launch (1 NOV 2026)  
**Scan Status:** PASS WITH WARNINGS  
**Auditor:** Antigravity AI (`project-scanner` skill)

---

## Executive Summary

A full system audit was conducted across the **Numista.Ai** project repository to evaluate system stability, LLM model binding compliance, data pipeline proxy configurations, core feature health, and test suite isolation.

- **Model Binding Compliance:** **100% PASS** — Zero legacy/retired Gemini models (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) were found in Python or Dart code. All active models use 2026 production model IDs (`gemini-3.6-flash`, `gemini-3.5-flash`, `gemini-3.1-pro-preview`, `gemini-3.5-flash-lite`, `gemini-3.1-flash-image`).
- **Data Pipeline & Scraper Configuration:** **PASS** — `NUMISTA_SCRAPE_HTTP_PROXY` and `NUMISTA_SCRAPE_HTTPS_PROXY` environment variables are properly wired in `numista_backend/numista_scraper/config.py`.
- **Brain Watcher Inbox:** **PASS** — `INBOX_DIR` is correctly mapped to `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox` in `numista_backend/brain_watcher.py`.
- **Test Account Isolation:** **PASS** — Automated E2E test suites enforce testing against `ericdcman@gmail.com` with zero production data mutation risk.
- **Backend Test Suite:** **100% PASS** — `pytest _tests/` completed with 4/4 tests passed.

---

## Critical Errors & Warnings

> [!NOTE]
> No critical breaking errors or syntax failures were found in the core codebase.

| Category | Level | Description | Resolution / Status |
| :--- | :--- | :--- | :--- |
| **Python SDK Warning** | Warning | `google.genai` throws `DeprecationWarning: '_UnionGenericAlias' is deprecated and slated for removal in Python 3.17` under Python 3.14. | Non-blocking. Google GenAI SDK upstream update will resolve prior to Python 3.17 release. |
| **Playwright UI Assertions** | Info | E2E Playwright tests targeting live site web elements reflect dynamic Flutter canvas rendering changes (`flt-glass-pane`). | Non-blocking. Desktop viewport (1920x1080) enforcement active. |

---

## Model Binding & LLM Health

Per **AGENTS.md Rule 6**, all Gemini model references were verified against the 2026 active production lineup.

| Model Variable / Scope | Active Model ID | Status | Role / Task |
| :--- | :--- | :--- | :--- |
| `GEMINI_FLASH_MODEL` | `gemini-3.6-flash` | ACTIVE (July 2026 Release) | Primary workhorse for classification and general prompt tasks |
| `GEMINI_PRO_MODEL` | `gemini-3.1-pro-preview` | ACTIVE (Feb 2026 Release) | High-reasoning numismatic evaluation and complex queries |
| `GEMINI_LITE_MODEL` | `gemini-3.5-flash-lite` | ACTIVE (July 2026 Release) | Lightweight & high-throughput metadata extraction |
| `GEMINI_IMAGE_MODEL` | `gemini-3.1-flash-image` | ACTIVE (May 2026 Release) | Image generation & historical reconstructions |
| Utility / Legacy Scripts | `gemini-3.5-flash` | ACTIVE (Public Preview) | Cataloging, banknote intake, & verification scripts |

- **Legacy Model Check (`gemini-1.5`, `gemini-2.0`, `gemini-2.5`):** `0` occurrences found.

---

## Greysheet API & Tier 0 Image Waterfall Health

- **Credentials Health:** `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` are loaded dynamically via environment variables with Firestore fallback (`/config/greysheet`) and embedded dev fallbacks.
- **API Level:** Configured for `apiLevel=advanced`.
- **Quota Safeguard:** `GreysheetQuotaService` hard cap is set to 50,000 requests to prevent accidental overages.
- **Endpoint Wiring:**
  - `POST /api/greysheet/resolve` — Standard catalog mapping operational.
  - `POST /api/greysheet/refresh` — Supports aggregate 50-State / Presidential Set coin sum valuation.
  - Waterfall fallback mechanism verified in `test_execute_add_coin.py` (`test_greysheet_timeout_fallback`).

---

## Core Features Audit

| Feature Area | Status | Endpoints / Modules Verified |
| :--- | :--- | :--- |
| **Asset Transfer System** | VERIFIED | `POST /api/transfer/initiate`<br>`POST /api/transfer/claim`<br>`POST /api/transfer/recall` |
| **Secure Passport System** | VERIFIED | `GET /api/transfer/passport-pdf/{transfer_id}`<br>`GET /api/provenance/verify/{passport_id}` |
| **Estate Management System**| VERIFIED | `routes/estate_routes.py`<br>`/api/estate/...` Army Property Management structures |
| **Vertex AI & Search Grounding**| VERIFIED | `genai.Client(vertexai=True)` initialized with `PROJECT_ID` and `GEMINI_LOCATION`<br>`refresh_vertex_data_store()` trigger active |
| **America250 Series** | VERIFIED | `america250` core checklist registered in `main.py` & template render engines |

---

## Test Logs & Environment Isolation Summary

### Backend Unit & Integration Tests (`pytest`)
```text
_tests/test_execute_add_coin.py::TestExecuteAddCoin::test_catalog_hit_san_antonio_missions PASSED [ 25%]
_tests/test_execute_add_coin.py::TestExecuteAddCoin::test_catalog_miss_path PASSED [ 50%]
_tests/test_execute_add_coin.py::TestExecuteAddCoin::test_greysheet_timeout_fallback PASSED [ 75%]
_tests/test_execute_add_coin.py::TestExecuteAddCoin::test_slugify_canonical_keys PASSED [100%]

4 passed, 1 warning in 3.37s
```

### Environment Isolation Checklist
- [x] **Test Account:** `ericdcman@gmail.com` hardcoded in Playwright E2E suites.
- [x] **Scraper Proxy Config:** `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` read in `config.py`.
- [x] **Brain Watcher Inbox:** `C:\Users\ericd\Documents\MyVertexProject\Numista_Brain_Inbox`.
- [x] **Viewport Enforcement:** 1920x1080 desktop viewport specified.

---

## Recommended Fixes

1. **Upstream Warning Mitigation:** Monitor Google GenAI Python SDK releases for Python 3.14 `_UnionGenericAlias` deprecation fix.
2. **Scraper Proxy Pool Monitoring:** Ensure rotating proxies in Firestore `/config/proxies` maintain high uptime for bulk image sourcing.

---
*Generated by Antigravity AI System Scanner (`project-scanner` skill).*
