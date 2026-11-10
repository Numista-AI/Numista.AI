import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/services/melt_value_service.dart';

Future<void> pumpLoadedCatalog(WidgetTester tester, Widget app) async {
  // PlatformAssetBundle extends CachingAssetBundle. This exact key is cached
  // before the screen starts, so its rootBundle.loadString hits a completed
  // Future instead of creating a compute() isolate inside fake async.
  expect(rootBundle, isA<CachingAssetBundle>());
  final loaded = await tester.runAsync<String>(() async {
    return rootBundle.loadString('assets/catalog/catalog_public_v1.json');
  });
  expect(loaded, isNotNull, reason: 'Real-async catalog preload must complete');
  expect(tester.takeException(), isNull, reason: 'Catalog preload must not fail');
  await tester.pumpWidget(app);
  // Bounded frames: never settle an indeterminate loading spinner.
  for (var frame = 0;
      frame < 20 && find.byType(CircularProgressIndicator).evaluate().isNotEmpty;
      frame++) {
    await tester.pump(const Duration(milliseconds: 50));
    if (find.byType(CircularProgressIndicator).evaluate().isNotEmpty) {
      await tester.runAsync(() => Future<void>.delayed(const Duration(milliseconds: 50)));
    }
  }
  expect(find.byType(CircularProgressIndicator), findsNothing,
      reason: 'Cached catalog must leave loading state within bounded frames');
}

