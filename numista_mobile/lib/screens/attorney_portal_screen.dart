// attorney_portal_screen.dart
// No-auth, token-gated read-only view of an estate report for attorneys.
//
// Route: Accessed via a signed URL or token in the query string.
// Token format: ?uid=<email>&token=<report_id>&state=NY&mode=living_inventory
//
// This screen fetches the report metadata from Firestore using the token
// (report_id = document ID in users/{uid}/estate_reports/{token}).
// It does NOT require Firebase Auth — it reads via the report_id token.
//
// Security: Firestore rules allow read of this document if the document ID
// matches the token in the request. Tokens expire after 30 days (checked here).

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:intl/intl.dart';

// ─────────────────────────────────────────────────────────────────────────────
// Theme constants (matches estate_planning_screen.dart)
// ─────────────────────────────────────────────────────────────────────────────
const _kNavy       = Color(0xFF0E1117);
const _kDeepBlue   = Color(0xFF0B1A2E);
const _kGold       = Color(0xFFFFD700);
const _kRed        = Color(0xFFF63366);
const _kGreen      = Color(0xFF10B981);
const _kCard       = Color(0xFF161B27);
const _kCardBorder = Color(0xFF2A3045);
const _kTextPrimary   = Color(0xFFECEFF4);
const _kTextSecondary = Color(0xFF8B92A5);
const _kAmber      = Color(0xFFF59E0B);

final _dollarFmt  = NumberFormat.currency(symbol: '\$', decimalDigits: 0);
final _dollar2Fmt = NumberFormat.currency(symbol: '\$', decimalDigits: 2);

// ─────────────────────────────────────────────────────────────────────────────
// AttorneyPortalScreen
// ─────────────────────────────────────────────────────────────────────────────
class AttorneyPortalScreen extends StatefulWidget {
  /// uid — Firestore user doc ID (email of collection owner)
  final String uid;

  /// token — report document ID in users/{uid}/estate_reports/{token}
  final String token;

  const AttorneyPortalScreen({
    super.key,
    required this.uid,
    required this.token,
  });

  @override
  State<AttorneyPortalScreen> createState() => _AttorneyPortalScreenState();
}

class _AttorneyPortalScreenState extends State<AttorneyPortalScreen> {
  bool _loading = true;
  bool _isNoToken = false;
  String? _error;
  Map<String, dynamic>? _report;
  List<Map<String, dynamic>> _coins = [];
  String _search = '';
  String _sortField = 'Name';
  bool _sortAscending = true;

  @override
  void initState() {
    super.initState();
    // Guard: Attorney Portal is only meaningful when a share token is present.
    // Accessing it from the sidebar nav passes an empty token — show a
    // friendly placeholder instead of crashing with a Firestore empty-path error.
    if (widget.token.isEmpty) {
      _isNoToken = true;
      _loading = false;
      return;
    }
    _loadReport();
  }

  Future<void> _loadReport() async {
    try {
      final db = FirebaseFirestore.instance;

      // 1. Load report metadata from root collection estate_reports/{token}
      DocumentSnapshot<Map<String, dynamic>> reportDoc;
      if (widget.token.isNotEmpty) {
        reportDoc = await db.collection('estate_reports').doc(widget.token).get();
      } else {
        // Fallback for legacy nested path if token missing
        reportDoc = await db
            .collection('users')
            .doc(widget.uid)
            .collection('estate_reports')
            .doc(widget.token)
            .get();
      }

      if (!reportDoc.exists) {
        setState(() {
          _error = 'This attorney report link is invalid or has expired.';
          _loading = false;
        });
        return;
      }

      final report = reportDoc.data()!;

      // 2. Check token status (active vs revoked)
      if (report['status'] == 'revoked') {
        setState(() {
          _error = 'This attorney report link has been revoked by the collection owner.';
          _loading = false;
        });
        return;
      }

      // 3. Check expiration
      final expiresAtStr = report['expires_at'] as String?;
      if (expiresAtStr != null) {
        final expiresAt = DateTime.tryParse(expiresAtStr);
        if (expiresAt != null && DateTime.now().toUtc().isAfter(expiresAt)) {
          setState(() {
            _error =
                'This attorney report link has expired. '
                'Please request a new link from the collection owner.';
            _loading = false;
          });
          return;
        }
      }

      // 4. Extract frozen snapshot or load inventory
      List<Map<String, dynamic>> coins = [];
      final snapshot = report['snapshot'] as Map<String, dynamic>?;
      final ownerUid = report['owner_uid'] as String? ?? widget.uid;

      if (snapshot != null && snapshot.containsKey('coins')) {
        coins = List<Map<String, dynamic>>.from(snapshot['coins']);
      } else if (ownerUid.isNotEmpty) {
        final coinsSnap = await db
            .collection('users')
            .doc(ownerUid)
            .collection('coins')
            .orderBy('Name')
            .get();

        coins = coinsSnap.docs
            .map((d) => {'id': d.id, ...d.data()})
            .toList();
      }

      setState(() {
        _report = report;
        _coins = coins;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = 'Failed to load report: $e';
        _loading = false;
      });
    }
  }

