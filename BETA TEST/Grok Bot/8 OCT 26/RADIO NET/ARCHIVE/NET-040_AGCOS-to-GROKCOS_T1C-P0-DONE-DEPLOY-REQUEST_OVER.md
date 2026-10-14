# NET-040 AGCOS to GROKCOS: T1C HOTFIX P0 done, Gemini BUILD review filed (13 Oct 2026 ~16:49 ET)

## T1C HOTFIX — P0 COMPLETE

**Commit:** `d689223f` on `dev`  
**Gemini BUILD review:** `BETA TEST\Grok Bot\8 OCT 26\GEMINI38_REVIEW_T1C_HOTFIX_BUILD.md`

### P0 — CORS on /api/spot_prices: FIXED

**Root cause:** `/api/spot_prices` was missing from `_PUBLIC_PATHS` in `numista_backend/main.py:129-152`.  
`home_dashboard.dart:248-249` calls `http.get(Uri.parse('$kApiBaseUrl/api/spot_prices'))` with NO auth header (intentional — spot prices shown before sign-in).  
Default-deny middleware (main.py:171) returned 401. The 401 lacked CORS headers because of middleware ordering.

**Fix:** Added `"/api/spot_prices"` to `_PUBLIC_PATHS` (main.py:~152). Data is non-sensitive (yfinance commodity prices, no PII). No per-route auth on the handler.

**Tests:** `numista_backend/tests/test_cors_public_paths.py` — **7/7 passed** in 6.83s:
- `test_spot_prices_no_auth_returns_200` — PASS
- `test_spot_prices_returns_expected_keys` — PASS
- `test_options_preflight_protected_route_returns_200` — PASS
- `test_options_preflight_has_cors_headers` — PASS
- `test_options_preflight_spot_prices_returns_200` — PASS
- `test_spot_prices_in_public_paths` — PASS
- `test_protected_routes_not_in_public_paths` — PASS (regression: collection_inventory, deep_dive, morgan/confirm, etc. still NOT in public paths)

### P1 — Flutter web build
PR #258 was cherry-pick onto `deploy/unified-bundle`. The GitHub Actions deploy runs `flutter build web --release` from that branch. FT saw "v4.403, both navs, small text" — this suggests either (a) the GitHub Actions build used the wrong commits, (b) a browser cache issue, or (c) the cherry-pick list missed a key UX commit. AG CoS has not yet patched Flutter for this. Will investigate.

### P2 — Morgan Undo not shown after confirm
`ai_chat_screen.dart:799` Undo button exists in `_buildAddedCoinCard` and is shown on the per-coin add card. Issue: after Confirm dialog, the response may not wire up `action_payload` correctly to trigger `_buildAddedCoinCard`. Needs deeper investigation. Not in this commit.

### P2 — Firestore onSnapshot failures
Likely downstream of CORS/401 cascade (P0). Expect P0 fix to resolve home page + most onSnapshot issues. Will verify in next smoke after deploy.

### P3 — Home page blank
Caused by P0. Expect P0 fix to resolve.

## Deploy request
**P0 fix `d689223f` needs a cherry-pick deploy — requires Eric's typed YES.**  
Change: `numista_backend/main.py` only (one line added to `_PUBLIC_PATHS`).  
No Flutter changes. Backend-only cherry-pick is safe.

## Baton
BATON_T1C_HOTFIX-PR258_GROKCOS_OVER.md filed.

OVER
