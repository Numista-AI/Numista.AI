import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';
import '../services/auth_service.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  MorganChatContext
//  ─────────────────
//  Loads the user's collection from Firestore and builds a plain-English
//  system-prompt snippet that Morgan uses as her "memory" in every chat.
//
//  Designed to be fast (cached for the session) and resilient (returns an
//  empty context gracefully if Firestore is offline or the collection is empty).
// ══════════════════════════════════════════════════════════════════════════════

class MorganCollectionContext {
  // ── Metrics ──────────────────────────────────────────────────────────────
  final int totalCoins;
  final double portfolioValue;   // sum of AI Estimated Value
  final double acquisitionCost;  // sum of Cost
  final double profit;           // portfolioValue - acquisitionCost

  // ── Breakdown ─────────────────────────────────────────────────────────────
  final List<String> topCoinsByValue;   // "1921 Morgan Silver Dollar — $225.00"
  final List<String> recentlyAdded;     // last 5 added
  final Map<String, int> byDenomination;
  final Map<String, int> bySeries;
  final Set<String> metals;
  final int gradeCount;  // coins with a numeric PCGS/NGC grade

  // ── Golden Schema Verification Indicators ──────────────────────────────────
  final int verifiedCount;       // coins with verification_confidence == HIGH or cert number
  final int unverifiedCount;     // unverified or self-entered coins

  // ── Owner ────────────────────────────────────────────────────────────────
  final String userName;

  const MorganCollectionContext({
    required this.totalCoins,
    required this.portfolioValue,
    required this.acquisitionCost,
    required this.profit,
    required this.topCoinsByValue,
    required this.recentlyAdded,
    required this.byDenomination,
    required this.bySeries,
    required this.metals,
    required this.gradeCount,
    required this.verifiedCount,
    required this.unverifiedCount,
    required this.userName,
  });

  bool get isEmpty => totalCoins == 0;

  // ── Build the system-prompt string (Max ~1,200 tokens) ─────────────────────
  String get systemPrompt {
    if (isEmpty) {
      return '''You are Morgan, an expert AI numismatic guide for Numista.AI.
Your user, $userName, is just getting started and has not yet added any coins.
Be warm, encouraging, and guide them through how to add their first coin.
Always speak in plain English — avoid jargon.
Keep responses concise (1-3 short paragraphs max).''';
    }

    final topList = topCoinsByValue.take(8).join('\n  • ');
    final recentList = recentlyAdded.take(5).join(', ');
    final denomList = byDenomination.entries
        .take(6)
        .map((e) => '${e.key}: ${e.value}')
        .join(', ');
    final seriesList = bySeries.entries
        .take(5)
        .map((e) => '${e.key}: ${e.value}')
        .join(', ');
    final metalList = metals.join(', ');
    final profitStr = profit >= 0
        ? '+\$${profit.toStringAsFixed(2)}'
        : '-\$${profit.abs().toStringAsFixed(2)}';

    return '''You are Morgan, an expert AI numismatic guide for Numista.AI.
You know $userName's coin collection intimately. Here is their current collection summary:

COLLECTION METRICS (GOLDEN SCHEMA VERIFIED):
  • Total Coins: $totalCoins ($verifiedCount Verified / PCGS/NGC Slabs, $unverifiedCount Self-Entered)
  • Estimated Portfolio Value: \$${portfolioValue.toStringAsFixed(2)}
  • Total Acquisition Cost: \$${acquisitionCost.toStringAsFixed(2)}
  • Portfolio P/L: $profitStr
  • Certified Graded Coins: $gradeCount

TOP COINS BY ESTIMATED VALUE:
  • $topList

RECENTLY ADDED:
  $recentList

SERIES & DENOMINATION BREAKDOWN:
  • Denominations: $denomList
  • Key Programs/Series: $seriesList
  • Metals Present: $metalList

INSTRUCTIONS & CONSTRAINTS:
  - Address the user as "$userName" naturally in conversation.
  - Rely on verified slab data for valuation statements when supporting estate planning queries.
  - Always speak in plain, friendly English — explain numismatic terms clearly.
  - Keep responses concise and focused (max 1-3 short paragraphs).
  - If asked about a coin not in the data, state clearly that it is not present in their collection catalog.
  - Use this collection data to answer any questions about their specific coins.
  - When asked "what is my most valuable coin?" use the TOP COINS list above.
  - Always speak in plain, friendly English — no jargon without explanation.
  - Keep responses helpful and concise (1-3 paragraphs max).
  - If a question is about a coin NOT in this data, say you don't see it and suggest they verify by browsing their collection.
  - You are warm, patient, and knowledgeable — like a trusted friend who happens to be a coin expert.''';
  }

