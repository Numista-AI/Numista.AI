# EXECUTE_DONE_REQ031B_V2.md
**Author:** Antigravity CoS (Gemini)  
**Date:** 2026-10-13  
**Commit:** `39125bac`  
**Track:** T1B V2 — REQ_031B Default-Deny Auth V2 + P0 Remediation  
**Status:** COMPLETE (Dev-only, ready for Grok CoS build scoring)

---

## 1. Summary of Deliverables & Fixes

Addressing all findings in `COS_SCORE_REQ031B_BUILD.md` and radio message `NET-022`:

| # | Item | Remediation | Verification |
|---|------|-------------|--------------|
| 1 | Middleware JWT validation | Middleware now calls `verify_firebase_bearer_token(request)` and caches decoded token in `request.state.user`. Rejects empty, missing, or garbage tokens with 401. Reused in `get_current_user`. | Walk test asserts 401 on missing & garbage token across all routes |
| 2 | Admin claim on sensitive routes | Added `_admin: dict = Depends(require_admin_user)` across 24 endpoints: Brain admin (7), cron routes (6), config routes (3), scraper (1), Greysheet batch/config (4), portfolio snapshot (1), ingestion batch async (1), normalize backfill (1). | Unit tests verify non-admin blocked with 403; admin allowed |
| 3 | IDOR checks | Added owner UID/email vs caller token checks: `subaccount_routes.py` checks `req.parent_email == caller_email` or admin; `estate_routes.py` checks `req.owner_uid in (caller_uid, caller_email)` or admin. | Unit tests in `test_default_deny_auth.py` verify 403 on IDOR mismatch |
| 4 | Acceptance test route walk | Added automated walk of `app.routes`: (a) asserts 401 with no token on non-public routes; (b) asserts 401 with garbage Bearer token on non-public routes; (c) inspects route dependency tree to verify every route is either protected with `get_current_user`/`require_admin_user` or explicitly cataloged in `REVIEWED_NON_GUARDED_ROUTES`. | `pytest numista_backend/tests/test_default_deny_auth.py` 20/20 PASS |
| 5 | `deep_dive` 500→401 fix | Added `except HTTPException: raise` before `except Exception:` in `main.py:3407` (`deep_dive`), matching earlier fix in `identify_group_photo` (:5622) and `estate_routes.py` (:51, :133). | Route raises 401 cleanly instead of swallowing into 500 |
| 6 | Public allowlist cleanup | Removed dead `/create-checkout-session` from `_PUBLIC_PATHS`; tightened `/api/coin_search` prefix matching to `/api/coin_search/`. | Allowlist is minimal, accurate, and secure |
| 7 | Full test suite passing | All tests across backend pass with zero regressions. | `pytest numista_backend/tests/` **494 passed, 0 failed**; Flutter analyze **clean** (0 issues) |

---

## 2. Test Execution Evidence

### Backend Pytest Suite
```
pytest numista_backend/tests/test_default_deny_auth.py
============================== 20 passed in 6.38s ==============================

pytest numista_backend/tests/
======================== 494 passed, 3 warnings in 13.64s ========================
```

### Static Analysis
```
flutter analyze lib/
Analyzing lib/...
No issues found! (ran in 10.8s)
```

---

## 3. Deployment Constraint Notice
- Changes committed exclusively to `dev` branch (`39125bac`).
- NO deploy to production without Eric's explicit typed YES.
