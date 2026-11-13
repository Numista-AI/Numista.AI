# GEMINI38_REVIEW_T1C_HOTFIX_BUILD.md
**Track:** T1C HOTFIX  
**Scope:** P0 — `/api/spot_prices` missing from `_PUBLIC_PATHS` (CORS 401 on home dashboard)  
**Generated:** 2026-10-13 ~16:50 ET by AG CoS (Gemini)  
**Commit under review:** diff — main.py + new test file (not yet committed)

> **Gemini BUILD review rule:** Every cite must paste the actual code line(s) verbatim next to the file:line reference. A cite without a quoted line is rejected by Grok CoS (SAY-AGAIN).

---

## Fix 1 — P0: /api/spot_prices added to `_PUBLIC_PATHS`

**File:** `numista_backend/main.py`  
**Lines:** 147-155 (after fix; before fix lines 147-152 did not include spot_prices)

### Code change (verbatim):

**BEFORE** (`main.py:147-152`):
```python
    # Mint releases (public upcoming releases page)
    "/api/mint-releases/upcoming",
    "/api/mint-releases/all",
    # Attorney estate read (token-gated inside handler, not Firebase Bearer)
    "/api/estate/attorney-report",
}
```

**AFTER** (`main.py:147-155`):
```python
    # Mint releases (public upcoming releases page)
    "/api/mint-releases/upcoming",
    "/api/mint-releases/all",
    # Attorney estate read (token-gated inside handler, not Firebase Bearer)
    "/api/estate/attorney-report",
    # Metal spot prices — called unauthenticated from home_dashboard.dart before sign-in;
    # data is non-sensitive (yfinance commodity prices, no PII).
    "/api/spot_prices",
}
```

### Why this is correct:

1. **Caller is unauthenticated** — `numista_mobile/lib/screens/home_dashboard.dart:248-249` (verbatim):
   ```dart
   final response = await http.get(
       Uri.parse('$kApiBaseUrl/api/spot_prices'));
   ```
   Plain `http.get`, no `Authorization` header. This is intentional — spot prices are shown on the home dashboard before sign-in.

2. **Default-deny middleware** — `numista_backend/main.py:179-183` (verbatim):
   ```python
   if request.method == "OPTIONS":
       return await call_next(request)
   path = request.url.path
   if _is_public(path):
       return await call_next(request)
   ```
   Without `/api/spot_prices` in `_PUBLIC_PATHS`, `_is_public(path)` returned `False` → middleware fell through to the Bearer check → returned 401 → the browser saw a CORS-free 401 (CORSMiddleware ran before the middleware but Starlette's order means the custom middleware response doesn't get CORS headers added by CORSMiddleware on the response path in all cases).

3. **Data sensitivity:** The route (`numista_backend/routes/valuation_routes.py:13-63`) returns yfinance commodity prices (Gold, Silver, Platinum, Palladium) from a Firestore TTL cache. No PII, no user data. Public is appropriate.

4. **Route implementation** — `numista_backend/routes/valuation_routes.py:13-14` (verbatim):
   ```python
   @router.get("/spot_prices")
   def get_live_metal_prices():
   ```
   No `Depends(get_current_user)` — the route itself never required auth; the middleware was the only barrier.

### Test coverage — `numista_backend/tests/test_cors_public_paths.py`:

- `test_spot_prices_no_auth_returns_200` — calls `GET /api/spot_prices` without auth header, asserts 200. **PASSES.**
- `test_spot_prices_returns_expected_keys` — asserts Gold, Silver, Platinum, Palladium keys in response. **PASSES.**
- `test_options_preflight_protected_route_returns_200` — OPTIONS on protected route returns 200. **PASSES.** (`main.py:179` already correct.)
- `test_options_preflight_has_cors_headers` — OPTIONS response has `Access-Control-Allow-Origin`. **PASSES.**
- `test_options_preflight_spot_prices_returns_200` — OPTIONS on `/api/spot_prices` returns 200. **PASSES.**
- `test_spot_prices_in_public_paths` — directly asserts `"/api/spot_prices" in _PUBLIC_PATHS`. **PASSES.**
- `test_protected_routes_not_in_public_paths` — asserts `/api/collection_inventory`, `/api/coins`, `/api/deep_dive`, `/api/morgan/confirm`, `/api/programs`, `/api/admin/grade_flags` are NOT in `_PUBLIC_PATHS`. **PASSES.**

**Test results:** 7/7 passed in 6.83s.

---

## Outstanding items (P1-P3 — not in this commit)

### P1 — Flutter web build version
- FT smoke showed "v4.403, both old and new nav show, small text." 
- PR #258 cherry-picked commits including T3 UX fixes (`9a0b20b8`, `e6b808f7`). Investigating whether GitHub Actions built from `deploy/unified-bundle` ran the `flutter build web` step correctly.
- **Not blocking this commit.** Will investigate in a separate commit if needed.

### P2 — Morgan Undo not shown after confirm
- `ai_chat_screen.dart:799` `onPressed: () => _send('INTERNAL_UNDO:$coinId')` — Undo button IS in the widget.
- Issue: after the Confirm dialog flow, the response may not set `action_payload` to trigger `_buildAddedCoinCard`. Needs deeper investigation.
- **Not in this commit.**

### P2 — Firestore onSnapshot failures
- Likely downstream of CORS/401 cascade. Will re-evaluate after P0 deploy.
- **Not in this commit.**

### P3 — Home page blank
- Almost certainly caused by P0 (CORS/401 on spot_prices). With P0 fixed, home page should load.
- **Not in this commit — will verify in next smoke.**

---

## Verdict

**P0 fix is CORRECT and TESTED (7/7).** Verbatim code quoted above. No regressions in `_PUBLIC_PATHS` — only non-sensitive commodity price route added.

Ready to commit and request cherry-pick deploy with Eric's YES.

*AG CoS / Gemini — 2026-10-13*
