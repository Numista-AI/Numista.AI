import 'dart:io' show File;
import 'dart:async';
import 'dart:typed_data';
import 'package:intl/intl.dart' as intl;
import 'package:two_dimensional_scrollables/two_dimensional_scrollables.dart';
import 'package:flutter/material.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import '../services/auth_service.dart';
// wishlist_service removed from this screen — wishlist action is in CoinDetailScreen
import '../models/coin_model.dart';
import '../services/epn_service.dart';
import '../services/reference_library_service.dart';
import '../services/coin_image_service.dart';
import '../widgets/coin_set_viewer.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/melt_value_service.dart';
import 'coin_detail_screen.dart';
import '../widgets/morgan_guide_flow.dart'; // Morgan guide step advancement

// --- Field name constants -----------------------------------------------------
class _F {
  static const country          = 'Country';
  static const year             = 'Year';
  static const mintMark         = 'Mint Mark';
  static const denomination     = 'Denomination';
  static const programSeries    = 'Program/Series';
  static const themeSubject     = 'Theme/Subject';
  static const condition        = 'Condition';
  static const strikeType       = 'Strike Type';
  static const holderType       = 'Holder Type';
  static const gradingService   = 'Grading Service';
  static const gradingCert      = 'Certification Number';
  static const metalContent     = 'Metal Content';
  static const cost             = 'Cost';
  static const purchaseDate     = 'Purchase Date';
  static const retailer         = 'Retailer/Website';
  static const retailerItemNo   = 'Retailer Item No.';
  static const retailerInvoice  = 'Retailer Invoice #';
  static const variety          = 'Variety';
  static const personalNotes    = 'Personal Notes';
  static const personalRef      = 'Personal Reference #';
  static const storageLocation  = 'Storage Location';
  // originalDesc removed — field exists in Firestore but not used in this screen

  // Internal/Legacy
  static const aiValue          = 'AI Estimated Value';
  static const meltValue        = 'Melt Value';
  static const isSilver         = 'Is Silver';
  static const pcgsNumber       = 'PCGS Number';
  static const imageObverse     = 'image_url_obverse';
  static const imageReverse     = 'image_url_reverse';
  // PCGS-specific extended fields
  static const population       = 'Population';
  static const isNfcSecure      = 'Is NFC Secure';
}

// --- Column definition --------------------------------------------------------
class _ColDef {
  final String field;
  final String header;
  final int    width;
  const _ColDef(this.field, this.header, this.width);
}

class MyCollectionScreen extends StatefulWidget {
  final Function(String)? onNavigate;
  /// Navigate to a screen AND pass an initial query (used for AI Deep Dive).
  final Function(String route, String query)? onNavigateWithQuery;
  const MyCollectionScreen({super.key, this.onNavigate, this.onNavigateWithQuery});
  @override
  State<MyCollectionScreen> createState() => _MyCollectionScreenState();
}

class _MyCollectionScreenState extends State<MyCollectionScreen> {

  // --- UI / filter state ---------------------------------------------------
  String? _selectedCoinId;
  int     _limit            = 50;
  String  _searchQuery      = '';
  // _showInspector removed — inspector is now always expanded in the dialog
  // Default: sort by date added, newest first (column index -1 = special Added sort)
  // Users can click any column header to override.
  int     _sortColumnIndex  = -1;   // -1 = sort by Added timestamp
  bool    _sortAscending    = false; // false = newest first
  /// Default: hide columns where every visible row is empty
  bool    _showOnlyPopulated = true;

  final _searchCtrl      = TextEditingController();
  final _searchFocus     = FocusNode();
  Timer? _searchDebounce;
  // Firestore stream -- created ONCE in initState to prevent StreamBuilder
  // re-subscription on every setState (which briefly unmounts the TextField
  // and causes focus loss on Flutter Web).
  late Stream<QuerySnapshot<Map<String, dynamic>>> _coinsStream;
  // Scroll controllers for the TableView (horizontal + vertical)
  final _tvHorizCtrl     = ScrollController();
  final _tvVertCtrl      = ScrollController();
  // Per-coin upload progress (null = idle, 0.0-1.0 = uploading)
  double? _uploadProgressObverse;
  double? _uploadProgressReverse;
  
  // Stores fetched eBay prices keyed by coinId
  final Map<String, String> _ebayPrices = {};
  // _isCheckingEbay removed — eBay fetch state tracked locally in each call

  // --- Similar Coins state (inspector) ------------------------------------
  List<ReferenceImage> _inspectorSimilar = [];
  bool _loadingInspectorSimilar = false;
  // _inspectorSimilarCoinId removed — tracking via _selectedCoinId is sufficient


  // --- Live spot prices (fetched once on mount, same endpoint as dashboard) --
  Map<String, double> _spotPrices = {};

  Future<void> _fetchSpotPrices() async {
    try {
      final resp = await http.get(Uri.parse(
          'https://numista-backend-568985927038.us-central1.run.app/api/spot_prices'));
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
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
    } catch (_) {}
  }

  // --- Colours (match Streamlit palette) ----------------------------------
  static const _bg        = Color(0xFFF0F2F6);
  static const _surface   = Colors.white;
  static const _text      = Color(0xFF31333F);
  static const _subtext   = Color(0xFF5A5C69);
  static const _accent    = Color(0xFF4C8CDA);
  static const _green     = Color(0xFF28A745);
  static const _greenBg   = Color(0xFFD4EED8);
  static const _greenText = Color(0xFF155724);
  static const _border    = Color(0xFFE2E6E9);
  static const _red       = Color(0xFFDC3545);

  // --- Column definitions (widths tuned so Value col is visible ≥1200px) --
  static const _columns = [
    // Year and Mint are narrow + adjacent so they read as one unit (e.g. 2025 W)
    // but remain independently sortable columns.
    _ColDef(_F.year,             'Year',           48),
    _ColDef(_F.mintMark,         'Mint',           28),
    _ColDef(_F.denomination,     'Denomination',  110),
    _ColDef(_F.programSeries,    'Program/Series',160),
    _ColDef(_F.themeSubject,     'Theme/Subject', 140),
    _ColDef(_F.variety,          'Variety/Error', 120),
    _ColDef(_F.condition,        'Condition',      70),
    _ColDef(_F.isSilver,         'Metal',          62),
    _ColDef(_F.meltValue,        'Melt Value',     80),
    _ColDef(_F.pcgsNumber,       'PCGS #',         80),
    _ColDef(_F.cost,             'Cost',           90),
    _ColDef(_F.purchaseDate,     'Date',           80),
    _ColDef(_F.retailerItemNo,   'Item #',         80),
    _ColDef(_F.retailerInvoice,  'Invoice #',      90),
    _ColDef(_F.storageLocation,  'Location',      100),
    _ColDef(_F.aiValue,          'AI Value',      100),
  ];

  /// Currency formatter shared across all cost/value cells.
  static final _currencyFmt =
      intl.NumberFormat.currency(symbol: r'$', decimalDigits: 2);

  // --- Lifecycle -----------------------------------------------------------
  @override
  void initState() {
    super.initState();
    // Create the Firestore stream ONCE -- reusing it in build() ensures
    // StreamBuilder never re-subscribes on setState, so the TextField
    // keeps its focus between keystrokes on Flutter Web.
    _coinsStream = _buildCoinsStream();

    _fetchSpotPrices();
    // Debounced search: 150ms after last keystroke before applying filter.
    // Short enough to feel instant; long enough to avoid per-character rebuilds.
    _searchCtrl.addListener(() {
      _searchDebounce?.cancel();
      _searchDebounce = Timer(const Duration(milliseconds: 150), () {
        if (mounted) {
          setState(() => _searchQuery = _searchCtrl.text.toLowerCase());
          // Re-request focus after setState to guard against Flutter Web
          // losing the active text field during the rebuild cycle.
          _searchFocus.requestFocus();
          // If Morgan is on Step 1 of the collection guide (the search-box
          // tutorial step), advance to Step 2 now that the user has used search.
          // This makes the guide reactive and prevents it from mysteriously
          // disappearing due to Flutter web rebuild cycles.
          _tryAdvanceMorganSearchStep();
        }
      });
    });
  }

  /// Advances the Morgan guide from Step 1 (search-box tutorial) to Step 2
  /// automatically when the user types their first search query.
  ///
  /// Only fires once per guide run: the guide must be on the collection flow
  /// AND on step 0 (the search step).  All other situations are ignored.
  void _tryAdvanceMorganSearchStep() {
    final gs = MorganGuideService.current.value;
    if (gs != null &&
        gs.guide.id == 'guide_collection' &&
        gs.step == 0 &&
        _searchCtrl.text.isNotEmpty) {
      MorganGuideService.next();
    }
  }

  Stream<QuerySnapshot<Map<String, dynamic>>> _buildCoinsStream() {
    Query<Map<String, dynamic>> q =
        FirebaseFirestore.instance.collection(AuthService.coinsPath);
    if (_limit > 0) q = q.limit(_limit);
    return q.snapshots();
  }

  @override
  void dispose() {
    _searchDebounce?.cancel();
    _searchCtrl.dispose();
    _searchFocus.dispose();
    _tvHorizCtrl.dispose();
    _tvVertCtrl.dispose();
    super.dispose();
  }

  // --- Face value lookup (mirrors Streamlit logic) -------------------------
  static double _faceValue(String denom) {
    final s = denom.toLowerCase().trim();
    if (s.contains('penny')   || s.contains('cent')   || s.contains('1c'))  return 0.01;
    if (s.contains('nickel')  || s.contains('5c'))                           return 0.05;
    if (s.contains('dime')    || s.contains('10c'))                          return 0.10;
    if (s.contains('quarter') || s.contains('25c'))                          return 0.25;
    if (s.contains('half')    || s.contains('50c'))                          return 0.50;
    if (s.contains('dollar')  || s.contains(r'$1'))                          return 1.00;
    if (s.contains(r'$2'))   return 2.00;
    if (s.contains(r'$5'))   return 5.00;
    if (s.contains(r'$10'))  return 10.00;
    if (s.contains(r'$20'))  return 20.00;
    if (s.contains(r'$50'))  return 50.00;
    if (s.contains(r'$100')) return 100.00;
    // Numeric fallback: "1" > 1.00, "0.25" > 0.25 (handles plain-number denominations
    // stored by PCGS import or CSV before display-string normalisation was in place).
    final n = double.tryParse(s.replaceAll(r'$', '').trim());
    if (n != null) return n;
    return 0.00;
  }

