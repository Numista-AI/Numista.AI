// numista_mobile/test/mint_product_fields_test.dart

import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // rootBundle, CachingAssetBundle, ByteData (v1.6)
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/mint_product_metadata.dart';
import 'package:numista_ai/services/mint_product_lookup_service.dart';
import 'package:numista_ai/screens/coin_detail_screen.dart';

/// v1.6 MF-3: test-only bundle. Catalog rows and overlay values are SYNTHETIC fixtures.
class _FixtureBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async => throw FlutterError('not used');
  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (key == 'assets/catalog/catalog_public_v1.json') {
      return jsonEncode([
        {'nac_code': 'NAC1.CN.US.FIXTURE.ELIGIBLE', 'type': 'coin', 'is_placeholder': false},
        {'nac_code': 'NAC1.CN.US.FIXTURE.STUB', 'type': 'coin', 'is_placeholder': true},
      ]);
    }
    if (key == 'assets/catalog/mint_product_fields_v1.json') {
      return jsonEncode({'NAC1.CN.US.FIXTURE.ELIGIBLE': {'product_price_usd': 1.0}});
    }
    throw FlutterError('Unable to load asset: $key');
  }
}

void main() {
  group('NET-810 Unit Tests: Join and Fail-Closed Logic', () {
    test('Primary NAC code join matches exact entry', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A': const MintProductMetadata(
            productPriceUsd: 80.00,
            mintScheduleStatus: 'NOT_AVAILABLE',
            productAvailability: 'No longer offered by U.S. Mint',
            releaseDate: '2024-07-11',
          ),
        },
        // v1.6 MF-2: primary join now requires an ELIGIBLE catalog row
        rawEntries: [
          {'nac_code': 'NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A', 'type': 'coin', 'is_placeholder': false},
        ],
      );

      final coin = CoinModel(
        id: 'c1',
        personalRef: 'NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A',
      );

      final meta = service.lookupForCoin(coin);
      expect(meta, isNotNull);
      expect(meta!.productPriceUsd, 80.00);
      expect(meta.displayStatus, 'No longer offered by U.S. Mint');
      expect(meta.displayReleaseDate, 'Jul 11, 2024');
    });

    test('Composite fallback matches single record and normalizes facility', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2': const MintProductMetadata(
            mintScheduleStatus: 'NOT_AVAILABLE',
            productAvailability: 'No longer offered by U.S. Mint',
          ),
        },
        rawEntries: [
          {
            'nac_code': 'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2',
            'type': 'coin',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
            'series': 'Morgan Silver Dollars',
            'is_placeholder': false,
            'status_badge': 'Needs source',
          }
        ],
      );

      final coin = CoinModel(
        id: 'c2',
        year: '1921',
        mintMark: 'D',
        denomination: 'Dollar',
        programSeries: 'Morgan Silver Dollars',
      );

      final meta = service.lookupForCoin(coin);
      expect(meta, isNotNull);
      expect(meta!.productAvailability, 'No longer offered by U.S. Mint');
    });

    test('Ambiguous composite match fails closed and returns null', () {
      final service = MintProductLookupService.forTesting(
        entries: {},
        rawEntries: [
          {
            'nac_code': 'NAC1.CN.US.DUP.1',
            'type': 'coin',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
            'series': 'Morgan Silver Dollars', // v1.6: complete keys so null is due to ambiguity
            'is_placeholder': false,
          },
          {
            'nac_code': 'NAC1.CN.US.DUP.2',
            'type': 'coin',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
            'series': 'Morgan Silver Dollars', // v1.6: complete keys so null is due to ambiguity
            'is_placeholder': false,
          },
        ],
      );

      final coin = CoinModel(id: 'c3', year: '1921', mintMark: 'D', denomination: 'Dollar', programSeries: 'Morgan Silver Dollars');
      expect(service.lookupForCoin(coin), isNull);
    });

    test('Quarantined placeholder status returns null (complete keys)', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.TEST': const MintProductMetadata(productAvailability: 'Should never render'),
        },
        rawEntries: [
          {
            'nac_code': 'NAC1.CN.US.TEST',
            'type': 'coin',
            'year': 2024,
            'mint_facility': 'West Point',
            'denomination': 'Dollar',
            'series': 'American Silver Eagle',
            'is_placeholder': true, // Sole reason lookup returns null
            'status_badge': 'Details coming',
          }
        ],
      );

      final coin = CoinModel(
        id: 'c4',
        year: '2024',
        mintMark: 'W',
        denomination: 'Dollar',
        programSeries: 'American Silver Eagle',
      );
      expect(service.lookupForCoin(coin), isNull);
    });

    test('v1.7 MF-5a: Non-US coin fails closed and returns null', () {
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2': const MintProductMetadata(
            productAvailability: 'No longer offered by U.S. Mint',
          ),
        },
        rawEntries: [
          {
            'nac_code': 'NAC1.CN.US.1D.MORGANSILV.1921.D.BASE.2',
            'type': 'coin',
            'year': 1921,
            'mint_facility': 'Denver',
            'denomination': 'Dollar',
            'series': 'Morgan Silver Dollars',
            'is_placeholder': false,
          },
        ],
      );
      final canadian = CoinModel(
        id: 'c-ca',
        country: 'Canada',
        year: '1921',
        mintMark: 'D',
        denomination: 'Dollar',
        programSeries: 'Morgan Silver Dollars',
      );
      expect(service.lookupForCoin(canadian), isNull);
    });
  });

  group('NET-810 Widget Tests: Detail Tab & Styling', () {
    testWidgets('Detail tab renders exact issue price label and muted styling', (tester) async {
      final coin = CoinModel(
        id: 'test-widget-coin',
        year: '2024',
        denomination: 'Dollar',
        mintMark: 'W',
      );

      const metadata = MintProductMetadata(
        productPriceUsd: 80.00,
        mintScheduleStatus: 'NOT_AVAILABLE',
        productAvailability: 'No longer offered by U.S. Mint',
        releaseDate: '2024-07-11',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DetailsTab(
              coin: coin,
              mintMetadata: metadata,
              onInspectField: (_, _) {},
            ),
          ),
        ),
      );

      // Verify exact neutral factual labels
      expect(find.text('Original U.S. Mint Issue Price'), findsOneWidget);
      expect(find.text('\$80.00'), findsOneWidget);
      expect(find.text('Mint Schedule Status'), findsOneWidget);
      expect(find.text('Product Availability'), findsOneWidget);
      expect(find.text('No longer offered by U.S. Mint'), findsNWidgets(2));
      expect(find.text('Original Release Date'), findsOneWidget);
      expect(find.text('Jul 11, 2024'), findsOneWidget);

      // Verify muted font weight
      final priceWidget = tester.widget<Text>(find.text('\$80.00'));
      expect(priceWidget.style?.fontWeight, FontWeight.normal);

      // Verify non-muted standard field has bold font weight
      final yearWidget = tester.widget<Text>(find.text('2024'));
      expect(yearWidget.style?.fontWeight, FontWeight.bold);
    });

    testWidgets('Detail tab renders ZERO commercial buy buttons or cart interactions', (tester) async {
      final coin = CoinModel(
        id: 'test-no-commerce-coin',
        year: '2024',
        denomination: 'Dollar',
      );

      const metadata = MintProductMetadata(
        productPriceUsd: 80.00,
        mintScheduleStatus: 'NOT_AVAILABLE',
      );

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DetailsTab(
              coin: coin,
              mintMetadata: metadata,
              onInspectField: (_, _) {},
            ),
          ),
        ),
      );

      // Assert zero commercial buy/cart action widgets
      expect(find.byType(ElevatedButton), findsNothing);
      expect(find.byType(TextButton), findsNothing);
      expect(find.byType(OutlinedButton), findsNothing);
      expect(find.textContaining('Buy', findRichText: true), findsNothing);
      expect(find.textContaining('Cart', findRichText: true), findsNothing);
      expect(find.textContaining('Order', findRichText: true), findsNothing);
      expect(find.textContaining('Shop', findRichText: true), findsNothing);
    });
  });

  group('NET-810 Verification: Zero Firestore Writes & PII Absence (MF-1, MF-3)', () {
    testWidgets('Lookup + DetailsTab render/tap touch no Firestore client (R2)', (tester) async {
      // No Firebase.initializeApp() is called anywhere in this file. Any access to
      // FirebaseFirestore.instance from lookup or DetailsTab would throw
      // (FlutterFire [core/no-app]) and fail this test.
      final service = MintProductLookupService.forTesting(
        entries: {
          'NAC1.CN.US.TEST': const MintProductMetadata(
            productPriceUsd: 80.00,
            mintScheduleStatus: 'NOT_AVAILABLE',
            productAvailability: 'No longer offered by U.S. Mint',
            releaseDate: '2024-07-11',
          ),
        },
        rawEntries: [{'nac_code': 'NAC1.CN.US.TEST', 'type': 'coin', 'is_placeholder': false}], // v1.6 MF-2
      );

      final coin = CoinModel(
        id: 'c-fs-test',
        personalRef: 'NAC1.CN.US.TEST',
        year: '2024',
        denomination: 'Dollar',
      );

      final meta = service.lookupForCoin(coin);
      expect(meta, isNotNull);

      // Render DetailsTab with the resolved metadata
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: DetailsTab(
              coin: coin,
              mintMetadata: meta,
              onInspectField: (_, _) {},
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Exercise interaction: tap the issue price detail tile
      final priceFinder = find.text('\$80.00');
      expect(priceFinder, findsOneWidget);
      await tester.tap(priceFinder);
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
    });

    testWidgets('v1.6 MF-3: ensureInitialized + DetailsTab run with no Firebase app and surface no swallowed error', (tester) async {
      // _FixtureBundle: test-only AssetBundle returning a 2-row catalog (one explicit false, one placeholder)
      // and a SYNTHETIC overlay. No Firebase.initializeApp anywhere in this file.
      final fresh = MintProductLookupService.forInitTesting(); // uninitialized instance (no entries)
      await tester.runAsync(() => fresh.ensureInitialized(bundle: _FixtureBundle()));
      expect(fresh.lastInitError, isNull);
      final coin = CoinModel(id: 'x', personalRef: 'NAC1.CN.US.FIXTURE.ELIGIBLE');
      final meta = fresh.lookupForCoin(coin);
      expect(meta, isNotNull);
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: DetailsTab(coin: coin, mintMetadata: meta, onInspectField: (_, _) {}))));
      await tester.pumpAndSettle();
      expect(tester.takeException(), isNull);
      // MUTATION CRITERION: adding FirebaseFirestore.instance to ensureInitialized / lookupForCoin /
      // DetailsTab.build throws [core/no-app]; it is NOT caught (only FlutterError/FormatException are),
      // so this test fails.
    });
  });

  group('v1.6 MF-2: placeholder quarantine applies to BOTH joins', () {
    final overlay = {'NAC1.CN.US.TEST': const MintProductMetadata(productPriceUsd: 1.0)}; // synthetic
    test('primary NAC pointing at a placeholder row returns null', () {
      final s = MintProductLookupService.forTesting(entries: overlay, rawEntries: [
        {'nac_code': 'NAC1.CN.US.TEST', 'type': 'coin', 'is_placeholder': true},
      ]);
      expect(s.lookupForCoin(CoinModel(id: 'a', personalRef: 'NAC1.CN.US.TEST')), isNull);
    });
    test('primary NAC with no catalog row returns null', () {
      final s = MintProductLookupService.forTesting(entries: overlay, rawEntries: const []);
      expect(s.lookupForCoin(CoinModel(id: 'a', personalRef: 'NAC1.CN.US.TEST')), isNull);
    });
    test('missing is_placeholder flag is ineligible', () {
      final s = MintProductLookupService.forTesting(entries: overlay, rawEntries: [
        {'nac_code': 'NAC1.CN.US.TEST', 'type': 'coin'},
      ]);
      expect(s.lookupForCoin(CoinModel(id: 'a', personalRef: 'NAC1.CN.US.TEST')), isNull);
    });
    test('composite: row missing facility or series does not match', () {
      final s = MintProductLookupService.forTesting(entries: overlay, rawEntries: [
        {'nac_code': 'NAC1.CN.US.TEST', 'type': 'coin', 'is_placeholder': false, 'year': 2024, 'denomination': 'Dollar', 'series': 'Fixture Series'},
        {'nac_code': 'NAC1.CN.US.TEST2', 'type': 'coin', 'is_placeholder': false, 'year': 2024, 'denomination': 'Dollar', 'mint_facility': 'West Point'},
      ]);
      expect(s.lookupForCoin(CoinModel(id: 'a', year: '2024', mintMark: 'W', denomination: 'Dollar', programSeries: 'Fixture Series')), isNull);
    });
    test('composite: blank mint mark resolves to Philadelphia', () {
      final s = MintProductLookupService.forTesting(entries: overlay, rawEntries: [
        {'nac_code': 'NAC1.CN.US.TEST', 'type': 'coin', 'is_placeholder': false, 'year': 1921, 'denomination': 'Dollar', 'series': 'Fixture Series', 'mint_facility': 'Philadelphia'},
      ]);
      expect(s.lookupForCoin(CoinModel(id: 'a', year: '1921', mintMark: '', denomination: 'Dollar', programSeries: 'Fixture Series')), isNotNull);
    });
  });

  group('NET-810 privacy', () {
    testWidgets('Serialized Mint metadata and real public catalog record guarantee 0 private collector keys (MF-3, R4)', (tester) async {
      // 1. Serialize overlay JSON emitted by MintProductMetadata / scripts/export_mint_product_fields.py
      const metadata = MintProductMetadata(
        productPriceUsd: 80.00,
        mintScheduleStatus: 'NOT_AVAILABLE',
        productAvailability: 'No longer offered by U.S. Mint',
        releaseDate: '2024-07-11',
      );
      final serializedOverlay = metadata.toJson();

      // 2. Load the REAL public catalog record from assets/catalog/catalog_public_v1.json
      // R4: asset bundle only (no CWD-relative File). Requires §4.4 pubspec registration of assets/catalog/.
      final rawString = await tester.runAsync(
        () => rootBundle.loadString('assets/catalog/catalog_public_v1.json'),
      );
      final catalogList = jsonDecode(rawString!) as List<dynamic>;

      final realRecord = catalogList.firstWhere(
        (item) => item['nac_code'] == 'NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A',
      ) as Map<String, dynamic>;

      // Assert real record exists with authentic public catalog fields
      expect(realRecord['nac_code'], 'NAC1.CN.US.1D.AMERICANSI.2024.W.SILVEREAGL.A');
      expect(realRecord['status_badge'], 'Needs source');
      expect(realRecord['is_placeholder'], isFalse);

      // 3. Assert all 10 forbidden private collector keys are absent from BOTH real objects
      const forbiddenPrivateKeys = [
        'Purchase Cost', 'purchaseCost',
        'Purchase Date', 'purchaseDate',
        'Retailer/Website', 'retailer',
        'Retailer Item No.', 'retailerItemNo',
        'Retailer Invoice #', 'retailerInvoiceNo',
        'Storage Location', 'storageLocation',
        'Personal Notes I', 'personalNotes',
        'Personal Reference #', 'personalRef',
        'owner_photos', 'ownerPhotos',
        'provenanceLedger',
        'transferStatus', 'transferId',
      ];

      for (final forbidden in forbiddenPrivateKeys) {
        expect(serializedOverlay.containsKey(forbidden), isFalse,
            reason: 'Forbidden private key $forbidden leaked into serialized overlay metadata!');
        expect(realRecord.containsKey(forbidden), isFalse,
            reason: 'Forbidden private key $forbidden leaked into real public catalog record!');
      }
    });
  });
}
