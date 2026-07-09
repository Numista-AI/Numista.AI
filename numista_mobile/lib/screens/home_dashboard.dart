import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart' as intl;
import 'package:cached_network_image/cached_network_image.dart';
import '../services/auth_service.dart';
import '../services/morgan_prefs.dart';
import '../services/guest_seed_service.dart';
import 'package:http/http.dart' as http;
import 'package:url_launcher/url_launcher.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;
import '../services/melt_value_service.dart';
import '../services/portfolio_snapshot_service.dart';
import '../services/batch_valuation_service.dart';
import '../services/valuation_mode_service.dart';
import '../widgets/portfolio_charts.dart';
import '../constants.dart';
import 'deals_screen.dart';

class HomeDashboard extends StatefulWidget {
  /// Called when the user taps "Ask Morgan" — routes to 'AI Deepdive'.
  final VoidCallback? onAskMorgan;
  /// Called when the user taps a Morgan suggestion chip — navigates to AI Deepdive
  /// with the given query pre-populated in the chat.
  final void Function(String query)? onAskMorganWithQuery;
  /// Called to navigate to My Collection (e.g. to run AI Valuation).
  final VoidCallback? onNavigateToCollection;
  const HomeDashboard({
    super.key,
    this.onAskMorgan,
    this.onAskMorganWithQuery,
    this.onNavigateToCollection,
  });

  @override
  State<HomeDashboard> createState() => _HomeDashboardState();
}

class CombinedDashboardData {
  final List<Map<String, dynamic>> coins;
  final List<Map<String, dynamic>> currency;
  final List<Map<String, dynamic>> worldItems;

  CombinedDashboardData({
    required this.coins,
    required this.currency,
    required this.worldItems,
  });
}

class _HomeDashboardState extends State<HomeDashboard> {
  Stream<CombinedDashboardData> _getCombinedStream() {
    final controller = StreamController<CombinedDashboardData>();
    List<Map<String, dynamic>> coins = [];
    List<Map<String, dynamic>> currency = [];
    List<Map<String, dynamic>> worldItems = [];

    StreamSubscription? subCoins;
    StreamSubscription? subCurrency;
    StreamSubscription? subWorldItems;

    void emit() {
      if (!controller.isClosed) {
        controller.add(CombinedDashboardData(
          coins: coins,
          currency: currency,
          worldItems: worldItems,
        ));
      }
    }

    final coinsStream = GuestSeedService.isBrowseDemoMode
        ? GuestSeedService.getDemoCoinsStream()
        : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
    subCoins = coinsStream.listen((snap) {
      coins = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
      emit();
    }, onError: (e) => controller.addError(e));

    final currencyStream = GuestSeedService.isBrowseDemoMode
        ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
        : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();
    subCurrency = currencyStream.listen((snap) {
      currency = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
      emit();
    }, onError: (e) => controller.addError(e));

    final worldItemsStream = GuestSeedService.isBrowseDemoMode
        ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
        : FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots();
    subWorldItems = worldItemsStream.listen((snap) {
      worldItems = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
      emit();
    }, onError: (e) => controller.addError(e));

    controller.onCancel = () {
      subCoins?.cancel();
      subCurrency?.cancel();
      subWorldItems?.cancel();
    };

    return controller.stream;
  }

  Map<String, double> _spotPrices = {};
  bool _isLoadingPrices = true;
  DateTime? _pricesLastUpdated;
  List<dynamic> _news = [];
  bool _isLoadingNews = true;
  Set<String> _dismissedNewsIds = {};

  // ── Portfolio Insights state ───────────────────────────────────────────
  List<PortfolioSnapshot> _snapshots = [];

  // ── Batch Valuation state ──────────────────────────────────────────────
  BatchValuationProgress _valuation = const BatchValuationProgress();
  StreamSubscription<BatchValuationProgress>? _valuationSub;

  @override
  void initState() {
    super.initState();
    _fetchSpotPrices();
    _fetchNews();
    _loadDismissedNews();
    // Listen to batch valuation progress so the dashboard updates live
    _valuationSub = BatchValuationService.instance.progressStream.listen((p) {
      if (mounted) setState(() => _valuation = p);
    });
    // Sync current state in case service was already running
    _valuation = BatchValuationService.instance.current;
    // Restore persisted progress so Resume banner appears after page refresh
    BatchValuationService.instance.restoreFromFirestore();
  }

  @override
  void dispose() {
    _valuationSub?.cancel();
    super.dispose();
  }

  /// Computes a stable, deterministic article ID from a URL.
  /// Dart's String.hashCode is randomized each app start since Dart 2.x,
  /// so we use a simple djb2-style hash instead — same URL → same ID always.
  static String _stableArticleId(String url) {
    // Normalize: strip trailing slash and query params so equivalent URLs match.
    final normalized = Uri.tryParse(url)?.replace(queryParameters: {}).toString()
        ?? url;
    int hash = 5381;
    for (final c in normalized.codeUnits) {
      hash = ((hash << 5) + hash + c) & 0x7FFFFFFF;
    }
    return hash.toRadixString(16);
  }

