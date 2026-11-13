# NET-314 | AGCOS to GROKCOS | P7 V8.15 Build Done — Ready for Score
Filed 18 Oct 2026, 8:13 AM ET.

## Commit
- **SHA:** `99773ac4e85ff45160ba64fbfe89995859cd723c` (short: `99773ac4`)
- **Branch:** `p7-v8.9` → pushed to `origin/p7-v8.9`
- **Range:** `f48d15e3..99773ac4`

## Gate Results
- `flutter analyze lib/`: **0 errors, 0 warnings** (ran in 19.1s)
- `flutter test --reporter compact`: **581/581 PASS** (+1 over V8.14 baseline of 580)

## Files Changed (9 files)
| File | Lines | Change |
|------|-------|--------|
| `numista_mobile/lib/constants.dart` | 13–22 | `kApiBaseUrl` + `kScanServiceUrl` → `String.fromEnvironment(...)` with byte-identical live defaults |
| `numista_mobile/lib/screens/program_manager_screen.dart` | 22, 2140 | Import `constants.dart`; replace hardcoded `baseUrl` with `kApiBaseUrl` |
| `numista_mobile/lib/services/family_subaccount_service.dart` | 2, 48 | Import `constants.dart`; replace hardcoded `baseUrl` with `'$kApiBaseUrl/api/v1/family'` |
| `numista_mobile/lib/services/market_news_service.dart` | 44 | Replace hardcoded `_baseUrl` with `kApiBaseUrl` |
| `numista_mobile/lib/services/stripe_service.dart` | 5, 9 | Import `constants.dart`; replace hardcoded `_baseUrl` with `kApiBaseUrl` |
| `numista_mobile/lib/services/upcoming_releases_service.dart` | 5, 78 | Import `constants.dart`; replace hardcoded `_baseUrl` with `kApiBaseUrl` |
| `numista_mobile/test/p7_v8_ux_safety_test.dart` | 30, 1867–1871 | Added test: `kApiBaseUrl` and `kScanServiceUrl` defaults == live URLs byte-for-byte |
| `numista_mobile/web/add_coins.html` | 2–9, 527–539 | `getApiBaseUrl()` JS fn with origin-gated `?api=` override |
| `numista_mobile/web/scraper_dashboard.html` | 2–9, 522–534 | Same `getApiBaseUrl()` pattern as add_coins.html |

## Exact Default URL Values (byte-identical to live)
- `kApiBaseUrl`: `https://numista-backend-568985927038.us-central1.run.app`
- `kScanServiceUrl`: `https://numista-scan-service-568985927038.us-central1.run.app`

## HTML Override Strategy
Dart `--dart-define` cannot be read by standalone HTML pages. Solution:
- `getApiBaseUrl()` JS function checks `window.location.origin`
- **Preview origins** (`*.run.app`, `numista-vault--*.web.app`, `numista-vault--*.firebaseapp.com`): honors `?api=<url>` if value matches `^https://[^\s]+\.run\.app`
- **Production origins** (`numista.ai`, `numista-vault.web.app` without preview prefix): override rejected completely — always returns live URL
- **Fallback**: returns `https://numista-backend-568985927038.us-central1.run.app`

## GEMINI38 Review
- `BATONS\GEMINI38_REVIEW_P7_V8_15_BUILD.md` — Verdict: **PASS**
- Rule 9.3 satisfied (>2 files touched → review filed)

## EXECUTE_DONE
- `BATONS\EXECUTE_DONE_P7_V8_15.md` ✅

Ready for Grok CoS scoring. Handing baton.
OVER
