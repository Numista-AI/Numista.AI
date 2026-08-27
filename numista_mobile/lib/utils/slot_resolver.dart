import 'dart:convert';
import 'package:crypto/crypto.dart';
import '../models/program_model.dart';

/// Representation of matching collection items for a specific program slot & variety.
class SlotMatchResult {
  final bool isOwned;
  final int quantity;
  final String primaryGrade;
  final String? primaryService;
  final String? primaryCertNumber;
  final List<String> allGrades;
  final String formattedNotes;

  const SlotMatchResult({
    required this.isOwned,
    required this.quantity,
    required this.primaryGrade,
    this.primaryService,
    this.primaryCertNumber,
    required this.allGrades,
    required this.formattedNotes,
  });

  static const empty = SlotMatchResult(
    isOwned: false,
    quantity: 0,
    primaryGrade: 'Unspecified',
    primaryService: null,
    primaryCertNumber: null,
    allGrades: [],
    formattedNotes: '',
  );

  Map<String, dynamic> toCanonicalMap(String slotKey) {
    final sortedGrades = List<String>.from(allGrades)..sort();
    return {
      'all_grades': sortedGrades,
      if (primaryCertNumber != null && primaryCertNumber!.isNotEmpty)
        'primary_cert': primaryCertNumber,
      'primary_grade': primaryGrade,
      if (primaryService != null && primaryService!.isNotEmpty)
        'primary_service': primaryService,
      'quantity': quantity,
      'slot_key': slotKey,
    };
  }
}

/// Numerical ranker & comparator for Sheldon coin grades, adjectival grades, and slab services.
class SheldonGradeRanker {
  /// Numerical Sheldon scale mapping (70 down to -1).
  static int getSheldonScore(String? gradeStr) {
    if (gradeStr == null) return -1;
    final g = gradeStr.trim().toUpperCase();
    if (g.isEmpty) return -1;

    // Check for explicit numerical score (e.g. MS-65, AU-58, VF-20, G-4, PO-1)
    final numMatch = RegExp(r'(\d{1,2})').firstMatch(g);
    if (numMatch != null) {
      final numVal = int.tryParse(numMatch.group(1)!);
      if (numVal != null && numVal >= 1 && numVal <= 70) {
        // If it's a details or problem coin, dock score slightly
        if (g.contains('DETAIL') || g.contains('CLEAN') || g.contains('DAMAG') || g.contains('SCRATCH')) {
          return (numVal - 5).clamp(2, 70);
        }
        return numVal;
      }
    }

    // Adjectival / unnumbered grades
    if (g.contains('PROOF') || g.contains('PF') || g.contains('PR')) return 65;
    if (g.contains('BU') || g.contains('BRILLIANT') || g.contains('UNC') || g.contains('MINT STATE')) return 63;
    if (g.contains('AU') || g.contains('ABOUT UNC')) return 53;
    if (g.contains('XF') || g.contains('EF') || g.contains('EXTRA FINE')) return 42;
    if (g.contains('VF') || g.contains('VERY FINE')) return 25;
    if (g.contains('FINE') || g == 'F') return 13;
    if (g.contains('VG') || g.contains('VERY GOOD')) return 9;
    if (g.contains('GOOD') || g == 'G') return 5;
    if (g.contains('AG') || g.contains('ABOUT GOOD')) return 3;
    if (g.contains('FAIR')) return 2;
    if (g.contains('POOR') || g.contains('CULL')) return 1;

    if (g.contains('DETAIL')) return 10;
    if (g.contains('CIRC') || g.contains('RAW')) return 0;

    return -1;
  }

  /// Grading service tier ranking.
  static int getServiceRank(String? serviceStr) {
    if (serviceStr == null) return 0;
    final s = serviceStr.trim().toUpperCase();
    if (s.contains('PCGS')) return 4;
    if (s.contains('NGC')) return 3;
    if (s.contains('ANACS')) return 2;
    if (s.contains('ICG')) return 1;
    return 0;
  }