  Future<void> _fetchNews({bool isRefresh = false}) async {
    // On refresh: show the shimmer bar but keep old articles visible — don't
    // clear _news until we have a successful response.  This prevents a blank
    // list + possible index-out-of-bounds crash during the in-flight period.
    if (!isRefresh) {
      if (mounted) setState(() => _isLoadingNews = true);
    }
    try {
      final response = await http.get(
          Uri.parse('$kApiBaseUrl/api/mint_news'));
      if (!mounted) return;
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _news = List<dynamic>.from(data['news'] ?? []);
          _isLoadingNews = false;
        });
      } else {
        setState(() => _isLoadingNews = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingNews = false);
    }
  }
  Future<void> _loadDismissedNews() async {
    try {
      final userEmail = AuthService.userEmail;

      if (userEmail.isEmpty) return;
      final resp = await http.get(
          Uri.parse('$kApiBaseUrl/api/dismissed_news/$userEmail'));
      if (!mounted) return;
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final ids = List<String>.from(data['ids'] ?? []);
        setState(() => _dismissedNewsIds = ids.toSet());
      }
    } catch (_) {}
  }

  Future<void> _dismissArticle(String articleId) async {
    // Immediately remove from view
    setState(() => _dismissedNewsIds.add(articleId));
    try {
      final userEmail = AuthService.userEmail;

      if (userEmail.isEmpty) return;
      await http.post(
        Uri.parse('$kApiBaseUrl/api/dismiss_news'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'user_email': userEmail, 'article_id': articleId}),
      );
    } catch (_) {}
  }


  Future<void> _fetchSpotPrices() async {

    try {
      final response = await http.get(
          Uri.parse('$kApiBaseUrl/api/spot_prices'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _spotPrices = {
            'Gold':      (data['Gold']      ?? 0).toDouble(),
            'Silver':    (data['Silver']    ?? 0).toDouble(),
            'Platinum':  (data['Platinum']  ?? 0).toDouble(),
            'Palladium': (data['Palladium'] ?? 0).toDouble(),
          };
          _isLoadingPrices = false;
          _pricesLastUpdated = DateTime.now();
        });
      } else {
        if (!mounted) return;
        setState(() => _isLoadingPrices = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingPrices = false);
    }
  }


  double _parseCurrency(dynamic value) {
    if (value == null) return 0.0;
    final raw  = value.toString();
    if (raw == 'Pending' || raw.isEmpty) return 0.0;
    // Normalise all dash variants and strip commas
    final norm = raw
        .replaceAll('\u2013', '-')   // en-dash
        .replaceAll('\u2014', '-')   // em-dash
        .replaceAll('\u2012', '-')   // figure dash
        .replaceAll(',', '');
    // Match any range: "$15-$25", "$15 - $25", "15-25", etc. allowing optional leading $ or non-digits on second part
    final rangeMatch = RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    if (rangeMatch != null) {
      final a = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
      return a > 100000 ? 0.0 : a;   // sanity cap: skip runaway AI estimates
    }
    final v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    return v > 100000 ? 0.0 : v;
  }


  static double _computeFaceValue(String denom) {
    final s = denom.toLowerCase().trim();
    // ── Word-based matches (unambiguous) ─────────────────────────────────────
    if (s.contains('penny')   || s.contains('cent')   || s.contains('1c'))  return 0.01;
    if (s.contains('nickel')  || s.contains('5c'))                           return 0.05;
    if (s.contains('dime')    || s.contains('10c'))                          return 0.10;
    if (s.contains('quarter') || s.contains('25c'))                          return 0.25;
    if (s.contains('half')    || s.contains('50c'))                          return 0.50;
    // ── Dollar-sign matches: MUST go largest → smallest to prevent
    // ── substring collisions (e.g. "$10" contains "$1" → wrong match) ────────
    if (s.contains(r'$500'))  return 500.00;  // 1oz gold bar / commemorative
    if (s.contains(r'$100'))  return 100.00;  // high-denomination gold
    if (s.contains(r'$50'))   return 50.00;   // $50 Buffalo / gold eagle
    if (s.contains(r'$25'))   return 25.00;   // $25 half-oz gold eagle
    if (s.contains(r'$20'))   return 20.00;   // Saint-Gaudens / Liberty double eagle
    if (s.contains(r'$10'))   return 10.00;   // Liberty / Indian Head gold eagle
    if (s.contains(r'$5'))    return 5.00;    // Half eagle
    if (s.contains(r'$2.50')) return 2.50;    // Quarter eagle
    if (s.contains(r'$3'))    return 3.00;    // Three-dollar gold piece
    if (s.contains(r'$2'))    return 2.00;    // Two-dollar note / $2 gold
    if (s.contains('dollar')  || s.contains(r'$1')) return 1.00;
    // ── Numeric fallback: "1" → 1.00, "0.25" → 0.25 ─────────────────────────
    // Handles plain-number denominations stored by PCGS import or legacy CSV.
    final n = double.tryParse(s.replaceAll(r'$', '').trim());
    if (n != null) return n;
    return 0.00;
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, outerConstraints) {
        return StreamBuilder<CombinedDashboardData>(
          stream: _getCombinedStream(),
          builder: (context, snapshot) {
            // Only show the spinner on the very first load (no cached data).
            // On subsequent Firestore updates keep showing the last known
            // content so the widget tree is not blanked between updates.
            if (!snapshot.hasData && snapshot.connectionState == ConnectionState.waiting) {
              return const Center(
                  child: CircularProgressIndicator(color: Color(0xFFF63366)));
            }
            if (snapshot.hasError) {
              return Center(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(mainAxisSize: MainAxisSize.min, children: const [
                    Icon(Icons.cloud_off_rounded, size: 48, color: Color(0xFFE53935)),
                    SizedBox(height: 16),
                    Text('Dashboard unavailable',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700,
                            color: Color(0xFF31333F))),
                    SizedBox(height: 8),
                    Text('Check your connection and refresh the page.',
                        textAlign: TextAlign.center,
                        style: TextStyle(color: Color(0xFF5A5C69))),
                  ]),
                ),
              );
            }

            final coins = snapshot.data?.coins ?? [];
            final currency = snapshot.data?.currency ?? [];
            final worldItems = snapshot.data?.worldItems ?? [];

            // ── Compute portfolio metrics ──────────────────────────────────
            int totalItems = coins.length + currency.length + worldItems.length;
            double cpgTotal = 0;
            // ignore: unused_local_variable
            double bidTotal = 0;
            // ignore: unused_local_variable
            double askTotal = 0;
            double acquisitionCost = 0;
            double meltValue       = 0;
            double faceValue       = 0;

            // ignore: unused_local_variable
            double coinsVal = 0;
            // ignore: unused_local_variable
            double currencyVal = 0;
            // ignore: unused_local_variable
            double medalsVal = 0;
            // ignore: unused_local_variable
            double othersVal = 0;

            Map<String, double> programValues = {};

            // 1. Process Coins collection
            for (final data in coins) {
              final valStr = data['AI Estimated Value'];
              final coinValue = _parseCurrency(valStr);

              // Melt Value
              final liveMelt = _spotPrices.isNotEmpty
                  ? (MeltValueService.compute(
                        metalContent: data['Metal Content']?.toString() ?? '',
                        denomination: data['Denomination']?.toString() ?? '',
                        spotPrices: _spotPrices,
                      ) ?? 0.0)
                  : _parseCurrency(data['Melt Value']);
              
              final finalVal = math.max(coinValue, liveMelt);

              // Classification
              final itemType = (data['item_type'] ?? '').toString().toLowerCase();
              final prog = (data['Program/Series'] ?? '').toString().toLowerCase();
              final desc = (data['description'] ?? '').toString().toLowerCase();
              final theme = (data['Theme/Subject'] ?? '').toString().toLowerCase();

              final isMedal = itemType.contains('medal') || prog.contains('medal') || desc.contains('medal') || theme.contains('medal');
              final isCurrency = itemType == 'paper_currency';

              if (isMedal) {
                medalsVal += finalVal;
              } else if (isCurrency) {
                currencyVal += finalVal;
              } else {
                coinsVal += finalVal;
              }

              // Greysheet fields
              final coinCpg = (data['cpgRetail'] as num?)?.toDouble() ?? 0.0;
              final coinBid = (data['greysheetBid'] as num?)?.toDouble() ?? 0.0;
              final coinAsk = (data['greysheetAsk'] as num?)?.toDouble() ?? 0.0;

              final finalCpg = coinCpg > 0 ? coinCpg : finalVal;
              final finalBid = coinBid > 0 ? coinBid : finalVal * 0.80;
              final finalAsk = coinAsk > 0 ? coinAsk : finalVal * 0.92;

              cpgTotal += finalCpg;
              bidTotal += finalBid;
              askTotal += finalAsk;
              acquisitionCost += _parseCurrency(data['Cost']);
              meltValue       += liveMelt;
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');

              // Track per-program value for the bar chart
              final program = data['Program/Series']?.toString() ?? 'Other';
              programValues[program] = (programValues[program] ?? 0) + finalCpg;
            }

            // 2. Process Currency collection
            for (final data in currency) {
              final rawAi = data['AI Estimated Value'];
              double finalVal = 0.0;
              if (rawAi != null && rawAi != 'None' && rawAi != 'Pending' && rawAi.toString().isNotEmpty) {
                finalVal = _parseCurrency(rawAi);
              } else {
                finalVal = _parseCurrency(data['Cost']);
              }

              final curCpg = (data['cpgRetail'] as num?)?.toDouble() ?? 0.0;
              final curBid = (data['greysheetBid'] as num?)?.toDouble() ?? 0.0;
              final curAsk = (data['greysheetAsk'] as num?)?.toDouble() ?? 0.0;

              cpgTotal += curCpg > 0 ? curCpg : finalVal;
              bidTotal += curBid > 0 ? curBid : finalVal * 0.80;
              askTotal += curAsk > 0 ? curAsk : finalVal * 0.92;

              currencyVal += finalVal;
              acquisitionCost += _parseCurrency(data['Cost']);
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');
            }

            // 3. Process World Items collection
            for (final data in worldItems) {
              final estVal = (data['estimated_value'] as num?)?.toDouble() ?? 0.0;
              final purchPrice = (data['purchase_price'] as num?)?.toDouble() ?? 0.0;
              final finalVal = estVal > 0 ? estVal : purchPrice;

              final catStr = (data['item_type'] ?? '').toString().toLowerCase();
              final name = (data['name'] ?? '').toString().toLowerCase();
              final notes = (data['notes'] ?? '').toString().toLowerCase();

              final isMedal = catStr.contains('medal') || name.contains('medal') || notes.contains('medal');

              if (isMedal) {
                medalsVal += finalVal;
              } else if (catStr == 'banknote') {
                currencyVal += finalVal;
              } else if (catStr == 'coin') {
                coinsVal += finalVal;
              } else {
                othersVal += finalVal;
              }

              final wCpg = (data['cpgRetail'] as num?)?.toDouble() ?? 0.0;
              final wBid = (data['greysheetBid'] as num?)?.toDouble() ?? 0.0;
              final wAsk = (data['greysheetAsk'] as num?)?.toDouble() ?? 0.0;

              cpgTotal += wCpg > 0 ? wCpg : finalVal;
              bidTotal += wBid > 0 ? wBid : finalVal * 0.80;
              askTotal += wAsk > 0 ? wAsk : finalVal * 0.92;

              acquisitionCost += purchPrice;
              final spotEntry = (data['spot_value_at_entry'] as num?)?.toDouble() ?? 0.0;
              if (spotEntry > 0) {
                meltValue += spotEntry;
              }
              faceValue += _computeFaceValue(data['denomination']?.toString() ?? '');
            }

            final portfolioValue = cpgTotal;

            // ── Portfolio snapshot (fire-and-forget) ───────────────────────
            if (totalItems > 0) {
              PortfolioSnapshotService.maybeTakeSnapshot(
                totalCoins: totalItems,
                portfolioValue: portfolioValue,
                meltValue: meltValue,
                acquisitionCost: acquisitionCost,
                faceValue: faceValue,
              );
              // Load historical snapshots for the line chart
              PortfolioSnapshotService.getSnapshots().then((snaps) {
                if (mounted) setState(() => _snapshots = snaps);
              });
            }

            // ── Last 3 added (using coins) ──────────────────────────────────
            final sorted = List<Map<String, dynamic>>.from(coins);
            sorted.sort((a, b) {
              final aTs = a['Added'] ?? a['timestamp'] ?? a['created_at'];
              final bTs = b['Added'] ?? b['timestamp'] ?? b['created_at'];

              final aHas = aTs is Timestamp;
              final bHas = bTs is Timestamp;

              if (aHas && bHas) return bTs.compareTo(aTs);
              if (aHas && !bHas) return -1;
              if (!aHas && bHas) return 1;
              return (b['id']?.toString() ?? '').compareTo(a['id']?.toString() ?? '');
            });
            final last5 = sorted.take(5).toList();

            final fmt = intl.NumberFormat.currency(symbol: '\$');
            final lastAdded = last5.isNotEmpty ? last5.first : null;
            // Determine gold/silver for the summary card
            final goldPrice = _spotPrices['Gold'] ?? 0.0;
            final silverPrice = _spotPrices['Silver'] ?? 0.0;
            final profit = portfolioValue - acquisitionCost;
            final profitPositive = profit >= 0;

            return LayoutBuilder(builder: (ctx, bc) {
              final isWide = bc.maxWidth >= 820;
              return SingleChildScrollView(
                padding: EdgeInsets.all(isWide ? 32 : 20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [

                    // ── Greeting header ─────────────────────────────────────
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.center,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              FutureBuilder<String>(
                                future: Future.value(
                                    FirebaseAuth.instance.currentUser
                                        ?.displayName?.split(' ').first ??
                                    FirebaseAuth.instance.currentUser
                                        ?.email?.split('@').first ??
                                    'Collector'),
                                builder: (ctx, snap) => Text(
                                  'Good to see you, ${snap.data ?? ''}!',
                                  style: const TextStyle(
                                    fontSize: 22,
                                    fontWeight: FontWeight.w800,
                                    color: Color(0xFF0F172A),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 4),
                              Text(
                                totalItems == 0
                                    ? 'Your collection is empty — add your first coin!'
                                    : 'Your collection has $totalItems item${totalItems == 1 ? '' : 's'}.',
                                style: const TextStyle(
                                    fontSize: 15, color: Color(0xFF64748B)),
                              ),
                            ],
                          ),
                        ),
                        // Version pill — subtle
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF0FDF4),
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(color: const Color(0xFF86EFAC)),
                          ),
                          child: const Text('v3.9',
                              style: TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF166534))),
                        ),
                      ],
                    ),
                    const SizedBox(height: 28),

                    // ── 3 Summary Cards ─────────────────────────────────────
                    isWide
                        ? Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Expanded(child: _buildPortfolioCard(portfolioValue, profit, profitPositive, fmt)),
                              const SizedBox(width: 16),
                              Expanded(child: _buildMetalPricesCard(goldPrice, silverPrice, fmt)),
                              const SizedBox(width: 16),
                              Expanded(child: _buildLastAddedCard(lastAdded)),
                            ],
                          )
                        : Column(
                            children: [
                              _buildPortfolioCard(portfolioValue, profit, profitPositive, fmt),
                              const SizedBox(height: 12),
                              _buildMetalPricesCard(goldPrice, silverPrice, fmt),
                              const SizedBox(height: 12),
                              _buildLastAddedCard(lastAdded),
                            ],
                          ),
                    const SizedBox(height: 36),

                    // ── What would you like to do? ──────────────────────────
                    const Text(
                      'What would you like to do?',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 14),

                    _DashboardActionButton(
                      icon: Icons.add_circle_rounded,
                      iconColor: const Color(0xFFF63366),
                      label: 'Add to My Collection',
                      subtitle: 'Photo, PDF receipt, or type it in — I\'ll help',
                      onTap: widget.onNavigateToCollection == null
                          ? null
                          : () {
                              // Navigate to Add New Coins
                              // We signal parent via a special query or direct
                            },
                      heroTag: 'dash_add',
                    ),
                    const SizedBox(height: 10),

                    _DashboardActionButton(
                      icon: Icons.camera_alt_rounded,
                      iconColor: const Color(0xFF0D9488),
                      label: 'Identify a Coin',
                      subtitle: 'Take a photo — Morgan will tell you what it is',
                      onTap: null, // handled by parent nav via sidebar
                      heroTag: 'dash_scan',
                    ),
                    const SizedBox(height: 10),

                    _DashboardActionButton(
                      icon: Icons.collections_bookmark_rounded,
                      iconColor: const Color(0xFF4F46E5),
                      label: 'Browse My Collection',
                      subtitle: 'See, filter, and manage everything you own',
                      onTap: widget.onNavigateToCollection,
                      heroTag: 'dash_browse',
                    ),
                    const SizedBox(height: 10),

                    _DashboardActionButton(
                      icon: Icons.manage_search_rounded,
                      iconColor: const Color(0xFFF59E0B),
                      label: 'Look Up a Coin\'s Value',
                      subtitle: 'Search by name, series, or year',
                      onTap: widget.onAskMorganWithQuery == null
                          ? null
                          : () => widget.onAskMorganWithQuery!(
                              'What is the current value of '),
                      heroTag: 'dash_lookup',
                    ),
                    const SizedBox(height: 36),

                    // ── More Details: portfolio metrics & charts (collapsible) ─
                    _ExpandableSection(
                      title: 'Portfolio Details',
                      subtitle: 'Value, profit/loss, melt value, charts',
                      icon: Icons.bar_chart_rounded,
                      child: Column(children: [
                        const SizedBox(height: 16),
                        // Metric cards
                        Wrap(
                          spacing: 12,
                          runSpacing: 12,
                          children: [
                            _metricCardFlex('Total Items', totalItems.toString()),
                            _metricCardFlex('Acquisition Cost', fmt.format(acquisitionCost)),
                            _metricCardFlex('Melt Value', fmt.format(meltValue)),
                            _metricCardFlex('Face Value', fmt.format(faceValue)),
                            _metricCardFlex(
                                'Profit / Loss',
                                (profit >= 0 ? '+' : '') + fmt.format(profit),
                                valueColor: profitPositive
                                    ? const Color(0xFF0F9D58)
                                    : const Color(0xFFE53935)),
                          ],
                        ),
                        const SizedBox(height: 20),
                        PortfolioChartsPanel(
                          portfolioValue: portfolioValue,
                          meltValue: meltValue,
                          acquisitionCost: acquisitionCost,
                          programValues: programValues,
                          snapshots: _snapshots,
                        ),
                      ]),
                    ),
                    const SizedBox(height: 16),

                    // ── Recently Added (collapsible) ────────────────────────
                    if (last5.isNotEmpty)
                      _ExpandableSection(
                        title: 'Recently Added',
                        subtitle: 'Your last ${last5.length} items',
                        icon: Icons.history_rounded,
                        child: Column(children: [
                          const SizedBox(height: 10),
                          Container(
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: const Color(0xFFE2E6E9)),
                            ),
                            child: Column(
                              children: last5.asMap().entries.map((entry) {
                                final data = entry.value;
                                final year = data['Year']?.toString()
                                        .replaceAll(RegExp(r'\.0$'), '') ??
                                    '';
                                final series = data['Program/Series']?.toString() ?? '';
                                final theme = data['Theme/Subject']?.toString() ?? '';
                                final denom = data['Denomination']?.toString() ?? '';
                                final estVal = data['AI Estimated Value']?.toString() ?? '—';
                                final coinName = series.isNotEmpty && series != 'Multiple'
                                    ? series
                                    : theme.isNotEmpty && theme != 'Multiple'
                                        ? theme
                                        : denom.isNotEmpty ? denom : 'Coin';
                                return Column(children: [
                                  if (entry.key > 0)
                                    const Divider(height: 1, color: Color(0xFFE2E6E9)),
                                  ListTile(
                                    dense: true,
                                    contentPadding: const EdgeInsets.symmetric(
                                        horizontal: 16, vertical: 6),
                                    leading: _CoinThumbnail(
                                      imageUrl: data['image_url_obverse']?.toString()
                                          ?? data['imageUrlObverse']?.toString(),
                                    ),
                                    title: Text(coinName,
                                        overflow: TextOverflow.ellipsis,
                                        style: const TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w600,
                                            color: Color(0xFF1E293B))),
                                    subtitle: year.isNotEmpty
                                        ? Text(year,
                                            style: const TextStyle(
                                                fontSize: 12,
                                                color: Color(0xFF64748B)))
                                        : null,
                                    trailing: Text(estVal,
                                        style: const TextStyle(
                                            fontSize: 14,
                                            fontWeight: FontWeight.w700,
                                            color: Color(0xFF0F9D58))),
                                  ),
                                ]);
                              }).toList(),
                            ),
                          ),
                        ]),
                      ),
                    const SizedBox(height: 16),

                    // ── Coin News (collapsible, collapsed by default) ───────
                    _ExpandableSection(
                      title: 'Coin & Market News',
                      subtitle: 'Latest numismatic headlines',
                      icon: Icons.newspaper_rounded,
                      initiallyExpanded: false,
                      child: Column(children: [
                        const SizedBox(height: 12),
                        if (_isLoadingNews)
                          const SizedBox(
                              height: 4,
                              child: LinearProgressIndicator(
                                  color: Color(0xFF3B82F6)))
                        else if (_news.isEmpty)
                          Container(
                            width: double.infinity,
                            padding: const EdgeInsets.symmetric(
                                vertical: 20, horizontal: 16),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF8FAFC),
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(
                                  color: const Color(0xFFE2E6E9)),
                            ),
                            child: const Column(children: [
                              Icon(Icons.wifi_off_outlined,
                                  size: 28, color: Color(0xFFCBD5E1)),
                              SizedBox(height: 8),
                              Text(
                                'Market news unavailable right now — check back shortly.',
                                textAlign: TextAlign.center,
                                style: TextStyle(
                                    fontSize: 13,
                                    color: Color(0xFF94A3B8)),
                              ),
                            ]),
                          )
                        else
                          SizedBox(
                            height: 158,
                            child: Builder(builder: (context) {
                              final visibleNews = _news
                                  .whereType<Map<String, dynamic>>()
                                  .where((item) {
                                final link = item['link']?.toString() ?? '';
                                final id = link.isNotEmpty
                                    ? _stableArticleId(link)
                                    : '';
                                return id.isEmpty ||
                                    !_dismissedNewsIds.contains(id);
                              }).toList();
                              return ListView.builder(
                                scrollDirection: Axis.horizontal,
                                itemCount: visibleNews.length,
                                itemBuilder: (ctx, i) {
                                  final item = visibleNews[i];
                                  final link =
                                      item['link']?.toString() ?? '';
                                  final articleId = link.isNotEmpty
                                      ? _stableArticleId(link)
                                      : '';
                                  return GestureDetector(
                                    onTap: link.isNotEmpty
                                        ? () async {
                                            final uri = Uri.parse(link);
                                            if (await canLaunchUrl(uri)) {
                                              await launchUrl(uri,
                                                  mode: LaunchMode
                                                      .externalApplication);
                                            }
                                          }
                                        : null,
                                    child: MouseRegion(
                                      cursor: link.isNotEmpty
                                          ? SystemMouseCursors.click
                                          : MouseCursor.defer,
                                      child: Container(
                                        width: 270,
                                        margin: const EdgeInsets.only(
                                            right: 12),
                                        padding: const EdgeInsets.all(14),
                                        decoration: BoxDecoration(
                                          color: Colors.white,
                                          borderRadius:
                                              BorderRadius.circular(10),
                                          border: Border.all(
                                              color: const Color(0xFFE2E6E9)),
                                          boxShadow: [
                                            BoxShadow(
                                              color: Colors.black
                                                  .withValues(alpha: 0.03),
                                              blurRadius: 4,
                                              offset: const Offset(0, 2),
                                            )
                                          ],
                                        ),
                                        child: Column(
                                          crossAxisAlignment:
                                              CrossAxisAlignment.start,
                                          children: [
                                            Row(children: [
                                              Expanded(
                                                child: Text(
                                                  item['source']
                                                          ?.toString() ??
                                                      'News',
                                                  overflow:
                                                      TextOverflow.ellipsis,
                                                  style: const TextStyle(
                                                      fontSize: 10,
                                                      fontWeight:
                                                          FontWeight.bold,
                                                      color: Color(
                                                          0xFF3B82F6)),
                                                ),
                                              ),
                                              Text(
                                                item['published']
                                                        ?.toString() ??
                                                    '',
                                                style: const TextStyle(
                                                    fontSize: 10,
                                                    color: Color(0xFF94A3B8)),
                                              ),
                                            ]),
                                            const SizedBox(height: 5),
                                            Text(
                                              item['title']?.toString() ??
                                                  '',
                                              maxLines: 2,
                                              overflow: TextOverflow.ellipsis,
                                              style: const TextStyle(
                                                  fontSize: 13,
                                                  fontWeight: FontWeight.w700,
                                                  color: Color(0xFF1E293B)),
                                            ),
                                            const SizedBox(height: 5),
                                            Expanded(
                                              child: Text(
                                                item['summary']
                                                        ?.toString() ??
                                                    '',
                                                maxLines: 3,
                                                overflow: TextOverflow.ellipsis,
                                                style: const TextStyle(
                                                    fontSize: 11,
                                                    color: Color(0xFF64748B),
                                                    height: 1.4),
                                              ),
                                            ),
                                            Row(
                                              mainAxisAlignment:
                                                  MainAxisAlignment
                                                      .spaceBetween,
                                              children: [
                                                if (link.isNotEmpty)
                                                  const Row(
                                                    mainAxisSize:
                                                        MainAxisSize.min,
                                                    children: [
                                                      Text('Read more',
                                                          style: TextStyle(
                                                              fontSize: 10,
                                                              color: Color(
                                                                  0xFF3B82F6),
                                                              fontWeight:
                                                                  FontWeight
                                                                      .w600)),
                                                      SizedBox(width: 2),
                                                      Icon(
                                                          Icons
                                                              .arrow_forward_ios,
                                                          size: 9,
                                                          color: Color(
                                                              0xFF3B82F6)),
                                                    ],
                                                  )
                                                else
                                                  const SizedBox.shrink(),
                                                if (articleId.isNotEmpty)
                                                  GestureDetector(
                                                    onTap: () =>
                                                        _dismissArticle(
                                                            articleId),
                                                    child: const Tooltip(
                                                      message:
                                                          'Not relevant — hide this article',
                                                      child: Icon(
                                                        Icons
                                                            .thumb_down_outlined,
                                                        size: 13,
                                                        color: Color(
                                                            0xFFCBD5E1),
                                                      ),
                                                    ),
                                                  ),
                                              ],
                                            ),
                                          ],
                                        ),
                                      ),
                                    ),
                                  );
                                },
                              );
                            }),
                          ),
                      ]),
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              );
            });
          },
        );
      },
    );
  }

  // ── Portfolio summary card ───────────────────────────────────────────────────
  Widget _buildPortfolioCard(
      double value, double profit, bool positive, intl.NumberFormat fmt) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF0F9D58).withAlpha(20),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.account_balance_wallet_rounded,
                  color: Color(0xFF0F9D58), size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Portfolio Value',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF64748B))),
          ]),
          const SizedBox(height: 12),
          FutureBuilder<bool>(
            future: ValuationModeService.isAdvancedMode(),
            builder: (context, snap) {
              final advanced = snap.data ?? false;
              return _buildPortfolioValueSection(
                  value,
                  value * 0.8, // bid approximation shown inside
                  value * 0.92,
                  fmt,
                  0,
                  advanced: advanced);
            },
          ),
          if (profit != 0) ...{
            const SizedBox(height: 8),
            Row(children: [
              Icon(
                positive
                    ? Icons.trending_up_rounded
                    : Icons.trending_down_rounded,
                color: positive
                    ? const Color(0xFF0F9D58)
                    : const Color(0xFFE53935),
                size: 16,
              ),
              const SizedBox(width: 4),
              Text(
                '${positive ? '+' : ''}${fmt.format(profit)} vs. cost',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: positive
                        ? const Color(0xFF0F9D58)
                        : const Color(0xFFE53935)),
              ),
            ]),
          },
        ],
      ),
    );
  }

  // ── Metal prices summary card ────────────────────────────────────────────────
  Widget _buildMetalPricesCard(
      double gold, double silver, intl.NumberFormat fmt) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFFFFD700).withAlpha(30),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.show_chart_rounded,
                  color: Color(0xFFB8860B), size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Today\'s Metal Prices',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF64748B))),
          ]),
          const SizedBox(height: 14),
          if (_isLoadingPrices)
            const SizedBox(
                height: 4,
                child: LinearProgressIndicator(color: Color(0xFFD4A843)))
          else if (gold > 0) ...{
            _metalPriceLine('Gold (oz)', fmt.format(gold), const Color(0xFFB8860B)),
            const SizedBox(height: 8),
            _metalPriceLine('Silver (oz)', fmt.format(silver), const Color(0xFF64748B)),
          } else
            const Text('Prices unavailable',
                style: TextStyle(fontSize: 13, color: Color(0xFF94A3B8))),
          if (_pricesLastUpdated != null) ...{
            const SizedBox(height: 10),
            Text(
              'Updated ${intl.DateFormat('h:mm a').format(_pricesLastUpdated!.toLocal())}',
              style: const TextStyle(fontSize: 10, color: Color(0xFFCBD5E1)),
            ),
          },
        ],
      ),
    );
  }

  Widget _metalPriceLine(String label, String price, Color color) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label,
            style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w500,
                color: color.withAlpha(200))),
        Text(price,
            style: TextStyle(
                fontSize: 15,
                fontWeight: FontWeight.w800,
                color: color)),
      ],
    );
  }

  // ── Last added summary card ──────────────────────────────────────────────────
  Widget _buildLastAddedCard(Map<String, dynamic>? coin) {
    if (coin == null) {
      return Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: const Color(0xFFE2E6E9)),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withValues(alpha: 0.04),
                blurRadius: 8,
                offset: const Offset(0, 2))
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF4F46E5).withAlpha(20),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.add_circle_rounded,
                    color: Color(0xFF4F46E5), size: 18),
              ),
              const SizedBox(width: 8),
              const Text('Last Added',
                  style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF64748B))),
            ]),
            const SizedBox(height: 16),
            const Text('No coins yet',
                style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF1E293B))),
            const SizedBox(height: 4),
            const Text('Add your first coin to get started.',
                style: TextStyle(fontSize: 13, color: Color(0xFF94A3B8))),
          ],
        ),
      );
    }

    final series = coin['Program/Series']?.toString() ?? '';
    final theme = coin['Theme/Subject']?.toString() ?? '';
    final denom = coin['Denomination']?.toString() ?? '';
    final year = coin['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final coinName = series.isNotEmpty && series != 'Multiple'
        ? series
        : theme.isNotEmpty && theme != 'Multiple'
            ? theme
            : denom.isNotEmpty
                ? denom
                : 'Coin';
    final estVal = coin['AI Estimated Value']?.toString() ?? '—';
    final imageUrl = coin['image_url_obverse']?.toString()
        ?? coin['imageUrlObverse']?.toString();

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2))
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF4F46E5).withAlpha(20),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.history_rounded,
                  color: Color(0xFF4F46E5), size: 18),
            ),
            const SizedBox(width: 8),
            const Text('Last Added',
                style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFF64748B))),
          ]),
          const SizedBox(height: 14),
          Row(
            children: [
              if (imageUrl != null && imageUrl.isNotEmpty)
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: CachedNetworkImage(
                    imageUrl: imageUrl,
                    width: 46,
                    height: 46,
                    fit: BoxFit.cover,
                    errorWidget: (ctx, url, err) => Container(
                      width: 46,
                      height: 46,
                      decoration: BoxDecoration(
                        color: const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Icon(Icons.monetization_on_outlined,
                          color: Color(0xFFCBD5E1), size: 26),
                    ),
                  ),
                )
              else
                Container(
                  width: 46,
                  height: 46,
                  decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: const Icon(Icons.monetization_on_outlined,
                      color: Color(0xFFCBD5E1), size: 26),
                ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(coinName,
                        overflow: TextOverflow.ellipsis,
                        style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF1E293B))),
                    if (year.isNotEmpty)
                      Text(year,
                          style: const TextStyle(
                              fontSize: 12, color: Color(0xFF64748B))),
                    Text(estVal,
                        style: const TextStyle(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF0F9D58))),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }



  // ── Portfolio value section with batch valuation progress ───────────────────
  Widget _buildPortfolioValueSection(
      double cpgTotal, double bidTotal, double askTotal, intl.NumberFormat fmt, int totalCoins, {bool advanced = false}) {
    final v = _valuation;
    final displayVal  = advanced ? cpgTotal : bidTotal;
    final hasValue    = displayVal > 0;
    final isRunning   = v.isRunning;
    final isPaused    = v.isPaused;
    final hasProgress = v.completed > 0 || v.failed > 0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Text(advanced ? 'EST. PORTFOLIO VALUE (RETAIL)' : 'EST. PORTFOLIO VALUE (ESTATE/LIQ)',
            style: const TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.w600,
                color: Color(0xFF5A5C69))),
        const SizedBox(height: 2),

        // ── Main value display ──────────────────────────────────────────────
        if (hasValue)
          Text(fmt.format(displayVal),
              style: const TextStyle(
                  fontSize: 26,
                  fontWeight: FontWeight.w900,
                  color: Color(0xFF0F9D58)))
        else if (isRunning)
          Text(
            hasProgress ? '${fmt.format(displayVal)} (est.)' : 'Valuing\u2026',
            style: const TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w900,
                color: Color(0xFF0F9D58)),
          )
        else
          const Text('Pending AI Valuation',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF9CA3AF))),

        if (hasValue && advanced) ...[
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Text('Bid: ${fmt.format(bidTotal)}',
                  style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF4A5568))),
              const SizedBox(width: 8),
              Text('Ask: ${fmt.format(askTotal)}',
                  style: const TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      color: Color(0xFF4A5568))),
            ],
          ),
        ],

        const SizedBox(height: 6),

        // ── Progress bar (running or paused with progress) ──────────────────
        if ((isRunning || isPaused) && v.total > 0) ...[
          ClipRRect(
            borderRadius: BorderRadius.circular(3),
            child: LinearProgressIndicator(
              value: v.pct,
              minHeight: 5,
              backgroundColor: const Color(0xFFE5E7EB),
              valueColor: AlwaysStoppedAnimation<Color>(
                isRunning ? const Color(0xFF0D9488) : const Color(0xFFF59E0B),
              ),
            ),
          ),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              Flexible(
                child: Text(
                  v.label,
                  style: const TextStyle(
                      fontSize: 10, color: Color(0xFF6B7280)),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (isRunning) ...[
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: BatchValuationService.instance.pause,
                  child: const Text('\u25a0 Pause',
                      style: TextStyle(
                          fontSize: 10,
                          color: Color(0xFFF59E0B),
                          fontWeight: FontWeight.w600)),
                ),
              ] else ...[
                const SizedBox(width: 8),
                GestureDetector(
                  onTap: BatchValuationService.instance.resume,
                  child: const Text('\u25ba Resume',
                      style: TextStyle(
                          fontSize: 10,
                          color: Color(0xFF0D9488),
                          fontWeight: FontWeight.w600)),
                ),
              ],
            ],
          ),
          if (isRunning && v.etaLabel.isNotEmpty)
            Text(v.etaLabel,
                style: const TextStyle(
                    fontSize: 9, color: Color(0xFF9CA3AF)),
                textAlign: TextAlign.right),
        ],

        // ── Run button (not started) ────────────────────────────────────────
        if (!isRunning && !isPaused && !hasValue && !hasProgress)
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              const SizedBox(height: 4),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: const Color(0xFFF0FDF4),
                  border: Border.all(color: const Color(0xFF86EFAC)),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  'Your collection has $totalCoins coins waiting for AI valuation. '
                  'Tap Run AI Valuation to get started \u2014 I\u2019ll estimate a range for each one. '
                  'No photos needed (upload images for a more precise value!).',
                  style: const TextStyle(
                      fontSize: 10,
                      color: Color(0xFF166534),
                      height: 1.4),
                  textAlign: TextAlign.right,
                ),
              ),
              const SizedBox(height: 6),
              ElevatedButton.icon(
                onPressed: () => BatchValuationService.instance.start(),
                icon: const Icon(Icons.play_arrow_rounded, size: 16),
                label: const Text('Run AI Valuation'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0D9488),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(6)),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 10),
                  textStyle: const TextStyle(
                      fontSize: 12, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),

        // ── Resume button (paused) ──────────────────────────────────────────
        if (!isRunning && isPaused && !hasValue)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: ElevatedButton.icon(
              onPressed: BatchValuationService.instance.resume,
              icon: const Icon(Icons.play_arrow_rounded, size: 16),
              label: Text('Resume (${v.remaining} remaining)'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0D9488),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6)),
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 10),
                textStyle: const TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ),
          ),
      ],
    );
  }

  Widget _metricCard(String label, String value, {Color? valueColor}) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 4,
            offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 11, color: Color(0xFF5A5C69))),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(value,
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                    color: valueColor ?? const Color(0xFF31333F))),
          ),
        ],
      ),
    );
  }

  /// Fixed-width card for use inside a Wrap row (5-card wide layout).
  Widget _metricCardFlex(String label, String value, {Color? valueColor}) {
    return SizedBox(
      width: 160,
      child: _metricCard(label, value, valueColor: valueColor),
    );
  }

  Widget _buildCategoryBreakdown(double coins, double currency, double medals, double others, intl.NumberFormat fmt) {
    final total = coins + currency + medals + others;
    final coinsPct = total > 0 ? (coins / total) * 100 : 0.0;
    final currencyPct = total > 0 ? (currency / total) * 100 : 0.0;
    final medalsPct = total > 0 ? (medals / total) * 100 : 0.0;
    final othersPct = total > 0 ? (others / total) * 100 : 0.0;

    Widget buildLegendItem(String label, double value, double pct, Color color) {
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B).withValues(alpha: 0.4),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white10),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: color,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: const TextStyle(
                    color: Colors.white70,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  fmt.format(value),
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 14,
                  ),
                ),
                Text(
                  '${pct.toStringAsFixed(1)}%',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.5),
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(18),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF334155)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.3),
            blurRadius: 12,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'VALUATION BREAKDOWN',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w800,
              letterSpacing: 1.2,
              color: Color(0xFF94A3B8),
            ),
          ),
          const SizedBox(height: 16),
          // Combined Progress Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: SizedBox(
              height: 14,
              child: Row(
                children: [
                  if (coins > 0)
                    Expanded(
                      flex: (coinsPct * 100).round(),
                      child: Container(color: const Color(0xFF6366F1)), // Indigo
                    ),
                  if (currency > 0)
                    Expanded(
                      flex: (currencyPct * 100).round(),
                      child: Container(color: const Color(0xFF10B981)), // Emerald
                    ),
                  if (medals > 0)
                    Expanded(
                      flex: (medalsPct * 100).round(),
                      child: Container(color: const Color(0xFFF59E0B)), // Amber
                    ),
                  if (others > 0)
                    Expanded(
                      flex: (othersPct * 100).round(),
                      child: Container(color: const Color(0xFFEC4899)), // Pink
                    ),
                  if (total == 0)
                    Expanded(
                      child: Container(color: const Color(0xFF334155)),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),
          LayoutBuilder(
            builder: (context, constraints) {
              final items = [
                buildLegendItem('Coins', coins, coinsPct, const Color(0xFF6366F1)),
                buildLegendItem('Currency', currency, currencyPct, const Color(0xFF10B981)),
                buildLegendItem('Medals', medals, medalsPct, const Color(0xFFF59E0B)),
                buildLegendItem('Others', others, othersPct, const Color(0xFFEC4899)),
              ];
              final width = constraints.maxWidth;
              if (width > 850) {
                return Row(
                  children: items.map((item) => Expanded(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4),
                      child: item,
                    ),
                  )).toList(),
                );
              } else if (width > 480) {
                return Wrap(
                  spacing: 10,
                  runSpacing: 10,
                  children: items.map((item) => SizedBox(
                    width: (width - 10) / 2,
                    child: item,
                  )).toList(),
                );
              } else {
                return Column(
                  children: [
                    items[0],
                    const SizedBox(height: 8),
                    items[1],
                    const SizedBox(height: 8),
                    items[2],
                    const SizedBox(height: 8),
                    items[3],
                  ],
                );
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildArbitrageDealsCard(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final headerColor = isDark ? Colors.white : const Color(0xFF31333F);
    final descColor = isDark ? const Color(0xFF94A3B8) : const Color(0xFF64748B);
    final borderColor = isDark ? const Color(0xFF374151) : const Color(0xFFE2E6E9);

    return Container(
      decoration: BoxDecoration(
        color: cardBg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withAlpha(15),
            blurRadius: 12,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(16),
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const DealsScreen()),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: const Color(0xFF0F9D58).withAlpha(20),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Icon(Icons.shopping_bag_outlined,
                      color: Color(0xFF0F9D58), size: 24),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Wishlist Deal Spotter',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: headerColor,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Find wishlist coins on eBay near or below Bid price',
                        style: TextStyle(fontSize: 12, color: descColor),
                      ),
                    ],
                  ),
                ),
                const Icon(Icons.chevron_right, color: Color(0xFFF63366)),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ─── Release Notes Data ────────────────────────────────────────────────────────

class _Release {
  final String version;
  final String date;
  final String description;
  final List<String> changes;
  final bool isLatest;
  final bool isLegacy;

  const _Release({
    required this.version,
    required this.date,
    required this.description,
    required this.changes,
    this.isLatest = false,
    this.isLegacy = false,
  });
}

const _versionHistory = <_Release>[
  _Release(
    version: 'v4.0',
    date: '2026-07-08',
    description: 'Greysheet Market Valuation Integration',
    isLatest: true,
    changes: [
      'Greysheet CDN API integrated: real-time bid/ask valuations for circulating and key-date US coins.',
      'Valuation pipeline hardened: graceful fallback when Greysheet returns no data for a coin type.',
      'Home dashboard error states resolved: collection stats, portfolio chart, and market news all load cleanly.',
      'Numismatic knowledge base expanded: additional coin series, mint marks, and legislative context seeded.',
      'Proxy manager skill added to Antigravity agent: Webshare proxy provisioning fully automated.',
      'Platform stability pass: backend startup errors eliminated, Cloud Run health checks passing.',
    ],
  ),
  _Release(
    version: 'v3.9',
    date: '2026-06-24',
    description: 'Ingestion Pipeline Hardening & Stability',
    isLatest: false,
    changes: [
      'Aligned spreadsheet ingestion schema: all cost/price column variants now map to the canonical "Cost" field; all notes variants map to "Personal Notes".',
      'Removed legacy back-compat sync logic that cross-populated deprecated Firestore fields.',
      'Replaced direct dictionary access with safe .get() methods throughout ingestion to prevent KeyError on optional columns.',
      'Pinned google-genai>=1.71.0 in requirements.txt and removed deprecated legacy AI libraries from the Docker build.',
      'Interactive Morgan suggestion chips: tapping a chip now launches Morgan with that query pre-filled.',
      'Legacy vertexai utility scripts migrated to google-genai SDK ahead of deprecation.',
    ],
  ),
  _Release(
    version: 'v3.8',
    date: '2026-06-23',
    description: 'Microscope Scanner Reliability & UX',
    isLatest: false,
    changes: [
      'Restored cv2 focus window: the desktop pop-up reappears when a scan starts so you can manually adjust the microscope before capture.',
      'Eliminated idle-preview lag: the web browser no longer streams a live camera feed while idle, keeping the status pane always fully visible.',
      'Fixed camera-ownership race condition: idle preview thread now correctly yields the camera before the scan worker opens it.',
      'Camera connection resilience: up to 5 consecutive frame-read retries before reporting a connection error (was 1).',
      'Added OpenCV frame-buffer limit (BUFFERSIZE=1) to prevent stale-frame accumulation and reduce lag.',
      'New \'I have flipped the coin\' button: tap to immediately start the reverse scan instead of waiting for the 8-second auto-timer.',
      'Preview resolution reduced to 1280x720 during idle to cut USB bandwidth and CPU usage.',
    ],
  ),
  _Release(
    version: 'v3.7',
    date: '2026-06-12',
    description: 'Code Quality & Morgan UX Pass',
    isLatest: false,
    changes: [
      'Morgan guide bubbles fully redesigned: concise narrations, explicit arrow directions, gold ← arrow points at search box.',
      'PDF invoice overlay: indeterminate bouncing progress bar replaces the frozen "0%" state; 10-30s timing hint added.',
      'API URL centralised in lib/constants.dart — all 11 files now reference kApiBaseUrl.',
      'Flutter analyze: 32 lint issues eliminated — zero warnings, zero errors.',
      'Home dashboard: friendly news-unavailable message replaces internal config detail.',
      'Unnecessary Map<String,dynamic> casts removed from 4 files.',
    ],
  ),
  _Release(
    version: 'v3.6 Beta',
    date: '2026-06-10',
    description: 'Vertex AI Coin Reference Search',
    isLatest: false,
    changes: [
      'New Coin Search screen: semantic search over 11,900+ coin reference entries powered by Vertex AI Search Enterprise tier.',
      'Natural language queries: ask about dates, mint marks, designers, metal content, or coin history.',
      'AI-generated summary banner surfaces key facts above results.',
      'Category filter chips (Circulating, Commemorative, Bullion, Proof) narrow results instantly.',
      'Mint mark chips and draggable detail sheet for every result card.',
      'AI Reference Search button added to My Collection toolbar for quick cross-reference.',
      'GET /api/coin_search open endpoint on Cloud Run — no authentication required (public reference data).',
    ],
  ),
  _Release(
    version: 'v3.5 Beta',
    date: '2026-06-09',
    description: 'Universal Item Routing & Supplies Tracking',
    isLatest: false,
    changes: [
      'Invoice AI now classifies every line item: coins, sets, stamps, currency, medals, and supplies.',
      'Coin sets create a single Set Record in Review Hub — choose Break Up or Keep as Set.',
      'Break Up Set expands a set into individual coins, each inheriting set provenance.',
      'Supplies (binders, pages, capsules) automatically routed to the new Inventory screen.',
      'Stamps and non-numismatic items held in Pending Items for future module support.',
      'Firestore security rules hardened: pending_items, supplies_log, admin_grade_flags, reference_library all covered.',
      'Fixed backend startup crash (Request import NameError in break_up_set endpoint).',
    ],
  ),
  _Release(
    version: 'v3.2 Beta',
    date: '2026-04-25',
    description: 'PCGS Import Wizard',
    isLatest: false,
    changes: [
      'Import graded coins directly from PCGS by certification number.',
      'Paste cert numbers manually or upload a PCGS registry CSV export.',
      'Automatic schema mapping: Year, Mint Mark, Grade, PCGS#, images, and price guide value.',
      'Duplicate detection prevents double-importing slabs.',
      'Bearer token saved to your account — no re-entry needed each session.',
      'API called client-side (Flutter Web) to bypass Cloudflare restrictions.',
    ],
  ),
  _Release(
    version: 'v3.1 Beta',
    date: '2026-04-23',
    description: 'AI Checklist Scanner',
    changes: [
      'Photograph a printed coin checklist — AI reads it and syncs your collection.',
      'Supports all 31 coin programs (Morgan Dollars, State Quarters, Lincoln Cents, etc.).',
      'QTY and notes column now captured from the checklist (e.g. "MS-65", "stored in binder").',
      'Unchecked coins auto-populate your Wish List in one scan.',
      'Page-aware chunking: Gemini processes one page at a time to prevent token overflow.',
      'SDK migrated from vertexai → google-genai ahead of June 24, 2026 shutdown.',
    ],
  ),
  _Release(
    version: 'v3 Beta',
    date: '2026-04-08',
    description: 'Flutter Platform Launch',
    changes: [
      'Rebuilt entire frontend on Flutter for true cross-platform support.',
      'Real-time Firestore streaming on all collection screens.',
      'Hardware agent bridge via Firestore command pattern.',
      'Full collection data grid with sortable columns and inline editing.',
      'Live Microscope Scan screen with sharpness meter and countdown rings.',
      'AI-driven obverse/reverse identification via Gemini.',
      'Enhanced Gemini prompt for precise mint mark detection.',
    ],
  ),
  _Release(
    version: 'v2.7',
    date: '2026-03-07',
    description: 'Improved UI Labels & Professional ID System',
    isLegacy: true,
    changes: [
      'Replaced cryptic hex IDs with professional Year-Mint-Denomination labels.',
      'Enhanced visual scannability for large collections.',
    ],
  ),
  _Release(
    version: 'v2.6',
    date: '2026-02-23',
    description: 'Checklist Logic Fixes & Strict Ingestion Rules',
    isLegacy: true,
    changes: [
      'Fixed Program Checklist matching to avoid false positives.',
      'Added Face Value and Melt Value to Dashboard & Database view.',
    ],
  ),
  _Release(
    version: 'v1.0',
    date: '2026-01-20',
    description: 'Initial Launch of Numista.AI',
    isLegacy: true,
    changes: [
      'Core Collection Management.',
      'AI Scan & Valuation.',
      'Market Data Integration.',
    ],
  ),
];

// ─── Release Notes Panel Widget ───────────────────────────────────────────────

class _ReleaseNotesPanel extends StatelessWidget {
  const _ReleaseNotesPanel();

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        border: Border.all(color: const Color(0xFFE2E6E9)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Theme(
        data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
        child: ExpansionTile(
          iconColor: const Color(0xFF31333F),
          collapsedIconColor: const Color(0xFF31333F),
          title: const Text('🚀 System Updates & Release Notes',
              style: TextStyle(
                  color: Color(0xFF31333F),
                  fontWeight: FontWeight.w500,
                  fontSize: 14)),
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 8),
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text(
                  'Track the latest features deployed to Numista.AI',
                  style: TextStyle(
                      color: const Color(0xFF5A5C69).withValues(alpha: 0.8),
                      fontSize: 12),
                ),
              ),
            ),
            const Divider(height: 1, indent: 16, endIndent: 16),
            ..._versionHistory.map((r) => _buildEntry(r)),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Widget _buildEntry(_Release r) {
    final vColor = r.isLatest
        ? const Color(0xFF1967D2)
        : r.isLegacy
            ? const Color(0xFF9AA0A6)
            : const Color(0xFF34A853);
    final vBg = r.isLatest
        ? const Color(0xFFE8F0FE)
        : r.isLegacy
            ? const Color(0xFFF1F3F4)
            : const Color(0xFFE6F4EA);

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 16, 16, 0),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 3),
            decoration: BoxDecoration(
                color: vBg, borderRadius: BorderRadius.circular(12)),
            child: Text(r.version,
                style: TextStyle(
                    color: vColor,
                    fontWeight: FontWeight.w700,
                    fontSize: 12,
                    letterSpacing: 0.5)),
          ),
          const SizedBox(width: 8),
          Text(r.date,
              style: const TextStyle(color: Color(0xFF9AA0A6), fontSize: 12)),
          if (r.isLatest) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                  color: const Color(0xFF34A853),
                  borderRadius: BorderRadius.circular(4)),
              child: const Text('LATEST',
                  style: TextStyle(
                      color: Colors.white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold)),
            ),
          ],
          if (r.isLegacy) ...[
            const SizedBox(width: 8),
            Text('Streamlit',
                style: TextStyle(
                    color: const Color(0xFF9AA0A6).withValues(alpha: 0.7),
                    fontSize: 10,
                    fontStyle: FontStyle.italic)),
          ],
        ]),
        const SizedBox(height: 6),
        Text(r.description,
            style: TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 13,
                color: r.isLegacy
                    ? const Color(0xFF9AA0A6)
                    : const Color(0xFF31333F))),
        const SizedBox(height: 4),
        ...r.changes.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 3),
              child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text('• ',
                    style: TextStyle(
                        color: r.isLegacy
                            ? const Color(0xFF9AA0A6)
                            : const Color(0xFF5A5C69),
                        fontSize: 13)),
                Expanded(
                    child: Text(c,
                        style: TextStyle(
                            color: r.isLegacy
                                ? const Color(0xFF9AA0A6)
                                : const Color(0xFF5A5C69),
                            fontSize: 13))),
              ]),
            )),
        const SizedBox(height: 12),
        const Divider(height: 1, color: Color(0xFFE2E6E9)),
      ]),
    );
  }
}

