import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart' as intl;
import 'package:cached_network_image/cached_network_image.dart';
import '../constants.dart';
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
import '../services/market_news_service.dart';
import '../widgets/portfolio_charts.dart';
import '../widgets/beta_checklist_widget.dart';
import '../widgets/beta_welcome_dialog.dart';
import 'ai_chat_screen.dart';

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
  Color get _bg => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
  Color get _surface => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF1E2937) : Colors.white;
  Color get _text => Theme.of(context).brightness == Brightness.dark ? const Color(0xFFE8EAF0) : const Color(0xFF0F172A);
  Color get _subtext => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF8B92B4) : const Color(0xFF5A5C69);
  Color get _border => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF2D3143) : const Color(0xFFE2E6E9);
  Color get _accent => Theme.of(context).brightness == Brightness.dark ? const Color(0xFFC9A227) : const Color(0xFF8C7355);

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

    // Auth-primary stream selection.
    // A real non-anonymous Firebase user always reads from Firestore,
    // regardless of the in-memory demo flag. The demo branch is only
    // reached when there is no authenticated user (Browse Demo path, State B).
    // Anonymous users (State C): _browseDemoActive is always false on their
    // path because activateBrowseDemo() is only called from _browseDemo(),
    // which bypasses Firebase auth entirely. They fall through to Firestore.
    final authUser = FirebaseAuth.instance.currentUser;
    final isRealUser = authUser != null && !authUser.isAnonymous;

    final coinsStream = isRealUser
        ? FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots()
        : GuestSeedService.isBrowseDemoMode
            ? GuestSeedService.getDemoCoinsStream()
            : FirebaseFirestore.instance.collection(AuthService.coinsPath).snapshots();
    subCoins = coinsStream.listen((snap) {
      coins = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
      emit();
    }, onError: (e) => controller.addError(e));

    final currencyStream = isRealUser
        ? FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots()
        : GuestSeedService.isBrowseDemoMode
            ? const Stream<QuerySnapshot<Map<String, dynamic>>>.empty()
            : FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots();
    subCurrency = currencyStream.listen((snap) {
      currency = snap.docs.map((d) => {'id': d.id, ...d.data()}).toList();
      emit();
    }, onError: (e) => controller.addError(e));

    final worldItemsStream = isRealUser
        ? FirebaseFirestore.instance.collection(AuthService.coinsPath.replaceAll('/coins', '/world_items')).snapshots()
        : GuestSeedService.isBrowseDemoMode
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
    // Auto-prompt Beta Welcome Dialog for new or uninitiated testers
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      if (await BetaWelcomeDialog.shouldAutoShow()) {
        if (mounted) BetaWelcomeDialog.show(context);
      }
    });
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
    if (!isRefresh) {
      if (mounted) setState(() => _isLoadingNews = true);
    }
    try {
      final articles = await MarketNewsService.fetchNewsFeed();
      if (!mounted) return;
      setState(() {
        _news = articles.map((a) => {
          'title': a.title,
          'link': a.link,
          'source': a.source,
          'published': a.published,
          'summary': a.summary,
        }).toList();
        _isLoadingNews = false;
      });
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
    return MeltValueService.parseFaceValue(denom);
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

            return FutureBuilder<bool>(
              future: ValuationModeService.isAdvancedMode(),
              builder: (context, modeSnap) {
                final advanced = modeSnap.data ?? false;

                // ── Compute portfolio metrics ──────────────────────────────────
                int totalItems = coins.length + currency.length + worldItems.length;
            double cpgTotal = 0;
            double bidTotal = 0;
            double askTotal = 0;
            double acquisitionCost = 0;
            double meltValue       = 0;
            double faceValue       = 0;

            double currencyVal     = 0;
            double medalsVal       = 0;
            double othersVal       = 0;

            Map<String, double> programValues = {};

            // 1. Process Coins collection
            for (final data in coins) {
              final valStr = data['ai_estimated_value'] ?? data['AI Estimated Value'];
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
              }

              // Greysheet fields
              final coinCpg = _parseCurrency(data['cpgRetail']);
              final coinBid = _parseCurrency(data['greysheetBid']);
              final coinAsk = _parseCurrency(data['greysheetAsk']);

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
              final rawAi = data['ai_estimated_value'] ?? data['AI Estimated Value'];
              double finalVal = 0.0;
              if (rawAi != null && rawAi != 'None' && rawAi != 'Pending' && rawAi.toString().isNotEmpty) {
                finalVal = _parseCurrency(rawAi);
              } else {
                finalVal = _parseCurrency(data['Cost']);
              }

              final curCpg = _parseCurrency(data['cpgRetail']);
              final curBid = _parseCurrency(data['greysheetBid']);
              final curAsk = _parseCurrency(data['greysheetAsk']);

              cpgTotal += curCpg > 0 ? curCpg : finalVal;
              bidTotal += curBid > 0 ? curBid : finalVal * 0.80;
              askTotal += curAsk > 0 ? curAsk : finalVal * 0.92;

              currencyVal += finalVal;
              acquisitionCost += _parseCurrency(data['Cost']);
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');
            }

            // 3. Process World Items collection
            for (final data in worldItems) {
              final estVal = _parseCurrency(data['estimated_value']);
              final purchPrice = _parseCurrency(data['purchase_price']);
              final finalVal = estVal > 0 ? estVal : purchPrice;

              final catStr = (data['item_type'] ?? '').toString().toLowerCase();
              final name = (data['name'] ?? '').toString().toLowerCase();
              final notes = (data['notes'] ?? '').toString().toLowerCase();

              final isMedal = catStr.contains('medal') || name.contains('medal') || notes.contains('medal');

              if (isMedal) {
                medalsVal += finalVal;
              } else if (catStr == 'banknote') {
                currencyVal += finalVal;
              } else if (catStr != 'coin') {
                othersVal += finalVal;
              }

              final wCpg = _parseCurrency(data['cpgRetail']);
              final wBid = _parseCurrency(data['greysheetBid']);
              final wAsk = _parseCurrency(data['greysheetAsk']);

              cpgTotal += wCpg > 0 ? wCpg : finalVal;
              bidTotal += wBid > 0 ? wBid : finalVal * 0.80;
              askTotal += wAsk > 0 ? wAsk : finalVal * 0.92;

              acquisitionCost += purchPrice;
              final spotEntry = _parseCurrency(data['spot_value_at_entry']);
              if (spotEntry > 0) {
                meltValue += spotEntry;
              }
              faceValue += _computeFaceValue(data['denomination']?.toString() ?? '');
            }

            final portfolioValue = advanced ? cpgTotal : bidTotal;
            final effectiveCoinsVal = advanced ? cpgTotal : bidTotal;

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

            final mainContent = SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Version badge ─────────────────────────────────────────
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.symmetric(vertical: 5),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0FDF4),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: const Color(0xFF86EFAC)),
                    ),
                    child: Text('Numista.AI $kAppVersion',
                        textAlign: TextAlign.center,
                        style: const TextStyle(
                            fontWeight: FontWeight.w600,
                            fontSize: 11,
                            color: Color(0xFF166534))),
                  ),
                  const SizedBox(height: 12),
                  // ── Welcome Beta Tester Banner Card ─────────────────────────────────
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                      ),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFF3B82F6).withValues(alpha: 0.4)),
                      boxShadow: [
                        BoxShadow(
                          color: const Color(0xFF2563EB).withValues(alpha: 0.1),
                          blurRadius: 12,
                          offset: const Offset(0, 4),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Flexible(
                              child: Row(
                                children: [
                                  const Text('👋 Welcome Beta Tester!',
                                      style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                                  const SizedBox(width: 8),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF166534),
                                      borderRadius: BorderRadius.circular(4),
                                    ),
                                    child: const Text('ACTIVE THROUGH OCT 1',
                                        style: TextStyle(color: Color(0xFF86EFAC), fontSize: 9, fontWeight: FontWeight.bold)),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 6),
                        const Text(
                          'Thank you for helping us test Numista.AI! Please use our 18-step checklist to test coin scanning, cert lookups, and collection tools.',
                          style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12, height: 1.4),
                        ),
                        const SizedBox(height: 12),
                        Wrap(
                          spacing: 10,
                          runSpacing: 8,
                          children: [
                            ElevatedButton.icon(
                              onPressed: () => BetaWelcomeDialog.show(context),
                              icon: const Icon(Icons.info_outline, size: 16),
                              label: const Text('Read Beta Guide & Info'),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF2563EB),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                              ),
                            ),
                            const BetaChecklistWidget(),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // ── Header: title + portfolio value ──────────────────────
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.end,
                    children: [
                      const Flexible(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('DASHBOARD',
                                style: TextStyle(
                                    fontSize: 26,
                                    fontWeight: FontWeight.w900,
                                    fontStyle: FontStyle.italic,
                                    color: Color(0xFF31333F))),
                            Text('AI POWERED COLLECTION MANAGER',
                                style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: Color(0xFF5A5C69))),
                          ],
                        ),
                      ),
                      const SizedBox(width: 12),
                      Flexible(
                        child: FutureBuilder<bool>(
                          future: ValuationModeService.isAdvancedMode(),
                          builder: (context, modeSnap) {
                            final advanced = modeSnap.data ?? false;
                            return _buildPortfolioValueSection(cpgTotal, bidTotal, askTotal, fmt, totalItems, advanced: advanced);
                          },
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // ── Category Breakdown ─────────────────────────────────────
                  _buildCategoryBreakdown(effectiveCoinsVal, currencyVal, medalsVal, othersVal, fmt),
                  const SizedBox(height: 24),

                   // ── Metric cards ──────────────────────────────────────────
                  LayoutBuilder(builder: (ctx, bc) {
                    final profit = portfolioValue - acquisitionCost;
                    final profitFmt = (profit >= 0 ? '+' : '') + fmt.format(profit);
                    final profitColor = profit >= 0
                        ? const Color(0xFF0F9D58)
                        : const Color(0xFFE53935);
                    final narrow = bc.maxWidth < 480;
                    if (narrow) {
                      return Column(children: [
                        Row(children: [
                          Expanded(child: _metricCard('Total Items', totalItems.toString())),
                          const SizedBox(width: 10),
                          Expanded(child: _metricCard('Acq. Cost', fmt.format(acquisitionCost))),
                        ]),
                        const SizedBox(height: 10),
                        Row(children: [
                          Expanded(child: _metricCard('Melt Value', fmt.format(meltValue))),
                          const SizedBox(width: 10),
                          Expanded(child: _metricCard('Face Value', fmt.format(faceValue))),
                        ]),
                        const SizedBox(height: 10),
                        _metricCard('Profit / Loss', profitFmt,
                            valueColor: profitColor),
                      ]);
                    }
                    return Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _metricCardFlex('Total Items', totalItems.toString()),
                        _metricCardFlex('Acquisition Cost', fmt.format(acquisitionCost)),
                        _metricCardFlex('Melt Value', fmt.format(meltValue)),
                        _metricCardFlex('Face Value', fmt.format(faceValue)),
                        _metricCardFlex('Profit / Loss', profitFmt,
                            valueColor: profitColor),
                      ],
                    );
                  }),
                  const SizedBox(height: 24),

                  // ── Portfolio Insights Charts ──────────────────────────────
                  PortfolioChartsPanel(
                    portfolioValue: portfolioValue,
                    meltValue: meltValue,
                    acquisitionCost: acquisitionCost,
                    programValues: programValues,
                    snapshots: _snapshots,
                  ),
                  const SizedBox(height: 24),

                  // ── Recently Added ────────────────────────────────────────
                  const Text('Recently Added',
                      style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: Color(0xFF31333F))),
                  const SizedBox(height: 10),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: const Color(0xFFE2E6E9)),
                    ),
                    child: last5.isEmpty
                        ? const Padding(
                            padding: EdgeInsets.all(16),
                            child: Text('No coins yet — add your first coin!',
                                style: TextStyle(color: Color(0xFF5A5C69))))
                        : Column(
                            children: last5.asMap().entries.map((entry) {
                              final data = entry.value;
                              final year   = data['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
                              final mint   = data['Mint Mark']?.toString() ?? '';
                              final denom  = data['Denomination']?.toString() ?? '';
                              final series = data['Program/Series']?.toString() ?? '';
                              final theme  = data['Theme/Subject']?.toString() ?? '';
                              final coinCpg = _parseCurrency(data['cpgRetail']);
                              final coinBid = _parseCurrency(data['greysheetBid']);
                              final gVal = advanced ? coinCpg : coinBid;
                              final estVal = gVal > 0 
                                  ? fmt.format(gVal)
                                  : (data['AI Estimated Value']?.toString() ?? '—');

                              // Build a human-readable coin name
                              // Priority: Program/Series > Theme/Subject > Denomination > fallback
                              final cleanDenom = denom.trim();
                              final denomFallback = cleanDenom.isNotEmpty && cleanDenom != 'Multiple'
                                  ? (cleanDenom[0].toUpperCase() + cleanDenom.substring(1))
                                      .replaceAll(r'$', '')
                                      .trim()
                                  : 'Coin';
                              final coinName = series.isNotEmpty && series != 'Multiple'
                                  ? series
                                  : theme.isNotEmpty && theme != 'Multiple'
                                      ? theme
                                      : denomFallback;

                              // Build year-mint label, normalise "Multiple" to "Various"
                              final yearLabel = (year.isEmpty || year == 'Multiple') ? 'Various' : year;
                              final mintLabel = (mint.isEmpty || mint == 'Multiple') ? '' : '-$mint';
                              // Build denomination label — only prepend '$' if the
                              // value is numeric (e.g. "1" → "$1") or already has it.
                              // Word-form denominations (penny, nickel, dime, quarter) stay as-is.
                              String fmtDenom(String d) {
                                final cleanD = d.trim();
                                if (cleanD.isEmpty || cleanD == 'Multiple') return '';
                                if (cleanD.startsWith(r'$')) return cleanD;              // already has $
                                final numeric = double.tryParse(
                                    cleanD.replaceAll(RegExp(r'[^\d.]'), ''));
                                if (numeric != null && cleanD.contains(RegExp(r'^[\d]'))) {
                                  return '\$$cleanD';                              // numeric → add $
                                }
                                return cleanD[0].toUpperCase() + cleanD.substring(1);   // word → capitalise
                              }
                              final denomLabel = fmtDenom(denom);
                              final condition = data['Condition']?.toString() ?? '';

                              // When year is known → "2025-W  $1"
                              // When year is Various (sets/lots) → use Theme + Condition to differentiate
                              final String subtitle;
                              if (yearLabel != 'Various') {
                                final parts = [
                                  '$yearLabel$mintLabel',
                                  if (denomLabel.isNotEmpty) denomLabel,
                                ].where((s) => s.isNotEmpty).toList();
                                subtitle = parts.join(' · ');
                              } else {
                                // Year unknown — use theme + condition to distinguish
                                final themeStr = theme.isNotEmpty && theme != 'Multiple' ? theme : '';
                                final condStr = (condition.isNotEmpty && condition != 'Ungraded') ? condition : '';
                                final parts = [
                                  if (themeStr.isNotEmpty) themeStr,
                                  if (condStr.isNotEmpty) condStr,
                                  if (denomLabel.isNotEmpty) denomLabel,
                                ];
                                subtitle = parts.isEmpty ? 'Set / Lot' : parts.join(' · ');
                              }

                              return Column(children: [
                                if (entry.key > 0)
                                  const Divider(height: 1, color: Color(0xFFE2E6E9)),
                                ListTile(
                                  dense: true,
                                  contentPadding: const EdgeInsets.symmetric(
                                      horizontal: 16, vertical: 4),
                                  leading: _CoinThumbnail(
                                    imageUrl: data['image_url_obverse']?.toString()
                                        ?? data['imageUrlObverse']?.toString(),
                                  ),
                                  title: Text(coinName,
                                      overflow: TextOverflow.ellipsis,
                                      style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w600,
                                          color: Color(0xFF31333F))),
                                  subtitle: Text(subtitle,
                                      style: const TextStyle(
                                          fontSize: 11,
                                          color: Color(0xFF64748B))),
                                  trailing: Text(estVal,
                                      style: const TextStyle(
                                          fontSize: 13,
                                          fontWeight: FontWeight.w700,
                                          color: Color(0xFF0F9D58))),
                                ),
                              ]);
                            }).toList(),
                          ),
                  ),
                  const SizedBox(height: 16),

                  // ── Morgan Widget ─────────────────────────────────────────
                  _MorganDashboardCard(
                    totalCoins: totalItems,
                    onAskMorgan: widget.onAskMorgan,
                    onAskMorganWithQuery: widget.onAskMorganWithQuery,
                  ),
                  const SizedBox(height: 24),

                  // ── Live Spot Prices ──────────────────────────────────────
                  Row(children: [
                    const Icon(Icons.show_chart, size: 14, color: Color(0xFF0F9D58)),
                    const SizedBox(width: 6),
                    const Text('LIVE SPOT PRICES',
                        style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.w700,
                            color: Color(0xFF64748B),
                            letterSpacing: 0.5)),
                    const SizedBox(width: 10),
                    if (_pricesLastUpdated != null)
                      Text(
                        'Last updated: ${intl.DateFormat("dd MMM yyyy @ HHmm").format(_pricesLastUpdated!.toLocal())} · Source: metals-api.com',
                        style: const TextStyle(
                            fontSize: 9,
                            color: Color(0xFF94A3B8)),
                      ),
                  ]),
                  const SizedBox(height: 8),
                  if (_isLoadingPrices)
                    const SizedBox(height: 4,
                        child: LinearProgressIndicator(color: Color(0xFF0F9D58)))
                  else if (_spotPrices.isNotEmpty)
                    SingleChildScrollView(
                      scrollDirection: Axis.horizontal,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: _spotPrices.entries.map((e) =>
                          Container(
                            margin: const EdgeInsets.only(right: 10),
                            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                            decoration: BoxDecoration(
                              color: Colors.white,
                              borderRadius: BorderRadius.circular(8),
                              border: Border.all(color: const Color(0xFFE2E6E9)),
                              boxShadow: [BoxShadow(
                                  color: Colors.black.withValues(alpha: 0.04),
                                  blurRadius: 4, offset: const Offset(0, 2))],
                            ),
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(e.key,
                                    style: const TextStyle(
                                        fontSize: 10,
                                        fontWeight: FontWeight.w600,
                                        color: Color(0xFF64748B))),
                                const SizedBox(height: 2),
                                Text(fmt.format(e.value),
                                    style: const TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w800,
                                        color: Color(0xFF0F172A))),
                              ],
                            ),
                          ),
                        ).toList(),
                      ),
                    ),
                  const SizedBox(height: 24),

                  // ── System Updates & Release Notes ────────────────────────
                  _ReleaseNotesPanel(),
                  const SizedBox(height: 24),

                  // ── Market Intel / News feed (bottom) ─────────────────────
                  Row(
                    children: [
                      const Icon(Icons.newspaper,
                          size: 15, color: Color(0xFF3B82F6)),
                      const SizedBox(width: 6),
                      const Text('MARKET INTEL',
                          style: TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w700,
                              color: Color(0xFF64748B),
                              letterSpacing: 0.5)),
                      const Spacer(),
                      if (!_isLoadingNews)
                        IconButton(
                          icon: const Icon(Icons.refresh,
                              size: 16, color: Color(0xFF94A3B8)),
                          tooltip: 'Refresh news',
                          visualDensity: VisualDensity.compact,
                          onPressed: () => _fetchNews(isRefresh: true),
                        ),
                    ],
                  ),
                  const SizedBox(height: 8),
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
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFE2E6E9)),
                      ),
                      child: Column(children: const [
                        Icon(Icons.wifi_off_outlined,
                            size: 28, color: Color(0xFFCBD5E1)),
                        SizedBox(height: 8),
                        Text('Market news unavailable right now — check back shortly.',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                                fontSize: 12, color: Color(0xFF94A3B8))),
                      ]),
                    )
                  else
                    SizedBox(
                      height: 158,
                      child: Builder(builder: (context) {
                        // Filter out dismissed articles client-side
                        final visibleNews = _news
                            .whereType<Map<String, dynamic>>()
                            .where((item) {
                          final link = item['link']?.toString() ?? '';
                          // Simple hash: use the link URL as a stable ID
                          final id = link.isNotEmpty
                              ? _stableArticleId(link)
                              : '';
                          return id.isEmpty || !_dismissedNewsIds.contains(id);
                        }).toList();
                        return ListView.builder(
                          scrollDirection: Axis.horizontal,
                          itemCount: visibleNews.length,
                          itemBuilder: (ctx, i) {
                            final item = visibleNews[i];
                            final link = item['link']?.toString() ?? '';
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
                                  margin: const EdgeInsets.only(right: 12),
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: Colors.white,
                                    borderRadius: BorderRadius.circular(8),
                                    border: Border.all(
                                        color: const Color(0xFFE2E6E9)),
                                    boxShadow: [
                                      BoxShadow(
                                        color: Colors.black.withValues(alpha: 0.03),
                                        blurRadius: 4,
                                        offset: const Offset(0, 2),
                                      )
                                    ],
                                  ),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Row(children: [
                                        Expanded(
                                          child: Text(
                                            item['source']?.toString() ?? 'News',
                                            overflow: TextOverflow.ellipsis,
                                            style: const TextStyle(
                                                fontSize: 10,
                                                fontWeight: FontWeight.bold,
                                                color: Color(0xFF3B82F6)),
                                          ),
                                        ),
                                        const SizedBox(width: 4),
                                        Text(
                                          item['published']?.toString() ?? '',
                                          style: const TextStyle(
                                              fontSize: 10,
                                              color: Color(0xFF94A3B8)),
                                        ),
                                      ]),
                                      const SizedBox(height: 5),
                                      Text(
                                        item['title']?.toString() ?? '',
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
                                          item['summary']?.toString() ?? '',
                                          maxLines: 3,
                                          overflow: TextOverflow.ellipsis,
                                          style: const TextStyle(
                                              fontSize: 11,
                                              color: Color(0xFF64748B),
                                              height: 1.4),
                                        ),
                                      ),
                                      // ── Bottom row: Read more + 👎 Not relevant ──
                                      Row(
                                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                        children: [
                                          if (link.isNotEmpty)
                                            Row(
                                              mainAxisSize: MainAxisSize.min,
                                              children: const [
                                                Text('Read more',
                                                    style: TextStyle(
                                                        fontSize: 10,
                                                        color: Color(0xFF3B82F6),
                                                        fontWeight: FontWeight.w600)),
                                                SizedBox(width: 2),
                                                Icon(Icons.arrow_forward_ios,
                                                    size: 9,
                                                    color: Color(0xFF3B82F6)),
                                              ],
                                            )
                                          else
                                            const SizedBox.shrink(),
                                          // 👎 Not relevant
                                          if (articleId.isNotEmpty)
                                            GestureDetector(
                                              onTap: () => _dismissArticle(articleId),
                                              child: const Tooltip(
                                                message: 'Not relevant — hide this article',
                                                child: Icon(
                                                  Icons.thumb_down_outlined,
                                                  size: 13,
                                                  color: Color(0xFFCBD5E1),
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
                  const SizedBox(height: 32),
                ],
              ),
            );

            if (outerConstraints.maxWidth >= 800) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    flex: 2,
                    child: mainContent,
                  ),
                  VerticalDivider(width: 1, color: _border, thickness: 1),
                  Expanded(
                    flex: 1,
                    child: Container(
                      color: _bg,
                      child: const AiChatScreen(),
                    ),
                  ),
                ],
              );
            } else {
              return mainContent;
            }
          },
            );
          },
        );
      },
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
            style: TextStyle(
                fontSize: 9,
                fontWeight: FontWeight.w600,
                color: _subtext)),
        const SizedBox(height: 2),

        // ── Main value display ──────────────────────────────────────────────
        if (hasValue) ...[
          Text(fmt.format(displayVal),
              style: TextStyle(
                  fontSize: 36,
                  fontWeight: FontWeight.w900,
                  color: _accent)),
          Text(
            advanced ? 'CPG Retail Market basis' : 'Wholesale / Greysheet Bid basis',
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w500,
              color: _subtext,
              fontStyle: FontStyle.italic,
            ),
          ),
        ]
        else if (isRunning)
          Text(
            hasProgress ? '${fmt.format(displayVal)} (est.)' : 'Valuing\u2026',
            style: TextStyle(
                fontSize: 26,
                fontWeight: FontWeight.w900,
                color: _accent),
          )
        else
          Text('Pending AI Valuation',
              style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.w700,
                  color: _subtext)),

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
    final isDark = Theme.of(context).brightness == Brightness.dark;
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 12),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: _border),
        boxShadow: [BoxShadow(
            color: Colors.black.withValues(alpha: isDark ? 0.20 : 0.04),
            blurRadius: 4,
            offset: const Offset(0, 2))],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.center,
        children: [
          Text(label,
              textAlign: TextAlign.center,
              style: TextStyle(fontSize: 11, color: _subtext)),
          const SizedBox(height: 6),
          FittedBox(
            fit: BoxFit.scaleDown,
            child: Text(value,
                style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.w800,
                    color: valueColor ?? _text)),
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
    version: 'v4.208',
    date: '2026-08-26',
    description: 'Beta Enhancements & Platform Updates',
    isLatest: true,
    changes: [
      'Beta: ITEM 6 DEMO badge + ITEM 7 zero-value warning + ITEM 8 Clear Demo Coins; fix error_message_service Crashlytics dep',
      'Release: auto-bump v4.207 for beta sprint P0 items 1-5',
      'Beta: ITEM 3 text scale + ITEM 4 ErrorMessageService + telemetry route + ITEM 5 browser back fix',
      'Release: auto-bump v4.204 release notes and dashboard version',
      'E2e: replace hard-coded 4s enterDemo() with flt-glass-pane wait in shared helper',
      'Ux: gray-screen fallback ErrorWidget with plain-English message + copyable support email (ITEM 2)',
      'Security: IDOR auth guard on 6 endpoints; PCGS proxy Option A confirmed + JWT header',
      'Release: v4.203 release notes update',
    ],
  ),
  _Release(
    version: 'v4.207',
    date: '2026-08-26',
    description: 'Beta Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Beta: ITEM 3 text scale + ITEM 4 ErrorMessageService + telemetry route + ITEM 5 browser back fix',
      'Release: auto-bump v4.204 release notes and dashboard version',
      'E2e: replace hard-coded 4s enterDemo() with flt-glass-pane wait in shared helper',
      'Ux: gray-screen fallback ErrorWidget with plain-English message + copyable support email (ITEM 2)',
      'Security: IDOR auth guard on 6 endpoints; PCGS proxy Option A confirmed + JWT header',
      'Release: v4.203 release notes update',
      'Audit: run full system scan and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.206',
    date: '2026-08-26',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: auto-bump v4.204 release notes and dashboard version',
      'E2e: replace hard-coded 4s enterDemo() with flt-glass-pane wait in shared helper',
      'Ux: gray-screen fallback ErrorWidget with plain-English message + copyable support email (ITEM 2)',
      'Security: IDOR auth guard on 6 endpoints; PCGS proxy Option A confirmed + JWT header',
      'Release: v4.203 release notes update',
      'Audit: run full system scan and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.205',
    date: '2026-08-26',
    description: 'E2e Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'E2e: replace hard-coded 4s enterDemo() with flt-glass-pane wait in shared helper',
      'Ux: gray-screen fallback ErrorWidget with plain-English message + copyable support email (ITEM 2)',
      'Security: IDOR auth guard on 6 endpoints; PCGS proxy Option A confirmed + JWT header',
      'Release: v4.203 release notes update',
      'Audit: run full system scan and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.204',
    date: '2026-08-26',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: v4.203 release notes update',
      'Audit: run full system scan and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.203',
    date: '2026-08-26',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: run full system scan and generate SCAN_REPORT.md',
      'Qc/layer1: dismiss \'Let\'s go!\' wizard dialog in theme_switch_guard signInAndWait() - was blocking Settings navigation',
      'Qc: add --no-fatal-warnings to flutter analyze (warnings != errors, should not fail suite)',
      'Qc/layer1: fix HTML entity encoding in theme_switch_guard.spec.js (=> was written as =&gt;)',
      'Security: fail closed on Stripe checkout and portal errors',
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
    ],
  ),
  _Release(
    version: 'v4.202',
    date: '2026-08-25',
    description: 'Qc/layer1 Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc/layer1: dismiss \'Let\'s go!\' wizard dialog in theme_switch_guard signInAndWait() - was blocking Settings navigation',
      'Qc: add --no-fatal-warnings to flutter analyze (warnings != errors, should not fail suite)',
      'Qc/layer1: fix HTML entity encoding in theme_switch_guard.spec.js (=> was written as =&gt;)',
      'Security: fail closed on Stripe checkout and portal errors',
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
    ],
  ),
  _Release(
    version: 'v4.201',
    date: '2026-08-25',
    description: 'Qc/layer1 Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc/layer1: dismiss \'Let\'s go!\' wizard dialog in theme_switch_guard signInAndWait() - was blocking Settings navigation',
      'Qc: add --no-fatal-warnings to flutter analyze (warnings != errors, should not fail suite)',
      'Qc/layer1: fix HTML entity encoding in theme_switch_guard.spec.js (=> was written as =&gt;)',
      'Security: fail closed on Stripe checkout and portal errors',
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
    ],
  ),
  _Release(
    version: 'v4.200',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: add --no-fatal-warnings to flutter analyze (warnings != errors, should not fail suite)',
      'Qc/layer1: fix HTML entity encoding in theme_switch_guard.spec.js (=> was written as =&gt;)',
      'Security: fail closed on Stripe checkout and portal errors',
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
    ],
  ),
  _Release(
    version: 'v4.199',
    date: '2026-08-25',
    description: 'Qc/layer1 Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc/layer1: fix HTML entity encoding in theme_switch_guard.spec.js (=> was written as =&gt;)',
      'Security: fail closed on Stripe checkout and portal errors',
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
    ],
  ),
  _Release(
    version: 'v4.198',
    date: '2026-08-25',
    description: 'Qc/layer1 Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc/layer1: navigate to Settings & Backup before looking for theme toggle; add role=switch fallback',
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
    ],
  ),
  _Release(
    version: 'v4.197',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: flutter analyze --no-fatal-infos (warnings don\'t fail suite); flutter test via Push-Location',
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
    ],
  ),
  _Release(
    version: 'v4.196',
    date: '2026-08-25',
    description: 'Security Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Security: require Firebase auth on collection clear',
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout — required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
    ],
  ),
  _Release(
    version: 'v4.195',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: exclude .venv/node_modules/__pycache__ from deprecated model ID scan to prevent hang',
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
    ],
  ),
  _Release(
    version: 'v4.194',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: replace Select-String -Recurse with Get-ChildItem | Select-String (PowerShell compatibility)',
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
    ],
  ),
  _Release(
    version: 'v4.193',
    date: '2026-08-25',
    description: 'Ui Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ui: default My Collection to card view and soften gray-screen errors',
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout — required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token — replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) → 503 instead of 500 crash',
    ],
  ),
  _Release(
    version: 'v4.192',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: remove non-ASCII chars from run_qc.ps1 (em dashes, variation selectors broke PowerShell parser)',
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
    ],
  ),
  _Release(
    version: 'v4.191',
    date: '2026-08-25',
    description: 'Build Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Build: add onNavigateToCollection param to MorganChatPopout â€” required by base_layout',
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
    ],
  ),
  _Release(
    version: 'v4.190',
    date: '2026-08-25',
    description: 'Ux Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ux: feedback button routes to general feedback or support ticket',
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
    ],
  ),
  _Release(
    version: 'v4.189',
    date: '2026-08-25',
    description: 'Support Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Support: remove stale grant-token text from portal empty state',
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
    ],
  ),
  _Release(
    version: 'v4.188',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: connect stacks, harden isolation guards, archive legacy scripts (v4 plan)',
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
    ],
  ),
  _Release(
    version: 'v4.187',
    date: '2026-08-25',
    description: 'Support Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Support: eliminate token â€” replace with server-side consent flag',
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.186',
    date: '2026-08-25',
    description: 'Support Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Support: catch FailedPrecondition (index building) â†’ 503 instead of 500 crash',
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
    ],
  ),
  _Release(
    version: 'v4.185',
    date: '2026-08-25',
    description: 'Ui Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ui: make customer service email clickable; brighten My Tickets heading/subtitle to silver',
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.184',
    date: '2026-08-25',
    description: 'Support Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Support: add My Tickets and Support Portal to nav enabled-routes allowlist',
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.183',
    date: '2026-08-25',
    description: 'Support Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Support: scoped consent support access system (v5)',
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.182',
    date: '2026-08-25',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: resolve layer 1 visual guard contrast sampling and modal dismissal',
      'Release: bump release notes to v4.181',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.181',
    date: '2026-08-25',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.180',
    date: '2026-08-25',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: auto-bump v4.179 release notes and dashboard version',
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.179',
    date: '2026-08-25',
    description: 'Infra+tests Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
    ],
  ),
  _Release(
    version: 'v4.178',
    date: '2026-08-25',
    description: 'Infra+tests Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Infra+tests: 40-min Playwright timeout, health-check retry, Phase 3 financials tests',
      'Phase3c: spec green â€” 16/16 tests passing on preview channel',
      'Qc: add numista_qc/ consolidated QC suite (v5 plan)',
      'A11y: enable Flutter web accessibility for Playwright testing',
      'Financials: Phase 3A cost-display + P&L; Phase 3B backfill script; Phase 3C auth fixture',
      'Mint-set: Phase 2C label color 0xFF64748B to 0xFFB0BEC5 in _mintSetField only',
      'Mint-set: add Silver Proof Set template + is_foreign fix + Morgan maxWidth 480',
      'Program-manager: fix white text on light background in detail view nav/headings/progress',
    ],
  ),
  _Release(
    version: 'v4.177',
    date: '2026-08-24',
    description: 'Qc Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qc: add numista_qc/ consolidated QC suite (v5 plan)',
      'A11y: enable Flutter web accessibility for Playwright testing',
      'Financials: Phase 3A cost-display + P&L; Phase 3B backfill script; Phase 3C auth fixture',
      'Mint-set: Phase 2C label color 0xFF64748B to 0xFFB0BEC5 in _mintSetField only',
      'Mint-set: add Silver Proof Set template + is_foreign fix + Morgan maxWidth 480',
      'Program-manager: fix white text on light background in detail view nav/headings/progress',
      'Program-manager: display coin name (state/design) in checklist rows',
      'Chat: View Binder button navigates to My Collection via onNavigateToCollection callback',
    ],
  ),
  _Release(
    version: 'v4.176',
    date: '2026-08-24',
    description: 'A11y Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'A11y: enable Flutter web accessibility for Playwright testing',
      'Financials: Phase 3A cost-display + P&L; Phase 3B backfill script; Phase 3C auth fixture',
      'Mint-set: Phase 2C label color 0xFF64748B to 0xFFB0BEC5 in _mintSetField only',
      'Mint-set: add Silver Proof Set template + is_foreign fix + Morgan maxWidth 480',
      'Program-manager: fix white text on light background in detail view nav/headings/progress',
      'Program-manager: display coin name (state/design) in checklist rows',
      'Chat: View Binder button navigates to My Collection via onNavigateToCollection callback',
      'Release: sync v4.174 release notes and dashboard version',
    ],
  ),
  _Release(
    version: 'v4.175',
    date: '2026-08-24',
    description: 'Financials Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Financials: Phase 3A cost-display + P&L; Phase 3B backfill script; Phase 3C auth fixture',
      'Mint-set: Phase 2C label color 0xFF64748B to 0xFFB0BEC5 in _mintSetField only',
      'Mint-set: add Silver Proof Set template + is_foreign fix + Morgan maxWidth 480',
      'Program-manager: fix white text on light background in detail view nav/headings/progress',
      'Program-manager: display coin name (state/design) in checklist rows',
      'Chat: View Binder button navigates to My Collection via onNavigateToCollection callback',
      'Release: sync v4.174 release notes and dashboard version',
      'Scanner: full system audit 2026-08-24 - 215 pytest PASS, 157 E2E PASS, domain engine 19 PASS',
    ],
  ),
  _Release(
    version: 'v4.174',
    date: '2026-08-24',
    description: 'Scanner Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scanner: full system audit 2026-08-24 - 215 pytest PASS, 157 E2E PASS, domain engine 19 PASS',
      'Qa: optimize daily audit runner with parallel workers and fast timeouts',
      'Home-dashboard: auth-primary stream selection fixes demo-mode leak',
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
    ],
  ),
  _Release(
    version: 'v4.173',
    date: '2026-08-23',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: optimize daily audit runner with parallel workers and fast timeouts',
      'Home-dashboard: auth-primary stream selection fixes demo-mode leak',
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
    ],
  ),
  _Release(
    version: 'v4.172',
    date: '2026-08-23',
    description: 'Home-dashboard Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Home-dashboard: auth-primary stream selection fixes demo-mode leak',
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
    ],
  ),
  _Release(
    version: 'v4.171',
    date: '2026-08-23',
    description: 'Home-dashboard Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Home-dashboard: auth-primary stream selection fixes demo-mode leak',
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
    ],
  ),
  _Release(
    version: 'v4.170',
    date: '2026-08-23',
    description: 'Home-dashboard Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Home-dashboard: auth-primary stream selection fixes demo-mode leak',
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
    ],
  ),
  _Release(
    version: 'v4.169',
    date: '2026-08-23',
    description: 'Ui Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ui: fix white-on-white text in dark mode forms + reroute Send Beta Feedback to Morgan drawer',
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
      'Checklist: flatten program checklist to variety-level slots',
    ],
  ),
  _Release(
    version: 'v4.168',
    date: '2026-08-23',
    description: 'Feedback Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Feedback: correct ServiceUnavailable exception name for installed SDK version',
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
      'Checklist: flatten program checklist to variety-level slots',
      'Release: sync release notes v4.163',
    ],
  ),
  _Release(
    version: 'v4.167',
    date: '2026-08-23',
    description: 'Feedback Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Feedback: resolve composite index error and correct transcript field names',
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
      'Checklist: flatten program checklist to variety-level slots',
      'Release: sync release notes v4.163',
      'Release: sync release notes v4.162',
    ],
  ),
  _Release(
    version: 'v4.166',
    date: '2026-08-23',
    description: 'Feedback Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Feedback: add Antigravity feedback reader, triage script, and workflow protocol',
      'Checklist: compact year-row layout â€” one row per year, varieties inline',
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
      'Checklist: flatten program checklist to variety-level slots',
      'Release: sync release notes v4.163',
      'Release: sync release notes v4.162',
      'Release: sync release notes v4.161',
    ],
  ),
  _Release(
    version: 'v4.165',
    date: '2026-08-23',
    description: 'Program_model Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Program_model: use List.from + Map.from to safely cast Firestore web SDK types',
      'Release: auto-bump version notes for checklist variety-level fix',
      'Checklist: flatten program checklist to variety-level slots',
      'Release: sync release notes v4.163',
      'Release: sync release notes v4.162',
      'Release: sync release notes v4.161',
      'Release: sync release notes v4.160',
      'Release: sync release notes v4.159',
    ],
  ),
  _Release(
    version: 'v4.164',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync release notes v4.163',
      'Release: sync release notes v4.162',
      'Release: sync release notes v4.161',
      'Release: sync release notes v4.160',
      'Release: sync release notes v4.159',
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
    ],
  ),
  _Release(
    version: 'v4.163',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync release notes v4.162',
      'Release: sync release notes v4.161',
      'Release: sync release notes v4.160',
      'Release: sync release notes v4.159',
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
    ],
  ),
  _Release(
    version: 'v4.162',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync release notes v4.161',
      'Release: sync release notes v4.160',
      'Release: sync release notes v4.159',
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
    ],
  ),
  _Release(
    version: 'v4.161',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync release notes v4.160',
      'Release: sync release notes v4.159',
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
    ],
  ),
  _Release(
    version: 'v4.160',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync release notes v4.159',
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
    ],
  ),
  _Release(
    version: 'v4.159',
    date: '2026-08-23',
    description: 'Lint Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Lint: resolve all flutter analyze warnings to 0 issues',
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
    ],
  ),
  _Release(
    version: 'v4.158',
    date: '2026-08-23',
    description: 'Known-errors Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Sync unstaged UI and test changes pre-deploy',
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
      'Release: bump release version to v4.151',
    ],
  ),
  _Release(
    version: 'v4.157',
    date: '2026-08-23',
    description: 'Known-errors Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.156',
    date: '2026-08-23',
    description: 'Known-errors Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Known-errors: Greysheet Known Errors tab â€” two-layer classification, GSID merge, lazy pricing, admin claim gate',
      'Sync release notes pre-push',
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.155',
    date: '2026-08-23',
    description: 'Model Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Add S-PROOF-T1/T2 resolver tests and catalog slot count regression tests',
      'Model: upgrade feedbackIntelligence.js to gemini-3.7-flash',
      'Release: auto-bump v4.154 release notes and run_tests.ps1 cleanup',
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.154',
    date: '2026-08-23',
    description: 'Checklist Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Checklist: Phase 1 audit script + Phase 4 server-mediated add_coins callable',
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.153',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.152',
    date: '2026-08-23',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump release version to v4.151',
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
    ],
  ),
  _Release(
    version: 'v4.151',
    date: '2026-08-23',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: generate 2026-08-23 SCAN_REPORT.md and sync morning QC benchmarks',
      'Login: remove Free Scan Preview button (desktop-only launch, not ready for mobile)',
      'Scan: friendly error on mobile CORS failure + explicit OPTIONS preflight for identify_coin_photo',
      'Audit: add greysheet node catalog and program node map',
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
    ],
  ),
  _Release(
    version: 'v4.150',
    date: '2026-08-22',
    description: 'Login Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Login: remove Free Scan Preview button (desktop-only launch, not ready for mobile)',
      'Scan: friendly error on mobile CORS failure + explicit OPTIONS preflight for identify_coin_photo',
      'Audit: add greysheet node catalog and program node map',
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
    ],
  ),
  _Release(
    version: 'v4.149',
    date: '2026-08-22',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: friendly error on mobile CORS failure + explicit OPTIONS preflight for identify_coin_photo',
      'Audit: add greysheet node catalog and program node map',
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
    ],
  ),
  _Release(
    version: 'v4.148',
    date: '2026-08-22',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: friendly error on mobile CORS failure + explicit OPTIONS preflight for identify_coin_photo',
      'Audit: add greysheet node catalog and program node map',
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
    ],
  ),
  _Release(
    version: 'v4.147',
    date: '2026-08-22',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: add greysheet node catalog and program node map',
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.146',
    date: '2026-08-22',
    description: 'Program-manager Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.145',
    date: '2026-08-22',
    description: 'Program-manager Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Program-manager: correct slot counts and remove filter bar',
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.144',
    date: '2026-08-22',
    description: 'Seeder Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Seeder: total_slots counts variety slots not year rows',
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.143',
    date: '2026-08-22',
    description: 'Kennedy Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Kennedy: 213-slot catalog rebuild per v3 plan',
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.142',
    date: '2026-08-22',
    description: 'Eisenhower Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Eisenhower: 32-slot catalog rebuild + S-PROOF-T1/T2 matcher fix',
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.141',
    date: '2026-08-22',
    description: 'Tests+infra Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Tests+infra: catalog-align slot resolver tests, Playwright Start-Process timeout fix',
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.140',
    date: '2026-08-22',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync v4.139 release notes and dashboard version',
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.139',
    date: '2026-08-22',
    description: 'Scanner Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scanner: update SCAN_REPORT.md via project-scanner full system audit',
      'Catalog: three easy program corrections',
      'Checklist: Washington Classic Quarters 0/210 SNAP fix',
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.138',
    date: '2026-08-21',
    description: 'Catalog Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Catalog: three easy program corrections',
      'Checklist: Washington Classic Quarters 0/210 SNAP fix',
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.137',
    date: '2026-08-21',
    description: 'Checklist Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Checklist: Washington Classic Quarters 0/210 SNAP fix',
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.136',
    date: '2026-08-21',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.135',
    date: '2026-08-21',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.134',
    date: '2026-08-21',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: daily system check 2026-08-21 â€” 201 pytest PASS, 103/103 E2E PASS, domain engine 19 PASS',
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
    ],
  ),
  _Release(
    version: 'v4.133',
    date: '2026-08-21',
    description: 'Infra+tests Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Infra+tests: Playwright 25-min hard timeout, slot resolver unit tests, Suite 24 autocomplete',
      'Infra: Firestore deploy steps use numista_mobile working-dir, not numista_backend',
      'Infra: add firestore target to numista_backend/firebase.json â€” fix deploy workflow Firestore rules step',
      'Sync release notes pre-push',
      'Flutter: Phase 4a-C1 â€” Program/Series Autocomplete picker with canonical write, Theme/Subject adjacency',
      'Backend: Phase 4a-C3 â€” 2026 Semiquincentennial prompt rules + program_hint injection',
      'Flutter: Phase 4a-C2 â€” matcher aliases, country guard, Rule 24 split, S-SILVER fix, requiresPrivy gate, cent quarantine, double-tap guard',
      'Functions: improve email CTA â€” sidebar nav hint + Firestore console link',
    ],
  ),
  _Release(
    version: 'v4.132',
    date: '2026-08-20',
    description: 'Flutter Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Flutter: Phase 4a-C1 â€” Program/Series Autocomplete picker with canonical write, Theme/Subject adjacency',
      'Backend: Phase 4a-C3 â€” 2026 Semiquincentennial prompt rules + program_hint injection',
      'Flutter: Phase 4a-C2 â€” matcher aliases, country guard, Rule 24 split, S-SILVER fix, requiresPrivy gate, cent quarantine, double-tap guard',
      'Functions: improve email CTA â€” sidebar nav hint + Firestore console link',
      'Functions: lazy-load heavy modules + fix .doc() Firestore API',
      'Functions: add numista_backend/firebase.json for standalone functions deploy',
      'Feedback: add onFeedbackCreated Cloud Function â€” Gemini analysis + email alert + monthly rollup',
      'Ui: Phase 1+2 â€” BACK contrast + Review Hub subtitle chain',
    ],
  ),
  _Release(
    version: 'v4.131',
    date: '2026-08-20',
    description: 'Flutter Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Flutter: Phase 4a-C1 â€” Program/Series Autocomplete picker with canonical write, Theme/Subject adjacency',
      'Backend: Phase 4a-C3 â€” 2026 Semiquincentennial prompt rules + program_hint injection',
      'Flutter: Phase 4a-C2 â€” matcher aliases, country guard, Rule 24 split, S-SILVER fix, requiresPrivy gate, cent quarantine, double-tap guard',
      'Functions: improve email CTA â€” sidebar nav hint + Firestore console link',
      'Functions: lazy-load heavy modules + fix .doc() Firestore API',
      'Functions: add numista_backend/firebase.json for standalone functions deploy',
      'Feedback: add onFeedbackCreated Cloud Function â€” Gemini analysis + email alert + monthly rollup',
      'Ui: Phase 1+2 â€” BACK contrast + Review Hub subtitle chain',
    ],
  ),
  _Release(
    version: 'v4.129',
    date: '2026-08-19',
    description: 'Feedback Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Feedback: No Overlay widget error - remove tooltip + replace showDialog with inline panel',
      'Feedback: FAB still invisible - remove LayoutBuilder from Positioned',
      'Feedback: FeedbackDrawerOverlay web crash - StackFit.expand + FocusNode lifecycle fix',
      'Feedback: FAB invisible on web - switch to Stack-relative bottom/right anchor',
      'Feedback: MORGAN Feedback System Phase 1 â€” callable architecture, interview drawer, fallback form',
      'Web: stop BaseLayout setState during My Collection build',
      'All-view: banknote and world-item cards open detail on tap',
      'Header-stats-bar: split Valuation chip into three distinct desktop facts',
    ],
  ),
  _Release(
    version: 'v4.128',
    date: '2026-08-19',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync v4.125 release notes',
      'Release: sync auto-generated release notes for v4.123',
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
    ],
  ),
  _Release(
    version: 'v4.127',
    date: '2026-08-18',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync v4.125 release notes',
      'Release: sync auto-generated release notes for v4.123',
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
    ],
  ),
  _Release(
    version: 'v4.126',
    date: '2026-08-18',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync v4.125 release notes',
      'Release: sync auto-generated release notes for v4.123',
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
    ],
  ),
  _Release(
    version: 'v4.125',
    date: '2026-08-18',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync auto-generated release notes for v4.123',
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
    ],
  ),
  _Release(
    version: 'v4.124',
    date: '2026-08-18',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: sync auto-generated release notes for v4.123',
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
    ],
  ),
  _Release(
    version: 'v4.123',
    date: '2026-08-18',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: execute beta test 3 v4 runbook with state machine, set catalog, and awq ingestion',
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
    ],
  ),
  _Release(
    version: 'v4.121',
    date: '2026-08-18',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Sync auto-generated release notes for v4.120',
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
      'Sync release notes pre-push',
    ],
  ),
  _Release(
    version: 'v4.120',
    date: '2026-08-18',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: synchronize valuation mode parity and gate collection stream on auth state',
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
      'Sync release notes pre-push',
      'Release notes update v4.113',
    ],
  ),
  _Release(
    version: 'v4.119',
    date: '2026-08-18',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: decouple collection totals via collection_stats, resolve scrollbar track, deterministic awq repair, and supply reclassification',
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
      'Sync release notes pre-push',
      'Release notes update v4.113',
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.118',
    date: '2026-08-18',
    description: 'Beta Test Remediation & System of Record Alignment',
    isLatest: false,
    changes: [
      'Single-source-of-truth collection_stats aggregate stream preserves total inventory totals across table pagination',
      'Morgan Welcome Screen: eliminated desktop scrollbar canvas track along 540px boundary',
      'Deterministic AWQ honoree repair: 20 official US Mint honorees mapped to canonical theme_subject',
      'Conjunctive supply classifier: protected commemorative coins while isolating supplies from coin grid',
      'Token-aware condition parser: resolved Unspecified / Raw wrapping while preserving Sheldon grades',
    ],
  ),
  _Release(
    version: 'v4.117',
    date: '2026-08-18',
    description: 'Ai Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Add E2E suite 22, Pytest manifest test, and Flutter unit tests for Aug 17 features',
      'Release notes update v4.116',
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
      'Sync release notes pre-push',
      'Release notes update v4.113',
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.116',
    date: '2026-08-18',
    description: 'Ai Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ai: upgrade primary flash model to gemini-3.7-flash',
      'Audit: update SCAN_REPORT.md with full Flutter analysis linter breakdown',
      'Sync release notes pre-push',
      'Release notes update v4.113',
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.115',
    date: '2026-08-18',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release notes update v4.113',
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.114',
    date: '2026-08-18',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release notes update v4.113',
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.113',
    date: '2026-08-18',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: update system scan report SCAN_REPORT.md via project-scanner skill',
    ],
  ),
  _Release(
    version: 'v4.112',
    date: '2026-08-18',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: refresh 2026 circulating series manifests, gcs inventory, and firestore image indexes',
      'Web: wire collector memory settings dialog, review hub staging delete, and ai memory badge',
      'Security+quality: Pillow CVE upgrades, datetime.utcnow deprecation, SCAN_REPORT sync',
      'Audit: sync SCAN_REPORT.md following full Playwright suite run',
      'Audit: update SCAN_REPORT.md with flutter analyze findings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.111',
    date: '2026-08-17',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: refresh 2026 circulating series manifests, gcs inventory, and firestore image indexes',
      'Web: wire collector memory settings dialog, review hub staging delete, and ai memory badge',
      'Security+quality: Pillow CVE upgrades, datetime.utcnow deprecation, SCAN_REPORT sync',
      'Audit: sync SCAN_REPORT.md following full Playwright suite run',
      'Audit: update SCAN_REPORT.md with flutter analyze findings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.110',
    date: '2026-08-17',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: refresh 2026 circulating series manifests, gcs inventory, and firestore image indexes',
      'Web: wire collector memory settings dialog, review hub staging delete, and ai memory badge',
      'Security+quality: Pillow CVE upgrades, datetime.utcnow deprecation, SCAN_REPORT sync',
      'Audit: sync SCAN_REPORT.md following full Playwright suite run',
      'Audit: update SCAN_REPORT.md with flutter analyze findings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.109',
    date: '2026-08-17',
    description: 'Web Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Web: wire collector memory settings dialog, review hub staging delete, and ai memory badge',
      'Security+quality: Pillow CVE upgrades, datetime.utcnow deprecation, SCAN_REPORT sync',
      'Audit: sync SCAN_REPORT.md following full Playwright suite run',
      'Audit: update SCAN_REPORT.md with flutter analyze findings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.108',
    date: '2026-08-17',
    description: 'Continuous Learning UI & Desktop Web Enhancements',
    isLatest: false,
    changes: [
      'Web: connect collector memory settings card with desktop dialog and snake_case schema validation',
      'Review-hub: unify staging discards with confirmation modal and batch deletion API progress locking',
      'Review-hub: add AI Memory Assisted badge with multi-line responsive tooltips',
      'Services: create CollectorProfileService for GET/POST /api/ai/profile communication',
    ],
  ),
  _Release(
    version: 'v4.107',
    date: '2026-08-17',
    description: 'Security+quality Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Security+quality: Pillow CVE upgrades, datetime.utcnow deprecation, SCAN_REPORT sync',
      'Audit: sync SCAN_REPORT.md following full Playwright suite run',
      'Audit: update SCAN_REPORT.md with flutter analyze findings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
      'Release: bump version to v4.105',
      'Ai: integrate continuous learning architecture with vector rag, few-shot injection, collector memory, and active learning',
      'Review-hub: add /api/review/delete_items backend route + fix pytest warnings',
    ],
  ),
  _Release(
    version: 'v4.106',
    date: '2026-08-16',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump version to v4.105',
      'Ai: integrate continuous learning architecture with vector rag, few-shot injection, collector memory, and active learning',
      'Review-hub: add /api/review/delete_items backend route + fix pytest warnings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.105',
    date: '2026-08-16',
    description: 'Ai Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ai: integrate continuous learning architecture with vector rag, few-shot injection, collector memory, and active learning',
      'Review-hub: add /api/review/delete_items backend route + fix pytest warnings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
    ],
  ),
  _Release(
    version: 'v4.104',
    date: '2026-08-16',
    description: 'Review-hub Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Review-hub: add /api/review/delete_items backend route + fix pytest warnings',
      'Audit: update SCAN_REPORT.md via project-scanner full system audit',
      'Review_hub: complete v8 Review Hub card actions, dual titles, Morgan avatar, and delete flows',
      'Review_hub: implement audit-logged review item deletion, official US Mint titles, storage normalization, and UI card actions',
      'Qa: update beta verification matrix and tracker to US Women Quarters 20-coin program',
      'Backend: export config variables in config package and add parse_checklist_notes implementation',
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
    ],
  ),
  _Release(
    version: 'v4.103',
    date: '2026-08-15',
    description: 'Review_hub Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Review_hub: complete v8 Review Hub card actions, dual titles, Morgan avatar, and delete flows',
      'Review_hub: implement audit-logged review item deletion, official US Mint titles, storage normalization, and UI card actions',
      'Qa: update beta verification matrix and tracker to US Women Quarters 20-coin program',
      'Backend: export config variables in config package and add parse_checklist_notes implementation',
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
    ],
  ),
  _Release(
    version: 'v4.102',
    date: '2026-08-15',
    description: 'Review_hub Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Review_hub: implement audit-logged review item deletion, official US Mint titles, storage normalization, and UI card actions',
      'Qa: update beta verification matrix and tracker to US Women Quarters 20-coin program',
      'Backend: export config variables in config package and add parse_checklist_notes implementation',
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
    ],
  ),
  _Release(
    version: 'v4.101',
    date: '2026-08-15',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: update beta verification matrix and tracker to US Women Quarters 20-coin program',
      'Backend: export config variables in config package and add parse_checklist_notes implementation',
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
    ],
  ),
  _Release(
    version: 'v4.100',
    date: '2026-08-15',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: export config variables in config package and add parse_checklist_notes implementation',
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
    ],
  ),
  _Release(
    version: 'v4.99',
    date: '2026-08-15',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: export all configuration variables from config package and restore parse_checklist_notes function',
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
    ],
  ),
  _Release(
    version: 'v4.98',
    date: '2026-08-15',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: auto-bump v4.97 release notes',
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
    ],
  ),
  _Release(
    version: 'v4.97',
    date: '2026-08-15',
    description: 'Ingestion Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ingestion: v7.1 surgical resolution of doc_hash deduplication, resume session flow, canonical audit assertion, and PDF layout budget',
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
    ],
  ),
  _Release(
    version: 'v4.96',
    date: '2026-08-15',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: auto-bump v4.95 release notes',
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
    ],
  ),
  _Release(
    version: 'v4.95',
    date: '2026-08-15',
    description: 'Ingestion Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ingestion: v7 checklist parser, document classifier gateway, and review hub SoR provenance engine',
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
      'Walkthrough: Aug 15 audit review - SCAN_REPORT v4.89 sync and Flutter lint remediation plan',
    ],
  ),
  _Release(
    version: 'v4.94',
    date: '2026-08-15',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump release notes to v4.93',
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
      'Walkthrough: Aug 15 audit review - SCAN_REPORT v4.89 sync and Flutter lint remediation plan',
      'Audit: update SCAN_REPORT to v4.89 with accurate test metrics, correct Dependabot count, and Flutter analyze results',
    ],
  ),
  _Release(
    version: 'v4.93',
    date: '2026-08-15',
    description: 'Ai Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ai: integrate Generate-and-Select verifier services and Antigravity command protocols',
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
      'Walkthrough: Aug 15 audit review - SCAN_REPORT v4.89 sync and Flutter lint remediation plan',
      'Audit: update SCAN_REPORT to v4.89 with accurate test metrics, correct Dependabot count, and Flutter analyze results',
      'Audit: update SCAN_REPORT.md with final Playwright 141/145 pass metrics',
    ],
  ),
  _Release(
    version: 'v4.92',
    date: '2026-08-15',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: synchronize v6.0 canonical 32-issue verification matrix and durable audit engine',
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
      'Walkthrough: Aug 15 audit review - SCAN_REPORT v4.89 sync and Flutter lint remediation plan',
      'Audit: update SCAN_REPORT to v4.89 with accurate test metrics, correct Dependabot count, and Flutter analyze results',
      'Audit: update SCAN_REPORT.md with final Playwright 141/145 pass metrics',
      'Audit: record flutter analyze zero-error result in SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.91',
    date: '2026-08-15',
    description: 'Lint Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Lint: resolve all use_build_context_synchronously warnings across 9 files',
      'Revert "fix(lint): resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits"',
      'Lint: resolve all use_build_context_synchronously warnings â€” add mounted guards and extract context refs before awaits',
      'Walkthrough: Aug 15 audit review - SCAN_REPORT v4.89 sync and Flutter lint remediation plan',
      'Audit: update SCAN_REPORT to v4.89 with accurate test metrics, correct Dependabot count, and Flutter analyze results',
      'Audit: update SCAN_REPORT.md with final Playwright 141/145 pass metrics',
      'Audit: record flutter analyze zero-error result in SCAN_REPORT.md',
      'Audit: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.90',
    date: '2026-08-14',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: synchronize v4.89 release notes',
      'Qa: resolve analyzer warnings, optimize dialog reactivity, and finalize beta test verification matrix',
      'Remediation: backfill canonical theme and reference images for 14 AUG checklist intake',
      'Release: bump version to v4.86',
      'Ingestion: remediate 14 AUG beta test checklist parsing, legislation, and desktop UX',
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
    ],
  ),
  _Release(
    version: 'v4.89',
    date: '2026-08-14',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: resolve analyzer warnings, optimize dialog reactivity, and finalize beta test verification matrix',
      'Remediation: backfill canonical theme and reference images for 14 AUG checklist intake',
      'Release: bump version to v4.86',
      'Ingestion: remediate 14 AUG beta test checklist parsing, legislation, and desktop UX',
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
    ],
  ),
  _Release(
    version: 'v4.88',
    date: '2026-08-14',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: backfill canonical theme and reference images for 14 AUG checklist intake',
      'Release: bump version to v4.86',
      'Ingestion: remediate 14 AUG beta test checklist parsing, legislation, and desktop UX',
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
      'Scanner: run project-scanner full system audit and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.87',
    date: '2026-08-14',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump version to v4.86',
      'Ingestion: remediate 14 AUG beta test checklist parsing, legislation, and desktop UX',
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
      'Scanner: run project-scanner full system audit and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.86',
    date: '2026-08-14',
    description: 'Ingestion Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ingestion: remediate 14 AUG beta test checklist parsing, legislation, and desktop UX',
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
      'Scanner: run project-scanner full system audit and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.85',
    date: '2026-08-14',
    description: 'Checklist Ingestion Remediation, Legislation Seeding & Desktop UX',
    isLatest: false,
    changes: [
      'Backend: implement 2-stage handwritten notes parser and theme slugifier for reference image keys',
      'Backend: add multi-series routing aliases for America the Beautiful, 50 States, DC & Territories, and Women Quarters',
      'Legislation: seed authoritative statutory public laws for PL 110-456, PL 105-124, PL 110-161, and PL 116-330',
      'Review Hub: add MORGAN guide banner, Add All with 100% AI Confidence action, Paper Trail viewer, and gold card styling',
      'Desktop UX: implement 12px high-contrast scrollbars, draggable feedback FAB, and Valuation Pending shimmer badges',
    ],
  ),
  _Release(
    version: 'v4.84',
    date: '2026-08-14',
    description: 'Frontend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Frontend: wire sort preference saving, clean unused ebay method, and resolve analyzer warnings',
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
      'Scanner: run project-scanner full system audit and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.83',
    date: '2026-08-14',
    description: 'E2e Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'E2e: migrate suites 18-21 from flt-glass-pane gating to enterDemo() pattern',
      'Qa: stabilize Playwright timing for suites 18-21 and verify 100% pass rate',
      'Scanner: update SCAN_REPORT.md with exact Playwright E2E execution metrics',
      'Scanner: run project-scanner full system audit and generate SCAN_REPORT.md',
      'Checklist: implement deterministic SlotResolver and System of Record personalized checklist export',
      'Audit: implement SoR v4.0.0 34-column missing image sourcing tracker and multi-account audit',
      'Release: bump to v4.79 with image fixes',
      'Images: resolve missing collection images with GCS reference fallback and card grid rendering',
    ],
  ),
  _Release(
    version: 'v4.82',
    date: '2026-08-13',
    description: 'Checklist Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Checklist: implement deterministic SlotResolver and System of Record personalized checklist export',
      'Audit: implement SoR v4.0.0 34-column missing image sourcing tracker and multi-account audit',
      'Release: bump to v4.79 with image fixes',
      'Images: resolve missing collection images with GCS reference fallback and card grid rendering',
      'Remediation: fix getter check on CoinModel in coin_detail_screen.dart',
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
    ],
  ),
  _Release(
    version: 'v4.81',
    date: '2026-08-13',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: implement SoR v4.0.0 34-column missing image sourcing tracker and multi-account audit',
      'Release: bump to v4.79 with image fixes',
      'Images: resolve missing collection images with GCS reference fallback and card grid rendering',
      'Remediation: fix getter check on CoinModel in coin_detail_screen.dart',
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
    ],
  ),
  _Release(
    version: 'v4.80',
    date: '2026-08-13',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: bump to v4.79 with image fixes',
      'Images: resolve missing collection images with GCS reference fallback and card grid rendering',
      'Remediation: fix getter check on CoinModel in coin_detail_screen.dart',
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
    ],
  ),
  _Release(
    version: 'v4.79',
    date: '2026-08-13',
    description: 'Images Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Images: resolve missing collection images with GCS reference fallback and card grid rendering',
      'Remediation: fix getter check on CoinModel in coin_detail_screen.dart',
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
    ],
  ),
  _Release(
    version: 'v4.78',
    date: '2026-08-13',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: fix getter check on CoinModel in coin_detail_screen.dart',
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
    ],
  ),
  _Release(
    version: 'v4.77',
    date: '2026-08-13',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: 13 Aug beta remediation -- Firestore patch for eric.seaman@yahoo.com, origin filter & acquisition cost display',
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
    ],
  ),
  _Release(
    version: 'v4.76',
    date: '2026-08-13',
    description: 'Tests Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Tests: clarify 2019-W Quarter is a US coin (America the Beautiful series) in suite 18 report highlights',
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.75',
    date: '2026-08-13',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: replace checkmark emoji with ASCII string for Windows console compatibility',
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.74',
    date: '2026-08-13',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: add automated beta test suite v4 with dual-account isolation and zero-drift verification',
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.73',
    date: '2026-08-13',
    description: 'Remediation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Remediation: 13 AUG beta fixes - DB patch, UI tab order, title formatting & grade tooltips',
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.72',
    date: '2026-08-13',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Add REPOSITORY_RULES.md for standalone AI advisors',
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.71',
    date: '2026-08-13',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: system-wide semantic test assertions and safe production account repair',
      'Scanner: update SCAN_REPORT.md with Playwright test metrics',
      'Scanner: update SCAN_REPORT.md from project-scanner run',
    ],
  ),
  _Release(
    version: 'v4.61',
    date: '2026-08-12',
    description: 'Catalog Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Catalog: resolve Beta Test III defects, enforce provenance ledger, and optimize PDF exports',
      'Agent: clean unused variables and getters',
      'Agent: align port 8443 dual-probe, enforce single-instance mutex, and update MORGAN/privacy copy',
      'Programs: implement deterministic SlotResolver matching engine and reseed 31 US Mint programs',
      'Ingestion: catalog-driven quarter normalization, Greysheet task queue timeout, and web inspector UI contrast',
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
    ],
  ),
  _Release(
    version: 'v4.60',
    date: '2026-08-12',
    description: 'Agent Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Agent: clean unused variables and getters',
      'Agent: align port 8443 dual-probe, enforce single-instance mutex, and update MORGAN/privacy copy',
      'Programs: implement deterministic SlotResolver matching engine and reseed 31 US Mint programs',
      'Ingestion: catalog-driven quarter normalization, Greysheet task queue timeout, and web inspector UI contrast',
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
    ],
  ),
  _Release(
    version: 'v4.59',
    date: '2026-08-12',
    description: 'Agent Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Agent: align port 8443 dual-probe, enforce single-instance mutex, and update MORGAN/privacy copy',
      'Programs: implement deterministic SlotResolver matching engine and reseed 31 US Mint programs',
      'Ingestion: catalog-driven quarter normalization, Greysheet task queue timeout, and web inspector UI contrast',
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.58',
    date: '2026-08-12',
    description: 'Programs Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Programs: implement deterministic SlotResolver matching engine and reseed 31 US Mint programs',
      'Ingestion: catalog-driven quarter normalization, Greysheet task queue timeout, and web inspector UI contrast',
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.57',
    date: '2026-08-12',
    description: 'Ingestion Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Ingestion: catalog-driven quarter normalization, Greysheet task queue timeout, and web inspector UI contrast',
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.56',
    date: '2026-08-12',
    description: 'Collection Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.55',
    date: '2026-08-12',
    description: 'Collection Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Collection: implement crash-proof top scrollbar track and viewport pan buttons',
    ],
  ),
  _Release(
    version: 'v4.54',
    date: '2026-08-12',
    description: 'Coins Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Coins: remove unused _faceValue helper',
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.53',
    date: '2026-08-12',
    description: 'Coins Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Coins: enforce unified collection model, country normalization & non-legal tender tab',
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.52',
    date: '2026-08-12',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: integrate run_overnight_tests.py and set Windows Task Scheduler to 6:00 AM daily',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.51',
    date: '2026-08-12',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.50',
    date: '2026-08-12',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: update Playwright selector in 15-domain-completeness.spec.js',
      'Qa: implement legal-grade domain completeness and QC suite v5',
      'Programs: add safe memory image decoding, 2026 America250 and Mint Set checklist matching',
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
    ],
  ),
  _Release(
    version: 'v4.49',
    date: '2026-08-11',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: update Playwright selector in 15-domain-completeness.spec.js',
      'Qa: implement legal-grade domain completeness and QC suite v5',
      'Programs: add safe memory image decoding, 2026 America250 and Mint Set checklist matching',
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
    ],
  ),
  _Release(
    version: 'v4.48',
    date: '2026-08-11',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: update Playwright selector in 15-domain-completeness.spec.js',
      'Qa: implement legal-grade domain completeness and QC suite v5',
      'Programs: add safe memory image decoding, 2026 America250 and Mint Set checklist matching',
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
    ],
  ),
  _Release(
    version: 'v4.47',
    date: '2026-08-11',
    description: 'Qa Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Qa: implement legal-grade domain completeness and QC suite v5',
      'Programs: add safe memory image decoding, 2026 America250 and Mint Set checklist matching',
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
    ],
  ),
  _Release(
    version: 'v4.46',
    date: '2026-08-11',
    description: 'Programs Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Programs: add safe memory image decoding, 2026 America250 and Mint Set checklist matching',
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
      'Release: update release notes v4.40',
    ],
  ),
  _Release(
    version: 'v4.45',
    date: '2026-08-11',
    description: 'Pdf Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Pdf: replace heavy AcroForm checkboxes with lightweight vector boxes to eliminate browser freeze',
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
      'Release: update release notes v4.40',
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
    ],
  ),
  _Release(
    version: 'v4.44',
    date: '2026-08-11',
    description: 'Images Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Images: enable multi-user support and execute image enrichment pipeline',
      'Programs: add download pdf button and safe byte data font parsing',
      'Transfer: enforce strict hard move pattern and clean residual transferred items',
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
      'Release: update release notes v4.40',
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
    ],
  ),
  _Release(
    version: 'v4.43',
    date: '2026-08-11',
    description: 'Mobile Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Mobile: add custom ErrorWidget.builder to render readable UI errors',
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
      'Release: update release notes v4.40',
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
    ],
  ),
  _Release(
    version: 'v4.42',
    date: '2026-08-11',
    description: 'Mobile Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Mobile: robust numeric parsing for collection pricing and counts to prevent gray screen crash',
      'Release: update release notes v4.40',
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
    ],
  ),
  _Release(
    version: 'v4.41',
    date: '2026-08-11',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: update release notes v4.40',
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
    ],
  ),
  _Release(
    version: 'v4.40',
    date: '2026-08-11',
    description: 'Collection Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Collection: remove incompatible RawScrollbar wrapper around TableView.builder resolving solid gray screen crash on web',
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
    ],
  ),
  _Release(
    version: 'v4.39',
    date: '2026-08-11',
    description: 'Web Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Web: harden doc.data() null checks to prevent grey container crash on ghost documents',
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
    ],
  ),
  _Release(
    version: 'v4.38',
    date: '2026-08-11',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: update release notes v4.37',
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
    ],
  ),
  _Release(
    version: 'v4.37',
    date: '2026-08-11',
    description: 'Programs Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Programs: harden checklist printing, UTF-8 font engine, and firestore ghost cleanup',
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
    ],
  ),
  _Release(
    version: 'v4.36',
    date: '2026-08-11',
    description: 'Web Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Web: resolve closing bracket syntax in my_collection_screen',
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
    ],
  ),
  _Release(
    version: 'v4.35',
    date: '2026-08-11',
    description: 'Build Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Build: restore missing try { block in my_collection_screen â€” orphaned catch was causing Dart syntax error',
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
    ],
  ),
  _Release(
    version: 'v4.34',
    date: '2026-08-11',
    description: 'Estate-v3 Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Estate-v3: harden state machine, morgan context, pdf clean schema, and web scrollbar',
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
    ],
  ),
  _Release(
    version: 'v4.33',
    date: '2026-08-11',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: update release notes',
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
    ],
  ),
  _Release(
    version: 'v4.32',
    date: '2026-08-11',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
    ],
  ),
  _Release(
    version: 'v4.31',
    date: '2026-08-11',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: add missing DEFAULT_VISION_MODEL, FALLBACK_VISION_MODEL, DEFAULT_CHAT_MODEL, FALLBACK_CHAT_MODEL constants â€” fixes Cloud Run startup crash',
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
    ],
  ),
  _Release(
    version: 'v4.30',
    date: '2026-08-11',
    description: 'Backend Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Backend: add missing GEMINI_FLASH_MODEL, GEMINI_PRO_MODEL, GEMINI_LITE_MODEL, GEMINI_IMAGE_MODEL constants to config.py â€” Cloud Run was crashing on import',
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.29',
    date: '2026-08-11',
    description: 'Version Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Version: sync kAppVersion to v4.28 and include auto-generated release notes',
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.28',
    date: '2026-08-11',
    description: 'Build Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Build: define missing kAppVersion constant and add constants import to home_dashboard',
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.27',
    date: '2026-08-11',
    description: 'Pdf Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Pdf: parse estimated portfolio market value and acquisition cost basis separately on transfer certificate',
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.26',
    date: '2026-08-11',
    description: 'Transfer Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Transfer: V2.2 atomic claim deletion, schema notes separation, query filters, and 1914 gold vault cleanup',
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.25',
    date: '2026-08-11',
    description: 'Transfer Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Transfer: resolve LT beta feedback V2.1 with feature registry, domain config, email audit, and UI crash fix',
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.24',
    date: '2026-08-11',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: sync SCAN_REPORT.md after full E2E test execution',
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.23',
    date: '2026-08-11',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: run full system check via project-scanner skill and update SCAN_REPORT.md',
      'Currency: fix string interpolation formatting in currency_collection_screen',
      'Currency: complete Phase 3 CurrencyImageService 3-stage fallback cascade, web UI credit badges, and legal PDF watermarking',
      'Currency: complete Phase 2 GCS CORS policy, banknote indexer, and intake engine',
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
    ],
  ),
  _Release(
    version: 'v4.22',
    date: '2026-08-10',
    description: 'Currency Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Currency: fix string interpolation formatting in currency_collection_screen',
      'Currency: complete Phase 3 CurrencyImageService 3-stage fallback cascade, web UI credit badges, and legal PDF watermarking',
      'Currency: complete Phase 2 GCS CORS policy, banknote indexer, and intake engine',
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
    ],
  ),
  _Release(
    version: 'v4.21',
    date: '2026-08-10',
    description: 'Currency Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Currency: fix string interpolation formatting in currency_collection_screen',
      'Currency: complete Phase 3 CurrencyImageService 3-stage fallback cascade, web UI credit badges, and legal PDF watermarking',
      'Currency: complete Phase 2 GCS CORS policy, banknote indexer, and intake engine',
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
    ],
  ),
  _Release(
    version: 'v4.20',
    date: '2026-08-10',
    description: 'Currency Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Currency: complete Phase 3 CurrencyImageService 3-stage fallback cascade, web UI credit badges, and legal PDF watermarking',
      'Currency: complete Phase 2 GCS CORS policy, banknote indexer, and intake engine',
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
      'Audit: generate SCAN_REPORT.md system audit report',
    ],
  ),
  _Release(
    version: 'v4.19',
    date: '2026-08-10',
    description: 'Currency Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Currency: complete Phase 2 GCS CORS policy, banknote indexer, and intake engine',
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
      'Audit: generate SCAN_REPORT.md system audit report',
    ],
  ),
  _Release(
    version: 'v4.18',
    date: '2026-08-10',
    description: 'Currency Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Currency: complete Phase 1 SOP, operator runbook, and legacy scraper quarantine',
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
      'Audit: generate SCAN_REPORT.md system audit report',
    ],
  ),
  _Release(
    version: 'v4.17',
    date: '2026-08-10',
    description: 'Valuation Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Valuation: fix face/melt value math, add report modal, upgrade beta testers to family_estate',
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
      'Audit: generate SCAN_REPORT.md system audit report',
      'Transfer: replace invalid activeThumbColor parameter with activeColor on SwitchListTile',
      'Transfer: replace activeThumbColor with activeColor on CheckboxListTile â€” activeThumbColor is a Switch-only parameter',
      'Transfer: overhaul PDF invoice formatting, default unscrubbed toggles, remove estate references, and add web receiving flow',
    ],
  ),
  _Release(
    version: 'v4.17',
    date: '2026-08-10',
    description: 'Hooks Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Hooks: use venv Python in pre-push hook to avoid Windows Store stub error; update walkthrough',
      'Audit: resolve 3 report-generation bugs + estate pipeline import error',
      'Estate: implement missing downsample_image_to_300dpi_thumb in passport_pdf_generator',
      'Audit: generate SCAN_REPORT.md system audit report',
      'Transfer: replace invalid activeThumbColor parameter with activeColor on SwitchListTile',
      'Transfer: replace activeThumbColor with activeColor on CheckboxListTile â€” activeThumbColor is a Switch-only parameter',
      'Transfer: overhaul PDF invoice formatting, default unscrubbed toggles, remove estate references, and add web receiving flow',
      'Release: sync release notes for system health check',
    ],
  ),
  _Release(
    version: 'v4.16',
    date: '2026-08-09',
    description: 'Merge(dev->main) Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Merge(dev->main): overhaul PDF invoice formatting, default unscrubbed toggles, remove estate references, and add web receiving flow',
      'Transfer: replace invalid activeThumbColor parameter with activeColor on SwitchListTile',
      'Transfer: replace activeThumbColor with activeColor on CheckboxListTile â€” activeThumbColor is a Switch-only parameter',
      'Transfer: overhaul PDF invoice formatting, default unscrubbed toggles, remove estate references, and add web receiving flow',
      'Mobile: remove unused imports, home dashboard improvements + docs: release notes, SCAN_REPORT, E2E test fixes',
      'Release: sync release notes for system health check',
      'Audit: v4.2 SCAN_REPORT - Phase 3 features, 22 CVEs resolved, E2E skip fix, walkthrough updated',
      'Release: update release notes for v4.14',
    ],
  ),
  _Release(
    version: 'v4.15',
    date: '2026-08-09',
    description: 'Audit Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Audit: v4.2 SCAN_REPORT - Phase 3 features, 22 CVEs resolved, E2E skip fix, walkthrough updated',
      'Release: update release notes for v4.14',
      'Master-e2e: skip localhost:5000 tests in automated audit when local dev server not running',
      'Scan: update Playwright E2E final tally (120/122 passed) in SCAN_REPORT.md',
      'Mobile: remove unused imports in settings_screen and http_auth_client',
      'Scan: run full system check and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.14',
    date: '2026-08-09',
    description: 'Master-e2e Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Master-e2e: skip localhost:5000 tests in automated audit when local dev server not running',
      'Scan: update Playwright E2E final tally (120/122 passed) in SCAN_REPORT.md',
      'Mobile: remove unused imports in settings_screen and http_auth_client',
      'Scan: run full system check and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.13',
    date: '2026-08-09',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: update Playwright E2E final tally (120/122 passed) in SCAN_REPORT.md',
      'Mobile: remove unused imports in settings_screen and http_auth_client',
      'Scan: run full system check and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.12',
    date: '2026-08-09',
    description: 'Mobile Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Mobile: remove unused imports in settings_screen and http_auth_client',
      'Scan: run full system check and generate SCAN_REPORT.md',
    ],
  ),
  _Release(
    version: 'v4.11',
    date: '2026-08-09',
    description: 'Scan Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Scan: run full system check and generate SCAN_REPORT.md',
      'Release: finalize release notes sync',
      'Release: update release notes',
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
    ],
  ),
  _Release(
    version: 'v4.10',
    date: '2026-08-08',
    description: 'Merge(dev->main) Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Merge(dev->main): email casing normalization',
      'Release: finalize release notes sync',
      'Release: update release notes',
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Merge(dev->main): clean unused functions',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Merge(dev->main): resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
    ],
  ),
  _Release(
    version: 'v4.9',
    date: '2026-08-08',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: update release notes',
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
    ],
  ),
  _Release(
    version: 'v4.8',
    date: '2026-08-08',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: update release notes',
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
    ],
  ),
  _Release(
    version: 'v4.7',
    date: '2026-08-08',
    description: 'Auth Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
      'Harness: complete 100% full design acceptance gate for Phase 3 Step 1',
    ],
  ),
  _Release(
    version: 'v4.6',
    date: '2026-08-08',
    description: 'Auth Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Auth: normalize user emails to lowercase across auth and Firestore path getters',
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
      'Harness: complete 100% full design acceptance gate for Phase 3 Step 1',
    ],
  ),
  _Release(
    version: 'v4.5',
    date: '2026-08-08',
    description: 'Release Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Release: automate release notes generation via git commits and CI build step',
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
      'Harness: complete 100% full design acceptance gate for Phase 3 Step 1',
      'Harness: finalize Master E2E Verification Harness v6 as full Design-Acceptance Gate for Phase 3 Step 1',
    ],
  ),
  _Release(
    version: 'v4.4',
    date: '2026-08-08',
    description: 'Transfer Enhancements & Platform Updates',
    isLatest: false,
    changes: [
      'Transfer: clean unused helper functions in lateral transfer screen',
      'Transfer: resolve Lateral Transfer inventory loading, multi-term search, and collection selection',
      'Billing: complete Phase 3 Step 2 Stripe billing integration and attorney portal signed URLs',
      'Seo: add non-affiliation disclaimer metadata and JSON-LD schema for Google indexing',
      'Harness: add explicit PROOF console logs for security, dual-write, lazy 48h release, and multi-token paths v8',
      'Harness: complete 100% full design acceptance gate for Phase 3 Step 1',
      'Harness: finalize Master E2E Verification Harness v6 as full Design-Acceptance Gate for Phase 3 Step 1',
      'Harness: expand Master E2E Verification Harness v5 with lazy 48h release test, multiple token creation, and complete assertion details',
    ],
  ),
  _Release(
    version: 'v4.3',
    date: '2026-08-08',
    description: 'Phase 2 & 3 Feature Suite & System Resilience',
    isLatest: false,
    changes: [
      'Phase 2 Step 3 Vision Ingestion: hardware capture v2, cv2 focus window, WebRTC fallback, frame buffer optimization',
      'Phase 2 Step 4 Morgan AI Persistence: session context engine, chat history persistence, pre-filled suggestion chips',
      'Phase 2 Step 5 Desktop Bulk Import: deduplication hub, spreadsheet import template, and valuation pipeline',
      'Phase 3 Step 1 EPN Wishlist Links: affiliate matcher, public reservation router, and security-compliant gift streams',
      'Phase 3 Step 2 Stripe Billing: subscription management and attorney portal signed PDF URLs',
      'Lateral Transfer System Resilience: inventory loading fixes, multi-term search, and collection selection',
    ],
  ),
  _Release(
    version: 'v4.2',
    date: '2026-08-05',
    description: 'Desktop Beta Enhancements & COA Validation Engine',
    isLatest: false,
    changes: [
      'COA Inspector Mintage Ceiling Validation: 3-state verdict chip and serial regex sanitization',
      'Program Manager Dual Filters: geographical mint mark and finish/strike responsive Wrap chips',
      'Security-Compliant Wishlist Gift Reservations: top-level public wishlist writes and real-time family activity stream',
      'Beta Feedback File Attachment: image upload, removal toggle, and open feedback counter badge',
    ],
  ),
  _Release(
    version: 'v4.1',
    date: '2026-07-30',
    description: 'Greysheet Valuation, Bulk Upload & System Resilience',
    isLatest: false,
    changes: [
      'Greysheet Market Valuation Integration: real-time CDN bid/ask prices, CPG retail attribution, and daily portfolio snapshot sync.',
      'Automated Arbitrage Deal Finder & Wishlist EPN matcher: spot underpriced coins and affiliate matches instantly.',
      'Bulk Upload Template: streamlined CSV/Excel ingestion template for uploading collections in bulk.',
      'Financials & Melt Valuation Card: live melt calculations for gold, silver, platinum, and palladium spot prices.',
      'Scraper Resilience Pass: TLS fingerprint bypass (curl_cffi) and direct candidates routing for US Mint, PCGS, and NGC sources.',
      'Backend Observability & System Audit: API request logging, automated diagnostic audit scripts, and Cloud Run health monitoring.',
    ],
  ),
  _Release(
    version: 'v4.0',
    date: '2026-07-08',
    description: 'Greysheet Market Valuation Integration',
    isLatest: false,
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
