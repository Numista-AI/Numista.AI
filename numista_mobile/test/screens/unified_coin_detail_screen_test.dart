import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:cloud_firestore/cloud_firestore.dart'
    show QueryDocumentSnapshot;
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/models/mint_product_metadata.dart';
import 'package:numista_ai/screens/unified_coin_detail_deps.dart';
import 'package:numista_ai/screens/unified_coin_detail_screen.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

class CountingCoinDocStore implements CoinDocStore {
  final Map<String, Map<String, dynamic>> _seed = {};

  @override
  int readCount = 0;

  @override
  int writeCount = 0;

  void seedDoc(String collection, String id, Map<String, dynamic> data) {
    _seed['$collection/$id'] = Map<String, dynamic>.from(data);
  }

  void resetCounts() {
    readCount = 0;
    writeCount = 0;
  }

  @override
  Future<Map<String, dynamic>?> getDoc(String collection, String id) async {
    readCount++;
    return _seed['$collection/$id'];
  }

  @override
  Future<void> setDoc(
    String collection,
    String id,
    Map<String, dynamic> data,
  ) async {
    writeCount++;
    _seed['$collection/$id'] = Map<String, dynamic>.from(data);
  }
}

class ManualClock implements DetailClock {
  DateTime _now = DateTime.utc(2026, 11, 13, 12, 0, 0);

  @override
  DateTime get now => _now;

  void advance(Duration d) {
    _now = _now.add(d);
  }
}

class TestDeps {
  final CountingCoinDocStore store = CountingCoinDocStore();
  final ManualClock clock = ManualClock();
  LawsFetcher? lawsFetcher;
  String? lastLaunchedUrl;
  final List<String> loadedImageUrls = [];

  UnifiedCoinDetailDeps toDeps() => UnifiedCoinDetailDeps(
        store: store,
        clock: clock,
        lawsFetcher: lawsFetcher,
        onLaunchUrl: (url) => lastLaunchedUrl = url,
        onImageLoad: (url) => loadedImageUrls.add(url),
      );
}

class _FakeRow {
  final String id;
  final bool isVirtualChild;
  final String? parentDocId;

  const _FakeRow({
    required this.id,
    this.isVirtualChild = false,
    this.parentDocId,
  });
}

// ignore: subtype_of_sealed_class
class _FakeQueryDocumentSnapshot
    implements QueryDocumentSnapshot<Map<String, dynamic>> {
  @override
  final String id;
  final Map<String, dynamic> _data;

  _FakeQueryDocumentSnapshot(this.id, this._data);

  @override
  Map<String, dynamic> data() => _data;

  @override
  bool get exists => true;

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _MapAssetBundle extends AssetBundle {
  final Map<String, String> _assets;
  _MapAssetBundle(this._assets);

  @override
  Future<ByteData> load(String key) async {
    final value = _assets[key];
    if (value == null) throw StateError('Missing asset: $key');
    final bytes = Uint8List.fromList(utf8.encode(value));
    return ByteData.sublistView(bytes);
  }

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    final value = _assets[key];
    if (value == null) throw StateError('Missing asset: $key');
    return value;
  }
}