  // ── Human-readable opening message ───────────────────────────────────────
  String get openingMessage {
    if (isEmpty) {
      return "Hi $userName! 👋 I'm Morgan, your personal coin guide. "
          "It looks like your collection is empty — let's fix that! "
          "Would you like me to walk you through adding your first coin?";
    }

    final profitStr = profit >= 0
        ? '📈 up \$${profit.toStringAsFixed(2)}'
        : '📉 down \$${profit.abs().toStringAsFixed(2)}';
    final topCoin = topCoinsByValue.isNotEmpty
        ? topCoinsByValue.first.split(' — ').first
        : 'some interesting pieces';

    return "Hi $userName! 👋 I've been looking at your collection — "
        "you've got **$totalCoins coins** worth about **\$${portfolioValue.toStringAsFixed(2)}** "
        "and you're $profitStr from what you paid. "
        "Your most valuable piece is **$topCoin**. "
        "What would you like to know?";
  }
}

// ── Service ───────────────────────────────────────────────────────────────────

class MorganChatContextService {
  MorganChatContextService._();

  /// Cached context for the current session.
  static MorganCollectionContext? _cache;

  /// Force a fresh reload on next call (e.g. after adding a new coin).
  static void invalidate() => _cache = null;

  static double _parseCurrency(dynamic value) {
    if (value == null) return 0.0;
    final raw = value.toString();
    if (raw == 'Pending' || raw.isEmpty) return 0.0;
    // Normalise all dash variants and strip commas
    final norm = raw
        .replaceAll(',', '')
        .replaceAll('\u2013', '-')   // en-dash
        .replaceAll('\u2014', '-')   // em-dash
        .replaceAll('\u2012', '-');  // figure dash
    // Match any range: "$15-$25", "$15 - $25", "15-25", etc. allowing optional leading $ or non-digits on second part
    final rangeMatch = RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    if (rangeMatch != null) {
      final a = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
      return a > 100000 ? 0.0 : a;   // sanity cap: skip runaway AI estimates
    }
    final v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    return v > 100000 ? 0.0 : v;         // sanity cap
  }

