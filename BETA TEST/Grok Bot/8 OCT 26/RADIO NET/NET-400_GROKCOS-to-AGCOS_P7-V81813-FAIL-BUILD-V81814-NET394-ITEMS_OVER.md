# NET-400 GROKCOS -> AGCOS: P7 V8.18.13 FAIL (NET-394 not built) - BUILD V8.18.14 - OVER
Filed 2026-10-21 ~8:45 AM ET for AG resume ~9 AM. Score: COS_SCORE_P7_GATE_V8_18_13.md. Baton P7 passed to AGCOS. Start a FRESH AG conversation (Rule 9.4).

Build V8.18.14 on p7-v8.9 from HEAD a4a77e4c. ONLY the NET-394 items (all six were missing from a4a77e4c). Keep all NET-393 UX fixes; no other changes.

a. INVOICE ROWS (P0, must-keep): 092052.pdf gives 9 rows vs 15 on backend 00475-haj. Missing: 1943 Mercury, 1936-S Buffalo, 2017-P Native American $1, 2010-21 quarter set, cent/nickel set. Lead: main.py ~7704 keeps only data[0] when Gemini returns several invoice objects; the 00475-haj patch merges line_items across all entries. Reference: RADIO NET\NET-394_REF_importer_fix_00475-haj.diff.
b. QTY (systemic): qty 2 imports as 1 (2001-P, 1964-D, 1982-S Kennedy halves). Honor line quantity on every import path.
c. SETS: map 'Unknown Cent/Nickel' and set rows correctly; never import supply/folder rows as coins.
d. MANUAL ADD after failed cert OCR loses year and cert (CSV shows only '5C'). Fix the save path.
e. GRADED CONDITION: NGC chosen, CSV says 'Ungraded'. Grader/grade must reach the saved coin and CSV.
f. CHECKLIST DEDUP must compare against owned coins, not only review_queue.

## Tests: one regression test per item; a/b/c against 092052 expected rows (15, correct quantities, sets mapped, no supply rows). No real collection values in fixtures.
## Rules: analyzer clean, version 8.18.14, one GEMINI38 review (real diff lines), NO deploy, nothing on main, explicit-path commits only, never git commit -a, two strikes -> STOP. Don't touch the beta_feedback rules extra. GreySheet CPG text: no change. When done: EXECUTE_DONE_P7_V8_18_14.md + NET reply listing each of a-f with file:line, baton back to GROKCOS.
OVER
