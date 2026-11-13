class CanonicalMintAssetPair {
  final String sku;
  final String obverseUrl;
  final String reverseUrl;
  final String? fallbackObverseUrl;
  final String? fallbackReverseUrl;
  final bool isSet;
  final bool isGenuine2026;
  final bool isRepresentativePreview;

  const CanonicalMintAssetPair({
    required this.sku,
    required this.obverseUrl,
    required this.reverseUrl,
    this.fallbackObverseUrl,
    this.fallbackReverseUrl,
    this.isSet = false,
    this.isGenuine2026 = false,
    this.isRepresentativePreview = false,
  }) : assert(obverseUrl != reverseUrl, 'Obverse and reverse URLs must be distinct');
}

class CanonicalMintAssetService {
  /// MF-B User Upload Guard: Never overwrite user-uploaded photos or microscope scans.
  /// If existing stored images are user uploads (under uploads bucket or /microscope/),
  /// or scan_source is microscope / hardware agent, return true to preserve existing.
  static bool hasUserUploadedPhotos(Map<String, dynamic> data) {
    final scanSource = (data['scan_source'] ?? data['source'] ?? '').toString().toLowerCase();
    if (scanSource == 'microscope' || scanSource == 'hardware agent') return true;

    bool isUserUrl(dynamic val) {
      if (val == null) return false;
      final s = val.toString().trim().toLowerCase();
      if (s.isEmpty) return false;
      if (s.contains('/reference_images/') || s.contains('reference_library')) return false;
      return s.contains('/microscope/') ||
             s.contains('studio-9101802118-8c9a8-uploads') ||
             s.contains('numista-uploads-studio-') ||
             s.contains('/users/') ||
             s.contains('/user_uploads/') ||
             s.contains('user_upload');
    }

    return isUserUrl(data['image_url_obverse']) ||
           isUserUrl(data['image_url_reverse']) ||
           isUserUrl(data['imageObverse']) ||
           isUserUrl(data['imageReverse']) ||
           isUserUrl(data['stored_obv']) ||
           isUserUrl(data['stored_rev']);
  }

  static const String _base =
      'https://storage.googleapis.com/numista-reference-library/reference_library';
  static const String _mintBase = '$_base/us_mint_official';
  static const String _wikiBase = '$_base/wikimedia_uscoin';

  static const List<String> _knownSkus = <String>[
    '26EA',
    '26XE',
    '26XL',
    '26XH',
    '26XF',
    '26RJ',
    '26GC',
    '26SQRP',
    '26RG',
    '23RG',
    '26RH',
    '23RH',
  ];

  static String _normYear(Object? y) {
    final s = (y ?? '').toString().trim();
    final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
    return m != null ? m.group(1)! : s;
  }

  /// MF-C7: Extracts normalized 4-digit canonical year from coin metadata.
  /// Strictly additive at line 77. Leaves resolveFromMap completely unchanged.
  /// Intentionally excludes Personal Notes to prevent neighbor note bleed.
  static String canonicalYear(Map<String, dynamic> data) {
    for (final k in const <String>[
      'year',
      'Year',
      'coin_year',
      'canonical_year',
      'issue_year',
      'mintDate',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString().trim();
        if (s.isNotEmpty) {
          final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
          if (dualMatch != null) return dualMatch.group(1)!;

          final norm = _normYear(s);
          if (RegExp(r'^\d{4}$').hasMatch(norm)) return norm;
        }
      }
    }

    for (final k in const <String>[
      'title',
      'name',
      'Theme/Subject',
      'theme_subject',
      'Program/Series',
      'program_series',
      'description',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString();
        final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
        if (dualMatch != null) return dualMatch.group(1)!;

        final m = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(s);
        if (m != null) return m.group(1)!;
      }
    }

    return '';
  }