  /// Sorts items deterministically: highest Sheldon grade, best service tier, cert#, then docId.
  static int compareItems(Map<String, dynamic> a, Map<String, dynamic> b) {
    final gradeA = a['Condition']?.toString() ?? a['grade']?.toString() ?? '';
    final gradeB = b['Condition']?.toString() ?? b['grade']?.toString() ?? '';
    final scoreA = getSheldonScore(gradeA);
    final scoreB = getSheldonScore(gradeB);

    if (scoreA != scoreB) {
      return scoreB.compareTo(scoreA); // Descending (higher score first)
    }

    final srvA = a['Grading Service']?.toString() ?? a['grading_service']?.toString() ?? '';
    final srvB = b['Grading Service']?.toString() ?? b['grading_service']?.toString() ?? '';
    final rankA = getServiceRank(srvA);
    final rankB = getServiceRank(srvB);

    if (rankA != rankB) {
      return rankB.compareTo(rankA);
    }

    final certA = a['Certification Number']?.toString() ?? a['cert_number']?.toString() ?? '';
    final certB = b['Certification Number']?.toString() ?? b['cert_number']?.toString() ?? '';
    if (certA != certB) {
      return certA.compareTo(certB);
    }

    final idA = a['id']?.toString() ?? a['doc_id']?.toString() ?? '';
    final idB = b['id']?.toString() ?? b['doc_id']?.toString() ?? '';
    return idA.compareTo(idB);
  }
}

/// Centralized deterministic engine for resolving collection items against US Mint programs.
class SlotResolver {
  /// Generates a reproducible, tamper-evident cryptographic Snapshot ID.
  static String generateSnapshotId({
    required String collectorEmail,
    required String programId,
    required int totalSlots,
    required Map<String, SlotMatchResult> resolvedSlots,
    required DateTime timestampUtc,
  }) {
    final dateStr = '${timestampUtc.year}${timestampUtc.month.toString().padLeft(2, '0')}${timestampUtc.day.toString().padLeft(2, '0')}';
    final isoUtc = '${timestampUtc.toUtc().toIso8601String().split('.').first}Z';

    // Sort slot keys alphabetically
    final sortedKeys = resolvedSlots.keys.toList()..sort();
    final canonicalOwnedSlots = <Map<String, dynamic>>[];

    for (final k in sortedKeys) {
      final res = resolvedSlots[k]!;
      if (res.isOwned) {
        canonicalOwnedSlots.add(res.toCanonicalMap(k));
      }
    }

    final payloadMap = {
      'collector_email': collectorEmail.trim().toLowerCase(),
      'denom_total_slots': totalSlots,
      'program_id': programId.trim(),
      'resolved_slots': canonicalOwnedSlots,
      'timestamp_utc': isoUtc,
    };

    final canonicalJson = jsonEncode(payloadMap);
    final hashBytes = sha256.convert(utf8.encode(canonicalJson)).bytes;
    final hashHex = hashBytes.map((b) => b.toRadixString(16).padLeft(2, '0')).join().toUpperCase();
    final hash8 = hashHex.substring(0, 8);

    return 'SNAP-$dateStr-$hash8';
  }

  // ─── Field alias helpers ───────────────────────────────────────────────────

  /// Returns the first non-empty value found under any of [keys], uppercased
  /// and trimmed. Returns '' if no key has a value.
  static String _field(Map<String, dynamic> item, List<String> keys) {
    for (final k in keys) {
      final v = item[k];
      if (v != null) {
        final s = v.toString().trim();
        if (s.isNotEmpty) return s.toUpperCase();
      }
    }
    return '';
  }

  static String _metalContent(Map<String, dynamic> item) =>
      _field(item, ['Metal Content', 'metal_content', 'Composition', 'composition']);

  static String _strikeType(Map<String, dynamic> item) =>
      _field(item, ['Strike Type', 'strike_type', 'Strike', 'strike']);

  /// Covers Variety AND Theme/Subject so privy detection works across both fields.
  static String _variety(Map<String, dynamic> item) =>
      _field(item, ['Variety', 'variety', 'Theme/Subject', 'theme_subject']);

  static String _mintMark(Map<String, dynamic> item) =>
      _field(item, ['Mint Mark', 'mint_mark', 'Mint', 'mint']);

