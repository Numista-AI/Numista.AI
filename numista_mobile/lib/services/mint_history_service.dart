// lib/services/mint_history_service.dart
// ─────────────────────────────────────────────────────────────────────────────
// Historical US mint mark data by denomination and year.
// Used by the Roll Entry wizard to auto-suggest mint marks.
//
// Mint mark conventions:
//   ''  = Philadelphia (no mint mark, pre-1980 for most coins)
//   'P' = Philadelphia (mint mark added 1980+ for cents, earlier for others)
//   'D' = Denver
//   'S' = San Francisco (circulation pre-1968; proof-only post-1968)
//   'W' = West Point (bullion / special issues)
//   'CC'= Carson City (historical, closed 1893)
//   'O' = New Orleans (historical, closed 1909)
// ─────────────────────────────────────────────────────────────────────────────

/// Represents which mint marks were issued for a denomination in a year.
class YearMints {
  final int year;
  /// Circulation-strike mint marks (what a collector would find in a roll).
  final List<String> circulation;
  /// Proof-only mint marks (not in circulation rolls — excluded by default).
  final List<String> proofOnly;

  const YearMints({
    required this.year,
    required this.circulation,
    this.proofOnly = const [],
  });
}

// ─────────────────────────────────────────────────────────────────────────────
// Standard roll sizes by denomination
// ─────────────────────────────────────────────────────────────────────────────
const Map<String, int> kRollSize = {
  'cent':       50,
  'nickel':     40,
  'dime':       50,
  'quarter':    40,
  'half':       20,
  'dollar':     25,
};

// ─────────────────────────────────────────────────────────────────────────────
// Denomination display names
// ─────────────────────────────────────────────────────────────────────────────
const List<Map<String, String>> kDenominations = [
  {'key': 'cent',    'label': '1¢  Cent / Penny',     'series': 'Lincoln Cent'},
  {'key': 'nickel',  'label': '5¢  Nickel',            'series': 'Jefferson Nickel'},
  {'key': 'dime',    'label': '10¢ Dime',              'series': 'Roosevelt Dimes'},
  {'key': 'quarter', 'label': '25¢ Quarter',           'series': 'Washington Silver Quarter'},
  {'key': 'half',    'label': '50¢ Half Dollar',       'series': 'Kennedy Half Dollar'},
  {'key': 'dollar',  'label': '\$1  Dollar',            'series': 'Presidential Dollars'},
];

// ─────────────────────────────────────────────────────────────────────────────
// Main lookup service
// ─────────────────────────────────────────────────────────────────────────────
class MintHistoryService {

  /// Returns the likely circulation mint marks for a denomination in [year].
  /// Never includes proof-only mints (S post-1968, W, etc.) unless the
  /// caller explicitly asks via [includeProof].
  static List<String> getMints(String denom, int year, {bool includeProof = false}) {
    final data = _lookupYear(denom, year);
    if (data == null) return [];
    if (includeProof) {
      return [...data.circulation, ...data.proofOnly];
    }
    return data.circulation;
  }

  /// Returns [YearMints] rows for a denomination across a year range,
  /// inclusive. Only years with known issues are returned.
  static List<YearMints> getRange(String denom, int startYear, int endYear) {
    final result = <YearMints>[];
    for (int y = startYear; y <= endYear; y++) {
      final data = _lookupYear(denom, y);
      if (data != null) result.add(data);
    }
    return result;
  }

  // ── Private lookup ─────────────────────────────────────────────────────────
  static YearMints? _lookupYear(String denom, int year) {
    final table = _tables[denom];
    if (table == null) return null;

    // Walk ranges in order — first match wins
    for (final entry in table) {
      if (year >= entry.year) {
        // Check if there's a later entry that supersedes this one
        final idx = table.indexOf(entry);
        final isLast = idx == table.length - 1;
        if (isLast || year < table[idx + 1].year) {
          return YearMints(
            year: year,
            circulation: List.from(entry.circulation),
            proofOnly: List.from(entry.proofOnly),
          );
        }
      }
    }
    return null;
  }

