/// Numista.AI Canonical US Mint Denominations (GI-NOM-01)
/// Authoritative client-side constants for formal US Mint nomenclature.
class DenominationCanon {
  static const String cent          = 'Cent';
  static const String fiveCents     = 'Five Cents';
  static const String dime          = 'Dime';
  static const String quarterDollar = 'Quarter Dollar';
  static const String halfDollar    = 'Half Dollar';
  static const String dollar        = 'Dollar';

  /// Primary active US circulating denominations
  static const List<String> usCirculating = [
    cent,
    fiveCents,
    dime,
    quarterDollar,
    halfDollar,
    dollar,
  ];

  /// Colloquial -> Canonical mapping dictionary
  static const Map<String, String> colloquialMap = {
    'penny': cent,
    'pennies': cent,
    'one cent': cent,
    '1 cent': cent,
    '1c': cent,
    '1¢': cent,
    'wheatie': cent,
    'lincoln cent': cent,
    'nickel': fiveCents,
    'nickels': fiveCents,
    'nickles': fiveCents,
    '5 cents': fiveCents,
    '5c': fiveCents,
    '5¢': fiveCents,
    'five cent': fiveCents,
    'five cents': fiveCents,
    'jefferson nickel': fiveCents,
    'buffalo nickel': fiveCents,
    '10c': dime,
    '10¢': dime,
    'ten cents': dime,
    '10 cents': dime,
    'roosevelt dime': dime,
    'dime': dime,
    'quarter': quarterDollar,
    'quarters': quarterDollar,
    '25c': quarterDollar,
    '25¢': quarterDollar,
    '25 cents': quarterDollar,
    'washington quarter': quarterDollar,
    'state quarter': quarterDollar,
    'quarter dollar': quarterDollar,
    'half': halfDollar,
    'halves': halfDollar,
    '50c': halfDollar,
    '50¢': halfDollar,
    '50 cents': halfDollar,
    'jfk half': halfDollar,
    'kennedy half': halfDollar,
    'half dollar': halfDollar,
    'dollar coin': dollar,
    '\$1': dollar,
    '1 dollar': dollar,
    'dollar': dollar,
    'silver dollar': dollar,
    'morgan dollar': dollar,
    'peace dollar': dollar,
  };

  /// Normalizes a raw string to canonical form if recognized as US denomination.
  /// Fails open (returns trimmed original) if unknown or foreign.
  static String normalize(String? raw) {
    if (raw == null) return '';
    final trimmed = raw.trim();
    if (trimmed.isEmpty) return '';

    // Strip suffixes like (25C)
    final clean = trimmed.replaceAll(RegExp(r'\s*\(\s*\d+\s*[c¢\w\s]*\)', caseSensitive: false), '').trim();
    final lower = clean.toLowerCase();

    if (lower == 'quarter dollar dollar') return quarterDollar;
    if (lower == 'dollar dollar') return dollar;
    if (lower == 'cent cent') return cent;

    return colloquialMap[lower] ?? trimmed;
  }

  /// Autocomplete suggestions for 60+ collectors entering denominations.
  /// e.g. "penn" -> ["Cent (Penny)"], "quart" -> ["Quarter Dollar (Quarter)"]
  static List<String> getSuggestions(String query) {
    final q = query.trim().toLowerCase();
    if (q.isEmpty) return usCirculating;

    final results = <String>{};
    for (final formal in usCirculating) {
      if (formal.toLowerCase().contains(q)) {
        results.add(formal);
      }
    }

    colloquialMap.forEach((alias, formal) {
      if (alias.contains(q) && !results.contains(formal)) {
        results.add('$formal ($alias)');
      }
    });

    return results.toList();
  }
}
