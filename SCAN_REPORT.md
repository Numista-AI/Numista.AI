# SCAN_REPORT.md — Numista.AI 360° System Audit

**Date:** 2026-10-16 09:07 ET  
**Branch:** `dev` (clean, synced with `origin/dev`)  
**Scanner:** Antigravity project-scanner skill  
**Session:** Docs-only scan (Rule 9 — no source code modifications)

---

## Executive Summary

### 🟢 PASS WITH WARNINGS

All test suites exit 0. Two non-fatal `dart analyze` warnings in a test file.
No compilation errors, no security alerts, no backend failures.

---

## 1. Frontend — Flutter

### `flutter analyze`
- **Exit code:** 1 (warnings only, no errors)
- **Issues:** 2 warnings, 0 errors, 0 info
  1. `warning` — Unused import: `package:firebase_auth/firebase_auth.dart`  
     → `test/p7_v8_ux_safety_test.dart:1:8` (`unused_import`)
  2. `warning` — Dead code  
     → `test/p7_v8_ux_safety_test.dart:1253:14` (`dead_code`)
- **Note:** Both warnings are in a test file, not production code. No production lint issues.

### `flutter test`
- **Exit code:** 0
- **Result:** **559 passed / 0 failed**
- **Non-fatal runtime note:** `test/ux_fixes_test.dart:202` — `tap()` on `PinBoxRow` widget derived offset off-screen (cosmetic, test still passed)
- **Version:** 4.403.0+403
- **Dart SDK:** ^3.11.3

---

## 2. Backend — Python / FastAPI

### Backend Pytest
- **Exit code:** 0
- **Result:** **566 passed / 0 failed / 0 errors** in 26.42s
- **Python:** 3.14.2, pytest 9.1.1
- **Artifact:** `numista_tests/reports/pytest-output.txt` matches (last line: `566 passed in 26.42s`)

### Dependencies
- **Total packages:** 115 (via `requirements.txt`)
- **Core:** FastAPI 0.141.1, Uvicorn 0.44.0, Pydantic 2.12.5
- **Google Cloud / GenAI:** google-genai 1.75.0, firebase_admin 7.3.0, google-cloud-firestore 2.26.0
- **Auth & Payments:** PyJWT 2.14.0, cryptography 50.0.1, stripe 15.2.1

### CORS Configuration
- Explicit allowlist: `numista.ai`, `numista-vault.web.app`, `numista-vault.firebaseapp.com`, localhost variants
- Regex: `^https://numista-vault--[a-z0-9-]+\.web\.app$` (preview channels)
- Explicit OPTIONS preflight handler for `identify_coin_photo` (prevents 405 on mobile)
- **Status:** ✅ Properly configured

---

## 3. End-to-End / Playwright

### Playwright Smoke: NOT RUN this session
### Master suite: NOT RUN this session

No E2E tests were executed during this scan session.

---

## 4. Git & Version Control

| Metric | Value |
|--------|-------|
| Branch | `dev` |
| Working tree | Clean |
| Ahead of `origin/dev` | 0 commits |
| Ahead of `origin/main` | 354 commits |
| Last commit | `51c3f57d` — Rule 9 Gemini quota saver + NET-271 to AGCOS |

### Recent Commits (last 10)
```
51c3f57d Rule 9 Gemini quota saver + NET-271 to AGCOS
2f8ec229 docs(radio): P7 V8.8 UX gate FAIL; NET-270 V8.9 orders
35d35cc9 docs(radio): NET-268 day watch; NET-269 P7 V8.8 preview up
32821a49 docs(radio): NET-267 day watch hourly re-flag
e104ee0f docs(radio): NET-264..266 day watch stand-down
d609bda1 docs(radio): NET-262/263 day watch stand-down
ff4c4213 docs(radio): NET-261 day watch board unchanged
1ff5e421 docs(radio): NET-260 day watch board unchanged
96c1767b docs(radio): NET-259 day watch board unchanged
feff22a5 docs(radio): NET-258 eve watch stand-down hourly re-flag
```

**⚠️ Note:** 354 commits on `dev` ahead of `main`. A merge/PR to `main` is pending Eric's review.

---

## 5. Security & Configuration

### Firestore Rules
| File | Size | Last Modified (UTC) |
|------|------|---------------------|
| `numista_mobile/firestore.rules` | 17,573 B | 2026-10-15 15:08:22 |
| `numista_backend/firestore.rules` | 12,166 B | 2026-10-14 15:41:16 |

**⚠️ HOLD — Firestore Rules Divergence:** The two `firestore.rules` files differ by **217 lines**. The `numista_mobile/` copy (deployed) is canonical; the `numista_backend/` copy is stale and behind. This is a known issue — the backend copy should be synced or removed to avoid confusion.

### Environment Files
| File | Status |
|------|--------|
| `numista_backend/.env` | ✅ Present (2,824 B, last modified 2026-07-25) |
| Root `.env` | Not present |
| `numista_mobile/.env` | Not present |
| `numista_admin/.env.local` | Present |
| `numista_hardware/.env` | Present |
| `numista_tests/.env` | Present |

### `.gitignore` Coverage
- `.env` files, `*.db`, `scratch/`, `output/`, `*.cache` — expected to be in `.gitignore`

---

## 6. Model & Program Registry

### Gemini Models in Use
| Model | Role | Shutdown Status |
|-------|------|-----------------|
| `gemini-3.8-flash` | Primary workhorse | No shutdown announced |
| `gemini-3.1-pro-preview` | Pro tasks | No shutdown announced |
| `gemini-3.5-flash-lite` | Lite tasks | No shutdown announced |
| `gemini-3.1-flash-image` | Image editing | No shutdown announced |
| `gemini-embedding-2` | RAG / vector embeddings (1536-dim) | No shutdown announced |

**Note:** `littleton_sku_helper.py:330` mentions `gemini-3.5-flash` in a docstring example only — not an active model call.

### Program Count
- **35 official programs** in `master_coin_programs.json` (563,938 B)
- Covers: Lincoln Cents, Morgan Dollars, American Silver Eagles, Presidential Dollars, America250, and 30 more series

---

## 7. Test Isolation

No E2E tests were executed this session. Default test account: `grokbot@numista.ai` (QC bot account).
No forbidden accounts (`ericdcman@gmail.com`, `eric.seaman@yahoo.com`, `jseaman1204@gmail.com`) were used.

---

## 8. Holds & Action Items

| # | Severity | Item | Owner |
|---|----------|------|-------|
| 1 | ⚠️ Warning | `flutter analyze` — 2 warnings in `test/p7_v8_ux_safety_test.dart` (unused import L1, dead code L1253) | Next P7 baton |
| 2 | ⚠️ Warning | `numista_backend/firestore.rules` is stale — 217-line divergence from canonical `numista_mobile/firestore.rules` | Dedicated baton |
| 3 | ℹ️ Info | 354 commits on `dev` ahead of `main` — PR/merge pending Eric's review | Eric |

---

## 9. Scanner Safety Compliance

- [x] Scanner ran on `dev` branch only
- [x] No push to `main`
- [x] No production Firestore mutations
- [x] No source code files modified (Rule 9 — docs-only)
- [x] Explicit file paths used for staging (no `git add .` or `git add -A`)
- [x] `SUITE_MANIFEST.json` forbidden accounts respected
- [x] Pytest artifact (`pytest-output.txt`) matches claimed count (566 passed)
