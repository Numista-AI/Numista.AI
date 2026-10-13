// Numista.AI — Slot Resolver AWQ Apostrophe/Okina Normalization Tests
// Tests _normalizeSubject's handling of okina (U+02BB), smart quotes,
// and the AWQ name changes (Rev. Dr. Pauli Murray, Patsy Takemoto Mink,
// Stacey Park Milbern, Edith Kanakaʻole) introduced in F1 RERUN6 apply.
//
// All tests are pure Dart — no Firebase, no network, no platform channels.
// ignore_for_file: use_null_aware_elements

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// ─── Helper builders ──────────────────────────────────────────────────────────

CoinProgram _awqProgram(List<ProgramCoin> coins) => CoinProgram(
      id: 'american_women_quarters',
      name: 'American Women Quarters',
      url: '',
      years: '2022-2025',
      coins: coins,
    );

ProgramCoin _slot(String name, {String? year}) => ProgramCoin(
      id: name.toLowerCase().replaceAll(' ', '_').replaceAll("'", '').replaceAll('ʻ', ''),
      name: name,
      varieties: const [],
      year: year,
    );

Map<String, dynamic> _item({
  required String themeSubject,
  String year = '2023',
  String mintMark = 'P',
}) =>
    {
      'program_id': 'american_women_quarters',
      'Program/Series': 'American Women Quarters',
      'Theme/Subject': themeSubject,
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': 'Quarter',
    };

// ─── Tests ────────────────────────────────────────────────────────────────────

void main() {
  group('_normalizeSubject apostrophe normalization — Kanakaʻole', () {
    // After F1: slot name in JSON/Firestore is "Edith Kanakaʻole" (U+02BB okina).
    // Old user coins may be stored as "Edith Kanaka'ole" (ASCII ').
    // _normalizeSubject must normalize both to the same string.

    test('ASCII apostrophe coin matches okina slot name', () {
      final program = _awqProgram([_slot('Edith Kanakaʻole', year: '2023')]);
      final coin = _item(themeSubject: "Edith Kanaka'ole", year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, _slot('Edith Kanakaʻole', year: '2023')),
        isTrue,
        reason: 'ASCII apostrophe coin must match okina slot after normalization',
      );
    });

    test('okina coin matches okina slot (round-trip)', () {
      final program = _awqProgram([_slot('Edith Kanakaʻole', year: '2023')]);
      final coin = _item(themeSubject: 'Edith Kanakaʻole', year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, _slot('Edith Kanakaʻole', year: '2023')),
        isTrue,
        reason: 'Okina-to-okina must match',
      );
    });

    test('right single quote (U+2019) coin matches okina slot', () {
      final program = _awqProgram([_slot('Edith Kanakaʻole', year: '2023')]);
      // U+2019 RIGHT SINGLE QUOTATION MARK
      final coin = _item(themeSubject: 'Edith Kanaka\u2019ole', year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, _slot('Edith Kanakaʻole', year: '2023')),
        isTrue,
        reason: 'Right single quote must normalize to match okina slot',
      );
    });

    test('left single quote (U+2018) coin matches okina slot', () {
      final program = _awqProgram([_slot('Edith Kanakaʻole', year: '2023')]);
      // U+2018 LEFT SINGLE QUOTATION MARK
      final coin = _item(themeSubject: 'Edith Kanaka\u2018ole', year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, _slot('Edith Kanakaʻole', year: '2023')),
        isTrue,
        reason: 'Left single quote must normalize to match okina slot',
      );
    });
  });

  group('AWQ F1 name changes — new canonical names match new slots', () {
    test('"Rev. Dr. Pauli Murray" coin matches new slot', () {
      final slot = _slot('Rev. Dr. Pauli Murray', year: '2024');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Rev. Dr. Pauli Murray', year: '2024', mintMark: 'S');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('"Dr. Pauli Murray" (old name) does NOT match "Rev. Dr. Pauli Murray" slot', () {
      // _isProgramMultiDesign requires >1 distinct slot name to activate the G3b
      // subject guard. Use a 2-slot program so the gate fires.
      final revDrPauliSlot = _slot('Rev. Dr. Pauli Murray', year: '2024');
      final program = _awqProgram([
        revDrPauliSlot,
        _slot('Patsy Takemoto Mink', year: '2024'), // second slot → multi-design
      ]);
      final coin = _item(themeSubject: 'Dr. Pauli Murray', year: '2024', mintMark: 'S');
      expect(SlotResolver.isMatch(coin, program, revDrPauliSlot), isFalse,
          reason: 'Old name "Dr. Pauli Murray" must NOT match "Rev. Dr. Pauli Murray" slot — requires Firestore migration');
    });

    test('"Patsy Takemoto Mink" coin matches new slot', () {
      final slot = _slot('Patsy Takemoto Mink', year: '2024');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Patsy Takemoto Mink', year: '2024', mintMark: 'P');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('"Stacey Park Milbern" coin matches new slot', () {
      final slot = _slot('Stacey Park Milbern', year: '2025');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Stacey Park Milbern', year: '2025', mintMark: 'D');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('"Zitkala-Ša" coin matches slot', () {
      final slot = _slot('Zitkala-Ša', year: '2024');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Zitkala-Ša', year: '2024', mintMark: 'S');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });
  });

  group('Apostrophe normalization does not break existing coins', () {
    test('Maya Angelou matches (no apostrophe chars)', () {
      final slot = _slot('Maya Angelou', year: '2022');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Maya Angelou', year: '2022');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('Nina Otero-Warren matches (hyphen preserved, no apostrophe issue)', () {
      final slot = _slot('Nina Otero-Warren', year: '2022');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Nina Otero-Warren', year: '2022', mintMark: 'D');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('Eleanor Roosevelt matches (no special chars)', () {
      final slot = _slot('Eleanor Roosevelt', year: '2023');
      final program = _awqProgram([slot]);
      final coin = _item(themeSubject: 'Eleanor Roosevelt', year: '2023', mintMark: 'P');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });
  });
}
