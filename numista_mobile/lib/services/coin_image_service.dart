import 'package:cloud_firestore/cloud_firestore.dart';

/// Looks up reference coin images from the Firestore coin_image_index collection,
/// which is built by build_image_index.py from the GCS buckets:
///   - gs://us_mint_coin_images        (Tier 1 — US Mint official images)
///   - gs://numista-reference-library  (Tier 2–5 — reference + Wikimedia)
///
/// Key format in Firestore: {year}[_{mint}][_{subject}]_{program}_{side}
/// where subject is the state/president/woman slug for series coins.
///
/// Returns null for both obverse and reverse if no image is found — the caller
/// should fall back to "No photo yet" rather than showing an error.

class CoinImageService {
  static const _collection = 'coin_image_index';

  /// Programs that have per-design subjects (state, president, woman, etc.)
  /// Matches SUBJECT_PROGRAMS in build_image_index.py.
  static const _subjectPrograms = {
    '50-state-quarters',
    'presidential-dollars',
    'american-women-quarters',
    'america-the-beautiful',
    'american-innovation',
    'native-american-dollar',
    'commemorative',
  };

  /// Maps subject names (states, presidents, women) to canonical slugs.
  /// Mirrors STATE_SLUG_MAP in build_image_index.py.
  static const _subjectSlugMap = <String, String>{
    // 50 US States
    'alabama': 'alabama', 'alaska': 'alaska', 'arizona': 'arizona',
    'arkansas': 'arkansas', 'california': 'california', 'colorado': 'colorado',
    'connecticut': 'connecticut', 'delaware': 'delaware', 'florida': 'florida',
    'georgia': 'georgia', 'hawaii': 'hawaii', 'idaho': 'idaho',
    'illinois': 'illinois', 'indiana': 'indiana', 'iowa': 'iowa',
    'kansas': 'kansas', 'kentucky': 'kentucky', 'louisiana': 'louisiana',
    'maine': 'maine', 'maryland': 'maryland', 'massachusetts': 'massachusetts',
    'michigan': 'michigan', 'minnesota': 'minnesota', 'mississippi': 'mississippi',
    'missouri': 'missouri', 'montana': 'montana', 'nebraska': 'nebraska',
    'nevada': 'nevada', 'new hampshire': 'new-hampshire', 'new jersey': 'new-jersey',
    'new mexico': 'new-mexico', 'new york': 'new-york',
    'north carolina': 'north-carolina', 'north dakota': 'north-dakota',
    'ohio': 'ohio', 'oklahoma': 'oklahoma', 'oregon': 'oregon',
    'pennsylvania': 'pennsylvania', 'rhode island': 'rhode-island',
    'south carolina': 'south-carolina', 'south dakota': 'south-dakota',
    'tennessee': 'tennessee', 'texas': 'texas', 'utah': 'utah',
    'vermont': 'vermont', 'virginia': 'virginia', 'washington': 'washington',
    'west virginia': 'west-virginia', 'wisconsin': 'wisconsin', 'wyoming': 'wyoming',
    // Territories
    'puerto rico': 'puerto-rico', 'guam': 'guam',
    'us virgin islands': 'us-virgin-islands',
    'american samoa': 'american-samoa',
    'northern mariana': 'northern-mariana-islands',
    'district of columbia': 'district-of-columbia',
    // ATB parks
    'yellowstone': 'yellowstone', 'grand canyon': 'grand-canyon',
    'yosemite': 'yosemite', 'gettysburg': 'gettysburg',
    'hot springs': 'hot-springs', 'mount hood': 'mount-hood',
    'glacier': 'glacier', 'olympic': 'olympic',
    // ATB park name → state/territory slug (2010–2021 complete program)
    // Note: coin_image_index keys images by state (from filename), not park name.
    // 2010
    'hot springs national park': 'arkansas',
    'yellowstone national park': 'wyoming',
    'yosemite national park': 'california',
    'grand canyon national park': 'arizona',
    'mount hood national forest': 'oregon',
    // 2011
    'gettysburg national military park': 'pennsylvania',
    'glacier national park': 'montana',
    'olympic national park': 'washington',
    'vicksburg national military park': 'mississippi',
    'chickasaw national recreation area': 'oklahoma',
    // 2012
    'el yunque national forest': 'puerto-rico',
    'chaco culture national historical park': 'new-mexico',
    'acadia national park': 'maine',
    'hawaii volcanoes national park': 'hawaii',
    'denali national park': 'alaska',
    // 2013
    'white mountain national forest': 'new-hampshire',
    "perry's victory and international peace memorial": 'ohio',
    'great basin national park': 'nevada',
    'fort mchenry national monument': 'maryland',
    'mount rushmore national memorial': 'south-dakota',
    // 2014
    'great smoky mountains national park': 'tennessee',
    'shenandoah national park': 'virginia',
    'arches national park': 'utah',
    'great sand dunes national park': 'colorado',
    'everglades national park': 'florida',
    // 2015
    'homestead national monument': 'nebraska',
    'kisatchie national forest': 'louisiana',
    'blue ridge parkway': 'north-carolina',
    'bombay hook national wildlife refuge': 'delaware',
    'saratoga national historical park': 'new-york',
    // 2016
    'shawnee national forest': 'illinois',
    'cumberland gap national historical park': 'kentucky',
    'harpers ferry national historical park': 'west-virginia',
    'theodore roosevelt national park': 'north-dakota',
    'fort moultrie national monument': 'south-carolina',
    // 2017
    'effigy mounds national monument': 'iowa',
    'frederick douglass national historic site': 'district-of-columbia',
    'ozark national scenic riverways': 'missouri',
    'ellis island national monument': 'new-jersey',
    'george rogers clark national historical park': 'indiana',
    // 2018
    'pictured rocks national lakeshore': 'michigan',
    'apostle islands national lakeshore': 'wisconsin',
    'voyageurs national park': 'minnesota',
    'cumberland island national seashore': 'georgia',
    'block island national wildlife refuge': 'rhode-island',
    // 2019
    'lowell national historical park': 'massachusetts',
    'lowell': 'massachusetts',
    'american memorial park': 'northern-mariana-islands',
    'war in the pacific national historical park': 'guam',
    'war in the pacific': 'guam',
    'san antonio missions national historical park': 'texas',
    'san antonio missions': 'texas',
    'frank church river of no return wilderness': 'idaho',
    'frank church': 'idaho',
    'river of no return': 'idaho',
    // 2020
    'national park of american samoa': 'american-samoa',
    'weir farm national historical park': 'connecticut',
    'salt river bay national historical park': 'us-virgin-islands',
    'marsh-billings-rockefeller national historical park': 'vermont',
    'tallgrass prairie national preserve': 'kansas',
    // 2021
    'tuskegee airmen national historic site': 'alabama',
    'crossing the delaware': 'new-jersey',
    'washington crossing historic park': 'new-jersey',
    // Presidents (presidential dollar subjects)
    'adams': 'adams', 'jefferson': 'jefferson', 'madison': 'madison',
    'monroe': 'monroe', 'jackson': 'jackson', 'van buren': 'van-buren',
    'harrison': 'harrison', 'tyler': 'tyler', 'polk': 'polk',
    'taylor': 'taylor', 'fillmore': 'fillmore', 'pierce': 'pierce',
    'buchanan': 'buchanan', 'lincoln': 'lincoln', 'johnson': 'johnson',
    'grant': 'grant', 'hayes': 'hayes', 'garfield': 'garfield',
    'arthur': 'arthur', 'cleveland': 'cleveland', 'mckinley': 'mckinley',
    'roosevelt': 'roosevelt', 'taft': 'taft', 'wilson': 'wilson',
    'harding': 'harding', 'coolidge': 'coolidge', 'hoover': 'hoover',
    'truman': 'truman', 'eisenhower': 'eisenhower', 'kennedy': 'kennedy',
    'ford': 'ford', 'carter': 'carter', 'reagan': 'reagan',
    'bush': 'bush', 'clinton': 'clinton', 'obama': 'obama',
    'trump': 'trump', 'biden': 'biden',
    // American Women Quarters
    'maya angelou': 'maya-angelou', 'sally ride': 'sally-ride',
    'wilma mankiller': 'wilma-mankiller', 'nina otero warren': 'nina-otero-warren',
    'nina otero-warren': 'nina-otero-warren', 'adelina otero-warren': 'nina-otero-warren',
    'anna may wong': 'anna-may-wong', 'anna mae wong': 'anna-may-wong',
    'bessie coleman': 'bessie-coleman',
    'edith kanaka ole': 'edith-kanaka-ole',
    "edith kanaka\u02bbole": 'edith-kanaka-ole',   // okina (ʻ)
    "edith kanaka\u2018ole": 'edith-kanaka-ole',   // left single quote
    "edith kanaka\u2019ole": 'edith-kanaka-ole',   // right single quote
    'edith kanakaole': 'edith-kanaka-ole',
    'eleanor roosevelt': 'eleanor-roosevelt',
    'jovita idar': 'jovita-idar', 'maria tallchief': 'maria-tallchief',
    'patsy mink': 'patsy-mink', 'patsy takemoto mink': 'patsy-mink',
    // 2024 AWQ
    'celia cruz': 'celia-cruz',
    'zitkala-sa': 'zitkala-sa', 'zitkala sa': 'zitkala-sa', 'zitkala sha': 'zitkala-sa',
    'mary edwards walker': 'mary-edwards-walker',
    'pauli murray': 'pauli-murray',
    // 2025 AWQ
    'ida b. wells': 'ida-b-wells', 'ida b wells': 'ida-b-wells',
    'vera rubin': 'vera-rubin',
    'althea gibson': 'althea-gibson',
    'stacey park milbern': 'stacey-park-milbern',
    'juliette gordon low': 'juliette-gordon-low',
  };

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
    'franklin half dollar':    'franklin-half-dollar',
    'franklin-half-dollar':    'franklin-half-dollar',
    'walking liberty':         'liberty-walking-half-dollar',
    'liberty walking':         'liberty-walking-half-dollar',
    'walking-liberty':         'liberty-walking-half-dollar',
    'liberty-walking-half-dollar': 'liberty-walking-half-dollar',
    'barber half dollar':      'barber-half-dollar',
    'barber-half-dollar':      'barber-half-dollar',
    'barber quarter':          'barber-quarter',
    'barber-quarter':          'barber-quarter',
    'barber dime':             'barber-dime',
    'barber-dime':             'barber-dime',
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
    'eisenhower':              'eisenhower-dollar',
    'eisenhower dollar':       'eisenhower-dollar',
    'eisenhower-dollar':       'eisenhower-dollar',
    'ike dollar':              'eisenhower-dollar',
    'susan b anthony':         'dollar',
    'susan b. anthony':        'dollar',
    // Cents
    'indian head cent':        'indian-head-cent',
    'indian head penny':       'indian-head-cent',
    'indian-head-cent':        'indian-head-cent',
    'flying eagle':            'flying-eagle-cent',
    'flying eagle cent':       'flying-eagle-cent',
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

