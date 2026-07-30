import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';
import '../constants.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/coin_model.dart';

const _apiUrl = kApiBaseUrl;

// ─── ANA Standard Grade Scale ────────────────────────────────────────────────

const _anaGrades = [
  'Ungraded', 'Unknown', 'P-1 (Poor)', 'FR-2 (Fair)', 'AG-3 (About Good)',
  'G-4 (Good)', 'G-6 (Good)', 'VG-8 (Very Good)', 'VG-10 (Very Good)',
  'F-12 (Fine)', 'F-15 (Fine)', 'VF-20 (Very Fine)', 'VF-25 (Very Fine)',
  'VF-30 (Very Fine)', 'VF-35 (Very Fine)', 'EF-40 (Extremely Fine)',
  'EF-45 (Extremely Fine)', 'AU-50 (About Uncirculated)',
  'AU-55 (About Uncirculated)', 'AU-58 (About Uncirculated)',
  'MS-60', 'MS-61', 'MS-62', 'MS-63', 'MS-64',
  'MS-65', 'MS-66', 'MS-67', 'MS-68', 'MS-69', 'MS-70',
  'PF-60 (Proof)', 'PF-61 (Proof)', 'PF-62 (Proof)', 'PF-63 (Proof)',
  'PF-64 (Proof)', 'PF-65 (Proof)', 'PF-66 (Proof)', 'PF-67 (Proof)',
  'PF-68 (Proof)', 'PF-69 (Proof)', 'PF-70 (Proof)',
  'SMS (Special Mint Set)', 'SP-63 (Specimen)', 'SP-65 (Specimen)',
];

// ─── Nickname data model ──────────────────────────────────────────────────────

class NicknameSuggestion {
  final String id, nickname, mapsTo, category, example, notes,
      submittedBy, status;
  final double avgRating;
  final int voteCount;
  final bool inAiDict, isBuiltin;
  int? yourRating;

  NicknameSuggestion({
    required this.id, required this.nickname, required this.mapsTo,
    required this.category, required this.example, required this.notes,
    required this.submittedBy, required this.status,
    required this.avgRating, required this.voteCount,
    required this.inAiDict, required this.isBuiltin, this.yourRating,
  });

  factory NicknameSuggestion.fromJson(Map<String, dynamic> j) =>
      NicknameSuggestion(
        id: j['id'] ?? '', nickname: j['nickname'] ?? '',
        mapsTo: j['maps_to'] ?? '', category: j['category'] ?? 'Other',
        example: j['example'] ?? '', notes: j['notes'] ?? '',
        submittedBy: j['submitted_by'] ?? '', status: j['status'] ?? 'pending',
        avgRating: (j['avg_rating'] ?? 0.0).toDouble(),
        voteCount: j['vote_count'] ?? 0,
        inAiDict: j['in_ai_dict'] ?? false,
        isBuiltin: j['is_builtin'] ?? false,
      );
}

// ─── Grade review data model ──────────────────────────────────────────────────

class GradeReviewCoin {
  final String coinId, year, mintMark, denomination, programSeries,
      themeSubject, condition, source, scanSource, imageUrl, imageUrlObverse, imageUrlReverse, reviewStatus;
  final double confidenceScore;
  final bool lowConfidence, hasBbox;
  final int reviewCount;
  final Map<String, dynamic> slotBbox;

  GradeReviewCoin({
    required this.coinId, required this.year, required this.mintMark,
    required this.denomination, required this.programSeries,
    required this.themeSubject, required this.condition,
    required this.confidenceScore, required this.lowConfidence,
    required this.source, required this.imageUrl,
    required this.reviewStatus, required this.reviewCount,
    this.scanSource = '',
    this.imageUrlObverse = '',
    this.imageUrlReverse = '',
    this.slotBbox = const {},
    this.hasBbox = false,
  });

  factory GradeReviewCoin.fromJson(Map<String, dynamic> j) {
    final bbox = j['slot_bbox'] as Map? ?? {};
    final hasBbox = bbox.isNotEmpty &&
        ((bbox['w_pct'] ?? 0.0) as num) > 0 &&
        ((bbox['h_pct'] ?? 0.0) as num) > 0;
    final obv = j['image_url_obverse'] ?? j['imageUrlObverse'] ?? '';
    final rev = j['image_url_reverse'] ?? j['imageUrlReverse'] ?? '';
    return GradeReviewCoin(
      coinId: j['coin_id'] ?? '', year: j['year'] ?? '',
      mintMark: j['mint_mark'] ?? '', denomination: j['denomination'] ?? '',
      programSeries: j['program_series'] ?? '',
      themeSubject: j['theme_subject'] ?? '',
      condition: j['condition'] ?? 'Ungraded',
      confidenceScore: (j['confidence_score'] ?? 0.0).toDouble(),
      lowConfidence: j['low_confidence'] ?? false,
      source: j['source'] ?? '',
      scanSource: j['scan_source'] ?? j['source'] ?? '',
      imageUrl: obv,
      imageUrlObverse: obv,
      imageUrlReverse: rev,
      slotBbox: Map<String, dynamic>.from(bbox),
      reviewStatus: j['grade_review_status'] ?? 'pending',
      reviewCount: j['grade_review_count'] ?? 0,
      hasBbox: hasBbox,
    );
  }

  String get displayName {
    final parts = [year, mintMark].where((s) => s.isNotEmpty).join('-');
    final series = programSeries.isNotEmpty ? programSeries
        : denomination.isNotEmpty ? denomination : 'Coin';
    return parts.isNotEmpty ? '$parts $series' : series;
  }
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

class HumanAiTrainerScreen extends StatefulWidget {
  const HumanAiTrainerScreen({super.key});

  @override
  State<HumanAiTrainerScreen> createState() => _HumanAiTrainerScreenState();
}

class _HumanAiTrainerScreenState extends State<HumanAiTrainerScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tab;

