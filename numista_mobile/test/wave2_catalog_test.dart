import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/screens/catalog/catalog_browse_screen.dart';
import 'package:numista_ai/screens/catalog/us_numismatics_catalog_screen.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/utils/catalog_image_guard.dart';

void main() {
  group('Wave 2 Component F — Image Guard Allow-List (3 GCS Buckets + CR3 P5 Hosts)', () {
    test('approves all 3 GCS image buckets and CR3 P5 source hosts; rejects attacks', () {
      // All 3 approved GCS image buckets (SAG 96 residual check)
      expect(
        isApprovedCatalogImageUrl(
          'https://storage.googleapis.com/us_mint_coin_images/catalog/test.jpg',
        ),
        isTrue,
      );
      expect(
        isApprovedCatalogImageUrl(
          'https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/test.jpg',
        ),
        isTrue,
      );
      expect(
        isApprovedCatalogImageUrl(
          'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/reference/promoted.jpg',
        ),
        isTrue,
      );
      // Reject unpromoted user uploads path on 3rd bucket
      expect(
        isApprovedCatalogImageUrl(
          'https://storage.googleapis.com/numista-uploads-studio-9101802118-8c9a8/users/private.jpg',
        ),
        isFalse,
      );
      // CR3 P5 exact 3 image source_url hosts
      expect(isApprovedSourceUrl('https://www.usmint.gov/coins'), isTrue);
      expect(isApprovedSourceUrl('https://usmint.gov/coins'), isTrue);
      expect(isApprovedSourceUrl('https://commons.wikimedia.org/wiki/File:Test.jpg'), isTrue);
      expect(isApprovedSourceUrl('http://www.usmint.gov/coins'), isFalse);
      expect(isApprovedSourceUrl('https://www.usmint.gov:443/coins'), isFalse);
      expect(isApprovedSourceUrl('https://user@www.usmint.gov/coins'), isFalse);
      expect(isApprovedSourceUrl('https://evil.usmint.gov/coins'), isFalse);
    });
  });

  group('Wave 2 Component D — 17-Row Capped Bust Right search_aliases Gate & nac_aliases', () {
    final gd5Heraldic = [
      'NAC1.CN.US.GD5.TURBANHEAD.1797.P.HERALDICEA.J',
      'NAC1.CN.US.GD5.TURBANHEAD.1798.P.HERALDICEA.F',
      'NAC1.CN.US.GD5.DRAPEDBUST.1799.P.BASE.2', // 1799 $5 hold intact!
      'NAC1.CN.US.GD5.DRAPEDBUST.1800.P.BASE.7',
      'NAC1.CN.US.GD5.DRAPEDBUST.1802.P.OD18021.T',
      'NAC1.CN.US.GD5.DRAPEDBUST.1803.P.OD18032.K',
      'NAC1.CN.US.GD5.DRAPEDBUST.1804.P.BASE.3',
      'NAC1.CN.US.GD5.DRAPEDBUST.1805.P.BASE.5',
      'NAC1.CN.US.GD5.DRAPEDBUST.1806.P.BASE.C',
      'NAC1.CN.US.GD5.DRAPEDBUST.1807.P.BASE.K',
    ];
    final gd5SmallEagle = [
      'NAC1.CN.US.GD5.DRAPEDBUST.1796.P.OD17965.7',
      'NAC1.CN.US.GD5.TURBANHEAD.1797.P.SMALLEAGLE.3',
      'NAC1.CN.US.GD5.TURBANHEAD.1798.P.SMALLEAGLE.0',
    ];
    final gd10Heraldic = [
      'NAC1.CN.US.GD10.TURBANHEAD.1797.P.HERALDICEA.P',
      'NAC1.CN.US.GD10.TURBANHEAD.1798.P.HERALDICEA.K',
      'NAC1.CN.US.GD10.TURBANHEAD.1799.P.HERALDICEA.G',
      'NAC1.CN.US.GD10.TURBANHEAD.1800.P.HERALDICEA.3',
    ];

    final entries = <Map<String, dynamic>>[
      for (final code in [...gd5Heraldic, ...gd10Heraldic])
        {
          'nac_code': code,
          'name': 'Capped Bust Right Gold ($code)',
          'type': 'coin',
          'series': 'Capped Bust Right',
          'search_aliases': ['Turban Head', 'Draped Bust', 'Capped Bust to Right', 'Heraldic Eagle'],
        },
      for (final code in gd5SmallEagle)
        {
          'nac_code': code,
          'name': 'Capped Bust Right Gold ($code)',
          'type': 'coin',
          'series': 'Capped Bust Right',
          'search_aliases': ['Turban Head', 'Draped Bust', 'Capped Bust to Right', 'Small Eagle'],
        },
      // 1807 Reich Capped Bust Left MUST stay unrenamed and excluded!
      {
        'nac_code': 'NAC1.CN.US.GD5.CAPPEDBUST.1807.P.BASE.A',
        'name': '1807 Capped Bust Left \$5 Half Eagle',
        'type': 'coin',
        'series': 'Capped Bust Left',
        'search_aliases': <String>[],
      },
    ];

    test('all 17 Capped Bust Right rows match Turban Head, Draped Bust, Capped Bust to Right; reverse filters stay strict; 1807 Left excluded', () {
      for (final q in ['Turban Head', 'Draped Bust', 'Capped Bust to Right']) {
        final hits = CatalogBrowseScreen.filterEntriesForTest(entries, query: q);
        expect(hits.length, 17, reason: 'Query "$q" must match all 17 Capped Bust Right rows');
        expect(hits.any((e) => e['nac_code'] == 'NAC1.CN.US.GD5.CAPPEDBUST.1807.P.BASE.A'), isFalse);
        expect(hits.any((e) => e['nac_code'] == 'NAC1.CN.US.GD5.DRAPEDBUST.1799.P.BASE.2'), isTrue);
      }

      final heraldicHits = CatalogBrowseScreen.filterEntriesForTest(entries, query: 'Heraldic Eagle');
      expect(heraldicHits.length, 14);
      final smallEagleHits = CatalogBrowseScreen.filterEntriesForTest(entries, query: 'Small Eagle');
      expect(smallEagleHits.length, 3);
    });

    test('resolveEntryByNacOrAlias resolves 1875 20C and 1795/1798 1D retired aliases', () {
      final recoded = [
        {
          'nac_code': 'NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0',
          'nac_aliases': ['NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1'],
          'name': '1875-S twenty-cent piece',
        },
        {
          'nac_code': 'NAC1.CN.US.1D.FLOWINGHAI.1795.P.BASE.J',
          'nac_aliases': ['NAC1.CN.US.D1.FLOWINGHAI.1795.P.BASE.S'],
          'name': '1795 Flowing hair',
        },
      ];
      final hit20c = CatalogBrowseScreen.resolveEntryByNacOrAliasForTest(
        recoded,
        'NAC1.CN.US.1C.20CENTPIEC.1875.S.BASE.1',
      );
      expect(hit20c?['nac_code'], 'NAC1.CN.US.20C.TWENTYCENT.1875.S.BASE.0');

      final hit1d = CatalogBrowseScreen.resolveEntryByNacOrAliasForTest(
        recoded,
        'NAC1.CN.US.D1.FLOWINGHAI.1795.P.BASE.S',
      );
      expect(hit1d?['nac_code'], 'NAC1.CN.US.1D.FLOWINGHAI.1795.P.BASE.J');
    });
  });

  group('Wave 2 Components E & F — OGP/Set Flip, Privy Detail, AI Watermark & 31 CFR § 411.1', () {
    testWidgets('Set OGP packaging + set_members tap-to-flip + privy_detail + credit scrub', (tester) async {
      final setItem = <String, dynamic>{
        'nac_code': 'NAC1.CN.US.SET.UNCSET.2026.XX.26RJ.X',
        'name': 'Uncirculated Coin Set 2026 (26RJ)',
        'type': 'coin',
        'packaging_images': [
          {
            'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/26rj_a.webp',
            'side': 'packaging',
            'role': 'packaging',
            'credit': 'Used with permission of the US Mint',
            'source_url': 'https://www.usmint.gov/uncirculated-coin-set-2026-26RJ.html',
          }
        ],
        'extra_images': [
          {
            'url': 'https://storage.googleapis.com/us_mint_coin_images/catalog/privy_demo.jpg',
            'side': 'privy_detail',
            'role': 'privy_detail',
            'credit': 'Image: United States Mint',
            'source_url': 'https://www.usmint.gov/',
          }
        ],
        'set_members': [
          {
            'position': 1,
            'label': '2026-P Mayflower Quarter',
            'default_side': 'reverse',
            'obverse': {'url': 'https://storage.googleapis.com/us_mint_coin_images/catalog/q_obv.jpg'},
            'reverse': {'url': 'https://storage.googleapis.com/us_mint_coin_images/catalog/q_rev.jpg'},
          }
        ],
      };

      expect(resolveCatalogImageCaption(setItem['packaging_images'][0]), 'Image: United States Mint');
      expect(resolveCatalogCardImage(setItem)?.role, 'packaging');

      await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(child: CatalogDetailImagesView(item: setItem)))));
      await tester.pump();

      expect(find.byKey(const Key('privy_detail_label')), findsOneWidget);
      expect(find.byKey(const Key('set_members_header')), findsOneWidget);
      expect(find.text('Showing: reverse'), findsOneWidget);

      // Tap member tile to flip reverse -> obverse
      await tester.tap(find.byKey(const Key('set_member_tile_0')));
      await tester.pump();
      expect(find.text('Showing: obverse'), findsOneWidget);
    });

    testWidgets('AI Coin & 31 CFR § 411.1 Banknote watermark + captions + AI reverse dropped', (tester) async {
      final aiCoin = <String, dynamic>{
        'nac_code': 'NAC1.CN.US.10C.MERCURY.1916.D.BASE.9',
        'name': '1916-D Mercury Dime',
        'type': 'coin',
        'primary_image': {
          'url': 'https://storage.googleapis.com/us_mint_coin_images/catalog/1916d_ai_obv.jpg',
          'side': 'obverse',
          'ai_generated': true,
          'credit': 'Numista.Ai AI Reference',
        },
      };

      await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(child: CatalogDetailImagesView(item: aiCoin)))));
      await tester.pump();
      expect(find.byKey(const Key('ai_generated_watermark_badge')), findsOneWidget);
      expect(find.text(kAiWatermarkLabel), findsOneWidget);
      expect(find.text(kAiCoinDisclosureLabel), findsOneWidget);

      final aiNote = <String, dynamic>{
        'nac_code': 'NAC1.BN.US.SC1.SCLARGE.1896.BEP.BASE.D',
        'name': 'Series 1896 \$1 Silver Certificate',
        'type': 'note',
        'primary_image': {
          'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/1896_ai_obv.jpg',
          'side': 'obverse',
          'ai_generated': true,
          'credit': 'Numista.Ai AI Note Reference',
        },
        'secondary_image': {
          'url': 'https://storage.googleapis.com/numista-reference-library/reference_library/us_banknotes/1896_ai_rev.jpg',
          'side': 'reverse',
          'ai_generated': true,
          'credit': 'Should be dropped',
        },
      };

      // Fail-closed 31 CFR § 411.1 check: AI reverse dropped, only 1 obverse image rendered
      final resolvedNoteImgs = resolveCatalogDetailImages(aiNote);
      expect(resolvedNoteImgs.length, 1);
      expect(resolvedNoteImgs.first.side, 'obverse');

      await tester.pumpWidget(MaterialApp(home: Scaffold(body: SingleChildScrollView(child: CatalogDetailImagesView(item: aiNote)))));
      await tester.pump();
      expect(find.text(kAiBanknoteDisclosureLabel), findsOneWidget);
      expect(find.text(kAiWatermarkLabel), findsOneWidget);
    });
  });

  group('Wave 2 Components A & B — Rename & Consolidated Sidebar Navigation', () {
    testWidgets('UsNumismaticsCatalogScreen header renamed to Catalog of American Numismatics', (tester) async {
      await tester.binding.setSurfaceSize(const Size(1440, 960));
      addTearDown(() => tester.binding.setSurfaceSize(null));
      await tester.pumpWidget(const MaterialApp(home: UsNumismaticsCatalogScreen(isAuthenticated: false)));
      await tester.pumpAndSettle();
      expect(find.text('CATALOG OF AMERICAN NUMISMATICS (1787 – 2026)'), findsOneWidget);
    });

    testWidgets('BaseLayout consolidates Research sidebar, removes Numista Lookup, binds Ctrl+K to Catalog', (tester) async {
      MorganScreenStateRegistry.instance.resetForTesting();
      MorganProactiveRescueObserver.instance.resetForTesting();
      addTearDown(() {
        MorganProactiveRescueObserver.instance.resetForTesting();
        MorganScreenStateRegistry.instance.resetForTesting();
      });

      await tester.binding.setSurfaceSize(const Size(1440, 900));
      addTearDown(() => tester.binding.setSurfaceSize(null));

      await tester.pumpWidget(
        MaterialApp(
          home: MediaQuery(
            data: const MediaQueryData(size: Size(1440, 900)),
            child: BaseLayout(
              isDemoMode: true,
              testSkipFirebase: true,
              testRouteBuilder: (route, q, tab) => Center(child: Text('ROUTE:$route')),
            ),
          ),
        ),
      );
      await tester.pump();
      await tester.pump(const Duration(milliseconds: 50));

      // Top-level Catalog entry present; duplicate Numista Lookup absent
      expect(find.text('Catalog'), findsOneWidget);
      await tester.tap(find.text('Research'));
      await tester.pump();
      expect(find.text('Numista Lookup'), findsNothing);
      expect(find.text('Catalog of American Numismatics'), findsOneWidget);

      // Ctrl+K opens Catalog of American Numismatics
      await tester.sendKeyEvent(LogicalKeyboardKey.tab);
      await tester.pump();
      await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
      await tester.sendKeyDownEvent(LogicalKeyboardKey.keyK);
      await tester.sendKeyUpEvent(LogicalKeyboardKey.keyK);
      await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);
      await tester.pump();
      expect(find.text('ROUTE:Catalog of American Numismatics'), findsOneWidget);
      MorganProactiveRescueObserver.instance.resetForTesting();
    });

    test('Gemini W2-1 & Muse Merge-Order Fixes: ai_chat_screen handles mintage_display/image_url, Map missing_item_report_prompt, missing-request endpoint, and zero new isGuest refs', () {
      final src = File('lib/screens/ai_chat_screen.dart').readAsStringSync();
      // Fix 1: reads canonical mintage_display & image_url with legacy fallback
      expect(src.contains("card['mintage_display'] ?? card['mintage_label']"), isTrue);
      expect(src.contains("card['image_url'] ?? card['thumb_url']"), isTrue);
      // Fix 2: handles Map payload for missing_item_report_prompt (not == true)
      expect(src.contains("data['missing_item_report_prompt'] == true"), isFalse);
      expect(src.contains("msg['missing_item_report_prompt'] == true"), isFalse);
      expect(src.contains("rawPrompt['query']"), isTrue);
      // Fix 3: posts to authenticated catalog-missing-request endpoint
      expect(src.contains('/api/v1/collection/catalog-missing-request'), isTrue);
      // Fix 4: Wave 2 handlers use user.isAnonymous (not AuthService.isGuest)
      final addIdx = src.indexOf('_addCatalogCardToCollection(');
      expect(addIdx, greaterThan(-1));
      final addSlice = src.substring(addIdx, addIdx + 400);
      expect(addSlice.contains('AuthService.isGuest'), isFalse);
      expect(addSlice.contains('user.isAnonymous'), isTrue);
    });
  });
}