  // --- Sort + filter helpers -----------------------------------------------
  List<QueryDocumentSnapshot> _sorted(List<QueryDocumentSnapshot> raw) {
    final copy = List<QueryDocumentSnapshot>.from(raw);

    // Special case: index -1 = sort by Added/timestamp (most recently added first)
    if (_sortColumnIndex < 0) {
      copy.sort((a, b) {
        final ad = a.data() as Map<String, dynamic>;
        final bd = b.data() as Map<String, dynamic>;
        final aTs = ad['Added'] ?? ad['timestamp'] ?? ad['created_at'];
        final bTs = bd['Added'] ?? bd['timestamp'] ?? bd['created_at'];

        final aHas = aTs is Timestamp;
        final bHas = bTs is Timestamp;

        if (aHas && bHas) {
          // Both timestamped -- sort by time
          return _sortAscending ? aTs.compareTo(bTs) : bTs.compareTo(aTs);
        }
        // One has a timestamp, the other doesn't.
        // The timestamped coin was added via a known flow (newer) -- sort it first.
        if (aHas && !bHas) return _sortAscending ? 1  : -1;  // a newer > a first (desc)
        if (!aHas && bHas) return _sortAscending ? -1 : 1;   // b newer > b first (desc)
        // Neither has a timestamp -- stable fallback by doc ID
        return _sortAscending ? a.id.compareTo(b.id) : b.id.compareTo(a.id);
      });
      return copy;
    }

    final key = _columns[_sortColumnIndex].field;
    copy.sort((a, b) {
      var av = (a.data() as Map)[key]?.toString() ?? '';
      var bv = (b.data() as Map)[key]?.toString() ?? '';
      // Strip leading currency/tilde for melt/cost columns so they sort numerically
      av = av.replaceAll(RegExp(r'[~\$\s]'), '');
      bv = bv.replaceAll(RegExp(r'[~\$\s]'), '');
      final an = double.tryParse(av.replaceAll(RegExp(r'[^\d.]'), ''));
      final bn = double.tryParse(bv.replaceAll(RegExp(r'[^\d.]'), ''));
      final cmp = (an != null && bn != null) ? an.compareTo(bn) : av.compareTo(bv);
      return _sortAscending ? cmp : -cmp;
    });
    return copy;
  }

  List<QueryDocumentSnapshot> _filtered(List<QueryDocumentSnapshot> docs) {
    if (_searchQuery.isEmpty) return docs;
    return docs.where((doc) {
      final m = doc.data() as Map<String, dynamic>;
      return [
        _F.year,
        _F.denomination,
        _F.mintMark,
        _F.country,
        _F.programSeries,
        _F.themeSubject,
        _F.variety,
        _F.condition,
        _F.pcgsNumber,
        _F.meltValue,
        _F.aiValue,
        _F.storageLocation,
      ].any((k) => (m[k]?.toString().toLowerCase() ?? '').contains(_searchQuery));
    }).toList();
  }

  // --- Returns columns that have ≥1 non-empty value in current docs ---------
  // When _showOnlyPopulated is false, returns all columns unchanged.
  List<_ColDef> _visibleColumns(List<QueryDocumentSnapshot> docs) {
    if (!_showOnlyPopulated) return _columns;
    return _columns.where((col) {
      return docs.any((doc) {
        final v = (doc.data() as Map)[col.field]?.toString().trim() ?? '';
        return v.isNotEmpty && v != 'null' && v != 'N/A' && v != '\$0.00';
      });
    }).toList();
  }

