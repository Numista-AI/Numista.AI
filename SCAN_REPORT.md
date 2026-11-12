# SCAN_REPORT.md — Numista.AI 360° System Audit

**Date:** 2026-11-12 18:38 ET  
**Branch:** `p7-v8.9` (at `2261f1cf`, 596 commits ahead of `origin/main`)  
**Scanner:** Antigravity overnight 360° audit (`project-scanner`)  
**Session:** Docs-only audit + plan revisions (no source code modifications)

---

## Executive Summary

### 🟡 NEEDS HYGIENE (Lint Clean; 5 Actionable Test/Env Findings)

`flutter analyze` passes with **0 issues**, and **1,446** automated tests pass across Flutter (`746`), `numista_backend/tests/` (`625`), and `numista_tests/` (`75`). Five concrete, low-blast-radius hygiene items were surfaced for the next code/ops baton.

---

## 1. Frontend — Flutter (`numista_mobile`)

- **App version:** `8.18.15+81818` (`numista_mobile/pubspec.yaml:19`)
- **Dart SDK:** `^3.11.3`

### `flutter analyze`
- **Exit code:** `0` (`No issues found!`)

### `flutter test`
- **Exit code:** `1`
- **Result:** **746 passed / 1 failed**
- **Failure:** `test/auth_guard_test.dart` — `"No bare http.* backend calls exist outside HttpAuthClient"` flagged `numista_mobile/lib/screens/desktop_agent_download_screen.dart:62`:
  ```dart
  final resp = await http.get(
  ```
  (Introduced in `9d736220`; should route through `HttpAuthClient`.)

---

## 2. Backend — Python / FastAPI

### `pytest numista_backend/tests/`
- **Raw invocation:** Blocked at collection/import by `UnicodeDecodeError: 'utf-8' codec can't decode byte 0x97` when `numista_backend/stripe_config.py:9` executes `load_dotenv()` against `numista_backend/.env` (cp1252 byte on line 3).
- **With cp1252 `load_dotenv()` fallback:** **625 passed / 2 failed** (`41.87s`, exit code `1`):
  1. `test_cert_lookup.py::test_extract_cert_from_image_truncated_json_repair` (`line 874`) — `No module named 'json_repair'`. `json-repair>=0.64.0` is listed at `numista_backend/requirements.txt:151` (`json-repair>=0.64.0`) but missing from `numista_backend/.venv`.
  2. `test_container_import_path.py::test_container_import_path` (`line 79`) — subprocess import of `main` hit the unpatched `stripe_config.py:9` `load_dotenv()` UTF-8 `0x97` error.

### `pytest numista_tests/`
- **Default collection:** **4 collection errors** caused by `numista_tests/test_attorney_routes.py:67-68`:
  ```python
  _deps_stub = types.SimpleNamespace(db=_mock_db, logger=_mock_log)
  sys.modules["routes.deps"] = _deps_stub
  ```
  The incomplete stub lacks `get_current_user` and leaks across module imports into `test_awq_intake_parser.py`, `test_denomination_normalizer.py`, and `test_feedback_callable.py`.
- **With `--ignore=numista_tests/test_attorney_routes.py`:** **75 passed / 2 failed** (exit code `1`):
  - `test_passport_pdf.py::test_format_financial_details_dual_valuation` and `test_format_financial_details_ukn_cost_and_missing_guide` fail because they still assert `'<b>Wholesale (Bid):</b>'` after retail-only CPG migration.

---

## 3. Git & Version Control

| Metric | Value |
|--------|-------|
| Branch | `p7-v8.9` |
| Head commit | `2261f1cf` (`fix(valuation,transfer): fix banknote valuation routing/schema sync and lateral transfer privacy/archive leaks`) |
| Ahead of `origin/main` | `596` commits |
| Deploy status | `origin/main` untouched (locked) |

---

## 4. Security & Configuration

- **Firestore Rules Divergence:** `numista_mobile/firestore.rules` is **350 lines** (canonical/deployed) vs `numista_backend/firestore.rules` at **248 lines** (stale).
- **`.env` Encoding:** `numista_backend/.env` contains a cp1252 `0x97` byte on line 3; re-saving as UTF-8 or adding a cp1252 fallback in `stripe_config.py:9` unblocks bare `pytest`.

---

## 5. Action Items & Overnight Plan Queue

### Hygiene Backlog (for next code/ops baton)
| # | Severity | Item | Target |
|---|----------|------|--------|
| 1 | ⚠️ Medium | Replace bare `http.get` at `desktop_agent_download_screen.dart:62` with `HttpAuthClient` | `numista_mobile/lib/screens/desktop_agent_download_screen.dart:62` |
| 2 | ⚠️ Medium | Fix `.env` UTF-8 encoding / `stripe_config.py:9` fallback and install `json-repair>=0.64.0` in `.venv` | `numista_backend/stripe_config.py:9` |
| 3 | ⚠️ Low | Restore `sys.modules["routes.deps"]` in `test_attorney_routes.py` (or use `monkeypatch`) + update `test_passport_pdf.py` Wholesale assertions | `numista_tests/test_attorney_routes.py:67-68` |
| 4 | ⚠️ Low | Sync or retire stale `numista_backend/firestore.rules` (248 vs 350 lines) | `numista_backend/firestore.rules` |

### Revised Overnight Plans Ready for Grok CoS Review (Sunday Quota Reset)
1. **NET-817 (Cards v2.3 & Images v2.3):** `docs/FAILFIX_PLAN_NET-780b_CARDS_v2.3.md`, `docs/FAILFIX_PLAN_NET-780c_IMAGES_v2.3.md`
2. **NET-810 (Mint Product Lookup v1.7):** `docs/PLAN_NET-810_MINT-PRODUCT-FIELDS_DETAIL-VIEW_v1.7.md`
3. **NET-814 (Public Catalog / Soft-404 / Pricing v2.0):** `docs/PLAN_SOFT404-PUBLIC-CATALOG-PRICING_v2.0.md` + `docs/PLAN_NET-801_SOFT404_PUBLIC-CATALOG_PRICING_v2.0.md`
4. **NET-813 (Unified Coin Details View v2.1):** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v2.1.md`
