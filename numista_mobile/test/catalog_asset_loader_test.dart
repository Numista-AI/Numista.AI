import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/services/catalog/catalog_asset_loader.dart';
import 'package:numista_ai/services/mint_product_lookup_service.dart';

class _ShardedFixtureBundle extends CachingAssetBundle {
  final List<String> requestedKeys = [];

  final Map<String, String> _assets = {
    'assets/catalog/catalog_manifest_v1.json': jsonEncode({
      'schema_version': 'catalog_sharded_v1',
      'master_sha8': '6db323ec',
      'public_row_count': 2,
      'monolith_present': false,
      'monolith_bytes': 0,
      'index': {
        'files': ['catalog_search_index_v1.json'],
        'row_count': 2,
        'bytes': 512,
        'sha256': 'deadbeef',
      },
      'chunks': [
        {
          'slug': 'seated_gold_rush_1839_1891',
          'era': 'Seated & Gold Rush (1839–1891)',
          'path': 'chunks/era_seated_gold_rush_1839_1891.json',
          'row_count': 1,
          'bytes': 256,
          'sha256': 'cafe0001',
        },
        {
          'slug': '21st_century_2000_2026_p1',
          'era': '21st century (2000–2026)',
          'path': 'chunks/era_21st_century_2000_2026_p1.json',
          'row_count': 1,
          'bytes': 256,
          'sha256': 'cafe0002',
        },
      ],
      'child_tables': {
        'varieties': {
          'path': 'children/varieties_v1.json',
          'row_count': 1,
          'bytes': 128,
          'sha256': 'cafe0003',
        },
        'nbn_charters': {
          'path': 'children/nbn_charters_v1.json',
          'row_count': 0,
          'bytes': 2,
          'sha256': 'cafe0004',
        },
        'obsolete_issuers': {
          'path': 'children/obsolete_issuers_v1.json',
          'row_count': 0,
          'bytes': 2,
          'sha256': 'cafe0005',
        },
      },
    }),
    'assets/catalog/catalog_search_index_v1.json': jsonEncode([
      {
        'nac_code': 'NAC1.CN.US.1D.MORGAN.1878.P.BASE.2',
        'nac_aliases': ['NAC1.CN.US.1D.MORGAN.1878.XX.BASE.1'],
        'search_aliases': ['8TF'],
        'name': '1878 Morgan Silver Dollar',
        'type': 'coin',
        'year': 1878,
        'denomination': 'Dollar',
        'series': 'Morgan Silver Dollar',
        'mint_facility': 'Philadelphia',
        'is_placeholder': false,
        'has_photo': true,
        'has_varieties': true,
        'variety_count': 1,
        'chunk': 'chunks/era_seated_gold_rush_1839_1891.json',
      },
      {
        'nac_code': 'NAC1.CN.US.25C.AWQ.2024.P.BASE.9',
        'name': '2024-P American Women Quarter',
        'type': 'coin',
        'year': 2024,
        'denomination': 'Quarter Dollar',
        'series': 'American Women Quarters',
        'mint_facility': 'Philadelphia',
        'mint_mark_on_coin': 'P',
        'is_placeholder': false,
        'chunk': 'chunks/era_21st_century_2000_2026_p1.json',
      },
    ]),
    'assets/catalog/chunks/era_seated_gold_rush_1839_1891.json': jsonEncode([
      {
        'nac_code': 'NAC1.CN.US.1D.MORGAN.1878.P.BASE.2',
        'name': '1878 Morgan Silver Dollar',
        'type': 'coin',
        'year': 1878,
        'denomination': 'Dollar',
        'series': 'Morgan Silver Dollar',
        'history': 'Hydrated full historical narrative from lazy chunk.',
        'weight_g': 26.73,
        'diameter_mm': 38.1,
        'mintage': {'value': 749500, 'label': '8TF'},
      },
    ]),
    'assets/catalog/chunks/era_21st_century_2000_2026_p1.json': jsonEncode([
      {
        'nac_code': 'NAC1.CN.US.25C.AWQ.2024.P.BASE.9',
        'name': '2024-P American Women Quarter',
        'type': 'coin',
        'year': 2024,
        'denomination': 'Quarter Dollar',
        'series': 'American Women Quarters',
        'history': 'Hydrated 2024 chunk.',
      },
    ]),
    'assets/catalog/children/varieties_v1.json': jsonEncode([
      {
        'variety_id': 'VAR.12345678.8_tail_feathers',
        'parent_nac1': 'NAC1.CN.US.1D.MORGAN.1878.P.BASE.2',
        'name': '8 Tail Feathers',
        'attribution': 'VAM-14',
        'reference_work': 'Van Allen & Mallis',
        'category': 'die_variety',
      },
    ]),
    'assets/catalog/mint_product_fields_v1.json': jsonEncode({
      'NAC1.CN.US.25C.AWQ.2024.P.BASE.9': {'product_price_usd': 12.50},
    }),
  };

  @override
  Future<ByteData> load(String key) async => throw FlutterError('not used');

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    requestedKeys.add(key);
    final val = _assets[key];
    if (val == null) {
      throw FlutterError('Unable to load asset: $key');
    }
    return val;
  }
}

class _LegacyOnlyFixtureBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async => throw FlutterError('not used');

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    if (key == 'assets/catalog/catalog_public_v1.json') {
      return jsonEncode([
        {
          'nac_code': 'NAC1.CN.US.1D.MORGAN.1921.P.BASE.4',
          'name': '1921 Morgan Silver Dollar',
          'type': 'coin',
          'year': 1921,
          'is_placeholder': false,
          'varieties': [
            {'name': 'Zerbe Proof', 'attribution': 'VAM-1', 'reference_work': 'VAM'},
          ],
        },
      ]);
    }
    throw FlutterError('Unable to load asset: $key');
  }
}

class _MissingAllBundle extends CachingAssetBundle {
  @override
  Future<ByteData> load(String key) async => throw FlutterError('not used');

  @override
  Future<String> loadString(String key, {bool cache = true}) async {
    throw FlutterError('Missing asset: $key');
  }
}

void main() {
  group('Chapter 0 CatalogAssetLoader (Plan 8f01c991)', () {
    test('loads sharded manifest+index without eagerly loading chunks, then hydrates single chunk and child varieties lazily', () async {
      final bundle = _ShardedFixtureBundle();
      final loader = CatalogAssetLoader();

      final index = await loader.loadIndex(bundle: bundle);
      expect(loader.isSharded, isTrue);
      expect(index.length, equals(2));
      expect(
        bundle.requestedKeys,
        equals([
          'assets/catalog/catalog_manifest_v1.json',
          'assets/catalog/catalog_search_index_v1.json',
        ]),
      );

      // Hydrate by retired alias -> fetches ONLY the seated chunk, never the 21st-century chunk
      final hydrated = await loader.loadFullEntry(
        'NAC1.CN.US.1D.MORGAN.1878.XX.BASE.1',
        bundle: bundle,
      );
      expect(hydrated, isNotNull);
      expect(hydrated!['nac_code'], equals('NAC1.CN.US.1D.MORGAN.1878.P.BASE.2'));
      expect(hydrated['history'], contains('Hydrated full historical narrative'));
      expect(
        bundle.requestedKeys.contains('assets/catalog/chunks/era_seated_gold_rush_1839_1891.json'),
        isTrue,
      );
      expect(
        bundle.requestedKeys.contains('assets/catalog/chunks/era_21st_century_2000_2026_p1.json'),
        isFalse,
      );

      // Repeat call uses chunk cache (no duplicate asset read)
      final callsBefore = bundle.requestedKeys.length;
      final hydratedAgain = await loader.loadFullEntry(
        'NAC1.CN.US.1D.MORGAN.1878.P.BASE.2',
        bundle: bundle,
      );
      expect(hydratedAgain!['weight_g'], equals(26.73));
      expect(bundle.requestedKeys.length, equals(callsBefore));

      // Lazy child varieties load from children/varieties_v1.json
      final varieties = await loader.loadVarietiesForParent(
        'NAC1.CN.US.1D.MORGAN.1878.P.BASE.2',
        bundle: bundle,
      );
      expect(varieties.length, equals(1));
      expect(varieties.first['attribution'], equals('VAM-14'));
    });

    test('falls back transparently to legacy catalog_public_v1.json when manifest is absent', () async {
      final bundle = _LegacyOnlyFixtureBundle();
      final loader = CatalogAssetLoader();

      final index = await loader.loadIndex(bundle: bundle);
      expect(loader.isSharded, isFalse);
      expect(index.length, equals(1));

      final full = await loader.loadFullEntry('NAC1.CN.US.1D.MORGAN.1921.P.BASE.4', bundle: bundle);
      expect(full, isNotNull);
      expect(full!['name'], equals('1921 Morgan Silver Dollar'));

      final varieties = await loader.loadVarietiesForParent('NAC1.CN.US.1D.MORGAN.1921.P.BASE.4', bundle: bundle);
      expect(varieties.length, equals(1));
      expect(varieties.first['name'], equals('Zerbe Proof'));
    });

    test('rethrows FlutterError when neither manifest nor monolith exists', () async {
      final loader = CatalogAssetLoader();
      expect(
        () => loader.loadIndex(bundle: _MissingAllBundle()),
        throwsA(isA<FlutterError>()),
      );
    });

    test('MintProductLookupService works seamlessly against sharded index without monolith', () async {
      final bundle = _ShardedFixtureBundle();
      final svc = MintProductLookupService.forInitTesting();
      await svc.ensureInitialized(bundle: bundle);
      expect(svc.lastInitError, isNull);

      final coin = CoinModel(
        id: 'c_awq',
        country: 'USA',
        personalRef: 'NAC1.CN.US.25C.AWQ.2024.P.BASE.9',
      );
      final meta = svc.lookupForCoin(coin);
      expect(meta, isNotNull);
      expect(meta!.productPriceUsd, equals(12.50));
      // Confirm no era chunk was loaded just for MintProductLookupService init
      expect(
        bundle.requestedKeys.any((k) => k.contains('/chunks/')),
        isFalse,
      );
    });
  });
}