  // Grade stats
  int _totalAiGraded = 0, _pendingGradeReview = 0,
      _confirmedGrades = 0, _flaggedGrades = 0;
  // Nickname stats
  int _nicknamePending = 0;

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 5, vsync: this);
    _loadStats();
    _loadImageStats();
  }

  int _pendingImageQc = 0;

  Future<void> _loadImageStats() async {
    final email = AuthService.userEmail;
    try {
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .where('image_verification_status', whereIn: ['unverified', 'flagged'])
          .get();
      if (mounted) {
        setState(() {
          _pendingImageQc = snap.docs.length;
        });
      }
    } catch (_) {}
  }

  @override
  void dispose() { _tab.dispose(); super.dispose(); }

  Future<void> _loadStats() async {
    _loadImageStats();
    final email = Uri.encodeComponent(AuthService.userEmail);
    try {
      final results = await Future.wait([
        http.get(Uri.parse('$_apiUrl/api/grade_review/stats?user_email=$email')),
        http.get(Uri.parse('$_apiUrl/api/nicknames/stats')),
      ]);
      if (!mounted) return;
      if (results[0].statusCode == 200) {
        final d = jsonDecode(results[0].body);
        setState(() {
          _totalAiGraded      = d['total_ai_graded'] ?? 0;
          _pendingGradeReview = d['pending_review']  ?? 0;
          _confirmedGrades    = d['confirmed']        ?? 0;
          _flaggedGrades      = d['flagged']           ?? 0;
        });
      }
      if (results[1].statusCode == 200) {
        final d = jsonDecode(results[1].body);
        setState(() { _nicknamePending = d['pending'] ?? 0; });
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _buildHeader(),
      _buildStatsBar(),
      _buildTabBar(),
      Expanded(
        child: TabBarView(controller: _tab, children: [
          _ImageQcQueueTab(onReviewed: _loadStats),
          _GradeReviewTab(onReviewed: _loadStats),
          _CommunityReviewTab(onVoted: _loadStats),
          _SubmitTab(onSubmitted: () { _loadStats(); _tab.animateTo(2); }),
          _ApprovedDictTab(),
        ]),
      ),
    ]);
  }

  Widget _buildHeader() => Padding(
    padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
    child: Row(children: [
      Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              colors: [Color(0xFF6366F1), Color(0xFFF63366)]),
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Icon(Icons.how_to_vote_outlined,
            color: Colors.white, size: 22),
      ),
      const SizedBox(width: 12),
      const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Human AI Trainer Review Board',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900,
                color: Color(0xFF0F172A))),
        Text('Help the AI grade coins accurately',
            style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
      ]),
    ]),
  );

  Widget _buildStatsBar() => Container(
    margin: const EdgeInsets.fromLTRB(24, 10, 24, 6),
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
    decoration: BoxDecoration(
      gradient: const LinearGradient(
          colors: [Color(0xFF0F172A), Color(0xFF1E293B)]),
      borderRadius: BorderRadius.circular(12),
    ),
    child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
      _sc('🖼️', '$_pendingImageQc',     'Image QC'),
      _vd(),
      _sc('🪙', '$_totalAiGraded',     'AI Graded'),
      _vd(),
      _sc('⏳', '$_pendingGradeReview', 'Awaiting'),
      _vd(),
      _sc('✅', '$_confirmedGrades',    'Confirmed'),
      _vd(),
      _sc('🚩', '$_flaggedGrades',      'Flagged'),
      _vd(),
      _sc('💡', '$_nicknamePending',    'Nicknames'),
    ]),
  );

  Widget _sc(String icon, String val, String lbl) => Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      Text('$icon $val', style: const TextStyle(
          color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12)),
      Text(lbl, style: const TextStyle(
          color: Color(0xFF94A3B8), fontSize: 10)),
    ],
  );

  Widget _vd() => Container(height: 26, width: 1, color: const Color(0xFF334155));

  Widget _buildTabBar() => Container(
    margin: const EdgeInsets.symmetric(horizontal: 24),
    decoration: const BoxDecoration(border: Border(
        bottom: BorderSide(color: Color(0xFFE2E6E9), width: 1))),
    child: TabBar(
      controller: _tab,
      labelColor: const Color(0xFFF63366),
      unselectedLabelColor: const Color(0xFF64748B),
      indicatorColor: const Color(0xFFF63366),
      indicatorWeight: 3,
      isScrollable: true,
      tabAlignment: TabAlignment.start,
      tabs: [
        Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.image_search_outlined, size: 16),
          const SizedBox(width: 6),
          const Text('Image QC'),
          if (_pendingImageQc > 0) ...[
            const SizedBox(width: 6),
            _badge(_pendingImageQc, const Color(0xFFF63366)),
          ],
        ])),
        Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.verified_outlined, size: 16),
          const SizedBox(width: 6),
          const Text('Grade Reviews'),
          if (_pendingGradeReview > 0) ...[
            const SizedBox(width: 6),
            _badge(_pendingGradeReview, const Color(0xFFEF4444)),
          ],
        ])),
        Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.rate_review_outlined, size: 16),
          const SizedBox(width: 6),
          const Text('Nickname Review'),
          if (_nicknamePending > 0) ...[
            const SizedBox(width: 6),
            _badge(_nicknamePending, const Color(0xFF6366F1)),
          ],
        ])),
        const Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.add_circle_outline, size: 16),
          SizedBox(width: 6), Text('Submit a Term'),
        ])),
        const Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.menu_book_outlined, size: 16),
          SizedBox(width: 6), Text('Dictionary'),
        ])),
      ],
    ),
  );

  Widget _badge(int count, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
    decoration: BoxDecoration(color: color, borderRadius: BorderRadius.circular(20)),
    child: Text('$count', style: const TextStyle(
        color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
  );
}

// ─── Tab 1: AI Grade Review ───────────────────────────────────────────────────

class _GradeReviewTab extends StatefulWidget {
  final VoidCallback onReviewed;
  const _GradeReviewTab({required this.onReviewed});
  @override
  State<_GradeReviewTab> createState() => _GradeReviewTabState();
}

class _GradeReviewTabState extends State<_GradeReviewTab>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  List<GradeReviewCoin> _items = [];
  bool _loading = true;
  String _error = '';
  final Set<String> _submitted = {};

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = ''; });
    try {
      final email = Uri.encodeComponent(AuthService.userEmail);
      final res = await http.get(Uri.parse(
          '$_apiUrl/api/grade_review/queue?user_email=$email&limit=30'));
      if (res.statusCode == 200 && mounted) {
        final data  = jsonDecode(res.body);
        final items = (data['results'] as List)
            .map((j) => GradeReviewCoin.fromJson(j)).toList();
        setState(() { _items = items; _loading = false; });
      } else {
        if (mounted) { setState(() { _loading = false; _error = 'Failed to load.'; }); }
      }
    } catch (e) {
      if (mounted) { setState(() { _loading = false; _error = e.toString(); }); }
    }
  }

  void _onSubmitted(String coinId) {
    setState(() => _submitted.add(coinId));
    widget.onReviewed();
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(
          color: Color(0xFF6366F1)));
    }
    if (_error.isNotEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 40),
        const SizedBox(height: 12),
        Text(_error, style: const TextStyle(color: Color(0xFF64748B))),
        const SizedBox(height: 16),
        ElevatedButton(onPressed: _load, child: const Text('Retry')),
      ]));
    }
    final pending = _items.where((c) => !_submitted.contains(c.coinId)).toList();
    if (pending.isEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.check_circle_outline,
            size: 64, color: Color(0xFF22C55E)),
        const SizedBox(height: 16),
        const Text('All caught up!', style: TextStyle(
            fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
        const SizedBox(height: 8),
        const Text(
          'All your AI-graded coins have been reviewed.\n'
          'Upload more coins or check back after the next import.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Color(0xFF64748B), height: 1.5)),
        const SizedBox(height: 20),
        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6366F1)),
          icon: const Icon(Icons.refresh, color: Colors.white),
          label: const Text('Refresh', style: TextStyle(color: Colors.white)),
          onPressed: _load,
        ),
      ]));
    }

    final lowConf = pending.where((c) => c.lowConfidence).toList();
    final normal  = pending.where((c) => !c.lowConfidence).toList();

    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF6366F1),
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (lowConf.isNotEmpty) ...[
            _secHeader('🔴 Low Confidence — Review Urgently', const Color(0xFFDC2626)),
            const SizedBox(height: 8),
            ...lowConf.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _GradeReviewCard(coin: c, onSubmitted: () => _onSubmitted(c.coinId)),
            )),
            const SizedBox(height: 8),
          ],
          if (normal.isNotEmpty) ...[
            if (lowConf.isNotEmpty) _secHeader('🟡 Review When Ready', const Color(0xFFF59E0B)),
            if (lowConf.isNotEmpty) const SizedBox(height: 8),
            ...normal.map((c) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _GradeReviewCard(coin: c, onSubmitted: () => _onSubmitted(c.coinId)),
            )),
          ],
        ],
      ),
    );
  }

  Widget _secHeader(String label, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
    decoration: BoxDecoration(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(8),
      border: Border.all(color: color.withValues(alpha: 0.3)),
    ),
    child: Text(label, style: TextStyle(
        color: color, fontWeight: FontWeight.bold, fontSize: 13)),
  );
}