  // ─── Coin matching ─────────────────────────────────────────────────────────

  // ── Call-chain for PDF banner and grid (both come from one inventoryMap) ───
  // program_manager_screen.dart:1237
  //   SlotResolver.resolveProgramInventory(program, coins)
  //     slot_resolver.dart:476  for each coinSlot in program.coins:
  //       slot_resolver.dart:487  slotMatches = pool.where((item) => isMatch(...))
  //         slot_resolver.dart:205  isMatch()  ← THIS FUNCTION — the only gate
  //       slot_resolver.dart:489  for each variety in coinSlot.varieties:
  //         slot_resolver.dart:490    slotKey = program.id_coinSlot.id_variety.id
  //         slot_resolver.dart:491    matchingItems = slotMatches.where(matchesVariety)
  //         slot_resolver.dart:525    result[slotKey] = SlotMatchResult(isOwned: true)
  //     returns Map<String, SlotMatchResult> inventoryMap
  //   program_manager_screen.dart:1241
  //     distinctOwned = inventoryMap.values.where((r) => r.isOwned).length
  //   ChecklistGeneratorService.generateChecklist(distinctOwnedSlots: distinctOwned)
  //     checklist_generator_service.dart:328  banner "Slots: N / 19"
  //     checklist_generator_service.dart:217  grid checkbox per slotKey

  /// Derives a stable product-family token from a coin's Program/Series + Theme/Subject.
  ///
  /// Order is mandatory — checked top-to-bottom, first match wins:
  ///   1. buffalo  — American Buffalo checked before any gold/eagle rule
  ///   2. ase      — American Silver Eagle checked before gold eagle (both contain 'eagle')
  ///   3. age      — American Gold Eagle
  ///   4. peace    — Peace Dollar
  ///   5. morgan   — Morgan Dollar
  ///   6. innovation:state — American Innovation $1; state derived from Theme/Subject.
  ///                         No state → returns '' → isMatch returns false (no tick).
  ///   7. trump    — Semiquincentennial Trump $1
  ///   Default: '' → isMatch returns false, not match-all.
  static String _deriveCoinFamily(String progSeries, String themeSub) {
    final ps = progSeries.toLowerCase();
    final th = themeSub.toLowerCase();
    if (ps.contains('american buffalo') || ps.contains('buffalo gold')) { return 'buffalo'; }
    if (ps.contains('american silver eagle') || ps.contains('silver eagle')) { return 'ase'; }
    if (ps.contains('american gold eagle') || ps.contains('gold eagle')) { return 'age'; }
    if (ps.contains('peace dollar')) { return 'peace'; }
    if (ps.contains('morgan dollar') || ps.contains('morgan silver')) { return 'morgan'; }
    if (ps.contains('american innovation') || ps.contains('innovation dollar')) {
      if (th.contains('iowa'))       { return 'innovation:iowa'; }
      if (th.contains('wisconsin'))  { return 'innovation:wisconsin'; }
      if (th.contains('california')) { return 'innovation:california'; }
      if (th.contains('minnesota'))  { return 'innovation:minnesota'; }
      return ''; // No state → no tick
    }
    if (ps.contains('trump') || ps.contains('semiquincentennial president')) { return 'trump'; }
    return '';
  }

  /// Evaluates an item from Firestore against a program coin slot.

