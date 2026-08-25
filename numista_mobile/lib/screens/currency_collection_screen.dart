import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import '../services/currency_image_service.dart';

/// ─────────────────────────────────────────────────────────────────────────────
///  CurrencyCollectionScreen
///  Browsable list of the user's paper-money / banknote sub-collection.
///  Data lives in:  `users/<email>/currency`
/// ─────────────────────────────────────────────────────────────────────────────

class CurrencyCollectionScreen extends StatefulWidget {
  final bool showAppBar;
  const CurrencyCollectionScreen({super.key, this.showAppBar = true});

  @override
  State<CurrencyCollectionScreen> createState() =>
      _CurrencyCollectionScreenState();
}

class _CurrencyCollectionScreenState extends State<CurrencyCollectionScreen> {
  // ── colour tokens (mirrors coin_detail_screen) ──────────────────────────
  Color get _kBg => Theme.of(context).brightness == Brightness.dark ? Color(0xFF0E1117) : Color(0xFFF1F5F9);
  Color get _kSurface => Theme.of(context).brightness == Brightness.dark ? Color(0xFF1A1D27) : Colors.white;
  Color get _kBorder => Theme.of(context).brightness == Brightness.dark ? Color(0xFF2D3143) : Color(0xFFE2E8F0);
  Color get _kText => Theme.of(context).brightness == Brightness.dark ? Color(0xFFE8EAF0) : Color(0xFF0F172A);
  Color get _kSubtext => Theme.of(context).brightness == Brightness.dark ? Color(0xFF8B92B4) : Color(0xFF475569);
  
  static const _kAccent  = Color(0xFF6366F1);
  static const _kGreen   = Color(0xFF10B981);
  static const _kGold    = Color(0xFFFFD700);

  // ── state ────────────────────────────────────────────────────────────────
  List<Map<String, dynamic>> _allNotes = [];
  List<Map<String, dynamic>> _filtered = [];
  bool   _loading = true;
  String _query   = '';
  String _filterType = 'All';

  final TextEditingController _searchCtrl = TextEditingController();
  final List<String> _typeFilters = [
    'All',
    'Federal Reserve Note',
    'Silver Certificate',
    'Gold Certificate',
    'Legal Tender',
    'National Bank Note',
    'Other',
  ];

  @override
  void initState() {
    super.initState();
    _loadNotes();
  }

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  // ── data loading ─────────────────────────────────────────────────────────
  Future<void> _loadNotes() async {
    setState(() => _loading = true);
    try {
      // Auth-primary gate: a real non-anonymous Firebase user always reads from
      // Firestore, regardless of the in-memory demo flag. The demo branch is
      // only reached when there is no authenticated user (Browse Demo path).
      final authUser = FirebaseAuth.instance.currentUser;
      final isRealUser = authUser != null && !authUser.isAnonymous;

      if (!isRealUser && GuestSeedService.isBrowseDemoMode) {
        final demoNotes = GuestSeedService.demoCoinCache
            .where((item) =>
                item['Is Currency'] == true ||
                item['Category'] == 'Currency' ||
                (item['Denomination']?.toString().contains('Bill') ?? false) ||
                (item['Denomination']?.toString().contains('Note') ?? false))
            .map((item) => Map<String, dynamic>.from(item))
            .toList();
        setState(() {
          _allNotes = demoNotes;
          _loading = false;
          _applyFilter();
        });
        return;
      }
      final snap = await FirebaseFirestore.instance
          .collection(AuthService.currencyPath)
          .get();
      final notes = snap.docs.map((d) {
        final data = d.data();
        return {'id': d.id, ...data};
      }).toList();
      // Sort by Personal Ref # as integer (it's stored as a string like '1', '282', etc.)
      notes.sort((a, b) {
        final aRef = int.tryParse((a['Personal Ref #'] ?? '').toString()) ?? 9999;
        final bRef = int.tryParse((b['Personal Ref #'] ?? '').toString()) ?? 9999;
        return aRef.compareTo(bRef);
      });
      setState(() {
        _allNotes = notes;
        _loading = false;
        _applyFilter();
      });
    } catch (e) {
      setState(() => _loading = false);
    }
  }