// ─── Grade Review Card ────────────────────────────────────────────────────────

class _GradeReviewCard extends StatefulWidget {
  final GradeReviewCoin coin;
  final VoidCallback onSubmitted;
  const _GradeReviewCard({required this.coin, required this.onSubmitted});
  @override
  State<_GradeReviewCard> createState() => _GradeReviewCardState();
}

class _GradeReviewCardState extends State<_GradeReviewCard> {
  int    _rating         = 0;
  bool   _correcting     = false;
  String _suggestedGrade = 'MS-63';
  final  _notesCtrl      = TextEditingController();
  bool   _submitting     = false;
  bool   _done           = false;
  String _doneMsg        = '';
  bool   _flagged        = false;

  String get _userEmail => AuthService.userEmail;

  @override
  void dispose() { _notesCtrl.dispose(); super.dispose(); }

  Future<void> _submit(String action) async {
    if (_rating == 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Please rate the AI\'s accuracy first (1–5 stars).'),
        backgroundColor: Color(0xFFF59E0B),
      ));
      return;
    }
    setState(() => _submitting = true);
    try {
      final res = await http.post(
        Uri.parse('$_apiUrl/api/grade_review/submit'),
        body: {
          'user_email':      AuthService.userEmail,
          'coin_id':         widget.coin.coinId,
          'action':          action,
          'suggested_grade': action == 'corrected' ? _suggestedGrade : '',
          'rating':          _rating.toString(),
          'notes':           _notesCtrl.text.trim(),
        },
      );
      if (res.statusCode == 200 && mounted) {
        final data = jsonDecode(res.body);
        setState(() {
          _submitting = false;
          _done       = true;
          _doneMsg    = data['message'] ?? '✓ Reviewed.';
          _flagged    = data['flagged'] ?? false;
        });
        await Future.delayed(const Duration(milliseconds: 800));
        if (mounted) { widget.onSubmitted(); }
      }
    } catch (e) {
      if (mounted) {
        setState(() => _submitting = false);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Error: $e'),
          backgroundColor: const Color(0xFFDC2626),
        ));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_done) { return _buildDoneCard(); }

    final coin    = widget.coin;
    final confPct = (coin.confidenceScore * 100).round();
    final confColor = coin.lowConfidence
        ? const Color(0xFFDC2626)
        : confPct < 95 ? const Color(0xFFF59E0B) : const Color(0xFF16A34A);

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: coin.lowConfidence
              ? const Color(0xFFDC2626).withValues(alpha: 0.4)
              : const Color(0xFFE2E6E9)),
        boxShadow: [BoxShadow(
          color: Colors.black.withValues(alpha: 0.04),
          blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        // Confidence banner
        if (coin.lowConfidence)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
            decoration: const BoxDecoration(
              color: Color(0xFFFEF2F2),
              borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
            ),
            child: const Row(children: [
              Icon(Icons.warning_amber_rounded,
                  color: Color(0xFFDC2626), size: 16),
              SizedBox(width: 6),
              Text('Low Confidence — AI was less certain about this grade',
                  style: TextStyle(color: Color(0xFFDC2626),
                      fontSize: 12, fontWeight: FontWeight.w600)),
            ]),
          ),

        Padding(
          padding: const EdgeInsets.all(14),
          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            // Coin info row
            Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              // Coin image with interactive high-res pop-out trigger
              GestureDetector(
                onTap: () => _openLightbox(context, coin, _userEmail),
                child: Tooltip(
                  message: 'Tap to view full resolution high-res image & zoom',
                  child: Stack(
                    children: [
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: coin.source == 'Binder Scan' && coin.imageUrl.isNotEmpty
                            ? _CoinCropImage(
                                coinId: coin.coinId,
                                userEmail: _userEmail,
                                fallbackUrl: coin.imageUrl,
                                hasBbox: coin.hasBbox,
                                size: 76,
                              )
                            : coin.imageUrl.isNotEmpty
                                ? Image.network(coin.imageUrl, width: 76, height: 76,
                                    fit: BoxFit.cover,
                                    errorBuilder: (c, e, s) => _placeholder())
                                : _placeholder(),
                      ),
                      Positioned(
                        right: 4,
                        bottom: 4,
                        child: Container(
                          padding: const EdgeInsets.all(4),
                          decoration: BoxDecoration(
                            color: Colors.black.withValues(alpha: 0.65),
                            shape: BoxShape.circle,
                          ),
                          child: const Icon(Icons.zoom_in_rounded, color: Colors.white, size: 14),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(coin.displayName, style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15, color: Color(0xFF0F172A))),
                      ),
                      InkWell(
                        onTap: () => _openLightbox(context, coin, _userEmail),
                        borderRadius: BorderRadius.circular(6),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: const [
                              Icon(Icons.fullscreen, size: 16, color: Color(0xFF6366F1)),
                              SizedBox(width: 2),
                              Text('Pop-Out High-Res View', style: TextStyle(
                                  fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF6366F1))),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (coin.themeSubject.isNotEmpty)
                    Text(coin.themeSubject, style: const TextStyle(
                        fontSize: 12, color: Color(0xFF64748B))),
                  const SizedBox(height: 6),
                  Container(
                    padding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF6366F1).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(
                          color: const Color(0xFF6366F1).withValues(alpha: 0.3)),
                    ),
                    child: Row(mainAxisSize: MainAxisSize.min, children: [
                      const Icon(Icons.auto_awesome,
                          size: 12, color: Color(0xFF6366F1)),
                      const SizedBox(width: 4),
                      Text('AI Grade: ${coin.condition}',
                          style: const TextStyle(fontSize: 12,
                              fontWeight: FontWeight.w600,
                              color: Color(0xFF6366F1))),
                    ]),
                  ),
                  const SizedBox(height: 4),
                  Row(children: [
                    Icon(Icons.speed, size: 13, color: confColor),
                    const SizedBox(width: 4),
                    Text('Confidence: $confPct%', style: TextStyle(
                        fontSize: 12, color: confColor,
                        fontWeight: FontWeight.w500)),
                    const SizedBox(width: 6),
                    Text('· ${coin.source}', style: const TextStyle(
                        fontSize: 11, color: Color(0xFFADB5BD))),
                  ]),
                ]),
              ),
            ]),

            const Divider(height: 20, color: Color(0xFFF1F5F9)),

            // Star accuracy rating
            const Text('How accurate is the AI grade?',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600,
                    color: Color(0xFF334155))),
            const SizedBox(height: 8),
            Row(children: [
              ...[1, 2, 3, 4, 5].map((s) => GestureDetector(
                onTap: () => setState(() => _rating = s),
                child: Padding(
                  padding: const EdgeInsets.only(right: 4),
                  child: Icon(
                    s <= _rating ? Icons.star_rounded : Icons.star_border_rounded,
                    size: 30,
                    color: s <= _rating
                        ? const Color(0xFFFBBF24) : const Color(0xFFCBD5E1),
                  ),
                ),
              )),
              const SizedBox(width: 8),
              Text(
                _rating == 0 ? 'Tap to rate'
                    : _rating <= 2 ? 'Way off'
                    : _rating == 3 ? 'Close'
                    : _rating == 4 ? 'Pretty good'
                    : 'Spot on!',
                style: TextStyle(fontSize: 12,
                  color: _rating == 0
                      ? const Color(0xFFADB5BD)
                      : const Color(0xFF64748B)),
              ),
            ]),

            const SizedBox(height: 14),

            // Action buttons
            Row(children: [
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: Color(0xFF16A34A)),
                    foregroundColor: const Color(0xFF16A34A),
                  ),
                  icon: const Icon(Icons.check_circle_outline, size: 18),
                  label: const Text('Confirm Grade'),
                  onPressed: _submitting ? null : () => _submit('confirmed'),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: OutlinedButton.icon(
                  style: OutlinedButton.styleFrom(
                    side: BorderSide(
                        color: _correcting
                            ? const Color(0xFFF63366)
                            : const Color(0xFF6366F1)),
                    foregroundColor: _correcting
                        ? const Color(0xFFF63366) : const Color(0xFF6366F1),
                  ),
                  icon: Icon(_correcting ? Icons.expand_less : Icons.edit_outlined,
                      size: 18),
                  label: Text(_correcting ? 'Cancel' : 'Suggest Grade'),
                  onPressed: () => setState(() => _correcting = !_correcting),
                ),
              ),
            ]),

            // Correction panel
            if (_correcting) ...[
              const SizedBox(height: 12),
              const Text('Select the correct grade:', style: TextStyle(
                  fontSize: 13, fontWeight: FontWeight.w600,
                  color: Color(0xFF334155))),
              const SizedBox(height: 6),
              DropdownButtonFormField<String>(
                initialValue: _suggestedGrade,
                decoration: _dec(null),
                items: _anaGrades.map((g) => DropdownMenuItem(
                    value: g, child: Text(g, style: const TextStyle(fontSize: 13)))).toList(),
                onChanged: (v) => setState(() => _suggestedGrade = v ?? 'MS-63'),
              ),
              const SizedBox(height: 10),
              TextField(
                controller: _notesCtrl, maxLines: 2,
                decoration: _dec('Optional: explain your reasoning…'),
              ),
              const SizedBox(height: 10),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF63366),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 13),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                  ),
                  icon: _submitting
                      ? const SizedBox(width: 18, height: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.send_rounded, size: 18),
                  label: Text(_submitting
                      ? 'Submitting…'
                      : 'Submit Correction: $_suggestedGrade',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                  onPressed: _submitting ? null : () => _submit('corrected'),
                ),
              ),
            ],
          ]),
        ),
      ]),
    );
  }

  Widget _buildDoneCard() => Container(
    padding: const EdgeInsets.all(16),
    decoration: BoxDecoration(
      color: _flagged ? const Color(0xFFFFF7ED) : const Color(0xFFF0FDF4),
      borderRadius: BorderRadius.circular(14),
      border: Border.all(color: _flagged
          ? const Color(0xFFFED7AA) : const Color(0xFFBBF7D0)),
    ),
    child: Row(children: [
      Icon(_flagged ? Icons.flag_rounded : Icons.check_circle_rounded,
          color: _flagged ? const Color(0xFFF97316) : const Color(0xFF16A34A),
          size: 28),
      const SizedBox(width: 12),
      Expanded(child: Text(_doneMsg, style: TextStyle(
          fontSize: 13, height: 1.4,
          color: _flagged ? const Color(0xFF92400E) : const Color(0xFF15803D)))),
    ]),
  );

  Widget _placeholder() => Container(
    width: 72, height: 72,
    decoration: BoxDecoration(
      color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(8)),
    child: const Icon(Icons.monetization_on_outlined,
        size: 36, color: Color(0xFFCBD5E1)),
  );

  InputDecoration _dec(String? hint) => InputDecoration(
    hintText: hint,
    hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 13),
    contentPadding: const EdgeInsets.all(12),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFFF63366), width: 2)),
  );
}

