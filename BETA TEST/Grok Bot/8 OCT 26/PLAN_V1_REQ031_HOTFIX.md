# PLAN V1 — REQ_031: API Auth Lockdown Hotfix
Prepared by: Antigravity CoS  
Date: 2026-10-12  
Model assigned: Claude Opus 4.6 (Thinking)  
Status: PLAN ONLY — awaiting Gemini review, then Grok CoS score, then founder Proceed + YES to deploy.  
Source inventory: `BETA TEST\Grok Bot\8 OCT 26\ROUTE_INVENTORY_031.csv`  
Code baseline: branch `dev`, commit `e5f5760c`

---

## 1. Problem Summary

Eleven live routes derive the acting user from a body/form field (`user_email`, `uid`) rather than from the Firebase ID token. An attacker with a valid token can write to another user's collection by setting the body email to any target. One route (`/api/v1/rag/query`) has no authentication at all and calls the Gemini model on any anonymous request.

A twelfth route (`/api/import_spreadsheet`) reads `user_email` from the form but also reads `user_id` from the token — the body email is accepted but not compared to the token, leaving a gap.

A thirteenth issue (`/api/ai/chat`) keys Firestore by uid but the live collection is keyed by email — not a cross-account write risk, but causes every real user's portfolio stats to return empty.

All details are in `ROUTE_INVENTORY_031.csv`.

---

## 2. Fix Strategy

**Principle:** the server never trusts an identity claim from the request body, form, or query string. The only source of truth is `Depends(get_current_user)` from `routes/deps.py`, which verifies the Firebase Bearer token and returns the decoded dict with `email`, `uid`, and `admin`.

**Three patterns to apply, in order of priority:**

### Pattern A — Add `Depends(get_current_user)` and derive from token
For routes that currently accept `user_email` from the body/form and use it directly as the Firestore document ID:

```python
# BEFORE (vulnerable)
async def some_endpoint(req: SomeRequest):
    user_ref = db.collection('users').document(req.user_email)

# AFTER (fixed)
from routes.deps import get_current_user
async def some_endpoint(
    req: SomeRequest,
    _user: dict = Depends(get_current_user),
):
    caller_email = (_user.get('email') or '').strip().lower()
    user_ref = db.collection('users').document(caller_email)
```

If `req.user_email` is also present (e.g., sent by the Flutter client for legacy reasons), it is **silently ignored** — the server uses only `caller_email` from the token.

### Pattern B — uid-keyed routes
For scan_routes endpoints that use `request.uid` as the Firestore key:

```python
# AFTER (fixed)
async def some_endpoint(
    request: SomeRequest,
    _user: dict = Depends(get_current_user),
):
    caller_uid = (_user.get('uid') or _user.get('user_id') or '').strip()
    user_ref = db.collection('users').document(caller_uid)
```

`request.uid` in the body is still accepted for the `import_session_id` and other non-identity fields, but the Firestore path uses only `caller_uid`.

### Pattern C — RAG endpoint (no auth → require auth + usage cap)
`/api/v1/rag/query` has no auth at all. Fix:

```python
@app.post("/api/v1/rag/query")
async def rag_query_endpoint(
    req: RagQueryRequest,
    _user: dict = Depends(get_current_user),
):
```

Add a per-user daily call cap (suggested: 50 RAG queries/day per uid), enforced server-side in the existing `RateLimitTracker` (convert it from log-only to blocking for this endpoint as a first step). If the cap is exceeded, return HTTP 429.

---

## 3. Route-by-Route Fix Plan

### 3.1 `/api/v1/rag/query` — `main.py:167-168` — Priority: CRITICAL (no auth at all)

**Current:** `async def rag_query_endpoint(req: RagQueryRequest):` — no `Depends`.  
**Fix:**
- Add `_user: dict = Depends(get_current_user)` parameter.
- Add per-uid daily cap (50 calls): check and increment a Firestore counter at `_rate_limits/{uid}/rag_query/YYYY-MM-DD`. Return 429 with `"detail": "Daily RAG query limit reached"` if exceeded.
- The cap document is created on first call and expires after 24 hours (set `ttl` field, or use the date key as a natural expiry).
- No body/form email field exists here — just add the Depends.