  void _applyFilter() {
    var list = List<Map<String, dynamic>>.from(_allNotes);
    // Type filter
    if (_filterType != 'All') {
      final ft = _filterType.toLowerCase();
      list = list.where((n) {
        final ct = (n['currency_type'] ?? '').toString().toLowerCase();
        final desc = (n['Description'] ?? '').toString().toLowerCase();
        return ct.contains(ft.split(' ').first) || desc.contains(ft.split(' ').first);
      }).toList();
    }
    // Search
    if (_query.isNotEmpty) {
      final q = _query.toLowerCase();
      list = list.where((n) {
        final desc = (n['Description'] ?? '').toString().toLowerCase();
        final yr   = (n['Year'] ?? '').toString().toLowerCase();
        final cond = (n['Condition'] ?? '').toString().toLowerCase();
        final notes = (n['Personal Notes'] ?? '').toString().toLowerCase();
        return desc.contains(q) || yr.contains(q) || cond.contains(q) || notes.contains(q);
      }).toList();
    }
    _filtered = list;
  }

  // ── helpers ──────────────────────────────────────────────────────────────
  String _labelForType(String? raw) {
    switch ((raw ?? '').toLowerCase()) {
      case 'federal_reserve_note': return 'Federal Reserve Note';
      case 'silver_certificate':  return 'Silver Certificate';
      case 'gold_certificate':    return 'Gold Certificate';
      case 'legal_tender':        return 'Legal Tender';
      case 'national_bank_note':  return 'National Bank Note';
      default:                    return 'Currency';
    }
  }

  Color _colorForType(String? raw) {
    switch ((raw ?? '').toLowerCase()) {
      case 'federal_reserve_note': return Color(0xFF059669);
      case 'silver_certificate':  return Color(0xFF3B82F6);
      case 'gold_certificate':    return _kGold;
      case 'legal_tender':        return Color(0xFFEF4444);
      case 'national_bank_note':  return Color(0xFF8B5CF6);
      default:                    return _kAccent;
    }
  }

  String _extractDenomination(Map<String, dynamic> note) {
    // Denomination field is often empty; parse from Description
    final denom = (note['Denomination'] ?? '').toString().trim();
    if (denom.isNotEmpty && denom != 'null') return denom;
    final desc = (note['Description'] ?? '').toString();
    // Match leading "$N" pattern
    final m = RegExp(r'^\$(\d+(?:\.\d+)?)').firstMatch(desc);
    return m != null ? '\$${m.group(1)}' : '?';
  }

  double _parseCost(String? raw) {
    if (raw == null || raw.isEmpty) return 0;
    return double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0;
  }

  // ── detail modal ─────────────────────────────────────────────────────────
  void _showDetail(BuildContext context, Map<String, dynamic> note) {
    showDialog(
      context: context,
      builder: (ctx) => NoteDetailDialog(
        note: note,
        kBg:      _kBg,
        kSurface: _kSurface,
        kBorder:  _kBorder,
        kText:    _kText,
        kSubtext: _kSubtext,
        kAccent:  _kAccent,
        kGreen:   _kGreen,
        typeLabel: _labelForType(note['currency_type']?.toString()),
        typeColor: _colorForType(note['currency_type']?.toString()),
        denomination: _extractDenomination(note),
      ),
    );
  }

  // ── totals ────────────────────────────────────────────────────────────────
  double get _totalCost => _filtered.fold(0, (s, n) => s + _parseCost(n['Cost']?.toString()));
  int    get _totalCount => _filtered.length;

