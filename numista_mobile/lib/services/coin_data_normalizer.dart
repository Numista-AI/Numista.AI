import '../constants/denomination_canon.dart';
import '../models/coin_model.dart';
import '../widgets/collection_card_valuation_row.dart';

/// Deterministic client-side normalizer for US Mint denominations, metal typos,
/// historical US Mint silver compositions, condition slang, classic series
/// inference, and bogus `$0.00` AI estimate cleanup.
class CoinDataNormalizer {
  static const Map<String, String> _metalWordTypos = {
    'silve': 'Silver',
    'sliver': 'Silver',
    'silvr': 'Silver',
    'siver': 'Silver',
    'silv': 'Silver',
    'ag': 'Silver',
    'gol': 'Gold',
    'gld': 'Gold',
    'godl': 'Gold',
    'au': 'Gold',
    'platnium': 'Platinum',
    'platnum': 'Platinum',
    'pt': 'Platinum',
    'coper': 'Copper',
    'coppr': 'Copper',
    'cu': 'Copper',
    'nickle': 'Nickel',
    'cupronickle': 'Cupro-Nickel Clad',
    'cupronickel': 'Cupro-Nickel Clad',
  };

  static const Set<String> _protectedBaseMetalPhrases = {
    'nickel silver',
    'german silver',
    'cupro-nickel',
    'cupronickel',
    'silver plated',
    'silver-plated',
    'gold plated',
    'gold-plated',
    'platinum plated',
    'platinum-plated',
  };

  static const Set<String> _placeholderSeries = {
    '',
    'general item',
    'standard circulation',
    'none',
    'n/a',
    'unknown',
    'other',
  };

  static final RegExp _sheldonOrSlabGradeRe = RegExp(
    r'^(?:PF|PR|MS|AU|XF|EF|VF|F|VG|G|AG|FR|PO)\s*[- ]?\s*\d{1,2}\b',
    caseSensitive: false,
  );

  static bool isZeroOrInvalidAiEstimate(dynamic raw) {
    if (raw == null) return true;
    final trimmed = raw.toString().trim();
    if (trimmed.isEmpty) return true;
    final lower = trimmed.toLowerCase();
    if (lower == 'pending' ||
        lower == 'valuation pending' ||
        lower == 'null' ||
        lower == 'none' ||
        lower == 'nan' ||
        trimmed == '—' ||
        trimmed == '-') {
      return true;
    }
    final numericMatch =
        RegExp(r'^\$?\s*(\d+(?:,\d{3})*(?:\.\d+)?)$').firstMatch(trimmed);
    if (numericMatch != null) {
      final parsed =
          double.tryParse(numericMatch.group(1)!.replaceAll(',', '')) ?? 0.0;
      return parsed <= 0.0;
    }
    return false;
  }

  static bool isUsCoinMap(Map<String, dynamic> data) {
    final itemType =
        (data['item_type'] ?? data['Item Type'] ?? '').toString().toLowerCase();
    if (itemType.contains('paper') || itemType == 'banknote') return false;
    return CollectionCardValuationRow.isUsOrigin(data);
  }

  static int? _parseYearInt(String? rawYear) {
    if (rawYear == null) return null;
    final m = RegExp(r'\b(1[7-9]\d{2}|20\d{2})\b').firstMatch(rawYear.trim());
    if (m != null) return int.tryParse(m.group(1)!);
    return int.tryParse(rawYear.replaceAll(RegExp(r'\.0+$'), '').trim());
  }