**Test cases:**
1. No token → 401
2. Valid token, under cap → 200
3. Valid token, at cap → 429

---

### 3.2 `/api/checklist/add_coins` — `main.py:7783-7784` — Priority: HIGH

**Current:** `def checklist_add_coins(req: ChecklistAddRequest):` — `req.user_email` from body used at `main.py:7839`.  
**Fix:** Pattern A. Add `_user: dict = Depends(get_current_user)`. Replace all `req.user_email` references (lines 7839, 7856, 7908, 7919) with `caller_email` derived from token. The `user_email` field in `ChecklistAddRequest` may stay for backward compat but is ignored server-side.

**Test cases:**
1. No token → 401
2. Token for user A, body `user_email=B@example.com` → writes to A's collection, not B's (verify Firestore path)
3. Happy path: valid token, valid slots → 200, coins written to correct user

---

### 3.3 `/api/review/commit` — `main.py:3000-3001` — Priority: HIGH

**Current:** `async def commit_reviews(request: CommitReviewsRequest):` — `request.user_email` from body at `main.py:3007`.  
**Fix:** Pattern A. Add `Depends(get_current_user)`, derive `caller_email`, replace `request.user_email` usages at lines 3007, 3247, 3273, 3285, 3304.

**Test cases:**
1. No token → 401
2. Token A, body email B → 403 (or writes to A, not B — verify)
3. Happy path → 200

---

### 3.4 `/api/analyze_binder_scan` — `main.py:3908-3913` — Priority: HIGH

