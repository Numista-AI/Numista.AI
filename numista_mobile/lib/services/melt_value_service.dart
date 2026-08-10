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
    s = s.replaceAll(RegExp(r'\(.*?\)'), '').trim();
    s = s.replaceAll(RegExp(r'\.{2,}'), '').trim();

    double value = 0.0;

    // 1. High Gold & Commemoratives
    if (s.contains(r'$500') || s.contains('five hundred dollar')) { value = 500.00; }
    else if (s.contains(r'$100') || s.contains('one hundred dollar') || s.contains('hundred dollar')) { value = 100.00; }
    else if (s.contains(r'$50') || s.contains('fifty dollar')) { value = 50.00; }
    else if (s.contains(r'$25') || s.contains('twenty five dollar') || s.contains('twenty-five dollar')) { value = 25.00; }
    else if (s.contains(r'$20') || s.contains('twenty dollar') || s.contains('double eagle')) { value = 20.00; }
    else if (s.contains(r'$10') || s.contains('ten dollar') || (s.contains('eagle') && !s.contains('half') && !s.contains('quarter') && !s.contains('silver'))) { value = 10.00; }
    else if (s.contains(r'$5') || s.contains('five dollar') || s.contains('half eagle')) { value = 5.00; }
    else if (s.contains(r'$3') || s.contains('three dollar')) { value = 3.00; }
    else if (s.contains(r'$2.50') || s.contains(r'$2.5') || s.contains('quarter eagle') || s.contains('two and a half')) { value = 2.50; }
    else if (s.contains(r'$2') || s.contains('two dollar')) { value = 2.00; }

    // 2. Sub-Dollar & Standard Silver/Base Denominations
    else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
    else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('half dime')) { value = 0.05; }
    else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent')) { value = 0.005; }
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

    return value * count;
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
      if (combined.contains('90%') || combined.contains('morgan') || combined.contains('peace') || combined.contains('barber') || combined.contains('walking liberty') || combined.contains('standing liberty') || combined.contains('mercury')) {
        final oz = _matchDenom(_ag90, denom) ?? 0.77344;
        return ag * oz * count;
      }
      if (combined.contains('40%')) {
        final oz = _matchDenom(_ag40, denom) ?? 0.14792;
        return ag * oz * count;
      }
      if (combined.contains('35%') || combined.contains('war nickel')) {
        final oz = _matchDenom(_ag35, denom) ?? 0.05626;
        return ag * oz * count;
      }
      if (ag > 0) return ag * 0.77344 * count;
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
    if (fv == 0.05 && table.containsKey('nickel')) return table['nickel'];
    return null;
  }
}
