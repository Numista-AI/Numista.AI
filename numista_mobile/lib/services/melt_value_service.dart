/// melt_value_service.dart
///
/// Calculates real-time melt value for a coin given:
///   - its standardized [metalContent] field (written by migrate_precious_metal.py)
///   - its [denomination] string
///   - a [spotPrices] map with keys 'Gold', 'Silver', 'Platinum', 'Palladium'
///     (price per troy oz, fetched by the dashboard from /api/spot_prices)
///
/// Returns the melt value in USD, or null if the coin has no precious metal content
/// worth calculating (e.g. modern clad coins, zinc pennies).
///
/// All silver weights are in troy oz of PURE silver per coin (Ag).
/// All gold weights are in troy oz of PURE gold per coin (Au).

class MeltValueService {
  // ── Silver (Ag) troy oz per coin by denomination ───────────────────────────
  // Source: US Mint specifications + standard numismatic references.
  static const _ag90 = {
    // 90% Silver series (pre-1965)
    'dime':        0.07234,   // 2.5g × 90% = 2.25g Ag ÷ 31.1035
    'quarter':     0.18084,   // 6.25g × 90% = 5.625g Ag ÷ 31.1035
    'half':        0.36169,   // 12.5g × 90% = 11.25g Ag ÷ 31.1035
    'half dollar': 0.36169,
    'dollar':      0.77344,   // Morgan / Peace: 26.73g × 90% ÷ 31.1035
  };

  static const _ag40 = {
    // 40% Silver Kennedy Halves (1965-1970)
    'half':        0.14792,   // 11.5g × 40% ÷ 31.1035
    'half dollar': 0.14792,
  };

  static const _ag35 = {
    // 35% Silver War Nickels (1942-1945, P-mint only)
    'nickel': 0.05626,        // 5.0g × 35% ÷ 31.1035
  };

  // American Silver Eagle: 1 troy oz Ag (999 fine)
  static const double _silverEagleOz = 1.0;

  // ── Gold (Au) troy oz per coin by face value ───────────────────────────────
  // Pre-1933 US Gold: 90% gold by weight.
  static final _au90ByFaceValue = {
    1.0:  0.04837,   // $1 gold piece
    2.5:  0.12094,   // Quarter Eagle
    3.0:  0.14513,   // $3 gold piece
    5.0:  0.24188,   // Half Eagle
    10.0: 0.48375,   // Eagle
    20.0: 0.96750,   // Double Eagle (most common)
  };

  // American Gold Eagles: 91.67% gold, stated in pure Au oz on the coin.
  static final _au9167ByFaceValue = {
    5.0:  0.10,   // 1/10 oz face=$5
    10.0: 0.25,   // 1/4 oz  face=$10
    25.0: 0.50,   // 1/2 oz  face=$25
    50.0: 1.00,   // 1 oz    face=$50
  };

  // American Gold Buffalo: 99.99% gold, 1 oz.
  static const double _buffaloAuOz = 1.0;

  // ── Public API ─────────────────────────────────────────────────────────────

  /// Returns melt value in dollars, or null for base-metal / unknown coins.
  ///
  /// [metalContent]  — standardised string from the 'Metal Content' Firestore field.
  /// [denomination]  — raw denomination string from Firestore.
  /// [spotPrices]    — {'Gold': 4647.50, 'Silver': 76.45, ...}
  static double? compute({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
  }) {
    final mc    = metalContent.trim().toLowerCase();
    final denom = denomination.trim().toLowerCase();
    final ag    = spotPrices['Silver'] ?? 0;
    final au    = spotPrices['Gold']   ?? 0;

    if (ag == 0 && au == 0) return null;

    // ── Silver Eagles ────────────────────────────────────────────────────────
    if (mc.contains('silver (99') || mc.contains('silver (999')) {
      return ag * _silverEagleOz;
    }

    // ── 90% Silver ───────────────────────────────────────────────────────────
    if (mc.startsWith('90% silver')) {
      final oz = _matchDenom(_ag90, denom);
      if (oz != null) return ag * oz;
    }

    // ── 40% Silver ───────────────────────────────────────────────────────────
    if (mc.startsWith('40% silver')) {
      final oz = _matchDenom(_ag40, denom);
      if (oz != null) return ag * oz;
    }

    // ── 35% Silver (War Nickels) ─────────────────────────────────────────────
    if (mc.startsWith('35% silver')) {
      final oz = _matchDenom(_ag35, denom);
      if (oz != null) return ag * oz;
    }

    // ── American Gold Buffalo (99.99%) ────────────────────────────────────────
    if (mc.contains('99.99') && mc.contains('gold')) {
      return au * _buffaloAuOz;
    }

    // ── American Gold Eagles (91.67%) ─────────────────────────────────────────
    if (mc.contains('91.67') && mc.contains('gold')) {
      final fv = _parseFaceValue(denom);
      if (fv != null) {
        final oz = _au9167ByFaceValue[fv];
        if (oz != null) return au * oz;
        // Fallback: treat as 1 oz if denomination is $50 or unknown high value
        return au * 1.0;
      }
    }

    // ── Pre-1933 Gold (90%) ───────────────────────────────────────────────────
    if (mc.contains('gold (90%)') || mc.contains('gold (90%')) {
      final fv = _parseFaceValue(denom);
      if (fv != null) {
        final oz = _au90ByFaceValue[fv];
        if (oz != null) return au * oz;
        // Fallback to Double Eagle weight for unrecognised large gold coins
        return au * _au90ByFaceValue[20.0]!;
      }
    }

    // ── Copper / Clad coins — return null (effectively zero precious value) ──
    // Copper melt is < face value; not meaningful for collection display.
    return null;
  }

  /// Formatted melt value string. Returns 'N/A' for non-precious coins.
  static String format({
    required String metalContent,
    required String denomination,
    required Map<String, double> spotPrices,
  }) {
    final v = compute(
      metalContent: metalContent,
      denomination: denomination,
      spotPrices: spotPrices,
    );
    if (v == null) return 'N/A';
    return '\$${v.toStringAsFixed(2)}';
  }

  /// Returns the silver troy oz for a precious-metal coin, or null.
  /// Used for display in the Coin Inspector detail panel.
  static double? silverTroyOz({
    required String metalContent,
    required String denomination,
  }) {
    final mc    = metalContent.trim().toLowerCase();
    final denom = denomination.trim().toLowerCase();

    if (mc.contains('silver (99')) return _silverEagleOz;
    if (mc.startsWith('90% silver')) return _matchDenom(_ag90, denom);
    if (mc.startsWith('40% silver')) return _matchDenom(_ag40, denom);
    if (mc.startsWith('35% silver')) return _matchDenom(_ag35, denom);
    return null;
  }

  // ── Private helpers ────────────────────────────────────────────────────────

  static double? _matchDenom(Map<String, double> table, String denom) {
    for (final entry in table.entries) {
      if (denom.contains(entry.key)) return entry.value;
    }
    return null;
  }

  static double? _parseFaceValue(String denom) {
    // Try "$20", "20", "20.0", "double eagle", etc.
    final cleaned = denom
        .replaceAll(RegExp(r'[^\d.]'), ' ')
        .trim();
    final parts = cleaned
        .split(RegExp(r'\s+'))
        .map((s) => double.tryParse(s))
        .whereType<double>()
        .toList();
    if (parts.isEmpty) return null;
    return parts.reduce((a, b) => a > b ? a : b); // largest numeric = face value
  }
}
