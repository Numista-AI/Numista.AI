# NET-314 GROKCOS -> AGCOS: V8.16 (queued right after V8.15). P7 MUST-FIX before any merge.
Source: Code Reviewer audit `1 NUMISTA.AI\BETA TEST\Grok Bot\18 OCT 26\CR_UNAUTHED_CLIENT_CALLS_AUDIT.md` (origin/main 3c1bacf5). Read it first.

Finish V8.15 (NET-312) first and file it. Then build V8.16 on the same branch (p7-v8.9, on top of V8.15). Dev only. No deploys. No main.

## Must-fix (P7 blocks on these)
1. **CORS outermost.** Today the CORS middleware sits inside the auth check, so a 401 goes out with no CORS headers and the browser shows "Failed to fetch". That's the root cause of Eric's error. Make CORS the outermost middleware so every response, including 401/403/500, carries the CORS headers. While you're in there, give the `@app.options("/api/import/upload")` handler proper Access-Control headers or drop it if middleware covers it.
2. **Import ownership.** The import routes trust the `user_email` in the request. Every import route (upload, process, status, and any other /api/import/*) must take the user from the verified Firebase token and reject a mismatch with a 403. f48 only does this on upload, and process (f48 main.py ~7168) still needs it.
3. **Tests.** (a) A 401 response carries Access-Control-Allow-Origin for an allowed origin. (b) Each import route returns 403 when the body's email doesn't match the token. (c) The existing upload/process/status happy path still passes.

## Should-fix (include if small; otherwise list as P7.1)
4. `numista_mobile/lib/services/market_news_service.dart:49-50` GET /api/news/feed uses plain http and fails silently, showing stale news. Switch it to the authenticated client (HttpAuthClient).
5. A shared `authFetch` helper for web/*.html pages, used in add_coins.html.

## Do NOT do in V8.16 (logged as a later ticket)
- scraper_dashboard.html (10 admin calls). That needs authFetch plus an admin sign-in design, so it's a separate ticket after P7.
- A CI guard against raw fetch/http: propose it in the DONE file, don't build it.

One GEMINI38 review (more than 2 files). File EXECUTE_DONE_P7_V8_16.md plus the review, and pass the baton to GROKCOS. Commit explicit paths only.
OVER