  static bool isMatch(Map<String, dynamic> item, CoinProgram program, ProgramCoin coinSlot) {
    // ── 0a. program_id fast path ────────────────────────────────────────────
    // Coins added via POST /api/checklist/add_coins carry a mandatory
    // snake_case `program_id` field written by the server. When present, use it
    // as the single source of truth and skip all string heuristics below.
    // Legacy coins (added before Phase 4) have no `program_id` field and fall
    // through to the existing matching logic unchanged.
    final storedProgramId = item['program_id']?.toString();
    if (storedProgramId != null && storedProgramId.isNotEmpty) {
      // Year guard still applies even on fast-path — we must still match the
      // correct slot row within the program.
      final slotYear = (coinSlot.year ?? '').trim();
      if (slotYear.isNotEmpty) {
        final itemYear = (item['Year']?.toString() ?? item['year']?.toString() ?? '').trim();
        final normalizedYear = (itemYear == '1776-1976') ? '1976' : itemYear;
        if (normalizedYear.isEmpty || normalizedYear != slotYear) return false;
      }
      return storedProgramId == program.id;
    }

    final denom      = (item['Denomination']?.toString() ?? item['denomination']?.toString() ?? '').toLowerCase();
    final progSeries = (item['Program/Series']?.toString() ?? item['program_series']?.toString() ?? '').trim();
    final themeSub   = (item['Theme/Subject']?.toString() ?? item['theme_subject']?.toString() ?? '').trim().toLowerCase();
    final title      = (item['Title']?.toString() ?? item['name']?.toString() ?? item['official_title']?.toString() ?? '').trim().toLowerCase();
    final year       = (item['Year']?.toString() ?? item['year']?.toString() ??
                        item['date']?.toString() ?? '').trim();
    final cNameLower = coinSlot.name.toLowerCase().trim();
    final slotYear   = (coinSlot.year ?? '').trim();

    // 0. Country guard — empty passes; explicit non-US rejects
    final country = _field(item, ['Country', 'country']).toLowerCase();
    if (country.isNotEmpty &&
        country != 'united states' && country != 'us' &&
        country != 'usa' && country != 'u.s.' &&
        country != 'united states of america') {
      return false;
    }

    // 1. Check Multi-coin Mint / Proof Set Matching
    if (denom == 'set' || progSeries.toLowerCase().contains('uncirculated set') || progSeries.toLowerCase().contains('proof set')) {
      final setContents = item['SetContents'] as List? ?? item['set_coins'] as List? ?? [];
      final contentsStr = setContents.join(' ').toLowerCase();
      final setStr = '$contentsStr $themeSub $title';
      if (setStr.trim().isNotEmpty && cNameLower.isNotEmpty && setStr.contains(cNameLower)) {
        return true;
      }
      // 2026 Annual Uncirculated Set: no SetContents in Firestore, but name/theme confirms
      // it contains P + D of every circulating denomination.
      // Match all denomination slots for the circulating program.
      // July 4th Privy columns are still blocked by requiresPrivy gate in matchesVariety().
      if (program.id == '2026_semiquincentennial_currency' && year == '2026') {
        final nameField = (item['name']?.toString() ?? '').toLowerCase();
        final isAnnualSet = themeSub.contains('250th') ||
            nameField.contains('uncirculated coin set') ||
            nameField.contains('annual') ||
            progSeries.toLowerCase().contains('uncirculated set');
        if (isAnnualSet) {
          if (cNameLower.contains('cent') ||
              cNameLower.contains('nickel') ||
              cNameLower.contains('dime') ||
              cNameLower.contains('quarter') ||
              cNameLower.contains('half')) {
            return true;
          }
        }
      }
      return false;
    }

    // 2. Denomination Alignment Guard
    if (denom.isNotEmpty) {
      final pNameLower = program.name.toLowerCase();
      if (pNameLower.contains('quarter') && !denom.contains('quarter') && !denom.contains('25c')) return false;
      if (pNameLower.contains('half dollar') && !denom.contains('half')) return false;
      if (pNameLower.contains('dollar') && !pNameLower.contains('half') && !denom.contains('dollar') && !denom.contains('\$1') && !denom.contains('1 dollar')) return false;
      if (pNameLower.contains('cent') && !denom.contains('cent') && !denom.contains('penny') && !denom.contains('1c')) return false;
      if (pNameLower.contains('nickel') && !denom.contains('nickel') && !denom.contains('5c')) return false;
      if (pNameLower.contains('dime') && !denom.contains('dime') && !denom.contains('10c')) return false;
    }

    // 3. Program/Series Alignment — rule 24 in matchesDbSeries handles 2026/America250 properly
    final bool seriesMatched = program.matchesDbSeries(progSeries);
    if (!seriesMatched && progSeries.isNotEmpty) { return false; }

    // 3b. TEMPORARY: Collectibles product-family guard.
    // matchesDbSeries() answers "is this coin in this program?" but not
    // "is this coin in THIS SPECIFIC SLOT?" For the collectibles program,
    // one W-Proof coin would paint every W-PROOF hole (AGE, Buffalo, ASE).
    // Fix: require exact productFamily match + finish guard.
    // Next commit: productFamily on every slot in all programs + delete _isMatch.
    if (program.id == '2026_semiquincentennial_collectibles') {
      final slotFamily = coinSlot.productFamily;
      if (slotFamily.isEmpty) { return false; } // Unknown slot → reject safely

      final coinFamily = _deriveCoinFamily(progSeries, themeSub);
      if (coinFamily.isEmpty || coinFamily != slotFamily) { return false; }

      // Stage 2: finish guard — RP coin cannot tick EU slot and vice versa.
      final cNameLower = coinSlot.name.toLowerCase();
      final variety = (item['Variety']?.toString() ?? item['variety']?.toString() ?? '').toLowerCase();
      final strikeType = (item['Strike Type']?.toString() ?? item['strike_type']?.toString() ?? '').toLowerCase();
      final finishHint = '$variety $strikeType'.trim();

      final slotIsRP   = cNameLower.contains('reverse proof');
      final slotIsEU   = cNameLower.contains('enhanced uncirculated');
      final slotIsCong = cNameLower.contains('congratulations');
      final coinIsRP   = finishHint.contains('reverse proof') || finishHint.contains('reverse-proof');
      final coinIsEU   = finishHint.contains('enhanced') || finishHint.contains(' eu');
      final coinIsCong = finishHint.contains('congratulations') || finishHint.contains('cong');

      if (slotIsRP   && !coinIsRP)   { return false; }
      if (slotIsEU   && !coinIsEU)   { return false; }
      if (slotIsCong && !coinIsCong) { return false; }
      if (coinIsRP   && !slotIsRP)   { return false; }
      if (coinIsEU   && !slotIsEU)   { return false; }
      if (coinIsCong && !slotIsCong) { return false; }

      // Family + finish matched — year guard falls through below
    }

    // 4. Year Alignment Guard — hard equality when slot has a year.
    // Empty item year is NOT a wildcard: it fails any dated slot.
    // Dual-date rule: '1776-1976' maps only to the 1976 Bicentennial row.
    if (slotYear.isNotEmpty) {
      final normalizedYear = (year == '1776-1976') ? '1976' : year;
      if (normalizedYear.isEmpty || normalizedYear != slotYear) {
        return false;
      }
    }

    // 3a. Classic Washington year-range guard (second barrier after Fix A).
    // 'washington_quarters_classic' = slugify("Washington Quarters (Classic)").
    // int.tryParse('1776-1976') returns null → itemYear=0 → guard skips safely;
    // dual-date is handled above in the normalizedYear rewrite instead.
    if (program.id == 'washington_quarters_classic') {
      final itemYear = int.tryParse(year) ?? 0;
      if (itemYear != 0 && (itemYear < 1932 || itemYear > 1998)) {
        return false;
      }
    }

    // 5. Subject / Design Match
    if (cNameLower.isNotEmpty) {
      if (themeSub.isNotEmpty && (themeSub.contains(cNameLower) || cNameLower.contains(themeSub))) return true;
      if (title.isNotEmpty && (title.contains(cNameLower) || cNameLower.contains(title))) return true;

      // Clean subject comparisons (remove dates and descriptors)
      final cleanSlotName = cNameLower.replaceAll(RegExp(r'^\d{4}\s*-\s*'), '').trim();
      if (cleanSlotName.isNotEmpty) {
        if (themeSub.isNotEmpty && (themeSub.contains(cleanSlotName) || cleanSlotName.contains(themeSub))) return true;
        if (title.isNotEmpty && (title.contains(cleanSlotName) || cleanSlotName.contains(title))) return true;
      }
    }

    // 5b. 2026 Circulating Currency: require design-level match — no year+series wildcard.
    // Without this, one Semiquincentennial coin (year=2026, seriesMatched=true) paints all 9 slots.
    if (program.id == '2026_semiquincentennial_currency') {
      final ts = themeSub; // already lowercased
      final sl = cNameLower;
      // Cent slot
      if (sl.contains('cent') &&
          (ts.contains('cent') || ts.contains('lincoln') || ts.contains('1776') ||
           progSeries.toLowerCase().contains('cent'))) {
        return true;
      }
      // Nickel slot
      if (sl.contains('nickel') &&
          (ts.contains('nickel') || ts.contains('jefferson') || ts.contains('1776') ||
           progSeries.toLowerCase().contains('nickel'))) {
        return true;
      }
      // Dime slot
      if (sl.contains('dime') &&
          (ts.contains('dime') || ts.contains('roosevelt') || ts.contains('emerging') ||
           progSeries.toLowerCase().contains('dime'))) {
        return true;
      }
      // Half Dollar slot: enduring liberty stored as Semiquincentennial + '250th anniversary'
      if (sl.contains('half') &&
          (ts.contains('half') || ts.contains('enduring') || ts.contains('250th') ||
           ts.contains('independence') || progSeries.toLowerCase().contains('half'))) {
        return true;
      }
      // Quarter slots: design keyword must be in BOTH slot name AND theme
      if (sl.contains('quarter')) {
        if (sl.contains('mayflower')     && ts.contains('mayflower'))     { return true; }
        if (sl.contains('revolutionary') && ts.contains('revolutionary')) { return true; }
        if (sl.contains('declaration')   && ts.contains('declaration'))   { return true; }
        if (sl.contains('constitution')  && ts.contains('constitution'))  { return true; }
        if (sl.contains('gettysburg')    && ts.contains('gettysburg'))    { return true; }
      }
      return false; // No design match → reject
    }

    // Single design series where year + series match is sufficient
    if (slotYear.isNotEmpty && year.isNotEmpty && slotYear == year && seriesMatched) {
      return true;
    }

    return false;
  }


