import 'package:cloud_firestore/cloud_firestore.dart';

/// Looks up reference coin images from the Firestore coin_image_index collection,
/// which is built by build_image_index.py from the GCS buckets:
///   - gs://us_mint_coin_images        (Tier 1 — US Mint official images)
///   - gs://numista-reference-library  (Tier 2–5 — reference + Wikimedia)
///
/// Key format in Firestore: {year}_{mint}_{program}_{side}
///              or without mint: {year}_{program}_{side}
///
/// Returns null for both obverse and reverse if no image is found — the caller
/// should fall back to "No photo yet" rather than showing an error.

class CoinImageService {
  static const _collection = 'coin_image_index';

  /// Maps denomination/series strings → canonical program slug used as the
  /// Firestore key fragment. Matches the PROGRAM_MAP in build_image_index.py.
  static const _programMap = <String, String>{
    // Lincoln / cents
    'penny':                   'lincoln-cent',
    'cent':                    'lincoln-cent',
    'lincoln cent':            'lincoln-cent',
    'lincoln-cent':            'lincoln-cent',
    'wheat cent':              'lincoln-cent',
    'wheat penny':             'lincoln-cent',
    // Nickels
    'nickel':                  'nickel',
    'jefferson nickel':        'jefferson-nickel',
    'jefferson-nickel':        'jefferson-nickel',
    'buffalo nickel':          'buffalo-nickel',
    'buffalo-nickel':          'buffalo-nickel',
    // Dimes
    'dime':                    'dime',
    'mercury dime':            'mercury-dime',
    'mercury-dime':            'mercury-dime',
    'roosevelt dime':          'dime',
    // Quarters
    'quarter':                 'quarter',
    '25c':                     'quarter',
    'state quarter':           '50-state-quarters',
    '50 state quarters':       '50-state-quarters',
    '50-state-quarters':       '50-state-quarters',
    'america the beautiful':   'america-the-beautiful',
    'american women quarters': 'american-women-quarters',
    'american innovation':     'american-innovation',
    // Half dollars
    'half dollar':             'kennedy-half-dollar',
    'kennedy half dollar':     'kennedy-half-dollar',
    'kennedy-half-dollar':     'kennedy-half-dollar',
    'walking liberty':         'walking-liberty',
    'walking-liberty':         'walking-liberty',
    // Dollars
    'dollar':                  'dollar',
    'morgan silver dollar':    'morgan-dollar',
    'morgan dollar':           'morgan-dollar',
    'morgan-dollar':           'morgan-dollar',
    'peace dollar':            'peace-dollar',
    'peace-dollar':            'peace-dollar',
    'sacagawea':               'native-american-dollar',
    'native american dollar':  'native-american-dollar',
    'presidential dollar':     'presidential-dollars',
    'presidential dollars':    'presidential-dollars',
    'eisenhower':              'dollar',
    'eisenhower dollar':       'dollar',
    // American Eagles
    'american eagle silver':   'american-eagle-silver',
    'american silver eagle':   'american-eagle-silver',
    'silver eagle':            'american-eagle-silver',
    'american eagle gold':     'american-eagle-gold',
    'american gold eagle':     'american-eagle-gold',
    'gold eagle':              'american-eagle-gold',
    'american eagle platinum': 'american-eagle-platinum',
    'platinum eagle':          'american-eagle-platinum',
    'american eagle palladium':'american-eagle-palladium',
    'palladium eagle':         'american-eagle-palladium',
    // Other
    'saint-gaudens':           'saint-gaudens',
    'saint gaudens':           'saint-gaudens',
    'double eagle':            'saint-gaudens',
    'bicentennial':            'bicentennial',
    'flowing hair':            'flowing-hair',
    'flowing-hair':            'flowing-hair',
    'american liberty':        'american-liberty',
    'commemorative':           'commemorative',
  };

  /// Resolve a coin's denomination + series fields to a canonical program slug.
  static String? _resolveProgram(String? denomination, String? series) {
    // Prefer the series name (more specific), fall back to denomination
    for (final raw in [series, denomination]) {
      if (raw == null || raw.trim().isEmpty) continue;
      final key = raw.trim().toLowerCase();
      // Exact match first
      if (_programMap.containsKey(key)) return _programMap[key];
      // Partial match
      for (final entry in _programMap.entries) {
        if (key.contains(entry.key) || entry.key.contains(key)) {
          return entry.value;
        }
      }
    }
    return null;
  }