  static String extractSku(Map<String, dynamic> data) {
    for (final k in const <String>[
      'mint_product_id',
      'sku',
      'product_code',
      'item_number',
      'Retailer Item No.',
      'retailer_item_no',
      'retailer_item_num',
    ]) {
      final val = (data[k] ?? '').toString().trim().toUpperCase();
      if (_knownSkus.contains(val)) return val;
    }
    for (final k in const <String>[
      'Personal Notes',
      'personal_notes',
      'title',
      'name',
      'Theme/Subject',
      'Program/Series',
      'Program / Series',
      'program_series',
    ]) {
      final txt = (data[k] ?? '').toString().toUpperCase();
      final tokens = txt.replaceAll('#', ' ').replaceAll('-', ' ').split(RegExp(r'\s+'));
      for (final candidate in _knownSkus) {
        if (tokens.contains(candidate)) return candidate;
      }
    }
    final year = _normYear(data['year'] ?? data['Year']);
    final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
    final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
    final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
    final cond = <Object?>[
      data['Condition'], data['condition'],
      data['Variety'], data['variety'],
      data['Strike Type'], data['strike_type'],
      data['Denomination'], data['denomination'],
    ].where((v) => v != null).map((v) => v.toString().toLowerCase()).join(' ');
    final combined = '$prog $theme $title $cond';
    if (year == '2026' &&
        RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
        !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
      return '26EA';
    }
    if (year == '2026') {
      if (combined.contains('morgan') && combined.contains('enhanced')) return '26XE';
      if (combined.contains('morgan') && combined.contains('proof')) return '26XF';
      if (combined.contains('peace') && combined.contains('reverse proof')) return '26XL';
      if (combined.contains('peace') && combined.contains('uncirculated')) return '26XH';
      if (combined.contains('uncirculated') && combined.contains('set')) return '26RJ';
      if (combined.contains('american innovation')) return '26GC';
      if (combined.contains('trump') || combined.contains('semiquincentennial president')) {
        return '26SQRP';
      }
      if (combined.contains('silver proof set')) return '26RH';
      if (combined.contains('clad proof set') ||
          (combined.contains('proof set') && !combined.contains('silver'))) {
        return '26RG';
      }
    }
    if (year == '2023') {
      if (combined.contains('silver proof set')) return '23RH';
      if (combined.contains('proof set')) return '23RG';
    }
    return (data['mint_product_id'] ??
            data['sku'] ??
            data['product_code'] ??
            data['Retailer Item No.'] ??
            '')
        .toString()
        .trim()
        .toUpperCase();
  }

  static CanonicalMintAssetPair? resolveFromMap(Map<String, dynamic> data) {
    // MF-B Guard: Non-destructive preservation of user-uploaded / microscope photos.
    // If doc contains user uploads (e.g. Row 10 Eric's microscope photos), return null.
    if (hasUserUploadedPhotos(data)) {
      return null;
    }
    final sku = extractSku(data);
    // Intentionally excludes `Personal Notes` so neighbor-coin notes in live Firestore
    // never hijack ATB/State quarter identification.
    final primaryTitle = <String>[
      (data['title'] ?? '').toString().trim(),
      (data['name'] ?? '').toString().trim(),
      (data['Theme/Subject'] ?? '').toString().trim(),
      (data['theme_subject'] ?? '').toString().trim(),
      (data['Program / Series'] ?? data['Program/Series'] ?? '').toString().trim(),
      (data['program_series'] ?? '').toString().trim(),
      (data['description'] ?? '').toString().trim(),
    ].where((s) => s.isNotEmpty).join(' ');

    final year = _normYear(data['year'] ?? data['Year']);
    final mintMark =
        (data['mint_mark'] ?? data['mint'] ?? data['Mint Mark'] ?? '').toString().trim();
    final denom =
        (data['denomination'] ?? data['Denomination'] ?? '').toString().trim();
    final storedObv =
        (data['image_url_obverse'] ?? data['obverse_image'] ?? data['image_url'] ?? '')
            .toString()
            .trim();

    return resolve(
      sku: sku,
      title: primaryTitle,
      year: year,
      mintMark: mintMark,
      denomination: denom,
      storedObverseUrl: storedObv.isNotEmpty ? storedObv : null,
    );
  }