**Current:** `user_email: str = Form(...)` at `main.py:3910`, no token check.  
**Fix:** Pattern A. Add `_user: dict = Depends(get_current_user)` to the function signature (alongside existing `Form` params — FastAPI allows mixing). Derive `caller_email` from token. Remove or ignore the `user_email` Form field (keep the parameter for client compat but don't use it for the Firestore path).

**Test cases:**
1. No token → 401
2. Token A, form `user_email=B` → uses A's path
3. Happy path → 200

---

### 3.5 `/api/confirm_binder_scan` — `main.py:4606` area — Priority: HIGH

**Current:** `request.user_email` from body model used at `main.py:4623`.  
**Fix:** Pattern A. Same as 3.4.

**Test cases:** Same pattern as 3.4.

---

### 3.6 `scan_routes.py` — `/api/upload_document` — `scan_routes.py:84-90` — Priority: HIGH

**Current:** `uid: str = Form(...)` and `user_email: Optional[str] = Form("")` — no `Depends`.  
**Fix:** Pattern B. Add `_user: dict = Depends(get_current_user)` to `upload_document`. Derive `caller_uid` from token. Use `caller_uid` as the Firestore path; ignore body `uid` and `user_email` for identity.

**Test cases:**
1. No token → 401
2. Token A, body `uid=B_uid` → uploads to A's path
3. Happy path → 200

---

### 3.7 `scan_routes.py` — `/api/review/resume_session` — `scan_routes.py:215-216` — Priority: HIGH

**Current:** `request.uid` from `ResumeSessionRequest` body (line 40-42) — no token.  
**Fix:** Pattern B.

---

### 3.8 `scan_routes.py` — `/api/review/abort_session` — `scan_routes.py:240-241` — Priority: HIGH

**Current:** Same pattern as 3.7.  
**Fix:** Pattern B.

---

### 3.9 `scan_routes.py` — `/api/review/commit_session` — `scan_routes.py:273-274` — Priority: HIGH

**Current:** Same pattern as 3.7.  
**Fix:** Pattern B. Also verify `audit_log` write at line ~342 uses `caller_uid`, not `request.uid`.

---

### 3.10 `scan_routes.py` — `/api/review/bulk_condition` — `scan_routes.py:359-360` — Priority: HIGH

**Current:** Same pattern as 3.7.  
**Fix:** Pattern B. Also verify audit log uses `caller_uid`.

---

### 3.11 `scan_routes.py` — `/api/review/delete_items` — `scan_routes.py:430-431` — Priority: HIGH

**Current:** `request.user_email` from `DeleteReviewItemsRequest` body (line 424-426); used as Firestore uid at line 438.  
**Fix:** Pattern A. Add `Depends(get_current_user)`. Use `caller_email` from token.

---

### 3.12 `/api/import_spreadsheet` — `import_routes.py:76-88` — Priority: MEDIUM

**Current:** `user_email: str = Form(...)` accepted but `user_id` is correctly taken from token at line 88 (`user.get("uid")`). The body `user_email` is not used for the Firestore path — it is used only for logging/metadata fields.  
**Fix:** Remove `user_email` from the `Form(...)` parameter (or make it `Optional` and stop reading it from the body). If `user_email` is needed for metadata, derive it from `_user.get("email")`. This eliminates the misleading parameter and prevents any future accidental use.

---

### 3.13 `/api/ai/chat` uid-vs-email key mismatch — `ai_routes.py:82,107` — Priority: MEDIUM

**Not a cross-account write**, but portfolio stats return empty for all real users.  
**Fix:** In `ai_routes.py:107` and similar, look up Firestore by `user.get("email")` (to match the live collection keyed by email), OR add a migration that normalizes the key. Coordinate with Workstream B (Morgan Gate 0) which touches the same file.

---

## 4. Shared Dependency: `_authenticate_request`

`main.py:11167` uses `_authenticate_request(authorization, req.user_email)` for some routes. That helper should also be checked to ensure it verifies the token and does not fall back to the body email when no token is present. Verify and document in code review.

---

## 5. Implementation Order

Do all three in this priority order within a single PR:

1. `/api/v1/rag/query` (no auth at all — most critical)
2. `/api/checklist/add_coins`, `/api/review/commit`, `/api/analyze_binder_scan`, `/api/confirm_binder_scan` (main.py body-email routes)
3. `scan_routes.py` — all 5 review/* endpoints + upload_document + delete_items
4. `import_routes.py` — remove body user_email from spreadsheet import
5. `ai_routes.py` — uid-vs-email fix (coordinate with Track 2)

---

## 6. Test Strategy

For each route, a pytest test in `numista_backend/tests/test_req031_auth.py`:

```python
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Pattern for no-token test:
def test_no_token_returns_401(client):
    response = client.post("/api/checklist/add_coins", json={...})
    assert response.status_code == 401

# Pattern for cross-account test:
def test_cross_account_write_uses_token_email(client):
    # Mock get_current_user to return user A
    # Send request with body user_email = user B
    # Assert Firestore was called with user A's email (mock firestore)
    ...
```

All tests must mock:
- `routes.deps.get_current_user` (or `firebase_auth.verify_id_token`)
- `firestore.Client` (to capture which document path was addressed)

---

## 7. Acceptance Criteria

- [ ] `pytest numista_backend/tests/test_req031_auth.py` — all pass
- [ ] Full pytest suite passes (407 clean / 411 local)
- [ ] `flutter analyze lib/` — 0 errors (no Flutter changes needed for this plan, but verify)
- [ ] `git status` shows only target files modified
- [ ] No deploy until founder types YES

---

## 8. What Does NOT Change

- The `/api/deep_dive` Morgan endpoint is already token-authenticated (`main.py:2722-2735`). No change.
- `routes/payment_routes.py` was fixed in REQ_027E/F. No change.
- `routes/admin_routes.py` uses `Depends(require_admin_user)`. No change.
- No Firestore data migration in this hotfix. Key format stays as-is.

---

## 9. Open Questions for Grok CoS

1. Should cross-account mismatch (token A, body B) return **403** (explicit rejection) or silently redirect to token user's data (transparent fix)? Recommendation: **transparent redirect** (use token email, ignore body) — simpler, no client-side changes needed, existing clients keep working.
2. Should `/api/v1/rag/query` daily cap be 50 or a different number?
3. The `_authenticate_request` helper at `main.py:11167` — scope for this PR or a follow-up?

---

*No code written. Awaiting Gemini review, then Grok CoS score, then founder Proceed.*
