import 'package:flutter/foundation.dart' show debugPrint;

/// Flutter-side model for PCGS CoinFacts enrichment data.
/// Populated from the `last_report` Firestore/Flask payload after a scan.
class PCGSCoinData {
  final bool isSilver;
  final String metalContent;
  final double silverTroyOz;
  final String meltValueEstimate;
  final int? pcgsNumber;
  final Map<String, dynamic>? rawPcgsData;

  const PCGSCoinData({
    required this.isSilver,
    required this.metalContent,
    required this.silverTroyOz,
    required this.meltValueEstimate,
    this.pcgsNumber,
    this.rawPcgsData,
  });

  factory PCGSCoinData.notEnriched() => const PCGSCoinData(
        isSilver: false,
        metalContent: 'Unknown',
        silverTroyOz: 0.0,
        meltValueEstimate: '—',
      );

  factory PCGSCoinData.fromReport(Map<String, dynamic> report) {
    return PCGSCoinData(
      isSilver: report['is_silver'] as bool? ?? false,
      metalContent: report['metal_content'] as String? ?? 'Unknown',
      silverTroyOz: (report['silver_troy_oz'] as num?)?.toDouble() ?? 0.0,
      meltValueEstimate: report['melt_value_estimate'] as String? ?? '—',
      pcgsNumber: report['pcgs_number'] as int?,
      rawPcgsData: report['pcgs_data'] as Map<String, dynamic>?,
    );
  }

  // ── Derived helpers ──────────────────────────────────────────────────────────

  /// Human-readable PCGS catalog link
  String? get pcgsUrl => pcgsNumber != null
      ? 'https://www.pcgs.com/coinfacts/coin/$pcgsNumber'
      : null;

  /// Display-ready price guide from PCGS (if available)
  String? get pcgsPriceGuide {
    if (rawPcgsData == null) return null;
    final ms60 = rawPcgsData!['ms60Price'] ?? rawPcgsData!['priceGuideMs60'];
    if (ms60 != null) return 'MS60: \$${ms60.toString()}';
    return null;
  }

  /// Population report summary (if available)
  String? get populationSummary {
    if (rawPcgsData == null) return null;
    final pop = rawPcgsData!['population'] ?? rawPcgsData!['popTotal'];
    if (pop != null) return 'PCGS Pop: ${pop.toString()} graded';
    return null;
  }
}

/// Service class — currently thin (enrichment happens on the Python side).
/// Reserved for future direct Flutter → PCGS API calls (e.g., cert lookups
/// entered manually by the user from the UI).
class PCGSService {
  // Future: endpoint + token will be wired here for direct cert lookups
  // static const String _pcgsBase = 'https://api.pcgs.com/publicapi';

  /// Parses raw scan report data into a structured PCGSCoinData object.
  static PCGSCoinData parseFromReport(Map<String, dynamic>? report) {
    if (report == null) return PCGSCoinData.notEnriched();
    debugPrint('[PCGS] Parsing report: ${report.keys.join(', ')}');
    return PCGSCoinData.fromReport(report);
  }

  /// Quick silver check from a coin's year and denomination string alone.
  /// Used as a fast UI pre-check before the PCGS API call completes.
  static bool quickSilverCheck(int? year, String denomination) {
    if (year == null) return false;
    final denom = denomination.toLowerCase();

    // Dimes, quarters, halves pre-1965 = 90% silver
    if ((denom.contains('dime') || denom.contains('10')) && year < 1965) return true;
    if ((denom.contains('quarter') || denom.contains('25')) && year < 1965) return true;
    if ((denom.contains('half') || denom.contains('50')) && year < 1965) return true;

    // Halves 1965-1970 = 40% silver (still silver!)
    if ((denom.contains('half') || denom.contains('50')) && year >= 1965 && year <= 1970) return true;

    // Silver Eagles (all years)
    if (denom.contains('silver eagle') || denom.contains('eagle')) return true;

    // Silver Dollars (Morgan, Peace, etc. — pre-1936)
    if ((denom.contains('dollar') || denom.contains('\$1')) && year < 1936) return true;

    return false;
  }
}
