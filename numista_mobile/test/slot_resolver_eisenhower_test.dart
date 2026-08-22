// ignore_for_file: lines_longer_than_80_chars
// Regression tests for Eisenhower Dollar (eisenhower_dollars) slot routing.
//
// Context:
//   - 1971/1972 S-mint: silver BU + silver proof only (no clad S proof).
//   - 1973/1974 S-mint: clad proof (S-PROOF) + silver BU + silver proof.
//   - 1976 S-mint: clad T1/T2 proof (S-PROOF-T1/T2) + silver BU + silver proof.
//   - 1977/1978 S-mint: clad proof only.
//   - T1/T2 have no type discriminator (Option B) — identical parity to P-T1/P-T2
//     and D-T1/D-T2 which also double-match on mint mark alone.
//   - All 32 slots confirmed. Banner = {owned} / 32.
//
// Run: flutter test test/slot_resolver_eisenhower_test.dart

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// ── Helpers ───────────────────────────────────────────────────────────────────
Map<String, dynamic> coin({
  required String year,
  String mint = '',
  String strikeType = '',
  String metal = '',
  String grade = '',
}) =>
    {
      'Year': year,
      'Mint Mark': mint,
      'Strike Type': strikeType,
      'Metal Content': metal,
      'Condition': grade,
    };

bool matches(Map<String, dynamic> coinMap, String slotId) =>
    SlotResolver.matchesVariety(
      coinMap,
      ChecklistVariety(id: slotId, label: slotId),
    );