  List<Map<String, dynamic>> get _filteredCoins {
    var list = _coins.where((c) {
      if (_search.isEmpty) return true;
      final q = _search.toLowerCase();
      return (c['Name']?.toString().toLowerCase().contains(q) ?? false) ||
          (c['Year']?.toString().contains(q) ?? false) ||
          (c['Program/Series']?.toString().toLowerCase().contains(q) ?? false) ||
          (c['Condition']?.toString().toLowerCase().contains(q) ?? false);
    }).toList();

    list.sort((a, b) {
      dynamic av = a[_sortField];
      dynamic bv = b[_sortField];
      if (av == null && bv == null) return 0;
      if (av == null) return 1;
      if (bv == null) return -1;
      final cmp = av.toString().compareTo(bv.toString());
      return _sortAscending ? cmp : -cmp;
    });

    return list;
  }

  double _parseFmv(dynamic v) {
    if (v == null) return 0;
    return double.tryParse(v.toString().replaceAll('\$', '').replaceAll(',', '')) ?? 0;
  }

  @override
  Widget build(BuildContext context) {
    return Theme(
      data: _portalTheme(),
      child: Scaffold(
        backgroundColor: _kNavy,
        appBar: _buildAppBar(),
        body: _loading
            ? _buildLoading()
            : _isNoToken
                ? _buildNoToken()
                : _error != null
                    ? _buildError()
                    : _buildBody(),
      ),
    );
  }