  String _yearMint(Map m) {
    final y  = m[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final mm = m[_F.mintMark]?.toString() ?? '';
    return mm.isNotEmpty ? '$y-$mm' : y;
  }

  /// Converts a raw Firestore condition value to a display-friendly label.
  /// Numeric values map to Sheldon scale abbreviations.
  static String _conditionLabel(String raw) {
    if (raw.isEmpty || raw == 'null') return '';
    // Plain text values -- pass through directly
    final lower = raw.toLowerCase();
    if (lower.contains('proof'))       return 'Proof';
    if (lower.contains('uncirculated') || lower == 'unc') return 'Unc.';
    if (lower.contains('circulated'))  return 'Circ.';
    if (lower.contains('ungraded'))    return 'Raw';
    if (lower.contains('ms'))         return raw.toUpperCase();
    if (lower.contains('pr'))         return raw.toUpperCase();
    if (lower.contains('pf'))         return raw.toUpperCase();

    // Numeric Sheldon scale codes
    final n = int.tryParse(raw);
    if (n == null) return raw; // unknown string -- return as-is
    if (n == 1)   return 'P-1';
    if (n == 2)   return 'FR-2';
    if (n == 3)   return 'AG-3';
    if (n == 6)   return 'G-6';
    if (n == 8)   return 'G-8';
    if (n == 10)  return 'VG-10';
    if (n == 12)  return 'F-12';
    if (n == 15)  return 'F-15';
    if (n == 20)  return 'VF-20';
    if (n == 25)  return 'VF-25';
    if (n == 30)  return 'VF-30';
    if (n == 35)  return 'VF-35';
    if (n == 40)  return 'EF-40';
    if (n == 45)  return 'EF-45';
    if (n == 50)  return 'AU-50';
    if (n == 55)  return 'AU-55';
    if (n == 58)  return 'AU-58';
    if (n >= 60 && n <= 70) return 'MS-$n';
    return 'Grade $n'; // fallback for any other number
  }

  // --- Root build ---------------------------------------------------------
  @override
  Widget build(BuildContext context) {
    return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: _coinsStream,
      builder: (context, snap) {
        // Only show spinner on the very first load (no cached data yet).
        // On subsequent Firestore updates, keep showing the last known
        // content so the widget tree is not unmounted between updates.
        if (!snap.hasData && snap.connectionState == ConnectionState.waiting) {
          return const Center(child: CircularProgressIndicator(color: _accent));
        }
        if (snap.hasError) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.cloud_off_rounded, size: 48, color: _red),
                  const SizedBox(height: 16),
                  const Text(
                    'Could not load your collection',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: _text),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Check your internet connection and try refreshing the page.\nIf the problem persists, contact support at beta@numista.ai',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: _subtext, height: 1.5),
                  ),
                ],
              ),
            ),
          );
        }

        final allDocs = snap.data?.docs ?? [];
        final docs    = _sorted(_filtered(allDocs));

        if (_selectedCoinId == null && docs.isNotEmpty) {
          _selectedCoinId = docs.first.id;
        }
        final selDoc = docs.isNotEmpty
            ? (docs.any((d) => d.id == _selectedCoinId)
                ? docs.firstWhere((d) => d.id == _selectedCoinId)
                : docs.first)
            : null;
        if (selDoc != null) _selectedCoinId = selDoc.id;

        return SingleChildScrollView(
          padding: const EdgeInsets.all(32),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              const Text('My Collection', style: TextStyle(
                  fontSize: 36, fontWeight: FontWeight.w900, color: _text)),
              const SizedBox(height: 16),

              // Beta banner
              Container(
                width: double.infinity,
                padding: const EdgeInsets.symmetric(vertical: 4, horizontal: 16),
                decoration: BoxDecoration(
                    color: _accent, borderRadius: BorderRadius.circular(4)),
                child: const Text('BETA TESTING', style: TextStyle(
                    fontWeight: FontWeight.bold, fontSize: 10,
                    color: Colors.white, letterSpacing: 1.0)),
              ),
              const SizedBox(height: 24),

              _buildFiltersRow(),
              const SizedBox(height: 24),
              const Divider(color: _border),
              const SizedBox(height: 16),

              _buildStatsRow(docs),
              const SizedBox(height: 16),

              // Toolbar: section label + toggle + AI Report button
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Inventory List', style: TextStyle(
                      fontSize: 18, fontWeight: FontWeight.bold, color: _text)),
                  Row(children: [
                    // Column visibility toggle
                    _columnToggleButton(),
                    const SizedBox(width: 12),
                    ElevatedButton.icon(
                      onPressed: _onGenerateReport,
                      icon: const Icon(Icons.auto_awesome, size: 16),
                      label: const Text('Generate AI Report Now'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF63366),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(4)),
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                      ),
                    ),
                  ]),
                ],
              ),
              const SizedBox(height: 12),

              // Data table -- three distinct states
              if (allDocs.isEmpty)
                _buildCollectionEmptyState()
              else if (docs.isEmpty)
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 40),
                  child: Center(child: Text('No coins match your filter.',
                      style: TextStyle(color: _subtext))))
              else
                // SizedBox height sets the visible viewport -- the TableView
                // scrolls vertically AND horizontally internally, with the
                // header row and Actions column pinned.
                SizedBox(
                  height: 520,
                  child: _buildDataTable(docs),
                ),

              const SizedBox(height: 16),

              // Save Grid Changes -- red button at bottom matching Streamlit
              ElevatedButton.icon(
                onPressed: _onSaveGridChanges,
                icon: const Icon(Icons.save, size: 16),
                label: const Text('Save Grid Changes'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _red,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(4)),
                  padding: const EdgeInsets.symmetric(
                      horizontal: 20, vertical: 14),
                ),
              ),

              const SizedBox(height: 32),
            ],
          ),
        );
      },
    );
  }

  // --- Filters row --------------------------------------------------------
  Widget _buildFiltersRow() {
    return Row(children: [
      SizedBox(
        width: 140,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Text('Show:', style: TextStyle(color: _text, fontSize: 14)),
          const SizedBox(height: 8),
          _styledDropdown<String>(
            value: _limit == 0 ? 'All' : (_limit == 100 ? 'Last 100' : 'Last 50'),
            items: const ['Last 50', 'Last 100', 'All'],
            label: (v) => v,
            onChanged: (v) => setState(() {
              _limit = v == 'Last 50' ? 50 : v == 'Last 100' ? 100 : 0;
              _coinsStream = _buildCoinsStream();
            }),
          ),
        ]),
      ),
      const SizedBox(width: 24),
      Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          const Row(children: [
            Icon(Icons.search, size: 16, color: _text),
            SizedBox(width: 4),
            Text('Search', style: TextStyle(color: _text, fontSize: 14)),
          ]),
          const SizedBox(height: 8),
          SizedBox(
            height: 44,
            child: TextField(
              controller: _searchCtrl,
              focusNode: _searchFocus,
              style: const TextStyle(color: _text, fontSize: 14),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: const BorderSide(color: _border, width: 1.5)),
                enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: const BorderSide(color: _border, width: 1.5)),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: const BorderSide(color: _accent, width: 2.0)),
                hintText: 'Search by year, series, grade...',
                hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 14),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12),
                prefixIcon: const Icon(Icons.search, size: 18, color: Color(0xFFADB5BD)),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear, size: 16),
                        onPressed: () {
                          _searchCtrl.clear();
                          setState(() => _searchQuery = '');
                        })
                    : null,
              ),
            ),
          ),
        ]),
      ),
      const SizedBox(width: 24),
      Expanded(
        child: Container(
          margin: const EdgeInsets.only(top: 22),
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
              color: _greenBg, borderRadius: BorderRadius.circular(4)),
          child: const Row(children: [
            Icon(Icons.check_box, color: _green, size: 20),
            SizedBox(width: 8),
            Text('All estimated.',
                style: TextStyle(color: _greenText, fontSize: 14)),
          ]),
        ),
      ),
      const SizedBox(width: 12),
      // ── Vertex AI Reference Search button ─────────────────────────────
      if (widget.onNavigate != null)
        Container(
          margin: const EdgeInsets.only(top: 22),
          child: Tooltip(
            message: 'Search 1,913 coin reference entries with Vertex AI',
            child: ElevatedButton.icon(
              onPressed: () => widget.onNavigate!('Coin Search'),
              icon: const Icon(Icons.manage_search, size: 16),
              label: const Text('AI Reference Search'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF0D9488),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6)),
                padding: const EdgeInsets.symmetric(
                    horizontal: 14, vertical: 12),
                textStyle: const TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ),
    ]);
  }

  // --- AI value parser -- mirrors home_dashboard._parseCurrency -------------
  // Averages range strings so Est. Value matches the dashboard total.
  // e.g. '$4,000 - $6,000' > 5000.0 | '$3,700' > 3700.0 | 'Pending' > 0.0
  static double _parseAiValue(String raw) {
    if (raw.isEmpty || raw == 'Pending' || raw == 'null') return 0.0;
    final clean = raw.replaceAll(',', '');
    if (clean.contains(' - ')) {
      final parts = clean.split(' - ');
      final a = double.tryParse(parts[0].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
      final b = double.tryParse(parts[1].replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
      return (a + b) / 2;
    }
    return double.tryParse(clean.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
  }

  // --- Stats row -----------------------------------------------------------
  Widget _buildStatsRow(List<QueryDocumentSnapshot> docs) {
    double aiTotal = 0;
    double fvTotal = 0;
    double meltTotal = 0;
    for (final doc in docs) {
      final m   = doc.data() as Map<String, dynamic>;
      
      // AI Value sum -- average range values to match dashboard logic
      // e.g. '$4,000 - $6,000' > 5000, '$3,700' > 3700
      final aiRaw = m[_F.aiValue]?.toString() ?? '';
      aiTotal += _parseAiValue(aiRaw);

      // Melt Value -- live from spot prices when available, else from Firestore
      final liveMelt = _spotPrices.isNotEmpty
          ? (MeltValueService.compute(
                metalContent: m[_F.metalContent]?.toString() ?? '',
                denomination: m[_F.denomination]?.toString() ?? '',
                spotPrices: _spotPrices,
              ) ?? 0.0)
          : () {
              final meltRaw = m[_F.meltValue]?.toString() ?? '';
              final match = RegExp(r'\d+\.?\d*').firstMatch(meltRaw.replaceAll(',', ''));
              return match != null ? (double.tryParse(match.group(0)!) ?? 0.0) : 0.0;
            }();
      meltTotal += liveMelt;

      // Face Value sum
      fvTotal += _faceValue(m[_F.denomination]?.toString() ?? '');
    }
    return Row(children: [
      _statChip('Showing', '${docs.length} coins'),
      const SizedBox(width: 12),
      _statChip('Face Value', '\$${fvTotal.toStringAsFixed(2)}'),
      const SizedBox(width: 12),
      _statChip('Melt Value', '🥈 \$${meltTotal.toStringAsFixed(2)}'),
      const SizedBox(width: 12),
      _statChip('Est. Value', '\$${aiTotal.toStringAsFixed(2)}'),
    ]);
  }

  Widget _statChip(String label, String value) => Container(
    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
    decoration: BoxDecoration(
        color: _surface,
        border: Border.all(color: _border),
        borderRadius: BorderRadius.circular(6)),
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 11, color: _subtext)),
      const SizedBox(height: 2),
      Text(value, style: const TextStyle(
          fontSize: 15, fontWeight: FontWeight.bold, color: _text)),
    ]),
  );

  // --- Column visibility toggle button -------------------------------------
  Widget _columnToggleButton() {
    return Container(
      decoration: BoxDecoration(
        border: Border.all(color: _border),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(mainAxisSize: MainAxisSize.min, children: [
        _toggleSegment(
          label: 'Only with data',
          icon: Icons.filter_alt_outlined,
          active: _showOnlyPopulated,
          onTap: () => setState(() => _showOnlyPopulated = true),
          isLeft: true,
        ),
        Container(width: 1, height: 36, color: _border),
        _toggleSegment(
          label: 'All columns',
          icon: Icons.view_column_outlined,
          active: !_showOnlyPopulated,
          onTap: () => setState(() => _showOnlyPopulated = false),
          isLeft: false,
        ),
      ]),
    );
  }

  Widget _toggleSegment({
    required String label,
    required IconData icon,
    required bool active,
    required VoidCallback onTap,
    required bool isLeft,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: active ? _accent : Colors.white,
          borderRadius: BorderRadius.only(
            topLeft:     isLeft  ? const Radius.circular(5) : Radius.zero,
            bottomLeft:  isLeft  ? const Radius.circular(5) : Radius.zero,
            topRight:    !isLeft ? const Radius.circular(5) : Radius.zero,
            bottomRight: !isLeft ? const Radius.circular(5) : Radius.zero,
          ),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 14, color: active ? Colors.white : _subtext),
          const SizedBox(width: 6),
          Text(label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: active ? Colors.white : _subtext,
              )),
        ]),
      ),
    );
  }

  // --- Data Table (TableView -- sticky header + pinned Actions col) ---------
  Widget _buildDataTable(List<QueryDocumentSnapshot> docs) {
    final visCols   = _visibleColumns(docs);
    final totalCols = 1 + visCols.length; // col 0 = Actions (pinned)
    final totalRows = 1 + docs.length;    // row 0 = header (pinned)

    const double actionsW   = 96.0;
    const double headerH    = 44.0;
    const double dataH      = 44.0;
    const double colPadding = 8.0;

    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: _surface,
          border: Border.all(color: _border),
          borderRadius: BorderRadius.circular(8),
        ),
        // -- RawScrollbar: binds directly to _tvHorizCtrl -- no notification
        // depth wrangling. Always-visible thumb shows users they can scroll right.
        child: RawScrollbar(
          controller: _tvHorizCtrl,
          thumbVisibility: true,
          trackVisibility: true,
          thickness: 8,
          scrollbarOrientation: ScrollbarOrientation.top,
          thumbColor: const Color(0xFFB0B8C8),
          trackColor: const Color(0xFFF0F2F5),
          trackBorderColor: const Color(0xFFE0E4EA),
          child: TableView.builder(
            horizontalDetails: ScrollableDetails.horizontal(
                controller: _tvHorizCtrl),
            verticalDetails: ScrollableDetails.vertical(
                controller: _tvVertCtrl),
          // -- Pinning: freeze row 0 and column 0 --------------------------
          pinnedRowCount:    1,
          pinnedColumnCount: 1,
          columnCount: totalCols,
          rowCount:    totalRows,

          // -- Column sizing -----------------------------------------------
          columnBuilder: (col) {
            final width = col == 0
                ? actionsW
                : visCols[col - 1].width.toDouble();
            return TableSpan(
              extent: FixedTableSpanExtent(width),
              padding: const TableSpanPadding(
                  leading: colPadding, trailing: colPadding),
              foregroundDecoration: col == 0
                  ? const TableSpanDecoration(
                      border: TableSpanBorder(
                        trailing: BorderSide(color: _border, width: 0.8),
                      ))
                  : null,
            );
          },

          // -- Row sizing --------------------------------------------------
          rowBuilder: (row) => TableSpan(
            extent: FixedTableSpanExtent(row == 0 ? headerH : dataH),
            backgroundDecoration: TableSpanDecoration(
              color: row == 0
                  ? const Color(0xFFF8F9FB)
                  : (docs.length > row - 1 &&
                          docs[row - 1].id == _selectedCoinId
                      ? _accent.withAlpha(28)
                      : null),
              border: TableSpanBorder(
                trailing: BorderSide(color: _border.withAlpha(120), width: 0.5),
              ),
            ),
          ),

          // -- Cell builder ------------------------------------------------
          cellBuilder: (context, vicinity) {
            final col = vicinity.column;
            final row = vicinity.row;

            // -- HEADER ROW (row 0) -------------------------------------
            if (row == 0) {
              if (col == 0) {
                return _tvHeaderCell('Actions', null, sortAsc: null);
              }
              final colDef    = visCols[col - 1];
              final sortIdx   = _columns.indexOf(colDef);
              final isSorted  = _sortColumnIndex == sortIdx;
              return _tvHeaderCell(
                colDef.header,
                () => setState(() {
                  if (_sortColumnIndex == sortIdx) {
                    _sortAscending = !_sortAscending;
                  } else {
                    _sortColumnIndex = sortIdx;
                    _sortAscending   = true;
                  }
                }),
                sortAsc: isSorted ? _sortAscending : null,
              );
            }

            // -- DATA ROW ----------------------------------------------
            final doc = docs[row - 1];
            final m   = doc.data() as Map<String, dynamic>;
            final sel = doc.id == _selectedCoinId;

            void onTap() => _showCoinInspectorDialog(doc.id, m);

            // Actions cell (col 0)
            if (col == 0) {
              return TableViewCell(
                child: InkWell(
                  onTap: onTap,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 2),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        _iconBtn(Icons.info_outline, 'View Details', () {
                          final coin = CoinModel.fromMap(m, doc.id);
                          CoinDetailScreen.show(
                            context,
                            coin: coin,
                            spotPrices: _spotPrices,
                            onNavigateToAiChat: widget.onNavigateWithQuery != null
                                ? (q) => widget.onNavigateWithQuery!('AI Deepdive', q)
                                : null,
                            onDeleted: () => setState(() {}),
                            onEdited: () => setState(() {}),
                          );
                        }),
                        _iconBtn(Icons.edit_outlined,   'Edit',
                            () => _onEdit(doc.id, m)),
                        _iconBtn(Icons.auto_stories,    'AI Deep Dive',
                            () => _onDeepDive(doc.id, m)),
                        _iconBtn(Icons.delete_outline,  'Delete',
                            () => _onDelete(doc.id, m)),
                      ],
                    ),
                  ),
                ),
              );
            }

            // Data cell
            final colDef = visCols[col - 1];
            final value  = _getCellValue(colDef, m);

            // -- Cert # column: tappable PCGS link -------------------------
            if (colDef.field == _F.gradingCert && value.isNotEmpty) {
              final gradingService =
                  m[_F.gradingService]?.toString().toUpperCase() ?? '';
              final isPcgs = gradingService.contains('PCGS');
              return TableViewCell(
                child: InkWell(
                  onTap: isPcgs
                      ? () async {
                          final uri = Uri.parse(
                              'https://www.pcgs.com/cert/${value.replaceAll(RegExp(r'\D'), '')}');
                          if (await canLaunchUrl(uri)) {
                            await launchUrl(uri,
                                mode: LaunchMode.externalApplication);
                          }
                        }
                      : onTap,
                  mouseCursor: isPcgs
                      ? SystemMouseCursors.click
                      : MouseCursor.defer,
                  child: Align(
                    alignment: Alignment.centerLeft,
                    child: Text(
                      value,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                          fontSize: 12,
                          color: isPcgs ? _accent : _text,
                          decoration: isPcgs
                              ? TextDecoration.underline
                              : TextDecoration.none),
                    ),
                  ),
                ),
              );
            }

            return TableViewCell(
              child: InkWell(
                onTap: onTap,
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text(
                    value,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        fontSize: 12,
                        color: sel ? _accent : _text),
                  ),
                ),
              ),
            );
          },
        ),       // TableView.builder
        ),       // Scrollbar
      ),         // DecoratedBox
    );           // ClipRRect
  }

  /// Sticky header cell with optional sort-direction arrow.
  TableViewCell _tvHeaderCell(
      String label, VoidCallback? onTap, {required bool? sortAsc}) {
    return TableViewCell(
      child: Material(
        color: const Color(0xFFF8F9FB),
        child: InkWell(
          onTap: onTap,
          mouseCursor: onTap != null
              ? SystemMouseCursors.click
              : SystemMouseCursors.basic,
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Flexible(
                  child: Text(
                    label,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: _text),
                  ),
                ),
                if (sortAsc != null) ...[
                  const SizedBox(width: 2),
                  Icon(
                    sortAsc ? Icons.arrow_upward : Icons.arrow_downward,
                    size: 11,
                    color: _accent,
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Extracts a formatted display string for [col] from the coin data map [m].
  /// All cell value logic lives here so it can be called from the TableView
  /// cellBuilder without duplicating the switch statement.
  String _getCellValue(_ColDef col, Map<String, dynamic> m) {
    switch (col.field) {
      case _F.year:
        final v = m[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
        return v == 'null' ? '' : v;
      case _F.mintMark:
        final v = m[_F.mintMark]?.toString().trim() ?? '';
        return (v == 'null' || v == 'nan') ? '' : v;
      case _F.denomination:
        final rawD = m[_F.denomination]?.toString().trim() ?? '';
        if (rawD.isEmpty || rawD == 'null') return '';
        if (rawD.startsWith(r'$')) return rawD;         // '$1', '$5' etc -- keep as-is
        if (RegExp(r'^\d+(\.\d+)?$').hasMatch(rawD)) { // '1', '25' etc -- add $
          final n = double.tryParse(rawD);
          return (n != null && n == n.truncateToDouble())
              ? r'$' + n.toInt().toString()
              : r'$' + rawD;
        }
        // Word-form denomination (penny, nickel, dime, quarter) -- capitalise
        return rawD[0].toUpperCase() + rawD.substring(1);
      case _F.condition:
        return _conditionLabel(m[_F.condition]?.toString().trim() ?? '');
      case _F.isSilver:
        // Derive metal type from Metal Content field
        final mc2 = (m[_F.metalContent]?.toString() ?? '').toLowerCase();
        if (mc2.contains('gold')) return 'Au';
        if (mc2.contains('silver')) return 'Ag';
        if (mc2.contains('platinum')) return 'Pt';
        if (mc2.contains('palladium')) return 'Pd';
        // Fallback to legacy Is Silver boolean
        final rawS = m[_F.isSilver];
        if (rawS == true || rawS == 'true' || rawS == 1) return 'Ag';
        return '';
      case _F.pcgsNumber:
        final pn = m[_F.pcgsNumber]?.toString().trim() ?? '';
        return (pn.isEmpty || pn == 'null') ? '' : pn;
      case _F.meltValue:
        // Compute live from spot prices when available
        if (_spotPrices.isNotEmpty) {
          final lv = MeltValueService.compute(
            metalContent: m[_F.metalContent]?.toString() ?? '',
            denomination: m[_F.denomination]?.toString() ?? '',
            spotPrices: _spotPrices,
          );
          return lv != null ? '\$${lv.toStringAsFixed(2)}' : '';
        }
        final mv = m[_F.meltValue]?.toString().trim() ?? '';
        return (mv.isEmpty || mv == 'null' || mv == '--') ? '' : mv;
      case _F.storageLocation:
        final v = m[_F.storageLocation]?.toString().trim() ??
                  m['storage_location']?.toString().trim() ?? '';
        return (v.isEmpty || v == 'null' || v == 'Hardware Scan') ? '' : v;
      case _F.cost:
        final rawC = m[_F.cost]?.toString().trim() ?? '';
        if (rawC.isEmpty || rawC == 'null' ||
            rawC == '0' || rawC == '0.0') { return ''; }
        final n = double.tryParse(rawC.replaceAll(RegExp(r'[^\d.]'), ''));
        return n != null ? _currencyFmt.format(n) : rawC;
      case _F.aiValue:
        final av = m[_F.aiValue]?.toString() ?? '';
        return (av == 'Pending' || av == 'null' || av.isEmpty) ? '' : av;
      default:
        final v = m[col.field]?.toString().trim() ?? '';
        return (v == 'null' || v == 'nan') ? '' : v;
    }
  }


  Widget _iconBtn(IconData icon, String tip, VoidCallback onTap) => IconButton(
    icon: Icon(icon, size: 16),
    tooltip: tip,
    color: _subtext,
    padding: EdgeInsets.zero,
    constraints: const BoxConstraints(maxWidth: 32, maxHeight: 32),
    onPressed: onTap,
  );

  // --- Empty state (zero coins in collection) -------------------------------
  Widget _buildCollectionEmptyState() {
    return Container(
      margin: const EdgeInsets.symmetric(vertical: 32),
      padding: const EdgeInsets.all(48),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _border),
        boxShadow: [BoxShadow(color: Colors.black.withAlpha(6), blurRadius: 20, offset: const Offset(0, 4))],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Coin icon with gradient ring
          Container(
            width: 88, height: 88,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: const LinearGradient(
                colors: [Color(0xFFF63366), Color(0xFFFF8C42)],
                begin: Alignment.topLeft, end: Alignment.bottomRight,
              ),
              boxShadow: [BoxShadow(color: _accent.withAlpha(60), blurRadius: 20, spreadRadius: 2)],
            ),
            child: const Icon(Icons.toll_rounded, size: 44, color: Colors.white),
          ),
          const SizedBox(height: 24),
          const Text(
            'Your collection is empty',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: _text),
          ),
          const SizedBox(height: 8),
          const Text(
            'Add your first coin using any of the methods below.\nYou can scan an invoice, enter it manually, import from PCGS,\nor add a whole roll in one step.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: _subtext, height: 1.6),
          ),
          const SizedBox(height: 32),
          Wrap(
            spacing: 12, runSpacing: 12,
            alignment: WrapAlignment.center,
            children: [
              ElevatedButton.icon(
                icon: const Icon(Icons.edit_note, size: 18),
                label: const Text('Add Manually'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accent, foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: () => widget.onNavigate?.call('Add New Coins'),
              ),
              OutlinedButton.icon(
                icon: const Icon(Icons.auto_awesome_motion, size: 18),
                label: const Text('Browse Add Methods'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _accent,
                  side: const BorderSide(color: _accent),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: () => widget.onNavigate?.call('Add New Coins'),
              ),
            ],
          ),
        ],
      ),
    );
  }


  // --- Coin Inspector Dialog ------------------------------------------------
  void _showCoinInspectorDialog(String coinId, Map<String, dynamic> data) {
    setState(() {
      _selectedCoinId   = coinId;
      _vaultShowObverse = true;
    });
    _fetchInspectorSimilar(data);

    final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final mint  = data[_F.mintMark]?.toString().trim() ?? '';
    final denom = data[_F.denomination]?.toString() ?? '';
    // Capitalise word-form denomination in the dialog title (penny > Penny)
    final denomDisplay = denom.isNotEmpty && !denom.startsWith(r'$')
        ? denom[0].toUpperCase() + denom.substring(1)
        : denom;
    final title = '$year${mint.isNotEmpty ? '-$mint' : ''} $denomDisplay'.trim();

    // Pre-fetch reference image once (no user photo path only).
    // Capture in closure so FutureBuilder doesn't re-run on every rebuild.
    final hasUserPhoto = data[_F.imageObverse]?.toString().startsWith('http') == true
        || data[_F.imageReverse]?.toString().startsWith('http') == true;
    final refFuture = hasUserPhoto
        ? null
        : CoinImageService.fetchReferenceImages(
            year:         year,
            mint:         mint.isEmpty ? null : mint,
            denomination: denom.isEmpty ? null : denom,
            series:       (data[_F.programSeries]?.toString() ?? '').isEmpty
                ? null
                : data[_F.programSeries]?.toString(),
            subject:      (data[_F.themeSubject]?.toString() ?? '').isEmpty
                ? null
                : data[_F.themeSubject]?.toString(),
          );
    // refFuture passed into FutureBuilder below

    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (_) => StatefulBuilder(
        builder: (ctx, setDlg) {
          final obvUrl   = data[_F.imageObverse]?.toString() ?? '';
          final revUrl   = data[_F.imageReverse]?.toString() ?? '';
          final hasObv   = obvUrl.isNotEmpty && obvUrl.startsWith('http');
          final hasRev   = revUrl.isNotEmpty && revUrl.startsWith('http');
          final showObv  = _vaultShowObverse || (!hasRev && hasObv);
          final activeUrl = showObv ? obvUrl : revUrl;
          final hasActive = showObv ? hasObv : hasRev;

          return Dialog(
            backgroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            insetPadding: const EdgeInsets.symmetric(horizontal: 32, vertical: 24),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: 1100,
                maxHeight: MediaQuery.of(context).size.height * 0.88,
              ),
              child: Column(children: [
                // -- Header -----------------------------------------------
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  decoration: const BoxDecoration(
                    color: Color(0xFFF8F9FB),
                    border: Border(bottom: BorderSide(color: _border)),
                    borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
                  ),
                  child: Row(children: [
                    const Icon(Icons.book_outlined, size: 18, color: _text),
                    const SizedBox(width: 8),
                    Text('Coin Inspector -- $title',
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: _text)),
                    const Spacer(),
                    // Google Images search
                    Tooltip(
                      message: 'Opens Google Images: searches for this coin',
                      child: OutlinedButton.icon(
                        onPressed: () => _onSearchGoogle(data),
                        icon: const Icon(Icons.image_search, size: 15),
                        label: const Text('Google Images'),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: _text, side: const BorderSide(color: _border),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          textStyle: const TextStyle(fontSize: 12),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    // eBay search -- opens eBay in browser
                    Tooltip(
                      message: 'Search eBay sold listings for this coin',
                      child: ElevatedButton.icon(
                        onPressed: () => _onSearchEbay(data),
                        icon: const Icon(Icons.shopping_cart_outlined, size: 15),
                        label: const Text('eBay Search'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _accent, foregroundColor: Colors.white,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          textStyle: const TextStyle(fontSize: 12),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    IconButton(
                      onPressed: () => Navigator.pop(ctx),
                      icon: const Icon(Icons.close, size: 20, color: _subtext),
                      tooltip: 'Close',
                    ),
                  ]),
                ),

                // -- Body -------------------------------------------------
                Expanded(
                  child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    // Left panel: image (300px)
                    Container(
                      width: 300,
                      decoration: const BoxDecoration(
                        color: Color(0xFFF8F9FB),
                        border: Border(right: BorderSide(color: _border)),
                      ),
                      padding: const EdgeInsets.all(16),
                      child: refFuture != null
                          // No user photo -- show reference image via FutureBuilder
                          ? FutureBuilder<CoinImageResult>(
                              future: refFuture,
                              builder: (ctx2, snap) {
                                final ref       = snap.data;
                                final refObvUrl = ref?.obverseUrl ?? '';
                                final refRevUrl = ref?.reverseUrl ?? '';
                                final hasRefObv = refObvUrl.isNotEmpty;
                                final hasRefRev = refRevUrl.isNotEmpty;
                                final hasRef    = hasRefObv || hasRefRev;
                                final refUrl    = _vaultShowObverse
                                    ? (hasRefObv ? refObvUrl : refRevUrl)
                                    : (hasRefRev ? refRevUrl : refObvUrl);
                                final hasRefActive = refUrl.isNotEmpty;

                                return Column(children: [
                                  // Badge (above toggles, centered)
                                  if (hasRef) Container(
                                    alignment: Alignment.center,
                                    margin: const EdgeInsets.only(bottom: 6),
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: const Color(0xFF1A237E).withAlpha(20),
                                        borderRadius: BorderRadius.circular(4),
                                        border: Border.all(color: const Color(0xFF1A237E), width: 1),
                                      ),
                                      child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                        Icon(Icons.collections_outlined, size: 11, color: Color(0xFF1A237E)),
                                        SizedBox(width: 4),
                                        Text('REFERENCE', style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Color(0xFF1A237E), letterSpacing: 0.8)),
                                      ]),
                                    ),
                                  ),
                                  // Obverse / Reverse toggle
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    children: [
                                      _vaultToggleButton('Obverse', showObv, hasRefObv, () {
                                        setState(() => _vaultShowObverse = true);
                                        setDlg(() {});
                                      }),
                                      const SizedBox(width: 8),
                                      _vaultToggleButton('Reverse', !showObv, hasRefRev, () {
                                        setState(() => _vaultShowObverse = false);
                                        setDlg(() {});
                                      }),
                                    ],
                                  ),

                                  const SizedBox(height: 12),
                                  // Image
                                  Expanded(
                                    child: GestureDetector(
                                      onTap: hasRefActive
                                          ? () => _showImageLightbox(refUrl,
                                                label: showObv ? 'Obverse' : 'Reverse',
                                                isMicroscope: false)
                                          : null,
                                      child: ClipRRect(
                                        borderRadius: BorderRadius.circular(8),
                                        child: hasRefActive
                                            ? Stack(fit: StackFit.expand, children: [
                                                Image.network(refUrl, fit: BoxFit.contain,
                                                  loadingBuilder: (ctx, child, prog) => prog == null
                                                      ? child
                                                      : const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                                  errorBuilder: (ctx, err, st) => _vaultPlaceholder(
                                                      showObv ? 'Obverse' : 'Reverse', isError: true),
                                                ),
                                                Positioned(bottom: 8, right: 8,
                                                  child: Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                    decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                    child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                                      Icon(Icons.zoom_in, size: 12, color: Colors.white),
                                                      SizedBox(width: 3),
                                                      Text('Enlarge', style: TextStyle(fontSize: 10, color: Colors.white)),
                                                    ]),
                                                  ),
                                                ),
                                              ])
                                            : snap.connectionState == ConnectionState.waiting
                                                ? const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2))
                                                : _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse'),
                                      ),
                                    ),
                                  ),
                                  // Attribution
                                  if (hasRef && ref!.attribution != null) ...[
                                    const SizedBox(height: 6),
                                    Text(ref.attribution!,
                                        style: const TextStyle(fontSize: 9, color: _subtext, fontStyle: FontStyle.italic),
                                        textAlign: TextAlign.center),
                                  ],
                                  const SizedBox(height: 12),
                                  // Upload buttons
                                  Row(children: [
                                    Expanded(child: _vaultUploadButton(
                                      label: '+ Add My Photo',
                                      icon: Icons.add_photo_alternate_outlined,
                                      progress: _uploadProgressObverse,
                                      onTap: () async {
                                        await _onUploadVaultImage(side: 'obverse', field: _F.imageObverse,
                                          setProgress: (p) { setState(() => _uploadProgressObverse = p); setDlg(() {}); });
                                      },
                                    )),
                                    const SizedBox(width: 8),
                                    Expanded(child: _vaultUploadButton(
                                      label: '+ Add Reverse',
                                      icon: Icons.add_photo_alternate_outlined,
                                      progress: _uploadProgressReverse,
                                      onTap: () async {
                                        await _onUploadVaultImage(side: 'reverse', field: _F.imageReverse,
                                          setProgress: (p) { setState(() => _uploadProgressReverse = p); setDlg(() {}); });
                                      },
                                    )),
                                  ]),
                                ]);
                              },
                            )
                          // User HAS their own photo -- show it directly
                          : Column(children: [
                              Row(mainAxisAlignment: MainAxisAlignment.center, children: [
                                _vaultToggleButton('Obverse', showObv, hasObv, () {
                                  setState(() => _vaultShowObverse = true);
                                  setDlg(() {});
                                }),
                                const SizedBox(width: 8),
                                _vaultToggleButton('Reverse', !showObv, hasRev, () {
                                  setState(() => _vaultShowObverse = false);
                                  setDlg(() {});
                                }),
                              ]),
                              const SizedBox(height: 12),
                              Expanded(
                                child: GestureDetector(
                                  onTap: hasActive ? () => _showImageLightbox(activeUrl,
                                      label: showObv ? 'Obverse' : 'Reverse',
                                      isMicroscope: data['scan_source'] == 'microscope') : null,
                                  child: ClipRRect(
                                    borderRadius: BorderRadius.circular(8),
                                    child: hasActive
                                        ? Stack(fit: StackFit.expand, children: [
                                            Image.network(activeUrl, fit: BoxFit.contain,
                                              loadingBuilder: (ctx, child, prog) => prog == null ? child
                                                  : const Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                              errorBuilder: (ctx, err, st) {
                                                debugPrint('Image load error: $err  url: $activeUrl');
                                                return _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse', isError: true);
                                              },
                                            ),
                                            Positioned(bottom: 8, right: 8,
                                              child: Container(
                                                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                child: const Row(mainAxisSize: MainAxisSize.min, children: [
                                                  Icon(Icons.zoom_in, size: 12, color: Colors.white),
                                                  SizedBox(width: 3),
                                                  Text('Enlarge', style: TextStyle(fontSize: 10, color: Colors.white)),
                                                ]),
                                              ),
                                            ),
                                          ])
                                        : _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse'),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 12),
                              Row(children: [
                                Expanded(child: _vaultUploadButton(
                                  label: hasObv ? 'Replace Obverse' : '+ Obverse',
                                  icon: hasObv ? Icons.refresh : Icons.add_photo_alternate_outlined,
                                  progress: _uploadProgressObverse,
                                  onTap: () async {
                                    await _onUploadVaultImage(side: 'obverse', field: _F.imageObverse,
                                      setProgress: (p) { setState(() => _uploadProgressObverse = p); setDlg(() {}); });
                                  },
                                )),
                                const SizedBox(width: 8),
                                Expanded(child: _vaultUploadButton(
                                  label: hasRev ? 'Replace Reverse' : '+ Reverse',
                                  icon: hasRev ? Icons.refresh : Icons.add_photo_alternate_outlined,
                                  progress: _uploadProgressReverse,
                                  onTap: () async {
                                    await _onUploadVaultImage(side: 'reverse', field: _F.imageReverse,
                                      setProgress: (p) { setState(() => _uploadProgressReverse = p); setDlg(() {}); });
                                  },
                                )),
                              ]),
                            ]),
                    ),

                    // Right: scrollable details
                    Expanded(
                      child: SingleChildScrollView(
                        padding: const EdgeInsets.all(24),
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          _buildMetricStrip(data),
                          const SizedBox(height: 12),
                          _buildPcgsBar(data),
                          const SizedBox(height: 20),
                          _buildDetailGrid(data),
                          _buildCoinSetSection(data),
                          _buildRollBanner(data),
                          _buildSimilarCoinsInspector(),
                        ]),
                      ),
                    ),
                  ]),
                ),
              ]),
            ),
          );
        },
      ),
    );
  }

  // _buildInspectorSection was removed — inspector is now rendered directly
  // inside showDialog via the _buildMetricStrip / _buildDetailGrid helpers below.

  // --- Metric strip --------------------------------------------------------
  Widget _buildMetricStrip(Map<String, dynamic> data) {
    final liveMelt = MeltValueService.compute(
      metalContent: data[_F.metalContent]?.toString() ?? '',
      denomination: data[_F.denomination]?.toString() ?? '',
      spotPrices: _spotPrices,
    );
    final meltStr  = liveMelt != null
        ? '\$${liveMelt.toStringAsFixed(2)}'
        : (data[_F.meltValue]?.toString().isNotEmpty == true
            ? data[_F.meltValue].toString()
            : 'N/A');
    return Row(children: [
      Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', const Color(0xFF1A73E8), Icons.attach_money)),
      const SizedBox(width: 10),
      Expanded(child: _metricCard('Melt Value', meltStr, const Color(0xFF34A853), Icons.blur_circular_outlined)),
      const SizedBox(width: 10),
      Expanded(child: _metricCard('Grade', data[_F.condition]?.toString() ?? '--', const Color(0xFFF9AB00), Icons.grade_outlined)),
      const SizedBox(width: 10),
      Expanded(child: _metricCard(
          'Live eBay',
          _ebayPrices[_selectedCoinId] ?? 'Check >',
          const Color(0xFFE53935),
          Icons.shopping_cart_outlined,
          onTap: _ebayPrices[_selectedCoinId] != null
              ? null
              : () => _onCheckEbay(data),
      )),
    ]);
  }

  Widget _metricCard(String label, String value, Color accent, IconData icon, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: accent.withAlpha(15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: accent.withAlpha(60)),
      ),
      child: Row(children: [
        Icon(icon, color: accent, size: 20),
        const SizedBox(width: 10),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: TextStyle(fontSize: 11, color: accent, fontWeight: FontWeight.w600, letterSpacing: 0.4)),
          const SizedBox(height: 2),
          Text(value, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: _text)),
        ]),
      ]),
    ));
  }

  // --- PCGS feature bar ----------------------------------------------------
  Widget _buildPcgsBar(Map<String, dynamic> data) {
    final svc = data[_F.gradingService]?.toString() ?? '';
    if (!svc.toUpperCase().contains('PCGS')) return const SizedBox.shrink();

    final isNfc  = data[_F.isNfcSecure] == true;
    final pop    = data[_F.population]?.toString() ?? '';
    final pcgsNo = data[_F.pcgsNumber]?.toString() ?? '';

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFF003087).withAlpha(12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: const Color(0xFF003087).withAlpha(50)),
      ),
      child: Wrap(spacing: 16, runSpacing: 8, crossAxisAlignment: WrapCrossAlignment.center, children: [
        // PCGS label
        const Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.verified_outlined, size: 16, color: Color(0xFF003087)),
          SizedBox(width: 5),
          Text('PCGS Certified', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF003087))),
        ]),
        // NFC badge
        if (isNfc)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: const Color(0xFF34A853).withAlpha(20),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: const Color(0xFF34A853).withAlpha(80)),
            ),
            child: const Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.nfc, size: 13, color: Color(0xFF34A853)),
              SizedBox(width: 4),
              Text('NFC Secured', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF34A853))),
            ]),
          ),
        // Population
        if (pop.isNotEmpty)
          Row(mainAxisSize: MainAxisSize.min, children: [
            const Icon(Icons.bar_chart, size: 14, color: _subtext),
            const SizedBox(width: 4),
            Text('Pop: $pop', style: const TextStyle(fontSize: 12, color: _subtext, fontWeight: FontWeight.w500)),
          ]),
        // CoinFacts link
        if (pcgsNo.isNotEmpty)
          GestureDetector(
            onTap: () async {
              final uri = Uri.parse('https://www.pcgs.com/coinfacts/coin/$pcgsNo');
              if (!await launchUrl(uri, mode: LaunchMode.externalApplication) && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Could not open browser.')));
              }
            },
            child: const Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.open_in_new, size: 13, color: _accent),
              SizedBox(width: 4),
              Text('CoinFacts', style: TextStyle(fontSize: 12, color: _accent, fontWeight: FontWeight.w600, decoration: TextDecoration.underline)),
            ]),
          ),
      ]),
    );
  }

  // --- Sectioned detail grid ------------------------------------------------
  Widget _buildDetailGrid(Map<String, dynamic> data) {
    Widget section(String title, List<List<String?>> fields) {
      final cells = fields.where((f) => (f[1] ?? '').isNotEmpty).toList();
      if (cells.isEmpty) return const SizedBox.shrink();
      return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: _subtext, letterSpacing: 1.0)),
        const SizedBox(height: 8),
        Wrap(spacing: 16, runSpacing: 12,
          children: cells.map((f) => _fieldCell(f[0]!, f[1]!)).toList()),
        const SizedBox(height: 20),
      ]);
    }

    return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      section('IDENTITY', [
        ['Year',          data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '')],
        ['Mint Mark',     data[_F.mintMark]?.toString()],
        // Capitalise denomination (e.g. 'penny' > 'Penny', '$1' stays '$1')
        ['Denomination',  _capitalizeDenom(data[_F.denomination]?.toString())],
        ['Country',       data[_F.country]?.toString()],
        ['Series',        data[_F.programSeries]?.toString()],
        ['Theme/Subject', data[_F.themeSubject]?.toString()],
        ['Variety',       data[_F.variety]?.toString()],
        ['Metal',         data[_F.metalContent]?.toString()],
      ]),
      section('CONDITION & AUTHENTICATION', [
        ['Condition',    data[_F.condition]?.toString()],
        ['Strike Type',  data[_F.strikeType]?.toString()],
        ['Holder',       data[_F.holderType]?.toString()],
        ['Grading Svc',  data[_F.gradingService]?.toString()],
        ['Cert #',       data[_F.gradingCert]?.toString()],
        ['PCGS #',       data[_F.pcgsNumber]?.toString()],
        ['Population',   data[_F.population]?.toString()],
      ]),
      section('PURCHASE & STORAGE', [
        // Format cost as currency ($XX.XX)
        ['Cost',        _formatCost(data[_F.cost]?.toString())],
        ['Date',        data[_F.purchaseDate]?.toString()],
        ['Retailer',    data[_F.retailer]?.toString()],
        ['Item #',      data[_F.retailerItemNo]?.toString()],
        ['Invoice #',   data[_F.retailerInvoice]?.toString()],
        ['Storage',     data[_F.storageLocation]?.toString()],
        ['Ref #',       data[_F.personalRef]?.toString()],
        ['Notes',       data[_F.personalNotes]?.toString()],
      ]),
    ]);
  }

  /// Format a raw cost string as USD currency.
  /// Handles: '25', '25.00', '$25.00', '$25', ''
  String? _formatCost(String? raw) {
    if (raw == null || raw.trim().isEmpty || raw == 'null') return null;
    if (raw.startsWith(r'$')) return raw; // already formatted
    final n = double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), ''));
    if (n == null) return raw;
    return '\$${n.toStringAsFixed(2)}';
  }

  /// Capitalise the first letter of a denomination string.
  /// e.g. 'penny' > 'Penny', '$1' > '$1' (unchanged).
  String? _capitalizeDenom(String? raw) {
    if (raw == null || raw.trim().isEmpty) return null;
    final t = raw.trim();
    if (t.startsWith(r'$') || t.startsWith(r'0')) return t; // currency / number: leave as-is
    return t[0].toUpperCase() + t.substring(1);
  }

  Widget _fieldCell(String label, String value) => SizedBox(
    width: 160,
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: const TextStyle(fontSize: 10, color: _subtext)),
      const SizedBox(height: 2),
      Text(value, style: const TextStyle(fontSize: 13, color: _text, fontWeight: FontWeight.w500)),
    ]),
  );

  // _metric removed — replaced by _metricCard (the used variant with accent+icon)

  // --- Dropdown helper -----------------------------------------------------
  Widget _styledDropdown<T>({
    required T value,
    required List<T> items,
    required String Function(T) label,
    required ValueChanged<T?> onChanged,
  }) =>
      Container(
        height: 44,
        padding: const EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
            color: _bg, borderRadius: BorderRadius.circular(4)),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<T>(
            value: value,
            isExpanded: true,
            icon: const Icon(Icons.keyboard_arrow_down, color: _text),
            items: items
                .map((v) => DropdownMenuItem<T>(
                    value: v,
                    child: Text(label(v),
                        style: const TextStyle(color: _text, fontSize: 14))))
                .toList(),
            onChanged: onChanged,
          ),
        ),
      );

  // --- Actions -------------------------------------------------------------

  /// Opens an edit dialog pre-populated with all editable fields for this coin.
  void _onEdit(String id, Map<String, dynamic> data) {
    final fieldKeys = [
      _F.year, _F.mintMark, _F.denomination, _F.programSeries,
      _F.themeSubject, _F.variety, _F.condition, _F.holderType,
      _F.gradingService, _F.gradingCert, _F.metalContent, _F.cost,
      _F.purchaseDate, _F.retailerItemNo, _F.retailerInvoice,
      _F.storageLocation, _F.personalNotes, _F.personalRef,
    ];
    const fieldLabels = [
      'Year', 'Mint Mark', 'Denomination', 'Program/Series',
      'Theme/Subject', 'Variety', 'Condition', 'Holder Type',
      'Grading Service', 'Cert #', 'Metal Content', 'Cost',
      'Purchase Date', 'Item #', 'Invoice #',
      'Storage Location', 'Personal Notes', 'Personal Ref #',
    ];
    final controllers = {
      for (final f in fieldKeys)
        f: TextEditingController(text: data[f]?.toString() ?? '')
    };
    final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final mint  = data[_F.mintMark]?.toString() ?? '';
    final denom = data[_F.denomination]?.toString() ?? '';
    final coinLabel = [year, if (mint.isNotEmpty) mint, denom]
        .where((s) => s.isNotEmpty).join(' ');

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text('Edit -- $coinLabel'),
        content: SizedBox(
          width: 520,
          height: 500,
          child: SingleChildScrollView(
            child: Wrap(
              spacing: 12, runSpacing: 12,
              children: List.generate(fieldKeys.length, (i) => SizedBox(
                width: 240,
                child: TextField(
                  controller: controllers[fieldKeys[i]],
                  decoration: InputDecoration(
                    labelText: fieldLabels[i],
                    border: const OutlineInputBorder(),
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(
                        horizontal: 10, vertical: 10),
                  ),
                  style: const TextStyle(fontSize: 13),
                ),
              )),
            ),
          ),
        ),
        actions: [
          TextButton(
              onPressed: () {
                for (final c in controllers.values) { c.dispose(); }
                Navigator.pop(ctx);
              },
              child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
                backgroundColor: _accent, foregroundColor: Colors.white),
            onPressed: () async {
              final updates = <String, dynamic>{
                for (final f in fieldKeys)
                  if ((controllers[f]?.text.trim() ?? '').isNotEmpty)
                    f: controllers[f]!.text.trim()
              };
              try {
                // set(merge:true) treats map keys as literal field names --
                // unlike update() which interprets '/' as a subcollection
                // separator, breaking fields like 'Program/Series'.
                await FirebaseFirestore.instance
                    .collection(AuthService.coinsPath)
                    .doc(id)
                    .set(updates, SetOptions(merge: true));
                for (final c in controllers.values) { c.dispose(); }
                if (ctx.mounted) Navigator.pop(ctx);
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                      content: Text('Coin updated.'),
                      backgroundColor: _green));
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text('Save failed: $e'),
                      backgroundColor: _red,
                      duration: const Duration(seconds: 6)));
                }
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _onDeepDive(String id, Map<String, dynamic> data) {
    final year   = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final mint   = data[_F.mintMark]?.toString() ?? '';
    final series = data[_F.programSeries]?.toString() ?? '';
    final denom  = data[_F.denomination]?.toString() ?? '';
    final condition = data[_F.condition]?.toString() ?? '';

    // Build a descriptive coin name for the AI query
    final coinDesc = [
      if (year.isNotEmpty) year,
      if (mint.isNotEmpty) mint,
      if (series.isNotEmpty) series else if (denom.isNotEmpty) denom,
      if (condition.isNotEmpty && condition != 'Ungraded') condition,
    ].join(' ');

    final query = 'Tell me about the $coinDesc in my collection: '
        'its history, current market value, key varieties or errors I should '
        'look for, and any tips for a collector.';

    if (widget.onNavigateWithQuery != null) {
      widget.onNavigateWithQuery!('AI Deepdive', query);
    } else if (widget.onNavigate != null) {
      widget.onNavigate!('AI Deepdive');
    }
  }

  void _onDelete(String id, Map<String, dynamic> data) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Delete Coin'),
        content: Text('Remove ${_yearMint(data)} '
            '${data[_F.denomination] ?? ''} from your collection?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: const Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
                backgroundColor: _red, foregroundColor: Colors.white),
            onPressed: () async {
              Navigator.pop(ctx);
              // Show snackbar IMMEDIATELY -- don't wait for Firestore round-trip
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                    content: Text('Coin deleted.'),
                    backgroundColor: _red,
                    duration: Duration(seconds: 2)));
                setState(() => _selectedCoinId = null);
              }
              // Delete runs in background after UI has already updated
              FirebaseFirestore.instance
                  .collection(AuthService.coinsPath)
                  .doc(id)
                  .delete();
            },
            child: const Text('Delete'),
          ),
        ],
      ),
    );
  }

  Future<void> _onCheckEbay(Map<String, dynamic> data) async {
    final coin = CoinModel.fromMap(data, _selectedCoinId!);
    setState(() {});
    
    try {
      final results = await EpnService.fetchEbayResults(coin);
      if (results.isNotEmpty) {
        final price = results.first['price']['value'];
        final currency = results.first['price']['currency'];
        setState(() {
          _ebayPrices[_selectedCoinId!] = '$currency $price';
        });
      } else {
        setState(() {
          _ebayPrices[_selectedCoinId!] = 'No Results';
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('eBay Check Failed: $e'), backgroundColor: _red));
      }
    } finally {
      if (mounted) setState(() {});
    }
  }

  void _onSearchGoogle(Map<String, dynamic> data) async {
    final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
    final mint  = data[_F.mintMark]?.toString() ?? '';
    final denom = data[_F.denomination]?.toString() ?? '';
    final query = Uri.encodeComponent('$year${mint.isNotEmpty ? '-$mint' : ''} $denom coin value'.trim());
    final uri = Uri.parse('https://www.google.com/search?tbm=isch&q=$query');
    try {
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Could not open browser.'), backgroundColor: _red));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Couldn\'t open the browser. Please try again.'), backgroundColor: _red));
      }
    }
  }

  /// Opens eBay SOLD listings in the browser using an EPN affiliate link
  /// so Numista.AI earns commission on any resulting purchase.
  void _onSearchEbay(Map<String, dynamic> data) async {
    try {
      final coin = CoinModel.fromMap(data, _selectedCoinId ?? '');
      final url  = await EpnService.generateSearchUrl(coin, soldOnly: true);
      final uri  = Uri.parse(url);
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
            content: Text('Could not open eBay.'), backgroundColor: _red));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
          content: Text('Couldn\'t open eBay. Please try again.'), backgroundColor: _red));
      }
    }
  }

  // _onAddToWishlist removed — wishlist action now lives in CoinDetailScreen.

  void _onGenerateReport() {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text('AI Report generation -- coming in Phase 3'),
      backgroundColor: _accent,
    ));
  }

  void _onSaveGridChanges() {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text('All changes saved to Firestore.'),
      backgroundColor: _green,
    ));
  }

  // --- Coin Vault Gallery state ---------------------------------------------
  bool _vaultShowObverse = true; // true = obverse, false = reverse

  // --- Coin Vault Gallery widget --------------------------------------------
  /// Replaces the old upload-zone pair with a premium personal scan gallery.
  /// Shows the user's microscope photo with a 📷 YOUR SCAN badge when present,
  /// or an inviting "Add Your Photo" prompt otherwise.
  // ignore: unused_element — kept for CoinDetailScreen integration (Phase 2)
  Widget _buildCoinVaultGallery(Map<String, dynamic> data) {
    final obvUrl = data[_F.imageObverse]?.toString() ?? '';
    final revUrl = data[_F.imageReverse]?.toString() ?? '';
    final hasObv = obvUrl.isNotEmpty && obvUrl.startsWith('http');
    final hasRev = revUrl.isNotEmpty && revUrl.startsWith('http');
    final hasAny = hasObv || hasRev;

    // If switching to reverse but no reverse exists, stay on obverse
    final showObverse = _vaultShowObverse || (!hasRev && hasObv);
    final activeUrl   = showObverse ? obvUrl : revUrl;
    final hasActive   = showObverse ? hasObv : hasRev;

    final scanSource   = data['scan_source']?.toString();
    final isMicroscope = scanSource == 'microscope';

    // When no user photo exists, try to fetch a reference image from GCS index
    if (!hasAny) {
      final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
      final mint  = data[_F.mintMark]?.toString().trim() ?? '';
      final denom = data[_F.denomination]?.toString() ?? '';
      final series = data[_F.programSeries]?.toString() ?? '';

      return FutureBuilder<CoinImageResult>(
        future: CoinImageService.fetchReferenceImages(
          year:         year,
          mint:         mint.isEmpty ? null : mint,
          denomination: denom.isEmpty ? null : denom,
          series:       series.isEmpty ? null : series,
          subject:      (data[_F.themeSubject]?.toString() ?? '').isEmpty
              ? null
              : data[_F.themeSubject]?.toString(),
        ),
        builder: (context, snap) {
          final ref = snap.data;
          final refObvUrl = ref?.obverseUrl ?? '';
          final refRevUrl = ref?.reverseUrl ?? '';
          final hasRefObv = refObvUrl.isNotEmpty;
          final hasRefRev = refRevUrl.isNotEmpty;
          final hasRef    = hasRefObv || hasRefRev;
          final refUrl    = _vaultShowObverse
              ? (hasRefObv ? refObvUrl : refRevUrl)
              : (hasRefRev ? refRevUrl : refObvUrl);
          final hasRefActive = refUrl.isNotEmpty;

          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // -- Header row -------------------------------------------------
              Row(
                children: [
                  if (hasRef) ...[
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFF1A237E).withAlpha(25),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                            color: const Color(0xFF1A237E), width: 1),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.collections_outlined,
                              size: 12, color: Color(0xFF1A237E)),
                          SizedBox(width: 4),
                          Text('REFERENCE IMAGE',
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: Color(0xFF1A237E),
                                letterSpacing: 0.8,
                              )),
                        ],
                      ),
                    ),
                    const Spacer(),
                    _vaultToggleButton('Obverse', _vaultShowObverse,
                        hasRefObv, () {
                      setState(() => _vaultShowObverse = true);
                    }),
                    const SizedBox(width: 6),
                    _vaultToggleButton('Reverse', !_vaultShowObverse,
                        hasRefRev, () {
                      setState(() => _vaultShowObverse = false);
                    }),
                  ] else ...[
                    const Icon(Icons.add_photo_alternate_outlined,
                        size: 14, color: _subtext),
                    const SizedBox(width: 6),
                    Text('Personal Coin Photos',
                        style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: _subtext)),
                  ],
                ],
              ),
              const SizedBox(height: 10),

              // -- Image panel ------------------------------------------------
              GestureDetector(
                onTap: hasRefActive
                    ? () => _showImageLightbox(refUrl,
                          label: _vaultShowObverse ? 'Obverse' : 'Reverse',
                          isMicroscope: false)
                    : null,
                child: AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  child: hasRefActive
                      ? ClipRRect(
                          key: ValueKey(refUrl),
                          borderRadius: BorderRadius.circular(8),
                          child: Stack(
                            children: [
                              Image.network(
                                refUrl,
                                width: double.infinity,
                                height: 220,
                                fit: BoxFit.contain,
                                loadingBuilder: (_, child, prog) =>
                                    prog == null
                                        ? child
                                        : Container(
                                            height: 220,
                                            color: const Color(0xFFF0F2F6),
                                            child: const Center(
                                                child:
                                                    CircularProgressIndicator(
                                                        color: _accent,
                                                        strokeWidth: 2)),
                                          ),
                                errorBuilder: (_, _, _) => _vaultPlaceholder(
                                    _vaultShowObverse ? 'Obverse' : 'Reverse',
                                    isError: true),
                              ),
                              Positioned(
                                bottom: 8, right: 8,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 6, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: Colors.black54,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: const Row(
                                    mainAxisSize: MainAxisSize.min,
                                    children: [
                                      Icon(Icons.zoom_in,
                                          size: 12, color: Colors.white),
                                      SizedBox(width: 3),
                                      Text('Enlarge',
                                          style: TextStyle(
                                              fontSize: 10,
                                              color: Colors.white)),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        )
                      : snap.connectionState == ConnectionState.waiting
                          ? Container(
                              height: 220,
                              decoration: BoxDecoration(
                                color: const Color(0xFFF0F2F6),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: const Center(
                                  child: CircularProgressIndicator(
                                      color: _accent, strokeWidth: 2)),
                            )
                          : _vaultPlaceholder(
                              _vaultShowObverse ? 'Obverse' : 'Reverse'),
                ),
              ),

              // Attribution caption
              if (hasRef && ref!.attribution != null &&
                  ref.attribution!.isNotEmpty) ...[
                const SizedBox(height: 6),
                Text(
                  ref.attribution!,
                  style: const TextStyle(
                      fontSize: 9,
                      color: _subtext,
                      fontStyle: FontStyle.italic),
                ),
              ],

              const SizedBox(height: 10),

              // -- Upload buttons ----------------------------------------------
              Row(
                children: [
                  Expanded(
                    child: _vaultUploadButton(
                      label: '+ Add My Photo',
                      icon: Icons.add_photo_alternate_outlined,
                      progress: _uploadProgressObverse,
                      onTap: () => _onUploadVaultImage(
                        side: 'obverse',
                        field: _F.imageObverse,
                        setProgress: (p) =>
                            setState(() => _uploadProgressObverse = p),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: _vaultUploadButton(
                      label: '+ Add Reverse',
                      icon: Icons.add_photo_alternate_outlined,
                      progress: _uploadProgressReverse,
                      onTap: () => _onUploadVaultImage(
                        side: 'reverse',
                        field: _F.imageReverse,
                        setProgress: (p) =>
                            setState(() => _uploadProgressReverse = p),
                      ),
                    ),
                  ),
                ],
              ),
            ],
          );
        },
      );
    }

    // -- User has their own photo -- show it ------------------------------------
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Container(
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: isMicroscope
                    ? const Color(0xFFFFC107).withAlpha(30)
                    : _accent.withAlpha(30),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                    color: isMicroscope
                        ? const Color(0xFFFFC107)
                        : _accent,
                    width: 1),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    isMicroscope
                        ? Icons.camera_alt
                        : Icons.photo_outlined,
                    size: 12,
                    color: isMicroscope
                        ? const Color(0xFFFFC107)
                        : _accent,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    isMicroscope ? 'YOUR SCAN' : 'YOUR PHOTO',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: isMicroscope
                          ? const Color(0xFFFFC107)
                          : _accent,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
            ),
            const Spacer(),
            _vaultToggleButton('Obverse', _vaultShowObverse, hasObv, () {
              setState(() => _vaultShowObverse = true);
            }),
            const SizedBox(width: 6),
            _vaultToggleButton('Reverse', !_vaultShowObverse, hasRev, () {
              setState(() => _vaultShowObverse = false);
            }),
          ],
        ),
        const SizedBox(height: 10),

        GestureDetector(
          onTap: hasActive
              ? () => _showImageLightbox(activeUrl,
                    label: showObverse ? 'Obverse' : 'Reverse',
                    isMicroscope: isMicroscope)
              : null,
          child: AnimatedSwitcher(
            duration: const Duration(milliseconds: 300),
            child: hasActive
                ? ClipRRect(
                    key: ValueKey(activeUrl),
                    borderRadius: BorderRadius.circular(8),
                    child: Stack(
                      children: [
                        Image.network(
                          activeUrl,
                          width: double.infinity,
                          height: 220,
                          fit: BoxFit.cover,
                          loadingBuilder: (_, child, prog) => prog == null
                              ? child
                              : Container(
                                  height: 220,
                                  color: const Color(0xFFF0F2F6),
                                  child: const Center(
                                      child: CircularProgressIndicator(
                                          color: _accent, strokeWidth: 2)),
                                ),
                          errorBuilder: (_, _, _) => _vaultPlaceholder(
                              showObverse ? 'Obverse' : 'Reverse',
                              isError: true),
                        ),
                        Positioned(
                          bottom: 8,
                          right: 8,
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 3),
                            decoration: BoxDecoration(
                              color: Colors.black54,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.zoom_in,
                                    size: 12, color: Colors.white),
                                SizedBox(width: 3),
                                Text('Enlarge',
                                    style: TextStyle(
                                        fontSize: 10, color: Colors.white)),
                              ],
                            ),
                          ),
                        ),
                      ],
                    ),
                  )
                : _vaultPlaceholder(showObverse ? 'Obverse' : 'Reverse'),
          ),
        ),

        const SizedBox(height: 10),

        Row(
          children: [
            Expanded(
              child: _vaultUploadButton(
                label: hasObv ? 'Replace Obverse' : '+ Obverse',
                icon: hasObv
                    ? Icons.refresh
                    : Icons.add_photo_alternate_outlined,
                progress: _uploadProgressObverse,
                onTap: () => _onUploadVaultImage(
                  side: 'obverse',
                  field: _F.imageObverse,
                  setProgress: (p) =>
                      setState(() => _uploadProgressObverse = p),
                ),
              ),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: _vaultUploadButton(
                label: hasRev ? 'Replace Reverse' : '+ Reverse',
                icon: hasRev
                    ? Icons.refresh
                    : Icons.add_photo_alternate_outlined,
                progress: _uploadProgressReverse,
                onTap: () => _onUploadVaultImage(
                  side: 'reverse',
                  field: _F.imageReverse,
                  setProgress: (p) =>
                      setState(() => _uploadProgressReverse = p),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }


  Widget _vaultToggleButton(
      String label, bool active, bool hasImage, VoidCallback onTap) {
    return GestureDetector(
      onTap: hasImage ? onTap : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
        decoration: BoxDecoration(
          color: active ? _accent : Colors.transparent,
          borderRadius: BorderRadius.circular(4),
          border: Border.all(color: active ? _accent : _border),
        ),
        child: Text(
          label,
          style: TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: active ? Colors.white : (hasImage ? _subtext : _border),
          ),
        ),
      ),
    );
  }

  Widget _vaultPlaceholder(String side, {bool isError = false}) {
    return Container(
      key: ValueKey('placeholder_$side'),
      height: 220,
      width: double.infinity,
      decoration: BoxDecoration(
        color: const Color(0xFFF0F2F6),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
            color: isError ? _red.withAlpha(80) : _border, width: 1.5),
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            isError ? Icons.broken_image_outlined : Icons.add_photo_alternate_outlined,
            size: 40,
            color: isError ? _red.withAlpha(120) : _border,
          ),
          const SizedBox(height: 8),
          Text(
            isError ? 'Image unavailable' : 'No $side photo yet',
            style: TextStyle(
                fontSize: 12,
                color: isError ? _red.withAlpha(160) : _subtext),
          ),
          if (!isError) ...[
            const SizedBox(height: 4),
            Text(
              'Use the button below to upload',
              style: TextStyle(fontSize: 10, color: _subtext.withAlpha(160)),
            ),
          ],
        ],
      ),
    );
  }

  Widget _vaultUploadButton({
    required String label,
    required IconData icon,
    required double? progress,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: progress == null ? onTap : null,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: const Color(0xFFF0F2F6),
          borderRadius: BorderRadius.circular(6),
          border: Border.all(color: _border),
        ),
        child: progress != null
            ? Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  SizedBox(
                    width: 80,
                    child: LinearProgressIndicator(
                      value: progress,
                      backgroundColor: _border,
                      color: _accent,
                      minHeight: 3,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text('${(progress * 100).toInt()}%',
                      style:
                          const TextStyle(fontSize: 10, color: _subtext)),
                ],
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, size: 14, color: _accent),
                  const SizedBox(width: 5),
                  Text(label,
                      style: const TextStyle(
                          fontSize: 11,
                          color: _accent,
                          fontWeight: FontWeight.w600)),
                ],
              ),
      ),
    );
  }

  /// Shows a source picker (camera vs. file) then uploads to Firebase Storage.
  /// Firestore is updated with the download URL under the logged-in user's path.
  Future<void> _onUploadVaultImage({
    required String side,        // 'obverse' | 'reverse'
    required String field,       // Firestore field name
    required void Function(double?) setProgress,
  }) async {
    if (_selectedCoinId == null) return;

    Uint8List? bytes;
    String ext = 'jpg';

    // On mobile: offer camera vs gallery; on web: use file picker directly.
    final bool isMobile = !identical(0, 0.0) ? false : (Theme.of(context).platform == TargetPlatform.android || Theme.of(context).platform == TargetPlatform.iOS);

    if (isMobile) {
      final source = await showModalBottomSheet<ImageSource>(
        context: context,
        shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
        builder: (_) => SafeArea(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            const SizedBox(height: 8),
            Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 16),
            ListTile(leading: const Icon(Icons.camera_alt, color: Color(0xFFF63366)), title: const Text('Take Photo'), onTap: () => Navigator.pop(context, ImageSource.camera)),
            ListTile(leading: const Icon(Icons.photo_library, color: Color(0xFF4C8CDA)),  title: const Text('Choose from Gallery'), onTap: () => Navigator.pop(context, ImageSource.gallery)),
            const SizedBox(height: 8),
          ]),
        ),
      );
      if (source == null) return;
      final picked = await ImagePicker().pickImage(source: source, imageQuality: 90, maxWidth: 2000);
      if (picked == null) return;
      bytes = await picked.readAsBytes();
      ext   = picked.path.split('.').last.toLowerCase();
    } else {
      final result = await FilePicker.pickFiles(type: FileType.image, withData: true, allowMultiple: false);
      if (result == null || result.files.isEmpty) return;
      final f = result.files.first;
      bytes = f.bytes;
      if (bytes == null && f.path != null) { bytes = await File(f.path!).readAsBytes(); }
      if (bytes == null) return;
      ext = f.extension?.toLowerCase() ?? 'jpg';
    }

    setProgress(0.0);
    try {
      // Use per-user storage path so data is isolated
      final userEmail = AuthService.userEmail;
      final storagePath = 'users/$userEmail/coins/${_selectedCoinId!}/$side.$ext';
      final ref = FirebaseStorage.instance.ref(storagePath);

      final task = ref.putData(
        bytes,
        SettableMetadata(contentType: 'image/$ext'),
      );

      task.snapshotEvents.listen((snap) {
        final pct = snap.bytesTransferred / (snap.totalBytes == 0 ? 1 : snap.totalBytes);
        setProgress(pct);
      });

      final snap = await task;
      final url  = await snap.ref.getDownloadURL();

      // Use the currently authenticated user's Firestore path
      await FirebaseFirestore.instance
          .collection('users')
          .doc(userEmail)
          .collection('coins')
          .doc(_selectedCoinId!)
          .update({
        field: url,
        'scan_source': 'manual_upload',
        'scan_date': DateTime.now().toIso8601String(),
      });

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('${side[0].toUpperCase()}${side.substring(1)} photo saved!'),
          backgroundColor: _green,
        ));
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Upload failed: $e'),
          backgroundColor: _red,
        ));
      }
    } finally {
      setProgress(null);
    }
  }

  /// Full-screen image lightbox with tap-anywhere-to-close.
  void _showImageLightbox(String url,
      {required String label, bool isMicroscope = false}) {
    showDialog(
      context: context,
      barrierColor: Colors.black87,
      builder: (dialogCtx) => GestureDetector(
        onTap: () => Navigator.pop(dialogCtx),
        child: Dialog(
          backgroundColor: Colors.transparent,
          insetPadding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (isMicroscope)
                    Container(
                      margin: const EdgeInsets.only(bottom: 8),
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFFFFC107).withAlpha(30),
                        borderRadius: BorderRadius.circular(4),
                        border:
                            Border.all(color: const Color(0xFFFFC107)),
                      ),
                      child: const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(Icons.camera_alt,
                              size: 12, color: Color(0xFFFFC107)),
                          SizedBox(width: 4),
                          Text('YOUR MICROSCOPE SCAN',
                              style: TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  color: Color(0xFFFFC107),
                                  letterSpacing: 0.8)),
                        ],
                      ),
                    ),
                ],
              ),
              // Image
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: InteractiveViewer(
                  minScale: 0.8,
                  maxScale: 5.0,
                  child: Image.network(
                    url,
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const Padding(
                      padding: EdgeInsets.all(40),
                      child: Icon(Icons.broken_image_outlined,
                          color: Colors.white30, size: 60),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 12),
              Text('$label  *  Tap anywhere to close',
                  style: const TextStyle(
                      color: Colors.white54, fontSize: 11)),
            ],
          ),
        ),
      ),
    );
  }


  Future<void> _fetchInspectorSimilar(Map<String, dynamic> data) async {
    final denom   = data[_F.denomination]?.toString() ?? '';
    final yearRaw = data[_F.year]?.toString() ?? '';
    final year    = int.tryParse(yearRaw.replaceAll(RegExp(r'\.0$'), ''));
    if (denom.isEmpty) return;

    setState(() {
      _loadingInspectorSimilar = true;
      _inspectorSimilar = [];
    });

    final imgs = await ReferenceLibraryService.fetchSimilar(
        denomination: denom, year: year);
    if (mounted) {
      setState(() {
        _inspectorSimilar = imgs;
        _loadingInspectorSimilar = false;
      });
    }
  }

  // --- Coin Set Viewer section ---------------------------------------------
  // -- Roll banner ----------------------------------------------------------
  /// Shows a compact info strip when the selected coin is part of a roll/batch.
  Widget _buildRollBanner(Map<String, dynamic> data) {
    final rollId   = data['roll_id'] as String?;
    if (rollId == null || rollId.isEmpty) return const SizedBox.shrink();
    final rollType = data['roll_type'] as String? ?? 'roll';
    final typeLabel = switch (rollType) {
      'identical'  => 'Identical Roll',
      'sequential' => 'Sequential Year Roll',
      'lot'        => 'Unopened Lot',
      _            => 'Batch Entry',
    };
    final typeIcon = switch (rollType) {
      'identical'  => Icons.content_copy_outlined,
      'sequential' => Icons.linear_scale_outlined,
      'lot'        => Icons.inventory_2_outlined,
      _            => Icons.currency_exchange,
    };
    const purple = Color(0xFF8B5CF6);
    return Container(
      margin: const EdgeInsets.only(top: 24),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: purple.withAlpha(15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: purple.withAlpha(60)),
      ),
      child: Row(children: [
        Icon(typeIcon, color: purple, size: 18),
        const SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(typeLabel, style: const TextStyle(fontWeight: FontWeight.w700, color: purple, fontSize: 13)),
          Text('Roll ID: $rollId', style: TextStyle(color: purple.withAlpha(160), fontSize: 11)),
        ])),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: purple),
          onPressed: () => setState(() => _searchQuery = rollId),
          child: const Text('View All >', style: TextStyle(fontSize: 12)),
        ),
      ]),
    );
  }

  // Shown in the inspector whenever the selected coin has a 'set_id' field
  // (populated by the ingestion pipeline). Falls back silently if not a set.
  Widget _buildCoinSetSection(Map<String, dynamic> data) {
    final setId = data['set_id'] as String?;
    if (setId == null || setId.isEmpty) return const SizedBox.shrink();

    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 16, 0, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(color: _border),
          const SizedBox(height: 16),
          CoinSetViewer(setId: setId),
        ],
      ),
    );
  }

  // --- Similar Coins widget for the inspector ------------------------------
  Widget _buildSimilarCoinsInspector() {
    if (!_loadingInspectorSimilar && _inspectorSimilar.isEmpty) {
      return const SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 24),
        const Divider(color: _border),
        const SizedBox(height: 16),
        Row(
          children: [
            const Icon(Icons.photo_library_outlined, color: _accent, size: 16),
            const SizedBox(width: 8),
            const Text(
              'Similar in Reference Library',
              style: TextStyle(
                  color: _text,
                  fontSize: 14,
                  fontWeight: FontWeight.w600),
            ),
            if (_loadingInspectorSimilar) ...[
              const SizedBox(width: 12),
              const SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(
                    color: _accent, strokeWidth: 2),
              ),
            ],
          ],
        ),
        const SizedBox(height: 12),
        if (!_loadingInspectorSimilar && _inspectorSimilar.isNotEmpty)
          SizedBox(
            height: 120,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _inspectorSimilar.length,
              separatorBuilder: (_, _) => const SizedBox(width: 10),
              itemBuilder: (ctx, i) {
                final img = _inspectorSimilar[i];
                return GestureDetector(
                  onTap: () => _showRefImageDialog(ctx, img),
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(6),
                    child: Container(
                      width: 100,
                      color: _bg,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.network(
                            img.gcsUrl,
                            fit: BoxFit.cover,
                            errorBuilder: (_, _, _) => const Icon(
                                Icons.broken_image_outlined,
                                color: _subtext,
                                size: 28),
                          ),
                          if (img.year != null && img.year!.isNotEmpty &&
                              img.year != 'Unknown')
                            Positioned(
                              bottom: 0,
                              left: 0,
                              right: 0,
                              child: Container(
                                padding: const EdgeInsets.symmetric(
                                    vertical: 2, horizontal: 4),
                                color: Colors.black54,
                                child: Text(
                                  img.year!,
                                  style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold),
                                  textAlign: TextAlign.center,
                                ),
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
          ),
        const SizedBox(height: 4),
        Text(
          'Tap to expand  *  Kaggle reference datasets',
          style: TextStyle(fontSize: 10, color: _subtext.withAlpha(160),
              fontStyle: FontStyle.italic),
        ),
      ],
    );
  }

  void _showRefImageDialog(BuildContext ctx, ReferenceImage img) {
    showDialog(
      context: ctx,
      builder: (_) => Dialog(
        insetPadding: const EdgeInsets.all(24),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ConstrainedBox(
                constraints: const BoxConstraints(maxHeight: 380),
                child: Image.network(
                  img.gcsUrl,
                  fit: BoxFit.contain,
                  errorBuilder: (_, _, _) => const Padding(
                    padding: EdgeInsets.all(40),
                    child: Icon(Icons.broken_image_outlined,
                        color: _subtext, size: 56),
                  ),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(16),
                child: Text(img.caption,
                    style: const TextStyle(fontSize: 12, color: _subtext)),
              ),
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Close'),
              ),
              const SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}
