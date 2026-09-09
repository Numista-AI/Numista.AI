// test/set_expansion_helper_test.dart
//
// Regression test: expandCollection() must preserve program_id, Strike Type,
// Variety, and variety_id in ALL three branches (regular coin, set parent,
// set child) so that SlotResolver.isMatch() can use the fast path and finish
// guard correctly.
//
// Root cause of A250 0/19 bug (9 Sep 2026): regular-coin branch projected
// a hardcoded 13-field map, silently dropping these fields before isMatch().
// This test locks in the fix.
//
// flutter test test/set_expansion_helper_test.dart  must exit 0.

import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/set_expansion_helper.dart';
import 'package:numista_ai/utils/slot_resolver.dart';
import 'package:numista_ai/models/program_model.dart';

void main() {
  // ── Regular coin branch ───────────────────────────────────────────────────

  group('expandCollection — regular coin', () {
    final rawDoc = {
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Reverse Proof',
      'Variety': 'Reverse Proof',
      'variety_id': 'P-REVERSE-PROOF',
      'Theme/Subject': '2026 Morgan Silver Dollar Reverse Proof',
      'Program/Series': '2026 America250 - Numismatic Collectibles',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
      'Condition': 'Proof',
    };

    late Map<String, dynamic> item;

    setUp(() {
      final res = expandCollection([rawDoc], ['doc_morgan_rp']);
      item = res.allItems.first;
    });

    test('preserves program_id', () {
      expect(item['program_id'], equals('2026_semiquincentennial_collectibles'));
    });

    test('preserves Strike Type', () {
      expect(item['Strike Type'], equals('Reverse Proof'));
    });

    test('preserves Variety', () {
      expect(item['Variety'], equals('Reverse Proof'));
    });

    test('preserves variety_id', () {
      expect(item['variety_id'], equals('P-REVERSE-PROOF'));
    });

    test('normalized fields still correct (theme_subject, year, mint_mark)', () {
      expect(item['theme_subject'], equals('2026 Morgan Silver Dollar Reverse Proof'));
      expect(item['year'], equals('2026'));
      expect(item['mint_mark'], equals(''));
    });

    test('system fields set correctly', () {
      expect(item['coin_id'], equals('doc_morgan_rp'));
      expect(item['from_set'], isNull);
      expect(item['is_set_parent'], isFalse);
    });
  });

  // ── EU coin variant ───────────────────────────────────────────────────────

  group('expandCollection — regular coin EU variant', () {
    final rawDoc = {
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Enhanced Uncirculated',
      'Variety': 'Enhanced Uncirculated',
      'variety_id': 'EU',
      'Theme/Subject': '2026 Morgan Silver Dollar Enhanced Uncirculated',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
    };

    test('preserves Strike Type for EU coin', () {
      final res = expandCollection([rawDoc], ['doc_morgan_eu']);
      expect(res.allItems.first['Strike Type'], equals('Enhanced Uncirculated'));
    });

    test('preserves Variety for EU coin', () {
      final res = expandCollection([rawDoc], ['doc_morgan_eu']);
      expect(res.allItems.first['Variety'], equals('Enhanced Uncirculated'));
    });
  });

  // ── Set parent branch ─────────────────────────────────────────────────────

  group('expandCollection — set parent', () {
    final rawSet = {
      'item_type': 'set',
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Proof',
      'Theme/Subject': 'Some Proof Set',
      'Year': '2026',
      'Mint Mark': 'W',
      'set_contents': jsonEncode([
        {'Theme/Subject': 'Child Coin', 'Year': '2026', 'Denomination': 'Dollar'},
      ]),
    };

    late Map<String, dynamic> parent;

    setUp(() {
      final res = expandCollection([rawSet], ['doc_set_parent']);
      parent = res.allItems.firstWhere((i) => i['is_set_parent'] == true);
    });

    test('set parent preserves program_id', () {
      expect(parent['program_id'], equals('2026_semiquincentennial_collectibles'));
    });

    test('set parent preserves Strike Type', () {
      expect(parent['Strike Type'], equals('Proof'));
    });

    test('set parent item_type is set', () {
      expect(parent['item_type'], equals('set'));
    });
  });

  // ── Set child branch ──────────────────────────────────────────────────────

  group('expandCollection — set child', () {
    final rawSet = {
      'item_type': 'set',
      'program_id': '2026_semiquincentennial_collectibles',
      'Theme/Subject': 'Parent Set',
      'Year': '2026',
      'set_contents': jsonEncode([
        {
          'Theme/Subject': 'Child Morgan RP',
          'Strike Type': 'Reverse Proof',
          'Variety': 'Reverse Proof',
          'variety_id': 'P-REVERSE-PROOF',
          'Year': '2026',
          'Denomination': 'Dollar',
        },
      ]),
    };

    late Map<String, dynamic> child;

    setUp(() {
      final res = expandCollection([rawSet], ['doc_set_child']);
      child = res.allItems.firstWhere((i) => i['is_set_parent'] == false);
    });

    test('set child preserves Strike Type', () {
      expect(child['Strike Type'], equals('Reverse Proof'));
    });

    test('set child preserves Variety', () {
      expect(child['Variety'], equals('Reverse Proof'));
    });


    test('set child preserves variety_id', () {
      expect(child['variety_id'], equals('P-REVERSE-PROOF'));
    });

    test('set child from_set points to parent', () {
      expect(child['from_set'], equals('doc_set_child'));
    });
  });

  // ── MF3: E2E Ownership — Gate0-shaped grokbot docs → isMatch + matchesVariety ─

  group('e2e ownership — Gate0 grokbot docs reach SlotResolver', () {
    // Mirrors exact Gate0 Firestore fields for grokbot's 9 docs.
    // program_id, Strike Type, Variety, variety_id must survive expandCollection
    // so SlotResolver.isMatch fast path lights the slot.

    CoinProgram _program(List<ProgramCoin> coins) => CoinProgram(
      id: '2026_semiquincentennial_collectibles',
      url: '',
      name: '2026 America250 - Numismatic Collectibles',
      years: '2026',
      category: 'Collectible Programs',
      coins: coins,
      mintMarkLocations: 'MIXED',
    );

    ProgramCoin _slot(String id, String name, String family, String varietyId) =>
        ProgramCoin(
          id: id,
          name: name,
          year: '2026',
          productFamily: family,
          varieties: [ChecklistVariety(id: varietyId, label: varietyId)],
        );

    final slotMorganRP = _slot('2026_morgan_reverse_proof',
        '2026 Morgan Silver Dollar Reverse Proof', 'morgan', 'P-REVERSE-PROOF');
    final slotPeaceRP  = _slot('2026_peace_silver_dollar_reverse_proof',
        '2026 Peace Silver Dollar Reverse Proof', 'peace', 'P-REVERSE-PROOF');
    final slotMorganEU = _slot('2026_morgan_silver_dollar_enhanced_uncirculated',
        '2026 Morgan Silver Dollar Enhanced Uncirculated', 'morgan', 'EU');
    final slotPeaceEU  = _slot('2026_peace_silver_dollar_enhanced_uncirculated',
        '2026 Peace Silver Dollar Enhanced Uncirculated', 'peace', 'EU');

    // Gate0-shaped grokbot coin docs (verbatim from Firestore dump, 9 Sep 2026)
    final grokbotMorganRP = <String, dynamic>{
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Reverse Proof',
      'Variety': 'Reverse Proof',
      'variety_id': 'P-REVERSE-PROOF',
      'Theme/Subject': '2026 Morgan Silver Dollar Reverse Proof',
      'Program/Series': '2026 America250 - Numismatic Collectibles',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
    };
    final grokbotPeaceRP = <String, dynamic>{
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Reverse Proof',
      'Variety': 'Reverse Proof',
      'variety_id': 'P-REVERSE-PROOF',
      'Theme/Subject': '2026 Peace Silver Dollar Reverse Proof',
      'Program/Series': '2026 America250 - Numismatic Collectibles',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
    };
    final grokbotMorganEU = <String, dynamic>{
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Enhanced Uncirculated',
      'Variety': 'Enhanced Uncirculated',
      'variety_id': 'EU',
      'Theme/Subject': '2026 Morgan Silver Dollar Enhanced Uncirculated',
      'Program/Series': '2026 America250 - Numismatic Collectibles',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
    };
    final grokbotPeaceEU = <String, dynamic>{
      'program_id': '2026_semiquincentennial_collectibles',
      'Strike Type': 'Enhanced Uncirculated',
      'Variety': 'Enhanced Uncirculated',
      'variety_id': 'EU',
      'Theme/Subject': '2026 Peace Silver Dollar Enhanced Uncirculated',
      'Program/Series': '2026 America250 - Numismatic Collectibles',
      'Year': '2026',
      'Mint Mark': '',
      'Denomination': 'Dollar',
    };

    test('Morgan RP coin → isMatch Morgan RP slot', () {
      final res = expandCollection([grokbotMorganRP], ['doc_morgan_rp']);
      final item = res.allItems.first;
      final prog = _program([slotMorganRP]);
      expect(SlotResolver.isMatch(item, prog, slotMorganRP), isTrue,
          reason: 'Morgan RP coin must match Morgan RP slot after field fix');
    });

    test('Peace RP coin → isMatch Peace RP slot', () {
      final res = expandCollection([grokbotPeaceRP], ['doc_peace_rp']);
      final item = res.allItems.first;
      final prog = _program([slotPeaceRP]);
      expect(SlotResolver.isMatch(item, prog, slotPeaceRP), isTrue,
          reason: 'Peace RP coin must match Peace RP slot');
    });

    test('Morgan EU coin → isMatch Morgan EU slot', () {
      final res = expandCollection([grokbotMorganEU], ['doc_morgan_eu']);
      final item = res.allItems.first;
      final prog = _program([slotMorganEU]);
      expect(SlotResolver.isMatch(item, prog, slotMorganEU), isTrue,
          reason: 'Morgan EU coin must match Morgan EU slot');
    });

    test('Peace EU coin → isMatch Peace EU slot', () {
      final res = expandCollection([grokbotPeaceEU], ['doc_peace_eu']);
      final item = res.allItems.first;
      final prog = _program([slotPeaceEU]);
      expect(SlotResolver.isMatch(item, prog, slotPeaceEU), isTrue,
          reason: 'Peace EU coin must match Peace EU slot');
    });

    test('Non-program coin does NOT match Numismatic slot', () {
      // A regular circulating coin with no program_id and unrelated theme
      // should not match any Numismatic Collectibles slot.
      final regularCoin = <String, dynamic>{
        'Theme/Subject': '2026 Lincoln Cent',
        'Program/Series': 'Lincoln Cent',
        'Year': '2026',
        'Mint Mark': 'P',
        'Denomination': 'Cent',
      };
      final res = expandCollection([regularCoin], ['doc_lincoln']);
      final item = res.allItems.first;
      final prog = _program([slotMorganRP]);
      expect(SlotResolver.isMatch(item, prog, slotMorganRP), isFalse,
          reason: 'Lincoln cent must not match Morgan RP slot');
    });
  });
}