  /// Resolves which specific variety/mint column an item belongs to.
  static bool matchesVariety(Map<String, dynamic> item, ChecklistVariety variety) {
    final mintMark   = _mintMark(item);
    final strikeType = _strikeType(item);
    final varField   = _variety(item);
    final metal      = _metalContent(item);
    final vId        = variety.id.toUpperCase();
    final grade      = _field(item, ['Condition', 'grade', 'Grade']);

    // ── Shared predicates — computed once, used by every branch ─────────────
    final isProof = strikeType.contains('PROOF') ||
                    varField.contains('PROOF')   ||
                    RegExp(r'\b(PR|PF)[- ]?\d', caseSensitive: false).hasMatch(grade);

    final isSilver = metal.contains('SILVER') || varField.contains('SILVER');

    final isSMS = strikeType.contains('SMS') ||
                  varField.contains('SMS')   ||
                  RegExp(r'\bSP[- ]?\d{2}', caseSensitive: false).hasMatch(grade);

    // isReverseProof: strike_type or variety explicitly says REVERSE.
    final isReverseProof = strikeType.contains('REVERSE') ||
                           varField.contains('REVERSE');

    // isEnhancedUnc: strike_type or variety says ENHANCED or EU.
    final isEnhancedUnc = strikeType.contains('ENHANCED') ||
                          varField.contains('ENHANCED')   ||
                          strikeType.contains('EU')        ||
                          varField.contains('EU');

    // ── requiresPrivy gate ───────────────────────────────────────────────────
    if (variety.requiresPrivy == true) {
      final title = _field(item, [
        'official_us_mint_title', 'Official US Mint Title', 'Title', 'title']);
      final hasPrivy =
          varField.contains('250')                 ||
          varField.contains('SEMIQUINCENTENNIAL')   ||
          varField.contains('AMERICA250')           ||
          title.contains('250')                    ||
          title.contains('SEMIQUINCENTENNIAL')      ||
          title.contains('AMERICA250');
      if (!hasPrivy) return false;
    }

    // ── Innovation legacy empty-variety.id positional fallback ───────────────
    // Pre-Phase-1 Innovation coins matched against variety.id="" slots.
    // READ TIME ONLY — zero writes to users/{uid}/coins.
    // Legacy empty-id slots: preserve existing owns; new IDs handle fresh matches.
    if (variety.id.isEmpty) {
      return true; // safe read-time fallback
    }

    // ── Privy-mark varieties ─────────────────────────────────────────────────
    if (vId.contains('PRIVY-JULY4')) {
      return (mintMark == 'P' || mintMark == 'D' || mintMark.isEmpty) &&
             (varField.contains('JULY 4') || varField.contains('JULY4') ||
              varField.contains('PRIVY') || strikeType.contains('PRIVY'));
    }

    // ── Reverse Proof — mint-specific ────────────────────────────────────────
    // P-REVERSE-PROOF: Philadelphia RP (Morgan 26XF, Peace 26XL)
    if (vId == 'P-REVERSE-PROOF') {
      return (mintMark == 'P' || mintMark.isEmpty) && isReverseProof;
    }
    // S-REVERSE-PROOF: San Francisco RP (Innovation dollars)
    if (vId == 'S-REVERSE-PROOF') {
      return mintMark == 'S' && isReverseProof;
    }
    // W-REVERSE-PROOF: West Point RP (reserved)
    if (vId == 'W-REVERSE-PROOF') {
      return mintMark == 'W' && isReverseProof;
    }
    // Generic REVERSE-PROOF legacy catch-all
    if (vId == 'REVERSE-PROOF') {
      return isReverseProof;
    }

    // ── Enhanced Uncirculated — mint-specific ─────────────────────────────────
    // EU: struck at West Point; coin may bear no mint mark (Morgan/Peace 2026 26XE/26XH)
    if (vId == 'EU') {
      return isEnhancedUnc && (mintMark == 'W' || mintMark.isEmpty);
    }
    // W-EU: Enhanced Unc, West Point marked (ASE 26EG, AGE 26EH)
    if (vId == 'W-EU') {
      return isEnhancedUnc && mintMark == 'W';
    }

    // ── West Point Uncirculated (Kennedy 2019-W/2020-W; AWQ W mint) ──────────
    if (vId == 'W-UNC') {
      return mintMark == 'W' && !isProof && !isEnhancedUnc;
    }

    // ── Congratulations Set Proof — Philadelphia (26RF) ───────────────────────
    // Separate row from W-PROOF (26EA). Requires 'congratulations' in variety/title.
    if (vId == 'P-PROOF-CONG') {
      final title = _field(item, ['Title', 'title', 'official_us_mint_title']);
      final isCongrats = varField.contains('CONGRATUL') || title.contains('CONGRATUL');
      return (mintMark == 'P' || mintMark.isEmpty) && isProof && isCongrats;
    }

    // ── S-SILVER (1976-S 40% silver BU only — NOT proof) ─────────────────────
    if (vId == 'S-SILVER') {
      return mintMark == 'S' && isSilver && !isProof;
    }

    // ── S-SILVER-PROOF (1976-S / 1992-1998 S silver proof) ───────────────────
    if (vId == 'S-SILVER-PROOF') {
      return mintMark == 'S' && isSilver && isProof;
    }

    // ── S-PROOF (S-mint clad proof only) ─────────────────────────────────────
    if (vId == 'S-PROOF' || vId == 'S-CLAD' || vId.startsWith('S-PROOF-')) {
      return mintMark == 'S' && isProof && !isSilver;
    }

    // ── Philadelphia Proof (1936-1942, 1950-1964) — id: 'PROOF' ──────────────
    if (vId == 'PROOF') {
      final isPhillyOrUnmarked = mintMark.isEmpty || mintMark == 'NONE' ||
                                  mintMark == 'P'  || mintMark == 'PHILADELPHIA';
      return isProof && isPhillyOrUnmarked && !isSMS;
    }

    // ── P-PROOF: Philadelphia Proof (Morgan 1895-P, proof-only dated coins) ───
    // isReverseProof guard prevents P-REVERSE-PROOF coins landing here.
    if (vId == 'P-PROOF') {
      return (mintMark == 'P' || mintMark.isEmpty) && isProof && !isReverseProof;
    }

    // ── Generic mint+PROOF (W-PROOF: ASE 26EA, AGE 26EB, Buffalo 26EL) ───────
    // isReverseProof guard: Reverse Proof coins must not land in W-PROOF.
    if (vId.contains('PROOF') && !isReverseProof) {
      final baseMint = vId.split('-').first;
      if (baseMint.isNotEmpty && baseMint != 'S') {
        return mintMark == baseMint && isProof;
      }
      return isProof;
    }

    // ── SMS (Special Mint Set) — 1965, 1966, 1967 ────────────────────────────
    if (vId == 'SMS') {
      return isSMS;
    }

    // ── Uncirculated standard mint marks (P, D, W, S, CC, O) ────────────────
    // !isProof, !isSMS, !isEnhancedUnc: each handled above.
    final baseMint = vId.split('-').first;
    if (mintMark == baseMint && !isProof && !isSMS && !isEnhancedUnc) return true;
    if (baseMint == 'P' &&
        (mintMark.isEmpty || mintMark == 'NONE' || mintMark == 'PHILADELPHIA') &&
        !isProof && !isSMS && !isEnhancedUnc) { return true; }

    return false;
  }


