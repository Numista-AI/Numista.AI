# EXECUTE_DONE — P4 Route Ownership (21 Routes)

**Date:** 2026-10-14  
**Branch:** dev  
**Commits audited:** `0ddbdec2` + `b3b7c30f` (and subsequent on dev)  
**Executed by:** AG CoS (Antigravity Chief of Staff)

---

## Hard Safety Attestation

> [!IMPORTANT]
> - **No deploys executed.** All changes are dev-branch only.
> - **No writes to Eric's Firestore.** Tests use `unittest.mock.patch` / `MagicMock` exclusively.
> - **No live network calls** in any test.
> - All 33 tests pass (33/33) after URL path correction.

---

## All 21 Routes — File:Line + Verbatim Check Code

The ownership-check pattern added to all routes is:

```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

Routes using `_authenticate_request(authorization, body_email, current_user=_user)` delegate to the centralized helper which applies the same 403 check internally (main.py L3081-3086).

---

### main.py Routes

| # | Route | File:Line | Check Type |
|---|-------|-----------|------------|
| 1 | `POST /api/nicknames/submit` | `main.py:1517` | Direct ownership check L1528–1533 |
| 2 | `POST /api/nicknames/{doc_id}/vote` | `main.py:1699` | Direct ownership check L1707–1712 |
| 3 | `POST /api/process_invoice` | `main.py:1962` | Direct ownership check L1975–1980 |
| 4 | `GET /api/coin_crop` | `main.py:4274` | Direct ownership check L4289–4294 |
| 5 | `POST /api/analyze_checklist` | `main.py:4883` | Direct ownership check L4905–4910 |
| 6 | `GET /api/binder_scans/{user_email}` | `main.py:5295` | Direct ownership check L5305–5310 |
| 7 | `GET /api/binder_scans/{user_email}/{binder_id}` | `main.py:5340` | Direct ownership check L5350–5355 |
| 8 | `POST /api/identify_group_photo` | `main.py:5558` | Via `_authenticate_request` L5579 |
| 9 | `POST /api/identify_coin_photo` | `main.py:6086` | Via `_authenticate_request` L6120 |
| 10 | `POST /api/import/upload` | `main.py:6938` | Direct ownership check L6949–6954 |
| 11 | `GET /api/import/status/{session_id}` | `main.py:7086` | Direct ownership check L7092–7097 |
| 12 | `GET /api/receipts/{user_email}` | `main.py:7800` | Via `_authenticate_request` L7809 |
| 13 | `DELETE /api/receipts/{user_email}/{receipt_id}` | `main.py:7853` | Via `_authenticate_request` L7865 |
| 14 | `GET /api/receipts/{user_email}/{receipt_id}/view_url` | `main.py:8114` | Via `_authenticate_request` L8127 |
| 15 | `GET /api/receipts/{user_email}/{receipt_id}/stream` | `main.py:8168` | Via `_authenticate_request` L8184 |
| 16 | `GET /api/collection/count` | `main.py:8243` | Via `_authenticate_request` L8255 |
| 17 | `GET /api/wishlist/deals/{user_email}` | `main.py:11445` | Direct ownership check L11453–11458 |
| 18 | `GET /api/transfer/sold-items/{user_id}` | `main.py:11679` | Via `_authenticate_request` L11688 |
| 19 | `GET /api/estate/generate-appraisal-url` | `main.py:11961` | Direct ownership check L11973–11978 |

### attorney_routes.py Route

| # | Route | File:Line | Check Added |
|---|-------|-----------|-------------|
| 20 | `GET /api/attorney/snapshot` | `routes/attorney_routes.py:168` | Caller ownership check L222–224 |

### payment_routes.py Route

| # | Route | File:Line | Check Added |
|---|-------|-----------|-------------|
| 21 | `GET /api/stripe/subscription-status` | `routes/payment_routes.py:130` | Direct ownership check L138–143 |

---

## Verbatim Code Citations Per Route

### Routes 1–3, 4–7, 10–11, 17, 19 (Direct ownership check — identical pattern)

**main.py:1528–1533** (submit_nickname):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:1707–1712** (vote_nickname — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:1975–1980** (process_invoice — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:4289–4294** (get_coin_crop — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:4905–4910** (analyze_checklist — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:5305–5310** (list_binder_scans — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:5350–5355** (get_binder_detail — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:6949–6954** (import_upload — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:7092–7097** (import_status — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:11453–11458** (get_user_wishlist_deals — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

**main.py:11973–11978** (api_generate_estate_appraisal_url — identical pattern):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if user_email.strip().lower() != caller_email and user_email.strip() != caller_uid:
        raise HTTPException(status_code=403, detail="Forbidden")
```

### Routes 8–9, 12–16, 18 (Via `_authenticate_request`)

**main.py:5579** (identify_group_photo):
```python
owner_key = _authenticate_request(authorization, user_email, current_user=_user)
```

**main.py:6120** (identify_coin_photo):
```python
owner_key = _authenticate_request(authorization, user_email, current_user=_user)
```

**main.py:7809** (list_receipts):
```python
owner_key = _authenticate_request(authorization, user_email, current_user=_user)
```

**main.py:7865** (delete_receipt):
```python
owner_key = _authenticate_request(authorization, user_email, current_user=_user)
```