// ─── Coin Crop Image Widget ───────────────────────────────────────────────────
/// For Binder Scan coins: calls /api/coin_crop and shows the cropped slot.
/// Falls back gracefully to full binder page image for old coins without bbox.

class _CoinCropImage extends StatefulWidget {
  final String coinId, userEmail, fallbackUrl;
  final bool hasBbox;
  final double size;

  const _CoinCropImage({
    required this.coinId, required this.userEmail,
    required this.fallbackUrl, required this.hasBbox,
    this.size = 72,
  });

  @override
  State<_CoinCropImage> createState() => _CoinCropImageState();
}

class _CoinCropImageState extends State<_CoinCropImage> {
  static const _api =
      kApiBaseUrl;

  _CropState _state = _CropState.loading;
  Uint8List?  _cropBytes;

  @override
  void initState() {
    super.initState();
    if (widget.hasBbox) {
      _fetchCrop();
    } else {
      // No bbox in Firestore — show full binder page immediately
      setState(() => _state = _CropState.fallback);
    }
  }

  Future<void> _fetchCrop() async {
    try {
      final uri = Uri.parse(
          '$_api/api/coin_crop'
          '?coin_id=${Uri.encodeComponent(widget.coinId)}'
          '&user_email=${Uri.encodeComponent(widget.userEmail)}');
      final res = await http.get(uri).timeout(const Duration(seconds: 15));
      if (!mounted) { return; }
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body);
        if (data['status'] == 'ok' && data['crop_b64'] != null) {
          final bytes = base64Decode(data['crop_b64'] as String);
          setState(() { _cropBytes = bytes; _state = _CropState.cropped; });
        } else {
          // status == 'fallback'
          setState(() => _state = _CropState.fallback);
        }
      } else {
        setState(() => _state = _CropState.fallback);
      }
    } catch (_) {
      if (mounted) { setState(() => _state = _CropState.fallback); }
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = widget.size;
    switch (_state) {
      case _CropState.loading:
        return Container(
          width: s, height: s,
          decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(8)),
          child: const Center(child: SizedBox(
              width: 20, height: 20,
              child: CircularProgressIndicator(strokeWidth: 2,
                  color: Color(0xFF6366F1)))),
        );

      case _CropState.cropped:
        return Image.memory(
          _cropBytes!,
          width: s, height: s, fit: BoxFit.cover,
          errorBuilder: (c, e, _) => _fallbackWidget(s),
        );

      case _CropState.fallback:
        return widget.fallbackUrl.isNotEmpty
            ? Image.network(
                widget.fallbackUrl, width: s, height: s,
                fit: BoxFit.cover,
                errorBuilder: (c, e, _) => _fallbackWidget(s),
              )
            : _fallbackWidget(s);
    }
  }

  Widget _fallbackWidget(double s) => Container(
    width: s, height: s,
    decoration: BoxDecoration(
        color: const Color(0xFFF1F5F9),
        borderRadius: BorderRadius.circular(8)),
    child: const Icon(Icons.monetization_on_outlined,
        size: 36, color: Color(0xFFCBD5E1)),
  );
}

enum _CropState { loading, cropped, fallback }

// ─── High-Resolution Pop-Out Image Lightbox ─────────────────────────────────

void _openLightbox(BuildContext context, GradeReviewCoin coin, String userEmail) {
  showDialog(
    context: context,
    barrierColor: Colors.black.withValues(alpha: 0.85),
    builder: (ctx) => _CoinImageLightboxDialog(coin: coin, userEmail: userEmail),
  );
}

class _CoinImageLightboxDialog extends StatefulWidget {
  final GradeReviewCoin coin;
  final String userEmail;

  const _CoinImageLightboxDialog({
    required this.coin,
    required this.userEmail,
  });

  @override
  State<_CoinImageLightboxDialog> createState() => _CoinImageLightboxDialogState();
}

class _CoinImageLightboxDialogState extends State<_CoinImageLightboxDialog> {
  late final TransformationController _transCtrl;
  String _activeSide = 'obverse';
  bool _showFullBinder = false;

