import 'dart:async';
import 'package:firebase_core/firebase_core.dart';
// ignore: depend_on_referenced_packages
import 'package:firebase_core_platform_interface/test.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/constants/denomination_canon.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/home_dashboard.dart';
import 'package:numista_ai/screens/login_screen.dart';
import 'package:numista_ai/screens/my_collection_screen.dart';
import 'package:numista_ai/screens/public_info_screens.dart';
import 'package:numista_ai/screens/settings_screen.dart';
import 'package:numista_ai/services/batch_valuation_service.dart';
import 'package:numista_ai/services/coin_data_normalizer.dart';
import 'package:numista_ai/services/display_preferences_service.dart';
import 'package:numista_ai/services/guest_seed_service.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/widgets/collection_card_valuation_row.dart';
import 'package:numista_ai/widgets/header_stats_bar.dart';
import 'package:numista_ai/widgets/morgan_owl_avatar.dart';

List<DemoDocumentSnapshot> _sampleVaultDocs({int count = 20}) {
  return List.generate(count, (i) {
    final idx = i + 1;
    final isSilverQuarter = i % 3 == 0;
    return DemoDocumentSnapshot('coin_$idx', {
      'Country': 'United States',
      'Year': isSilverQuarter ? '1958' : '${1965 + i}',
      'Mint Mark': i.isEven ? 'P' : 'D',
      'Denomination': isSilverQuarter ? 'Quarter Dollar' : 'Dollar',
      'Program/Series': isSilverQuarter ? 'Washington Quarters' : 'Morgan Dollar',
      'Metal Content': isSilverQuarter ? '90% Silver, 10% Copper' : 'Cupro-Nickel Clad',
      'Condition': i == 0 ? 'Unspecified / Raw' : 'MS65',
      'cpgRetail': i == 0 ? 0 : 125.00,
      'AI Estimated Value': i == 0 ? r'$0.00' : r'$125.00',
    });
  });
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setupFirebaseCoreMocks();

  setUpAll(() async {
    await Firebase.initializeApp();
  });

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    DisplayPreferencesService.instance.resetForTest(initialValue: true);
    BatchValuationService.instance.resetForTest();
  });

  tearDown(() {
    BatchValuationService.instance.resetForTest();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  group('WS 1 — Login Page Clean Light Polish & Accurate Catalog Stats', () {
    testWidgets('Desktop 1440x860 shows circular medallion, 274/3,202/U.S. & World, vector icons, zero emojis', (tester) async {
      tester.view.physicalSize = const Size(1440, 860);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(const MaterialApp(home: LoginScreen()));
      await tester.pumpAndSettle();

      // Circular ClipOval around brand logo_owl.png
      final clipImages = find.descendant(
        of: find.byType(ClipOval),
        matching: find.byWidgetPredicate(
          (w) => w is Image && w.image is AssetImage && (w.image as AssetImage).assetName == 'assets/logo_owl.png',
        ),
      );
      expect(clipImages, findsOneWidget);

      // Accurate stats strip & clarifier caption
      expect(find.text('274'), findsOneWidget);
      expect(find.text('3,202'), findsOneWidget);
      expect(find.text('U.S. & World'), findsOneWidget);
      expect(find.textContaining('U.S. Mint reference catalogs plus AI recognition'), findsOneWidget);

      // Approved Morgan owl vector/avatar replaces raw emojis
      expect(find.byType(MorganOwlAvatar), findsWidgets);
      for (final emoji in const ['🤖', '📊', '📋', '💬', '🧑']) {
        expect(find.textContaining(emoji), findsNothing);
      }
    });

    testWidgets('Phone 390x844 mounts LoginScreen with zero overflow and accurate stats', (tester) async {
      tester.view.physicalSize = const Size(390, 844);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(const MaterialApp(home: LoginScreen()));
      await tester.pumpAndSettle();

      expect(find.text('274'), findsOneWidget);
      expect(find.text('3,202'), findsOneWidget);
      expect(find.text('U.S. & World'), findsOneWidget);
    });
  });

  group('WS 2 & WS 3 — Full Beta Removal & Collection Value Default Visible + Settings Sync', () {
    test('DisplayPreferencesService defaults showCollectionValue to true', () {
      expect(DisplayPreferencesService.instance.showCollectionValue.value, isTrue);
    });

    testWidgets('HomeDashboard shows formatted currency by default and syncs with DisplayPreferencesService / Settings', (tester) async {
      tester.view.physicalSize = const Size(1440, 860);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final testStream = Stream<CombinedDashboardData>.value(
        CombinedDashboardData(
          coins: const [
            {
              'id': 'c1',
              'Program/Series': 'Morgan Dollar',
              'Year': '1881',
              'cpgRetail': 1344.30,
            },
          ],
          currency: const [],
          worldItems: const [],
        ),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HomeDashboard(testStream: testStream),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      // Default visible currency ($1,344.30) + MorganOwlAvatar + zero Beta copy
      expect(find.text(r'$1,344.30'), findsOneWidget);
      expect(find.text('Hide value'), findsOneWidget);
      expect(find.byType(MorganOwlAvatar), findsOneWidget);
      expect(find.byIcon(Icons.psychology_outlined), findsNothing);
      expect(find.textContaining('Beta'), findsNothing);
      expect(find.textContaining('beta'), findsNothing);

      // Toggling from Settings / DisplayPreferencesService updates Home immediately
      await DisplayPreferencesService.instance.setShowCollectionValue(false);
      await tester.pump();
      expect(find.text('Hidden for your safety'), findsOneWidget);
      expect(find.text('Show value'), findsOneWidget);

      await DisplayPreferencesService.instance.setShowCollectionValue(true);
      await tester.pump();
      expect(find.text(r'$1,344.30'), findsOneWidget);

      await tester.pumpWidget(const SizedBox.shrink());
      MorganScreenStateRegistry.instance.resetForTesting();
      MorganProactiveRescueObserver.instance.resetForTesting();
      await tester.pump();
    });

    testWidgets('SettingsScreen exposes synced Show Collection Value on Home toggle', (tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: SettingsScreen(testSkipInitialLoad: true),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      final switchFinder =
          find.widgetWithText(SwitchListTile, 'Show Collection Value on Home');
      expect(switchFinder, findsOneWidget);
      await tester.ensureVisible(switchFinder);
      await tester.pump();

      final tile = tester.widget<SwitchListTile>(switchFinder);
      expect(tile.value, isTrue);

      await tester.tap(switchFinder);
      await tester.pump();
      expect(DisplayPreferencesService.instance.showCollectionValue.value, isFalse);
    });

    testWidgets('PublicInfoShell (/features, /pricing, /faq) contains zero user-facing Beta strings', (tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      for (final route in const ['/features', '/pricing', '/faq']) {
        await tester.pumpWidget(
          MaterialApp(home: PublicInfoShell(targetRoute: route)),
        );
        await tester.pumpAndSettle();
        expect(find.textContaining('Beta'), findsNothing, reason: '$route must not show Beta');
        expect(find.textContaining('beta'), findsNothing, reason: '$route must not show beta');
      }
    });
  });

  group('WS 4 — Single Ask Morgan on Home & Send Feedback Label', () {
    testWidgets('BaseLayout hides lower-left sidebar Ask Morgan on Home and shows it on My Collection', (tester) async {
      tester.view.physicalSize = const Size(1440, 860);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      await tester.pumpWidget(
        MaterialApp(
          home: BaseLayout(
            isDemoMode: true,
            testSkipFirebase: true,
            testRouteBuilder: (route, _, _) => Center(child: Text('BODY:$route')),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      // On Home Dashboard: sidebar Ask Morgan button is hidden; Send Feedback is visible
      expect(find.text('BODY:Home Dashboard'), findsOneWidget);
      expect(find.text('Your AI guide'), findsNothing);
      expect(find.text('Send Feedback'), findsOneWidget);
      expect(find.textContaining('Beta'), findsNothing);

      // Navigate to My Collection: sidebar Ask Morgan appears
      await tester.tap(find.text('My Collection'));
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.text('BODY:My Collection'), findsOneWidget);
      expect(find.text('Your AI guide'), findsOneWidget);

      await tester.pumpWidget(const SizedBox.shrink());
      MorganScreenStateRegistry.instance.resetForTesting();
      MorganProactiveRescueObserver.instance.resetForTesting();
      await tester.pump();
    });
  });

  group('WS 5 — My Collection Cards Viewport Density (>= 3 rows) & Comma Stats', () {
    Future<void> verifyRowsInViewport(
      WidgetTester tester, {
      required Size size,
      required int minFullRows,
    }) async {
      tester.view.physicalSize = size;
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final docs = _sampleVaultDocs(count: 24);
      await tester.pumpWidget(
        MaterialApp(
          home: MyCollectionScreen(
            initialTab: 'Coins',
            initialDocsForTest: docs,
            initialIsCardViewForTest: true,
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      expect(find.text('BETA TESTING'), findsNothing);

      final cards = find.byType(Card);
      expect(cards, findsWidgets);

      final fullRowTops = <double>{};
      for (final elem in cards.evaluate()) {
        final box = elem.renderObject as RenderBox?;
        if (box == null || !box.hasSize) continue;
        final topLeft = box.localToGlobal(Offset.zero);
        final bottom = topLeft.dy + box.size.height;
        if (topLeft.dy >= 0 && bottom <= size.height) {
          fullRowTops.add((topLeft.dy / 4).round() * 4.0);
        }
      }

      expect(
        fullRowTops.length,
        greaterThanOrEqualTo(minFullRows),
        reason: 'Expected >= $minFullRows full card rows above the fold at $size, got $fullRowTops',
      );

      await tester.pumpWidget(const SizedBox.shrink());
      MorganScreenStateRegistry.instance.resetForTesting();
      MorganProactiveRescueObserver.instance.resetForTesting();
      await tester.pump();
    }

    testWidgets('Desktop 1440x860 fits >= 3 full card rows above the fold', (tester) async {
      await verifyRowsInViewport(
        tester,
        size: const Size(1440, 860),
        minFullRows: 3,
      );
    });

    testWidgets('Tablet Landscape 1024x768 fits >= 3 full card rows above the fold', (tester) async {
      await verifyRowsInViewport(
        tester,
        size: const Size(1024, 768),
        minFullRows: 3,
      );
    });

    testWidgets('Phone 390x844 fits >= 2 full card rows above the fold without overflow', (tester) async {
      await verifyRowsInViewport(
        tester,
        size: const Size(390, 844),
        minFullRows: 2,
      );
    });

    testWidgets('HeaderStatsBar formats large currency totals with commas', (tester) async {
      tester.view.physicalSize = const Size(1280, 900);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);

      final docs = [
        DemoDocumentSnapshot('d1', {
          'Country': 'United States',
          'Year': '1881',
          'Denomination': 'Dollar',
          'Metal Content': '90% Silver, 10% Copper',
          'cpgRetail': 1344.30,
          'AI Estimated Value': r'$1,344.30',
        }),
      ];

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: HeaderStatsBar(
              docs: docs,
              totalCoinsCount: 1,
              spotPrices: const {'Silver': 30.0},
              valuation: const BatchValuationProgress(),
              onRunValuation: () {},
              isFiltered: false,
            ),
          ),
        ),
      );
      await tester.pump();
      expect(find.textContaining(r'$1,344.30'), findsOneWidget);
    });
  });

  group('WS 6 — Valuation Floor, Melt, US Mint Normalization, Cert URL & Auto-Queue', () {
    testWidgets('CollectionCardValuationRow rejects \$0.00, shows Melt floor, Pending chip & compact Raw without truncation', (tester) async {
      final data = {
        'Year': '1958',
        'Denomination': 'Quarter Dollar',
        'Metal Content': 'Silve',
        'AI Estimated Value': r'$0.00',
        'cpgRetail': 0,
      };

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Center(
              child: SizedBox(
                width: 200, // 220px card minus padding
                child: CollectionCardValuationRow(
                  data: data,
                  condition: 'Unspecified / Raw',
                  spotPrices: const {'Silver': 60.0},
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.text(r'$0.00'), findsNothing);
      // 1958 90% Silver quarter melt at $60/oz = 0.18084 * 60 = $10.85 (> $0.25 face)
      expect(find.text(r'$10.85'), findsOneWidget);
      expect(find.text('Pending'), findsOneWidget);
      expect(find.text('Raw'), findsOneWidget);
      expect(find.text('Unspecified / Raw'), findsNothing);
    });

    test('DenominationCanon & CoinDataNormalizer Section 9.2 matrix + hard negatives', () {
      const cases = <String, String>{
        'penny': 'Cent',
        '1¢': 'Cent',
        '1₵': 'Cent',
        'nickel': 'Five Cents',
        '5₵': 'Five Cents',
        '10₵': 'Dime',
        'quarter': 'Quarter Dollar',
        '25C': 'Quarter Dollar',
        '.25 ₵': 'Quarter Dollar',
        'Fifty cent piece': 'Half Dollar',
        'JFK 50 cent piece': 'Half Dollar',
        r'$1 coin': 'Dollar',
      };
      for (final e in cases.entries) {
        expect(
          DenominationCanon.normalize(e.key, country: 'United States'),
          e.value,
          reason: 'Failed normalizing ${e.key}',
        );
      }

      // Hard negatives: foreign & banknotes remain untouched
      expect(DenominationCanon.normalize('25c', country: 'Canada'), '25c');
      expect(DenominationCanon.normalize(r'$5', itemType: 'paper_currency'), r'$5');

      // Exact founder 1958 Quarter screenshot fix
      final normalized = CoinDataNormalizer.normalizeCoinMap({
        'Year': '1958',
        'Denomination': '25C',
        'Metal Content': 'Silve',
        'Program/Series': 'Standard Circulation',
        'Condition': 'shiny',
        'AI Estimated Value': r'$0.00',
        'ai_value_status': 'valued',
      });
      expect(normalized['Denomination'], 'Quarter Dollar');
      expect(normalized['Metal Content'], '90% Silver, 10% Copper');
      expect(normalized['Program/Series'], 'Washington Quarters');
      expect(normalized['Condition'], 'Uncirculated');
      expect(normalized['AI Estimated Value'], 'Pending');
      expect(normalized['ai_value_status'], 'pending');

      // Plated / base-metal alloy guards
      expect(
        CoinDataNormalizer.normalizeMetal('Nickel Silver', year: '1958', canonicalDenom: 'Quarter Dollar'),
        'Nickel Silver',
      );
      expect(
        CoinDataNormalizer.normalizeMetal('Silver Plated', year: '1958', canonicalDenom: 'Quarter Dollar'),
        'Silver Plated',
      );
    });

    test('CoinModel.getVerificationUrl & computeNormV2Patch preserve NGC hyphens + numeric grade', () {
      final ngcCoin = CoinModel.fromMap({
        'Grading Service': 'NGC',
        'Certification Number': '6914394-002',
        'Condition': 'PF 69 ULTRA CAMEO',
      }, 'ngc1');
      expect(ngcCoin.getVerificationServiceLabel(), 'NGC');
      expect(
        ngcCoin.getVerificationUrl(),
        'https://www.ngccoin.com/certlookup/6914394-002/69/',
      );

      final pcgsCoin = CoinModel.fromMap({
        'Grading Service': 'PCGS',
        'Certification Number': '986403.70/53652580',
        'Condition': 'MS65',
      }, 'pcgs1');
      expect(pcgsCoin.getVerificationServiceLabel(), 'PCGS');
      expect(pcgsCoin.getVerificationUrl(), 'https://www.pcgs.com/cert/53652580');

      final rawCoin = CoinModel.fromMap({
        'Grading Service': 'None',
        'Certification Number': '',
        'Condition': 'AU58',
      }, 'raw1');
      expect(rawCoin.getVerificationServiceLabel(), isNull);
      expect(rawCoin.getVerificationUrl(), isNull);

      final healedPatch = CoinDataNormalizer.computeNormV2Patch({
        'Grading Service': 'NGC',
        'cert_number': '8321797-003',
        'Condition': 'PF 70 ULTRA CAMEO',
        'verify_link': 'https://www.pcgs.com/cert/8321797003',
      });
      expect(
        healedPatch['verify_link'],
        'https://www.ngccoin.com/certlookup/8321797-003/70/',
      );
    });

    test('BatchValuationService.enqueueSingleCoin deduplicates, caps cleanup <= 10, never writes \$0.00 on errors', () async {
      final svc = BatchValuationService.instance;
      svc.singleCoinDelay = Duration.zero;

      var apiCalls = 0;
      final writes = <String, Map<String, dynamic>>{};
      svc.testEstimateCaller = ({
        required year,
        required denomination,
        required mintMark,
        required condition,
        required programSeries,
        required metalContent,
        required country,
      }) async {
        apiCalls++;
        if (year == '1900') {
          throw Exception('API 500: simulated failure');
        }
        if (year == '1901') {
          return {'estimated_value': r'$0.00', 'numeric_median': 0};
        }
        return {
          'estimated_value': r'$45.00',
          'numeric_median': 45.0,
          'confidence': 'HIGH',
        };
      };
      svc.testFirestoreWriter = (uid, docId, payload) async {
        writes[docId] = payload;
      };

      // Deduplication check: same docId queued twice -> 1 call
      expect(
        svc.enqueueSingleCoin('u1', 'doc_dedup', {'Year': '1958', 'Denomination': '25C'}),
        isTrue,
      );
      expect(
        svc.enqueueSingleCoin('u1', 'doc_dedup', {'Year': '1958', 'Denomination': '25C'}),
        isFalse,
      );

      // 500 error & $0.00 response must never persist $0.00
      svc.enqueueSingleCoin('u1', 'doc_err_500', {'Year': '1900', 'Denomination': 'Cent'});
      svc.enqueueSingleCoin('u1', 'doc_zero_resp', {'Year': '1901', 'Denomination': 'Cent'});

      await svc.waitForSingleQueueForTest();

      expect(apiCalls, 3);
      expect(writes['doc_dedup']?['AI Estimated Value'], r'$45.00');
      expect(writes.containsKey('doc_err_500'), isFalse);
      expect(writes.containsKey('doc_zero_resp'), isFalse);

      // Storm cap check: fromCleanup <= 10 max per session
      svc.resetForTest();
      svc.singleCoinDelay = Duration.zero;
      svc.testEstimateCaller = ({
        required year,
        required denomination,
        required mintMark,
        required condition,
        required programSeries,
        required metalContent,
        required country,
      }) async =>
          {'estimated_value': r'$12.00', 'numeric_median': 12.0};
      svc.testFirestoreWriter = (_, _, _) async {};

      var accepted = 0;
      for (int i = 0; i < 15; i++) {
        if (svc.enqueueSingleCoin(
          'u1',
          'cleanup_$i',
          {'Year': '1960', 'Denomination': 'Dime'},
          fromCleanup: true,
        )) {
          accepted++;
        }
      }
      await svc.waitForSingleQueueForTest();
      expect(accepted, 10);
    });
  });
}