  // ── Historical tables (range-based, sorted ascending by start year) ────────
  // Each entry applies from its year until the next entry's year (exclusive).
  // We use a simplified, collector-friendly view:
  //   - 1965-1967: no mint marks on any US coin (Special Mint Sets)
  //   - Post-1968 S: proof only (included in proofOnly, not circulation)
  //   - P mark added: cents 1980, nickels 1942, others 1979/1980
  static final Map<String, List<_RangeEntry>> _tables = {

    // ── Lincoln Cent ──────────────────────────────────────────────────────────
    'cent': [
      _RangeEntry(1909, ['', 'D', 'S']),           // 1909: also VDB varieties
      _RangeEntry(1922, ['D']),                     // 1922: D only (weak D exists)
      _RangeEntry(1923, ['', 'D', 'S']),
      _RangeEntry(1932, ['', 'D']),                 // S struck but very rare 1932-S
      _RangeEntry(1934, ['', 'D', 'S']),
      _RangeEntry(1943, ['', 'D', 'S']),            // Steel wartime cents
      _RangeEntry(1944, ['', 'D', 'S']),            // Back to bronze
      _RangeEntry(1956, ['', 'D']),                 // S dropped for circulation
      _RangeEntry(1965, [''], proofOnly: []),        // No mint mark, SMS only
      _RangeEntry(1968, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1973, ['', 'D', 'S'], proofOnly: []),  // 1973-S circulation
      _RangeEntry(1974, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1980, ['P', 'D'], proofOnly: ['S']),   // P mark added 1980
    ],

    // ── Jefferson Nickel ──────────────────────────────────────────────────────
    'nickel': [
      _RangeEntry(1938, ['', 'D', 'S']),
      _RangeEntry(1942, ['P', 'D', 'S']),           // Wartime silver — P on reverse
      _RangeEntry(1946, ['', 'D', 'S']),
      _RangeEntry(1955, ['', 'D']),                 // S dropped after 1955
      _RangeEntry(1965, [''],  proofOnly: []),
      _RangeEntry(1968, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1979, ['P', 'D'], proofOnly: ['S']),  // P mark 1979
    ],

    // ── Roosevelt Dime ────────────────────────────────────────────────────────
    'dime': [
      _RangeEntry(1946, ['', 'D', 'S']),
      _RangeEntry(1956, ['', 'D']),                 // S dropped for circ. after 1955
      _RangeEntry(1965, [''],  proofOnly: []),
      _RangeEntry(1968, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1980, ['P', 'D'], proofOnly: ['S']),
    ],

    // ── Washington Quarter ────────────────────────────────────────────────────
    'quarter': [
      _RangeEntry(1932, ['', 'D', 'S']),
      _RangeEntry(1934, ['', 'D']),                 // 1934: no S
      _RangeEntry(1936, ['', 'D', 'S']),
      _RangeEntry(1938, ['', 'S']),                 // 1938: no D
      _RangeEntry(1939, ['', 'D', 'S']),
      _RangeEntry(1940, ['', 'D', 'S']),
      _RangeEntry(1965, [''],  proofOnly: []),
      _RangeEntry(1968, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1979, ['P', 'D'], proofOnly: ['S']),
      _RangeEntry(1999, ['P', 'D'], proofOnly: ['S']),  // State quarters begin
      _RangeEntry(2010, ['P', 'D'], proofOnly: ['S']),  // ATB quarters
      _RangeEntry(2022, ['P', 'D'], proofOnly: ['S', 'W']),  // American Women
    ],

    // ── Kennedy Half Dollar ───────────────────────────────────────────────────
    'half': [
      _RangeEntry(1964, ['', 'D']),                 // 90% silver
      _RangeEntry(1965, [''],  proofOnly: []),       // 40% silver, no mark
      _RangeEntry(1968, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1971, ['', 'D'], proofOnly: ['S']),
      _RangeEntry(1979, ['P', 'D'], proofOnly: ['S']),
    ],

    // ── Dollar (Eisenhower / SBA / Sacagawea / Presidential) ─────────────────
    'dollar': [
      _RangeEntry(1971, ['', 'D'], proofOnly: ['S']),  // Ike dollar begins
      _RangeEntry(1979, ['P', 'D', 'S']),               // SBA — S was circulation
      _RangeEntry(1981, ['P', 'D'], proofOnly: ['S']),  // SBA ends
      _RangeEntry(2000, ['P', 'D'], proofOnly: ['S']),  // Sacagawea / Golden
      _RangeEntry(2007, ['P', 'D'], proofOnly: ['S']),  // Presidential begins
      _RangeEntry(2012, ['P', 'D'], proofOnly: ['S']),  // Presidential to sack-only for circ
    ],
  };
}

// Internal range entry (not exported)
class _RangeEntry extends YearMints {
  const _RangeEntry(int year, List<String> circulation,
      {List<String> proofOnly = const []})
      : super(year: year, circulation: circulation, proofOnly: proofOnly);
}