  @override
  void initState() {
    super.initState();
    _transCtrl = TransformationController();
  }

  @override
  void dispose() {
    _transCtrl.dispose();
    super.dispose();
  }

  void _resetZoom() {
    _transCtrl.value = Matrix4.identity();
  }

  @override
  Widget build(BuildContext context) {
    final coin = widget.coin;
    final hasReverse = coin.imageUrlReverse.isNotEmpty;
    final isMicroscope = coin.source.toLowerCase().contains('microscope') ||
        coin.scanSource.toLowerCase().contains('microscope');
    final isBinder = coin.source == 'Binder Scan';

    String currentUrl = _activeSide == 'obverse'
        ? (coin.imageUrlObverse.isNotEmpty ? coin.imageUrlObverse : coin.imageUrl)
        : coin.imageUrlReverse;

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 900),
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: const Color(0xFF334155)),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.5),
              blurRadius: 24,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Header bar
            Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Flexible(
                              child: Text(
                                coin.displayName,
                                style: const TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                                overflow: TextOverflow.ellipsis,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: const Color(0xFF6366F1).withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: const Color(0xFF6366F1)),
                              ),
                              child: Text(
                                'AI Grade: ${coin.condition}',
                                style: const TextStyle(
                                  color: Color(0xFF818CF8),
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                              decoration: BoxDecoration(
                                color: isMicroscope
                                    ? const Color(0xFF059669).withValues(alpha: 0.25)
                                    : const Color(0xFF3B82F6).withValues(alpha: 0.25),
                                borderRadius: BorderRadius.circular(6),
                                border: Border.all(
                                  color: isMicroscope
                                      ? const Color(0xFF059669)
                                      : const Color(0xFF3B82F6),
                                ),
                              ),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(
                                    isMicroscope
                                        ? Icons.science_outlined
                                        : isBinder
                                            ? Icons.folder_open
                                            : Icons.camera_alt_outlined,
                                    size: 13,
                                    color: isMicroscope
                                        ? const Color(0xFF34D399)
                                        : const Color(0xFF60A5FA),
                                  ),
                                  const SizedBox(width: 4),
                                  Text(
                                    isMicroscope
                                        ? '🔬 Digital Microscope Scan (High Resolution)'
                                        : isBinder
                                            ? '📁 Binder Page Scan'
                                            : '📸 High-Res Photo (${coin.source})',
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: FontWeight.w600,
                                      color: isMicroscope
                                          ? const Color(0xFF34D399)
                                          : const Color(0xFF60A5FA),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Color(0xFF94A3B8)),
                    onPressed: () => Navigator.of(context).pop(),
                    tooltip: 'Close',
                  ),
                ],
              ),
            ),

            const Divider(height: 1, color: Color(0xFF1E293B)),

            // View Controls / Side Toggle
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              color: const Color(0xFF1E293B),
              child: Row(
                children: [
                  if (hasReverse) ...[
                    SegmentedButton<String>(
                      segments: const [
                        ButtonSegment(value: 'obverse', label: Text('Obverse (Front)')),
                        ButtonSegment(value: 'reverse', label: Text('Reverse (Back)')),
                      ],
                      selected: {_activeSide},
                      onSelectionChanged: (set) {
                        setState(() {
                          _activeSide = set.first;
                          _resetZoom();
                        });
                      },
                      style: SegmentedButton.styleFrom(
                        visualDensity: VisualDensity.compact,
                        selectedBackgroundColor: const Color(0xFF6366F1),
                        selectedForegroundColor: Colors.white,
                        foregroundColor: const Color(0xFF94A3B8),
                        backgroundColor: const Color(0xFF0F172A),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],

                  if (isBinder && coin.hasBbox) ...[
                    FilterChip(
                      label: Text(_showFullBinder ? 'Full Binder Page' : 'Cropped Slot'),
                      selected: _showFullBinder,
                      onSelected: (val) {
                        setState(() {
                          _showFullBinder = val;
                          _resetZoom();
                        });
                      },
                      selectedColor: const Color(0xFF6366F1),
                      labelStyle: TextStyle(
                        color: _showFullBinder ? Colors.white : const Color(0xFF94A3B8),
                        fontSize: 12,
                      ),
                      avatar: Icon(
                        _showFullBinder ? Icons.description_outlined : Icons.crop_outlined,
                        size: 14,
                        color: _showFullBinder ? Colors.white : const Color(0xFF94A3B8),
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],

                  const Spacer(),

                  OutlinedButton.icon(
                    onPressed: _resetZoom,
                    style: OutlinedButton.styleFrom(
                      foregroundColor: const Color(0xFF94A3B8),
                      side: const BorderSide(color: Color(0xFF475569)),
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    ),
                    icon: const Icon(Icons.restart_alt, size: 16),
                    label: const Text('Reset Zoom', style: TextStyle(fontSize: 12)),
                  ),
                ],
              ),
            ),

            // High-Resolution Interactive Image View Canvas
            Container(
              height: 480,
              width: double.infinity,
              color: Colors.black,
              child: ClipRect(
                child: InteractiveViewer(
                  transformationController: _transCtrl,
                  minScale: 0.5,
                  maxScale: 10.0,
                  child: Center(
                    child: (isBinder && !_showFullBinder && currentUrl.isNotEmpty)
                        ? _CoinCropImage(
                            coinId: coin.coinId,
                            userEmail: widget.userEmail,
                            fallbackUrl: currentUrl,
                            hasBbox: coin.hasBbox,
                            size: 400,
                          )
                        : currentUrl.isNotEmpty
                            ? Image.network(
                                currentUrl,
                                fit: BoxFit.contain,
                                errorBuilder: (ctx, err, stack) => const Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.broken_image_outlined, color: Colors.white38, size: 48),
                                    SizedBox(height: 8),
                                    Text('Failed to load high resolution photo', style: TextStyle(color: Colors.white54)),
                                  ],
                                ),
                              )
                            : const Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(Icons.monetization_on_outlined, color: Colors.white38, size: 48),
                                  SizedBox(height: 8),
                                  Text('No high resolution photo available', style: TextStyle(color: Colors.white54)),
                                ],
                              ),
                  ),
                ),
              ),
            ),

            // Footer hint bar
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: const BoxDecoration(
                color: Color(0xFF0F172A),
                borderRadius: BorderRadius.vertical(bottom: Radius.circular(16)),
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.zoom_in, size: 14, color: Color(0xFF94A3B8)),
                  SizedBox(width: 6),
                  Text(
                    'Pinch or scroll to zoom up to 10x high-res details · Drag to pan around coin',
                    style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}



// ─── Tab 2: Community Nickname Review ────────────────────────────────────────

class _CommunityReviewTab extends StatefulWidget {
  final VoidCallback onVoted;
  const _CommunityReviewTab({required this.onVoted});
  @override
  State<_CommunityReviewTab> createState() => _CommunityReviewTabState();
}

