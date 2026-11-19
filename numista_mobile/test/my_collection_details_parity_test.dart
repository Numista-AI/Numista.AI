import 'dart:convert';
import 'package:firebase_core/firebase_core.dart';
// ignore: depend_on_referenced_packages
import 'package:firebase_core_platform_interface/test.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/screens/coin_detail_screen.dart';
import 'package:numista_ai/screens/my_collection_screen.dart';
import 'package:numista_ai/screens/unified_coin_detail_screen.dart';
import 'package:numista_ai/services/guest_seed_service.dart';

class _TestFeaturesBundle extends CachingAssetBundle {
  final bool unifiedEnabled;
  _TestFeaturesBundle({required this.unifiedEnabled});

  @override
  Future<ByteData> load(String key) async => ByteData(0);

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (key == 'assets/config/features.json') {
      return jsonEncode({'unified_details_view_v1': unifiedEnabled});
    }
    return '{}';
  }
}

void _assertFullCoinDetailScreenOpen({required String expectedIdentityText}) {
  expect(find.text('Coin Inspector'), findsNothing);
  expect(find.byType(CoinDetailScreen), findsOneWidget);
  expect(find.textContaining(expectedIdentityText), findsWidgets);
  for (final tab in const [
    'Details',
    'Financials',
    'Provenance',
    'AI Insights',
    'History',
    'Legislation',
    'Known Errors',
  ]) {
    expect(find.text(tab), findsOneWidget);
  }
  expect(find.text('Wishlist'), findsOneWidget);
  expect(find.text('Edit'), findsOneWidget);
  expect(find.text('Delete'), findsOneWidget);
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setupFirebaseCoreMocks();

  setUpAll(() async {
    await Firebase.initializeApp();
  });

  setUp(() {
    UnifiedDetailsGate.debugReset();
    UnifiedDetailsGate.debugBundle = _TestFeaturesBundle(unifiedEnabled: false);
  });

  tearDown(() {
    UnifiedDetailsGate.debugBundle = null;
    UnifiedDetailsGate.debugReset();
  });

  List<DemoDocumentSnapshot> sampleDocs() => [
        DemoDocumentSnapshot('coin_1', {
          'Country': 'United States',
          'Year': '2024',
          'Mint Mark': 'P',
          'Denomination': 'Dollar',
          'Program/Series': 'Morgan Dollar',
          'Condition': 'MS65',
        }),
        DemoDocumentSnapshot('set_parent_1', {
          'Country': 'United States',
          'Year': '2023',
          'Denomination': 'Mint Set',
          'Program/Series': '2023 U.S. Mint Set',
          'is_set': true,
          'set_contents': [
            {
              'Country': 'United States',
              'Year': '2023',
              'Mint Mark': 'D',
              'Denomination': 'Quarter',
              'Theme/Subject': 'Bessie Coleman',
            },
          ],
        }),
      ];

  Widget buildCollectionApp({bool isCardView = true}) => MaterialApp(
        home: SizedBox(
          width: 1440,
          height: 900,
          child: MyCollectionScreen(
            initialTab: 'Coins',
            initialDocsForTest: sampleDocs(),
            initialIsCardViewForTest: isCardView,
          ),
        ),
      );

  void configureDesktopViewport(WidgetTester tester) {
    tester.view.physicalSize = const Size(1920, 1080);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.resetPhysicalSize);
    addTearDown(tester.view.resetDevicePixelRatio);

    final prevOnError = FlutterError.onError;
    FlutterError.onError = (FlutterErrorDetails details) {
      if (details.exceptionAsString().contains('A RenderFlex overflowed')) {
        return;
      }
      prevOnError?.call(details);
    };
    addTearDown(() => FlutterError.onError = prevOnError);
  }

  Future<void> pumpFrames(WidgetTester tester) async {
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 350));
    await tester.pump(const Duration(milliseconds: 350));
  }

  testWidgets('Cards view: tapping coin card opens full CoinDetailScreen', (tester) async {
    configureDesktopViewport(tester);
    await tester.pumpWidget(buildCollectionApp(isCardView: true));
    await pumpFrames(tester);

    await tester.tap(find.textContaining('Morgan Dollar').first);
    await pumpFrames(tester);

    _assertFullCoinDetailScreenOpen(expectedIdentityText: '2024');
  });

  testWidgets('Cards view: tapping virtual child opens parent CoinDetailScreen', (tester) async {
    configureDesktopViewport(tester);
    await tester.pumpWidget(buildCollectionApp(isCardView: true));
    await pumpFrames(tester);

    await tester.tap(find.textContaining('Bessie Coleman').first);
    await pumpFrames(tester);

    _assertFullCoinDetailScreenOpen(expectedIdentityText: '2023');
  });

  testWidgets('Table view: tapping (i) View Details and row cell both open CoinDetailScreen', (tester) async {
    configureDesktopViewport(tester);
    await tester.pumpWidget(buildCollectionApp(isCardView: false));
    await pumpFrames(tester);

    // Smoke check: Table view renders (i) View Details icon button when initialIsCardViewForTest is false.
    expect(find.byTooltip('View Details'), findsWidgets);

    await tester.tap(find.byTooltip('View Details').first);
    await pumpFrames(tester);
    _assertFullCoinDetailScreenOpen(expectedIdentityText: '2024');

    Navigator.of(tester.element(find.byType(CoinDetailScreen))).pop();
    await pumpFrames(tester);

    await tester.tap(find.textContaining('Morgan Dollar').first);
    await pumpFrames(tester);
    _assertFullCoinDetailScreenOpen(expectedIdentityText: '2024');
  });

  testWidgets('Missing-parent virtual child safely no-ops without crashing', (tester) async {
    configureDesktopViewport(tester);
    final orphanChildDoc = DemoDocumentSnapshot('orphan_child', {
      'Country': 'United States',
      'Year': '2022',
      'Denomination': 'Dime',
      'parent_set_id': 'missing_parent_id',
    });
    await tester.pumpWidget(MaterialApp(
      home: SizedBox(
        width: 1440,
        height: 900,
        child: MyCollectionScreen(
          initialTab: 'Coins',
          initialDocsForTest: [orphanChildDoc],
          initialIsCardViewForTest: true,
        ),
      ),
    ));
    await pumpFrames(tester);

    // Tapping parent_set_id badge when parent is missing in _cachedCoinsDocs must not throw or open Inspector.
    final badgeFinder = find.textContaining('Part of Set');
    if (badgeFinder.evaluate().isNotEmpty) {
      await tester.tap(badgeFinder.first);
      await pumpFrames(tester);
    }
    expect(find.text('Coin Inspector'), findsNothing);
    expect(find.byType(CoinDetailScreen), findsNothing);
  });

  testWidgets('UnifiedDetailsGate contract: false triggers legacyOpen', (tester) async {
    final coin = CoinModel.fromMap({'Year': '2024', 'Denomination': 'Dollar'}, 'gate_1');
    var legacyCalled = false;
    await tester.pumpWidget(MaterialApp(
      home: Builder(
        builder: (ctx) => ElevatedButton(
          onPressed: () => UnifiedCoinDetailScreen.show(
            ctx,
            coin: coin,
            legacyOpen: () => legacyCalled = true,
          ),
          child: const Text('Open'),
        ),
      ),
    ));
    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();
    expect(legacyCalled, isTrue);
  });
}
