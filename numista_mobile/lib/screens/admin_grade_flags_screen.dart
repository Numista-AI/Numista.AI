import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../services/auth_service.dart';

const _apiUrl = 'https://numista-backend-568985927038.us-central1.run.app';

// ─── Data model ───────────────────────────────────────────────────────────────

class GradeFlag {
  final String flagId, coinId, userEmail, year, mintMark, programSeries,
      themeSubject, aiGrade, communityGrade, imageUrl,
      flaggedAt, resolvedGrade, resolvedBy;
  final int reviewCount;
  final double confidenceScore;
  final bool resolved;
  final Map<String, int> gradeTally;

  GradeFlag({
    required this.flagId, required this.coinId, required this.userEmail,
    required this.year, required this.mintMark, required this.programSeries,
    required this.themeSubject, required this.aiGrade,
    required this.communityGrade, required this.imageUrl,
    required this.flaggedAt, required this.resolvedGrade,
    required this.resolvedBy, required this.reviewCount,
    required this.confidenceScore, required this.resolved,
    required this.gradeTally,
  });

  factory GradeFlag.fromJson(Map<String, dynamic> j) => GradeFlag(
    flagId:         j['flag_id'] ?? '',
    coinId:         j['coin_id'] ?? '',
    userEmail:      j['user_email'] ?? '',
    year:           j['year'] ?? '',
    mintMark:       j['mint_mark'] ?? '',
    programSeries:  j['program_series'] ?? '',
    themeSubject:   j['theme_subject'] ?? '',
    aiGrade:        j['ai_grade'] ?? '',
    communityGrade: j['community_grade'] ?? '',
    imageUrl:       j['image_url'] ?? '',
    flaggedAt:      j['flagged_at'] ?? '',
    resolvedGrade:  j['resolved_grade'] ?? '',
    resolvedBy:     j['resolved_by'] ?? '',
    reviewCount:    j['review_count'] ?? 0,
    confidenceScore: (j['confidence_score'] ?? 0.0).toDouble(),
    resolved:       j['resolved'] ?? false,
    gradeTally:     Map<String, int>.from(j['grade_tally'] ?? {}),
  );

  String get displayName {
    final parts = [year, mintMark].where((s) => s.isNotEmpty).join('-');
    return parts.isNotEmpty
        ? '$parts ${programSeries.isNotEmpty ? programSeries : "Coin"}'
        : programSeries.isNotEmpty ? programSeries : 'Coin';
  }
}

// ─── Screen ───────────────────────────────────────────────────────────────────

class AdminGradeFlagsScreen extends StatefulWidget {
  const AdminGradeFlagsScreen({super.key});

  @override
  State<AdminGradeFlagsScreen> createState() => _AdminGradeFlagsScreenState();
}

