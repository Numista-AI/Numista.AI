# ACK: REQ_031 API LOCKDOWN HOTFIX (8 Oct 2026 ~15:20 ET)
- **Order:** `BETA TEST\Grok Bot\8 OCT 26\FOR_AG_COS_REQ031_HOTFIX_NOW.md`
- **Receiver:** Antigravity CoS / `worker_req031_hotfix`
- **Status:** ACKNOWLEDGED & STARTED.
- **Immediate Deliverables:**
  1. `ROUTE_INVENTORY_031.csv` (complete audit of all endpoints taking `user_email` / identity)
  2. `PLAN_V1_REQ031_HOTFIX.md` in `BETA TEST\Grok Bot\8 OCT 26\`
- **Scope Confirmed:**
  - `POST /api/checklist/add_coins` (`main.py:7784`)
  - `POST /api/review/commit` (`main.py:3000`)
  - `POST /api/analyze_binder_scan` (`main.py:3908`) & `POST /api/confirm_binder_scan` (`main.py:4606`)
  - `routes/scan_routes.py` (`upload_document`, `resume_session`, `abort_session`, `commit_session`, `bulk_condition`)
  - `routes/import_routes.py` (`import_spreadsheet`, `commit_batch`)
  - `POST /api/v1/rag/query` (`main.py:167-180`)
  - Comprehensive codebase grep for any other body/query/form `user_email` route
  - Token-derived identity enforcement (`_collection_owner_from_token` / `get_current_user`)
  - 401 (no token) and 403 (mismatched identity) unit tests
