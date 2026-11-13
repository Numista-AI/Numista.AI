import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/routing/public_catalog_route.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/screens/public_info_screens.dart';

Future<void> _pumpCatalogScreen(WidgetTester tester, Widget widget) async {
  await tester.pumpWidget(widget);
  // Allow real async rootBundle.loadString('assets/catalog/catalog_public_v1.json') + 2MB json.decode to complete
  for (var i = 0; i < 200; i++) {
    await tester.runAsync(() async {
      await Future<void>.delayed(const Duration(milliseconds: 250));
    });
    await tester.pump();
    if (find.byType(CircularProgressIndicator).evaluate().isEmpty) {
      break;
    }
  }
  expect(find.byType(CircularProgressIndicator), findsNothing);
  await tester.pump(const Duration(milliseconds: 100));
  await tester.pump(const Duration(milliseconds: 400));
}

void main() {
  setUp(() {
    rootBundle.evict('assets/catalog/catalog_public_v1.json');
  });

  group('main.dart Dispatch Route Extraction (MF-4)', () {
    test('extractInitialNac: returns null for bare /catalog', () {
      final uri = Uri.parse('https://numista.ai/catalog');
      expect(extractInitialNac(uri), isNull);
    });

    test('extractInitialNac: parses NAC from /catalog/<nac>', () {
      final uri = Uri.parse(
        'https://numista.ai/catalog/NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
      );
      expect(
        extractInitialNac(uri),
        equals('NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3'),
      );
    });

    test('extractInitialNac: parses NAC from query parameter ?item=<nac>', () {
      final uri = Uri.parse(
        'https://numista.ai/catalog?item=NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2',
      );
      expect(
        extractInitialNac(uri),
        equals('NAC1.CN.US.1C.LINCOLNCEN.1909.S.BASE.2'),
      );
    });

    test('extractInitialNac: returns null for non-catalog path', () {
      final uri = Uri.parse('https://numista.ai/pricing');
      expect(extractInitialNac(uri), isNull);
    });
  });

  testWidgets('Routing: Catalog loads successfully with light theme', (tester) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);

    await _pumpCatalogScreen(
      tester,
      const MaterialApp(
        home: CatalogBrowseScreen(),
      ),
    );

    expect(find.text('Public Catalog'), findsOneWidget);
    expect(find.text('U.S. Numismatics Catalog'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);
  });

  testWidgets(
    'Pricing: Fail-closed copy renders free-beta strings and excludes unapproved tier & ETA',
    (tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        const MaterialApp(
          home: PublicInfoShell(targetRoute: '/pricing'),
        ),
      );
      await tester.pumpAndSettle();

      // Positive assertions: 4 established free-beta strings (public_info_screens.dart:362/396/407/412)
      expect(find.textContaining('Free During Beta — Pricing TBA'), findsOneWidget);
      expect(find.textContaining(r'$0 / month'), findsOneWidget);
      expect(find.textContaining('completely free for registered participants.'), findsOneWidget);
      expect(find.textContaining('Existing beta accounts will be grandfathered'), findsOneWidget);

      // Negative assertions: unapproved paid tier & world-coverage ETA must be absent
      expect(find.textContaining(r'$30 / 6 months'), findsNothing);
      expect(find.textContaining('2027'), findsNothing);
    },
  );

  testWidgets('Routing: Valid NAC code auto-selects and displays detail', (tester) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);

    await _pumpCatalogScreen(
      tester,
      const MaterialApp(
        home: CatalogBrowseScreen(
          initialNacCode: 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
        ),
      ),
    );

    expect(find.text('1921-P Morgan Silver Dollars'), findsWidgets);
  });

  testWidgets('Routing: Unknown NAC code displays persistent in-screen banner', (tester) async {
    tester.view.physicalSize = const Size(1280, 900);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);

    await _pumpCatalogScreen(
      tester,
      const MaterialApp(
        home: CatalogBrowseScreen(
          initialNacCode: 'NAC1.CN.US.NONEXISTENT.BASE.9',
        ),
      ),
    );

    expect(
      find.textContaining(
        'Reference code "NAC1.CN.US.NONEXISTENT.BASE.9" was not found in the public catalog.',
      ),
      findsOneWidget,
    );
  });
}
