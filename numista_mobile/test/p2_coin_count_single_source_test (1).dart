import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/set_expansion_helper.dart';
import 'package:numista_ai/services/batch_valuation_service.dart';
import 'package:numista_ai/widgets/header_stats_bar.dart';

class FakeQueryDocumentSnapshot implements QueryDocumentSnapshot<Map<String, dynamic>> {
  @override
  final String id;
  final Map<String, dynamic> _data;

  FakeQueryDocumentSnapshot(this.id, this._data);

  @override
  Map<String, dynamic> data() => _data;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

void main() {
  group('P2 Coin Count Single Source of Truth', () {
    test('expandCollection accurately expands sets and excludes supplies and non-coins', () {
      final List<Map<String, dynamic>> rawDocs = [];
      final List<String> docIds = [];

      // 280 loose coins
      for (int i = 0; i < 280; i++) {
        rawDocs.add({
          'Year': '1964',
          'Denomination': 'Quarter',
          'item_type': 'coin',
        });
        docIds.add('coin_$i');
      }

      // 4 sets with 31 total child coins
      rawDocs.add({
        'item_type': 'set',
        'Theme/Subject': '1999 Silver Proof Set',
        'set_contents': [
          {'Denomination': 'Cent', 'Year': '1999', 'item_type': 'coin'},
          {'Denomination': 'Nickel', 'Year': '1999', 'item_type': 'coin'},
          {'Denomination': 'Dime', 'Year': '1999', 'item_type': 'coin'},
          {'Denomination': 'Quarter', 'Year': '1999', 'item_type': 'coin'},
          {'Denomination': 'Half Dollar', 'Year': '1999', 'item_type': 'coin'},
        ],
      });
      docIds.add('set_1');

      rawDocs.add({
        'item_type': 'set',
        'Theme/Subject': '2000 Mint Set',
        'set_contents': [
          {'Denomination': 'Cent', 'Year': '2000', 'item_type': 'coin'},
          {'Denomination': 'Nickel', 'Year': '2000', 'item_type': 'coin'},
          {'Denomination': 'Dime', 'Year': '2000', 'item_type': 'coin'},
          {'Denomination': 'Quarter', 'Year': '2000', 'item_type': 'coin'},
          {'Denomination': 'Half Dollar', 'Year': '2000', 'item_type': 'coin'},
          {'Denomination': 'Dollar', 'Year': '2000', 'item_type': 'coin'},
        ],
      });
      docIds.add('set_2');

      rawDocs.add({
        'item_type': 'set',
        'Theme/Subject': 'State Quarters Set',
        'set_contents': List.generate(
          10,
          (_) => {'Denomination': 'Quarter', 'Year': '2004', 'item_type': 'coin'},
        ),
      });
      docIds.add('set_3');

      rawDocs.add({
        'item_type': 'set',
        'Theme/Subject': '2007 Proof Set',
        'set_contents': List.generate(
          10,
          (_) => {'Denomination': 'Quarter', 'Year': '2007', 'item_type': 'coin'},
        ),
      });
      docIds.add('set_4');

      // 1 supply item
      rawDocs.add({
        'item_type': 'supply',
        'is_supply': true,
      });
      docIds.add('sup_1');

      final result = expandCollection(rawDocs, docIds);

      // Unexpanded lots = 280 loose + 4 sets + 1 supply = 285 lots
      expect(result.totalLots, equals(285));
      expect(result.setCount, equals(4));

      // Physical coins count MUST be 280 + 31 = 311 (excluding supply and set parents)
      expect(result.totalCoins, equals(311));
    });

    testWidgets('HeaderStatsBar displays totalCoinsCount when unfiltered', (tester) async {
      // 284 parent lots in Firestore
      final docs = List.generate(
        284,
        (i) => FakeQueryDocumentSnapshot('doc_$i', {
          'Denomination': 'Quarter',
          'is_foreign': false,
          'item_type': 'coin',
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HeaderStatsBar(
              docs: docs,
              totalCoinsCount: 311, // Authoritative expanded physical coins count
              spotPrices: const {},
              valuation: const BatchValuationProgress(),
              onRunValuation: () {},
              isFiltered: false,
            ),
          ),
        ),
      );

      // Must display '311 coins', NEVER '284 coins'
      expect(find.text('311 coins'), findsOneWidget);
      expect(find.text('284 coins'), findsNothing);
      expect(find.text('TOTAL COINS'), findsOneWidget);
    });

    testWidgets('HeaderStatsBar displays filtered count of totalCoinsCount when filtered', (tester) async {
      // 10 loose coins matching filter
      final docs = List.generate(
        10,
        (i) => FakeQueryDocumentSnapshot('doc_$i', {
          'Denomination': 'Quarter',
          'is_foreign': false,
          'item_type': 'coin',
        }),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HeaderStatsBar(
              docs: docs,
              totalCoinsCount: 311,
              spotPrices: const {},
              valuation: const BatchValuationProgress(),
              onRunValuation: () {},
              isFiltered: true,
            ),
          ),
        ),
      );

      // Must display '10 of 311'
      expect(find.text('10 of 311'), findsOneWidget);
      expect(find.text('FILTERED COINS'), findsOneWidget);
    });
  });
}