class _AdminGradeFlagsScreenState extends State<AdminGradeFlagsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tab;
  List<GradeFlag> _open = [], _resolved = [];
  bool _loadingOpen = true, _loadingResolved = false;
  bool _resolvedLoaded = false;

  @override
  void initState() {
    super.initState();
    _tab = TabController(length: 2, vsync: this);
    _tab.addListener(() {
      if (_tab.index == 1 && !_resolvedLoaded) { _loadResolved(); }
    });
    _loadOpen();
  }

  @override
  void dispose() { _tab.dispose(); super.dispose(); }

  Future<void> _loadOpen() async {
    setState(() => _loadingOpen = true);
    try {
      final res = await http.get(
          Uri.parse('$_apiUrl/api/admin/grade_flags?resolved=false&limit=100'));
      if (res.statusCode == 200 && mounted) {
        final data = jsonDecode(res.body);
        setState(() {
          _open = (data['results'] as List)
              .map((j) => GradeFlag.fromJson(j)).toList();
          _loadingOpen = false;
        });
      } else {
        if (mounted) { setState(() => _loadingOpen = false); }
      }
    } catch (e) {
      if (mounted) { setState(() => _loadingOpen = false); }
    }
  }

  Future<void> _loadResolved() async {
    setState(() => _loadingResolved = true);
    try {
      final res = await http.get(
          Uri.parse('$_apiUrl/api/admin/grade_flags?resolved=true&limit=100'));
      if (res.statusCode == 200 && mounted) {
        final data = jsonDecode(res.body);
        setState(() {
          _resolved = (data['results'] as List)
              .map((j) => GradeFlag.fromJson(j)).toList();
          _loadingResolved = false;
          _resolvedLoaded  = true;
        });
      } else {
        if (mounted) { setState(() => _loadingResolved = false); }
      }
    } catch (e) {
      if (mounted) { setState(() => _loadingResolved = false); }
    }
  }

  void _onResolved(String flagId) {
    setState(() => _open.removeWhere((f) => f.flagId == flagId));
    _resolvedLoaded = false; // force reload of resolved tab
  }

  @override
  Widget build(BuildContext context) {
    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      _buildHeader(),
      _buildSummaryBar(),
      _buildTabBar(),
      Expanded(child: TabBarView(controller: _tab, children: [
        _FlagListTab(
          flags:     _open,
          loading:   _loadingOpen,
          emptyMsg:  'No open flags — all AI grades have been reviewed or not yet flagged.',
          emptyIcon: Icons.check_circle_outline,
          emptyColor: const Color(0xFF22C55E),
          onRefresh: _loadOpen,
          onResolved: _onResolved,
        ),
        _FlagListTab(
          flags:     _resolved,
          loading:   _loadingResolved,
          emptyMsg:  'No resolved flags yet.',
          emptyIcon: Icons.history,
          emptyColor: const Color(0xFF94A3B8),
          onRefresh: _loadResolved,
          onResolved: (_) {},
          readOnly:  true,
        ),
      ])),
    ]);
  }

  Widget _buildHeader() => Padding(
    padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
    child: Row(children: [
      Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
              colors: [Color(0xFFDC2626), Color(0xFFF97316)]),
          borderRadius: BorderRadius.circular(10),
        ),
        child: const Icon(Icons.admin_panel_settings_outlined,
            color: Colors.white, size: 22),
      ),
      const SizedBox(width: 12),
      const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text('Admin: Grade Flag Review',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900,
                color: Color(0xFF0F172A))),
        Text('Resolve community-disputed AI grades',
            style: TextStyle(fontSize: 13, color: Color(0xFF64748B))),
      ]),
    ]),
  );

  Widget _buildSummaryBar() {
    final flagged    = _open.length;
    final avgConf    = _open.isEmpty ? 0.0
        : _open.map((f) => f.confidenceScore).reduce((a, b) => a + b) / _open.length;
    final resolved   = _resolved.length;

    return Container(
      margin: const EdgeInsets.fromLTRB(24, 10, 24, 6),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
            colors: [Color(0xFF7F1D1D), Color(0xFF991B1B)]),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(mainAxisAlignment: MainAxisAlignment.spaceAround, children: [
        _sc('🚩', '$flagged',              'Open Flags'),
        _vd(),
        _sc('📊', '${(avgConf * 100).round()}%', 'Avg AI Conf'),
        _vd(),
        _sc('✅', '$resolved',             'Resolved'),
      ]),
    );
  }

  Widget _sc(String icon, String val, String lbl) => Column(
    mainAxisSize: MainAxisSize.min,
    children: [
      Text('$icon $val', style: const TextStyle(
          color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
      Text(lbl, style: const TextStyle(
          color: Color(0xFFFCA5A5), fontSize: 10)),
    ],
  );

  Widget _vd() => Container(
      height: 28, width: 1, color: const Color(0xFFF87171).withValues(alpha: 0.3));

  Widget _buildTabBar() => Container(
    margin: const EdgeInsets.symmetric(horizontal: 24),
    decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFE2E6E9)))),
    child: TabBar(
      controller: _tab,
      labelColor: const Color(0xFFDC2626),
      unselectedLabelColor: const Color(0xFF64748B),
      indicatorColor: const Color(0xFFDC2626),
      indicatorWeight: 3,
      tabs: [
        Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          const Icon(Icons.flag_rounded, size: 16),
          const SizedBox(width: 6),
          const Text('Open Flags'),
          if (_open.isNotEmpty) ...[
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
              decoration: BoxDecoration(
                  color: const Color(0xFFDC2626),
                  borderRadius: BorderRadius.circular(20)),
              child: Text('${_open.length}',
                  style: const TextStyle(color: Colors.white,
                      fontSize: 10, fontWeight: FontWeight.bold)),
            ),
          ],
        ])),
        const Tab(child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.history, size: 16),
          SizedBox(width: 6),
          Text('Resolved'),
        ])),
      ],
    ),
  );
}

