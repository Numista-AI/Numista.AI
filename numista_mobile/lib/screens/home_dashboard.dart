import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:intl/intl.dart' as intl;
import '../constants.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import '../services/http_auth_client.dart';
import 'dart:async';
import 'dart:convert';
import 'dart:math' as math;
import '../services/melt_value_service.dart';
import '../services/portfolio_snapshot_service.dart';
import '../services/set_expansion_helper.dart';
import '../services/batch_valuation_service.dart';
import '../widgets/collection_card_image.dart';
import '../services/beta_checklist_service.dart';
import '../services/coin_programs_data.dart';
import '../models/program_model.dart';
import '../utils/slot_resolver.dart';
import '../widgets/beta_welcome_dialog.dart';

class HomeDashboard extends StatefulWidget {
  /// Called when the user taps "Ask Morgan" — routes to 'AI Deepdive'.
  final VoidCallback? onAskMorgan;
  /// Called when the user taps a Morgan suggestion chip — navigates to AI Deepdive
  /// with the given query pre-populated in the chat.
  final void Function(String query)? onAskMorganWithQuery;
  /// Called to navigate to My Collection (e.g. to run AI Valuation).
  final VoidCallback? onNavigateToCollection;
  final VoidCallback? onAddCoin;
  final VoidCallback? onTakePhoto;
  final VoidCallback? onOpenReview;
  final VoidCallback? onOpenPrograms;
  final int reviewQueueCount;
  final bool isReviewCountLoading;
  final Stream<CombinedDashboardData>? testStream;

  const HomeDashboard({
    super.key,
    this.onAskMorgan,
    this.onAskMorganWithQuery,
    this.onNavigateToCollection,
    this.onAddCoin,
    this.onTakePhoto,
    this.onOpenReview,
    this.onOpenPrograms,
    this.reviewQueueCount = 0,
    this.isReviewCountLoading = false,
    this.testStream,
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

  bool _showCollectionValue = false;
  final TextEditingController _morganQueryCtrl = TextEditingController();
  final FocusNode _morganFocusNode = FocusNode();
  int _streamNonce = 0;

  @override
  void initState() {
    super.initState();
    if (widget.testStream != null) {
      return;
    }
    _fetchSpotPrices();
    // Restore persisted progress so Resume banner appears after page refresh
    BatchValuationService.instance.restoreFromFirestore();
    // Auto-prompt Beta Welcome Dialog for new or uninitiated testers
    WidgetsBinding.instance.addPostFrameCallback((_) async {
      BetaChecklistService.syncExistingAccountProgress();
      if (await BetaWelcomeDialog.shouldAutoShow()) {
        if (mounted) BetaWelcomeDialog.show(context);
      }
    });
  }

  @override
  void dispose() {
    _morganQueryCtrl.dispose();
    _morganFocusNode.dispose();
    super.dispose();
  }

  Future<void> _fetchSpotPrices() async {

    try {
      final response = await HttpAuthClient.get(
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
        });
      }
    } catch (e) {
      // Ignore spot price fetch failures on dashboard load.
    }
  }


