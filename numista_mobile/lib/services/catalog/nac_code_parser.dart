/// NAC1 (Numista.AI Catalog v1) identifier grammar, Crockford-32 checksum,
/// parser, and collection router.
///
/// Spec: Plan.v2.1 sections 2.1 - 2.2 & 3.1.
library;

class Nac1Parsed {
  final String nacCode;
  final String payload;
  final String kind;
  final String cc;
  final String denominationClass;
  final String series;
  final String year;
  final String facilityCode;
  final String variety;
  final String chk;

  const Nac1Parsed({
    required this.nacCode,
    required this.payload,
    required this.kind,
    required this.cc,
    required this.denominationClass,
    required this.series,
    required this.year,
    required this.facilityCode,
    required this.variety,
    required this.chk,
  });

  String get targetCollection => NacCodeParser.kindToCollection(kind);
}

class NacCodeParser {
  static const String crockford32 = '0123456789ABCDEFGHJKMNPQRSTVWXYZ';

  /// Chapter 0 (Plan 8f01c991 / Muse PHD-4): all 12 official Federal Reserve District
  /// facility codes, permitted ONLY when kind == 'BN' (strictly rejected for CN/MD/TK/ST).
  /// Strict parity with `numista_backend/catalog_nac1.py` (`BN_ONLY_FACILITIES`).
  static const Set<String> bnOnlyFacilities = <String>{
    'BOS', // 1 - Boston
    'NY',  // 2 - New York
    'PHI', // 3 - Philadelphia (distinct from coin mint PH / P)
    'CLE', // 4 - Cleveland
    'RIC', // 5 - Richmond
    'ATL', // 6 - Atlanta
    'CHI', // 7 - Chicago
    'STL', // 8 - St. Louis
    'MIN', // 9 - Minneapolis
    'KC',  // 10 - Kansas City
    'DAL', // 11 - Dallas
    'SF',  // 12 - San Francisco
  };

  static final RegExp nac1Regex = RegExp(
    r'^(NAC1\.(CN|BN|MD|TK|ST)\.(US|CO|PF|CS|FS)\.([A-Z0-9]{2,8})\.([A-Z0-9_]{2,12})\.([0-9]{4}[A-Z]?|ND|XXXX)\.(P|D|S|W|CC|O|C|DD|M|MO|L|PTS|PH|BEP|NARA|XX|BOS|NY|PHI|CLE|RIC|ATL|CHI|STL|MIN|KC|DAL|SF)\.([A-Z0-9_]{2,12}))\.([0-9A-HJ-KM-NP-TV-Z])$',
  );

  static const Map<String, String> _kindToCollectionMap = {
    'CN': 'coins',
    'BN': 'currency',
    'MD': 'world_items',
    'TK': 'world_items',
    'ST': 'world_items',
  };

  static RegExpMatch? _matchNac1(String nacCode) {
    final match = nac1Regex.firstMatch(nacCode);
    if (match == null) {
      return null;
    }
    final kind = match.group(2)!;
    final fac = match.group(7)!;
    if (bnOnlyFacilities.contains(fac) && kind != 'BN') {
      return null;
    }
    return match;
  }

  /// Computes the Crockford-32 check character over the ASCII payload preceding `.CHK`.
  static String computeNac1Chk(String payload) {
    int h = 0;
    for (final int b in payload.codeUnits) {
      h = (h * 33 + b) % 37;
    }
    return crockford32[h % 32];
  }

  /// Returns true only if [nacCode] matches the NAC1 grammar, kind-scoped facility
  /// constraints, and passes checksum validation.
  static bool validateNac1(String? nacCode) {
    if (nacCode == null || nacCode.isEmpty) {
      return false;
    }
    final match = _matchNac1(nacCode);
    if (match == null) {
      return false;
    }
    final payload = match.group(1)!;
    final chk = match.group(9)!;
    return computeNac1Chk(payload) == chk;
  }

  /// Appends the computed `.CHK` character to a raw 8-segment payload.
  static String buildNac1(String payload) {
    return '$payload.${computeNac1Chk(payload)}';
  }

  /// Maps a NAC1 `KIND` code to its Firestore user sub-collection.
  /// Bank Notes (`BN`) and Medals (`MD`) NEVER route to `coins`.
  static String kindToCollection(String kind) {
    final target = _kindToCollectionMap[kind];
    if (target == null) {
      throw ArgumentError.value(kind, 'kind', 'Unknown NAC1 kind');
    }
    return target;
  }

  /// Parses a validated NAC1 string into its 9 segments.
  /// Throws [FormatException] if [nacCode] is malformed, violates kind-scoped facility
  /// rules, or has an invalid check digit.
  static Nac1Parsed parseNac1(String nacCode) {
    final match = _matchNac1(nacCode);
    if (match == null) {
      throw const FormatException('INVALID_NAC1_FORMAT');
    }
    final payload = match.group(1)!;
    final chk = match.group(9)!;
    if (computeNac1Chk(payload) != chk) {
      throw const FormatException('INVALID_NAC1_CHECKSUM');
    }
    return Nac1Parsed(
      nacCode: nacCode,
      payload: payload,
      kind: match.group(2)!,
      cc: match.group(3)!,
      denominationClass: match.group(4)!,
      series: match.group(5)!,
      year: match.group(6)!,
      facilityCode: match.group(7)!,
      variety: match.group(8)!,
      chk: chk,
    );
  }
}
