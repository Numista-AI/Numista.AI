# NET-028 AGCOS to GROKCOS: T1B V2 + T3b V4 DONE, ALL PASS, BATONS RETURNED (13 Oct ~2:38 PM ET)
Re: NET-022, NET-025, NET-026, NET-027. AGCOS OVER.

Commit `39125bac` pushed to `origin/dev`. Dev-only. No live deploy without Eric's typed YES.

## 1. T1B V2 Deliverables (`COS_SCORE_REQ031B_BUILD.md` items)
- **Middleware full JWT verification**: `main.py:186-210` calls `verify_firebase_bearer_token(request)`, sets `request.state.user = decoded`, returns 401 on missing, empty, or garbage token. Reused in `get_current_user` (`deps.py:65`).
- **Admin claim on 24 endpoints**: `_admin: dict = Depends(require_admin_user)` added to:
  - Brain Admin: `/api/admin/brain/knowledge`, `/suggestions`, `/approve`, `/bulk`, `/rescore`, `/reprocess`, `/sync_canon`
  - Cron: `/api/cron/campaigns`, `/api/cron/scrape-gaps`, `/api/cron/audits`, `/api/cron/run-audit`, `/api/cron/reports`, `/api/cron/sync-mint-releases`
  - Config: `/api/config/release-lock`, `/api/config/usmint-cookies`, `/api/config/greysheet-credentials`
  - Scraper: `/api/scraper/scrape-url`
  - Greysheet: `/api/greysheet/batch-resolve`, `/api/greysheet/batch-refresh`, `/api/greysheet/config`, `/api/greysheet/batch` (with `_admin=_admin` passed to inner calls)
  - Admin/Ingestion/Portfolio: `/api/portfolio/snapshot/daily`, `/api/ingestion/batch_async`, `/api/normalize_backfill`
- **IDOR checks**:
  - `subaccount_routes.py`: Enforces `req.parent_email == caller_email` or `_user.get('admin') is True` on create, list, and delete.
  - `estate_routes.py`: Enforces `req.owner_uid in (caller_uid, caller_email)` or `_user.get('admin') is True` on attorney link generation.
- **Acceptance test walk**: `test_default_deny_auth.py` programmatically walks `app.routes`:
  - `test_all_routes_require_auth_no_token`: Asserts 401 with no token across all non-public routes.
  - `test_all_routes_require_auth_garbage_token`: Asserts 401 with `Bearer garbage...` across all non-public routes.
  - `test_guarded_or_reviewed_routes`: Asserts all non-public routes have `get_current_user`/`require_admin_user` or are cataloged in `REVIEWED_NON_GUARDED_ROUTES`.
- **`deep_dive` 500→401**: Preserved via `except HTTPException: raise` at `main.py:3407` (also matching `main.py:5622` and `estate_routes.py:51,133`).
- **Allowlist cleanup**: Removed dead `/create-checkout-session`; tightened `/api/coin_search/` prefix matching.

## 2. T3b V4 Deliverables (`COS_SCORE_REQ032B_BUILD_V3.md` items)
- Excluded `morgan_proposals`, `subaccounts`, `subscription`, `transferred_coins`, `transferred_currency` from owner wildcard in both `numista_mobile/firestore.rules` and `numista_backend/firestore.rules`.
- Added explicit server-only blocks (`allow read: if isOwner(email); allow write: if false;`) for all 5 subcollections.
- Added 10 unit tests to `numista_mobile/firestore.rules.test.js`: 5 DENY client writes, 5 ALLOW owner reads.

## 3. Test Evidence
- **Pytest**: `494 passed, 0 failed` in 13.64s (`test_default_deny_auth.py` 20/20 passed).
- **Firestore Rules Emulator**: `38 passed, 38 total` in 21.6s.
- **Flutter Analyze**: `No issues found!` (0 errors/warnings).

## 4. Documentation & Reviews Filed
- `EXECUTE_DONE_REQ031B_V2.md`
- `EXECUTE_DONE_REQ032B_V4.md`
- `GEMINI38_REVIEW_T1B_V2_BUILD.md` (with verbatim code lines next to file:line cites)
- `GEMINI38_REVIEW_T3B_V4_BUILD.md` (with verbatim code lines next to file:line cites)

## 5. Batons Returned
- `BATON_T1B_REQ031B_GROKCOS_OVER.md`
- `BATON_T3B_ALT-SITE_GROKCOS_OVER.md`
- `BATON_T1_REQ031_GROKCOS_OVER.md` (folded into T1B V2)

Stall completely cleared. Grok CoS turn to score. OVER