  double _parseCurrency(dynamic value) {
    if (value == null) return 0.0;
    final raw  = value.toString();
    if (raw == 'Pending' || raw.isEmpty) return 0.0;
    // Normalise all dash variants and strip commas
    final norm = raw
        .replaceAll('Â£', '£')
        .replaceAll('Â', '')
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
          key: ValueKey(_streamNonce),
          stream: widget.testStream ?? _getCombinedStream(),
          builder: (context, snapshot) {
            if (!snapshot.hasData && snapshot.connectionState == ConnectionState.waiting) {
              return _buildLoadingHome();
            }
            if (snapshot.hasError) {
              return _buildErrorHome();
            }

            final coins = snapshot.data?.coins ?? [];
            final currency = snapshot.data?.currency ?? [];
            final worldItems = snapshot.data?.worldItems ?? [];

            return Builder(
              builder: (context) {
                final isNativePhone = outerConstraints.maxWidth < 800;

                // ── Compute portfolio metrics ──────────────────────────────────
                // Use expansion-aware counting (Dimes Bug v2.2)
                final coinDocIds = coins.map((d) => (d['id'] ?? '').toString()).toList();
                final expansion = expandCollection(coins, coinDocIds);
                final int totalCoins = expansion.totalCoins;
                final int totalItems = totalCoins + currency.length + worldItems.length;
            double cpgTotal = 0;
            double acquisitionCost = 0;
            double meltValue       = 0;
            double faceValue       = 0;

            Map<String, double> programValues = {};

            // 1. Process Coins collection
            for (final data in coins) {
              final valStr = data['ai_estimated_value'] ?? data['AI Estimated Value'];
              final valueStatus = data['ai_value_status']?.toString() ?? '';
              final isPending = valueStatus == 'pending' || 
                  valStr?.toString() == 'Pending' ||
                  valStr?.toString() == '\$0.50';

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

              // Valuation fields (NET-372: CPG Retail only, bid removed)
              final coinCpg = _parseCurrency(data['cpgRetail']);
              final finalCpg = coinCpg > 0 ? coinCpg : finalVal;

              if (!isPending) {
                cpgTotal += finalCpg;
              }
              acquisitionCost += _parseCurrency(data['Cost']);
              meltValue       += liveMelt;
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');

              // Track per-program value for the bar chart
              if (!isPending) {
                final program = data['Program/Series']?.toString() ?? 'Other';
                programValues[program] = (programValues[program] ?? 0) + finalCpg;
              }
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

              cpgTotal += curCpg > 0 ? curCpg : finalVal;

              acquisitionCost += _parseCurrency(data['Cost']);
              faceValue       += _computeFaceValue(data['Denomination']?.toString() ?? '');
            }

            // 3. Process World Items collection
            for (final data in worldItems) {
              final estVal = _parseCurrency(data['estimated_value']);
              final purchPrice = _parseCurrency(data['purchase_price']);
              final finalVal = estVal > 0 ? estVal : purchPrice;

              final wCpg = _parseCurrency(data['cpgRetail']);

              cpgTotal += wCpg > 0 ? wCpg : finalVal;

              acquisitionCost += purchPrice;
              final spotEntry = _parseCurrency(data['spot_value_at_entry']);
              if (spotEntry > 0) {
                meltValue += spotEntry;
              }
              faceValue += _computeFaceValue(data['denomination']?.toString() ?? '');
            }

            final portfolioValue = cpgTotal;

            // ── Portfolio snapshot (fire-and-forget) ───────────────────────
            if (widget.testStream == null && (totalCoins > 0 || totalItems > 0)) {
              PortfolioSnapshotService.maybeTakeSnapshot(
                totalCoins: totalCoins,
                portfolioValue: portfolioValue,
                meltValue: meltValue,
                acquisitionCost: acquisitionCost,
                faceValue: faceValue,
              );
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

            final mainContent = Container(
              color: const Color(0xFFEEF3F8),
              child: SingleChildScrollView(
                padding: EdgeInsets.fromLTRB(20, 20, 20, isNativePhone ? 32 : 24),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    if (isNativePhone) ...[
                      ElevatedButton.icon(
                        onPressed: widget.onAddCoin,
                        icon: const Icon(Icons.add_circle_outline, size: 22),
                        label: const Text(
                          'Add to collection',
                          style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF1D4F91),
                          foregroundColor: Colors.white,
                          minimumSize: const Size(double.infinity, 56),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12),
                          ),
                          elevation: 0,
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Save a coin to your collection',
                        style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
                      ),
                      const SizedBox(height: 16),
                    ],
                    _buildAskMorganCard(isNativePhone),
                    const SizedBox(height: 16),
                    if (isNativePhone) ...[
                      _buildCollectionValueCard(totalCoins, portfolioValue),
                      const SizedBox(height: 16),
                      _buildCoinProgramCard(coins),
                    ] else
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(child: _buildCollectionValueCard(totalCoins, portfolioValue)),
                          const SizedBox(width: 16),
                          Expanded(child: _buildCoinProgramCard(coins)),
                        ],
                      ),
                    const SizedBox(height: 16),
                    _buildYourNextActionCard(totalCoins),
                    const SizedBox(height: 16),
                    _buildRecentlyAddedCard(last5, isNativePhone),
                  ],
                ),
              ),
            );

            return mainContent;
              },
            );
          },
        );
      },
    );
  }

  Widget _buildLoadingHome() {
    return Container(
      color: const Color(0xFFEEF3F8),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFFFF),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFF1D4F91), width: 1.5),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      SizedBox(
                        width: 28,
                        height: 28,
                        child: CircularProgressIndicator(
                          strokeWidth: 3,
                          color: Color(0xFF1D4F91),
                        ),
                      ),
                      SizedBox(width: 14),
                      Text(
                        'Loading your home',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w800,
                          color: Color(0xFF0B1A2E),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'This may take a moment.',
                    style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    height: 18,
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: const Color(0xFFD5DEEA),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    height: 44,
                    width: 160,
                    decoration: BoxDecoration(
                      color: const Color(0xFFD5DEEA),
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xFFFFFFFF),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xFFD5DEEA)),
              ),
              child: const Text(
                'Recently added',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0B1A2E),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorHome() {
    return Container(
      color: const Color(0xFFEEF3F8),
      padding: const EdgeInsets.all(20),
      alignment: Alignment.topCenter,
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: const Color(0xFFFFF5F5),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFF6B1A1A), width: 1.5),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              "We couldn't load your home",
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Color(0xFF6B1A1A),
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Please try again. Your coins are safe.',
              style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
            ),
            const SizedBox(height: 18),
            ElevatedButton(
              onPressed: () => setState(() => _streamNonce++),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF1D4F91),
                foregroundColor: Colors.white,
                minimumSize: const Size(140, 56),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              child: const Text(
                'Try again',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAskMorganCard(bool isPhone) {
    void submitQuery() {
      final q = _morganQueryCtrl.text.trim();
      if (q.isEmpty) {
        widget.onAskMorgan?.call();
      } else {
        widget.onAskMorganWithQuery?.call(q);
      }
    }

    final micBtn = OutlinedButton.icon(
      onPressed: () {
        _morganFocusNode.requestFocus();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Voice input coming soon — type your question above.'),
            duration: Duration(seconds: 2),
          ),
        );
      },
      icon: const Icon(Icons.mic_none, color: Color(0xFF0B1A2E), size: 22),
      label: const Text(
        'Microphone',
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF0B1A2E)),
      ),
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(140, 56),
        side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );

    final photoBtn = OutlinedButton.icon(
      onPressed: widget.onTakePhoto,
      icon: const Icon(Icons.photo_camera_outlined, color: Color(0xFF0B1A2E), size: 22),
      label: const Text(
        'Photo',
        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: Color(0xFF0B1A2E)),
      ),
      style: OutlinedButton.styleFrom(
        minimumSize: const Size(120, 56),
        side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );

    final queryField = TextField(
      controller: _morganQueryCtrl,
      focusNode: _morganFocusNode,
      onSubmitted: (_) => submitQuery(),
      style: const TextStyle(fontSize: 18, color: Color(0xFF0B1A2E)),
      decoration: InputDecoration(
        hintText: 'Type or say your question...',
        hintStyle: const TextStyle(fontSize: 18, color: Color(0xFF0B1A2E)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(10),
          borderSide: const BorderSide(color: Color(0xFF1D4F91), width: 2),
        ),
      ),
    );

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1D4F91), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  border: Border.all(color: const Color(0xFF1D4F91), width: 2),
                ),
                child: const Icon(Icons.psychology_outlined, color: Color(0xFF1D4F91), size: 30),
              ),
              const SizedBox(width: 14),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Ask Morgan',
                      style: TextStyle(
                        fontSize: 26,
                        fontWeight: FontWeight.w800,
                        color: Color(0xFF0B1A2E),
                      ),
                    ),
                    SizedBox(height: 2),
                    Text(
                      'Type a question, or use the buttons. Morgan will help.',
                      style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (isPhone) ...[
            queryField,
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(child: micBtn),
                const SizedBox(width: 10),
                Expanded(child: photoBtn),
              ],
            ),
          ] else
            Row(
              children: [
                Expanded(child: queryField),
                const SizedBox(width: 10),
                micBtn,
                const SizedBox(width: 10),
                photoBtn,
              ],
            ),
          const SizedBox(height: 10),
          const Text(
            'Take a photo and Morgan will tell you what coin it is',
            style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
          ),
        ],
      ),
    );
  }

  Widget _buildCollectionValueCard(int totalCoins, double portfolioValue) {
    final formattedWords =
        '${intl.NumberFormat('#,##0').format(portfolioValue.round())} dollars';
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFF3F6FA),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1D4F91), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Collection value',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0B1A2E),
            ),
          ),
          const SizedBox(height: 8),
          if (totalCoins == 0)
            const Text(
              'No coins yet. Value stays hidden for your safety once you add some.',
              style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
            )
          else if (!_showCollectionValue) ...[
            const Text(
              'Hidden for your safety',
              style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: () => setState(() => _showCollectionValue = true),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(140, 56),
                backgroundColor: const Color(0xFFFFFFFF),
                side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              child: const Text(
                'Show value',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0B1A2E),
                ),
              ),
            ),
          ] else ...[
            Text(
              formattedWords,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0B1A2E),
              ),
            ),
            const SizedBox(height: 14),
            OutlinedButton(
              onPressed: () => setState(() => _showCollectionValue = false),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(140, 56),
                backgroundColor: const Color(0xFFFFFFFF),
                side: const BorderSide(color: Color(0xFF1D4F91), width: 1.5),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10),
                ),
              ),
              child: const Text(
                'Hide value',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0B1A2E),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  ({String name, int found, int total})? _computeActiveProgramProgress(
    List<Map<String, dynamic>> coins,
  ) {
    if (coins.isEmpty) return null;
    for (final list in CoinProgramsData.usPrograms.values) {
      for (final prog in list) {
        int found = 0;
        int total = 0;
        for (final pc in prog.coins) {
          if (pc.name.contains('Pending')) continue;
          final varieties = pc.varieties.isEmpty
              ? [const ChecklistVariety(id: '', label: '')]
              : pc.varieties;
          for (final v in varieties) {
            total++;
            final owned = coins.any(
              (c) => SlotResolver.isMatch(c, prog, pc) && SlotResolver.matchesVariety(c, v),
            );
            if (owned) found++;
          }
        }
        if (found > 0 && total > 0) {
          return (name: prog.name, found: found, total: total);
        }
      }
    }
    return null;
  }

  Widget _buildCoinProgramCard(List<Map<String, dynamic>> coins) {
    final prog = _computeActiveProgramProgress(coins);
    final ratio = prog == null ? 0.0 : (prog.found / prog.total).clamp(0.0, 1.0);

    return InkWell(
      onTap: widget.onOpenPrograms,
      borderRadius: BorderRadius.circular(14),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFFFFFFFF),
          borderRadius: BorderRadius.circular(14),
          border: Border.all(color: const Color(0xFFD5DEEA), width: 1.5),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Coin program',
              style: TextStyle(
                fontSize: 22,
                fontWeight: FontWeight.w800,
                color: Color(0xFF0B1A2E),
              ),
            ),
            const SizedBox(height: 8),
            Text(
              prog == null
                  ? 'No program started yet. Programs help you track a set, like State Quarters.'
                  : '${prog.name}: ${prog.found} of ${prog.total} found',
              style: const TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(999),
              child: LinearProgressIndicator(
                value: ratio,
                minHeight: 16,
                backgroundColor: const Color(0xFFD5DEEA),
                valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF1D4F91)),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildYourNextActionCard(int totalCoins) {
    final bool hasReview = !widget.isReviewCountLoading && widget.reviewQueueCount > 0;
    final String headline;
    final String? subtitle;
    final String buttonLabel;
    final VoidCallback? onPressed;

    if (hasReview) {
      final n = widget.reviewQueueCount;
      headline = '$n coin${n == 1 ? '' : 's'} ${n == 1 ? 'is' : 'are'} waiting for your OK';
      subtitle = null;
      buttonLabel = 'Review now';
      onPressed = widget.onOpenReview;
    } else if (totalCoins == 0) {
      headline = 'Add your first coin';
      subtitle = 'Start with one coin you have nearby.';
      buttonLabel = 'Add to collection';
      onPressed = widget.onAddCoin;
    } else {
      headline = 'Explore your collection';
      subtitle = 'You have $totalCoins coin${totalCoins == 1 ? '' : 's'} saved. Open your collection or track a coin program.';
      buttonLabel = 'My Collection';
      onPressed = widget.onNavigateToCollection;
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFE8F0FB),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF1D4F91), width: 1.5),
      ),
      child: Wrap(
        spacing: 16,
        runSpacing: 14,
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        children: [
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'Your next action',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: Color(0xFF0B1A2E),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                headline,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.w800,
                  color: Color(0xFF0B1A2E),
                ),
              ),
              if (subtitle != null) ...[
                const SizedBox(height: 4),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
                ),
              ],
            ],
          ),
          ElevatedButton(
            onPressed: onPressed,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1D4F91),
              foregroundColor: Colors.white,
              minimumSize: const Size(160, 56),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
              elevation: 0,
            ),
            child: Text(
              buttonLabel,
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentlyAddedCard(List<Map<String, dynamic>> last5, bool isPhone) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFFFFFFFF),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFD5DEEA), width: 1.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Recently added',
            style: TextStyle(
              fontSize: 22,
              fontWeight: FontWeight.w800,
              color: Color(0xFF0B1A2E),
            ),
          ),
          const SizedBox(height: 14),
          if (last5.isEmpty)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF1D4F91), width: 1.5),
              ),
              child: const Text(
                'No coins yet. Add your first coin to see it here.',
                style: TextStyle(fontSize: 20, color: Color(0xFF0B1A2E)),
              ),
            )
          else
            LayoutBuilder(
              builder: (context, bc) {
                final cols = isPhone ? 2 : 5;
                const spacing = 12.0;
                final tileWidth = ((bc.maxWidth - spacing * (cols - 1)) / cols).clamp(130.0, 260.0);
                return Wrap(
                  spacing: spacing,
                  runSpacing: spacing,
                  children: last5.map((data) {
                    final year = data['Year']?.toString().replaceAll(RegExp(r'\.0$'), '') ??
                        data['year']?.toString().replaceAll(RegExp(r'\.0$'), '') ??
                        '';
                    final series = data['Program/Series']?.toString() ?? data['program_series']?.toString() ?? '';
                    final theme = data['Theme/Subject']?.toString() ?? data['theme_subject']?.toString() ?? '';
                    final denom = data['Denomination']?.toString() ?? data['denomination']?.toString() ?? '';
                    final coinName = series.isNotEmpty && series != 'Multiple'
                        ? series
                        : theme.isNotEmpty && theme != 'Multiple'
                            ? theme
                            : (denom.isNotEmpty ? denom : 'Coin');
                    return SizedBox(
                      width: tileWidth,
                      child: InkWell(
                        onTap: widget.onNavigateToCollection,
                        borderRadius: BorderRadius.circular(12),
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF7F9FC),
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Column(
                            children: [
                              SizedBox(
                                width: 96,
                                height: 96,
                                child: CollectionCardImage(
                                  data: data,
                                  emptyPlaceholderBuilder: (_) => _buildNoPhotoYetTile(),
                                ),
                              ),
                              const SizedBox(height: 10),
                              Text(
                                coinName,
                                maxLines: 2,
                                overflow: TextOverflow.ellipsis,
                                textAlign: TextAlign.center,
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF0B1A2E),
                                ),
                              ),
                              if (year.isNotEmpty && year != 'Multiple') ...[
                                const SizedBox(height: 4),
                                Text(
                                  year,
                                  style: const TextStyle(
                                    fontSize: 18,
                                    color: Color(0xFF0B1A2E),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                );
              },
            ),
        ],
      ),
    );
  }

  Widget _buildNoPhotoYetTile() {
    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: const Color(0xFF1D4F91), width: 2),
      ),
      child: const Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.no_photography_outlined, size: 22, color: Color(0xFF1D4F91)),
          SizedBox(height: 4),
          Text(
            'No photo\nyet',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0B1A2E),
              height: 1.1,
            ),
          ),
        ],
      ),
    );
  }

}
