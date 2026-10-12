# WHOSE TURN: single source of truth for who holds the ball
Both CoS bots update this file every time they hand off. Format: Track | Ball with | Owes what | Since

Last updated by AG CoS: 2026-10-12 12:31 PM ET

| Track | Ball with | Owes what | Since |
|---|---|---|---|
| 1. REQ_031 hotfix | **Grok CoS: score it** | PLAN_V1_REQ031_HOTFIX.md + ROUTE_INVENTORY_031.csv filed | 12:22 PM 10/12 |
| 2. Morgan Gate 0 | **Grok CoS: score it** | PLAN_V1_MORGAN_GATE0.md filed | 12:22 PM 10/12 |
| 3. REQ_032 UX | **Grok CoS: score it** | PLAN_V1_REQ032_UX.md filed | 12:22 PM 10/12 |
| 3b. ALT SITE (REQ_032B) | **Grok CoS: score it** | PLAN_V1_REQ032B_ALT_SITE.md filed (Eric YES 12:24 PM 10/12) | 12:31 PM 10/12 |
| 4. Gemini reviews | **COMPLETED** | GEMINI38_REVIEW_REQ031_HOTFIX.md, GEMINI38_REVIEW_MORGAN_GATE0.md, GEMINI38_REVIEW_REQ032_UX.md, GEMINI38_REVIEW_REQ032B_ALT_SITE.md filed beside plans | 12:32 PM 10/12 |
| 5. RADIO NET 004 | **Eric** | NET-004_JOINT-BRIEF-TO-ERIC_OVER.md filed — Eric picks Option 1 or 2 | 12:22 PM 10/12 |
| F1 RERUN6 (AWQ 25 rows) | **BLOCKED — see ACK_RERUN6.md** | S-SILVER-PROOF pages need browser fetch; queued to conversation d8fce90c | 12:22 PM 10/12 |

## Handoff rules (AG CoS and Grok CoS both follow these)
1. When AG finishes a plan or review, it drops the file here and changes that row to "Grok CoS: score it". It does NOT write "waiting on Grok" anywhere else.
2. Grok CoS checks this folder every 15 minutes on weekdays from 9 AM to 7 PM ET. It writes COS_SCORE_<name>.md (PASS or ITERATE) and flips the row back.
3. PASS means AG may build and test on dev right away. AG does not need to wait for Eric unless the row says **Eric**.
4. Only these rows say **Eric**: a deploy YES, live data writes, or a scope decision.
5. If a row hasn't moved in 2 hours of Eric's working time, the holder says why in the row.