// ══════════════════════════════════════════════════════════════════════════════
//  _MorganDashboardCard
//  ────────────────────
//  Contextual "Ask Morgan" card shown on the home dashboard.
//  Shows a personalised greeting, coin count, and one-tap access to Morgan chat.
// ══════════════════════════════════════════════════════════════════════════════
class _MorganDashboardCard extends StatelessWidget {
  final int totalCoins;
  final VoidCallback? onAskMorgan;
  /// Navigates to AI Deepdive with a specific query pre-filled.
  final void Function(String query)? onAskMorganWithQuery;

  const _MorganDashboardCard({
    required this.totalCoins,
    this.onAskMorgan,
    this.onAskMorganWithQuery,
  });

  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<String>(
      future: MorganPrefs.getDisplayName(),
      builder: (context, snap) {
        final name = snap.data ?? '';
        final greeting = name.isNotEmpty ? 'Hi $name! ' : '';
        final coinLine = totalCoins == 0
            ? 'Your collection is ready to grow.'
            : 'I\'ve reviewed your $totalCoins coin${totalCoins == 1 ? '' : 's'}.';

        return Container(
          width: double.infinity,
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF0B1220), Color(0xFF112240)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _gold.withAlpha(60), width: 1.5),
            boxShadow: [
              BoxShadow(
                color: _teal.withAlpha(20),
                blurRadius: 16,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Padding(
            padding: const EdgeInsets.all(18),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // ── Header row ──────────────────────────────────────────────
                Row(
                  children: [
                    // Morgan avatar
                    Container(
                      width: 48, height: 48,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(
                          colors: [Color(0xFFD4A843), Color(0xFF8B6914)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        border: Border.all(color: _gold.withAlpha(120), width: 2),
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/morgan_avatar.png',
                          fit: BoxFit.cover,
                          errorBuilder: (ctx, err, stack) => const Icon(
                              Icons.smart_toy_rounded,
                              color: Colors.white, size: 24),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Text('Morgan',
                                  style: TextStyle(
                                      color: Colors.white,
                                      fontSize: 15,
                                      fontWeight: FontWeight.bold)),
                              const SizedBox(width: 6),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                    horizontal: 6, vertical: 2),
                                decoration: BoxDecoration(
                                  color: _teal.withAlpha(30),
                                  borderRadius: BorderRadius.circular(4),
                                  border: Border.all(
                                      color: _teal.withAlpha(80), width: 1),
                                ),
                                child: const Text('AI Guide',
                                    style: TextStyle(
                                        color: _teal,
                                        fontSize: 9,
                                        fontWeight: FontWeight.w700,
                                        letterSpacing: 0.5)),
                              ),
                            ],
                          ),
                          const SizedBox(height: 2),
                          Text('$greeting$coinLine',
                              style: const TextStyle(
                                  color: _sub, fontSize: 12)),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // ── Suggestion chips ─────────────────────────────────────────
                SingleChildScrollView(
                  scrollDirection: Axis.horizontal,
                  child: Row(
                    children: [
                      _chip(
                        totalCoins == 0
                            ? 'How do I add my first coin?'
                            : 'What\'s my most valuable coin?',
                        onAskMorganWithQuery: onAskMorganWithQuery,
                        onAskMorgan: onAskMorgan,
                      ),
                      const SizedBox(width: 8),
                      _chip(
                        totalCoins == 0
                            ? 'What can Morgan help me with?'
                            : 'Give me a collection summary',
                        onAskMorganWithQuery: onAskMorganWithQuery,
                        onAskMorgan: onAskMorgan,
                      ),
                      if (totalCoins > 0) ...[
                        const SizedBox(width: 8),
                        _chip(
                          'Am I missing any coins from my sets?',
                          onAskMorganWithQuery: onAskMorganWithQuery,
                          onAskMorgan: onAskMorgan,
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 14),

                // ── Ask Morgan button ────────────────────────────────────────
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: onAskMorgan,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: _teal,
                      foregroundColor: Colors.black87,
                      padding: const EdgeInsets.symmetric(vertical: 13),
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(10)),
                      elevation: 0,
                    ),
                    icon: const Icon(Icons.chat_bubble_rounded, size: 16),
                    label: const Text('Ask Morgan',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 14)),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _chip(
    String label, {
    void Function(String query)? onAskMorganWithQuery,
    VoidCallback? onAskMorgan,
  }) {
    void handleTap() {
      if (onAskMorganWithQuery != null) {
        onAskMorganWithQuery(label);
      } else {
        onAskMorgan?.call();
      }
    }

    return MouseRegion(
      cursor: SystemMouseCursors.click,
      child: GestureDetector(
        onTap: handleTap,
        child: AnimatedContainer(
          duration: const Duration(milliseconds: 150),
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.white.withAlpha(10),
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: Colors.white.withAlpha(30)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(label, style: const TextStyle(color: _sub, fontSize: 11)),
              const SizedBox(width: 4),
              const Icon(Icons.arrow_forward_ios_rounded,
                  size: 8, color: _sub),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Coin Thumbnail ────────────────────────────────────────────────────────────
/// Circular 36×36 coin image for use in list tiles.
/// Shows the actual coin photo when [imageUrl] is available;
/// falls back to a generic coin icon on null / error.
class _CoinThumbnail extends StatelessWidget {
  final String? imageUrl;
  const _CoinThumbnail({this.imageUrl});

  static const _placeholder = BoxDecoration(
    color: Color(0xFFF0F2F6),
    shape: BoxShape.circle,
  );

  @override
  Widget build(BuildContext context) {
    final url = imageUrl;
    if (url == null || url.isEmpty) {
      return Container(
        width: 36, height: 36,
        decoration: _placeholder,
        child: const Icon(Icons.toll, size: 18, color: Color(0xFF5A5C69)),
      );
    }
    return ClipOval(
      child: CachedNetworkImage(
        imageUrl: url,
        width: 36, height: 36,
        fit: BoxFit.cover,
        placeholder: (ctx, _) => Container(
          width: 36, height: 36,
          decoration: _placeholder,
          child: const SizedBox(
            width: 18, height: 18,
            child: CircularProgressIndicator(
              strokeWidth: 1.5,
              color: Color(0xFF5A5C69),
            ),
          ),
        ),
        errorWidget: (ctx, _, err) => Container(
          width: 36, height: 36,
          decoration: _placeholder,
          child: const Icon(Icons.toll, size: 18, color: Color(0xFF5A5C69)),
        ),
      ),
    );
  }
}

// ─── Large senior-friendly action button ──────────────────────────────────────
class _DashboardActionButton extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String label;
  final String subtitle;
  final VoidCallback? onTap;
  final String heroTag;

  const _DashboardActionButton({
    required this.icon,
    required this.iconColor,
    required this.label,
    required this.subtitle,
    required this.onTap,
    required this.heroTag,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFE2E6E9)),
          ),
          child: Row(children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: iconColor.withAlpha(20),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(icon, color: iconColor, size: 24),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label,
                      style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF0F172A))),
                  const SizedBox(height: 2),
                  Text(subtitle,
                      style: const TextStyle(
                          fontSize: 13, color: Color(0xFF64748B))),
                ],
              ),
            ),
            const Icon(Icons.arrow_forward_ios_rounded,
                size: 14, color: Color(0xFFCBD5E1)),
          ]),
        ),
      ),
    );
  }
}

