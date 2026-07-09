# Walkthrough — Numista.Ai System Check & Audit (2026-07-09)

## Audit Results Committed and Pushed to `main`

| Commit | Scope | Summary |
|---|---|---|
| `1c8ca8e` | Scan Report | Generated and updated `SCAN_REPORT.md` with comprehensive system scan and audit results |
| `6504f9a` | Walkthrough | Documented today's system scan report and findings |

**Status Summary:**
- **Core App Navigation & Demo (Suites 01-07):** **✅ PASSING (94/104 tests passed)**
- **Greysheet API & Deals (Suites 08-10):** ❌ **FAIL (10/104 tests failed)** due to missing API endpoints in backend routing and credential degradation.
- **Flutter Code Health (dart analyze):** ❌ **FAIL** (0 Errors, 11 Warnings, 19 Info messages)

---

## Findings Details

### 1. Backend Route Regression & Mismatches
- **Critical Mismatches:**
  - `GET /api/greysheet/config` -> ❌ **404 Not Found** (Expected by `08-greysheet-valuation.spec.js` and `10-greysheet-coin-detail.spec.js`)
  - `POST /api/greysheet/batch` -> ❌ **404 Not Found** (Expected by `08-greysheet-valuation.spec.js` and `10-greysheet-coin-detail.spec.js`)
  - `GET /api/ebay/search` -> ❌ **404 Not Found** (Expected by `09-deals-arbitrage.spec.js` as EPN affiliate endpoint)
  - `GET /api/greysheet/cac` -> ❌ **404 Not Found** (Expected by `10-greysheet-coin-detail.spec.js`)
  - `GET /api/portfolio/snapshot` -> ❌ **404 Not Found** (Backend implements `@app.post("/api/portfolio/snapshot/daily")`)
  - Pricing `/api/greysheet/pricing/{gsid}` and `/api/greysheet/resolve` endpoints failed assertions due to credential/config mismatches during automated testing.

### 2. Greysheet API Key & Credentials
- **Credentials:** Missing `GREYSHEET_API_KEY` and `GREYSHEET_API_TOKEN` in the environment configuration, falling back to default/restricted dev credentials.
- **API Response:** The Greysheet API returns pricing records containing only CPG Retail values, with all wholesale bid/ask fields (`GreyVal`) empty.
- **Fallback Rate:** **100%** fallback to `cpg_retail * 0.80` bid calculation.

### 3. Flutter Code Quality (30 Issues)
- **11 Warnings:** Unused variables (`margin`, `totalCount`), unused imports (`dart:typed_data`), and extending sealed classes (`DocumentSnapshot`).
- **19 Info Messages:** Deprecated Flutter member usages (`withOpacity` should use `.withValues()`, `activeColor` should use `activeThumbColor`/`activeTrackColor`).

---

## Action Items Recommended
1. **Synchronize FastAPI Routes:** Align backend routing definitions in `main.py` with test suite calls (or correct the test suites to match the actual implemented routes).
2. **Configure API Credentials:** Update environment parameters with active Greysheet production API keys to unlock advanced wholesale valuation.
3. **Clean Up Flutter Warnings:** Resolve the Dart analyzer findings to restore compiler status.
