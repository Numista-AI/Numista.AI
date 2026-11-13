# ORDER TO ANTIGRAVITY CoS: REQ_031 API Lockdown as a HOTFIX (priority)
From: Grok Bot Chief of Staff, 8 Oct 2026, on the founder's direction (outside Grok review accepted).

REQ_031 is pulled out of the Morgan project and goes first. Model: Claude Opus 4.6 (Thinking). Reviewer: Gemini 3.8 Flash.

Scope. Every route below must derive the user from the sign-in token, never from a body, form or query email, and must reject cross-account access:
- POST /api/checklist/add_coins (main.py:7784)
- POST /api/review/commit (main.py:3000)
- binder scan analyze/confirm (main.py:3908, 4606)
- scan_routes: /upload_document, /review/resume_session, /review/abort_session, /review/commit_session, /review/bulk_condition (84-359)
- import_routes: /import_spreadsheet (76), /v1/import/commit_batch (234)
- /api/v1/rag/query (main.py:167-180): require sign-in plus a usage cap
- Grep for any other route that takes user_email from the request and list it in ROUTE_INVENTORY_031.csv

Tests: for each route, prove that no token returns 401, that user A's token with user B's email returns 403 or is ignored, and that the happy path still works.

Steps:
1. Write Plan.v1 to this folder.
2. Gemini reviews it, quoting the file:line it actually opened.
3. Grok CoS scores it.
4. The founder says Proceed.
5. Execute on dev.
6. Code Reviewer and Field Tester check it.
7. Deploy only on the founder's YES.

No live data writes. Write ACK_REQ031_HOTFIX.md here when you start.

The full plan is in IMPLEMENTATION_PLAN_UX_AND_MORGAN_2026-10-08_v2.md (this folder). The Gate 0 and UX workstreams proceed in parallel under the model assignments already ordered.
