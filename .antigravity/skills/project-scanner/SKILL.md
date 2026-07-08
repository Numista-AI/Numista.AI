---
name: project-scanner
description: Run a comprehensive check on the Numista.Ai codebase, including error checks, pipeline audit, running test suites, and Greysheet API key validation to produce a scan report.
---

# Numista.Ai System Scanner Skill

## Context
This skill is triggered to perform a comprehensive system check, error audit, pipeline verification, and API credential health check for the Numista.Ai coin-recognition/data project.

## Instructions

### 1. Error Check
Scan the repository for:
- Broken imports, syntax errors, and undefined symbols in Python and Dart files.
- Malfunctioning LLM integration boundaries or missing API keys.
- Deprecated model IDs (e.g., `gemini-1.5-flash` — must be `gemini-3.5-flash` or newer per AGENTS.md Rule 5).

### 2. Data Pipeline Audit
Verify that local data schemas match the expected format for coin datasets, including:
- `numista_backend/numista_scraper/scrapers.py` — check proxy env vars are `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY` (not the global `HTTP_PROXY`).
- `numista_backend/brain_watcher.py` — confirm `INBOX_DIR` is set to `Numista_Brain_Inbox` only (not expanded to other directories).

### 3. Greysheet API Key Validation *(new — added v4.0)*
Check the health of the Greysheet CDN API integration:
- Verify the `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` environment variables are present in the Cloud Run service or `.env` config.
- Send a test probe to `https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/config` — expect HTTP 200 or 401/403 (never 404 or 500).
- Send a test probe to `https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/pricing/<any-gsid>` — expect HTTP 200, 401, or 403 (never 404 or 500).
- Report the Greysheet API tier in use: **Basic** (GreyVal1 only) or **Advanced** (full bid/ask).
- Flag if `greysheet_service.py` is returning fallback values for >80% of coins (indicates API key may be expired or invalid).

### 4. Execution
Run any existing local test suites and log the output:
```powershell
cd c:\Users\ericd\Documents\MyVertexProject\numista_tests
npx playwright test --reporter=json,list
```

### 5. No Wandering
Do not attempt to fix errors automatically during this scan. Only audit and document them.

## Output Requirement
Generate a clean, human-readable markdown file titled `SCAN_REPORT.md` in the project root. Use the "Artifacts" framework to present the data with sections for:
- **Executive Summary** (Pass/Fail status, version scanned)
- **Critical Errors & Warnings**
- **Greysheet API Health** *(new section)*
  - Key presence: ✅ / ❌
  - Endpoint probe results
  - API tier detected
  - Fallback rate estimate
- **Test Logs Summary**
- **Recommended Fixes**
