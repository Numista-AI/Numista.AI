// Numista.AI — Slot Resolver AWQ Apostrophe/Okina Normalization Tests
// Tests _normalizeSubject's handling of okina (U+02BB), smart quotes,
// and the AWQ name changes (Rev. Dr. Pauli Murray, Patsy Takemoto Mink,
// Stacey Park Milbern, Edith Kanakaʻole) introduced in F1 RERUN6 apply.
//
// All tests are pure Dart — no Firebase, no network, no platform channels.
//
// MUTATION PROOF (NET-056 requirement):
// Before fix (d1492b47~1): _normalizeSubject had no replaceAll calls:
//   static String _normalizeSubject(String raw) => raw
//       .toLowerCase().trim()
//       .replaceFirst(RegExp(r'^\d{4}\s*[-–]\s*'), '');
// With the pre-fix code, "kanakaʻole" (okina) != "kanaka'ole" (ASCII),
// so _fastPathSubjectMatchesSlot returns false for ASCII-apostrophe coins.
// To verify: revert the 3 .replaceAll lines in slot_resolver.dart:209-213
// and re-run — all 4 Kanakaʻole multi-slot tests FAIL with:
//   Expected: <true>  Actual: <false>
// The okina round-trip test and no-false-positive test still pass (they
// don't rely on normalization), proving the fix is specifically targeted.
//
// ignore_for_file: use_null_aware_elements

import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/program_model.dart';
import 'package:numista_ai/utils/slot_resolver.dart';

// ─── Helper builders ──────────────────────────────────────────────────────────

/// Standard AWQ varieties — matches master_coin_programs.json post F1 apply.
const _awqVarieties = [
  ChecklistVariety(id: 'P', label: 'P'),
  ChecklistVariety(id: 'D', label: 'D'),
  ChecklistVariety(id: 'S', label: 'S Uncirculated'),
  ChecklistVariety(id: 'S-PROOF', label: 'S Proof (clad)'),
  ChecklistVariety(id: 'S-SILVER-PROOF', label: 'S Silver Proof (99.9% silver)'),
];

/// Builds the full 20-slot AWQ program matching master_coin_programs.json
/// (post F1 apply, commit d1492b47). 20 distinct names → multi-design program.
/// _isProgramMultiDesign returns true → G3b subject guard fires on all tests.
CoinProgram _fullAwqProgram() {
  final slots = [
    // 2022
    _slot('Maya Angelou', id: 'awq_2022_maya_angelou', year: '2022'),
    _slot('Dr. Sally Ride', id: 'awq_2022_dr__sally_ride', year: '2022'),
    _slot('Wilma Mankiller', id: 'awq_2022_wilma_mankiller', year: '2022'),
    _slot('Nina Otero-Warren', id: 'awq_2022_nina_otero_warren', year: '2022'),
    _slot('Anna May Wong', id: 'awq_2022_anna_may_wong', year: '2022'),
    // 2023
    _slot('Bessie Coleman', id: 'awq_2023_bessie_coleman', year: '2023'),
    _slot('Edith Kanakaʻole', id: 'awq_2023_edith_kanaka_ole', year: '2023'), // okina U+02BB
    _slot('Eleanor Roosevelt', id: 'awq_2023_eleanor_roosevelt', year: '2023'),
    _slot('Jovita Idar', id: 'awq_2023_jovita_idar', year: '2023'),
    _slot('Maria Tallchief', id: 'awq_2023_maria_tallchief', year: '2023'),
    // 2024
    _slot('Rev. Dr. Pauli Murray', id: 'awq_2024_dr__pauli_murray', year: '2024'),
    _slot('Patsy Takemoto Mink', id: 'awq_2024_patsy_mink', year: '2024'),
    _slot('Dr. Mary Edwards Walker', id: 'awq_2024_dr__mary_edwards_walker', year: '2024'),
    _slot('Celia Cruz', id: 'awq_2024_celia_cruz', year: '2024'),
    _slot('Zitkala-Ša', id: 'awq_2024_zitkala_sa', year: '2024'),
    // 2025
    _slot('Ida B. Wells', id: 'awq_2025_ida_b__wells', year: '2025'),
    _slot('Juliette Gordon Low', id: 'awq_2025_juliette_gordon_low', year: '2025'),
    _slot('Dr. Vera Rubin', id: 'awq_2025_dr__vera_rubin', year: '2025'),
    _slot('Stacey Park Milbern', id: 'awq_2025_stacey_milbern', year: '2025'),
    _slot('Althea Gibson', id: 'awq_2025_althea_gibson', year: '2025'),
  ];
  return CoinProgram(
    id: 'american_women_quarters',
    name: 'American Women Quarters',
    url: '',
    years: '2022-2025',
    coins: slots,
  );
}

