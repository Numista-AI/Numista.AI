# EXECUTE_DONE: P7 V8.15 Build

**Date:** 2026-10-18 08:12 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `99773ac4e85ff45160ba64fbfe89995859cd723c` (short: `99773ac4`)  
**Git Push Target:** `origin/p7-v8.9` (pushed `f48d15e3..99773ac4`)  
**Flutter Analyze:** 0 errors, 0 warnings (`No issues found! (ran in 19.1s)`)  
**Flutter Test:** 581/581 passed (+1 new test over baseline 580)  

---

## 1. Summary of Changes (NET-312)

This build is a URL-constants refactor so preview builds and integration environments can easily point to test backends using `--dart-define` at compile time and safe origin-gated URL parameters in standalone web assets, while maintaining 100% byte-identical live production defaults.

### Exact Live Backend Default URLs
- **`kApiBaseUrl`:** `https://numista-backend-568985927038.us-central1.run.app`
- **`kScanServiceUrl`:** `https://numista-scan-service-568985927038.us-central1.run.app`

---

## 2. File & Line Cites (`git show 99773ac4`)

| File | Line(s) | Change Summary |
|---|---|---|
| `numista_mobile/lib/constants.dart` | 13–22 | Changed `kApiBaseUrl` and `kScanServiceUrl` to use `String.fromEnvironment('API_BASE_URL', ...)` and `String.fromEnvironment('SCAN_SERVICE_URL', ...)` with byte-identical live URL defaults. |
| `numista_mobile/lib/screens/program_manager_screen.dart` | 22, 2140 | Imported `../constants.dart` and replaced hardcoded string `baseUrl` with `kApiBaseUrl`. |
| `numista_mobile/lib/services/family_subaccount_service.dart` | 2, 48 | Imported `../constants.dart` and replaced hardcoded string `baseUrl` with `'$kApiBaseUrl/api/v1/family'`. |
| `numista_mobile/lib/services/market_news_service.dart` | 44 | Replaced hardcoded string `_baseUrl` with `kApiBaseUrl`. |
| `numista_mobile/lib/services/stripe_service.dart` | 5, 9 | Imported `../constants.dart` and replaced hardcoded string `_baseUrl` with `kApiBaseUrl`. |
| `numista_mobile/lib/services/upcoming_releases_service.dart` | 5, 78 | Imported `../constants.dart` and replaced hardcoded string `_baseUrl` with `kApiBaseUrl`. |
| `numista_mobile/test/p7_v8_ux_safety_test.dart` | 30, 1867–1871 | Added import of `constants.dart` and unit test asserting `kApiBaseUrl` and `kScanServiceUrl` defaults match live URLs byte-for-byte. |
| `numista_mobile/web/add_coins.html` | 2–9, 527–539 | Documented backend API URL strategy at top; implemented `getApiBaseUrl()` with origin-gated `?api=<url>` parameter override for preview channels. |
| `numista_mobile/web/scraper_dashboard.html` | 2–9, 522–534 | Documented backend API URL strategy at top; implemented `getApiBaseUrl()` with origin-gated `?api=<url>` parameter override for preview channels. |

---

## 3. HTML Override Strategy Explanation

Dart `--dart-define` environment values are evaluated at Dart compile time and are not accessible to standalone HTML files (`add_coins.html`, `scraper_dashboard.html`).

To allow preview builds and test environments to point these standalone HTML pages to alternate test backends without security risks:
1. **Origin Verification (`isPreview`):** The origin is verified using regular expressions against known preview patterns:
   - `/\.run\.app$/` (Cloud Run direct preview)
   - `/numista-vault--[^.]+\.(web\.app\|firebaseapp\.com)$/` (Firebase Hosting preview channels)
2. **Strict Production Lockout:** On production domains (`numista.ai` or `numista-vault.web.app` without preview channel prefix), `isPreview` evaluates to `false`. Query parameter overrides are ignored completely and the hardcoded live backend URL is always returned.
3. **Target Validation:** If `isPreview` is true, the `?api=` query parameter is inspected. It must start with `https://` and target a valid `.run.app` Cloud Run endpoint (`/^https:\/\/[^\s]+\.run\.app/`).
4. **Fallback:** If not in preview or if no valid override is supplied, the production live URL `https://numista-backend-568985927038.us-central1.run.app` is returned.

---

## 4. Verification Commands & Results

1. **`flutter analyze lib/`**
   ```
   Analyzing lib...
   No issues found! (ran in 19.1s)
   ```
   Result: **0 errors, 0 warnings.**

2. **`flutter test --reporter compact`**
   ```
   00:31 +581: All tests passed!
   ```
   Result: **581 passed, 0 failed.** (Baseline: 580 -> 581 with new URL constants test).

3. **`git push origin p7-v8.9`**
   ```
   To https://github.com/Numista-AI/Numista.AI.git
      f48d15e3..99773ac4  p7-v8.9 -> p7-v8.9
   ```
   Result: **Clean push to branch `p7-v8.9`.**
