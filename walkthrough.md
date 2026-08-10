# Walkthrough — Audit Review & Infrastructure Fixes (2026-08-10)

## Overview
Morning audit scan revealed a Pytest collection failure and three report generation bugs. All fixed and verified.

## Issues Found & Resolved

### 1. Pytest Collection Failure (CRITICAL)
**File:** `numista_backend/services/passport_pdf_generator.py`
**Root cause:** `test_beta_estate_pipeline.py` imported `downsample_image_to_300dpi_thumb` which was referenced in the test but never implemented. This caused Pytest to abort at the collection phase — zero tests ran, the entire suite appeared to fail.
**Fix:** Implemented the missing function using PIL `thumbnail()` with Lanczos resampling. Returns a `BytesIO` PNG stream ready for ReportLab PDF embedding.
**Result:** 37/37 Pytest tests passing.

### 2. Report Generator: Pytest Log Encoding Bug
**File:** `numista_tests/generate_report.js`
**Root cause:** PowerShell's `Tee-Object` writes files as **UTF-16 LE** (BOM: `FF FE`). Node's `readFileSync('utf8')` read each character as garbled (null bytes between every char), so regex matches on `"37 passed"` returned null — the scorecard showed `"See log"` instead of the actual result.
**Fix:** Detect UTF-16 LE BOM and decode accordingly before running regex.

### 3. Report Generator: Skipped Tests Counted as Failures
**File:** `numista_tests/generate_report.js`
**Root cause:** `countSuiteTests()` incremented `total` for every test including skipped ones, then compared `total === passed`. Skipped tests were never in `passed`, so `master_ui_e2e.spec.ts` always showed `❌ 2 failed`.
**Fix:** Skipped tests excluded from `total`/`passed` counts. Suite shows `⏭️ 2 skipped (local server required)`.

### 4. Report Generator: Pytest Scorecard Always Showed ✅ PASS
**File:** `numista_tests/generate_report.js`
**Root cause:** Pytest row was hardcoded to `✅ PASS` regardless of log content. Even when Pytest showed `ERRORS`, the scorecard showed green.
**Fix:** `pytestPassed` boolean now derived from log parsing. Scorecard shows `❌ FAIL` when errors detected.

### 5. Pre-Push Hook: Broken Windows Store Python Stub
**File:** `.git/hooks/pre-push`
**Root cause:** Hook called `python3` which on Windows resolves to `AppData/Local/Python/pythoncore-3.14-64/python.exe` — an orphaned Windows Store Python stub with no actual binary. Emitted `[ERROR] Failed to launch... (0x80070002)` on every push.
**Fix:** Hook now uses `numista_backend/.venv/Scripts/python.exe` directly. Falls back to bare `python` if venv doesn't exist.

## Final State
| Component | Status |
|---|---|
| Pytest | ✅ 37/37 |
| Playwright E2E | ✅ 120/120 active (2 skipped — expected) |
| Report scorecard accuracy | ✅ All rows now reflect actual state |
| Pre-push hook noise | ✅ Eliminated |
| Dependabot on `main` | ⚠️ 128 alerts — cleared after next `dev → main` merge |
