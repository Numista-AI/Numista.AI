# ACK NET-041 — AG CoS

**ACK'd:** 2026-10-13 ~16:55 ET

## T1C P0 PASS — acknowledged

- Score PASS noted. Cherry-pick `d689223f` (`main.py` + `tests/test_cors_public_paths.py`) is ready to deploy.
- Systemic follow-up (middleware 401 lacking CORS headers) noted — will audit unauthenticated Flutter calls vs `_PUBLIC_PATHS`. Options: (a) add CORS headers to the middleware 401 response, (b) audit all plain `http.get/post` in Flutter for missing paths.
- P1 Flutter web build investigation, P2 Morgan Undo, P2 onSnapshot — continuing.

## Next action
Raising deploy request to Eric for typed YES. Baton → CLOSED_OUT pending deploy.

AG CoS OVER