  /// Loads and caches the collection context.
  /// Returns an empty context on error (never throws).
  static Future<MorganCollectionContext> load({bool forceRefresh = false}) async {
    if (_cache != null && !forceRefresh) return _cache!;

    final user = FirebaseAuth.instance.currentUser;
    final userName = user?.displayName?.split(' ').first ??
        user?.email?.split('@').first ??
        'there';

    if (AuthService.isGuest) {
      _cache = _empty(userName);
      return _cache!;
    }

    try {
      final snap = await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .get();

      final docs = snap.docs;
      if (docs.isEmpty) {
        _cache = _empty(userName);
        return _cache!;
      }

      double portfolioValue = 0;
      double acquisitionCost = 0;
      int gradeCount = 0;
      int verifiedCount = 0;
      int unverifiedCount = 0;

      final Map<String, int> byDenomination = {};
      final Map<String, int> bySeries = {};
      final Set<String> metals = {};

      // Collect all docs with their parsed value for ranking
      final ranked = <Map<String, dynamic>>[];

      for (final doc in docs) {
        final data = doc.data();

        final value = _parseCurrency(data['AI Estimated Value']);
        final cost  = _parseCurrency(data['Cost']);
        portfolioValue  += value;
        acquisitionCost += cost;

        // Grade & Verification count
        final condition = data['Condition']?.toString() ?? '';
        final certNo = data['Certification Number']?.toString().trim() ?? '';
        final confidence = data['verification_confidence']?.toString().toUpperCase() ?? '';

        if (RegExp(r'\d{2,3}').hasMatch(condition)) gradeCount++;
        if (certNo.isNotEmpty || confidence == 'HIGH') {
          verifiedCount++;
        } else {
          unverifiedCount++;
        }

        // By denomination
        final denom = data['Denomination']?.toString().trim() ?? '';
        if (denom.isNotEmpty && denom != 'Multiple') {
          byDenomination[denom] = (byDenomination[denom] ?? 0) + 1;
        }

        // By series
        final series = data['Program/Series']?.toString().trim() ?? '';
        if (series.isNotEmpty && series != 'Multiple') {
          bySeries[series] = (bySeries[series] ?? 0) + 1;
        }

        // Metals
        final metal = data['Metal Content']?.toString().trim() ?? '';
        if (metal.isNotEmpty && metal != 'Multiple') {
          // Extract primary metal name (e.g. "90% Silver" → "Silver")
          final match = RegExp(r'[A-Z][a-z]+').firstMatch(metal);
          if (match != null) metals.add(match.group(0)!);
        }

        ranked.add({...data, '_parsedValue': value, '_docId': doc.id});
      }

      // Sort by value descending
      ranked.sort((a, b) =>
          (b['_parsedValue'] as double).compareTo(a['_parsedValue'] as double));

      // Build top coins list
      final topCoinsByValue = ranked.take(10).map((item) {
        final year   = item['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
        final mint   = item['Mint Mark']?.toString() ?? '';
        final series = item['Program/Series']?.toString() ?? '';
        final theme  = item['Theme/Subject']?.toString() ?? '';
        final denom  = item['Denomination']?.toString() ?? '';
        final value  = item['_parsedValue'] as double;

        final name = series.isNotEmpty && series != 'Multiple'
            ? series
            : theme.isNotEmpty && theme != 'Multiple'
                ? theme
                : denom.isNotEmpty
                    ? denom
                    : 'Coin';

        final yearMint = [
          if (year.isNotEmpty && year != 'Multiple') year,
          if (mint.isNotEmpty && mint != 'Multiple') mint,
        ].join('-');

        final label = yearMint.isNotEmpty ? '$yearMint $name' : name;
        return '$label — \$${value.toStringAsFixed(2)}';
      }).toList();

      // Sort by timestamp to get recently added
      final sorted = List.from(docs);
      sorted.sort((a, b) {
        final ad = a.data() as Map<String, dynamic>;
        final bd = b.data() as Map<String, dynamic>;
        final aTs = ad['Added'] ?? ad['timestamp'] ?? ad['created_at'];
        final bTs = bd['Added'] ?? bd['timestamp'] ?? bd['created_at'];
        if (aTs is Timestamp && bTs is Timestamp) return bTs.compareTo(aTs);
        if (aTs is Timestamp) return -1;
        if (bTs is Timestamp) return 1;
        return b.id.compareTo(a.id);
      });

      final recentlyAdded = sorted.take(5).map((doc) {
        final item = doc.data() as Map<String, dynamic>;
        final year   = item['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
        final series = item['Program/Series']?.toString() ?? '';
        final denom  = item['Denomination']?.toString() ?? '';
        final name = series.isNotEmpty && series != 'Multiple' ? series : denom;
        return year.isNotEmpty ? '$year $name' : name;
      }).where((s) => s.trim().isNotEmpty).toList();

      _cache = MorganCollectionContext(
        totalCoins: docs.length,
        portfolioValue: portfolioValue,
        acquisitionCost: acquisitionCost,
        profit: portfolioValue - acquisitionCost,
        topCoinsByValue: topCoinsByValue,
        recentlyAdded: recentlyAdded,
        byDenomination: byDenomination,
        bySeries: bySeries,
        metals: metals,
        gradeCount: gradeCount,
        verifiedCount: verifiedCount,
        unverifiedCount: unverifiedCount,
        userName: userName,
      );

      return _cache!;
    } catch (e) {
      debugPrint('[MorganChatContext] Error loading: $e');
      return _empty(userName);
    }
  }

  static MorganCollectionContext _empty(String userName) =>
      MorganCollectionContext(
        totalCoins: 0,
        portfolioValue: 0,
        acquisitionCost: 0,
        profit: 0,
        topCoinsByValue: [],
        recentlyAdded: [],
        byDenomination: {},
        bySeries: {},
        metals: {},
        gradeCount: 0,
        verifiedCount: 0,
        unverifiedCount: 0,
        userName: userName,
      );
}