**main.py:8127** (receipt_view_url):
```python
owner_key = _authenticate_request(authorization, user_email, current_user=_user)
```

**main.py:8184** (receipt_stream):
```python
owner_key = _authenticate_request(auth_header, user_email, current_user=_user)
```

**main.py:8255** (collection_count):
```python
owner_key = _authenticate_request(authorization, user_email if user_email else None, current_user=_user)
```

**main.py:11688** (api_get_sold_items):
```python
owner_key = _authenticate_request(authorization, user_id, current_user=_user)
```

**`_authenticate_request` 403 enforcement (main.py:3081–3086):**
```python
if not is_admin and not is_dev_guest:
    if clean_body != owner_key and clean_body != token_email and clean_body != token_uid.lower():
        raise HTTPException(
            status_code=403,
            detail="Forbidden: Mismatched authenticated identity and requested user_email"
        )
```

### Route 20 — attorney_routes.py:168, 222–224

**routes/attorney_routes.py:173** (Depends added):
```python
_user: dict = Depends(get_current_user),
```

**routes/attorney_routes.py:209–224** (ownership check):
```python
owner_uid = data.get("uid") or ""
owner_email = (data.get("user_email") or "").strip().lower()
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"

# Verify uid matches
if data.get("uid") != uid:
    raise HTTPException(
        status_code=403,
        detail="Forbidden",
    )

if not _user.get("admin") and not is_dev_guest:
    if caller_uid != owner_uid and caller_email != owner_uid and caller_email != owner_email:
        raise HTTPException(status_code=403, detail="Forbidden")
```

### Route 21 — payment_routes.py:130, 138–143

**routes/payment_routes.py:133** (Depends added):
```python
_user: Dict[str, Any] = Depends(get_current_user),
```

**routes/payment_routes.py:138–143** (ownership check):
```python
caller_uid = _user.get("uid") or _user.get("user_id") or ""
caller_email = (_user.get("email") or "").strip().lower()
is_dev_guest = os.environ.get("ALLOW_UNAUTHENTICATED") == "1" and caller_email == "dev_guest@numista.ai"
if not _user.get("admin") and not is_dev_guest:
    if uid.strip() != caller_uid and uid.strip().lower() != caller_email:
        raise HTTPException(status_code=403, detail="Forbidden")
```

---

## Test Results

```
numista_backend/tests/test_idor_fixes.py — 33/33 passed

test_portfolio_snapshot_token_a_query_a_returns_200      PASSED
test_portfolio_snapshot_token_a_query_b_returns_403      PASSED
test_portfolio_snapshot_no_token_returns_401             PASSED
test_estate_valid_days_90_capped_to_30                   PASSED
test_estate_valid_days_0_capped_to_1                     PASSED
test_nicknames_submit_token_a_email_b_returns_403        PASSED
test_nicknames_submit_token_a_email_a_passes_check       PASSED
test_nicknames_vote_token_a_email_b_returns_403          PASSED
test_process_invoice_token_a_email_b_returns_403         PASSED
test_coin_crop_token_a_email_b_returns_403               PASSED
test_analyze_checklist_token_a_email_b_returns_403       PASSED
test_list_binder_scans_token_a_email_b_returns_403       PASSED
test_list_binder_scans_token_a_email_a_returns_not_403   PASSED
test_get_binder_detail_token_a_email_b_returns_403       PASSED
test_import_upload_token_a_email_b_returns_403           PASSED
test_import_status_token_a_email_b_returns_403           PASSED
test_list_receipts_token_a_email_b_returns_403           PASSED
test_list_receipts_token_a_email_a_returns_not_403       PASSED
test_delete_receipt_token_a_email_b_returns_403          PASSED
test_receipt_view_url_token_a_email_b_returns_403        PASSED
test_receipt_stream_token_a_email_b_returns_403          PASSED
test_collection_count_token_a_email_b_returns_403        PASSED
test_wishlist_deals_token_a_email_b_returns_403          PASSED
test_wishlist_deals_admin_can_access_any_user            PASSED
test_sold_items_token_a_user_b_returns_403               PASSED
test_estate_appraisal_url_token_a_email_b_returns_403    PASSED
test_estate_appraisal_url_token_a_email_a_not_403        PASSED
test_subscription_status_token_a_uid_b_returns_403       PASSED
test_subscription_status_token_a_uid_a_not_403           PASSED
test_attorney_snapshot_token_a_uid_b_returns_403         PASSED
test_attorney_snapshot_token_a_uid_a_not_403             PASSED
test_identify_group_photo_token_a_email_b_returns_403    PASSED
test_identify_coin_photo_token_a_email_b_returns_403     PASSED
```

**33 passed, 0 failed**

---

## deps.py Enhancement

**routes/deps.py:57–63** — `verify_firebase_bearer_token` now also accepts query-param `token` (for receipt streaming via URL):
```python
token = None
if auth_header and auth_header.startswith("Bearer "):
    token = auth_header.split("Bearer ")[1].strip()
elif request.query_params.get("token"):
    token = request.query_params.get("token", "").strip()
if not token:
    return None
```

---

*AG CoS — P4 Route Ownership — EXECUTE_DONE*