void main() {
  group('NET-816 Chunk 1 — MeltValueService.parseFaceValue (#1 & NET-837 #2/#4/#5)', () {
    test('parses previously mis-valued catalog denominations, canonical names, sets, and planchets', () {
      const expectedByDenom = <String, double>{
        // Required CoS / Starter Prompt cases
        'Half dime': 0.05,
        '3 cents': 0.03,
        '3 Cents': 0.03,
        '10 Dollars': 10.00,
        '2 1/2 Dollars': 2.50,
        '1,000 Dollars': 1000.00,
        '10,000 Dollars': 10000.00,
        r'$1000': 1000.00,
        'Dime': 0.10,
        // Remaining N Dollars & catalog variants
        '1 Dollar': 1.00,
        '2 Dollars': 2.00,
        '5 Dollars': 5.00,
        '20 Dollars': 20.00,
        '50 Dollars': 50.00,
        '100 Dollars': 100.00,
        '500 Dollars': 500.00,
        'G\$2\u00bd': 2.50,
        r'$40': 40.00,
        r'$4 Stella': 4.00,
        'Half cent': 0.005,
        'half cent': 0.005,
        '1 Cent': 0.01,
        '1 cent': 0.01,
        '5 Cents': 0.05,
        '5 cents': 0.05,
        '10 Cents': 0.10,
        'Quarter': 0.25,
        '50 Cents': 0.50,
        'Half dollar': 0.50,
        'Dollar': 1.00,
        'Gold dollar': 1.00,
        r'1$': 1.00,
        // Canonical / user collection strings (caller blast radius)
        'Five Cents': 0.05,
        'Ten Cents': 0.10,
        'Ten Cent': 0.10,
        'Twenty-Five Cents': 0.25,
        'Fifty Cents': 0.50,
        'Three Cent Nickel': 0.03,
        '2 Cent': 0.02,
        '5 Dollar': 5.00,
        '25 Dollars (1/2 oz)': 25.00,
        // Multi-denomination sets, ranges, planchets & non-USD guards (NET-837 #5)
        r'$100/$50/$25/$10 platinum': 0.0,
        r'$50/$25/$10/$5 gold': 0.0,
        r'$1, $2, $5, $10 (uncut sheet)': 0.0,
        '3\u00a2\u201350\u00a2': 0.0,
        '50 cent coin planchet': 0.0,
        'Planchet for 1 Cent Coin': 0.0,
        '3.6 Candareens': 0.0,
        '': 0.0,
      };

      expectedByDenom.forEach((raw, expected) {
        expect(
          MeltValueService.parseFaceValue(raw),
          closeTo(expected, 1e-6),
          reason: 'Failed for denomination "$raw"',
        );
      });
    });

    test('full catalog_public_v1.json check: 0 mis-parses across all 3,202 entries, 66 non-null strings, and 71 (type, denomination) pairs', () {
      final file = File('assets/catalog/catalog_public_v1.json');
      final List<dynamic> rawList = json.decode(file.readAsStringSync()) as List<dynamic>;
      expect(rawList.length, 3202);

      // Exact 66 unique non-null denomination strings in catalog_public_v1.json (zero duplicate keys)
      const expectedCatalogDenomValues = <String, double>{
        r'$1 (1 oz silver)': 1.00,
        r'$10 eagle': 10.00,
        r'$100/$50/$25/$10 platinum': 0.00,
        r'$2.50 quarter eagle': 2.50,
        r'$20 double eagle': 20.00,
        r'$25 (1 oz palladium)': 25.00,
        r'$3': 3.00,
        r'$4 Stella': 4.00,
        r'$5 half eagle': 5.00,
        r'$50': 50.00,
        r'$50 (1 oz gold)': 50.00,
        r'$50/$25/$10/$5 gold': 0.00,
        '1 Cent': 0.01,
        '1 Dollar': 1.00,
        '1 cent': 0.01,
        r'1$': 1.00,
        '10 Cents': 0.10,
        '2 1/2 Dollars': 2.50,
        '20 Dollars': 20.00,
        '3 Cents': 0.03,
        '3 cents': 0.03,
        '3.6 Candareens': 0.00,
        '5 Cents': 0.05,
        '5 Dollars': 5.00,
        '5 cents': 0.05,
        '50 Cents': 0.50,
        '50 cent coin planchet': 0.00,
        'CC': 0.00,
        'D': 0.00,
        'Dime': 0.10,
        'Dollar': 1.00,
        'Dollar (two-coin set)': 1.00,
        'G\$2\u00bd': 2.50,
        'Gold dollar': 1.00,
        'Half cent': 0.005,
        'Half dime': 0.05,
        'Half dollar': 0.50,
        "New York World's Fair Billy Rose's Aquacade Commemorative Coin": 0.00,
        "New York World's Fair Frank Buck's Jungleland Commemorative Coin": 0.00,
        "New York World's Fair George Washington Commemorative Coin": 0.00,
        "New York World's Fair George Washington Inauguration Commemorative Coin": 0.00,
        "New York World's Fair Stack's Coin Dealers Commemorative Coin": 0.00,
        'O': 0.00,
        'Planchet for 1 Cent Coin': 0.00,
        'Quarter': 0.25,
        'Quarter (rolls/bags product)': 0.25,
        'copper': 0.00,
        'half cent': 0.005,
        r'$1': 1.00,
        r'$1, $2, $5, $10 (uncut sheet)': 0.00,
        r'$10': 10.00,
        r'$100': 100.00,
        r'$1000': 1000.00,
        r'$2': 2.00,
        r'$20': 20.00,
        r'$40': 40.00,
        r'$5': 5.00,
        r'$500': 500.00,
        '1,000 Dollars': 1000.00,
        '10 Dollars': 10.00,
        '10,000 Dollars': 10000.00,
        '100 Dollars': 100.00,
        '2 Dollars': 2.00,
        '3\u00a2\u201350\u00a2': 0.00,
        '50 Dollars': 50.00,
        '500 Dollars': 500.00,
      };
      expect(expectedCatalogDenomValues.length, 66);

      final seenPairs = <String>{};
      int misParses = 0;
      int medalCount = 0;
      for (final rawItem in rawList) {
        final item = Map<String, dynamic>.from(rawItem as Map);
        final type = item['type'] as String?;
        final denom = item['denomination'] as String?;
        seenPairs.add('$type|${denom ?? "NULL"}');
        if (type == 'medal') {
          medalCount++;
          expect(denom, isNull, reason: 'Medals have no face value denomination');
          continue;
        }
        expect(denom, isNotNull);
        final expected = expectedCatalogDenomValues[denom!];
        expect(expected, isNotNull, reason: 'Unmapped catalog denomination: $denom');
        final actual = MeltValueService.parseFaceValue(denom);
        if ((actual - expected!).abs() > 1e-6) {
          misParses++;
        }
      }
      expect(seenPairs.length, 71);
      expect(medalCount, 56);
      expect(misParses, 0);
    });

    test('caller blast-radius regression: header_stats_bar.dart:108 qty-weighted usdFaceSum & MeltValueService.compute', () {
      // Simulates header_stats_bar.dart:108 usdFaceSum accumulation over a multi-item collection
      final sampleCollection = <Map<String, dynamic>>[
        {'Denomination': 'Five Cents', 'qty': 4},           // 4 * 0.05 = 0.20 (was 0.04)
        {'Denomination': 'Twenty-Five Cents', 'qty': 2},    // 2 * 0.25 = 0.50 (was 0.02)
        {'Denomination': 'Half Dime', 'qty': 3},            // 3 * 0.05 = 0.15 (was 0.30)
        {'Denomination': 'Three Cent Nickel', 'qty': 1},    // 1 * 0.03 = 0.03 (was 0.05)
        {'Denomination': '25 Dollars (1/2 oz)', 'qty': 2},  // 2 * 25.00 = 50.00 (was 2.00)
      ];

      double usdFaceSum = 0.0;
      for (final m in sampleCollection) {
        final denom = m['Denomination'] as String;
        final qty = m['qty'] as int;
        usdFaceSum += MeltValueService.parseFaceValue(denom, qty: qty);
      }
      expect(usdFaceSum, closeTo(50.88, 1e-6));

      // Verify MeltValueService.compute (:141, :146, :200) uses corrected face values for gold/silver oz lookup
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};
      // 1/2 oz Gold Eagle ('25 Dollars (1/2 oz)', 91.67% gold) -> fv=25.0 -> 0.50 oz * 3000 = 1500.0
      final halfOzGoldEagleMelt = MeltValueService.compute(
        metalContent: '91.67% Gold',
        denomination: '25 Dollars (1/2 oz)',
        spotPrices: spot,
      );
      expect(halfOzGoldEagleMelt, closeTo(1500.0, 1e-4));

      // Pre-1933 Quarter Eagle ('2 1/2 Dollars', 90% gold) -> fv=2.5 -> 0.12094 oz * 3000 = 362.82
      final quarterEagleMelt = MeltValueService.compute(
        metalContent: '90% Gold',
        denomination: '2 1/2 Dollars',
        spotPrices: spot,
      );
      expect(quarterEagleMelt, closeTo(362.82, 1e-2));

      // 90% Silver Quarter ('Twenty-Five Cents') -> fv=0.25 -> 0.18084 oz * 30 = 5.4252
      final silverQuarterMelt = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty-Five Cents',
        spotPrices: spot,
      );
      expect(silverQuarterMelt, closeTo(5.4252, 1e-3));
    });

    test('NET-816 Fail-Fix A2 & D1-D3/N2/N4 regression: half dime, war nickel, sub-dollar silver, and Morgan dollars', () {
      const spot = <String, double>{'Gold': 3000.0, 'Silver': 30.0};

      // (a) Removed fallback: unlisted 90% sub-dollar returns null, NOT 0.77344
      final unlistedTwentyCent = MeltValueService.compute(
        metalContent: '90% Silver',
        denomination: 'Twenty Cent',
        spotPrices: spot,
      );
      expect(unlistedTwentyCent, isNull,
          reason: 'Unlisted sub-dollar silver must return null, never 0.77344');

      // (b) Dollar fallback preserved for Morgan/Peace without "dollar" in denomination
      final morganCC = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: 'CC',
        programSeries: r'1$-Morgan dollar',
        spotPrices: spot,
      );
      expect(morganCC, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with denom CC must receive 0.77344 dollar melt');

      final morganNoDenom = MeltValueService.compute(
        metalContent: 'Silver',
        denomination: '',
        programSeries: 'Morgan',
        spotPrices: spot,
      );
      expect(morganNoDenom, closeTo(0.77344 * 30.0, 1e-4),
          reason: 'Morgan with empty denom must receive 0.77344 dollar melt');

      // (c) Standard denominations preserved unchanged:
      // 90% Dime (0.07234 oz -> $2.1702 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dime', spotPrices: spot),
        closeTo(0.07234 * 30.0, 1e-4),
      );
      // 90% Quarter (0.18084 oz -> $5.4252 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Quarter', spotPrices: spot),
        closeTo(0.18084 * 30.0, 1e-4),
      );
      // 90% Half Dollar (0.36169 oz -> $10.8507 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.36169 * 30.0, 1e-4),
      );
      // 90% Dollar (0.77344 oz -> $23.2032 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Dollar', spotPrices: spot),
        closeTo(0.77344 * 30.0, 1e-4),
      );
      // 40% Half Dollar (0.14792 oz -> $4.4376 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '40% Silver', denomination: 'Half dollar', spotPrices: spot),
        closeTo(0.14792 * 30.0, 1e-4),
      );
      // 35% War Nickel (0.05626 oz -> $1.6878 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: '35% Silver', denomination: 'Nickel', spotPrices: spot),
        closeTo(0.05626 * 30.0, 1e-4),
      );

      // (d) N4: Wartime nickel with "Silver Alloy" and "Wartime Nickel" series (lacking "35%")
      expect(
        MeltValueService.compute(
          metalContent: 'Silver Alloy',
          denomination: '5 cents',
          programSeries: 'Jefferson Wartime Nickel',
          spotPrices: spot,
        ),
        closeTo(0.05626 * 30.0, 1e-4),
        reason: 'Jefferson Wartime Nickel in Silver Alloy must receive 0.05626 oz melt',
      );

      // (e) Half dime variants compute to 0.03617 oz * spot (~$1.0851 at $30/oz)
      expect(
        MeltValueService.compute(metalContent: 'Silver (90%)', denomination: 'Half Dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Silver (90%) Half Dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: 'Silver', denomination: 'Half dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: 'Generic "Silver" Half dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.compute(metalContent: '90% Silver', denomination: 'Half-dime', spotPrices: spot),
        closeTo(0.03617 * 30.0, 1e-4),
        reason: '"90% Silver" Half-dime must equal 0.03617 oz',
      );
      expect(
        MeltValueService.format(metalContent: '90% Silver', denomination: 'Half Dime', spotPrices: spot),
        equals(r'$1.09'),
        reason: r'Formatted melt value string at $30/oz silver spot must round to $1.09',
      );
    });
  });

  group('NET-816 Chunk 1 — _CatalogCard Widget Tests (#2 & NET-837 #3/#6)', () {
    testWidgets('shows "type photo (date may differ)" when isTypeImage is true and renders parsed face value + honest non-promissory chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      // 1842 Liberty Seated dollar in catalog_public_v1.json has primary_image: null, type_image != null, denomination: "Dollar"
      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: '1842 Liberty Seated dollar'),
        ),
      );
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      // Scoped to GridView so initialQuery inside the search TextField (:44, :505-506) does not double-match
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 Liberty Seated dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('1842 \u00b7 Dollar')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('type photo (date may differ)')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text(r'$1.00')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('Face value \u00b7 No retail estimate')),
        findsOneWidget,
      );
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('medal cards display "No face value" and omit face-value chip', (WidgetTester tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 2400));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await pumpLoadedCatalog(
        tester,
        const MaterialApp(
          home: CatalogBrowseScreen(initialQuery: 'Libertas Americana medal'),
        ),
      );
      await tester.pumpAndSettle();

      await tester.tap(find.text('Medals (56)'));
      await tester.pumpAndSettle();

      final gridFinder = find.byType(GridView);
      expect(gridFinder, findsOneWidget);

      expect(
        find.descendant(of: gridFinder, matching: find.textContaining('Libertas Americana medal')),
        findsOneWidget,
      );
      expect(
        find.descendant(of: gridFinder, matching: find.text('No face value')),
        findsOneWidget,
      );
      expect(find.text('Face Value N/A'), findsNothing);
      expect(find.text('Face value \u00b7 No retail estimate'), findsNothing);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });
  });
}
