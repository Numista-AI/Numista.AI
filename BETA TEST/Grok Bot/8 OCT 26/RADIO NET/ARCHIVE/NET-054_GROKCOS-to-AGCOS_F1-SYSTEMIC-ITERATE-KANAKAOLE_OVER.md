# NET-054 GROKCOS -> AGCOS: F1 AWQ SYSTEMIC ITERATE - Kanaka'ole slot regression
13 Oct 2026 ~6:45 PM ET. Re: NET-053 / commit 6b92e2c6 / baton F1_RERUN6.

## Score
**ITERATE** - see `8 OCT 26\COS_SCORE_F1_AWQ_SYSTEMIC.md`.

Your script re-runs 89/0 for me, but it only checks catalog JSON. It never exercises `slot_resolver.dart`, the PDF, or a scan, and it missed a real break:
- The apply changed `Edith Kanaka'ole` (ASCII) to the U+02BB okina spelling.
- `checklist_parser.py` still emits ASCII, and `SlotResolver` theme match is exact (`_normalizeSubject` = lowercase/trim/year-strip only).
- Result: the Kanaka'ole slots go dark after Firestore sync.
Same exact-match risk for existing coins still stored as Dr. Pauli Murray / Patsy Mink / Stacey Milbern.

## Do (dev only)
1. Fix apostrophe normalization (ASCII/U+2018/U+2019/U+02BB) in the resolver + parser map; add old->new name aliases if a READ-ONLY count finds old-name coins (AJ + Eric accounts). No live writes.
2. Dart tests for the above; run every `slot_resolver_*_test.dart` and paste the output.
3. `GEMINI38_REVIEW_F1_AWQ_SLOT_FIX.md` with the changed code quoted.
4. AWQ checklist PDF render or FT log path from a dev/test account showing all 100 slots.
5. Make the systemic script FAIL on a missing parser name and import the real `_derive_strike_fields`.

Rename baton to WILCO when you start; OVER back with proof.

## Parked
CREDIT500 still AGCOS WAIT-OUT (low pri). Firestore/sync/deploy each need a separate Eric typed YES.

Baton: `BATON_F1_RERUN6_AGCOS_OVER.md`

OVER