class _CommunityReviewTabState extends State<_CommunityReviewTab>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  List<NicknameSuggestion> _items = [];
  bool _loading = true;
  String _error = '';
  final Map<String, int> _pendingVotes = {};

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() { _loading = true; _error = ''; });
    try {
      final res = await http.get(Uri.parse(
          '$_apiUrl/api/nicknames?status=pending&limit=50'));
      if (res.statusCode == 200) {
        final data  = jsonDecode(res.body);
        final items = (data['results'] as List)
            .map((j) => NicknameSuggestion.fromJson(j)).toList();
        if (mounted) { setState(() { _items = items; _loading = false; }); }
      } else {
        if (mounted) { setState(() { _loading = false; _error = 'Failed to load.'; }); }
      }
    } catch (e) {
      if (mounted) { setState(() { _loading = false; _error = e.toString(); }); }
    }
  }

  Future<void> _vote(NicknameSuggestion item, int rating) async {
    if (item.isBuiltin) return;
    final myEmail = AuthService.userEmail;
    if (item.submittedBy == myEmail) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text("You can't vote on your own submission."),
        backgroundColor: Color(0xFFDC2626),
      ));
      return;
    }
    setState(() => _pendingVotes[item.id] = rating);
    try {
      final res = await http.post(
        Uri.parse('$_apiUrl/api/nicknames/${item.id}/vote'),
        body: {'user_email': myEmail, 'rating': rating.toString()},
      );
      if (res.statusCode == 200 && mounted) {
        final data      = jsonDecode(res.body);
        final msg       = data['message'] ?? 'Vote recorded.';
        final newStatus = data['new_status'] ?? 'pending';
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(msg),
          backgroundColor: newStatus == 'approved'
              ? const Color(0xFF16A34A) : const Color(0xFF6366F1),
          duration: const Duration(seconds: 3),
        ));
        widget.onVoted();
        await Future.delayed(const Duration(milliseconds: 600));
        _load();
      }
    } catch (e) {
      setState(() => _pendingVotes.remove(item.id));
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(
          color: Color(0xFF6366F1)));
    }
    if (_error.isNotEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.error_outline, color: Color(0xFFDC2626), size: 40),
        const SizedBox(height: 12),
        Text(_error, style: const TextStyle(color: Color(0xFF64748B))),
        const SizedBox(height: 16),
        ElevatedButton(onPressed: _load, child: const Text('Retry')),
      ]));
    }
    if (_items.isEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        const Icon(Icons.check_circle_outline, size: 64, color: Color(0xFF22C55E)),
        const SizedBox(height: 16),
        const Text('All caught up!', style: TextStyle(
            fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF0F172A))),
        const SizedBox(height: 8),
        const Text('No pending nickname submissions right now.',
            textAlign: TextAlign.center,
            style: TextStyle(color: Color(0xFF64748B), height: 1.5)),
        const SizedBox(height: 20),
        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF6366F1)),
          icon: const Icon(Icons.refresh, color: Colors.white),
          label: const Text('Refresh', style: TextStyle(color: Colors.white)),
          onPressed: _load,
        ),
      ]));
    }
    return RefreshIndicator(
      onRefresh: _load,
      color: const Color(0xFF6366F1),
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: _items.length,
        separatorBuilder: (_, idx) => const SizedBox(height: 12),
        itemBuilder: (_, i) => _NicknameCard(
          item: _items[i],
          pendingRating: _pendingVotes[_items[i].id],
          onVote: (r) => _vote(_items[i], r),
        ),
      ),
    );
  }
}

// ─── Nickname Card ────────────────────────────────────────────────────────────

class _NicknameCard extends StatelessWidget {
  final NicknameSuggestion item;
  final int? pendingRating;
  final void Function(int) onVote;
  const _NicknameCard({required this.item, required this.pendingRating, required this.onVote});

  @override
  Widget build(BuildContext context) {
    final isMine        = item.submittedBy == AuthService.userEmail;
    final displayRating = pendingRating ?? item.yourRating;
    return Container(
      decoration: BoxDecoration(
        color: Colors.white, borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E6E9)),
        boxShadow: [BoxShadow(
          color: Colors.black.withValues(alpha: 0.04),
          blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Expanded(child: RichText(text: TextSpan(
              style: const TextStyle(fontSize: 16, color: Color(0xFF0F172A)),
              children: [
                TextSpan(text: '"${item.nickname}"',
                    style: const TextStyle(fontWeight: FontWeight.bold,
                        color: Color(0xFF6366F1), fontStyle: FontStyle.italic)),
                const TextSpan(text: '  →  '),
                TextSpan(text: item.mapsTo,
                    style: const TextStyle(fontWeight: FontWeight.w600)),
              ],
            ))),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(color: const Color(0xFFF1F5F9),
                  borderRadius: BorderRadius.circular(20)),
              child: Text(item.category, style: const TextStyle(
                  fontSize: 11, color: Color(0xFF64748B))),
            ),
          ]),
          if (item.example.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text('"${item.example}"', style: const TextStyle(
                fontSize: 13, color: Color(0xFF64748B),
                fontStyle: FontStyle.italic)),
          ],
          const SizedBox(height: 12),
          Row(children: [
            CircleAvatar(radius: 14,
              backgroundColor: const Color(0xFF6366F1).withValues(alpha: 0.15),
              child: Text(
                item.submittedBy.isNotEmpty
                    ? item.submittedBy[0].toUpperCase() : '?',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold,
                    color: Color(0xFF6366F1))),
            ),
            const SizedBox(width: 6),
            Text(isMine ? 'You submitted this' : item.submittedBy.split('@').first,
                style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
            const Spacer(),
            if (item.voteCount > 0) ...[
              Text('${item.avgRating.toStringAsFixed(1)} ⭐ · ${item.voteCount} vote${item.voteCount == 1 ? "" : "s"}',
                  style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
              const SizedBox(width: 10),
            ],
            if (isMine)
              const Tooltip(message: "You can't vote on your own submission",
                child: Icon(Icons.block, size: 18, color: Color(0xFFCBD5E1)))
            else
              _StarWidget(current: displayRating, enabled: pendingRating == null, onRate: onVote),
          ]),
        ]),
      ),
    );
  }
}

// ─── Star Widget ──────────────────────────────────────────────────────────────

class _StarWidget extends StatefulWidget {
  final int? current;
  final bool enabled;
  final void Function(int) onRate;
  const _StarWidget({required this.current, required this.enabled, required this.onRate});
  @override
  State<_StarWidget> createState() => _StarWidgetState();
}

class _StarWidgetState extends State<_StarWidget> {
  int _hover = 0;
  @override
  Widget build(BuildContext context) {
    final active = _hover > 0 ? _hover : (widget.current ?? 0);
    return Row(mainAxisSize: MainAxisSize.min,
      children: List.generate(5, (i) {
        final star = i + 1;
        final filled = star <= active;
        return GestureDetector(
          onTap: widget.enabled ? () => widget.onRate(star) : null,
          child: MouseRegion(
            onEnter: widget.enabled ? (_) => setState(() => _hover = star) : null,
            onExit:  widget.enabled ? (_) => setState(() => _hover = 0) : null,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 120),
              padding: const EdgeInsets.symmetric(horizontal: 2),
              child: Icon(
                filled ? Icons.star_rounded : Icons.star_border_rounded,
                size: 26,
                color: filled ? const Color(0xFFFBBF24) : const Color(0xFFCBD5E1)),
            ),
          ),
        );
      }),
    );
  }
}

// ─── Tab 3: Submit a Term ─────────────────────────────────────────────────────

class _SubmitTab extends StatefulWidget {
  final VoidCallback onSubmitted;
  const _SubmitTab({required this.onSubmitted});
  @override
  State<_SubmitTab> createState() => _SubmitTabState();
}

class _SubmitTabState extends State<_SubmitTab> {
  final _nicknameCtrl = TextEditingController();
  final _mapsToCtrl   = TextEditingController();
  final _exampleCtrl  = TextEditingController();
  final _notesCtrl    = TextEditingController();
  String _category    = 'Other';
  bool   _submitting  = false;
  String _feedback    = '';
  bool   _isSuccess   = false;

