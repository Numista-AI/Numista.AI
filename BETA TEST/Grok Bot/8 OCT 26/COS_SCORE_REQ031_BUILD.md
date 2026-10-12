# COS SCORE - T1 REQ_031 BUILD (commit a774152f on dev)
Scored by: Grok CoS, 12 Oct 2026 ~5:25 PM ET. Read: git show a774152f (6 files, +721/-122). Ran pytest myself.
PASS = code accepted on dev. DEPLOY needs Eric's typed YES. Nothing deployed.

## Verdict: PASS

## Pytest (run by Grok CoS, numista_backend\.venv, `pytest tests -s`)
447 passed, 0 failed (11.0s). tests/test_req031_auth.py: 35/35 passed.
- 401 no-token: 10/10 (rag_query, checklist_add_coins, review_commit, analyze_binder_scan, confirm_binder_scan, bulk_update, delete_items, upload_document, resume_session, import_spreadsheet).
- 403 mismatch: 10/10 (checklist, review_commit, analyze, confirm, bulk_update, delete_items, resume/abort/commit_session, bulk_condition).
- 429 caps: rag at_cap, analyze at_cap, upload at_cap, import at_cap, admin exempt - all pass.
(Note: plain `pytest -q` crashes in capture on this laptop; `-s` works.)

## Required fixes - checked in the diff
1. bulk_update auth + allowlist - DONE. `async def bulk_update_reviews(request: BulkUpdateRequest, _user: dict = Depends(get_current_user)):` / `raise HTTPException(status_code=403, detail="Forbidden: email mismatch")` / `allowed_keys = {"storage_location", "condition", "notes", "status"}` / `queue_ref = db.collection('users').document(caller_email).collection('review_queue')`.
2. One delete route, soft - DONE. scan_routes.py hard delete removed in full (`-@router.post("/review/delete_items")`, `-            batch.delete(doc_ref)`); main.py route kept with token: `async def delete_review_items(request: DeleteReviewItemsRequest, _user: dict = Depends(get_current_user)):`. test_delete_items_soft_delete_happy_path passes.
3. ai_routes uid->email, no dev_guest_uid - DONE. `-    user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"` -> `+    user_email = _get_user_email(user)`; `stats_doc = db.collection("users").document(user_email).collection("summary")...`. No-email -> `raise HTTPException(status_code=401, ...)`; dev guest only when not prod AND ALLOW_UNAUTHENTICATED=1.
4. Body-email routes - DONE for all 15 inventory rows + bulk_update (rag, checklist, review/commit, analyze/confirm binder, upload_document, 4 session routes, import).
5. Caps - DONE. deps.py `check_and_increment_rate_cap` (fails closed: `raise HTTPException(status_code=429, detail="Daily limit reached")`); rag 50, analyze_binder_scan 10, upload_document 20, import_spreadsheet 5; admin exempt.
6. _authenticate_request (main.py:2689 now) - OK: `if not authorization or not authorization.startswith("Bearer "): raise HTTPException(status_code=401, ...)`.

## Follow-ups (not blockers; file as tickets)
- Key split: main.py routes key Firestore by token EMAIL, scan_routes session/upload routes key by Firebase UID (`caller_uid = (_user.get('uid') ...`). Pre-existing pattern (those routes already took `uid` before), but confirm which key Review Hub reads before deploy smoke.
- Rate-cap read+increment is not a transaction; a burst can overshoot by a few. Fine for now.
- Deploy smoke on grokbot: sign in, scan 1 page, Review Hub delete -> item recoverable, AI chat shows real stats.

Ball: ERIC - typed YES to deploy a774152f (backend). T2 and T3B may now build on dev.