  AppBar _buildAppBar() {
    return AppBar(
      backgroundColor: _kDeepBlue,
      elevation: 0,
      automaticallyImplyLeading: false,
      title: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              color: _kGold.withAlpha(20),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _kGold.withAlpha(60)),
            ),
            child: const Icon(Icons.account_balance_rounded,
                color: _kGold, size: 18),
          ),
          const SizedBox(width: 12),
          const Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Numista.AI',
                  style: TextStyle(
                      color: _kGold,
                      fontSize: 14,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.5)),
              Text('Attorney Access — Read Only',
                  style: TextStyle(
                      color: _kTextSecondary, fontSize: 10)),
            ],
          ),
          const Spacer(),
          if (_report != null)
            _ExpiryBadge(generatedAt: _report!['generated_at'] as String?),
        ],
      ),
    );
  }

  Widget _buildLoading() {
    return const Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          CircularProgressIndicator(color: _kGold, strokeWidth: 2),
          SizedBox(height: 16),
          Text('Loading estate report…',
              style: TextStyle(color: _kTextSecondary)),
        ],
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(32),
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _kRed.withAlpha(80)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline_rounded, color: _kRed, size: 48),
            const SizedBox(height: 16),
            const Text('Access Error',
                style: TextStyle(
                    color: _kRed, fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 12),
            Text(_error!,
                style: const TextStyle(color: _kTextSecondary, fontSize: 14),
                textAlign: TextAlign.center),
            const SizedBox(height: 20),
            const Text(
                'Contact the collection owner at Numista.AI to request a new report link.',
                style: TextStyle(color: _kTextSecondary, fontSize: 12),
                textAlign: TextAlign.center),
          ],
        ),
      ),
    );
  }

  /// Shown when the Attorney Portal is accessed from the sidebar nav without a
  /// share token. This is expected behaviour — the portal requires a URL that
  /// is generated from Estate Planning. No Firestore calls are made here.
  Widget _buildNoToken() {
    return Center(
      child: Container(
        margin: const EdgeInsets.all(32),
        padding: const EdgeInsets.all(28),
        constraints: const BoxConstraints(maxWidth: 480),
        decoration: BoxDecoration(
          color: _kCard,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: _kGold.withAlpha(80)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: _kGold.withAlpha(20),
                borderRadius: BorderRadius.circular(28),
                border: Border.all(color: _kGold.withAlpha(60)),
              ),
              child: const Icon(Icons.link_rounded, color: _kGold, size: 28),
            ),
            const SizedBox(height: 20),
            const Text(
              'No Report Link Provided',
              style: TextStyle(
                  color: _kGold, fontSize: 18, fontWeight: FontWeight.w700),
            ),
            const SizedBox(height: 12),
            const Text(
              'The Attorney Portal is only accessible via a secure share link '
              'generated from Estate Planning.',
              style: TextStyle(color: _kTextSecondary, fontSize: 14),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _kNavy,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: _kCardBorder),
              ),
              child: const Row(
                children: [
                  Icon(Icons.info_outline_rounded,
                      color: _kAmber, size: 16),
                  SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      'Go to Estate Planning → generate a report → '
                      'tap "Share with Attorney" to create a secure link.',
                      style: TextStyle(color: _kTextSecondary, fontSize: 12),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBody() {
    final r = _report!;
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFF59E0B).withAlpha(20),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFF59E0B).withAlpha(80)),
            ),
            child: const Row(
              children: [
                Icon(Icons.gavel_rounded, color: Color(0xFFF59E0B), size: 20),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    "LEGAL DISCLAIMER: This document is an inventory schedule prepared for estate reference purposes only. It does not constitute formal legal or tax advice. Consult a licensed probate attorney.",
                    style: TextStyle(color: Color(0xFFF59E0B), fontSize: 12, fontWeight: FontWeight.w600, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 8),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: const Color(0xFFEF4444).withAlpha(20),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xFFEF4444).withAlpha(90)),
            ),
            child: const Row(
              children: [
                Icon(Icons.warning_amber_rounded, color: Color(0xFFEF4444), size: 20),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    "LEGAL PROVENANCE WATERMARK: CATALOG REFERENCE PHOTO — NOT INDIVIDUAL ASSET PHOTO. Items relying on reference catalog imagery are contractually flagged for court audit compliance.",
                    style: TextStyle(color: Color(0xFFEF4444), fontSize: 12, fontWeight: FontWeight.w700, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          _buildHeader(r),
          const SizedBox(height: 24),
          _buildSummaryCards(r),
          const SizedBox(height: 24),
          if ((r['total_coins_needing_appraisal'] ?? 0) > 0)
            _buildIrsAppraisalBanner(r),
          const SizedBox(height: 24),
          _buildCoinTable(),
          const SizedBox(height: 24),
          _buildLegalDisclaimer(r),
        ],
      ),
    );
  }

  // ── Header ──────────────────────────────────────────────────────────────────
  Widget _buildHeader(Map<String, dynamic> r) {
    final mode = r['mode'] == 'estate_settlement'
        ? 'Estate Settlement Report'
        : 'Living Inventory Report';
    final state = r['state'] ?? '';
    final reportDate = r['report_date'] ?? '';

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF1a1a2e), Color(0xFF0E1117)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _kGold.withAlpha(40)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.description_outlined, color: _kGold, size: 20),
              const SizedBox(width: 8),
              Text(mode,
                  style: const TextStyle(
                      color: _kGold,
                      fontSize: 18,
                      fontWeight: FontWeight.w700,
                      letterSpacing: -0.3)),
            ],
          ),
          const SizedBox(height: 8),
          const Text('Secure Client Collection',
              style: TextStyle(
                  color: _kTextPrimary,
                  fontSize: 26,
                  fontWeight: FontWeight.w800,
                  letterSpacing: -0.5)),
          const SizedBox(height: 4),
          Row(
            children: [
              _Chip('$state Jurisdiction', _kAmber),
              const SizedBox(width: 8),
              _Chip('Report Date: $reportDate', _kTextSecondary),
              const SizedBox(width: 8),
              _Chip('Prepared by Numista.AI', _kTextSecondary),
            ],
          ),
          const SizedBox(height: 16),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFF10B981).withAlpha(15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFF10B981).withAlpha(40)),
            ),
            child: Row(
              children: [
                const Icon(Icons.lock_outline_rounded,
                    color: Color(0xFF10B981), size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Confidential Zero-Knowledge Client Database. '
                    'To protect user physical security, legal names are not stored on our servers. '
                    'Please cross-reference this database view with your client\'s PDF report (Token: ${widget.token.length > 15 ? widget.token.substring(0, 15) : widget.token}...).',
                    style: const TextStyle(color: Color(0xFF10B981), fontSize: 11),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Summary cards ────────────────────────────────────────────────────────────
  Widget _buildSummaryCards(Map<String, dynamic> r) {
    final totalFmv = (r['total_fmv'] as num?)?.toDouble() ?? 0;
    final totalCoins = r['total_coins'] as int? ?? 0;
    final costBasis = (r['total_cost_basis'] as num?)?.toDouble() ?? 0;
    final meltValue = (r['total_melt_value'] as num?)?.toDouble() ?? 0;
    final stepUp = (r['stepped_up_basis_benefit'] as num?)?.toDouble() ?? 0;
    final needsAppraisal = r['total_coins_needing_appraisal'] as int? ?? 0;

    return GridView.count(
      crossAxisCount: 3,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 2.0,
      children: [
        _SummaryCard('Total Collection FMV', _dollarFmt.format(totalFmv),
            Icons.monetization_on_outlined, _kGold),
        _SummaryCard('Total Coins', '$totalCoins items',
            Icons.toll_rounded, _kGreen),
        _SummaryCard('Cost Basis', _dollarFmt.format(costBasis),
            Icons.receipt_long_outlined, _kTextSecondary),
        _SummaryCard('Melt / Bullion Value', _dollarFmt.format(meltValue),
            Icons.bar_chart_rounded, _kAmber),
        _SummaryCard('Step-Up Benefit', _dollarFmt.format(stepUp),
            Icons.trending_up_rounded, _kGreen),
        _SummaryCard('Needs IRS Appraisal', '$needsAppraisal coins',
            Icons.gavel_rounded,
            needsAppraisal > 0 ? _kRed : _kGreen),
      ],
    );
  }

  // ── IRS appraisal banner ─────────────────────────────────────────────────────
  Widget _buildIrsAppraisalBanner(Map<String, dynamic> r) {
    final count = r['total_coins_needing_appraisal'] as int? ?? 0;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _kRed.withAlpha(15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _kRed.withAlpha(60)),
      ),
      child: Row(
        children: [
          const Icon(Icons.gavel_rounded, color: _kRed, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('IRS Qualified Appraisal Required',
                    style: TextStyle(
                        color: _kRed,
                        fontSize: 14,
                        fontWeight: FontWeight.w700)),
                const SizedBox(height: 4),
                Text(
                  '$count coin(s) have an estimated FMV ≥ \$3,000 and require a '
                  'qualified appraisal under IRC §170(f)(11) for inclusion on IRS Form 706.',
                  style:
                      const TextStyle(color: _kTextSecondary, fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ── Coin table ───────────────────────────────────────────────────────────────
  Widget _buildCoinTable() {
    final coins = _filteredCoins;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('Collection Inventory',
                style: TextStyle(
                    color: _kTextPrimary,
                    fontSize: 16,
                    fontWeight: FontWeight.w700)),
            const SizedBox(width: 12),
            Text('(${coins.length} of ${_coins.length} shown)',
                style:
                    const TextStyle(color: _kTextSecondary, fontSize: 12)),
            const Spacer(),
            SizedBox(
              width: 240,
              child: TextField(
                style:
                    const TextStyle(color: _kTextPrimary, fontSize: 13),
                decoration: InputDecoration(
                  hintText: 'Search coins…',
                  hintStyle: TextStyle(
                      color: _kTextSecondary.withAlpha(120), fontSize: 13),
                  prefixIcon: const Icon(Icons.search,
                      color: _kTextSecondary, size: 18),
                  filled: true,
                  fillColor: _kCard,
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 12, vertical: 8),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(color: _kCardBorder),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(color: _kCardBorder),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide:
                        const BorderSide(color: _kGold, width: 1.5),
                  ),
                ),
                onChanged: (v) => setState(() => _search = v),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Container(
          decoration: BoxDecoration(
            color: _kCard,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _kCardBorder),
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: DataTable(
                headingRowColor:
                    WidgetStateProperty.all(_kDeepBlue),
                dataRowColor: WidgetStateProperty.resolveWith((states) {
                  if (states.contains(WidgetState.hovered)) {
                    return _kGold.withAlpha(10);
                  }
                  return Colors.transparent;
                }),
                dividerThickness: 0.5,
                columnSpacing: 20,
                sortColumnIndex: _sortColumnIndex,
                sortAscending: _sortAscending,
                columns: [
                  _sortableCol('Name', 'Name'),
                  _sortableCol('Year', 'Year'),
                  _sortableCol('Mint', 'Mint Mark'),
                  _sortableCol('Condition', 'Condition'),
                  _sortableCol('Series', 'Program/Series'),
                  _sortableCol('Est. FMV', 'AI_Estimated_FMV'),
                  _sortableCol('Cost', 'Cost'),
                  _sortableCol('Melt Value', 'Melt_Value'),
                ],
                rows: coins.map((c) => _buildRow(c)).toList(),
              ),
            ),
          ),
        ),
      ],
    );
  }

  int get _sortColumnIndex {
    const cols = ['Name', 'Year', 'Mint Mark', 'Condition',
        'Program/Series', 'AI_Estimated_FMV', 'Cost', 'Melt_Value'];
    return cols.indexOf(_sortField).clamp(0, 7);
  }

  DataColumn _sortableCol(String label, String field) {
    return DataColumn(
      label: Text(label,
          style: const TextStyle(
              color: _kGold, fontSize: 11, fontWeight: FontWeight.w600)),
      onSort: (_, asc) => setState(() {
        _sortField = field;
        _sortAscending = asc;
      }),
    );
  }

  DataRow _buildRow(Map<String, dynamic> c) {
    final fmv = _parseFmv(c['AI_Estimated_FMV']);
    final melt = _parseFmv(c['Melt_Value']);
    final cost = _parseFmv(c['Cost']);
    final needsAppraisal = fmv >= 3000;

    return DataRow(cells: [
      DataCell(Row(children: [
        if (needsAppraisal)
          const Padding(
            padding: EdgeInsets.only(right: 4),
            child: Icon(Icons.gavel_rounded, color: _kRed, size: 12),
          ),
        Flexible(
          child: Text(c['Name']?.toString() ?? '—',
              style: TextStyle(
                  color: needsAppraisal ? _kRed : _kTextPrimary,
                  fontSize: 12,
                  fontWeight: needsAppraisal
                      ? FontWeight.w600
                      : FontWeight.normal),
              overflow: TextOverflow.ellipsis,
              maxLines: 1),
        ),
      ])),
      DataCell(Text(c['Year']?.toString() ?? '—',
          style: const TextStyle(color: _kTextSecondary, fontSize: 12))),
      DataCell(Text(c['Mint Mark']?.toString() ?? '—',
          style: const TextStyle(color: _kTextSecondary, fontSize: 12))),
      DataCell(Text(c['Condition']?.toString() ?? '—',
          style: const TextStyle(color: _kTextPrimary, fontSize: 12))),
      DataCell(
        SizedBox(
          width: 120,
          child: Text(c['Program/Series']?.toString() ?? '—',
              style: const TextStyle(color: _kTextSecondary, fontSize: 11),
              overflow: TextOverflow.ellipsis),
        ),
      ),
      DataCell(Text(
          fmv > 0 ? _dollar2Fmt.format(fmv) : '—',
          style: TextStyle(
              color: fmv > 0 ? _kGold : _kTextSecondary, fontSize: 12))),
      DataCell(Text(
          cost > 0 ? _dollar2Fmt.format(cost) : '—',
          style: const TextStyle(color: _kTextSecondary, fontSize: 12))),
      DataCell(Text(
          melt > 0 ? _dollar2Fmt.format(melt) : '—',
          style: TextStyle(
              color: melt > 0 ? _kAmber : _kTextSecondary, fontSize: 12))),
    ]);
  }

  // ── Legal disclaimer ─────────────────────────────────────────────────────────
  Widget _buildLegalDisclaimer(Map<String, dynamic> r) {
    final state = r['state'] ?? '';
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _kCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _kCardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.info_outline_rounded,
                  color: _kTextSecondary, size: 16),
              SizedBox(width: 8),
              Text('Legal Disclaimer',
                  style: TextStyle(
                      color: _kTextSecondary,
                      fontSize: 12,
                      fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'This report was generated by Numista.AI for informational purposes only and does '
            'not constitute legal, tax, or financial advice. FMV estimates are AI-generated '
            'approximations and should not be used as formal appraisals. For $state estate '
            'tax purposes, a qualified appraisal by a certified numismatist may be required. '
            'This document is intended solely for the named recipient and is confidential. '
            'Numista.AI is a product of SGroup LLC.',
            style: const TextStyle(
                color: _kTextSecondary, fontSize: 11, height: 1.5),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              const Icon(Icons.copyright_rounded,
                  color: _kTextSecondary, size: 12),
              const SizedBox(width: 4),
              Text(
                '${DateTime.now().year} SGroup LLC / Numista.AI  •  '
                'Report ID: ${widget.token}',
                style:
                    const TextStyle(color: _kTextSecondary, fontSize: 10),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: () {
                  Clipboard.setData(ClipboardData(
                      text:
                          'https://numista.ai/attorney?uid=${widget.uid}&token=${widget.token}'));
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content:
                          Text('Report link copied to clipboard'),
                      backgroundColor: _kCard,
                    ),
                  );
                },
                icon: const Icon(Icons.link_rounded,
                    size: 14, color: _kGold),
                label: const Text('Copy link',
                    style: TextStyle(color: _kGold, fontSize: 11)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Helper widgets
// ─────────────────────────────────────────────────────────────────────────────

class _ExpiryBadge extends StatelessWidget {
  final String? generatedAt;
  const _ExpiryBadge({this.generatedAt});

  @override
  Widget build(BuildContext context) {
    if (generatedAt == null) return const SizedBox.shrink();
    final generated = DateTime.tryParse(generatedAt!);
    if (generated == null) return const SizedBox.shrink();
    final expiry = generated.add(const Duration(days: 30));
    final daysLeft = expiry.difference(DateTime.now()).inDays;
    final expired = daysLeft < 0;
    final color = expired ? _kRed : daysLeft < 7 ? _kAmber : _kGreen;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Text(
        expired
            ? 'EXPIRED'
            : daysLeft == 0
                ? 'Expires today'
                : 'Expires in $daysLeft days',
        style: TextStyle(
            color: color,
            fontSize: 10,
            fontWeight: FontWeight.w600),
      ),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const _SummaryCard(this.label, this.value, this.icon, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _kCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _kCardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 16),
              const SizedBox(width: 6),
              Flexible(
                child: Text(label,
                    style: const TextStyle(
                        color: _kTextSecondary, fontSize: 10),
                    overflow: TextOverflow.ellipsis),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(value,
              style: TextStyle(
                  color: color,
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  letterSpacing: -0.5)),
        ],
      ),
    );
  }
}

class _Chip extends StatelessWidget {
  final String label;
  final Color color;
  const _Chip(this.label, this.color);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withAlpha(20),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withAlpha(50)),
      ),
      child: Text(label,
          style: TextStyle(color: color, fontSize: 10)),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// Theme
// ─────────────────────────────────────────────────────────────────────────────
ThemeData _portalTheme() => ThemeData.dark().copyWith(
      scaffoldBackgroundColor: _kNavy,
      colorScheme: const ColorScheme.dark(
        primary: _kGold,
        secondary: _kGold,
        surface: _kCard,
        error: _kRed,
      ),
      dataTableTheme: const DataTableThemeData(
        headingTextStyle:
            TextStyle(color: _kGold, fontSize: 11, fontWeight: FontWeight.w600),
        dataTextStyle:
            TextStyle(color: _kTextPrimary, fontSize: 12),
      ),
    );
