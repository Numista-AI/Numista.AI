/// Centralized two-field mint helpers (`mint` facility + `mint_mark` on-coin mark).
///
/// Mirrors `numista_backend/services/mint_helpers.py` and implements the
/// dual-key reader + display rules from PLAN_TWO_FIELD_MINT_MODEL_v3.0.md.
class MintHelpers {
  static const Set<String> _dirtyPlaceholders = {
    'none',
    '(none)',
    'null',
    'n/a',
    'nan',
  };

  static const Set<String> _phillyTextAliases = {
    'nmm',
    'no mint mark',
    'philadelphia',
  };

  static const Set<String> _usCountries = {
    'usa',
    'us',
    'united states',
    '',
  };

  static final RegExp _yearRe = RegExp(r'^(\d{4})');

  /// Dual-key reader for on-coin mint mark.
  /// Priority: `mint_mark` -> `'Mint Mark'` -> `mintMark` -> `MintMark`.
  /// Sanitizes placeholder strings ("none", "(none)", "null", "n/a", "nmm",
  /// "no mint mark", "philadelphia") to "".
  static String readMintMark(Map<String, dynamic> data) {
    String raw = '';
    if (data.containsKey('mint_mark') && data['mint_mark'] != null) {
      raw = data['mint_mark'].toString().trim();
    } else {
      for (final key in const ['Mint Mark', 'mintMark', 'MintMark']) {
        final val = data[key];
        if (val != null && val.toString().trim().isNotEmpty) {
          raw = val.toString().trim();
          break;
        }
      }
    }
    if (raw.isEmpty) return '';
    final lower = raw.toLowerCase();
    if (_dirtyPlaceholders.contains(lower) || _phillyTextAliases.contains(lower)) {
      return '';
    }
    return raw.toUpperCase();
  }

  /// Dual-key reader for mint facility.
  /// Priority: `mint` -> `mint_facility` -> `Mint` -> `Mint Facility`.
  /// Returns "" if absent or placeholder.
  static String readMintFacility(Map<String, dynamic> data) {
    for (final key in const ['mint', 'mint_facility', 'Mint', 'Mint Facility']) {
      final val = data[key];
      if (val != null) {
        final s = val.toString().trim();
        if (s.isNotEmpty && !_dirtyPlaceholders.contains(s.toLowerCase())) {
          return s;
        }
      }
    }
    return '';
  }

  /// Exact programmatic implementation of Table §2.3 Rule 9 (West Point NMM).
  static bool isWestPointNmm({
    String year = '',
    String series = '',
    String denomination = '',
    String variety = '',
    String strikeType = '',
    String retailerItemNo = '',
    String country = 'United States',
  }) {
    final isUs = _usCountries.contains(country.trim().toLowerCase());
    if (!isUs) return false;

    final itemNoUpper = retailerItemNo.trim().toUpperCase();
    if (itemNoUpper == '26XE' || itemNoUpper == '26XH') {
      return true;
    }

    final yearStr = year.trim();
    final seriesOrDenomLower =
        '${series.trim().toLowerCase()} ${denomination.trim().toLowerCase()}';
    final strikeLower = strikeType.trim().toLowerCase();
    final varietyLower = variety.trim().toLowerCase();

    return yearStr == '2026' &&
        (seriesOrDenomLower.contains('morgan') ||
            seriesOrDenomLower.contains('peace')) &&
        (strikeLower.contains('enhanced') ||
            varietyLower.contains('enhanced') ||
            strikeLower == 'eu' ||
            varietyLower == 'eu');
  }

