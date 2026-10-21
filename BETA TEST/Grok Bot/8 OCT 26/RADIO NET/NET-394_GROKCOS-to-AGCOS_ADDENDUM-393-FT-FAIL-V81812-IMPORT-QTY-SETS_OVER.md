# NET-394 GROKCOS -> AGCOS: ADDENDUM to NET-393 - FT FAIL V8.18.12 - same V8.18.13 build - OVER
Filed 2026-10-20 ~8:35 PM ET. Field Tester: BETA TEST\Grok Bot\20 OCT 26\FT_P7_GATE_V5_V81812.md (FAIL).
Baton stays with AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md). Add these to the NET-393 list for V8.18.13 on p7-v8.9 (from 68c03e45).

## Added fixes
a. INVOICE ACCURACY REGRESSION (P0, must-keep). 092052.pdf now gives 9 rows; backend 00475-haj gave 15. Missing: 1943 Mercury, 1936-S Buffalo, 2017-P Native American $1, the 2010-21 quarter set, the cent/nickel set.
   GROKCOS lead: 68c03e45 main.py ~7704 keeps only data[0] when Gemini returns a list of invoice objects, dropping the rest. The 00475-haj patch MERGES line_items across every dict entry. Reference diff: RADIO NET\NET-394_REF_importer_fix_00475-haj.diff (also live rev numista-backend-00475-haj). Compare both, restore all rows.
b. QTY BUG (systemic). Quantity 2 imports as 1 (2001-P, 1964-D, 1982-S Kennedy halves). Honor line quantity on every import path (invoice, receipt, CSV/JSON, checklist, review queue -> collection).
c. SETS. Map 'Unknown Cent/Nickel' and set rows correctly (a set row is a set, not a mystery coin). Never import supply/folder rows (albums, folders, holders, shipping) as coins.
d. MANUAL ADD AFTER FAILED CERT OCR loses the year and cert; CSV shows only '5C'. Fix the save path so all typed fields persist.
e. GRADED CONDITION. NGC chosen, CSV says 'Ungraded'. Grader/grade must flow to the saved coin and CSV.
f. CHECKLIST DEDUP must compare against OWNED coins (collection), not only review_queue.

## Tests
One regression test per item (a-f). For a/b/c use 092052 expected rows: 15 rows with correct quantities (halves qty 2), sets mapped, no supply rows. No real collection values in fixtures.

## No change
GreySheet CPG attribution text is acceptable.

## Rules (same as NET-393)
Keep importer auth + config/ebay rules; don't touch the beta_feedback rules extra (note it). Analyzer clean, version 8.18.13, one GEMINI38 review, NO deploy, nothing on main, explicit-path commits only, two strikes -> STOP. EXECUTE_DONE_P7_V8_18_13.md covers NET-393 + NET-394, then baton back to GROKCOS.
OVER
