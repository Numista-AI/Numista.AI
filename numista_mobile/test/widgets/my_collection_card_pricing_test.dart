import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/melt_value_service.dart';
import 'package:numista_ai/widgets/collection_card_valuation_row.dart';

double _luminance(int r, int g, int b) {
  double transform(int c) {
    final s = c / 255.0;
    return s <= 0.03928 ? s / 12.92 : pow((s + 0.055) / 1.055, 2.4).toDouble();
  }
  return 0.2126 * transform(r) + 0.7152 * transform(g) + 0.0722 * transform(b);
}

/// v2.2: source-over alpha composite of fg onto an opaque bg (for any translucent chip fill).
Color _over(Color fg, Color bg) {
  final a = fg.a;
  double mix(double f, double b) => f * a + b * (1 - a);
  return Color.from(alpha: 1.0, red: mix(fg.r, bg.r), green: mix(fg.g, bg.g), blue: mix(fg.b, bg.b));
}

int _ch(double v) => (v * 255).round(); // v2.1: Color.r/.g/.b (non-deprecated) on pin SDK ^3.11.3
double _contrastRatio(Color c1, Color c2) {
  final l1 = _luminance(_ch(c1.r), _ch(c1.g), _ch(c1.b));
  final l2 = _luminance(_ch(c2.r), _ch(c2.g), _ch(c2.b));
  final lighter = max(l1, l2);
  final darker = min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

void main() {
  group('CollectionCardValuationRow Production Widget Tests (MF-C2\', MF-C3\', MF-C4, MF-C6\')', () {
    test('Standalone MeltValueService.parseFaceValue table test (shared home_dashboard + cards parser)', () {
      expect(MeltValueService.parseFaceValue('Cent'), 0.01);
      expect(MeltValueService.parseFaceValue('Five Cents'), 0.05);
      expect(MeltValueService.parseFaceValue('Dime'), 0.10);
      expect(MeltValueService.parseFaceValue('Quarter Dollar'), 0.25);
      expect(MeltValueService.parseFaceValue('Half Dollar'), 0.50);
      expect(MeltValueService.parseFaceValue('Dollar'), 1.00);
      expect(MeltValueService.parseFaceValue('Half Dime'), 0.05);
      expect(MeltValueService.parseFaceValue('Three Cent Nickel'), 0.03);
      expect(MeltValueService.parseFaceValue('Set'), 0.0);
    });

    testWidgets('Case 1: CPG retail override displays retail without pending chip (even if enrichment_status is pending)', (tester) async {
      final data = {
        'cpgRetail': 12.50,
        'Denomination': 'Quarter Dollar',
        'enrichment_status': 'pending',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$12.50'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 2 (MF-C2\'): Real Firestore key "AI Estimated Value" displays formatted AI value when cpgRetail is 0', (tester) async {
      final data = {
        'cpgRetail': 0,
        'AI Estimated Value': '35.00',
        'Denomination': 'Half Dollar',
        'enrichment_status': 'completed',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$35.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 3 (MF-C2\'): Real Firestore key "AI Estimated Value" with enrichment_status == pending shows AI value AND pending chip', (tester) async {
      final data = {
        'cpgRetail': 0,
        'AI Estimated Value': '35.00',
        'Denomination': 'Half Dollar',
        'enrichment_status': 'pending',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$35.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('Case 4 (MF-C2\'): Sentinel AI values ("Pending", "null", "—") fall through to denomination face value + pending chip', (tester) async {
      for (final sentinel in const ['Pending', 'null', '—', '']) {
        final data = {
          'cpgRetail': 0,
          'AI Estimated Value': sentinel,
          'Denomination': 'Quarter Dollar',
        };

        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: Scaffold(
              body: CollectionCardValuationRow(data: data),
            ),
          ),
        );

        expect(find.text('\$0.25'), findsOneWidget, reason: 'Sentinel "$sentinel" must fall through to Quarter face value');
        expect(find.text('Value pending AI estimate'), findsOneWidget);
      }
    });

    testWidgets('Case 5 (MF-C3\'): Full canonical and historical denomination face-value table', (tester) async {
      final expectedTable = <String, String>{
        'Cent': '\$0.01',
        'Five Cents': '\$0.05',
        'Dime': '\$0.10',
        'Quarter Dollar': '\$0.25',
        'Half Dollar': '\$0.50',
        'Dollar': '\$1.00',
        'Half Dime': '\$0.05',
        'Three Cent Nickel': '\$0.03',
        'Set': '—',
      };

      for (final entry in expectedTable.entries) {
        final data = {
          'cpgRetail': 0.0,
          'Denomination': entry.key,
        };

        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: Scaffold(
              body: CollectionCardValuationRow(data: data),
            ),
          ),
        );

        expect(
          find.text(entry.value),
          findsOneWidget,
          reason: 'Denomination "${entry.key}" must render "${entry.value}"',
        );
        expect(find.text('Value pending AI estimate'), findsOneWidget);
        expect(find.text('\$0.00'), findsNothing);
      }
    });

    testWidgets('Case 6 (MF-C6\', v2.2): mounts each cited surface and measures text vs PUMPED surface and PUMPED chip fill', (tester) async {
      // Cited surfaces: my_collection_screen.dart:211 _surface (dark 0xFF1E2937 / light Colors.white)
      // and :3031 virtual-child card colors (dark 0xFF0D1520 / light 0xFFF5F5F0).
      final cases = <(ThemeData, Color, double)>[
        (ThemeData.dark(), const Color(0xFF1E2937), 7.0),
        (ThemeData.dark(), const Color(0xFF0D1520), 7.0),
        (ThemeData.light(), const Color(0xFFFFFFFF), 4.5),
        (ThemeData.light(), const Color(0xFFF5F5F0), 4.5),
      ];
      final sampleData = {'cpgRetail': 0.0, 'Denomination': 'Five Cents'};
      for (final (theme, surface, min) in cases) {
        await tester.pumpWidget(MaterialApp(
          key: ValueKey('${theme.brightness}-${surface.toARGB32()}'),
          theme: theme,
          home: Scaffold(
            body: Container(
              key: const Key('udv_card_surface'),
              color: surface,
              child: CollectionCardValuationRow(data: sampleData),
            ),
          ),
        ));
        await tester.pumpAndSettle();
        // Background actually rendered under the row (read from the pumped tree, not a local constant)
        final surfaceBox = tester.widget<Container>(find.byKey(const Key('udv_card_surface')));
        final renderedSurface = (surfaceBox.decoration as BoxDecoration?)?.color ?? surfaceBox.color!;
        expect(renderedSurface.a, 1.0, reason: 'card surface must be opaque for a valid ratio');

        final chipText = tester.widget<Text>(find.text('Value pending AI estimate'));
        final valText = tester.widget<Text>(find.text('\$0.05'));
        final textColor = chipText.style!.color!;
        expect(valText.style!.color, equals(textColor));

        final chip = tester.widget<Container>(find.byKey(const Key('valuation_pending_chip')));
        final chipFill = (chip.decoration! as BoxDecoration).color!;
        final effectiveChipBg = _over(chipFill, renderedSurface); // composited if translucent

        final label = '${theme.brightness} on ${renderedSurface.toARGB32().toRadixString(16)}';
        expect(_contrastRatio(textColor, renderedSurface), greaterThanOrEqualTo(min), reason: 'value text $label');
        expect(_contrastRatio(textColor, effectiveChipBg), greaterThanOrEqualTo(min), reason: 'chip text $label');
      }
    });

    testWidgets('Case 7 (v2.1 MF-SAG-C4): AI range strings with and without \$ format as \$a - \$b; non-numeric never \$0.00', (tester) async {
      for (final raw in ['12.00 - 15.00', '\$12.00 - \$15.00']) {
        await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
          data: {'cpgRetail': 0.0, 'AI Estimated Value': raw, 'Denomination': 'Quarter Dollar'}))));
        expect(find.text('\$12.00 - \$15.00'), findsOneWidget, reason: 'input "$raw"');
      }
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
        data: {'cpgRetail': 0.0, 'AI Estimated Value': 'about twelve', 'Denomination': 'Quarter Dollar'}))));
      expect(find.text('\$0.00'), findsNothing);
      expect(find.text('\$about twelve'), findsOneWidget);
    });

    testWidgets('Case 8 (v2.3 MF-3): Non-US row with "cent" or blank-country "Centimes" never renders USD face value', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
        data: {'Country': 'Canada', 'Denomination': '1 Cent', 'cpgRetail': 0.0}))));
      expect(find.text('\$0.01'), findsNothing);
      expect(find.text('—'), findsOneWidget);

      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
        data: {'Denomination': '50 Centimes', 'cpgRetail': 0.0}))));
      expect(find.text('\$0.01'), findsNothing);
      expect(find.text('—'), findsOneWidget);
    });
  });
}
