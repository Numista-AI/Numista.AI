---
name: project-scanner
description: Run a comprehensive check on the Numista.Ai codebase, including error checks, pipeline audit, running test suites, and Greysheet API key validation to produce a scan report.
---

# Numista.Ai System Scanner Skill

## Context
This skill is triggered to perform a comprehensive system check, error audit, pipeline verification, API credential health check, and model binding verification for the Numista.Ai coin-recognition/data project ahead of Beta (1 AUG 26) and Launch (1 NOV 26).

## Instructions

### 1. Error & Model Binding Check
Scan the repository for:
- Broken imports, syntax errors, and undefined symbols in Python and Dart files.
- Malfunctioning LLM integration boundaries or missing API keys.
- Model Binding Integrity: Confirm all Gemini model references use active 2026 production models (`gemini-3.7-flash`, `gemini-3.6-flash`, `gemini-3.5-flash`, or `gemini-3.1-pro-preview`). Flag any retired/shutdown model IDs (`gemini-1.5-*`, `gemini-2.0-*`, `gemini-2.5-*`) per AGENTS.md Rule 6.

### 2. Data Pipeline & Test Isolation Audit
Verify data schemas and test environment configuration:
- `numista_backend/numista_scraper/scrapers.py` — check proxy env vars are `NUMISTA_SCRAPE_HTTP_PROXY` / `NUMISTA_SCRAPE_HTTPS_PROXY`.
- `numista_backend/brain_watcher.py` — confirm `INBOX_DIR` is set to `Numista_Brain_Inbox`.
- Test Isolation: Verify automated E2E tests run against designated test accounts (`ericdcman@gmail.com`) or local emulator suites to guarantee zero production data mutation.

### 3. Core Feature Health Probes
Audit core platform features:
- **Greysheet API Health**: Check `GREYSHEET_API_KEY` / `GREYSHEET_API_TOKEN` presence and probe endpoints (`/api/greysheet/config`, `/api/greysheet/pricing/<gsid>`). Report tier (Basic vs Advanced) and fallback rates.
- **Asset Transfer & Passport System**: Verify Lateral Transfer API routes (`/api/transfer/...`) and Secure Passport schema endpoints.
- **Estate Management System**: Audit Army Property Management estate data structures (`/api/estate/...`) and ownership handshakes.
- **Vertex AI & Search Grounding**: Verify Vertex AI Data Store connection and Morgan Chat Google Search grounding configurations.
- **2026 America250 Coin Series & Checklists**: Validate 2026 series registration and Uncirculated Set / checklist templates.

### 4. Execution
Run existing test suites with desktop viewport (1920x1080) enforcement:
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
- **Model Binding & LLM Health** (Verification of 2026 Gemini model IDs)
- **Greysheet API & Tier 0 Image Waterfall Health**
- **Core Features Audit** (Asset Transfer, Estate System, 2026 America250 Series, Vertex AI)
- **Test Logs & Environment Isolation Summary**
- **Recommended Fixes**
