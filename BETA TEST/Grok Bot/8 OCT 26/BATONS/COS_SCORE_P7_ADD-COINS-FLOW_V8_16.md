# COS SCORE - P7 ADD-COINS-FLOW V8.16 BUILD
Scorer: Grok CoS (evening watch) | 2026-10-18 19:45 ET | Reviewed: code `7c5179cd` on origin/p7-v8.9 (parent 99773ac4) + EXECUTE_DONE_P7_V8_16.md + GEMINI38_REVIEW_P7_V8_16_BUILD.md + NET-324/NET-325 + independent read of `git diff 99773ac4 7c5179cd` in worktree `C:\Users\ericd\AppData\Local\Temp\p7v89_build` (5 files, +305/-31). Allowlist regex re-tested by the watch in node (results below). Tests not re-run by the watch (AG reports 581/581 flutter, 571 pytest, analyze clean).
Verdict: **PASS (code) WITH 1 SECURITY MUST-FIX + 1 SHOULD-FIX -> V8.17 (2 files, Rule 9.3: no GEMINI38 review).** Dev only. No deploys.

| # | Item (NET-315 / NET-314 GROKCOS) | Score | Independent check (7c5179cd) |
|---|---|---|---|
| 1 | `?api=` override: new URL(), https only, our hosts only, return u.origin, anchored regexes, accept/reject tests | **PARTIAL -> MUST-FIX** | new URL(), https check, u.origin and anchored PREVIEW_ORIGIN_RE are correct. But ALLOWED_HOST_RE is not pinned to OUR project. See below. |
| 2 | localhost/127.0.0.1 -> '' | **PASS** | add_coins.html and scraper_dashboard.html both return '' for http://localhost[:port] and http://127.0.0.1[:port]. |
| 3 | CORS outermost | **PASS** | add_middleware(CORSMiddleware) removed at :72 and re-added at :261-276 after both @app.middleware("http") functions, so it wraps auth + observability. Tests assert 401 carries ACAO for numista-vault.web.app and numista-vault--p7gate.web.app. |
| 4 | Import ownership on /api/import/* (403 on mismatch) + tests | **PASS** | start, process, littleton_sync now Depends(get_current_user) and 403 when body user_email != token email/uid (admin and ALLOW_UNAUTHENTICATED dev_guest exempt). upload + status already checked. 3 mismatch tests present. |
| 5 | market_news_service.dart -> HttpAuthClient | **PASS** | Bare http.get replaced, unused http import removed. |
| 6 | One GEMINI38 review | **PASS** | Filed once for V8.16. |

## MUST-FIX (security, V8.17, before the p7-gate preview is shared)
ALLOWED_HOST_RE = `^((?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-[a-z0-9]+\.(?:us-central1|[a-z0-9-]+)\.run\.app)$`
- `[a-z0-9]+` accepts ANY project number and `[a-z0-9-]+` accepts ANY region. Anyone can create a Cloud Run service named `numista-backend` in their own project and get `numista-backend-<their-project-number>.us-central1.run.app`, which this regex ACCEPTS (watch test: `numista-backend-123456789012.us-central1.run.app` -> true; `numista-scan-service-999.europe-west1.run.app` -> true). A crafted preview link would still send the signed-in user's Firebase Bearer token to a stranger. Same hole as the V8.15 must-fix, just one level down.
- It also REJECTS our real `.a.run.app` form (`numista-backend-qntvrqvxma-uc.a.run.app` and `p7gate---numista-backend-qntvrqvxma-uc.a.run.app` -> false), because `[a-z0-9]+` cannot include the `-uc` part.
Fix: pin to our project only, e.g.
`^(?:[a-z0-9-]+---)?numista-(?:backend|scan-service)-(?:568985927038\.us-central1\.run\.app|qntvrqvxma-uc\.a\.run\.app)$`
Add rejects: `numista-backend-123456789012.us-central1.run.app`, `numista-backend-568985927038.europe-west1.run.app`, `numista-backend-attackerxyz-uc.a.run.app`. Add accepts: `p7gate---numista-backend-568985927038.us-central1.run.app`, `p7gate---numista-backend-qntvrqvxma-uc.a.run.app`, `numista-scan-service-568985927038.us-central1.run.app`.

## SHOULD-FIX (V8.17)
- The self-tests check a COPY of the logic (mockOrigin), not getApiBaseUrl() itself, so they can drift and would not have caught a typo in the real function. Make one pure function `resolveApiBase(origin, search, liveUrl)` that getApiBaseUrl() calls, and run the asserts against that same function. Keep it in both HTML files.

## Notes (no action now)
- Starlette ServerErrorMiddleware still sits outside CORS, so an unhandled 500 will not carry CORS headers. Handled HTTPException 4xx/5xx do. Fine for P7; log for later.
- Confirm ALLOW_UNAUTHENTICATED is not "1" on the live and p7gate backends before the gate (dev_guest bypass).

## Gates / Next
- Baton -> **AGCOS_OVER** for V8.17 (2 files: add_coins.html, scraper_dashboard.html). Rule 9.3: no GEMINI38 review. Explicit-path commits on p7-v8.9. No deploys, no main.
- Eric's 8:30 PM ET stop tonight applies. If V8.17 can't finish by then, stand down and resume in the morning.
- Then Grok CoS builds the ONE p7-gate preview + p7gate tagged backend/scan_service from the V8.17 tip (main.py is unchanged from V8.16), then UX Designer + Field Tester re-gate.
- No ERIC baton. No live deploy YES pending. Live deploy later = cherry-pick approved commits onto a branch from main, only on Eric's typed YES.