  /// Resolve a coin's Theme/Subject field to a canonical subject slug used in
  /// the Firestore key for series coins (State Quarters, Presidents, Women, etc.)
  static String? _resolveSubject(String? subject, String? program) {
    if (subject == null || subject.trim().isEmpty) return null;
    if (program == null || !_subjectPrograms.contains(program)) return null;
    final key = subject.trim().toLowerCase();
    // Exact match first
    if (_subjectSlugMap.containsKey(key)) return _subjectSlugMap[key];
    // Partial match — try longest matching key first to avoid e.g. 'adams' matching 'van buren'
    final sorted = _subjectSlugMap.entries.toList()
      ..sort((a, b) => b.key.length.compareTo(a.key.length));
    for (final entry in sorted) {
      if (key.contains(entry.key) || entry.key.contains(key)) {
        return entry.value;
      }
    }
    return null;
  }

  /// Build all candidate Firestore document keys for a coin, in priority order.
  /// Each key is a base (without side suffix) that we'll probe for both _obverse
  /// and _reverse documents.
  static List<String> _candidateBases(
      String year, String? mint, String? program, {String? subject}) {
    final bases = <String>[];
    if (program == null) return bases;

    // Subject-specific keys have highest priority (e.g. 1999_new-jersey_50-state-quarters)
    if (subject != null) {
      if (mint != null && mint.isNotEmpty) {
        bases.add('${year}_${mint}_${subject}_$program');
      }
      bases.add('${year}_${subject}_$program');
    }

    // Exact program with mint, then without (generic year+program fallbacks)
    if (mint != null && mint.isNotEmpty) {
      bases.add('${year}_${mint}_$program');
    }
    bases.add('${year}_$program');

    // Simpler fallbacks: e.g. lincoln-cent -> cent
    const simpleFallbacks = {
      'lincoln-cent':              'cent',
      'indian-head-cent':          'cent',
      'flying-eagle-cent':         'cent',
      'kennedy-half-dollar':       'dollar',
      'franklin-half-dollar':      'dollar',
      'liberty-walking-half-dollar':'dollar',
      'barber-half-dollar':        'dollar',
      'native-american-dollar':    'dollar',
      'presidential-dollars':      'dollar',
      'morgan-dollar':             'dollar',
      'peace-dollar':              'dollar',
      'eisenhower-dollar':         'dollar',
      '50-state-quarters':         'quarter',
      'american-women-quarters':   'quarter',
      'american-innovation':       'quarter',
      'america-the-beautiful':     'quarter',
      'barber-quarter':            'quarter',
      'jefferson-nickel':          'nickel',
      'buffalo-nickel':            'nickel',
      'mercury-dime':              'dime',
      'barber-dime':               'dime',
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
  ///
  /// Obverse and reverse are resolved INDEPENDENTLY across all candidate bases,
  /// so a subject-specific reverse (e.g. 1999_new-jersey_50-state-quarters_reverse)
  /// can be paired with a generic obverse (e.g. 1999_50-state-quarters_obverse)
  /// from a different candidate base.
  static Future<CoinImageResult> fetchReferenceImages({
    required String year,
    String? mint,
    String? denomination,
    String? series,
    String? subject,   // Theme/Subject field — e.g. 'New Jersey' for state quarters
  }) async {
    try {
      final program = _resolveProgram(denomination, series);
      if (program == null) return const CoinImageResult();

      // Resolve subject slug (e.g. 'New Jersey' -> 'new-jersey')
      final subjectSlug = _resolveSubject(subject, program);

      final db = FirebaseFirestore.instance;
      final bases = _candidateBases(
        year, mint?.toUpperCase(), program,
        subject: subjectSlug,
      );

      // Independently track the best obverse and best reverse found.
      // We keep scanning all candidate bases until both sides are resolved.
      String? bestObvUrl;
      String? bestRevUrl;
      String? bestAttr;
      String? bestLabel;
      String? bestKey;

      for (final base in bases) {
        final needsObv = bestObvUrl == null;
        final needsRev = bestRevUrl == null;
        if (!needsObv && !needsRev) break; // both sides resolved

        if (needsObv) {
          final obvDoc = await db.collection(_collection)
              .doc('${base}_obverse').get();
          if (obvDoc.exists) {
            final d = obvDoc.data()!['obverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestObvUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }

        if (needsRev) {
          final revDoc = await db.collection(_collection)
              .doc('${base}_reverse').get();
          if (revDoc.exists) {
            final d = revDoc.data()!['reverse'] as Map<String, dynamic>?;
            if (d != null) {
              bestRevUrl = d['public_url'] as String?;
              bestAttr  ??= d['attribution'] as String?;
              bestLabel ??= d['source_label'] as String?;
              bestKey   ??= base;
            }
          }
        }
      }

      if (bestObvUrl != null || bestRevUrl != null) {
        return CoinImageResult(
          obverseUrl:  bestObvUrl,
          reverseUrl:  bestRevUrl,
          attribution: bestAttr,
          sourceLabel: bestLabel,
          matchedKey:  bestKey,
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