  /// Normalizes metal composition typos (`Silve` -> `Silver`) and enriches
  /// historical US Mint silver compositions when applicable.
  /// Never promotes plated or base-metal alloys (`Nickel Silver`, `Silver Plated`).
  static String normalizeMetal(
    String? raw, {
    String? year,
    String? canonicalDenom,
    bool isUsCoin = true,
  }) {
    final trimmed = (raw ?? '').trim();
    final lower = trimmed.toLowerCase();

    for (final phrase in _protectedBaseMetalPhrases) {
      if (lower.contains(phrase)) {
        return trimmed;
      }
    }

    String cleaned = trimmed;
    if (lower == 'clad') {
      cleaned = 'Cupro-Nickel Clad';
    } else if (_metalWordTypos.containsKey(lower)) {
      cleaned = _metalWordTypos[lower]!;
    } else if (cleaned.isNotEmpty) {
      cleaned = cleaned.replaceAllMapped(
        RegExp(r'\b[A-Za-z]+\b'),
        (m) => _metalWordTypos[m.group(0)!.toLowerCase()] ?? m.group(0)!,
      );
      if (cleaned.toLowerCase() == 'silver') {
        cleaned = 'Silver';
      } else if (cleaned.toLowerCase() == 'gold') {
        cleaned = 'Gold';
      } else if (cleaned.toLowerCase() == 'platinum') {
        cleaned = 'Platinum';
      }
    }

    final yr = _parseYearInt(year);
    final cLower = cleaned.toLowerCase();
    final isBareOrEmptySilver = cLower.isEmpty ||
        cLower == 'pending' ||
        cLower == 'unknown' ||
        cLower == 'silver';

    if (isUsCoin && yr != null && canonicalDenom != null) {
      final isPre1965SilverDenom = canonicalDenom == DenominationCanon.dime ||
          canonicalDenom == DenominationCanon.quarterDollar ||
          canonicalDenom == DenominationCanon.halfDollar;
      if (yr <= 1964 && isPre1965SilverDenom && isBareOrEmptySilver) {
        return '90% Silver, 10% Copper';
      }
      if (yr >= 1965 &&
          yr <= 1970 &&
          canonicalDenom == DenominationCanon.halfDollar &&
          cLower == 'silver') {
        return '40% Silver, 60% Copper';
      }
      if (yr >= 1942 &&
          yr <= 1945 &&
          canonicalDenom == DenominationCanon.fiveCents &&
          cLower == 'silver') {
        return '35% Silver, 56% Copper, 9% Manganese';
      }
    }

    return cleaned;
  }

  /// Normalizes colloquial condition words (`shiny` -> `Uncirculated`) while
  /// leaving numeric Sheldon / certified slab grades intact.
  static String normalizeCondition(String? raw) {
    final trimmed = (raw ?? '').trim();
    if (trimmed.isEmpty) return '';
    if (_sheldonOrSlabGradeRe.hasMatch(trimmed) ||
        trimmed.toLowerCase().contains('details')) {
      return trimmed;
    }
    switch (trimmed.toLowerCase()) {
      case 'shiny':
      case 'bright':
      case 'mint':
      case 'bu':
      case 'brilliant uncirculated':
        return 'Uncirculated';
      case 'worn':
      case 'heavily circulated':
        return 'Circulated';
      default:
        return trimmed;
    }
  }

  /// Infers classic US Mint series when `Program/Series` is missing or generic
  /// (e.g., `'Standard Circulation'`, `'General Item'`).
  static String inferClassicUsSeries({
    required String year,
    required String canonicalDenom,
    required String existingSeries,
    required bool isUsCoin,
  }) {
    final trimmedSeries = existingSeries.trim();
    if (!isUsCoin) return trimmedSeries;
    if (!_placeholderSeries.contains(trimmedSeries.toLowerCase())) {
      return trimmedSeries;
    }

    final yr = _parseYearInt(year);
    if (yr == null) return trimmedSeries;

    switch (canonicalDenom) {
      case DenominationCanon.quarterDollar:
        if (yr >= 1932 && yr <= 1998) return 'Washington Quarters';
        if (yr >= 1916 && yr <= 1930) return 'Standing Liberty Quarters';
        if (yr >= 1892 && yr <= 1916) return 'Barber Quarters';
        break;
      case DenominationCanon.dime:
        if (yr >= 1946) return 'Roosevelt Dimes';
        if (yr >= 1916 && yr <= 1945) return 'Mercury Dimes';
        if (yr >= 1892 && yr <= 1916) return 'Barber Dimes';
        break;
      case DenominationCanon.halfDollar:
        if (yr >= 1964) return 'Kennedy Half Dollars';
        if (yr >= 1948 && yr <= 1963) return 'Franklin Half Dollars';
        if (yr >= 1916 && yr <= 1947) return 'Walking Liberty Half Dollars';
        break;
      case DenominationCanon.fiveCents:
        if (yr >= 1938) return 'Jefferson Nickels';
        if (yr >= 1913 && yr <= 1938) return 'Buffalo Nickels';
        if (yr >= 1883 && yr <= 1912) return 'Liberty Head Nickels';
        break;
      case DenominationCanon.cent:
        if (yr >= 2010) return 'Lincoln Shield Cents';
        if (yr >= 1959 && yr <= 2008) return 'Lincoln Memorial Cents';
        if (yr >= 1909 && yr <= 1958) return 'Lincoln Wheat Cents';
        if (yr >= 1859 && yr <= 1909) return 'Indian Head Cents';
        break;
      case DenominationCanon.dollar:
        if (yr >= 1921 && yr <= 1935) return 'Peace Dollars';
        if (yr >= 1878 && yr <= 1921) return 'Morgan Dollars';
        if (yr >= 1971 && yr <= 1978) return 'Eisenhower Dollars';
        break;
    }
    return trimmedSeries;
  }

