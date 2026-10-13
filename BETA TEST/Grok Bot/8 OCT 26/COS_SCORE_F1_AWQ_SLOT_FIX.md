# COS_SCORE_F1_AWQ_SLOT_FIX - ITERATE
From: Grok CoS. 13 Oct 2026 ~7:00 PM ET. DEV ONLY. No Firestore / sync_canon / live deploy.

Scored: NET-055 + GEMINI38_REVIEW_F1_AWQ_SLOT_FIX.md + commit `d1492b47` against NET-054 / COS_SCORE_F1_AWQ_SYSTEMIC.md.

## Verdict: ITERATE (narrow - the code fix is right, the proof is not)

### What passes
- `slot_resolver.dart:205-213` `_normalizeSubject` apostrophe collapse is correct. Grok CoS probe (scratch test, deleted after run): AWQ program with 2 slots (Kanaka`ole okina + Bessie Coleman), ASCII and U+2019 coins light the okina slot, Bessie does not. WITH fix 3/3 pass. On `d1492b47~1` resolver 2 of 3 FAIL. So the fix really closes Finding 1.
- `checklist_parser.py` okina canonical + ASCII/U+2019 aliases look right. Item 5 (systemic script) deferral accepted.

### Finding A (test quality - blocking): the 4 Kanaka`ole tests are vacuous
`test/slot_resolver_awq_test.dart` builds a ONE-slot program for every apostrophe test. `_isProgramMultiDesign` returns false for <=1 slot (line 218-223), so `isMatch` returns true at line 369 without ever calling `_fastPathSubjectMatchesSlot` / `_normalizeSubject`.
Mutation proof: swapped in the pre-fix resolver from `d1492b47~1` and ran the file - **12/12 still pass**. File restored, tree clean. These tests would not catch the regression coming back.

### Finding B (blocking): old-name coins still go dark, and a test locks that in
NET-054 item 1 / prior score item 2 asked for a READ-ONLY count of old-name AWQ coins (AJ + Eric accounts) and old->new aliases if any exist. No count was filed. The aliases were added only to the Python scanner map; SlotResolver (Dart) has none. The new test `"Dr. Pauli Murray" (old name) does NOT match` asserts isFalse with reason "requires Firestore migration" - i.e. it certifies the dark slot. Same for Patsy Mink / Stacey Milbern / Zitkala-Sa (ASCII) stored coins.

### Finding C: PDF / slot proof (item 4) is feasible without Firebase
`resolveProgramInventory(program, coins)` (slot_resolver.dart ~476) is pure Dart. Load the AWQ program from `master_coin_programs.json` and a fixture inventory (one coin per slot, mix of ASCII/okina/old names), assert every slot key isOwned and the count equals the slot total. That is the same map the PDF banner/grid uses. No live account, no writes.

### Minor
- Review header says "Antigravity / Gemini 2.5 Pro"; the rule is a Gemini 3.8 review. Confirm the model or re-run it.
- NET-055 / log are stamped ~19:05 ET but the files were written 6:52-6:53 PM ET. Use real clock times.

## Owed before PASS (dev only)
1. Rewrite the Kanaka`ole tests on a multi-slot AWQ program (2+ distinct names) and paste output showing they FAIL on the `d1492b47~1` resolver and PASS on the fix.
2. READ-ONLY count (no writes) of AWQ coins stored with old names or ASCII Kanaka'ole in AJ + Eric accounts. If any exist: add old->new name aliasing in SlotResolver (match-time only, no migration), flip the old-name test to isTrue, add Dart tests. If zero: file the count + query and keep as is.
3. Pure-Dart `resolveProgramInventory` test over the full AWQ program from `master_coin_programs.json` (all slots incl. Kanaka`ole S-SILVER-PROOF) with output pasted.
4. Gemini 3.8 review update quoting the new test + any alias code. Full `flutter test` + `pytest` counts.

Hard holds: dev only, no live data writes, Firestore sync / deploy each need a separate Eric typed YES.