  static const _cats = [
    'Cent','Nickel','Dime','Quarter','Half Dollar','Dollar','Gold','Silver','Other'];

  @override
  void dispose() {
    _nicknameCtrl.dispose(); _mapsToCtrl.dispose();
    _exampleCtrl.dispose(); _notesCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final nickname = _nicknameCtrl.text.trim();
    final mapsTo   = _mapsToCtrl.text.trim();
    if (nickname.isEmpty || mapsTo.isEmpty) {
      setState(() { _feedback = 'Fill in both Nickname and Official Name.'; _isSuccess = false; });
      return;
    }
    setState(() { _submitting = true; _feedback = ''; });
    try {
      final res = await http.post(Uri.parse('$_apiUrl/api/nicknames/submit'), body: {
        'user_email': AuthService.userEmail,
        'nickname': nickname, 'maps_to': mapsTo, 'category': _category,
        'example': _exampleCtrl.text.trim(), 'notes': _notesCtrl.text.trim(),
      });
      if (res.statusCode == 200 && mounted) {
        final data   = jsonDecode(res.body);
        final status = data['status'] ?? 'error';
        setState(() {
          _submitting = false;
          _feedback   = data['message'] ?? '';
          _isSuccess  = status == 'submitted';
        });
        if (status == 'submitted') {
          _nicknameCtrl.clear(); _mapsToCtrl.clear();
          _exampleCtrl.clear(); _notesCtrl.clear();
          widget.onSubmitted();
        }
      }
    } catch (e) {
      if (mounted) { setState(() { _submitting = false; _feedback = 'Network error: $e'; _isSuccess = false; }); }
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Center(child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 560),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: const LinearGradient(colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)]),
              borderRadius: BorderRadius.circular(14),
            ),
            child: const Row(children: [
              Icon(Icons.lightbulb_outline, color: Colors.white, size: 24),
              SizedBox(width: 12),
              Expanded(child: Text(
                'Know a coin nickname the AI should learn? '
                'Submit it — community votes approve it and it goes live within minutes!',
                style: TextStyle(color: Colors.white, fontSize: 13, height: 1.4))),
            ]),
          ),
          const SizedBox(height: 24),
          _lbl('Nickname / Slang *'), const SizedBox(height: 6),
          _tf(_nicknameCtrl, 'e.g.  Ike,  Merc,  Walker,  Wheatie'),
          const SizedBox(height: 16),
          _lbl('Official Coin Name *'), const SizedBox(height: 6),
          _tf(_mapsToCtrl, 'e.g.  Eisenhower Dollar,  Mercury Dime'),
          const SizedBox(height: 16),
          _lbl('Category'), const SizedBox(height: 6),
          DropdownButtonFormField<String>(
            initialValue: _category, decoration: _dec(null),
            items: _cats.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
            onChanged: (v) => setState(() => _category = v ?? 'Other'),
          ),
          const SizedBox(height: 16),
          _lbl('Example Usage (optional)'), const SizedBox(height: 6),
          _tf(_exampleCtrl, '"I have an Ike from 1972"'),
          const SizedBox(height: 16),
          _lbl('Notes (optional)'), const SizedBox(height: 6),
          _tf(_notesCtrl, 'Regional usage, era, origin…', maxLines: 2),
          const SizedBox(height: 24),
          if (_feedback.isNotEmpty)
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              padding: const EdgeInsets.all(14), margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: _isSuccess ? const Color(0xFFF0FDF4) : const Color(0xFFFFF7ED),
                border: Border.all(color: _isSuccess
                    ? const Color(0xFFBBF7D0) : const Color(0xFFFED7AA)),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(children: [
                Icon(_isSuccess ? Icons.check_circle_outline : Icons.info_outline,
                    color: _isSuccess ? const Color(0xFF16A34A) : const Color(0xFFF97316),
                    size: 20),
                const SizedBox(width: 10),
                Expanded(child: Text(_feedback, style: TextStyle(
                    fontSize: 13, height: 1.4,
                    color: _isSuccess ? const Color(0xFF15803D) : const Color(0xFF92400E)))),
              ]),
            ),
          SizedBox(width: double.infinity,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF6366F1), foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
              ),
              icon: _submitting
                  ? const SizedBox(width: 18, height: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.send_rounded, size: 20),
              label: Text(_submitting ? 'Submitting…' : 'Submit for Community Review',
                  style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
              onPressed: _submitting ? null : _submit,
            ),
          ),
          const SizedBox(height: 12),
          const Center(child: Text(
            'Auto-approved when avg ≥ 4 ⭐ with 3+ votes · Goes live within 60 s',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)))),
        ]),
      )),
    );
  }

  Widget _lbl(String t) => Text(t, style: const TextStyle(
      fontWeight: FontWeight.w600, fontSize: 13, color: Color(0xFF334155)));

  InputDecoration _dec(String? hint) => InputDecoration(
    hintText: hint,
    hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 13),
    border: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0xFF6366F1), width: 2)),
    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 13),
  );

  Widget _tf(TextEditingController ctrl, String? hint, {int maxLines = 1}) =>
      TextField(controller: ctrl, maxLines: maxLines, decoration: _dec(hint));
}

// ─── Tab 4: Approved Dictionary ───────────────────────────────────────────────

class _ApprovedDictTab extends StatefulWidget {
  @override
  State<_ApprovedDictTab> createState() => _ApprovedDictTabState();
}

class _ApprovedDictTabState extends State<_ApprovedDictTab>
    with AutomaticKeepAliveClientMixin {
  @override
  bool get wantKeepAlive => true;

  List<NicknameSuggestion> _all = [], _filtered = [];
  bool _loading = true;
  String _search = '', _catFilter = 'All';
  static const _cats = ['All','Built-In','Cent','Nickel','Dime','Quarter',
      'Half Dollar','Dollar','Gold','Silver','Other'];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final res = await http.get(Uri.parse(
          '$_apiUrl/api/nicknames?status=approved&limit=100'));
      if (res.statusCode == 200 && mounted) {
        final data  = jsonDecode(res.body);
        final items = (data['results'] as List)
            .map((j) => NicknameSuggestion.fromJson(j)).toList();
        setState(() { _all = items; _loading = false; });
        _applyFilters();
      }
    } catch (e) {
      if (mounted) { setState(() => _loading = false); }
    }
  }

  void _applyFilters() {
    setState(() {
      _filtered = _all.where((item) {
        final ms = _search.isEmpty ||
            item.nickname.toLowerCase().contains(_search.toLowerCase()) ||
            item.mapsTo.toLowerCase().contains(_search.toLowerCase());
        final mc = _catFilter == 'All' || item.category == _catFilter ||
            (_catFilter == 'Built-In' && item.isBuiltin);
        return ms && mc;
      }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    if (_loading) {
      return const Center(child: CircularProgressIndicator(
          color: Color(0xFF6366F1)));
    }
    return Column(children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
        child: Row(children: [
          Expanded(child: TextField(
            decoration: InputDecoration(
              hintText: 'Search nicknames…',
              prefixIcon: const Icon(Icons.search, color: Color(0xFF94A3B8), size: 20),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
                  borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(10),
                  borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
              contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
            ),
            onChanged: (v) { _search = v; _applyFilters(); },
          )),
          const SizedBox(width: 10),
          DropdownButton<String>(
            value: _catFilter, underline: const SizedBox(),
            items: _cats.map((c) => DropdownMenuItem(value: c,
                child: Text(c, style: const TextStyle(fontSize: 13)))).toList(),
            onChanged: (v) { _catFilter = v ?? 'All'; _applyFilters(); },
          ),
        ]),
      ),
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        child: Row(children: [
          Text('${_filtered.length} terms',
              style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
        ]),
      ),
      Expanded(child: GridView.builder(
        padding: const EdgeInsets.all(16),
        gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
          maxCrossAxisExtent: 280, mainAxisExtent: 110,
          crossAxisSpacing: 10, mainAxisSpacing: 10),
        itemCount: _filtered.length,
        itemBuilder: (_, i) => _DictCard(item: _filtered[i]),
      )),
    ]);
  }
}