// ─── Flag list ────────────────────────────────────────────────────────────────

class _FlagListTab extends StatelessWidget {
  final List<GradeFlag> flags;
  final bool loading, readOnly;
  final String emptyMsg;
  final IconData emptyIcon;
  final Color emptyColor;
  final Future<void> Function() onRefresh;
  final void Function(String) onResolved;

  const _FlagListTab({
    required this.flags, required this.loading,
    required this.emptyMsg, required this.emptyIcon,
    required this.emptyColor, required this.onRefresh,
    required this.onResolved, this.readOnly = false,
  });

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Center(child: CircularProgressIndicator(
          color: Color(0xFFDC2626)));
    }
    if (flags.isEmpty) {
      return Center(child: Column(mainAxisSize: MainAxisSize.min, children: [
        Icon(emptyIcon, size: 64, color: emptyColor),
        const SizedBox(height: 16),
        Text(emptyMsg, textAlign: TextAlign.center,
            style: const TextStyle(color: Color(0xFF64748B),
                fontSize: 15, height: 1.5)),
        const SizedBox(height: 20),
        ElevatedButton.icon(
          style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFDC2626)),
          icon: const Icon(Icons.refresh, color: Colors.white),
          label: const Text('Refresh', style: TextStyle(color: Colors.white)),
          onPressed: onRefresh,
        ),
      ]));
    }
    return RefreshIndicator(
      onRefresh: onRefresh,
      color: const Color(0xFFDC2626),
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: flags.length,
        separatorBuilder: (_, i) => const SizedBox(height: 14),
        itemBuilder: (_, i) => _FlagCard(
          flag: flags[i],
          readOnly: readOnly,
          onResolved: onResolved,
        ),
      ),
    );
  }
}

// ─── Flag Card ────────────────────────────────────────────────────────────────

class _FlagCard extends StatefulWidget {
  final GradeFlag flag;
  final bool readOnly;
  final void Function(String) onResolved;
  const _FlagCard({required this.flag, required this.readOnly,
      required this.onResolved});

  @override
  State<_FlagCard> createState() => _FlagCardState();
}

class _FlagCardState extends State<_FlagCard> {
  bool _expanded    = false;
  bool _submitting  = false;
  String _overrideGrade = '';