/// 5-slot mini-AWQ (2023 only): has >1 distinct name → multi-design → subject guard fires.
/// Used for the 4 Kanakaʻole apostrophe tests to prove the subject guard is exercised.
CoinProgram _awq2023Program() => CoinProgram(
      id: 'american_women_quarters',
      name: 'American Women Quarters',
      url: '',
      years: '2022-2025',
      coins: [
        _slot('Bessie Coleman', id: 'awq_2023_bessie_coleman', year: '2023'),
        _slot('Edith Kanakaʻole', id: 'awq_2023_edith_kanaka_ole', year: '2023'), // okina
        _slot('Eleanor Roosevelt', id: 'awq_2023_eleanor_roosevelt', year: '2023'),
        _slot('Jovita Idar', id: 'awq_2023_jovita_idar', year: '2023'),
        _slot('Maria Tallchief', id: 'awq_2023_maria_tallchief', year: '2023'),
      ],
    );

ProgramCoin _slot(String name, {required String id, String? year}) => ProgramCoin(
      id: id,
      name: name,
      varieties: _awqVarieties, // real AWQ varieties — needed for resolveProgramInventory
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

/// Title-only coin — no Theme/Subject field.
/// Exercises the Title path (_fastPathSubjectMatchesSlot lines 276-320).
/// Grok CoS probe: "2024 Patsy Mink Quarter", "2025 Stacey Milbern Quarter" etc.
Map<String, dynamic> _titleItem({
  required String title,
  String year = '2024',
  String mintMark = 'P',
}) =>
    {
      'program_id': 'american_women_quarters',
      'Program/Series': 'American Women Quarters',
      'Title': title,          // ← Title path; NO Theme/Subject key
      'Year': year,
      'Mint Mark': mintMark,
      'Denomination': 'Quarter',
    };

// ─── Tests ────────────────────────────────────────────────────────────────────

void main() {
  // ===========================================================================
  // GROUP 1: Kanakaʻole apostrophe normalization — MULTI-SLOT program
  // These use a 5-slot 2023 AWQ program so _isProgramMultiDesign returns true
  // and the G3b subject guard (_fastPathSubjectMatchesSlot) fires.
  // On the pre-fix resolver (d1492b47~1), tests 1, 3, 4 FAIL because
  // "kanaka'ole" != "kanakaʻole" without normalization.
  // ===========================================================================

  group('_normalizeSubject apostrophe normalization — Kanakaʻole (multi-slot)', () {
    // The 5-slot _awq2023Program() has 5 distinct names → _isProgramMultiDesign = true
    // → _fastPathSubjectMatchesSlot is invoked → _normalizeSubject is called on both
    // the coin's Theme/Subject and the slot name.

    test('ASCII apostrophe coin matches okina slot [FAILS on d1492b47~1 pre-fix]', () {
      final program = _awq2023Program();
      final targetSlot = program.coins.firstWhere((s) => s.name.contains('Kanaka'));
      final coin = _item(themeSubject: "Edith Kanaka'ole", year: '2023'); // ASCII '
      expect(
        SlotResolver.isMatch(coin, program, targetSlot),
        isTrue,
        reason: 'ASCII apostrophe coin MUST match okina slot after normalization. '
            'FAILS on d1492b47~1: "kanaka\'ole" != "kanakaʻole" without replaceAll.',
      );
    });

    test('okina coin matches okina slot — round-trip idempotent', () {
      final program = _awq2023Program();
      final targetSlot = program.coins.firstWhere((s) => s.name.contains('Kanaka'));
      final coin = _item(themeSubject: 'Edith Kanakaʻole', year: '2023'); // U+02BB
      expect(
        SlotResolver.isMatch(coin, program, targetSlot),
        isTrue,
        reason: 'Okina-to-okina must match (round-trip idempotent).',
      );
    });

    test('right single quote (U+2019) coin matches okina slot [FAILS on d1492b47~1 pre-fix]', () {
      final program = _awq2023Program();
      final targetSlot = program.coins.firstWhere((s) => s.name.contains('Kanaka'));
      // U+2019 RIGHT SINGLE QUOTATION MARK — common in Word/PDF processors
      final coin = _item(themeSubject: 'Edith Kanaka\u2019ole', year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, targetSlot),
        isTrue,
        reason: 'U+2019 right single quote must normalize to match okina slot. '
            'FAILS on d1492b47~1.',
      );
    });

    test('left single quote (U+2018) coin matches okina slot [FAILS on d1492b47~1 pre-fix]', () {
      final program = _awq2023Program();
      final targetSlot = program.coins.firstWhere((s) => s.name.contains('Kanaka'));
      // U+2018 LEFT SINGLE QUOTATION MARK
      final coin = _item(themeSubject: 'Edith Kanaka\u2018ole', year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, targetSlot),
        isTrue,
        reason: 'U+2018 left single quote must normalize to match okina slot. '
            'FAILS on d1492b47~1.',
      );
    });

    test('ASCII apostrophe coin does NOT match Eleanor Roosevelt slot (no false positives)', () {
      final program = _awq2023Program();
      final eleanorSlot = program.coins.firstWhere((s) => s.name == 'Eleanor Roosevelt');
      final coin = _item(themeSubject: "Edith Kanaka'ole", year: '2023');
      expect(
        SlotResolver.isMatch(coin, program, eleanorSlot),
        isFalse,
        reason: 'Kanakaole coin must not match Eleanor Roosevelt slot — no false positives.',
      );
    });
  });

  // ===========================================================================
  // GROUP 2: AWQ F1 name changes — new canonical names match new slots
  // Full program (20 slots → multi-design → subject guard fires on all)
  // ===========================================================================

  group('AWQ F1 name changes — new canonical names match new slots', () {
    test('"Rev. Dr. Pauli Murray" coin matches new slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Rev. Dr. Pauli Murray');
      final coin = _item(themeSubject: 'Rev. Dr. Pauli Murray', year: '2024', mintMark: 'S');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

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

    test('"Patsy Takemoto Mink" coin matches new slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Patsy Takemoto Mink');
      final coin = _item(themeSubject: 'Patsy Takemoto Mink', year: '2024', mintMark: 'P');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('"Stacey Park Milbern" coin matches new slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Stacey Park Milbern');
      final coin = _item(themeSubject: 'Stacey Park Milbern', year: '2025', mintMark: 'D');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('"Zitkala-Ša" coin matches slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name.startsWith('Zitkala'));
      final coin = _item(themeSubject: 'Zitkala-Ša', year: '2024', mintMark: 'S');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });
  });

  // ===========================================================================
  // GROUP 3: No-regression — existing coins still match after normalization fix
  // ===========================================================================

  group('Apostrophe normalization does not break existing coins', () {
    test('Maya Angelou matches (no apostrophe chars)', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Maya Angelou');
      final coin = _item(themeSubject: 'Maya Angelou', year: '2022');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('Nina Otero-Warren matches (hyphen preserved, no apostrophe issue)', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Nina Otero-Warren');
      final coin = _item(themeSubject: 'Nina Otero-Warren', year: '2022', mintMark: 'D');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });

    test('Eleanor Roosevelt matches (no special chars)', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Eleanor Roosevelt');
      final coin = _item(themeSubject: 'Eleanor Roosevelt', year: '2023', mintMark: 'P');
      expect(SlotResolver.isMatch(coin, program, slot), isTrue);
    });
  });

  // ===========================================================================
  // GROUP 4: Pure-Dart resolveProgramInventory — all 20 AWQ slots
  // This is the "PDF proof" equivalent per NET-056. Exercises the same code
  // path as the live app (identical to what happens after checklist PDF scan)
  // without Firebase. All 20 AWQ subjects owned as P-mint coins.
  // ===========================================================================

  group('resolveProgramInventory — full AWQ program (pure Dart, no Firebase)', () {
    test('All 20 AWQ P-mint slots OWNED when all canonical coins present', () {
      final program = _fullAwqProgram();

      // One P-mint coin per AWQ subject — canonical names matching post-F1 JSON.
      // Kanakaʻole uses okina (the new canonical from master_coin_programs.json).
      final coins = <Map<String, dynamic>>[
        _item(themeSubject: 'Maya Angelou', year: '2022'),
        _item(themeSubject: 'Dr. Sally Ride', year: '2022'),
        _item(themeSubject: 'Wilma Mankiller', year: '2022'),
        _item(themeSubject: 'Nina Otero-Warren', year: '2022'),
        _item(themeSubject: 'Anna May Wong', year: '2022'),
        _item(themeSubject: 'Bessie Coleman', year: '2023'),
        _item(themeSubject: 'Edith Kanakaʻole', year: '2023'),    // okina U+02BB
        _item(themeSubject: 'Eleanor Roosevelt', year: '2023'),
        _item(themeSubject: 'Jovita Idar', year: '2023'),
        _item(themeSubject: 'Maria Tallchief', year: '2023'),
        _item(themeSubject: 'Rev. Dr. Pauli Murray', year: '2024'),
        _item(themeSubject: 'Patsy Takemoto Mink', year: '2024'),
        _item(themeSubject: 'Dr. Mary Edwards Walker', year: '2024'),
        _item(themeSubject: 'Celia Cruz', year: '2024'),
        _item(themeSubject: 'Zitkala-Ša', year: '2024'),
        _item(themeSubject: 'Ida B. Wells', year: '2025'),
        _item(themeSubject: 'Juliette Gordon Low', year: '2025'),
        _item(themeSubject: 'Dr. Vera Rubin', year: '2025'),
        _item(themeSubject: 'Stacey Park Milbern', year: '2025'),
        _item(themeSubject: 'Althea Gibson', year: '2025'),
      ];

      final result = SlotResolver.resolveProgramInventory(
        program: program,
        coins: coins,
      );

      // Count P-mint slots (variety id 'P') owned vs empty
      int ownedCount = 0;
      int emptyCount = 0;
      final emptySlots = <String>[];

      for (final entry in result.entries) {
        if (entry.key.endsWith('_P')) {
          if (entry.value == SlotMatchResult.empty) {
            emptyCount++;
            emptySlots.add(entry.key);
          } else {
            ownedCount++;
          }
        }
      }

      expect(
        emptyCount,
        0,
        reason: 'All 20 AWQ P-mint slots must be OWNED. '
            'Empty slots (would go dark after Firestore sync): $emptySlots. '
            'If Kanakaʻole is empty, apostrophe normalization is broken.',
      );
      expect(ownedCount, 20,
          reason: 'Expected 20 AWQ P-mint slots owned. Got: $ownedCount owned / $emptyCount empty. '
              'Empty: $emptySlots');
    });

    test('ASCII apostrophe Kanakaole coin lights up the P-mint slot (old-coin path)', () {
      // Simulates an old coin stored with ASCII apostrophe — must light up okina slot.
      // This is the exact scenario Grok CoS identified: after Firestore sync, old stored
      // coins have "Edith Kanaka'ole" (ASCII) but the slot is "Edith Kanakaʻole" (okina).
      // Without _normalizeSubject fix: slot goes dark. With fix: slot stays lit.
      final program = _fullAwqProgram();

      final coins = <Map<String, dynamic>>[
        _item(themeSubject: "Edith Kanaka'ole", year: '2023'), // ASCII ' — old stored coin
      ];

      final result = SlotResolver.resolveProgramInventory(
        program: program,
        coins: coins,
      );

      // The Kanakaʻole P-mint slot key
      const kanakaSlotKey = 'american_women_quarters_awq_2023_edith_kanaka_ole_P';
      final kanakaResult = result[kanakaSlotKey];

      expect(
        kanakaResult != null && kanakaResult != SlotMatchResult.empty,
        isTrue,
        reason: 'ASCII apostrophe old coin MUST light up the okina P-mint slot. '
            'Key: $kanakaSlotKey. Result: $kanakaResult. '
            'FAILS on d1492b47~1 (pre-fix): "kanaka\'ole" != "kanakaʻole".',
      );
    });

    test('Kanakaole S-PROOF slot also matches okina-canonical coin', () {
      // Confirms normalization works for proof variants too (not just P-mint).
      final program = _fullAwqProgram();

      final coins = <Map<String, dynamic>>[
        {
          'program_id': 'american_women_quarters',
          'Program/Series': 'American Women Quarters',
          'Theme/Subject': 'Edith Kanakaʻole', // okina
          'Year': '2023',
          'Mint Mark': 'S',
          'Strike Type': 'Proof',
          'Denomination': 'Quarter',
        }
      ];

      final result = SlotResolver.resolveProgramInventory(
        program: program,
        coins: coins,
      );

      const kanakaProofKey = 'american_women_quarters_awq_2023_edith_kanaka_ole_S-PROOF';
      final kanakaResult = result[kanakaProofKey];

      expect(
        kanakaResult != null && kanakaResult != SlotMatchResult.empty,
        isTrue,
        reason: 'Okina Kanakaʻole proof coin must match S-PROOF slot. '
            'Key: $kanakaProofKey. Result: $kanakaResult.',
      );
    });
  });

  // ===========================================================================
  // GROUP 5: AWQ old-name alias map — match-time canonicalization
  // No Firestore write, no migration. Pure read-time alias lookup.
  // NET-058 requirement: "Pauli Murray, Patsy Mink, Stacey Milbern, Zitkala-Sa"
  // must light up renamed slots regardless of stored name.
  //
  // MUTATION PROOF (NET-058):
  // To verify: remove _awqOldNameAliases map OR comment out the
  // _canonicalizeAwqSubject call in _fastPathSubjectMatchesSlot.
  // All 5 alias isMatch tests + the resolveProgramInventory test FAIL with:
  //   Expected: <true>  Actual: <false>
  // The no-false-positive test still passes (it tests a different slot).
  // ===========================================================================

  group('AWQ old-name alias map — match-time canonicalization (no Firestore write)', () {
    test('"Dr. Pauli Murray" (old stored name) matches "Rev. Dr. Pauli Murray" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Rev. Dr. Pauli Murray');
      final coin = _item(themeSubject: 'Dr. Pauli Murray', year: '2024', mintMark: 'P');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: '"Dr. Pauli Murray" → "rev. dr. pauli murray" via _awqOldNameAliases. '
            'No Firestore write required.',
      );
    });

    test('"Pauli Murray" (short alias) matches "Rev. Dr. Pauli Murray" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Rev. Dr. Pauli Murray');
      final coin = _item(themeSubject: 'Pauli Murray', year: '2024', mintMark: 'D');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: '"Pauli Murray" → "rev. dr. pauli murray" via _awqOldNameAliases.',
      );
    });

    test('"Patsy Mink" (old stored name) matches "Patsy Takemoto Mink" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Patsy Takemoto Mink');
      final coin = _item(themeSubject: 'Patsy Mink', year: '2024', mintMark: 'P');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: '"Patsy Mink" → "patsy takemoto mink" via _awqOldNameAliases.',
      );
    });

    test('"Stacey Milbern" (old stored name) matches "Stacey Park Milbern" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Stacey Park Milbern');
      final coin = _item(themeSubject: 'Stacey Milbern', year: '2025', mintMark: 'D');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: '"Stacey Milbern" → "stacey park milbern" via _awqOldNameAliases.',
      );
    });

    test('"Zitkala-Sa" (ASCII, no diacritic) matches "Zitkala-Ša" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name.startsWith('Zitkala'));
      final coin = _item(themeSubject: 'Zitkala-Sa', year: '2024', mintMark: 'P');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: '"Zitkala-Sa" (ASCII) → "zitkala-\u0161a" via _awqOldNameAliases. '
            'Covers OCR-dropped diacritic case.',
      );
    });

    test('No false positive: "Dr. Pauli Murray" does NOT match "Patsy Takemoto Mink" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Patsy Takemoto Mink');
      final coin = _item(themeSubject: 'Dr. Pauli Murray', year: '2024', mintMark: 'P');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isFalse,
        reason: 'Alias map must not cause cross-slot false positives.',
      );
    });

    test('resolveProgramInventory: old-name coins (Dr. Pauli Murray, Patsy Mink, '
        'Stacey Milbern, Zitkala-Sa) all OWNED via alias map', () {
      // Simulates a user whose collection was scanned before F1 apply.
      // Stored coins use old/short names; slots now have canonical names.
      // Without alias map: 4 slots go dark. With alias map: all 4 light up.
      final program = _fullAwqProgram();

      final coins = <Map<String, dynamic>>[
        _item(themeSubject: 'Dr. Pauli Murray', year: '2024'),      // → Rev. Dr. Pauli Murray
        _item(themeSubject: 'Patsy Mink', year: '2024'),             // → Patsy Takemoto Mink
        _item(themeSubject: 'Stacey Milbern', year: '2025'),         // → Stacey Park Milbern
        _item(themeSubject: 'Zitkala-Sa', year: '2024'),             // → Zitkala-Ša
      ];

      final result = SlotResolver.resolveProgramInventory(
        program: program,
        coins: coins,
      );

      // Each old-name coin must light up its renamed slot's P-mint key.
      // Slot IDs come from _fullAwqProgram() definitions:
      //   Rev. Dr. Pauli Murray  → awq_2024_dr__pauli_murray
      //   Patsy Takemoto Mink    → awq_2024_patsy_mink
      //   Stacey Park Milbern    → awq_2025_stacey_milbern
      //   Zitkala-Ša             → awq_2024_zitkala_sa
      const pauliKey   = 'american_women_quarters_awq_2024_dr__pauli_murray_P';
      const patsyKey   = 'american_women_quarters_awq_2024_patsy_mink_P';
      const staceyKey  = 'american_women_quarters_awq_2025_stacey_milbern_P';
      const zitkalaKey = 'american_women_quarters_awq_2024_zitkala_sa_P';

      expect(result.containsKey(pauliKey),   isTrue, reason: 'Rev. Dr. Pauli Murray P-slot key must exist in result map');
      expect(result.containsKey(patsyKey),   isTrue, reason: 'Patsy Takemoto Mink P-slot key must exist in result map');
      expect(result.containsKey(staceyKey),  isTrue, reason: 'Stacey Park Milbern P-slot key must exist in result map');
      expect(result.containsKey(zitkalaKey), isTrue, reason: 'Zitkala-Ša P-slot key must exist in result map');

      expect(result[pauliKey],   isNot(SlotMatchResult.empty), reason: '"Dr. Pauli Murray" coin must OWNED Pauli Murray slot via alias');
      expect(result[patsyKey],   isNot(SlotMatchResult.empty), reason: '"Patsy Mink" coin must OWNED Patsy Takemoto Mink slot via alias');
      expect(result[staceyKey],  isNot(SlotMatchResult.empty), reason: '"Stacey Milbern" coin must OWNED Stacey Park Milbern slot via alias');
      expect(result[zitkalaKey], isNot(SlotMatchResult.empty), reason: '"Zitkala-Sa" coin must OWNED Zitkala-Ša slot via alias');
    });
  });

  // ===========================================================================
  // GROUP 6: Title-only old-name alias — Title path canonicalization
  // Grok CoS probe (NET-060): coins with ONLY a Title field (no Theme/Subject),
  // e.g. "2024 Patsy Mink Quarter" — Title path must apply alias map too.
  // "2024 Celia Cruz Quarter" lights on canonical path → Title path is live.
  //
  // MUTATION PROOF (NET-060):
  // Remove alias keys from candidateToCanonical build loop in _fastPathSubjectMatchesSlot.
  // All 4 Title-only old-name isMatch tests FAIL (Expected: <true> Actual: <false>).
  // Canonical Title test + no-false-positive test still PASS.
  // Restore → all PASS again.
  // ===========================================================================

  group('AWQ Title-path old-name alias — Title-only coins (no Theme/Subject)', () {
    test('"2024 Patsy Mink Quarter" Title-only matches "Patsy Takemoto Mink" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Patsy Takemoto Mink');
      final coin = _titleItem(title: '2024 Patsy Mink Quarter', year: '2024');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Title "2024 Patsy Mink Quarter" contains alias "patsy mink" → '
            '"patsy takemoto mink" canonical via Title path alias extension.',
      );
    });

    test('"2024 Dr. Pauli Murray Quarter" Title-only matches "Rev. Dr. Pauli Murray" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Rev. Dr. Pauli Murray');
      final coin = _titleItem(title: '2024 Dr. Pauli Murray Quarter', year: '2024');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Title contains alias "dr. pauli murray" → "rev. dr. pauli murray" via Title path.',
      );
    });

    test('"2025 Stacey Milbern Quarter" Title-only matches "Stacey Park Milbern" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Stacey Park Milbern');
      final coin = _titleItem(title: '2025 Stacey Milbern Quarter', year: '2025');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Title contains alias "stacey milbern" → "stacey park milbern" via Title path.',
      );
    });

    test('"2024 Zitkala-Sa Quarter" Title-only matches "Zitkala-Ša" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name.startsWith('Zitkala'));
      final coin = _titleItem(title: '2024 Zitkala-Sa Quarter', year: '2024');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Title contains alias "zitkala-sa" (ASCII) → "zitkala-\u0161a" via Title path.',
      );
    });

    test('"2024 Celia Cruz Quarter" canonical Title still matches "Celia Cruz" slot', () {
      // Regression: canonical path must still work after alias extension.
      // Grok CoS confirmed "Celia Cruz" lights — verify it still does.
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Celia Cruz');
      final coin = _titleItem(title: '2024 Celia Cruz Quarter', year: '2024');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isTrue,
        reason: 'Canonical "celia cruz" in title must still match its slot (no regression).',
      );
    });

    test('No false positive: "2024 Patsy Mink Quarter" Title does NOT match "Celia Cruz" slot', () {
      final program = _fullAwqProgram();
      final slot = program.coins.firstWhere((s) => s.name == 'Celia Cruz');
      final coin = _titleItem(title: '2024 Patsy Mink Quarter', year: '2024');
      expect(
        SlotResolver.isMatch(coin, program, slot),
        isFalse,
        reason: 'Title alias must not cause cross-slot false positives.',
      );
    });

    test('resolveProgramInventory: Title-only old-name coins all OWNED via Title path alias', () {
      // Simulates coins whose Title embeds old names but have no Theme/Subject.
      // Without alias extension in Title path: 4 slots go dark.
      // With alias extension: all 4 light up.
      final program = _fullAwqProgram();

      final coins = <Map<String, dynamic>>[
        _titleItem(title: '2024 Patsy Mink Quarter',    year: '2024'),  // → Patsy Takemoto Mink
        _titleItem(title: '2024 Dr. Pauli Murray Quarter', year: '2024'), // → Rev. Dr. Pauli Murray
        _titleItem(title: '2025 Stacey Milbern Quarter', year: '2025'), // → Stacey Park Milbern
        _titleItem(title: '2024 Zitkala-Sa Quarter',    year: '2024'),  // → Zitkala-Ša
      ];

      final result = SlotResolver.resolveProgramInventory(
        program: program,
        coins: coins,
      );

      // Use same slot key constants as Group 5 (keys are program-id + slot-id + variety).
      const pauliKey   = 'american_women_quarters_awq_2024_dr__pauli_murray_P';
      const patsyKey   = 'american_women_quarters_awq_2024_patsy_mink_P';
      const staceyKey  = 'american_women_quarters_awq_2025_stacey_milbern_P';
      const zitkalaKey = 'american_women_quarters_awq_2024_zitkala_sa_P';

      expect(result.containsKey(pauliKey),   isTrue, reason: 'Rev. Dr. Pauli Murray P-slot key must exist');
      expect(result.containsKey(patsyKey),   isTrue, reason: 'Patsy Takemoto Mink P-slot key must exist');
      expect(result.containsKey(staceyKey),  isTrue, reason: 'Stacey Park Milbern P-slot key must exist');
      expect(result.containsKey(zitkalaKey), isTrue, reason: 'Zitkala-Ša P-slot key must exist');

      expect(result[pauliKey],   isNot(SlotMatchResult.empty),
          reason: 'Title "2024 Dr. Pauli Murray Quarter" must OWNED Rev. Dr. Pauli Murray slot via Title alias');
      expect(result[patsyKey],   isNot(SlotMatchResult.empty),
          reason: 'Title "2024 Patsy Mink Quarter" must OWNED Patsy Takemoto Mink slot via Title alias');
      expect(result[staceyKey],  isNot(SlotMatchResult.empty),
          reason: 'Title "2025 Stacey Milbern Quarter" must OWNED Stacey Park Milbern slot via Title alias');
      expect(result[zitkalaKey], isNot(SlotMatchResult.empty),
          reason: 'Title "2024 Zitkala-Sa Quarter" must OWNED Zitkala-Ša slot via Title alias');
    });
  });
}
