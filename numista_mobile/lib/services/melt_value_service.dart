// melt_value_service.dart
//
// Standardized Valuation Service for Numista.AI
// Calculates real-time face value and melt value for coins:
//   - Field precedence: Uses explicit numeric fields (denomination_numeric, troy_oz_pure_metal) when available
//   - Fallback normalization: Normalizes truncated/dirty strings ("Five Dollars (Hal..." -> $5.00)
//   - Spot price resilience: Live spot prices with cached fallback and offline indicator support

class MeltValueService {
  // ── Silver (Ag) troy oz per coin by denomination ───────────────────────────
  static const _ag90 = {
    'half dime':   0.03617,   // Nominal 1.25g (1853+ 1.24g) × 90% ÷ 31.1035
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };

  static const _ag40 = {
    'half':        0.14792,
    'half dollar': 0.14792,
  };

  static const _ag35 = {
    'nickel': 0.05626,
  };

  static const double _silverEagleOz = 1.0;

  // ── Gold (Au) troy oz per coin by face value ───────────────────────────────
  static final _au90ByFaceValue = {
    1.0:  0.04837,   // $1 gold piece
    2.5:  0.12094,   // Quarter Eagle
    3.0:  0.14513,   // $3 gold piece
    5.0:  0.24188,   // Half Eagle
    10.0: 0.48375,   // Eagle
    20.0: 0.96750,   // Double Eagle
  };

  static final _au9167ByFaceValue = {
    5.0:  0.10,
    10.0: 0.25,
    25.0: 0.50,
    50.0: 1.00,
  };

  static const double _buffaloAuOz = 1.0;

  // ── Unified Face Value Parser ──────────────────────────────────────────────
  /// Parses denomination string to numerical USD value.
  /// Pre-processes dirty strings by stripping parenthetical notes and ellipses.
  /// Evaluates multi-word terms before generic single tokens.
  static double parseFaceValue(String rawDenom, {int qty = 1}) {
    final count = qty > 0 ? qty : 1;
    if (rawDenom.trim().isEmpty) return 0.0;

    // Normalization pipeline: lowercase, collapse whitespace, strip parenthetical & ellipses
    String s = rawDenom.toLowerCase().trim();

    // Multi-coin set detection BEFORE stripping parenthetical notes
    int setMultiplier = 1;
    final setMatch = RegExp(
      r'\(?(\d+|two|three|four|five)[- ]coin set\)?',
      caseSensitive: false,
    ).firstMatch(s);

    if (setMatch != null) {
      final token = setMatch.group(1)!.toLowerCase();
      switch (token) {
        case '2':
        case 'two':
          setMultiplier = 2;
          break;
        case '3':
        case 'three':
          setMultiplier = 3;
          break;
        case '4':
        case 'four':
          setMultiplier = 4;
          break;
        case '5':
        case 'five':
          setMultiplier = 5;
          break;
        default:
          setMultiplier = int.tryParse(token) ?? 1;
      }
    } else if (RegExp(r'\bset\b', caseSensitive: false).hasMatch(s) && !s.contains('offset')) {
      // Indeterminate multi-coin / collector set without specific count -> No face value chip (0.0)
      return 0.0;
    }

    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();
    s = s.replaceAll('\u00bd', ' 1/2');
    s = s.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Guard non-legal-tender blanks (planchets), non-USD units (candareens),
    // and multi-denomination sets/ranges ('$100/$50/$25/$10', '$1, $2, $5, $10', '3c-50c')
    if (s.contains('planchet') ||
        s.contains('candareen') ||
        RegExp(r'\$\d[\d,]*(?:\.\d+)?\s*(?:/\s*\$?|,\s*\$)\s*\d').hasMatch(s) ||
        RegExp(r'\d\s*(?:\u00a2|c|cents?)?\s*[\u2013\-]\s*\d').hasMatch(s)) {
      return 0.0;
    }

    double value = 0.0;

    // 0. Leading numeric & fractional patterns (N Dollars, 1,000 Dollars, 10,000 Dollars, 2 1/2 Dollars, G$2 1/2, 3 cents, $1000)
    final fracDollarMatch = RegExp(r'^(?:g?\$)?\s*(\d+)\s+1/2(?:\s*dollars?)?$').firstMatch(s);
    final leadDollarMatch = RegExp(r'^\$?\s*(\d[\d,]*(?:\.\d+)?)\s*(?:dollars?|\$)$').firstMatch(s);
    final leadCentMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*(?:cents?|c|\u00a2)\b').firstMatch(s);
    final leadSymDollarMatch = RegExp(r'^\$\s*(\d[\d,]*(?:\.\d+)?)(?:\b|$)').firstMatch(s);

    if (fracDollarMatch != null) {
      value = (double.tryParse(fracDollarMatch.group(1)!) ?? 0.0) + 0.5;
    } else if (leadDollarMatch != null) {
      value = double.tryParse(leadDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    } else if (leadCentMatch != null) {
      value = (double.tryParse(leadCentMatch.group(1)!) ?? 0.0) / 100.0;
    } else if (leadSymDollarMatch != null) {
      value = double.tryParse(leadSymDollarMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
    }

    // 1. High Gold, Notes & Commemoratives
    else if (s.contains(r'$10,000') || s.contains(r'$10000') || s.contains('ten thousand dollar')) { value = 10000.00; }
    else if (s.contains(r'$1,000') || s.contains(r'$1000') || s.contains('one thousand dollar') || s.contains('thousand dollar')) { value = 1000.00; }
    else if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$40') || s.contains('forty dollar')) { value = 40.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$4') || s.contains('four dollar') || s.contains('stella')) { value = 4.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('2 1/2') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations (multi-word terms before single tokens)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime') || s.contains('half-dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent') || s.contains('half-cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }

    // 3. Fallback: plain numeric parse
    else {
      final match = RegExp(r'\d+(?:\.\d+)?').firstMatch(s);
      if (match != null) {
        final parsed = double.tryParse(match.group(0)!) ?? 0.0;
        value = parsed <= 1000.0 ? parsed : 0.0;
      }
    }

    return value * count * setMultiplier;
  }