  static CanonicalMintAssetPair? resolve({
    String? sku,
    String? title,
    String? year,
    String? mintMark,
    String? denomination,
    String? storedObverseUrl,
  }) {
    final cleanTitle = (title ?? '').trim().toLowerCase();
    final cleanYear = _normYear(year);
    final rawMint = (mintMark ?? '').trim().toUpperCase();
    final cleanDenom = (denomination ?? '').trim().toLowerCase();
    final cleanMint = rawMint.contains('WEST POINT') || rawMint == 'W'
        ? 'W'
        : (rawMint.contains('S')
            ? 'S'
            : (rawMint.contains('D')
                ? 'D'
                : (rawMint.contains('P') ? 'P' : rawMint)));

    final rawSku = (sku ?? '').trim().toUpperCase();
    final cleanSku = rawSku.isNotEmpty
        ? rawSku
        : extractSku(<String, dynamic>{
            'year': cleanYear,
            'title': cleanTitle,
            'denomination': cleanDenom,
            'mint_mark': cleanMint,
          });

    // 1. Exact / Inferred SKU Match
    switch (cleanSku) {
      case '26EA':
        return const CanonicalMintAssetPair(
          sku: '26EA',
          obverseUrl: '$_mintBase/2026_products/26EA_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26EA_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26ea_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26ea_b.webp',
          isSet: false,
          isGenuine2026: true,
        );
      case '26XE':
        return const CanonicalMintAssetPair(
          sku: '26XE',
          obverseUrl: '$_mintBase/2026_products/26XE_image_2.jpg',
          reverseUrl: '$_mintBase/2026_products/26XE_image_3.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26xe_a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26xe_b.webp',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XL':
        return const CanonicalMintAssetPair(
          sku: '26XL',
          obverseUrl: '$_mintBase/2026_products/26XL_image_3.jpg',
          reverseUrl: '$_mintBase/2026_products/26XL_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26xl___a.webp',
          fallbackReverseUrl: '$_mintBase/2026_products/26XL_image_1.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XH':
        return const CanonicalMintAssetPair(
          sku: '26XH',
          obverseUrl: '$_mintBase/2026_products/26XH_image_2.jpg',
          reverseUrl: '$_mintBase/2026_products/26XH_image_3.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26XH_image_1.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26xh_image_3.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26XF':
        return const CanonicalMintAssetPair(
          sku: '26XF',
          obverseUrl: '$_mintBase/2026_products/26XF_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26XF_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26XE_image_2.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26XE_image_3.jpg',
          isSet: false,
          isRepresentativePreview: true,
        );
      case '26RJ':
        return const CanonicalMintAssetPair(
          sku: '26RJ',
          obverseUrl:
              '$_base/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_e.jpg',
          reverseUrl:
              '$_base/user_contributed/coin_sets/uncirculated-coin-set-2026/26rj_b.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26RJ_image_1.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26RJ_image_2.jpg',
          isSet: true,
          isGenuine2026: true,
        );
      case '26GC':
        return const CanonicalMintAssetPair(
          sku: '26GC',
          obverseUrl: '$_mintBase/2026_products/26GC_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26gc_b.webp',
          fallbackObverseUrl: '$_base/2026_series/2026_american_innovation_obverse.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26GC_image_2.jpg',
          isSet: true,
          isGenuine2026: true,
        );
      case '26SQRP':
        return const CanonicalMintAssetPair(
          sku: '26SQRP',
          obverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26sqrp_b.webp',
          fallbackObverseUrl: '$_mintBase/2026_products/MASTER_SEMIQDJT_image_2.jpg',
          fallbackReverseUrl: null,
          isSet: true,
          isGenuine2026: true,
        );
      case '26RG':
      case '23RG':
        return CanonicalMintAssetPair(
          sku: cleanSku,
          obverseUrl: '$_mintBase/2026_products/26RG_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26rg_b.webp',
          fallbackObverseUrl: '$_mintBase/2026_products/26RG_image_2.jpg',
          fallbackReverseUrl: '$_mintBase/2026_products/26RG_image_3.jpg',
          isSet: true,
          isRepresentativePreview: true,
        );
      case '26RH':
        return const CanonicalMintAssetPair(
          sku: '26RH',
          obverseUrl: '$_mintBase/2026_products/26RH_image_1.jpg',
          reverseUrl: '$_mintBase/2026_products/26RH_image_2.jpg',
          fallbackObverseUrl: '$_mintBase/2026_products/26RH_image_3.jpg',
          fallbackReverseUrl: null,
          isSet: true,
          isRepresentativePreview: true,
        );
      case '23RH':
        return const CanonicalMintAssetPair(
          sku: '23RH',
          obverseUrl:
              '$_base/2023_series/2023_american_women_quarters_five_honorees_composite.jpg',
          reverseUrl:
              '$_base/2023_series/2023_american_innovation_four_states_composite.jpg',
          fallbackObverseUrl: '$_mintBase/2023_products/23rh_b.webp',
          fallbackReverseUrl: '$_mintBase/2023_products/23rh_c.webp',
          isSet: true,
        );
    }

    // 2. 2026 Semiquincentennial Individual Coin Match (Rows 08–11)
    if (cleanYear == '2026') {
      if (cleanTitle.contains('roosevelt') ||
          cleanTitle.contains('dime') ||
          cleanDenom.contains('10c') ||
          cleanDenom.contains('dime')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvFile = effMint == 'D'
            ? 'SemiQ-Dime-Obverse-Unc-D.jpg'
            : 'SemiQ-Dime-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-DIME-$effMint',
          obverseUrl: '$_base/bulk_programs/dime/$obvFile',
          reverseUrl: '$_base/bulk_programs/dime/SemiQ-Dime-Reverse-Unc.jpg',
          fallbackObverseUrl: null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
      final isQuarter = RegExp(r'\b(25c|25¢|quarter)\b').hasMatch(cleanDenom) ||
          RegExp(r'\bquarter\b').hasMatch(cleanTitle);
      final isHalf = RegExp(r'\b(50c|50¢|half)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(kennedy|half dollar)\b').hasMatch(cleanTitle);
      if (cleanTitle.contains('kennedy') ||
          cleanTitle.contains('half dollar') ||
          cleanDenom.contains('50c') ||
          cleanDenom.contains('half') ||
          (cleanTitle.contains('independence') && !isQuarter)) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Obverse-Unc-D.jpg'
            : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-HALF-$effMint',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/bulk_programs/half_dollar/SemiQ-Half-Dollar-Reverse-Unc.jpg',
          fallbackObverseUrl: effMint == 'P'
              ? '$_base/2026_series/2026_half_dollar_enduring_liberty_obverse.jpg'
              : '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Half-Dollar-Obverse-Unc-P.jpg',
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
      if (cleanTitle.contains('mayflower')) {
        final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
        final obvUrl = effMint == 'D'
            ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Mayflower-Obverse-Unc-D.jpg'
            : '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg';
        return CanonicalMintAssetPair(
          sku: '2026-MAYFLOWER-$effMint',
          obverseUrl: obvUrl,
          reverseUrl:
              '$_base/2026_series/2026_quarter_dollar_mayflower_compact_reverse.jpg',
          fallbackObverseUrl: effMint == 'D'
              ? '$_base/2026_series/2026_quarter_dollar_mayflower_compact_obverse.jpg'
              : null,
          fallbackReverseUrl: null,
          isGenuine2026: true,
        );
      }
      // 2026 Semiquincentennial quarters (Declaration, Gettysburg, Revolutionary War, Constitution)
      const qtrs = <String, String>{
        'declaration of independence': 'declaration_of_independence',
        'gettysburg': 'gettysburg_address',
        'revolutionary war': 'revolutionary_war',
        'constitution': 'us_constitution',
      };
      for (final e in qtrs.entries) {
        if (cleanTitle.contains(e.key) && (isQuarter || !isHalf)) {
          final effMint = (cleanMint.isEmpty || cleanMint == 'P') ? 'P' : cleanMint;
          return CanonicalMintAssetPair(
            sku: '2026-QTR-${e.value.toUpperCase()}-$effMint',
            obverseUrl: '$_base/2026_series/2026_quarter_dollar_${e.value}_obverse.jpg',
            reverseUrl: '$_base/2026_series/2026_quarter_dollar_${e.value}_reverse.jpg',
            isGenuine2026: true,
          );
        }
      }
      // 2026 Native American $1 (Polly Cooper)
      if (cleanTitle.contains('polly cooper') ||
          (RegExp(r'\bnative american\b').hasMatch(cleanTitle) &&
              (cleanDenom.contains('1') || cleanTitle.contains('dollar')))) {
        return const CanonicalMintAssetPair(
          sku: '2026-NATIVE-POLLY',
          obverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_obverse.jpg',
          reverseUrl: '$_base/2026_series/2026_native_american_dollar_polly_cooper_reverse.jpg',
          isGenuine2026: true,
        );
      }
      // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
      // MF-C5': (?!\w) fixes broken trailing \b on Unicode ¢; (?<![\d.]) prevents 15¢/25c/25 cent
      // from matching 1¢/5¢/cent while preserving '1 cent', '1¢', 'cent', '5¢', '5 cents', 'five cents'.
      final isCent = RegExp(r'(?<![\d.])(?:1c|1¢|1 cents?|one cent|penny)(?!\w)|(?:^|(?<![\d.])\s+)\bcent\b', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b', caseSensitive: false).hasMatch(cleanTitle);
      final isNickel = RegExp(r'(?<![\d.])(?:5c|5¢|5 cents?|five cents?|nickel)(?!\w)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
      if (isCent && !isQuarter && !isHalf && !isNickel) {
        final effMint = cleanMint == 'D' ? 'D' : 'P';
        return CanonicalMintAssetPair(
          sku: '2026-CENT-$effMint',
          obverseUrl: effMint == 'D'
              ? '$_base/bulk_programs/us_mint_manual/highres_scrape/SemiQ-Penny-Obverse-Unc-D.jpg'
              : '$_base/bulk_programs/penny/SemiQ-Penny-Obverse-Unc-P.jpg',
          reverseUrl: '$_base/bulk_programs/penny/SemiQ-Penny-Reverse-Unc.jpg',
          isGenuine2026: true,
        );
      }
      if (isNickel && !isQuarter && !isHalf) {
        final effMint = cleanMint == 'D' ? 'D' : 'P';
        return CanonicalMintAssetPair(
          sku: '2026-NICKEL-$effMint',
          obverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Obverse-Unc-$effMint.jpg',
          reverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Reverse-Unc.jpg',
          isGenuine2026: true,
        );
      }
    }

    // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
    if (cleanYear == '2023') {
      const awqObv =
          '$_base/2023_series/2023_american_women_quarters_shared_obverse.jpg';
      const awqFallbackObv =
          '$_base/2023_series/2023_american_women_quarters_shared_obverse.png';
      const awqRevs = <String, String>{
        'bessie coleman':
            '2023_american_women_quarters_bessie_coleman_reverse.jpg',
        'edith kanaka':
            '2023_american_women_quarters_edith_kanakaole_reverse.jpg',
        'kanakaole':
            '2023_american_women_quarters_edith_kanakaole_reverse.jpg',
        'eleanor roosevelt':
            '2023_american_women_quarters_eleanor_roosevelt_reverse.jpg',
        'jovita idar': '2023_american_women_quarters_jovita_idar_reverse.jpg',
        'maria tallchief':
            '2023_american_women_quarters_maria_tallchief_reverse.jpg',
      };
      for (final entry in awqRevs.entries) {
        if (cleanTitle.contains(entry.key)) {
          final revUrl = '$_base/2023_series/${entry.value}';
          return CanonicalMintAssetPair(
            sku: '2023-AWQ-${entry.key.split(' ').first.toUpperCase()}',
            obverseUrl: awqObv,
            reverseUrl: revUrl,
            fallbackObverseUrl: awqFallbackObv,
            fallbackReverseUrl: revUrl.replaceAll('.jpg', '.png'),
          );
        }
      }
    }

    // 4. 2005-D Kansas State Quarter (Row 12) - Strict && guard per MF8
    if (cleanYear == '2005' &&
        cleanMint == 'D' &&
        cleanTitle.contains('kansas') &&
        (cleanDenom.contains('quarter') ||
            cleanDenom.contains('25c') ||
            cleanTitle.contains('quarter'))) {
      return const CanonicalMintAssetPair(
        sku: '2005-SQ-KS-D',
        obverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg',
        reverseUrl:
            '$_base/bulk_programs/50_state_quarters/2005-50-state-quarters-coin-kansas-uncirculated-reverse.jpg',
        fallbackObverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Philadelphia_29.jpg',
        fallbackReverseUrl:
            '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/2005_United_States_quarters/50_State_quarter__Kansas_/Kansas_quarter_2C_reverse_side_2C_2005.jpg',
      );
    }

    // 5. 1962 Lincoln Cent (Row 18) - MF9: Obverse kept as stored; reverse replaced with Lincoln Memorial reverse
    if (cleanYear == '1962' &&
        (cleanTitle.contains('lincoln') ||
            cleanTitle.contains('cent') ||
            cleanDenom.contains('1c') ||
            cleanDenom.contains('cent'))) {
      return CanonicalMintAssetPair(
        sku: '1962-LINCOLN-1C',
        obverseUrl: storedObverseUrl ??
            '$_wikiBase/Coins__NNC_/NNC-US-1909-1C-Lincoln_Cent__28wheat_29_LEFT.jpg',
        reverseUrl:
            '$_wikiBase/United_States_cents/Lincoln_cents/Lincoln_Memorial_cent/United_States_penny_2C_reverse.jpg',
        fallbackObverseUrl:
            '$_wikiBase/United_States_cents/Obverses_of_United_States_cents/2002_Penny_Proof_Obv.png',
        fallbackReverseUrl: null,
      );
    }

    // 6. America the Beautiful (ATB) Quarters (Live Firestore Rows 13–17, 19–24 + Synthetic Tracker B26-25..B26-30)
    const atbRevs = <String, String>{
      'american memorial':
          '2019-america-the-beautiful-quarters-coin-american-memorial-park-northern-mariana-islands-uncirculated-reverse.jpg',
      'salt river':
          '2020-america-the-beautiful-quarters-coin-salt-river-bay-us-virgin-islands-uncirculated-reverse.jpg',
      'mount rushmore':
          '2013-america-the-beautiful-quarters-coin-mount-rushmore-south-dakota-uncirculated-reverse.jpg',
      'cumberland island':
          '2018-america-the-beautiful-quarters-coin-cumberland-island-georgia-uncirculated-reverse.jpg',
      'block island':
          '2018-america-the-beautiful-quarters-coin-block-island-rhode-island-uncirculated-reverse.jpg',
      'san antonio':
          '2019-america-the-beautiful-quarters-coin-san-antonio-missions-texas-uncirculated-reverse.jpg',
      'effigy mounds':
          '2017-america-the-beautiful-quarters-coin-effigy-mounds-iowa-uncirculated-reverse.jpg',
      'frederick douglass':
          '2017-america-the-beautiful-quarters-coin-frederick-douglass-district-of-columbia-uncirculated-reverse.jpg',
      'yellowstone':
          '2010-america-the-beautiful-quarters-coin-yellowstone-wyoming-uncirculated-reverse.jpg',
      'george rogers clark':
          '2017-america-the-beautiful-quarters-coin-george-rogers-clark-indiana-uncirculated-reverse.jpg',
      'ozark':
          '2017-america-the-beautiful-quarters-coin-ozark-riverways-missouri-uncirculated-reverse.jpg',
      'white mountain':
          '2013-america-the-beautiful-quarters-coin-white-mountain-new-hampshire-uncirculated-reverse.jpg',
      'mount hood':
          '2010-america-the-beautiful-quarters-coin-mount-hood-oregon-uncirculated-reverse.jpg',
      'marsh-billings':
          '2020-america-the-beautiful-quarters-coin-marsh-billings-rockefeller-vermont-uncirculated-reverse.jpg',
      'tallgrass':
          '2020-america-the-beautiful-quarters-coin-tallgrass-prairie-kansas-uncirculated-reverse.jpg',
      'weir farm':
          '2020-america-the-beautiful-quarters-coin-weir-farm-connecticut-uncirculated-reverse.jpg',
    };

    const atbObvByYearMint = <String, String>{
      '2013-P':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-p.jpg',
      '2013-D':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-uncirculated-obverse-d.jpg',
      '2013-S':
          '$_base/atb_quarters/2013-america-the-beautiful-quarters-coin-proof-obverse-s.jpg',
      '2018-P':
          '$_base/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2018-D':
          '$_base/atb_quarters/2018-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
      '2019-P':
          '$_base/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2019-D':
          '$_base/atb_quarters/2019-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
      '2020-P':
          '$_base/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-philadelphia.jpg',
      '2020-D':
          '$_base/atb_quarters/2020-america-the-beautiful-quarters-coin-uncirculated-obverse-denver.jpg',
    };

    for (final entry in atbRevs.entries) {
      if (cleanTitle.contains(entry.key)) {
        final revUrl = '$_base/atb_quarters/${entry.value}';
        final exactObv = atbObvByYearMint['$cleanYear-$cleanMint'];
        late final String obvUrl;
        late final String fallbackObv;
        if (exactObv != null) {
          obvUrl = exactObv;
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
        } else if (cleanMint == 'S') {
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_proof_obverse__28San_Francisco_29.jpg';
          fallbackObv =
              '$_base/atb_quarters/2014-america-the-beautiful-quarters-coin-proof-obverse-s.jpg';
        } else if (cleanMint == 'D') {
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/50_State_Quarters/50_State_and_Territories_quarter_obverse__28Denver_29.jpg';
        } else if (cleanMint == 'W') {
          // MF8: Do not assign a P-mint obverse to a W-mint coin; use undated ATB obverse
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg';
        } else {
          // MF8: Undated Philadelphia ATB obverse (no conflicting year in filename)
          obvUrl =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_quarter_obverse__28Philadeplhia_29.jpg';
          fallbackObv =
              '$_wikiBase/United_States_quarters/Washington_quarter/America_the_Beautiful_Quarters/America_the_Beautiful_quarter_2C_obverse.jpg';
        }
        return CanonicalMintAssetPair(
          sku: 'ATB-$cleanYear-$cleanMint',
          obverseUrl: obvUrl,
          reverseUrl: revUrl,
          fallbackObverseUrl: fallbackObv,
          fallbackReverseUrl: null,
        );
      }
    }

    return null;
  }
}
