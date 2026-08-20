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

  /// Evaluates an item from Firestore against a program coin slot.

  static bool isMatch(Map<String, dynamic> item, CoinProgram program, ProgramCoin coinSlot) {
    final denom      = (item['Denomination']?.toString() ?? item['denomination']?.toString() ?? '').toLowerCase();
    final progSeries = (item['Program/Series']?.toString() ?? item['program_series']?.toString() ?? '').trim();
    final themeSub   = (item['Theme/Subject']?.toString() ?? item['theme_subject']?.toString() ?? '').trim().toLowerCase();
    final title      = (item['Title']?.toString() ?? item['name']?.toString() ?? item['official_title']?.toString() ?? '').trim().toLowerCase();
    final year       = (item['Year']?.toString() ?? item['year']?.toString() ?? '').trim();
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
    if (!seriesMatched && progSeries.isNotEmpty) return false;

    // 4. Year Alignment Guard (if slot specifies year)
    if (slotYear.isNotEmpty && year.isNotEmpty && slotYear != year) {
      return false;
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

    // Single design series where year + series match is sufficient
    if (slotYear.isNotEmpty && year.isNotEmpty && slotYear == year && seriesMatched) {
      return true;
    }

    return false;
  }

  /// Resolves which specific variety/mint column an item belongs to.
  static bool matchesVariety(Map<String, dynamic> item, ChecklistVariety variety) {
    final mintMark    = _mintMark(item);
    final strikeType  = _strikeType(item);
    final varField    = _variety(item);   // Variety + Theme/Subject
    final metal       = _metalContent(item);
    final vId         = variety.id.toUpperCase();

    // ── requiresPrivy gate ───────────────────────────────────────────────────
    // Fires before any mint-mark logic. Only 250/SEMIQUINCENTENNIAL/AMERICA250
    // qualify — PRIVY alone or ANNIVERSARY alone do not (too broad).
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
      // Privy confirmed — fall through to mint-mark check below.
    }

    // ── Privy-mark varieties ─────────────────────────────────────────────────
    if (vId.contains('PRIVY-JULY4')) {
      return (mintMark == 'P' || mintMark == 'D' || mintMark.isEmpty) &&
             (varField.contains('JULY 4') || varField.contains('JULY4') ||
              varField.contains('PRIVY') || strikeType.contains('PRIVY'));
    }

    // ── Reverse Proof ────────────────────────────────────────────────────────
    if (vId.contains('REVERSE-PROOF')) {
      return (mintMark == 'S' || mintMark == 'W' || mintMark.isEmpty) &&
             (strikeType.contains('REVERSE') || varField.contains('REVERSE'));
    }

    // ── S-SILVER ─────────────────────────────────────────────────────────────
    // Must be S-mint AND silver content AND NOT an explicit proof strike.
    // mintMark == 'S' alone does NOT make a coin proof-like.
    if (vId == 'S-SILVER') {
      final isSilver = metal.contains('SILVER') || varField.contains('SILVER');
      final isProof  = strikeType.contains('PROOF') && !strikeType.contains('REVERSE');
      return mintMark == 'S' && isSilver && !isProof;
    }

    // ── S-PROOF (clad or generic proof) ──────────────────────────────────────
    if (vId == 'S-PROOF' || vId == 'S-CLAD') {
      final isProof = strikeType.contains('PROOF') || varField.contains('PROOF');
      return mintMark == 'S' && isProof;
    }

    // ── Generic PROOF / specific mint proofs (W-PROOF, P-PROOF, etc.) ────────
    if (vId.contains('PROOF')) {
      final baseMint = vId.split('-').first;
      final isProof  = strikeType.contains('PROOF') || varField.contains('PROOF');
      if (baseMint.isNotEmpty && baseMint != 'S') {
        return mintMark == baseMint && isProof;
      }
      return isProof;
    }

    // ── Uncirculated standard mint marks (P, D, W, S, CC, O) ────────────────
    final baseMint = vId.split('-').first;
    if (mintMark == baseMint) return true;
    if (baseMint == 'P' && (mintMark.isEmpty || mintMark == 'NONE' || mintMark == 'PHILADELPHIA')) return true;

    return false;
  }

  /// Resolves the entire program inventory across coins, currency, and world_items subcollections.
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