// ── Tests ─────────────────────────────────────────────────────────────────────
void main() {
  // Test 1 — 1971-S silver proof (strike_type=PROOF) → S-SILVER-PROOF only
  group('Test 1 — 1971-S silver proof (strike_type=PROOF)', () {
    final c = coin(year: '1971', mint: 'S', strikeType: 'PROOF', metal: 'SILVER');
    test('S-SILVER-PROOF = true', () => expect(matches(c, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF = false (!isSilver gate)', () => expect(matches(c, 'S-PROOF'), isFalse));
    test('S-PROOF-T1 = false (!isSilver gate)', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
    test('S-SILVER = false (!isProof)', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 1b — 1971-S PR69 silver (empty strike_type) → S-SILVER-PROOF via grade
  group('Test 1b — 1971-S PR69 silver (empty strike_type)', () {
    final c = coin(year: '1971', mint: 'S', metal: 'SILVER', grade: 'PR69');
    test('S-SILVER-PROOF = true (isProof via grade)', () => expect(matches(c, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF-T1 = false (!isSilver)', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
    test('S-SILVER = false (!isProof)', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 2 — 1971-S silver BU (MS65) → S-SILVER only
  group('Test 2 — 1971-S silver BU (MS65)', () {
    final c = coin(year: '1971', mint: 'S', metal: 'SILVER', grade: 'MS65');
    test('S-SILVER = true', () => expect(matches(c, 'S-SILVER'), isTrue));
    test('S-SILVER-PROOF = false (!isProof)', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
    test('S-PROOF-T1 = false', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
  });

  // Test 3 — 1972-S silver proof → S-SILVER-PROOF only
  group('Test 3 — 1972-S silver proof', () {
    final c = coin(year: '1972', mint: 'S', strikeType: 'PROOF', metal: 'SILVER');
    test('S-SILVER-PROOF = true', () => expect(matches(c, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF-T1 = false (!isSilver)', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
    test('S-SILVER = false', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 4 — 1972-S silver BU → S-SILVER only
  group('Test 4 — 1972-S silver BU', () {
    final c = coin(year: '1972', mint: 'S', metal: 'SILVER', grade: 'MS63');
    test('S-SILVER = true', () => expect(matches(c, 'S-SILVER'), isTrue));
    test('S-SILVER-PROOF = false', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
  });

  // Test 5 — 1972-S clad (no metal field) → no S slot owns it
  // No clad S proof exists for 1972; a 1972-S clad coin owns nothing.
  group('Test 5 — 1972-S clad (no metal field) → no S slot', () {
    final c = coin(year: '1972', mint: 'S');
    test('S-PROOF = false (no 1972 clad S proof slot)', () => expect(matches(c, 'S-PROOF'), isFalse));
    test('S-SILVER = false (not silver)', () => expect(matches(c, 'S-SILVER'), isFalse));
    test('S-SILVER-PROOF = false', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
  });

  // Test 6 — 1973-S clad proof (no metal) → S-PROOF only
  group('Test 6 — 1973-S clad proof (no metal)', () {
    final c = coin(year: '1973', mint: 'S', strikeType: 'PROOF');
    test('S-PROOF = true', () => expect(matches(c, 'S-PROOF'), isTrue));
    test('S-SILVER-PROOF = false (not silver)', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
    test('S-SILVER = false', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 7 — 1973-S silver proof → S-SILVER-PROOF only
  group('Test 7 — 1973-S silver proof', () {
    final c = coin(year: '1973', mint: 'S', strikeType: 'PROOF', metal: 'SILVER');
    test('S-SILVER-PROOF = true', () => expect(matches(c, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF = false (!isSilver)', () => expect(matches(c, 'S-PROOF'), isFalse));
  });

  // Test 8 — 1976-S silver BU (T1 only) → S-SILVER only
  group('Test 8 — 1976-S silver BU (T1 only)', () {
    final c = coin(year: '1976', mint: 'S', metal: 'SILVER', grade: 'MS65');
    test('S-SILVER = true', () => expect(matches(c, 'S-SILVER'), isTrue));
    test('S-PROOF-T1 = false (!isSilver gate)', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
    test('S-PROOF-T2 = false (!isSilver gate)', () => expect(matches(c, 'S-PROOF-T2'), isFalse));
    test('S-SILVER-PROOF = false (!isProof)', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
  });

  // Test 9 — 1976-S silver proof → S-SILVER-PROOF only
  group('Test 9 — 1976-S silver proof', () {
    final c = coin(year: '1976', mint: 'S', strikeType: 'PROOF', metal: 'SILVER');
    test('S-SILVER-PROOF = true', () => expect(matches(c, 'S-SILVER-PROOF'), isTrue));
    test('S-PROOF-T1 = false (!isSilver)', () => expect(matches(c, 'S-PROOF-T1'), isFalse));
    test('S-PROOF-T2 = false (!isSilver)', () => expect(matches(c, 'S-PROOF-T2'), isFalse));
    test('S-SILVER = false (!isProof)', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 10 — 1976-S clad proof → S-PROOF-T1 AND S-PROOF-T2 (Option B parity)
  // No type discriminator. Known parity with P-T1/P-T2 and D-T1/D-T2.
  group('Test 10 — 1976-S clad proof → both S-PROOF-T1 and S-PROOF-T2 (Option B)', () {
    final c = coin(year: '1976', mint: 'S', strikeType: 'PROOF');
    test('S-PROOF-T1 = true (double-match, Option B)', () => expect(matches(c, 'S-PROOF-T1'), isTrue));
    test('S-PROOF-T2 = true (double-match, Option B)', () => expect(matches(c, 'S-PROOF-T2'), isTrue));
    test('S-SILVER-PROOF = false (not silver)', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
    test('S-SILVER = false', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 11 — 1977-S clad proof → S-PROOF only
  group('Test 11 — 1977-S clad proof', () {
    final c = coin(year: '1977', mint: 'S', strikeType: 'PROOF');
    test('S-PROOF = true', () => expect(matches(c, 'S-PROOF'), isTrue));
    test('S-SILVER-PROOF = false', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
    test('S-SILVER = false', () => expect(matches(c, 'S-SILVER'), isFalse));
  });

  // Test 12 — startsWith fix: 1976-S PR67 clad never hits S-SILVER-PROOF
  // grade PR67 -> isProof=true; no metal field -> isSilver=false
  // startsWith('S-PROOF-') keeps it in the !isSilver branch.
  group('Test 12 — startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF', () {
    final c = coin(year: '1976', mint: 'S', grade: 'PR67');
    test('S-PROOF-T1 = true (isProof && !isSilver)', () => expect(matches(c, 'S-PROOF-T1'), isTrue));
    test('S-SILVER-PROOF = false (isSilver is false)', () => expect(matches(c, 'S-SILVER-PROOF'), isFalse));
  });
}
