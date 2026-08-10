import 'package:cloud_firestore/cloud_firestore.dart';

/// Result object returned by [CurrencyImageService] containing image URL,
/// attribution metadata, and fallback flags/badges.
class BanknoteImageResult {
  final String publicUrl;
  final String? attribution;
  final String? license;
  final bool isReferenceFallback;
  final String badgeText;

  BanknoteImageResult({
    required this.publicUrl,
    this.attribution,
    this.license,
    this.isReferenceFallback = true,
    required this.badgeText,
  });

  factory BanknoteImageResult.fromDoc(DocumentSnapshot doc, {required String badgeText}) {
    final data = doc.data() as Map<String, dynamic>? ?? {};
    return BanknoteImageResult(
      publicUrl: data['public_url'] ?? '',
      attribution: data['attribution'],
      license: data['license'],
      isReferenceFallback: data['is_reference_fallback'] ?? true,
      badgeText: badgeText,
    );
  }
}

/// Service for looking up banknote reference images from Firestore `currency_image_index`.
///
/// Uses direct $O(1)$ point-reads on document paths (`currency_image_index/{catalog_key}`)
/// and implements a 3-stage fallback lookup cascade:
///   1. Stage 1: Exact Match (e.g. fr_1613_n_star_obv) -> "CATALOG REFERENCE (EXACT)"
///   2. Stage 2: Base Star Match (e.g. fr_1613_star_obv) -> "CATALOG REFERENCE (CLOSEST STAR MATCH)"
///   3. Stage 3: Generic Type Match (e.g. fr_1613_norm_obv) -> "CATALOG REFERENCE (CLOSEST TYPE MATCH)"
class CurrencyImageService {
  static const String _collection = 'currency_image_index';
  final FirebaseFirestore _firestore;

  CurrencyImageService({FirebaseFirestore? firestore})
      : _firestore = firestore ?? FirebaseFirestore.instance;

  /// Looks up a reference image for a banknote using the 3-stage fallback cascade.
  Future<BanknoteImageResult?> getReferenceImage(String catalogKey, String side) async {
    final sideSuffix = side.toLowerCase().startsWith('rev') ? 'rev' : 'obv';
    final normalizedKey = catalogKey.toLowerCase();

    // Stage 1: Exact Match O(1) Point-Read
    try {
      final doc1 = await _firestore.collection(_collection).doc(normalizedKey).get();
      if (doc1.exists && doc1.data() != null) {
        return BanknoteImageResult.fromDoc(doc1, badgeText: 'CATALOG REFERENCE (EXACT)');
      }
    } catch (_) {}

    // Stage 2: Base Star Match
    final starKey = _deriveStarKey(normalizedKey, sideSuffix);
    if (starKey != null && starKey != normalizedKey) {
      try {
        final doc2 = await _firestore.collection(_collection).doc(starKey).get();
        if (doc2.exists && doc2.data() != null) {
          return BanknoteImageResult.fromDoc(doc2, badgeText: 'CATALOG REFERENCE (CLOSEST STAR MATCH)');
        }
      } catch (_) {}
    }

    // Stage 3: Generic Type Match
    final genericKey = _deriveGenericKey(normalizedKey, sideSuffix);
    if (genericKey != null && genericKey != normalizedKey && genericKey != starKey) {
      try {
        final doc3 = await _firestore.collection(_collection).doc(genericKey).get();
        if (doc3.exists && doc3.data() != null) {
          return BanknoteImageResult.fromDoc(doc3, badgeText: 'CATALOG REFERENCE (CLOSEST TYPE MATCH)');
        }
      } catch (_) {}
    }

    return null;
  }

  String? _deriveStarKey(String key, String sideSuffix) {
    if (key.contains('_star_')) {
      final m = RegExp(r'^fr_([0-9]+)_[a-z]+_star_(obv|rev)$').firstMatch(key);
      if (m != null) {
        return 'fr_${m.group(1)}_star_${m.group(2)}';
      }
    }
    return null;
  }

  String? _deriveGenericKey(String key, String sideSuffix) {
    final m = RegExp(r'^(fr_[0-9]+|csa_t[0-9]+|frac_fr[0-9]+)').firstMatch(key);
    if (m != null) {
      final prefix = m.group(1);
      return '${prefix}_norm_$sideSuffix';
    }
    return null;
  }
}
