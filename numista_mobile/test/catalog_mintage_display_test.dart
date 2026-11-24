import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';

Widget _wrapMintageRow(Map<String, dynamic> item, {double width = 360}) {
  return MaterialApp(
    home: Scaffold(
      body: Align(
        alignment: Alignment.topLeft,
        child: SizedBox(
          width: width,
          child: CatalogBrowseScreen.buildMintageRowForTest(item),
        ),
      ),
    ),
  );
}

List<String> _visibleTextStrings(WidgetTester tester) {
  return tester
      .widgetList<Text>(find.byType(Text))
      .map((t) => t.data ?? '')
      .where((s) => s.isNotEmpty)
      .toList();
}

void main() {
  group('B1 Mintage Display v1.1 Widget Tests', () {
    testWidgets('1. Value 1597367 with label renders 1,597,367 and full label; raw 1597367 absent', (tester) async {
      const caveat = 'Struck in calendar year 1841, Philadelphia Mint (Mint record).';
      await tester.pumpWidget(_wrapMintageRow({
        'nac_code': 'NAC1.CN.US.1C.BRAIDEDHAI.1841.P.BASE.Z',
        'mintage': {
          'value': 1597367,
          'label': caveat,
          'source_url': 'https://example.com/mint-record',
        },
      }));

      expect(find.text('1,597,367'), findsOneWidget);
      expect(find.text(caveat), findsOneWidget);
      expect(find.text('(source)'), findsOneWidget);
      expect(find.textContaining('1597367'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('2. Value 999 renders 999 without comma', (tester) async {
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': 999, 'label': 'Mint record'},
      }));

      expect(find.text('999'), findsOneWidget);
      expect(find.text('Mint record'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('3. Value 0 and fractionless double render cleanly without Needs source', (tester) async {
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': 0},
      }));
      expect(find.text('0'), findsOneWidget);
      expect(find.text('Needs source'), findsNothing);
      expect(tester.takeException(), isNull);

      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': 1597367.0, 'label': 'Fractionless double'},
      }));
      expect(find.text('1,597,367'), findsOneWidget);
      expect(find.textContaining('.0'), findsNothing);
      expect(tester.takeException(), isNull);

      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': double.nan, 'label': '   '},
      }));
      expect(find.text('Needs source'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('4. String value "4,361.22 million (as published, rounded)" renders verbatim', (tester) async {
      const verbatim = '4,361.22 million (as published, rounded)';
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {
          'value': verbatim,
          'label': 'U.S. Mint annual production figure',
          'source_url': 'https://example.com/2017-cent',
        },
      }));

      expect(find.text(verbatim), findsOneWidget);
      expect(find.text('U.S. Mint annual production figure'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('5. Null value with label renders label only', (tester) async {
      const label = 'No official mintage for this variety.';
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': null, 'label': label},
      }));

      expect(find.text(label), findsOneWidget);
      expect(find.text('Needs source'), findsNothing);
      expect(find.text('(source)'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('6. Null value with null or whitespace label renders Needs source', (tester) async {
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': null, 'label': null},
      }));
      expect(find.text('Needs source'), findsOneWidget);
      expect(tester.takeException(), isNull);

      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': null, 'label': '   \t  '},
      }));
      expect(find.text('Needs source'), findsOneWidget);
      expect(tester.takeException(), isNull);
    });

    testWidgets('7. Missing source_url renders no (source) link and does not crash', (tester) async {
      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {'value': 42500, 'label': 'Official Mint report'},
      }));

      expect(find.text('42,500'), findsOneWidget);
      expect(find.text('Official Mint report'), findsOneWidget);
      expect(find.text('(source)'), findsNothing);
      expect(tester.takeException(), isNull);
    });

    testWidgets('8. Long label (>200 chars) wraps cleanly at 360px with zero overflow; duplicate-prefix label still renders', (tester) async {
      await tester.binding.setSurfaceSize(const Size(360, 800));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final longLabel =
          '1,597,367 struck in calendar year 1841 at the Philadelphia Mint according to Bureau of the Mint Table C21 p. 42; pre-1889 figures reflect calendar-year delivery dates across multiple dies and minor die marriages without separating overdates or proofs.';
      expect(longLabel.length, greaterThan(200));

      await tester.pumpWidget(_wrapMintageRow({
        'mintage': {
          'value': 1597367,
          'label': longLabel,
          'source_url': 'https://example.com/c21',
        },
      }, width: 360));
      await tester.pumpAndSettle();

      expect(find.text('1,597,367'), findsOneWidget);
      expect(find.text('(source)'), findsOneWidget);
      expect(find.text(longLabel), findsOneWidget);
      expect(tester.takeException(), isNull);
    });
  });

  group('Offline P10 Rendered-Card Scan (3,202 live + 264 fold 6703e2fc)', () {
    testWidgets('renders all 3,202 live rows + 264 fold adds at 360px with zero P10 violations', (tester) async {
      await tester.binding.setSurfaceSize(const Size(360, 800));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      final catalogFile = File('assets/catalog/catalog_public_v1.json');
      expect(catalogFile.existsSync(), isTrue);
      final liveEntries = (json.decode(catalogFile.readAsStringSync()) as List<dynamic>)
          .cast<Map<String, dynamic>>();
      expect(liveEntries.length, 3202);

      final foldPath = Platform.environment['B1_FOLD_JSONL_PATH'];
      final List<Map<String, dynamic>> foldEntries = [];
      if (foldPath != null && foldPath.isNotEmpty) {
        final foldFile = File(foldPath);
        expect(foldFile.existsSync(), isTrue,
            reason: 'Expected fold 6703e2fc JSONL at $foldPath');
        foldEntries.addAll(
          foldFile
              .readAsLinesSync()
              .where((l) => l.trim().isNotEmpty)
              .map((l) => (json.decode(l) as Map<String, dynamic>)['public_entry']
                  as Map<String, dynamic>),
        );
        expect(foldEntries.length, 264);
      }

      final currentItem = ValueNotifier<Map<String, dynamic>>(liveEntries.first);
      addTearDown(currentItem.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: SizedBox(
                width: 360,
                child: ValueListenableBuilder<Map<String, dynamic>>(
                  valueListenable: currentItem,
                  builder: (_, item, _) =>
                      CatalogBrowseScreen.buildMintageRowForTest(item),
                ),
              ),
            ),
          ),
        ),
      );

      final bareNumericRe = RegExp(r'\b\d{4,}\b');
      final boolLiteralRe = RegExp(r'\b(true|false)\b', caseSensitive: false);
      final nullLiteralRe = RegExp(r'\b(null|None)\b');
      final idLikeRe = RegExp(r'NAC1\.[A-Z0-9.]+|[0-9a-f]{8}-[0-9a-f]{4}-',
          caseSensitive: false);

      int overflowCount = 0;
      int bareNumericValueHits = 0;
      int rawBoolHits = 0;
      int nullNoneHits = 0;
      int idLikeHits = 0;
      int pre1889FoldChecked = 0;
      int pre1889FoldWithNumericVal = 0;
      int pre1889LabelMissing = 0;
      int stringOrLabel4DigitRows = 0;
      final List<Map<String, dynamic>> stringOrLabel4DigitSample = [];
      final List<Map<String, dynamic>> badgeSourceContradictions = [];

      Future<void> scanBatch(
        String dataset,
        List<Map<String, dynamic>> rows,
      ) async {
        for (final entry in rows) {
          currentItem.value = entry;
          await tester.pump();
          final exc = tester.takeException();
          if (exc != null) {
            overflowCount++;
          }

          final nac = (entry['nac_code'] ?? '').toString();
          final mintage = entry['mintage'] as Map?;
          final rawVal = mintage?['value'];
          final rawLabel = (mintage?['label'] is String)
              ? (mintage!['label'] as String).trim()
              : '';
          final sourceUrl = (mintage?['source_url'] is String)
              ? (mintage!['source_url'] as String).trim()
              : '';

          final renderedTexts = _visibleTextStrings(tester);
          // Inspect rendered widgets specifically
          for (final w in tester.widgetList<Text>(find.byType(Text))) {
            final txt = w.data ?? '';
            if (txt == 'Mintage:' || txt == '(source)') continue;
            final isBoldNumericWidget = w.style?.color == const Color(0xFF0B2545);

            if (isBoldNumericWidget && (rawVal is int || rawVal is double)) {
              final stripped = txt.replaceAll(',', '');
              if ((rawVal as num) >= 1000 && !txt.contains(',')) {
                bareNumericValueHits++;
              }
              if (stripped != (rawVal).toInt().toString() &&
                  rawVal == rawVal.truncateToDouble()) {
                bareNumericValueHits++;
              }
            } else if (bareNumericRe.hasMatch(txt)) {
              // Number inside string value or caveat label (e.g. years 1841, 1974)
              stringOrLabel4DigitRows++;
              if (stringOrLabel4DigitSample.length < 15) {
                stringOrLabel4DigitSample.add({
                  'dataset': dataset,
                  'nac_code': nac,
                  'matches': bareNumericRe
                      .allMatches(txt)
                      .map((m) => m.group(0))
                      .toList(),
                });
              }
            }
          }

          final joined = renderedTexts.join(' | ');
          if (boolLiteralRe.hasMatch(joined)) rawBoolHits++;
          if (nullLiteralRe.hasMatch(joined)) nullNoneHits++;
          if (idLikeRe.hasMatch(joined)) idLikeHits++;

          if (dataset == 'FOLD_6703e2fc') {
            final yr = entry['year'];
            if (yr is int && yr < 1889) {
              pre1889FoldChecked++;
              if (rawVal != null) pre1889FoldWithNumericVal++;
              if (rawLabel.isEmpty || !renderedTexts.contains(rawLabel)) {
                pre1889LabelMissing++;
              }
            }
          }

          if (rawLabel.toLowerCase().contains('proposal') &&
              sourceUrl.isNotEmpty) {
            badgeSourceContradictions.add({
              'dataset': dataset,
              'nac_code': nac,
              'label': rawLabel,
              'source_url': sourceUrl,
            });
          }
        }
      }

      await scanBatch('LIVE_3202', liveEntries);
      if (foldEntries.isNotEmpty) {
        await scanBatch('FOLD_6703e2fc', foldEntries);
      }

      final summary = {
        'live_rows_rendered': liveEntries.length,
        'fold_rows_rendered': foldEntries.length,
        'total_rows_rendered': liveEntries.length + foldEntries.length,
        'render_exceptions_at_360px': overflowCount,
        'bare_4plus_digit_numeric_value_hits': bareNumericValueHits,
        'raw_boolean_hits': rawBoolHits,
        'null_or_none_hits': nullNoneHits,
        'id_or_nac_code_hits': idLikeHits,
        'pre1889_fold_total': pre1889FoldChecked,
        'pre1889_fold_with_numeric_val': pre1889FoldWithNumericVal,
        'pre1889_fold_caveat_label_missing': pre1889LabelMissing,
        'pre1889_fold_caveat_label_visible': pre1889FoldChecked - pre1889LabelMissing,
        'rows_with_4plus_digit_numbers_inside_string_or_label': stringOrLabel4DigitRows,
        'string_or_label_4digit_sample': stringOrLabel4DigitSample,
        'upstream_label_vs_source_url_notes': badgeSourceContradictions,
      };

      final outPath = Platform.environment['B1_P10_OUT_PATH'];
      if (outPath != null && outPath.isNotEmpty) {
        final outFile = File(outPath);
        outFile.parent.createSync(recursive: true);
        outFile.writeAsStringSync(const JsonEncoder.withIndent('  ').convert(summary));
      }

      expect(overflowCount, 0, reason: 'No overflow allowed at 360px across rendered rows');
      expect(bareNumericValueHits, 0, reason: 'Every numeric mintage >= 1000 must format with commas');
      expect(rawBoolHits, 0, reason: 'No raw booleans allowed in mintage row');
      expect(nullNoneHits, 0, reason: 'No "null" or "None" allowed in mintage row');
      expect(idLikeHits, 0, reason: 'No NAC codes or ID-like tokens allowed in mintage row');
      if (foldEntries.isNotEmpty) {
        expect(pre1889FoldChecked, 228);
        expect(pre1889FoldWithNumericVal, 223);
        expect(pre1889LabelMissing, 0, reason: 'Every pre-1889 fold row must display its caveat label');
      }
    });
  });
}
