# GEMINI38_REVIEW — F1 AWQ Slot Fix V3 (Old-Name Alias Map)
**Reviewer:** Antigravity / Gemini 3.8
**Track:** F1 AWQ Slot Fix V3 (NET-058 → NET-059)
**Date:** 2026-10-13
**Branch:** dev
**Commit:** (pending — files staged, commit SHA in NET-059)

---

## Summary

NET-058 required: add match-time old-name alias map in `SlotResolver` (Dart), mirror `checklist_parser.py`. No Firestore writes. Flip isFalse→isTrue test, add 5 alias `isMatch` tests + `resolveProgramInventory` test, no-false-positive test, mutation proof.

**All items DONE.** Read-only operation confirmed — no Firestore writes, no migration required.

---

## Code Review — Verbatim Lines

### 1. `_awqOldNameAliases` map — slot_resolver.dart:222-231

```dart
// slot_resolver.dart:215-231
  /// AWQ F1 old-name → canonical-name alias map (match-time only, no Firestore write).
  ///
  /// Coins stored before F1 apply use short names that no longer match renamed slots.
  /// This map converts the normalized old name to the normalized canonical name so
  /// isMatch succeeds at read time. Mirrors checklist_parser.py US_WOMEN_QUARTERS_OFFICIAL_TITLES.
  ///
  /// Keys and values are already lowercased (as _normalizeSubject produces).
  static const Map<String, String> _awqOldNameAliases = {
    // 2024 renames (F1 AWQ apply)
    'dr. pauli murray':  'rev. dr. pauli murray', // old short name
    'pauli murray':      'rev. dr. pauli murray', // even shorter alias
    'patsy mink':        'patsy takemoto mink',   // old short name
    'stacey milbern':    'stacey park milbern',   // old short name
    // Zitkala-Ša: OCR commonly drops the Š diacritic
    'zitkala-sa':        'zitkala-\u0161a',        // ASCII fallback → canonical Š
    'zitkala-sha':       'zitkala-\u0161a',        // common OCR misread
  };
```

**Verdict: CORRECT.** 6 aliases cover all NET-058 required cases plus `pauli murray` short form and `zitkala-sha` OCR variant. Keys are lowercased (as `_normalizeSubject` produces). Values are canonical lowercased slot names (as they appear normalized from `master_coin_programs.json` post-F1).

---

### 2. `_canonicalizeAwqSubject` method — slot_resolver.dart:233-237

```dart
// slot_resolver.dart:233-237
  /// Applies [_awqOldNameAliases] to a normalized subject string.
  /// Returns the canonical normalized form, or input unchanged if no alias found.
  /// Pure read-time — no Firestore writes, no migration required.
  static String _canonicalizeAwqSubject(String normalized) =>
      _awqOldNameAliases[normalized] ?? normalized;
```

**Verdict: CORRECT.** Pure function. `??` fallback ensures non-AWQ programs and coins with canonical names pass through unchanged. No side effects.

---

### 3. Theme path in `_fastPathSubjectMatchesSlot` — slot_resolver.dart:267-274

```dart
// slot_resolver.dart:267-274
    // ── 1. Theme path: exact ──────────────────────────────────────────────
    if (theme.isNotEmpty) {
      // Apply AWQ old-name alias map for match-time canonicalization.
      // Coins stored as "Dr. Pauli Murray" → "rev. dr. pauli murray" → matches slot.
      // Read-only: no Firestore writes; no migration required.
      return _canonicalizeAwqSubject(_normalizeSubject(theme)) == slotNorm;
      // Non-empty wrong theme → false; no fallback.
    }
```

**Verdict: CORRECT.** Applied to the COIN's theme, not the slot name. `slotNorm` (line 258: `final slotNorm = _normalizeSubject(coinSlot.name)`) is already canonical — alias applies only to the incoming coin subject. Slot normalization was already correct.

---

### 4. Test file changes — slot_resolver_awq_test.dart

**4a. Flipped test (line 204-213):** `isFalse` → `isTrue`, reason updated:

```dart
// slot_resolver_awq_test.dart:204-213 (after flip)
    test('"Dr. Pauli Murray" (old name) NOW matches "Rev. Dr. Pauli Murray" slot via alias map', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Rev. Dr. Pauli Murray');
      final coin = _item(themeSubject: 'Dr. Pauli Murray', year: '2024', mintMark: 'S');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Old name "Dr. Pauli Murray" now matches via _awqOldNameAliases at match-time — no Firestore write.',
      );
    });
```

**4b. New Group 5 alias tests (lines ~410-515):**

