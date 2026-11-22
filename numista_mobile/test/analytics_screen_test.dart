import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/screens/analytics_screen.dart';

void main() {
  final sampleCoins = [
    CoinModel(
      id: 'm1',
      country: 'USA',
      year: '1881',
      mintMark: 'S',
      denomination: 'Dollar',
      programSeries: 'Morgan Dollar',
      metalContent: '90% Silver',
      quantity: '2',
      cpgRetail: 80.0,
      greysheetBid: 65.0,
      meltValue: '\$24.00',
      purchaseCost: '\$50.00',
      gradingService: 'PCGS',
    ),
    CoinModel(
      id: 'g1',
      country: 'USA',
      year: '2024',
      mintMark: 'W',
      denomination: '\$50',
      programSeries: 'American Gold Eagle',
      metalContent: '1 oz Gold',
      quantity: '1',
      cpgRetail: 2800.0,
      greysheetBid: 2680.0,
      meltValue: '\$2650.00',
      purchaseCost: '\$2400.00',
      gradingService: 'NGC',
    ),
  ];

  Future<void> pumpAtSize(WidgetTester tester, Size size, Widget child) async {
    tester.view.physicalSize = size;
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() => tester.view.resetPhysicalSize());
    await tester.pumpWidget(MaterialApp(home: Scaffold(body: child)));
    await tester.pumpAndSettle();
  }

  testWidgets('AnalyticsScreen renders KPIs, coverage pills, and Morgan panel',
      (tester) async {
    await pumpAtSize(
      tester,
      const Size(1440, 860),
      AnalyticsScreen(
        initialCoins: sampleCoins,
        initialAdvancedMode: true,
        onMorganSubmitOverride: (q) async => {
          'reply': 'Mocked Morgan Analytics response for: $q',
          'action_coin_ids': ['m1'],
          'action_label': 'View 1 coin in My Collection',
        },
      ),
    );

    expect(find.text('Vault Analytics'), findsOneWidget);
    expect(find.text('3/3 priced'), findsOneWidget);
    expect(find.byKey(const Key('morgan_analytics_panel')), findsOneWidget);
    expect(find.byKey(const Key('duplicate_finder_card')), findsOneWidget);

    // Single-Morgan-Per-Screen: only 1 Ask Morgan entry point present
    expect(find.text('Ask Morgan Analytics'), findsOneWidget);
    expect(find.text('Ask Morgan AI'), findsNothing);
  });

  testWidgets('Spot Simulator preset updates simulated vault value',
      (tester) async {
    await pumpAtSize(
      tester,
      const Size(1440, 860),
      AnalyticsScreen(
        initialCoins: sampleCoins,
        initialAdvancedMode: true,
      ),
    );

    expect(find.byKey(const Key('sim_total_value')), findsOneWidget);
    await tester.tap(find.text('Silver \$50 / Gold \$3,500'));
    await tester.pumpAndSettle();

    // Gold Eagle 1 oz bumps from $2800 -> $3500; total = 3500 + 160 = $3660.00
    expect(find.text('\$3660.00'), findsOneWidget);
  });

  testWidgets('Zero RenderFlex overflow across Desktop, Tablet, and Phone',
      (tester) async {
    for (final size in const [
      Size(1440, 860),
      Size(1024, 768),
      Size(390, 844),
    ]) {
      await pumpAtSize(
        tester,
        size,
        AnalyticsScreen(
          initialCoins: sampleCoins,
          initialAdvancedMode: true,
        ),
      );
      expect(tester.takeException(), isNull,
          reason: 'Unexpected layout exception at $size');
    }
  });
}