// ─── Collapsible section for the dashboard ────────────────────────────────────
class _ExpandableSection extends StatefulWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final Widget child;
  final bool initiallyExpanded;

  const _ExpandableSection({
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.child,
    this.initiallyExpanded = true,
  });

  @override
  State<_ExpandableSection> createState() => _ExpandableSectionState();
}

class _ExpandableSectionState extends State<_ExpandableSection> {
  late bool _expanded;

  @override
  void initState() {
    super.initState();
    _expanded = widget.initiallyExpanded;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFFE2E6E9)),
      ),
      child: Column(children: [
        InkWell(
          borderRadius: _expanded
              ? const BorderRadius.vertical(top: Radius.circular(12))
              : BorderRadius.circular(12),
          onTap: () => setState(() => _expanded = !_expanded),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
            child: Row(children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF0F172A).withAlpha(8),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(widget.icon,
                    size: 16, color: const Color(0xFF475569)),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(widget.title,
                        style: const TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF0F172A))),
                    Text(widget.subtitle,
                        style: const TextStyle(
                            fontSize: 12, color: Color(0xFF94A3B8))),
                  ],
                ),
              ),
              AnimatedRotation(
                turns: _expanded ? 0.5 : 0,
                duration: const Duration(milliseconds: 200),
                child: const Icon(Icons.expand_more_rounded,
                    size: 20, color: Color(0xFF94A3B8)),
              ),
            ]),
          ),
        ),
        if (_expanded)
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 0, 18, 16),
            child: widget.child,
          ),
      ]),
    );
  }
}