  /// Build all candidate Firestore document keys for a coin, in priority order.
  /// Each key is a base (without side suffix) that we'll probe for both _obverse
  /// and _reverse documents.
  static List<String> _candidateBases(
      String year, String? mint, String? program) {
    final bases = <String>[];
    if (program == null) return bases;

    // Exact program with mint, then without
    if (mint != null && mint.isNotEmpty) {
      bases.add('${year}_${mint}_$program');
    }
    bases.add('${year}_$program');

    // Simpler fallbacks: e.g. lincoln-cent -> cent
    const simpleFallbacks = {
      'lincoln-cent':          'cent',
      'kennedy-half-dollar':   'dollar',
      'native-american-dollar':'dollar',
      'presidential-dollars':  'dollar',
      'morgan-dollar':         'dollar',
      'peace-dollar':          'dollar',
      '50-state-quarters':     'quarter',
      'american-women-quarters':'quarter',
      'american-innovation':   'quarter',
      'america-the-beautiful': 'quarter',
      'jefferson-nickel':      'nickel',
      'buffalo-nickel':        'nickel',
      'mercury-dime':          'dime',
    };
    final simple = simpleFallbacks[program];
    if (simple != null) {
      if (mint != null && mint.isNotEmpty) {
        bases.add('${year}_${mint}_$simple');
      }
      bases.add('${year}_$simple');
    }

    // Reverse fallback: simple -> specific programs (quarter -> 50-state-quarters)
    const expandFallbacks = {
      'quarter': ['50-state-quarters', 'america-the-beautiful', 'american-women-quarters', 'american-innovation'],
      'cent':    ['lincoln-cent'],
      'nickel':  ['jefferson-nickel', 'buffalo-nickel'],
      'dime':    ['mercury-dime'],
      'dollar':  ['morgan-dollar', 'peace-dollar', 'native-american-dollar', 'presidential-dollars', 'kennedy-half-dollar'],
    };
    final expanded = expandFallbacks[program];
    if (expanded != null) {
      for (final p in expanded) {
        if (mint != null && mint.isNotEmpty) {
          bases.add('${year}_${mint}_$p');
        }
        bases.add('${year}_$p');
      }
    }

    return bases;
  }

  /// Fetches obverse + reverse public URLs for a coin from Firestore.
  /// Returns a [CoinImageResult] -- fields are null if no image found.
  /// Never throws; errors are silently swallowed so the UI degrades gracefully.
  static Future<CoinImageResult> fetchReferenceImages({
    required String year,
    String? mint,
    String? denomination,
    String? series,
  }) async {
    try {
      final program = _resolveProgram(denomination, series);
      if (program == null) return const CoinImageResult();

      final db = FirebaseFirestore.instance;
      final bases = _candidateBases(year, mint?.toUpperCase(), program);

      for (final base in bases) {
        final obvKey = '${base}_obverse';
        final revKey = '${base}_reverse';

        final obvDoc = await db.collection(_collection).doc(obvKey).get();
        final revDoc = await db.collection(_collection).doc(revKey).get();

        if (!obvDoc.exists && !revDoc.exists) continue;

        final obvData = obvDoc.exists
            ? (obvDoc.data()!['obverse'] as Map<String, dynamic>?)
            : null;
        final revData = revDoc.exists
            ? (revDoc.data()!['reverse'] as Map<String, dynamic>?)
            : null;

        if (obvData == null && revData == null) continue;

        // Use whichever side has attribution info
        final attrSource = obvData ?? revData;

        return CoinImageResult(
          obverseUrl:   obvData?['public_url'] as String?,
          reverseUrl:   revData?['public_url'] as String?,
          attribution:  attrSource?['attribution'] as String?,
          sourceLabel:  attrSource?['source_label'] as String?,
          matchedKey:   base,
        );
      }
    } catch (e) {
      // Silent fail -- image lookup is non-critical
    }
    return const CoinImageResult();
  }
}

/// Result object for a coin image lookup.
class CoinImageResult {
  final String? obverseUrl;
  final String? reverseUrl;
  final String? attribution;
  final String? sourceLabel;
  final String? matchedKey;

  const CoinImageResult({
    this.obverseUrl,
    this.reverseUrl,
    this.attribution,
    this.sourceLabel,
    this.matchedKey,
  });

  bool get hasObverse => obverseUrl != null && obverseUrl!.isNotEmpty;
  bool get hasReverse => reverseUrl != null && reverseUrl!.isNotEmpty;
  bool get hasAny     => hasObverse || hasReverse;
}