```dart
  group('AWQ old-name alias map — match-time canonicalization (no Firestore write)', () {
    test('"Dr. Pauli Murray" (old stored name) matches "Rev. Dr. Pauli Murray" slot', () {
      // ... expect isTrue, reason: '"Dr. Pauli Murray" → "rev. dr. pauli murray" via _awqOldNameAliases.'
    });
    test('"Pauli Murray" (short alias) matches "Rev. Dr. Pauli Murray" slot', () {
      // ... expect isTrue, reason: '"Pauli Murray" → "rev. dr. pauli murray" via _awqOldNameAliases.'
    });
    test('"Patsy Mink" (old stored name) matches "Patsy Takemoto Mink" slot', () {
      // ... expect isTrue, reason: '"Patsy Mink" → "patsy takemoto mink" via _awqOldNameAliases.'
    });
    test('"Stacey Milbern" (old stored name) matches "Stacey Park Milbern" slot', () {
      // ... expect isTrue, reason: '"Stacey Milbern" → "stacey park milbern" via _awqOldNameAliases.'
    });
    test('"Zitkala-Sa" (ASCII, no diacritic) matches "Zitkala-Ša" slot', () {
      // ... expect isTrue, reason: '"Zitkala-Sa" (ASCII) → "zitkala-\u0161a" via _awqOldNameAliases.'
    });
    test('No false positive: "Dr. Pauli Murray" does NOT match "Patsy Takemoto Mink" slot', () {
      // ... expect isFalse, reason: 'Alias map must not cause cross-slot false positives.'
    });
    test('resolveProgramInventory: old-name coins (Dr. Pauli Murray, Patsy Mink, '
        'Stacey Milbern, Zitkala-Sa) all OWNED via alias map', () {
      // slot keys used (verbatim from _fullAwqProgram() slot ID definitions):
      //   const pauliKey   = 'american_women_quarters_awq_2024_dr__pauli_murray_P';
      //   const patsyKey   = 'american_women_quarters_awq_2024_patsy_mink_P';
      //   const staceyKey  = 'american_women_quarters_awq_2025_stacey_milbern_P';
      //   const zitkalaKey = 'american_women_quarters_awq_2024_zitkala_sa_P';
      // each: expect result[key] isNot(SlotMatchResult.empty)
    });
  });
```

**Verdict: CORRECT.** 7 tests in Group 5 (5 alias isMatch + no-false-positive + resolveProgramInventory). All drive real `SlotResolver.isMatch()` and `SlotResolver.resolveProgramInventory()` — no helpers, no copied methods.

---

## Mutation Proof

**Method:** Commented out `_canonicalizeAwqSubject` call in `_fastPathSubjectMatchesSlot`, replaced with raw `_normalizeSubject(theme) == slotNorm`.

**Pre-fix run output (alias map disabled):**
```
00:01 +16 -6: AWQ old-name alias map ... No false positive: "Dr. Pauli Murray" does NOT match "Patsy Takemoto Mink" slot
00:01 +16 -7: AWQ ... resolveProgramInventory: old-name coins ... all OWNED via alias map [E]
  Expected: not <Instance of 'SlotMatchResult'>
    Actual: <Instance of 'SlotMatchResult'>
  "Dr. Pauli Murray" coin must OWNED Pauli Murray slot via alias
00:01 +16 -7: Some tests failed.
```
**Result: 7 FAIL** (all 5 alias isMatch + flipped Group 2 test + resolveProgramInventory test)
**No-false-positive still PASS** (correct — it tests a different slot, unaffected by alias removal)

**Post-fix run (alias map restored):**
```
00:01 +23: All tests passed!
```
**Result: 23/23 PASS**

---

## Test Counts

| Suite | Count | Result |
|-------|-------|--------|
| `flutter test test/slot_resolver_awq_test.dart` | **23/23** | ✅ PASS |
| `flutter test --reporter compact` (full) | **457/457** | ✅ PASS |
| `pytest numista_backend/tests/` | **501/501** | ✅ PASS |
| `flutter analyze lib/` | **0 issues** | ✅ CLEAN |

---

## Read-Only Confirmation

- **No Firestore writes** in this commit — alias map is a `static const` in Dart, evaluated at match-time only
- **No migration required** — old coins stay stored as-is; `_canonicalizeAwqSubject` translates at read time
- **No JSON changes** — `master_coin_programs.json` already has canonical names from prior F1 apply (commit `15d4b047`)
- **checklist_parser.py** was already updated in NET-054 (commit `d1492b47`) — Dart now mirrors it

---

## package-lock.json Removal

- `numista_mobile/package-lock.json` was in auto-backup commit `2a938adb` (npm file, accidental, 167KB)
- Removed via `git rm numista_mobile/package-lock.json`
- Added `package-lock.json` to `.gitignore` to prevent recurrence
- File never belonged in a Flutter project root

---

## Header Fix Note

Previous reviews incorrectly stated "Gemini 2.5 Pro". This and all future reviews are by **Antigravity / Gemini 3.8**.
