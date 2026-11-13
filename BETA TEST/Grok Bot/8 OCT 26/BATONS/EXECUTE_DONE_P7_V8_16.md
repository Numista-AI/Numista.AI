# EXECUTE_DONE — P7 V8.16

**Build Version**: P7 V8.16  
**Commit SHA**: `7c5179cd87f425f3581af99f280f90979d0a47d2`  
**Branch**: `p7-v8.9` (pushed to `origin/p7-v8.9`)  
**Base Commit**: `99773ac4`  
**Date**: 2026-10-18  

---

## 1. Summary of Changes & File:Line Mappings

| File | Lines Changed | Description |
|---|---|---|
| `numista_mobile/web/add_coins.html` | 527–573, 1175–1218 | Hardened `getApiBaseUrl()`, strict preview origin check, Cloud Run hostname regex, added inline browser self-test assertions. |
| `numista_mobile/web/scraper_dashboard.html` | 522–568, 925–968 | Hardened `getApiBaseUrl()` with `numista-scan-service` live default, strict preview origin check, added inline browser self-test assertions. |
| `numista_backend/main.py` | 72–79 (removed), 261–276 (added), 7103–7110, 7178–7212, 9526–9533 | Moved `CORSMiddleware` outermost (after auth/observability middlewares); added ownership mismatch checks to `/api/import/start`, `/api/import/process`, `/api/import/littleton_sync`. |
| `numista_mobile/lib/services/market_news_service.dart` | 1–5 (import cleanup), 62–67 | Replaced bare `http.get` with `HttpAuthClient.get`; removed unused `package:http/http.dart`. |
| `numista_backend/tests/test_cors_auth.py` | 1–77 | Regression tests for 401 carrying CORS headers, preview origin regex matching, and import email mismatch returning 403. |

---

## 2. Security Fix Details (`?api=` Override)

### Accept/Reject Test Cases Enforced in `add_coins.html` and `scraper_dashboard.html`:
- **a1**: Preview origin with no `?api=` query parameter $\rightarrow$ returns default `LIVE_URL`.
- **a2**: Preview origin with valid `?api=` override for an authorized `p7gate---numista-backend-*.run.app` service $\rightarrow$ accepted and origin returned.
- **a3**: Local development host (`localhost:8080`) $\rightarrow$ returns empty string for relative paths.
- **r1**: Production origin (`https://numista.ai`) with valid `?api=` $\rightarrow$ rejected, returns `LIVE_URL`.
- **r2**: Preview origin with evil subdomain path `https://evil.example/x.run.app` $\rightarrow$ rejected, returns `LIVE_URL`.
- **r3**: Preview origin with foreign run.app hostname `https://attacker.run.app` $\rightarrow$ rejected, returns `LIVE_URL`.
- **r4**: Preview origin with insecure protocol `http://...run.app` $\rightarrow$ rejected, returns `LIVE_URL`.
- **r5**: Production Firebase Hosting domain without preview prefix (`https://numista-vault.web.app`) $\rightarrow$ rejected, returns `LIVE_URL`.

---

## 3. CORS Fix Details

- **Before**: `CORSMiddleware` was registered at `numista_backend/main.py:72-79`, BEFORE the default-deny auth middleware (`line 190`) and observability middleware (`line 236`). In Starlette's reversed middleware stack, `default_deny_auth_middleware` executed outside of `CORSMiddleware`, returning 401 JSONResponses without CORS headers.
- **After**: `CORSMiddleware` moved to `numista_backend/main.py:261-276`, AFTER all `@app.middleware("http")` calls. In Starlette's stack, it becomes the outermost layer, executing first on ingress and last on egress, ensuring every response (including unauthenticated 401s) carries `Access-Control-Allow-Origin`.

---

## 4. Import Route Ownership Verification

All `/api/import/*` routes now enforce strict ownership by verifying the Firebase caller token against the request body/parameter:
- `POST /api/import/upload`: `numista_backend/main.py:7003-7008` (verified intact)
- `POST /api/import/start`: `numista_backend/main.py:7103-7110` (added `_user: dict = Depends(get_current_user)` and mismatch 403)
- `GET /api/import/status/{session_id}`: `numista_backend/main.py:7153-7158` (verified intact)
- `POST /api/import/process`: `numista_backend/main.py:7192-7204` (added `_user: dict = Depends(get_current_user)`, mismatch 403, and allowed `import_id` or `session_id` via Pydantic validator)
- `POST /api/import/littleton_sync`: `numista_backend/main.py:9526-9533` (added mismatch 403 comparing caller token against `payload.user_email`)

---

## 5. Test Results

### Flutter Analyze
```
flutter analyze lib/
Analyzing lib...
No issues found! (ran in 12.7s)
Result: 0 errors, 0 warnings
```

### Flutter Unit / Integration Tests
```
flutter test --reporter compact
00:38 +581: All tests passed!
Result: 581 passed (baseline 581)
```

### Pytest Backend Test Suite
```
pytest numista_backend/tests/ -q
571 passed, 250 warnings in 22.32s
Result: 571 passed (100% pass rate)
```

---

## 6. GEMINI 3.8 Review Verdict

**Verdict**: **PASS**  
Review document saved at:
`C:\Users\ericd\Documents\MyVertexProject\BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_16_BUILD.md`
