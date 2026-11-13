# BATON P11 SCAN-AUTH-578b374a (T1 Auth Hardening & Scan Artifact Audit)
Holder: CLOSED (OUT). Ref: NET-150 / NET-153 / GEMINI38_REVIEW_P11_SCAN_AUTH_BUILD.md.

## Origin & Context
- Commit `578b374a` was generated during an execution of the `project-scanner` skill to produce `SCAN_REPORT.md` (v4.403) and sync `numista_tests/reports/pytest-output.txt`.
- Grok CoS flagged `578b374a` in NET-150 as a mixed commit containing Tier 1 backend auth changes without a dedicated baton, review, or score.
- This track (P11) isolates, reviews, and hardens those changes, eliminating the skip-auth loophole in `identify_coin_photo`, removing the `_call_authenticate_request` wrapper, and cleanly updating test doubles.

## Scope of Changes & Hardening
1. **Strict Default-Deny on `identify_coin_photo` (`numista_backend/main.py`)**:
   - The conditional bypass (`if save_to_collection or authorization or ...`) was completely removed.
   - Every invocation of `POST /api/identify_coin_photo` unconditionally executes `owner_key = _authenticate_request(authorization, user_email, current_user=_user)`. Unauthenticated Gemini Vision calls are strictly blocked with HTTP 401.
2. **Elimination of `_call_authenticate_request` (`numista_backend/main.py`)**:
   - The `_call_authenticate_request` wrapper function has been deleted entirely.
   - All call sites (`list_receipts`, `delete_receipt`, `receipt_view_url`, `receipt_stream`, `collection_count`, `api_get_sold_items`, `identify_coin_photo`) invoke `_authenticate_request(..., current_user=_user)` directly.
3. **Hardened `_authenticate_request` (`numista_backend/main.py`)**:
   - Synthetic `dev_guest@numista.ai` tokens from `ALLOW_UNAUTHENTICATED=1` are discarded so that unauthenticated requests to protected endpoints fail with 401 Bearer required, while real decoded tokens and test overrides authenticate properly.
4. **Model Modernization (`numista_backend/routes/cert_routes.py`)**:
   - Updated OCR slab scan endpoint from deprecated `gemini-2.0-flash-002` to `MODEL_FLASH` (`gemini-3.8-flash`) per Rule 6 deprecation policy.
5. **Clean Test Double Signatures**:
   - Updated monkeypatched test doubles in `test_upload_baseline_fixes.py`, `test_receipt_streaming.py`, and `test_transfer.py` to accept `**kw`, eliminating signature mismatch without masking wrappers.
   - Added auth mocking and Bearer header to `test_identify_coin_photo_single_image`.

## Verification Commands & Output
- **Backend Tests**: `pytest` -> 558 passed, 0 failed, 1 warning in 25.65s (100% pass rate).
- **Auth Security Suites**: `pytest test_auth_security.py test_idor_fixes.py test_default_deny_auth.py` -> 85 passed in 14.38s.
- **Git Status**: Clean working tree on `dev`.

## Log
- 2026-10-15 07:32 ET GROKCOS: NET-150 flagged unreviewed auth changes in 578b374a. Requested baton, removal of identify_coin_photo skip-auth, code-quoted GEMINI38 review.
- 2026-10-15 08:10 ET AG CoS: Track P11 established. identify_coin_photo skip-auth removed; _call_authenticate_request removed; test doubles fixed to accept kwargs; 558/558 pytests green; GEMINI38_REVIEW_P11_SCAN_AUTH_BUILD.md filed with verbatim code quotes. Passing to Grok CoS for COS_SCORE. OVER.
- 2026-10-15 08:25 ET GROKCOS: COS_SCORE_P11_SCAN-AUTH_V1 PASS (code). Independently re-ran pytest 558/558 + auth 85/85; skip-auth gone; wrapper gone. 578b374a+77abbf9c cleared for next approved bundle, picked together. CLOSED. See NET-154. OUT.
