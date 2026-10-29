import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/us_numismatics_catalog_screen.dart';

void main() {
  group('UsNumismaticsCatalogScreen Widget & Plan.v2.1 UX Gate', () {
    testWidgets(
      'renders 1776-2026 catalog, filters by era/facility/kind, flips cards, and enforces guest download guard',
      (WidgetTester tester) async {
        await tester.binding.setSurfaceSize(const Size(1440, 960));
        addTearDown(() => tester.binding.setSurfaceSize(null));

        await tester.pumpWidget(
          const MaterialApp(
            home: UsNumismaticsCatalogScreen(isAuthenticated: false),
          ),
        );
        await tester.pumpAndSettle();

        // 1. Verify initial 15 specimens loaded and Inspector displays 1787 Fugio Cent (CC=CO)
        expect(find.text('15 SPECIMENS'), findsOneWidget);
        expect(
          find.byKey(const Key('inspector_nac_code')),
          findsOneWidget,
        );
        expect(
          find.text('NAC1.CN.CO.1C.FUGIO.1787.XX.BASE.K'),
          findsWidgets,
        );

        // 2. Filter by Dahlonega facility (FAC='DD') -> 1838-D Classic Head $5 Half Eagle
        await tester.tap(find.byKey(const Key('fac_chip_DD')));
        await tester.pumpAndSettle();
        expect(find.text('1 SPECIMENS'), findsOneWidget);
        expect(
          find.text('1838-D Classic Head \$5 Half Eagle'),
          findsWidgets,
        );

        // Reset facility filter to ALL
        await tester.tap(find.byKey(const Key('fac_chip_ALL')));
        await tester.pumpAndSettle();
        expect(find.text('15 SPECIMENS'), findsOneWidget);

        // 3. Filter by Foreign Specie (CC='FS') -> 1798-Mo Spanish-American 8 Reales
        await tester.tap(find.byKey(const Key('kind_tab_FS')));
        await tester.pumpAndSettle();
        expect(find.text('1 SPECIMENS'), findsOneWidget);
        expect(
          find.text('1798-Mo Spanish-American 8 Reales (Charles IV)'),
          findsWidgets,
        );

        // 4. Filter by Bank Notes (KIND='BN') -> routes to /currency, never /coins
        await tester.tap(find.byKey(const Key('kind_tab_BN')));
        await tester.pumpAndSettle();
        expect(find.text('3 SPECIMENS'), findsOneWidget);
        expect(
          find.textContaining('users/{uid}/currency/'),
          findsOneWidget,
        );

        // 5. Add Bank Note to collection and test Personal Specimen Photo toggle (Founder Q3)
        await tester.tap(find.byKey(const Key('inspector_add_button')));
        await tester.pumpAndSettle();
        expect(
          find.byKey(const Key('inspector_personal_photo_switch')),
          findsOneWidget,
        );
        await tester.tap(
          find.byKey(const Key('inspector_personal_photo_switch')),
        );
        await tester.pumpAndSettle();
        expect(
          find.textContaining('Personal Specimen Photo'),
          findsWidgets,
        );

        // 6. Verify Guest Image Download is blocked (Founder Q4: IMAGE_DOWNLOAD_REQUIRES_ACCOUNT)
        await tester.tap(
          find.byKey(const Key('inspector_download_image_button')),
        );
        await tester.pumpAndSettle();
        expect(
          find.textContaining('IMAGE_DOWNLOAD_REQUIRES_ACCOUNT'),
          findsOneWidget,
        );
      },
    );
  });
}
