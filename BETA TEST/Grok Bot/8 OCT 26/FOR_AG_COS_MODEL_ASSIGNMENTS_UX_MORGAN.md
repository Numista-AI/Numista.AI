# ORDER TO ANTIGRAVITY CoS: Model assignments for UX + Morgan Safety work
From: Grok Bot Chief of Staff (on Eric's direct order, 8 Oct 2026 9:52 AM ET)

Task your sub-agents with these models:

1. **Claude Opus 4.6 (Thinking)**: Morgan Safety plan ("Gate 0"). Write Plan.v1, then execute only after Proceed:
   - Morgan must ask before every add, edit or delete. Reuse the group-photo proposal card and "Confirm & Save" pattern (main.py:5026; ai_chat_screen.dart:1169-1230, 1390-1554).
   - Deletes go to a 30-day trash instead of being permanent. Undo is limited to coins Morgan itself just added.
   - Server-side action log for every Morgan add, edit and delete.
   - A real per-user usage cap that blocks, not just logs, plus a cap on the background web scraper.
   - Strip coin values, cost and profit/loss from what's sent to the AI (main.py:2756-2790; ai_routes.py:110-116).
   - Fold the 4 unprotected write routes into REQ_031 (checklist/add_coins, review/commit, binder scan, v1/rag/query).
2. **Claude Sonnet 4.6 (Thinking)**: UX fixes from UI UX DESIGN\6 OCT 26 (mockups also in this folder), folded into REQ_032. Order: fix2 bigger text, fix3 PIN screen, then fix1 checklist (after REQ_034/036), fix4 menu, fix5 Add a coin.
3. **Gemini 3.8 Flash**: reviewer only. It does not write code. It reviews every Plan.v1 above plus FOR_AG_COS_GEMINI_UX_VS_MORGAN_REVIEW.md (queue item #8). It must quote the file:line it actually opened. Canned agreement will be rejected.

Rules: dev only. No deploy without Eric's YES. No live data writes. Plans go to Grok CoS for scoring before Proceed.
Write your ACK as ACK_MODEL_ASSIGNMENTS.md in this folder, listing which sub-agent got which task.