  // ─── build ────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: widget.showAppBar ? _kBg : Colors.transparent,
      appBar: widget.showAppBar ? AppBar(
        backgroundColor: _kSurface,
        elevation: 0,
        title: Row(
          children: [
            Icon(Icons.account_balance_wallet_outlined,
                color: _kGold, size: 22),
            SizedBox(width: 10),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Currency Collection',
                    style: TextStyle(
                        color: _kText,
                        fontWeight: FontWeight.w700,
                        fontSize: 16)),
                Text(
                  '$_totalCount note${_totalCount != 1 ? "s" : ""}  ·  '
                  '\$${_totalCost.toStringAsFixed(0)} invested',
                  style: TextStyle(color: _kSubtext, fontSize: 11),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh_rounded, color: _kSubtext),
            tooltip: 'Refresh',
            onPressed: _loadNotes,
          ),
        ],
      ) : null,
      body: Column(
        children: [
          // ── Search + filter bar ──────────────────────────────────────────
          Container(
            color: _kSurface,
            padding: EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: Column(
              children: [
                TextField(
                  controller: _searchCtrl,
                  style: TextStyle(color: _kText, fontSize: 13),
                  decoration: InputDecoration(
                    hintText: 'Search descriptions, years, conditions…',
                    hintStyle: TextStyle(color: _kSubtext, fontSize: 13),
                    prefixIcon: Icon(Icons.search, color: _kSubtext, size: 18),
                    suffixIcon: _query.isNotEmpty
                        ? IconButton(
                            icon: Icon(Icons.close, color: _kSubtext, size: 16),
                            onPressed: () {
                              _searchCtrl.clear();
                              setState(() {
                                _query = '';
                                _applyFilter();
                              });
                            })
                        : null,
                    filled: true,
                    fillColor: _kBg,
                    border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: _kBorder)),
                    enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: _kBorder)),
                    focusedBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(8),
                        borderSide: BorderSide(color: _kAccent)),
                    contentPadding:
                        EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                  ),
                  onChanged: (v) => setState(() {
                    _query = v;
                    _applyFilter();
                  }),
                ),
                SizedBox(height: 8),
                // Type filter chips
                SizedBox(
                  height: 28,
                  child: ListView.separated(
                    scrollDirection: Axis.horizontal,
                    itemCount: _typeFilters.length,
                    separatorBuilder: (_, _) => SizedBox(width: 6),
                    itemBuilder: (ctx, i) {
                      final f = _typeFilters[i];
                      final active = _filterType == f;
                      return GestureDetector(
                        onTap: () => setState(() {
                          _filterType = f;
                          _applyFilter();
                        }),
                        child: Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: active ? _kAccent : _kBg,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                                color: active ? _kAccent : _kBorder),
                          ),
                          child: Text(f,
                              style: TextStyle(
                                  color: active ? Colors.white : _kSubtext,
                                  fontSize: 11,
                                  fontWeight: active
                                      ? FontWeight.w600
                                      : FontWeight.normal)),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),

          // ── List ─────────────────────────────────────────────────────────
          Expanded(
            child: _loading
                ? Center(
                    child: CircularProgressIndicator(color: _kAccent))
                : _filtered.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Icon(Icons.account_balance_wallet_outlined,
                                color: _kSubtext, size: 48),
                            SizedBox(height: 12),
                            Text(
                              _query.isEmpty
                                  ? 'No currency notes found'
                                  : 'No notes match "$_query"',
                              style: TextStyle(
                                  color: _kSubtext, fontSize: 14),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: EdgeInsets.all(12),
                        itemCount: _filtered.length,
                        itemBuilder: (ctx, i) {
                          final note = _filtered[i];
                          return _NoteCard(
                            note: note,
                            onTap: () => _showDetail(context, note),
                            typeLabel: _labelForType(
                                note['currency_type']?.toString()),
                            typeColor: _colorForType(
                                note['currency_type']?.toString()),
                            denomination: _extractDenomination(note),
                            kBg:      _kBg,
                            kSurface: _kSurface,
                            kBorder:  _kBorder,
                            kText:    _kText,
                            kSubtext: _kSubtext,
                            kGold:    _kGold,
                          );
                        },
                      ),
          ),
        ],
      ),
    );
  }
}

// ─── Note list card ──────────────────────────────────────────────────────────
class _NoteCard extends StatelessWidget {
  final Map<String, dynamic> note;
  final VoidCallback onTap;
  final String typeLabel;
  final Color  typeColor;
  final String denomination;
  final Color kBg, kSurface, kBorder, kText, kSubtext, kGold;

