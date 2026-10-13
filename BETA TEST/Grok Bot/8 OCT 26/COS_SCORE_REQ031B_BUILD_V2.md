# COS SCORE - T1B REQ_031B DEFAULT-DENY AUTH BUILD V2 (commit 39125bac on dev)
Scored by: Grok CoS, 13 Oct 2026 ~2:45 PM ET. Read real code at HEAD after 39125bac: main.py middleware + allowlist, routes/deps.py, subaccount_routes.py, estate_routes.py, tests/test_default_deny_auth.py. Cross-checked GEMINI38_REVIEW_T1B_V2_BUILD.md quotes against file lines (line numbers in the review drift; code content matches). Ran pytest myself. Emulator covered under T3b V4 score.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed. No live writes.

## Verdict: PASS on dev. All 6 items from COS_SCORE_REQ031B_BUILD.md are fixed. Middleware now full-verifies the Firebase Bearer token; garbage tokens get 401 before routing.

## Tests (run by Grok CoS)
- pytest `numista_backend\.venv\Scripts\pytest.exe tests -q`: **494 passed, 0 failed** (14.42s). Matches EXECUTE_DONE.
- `test_default_deny_auth.py`: **20 passed** (6.83s), including app.routes walk with no token and with `Bearer garbage_invalid_token_12345`.
- Emulator: see T3b V4 score (38/38 on my run).

## Fixed and checked in code
1. **P0 middleware JWT verify.** main.py:171-209 `default_deny_auth_middleware`: after OPTIONS + `_is_public`, calls `verify_firebase_bearer_token(request)` (deps.py:65-76 -> `firebase_auth.verify_id_token`), caches `request.state.user`, else 401. Structural-only `if token: return await call_next` branch is gone. deps.py:78-81 `get_current_user` reuses `request.state.user`.
2. **Admin claim on sensitive routes.** 29 `Depends(require_admin_user)` hits in main.py including brain (9860-10001), cron (9524-9806), config/cookies/greysheet (9754, 9823, 10760), scraper (9843), greysheet batch/resolve/refresh/config (10778-11029), portfolio snapshot (10658), ingestion batch (11251), normalize_backfill (1417), plus prior P0 dedup (3786, 3902). `require_admin_user` uses `user.get("admin") is not True` (deps.py:104-106).
3. **IDOR.** subaccount_routes.py create/list/delete: 403 unless `parent_email` matches caller email or admin is True. estate_routes.py: generate_attorney_link 403 unless `owner_uid` matches uid/user_id/email or admin.
4. **Acceptance walk.** test_default_deny_auth.py:91-147 walks `app.routes` for no-token and garbage-token 401; :209+ requires get_current_user/require_admin_user or an entry in `REVIEWED_NON_GUARDED_ROUTES` (handler-auth catalog).
5. **deep_dive 401 preserved.** main.py:3407-3408 `except HTTPException: raise` before the 500 catch. Same pattern at identify_group_photo and estate_routes.
6. **Allowlist.** `_PUBLIC_PATHS` no longer contains `/create-checkout-session`. Prefix list uses `/api/coin_search/` (main.py:165). Exact `/api/coin_search` remains for the open Vertex search GET.

## Gemini BUILD review
GEMINI38_REVIEW_T1B_V2_BUILD.md has verbatim quotes that match the code; some cited line numbers are stale vs current main.py (e.g. brain routes ~9860 not ~9459). Content check passed.

## Report-only (pre-deploy gate, unchanged)
- Eric's Firebase `admin: true` custom claim is still **not confirmed** in this score. Confirm read-only before YES, or admin routes 403 in prod (deps.py:104-106).

## Follow-ups (ticket, not blockers for this PASS)
- main.py:187-188 `if app.dependency_overrides:` test bypass: also require a test-only env flag.
- T3 F1-F2 (FreeScanPreviewScreen fonts <14 + email->PIN widget test) were ordered folded into this commit and **were not**. Reopened on T3 baton.
- Backend `firestore.rules` mirror still drifts from mobile (missing `coins`/`profile` exclusions). Deployed file is mobile only; re-sync mirror.

## Bundle
T1B PASS + T3b PASS + T2 already PASS. Hold Eric's one YES until T3 F1-F2 land (or Eric explicitly ships without them). Confirm admin claim before deploy.

Ball: AG CoS for T3 F1-F2 only. T1B baton -> CLOSED after this rename path (see NET-029). No deploy.
