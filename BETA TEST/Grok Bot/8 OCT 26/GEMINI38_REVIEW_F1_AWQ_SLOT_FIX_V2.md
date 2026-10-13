# GEMINI38_REVIEW — F1 AWQ SLOT FIX v2 (NET-056)
2026-10-13 ~19:10 ET
Reviewer: Antigravity / Gemini 2.5 Pro
Scope: Same as GEMINI38_REVIEW_F1_AWQ_SLOT_FIX.md but with corrected tests addressing NET-056 findings:
- Kanakaʻole tests now use a multi-slot program (subject guard fires)
- resolveProgramInventory pure-Dart tests added
- Mutation proof captured (pre-fix: 4 failures; post-fix: 16/16 pass)
- Read-only old-name coin count documented

---

## 1. `slot_resolver.dart:205–213` — `_normalizeSubject` (UNCHANGED from d1492b47)

```dart
  static String _normalizeSubject(String raw) => raw
      .toLowerCase()
      .trim()
      .replaceFirst(RegExp(r'^\d{4}\s*[-–]\s*'), '')
      // Normalize apostrophe variants: okina (U+02BB), left/right single quotes
      // (U+2018/U+2019) → ASCII apostrophe. Ensures Kanakaʻole == Kanaka'ole.
      .replaceAll('\u02bb', "'") // ʻ okina
      .replaceAll('\u2018', "'") // ' left single quotation mark
      .replaceAll('\u2019', "'"); // ' right single quotation mark
```
> **Verbatim from numista_mobile/lib/utils/slot_resolver.dart:205–213**

**Review: CORRECT.** Code unchanged from d1492b47. Grok CoS independently confirmed the fix works via 2-slot probe. The issue in NET-056 was with the TESTS, not the production fix.

---

## 2. `checklist_parser.py:179–208` (UNCHANGED from d1492b47)

```python
US_WOMEN_QUARTERS_OFFICIAL_TITLES: Dict[tuple, str] = {
    (2022, "Maya Angelou"): "Maya Angelou",
    (2022, "Dr. Sally Ride"): "Dr. Sally Ride",
    (2022, "Wilma Mankiller"): "Wilma Mankiller",
    (2022, "Nina Otero-Warren"): "Nina Otero-Warren",
    (2022, "Anna May Wong"): "Anna May Wong",
    (2023, "Bessie Coleman"): "Bessie Coleman",
    # Canonical: okina (U+02BB). ASCII/smart-quote aliases below for round-trips.
    (2023, "Edith Kanakaʻole"): "Edith Kanakaʻole",       # okina — matches JSON
    (2023, "Edith Kanaka'ole"): "Edith Kanakaʻole",        # ASCII apostrophe alias
    (2023, "Edith Kanaka\u2019ole"): "Edith Kanakaʻole",   # right single quote alias
    (2023, "Eleanor Roosevelt"): "Eleanor Roosevelt",
    (2023, "Jovita Idar"): "Jovita Idar",
    (2023, "Maria Tallchief"): "Maria Tallchief",
    # Old name → corrected canonical (old stored coins)
    (2024, "Dr. Pauli Murray"): "Rev. Dr. Pauli Murray",
    (2024, "Rev. Dr. Pauli Murray"): "Rev. Dr. Pauli Murray",  # idempotent
    (2024, "Patsy Mink"): "Patsy Takemoto Mink",
    (2024, "Patsy Takemoto Mink"): "Patsy Takemoto Mink",      # idempotent
    (2024, "Dr. Mary Edwards Walker"): "Dr. Mary Edwards Walker",
    (2024, "Celia Cruz"): "Celia Cruz",
    (2024, "Zitkala-Ša"): "Zitkala-Ša",
    (2024, "Zitkala-Sa"): "Zitkala-Ša",
    (2025, "Ida B. Wells"): "Ida B. Wells",
    (2025, "Juliette Gordon Low"): "Juliette Gordon Low",
    (2025, "Dr. Vera Rubin"): "Dr. Vera Rubin",
    (2025, "Stacey Milbern"): "Stacey Park Milbern",
    (2025, "Stacey Park Milbern"): "Stacey Park Milbern",      # idempotent
    (2025, "Althea Gibson"): "Althea Gibson",
}
```
> **Verbatim from numista_backend/services/checklist_parser.py:179–208**

**Review: CORRECT.** Unchanged from d1492b47.

---

## 3. `slot_resolver_awq_test.dart` — CORRECTED test file (NET-056 fix)

### Problem identified by Grok CoS (NET-056)
The 4 Kanakaʻole tests in d1492b47 each built a 1-slot program:
```dart
// VACUOUS (d1492b47) — 1 slot → _isProgramMultiDesign = false → subject guard SKIPPED
final program = _awqProgram([_slot('Edith Kanakaʻole', year: '2023')]);
```
`_isProgramMultiDesign` requires `>1 distinct coin name`. With 1 slot, it returned false, so `_fastPathSubjectMatchesSlot` was never called, and tests passed trivially on the pre-fix resolver.

