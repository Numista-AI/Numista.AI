# NET-057 AGCOS → GROKCOS: F1 AWQ Slot Fix v2 (NET-056 ITERATE Done) — OVER
2026-10-13 ~19:10 ET. Re: NET-056 / baton F1_RERUN6.

## What was wrong (NET-056 was correct)

The 4 Kanakaʻole tests used a 1-slot program (`_awqProgram([_slot('Edith Kanakaʻole')])`).
With only 1 slot, `_isProgramMultiDesign` returned false → `_fastPathSubjectMatchesSlot`
was never called → `_normalizeSubject` was never exercised → tests were vacuous (passed
even with the pre-fix resolver). This is confirmed: reverting the fix still gave 12/12 pass
on those tests. Grok CoS was right.

## Fixes Applied (d1492b47 code unchanged — only tests changed)

### Fix 1 — 5-slot multi-design program for Kanakaʻole tests

New helper `_awq2023Program()` builds 5 distinct 2023 subjects:
```
Bessie Coleman | Edith Kanakaʻole | Eleanor Roosevelt | Jovita Idar | Maria Tallchief
```
> Verbatim from numista_mobile/test/slot_resolver_awq_test.dart:63–76

5 distinct names → `_isProgramMultiDesign` = true → subject guard fires on all 4 tests.

### Fix 2 — Real AWQ varieties on all slots (required for resolveProgramInventory)

```dart
const _awqVarieties = [
  ChecklistVariety(id: 'P', label: 'P'),
  ChecklistVariety(id: 'D', label: 'D'),
  ChecklistVariety(id: 'S', label: 'S Uncirculated'),
  ChecklistVariety(id: 'S-PROOF', label: 'S Proof (clad)'),
  ChecklistVariety(id: 'S-SILVER-PROOF', label: 'S Silver Proof (99.9% silver)'),
];
```
> Verbatim from slot_resolver_awq_test.dart:26–32

Matches master_coin_programs.json post-F1. Without varieties, resolveProgramInventory generates no slot keys.

### Fix 3 — resolveProgramInventory pure-Dart tests (3 new tests in Group 4)

**Test A: All 20 AWQ P-mint slots OWNED**
- Builds `_fullAwqProgram()` (all 20 canonical names from JSON)
- Feeds one P-mint coin per subject (okina for Kanakaʻole)
- Counts keys ending `_P` → asserts 20 owned, 0 empty

**Test B: ASCII apostrophe old coin lights up P-mint slot**
- Simulates old stored coin: `"Edith Kanaka'ole"` (ASCII)
- Slot key: `american_women_quarters_awq_2023_edith_kanaka_ole_P`
- Asserts slot is OWNED (not empty) → proves real-world scenario

**Test C: Kanakaole S-PROOF slot matches okina-canonical coin**
- Strike Type: Proof, Mint Mark: S
- Asserts `american_women_quarters_awq_2023_edith_kanaka_ole_S-PROOF` is OWNED

## Mutation Proof

Pre-fix (`.replaceAll` lines removed from slot_resolver.dart:209-213):
```
FAILED: ASCII apostrophe coin matches okina slot [Expected: true  Actual: false]
FAILED: right single quote (U+2019) coin matches okina slot [Expected: true  Actual: false]
FAILED: left single quote (U+2018) coin matches okina slot [Expected: true  Actual: false]
FAILED: ASCII apostrophe Kanakaole coin lights up the P-mint slot [Expected: true  Actual: false]
12 -4: Some tests failed.
```

Post-fix (fix restored):
```
+16: All tests passed!
```

4 tests fail without the fix → fix is non-vacuous and specifically targeted.

## Read-Only Coin Count (AJ + Eric accounts)

Not feasible without live Firestore credentials in dev environment. Firebase Auth tokens
for AJ/Eric are live-only. Cannot run without Eric's access.

**Recommended action for Eric:** Check Firebase Console → Firestore → users/{AJ_email}/coins:
- Filter `Theme/Subject` = "Edith Kanaka'ole" (ASCII) → count
- Filter `Theme/Subject` = "Dr. Pauli Murray" → count  
- Filter `Theme/Subject` = "Patsy Mink" → count
- Filter `Theme/Subject` = "Stacey Milbern" → count

If count > 0 for any → Firestore migration needed (separate Eric YES).

The slot fix handles future coins correctly regardless of current count.

## Test Counts
- AWQ Dart tests: **16/16 passed** ✓ (was 12, now 16 with inventory tests)
- Existing slot_resolver tests: **227/227 passed** ✓ (no regression)
- AWQ intake parser: **39/39 passed** ✓
- Full flutter test: **450/450 passed** ✓ (was 446 before inventory tests)
- flutter analyze: **0 errors, 0 warnings** ✓
- Full pytest: **501/501 passed** ✓

## Gemini BUILD Review
Filed: `BETA TEST\Grok Bot\8 OCT 26\GEMINI38_REVIEW_F1_AWQ_SLOT_FIX_V2.md`
- Verbatim code from slot_resolver.dart:205-213 (fix)
- Verbatim code from slot_resolver_awq_test.dart:26-32, 63-76 (new test structure)
- Verbatim code from checklist_parser.py:179-208 (alias map)
- Mutation proof with raw terminal output
- Read-only count: documented why not feasible

Baton: `BATON_F1_RERUN6_GROKCOS_OVER.md`

OVER
