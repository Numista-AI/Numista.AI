# EXECUTE_DONE — REQ_031 API Auth Lockdown
Filed by: Antigravity CoS  
Date: 2026-10-12 ~5:11 PM ET  
Commit: `a774152f` on `dev`

## Result: DONE — all 12 fixes applied, 447 tests pass, pushed to dev

| Fix | Endpoint | File:Line | Auth added |
|---|---|---|---|
| 1 | `/api/v1/rag/query` | main.py:168-175 | Depends(get_current_user) + 50/day cap |
| 2 | `/api/checklist/add_coins` | main.py:7834-7975 | Depends + caller_email + 403 mismatch |
| 3 | `/api/review/commit` | main.py:3005-3020 | Depends + caller_email + 403 mismatch |
| 4 | `/api/analyze_binder_scan` | main.py:3940-3975 | Depends + caller_email + 10/day cap |
| 5 | `/api/confirm_binder_scan` | main.py:4650-4675 | Depends + caller_email + 403 mismatch |
| 6 | `/api/review/bulk_update` | main.py:3252-3275 | Depends + caller_email + field allowlist |
| 7 | `/api/review/delete_items` dedup | main.py:3276-3320 + scan_routes.py | Hard-delete route REMOVED; soft-delete token-authed |
| 8 | scan_routes.py review/* | scan_routes.py:84-410 | Depends + caller_uid + 20/day upload cap |
| 9 | `/api/import_spreadsheet` | import_routes.py:76-90 | Token-derived user_id only + 5/day cap |
| 10 | ai_routes.py email key | ai_routes.py:74-245 | Firestore keyed by email not uid; dev_guest_uid gone |
| 11 | `_authenticate_request` | main.py:2685-2712 | Verified correct; full test coverage added |
| 12 | `_check_and_increment_rate_cap` | routes/deps.py:96-125 | Atomic Firestore cap helper; fail-closed; admin exempt |

## Pytest counts
- REQ_031 suite: **35 passed, 0 failed**
- Full backend suite: **447 passed, 0 failed**

## What's next (per COS_SCORE_MORGAN_GATE0.md)
T2 Morgan Gate 0 may now begin — it was gated on T1 EXECUTE_DONE landing on dev. That condition is satisfied.
