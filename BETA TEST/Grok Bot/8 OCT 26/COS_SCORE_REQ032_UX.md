# COS SCORE - T3 REQ_032 UX
Scored by: Grok CoS, 12 Oct 2026 ~12:50 PM ET. Code checked: dev HEAD 67ea1040 (docs-only on top of e5f5760c).
PASS = build on dev only. No deploy, no live data writes, no sync_canon without Eric's typed YES.

## Verdict: PASS (conditional)

### Required fixes before code
1. Replace every guessed path ("likely", "or equivalent", "identify") with real numista_mobile\lib paths you opened, with line numbers. Post the corrected file table in a short PLAN_V1.1 note beside this file, then build.
2. Menu count: plan says 25, Gemini counted 29. Commit a list of every current menu item with file:line; the regression test must cover all of them.
3. Fix 1 deferral accepted (blocked on REQ_034/036).
4. Font sizes via the central theme file; don't hand-edit each widget.
5. PIN: keep the backend 5-guess lockout untouched.
6. Coordinate ai_chat_screen.dart with T2.

Ball: AG CoS: build on dev (fold in fixes).
