import 'package:cloud_firestore/cloud_firestore.dart';

/// A single image entry from the `reference_library` Firestore collection.
class ReferenceImage {
  final String gcsUrl;
  final String gcsBucket;
  final String? year;
  final String? denomination;
  final String? side;
  final String source;
  final String attribution;
  final String license;
  final String? licenseUrl;
  final int? yearInt;

  const ReferenceImage({
    required this.gcsUrl,
    required this.gcsBucket,
    required this.source,
    required this.attribution,
    required this.license,
    this.year,
    this.denomination,
    this.side,
    this.licenseUrl,
    this.yearInt,
  });

  factory ReferenceImage.fromDoc(DocumentSnapshot doc) {
    final m = doc.data() as Map<String, dynamic>;
    final yearStr = m['year']?.toString() ?? '';
    return ReferenceImage(
      gcsUrl:      m['gcs_url']?.toString()      ?? '',
      gcsBucket:   m['gcs_path']?.toString()     ?? '',
      year:        yearStr,
      denomination: m['denomination']?.toString(),
      side:        m['side']?.toString(),
      source:      m['source']?.toString()       ?? 'Unknown',
      attribution: m['attribution']?.toString()  ?? '',
      license:     m['license']?.toString()      ?? '',
      licenseUrl:  m['license_url']?.toString(),
      yearInt:     int.tryParse(yearStr),
    );
  }

  /// Human-readable caption for the expanded image view.
  String get caption {
    final parts = <String>[];
    if (year != null && year!.isNotEmpty && year != 'Unknown') parts.add(year!);
    if (denomination != null && denomination!.isNotEmpty &&
        denomination != 'Unknown') { parts.add(denomination!); }
    if (side != null && side!.isNotEmpty) { parts.add('(${side!})'); }
    final coinLabel = parts.join(' ');
    final attrStr = attribution.isNotEmpty ? ' — $attribution' : '';
    return '$coinLabel$attrStr · $license';
  }
}

/// Queries the `reference_library` Firestore collection for images that
/// visually match a given coin (denomination + year).
///
/// Results are sorted by year proximity (closest year first) and capped at
/// [maxResults]. Results are cached in-memory for the app session to avoid
/// re-querying Firestore on every panel open.
class ReferenceLibraryService {
  ReferenceLibraryService._();

  // ── In-memory cache — keyed by "denomination|targetYear" ─────────────────
  static final Map<String, List<ReferenceImage>> _cache = {};

  static const int _yearWindow = 5;
  static const int maxResults  = 6;

  /// Fetches matching reference images.
  ///
  /// [denomination] — e.g. "Quarter", "Dime". Case-insensitive prefix match.
  /// [year]         — the target year (can be null / 0 for unknown).
  ///
  /// Returns an empty list if Firestore is unreachable.
  static Future<List<ReferenceImage>> fetchSimilar({
    required String denomination,
    required int? year,
  }) async {
    final normDenom = _normalizeDenom(denomination);
    final targetYear = year ?? 0;
    final cacheKey = '$normDenom|$targetYear';

    if (_cache.containsKey(cacheKey)) return _cache[cacheKey]!;

    try {
      // Firestore only allows range filters on one field, so we filter by
      // denomination client-side and year range server-side.
      final low  = targetYear > 0 ? targetYear - _yearWindow : 0;
      final high = targetYear > 0 ? targetYear + _yearWindow : 9999;

      // Query: denomination exact match + year range.
      // If year is unknown we fall back to denomination-only.
      Query<Map<String, dynamic>> q = FirebaseFirestore.instance
          .collection('reference_library')
          .where('denomination', isEqualTo: normDenom)
          .limit(50); // fetch more than maxResults so we can sort

      if (targetYear > 0) {
        q = q
            .where('year_int', isGreaterThanOrEqualTo: low)
            .where('year_int', isLessThanOrEqualTo: high);
      }

      QuerySnapshot snap;
      try {
        snap = await q.get();
      } catch (_) {
        // If composite index is missing, fall back to a simpler query.
        snap = await FirebaseFirestore.instance
            .collection('reference_library')
            .where('denomination', isEqualTo: normDenom)
            .limit(50)
            .get();
      }

      final images = snap.docs
          .map((d) => ReferenceImage.fromDoc(d))
          .where((img) => img.gcsUrl.isNotEmpty)
          .toList();

      // Sort by year proximity
      if (targetYear > 0) {
        images.sort((a, b) {
          final da = (a.yearInt != null)
              ? (a.yearInt! - targetYear).abs()
              : 9999;
          final db = (b.yearInt != null)
              ? (b.yearInt! - targetYear).abs()
              : 9999;
          return da.compareTo(db);
        });
      }

      final result = images.take(maxResults).toList();
      _cache[cacheKey] = result;
      return result;
    } catch (e) {
      // Graceful failure — don't surface errors to the user
      return [];
    }
  }

  // ── Denomination normalizer ───────────────────────────────────────────────
  /// Maps free-form denomination strings to the canonical values used by the
  /// upload script (e.g. "quarter", "dime", "half dollar", etc.).
  static String _normalizeDenom(String raw) {
    final s = raw.toLowerCase().trim();
    if (s.contains('cent')    || s.contains('penny') || s.contains('1c'))  return 'Cent';
    if (s.contains('nickel')  || s.contains('5c'))                          return 'Nickel';
    if (s.contains('dime')    || s.contains('10c'))                         return 'Dime';
    if (s.contains('quarter') || s.contains('25c'))                         return 'Quarter';
    if (s.contains('half')    || s.contains('50c'))                         return 'Half Dollar';
    if (s.contains('dollar') || s.contains('\$1'))                           return 'Dollar';
    return raw; // pass through unknown denominations unchanged
  }

  /// Clears the in-memory cache (call on sign-out if needed).
  static void clearCache() => _cache.clear();
}