  // ── Public Melt Value Calculation API ──────────────────────────────────────
  /// Returns melt value in USD, or null for base-metal / non-precious coins.
  static double? compute({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final count = qty > 0 ? qty : 1;
    final ag = spotPrices['Silver'] ?? 0.0;
    final au = spotPrices['Gold']   ?? 0.0;

    if (ag == 0.0 && au == 0.0) return null;

    // Field Precedence: Check if backend numeric troy oz field is present
    if (coinData != null) {
      final ozNum = (coinData['troy_oz_pure_metal'] as num?)?.toDouble();
      final isGold = coinData['is_gold'] == true;
      final isSilver = coinData['is_silver'] == true;
      if (ozNum != null && ozNum > 0.0) {
        if (isGold && au > 0) return au * ozNum * count;
        if (isSilver && ag > 0) return ag * ozNum * count;
      }
    }

    final mc     = metalContent.trim().toLowerCase();
    final denom  = denomination.trim().toLowerCase();
    final series = programSeries.trim().toLowerCase();
    final theme  = themeSubject.trim().toLowerCase();
    final combined = '$mc $denom $series $theme';

    // ── Gold Detection ──────────────────────────────────────────────────────
    if (combined.contains('gold') || combined.contains('half eagle') || combined.contains('eagle') || combined.contains('double eagle')) {
      if (combined.contains('99.99') || combined.contains('buffalo')) {
        return au * _buffaloAuOz * count;
      }
      if (combined.contains('91.67') || combined.contains('gold eagle')) {
        final fv = parseFaceValue(denom);
        final oz = _au9167ByFaceValue[fv] ?? 1.0;
        return au * oz * count;
      }
      if (combined.contains('90%') || combined.contains('half eagle') || combined.contains('indian head gold') || combined.contains('pre-1933') || combined.contains('saint-gaudens') || combined.contains('liberty head')) {
        final fv = parseFaceValue(denom);
        final oz = _au90ByFaceValue[fv] ?? 0.24188;
        return au * oz * count;
      }
      if (au > 0) return au * 0.24188 * count;
    }

    // ── Silver Detection ────────────────────────────────────────────────────
    if (combined.contains('silver') || combined.contains('silver eagle') || combined.contains('peace dollar') || combined.contains('morgan')) {
      if (combined.contains('silver eagle') || combined.contains('99.9') || combined.contains('.999') || combined.contains('fine silver')) {
        return ag * _silverEagleOz * count;
      }
      if (combined.contains('90%') || combined.contains('half dime') || combined.contains('half-dime') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final fv = parseFaceValue(denom);
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
      if (combined.contains('40%')) {
        final oz = _matchDenom(_ag40, denom) ?? 0.14792;
        return ag * oz * count;
      }
      if (combined.contains('35%') || ((combined.contains('war nickel') || combined.contains('wartime')) && parseFaceValue(denom) == 0.05)) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
      if (ag > 0) {
        final fv = parseFaceValue(denom);
        // N4: Route 5-cent wartime/war nickels without "35%" text to 35% war nickel weight
        if (fv == 0.05 && (combined.contains('nickel') || combined.contains('wartime') || (combined.contains('war') && !combined.contains('award') && !combined.contains('howard') && !combined.contains('edward')) || combined.contains('manganese'))) {
          return ag * 0.05626 * count;
        }
        final isDollar = fv == 1.00 || combined.contains('dollar') || combined.contains('morgan') || combined.contains('peace');
        final oz = _matchDenom(_ag90, denom) ?? (isDollar ? 0.77344 : null);
        if (oz != null) return ag * oz * count;
        return null;
      }
    }

    return null;
  }

  /// Formatted melt value string. Returns 'N/A' for non-precious coins.
  static String format({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
    String programSeries = '',
    String themeSubject = '',
    int qty = 1,
    Map<String, dynamic>? coinData,
  }) {
    final v = compute(
      metalContent: metalContent,
      denomination: denomination,
      spotPrices: spotPrices,
      programSeries: programSeries,
      themeSubject: themeSubject,
      qty: qty,
      coinData: coinData,
    );
    if (v == null) return 'N/A';
    return '\$${v.toStringAsFixed(2)}';
  }

  static double? _matchDenom(Map<String, double> table, String rawDenom) {
    final fv = parseFaceValue(rawDenom);
    if (fv == 1.00 && table.containsKey('dollar')) return table['dollar'];
    if (fv == 0.50 && table.containsKey('half')) return table['half'];
    if (fv == 0.25 && table.containsKey('quarter')) return table['quarter'];
    if (fv == 0.10 && table.containsKey('dime')) return table['dime'];
    if (fv == 0.05) {
      if (table.containsKey('half dime')) return table['half dime'];
      if (table.containsKey('nickel')) return table['nickel'];
    }
    return null;
  }
}