void main() {
  late TestDeps t;
  late UnifiedCoinDetailDeps harness;

  setUp(() {
    t = TestDeps();
    harness = t.toDeps();
    UnifiedDetailsGate.debugBundle = null;
    UnifiedDetailsGate.debugReset();
  });

  testWidgets('Test 1: Virtual-child parent resolution and Next navigation',
      (tester) async {
    final rows = [
      const _FakeRow(id: 'parent_1'),
      const _FakeRow(
          id: 'child_1', isVirtualChild: true, parentDocId: 'parent_1'),
      const _FakeRow(id: 'parent_2'),
    ];
    final cachedDocs = [
      _FakeQueryDocumentSnapshot('parent_1', {
        'themeSubject': '2024 Proof Set',
        'metalContent': 'Clad',
      }),
      _FakeQueryDocumentSnapshot('parent_2', {
        'themeSubject': '1921 Morgan Dollar',
        'metalContent': '90% Silver',
      }),
    ];
    final initialCoin = CoinModel(
      id: 'parent_1',
      themeSubject: '2024 Proof Set',
      metalContent: 'Clad',
    );
    final initialParentIndex = resolveParentIndex(rows, 'parent_1');
    expect(initialParentIndex, 0);

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: initialCoin,
          initialParentIndex: initialParentIndex,
          collectionRows: rows,
          cachedCoinsDocs: cachedDocs,
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('2024 Proof Set'), findsOneWidget);
    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();

    expect(find.text('1921 Morgan Dollar'), findsOneWidget);
    final navState = tester.state(find.byType(UnifiedCoinDetailScreen))
        as UnifiedCoinDetailNavState;
    expect(navState.currentParentIndex, 2);
  });

  testWidgets('Test 2: Owned storage URLs vs unowned hosts', (tester) async {
    expect(
      isOwnedStorageUrl(
          'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fcoin.jpg?alt=media'),
      isTrue,
    );
    expect(
      isOwnedStorageUrl(
          'https://storage.googleapis.com/numista-reference-library/morgan.jpg'),
      isTrue,
    );
    expect(isOwnedStorageUrl('https://evil.example.com/coin.jpg'), isFalse);
    expect(isOwnedStorageUrl('http://storage.googleapis.com/us_mint_coin_images/a.jpg'), isFalse);
  });

  testWidgets('Test 3: Header contrast meets WCAG AAA (>= 7:1)', (tester) async {
    final coin = CoinModel(id: 'c1', themeSubject: 'Contrast Coin');
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    final container =
        tester.widget<Container>(find.byKey(const Key('udv_header_surface')));
    final bg = (container.decoration as BoxDecoration).color!;
    final title =
        tester.widget<Text>(find.byKey(const Key('udv_header_title')));
    final fg = title.style!.color!;
    final l1 = bg.computeLuminance();
    final l2 = fg.computeLuminance();
    final ratio = (l1 > l2 ? (l1 + 0.05) / (l2 + 0.05) : (l2 + 0.05) / (l1 + 0.05));
    expect(ratio, greaterThanOrEqualTo(7.0));
  });

  testWidgets('Test 4: Image load hook records hero URL', (tester) async {
    const userPhoto =
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fu1%2Fobv.jpg?alt=media';
    final coin = CoinModel(
      id: 'c_img',
      themeSubject: 'Photo Coin',
      imageUrlObverse: userPhoto,
    );
    final customHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      lawsFetcher: t.lawsFetcher,
      onLaunchUrl: (url) => t.lastLaunchedUrl = url,
      onImageLoad: (url) => t.loadedImageUrls.add(url),
      resolvePhotoUrl: (url) async => url,
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: customHarness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(t.loadedImageUrls, contains(userPhoto));
  });

  testWidgets('Test 5: Purchase cost masked by default and shown in \$XX.XX',
      (tester) async {
    final coin = CoinModel(
      id: 'c_val',
      themeSubject: 'Valued Coin',
      cpgRetail: 120.0,
      purchaseCost: '50.00',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text(r'$50.00'), findsNothing);
    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text(r'$50.00'), findsOneWidget);
    expect(find.text(r'$120.00'), findsOneWidget);
  });

  test('Test 6: Strict Congress.gov URL validator', () {
    expect(
      isValidCongressGovUrl(
          'https://www.congress.gov/bill/110th-congress/house-bill/6184'),
      isTrue,
    );
    expect(
      isValidCongressGovUrl(
          'https://user:pass@www.congress.gov/bill/110th-congress/house-bill/6184'),
      isFalse,
    );
    expect(
      isValidCongressGovUrl(
          'https://evil.com/bill/110th-congress/house-bill/6184'),
      isFalse,
    );
    expect(
      isValidCongressGovUrl(
          'http://www.congress.gov/bill/110th-congress/house-bill/6184'),
      isFalse,
    );
  });

  testWidgets('Test 7: Outbound Congress URL launch records clean URL',
      (tester) async {
    const validUrl =
        'https://www.congress.gov/bill/110th-congress/house-bill/6184';
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: Builder(
          builder: (ctx) => TextButton(
            onPressed: () =>
                launchOutboundCongressUrl(ctx, validUrl, harness: harness),
            child: const Text('Open Congress'),
          ),
        ),
      ),
    ));
    await tester.tap(find.text('Open Congress'));
    await tester.pumpAndSettle();
    expect(t.lastLaunchedUrl, equals(validUrl));
  });

  testWidgets('Test 8: Legislation resolves from offline manifest',
      (tester) async {
    final coin = CoinModel(
      id: 'atb_1',
      themeSubject: 'Yellowstone Quarter',
      programSeries: 'America the Beautiful Quarters',
      denomination: 'Quarter',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Legislation'));
    await tester.pumpAndSettle();

    expect(
      find.text(
          'America’s Beautiful National Parks Quarter Dollar Coin Act of 2008'),
      findsOneWidget,
    );
    expect(find.text('122 Stat. 5038 (31 U.S.C. § 5112(t))'), findsOneWidget);
  });

  testWidgets('Test 9: Markdown sanitizer strips HTML/images/links, keeps bold',
      (tester) async {
    final cleaned = sanitizeNotesText(
        '**Bold Note** <script>alert(1)</script> ![img](https://evil.com/x.png) [link](https://evil.com)');
    expect(cleaned, equals('**Bold Note**   link'));

    final coin = CoinModel(
      id: 'c_md',
      themeSubject: 'Markdown Coin',
      personalNotes: '**Cleaned Bold** <img src=x>',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Cleaned Bold'), findsOneWidget);
  });

  testWidgets('Test 10: Missing composition renders Not Recorded + hero placeholder',
      (tester) async {
    final proj = PublicCoinProjection.fromCatalogMap({
      'nac_code': 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
      'title': '1921 Morgan Dollar',
      'denomination': 'Dollar',
    });
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen.public(projection: proj, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Not Recorded'), findsAtLeastNWidgets(1));
    expect(find.byKey(const Key('hero_coin_placeholder')), findsOneWidget);
  });

  testWidgets('Test 11: Read-only contract (0 writes, cached read)',
      (tester) async {
    t.store.seedDoc('coins', 'c_ro', {
      'themeSubject': 'Read Only Coin',
      'metalContent': 'Copper',
    });
    t.store.resetCounts();

    final coin = CoinModel(id: 'c_ro', themeSubject: 'Initial');
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(t.store.readCount, equals(1));
    expect(t.store.writeCount, equals(0));
    expect(find.text('Read Only Coin'), findsOneWidget);
  });

  testWidgets(
      'Test 12: Photo priority (user photo > reference image) and guest redactions on same fixture',
      (tester) async {
    const userPhoto =
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fuser1%2Fphoto.jpg?alt=media';
    const refPhoto =
        'https://storage.googleapis.com/numista-reference-library/morgan.jpg';

    final ownerCoin = CoinModel(
      id: 'fixture_1',
      personalRef: 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
      themeSubject: '1921 Morgan Dollar',
      imageUrlObverse: userPhoto,
      purchaseCost: '45.00',
      storageLocation: 'Safe Box 3',
      personalNotes: 'Private note: bought at ANA convention',
    );

    final ownerHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      lawsFetcher: t.lawsFetcher,
      onLaunchUrl: (url) => t.lastLaunchedUrl = url,
      onImageLoad: (url) => t.loadedImageUrls.add(url),
      resolvePhotoUrl: (url) async => url,
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: ownerCoin, deps: ownerHarness),
      ),
    ));
    await tester.pumpAndSettle();

    final heroImage =
        tester.widget<Image>(find.byKey(const Key('hero_coin_image')));
    expect((heroImage.image as NetworkImage).url, equals(userPhoto));
    expect(find.text('Safe Box 3'), findsOneWidget);
    expect(find.text('Private note: bought at ANA convention'), findsOneWidget);
    expect(find.text(r'$45.00'), findsNothing);
    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text(r'$45.00'), findsOneWidget);

    final guestProjection = PublicCoinProjection.fromCoinModel(ownerCoin,
        referenceImageUrl: refPhoto);
    final synthetic = guestProjection.toSyntheticCoinModel();
    expect(synthetic.storageLocation, isNot(equals(ownerCoin.storageLocation)));
    expect(synthetic.personalNotes, isNot(equals(ownerCoin.personalNotes)));
    expect(synthetic.purchaseCost, isNot(equals(ownerCoin.purchaseCost)));
    expect(synthetic.imageUrlObverse, isNot(equals(userPhoto)));
    expect(guestProjection.primaryImageUrl, equals(refPhoto));

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen.public(
            projection: guestProjection, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    final guestHeroImage =
        tester.widget<Image>(find.byKey(const Key('hero_coin_image')));
    expect((guestHeroImage.image as NetworkImage).url, equals(refPhoto));
    expect(find.text('Safe Box 3'), findsNothing);
    expect(find.text('Private note: bought at ANA convention'), findsNothing);
    expect(find.text(r'$45.00'), findsNothing);
    expect(find.byKey(const Key('ebay_search_button')), findsNothing);
  });

  testWidgets(
      'Test 13: Laws fetch > 4.0s on harness.clock shows pending-verification fallback',
      (tester) async {
    final coin = CoinModel(
      id: 'unlisted_comm',
      themeSubject: 'Unlisted Test Commemorative',
      programSeries: 'Test Series Not In Manifest',
      denomination: 'Dollar',
    );
    final never = Completer<Map<String, dynamic>?>();
    t.lawsFetcher = (_) => never.future;
    harness = t.toDeps();

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    await tester.tap(find.text('Legislation'));
    await tester.pump();

    t.clock.advance(const Duration(seconds: 5));
    await tester.pump(const Duration(milliseconds: 300));
    await tester.pump();

    expect(find.text('Founding legislation details pending verification.'),
        findsOneWidget);
    await tester.pumpAndSettle();
  });

  testWidgets(
      'Test 14: Two consecutive Next steps across virtual-child group maintains correct parent index',
      (tester) async {
    final rows = [
      const _FakeRow(id: 'p1'),
      const _FakeRow(id: 'c1', isVirtualChild: true, parentDocId: 'p1'),
      const _FakeRow(id: 'c2', isVirtualChild: true, parentDocId: 'p1'),
      const _FakeRow(id: 'p2'),
      const _FakeRow(id: 'p3'),
    ];
    final cachedDocs = [
      _FakeQueryDocumentSnapshot('p1', {'themeSubject': 'Parent 1'}),
      _FakeQueryDocumentSnapshot('p2', {'themeSubject': 'Parent 2'}),
      _FakeQueryDocumentSnapshot('p3', {'themeSubject': 'Parent 3'}),
    ];
    final startCoin = CoinModel(id: 'p1', themeSubject: 'Parent 1');

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          coin: startCoin,
          initialParentIndex: resolveParentIndex(rows, 'p1'),
          collectionRows: rows,
          cachedCoinsDocs: cachedDocs,
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    final navState = tester.state(find.byType(UnifiedCoinDetailScreen))
        as UnifiedCoinDetailNavState;
    expect(navState.currentParentIndex, 0);

    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();
    expect(navState.currentParentIndex, 3);
    expect(find.text('Parent 2'), findsOneWidget);

    await tester.tap(find.byIcon(Icons.arrow_forward_ios));
    await tester.pumpAndSettle();
    expect(navState.currentParentIndex, 4);
    expect(find.text('Parent 3'), findsOneWidget);
  });

  test(
      'Test 15: PublicCoinProjection.fromCatalogMap handles Met primary_image and null primary_image',
      () {
    final libam = PublicCoinProjection.fromCatalogMap({
      'nac_code': 'NAC1.MD.US.PRV.LIBAM.1782.XX.BASE.S',
      'title': '1782 Libertas Americana Medal',
      'denomination': 'Medal',
      'primary_image': {
        'url':
            'https://images.metmuseum.org/CRDImages/ad/web-large/DP165213.jpg',
        'license': 'CC0 1.0',
        'source_url': 'https://www.metmuseum.org/art/collection/search/1234',
      },
    });
    expect(
      libam.primaryImageUrl,
      equals(
          'https://images.metmuseum.org/CRDImages/ad/web-large/DP165213.jpg'),
    );

    final morgan = PublicCoinProjection.fromCatalogMap({
      'nac_code': 'NAC1.CN.US.1D.MORGANSILV.1921.P.BASE.3',
      'title': '1921 Morgan Dollar',
      'denomination': 'Dollar',
      'primary_image': null,
    });
    expect(morgan.primaryImageUrl, isNull);
  });

  test('Test 16: UnifiedDetailsGate fails closed when false or missing',
      () async {
    UnifiedDetailsGate.debugBundle = _MapAssetBundle({
      'assets/config/features.json': '{"unified_details_view_v1": false}',
    });
    UnifiedDetailsGate.debugReset();
    expect(await UnifiedDetailsGate.isEnabled(), isFalse);

    UnifiedDetailsGate.debugBundle = _MapAssetBundle({});
    UnifiedDetailsGate.debugReset();
    expect(await UnifiedDetailsGate.isEnabled(), isFalse);

    UnifiedDetailsGate.debugBundle = _MapAssetBundle({
      'assets/config/features.json': '{"unified_details_view_v1": true}',
    });
    UnifiedDetailsGate.debugReset();
    expect(await UnifiedDetailsGate.isEnabled(), isTrue);
  });

  testWidgets('Test 17: Previous arrow and Close button work in header',
      (tester) async {
    final rows = [
      const _FakeRow(id: 'p1'),
      const _FakeRow(id: 'p2'),
    ];
    final cachedDocs = [
      _FakeQueryDocumentSnapshot('p1', {'themeSubject': 'First Coin'}),
      _FakeQueryDocumentSnapshot('p2', {'themeSubject': 'Second Coin'}),
    ];
    final startCoin = CoinModel(id: 'p2', themeSubject: 'Second Coin');

    await tester.pumpWidget(MaterialApp(
      home: Navigator(
        onGenerateRoute: (_) => MaterialPageRoute(
          builder: (ctx) => Scaffold(
            body: Center(
              child: ElevatedButton(
                onPressed: () => showDialog(
                  context: ctx,
                  builder: (_) => Dialog(
                    child: UnifiedCoinDetailScreen(
                      coin: startCoin,
                      initialParentIndex: resolveParentIndex(rows, 'p2'),
                      collectionRows: rows,
                      cachedCoinsDocs: cachedDocs,
                      deps: harness,
                    ),
                  ),
                ),
                child: const Text('Open'),
              ),
            ),
          ),
        ),
      ),
    ));

    await tester.tap(find.text('Open'));
    await tester.pumpAndSettle();

    expect(find.text('Second Coin'), findsOneWidget);
    expect(find.byKey(const Key('udv_prev_button')), findsOneWidget);
    expect(find.byKey(const Key('udv_close_button')), findsOneWidget);

    await tester.tap(find.byKey(const Key('udv_prev_button')));
    await tester.pumpAndSettle();
    expect(find.text('First Coin'), findsOneWidget);

    await tester.tap(find.byKey(const Key('udv_close_button')));
    await tester.pumpAndSettle();
    expect(find.byType(UnifiedCoinDetailScreen), findsNothing);
  });

  testWidgets(
      'Test 18: Tapping Show values does not re-fetch signed hero URL',
      (tester) async {
    int resolveCalls = 0;
    const gsUri = 'gs://numista-uploads-studio-9101802118-8c9a8/users/u1/hero.jpg';
    final customHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      lawsFetcher: (_) async => null,
      onLaunchUrl: (url) => t.lastLaunchedUrl = url,
      resolvePhotoUrl: (_) async {
        resolveCalls++;
        return 'https://storage.googleapis.com/signed-hero.jpg';
      },
    );

    final coin = CoinModel(
      id: 'c_cached_hero',
      themeSubject: 'Cached Hero',
      imageUrlObverse: gsUri,
      cpgRetail: 42.0,
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: customHarness),
      ),
    ));
    await tester.pumpAndSettle();
    final callsBeforeTap = resolveCalls;
    expect(callsBeforeTap, greaterThanOrEqualTo(1));

    await tester.tap(find.text('Show values'));
    await tester.pumpAndSettle();
    expect(find.text(r'$42.00'), findsOneWidget);
    expect(resolveCalls, equals(callsBeforeTap));
  });

  testWidgets(
      'Test 19: Obverse/Reverse toggle switches hero image when reverse exists',
      (tester) async {
    final requested = <String>[];
    const obvUri = 'gs://numista-uploads-studio-9101802118-8c9a8/users/u1/obv.jpg';
    const revUri = 'gs://numista-uploads-studio-9101802118-8c9a8/users/u1/rev.jpg';
    final customHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      lawsFetcher: (_) async => null,
      onLaunchUrl: (url) => t.lastLaunchedUrl = url,
      resolvePhotoUrl: (raw) async {
        requested.add(raw);
        return 'https://storage.googleapis.com/${raw.split('/').last}';
      },
    );

    final coin = CoinModel(
      id: 'c_rev_toggle',
      themeSubject: 'Two-Sided Coin',
      imageUrlObverse: obvUri,
      imageUrlReverse: revUri,
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: customHarness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(requested.toSet(), equals({obvUri}));
    expect(find.byKey(const Key('udv_toggle_side_button')), findsOneWidget);
    expect(find.text('Show Reverse'), findsOneWidget);

    await tester.tap(find.byKey(const Key('udv_toggle_side_button')));
    await tester.pumpAndSettle();

    expect(requested.toSet(), equals({obvUri, revUri}));
    expect(find.text('Show Obverse'), findsOneWidget);
  });

  testWidgets(
      'Test 20: private /users/ URL fails closed to placeholder when resolvePhotoUrl is null',
      (tester) async {
    const userPhoto =
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fuser1%2Fphoto.jpg?alt=media';
    final ownerCoin = CoinModel(
      id: 'c_fail_closed',
      themeSubject: 'Private Coin',
      imageUrlObverse: userPhoto,
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: ownerCoin, deps: harness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('hero_coin_placeholder')), findsOneWidget);
    expect(find.byKey(const Key('hero_coin_image')), findsNothing);
  });

  testWidgets(
      'Test 21: SignedStorageImage resolves private URL and records resolved URL once',
      (tester) async {
    const userPhoto =
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fuser1%2Fphoto.jpg?alt=media';
    const signedUrl = 'https://signed.example.com/user1/photo.jpg?token=v1';
    final loadedUrls = <String>[];
    final ownerCoin = CoinModel(
      id: 'c_signed',
      themeSubject: 'Signed Coin',
      imageUrlObverse: userPhoto,
    );
    final customHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      resolvePhotoUrl: (_) async => signedUrl,
      onImageLoad: loadedUrls.add,
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: ownerCoin, deps: customHarness),
      ),
    ));
    await tester.pump();
    await tester.pump();

    expect(find.byKey(const Key('hero_coin_image')), findsOneWidget);
    expect(loadedUrls, equals([signedUrl]));
  });

  testWidgets(
      'Test 22: two-field Mint rendering shows No Mint Mark for Philadelphia blank mark and W for West Point',
      (tester) async {
    final phillyCoin = CoinModel(
      id: 'c_philly',
      themeSubject: '2026 Lincoln Cent',
      year: '2026',
      mint: 'Philadelphia',
      mintMark: '',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          key: const ValueKey('philly'),
          coin: phillyCoin,
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Mint Facility: Philadelphia'), findsOneWidget);
    expect(find.text('Mint Mark: No Mint Mark'), findsOneWidget);

    final wpCoin = CoinModel(
      id: 'c_wp',
      themeSubject: '2026 Proof Silver Eagle',
      year: '2026',
      mint: 'West Point',
      mintMark: 'W',
    );
    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(
          key: const ValueKey('wp'),
          coin: wpCoin,
          deps: harness,
        ),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Mint Facility: West Point'), findsOneWidget);
    expect(find.text('Mint Mark: W'), findsOneWidget);
  });

  testWidgets(
      'Test 23: NET-810 MintProductMetadata fields render when lookup returns a match',
      (tester) async {
    final coin = CoinModel(
      id: 'c_net810',
      personalRef: 'NAC1.CN.US.1D.ASE.2026.W.PRF.1',
      themeSubject: '2026-W Proof Silver Eagle',
      year: '2026',
      mint: 'West Point',
      mintMark: 'W',
      denomination: '1 Dollar',
      country: 'USA',
    );
    final customHarness = UnifiedCoinDetailDeps(
      store: t.store,
      clock: t.clock,
      lookupMintProduct: (_) => const MintProductMetadata(
        productPriceUsd: 95.0,
        mintScheduleStatus: 'ON_SALE',
        productAvailability: 'In Stock',
        releaseDate: '2026-03-19',
      ),
    );

    await tester.pumpWidget(MaterialApp(
      home: Scaffold(
        body: UnifiedCoinDetailScreen(coin: coin, deps: customHarness),
      ),
    ));
    await tester.pumpAndSettle();

    expect(find.text('Mint Status: Available from U.S. Mint'), findsOneWidget);
    expect(find.text(r'Mint Issue Price: $95.00'), findsOneWidget);
    expect(find.text('Availability: In Stock'), findsOneWidget);
    expect(find.text('Release Date: 2026-03-19'), findsOneWidget);
  });
}