  /// Deterministic two-field mint resolver returning `(mint, mintMark, ruleId)`.
  /// Mirrors Python `resolve_two_field_mint` in `mint_helpers.py`.
  static ({String mint, String mintMark, int ruleId}) resolveTwoFieldMint({
    String rawMintMark = '',
    String rawMint = '',
    String year = '',
    String series = '',
    String denomination = '',
    String country = 'United States',
    String variety = '',
    String strikeType = '',
    String metalContent = '',
    String retailerItemNo = '',
    bool catalogPhillyNmm = false,
  }) {
    final isUs = _usCountries.contains(country.trim().toLowerCase());
    final yearMatch = _yearRe.firstMatch(year.trim());
    final intYear = yearMatch != null ? int.tryParse(yearMatch.group(1)!) : null;

    final rawMmClean = rawMintMark.trim();
    final rawMmLower = rawMmClean.toLowerCase();
    var rawMintClean = rawMint.trim();
    if (_dirtyPlaceholders.contains(rawMintClean.toLowerCase())) {
      rawMintClean = '';
    }

    String mm;
    if (_dirtyPlaceholders.contains(rawMmLower)) {
      mm = '';
    } else if (_phillyTextAliases.contains(rawMmLower)) {
      mm = '';
      if (isUs && rawMintClean.isEmpty) {
        rawMintClean = 'Philadelphia';
      }
    } else {
      mm = rawMmClean.toUpperCase();
    }

    if (isUs) {
      if (mm == 'P') return (mint: 'Philadelphia', mintMark: 'P', ruleId: 1);
      if (mm == 'D' && intYear != null && intYear >= 1838 && intYear <= 1861) {
        return (mint: 'Dahlonega', mintMark: 'D', ruleId: 2);
      }
      if (mm == 'D' && (intYear == null || intYear >= 1906)) {
        return (mint: 'Denver', mintMark: 'D', ruleId: 3);
      }
      if (mm == 'C' && intYear != null && intYear >= 1838 && intYear <= 1861) {
        return (mint: 'Charlotte', mintMark: 'C', ruleId: 4);
      }
      if (mm == 'S') return (mint: 'San Francisco', mintMark: 'S', ruleId: 5);
      if (mm == 'W') return (mint: 'West Point', mintMark: 'W', ruleId: 6);
      if (mm == 'O') return (mint: 'New Orleans', mintMark: 'O', ruleId: 7);
      if (mm == 'CC') return (mint: 'Carson City', mintMark: 'CC', ruleId: 8);
    }

    if (mm.isEmpty) {
      if (isWestPointNmm(
        year: year,
        series: series,
        denomination: denomination,
        variety: variety,
        strikeType: strikeType,
        retailerItemNo: retailerItemNo,
        country: country,
      )) {
        return (mint: 'West Point', mintMark: '', ruleId: 9);
      }

      if (isUs) {
        final seriesOrDenomLower =
            '${series.trim().toLowerCase()} ${denomination.trim().toLowerCase()}';
        final strikeLower = strikeType.trim().toLowerCase();
        final varietyLower = variety.trim().toLowerCase();
        final metalLower = metalContent.trim().toLowerCase();
        final itemNoUpper = retailerItemNo.trim().toUpperCase();

        final isWarNickelAmbiguous = intYear != null &&
            intYear >= 1942 &&
            intYear <= 1945 &&
            (seriesOrDenomLower.contains('nickel') ||
                seriesOrDenomLower.contains('jefferson') ||
                seriesOrDenomLower.contains('5c') ||
                seriesOrDenomLower.contains('5 cent')) &&
            (varietyLower.contains('war') ||
                metalLower.contains('silver') ||
                intYear >= 1943);

        final pre1980PhillyNmm =
            intYear != null && intYear <= 1979 && !isWarNickelAmbiguous;

        final strikeOrVarietyPhillyNmm =
            strikeLower.contains('reverse proof') ||
                varietyLower.contains('reverse proof') ||
                strikeLower.contains('congratulations') ||
                varietyLower.contains('congratulations') ||
                ((strikeLower == 'proof' ||
                        strikeLower == 'pr' ||
                        strikeLower == 'pf') &&
                    (intYear == null ||
                        intYear <= 1964 ||
                        itemNoUpper == '26XF' ||
                        itemNoUpper == '26XL' ||
                        itemNoUpper == '26RF'));

        final explicitPhillyFacility =
            rawMintClean.toLowerCase() == 'philadelphia';

        if (catalogPhillyNmm ||
            explicitPhillyFacility ||
            pre1980PhillyNmm ||
            strikeOrVarietyPhillyNmm) {
          return (mint: 'Philadelphia', mintMark: '', ruleId: 10);
        }
      }
    }

    return (mint: '', mintMark: mm, ruleId: 11);
  }

  /// Display formatter:
  /// - compact=true (badges/chips/table): "NMM" when mint=="Philadelphia" && mint_mark=="", else mint_mark
  /// - compact=false (detail view): "No Mint Mark" when mint=="Philadelphia" && mint_mark==""
  static String formatMintMarkForDisplay(
    String mint,
    String mintMark, {
    bool compact = false,
  }) {
    final mm = mintMark.trim().toUpperCase();
    if (mm.isNotEmpty) return mm;
    if (mint.trim().toLowerCase() == 'philadelphia') {
      return compact ? 'NMM' : 'No Mint Mark';
    }
    return '';
  }

  /// Combined facility + mark display, e.g. "Philadelphia (NMM)" or "Denver (D)".
  static String formatMintFacilityAndMark(String mint, String mintMark) {
    final facility = mint.trim();
    final mm = mintMark.trim().toUpperCase();
    if (facility.isNotEmpty && mm.isNotEmpty) {
      return '$facility ($mm)';
    }
    if (facility.toLowerCase() == 'philadelphia' && mm.isEmpty) {
      return 'Philadelphia (NMM)';
    }
    if (facility.isNotEmpty) return facility;
    return mm;
  }
}
