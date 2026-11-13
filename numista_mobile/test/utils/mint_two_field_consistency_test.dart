import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/batch_valuation_service.dart';
import 'package:numista_ai/utils/mint_helpers.dart';
import 'package:numista_ai/widgets/add_coin_manual_form.dart';

void main() {
  group('Review 04 Two-Field Mint Consistency', () {
    test('NMM blank mint resolves to Philadelphia + empty mintMark', () {
      final resolved = MintHelpers.resolveTwoFieldMint(
        rawMintMark: '',
        year: '1964',
        series: 'Kennedy Half Dollar',
        denomination: '50c',
      );
      expect(resolved.mint, 'Philadelphia');
      expect(resolved.mintMark, '');
    });

    test('readMintMark works on post-prune, legacy, and NMM documents', () {
      expect(MintHelpers.readMintMark({'mint_mark': 'S'}), 'S');
      expect(MintHelpers.readMintMark({'Mint Mark': 'D'}), 'D');
      expect(
        MintHelpers.readMintMark({'mint': 'Philadelphia', 'mint_mark': ''}),
        '',
      );
    });

    test('BatchValuationService.buildCoinTask formats post-prune mint_mark', () {
      final task = BatchValuationService.buildCoinTask('doc1', {
        'Year': '2024',
        'Denomination': 'Quarter',
        'mint': 'Denver',
        'mint_mark': 'D',
      });
      expect(task, isNotNull);
      expect(task!.name, contains('2024-D'));
    });

    testWidgets('AddCoinManualForm emits mint, mint_mark, and Mint Mark',
        (tester) async {
      Map<String, dynamic>? submitted;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                onSubmit: (data) => submitted = data,
              ),
            ),
          ),
        ),
      );

      final fields = find.byType(TextFormField);
      // Year, Mint Mark, Denomination, Program/Series
      await tester.enterText(fields.at(0), '1964');
      await tester.enterText(fields.at(1), '');
      await tester.enterText(fields.at(2), '50c');
      await tester.enterText(fields.at(3), 'Kennedy Half Dollar');

      final submitBtn = find.text('Save to My Collection');
      await tester.ensureVisible(submitBtn);
      await tester.tap(submitBtn);
      await tester.pumpAndSettle();

      expect(submitted, isNotNull);
      expect(submitted!['mint'], 'Philadelphia');
      expect(submitted!['mint_mark'], '');
      expect(submitted!['Mint Mark'], '');
    });
  });
}