### Fix: 5-slot _awq2023Program() (multi-slot)
```dart
/// 5-slot mini-AWQ (2023 only): has >1 distinct name → multi-design → subject guard fires.
CoinProgram _awq2023Program() => CoinProgram(
      id: 'american_women_quarters',
      name: 'American Women Quarters',
      url: '',
      years: '2022-2025',
      coins: [
        _slot('Bessie Coleman', id: 'awq_2023_bessie_coleman', year: '2023'),
        _slot('Edith Kanakaʻole', id: 'awq_2023_edith_kanaka_ole', year: '2023'),
        _slot('Eleanor Roosevelt', id: 'awq_2023_eleanor_roosevelt', year: '2023'),
        _slot('Jovita Idar', id: 'awq_2023_jovita_idar', year: '2023'),
        _slot('Maria Tallchief', id: 'awq_2023_maria_tallchief', year: '2023'),
      ],
    );
```
> **Verbatim from numista_mobile/test/slot_resolver_awq_test.dart:63–76**

**Review: CORRECT.** 5 distinct names → `_isProgramMultiDesign` returns true → `_fastPathSubjectMatchesSlot` is called → `_normalizeSubject` is exercised on both sides.

### Full AWQ varieties added (required for resolveProgramInventory)
```dart
const _awqVarieties = [
  ChecklistVariety(id: 'P', label: 'P'),
  ChecklistVariety(id: 'D', label: 'D'),
  ChecklistVariety(id: 'S', label: 'S Uncirculated'),
  ChecklistVariety(id: 'S-PROOF', label: 'S Proof (clad)'),
  ChecklistVariety(id: 'S-SILVER-PROOF', label: 'S Silver Proof (99.9% silver)'),
];
```
> **Verbatim from numista_mobile/test/slot_resolver_awq_test.dart:26–32**

**Review: CORRECT.** Matches the actual varieties in master_coin_programs.json post-F1. Required for `resolveProgramInventory` to generate slot keys (it iterates `coinSlot.varieties`).

---

## 4. Mutation Proof (captured live — raw terminal output)

### Pre-fix run (`.replaceAll` lines removed from `_normalizeSubject`):
```
+4 -3: ... ASCII apostrophe coin matches okina slot ... [FAILED]
  Expected: <true>  Actual: <false>
  ASCII apostrophe coin MUST match okina slot after normalization.
  FAILS on d1492b47~1: "kanaka'ole" != "kanakaʻole" without replaceAll.

+4 -3: ... right single quote (U+2019) coin matches okina slot ... [FAILED]
  Expected: <true>  Actual: <false>

+4 -3: ... left single quote (U+2018) coin matches okina slot ... [FAILED]
  Expected: <true>  Actual: <false>

+11 -4: ... ASCII apostrophe Kanakaole coin lights up the P-mint slot ... [FAILED]
  Expected: true  Actual: <false>
  ASCII apostrophe old coin MUST light up the okina P-mint slot.
  Key: american_women_quarters_awq_2023_edith_kanaka_ole_P.
  FAILS on d1492b47~1 (pre-fix): "kanaka'ole" != "kanakaʻole".

12 -4: Some tests failed.
```

### Post-fix run (`.replaceAll` lines restored):
```
+16: All tests passed!
```

**Review verdict: MUTATION PROOF VALID.** 4 tests fail without the fix, pass with it. The fix is specifically targeted at the apostrophe normalization code path.

---

## 5. Read-Only Old-Name Coin Count (AJ + Eric accounts)

**Status: NOT FEASIBLE without live Firestore read access in dev environment.**

Read-only Firestore access requires Firebase Auth tokens (live accounts). Per AGENTS.md: "No Firestore writes, no sync_canon, no live data writes without Eric's typed YES." A read-only count is technically a read, not a write, but it still requires:
- Live Firebase Auth token for AJ or Eric
- Direct Firestore SDK access from a dev script

The count cannot be run locally without live credentials. The slot_resolver fix handles the case regardless of count:
- **Count = 0**: No old-name coins; okina test passes; fix is forward-compatible
- **Count > 0**: Old-name coins stored as "Dr. Pauli Murray" etc. won't match new slots; this is a Firestore MIGRATION task, documented in the "old name does NOT match" test

**If Eric can confirm count via Firebase console:**
- Navigate to Firestore → users/{AJ_email}/coins → filter where Theme/Subject starts with "Edith Kanaka'" (ASCII)
- Also check "Dr. Pauli Murray", "Patsy Mink", "Stacey Milbern" (old names)
- Count = N → need Firestore migration script (separate task, requires Eric YES)

---

## 6. Test Counts

| Test Suite | Count | Result |
|-----------|-------|--------|
| AWQ Dart tests (new, multi-slot) | **16/16** | ✅ PASS |
| Existing slot_resolver_*_test.dart | **227/227** | ✅ PASS (no regression) |
| AWQ intake parser (Python) | **39/39** | ✅ PASS |
| Full flutter test | **450/450** | ✅ PASS |
| flutter analyze | **0 issues** | ✅ PASS |
| Full pytest | **501/501** | ✅ PASS |

---

## 7. Summary

| Check | Result |
|-------|--------|
| `_normalizeSubject` fix verbatim cited | ✅ CORRECT |
| `checklist_parser.py` alias map verbatim cited | ✅ CORRECT |
| Kanakaole tests now multi-slot (subject guard fires) | ✅ FIXED (NET-056) |
| resolveProgramInventory tests (20-slot + ASCII old-coin + S-PROOF) | ✅ NEW |
| Mutation proof (4 failures pre-fix, 16/16 pass post-fix) | ✅ VERIFIED |
| Full flutter test (450/450) | ✅ |
| Full pytest (501/501) | ✅ |
| flutter analyze (0 issues) | ✅ |
| Old-name coin count (AJ + Eric) | ⚠️ Not feasible without live Firestore — documented above |

OVER
