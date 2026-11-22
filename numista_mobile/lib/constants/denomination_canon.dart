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
    '1₵': cent,
    '\$0.01': cent,
    '0.01': cent,
    '.01': cent,
    '.01¢': cent,
    '.01₵': cent,
    'wheatie': cent,
    'wheat penny': cent,
    'wheat cent': cent,
    'lincoln penny': cent,
    'lincoln cent': cent,
    'indian head penny': cent,
    'flying eagle cent': cent,
    'cent': cent,
    'nickel': fiveCents,
    'nickels': fiveCents,
    'nickles': fiveCents,
    '5 cents': fiveCents,
    '5c': fiveCents,
    '5¢': fiveCents,
    '5₵': fiveCents,
    '\$0.05': fiveCents,
    '0.05': fiveCents,
    '.05': fiveCents,
    '.05¢': fiveCents,
    '.05₵': fiveCents,
    'five cent': fiveCents,
    'five cents': fiveCents,
    'jefferson nickel': fiveCents,
    'buffalo nickel': fiveCents,
    'indian head nickel': fiveCents,
    'v nickel': fiveCents,
    'liberty nickel': fiveCents,
    'shield nickel': fiveCents,
    'one dime': dime,
    '10c': dime,
    '10¢': dime,
    '10₵': dime,
    '\$0.10': dime,
    '0.10': dime,
    '.10': dime,
    '.10¢': dime,
    '.10₵': dime,
    'ten cents': dime,
    '10 cents': dime,
    'roosevelt dime': dime,
    'mercury dime': dime,
    'winged liberty dime': dime,
    'barber dime': dime,
    'seated dime': dime,
    'dime': dime,
    'quarter': quarterDollar,
    'quarters': quarterDollar,
    '25c': quarterDollar,
    '25¢': quarterDollar,
    '25₵': quarterDollar,
    '25 cents': quarterDollar,
    '.25¢': quarterDollar,
    '.25₵': quarterDollar,
    '0.25¢': quarterDollar,
    '0.25₵': quarterDollar,
    '\$0.25': quarterDollar,
    '0.25': quarterDollar,
    '.25': quarterDollar,
    'washington quarter': quarterDollar,
    'state quarter': quarterDollar,
    'atb quarter': quarterDollar,
    'standing liberty quarter': quarterDollar,
    'barber quarter': quarterDollar,
    'two bits': quarterDollar,
    'quarter dollar': quarterDollar,
    'half': halfDollar,
    'halves': halfDollar,
    '50c': halfDollar,
    '50¢': halfDollar,
    '50₵': halfDollar,
    '50 cents': halfDollar,
    '.50¢': halfDollar,
    '.50₵': halfDollar,
    '\$0.50': halfDollar,
    '0.50': halfDollar,
    '.50': halfDollar,
    'fifty cent piece': halfDollar,
    '50 cent piece': halfDollar,
    'jfk 50 cent piece': halfDollar,
    'jfk half': halfDollar,
    'kennedy half': halfDollar,
    'kennedy half dollar': halfDollar,
    'franklin half': halfDollar,
    'walking liberty half': halfDollar,
    'barber half': halfDollar,
    'half dollar': halfDollar,
    'dollar coin': dollar,
    'one dollar': dollar,
    '\$1': dollar,
    '\$1 coin': dollar,
    '\$1.00': dollar,
    '1.00': dollar,
    '1 dollar': dollar,
    'buck': dollar,
    'dollar': dollar,
    'silver dollar': dollar,
    'morgan dollar': dollar,
    'peace dollar': dollar,
    'eisenhower dollar': dollar,
    'ike dollar': dollar,
    'susan b anthony dollar': dollar,
    'sacagawea dollar': dollar,
    'presidential dollar': dollar,
    'native american dollar': dollar,
    'american innovation dollar': dollar,
  };

  static const Set<String> _usCountryNames = {
    '',
    'us',
    'usa',
    'u.s.',
    'u.s.a.',
    'united states',
    'united states of america',
    'united states mint',
  };

  /// Normalizes a raw string to canonical form if recognized as US denomination.
  /// Guards banknotes and non-US coins (returns trimmed original unchanged).
  static String normalize(
    String? raw, {
    String? country,
    String? itemType,
    bool? isForeign,
  }) {
    if (raw == null) return '';
    final trimmed = raw.trim();
    if (trimmed.isEmpty) return '';

    // Guard 1: Paper currency / banknotes
    final itemLower = (itemType ?? '').trim().toLowerCase();
    if (itemLower.contains('paper') || itemLower == 'banknote' || itemLower == 'currency') {
      return trimmed;
    }
    if (RegExp(r'^\$[2-9]\d*(\.\d+)?$').hasMatch(trimmed) ||
        RegExp(r'^\$1\d+(\.\d+)?$').hasMatch(trimmed)) {
      return trimmed;
    }

    // Guard 2: Explicit non-US coin
    if (isForeign == true) return trimmed;
    if (country != null) {
      final cLower = country.trim().toLowerCase();
      if (cLower.isNotEmpty && !_usCountryNames.contains(cLower)) {
        return trimmed;
      }
    }

    // Strip parenthetical suffixes like (25C) and collapse spaces before ¢/₵ ('.25 ₵' -> '.25₵')
    var clean = trimmed
        .replaceAll(RegExp(r'\s*\(\s*\d+\s*[c¢₵\w\s]*\)', caseSensitive: false), '')
        .replaceAllMapped(RegExp(r'\s+([¢₵])'), (m) => m.group(1)!)
        .trim();
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
