# EXECUTE ORDER: Antigravity CoS (founder said "Execute", 8 Oct 2026 10:35 AM ET)

The founder approved IMPLEMENTATION_PLAN_UX_AND_MORGAN_2026-10-08_v2.md. Start now, with all three tracks in parallel.

| Track | Sub-agent model | First deliverable (this folder) |
|---|---|---|
| 1. REQ_031 HOTFIX (per FOR_AG_COS_REQ031_HOTFIX_NOW.md) | Claude Opus 4.6 (Thinking) | PLAN_V1_REQ031_HOTFIX.md + ROUTE_INVENTORY_031.csv |
| 2. Morgan Gate 0 (v2 items 1-10 + original Gate 0) | Claude Opus 4.6 (Thinking), separate sub-agent | PLAN_V1_MORGAN_GATE0.md |
| 3. UX fixes 2, 3, 1, 4, 5 (REQ_032) | Claude Sonnet 4.6 (Thinking) | PLAN_V1_REQ032_UX.md |
| Reviewer for all three | Gemini 3.8 Flash | GEMINI38_REVIEW_<track>.md, quoting the file:line it actually opened |

What the founder approved:
- Writing plans.
- After Grok CoS scores a plan PASS, building and testing that track on dev and branches.

What still needs the founder's typed YES:
- Any deploy to production.
- Any write to live data or user collections.
- Any sync_canon run.

Rules:
- Each track goes to Grok CoS for scoring before code is written.
- Track 3 waits on REQ_034/036 for Fix 1 only. Fixes 2, 3, 4 and 5 go ahead without it.
- Tracks 2 and 3 coordinate on ai_chat_screen.dart only.
- No canned reviews.

Write ACK_EXECUTE_GO.md here listing the sub-agent names and tracks, then start.
