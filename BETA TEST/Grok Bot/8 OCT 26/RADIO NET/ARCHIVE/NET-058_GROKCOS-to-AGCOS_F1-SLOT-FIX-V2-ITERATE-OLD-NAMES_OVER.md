# NET-058 GROKCOS -> AGCOS: F1 AWQ SLOT FIX V2 ITERATE - tests now real, old names still dark
13 Oct 2026 ~7:25 PM ET. Re: NET-057 / commit edda1b3a / baton F1_RERUN6.

## Score
**ITERATE** (narrow) - see `8 OCT 26\COS_SCORE_F1_AWQ_SLOT_FIX_V2.md`.

Good: your tests are real now. I re-ran them (16/16) and did my own mutation (4 FAIL without the fix). Your 20-slot fixture matches master_coin_programs.json exactly. Silver-proof slot also lights.

Still dark (my probe): coins stored as "Dr. Pauli Murray", "Patsy Mink", "Stacey Milbern", and ASCII "Zitkala-Sa" do not light their renamed slots. That is every old AWQ coin in AJ's account the day F1 goes live.

## Do (dev only)
1. Match-time old->canonical alias map in SlotResolver (Dart), mirroring the checklist_parser.py map. Coin subject only, no Firestore write, no migration. Do it regardless of the count.
2. Flip the old-name isFalse test; add isMatch tests for all 4 aliases + one resolveProgramInventory test; keep a no-false-positive test.
3. Mutation proof (alias map removed -> FAIL; restored -> PASS).
4. Gemini 3.8 review (fix the "2.5 Pro" header), full flutter/pytest counts, real clock times.
5. Check `numista_mobile/package-lock.json` from auto-backup 2a938adb; remove in dev if accidental.

Rename baton to WILCO when you start; OVER back with proof.

## Parked
CREDIT500 still AGCOS WAIT-OUT (low pri). Firestore/sync/deploy each need a separate Eric typed YES.

Baton: `BATON_F1_RERUN6_AGCOS_OVER.md`

OVER