  Future<void> _resolve(String decision) async {
    setState(() => _submitting = true);
    try {
      final res = await http.post(
        Uri.parse('$_apiUrl/api/admin/grade_flags/${widget.flag.flagId}/resolve'),
        body: {
          'admin_email':    AuthService.userEmail,
          'decision':       decision,
          'resolved_grade': _overrideGrade,
          'notes':          '',
        },
      );
      if (res.statusCode == 200 && mounted) {
        final data = jsonDecode(res.body);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text(data['message'] ?? 'Resolved.'),
          backgroundColor: const Color(0xFF16A34A),
          duration: const Duration(seconds: 4),
        ));
        widget.onResolved(widget.flag.flagId);
      } else {
        if (mounted) {
          setState(() => _submitting = false);
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Failed to resolve. Try again.'),
            backgroundColor: Color(0xFFDC2626),
          ));
        }
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
    final f       = widget.flag;
    final confPct = (f.confidenceScore * 100).round();

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(
          color: widget.readOnly
              ? const Color(0xFFE2E6E9)
              : const Color(0xFFDC2626).withValues(alpha: 0.35),
          width: widget.readOnly ? 1 : 1.5,
        ),
        boxShadow: [BoxShadow(
          color: Colors.black.withValues(alpha: 0.05),
          blurRadius: 8, offset: const Offset(0, 2))],
      ),
      child: Column(children: [
        // ── Header ──
        Padding(
          padding: const EdgeInsets.all(14),
          child: Row(children: [
            // Coin image
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: f.imageUrl.isNotEmpty
                  ? Image.network(f.imageUrl, width: 68, height: 68,
                      fit: BoxFit.cover,
                      errorBuilder: (c, e, s) => _placeholder())
                  : _placeholder(),
            ),
            const SizedBox(width: 12),

            // Coin info
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(children: [
                  Expanded(child: Text(f.displayName, style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 15,
                      color: Color(0xFF0F172A)))),
                  if (widget.readOnly)
                    _badge('Resolved', const Color(0xFF22C55E))
                  else
                    _badge('🚩 Flagged', const Color(0xFFDC2626)),
                ]),
                if (f.themeSubject.isNotEmpty)
                  Text(f.themeSubject, style: const TextStyle(
                      fontSize: 12, color: Color(0xFF64748B))),
                const SizedBox(height: 8),

                // AI grade vs community
                Row(children: [
                  _gradeChip('AI Grade', f.aiGrade, const Color(0xFF6366F1)),
                  const SizedBox(width: 8),
                  const Icon(Icons.arrow_forward, size: 14,
                      color: Color(0xFFDC2626)),
                  const SizedBox(width: 8),
                  _gradeChip('Community', f.communityGrade,
                      const Color(0xFFDC2626)),
                ]),
                const SizedBox(height: 4),
                Text('${f.reviewCount} reviews · AI conf $confPct%',
                    style: const TextStyle(
                        fontSize: 11, color: Color(0xFFADB5BD))),
              ]),
            ),

            // Expand toggle
            if (!widget.readOnly)
              IconButton(
                icon: Icon(_expanded ? Icons.expand_less : Icons.expand_more,
                    color: const Color(0xFF94A3B8)),
                onPressed: () => setState(() => _expanded = !_expanded),
              ),
          ]),
        ),

        // ── Expanded detail + actions ──
        if (_expanded && !widget.readOnly)
          _buildActionPanel(f),

        // ── Resolved info (read-only tab) ──
        if (widget.readOnly && f.resolvedGrade.isNotEmpty)
          Container(
            padding: const EdgeInsets.fromLTRB(14, 0, 14, 12),
            child: Row(children: [
              const Icon(Icons.check_circle_rounded,
                  color: Color(0xFF22C55E), size: 16),
              const SizedBox(width: 6),
              Text('Resolved → ${f.resolvedGrade}',
                  style: const TextStyle(
                      fontSize: 12, color: Color(0xFF16A34A),
                      fontWeight: FontWeight.w600)),
              if (f.resolvedBy.isNotEmpty) ...[
                Text(' by ${f.resolvedBy.split('@').first}',
                    style: const TextStyle(
                        fontSize: 12, color: Color(0xFF94A3B8))),
              ],
            ]),
          ),
      ]),
    );
  }

  Widget _buildActionPanel(GradeFlag f) {
    // Grade tally bars
    final tally  = f.gradeTally;
    final maxVal = tally.isEmpty ? 1 : tally.values.reduce((a, b) => a > b ? a : b);

    return Container(
      padding: const EdgeInsets.fromLTRB(14, 0, 14, 14),
      decoration: const BoxDecoration(
        border: Border(top: BorderSide(color: Color(0xFFF1F5F9))),
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const SizedBox(height: 12),

        // Grade tally
        if (tally.isNotEmpty) ...[
          const Text('Community Grade Votes',
              style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600,
                  color: Color(0xFF334155))),
          const SizedBox(height: 8),
          ...tally.entries.map((e) => Padding(
            padding: const EdgeInsets.only(bottom: 6),
            child: Row(children: [
              SizedBox(width: 80, child: Text(e.key, style: const TextStyle(
                  fontSize: 12, fontWeight: FontWeight.w500,
                  color: Color(0xFF334155)))),
              Expanded(child: Stack(children: [
                Container(height: 16, decoration: BoxDecoration(
                    color: const Color(0xFFF1F5F9),
                    borderRadius: BorderRadius.circular(8))),
                FractionallySizedBox(
                  widthFactor: e.value / maxVal,
                  child: Container(height: 16, decoration: BoxDecoration(
                      color: e.key == f.communityGrade
                          ? const Color(0xFFDC2626)
                          : const Color(0xFF94A3B8),
                      borderRadius: BorderRadius.circular(8))),
                ),
              ])),
              const SizedBox(width: 8),
              Text('${e.value}×', style: const TextStyle(
                  fontSize: 12, color: Color(0xFF64748B))),
            ]),
          )),
          const SizedBox(height: 14),
        ],

        // Optional override dropdown
        const Text('Admin Override (optional)',
            style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600,
                color: Color(0xFF64748B))),
        const SizedBox(height: 6),
        DropdownButtonFormField<String>(
          initialValue: _overrideGrade.isEmpty ? null : _overrideGrade,
          hint: const Text('Leave blank to use recommended grade',
              style: TextStyle(fontSize: 12, color: Color(0xFFADB5BD))),
          decoration: InputDecoration(
            contentPadding: const EdgeInsets.symmetric(
                horizontal: 12, vertical: 10),
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
            enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8),
                borderSide: const BorderSide(color: Color(0xFFCBD5E1))),
          ),
          items: [
            const DropdownMenuItem(value: '', child: Text('— Use recommended —',
                style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)))),
            ...const [
              'P-1 (Poor)','FR-2 (Fair)','AG-3 (About Good)',
              'G-4 (Good)','VG-8 (Very Good)','F-12 (Fine)',
              'VF-20 (Very Fine)','VF-30 (Very Fine)','EF-40 (Extremely Fine)',
              'AU-50 (About Uncirculated)','AU-58 (About Uncirculated)',
              'MS-60','MS-61','MS-62','MS-63','MS-64','MS-65',
              'MS-66','MS-67','MS-68','MS-69','MS-70',
              'PF-63 (Proof)','PF-65 (Proof)','PF-67 (Proof)','PF-69 (Proof)',
              'PF-70 (Proof)',
            ].map((g) => DropdownMenuItem(value: g,
                child: Text(g, style: const TextStyle(fontSize: 12)))),
          ],
          onChanged: (v) => setState(() => _overrideGrade = v ?? ''),
        ),
        const SizedBox(height: 14),

        // Action buttons
        Row(children: [
          Expanded(
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFFDC2626),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
              icon: _submitting
                  ? const SizedBox(width: 16, height: 16,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.people_alt_outlined, size: 18),
              label: Text(
                _overrideGrade.isNotEmpty
                    ? 'Set to $_overrideGrade'
                    : 'Accept: ${f.communityGrade}',
                style: const TextStyle(
                    fontSize: 13, fontWeight: FontWeight.bold)),
              onPressed: _submitting
                  ? null : () => _resolve('accept_community'),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: OutlinedButton.icon(
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Color(0xFF6366F1)),
                foregroundColor: const Color(0xFF6366F1),
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
              icon: const Icon(Icons.auto_awesome, size: 18),
              label: Text('Keep AI: ${f.aiGrade}',
                  style: const TextStyle(fontSize: 13,
                      fontWeight: FontWeight.bold)),
              onPressed: _submitting
                  ? null : () => _resolve('keep_ai'),
            ),
          ),
        ]),
      ]),
    );
  }

  Widget _gradeChip(String label, String grade, Color color) => Column(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Text(label, style: TextStyle(fontSize: 9, color: color.withValues(alpha: 0.7))),
      Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Text(grade.isEmpty ? '—' : grade, style: TextStyle(
            fontSize: 11, fontWeight: FontWeight.bold, color: color)),
      ),
    ],
  );

  Widget _badge(String label, Color color) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
    decoration: BoxDecoration(
      color: color.withValues(alpha: 0.1),
      borderRadius: BorderRadius.circular(20),
      border: Border.all(color: color.withValues(alpha: 0.3)),
    ),
    child: Text(label, style: TextStyle(
        fontSize: 11, fontWeight: FontWeight.bold, color: color)),
  );

  Widget _placeholder() => Container(
    width: 68, height: 68,
    decoration: BoxDecoration(
      color: const Color(0xFFF1F5F9),
      borderRadius: BorderRadius.circular(8)),
    child: const Icon(Icons.monetization_on_outlined,
        size: 34, color: Color(0xFFCBD5E1)),
  );
}
