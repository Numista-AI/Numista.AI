import 'package:cloud_firestore/cloud_firestore.dart' show QueryDocumentSnapshot;

import '../models/coin_model.dart';
import '../models/mint_product_metadata.dart';
import '../services/mint_product_lookup_service.dart';
import '../services/signed_photo_url_service.dart';

abstract class CoinDocStore {
  int get writeCount;
  int get readCount;
  Future<Map<String, dynamic>?> getDoc(String collection, String id);
  Future<void> setDoc(String collection, String id, Map<String, dynamic> data);
}

abstract class DetailClock {
  DateTime get now;
}

typedef LawsFetcher = Future<Map<String, dynamic>?> Function(String legislationKey);
typedef UrlLauncherHook = void Function(String url);
typedef ImageLoadRecorder = void Function(String url);
typedef PhotoUrlResolver = Future<String?> Function(String url);
typedef MintCatalogInitializer = Future<void> Function();
typedef MintProductLookup = MintProductMetadata? Function(CoinModel coin);

class UnifiedCoinDetailDeps {
  final CoinDocStore store;
  final DetailClock clock;
  final LawsFetcher? lawsFetcher; // null -> no online fallback
  final UrlLauncherHook? onLaunchUrl; // injected in tests, null in production
  final ImageLoadRecorder? onImageLoad; // injected in tests, null in production
  final PhotoUrlResolver? resolvePhotoUrl;
  final MintCatalogInitializer? ensureMintCatalogInitialized;
  final MintProductLookup? lookupMintProduct;

  const UnifiedCoinDetailDeps({
    required this.store,
    required this.clock,
    this.lawsFetcher,
    this.onLaunchUrl,
    this.onImageLoad,
    this.resolvePhotoUrl,
    this.ensureMintCatalogInitialized,
    this.lookupMintProduct,
  });

  factory UnifiedCoinDetailDeps.production(
    List<QueryDocumentSnapshot<Map<String, dynamic>>> cached,
  ) =>
      UnifiedCoinDetailDeps(
        store: CachedCoinDocStore(cached),
        clock: const SystemDetailClock(),
        resolvePhotoUrl: SignedPhotoUrlService.resolve,
        ensureMintCatalogInitialized:
            MintProductLookupService.instance.ensureInitialized,
        lookupMintProduct: MintProductLookupService.instance.lookupForCoin,
      );
}

/// Production store: in-memory over cachedCoinsDocs. 0 Firestore reads, 0 writes.
class CachedCoinDocStore implements CoinDocStore {
  final List<QueryDocumentSnapshot<Map<String, dynamic>>> _docs;
  CachedCoinDocStore(this._docs);

  @override
  int get writeCount => 0;

  @override
  int readCount = 0;

  @override
  Future<Map<String, dynamic>?> getDoc(String collection, String id) async {
    readCount++;
    for (final d in _docs) {
      if (d.id == id) return d.data();
    }
    return null;
  }

  @override
  Future<void> setDoc(String collection, String id, Map<String, dynamic> data) async {}
}

class SystemDetailClock implements DetailClock {
  const SystemDetailClock();

  @override
  DateTime get now => DateTime.now();
}