  const _NoteCard({
    required this.note,
    required this.onTap,
    required this.typeLabel,
    required this.typeColor,
    required this.denomination,
    required this.kBg,
    required this.kSurface,
    required this.kBorder,
    required this.kText,
    required this.kSubtext,
    required this.kGold,
  });

  @override
  Widget build(BuildContext context) {
    final desc    = (note['Description'] ?? '').toString();
    final yr      = (note['Year'] ?? '').toString();
    final cond    = (note['Condition'] ?? '').toString();
    final cost    = (note['Cost'] ?? '').toString();
    final refNo   = (note['Personal Ref #'] ?? '').toString();
    final imgObv  = (note['image_url_obverse'] ?? '').toString();
    // Some records have Description in the Year field — validate year before displaying
    final isValidYear = yr.isNotEmpty && yr.length <= 8 && !yr.startsWith(r'$');

    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: EdgeInsets.only(bottom: 8),
        decoration: BoxDecoration(
          color: kSurface,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: kBorder),
        ),
        child: Row(
          children: [
            // ── Image placeholder / actual image ─────────────────────────
            Container(
              width: 80,
              height: 72,
              decoration: BoxDecoration(
                color: typeColor.withAlpha(20),
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(10),
                  bottomLeft: Radius.circular(10),
                ),
              ),
              child: imgObv.isNotEmpty
                  ? ClipRRect(
                      borderRadius: BorderRadius.only(
                        topLeft: Radius.circular(10),
                        bottomLeft: Radius.circular(10),
                      ),
                      child: Image.network(
                        imgObv,
                        fit: BoxFit.cover,
                        errorBuilder: (_, _, _) =>
                            _notePlaceholder(denomination, typeColor),
                      ),
                    )
                  : _notePlaceholder(denomination, typeColor),
            ),

            // ── Content ──────────────────────────────────────────────────
            Expanded(
              child: Padding(
                padding:
                    EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Type badge + ref number
                    Row(
                      children: [
                        Container(
                          padding: EdgeInsets.symmetric(
                              horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: typeColor.withAlpha(30),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(
                                color: typeColor.withAlpha(80)),
                          ),
                          child: Text(typeLabel,
                              style: TextStyle(
                                  color: typeColor,
                                  fontSize: 9,
                                  fontWeight: FontWeight.w600)),
                        ),
                        Spacer(),
                        if (refNo.isNotEmpty)
                          Text('#$refNo',
                              style: TextStyle(
                                  color: kSubtext,
                                  fontSize: 10)),
                      ],
                    ),
                    SizedBox(height: 4),
                    // Description
                    Text(
                      desc,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                          color: kText,
                          fontSize: 12,
                          fontWeight: FontWeight.w600),
                    ),
                    SizedBox(height: 4),
                    // Year · Condition · Cost
                    Row(
                      children: [
                        if (isValidYear)
                          _chip(yr, kSubtext),
                        if (isValidYear && cond.isNotEmpty)
                          SizedBox(width: 6),
                        if (cond.isNotEmpty)
                          _chip(cond, kSubtext),
                        Spacer(),
                        if (cost.isNotEmpty && cost != r'$0.00')
                          Text(cost,
                              style: TextStyle(
                                  color: kGold,
                                  fontSize: 11,
                                  fontWeight: FontWeight.w700)),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            // ── Chevron ──────────────────────────────────────────────────
            Padding(
              padding: EdgeInsets.only(right: 10),
              child: Icon(Icons.chevron_right, color: kSubtext, size: 18),
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, Color color) => Container(
    padding: EdgeInsets.symmetric(horizontal: 5, vertical: 2),
    decoration: BoxDecoration(
      color: color.withAlpha(20),
      borderRadius: BorderRadius.circular(4),
    ),
    child: Text(label,
        style: TextStyle(
            color: color, fontSize: 9, fontWeight: FontWeight.w500)),
  );

  Widget _notePlaceholder(String denom, Color color) => Column(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Icon(Icons.account_balance_wallet_outlined,
          color: color, size: 22),
      SizedBox(height: 2),
      Text(denom,
          style: TextStyle(
              color: color,
              fontSize: 13,
              fontWeight: FontWeight.w800)),
    ],
  );
}

// ─── Note detail dialog ───────────────────────────────────────────────────────
class NoteDetailDialog extends StatelessWidget {
  final Map<String, dynamic> note;
  final String typeLabel;
  final Color  typeColor;
  final String denomination;
  final Color kBg, kSurface, kBorder, kText, kSubtext, kAccent, kGreen;

  const NoteDetailDialog({
    super.key,
    required this.note,
    required this.typeLabel,
    required this.typeColor,
    required this.denomination,
    required this.kBg,
    required this.kSurface,
    required this.kBorder,
    required this.kText,
    required this.kSubtext,
    required this.kAccent,
    required this.kGreen,
  });

  @override
  Widget build(BuildContext context) {
    final desc       = (note['Description'] ?? '').toString();
    final yr         = (note['Year'] ?? '').toString();
    final cond       = (note['Condition'] ?? '').toString();
    final cost       = (note['Cost'] ?? '').toString();
    final country    = (note['Country'] ?? '').toString();
    final purchDate  = (note['Purchase Date'] ?? '').toString();
    final series     = (note['Series/Issuer'] ?? '').toString();
    final pNotes     = (note['Personal Notes'] ?? '').toString();
    final refNo      = (note['Personal Ref #'] ?? '').toString();
    final sourceFile = (note['source_file'] ?? '').toString();
    final imgObv     = (note['image_url_obverse'] ?? '').toString();
    final imgRev     = (note['image_url_reverse'] ?? '').toString();

    return Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: EdgeInsets.all(20),
      child: Container(
        constraints: BoxConstraints(maxWidth: 500, maxHeight: 700),
        decoration: BoxDecoration(
          color: kBg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: kBorder),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Header ─────────────────────────────────────────────────
            Container(
              padding: EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: kSurface,
                borderRadius: BorderRadius.vertical(
                    top: Radius.circular(16)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Type badge
                  Container(
                    padding: EdgeInsets.symmetric(
                        horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: typeColor.withAlpha(30),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: typeColor.withAlpha(80)),
                    ),
                    child: Text(typeLabel,
                        style: TextStyle(
                            color: typeColor,
                            fontSize: 10,
                            fontWeight: FontWeight.w600)),
                  ),
                  Spacer(),
                  if (refNo.isNotEmpty)
                    Text('Ref #$refNo',
                        style: TextStyle(
                            color: kSubtext, fontSize: 11)),
                  SizedBox(width: 8),
                  GestureDetector(
                    onTap: () => Navigator.of(context).pop(),
                    child: Icon(Icons.close, color: kSubtext, size: 20),
                  ),
                ],
              ),
            ),

            Expanded(
              child: SingleChildScrollView(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Description title
                    Text(desc,
                        style: TextStyle(
                            color: kText,
                            fontSize: 16,
                            fontWeight: FontWeight.w700,
                            height: 1.3)),
                    if (yr.isNotEmpty) ...[
                      SizedBox(height: 4),
                      Text(yr,
                          style:
                              TextStyle(color: kSubtext, fontSize: 13)),
                    ],
                    SizedBox(height: 16),

                    // ── Images ──────────────────────────────────────────
                    Row(
                      children: [
                        _imageBox(context, imgObv, 'Obverse', typeColor, denomination),
                        SizedBox(width: 12),
                        _imageBox(context, imgRev, 'Reverse', typeColor, denomination),
                      ],
                    ),
                    SizedBox(height: 16),

                    // ── Key metrics ─────────────────────────────────────
                    _sectionHeader('Details', kSubtext),
                    SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: [
                        if (cost.isNotEmpty)
                          _infoChip('Cost', cost, kText, kSurface, kBorder),
                        if (cond.isNotEmpty)
                          _infoChip('Condition', cond, kText, kSurface, kBorder),
                        if (country.isNotEmpty)
                          _infoChip('Country', country, kText, kSurface, kBorder),
                        if (purchDate.isNotEmpty)
                          _infoChip('Purchased', purchDate, kText, kSurface, kBorder),
                        if (series.isNotEmpty)
                          _infoChip('Series', series, kText, kSurface, kBorder),
                      ],
                    ),

                    // ── Personal Notes ───────────────────────────────────
                    if (pNotes.isNotEmpty) ...[
                      SizedBox(height: 16),
                      _sectionHeader('Notes', kSubtext),
                      SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: kSurface,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: kBorder),
                        ),
                        child: Text(pNotes,
                            style: TextStyle(
                                color: kText, fontSize: 13, height: 1.5)),
                      ),
                    ],

                    // ── Provenance ───────────────────────────────────────
                    if (sourceFile.isNotEmpty) ...[
                      SizedBox(height: 16),
                      _sectionHeader('Record Source', kSubtext),
                      SizedBox(height: 8),
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: kAccent.withAlpha(12),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: kAccent.withAlpha(50)),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.insert_drive_file_outlined,
                                color: kAccent, size: 16),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                sourceFile.split('/').last,
                                style: TextStyle(
                                    color: kText,
                                    fontSize: 12,
                                    fontWeight: FontWeight.w500),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],

                    SizedBox(height: 8),
                    // "No image yet" notice
                    if (imgObv.isEmpty)
                      Container(
                        width: double.infinity,
                        padding: EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: Colors.amber.withAlpha(15),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                              color: Colors.amber.withAlpha(60)),
                        ),
                        child: Row(
                          children: [
                            Icon(Icons.image_not_supported_outlined,
                                color: Colors.amber, size: 14),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'No images yet for this note. '
                                'Photos can be added via the invoice scanner.',
                                style: TextStyle(
                                    color: Colors.amber,
                                    fontSize: 11),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String? _deriveCatalogKey(Map<String, dynamic> noteData, String side) {
    final sideSuffix = side.toLowerCase().startsWith('rev') ? 'rev' : 'obv';
    if (noteData['catalog_key'] != null && noteData['catalog_key'].toString().isNotEmpty) {
      final k = noteData['catalog_key'].toString().toLowerCase();
      return k.endsWith('_obv') || k.endsWith('_rev') ? k : '${k}_$sideSuffix';
    }
    final desc = (noteData['Description'] ?? '').toString();
    final type = (noteData['currency_type'] ?? '').toString().toLowerCase();

    final mFr = RegExp(r'fr[-._\s]*([0-9]+)([a-z]?)', caseSensitive: false).firstMatch(desc);
    if (mFr != null) {
      final frNum = mFr.group(1);
      final variant = mFr.group(2)?.toLowerCase() ?? '';
      final isStar = desc.toLowerCase().contains('star') || desc.contains('*');
      final starToken = isStar ? 'star' : 'norm';
      final varToken = variant.isNotEmpty ? '_$variant' : '';
      return 'fr_$frNum${varToken}_${starToken}_$sideSuffix';
    }

    final mCsa = RegExp(r't[-._\s]*([0-9]+)', caseSensitive: false).firstMatch(desc);
    if (mCsa != null || type.contains('csa') || type.contains('confederate')) {
      final tNum = mCsa != null ? mCsa.group(1) : '64';
      return 'csa_t${tNum}_$sideSuffix';
    }

    if (type.contains('fractional') || desc.toLowerCase().contains('fractional')) {
      return 'frac_fr1230_norm_$sideSuffix';
    }

    return null;
  }

  Widget _imageBox(BuildContext ctx, String url, String label, Color color, String denom) {
    if (url.isNotEmpty) {
      return _renderImageBoxContent(ctx, url, label, color, denom, null);
    }

    final catalogKey = _deriveCatalogKey(note, label);
    if (catalogKey == null) {
      return Expanded(child: _renderPlaceholder(label, color, denom));
    }

    return Expanded(
      child: FutureBuilder<BanknoteImageResult?>(
        future: CurrencyImageService().getReferenceImage(catalogKey, label),
        builder: (context, snapshot) {
          if (snapshot.hasData && snapshot.data != null) {
            final res = snapshot.data!;
            return _renderImageBoxContent(ctx, res.publicUrl, label, color, denom, res);
          }
          return _renderPlaceholder(label, color, denom);
        },
      ),
    );
  }

  Widget _renderImageBoxContent(
      BuildContext ctx, String displayUrl, String label, Color color, String denom, BanknoteImageResult? fallbackRes) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(label,
                style: TextStyle(
                    color: kSubtext,
                    fontSize: 10,
                    fontWeight: FontWeight.w600)),
            if (fallbackRes != null) ...[
              Spacer(),
              Container(
                padding: EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                decoration: BoxDecoration(
                  color: Colors.amber.withAlpha(30),
                  borderRadius: BorderRadius.circular(3),
                  border: Border.all(color: Colors.amber.withAlpha(90), width: 0.5),
                ),
                child: Text(
                  fallbackRes.badgeText,
                  style: TextStyle(color: Colors.amber, fontSize: 7, fontWeight: FontWeight.w700),
                ),
              ),
            ],
          ],
        ),
        SizedBox(height: 4),
        GestureDetector(
          onTap: displayUrl.isNotEmpty ? () => _openZoom(ctx, displayUrl) : null,
          child: Container(
            height: 90,
            decoration: BoxDecoration(
              color: color.withAlpha(15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: fallbackRes != null ? Colors.amber.withAlpha(100) : kBorder),
            ),
            child: displayUrl.isNotEmpty
                ? ClipRRect(
                    borderRadius: BorderRadius.circular(8),
                    child: Image.network(
                      displayUrl,
                      fit: BoxFit.cover,
                      width: double.infinity,
                      errorBuilder: (_, _, _) => _placeholder(color, denom),
                    ),
                  )
                : _placeholder(color, denom),
          ),
        ),
        if (fallbackRes != null && fallbackRes.attribution != null) ...[
          SizedBox(height: 2),
          Text(
            'Source: ${fallbackRes.attribution}',
            style: TextStyle(color: kSubtext, fontSize: 8, fontStyle: FontStyle.italic),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
        ],
      ],
    );
  }

  Widget _renderPlaceholder(String label, Color color, String denom) => Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: TextStyle(color: kSubtext, fontSize: 10, fontWeight: FontWeight.w600)),
          SizedBox(height: 4),
          Container(
            height: 90,
            decoration: BoxDecoration(
              color: color.withAlpha(15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: kBorder),
            ),
            child: _placeholder(color, denom),
          ),
        ],
      );

  void _openZoom(BuildContext ctx, String url) {
    Navigator.of(ctx).push(PageRouteBuilder(
      opaque: false,
      barrierColor: Colors.black87,
      barrierDismissible: true,
      pageBuilder: (c, anim, _) => GestureDetector(
        onTap: () => Navigator.of(ctx).pop(),
        child: Scaffold(
          backgroundColor: Colors.transparent,
          body: Center(
            child: InteractiveViewer(
              panEnabled: true,
              minScale: 0.5,
              maxScale: 5.0,
              child: Image.network(url, fit: BoxFit.contain),
            ),
          ),
        ),
      ),
    ));
  }

  Widget _placeholder(Color color, String denom) => Center(
    child: Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(Icons.account_balance_wallet_outlined,
            color: color, size: 26),
        SizedBox(height: 4),
        Text(denom,
            style: TextStyle(
                color: color,
                fontSize: 14,
                fontWeight: FontWeight.w700)),
      ],
    ),
  );

  Widget _sectionHeader(String text, Color color) => Text(
    text.toUpperCase(),
    style: TextStyle(
        color: color,
        fontSize: 10,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.2),
  );

  Widget _infoChip(String label, String value, Color textColor,
      Color bgColor, Color borderColor) =>
      Container(
        padding:
            EdgeInsets.symmetric(horizontal: 10, vertical: 6),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: borderColor),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label.toUpperCase(),
                style: TextStyle(
                    color: kSubtext,
                    fontSize: 9,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.5)),
            SizedBox(height: 2),
            Text(value,
                style: TextStyle(
                    color: textColor,
                    fontSize: 12,
                    fontWeight: FontWeight.w600)),
          ],
        ),
      );
}
