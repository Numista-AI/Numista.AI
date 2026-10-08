# WHOSE TURN: single source of truth for who holds the ball
Both CoS bots update this file every time they hand off. Format: Track | Ball with | Owes what | Since

Last updated by Grok CoS: 8 Oct 2026 3:25 PM ET

| Track | Ball with | Owes what | Since |
|---|---|---|---|
| 1. REQ_031 hotfix | **AG CoS** (worker_req031_hotfix) | PLAN_V1_REQ031_HOTFIX.md + ROUTE_INVENTORY_031.csv, then Gemini review | 3:20 PM |
| 2. Morgan Gate 0 | **AG CoS** (worker_morgan_gate0) | PLAN_V1_MORGAN_GATE0.md, then Gemini review | 3:20 PM |
| 3. REQ_032 UX | **AG CoS** (worker_req032_ux) | PLAN_V1_REQ032_UX.md, then Gemini review | 3:20 PM |
| F1 RERUN6 (AWQ 25 rows) | **AG CoS** | ACK_RERUN6.md + evidence pack (7 OCT 26 folder) | 7 Oct 11:03 AM |

## Handoff rules (AG CoS and Grok CoS both follow these)
1. When AG finishes a plan or review, it drops the file here and changes that row to "Grok CoS: score it". It does NOT write "waiting on Grok" anywhere else.
2. Grok CoS checks this folder every 15 minutes on weekdays from 9 AM to 7 PM ET. It writes COS_SCORE_<name>.md (PASS or ITERATE) and flips the row back.
3. PASS means AG may build and test on dev right away. AG does not need to wait for Eric unless the row says **Eric**.
4. Only these rows say **Eric**: a deploy YES, live data writes, or a scope decision.
5. If a row hasn't moved in 2 hours of Eric's working time, the holder says why in the row.
