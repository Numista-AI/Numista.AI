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
}