  /// Normalizes a coin payload (save, edit, or retroactive cleanup).
  /// When [recordRawAudit] is true, stores pre-cleanup values in `_raw_*` keys.
  static Map<String, dynamic> normalizeCoinMap(
    Map<String, dynamic> input, {
    bool recordRawAudit = false,
  }) {
    final out = Map<String, dynamic>.from(input);
    final isUs = isUsCoinMap(out);
    final itemType =
        (out['item_type'] ?? out['Item Type'] ?? '').toString().trim();
    final country = (out['Country'] ?? out['country'] ?? '').toString().trim();
    final isForeign = out['is_foreign'] == true || !isUs;
    final rawYear = (out['Year'] ?? out['year'] ?? '').toString().trim();

    // 1. Denomination
    final rawDenom =
        (out['Denomination'] ?? out['denomination'] ?? '').toString().trim();
    final normDenom = DenominationCanon.normalize(
      rawDenom,
      country: country,
      itemType: itemType,
      isForeign: isForeign,
    );
    if (normDenom.isNotEmpty) {
      if (recordRawAudit &&
          rawDenom.isNotEmpty &&
          normDenom != rawDenom &&
          !out.containsKey('_raw_denomination')) {
        out['_raw_denomination'] = rawDenom;
      }
      if (out.containsKey('Denomination') || !out.containsKey('denomination')) {
        out['Denomination'] = normDenom;
      }
      if (out.containsKey('denomination')) {
        out['denomination'] = normDenom;
      }
    }

    // 2. Metal Content
    final rawMetal =
        (out['Metal Content'] ?? out['metalContent'] ?? out['metal_content'] ?? '')
            .toString()
            .trim();
    final normMetal = normalizeMetal(
      rawMetal,
      year: rawYear,
      canonicalDenom: normDenom,
      isUsCoin: isUs,
    );
    if (normMetal.isNotEmpty && normMetal != rawMetal) {
      if (recordRawAudit &&
          rawMetal.isNotEmpty &&
          !out.containsKey('_raw_metal_content')) {
        out['_raw_metal_content'] = rawMetal;
      }
      if (out.containsKey('Metal Content') ||
          (!out.containsKey('metalContent') && !out.containsKey('metal_content'))) {
        out['Metal Content'] = normMetal;
      }
      if (out.containsKey('metalContent')) out['metalContent'] = normMetal;
      if (out.containsKey('metal_content')) out['metal_content'] = normMetal;
    }

    // 3. Classic Series inference
    final rawSeries =
        (out['Program/Series'] ?? out['program_series'] ?? out['programSeries'] ?? '')
            .toString()
            .trim();
    final normSeries = inferClassicUsSeries(
      year: rawYear,
      canonicalDenom: normDenom,
      existingSeries: rawSeries,
      isUsCoin: isUs,
    );
    if (normSeries.isNotEmpty && normSeries != rawSeries) {
      if (out.containsKey('Program/Series') || !out.containsKey('program_series')) {
        out['Program/Series'] = normSeries;
      }
      if (out.containsKey('program_series')) {
        out['program_series'] = normSeries;
      }
    }

    // 4. Condition slang
    final rawCond =
        (out['Condition'] ?? out['condition'] ?? '').toString().trim();
    final normCond = normalizeCondition(rawCond);
    if (normCond.isNotEmpty && normCond != rawCond) {
      if (out.containsKey('Condition') || !out.containsKey('condition')) {
        out['Condition'] = normCond;
      }
      if (out.containsKey('condition')) out['condition'] = normCond;
    }

    // 5. Clear bogus "$0.00" / "0" AI Estimated Value sentinels
    final aiUpper = out['AI Estimated Value'];
    final aiLower = out['ai_estimated_value'];
    final estNum = out['estimated_value'];
    var clearedBogusValue = false;
    if (aiUpper != null &&
        aiUpper.toString().trim().isNotEmpty &&
        aiUpper.toString().trim() != 'Pending' &&
        isZeroOrInvalidAiEstimate(aiUpper)) {
      out['AI Estimated Value'] = 'Pending';
      clearedBogusValue = true;
    }
    if (aiLower != null &&
        aiLower.toString().trim().isNotEmpty &&
        aiLower.toString().trim() != 'Pending' &&
        isZeroOrInvalidAiEstimate(aiLower)) {
      out['ai_estimated_value'] = 'Pending';
      clearedBogusValue = true;
    }
    if (estNum != null && estNum is num && estNum <= 0) {
      out.remove('estimated_value');
      clearedBogusValue = true;
    }
    if (clearedBogusValue &&
        out['ai_value_status']?.toString().toLowerCase() == 'valued') {
      out['ai_value_status'] = 'pending';
    }

    // 6. Heal stale verify_link on certified coins
    final cert = (out['Certification Number'] ??
            out['certificationNumber'] ??
            out['cert_number'] ??
            out['Cert #'] ??
            out['certNo'] ??
            '')
        .toString()
        .trim();
    final grader = (out['Grading Service'] ??
            out['gradingService'] ??
            out['grading_service'] ??
            out['grader'] ??
            '')
        .toString()
        .trim();
    final holder = (out['Holder Type'] ?? out['holderType'] ?? '').toString().trim();
    final expectedVerifyUrl = CoinModel.buildVerificationUrl(
      certificationNumber: cert,
      gradingService: grader,
      holderType: holder,
      condition: normCond.isNotEmpty ? normCond : rawCond,
      hasCac: (out['cac_premium_flag'] == true) || (out['hasCac'] == true),
    );
    final existingVerifyLink = (out['verify_link'] ?? '').toString().trim();
    if (expectedVerifyUrl != null &&
        existingVerifyLink != expectedVerifyUrl) {
      if (recordRawAudit &&
          existingVerifyLink.isNotEmpty &&
          !out.containsKey('_raw_verify_link')) {
        out['_raw_verify_link'] = existingVerifyLink;
      }
      out['verify_link'] = expectedVerifyUrl;
    }

    return out;
  }

  /// Computes a minimal Firestore update map for idempotent `_norm_v2` cleanup.
  /// Always includes `'_norm_v2': true` plus any normalized field deltas.
  static Map<String, dynamic> computeNormV2Patch(Map<String, dynamic> input) {
    final normalized = normalizeCoinMap(input, recordRawAudit: true);
    final patch = <String, dynamic>{'_norm_v2': true};
    for (final entry in normalized.entries) {
      if (input[entry.key] != entry.value) {
        patch[entry.key] = entry.value;
      }
    }
    return patch;
  }

  /// Returns true when the coin lacks both a valid positive AI estimate and CPG retail.
  static bool needsValuation(Map<String, dynamic> data) {
    final cpg = data['cpg_retail'] ?? data['cpgRetail'];
    if (!isZeroOrInvalidAiEstimate(cpg)) return false;
    final aiVal = data['AI Estimated Value'] ??
        data['ai_estimated_value'] ??
        data['estimated_value'];
    return isZeroOrInvalidAiEstimate(aiVal);
  }
}