  /// Resolves the entire program inventoryllections.
  static Map<String, SlotMatchResult> resolveProgramInventory({
    required CoinProgram program,
    required List<Map<String, dynamic>> coins,
    List<Map<String, dynamic>> currency = const [],
    List<Map<String, dynamic>> worldItems = const [],
  }) {
    final result = <String, SlotMatchResult>{};

    for (final coinSlot in program.coins) {
      // Determine domain pool based on category/name
      List<Map<String, dynamic>> pool = coins;
      final slotLower = coinSlot.name.toLowerCase();
      if (slotLower.contains('banknote') || slotLower.contains('bill') || slotLower.contains('currency')) {
        pool = currency.isNotEmpty ? currency : coins;
      } else if (slotLower.contains('medal') || slotLower.contains('token') || slotLower.contains('round')) {
        pool = worldItems.isNotEmpty ? worldItems : coins;
      }

      // Find all matching items for this slot
      final slotMatches = pool.where((item) => isMatch(item, program, coinSlot)).toList();

      for (final variety in coinSlot.varieties) {
        final slotKey = '${program.id}_${coinSlot.id}_${variety.id}';
        final matchingItems = slotMatches.where((item) => matchesVariety(item, variety)).toList();

        if (matchingItems.isEmpty) {
          result[slotKey] = SlotMatchResult.empty;
        } else {
          // Sort items deterministically
          matchingItems.sort(SheldonGradeRanker.compareItems);

          final topItem = matchingItems.first;
          final topGrade = topItem['Condition']?.toString() ?? topItem['grade']?.toString() ?? 'Raw';
          final topService = topItem['Grading Service']?.toString() ?? topItem['grading_service']?.toString();
          final topCert = topItem['Certification Number']?.toString() ?? topItem['cert_number']?.toString();

          final allGrades = matchingItems.map((item) {
            final g = item['Condition']?.toString() ?? item['grade']?.toString() ?? 'Raw';
            final s = item['Grading Service']?.toString() ?? item['grading_service']?.toString();
            return (s != null && s.isNotEmpty) ? '$g $s' : g;
          }).toList();

          String formattedNotes;
          if (matchingItems.length == 1) {
            if (topService != null && topService.isNotEmpty && topCert != null && topCert.isNotEmpty) {
              formattedNotes = '$topGrade $topService #$topCert';
            } else if (topService != null && topService.isNotEmpty) {
              formattedNotes = '$topGrade $topService';
            } else {
              formattedNotes = topGrade;
            }
          } else {
            final othersCount = matchingItems.length - 1;
            final topStr = (topService != null && topService.isNotEmpty) ? '$topGrade $topService' : topGrade;
            formattedNotes = 'QTY: ${matchingItems.length} | $topStr, +$othersCount other${othersCount > 1 ? "s" : ""}';
          }

          result[slotKey] = SlotMatchResult(
            isOwned: true,
            quantity: matchingItems.length,
            primaryGrade: topGrade,
            primaryService: topService,
            primaryCertNumber: topCert,
            allGrades: allGrades,
            formattedNotes: formattedNotes,
          );
        }
      }
    }

    return result;
  }
}
