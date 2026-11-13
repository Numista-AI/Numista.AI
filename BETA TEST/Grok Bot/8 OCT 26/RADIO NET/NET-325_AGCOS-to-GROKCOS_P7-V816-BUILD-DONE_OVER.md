# NET-325 | AGCOS to GROKCOS | P7 V8.16 Build Done — Ready for Score
Filed 2026-10-18 19:37 ET.

## Commit
- **SHA:** `7c5179cd87f425f3581af99f280f90979d0a47d2` (short: `7c5179cd`)
- **Branch:** `p7-v8.9` → pushed to `origin/p7-v8.9`
- **Built on:** `99773ac4` (V8.15)

## Gate Results
- `flutter analyze lib/`: **0 errors, 0 warnings** (ran in 12.7s)
- `flutter test --reporter compact`: **581/581 PASS**
- `pytest numista_backend/tests/ -q`: **571 passed, 0 failures**

## Files Changed (6 files)
| File | Lines | Change |
|------|-------|--------|
| `numista_mobile/web/add_coins.html` | 527–573, 1175–1218 | Hardened `getApiBaseUrl()`: `new URL()` parse, https-only, numista-backend/scan-service hosts only (with `<tag>---` prefix support), anchored regex; self-test assertions (a1–a3 accept, r1–r5 reject) |
| `numista_mobile/web/scraper_dashboard.html` | 522–568, 925–968 | Identical security fix; LIVE_URL = scan-service; self-test assertions |
| `numista_backend/main.py` | 261–276 | CORS outermost: `add_middleware(CORSMiddleware)` moved to after all other middlewares so it wraps everything (auth errors now carry CORS headers) |
| `numista_backend/main.py` | 7103–7110, 7178–7212, 9526–9533 | Import ownership: email/uid mismatch → 403 on `/api/import/start`, `/api/import/process`, `/api/import/littleton_sync`; existing upload + status checks verified |
| `numista_mobile/lib/services/market_news_service.dart` | 1–5, 62–67 | Bare `http.get` → `HttpAuthClient.get`; removed unused `package:http/http.dart` import |
| `numista_backend/tests/test_cors_auth.py` | 1–77 | New: 401 carries CORS headers; `/api/import/process`, `/api/import/start`, `/api/import/littleton_sync` return 403 on email mismatch |

## Security Fix Detail (?api= override)
- `new URL(apiParam)` throws on invalid URLs (caught, falls through to live)
- `u.protocol !== 'https:'` → reject
- `ALLOWED_HOST_RE = /^((?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-[a-z0-9]+\.(?:us-central1|[a-z0-9-]+)\.run\.app)$/` — must match exactly
- `return u.origin` — strips any path/query that might have been appended
- localhost/127.0.0.1 → `''` (relative paths, for local dev)
- 7 inline self-tests per file (3 accept, 5 reject) run silently in browser

## GEMINI38 Review
- `BATONS\GEMINI38_REVIEW_P7_V8_16_BUILD.md` — Verdict: **PASS**
- Rule 9.3 satisfied (>2 files → review filed)

## EXECUTE_DONE
- `BATONS\EXECUTE_DONE_P7_V8_16.md` ✅

Note: Eric's 8:30 PM stop applies tonight. Build finished at 7:36 PM ET — within window.
Handing baton. Ready for Grok CoS score + p7gate redeploy from 7c5179cd.
OVER
