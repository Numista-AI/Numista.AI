import 'dart:io';

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

class _FakeFeatureBundle extends CachingAssetBundle {
  final String json;
  _FakeFeatureBundle(this.json);

  @override
  Future<ByteData> load(String key) async {
    final bytes = Uint8List.fromList(json.codeUnits);
    return ByteData.sublistView(bytes);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async => json;
}

class _ThrowingPositionScrollController extends ScrollController {
  @override
  bool get hasClients => true;

  @override
  ScrollPosition get position =>
      throw AssertionError('TableView 2D scroll position');
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  setupFirebaseCoreMocks();

  setUpAll(() async {
    await Firebase.initializeApp();
  });

  final myCollectionSource =
      File('lib/screens/my_collection_screen.dart').readAsStringSync();

  group('FF1-A: My Collection opens 7-tab CoinDetailScreen', () {
    test('A1: kCoinDetailTabLabels has the exact 7 approved tabs', () {
      expect(kCoinDetailTabLabels, const [
        'Details',
        'Financials',
        'Provenance',
        'AI Insights',
        'History',
        'Legislation',
        'Known Errors',
      ]);
    });

    testWidgets('A1/A2: CoinDetailScreen renders TabBar matching kCoinDetailTabLabels',
        (tester) async {
      final coin = CoinModel.fromMap({
        'Year': '2026',
        'Mint Mark': 'W',
        'Series': 'Morgan Dollar',
        'Denomination': '1 Dollar',
        'Condition': 'Enhanced Uncirculated',
      }, 'test_2026_morgan');

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: CoinDetailScreen(
              coin: coin,
              spotPrices: const {},
            ),
          ),
        ),
      );
      await tester.pump();

      final tabBar = tester.widget<TabBar>(find.byType(TabBar));
      final labels = tabBar.tabs
          .whereType<Tab>()
          .map((t) => t.text)
          .toList();
      expect(labels, equals(kCoinDetailTabLabels));
    });

    test('A2/A3: UnifiedCoinDetailScreen is removed from MyCollectionScreen regardless of UnifiedDetailsGate',
        () async {
      UnifiedDetailsGate.debugReset();
      UnifiedDetailsGate.debugBundle =
          _FakeFeatureBundle('{"unified_details_view_v1": true}');
      expect(await UnifiedDetailsGate.isEnabled(), isTrue);

      UnifiedDetailsGate.debugReset();
      UnifiedDetailsGate.debugBundle =
          _FakeFeatureBundle('{"unified_details_view_v1": false}');
      expect(await UnifiedDetailsGate.isEnabled(), isFalse);
      UnifiedDetailsGate.debugBundle = null;
      UnifiedDetailsGate.debugReset();

      expect(myCollectionSource.contains('UnifiedCoinDetailScreen'), isFalse);
      expect(myCollectionSource.contains('unified_coin_detail_screen.dart'), isFalse);
      expect(myCollectionSource.contains('CoinDetailScreen.show('), isTrue);
      expect(myCollectionSource.contains('_openCoinDetailForRow('), isTrue);
    });

    test('A4: _showCoinInspectorDialog( is referenced only from Photos & eBay', () {
      final lines = myCollectionSource.split('\n');
      final callSites = <int>[];
      for (var i = 0; i < lines.length; i++) {
        final line = lines[i];
        if (line.contains('_showCoinInspectorDialog(') &&
            !line.contains('void _showCoinInspectorDialog(')) {
          callSites.add(i);
          final windowStart = (i - 2).clamp(0, lines.length - 1);
          final windowEnd = (i + 3).clamp(0, lines.length - 1);
          final window = lines.sublist(windowStart, windowEnd + 1).join('\n');
          expect(
            window.contains('Photos & eBay'),
            isTrue,
            reason:
                'Line ${i + 1} calls _showCoinInspectorDialog( without Photos & eBay',
          );
        }
      }
      expect(callSites.length, greaterThanOrEqualTo(2));
    });

    test('A5: virtual child tap points resolve to parentDoc and open _openCoinDetailForRow', () {
      // Verify table onTap, card onTap, and parent_set_id chip all use _openCoinDetailForRow
      final openCalls = RegExp(r'_openCoinDetailForRow\(')
          .allMatches(myCollectionSource)
          .length;
      // 1 definition + at least 5 call sites (table virtual/real, card virtual/real, parent chip)
      expect(openCalls, greaterThanOrEqualTo(6));
      expect(
        myCollectionSource.contains('if (parentDoc == null) return;'),
        isTrue,
      );
    });
  });

  group('A6: beta3 B3 safeHorizontalMetrics table-scroll crash guard', () {
    test('returns null when ScrollController has no clients', () {
      final ctrl = ScrollController();
      addTearDown(ctrl.dispose);
      expect(safeHorizontalMetrics(ctrl), isNull);
    });

    test('returns null without throwing when position throws (2D scroll position)', () {
      final ctrl = _ThrowingPositionScrollController();
      addTearDown(ctrl.dispose);
      expect(safeHorizontalMetrics(ctrl), isNull);
    });

    testWidgets('returns valid metrics when attached to a 1D horizontal ScrollView',
        (tester) async {
      final ctrl = ScrollController(initialScrollOffset: 25);
      addTearDown(ctrl.dispose);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 200,
              height: 100,
              child: SingleChildScrollView(
                controller: ctrl,
                scrollDirection: Axis.horizontal,
                child: const SizedBox(width: 600, height: 100),
              ),
            ),
          ),
        ),
      );
      await tester.pump();

      final metrics = safeHorizontalMetrics(ctrl);
      expect(metrics, isNotNull);
      expect(metrics!.maxExtent, equals(400.0));
      expect(metrics.viewport, equals(200.0));
      expect(metrics.offset, equals(25.0));
    });
  });
}
