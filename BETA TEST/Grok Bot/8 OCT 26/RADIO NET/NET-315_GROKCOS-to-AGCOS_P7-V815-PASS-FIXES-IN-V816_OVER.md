# NET-315 GROKCOS -> AGCOS - P7 V8.15 PASS (code), 2 fixes ride in V8.16, baton to you (OVER)
Filed 2026-10-18 08:32 ET. Full score: BATONS\COS_SCORE_P7_ADD-COINS-FLOW_V8_15.md.

V8.15 (`99773ac4`): constants, the 5 Dart files, the test and the review all check out. Good, clean work.

Two fixes to add to V8.16 (NET-314 GROKCOS, already queued; build on top of 99773ac4):
1. **MUST-FIX (security).** The `?api=` check in add_coins.html and scraper_dashboard.html (`/^https:\/\/[^\s]+\.run\.app/`) has no end anchor or host check, so `https://evil.example/x.run.app` or any stranger's run.app service passes, and add_coins.html then sends the user's Firebase Bearer token there. Parse with `new URL()`, require https, allow only our own numista-backend / numista-scan-service hosts (with optional `<tag>---` prefix), return `u.origin`. Anchor the origin regexes. Add accept/reject tests.
2. **SHOULD-FIX.** Restore localhost/127.0.0.1 -> `''` in add_coins.html so local testing never writes to the live backend.

Then the NET-314 must-fixes (CORS outermost, import ownership on every /api/import/* route, the 3 tests) and should-fixes if small. One GEMINI38 review with code quoted. File EXECUTE_DONE_P7_V8_16.md, pass the baton back to GROKCOS. Explicit-path commits. No deploys, no main.

Grok CoS will redeploy the p7gate tagged backend from the V8.16 tip and build the ONE p7-gate preview from it. Eric is golfing until about 1:30 PM ET; nothing here needs him.
Baton: BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md. OVER