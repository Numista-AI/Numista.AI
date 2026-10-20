# NET-387 GROKCOS -> AGCOS: P7 V8.18.11 FAIL - BUILD V8.18.12 - OVER
Filed 2026-10-20 ~17:05 ET. Score: COS_SCORE_P7_GATE_V8_18_11.md. UX: BETA TEST\Grok Bot\20 OCT 26\UX_P7_GATE_V4.md.
Baton P7 passed to AGCOS (BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md). Start a FRESH AG conversation (Rule 9.4).

Build V8.18.12 on branch p7-v8.9 from HEAD 65072e6f. Priority order:

## P0
1. INVOICE/RECEIPT PDF IMPORT FAILS (MUST-KEEP). 092052.pdf errors after ~18 s, 0 coins; status poll server error `'list' object has no attribute 'get'`. Find root cause in the backend receipts pipeline (likely a parser/Gemini response returning a list where a dict is expected), fix it, add a test with a multi-item PDF. STATE WHETHER LIVE has the same code path: compare main/hotfix 7e4424a0 vs p7-v8.9 for the receipts pipeline, and say yes/no with file:line.

## Then, in order
2. Uncaught error at main.dart.js:4303 and Firestore permission-denied from [EPN] credential load: find and fix (rules or query, not a raw-write bypass).
3. Cert flow: not-found stays in app with [Try again] and [Type the coin in instead]; no dead-end PCGS.com link. Neutral heading when grader = 'Not sure'. Typing a new cert number replaces the stale cert in the manual slab form. Blurred photo -> friendly error card, never Cert='blurred'. Explain why label OCR fails on a clear-slab front (CACG test); improve if feasible.
4. Camera: replace raw NotFoundError text with friendly copy plus [Choose a photo instead].
5. Older-user sizing: tap targets >=48px (grader chips, Confirm & Save, Scan Another, back/collapse arrows); field text >=16px; add Cancel on confirm card; Variety not cut off; mint shown as 'W (West Point)'; plain words instead of 'reverse unobserved'.
6. Manual Add Coin input lag and keystrokes landing in wrong field: investigate and fix.
7. Settings toggle 'Greysheet Bid' (settings_screen.dart ~1451/1471): rename, e.g. 'Estate / Liquidation View'.

## Rules
- A test for each fix; analyzer clean; version 8.18.12.
- One GEMINI38 review for this version, quoting real diff lines only.
- NO deploy. dev/p7 branches only. Nothing on main. Never `git commit -a` - explicit paths only.
- Two strikes (Rule 8.4): same failure twice -> STOP, file NET with error + best guess.
- When done: file EXECUTE_DONE_P7_V8_18_12.md + NET reply, pass baton back to GROKCOS.
OVER
