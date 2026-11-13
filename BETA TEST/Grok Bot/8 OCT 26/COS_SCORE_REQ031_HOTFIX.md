# COS SCORE - T1 REQ_031 Hotfix
Scored by: Grok CoS, 12 Oct 2026 ~12:50 PM ET. Code checked: dev HEAD 67ea1040 (docs-only on top of e5f5760c).
PASS = build on dev only. No deploy, no live data writes, no sync_canon without Eric's typed YES.

## Verdict: PASS (conditional - fold these in before writing code)

### Spot-checks (lines I opened)
- main.py:3241-3242 `@app.post("/api/review/bulk_update")` / `async def bulk_update_reviews(request: BulkUpdateRequest):` and :3247 `queue_ref = db.collection('users').document(request.user_email).collection('review_queue')` - CONFIRMED: no auth, body email. Gemini right.
- main.py:3265 `@app.post("/api/review/delete_items")` and scan_routes.py:430 `@router.post("/review/delete_items")` (docstring: "Permanently delete one or more review_queue documents") - CONFIRMED duplicate. main.py:96 `app.include_router(scan_router)` registers before line 3265, so the hard delete wins.
- ai_routes.py:82 `user_id = user.get("uid") or user.get("user_id") or "dev_guest_uid"` and :107 `stats_doc = db.collection("users").document(user_id).collection("summary").document("stats").get()` - CONFIRMED uid vs email key.

### Required fixes
1. Add /api/review/bulk_update to ROUTE_INVENTORY_031.csv and the plan; Pattern A (token email). Restrict `request.updates` to an allowlist of fields.
2. Duplicate /api/review/delete_items: keep ONE route = the SOFT delete (main.py:3265 logic), token-authed. Remove the scan_routes.py:430 hard-delete route. Test proves deleted items are recoverable.
3. ai_routes.py:82/107: key Firestore by token email (lowercased); remove the "dev_guest_uid" fallback (no token = 401).
4. Re-grep main.py + routes/*.py for any other `user_email`/`uid` taken from body/form and add to inventory.
5. Scan and import route caps (Gate 0 addition #5) belong in T1: add per-user daily caps on /api/analyze_binder_scan, /api/upload_document, /api/import_spreadsheet (429 when exceeded).

### Answers to open questions (decided by Grok CoS)
1. Token A / body B: return 403 when a body email is present AND differs from the token; ignore it when blank. Safer and visible in logs; our own app always sends the matching email, so no client breakage.
2. RAG cap: 50/day per user is fine. Admin exempt.
3. `_authenticate_request` (main.py:11167): IN SCOPE for this PR. It must never fall back to the body email.
None need Eric.

Ball: AG CoS: build on dev (fold in fixes). Write EXECUTE_DONE_REQ031.md with commit hash + pytest result.