class _DictCard extends StatelessWidget {
  final NicknameSuggestion item;
  const _DictCard({required this.item});
  @override
  Widget build(BuildContext context) {
    final b = item.isBuiltin;
    return Container(
      decoration: BoxDecoration(
        color: b ? const Color(0xFFF8FAFC) : const Color(0xFFF0FDF4),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: b
            ? const Color(0xFFE2E6E9) : const Color(0xFFBBF7D0)),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          Text(b ? '🔒' : '🏆', style: const TextStyle(fontSize: 14)),
          const SizedBox(width: 6),
          Expanded(child: Text('"${item.nickname}"', style: const TextStyle(
              fontWeight: FontWeight.bold, color: Color(0xFF6366F1),
              fontSize: 15, fontStyle: FontStyle.italic),
              overflow: TextOverflow.ellipsis)),
        ]),
        const SizedBox(height: 4),
        Text(item.mapsTo, style: const TextStyle(
            fontWeight: FontWeight.w600, color: Color(0xFF0F172A), fontSize: 13),
            overflow: TextOverflow.ellipsis),
        const Spacer(),
        Row(children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: b ? const Color(0xFFE2E8F0) : const Color(0xFFDCFCE7),
              borderRadius: BorderRadius.circular(20)),
            child: Text(item.category, style: TextStyle(fontSize: 10,
                color: b ? const Color(0xFF64748B) : const Color(0xFF16A34A))),
          ),
          const Spacer(),
          if (!b && item.voteCount > 0)
            Text('${item.avgRating.toStringAsFixed(1)}⭐',
                style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
        ]),
      ]),
    );
  }
}

// ─── Image QC Queue Tab ───────────────────────────────────────────────────────

class _ImageQcQueueTab extends StatefulWidget {
  final VoidCallback onReviewed;
  const _ImageQcQueueTab({required this.onReviewed});

  @override
  State<_ImageQcQueueTab> createState() => _ImageQcQueueTabState();
}

class _ImageQcQueueTabState extends State<_ImageQcQueueTab> {
  bool _loading = true;
  List<CoinModel> _coins = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    if (!mounted) return;
    setState(() => _loading = true);
    try {
      final email = AuthService.userEmail;
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .where('image_verification_status', whereIn: ['unverified', 'flagged'])
          .get();
      final list = snap.docs.map((doc) => CoinModel.fromFirestore(doc)).toList();
      if (mounted) {
        setState(() {
          _coins = list;
          _loading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _loading = false);
      }
    }
  }

  Future<void> _approve(CoinModel coin) async {
    await FirebaseFirestore.instance
        .doc('${AuthService.coinsPath}/${coin.id}')
        .update({'image_verification_status': 'human_verified'});
    _load();
    widget.onReviewed();
  }

  Future<void> _purgeAndReSource(CoinModel coin) async {
    await FirebaseFirestore.instance
        .doc('${AuthService.coinsPath}/${coin.id}')
        .update({
      'image_url_obverse': '',
      'image_url_reverse': '',
      'image_verification_status': 'unverified',
      'image_verification_reason': 'Purged for rescan/re-sourcing by trainer.',
    });
    _load();
    widget.onReviewed();
  }

  void _editMetadata(CoinModel coin) {
    final yearCtrl = TextEditingController(text: coin.year);
    final mintCtrl = TextEditingController(text: coin.mintMark);
    final varCtrl = TextEditingController(text: coin.variety);
    final denomCtrl = TextEditingController(text: coin.denomination);

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit Metadata'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: yearCtrl, decoration: const InputDecoration(labelText: 'Year')),
            TextField(controller: mintCtrl, decoration: const InputDecoration(labelText: 'Mint Mark')),
            TextField(controller: denomCtrl, decoration: const InputDecoration(labelText: 'Denomination')),
            TextField(controller: varCtrl, decoration: const InputDecoration(labelText: 'Variety')),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              await FirebaseFirestore.instance
                  .doc('${AuthService.coinsPath}/${coin.id}')
                  .update({
                'Year': yearCtrl.text.trim(),
                'Mint Mark': mintCtrl.text.trim(),
                'Denomination': denomCtrl.text.trim(),
                'Variety': varCtrl.text.trim(),
              });
              if (ctx.mounted) Navigator.pop(ctx);
              _load();
              widget.onReviewed();
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(child: CircularProgressIndicator(color: Color(0xFF6366F1)));
    }
    if (_coins.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: const [
            Icon(Icons.check_circle_outline, size: 64, color: Color(0xFF22C55E)),
            SizedBox(height: 16),
            Text('No images to verify!', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('All coin images are verified or checked.', style: TextStyle(color: Colors.grey)),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _load,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: _coins.length,
        itemBuilder: (context, index) {
          final coin = _coins[index];
          final reason = coin.imageVerificationReason;
          final isFlagged = coin.imageVerificationStatus == 'flagged';

          return Card(
            margin: const EdgeInsets.only(bottom: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(
                color: isFlagged ? const Color(0xFFEF4444) : const Color(0xFFE2E6E9),
                width: isFlagged ? 1.5 : 1,
              ),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${coin.year} ${coin.mintMark} ${coin.denomination}',
                        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: isFlagged ? const Color(0xFFFEE2E2) : const Color(0xFFF1F5F9),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          coin.imageVerificationStatus.toUpperCase(),
                          style: TextStyle(
                            color: isFlagged ? const Color(0xFFEF4444) : const Color(0xFF64748B),
                            fontSize: 10,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ],
                  ),
                  if (coin.variety.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text('Variety: ${coin.variety}', style: const TextStyle(color: Colors.grey, fontSize: 13)),
                  ],
                  if (reason.isNotEmpty) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFFBEB),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFFDE68A)),
                      ),
                      child: Text(
                        'Reason: $reason',
                        style: const TextStyle(color: Color(0xFFB45309), fontSize: 12),
                      ),
                    ),
                  ],
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      if (coin.imageUrlObverse.isNotEmpty)
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(coin.imageUrlObverse, height: 120, fit: BoxFit.cover),
                          ),
                        ),
                      if (coin.imageUrlObverse.isNotEmpty && coin.imageUrlReverse.isNotEmpty)
                        const SizedBox(width: 8),
                      if (coin.imageUrlReverse.isNotEmpty)
                        Expanded(
                          child: ClipRRect(
                            borderRadius: BorderRadius.circular(8),
                            child: Image.network(coin.imageUrlReverse, height: 120, fit: BoxFit.cover),
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      OutlinedButton(
                        onPressed: () => _editMetadata(coin),
                        child: const Text('Edit Metadata'),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFFEF4444),
                          side: const BorderSide(color: Color(0xFFFCA5A5)),
                        ),
                        onPressed: () => _purgeAndReSource(coin),
                        child: const Text('Purge & Re-Source'),
                      ),
                      const SizedBox(width: 8),
                      ElevatedButton(
                        style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF22C55E)),
                        onPressed: () => _approve(coin),
                        child: const Text('Approve', style: TextStyle(color: Colors.white)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
