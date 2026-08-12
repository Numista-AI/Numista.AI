import 'dart:io' show File;
import 'dart:async';
import 'package:intl/intl.dart' as intl;
import 'package:two_dimensional_scrollables/two_dimensional_scrollables.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:firebase_storage/firebase_storage.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/valuation_mode_service.dart';
import 'currency_collection_screen.dart';
import '../services/world_item_service.dart';
import '../services/auth_service.dart';
import '../models/coin_model.dart';
import '../services/epn_service.dart';
import '../services/guest_seed_service.dart';
import '../services/reference_library_service.dart';
import '../services/coin_image_service.dart';
import '../widgets/coin_set_viewer.dart';
import '../widgets/set_contents_panel.dart';
import '../widgets/grade_badge_widget.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import '../services/melt_value_service.dart';
import '../services/batch_valuation_service.dart';
import '../services/photo_sharing_service.dart';
import '../services/estate_report_service.dart';
import '../models/estate_models.dart';
import 'coin_detail_screen.dart';
import '../widgets/morgan_guide_flow.dart'; // Morgan guide step advancement
import '../constants.dart';

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
  final String? initialTab;
  final Function(String)? onNavigate;
  /// Navigate to a screen AND pass an initial query (used for AI Deep Dive).
  final Function(String route, String query)? onNavigateWithQuery;
  final Function(String)? onTabChanged;
  const MyCollectionScreen({super.key, this.initialTab, this.onNavigate, this.onNavigateWithQuery, this.onTabChanged});
  @override
  State<MyCollectionScreen> createState() => _MyCollectionScreenState();
}

class _MyCollectionScreenState extends State<MyCollectionScreen> {

  // --- UI / filter state ---------------------------------------------------
  String _currentTab = 'All';
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
  bool    _isCardView = false;

  final _searchCtrl      = TextEditingController();
  final _searchFocus     = FocusNode();
  Timer? _searchDebounce;
  // Firestore stream -- created ONCE in initState to prevent StreamBuilder
  // re-subscription on every setState (which briefly unmounts the TextField
  // and causes focus loss on Flutter Web).
  late Stream<QuerySnapshot<Map<String, dynamic>>> _coinsStream;
  
  // ── Batch valuation progress ────────────────────────────────────────────────
  BatchValuationProgress _valuation = BatchValuationProgress();
  StreamSubscription<BatchValuationProgress>? _valuationSub;

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


  // --- Coin origin filter state ('All', 'U.S.', 'World') ------------------
  String _coinOriginFilter = 'All';

  // --- Live spot prices (fetched once on mount, same endpoint as dashboard) --
  Map<String, double> _spotPrices = {};
  Map<String, dynamic> _completionStats = {};
  bool _isLoadingCompletion = true;

  Future<void> _fetchSpotPrices() async {
    try {
      final resp = await http.get(Uri.parse(
          '$kApiBaseUrl/api/spot_prices'));
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

  Future<void> _fetchCompletionStats() async {
    try {
      final userEmail = AuthService.userEmail;
      if (userEmail.isEmpty) return;
      
      final response = await http.get(
        Uri.parse('$kApiBaseUrl/api/collection/completion_stats?user_email=$userEmail')
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _completionStats = data;
          _isLoadingCompletion = false;
        });
      } else {
        if (!mounted) return;
        setState(() => _isLoadingCompletion = false);
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoadingCompletion = false);
    }
  }

  // --- Colours (match dynamic dark/light brightness toggle) ----------------
  Color get _bg => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
  Color get _surface => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF1E2937) : Colors.white;
  Color get _text => Theme.of(context).brightness == Brightness.dark ? const Color(0xFFE8EAF0) : const Color(0xFF0F172A);
  Color get _subtext => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF8B92B4) : const Color(0xFF5A5C69);
  Color get _border => Theme.of(context).brightness == Brightness.dark ? const Color(0xFF2D3143) : const Color(0xFFE2E8F0);
  Color get _accent => Theme.of(context).brightness == Brightness.dark ? const Color(0xFFC9A227) : const Color(0xFF8C7355);

  static const _green     = Color(0xFF28A745);
  static const _greenBg   = Color(0xFFD4EED8);
  static const _greenText = Color(0xFF155724);
  static const _red       = Color(0xFFDC3545);

  // --- Column definitions -------------------------------------------------------
  // AI Value sits right after Condition so it is visible without scrolling.
  // Metal and Melt Value moved right (after Cost) since they are reference data
  // that collectors check less frequently than the estimated value.
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
    _ColDef(_F.gradingService,   'Service',        90),
    _ColDef(_F.gradingCert,      'Cert #',        120),
    _ColDef(_F.aiValue,          'AI Value',      100), // moved left — visible on load
    _ColDef(_F.cost,             'Cost',           90),
    _ColDef(_F.isSilver,         'Metal',          62), // moved right
    _ColDef(_F.meltValue,        'Melt Value',     80), // moved right
    _ColDef(_F.pcgsNumber,       'PCGS #',         80),
    _ColDef(_F.purchaseDate,     'Date',           80),
    _ColDef(_F.retailerItemNo,   'Item #',         80),
    _ColDef(_F.retailerInvoice,  'Invoice #',      90),
    _ColDef(_F.storageLocation,  'Location',      100),
  ];

  /// Currency formatter shared across all cost/value cells.
  static final _currencyFmt =
      intl.NumberFormat.currency(symbol: r'$', decimalDigits: 2);

  // --- Lifecycle -----------------------------------------------------------
  @override
  void initState() {
    super.initState();
    _loadDefaultTab();
    // Create the Firestore stream ONCE -- reusing it in build() ensures
    // StreamBuilder never re-subscribes on setState, so the TextField
    // keeps its focus between keystrokes on Flutter Web.
    _coinsStream = _buildCoinsStream();

    // Listen to batch valuation progress for the live badge in _buildFiltersRow
    _valuationSub = BatchValuationService.instance.progressStream.listen((p) {
      if (mounted) setState(() => _valuation = p);
    });
    _valuation = BatchValuationService.instance.current;
    // Restore persisted progress so AI Valuation badge appears after page refresh
    BatchValuationService.instance.restoreFromFirestore();

    _fetchSpotPrices();
    _fetchCompletionStats();
    // Debounced search: 150ms after last keystroke before applying filter.
    // Short enough to feel instant; long enough to avoid per-character rebuilds.
    _searchCtrl.addListener(() {
      _searchDebounce?.cancel();
      _searchDebounce = Timer(Duration(milliseconds: 150), () {
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

  void _loadDefaultTab() async {
    final prefs = await SharedPreferences.getInstance();
    final savedTab = prefs.getString('my_collection_default_tab');
    if (mounted) {
      setState(() {
        _currentTab = widget.initialTab ?? savedTab ?? 'All';
      });
      if (widget.onTabChanged != null) {
        widget.onTabChanged!(_currentTab);
      }
    }
  }

  void _onTabChanged(String tab) async {
    setState(() {
      _currentTab = tab;
    });
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('my_collection_default_tab', tab);
    if (widget.onTabChanged != null) {
      widget.onTabChanged!(tab);
    }
  }

  @override
  void didUpdateWidget(MyCollectionScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialTab != null && widget.initialTab != oldWidget.initialTab) {
      setState(() {
        _currentTab = widget.initialTab!;
      });
      if (widget.onTabChanged != null) {
        widget.onTabChanged!(_currentTab);
      }
    }
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
    if (GuestSeedService.isBrowseDemoMode) {
      return GuestSeedService.getDemoCoinsStream();
    }
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
    _valuationSub?.cancel();
    super.dispose();
  }

  // --- Sort + filter helpers -----------------------------------------------
  // ---------------------------------------------------------------------------
  // _sortKey — returns a Comparable that represents the column's logical sort
  // order for a single coin data map.  This mirrors _getCellValue logic so that
  // the sort order always matches what the user *sees* in the cell.
  // ---------------------------------------------------------------------------
  Comparable _sortKey(String field, Map<String, dynamic> m) {
    switch (field) {
      // ── AI Value ────────────────────────────────────────────────────────────
      // Display logic (in _getCellValue) prefers greysheetBid / cpgRetail over
      // the raw AI Estimated Value string.  Sort must use the same hierarchy.
      case _F.aiValue:
        final cpg = _parseNumber(m['cpgRetail']);
        final bid = _parseNumber(m['greysheetBid']);
        // CPG Retail is the collector/market price (default); bid is dealer-wholesale (advanced)
        final gVal = cpg > 0 ? cpg : bid;
        if (gVal > 0) return gVal;
        final av = m[_F.aiValue]?.toString() ?? '';
        return _parseAiValue(av); // strips ~, $, commas → double (0 if empty)

      // ── Condition ──────────────────────────────────────────────────────────
      // Sort by Sheldon numeric grade (0–70) so grades appear in proper order.
      // Blank / unknown values sort last (use -1 so they sink to the bottom
      // when ascending, which is more useful than floating to the top).
      case _F.condition:
        final raw = m[_F.condition]?.toString().trim() ?? '';
        return _conditionToGrade(raw); // returns double 0–70

      // ── Melt Value ─────────────────────────────────────────────────────────
      // Live value from spot prices if available, otherwise stored string.
      case _F.meltValue:
        if (_spotPrices.isNotEmpty) {
          final lv = MeltValueService.compute(
            metalContent: m[_F.metalContent]?.toString() ?? '',
            denomination: m[_F.denomination]?.toString() ?? '',
            spotPrices: _spotPrices,
          );
          return lv ?? 0.0;
        }
        final mv = m[_F.meltValue]?.toString() ?? '';
        return double.tryParse(mv.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;

      // ── Cost ───────────────────────────────────────────────────────────────
      case _F.cost:
        final raw = m[_F.cost]?.toString() ?? '';
        return double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;

      // ── Year ───────────────────────────────────────────────────────────────
      case _F.year:
        final raw = m[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
        return double.tryParse(raw) ?? 0.0;

      // ── Default: plain text (alphabetical) ─────────────────────────────────
      default:
        final v = m[field]?.toString().trim() ?? '';
        return (v == 'null' || v == 'nan') ? '' : v;
    }
  }

  // Converts a raw condition string → Sheldon grade (0–70).
  // Unknown/blank values return -1 so they sort consistently to the bottom.
  static double _conditionToGrade(String raw) {
    if (raw.isEmpty || raw == 'null') return -1;
    final lower = raw.toLowerCase();
    // Text shorthands
    if (lower == 'p-1'   || lower == 'p')    return 1;
    if (lower == 'fr-2'  || lower == 'fr')   return 2;
    if (lower == 'ag-3'  || lower == 'ag')   return 3;
    if (lower == 'g-4')                      return 4;
    if (lower == 'g-6')                      return 6;
    if (lower == 'g-8')                      return 8;
    if (lower == 'vg-10' || lower == 'vg')   return 10;
    if (lower == 'f-12')                     return 12;
    if (lower == 'f-15')                     return 15;
    if (lower == 'vf-20' || lower == 'vf')   return 20;
    if (lower == 'vf-25')                    return 25;
    if (lower == 'vf-30')                    return 30;
    if (lower == 'vf-35')                    return 35;
    if (lower == 'ef-40' || lower == 'xf-40' || lower == 'ef' || lower == 'xf') return 40;
    if (lower == 'ef-45' || lower == 'xf-45') return 45;
    if (lower == 'au-50' || lower == 'au50') return 50;
    if (lower == 'au-55' || lower == 'au55') return 55;
    if (lower == 'au-58' || lower == 'au58') return 58;
    // Circulated shorthand (mid-range estimate: ~25)
    if (lower.contains('circ') && !lower.contains('unc')) return 25;
    // Uncirculated shorthand (≈ MS-60)
    if (lower.contains('unc') || lower.contains('uncirculated')) return 60;
    // Proof (≈ PF-65)
    if (lower.contains('proof')) return 65;
    // MS-xx or PF-xx (e.g. "MS-65", "MS65", "PF-68")
    final msMatch = RegExp(r'(?:ms|pf|pr)[-\s]?(\d{1,2})', caseSensitive: false).firstMatch(lower);
    if (msMatch != null) return double.tryParse(msMatch.group(1)!) ?? 60;
    // Raw numeric Sheldon (stored as integer string)
    final n = double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), ''));
    return n ?? -1;
  }

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

    final field = _columns[_sortColumnIndex].field;
    copy.sort((a, b) {
      final ak = _sortKey(field, a.data() as Map<String, dynamic>);
      final bk = _sortKey(field, b.data() as Map<String, dynamic>);
      // Compare: if both are numeric use numeric comparison, else string
      int cmp;
      if (ak is double && bk is double) {
        cmp = ak.compareTo(bk);
      } else {
        cmp = ak.toString().compareTo(bk.toString());
      }
      return _sortAscending ? cmp : -cmp;
    });
    return copy;
  }


  List<QueryDocumentSnapshot> _filtered(List<QueryDocumentSnapshot> docs) {
    // Option A: individual set-member coins are hidden from the default grid.
    // Only the parent SET card is shown. When actively searching, ALL coins
    // (including set members) are revealed so Morgan/AI never misses them.
    final List<QueryDocumentSnapshot> visible = docs.where((doc) {
      final m = (doc.data() as Map<String, dynamic>?) ?? {};
      if (m.isEmpty) return false;
      final tStatus = m['transferStatus']?.toString() ?? '';
      if (tStatus == 'transferred') return false;
      if (_searchQuery.isNotEmpty) return true;
      final parentSetId = m['parent_set_id']?.toString() ?? '';
      return parentSetId.isEmpty;
    }).toList();

    const usAllowList = {
      'united states', 'usa', 'us', 'united states of america', 'u.s.', 'u.s.a.',
      'united states mint', 'puerto rico', 'guam', 'u.s. virgin islands', 'usvi',
      'american samoa', 'northern mariana islands', 'confederate states', 'csa', 'us philippines'
    };

    final originFiltered = visible.where((doc) {
      if (_coinOriginFilter == 'All') return true;
      final m = (doc.data() as Map<String, dynamic>?) ?? {};
      // Primary boolean check with migration shim fallback for legacy un-patched docs
      final isForeign = (m['is_foreign'] as bool?) ??
          (!usAllowList.contains((m['country'] ?? m['Country'] ?? '').toString().toLowerCase().trim()));

      if (_coinOriginFilter == 'World') return isForeign;
      if (_coinOriginFilter == 'U.S.') return !isForeign;
      return true;
    }).toList();

    if (_searchQuery.isEmpty) return originFiltered;
    return originFiltered.where((doc) {
      final m = (doc.data() as Map<String, dynamic>?) ?? {};
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
        final m = (doc.data() as Map<String, dynamic>?) ?? {};
        final v = m[col.field]?.toString().trim() ?? '';
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
    final email = FirebaseAuth.instance.currentUser?.email ?? '';

    return Scaffold(
      backgroundColor: _bg,
      body: SingleChildScrollView(
        padding: EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header & Segmented Tab Picker
            LayoutBuilder(
              builder: (context, constraints) {
                final isWide = constraints.maxWidth > 800;
                final headerText = Text(
                  'My Collection',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.w900,
                    color: _text,
                  ),
                );
                final picker = MyCollectionSegmentedControl(
                  selectedTab: _currentTab,
                  onTabChanged: _onTabChanged,
                );

                if (isWide) {
                  return Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      headerText,
                      picker,
                    ],
                  );
                } else {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      headerText,
                      SizedBox(height: 12),
                      picker,
                    ],
                  );
                }
              },
            ),
            SizedBox(height: 16),

            // Beta banner
            Container(
              width: double.infinity,
              padding: EdgeInsets.symmetric(vertical: 4, horizontal: 16),
              decoration: BoxDecoration(
                  color: _accent, borderRadius: BorderRadius.circular(4)),
              child: Text('BETA TESTING', style: TextStyle(
                  fontWeight: FontWeight.bold, fontSize: 10,
                  color: Colors.white, letterSpacing: 1.0)),
            ),
            SizedBox(height: 24),

            // Tab View Dispatcher
            _buildTabContent(email),
            SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildTabContent(String email) {
    switch (_currentTab) {
      case 'Coins':
        return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
          stream: _coinsStream,
          builder: (context, snap) {
            if (!snap.hasData && snap.connectionState == ConnectionState.waiting) {
              return Center(child: CircularProgressIndicator(color: _accent));
            }
            if (snap.hasError) {
              return _buildErrorState();
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

            return FutureBuilder<bool>(
              future: ValuationModeService.isAdvancedMode(),
              builder: (context, modeSnap) {
                final advanced = modeSnap.data ?? false;
                return _buildCoinsTab(docs, allDocs, advanced: advanced);
              },
            );
          },
        );
      case 'Currency':
        return CurrencyCollectionScreen(showAppBar: false);
      case 'Non-Legal Tender':
      case 'World & Specialty':
        return _buildWorldItemsTab();
      case 'All':
      default:
        return _buildUnifiedDashboard(email);
    }
  }

  Widget _buildCoinsTab(List<QueryDocumentSnapshot> docs, List<QueryDocumentSnapshot> allDocs, {bool advanced = false}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildFiltersRow(allDocs),
        SizedBox(height: 24),
        Divider(color: _border),
        SizedBox(height: 16),

        _buildStatsRow(docs, advanced: advanced),
        SizedBox(height: 16),

        // Toolbar: origin sub-filter + view toggle + column visibility toggle + AI Report button
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // Origin Sub-Filter Chips (All | U.S. | World)
            Container(
              decoration: BoxDecoration(
                border: Border.all(color: _border),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  _toggleSegment(
                    label: 'All Coins',
                    icon: Icons.public,
                    active: _coinOriginFilter == 'All',
                    onTap: () => setState(() => _coinOriginFilter = 'All'),
                    isLeft: true,
                  ),
                  _toggleSegment(
                    label: 'U.S.',
                    icon: Icons.flag_outlined,
                    active: _coinOriginFilter == 'U.S.',
                    onTap: () => setState(() => _coinOriginFilter = 'U.S.'),
                    isLeft: false,
                  ),
                  _toggleSegment(
                    label: 'World',
                    icon: Icons.language,
                    active: _coinOriginFilter == 'World',
                    onTap: () => setState(() => _coinOriginFilter = 'World'),
                    isLeft: false,
                  ),
                ],
              ),
            ),

            Row(
              children: [
                // Card / Table View Toggle
                Container(
                  decoration: BoxDecoration(
                    border: Border.all(color: _border),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      _toggleSegment(
                        label: 'Table',
                        icon: Icons.table_chart_outlined,
                        active: !_isCardView,
                        onTap: () => setState(() => _isCardView = false),
                        isLeft: true,
                      ),
                      _toggleSegment(
                        label: 'Cards',
                        icon: Icons.grid_view_outlined,
                        active: _isCardView,
                        onTap: () => setState(() => _isCardView = true),
                        isLeft: false,
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 12),
                // Column visibility toggle (only relevant when table is visible)
                if (!_isCardView) ...[
                  _columnToggleButton(),
                  const SizedBox(width: 12),
                  _buildPanButtonsToolbar(),
                  const SizedBox(width: 12),
                ],
                ElevatedButton.icon(
                  onPressed: () => _showGenerateReportModal(),
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
              ],
            ),
          ],
        ),
        const SizedBox(height: 12),

        // Data view -- three distinct states
        if (allDocs.isEmpty)
          _buildCollectionEmptyState()
        else if (docs.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 40),
            child: Center(child: Text('No coins match your filter.',
                style: TextStyle(color: _subtext))))
        else
          SizedBox(
            height: 520,
            child: _isCardView 
                ? _buildCardGrid(docs, advanced: advanced)
                : _buildDataTable(docs, advanced: advanced),
          ),
      ],
    );
  }

  Widget _buildUnifiedDashboard(String email) {
    return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
      stream: _coinsStream,
      builder: (context, coinsSnap) {
        return StreamBuilder<QuerySnapshot<Map<String, dynamic>>>(
          stream: email.isNotEmpty
              ? FirebaseFirestore.instance.collection(AuthService.currencyPath).snapshots()
              : Stream.empty(),
          builder: (context, currencySnap) {
            return StreamBuilder<List<WorldItem>>(
              stream: WorldItemService.worldItemsStream(),
              builder: (context, worldSnap) {
                return FutureBuilder<bool>(
                  future: ValuationModeService.isAdvancedMode(),
                  builder: (context, modeSnap) {
                    final advanced = modeSnap.data ?? false;
                    final coinsDocs = coinsSnap.data?.docs ?? [];
                    final currencyDocs = currencySnap.data?.docs ?? [];
                    final worldDocs = worldSnap.data ?? [];

                    final coinsCount = coinsDocs.length;
                    final currencyCount = currencyDocs.length;
                    final worldCount = worldDocs.length;

                    double coinsValue = 0;
                    for (final doc in coinsDocs) {
                      try {
                        final data = doc.data();
                        final coinCpg = _parseNumber(data['cpgRetail']);
                        final coinBid = _parseNumber(data['greysheetBid']);
                        final gVal = advanced ? coinCpg : coinBid;
                        if (gVal > 0) {
                          coinsValue += gVal;
                        } else {
                          coinsValue += _parseAiValue(data[_F.aiValue]?.toString() ?? '');
                        }
                      } catch (_) {}
                    }

                    double currencyValue = 0;
                    for (final doc in currencyDocs) {
                      try {
                        final data = doc.data();
                        currencyValue += _parseNumber(data['Cost']);
                      } catch (_) {}
                    }

                    double worldValue = 0;
                    for (final item in worldDocs) {
                      worldValue += item.estimatedValue ?? 0.0;
                    }
                    
                    final grandTotalValue = coinsValue + currencyValue + worldValue;

                    // Merge and map for the combined additions feed
                    final coinItems = coinsDocs.map((doc) {
                      final data = doc.data();
                      final addedTs = data['Added'] ?? data['timestamp'] ?? data['created_at'];
                      DateTime? addedDate;
                      if (addedTs is Timestamp) {
                        addedDate = addedTs.toDate();
                      } else if (addedTs is String) {
                        addedDate = DateTime.tryParse(addedTs);
                      }
                      final denom = data['Denomination']?.toString() ?? '';
                      final year = data['Year']?.toString() ?? '';
                      final title = '$year $denom'.trim();

                      final coinCpg = _parseNumber(data['cpgRetail']);
                      final coinBid = _parseNumber(data['greysheetBid']);
                      final gVal = advanced ? coinCpg : coinBid;
                      final displayValue = gVal > 0 
                          ? gVal 
                          : _parseAiValue(data['AI Estimated Value']?.toString() ?? '');

                      return UnifiedCollectionItem(
                        title: title.isNotEmpty ? title : 'Coin',
                        category: 'Coin',
                        emoji: '🪙',
                        country: data['Country']?.toString() ?? 'US',
                        dateAdded: addedDate,
                        value: displayValue,
                      );
                    }).toList();

                    final currencyItems = currencyDocs.map((doc) {
                      final data = doc.data();
                      final addedTs = data['Added'] ?? data['created_at'] ?? data['timestamp'];
                      DateTime? addedDate;
                      if (addedTs is Timestamp) {
                        addedDate = addedTs.toDate();
                      } else if (addedTs is String) {
                        addedDate = DateTime.tryParse(addedTs);
                      }
                      return UnifiedCollectionItem(
                        title: data['Description']?.toString() ?? 'Banknote',
                        category: 'Currency',
                        emoji: '💵',
                        country: data['Country']?.toString() ?? 'US',
                        dateAdded: addedDate,
                        value: _parseNumber(data['Cost']),
                      );
                    }).toList();

                    final worldItems = worldDocs.map((item) {
                      return UnifiedCollectionItem(
                        title: item.name.isNotEmpty ? item.name : 'World Item',
                        category: 'World & Specialty',
                        emoji: item.itemCategory.emoji,
                        country: item.country,
                        dateAdded: item.createdAt,
                        value: item.estimatedValue ?? 0.0,
                      );
                    }).toList();

                    // Combine and sort by date added, newest first
                    final combinedItems = [...coinItems, ...currencyItems, ...worldItems];
                    combinedItems.sort((a, b) {
                      if (a.dateAdded == null && b.dateAdded == null) return 0;
                      if (a.dateAdded == null) return 1;
                      if (b.dateAdded == null) return -1;
                      return b.dateAdded!.compareTo(a.dateAdded!);
                    });

                    // Take top 10
                    final recentAdditions = combinedItems.take(10).toList();

                    return Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Portfolio Stats Grid
                        GridView(
                          shrinkWrap: true,
                          physics: NeverScrollableScrollPhysics(),
                          gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
                            maxCrossAxisExtent: 280,
                            crossAxisSpacing: 16,
                            mainAxisSpacing: 16,
                            childAspectRatio: 2.0,
                          ),
                          children: [
                            _buildDashboardCard(
                              'Total Inventory Value',
                              'ESTIMATED PORTFOLIO VALUE',
                              '\$${grandTotalValue.toStringAsFixed(2)}',
                              'Based on AI, cost, and specialty appraisals',
                              Icons.account_balance_wallet_rounded,
                              _accent,
                            ),
                            _buildDashboardCard(
                              'Coins',
                              'COIN COLLECTION',
                              '$coinsCount Items',
                              'Valued at \$${coinsValue.toStringAsFixed(2)}',
                              Icons.monetization_on_rounded,
                              Colors.amber,
                            ),
                            _buildDashboardCard(
                              'Currency',
                              'PAPER BANKNOTES',
                              '$currencyCount Items',
                              'Valued at \$${currencyValue.toStringAsFixed(2)}',
                              Icons.money_rounded,
                              Colors.green,
                            ),
                            _buildDashboardCard(
                              'Non-Legal Tender',
                              'OTHER ITEMS',
                              '$worldCount Items',
                              'Valued at \$${worldValue.toStringAsFixed(2)}',
                              Icons.language_rounded,
                              Colors.teal,
                            ),
                            _buildCompletionCard(),
                          ],
                        ),
                        SizedBox(height: 32),

                        // Recent Additions Title
                        Text(
                          'Recent Additions (${combinedItems.length} total)',
                          style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: _text,
                          ),
                        ),
                        SizedBox(height: 12),

                        // Combined Feed List
                        if (recentAdditions.isEmpty)
                          Card(
                            color: _surface,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                              side: BorderSide(color: _border),
                            ),
                            child: Padding(
                              padding: EdgeInsets.all(24),
                              child: Center(child: Text('No items in your collection yet.')),
                            ),
                          )
                        else
                          ListView.builder(
                            shrinkWrap: true,
                            physics: NeverScrollableScrollPhysics(),
                            itemCount: recentAdditions.length,
                            itemBuilder: (context, index) {
                              final item = recentAdditions[index];
                              return Card(
                                color: _surface,
                                margin: EdgeInsets.symmetric(vertical: 4),
                                shape: RoundedRectangleBorder(
                                  borderRadius: BorderRadius.circular(8),
                                  side: BorderSide(color: _border),
                                ),
                                child: ListTile(
                                  leading: CircleAvatar(
                                    backgroundColor: _bg,
                                    child: Text(item.emoji, style: TextStyle(fontSize: 18)),
                                  ),
                                  title: Text(item.title, style: TextStyle(color: _text, fontWeight: FontWeight.w600)),
                                  subtitle: Text('${item.category} · ${item.country}', style: TextStyle(color: _subtext)),
                                  trailing: Text(
                                    '\$${item.value.toStringAsFixed(2)}',
                                    style: TextStyle(color: Colors.green, fontWeight: FontWeight.bold, fontSize: 13),
                                  ),
                                ),
                              );
                            },
                          ),
                      ],
                    );
                  },
                );
              },
            );
          },
        );
      },
    );
  }

  Widget _buildDashboardCard(String title, String subtitle, String value, String description, IconData icon, Color color) {
    return Card(
      color: _surface,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: _border),
      ),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: color, size: 24),
                Text(subtitle, style: TextStyle(color: _subtext, fontSize: 11)),
              ],
            ),
            SizedBox(height: 10),
            Text(
              value,
              style: TextStyle(
                color: _text,
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            SizedBox(height: 4),
            Text(description, style: TextStyle(color: _subtext, fontSize: 10)),
          ],
        ),
      ),
    );
  }

  Widget _buildCompletionCard() {
    if (_isLoadingCompletion || _completionStats.isEmpty) {
      return Card(
        color: _surface,
        elevation: 2,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: _border),
        ),
        child: Center(
          child: SizedBox(
            width: 20,
            height: 20,
            child: CircularProgressIndicator(strokeWidth: 2, color: _accent),
          ),
        ),
      );
    }

    final pct = _parseNumber(_completionStats['completion_percentage']);
    final owned = _parseNumber(_completionStats['owned_count']).toInt();
    final total = _parseNumber(_completionStats['total_count']).toInt();

    return Card(
      color: _surface,
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: _border),
      ),
      child: InkWell(
        onTap: () => _showCompletionBreakdownBottomSheet(),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Icon(Icons.check_circle_outline, color: _green, size: 24),
                  Text('U.S. CURRENCY COMPLETION', style: TextStyle(color: _subtext, fontSize: 11)),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                crossAxisAlignment: CrossAxisAlignment.baseline,
                textBaseline: TextBaseline.alphabetic,
                children: [
                  Text(
                    '${pct.toStringAsFixed(1)}%',
                    style: TextStyle(
                      color: _text,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    '($owned / $total varieties)',
                    style: TextStyle(
                      color: _subtext,
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Text('Collection coverage across all legal tender', style: TextStyle(color: _subtext, fontSize: 10)),
            ],
          ),
        ),
      ),
    );
  }

  void _showCompletionBreakdownBottomSheet() {
    showModalBottomSheet(
      context: context,
      backgroundColor: _surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) {
        final breakdown = _completionStats['breakdown'] as Map<String, dynamic>? ?? {};
        
        Widget buildRow(String title, String key, IconData icon, Color color) {
          final data = breakdown[key] as Map<String, dynamic>? ?? {};
          final bPct = _parseNumber(data['percentage']);
          final bOwned = _parseNumber(data['owned']).toInt();
          final bTotal = _parseNumber(data['total']).toInt();
          
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withAlpha(30),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: color, size: 18),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(color: _text, fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        'Collected $bOwned of $bTotal varieties',
                        style: TextStyle(color: _subtext, fontSize: 11),
                      ),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${bPct.toStringAsFixed(1)}%',
                      style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                    const SizedBox(height: 4),
                    SizedBox(
                      width: 80,
                      height: 4,
                      child: ClipRRect(
                        borderRadius: BorderRadius.circular(2),
                        child: LinearProgressIndicator(
                          value: bPct / 100,
                          backgroundColor: _border,
                          valueColor: AlwaysStoppedAnimation<Color>(color),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          );
        }

        return Padding(
          padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 36,
                height: 4,
                decoration: BoxDecoration(
                  color: _border,
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
              const SizedBox(height: 16),
              Text(
                'U.S. Legal Tender Breakdown',
                style: TextStyle(color: _text, fontWeight: FontWeight.bold, fontSize: 18),
              ),
              const SizedBox(height: 20),
              buildRow('Coins', 'coin', Icons.circle_outlined, const Color(0xFF2DD4BF)),
              Divider(color: _border),
              buildRow('Banknotes', 'banknote', Icons.wallet_membership_outlined, const Color(0xFF3B82F6)),
              Divider(color: _border),
              buildRow('Medals', 'medal', Icons.military_tech_outlined, const Color(0xFFFFD700)),
            ],
          ),
        );
      },
    );
  }

  Widget _buildWorldItemsTab() {
    return StreamBuilder<List<WorldItem>>(
      stream: WorldItemService.worldItemsStream(),
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return Center(child: CircularProgressIndicator());
        }
        final items = snapshot.data ?? [];
        if (items.isEmpty) {
          return Center(
            child: Padding(
              padding: EdgeInsets.all(40),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.language_rounded, size: 48, color: Colors.grey),
                  SizedBox(height: 16),
                  Text(
                    'No World & Specialty items yet',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: _text),
                  ),
                  SizedBox(height: 8),
                  ElevatedButton(
                    onPressed: () {
                      if (widget.onNavigate != null) {
                        widget.onNavigate!('Add World Item');
                      }
                    },
                    style: ElevatedButton.styleFrom(backgroundColor: _accent),
                    child: Text('Add Your First Item', style: TextStyle(color: Colors.white)),
                  ),
                ],
              ),
            ),
          );
        }
        return Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('${items.length} Items Found', style: TextStyle(color: _subtext, fontSize: 14)),
                ElevatedButton.icon(
                  onPressed: () {
                    if (widget.onNavigate != null) {
                      widget.onNavigate!('Add World Item');
                    }
                  },
                  icon: Icon(Icons.add, size: 16, color: Colors.white),
                  label: Text('Add World Item', style: TextStyle(color: Colors.white)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _accent,
                    padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                ),
              ],
            ),
            SizedBox(height: 16),
            GridView.builder(
              shrinkWrap: true,
              physics: NeverScrollableScrollPhysics(),
              gridDelegate: SliverGridDelegateWithMaxCrossAxisExtent(
                maxCrossAxisExtent: 280,
                crossAxisSpacing: 16,
                mainAxisSpacing: 16,
                childAspectRatio: 0.8,
              ),
              itemCount: items.length,
              itemBuilder: (context, index) {
                final item = items[index];
                return Card(
                  color: _surface,
                  elevation: 2,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: BorderSide(color: _border),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Expanded(
                        child: Container(
                          decoration: BoxDecoration(
                            color: _bg,
                            borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
                          ),
                          child: Center(
                            child: item.imageObverse != null
                                ? Image.network(
                                    item.imageObverse!,
                                    fit: BoxFit.contain,
                                    errorBuilder: (context, error, stackTrace) => Text(item.itemCategory.emoji, style: TextStyle(fontSize: 36)),
                                  )
                                : Text(item.itemCategory.emoji, style: TextStyle(fontSize: 36)),
                          ),
                        ),
                      ),
                      Padding(
                        padding: EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              item.name.isNotEmpty ? item.name : 'Unnamed Item',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: _text,
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                              ),
                            ),
                            SizedBox(height: 4),
                            Text(
                              '${item.country} · ${item.era}',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                color: _subtext,
                                fontSize: 11,
                              ),
                            ),
                            SizedBox(height: 4),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Container(
                                  padding: EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: _accent.withAlpha(20),
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Text(
                                    item.itemCategory.displayLabel,
                                    style: TextStyle(
                                      color: _accent,
                                      fontSize: 9,
                                      fontWeight: FontWeight.w600,
                                    ),
                                  ),
                                ),
                                if (item.estimatedValue != null)
                                  Text(
                                    '\$${item.estimatedValue!.toStringAsFixed(2)}',
                                    style: TextStyle(
                                      color: Colors.green,
                                      fontWeight: FontWeight.bold,
                                      fontSize: 12,
                                    ),
                                  )
                                else
                                  Text(
                                    'No Value',
                                    style: TextStyle(
                                      color: _subtext,
                                      fontSize: 11,
                                    ),
                                  ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                );
              },
            ),
          ],
        );
      },
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Padding(
        padding: EdgeInsets.all(32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.cloud_off_rounded, size: 48, color: _red),
            SizedBox(height: 16),
            Text(
              'Could not load your collection',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: _text),
            ),
            SizedBox(height: 8),
            Text(
              'Check your internet connection and try refreshing the page.\nIf the problem persists, contact support at beta@numista.ai',
              textAlign: TextAlign.center,
              style: TextStyle(color: _subtext, height: 1.5),
            ),
          ],
        ),
      ),
    );
  }

  double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final s = val.toString().replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(s) ?? 0.0;
  }

  static double _parseAiValue(String raw) {
    if (raw.isEmpty || raw == 'Pending' || raw == 'null') return 0.0;
    final norm = raw
        .replaceAll(',', '')
        .replaceAll('\u2013', '-')
        .replaceAll('\u2014', '-')
        .replaceAll('\u2012', '-');
    final rangeMatch = RegExp(r'(\d+\.?\d*)\s*-\s*[^0-9]*(\d+\.?\d*)').firstMatch(norm);
    if (rangeMatch != null) {
      final a = double.tryParse(rangeMatch.group(1)!) ?? 0.0;
      return a > 100000 ? 0.0 : a;
    }
    final v = double.tryParse(norm.replaceAll(RegExp(r'[^\d.]'), '')) ?? 0.0;
    return v > 100000 ? 0.0 : v;
  }

  // --- Filters row --------------------------------------------------------
  Widget _buildFiltersRow(List<QueryDocumentSnapshot> allDocs) {
    // Compute how many coins in the current view have a real AI estimated value
    final estimated = allDocs.where((d) {
      final v = (d.data() as Map<String, dynamic>)[_F.aiValue]?.toString() ?? '';
      return v.isNotEmpty && v != 'Pending' && v != 'null';
    }).length;
    final total = allDocs.length;
    final allEstimated = estimated == total && total > 0;
    return Row(children: [
      SizedBox(
        width: 140,
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('Show:', style: TextStyle(color: _text, fontSize: 14)),
          SizedBox(height: 8),
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
      SizedBox(width: 24),
      Expanded(
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Icon(Icons.search, size: 16, color: _text),
            SizedBox(width: 4),
            Text('Search', style: TextStyle(color: _text, fontSize: 14)),
          ]),
          SizedBox(height: 8),
          SizedBox(
            height: 44,
            child: TextField(
              controller: _searchCtrl,
              focusNode: _searchFocus,
              style: TextStyle(color: _text, fontSize: 14),
              decoration: InputDecoration(
                filled: true,
                fillColor: Colors.white,
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: BorderSide(color: _border, width: 1.5)),
                enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: BorderSide(color: _border, width: 1.5)),
                focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(6),
                    borderSide: BorderSide(color: _accent, width: 2.0)),
                hintText: 'Search by year, series, grade...',
                hintStyle: TextStyle(color: Color(0xFFADB5BD), fontSize: 14),
                contentPadding: EdgeInsets.symmetric(horizontal: 12),
                prefixIcon: Icon(Icons.search, size: 18, color: Color(0xFFADB5BD)),
                suffixIcon: _searchQuery.isNotEmpty
                    ? IconButton(
                        icon: Icon(Icons.clear, size: 16),
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
      SizedBox(width: 24),
      Expanded(
        child: _buildValuationBadge(allEstimated, estimated, total),
      ),
      SizedBox(width: 12),
      // ── Vertex AI Reference Search button ─────────────────────────────
      if (widget.onNavigate != null)
        Container(
          margin: EdgeInsets.only(top: 22),
          child: Tooltip(
            message: 'Search 11,900+ coin reference entries with Vertex AI',
            child: ElevatedButton.icon(
              onPressed: () => widget.onNavigate!('Coin Search'),
              icon: Icon(Icons.manage_search, size: 16),
              label: Text('AI Reference Search'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Color(0xFF0D9488),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(6)),
                padding: EdgeInsets.symmetric(
                    horizontal: 14, vertical: 12),
                textStyle: TextStyle(
                    fontSize: 12, fontWeight: FontWeight.w600),
              ),
            ),
          ),
        ),
    ]);
  }


  // --- Stats row -----------------------------------------------------------
  Widget _buildStatsRow(List<QueryDocumentSnapshot> docs, {bool advanced = false}) {
    double valueTotal = 0;
    double fvTotal = 0;
    double meltTotal = 0;
    for (final doc in docs) {
      final m   = doc.data() as Map<String, dynamic>;
      
      final coinCpg = _parseNumber(m['cpgRetail']);
      final coinBid = _parseNumber(m['greysheetBid']);
      final gVal = advanced ? coinCpg : coinBid;
      if (gVal > 0) {
        valueTotal += gVal;
      } else {
        final aiRaw = m[_F.aiValue]?.toString() ?? '';
        valueTotal += _parseAiValue(aiRaw);
      }

      // Melt Value -- live from spot prices when available, else from Firestore
      final qtyRaw = _parseNumber(m['Quantity'] ?? m['qty']).toInt();
      final qty = qtyRaw > 0 ? qtyRaw : 1;
      final liveMelt = _spotPrices.isNotEmpty
          ? (MeltValueService.compute(
                metalContent: m[_F.metalContent]?.toString() ?? '',
                denomination: m[_F.denomination]?.toString() ?? '',
                spotPrices: _spotPrices,
                programSeries: m[_F.programSeries]?.toString() ?? '',
                themeSubject: m[_F.themeSubject]?.toString() ?? '',
                qty: qty,
                coinData: m,
              ) ?? 0.0)
          : () {
              final meltRaw = m[_F.meltValue]?.toString() ?? '';
              final match = RegExp(r'\d+\.?\d*').firstMatch(meltRaw.replaceAll(',', ''));
              return match != null ? ((double.tryParse(match.group(0)!) ?? 0.0) * qty) : 0.0;
            }();
      meltTotal += liveMelt;

      // Face Value sum
      fvTotal += MeltValueService.parseFaceValue(m[_F.denomination]?.toString() ?? '', qty: qty);
    }

    final isOffline = _spotPrices.isEmpty;
    final meltText = isOffline
        ? '⚠️ \$${meltTotal.toStringAsFixed(2)} (offline)'
        : '🥈 \$${meltTotal.toStringAsFixed(2)}';

    return Row(children: [
      _statChip('Showing', '${docs.length} coins'),
      const SizedBox(width: 12),
      _statChip('Face Value', '\$${fvTotal.toStringAsFixed(2)}', isGold: true),
      const SizedBox(width: 12),
      _statChip('Melt Value', meltText, isGold: true),
      const SizedBox(width: 12),
      _statChip('Est. Value', '\$${valueTotal.toStringAsFixed(2)}', isGold: true),
    ]);
  }

  // ── Valuation badge / progress banner ──────────────────────────────────────
  Widget _buildValuationBadge(bool allEstimated, int estimated, int total) {
    final v = _valuation;

    // ─ All done ──────────────────────────────────────────────────────────────
    if (allEstimated) {
      return Container(
        margin: EdgeInsets.only(top: 22),
        padding: EdgeInsets.all(12),
        decoration: BoxDecoration(
            color: _greenBg, borderRadius: BorderRadius.circular(4)),
        child: Row(children: [
          Icon(Icons.check_box, color: _green, size: 20),
          SizedBox(width: 8),
          Expanded(
            child: Text('All estimated.',
                style: TextStyle(color: _greenText, fontSize: 13)),
          ),
        ]),
      );
    }

    // ─ Running ───────────────────────────────────────────────────────────────
    if (v.isRunning) {
      return Container(
        margin: EdgeInsets.only(top: 22),
        padding: EdgeInsets.all(10),
        decoration: BoxDecoration(
            color: Color(0xFFECFDF5),
            border: Border.all(color: Color(0xFF86EFAC)),
            borderRadius: BorderRadius.circular(4)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              SizedBox(
                width: 12, height: 12,
                child: CircularProgressIndicator(
                    strokeWidth: 2, color: Color(0xFF0D9488)),
              ),
              SizedBox(width: 8),
              Expanded(
                child: Text(v.label,
                    style: TextStyle(
                        fontSize: 12, color: _text,
                        fontWeight: FontWeight.w600),
                    overflow: TextOverflow.ellipsis),
              ),
              GestureDetector(
                onTap: BatchValuationService.instance.pause,
                child: Text('\u25a0 Pause',
                    style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFFF59E0B),
                        fontWeight: FontWeight.w600)),
              ),
            ]),
            SizedBox(height: 6),
            ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: v.pct, minHeight: 4,
                backgroundColor: Color(0xFFD1FAE5),
                valueColor: const AlwaysStoppedAnimation<Color>(
                    Color(0xFF0D9488)),
              ),
            ),
            if (v.etaLabel.isNotEmpty) ...[
              SizedBox(height: 4),
              Text(v.etaLabel,
                  style: TextStyle(
                      fontSize: 10, color: Color(0xFF6B7280))),
            ],
          ],
        ),
      );
    }

    // ─ Paused with progress ──────────────────────────────────────────────────
    if (v.isPaused && v.total > 0) {
      return Container(
        margin: EdgeInsets.only(top: 22),
        padding: EdgeInsets.all(10),
        decoration: BoxDecoration(
            color: Color(0xFFFFFBEB),
            border: Border.all(color: Color(0xFFFDE68A)),
            borderRadius: BorderRadius.circular(4)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(children: [
              Icon(Icons.pause_circle_outline,
                  size: 14, color: Color(0xFFF59E0B)),
              SizedBox(width: 6),
              Expanded(
                child: Text('Paused — ${v.label}',
                    style: TextStyle(
                        fontSize: 12, color: _text,
                        fontWeight: FontWeight.w600),
                    overflow: TextOverflow.ellipsis),
              ),
              GestureDetector(
                onTap: BatchValuationService.instance.resume,
                child: Text('\u25ba Resume',
                    style: TextStyle(
                        fontSize: 11,
                        color: Color(0xFF0D9488),
                        fontWeight: FontWeight.w600)),
              ),
            ]),
            SizedBox(height: 5),
            ClipRRect(
              borderRadius: BorderRadius.circular(2),
              child: LinearProgressIndicator(
                value: v.pct, minHeight: 4,
                backgroundColor: Color(0xFFFEF3C7),
                valueColor: const AlwaysStoppedAnimation<Color>(
                    Color(0xFFF59E0B)),
              ),
            ),
          ],
        ),
      );
    }

    // ─ Not started ───────────────────────────────────────────────────────────
    return Container(
      margin: EdgeInsets.only(top: 22),
      padding: EdgeInsets.all(10),
      decoration: BoxDecoration(
          color: Color(0xFFFFF3CD),
          border: Border.all(color: Color(0xFFFDE68A)),
          borderRadius: BorderRadius.circular(4)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Icon(Icons.info_outline,
                size: 14, color: Color(0xFF856404)),
            SizedBox(width: 6),
            Expanded(
              child: Text(
                total == 0
                    ? 'No coins loaded.'
                    : '$estimated of $total estimated.',
                style: TextStyle(
                    fontSize: 12,
                    color: Color(0xFF664D03),
                    fontWeight: FontWeight.w600),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ]),
          SizedBox(height: 6),
          Text(
            'Our AI needs ~2 sec per coin to estimate value from year, grade & mint mark — no photos needed.',
            style: TextStyle(fontSize: 10, color: Color(0xFF92400E), height: 1.4),
          ),
          SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () => BatchValuationService.instance.start(),
            icon: Icon(Icons.play_arrow_rounded, size: 14),
            label: Text('Run AI Valuation'),
            style: ElevatedButton.styleFrom(
              backgroundColor: Color(0xFF0D9488),
              foregroundColor: Colors.white,
              minimumSize: Size(0, 30),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(4)),
              padding: EdgeInsets.symmetric(
                  horizontal: 12, vertical: 6),
              textStyle: TextStyle(
                  fontSize: 11, fontWeight: FontWeight.w600),
            ),
          ),
        ],
      ),
    );
  }

  Widget _statChip(String label, String value, {bool isGold = false}) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final goldColor = const Color(0xFFC9A227);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
      decoration: BoxDecoration(
        color: _surface,
        border: Border.merge(
          Border(left: BorderSide(color: isGold ? goldColor : _border, width: 4)),
          Border.all(color: _border.withAlpha(isDark ? 30 : 15)),
        ),
        borderRadius: BorderRadius.circular(8),
        boxShadow: [
          BoxShadow(
            color: isGold ? goldColor.withAlpha(15) : Colors.black.withAlpha(isDark ? 15 : 5),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label.toUpperCase(),
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              letterSpacing: 0.8,
              color: _subtext,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w800,
              color: isGold ? goldColor : _text,
            ),
          ),
        ],
      ),
    );
  }

  void _toggleColumnVisibility(bool showOnlyPopulated) {
    setState(() {
      _showOnlyPopulated = showOnlyPopulated;
    });
    // Event-driven post-frame offset correction when maxScrollExtent shrinks
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_tvHorizCtrl.hasClients &&
          _tvHorizCtrl.position.hasContentDimensions &&
          _tvHorizCtrl.offset > _tvHorizCtrl.position.maxScrollExtent) {
        _tvHorizCtrl.jumpTo(_tvHorizCtrl.position.maxScrollExtent);
      }
    });
  }

  void _panTable(bool scrollRight) {
    if (!_tvHorizCtrl.hasClients || !_tvHorizCtrl.position.hasContentDimensions) return;
    final double viewport = _tvHorizCtrl.position.viewportDimension;
    final double panDelta = viewport * 0.6; // Viewport-relative step size
    final double maxExtent = _tvHorizCtrl.position.maxScrollExtent;
    final double currentOffset = _tvHorizCtrl.offset;
    final double targetOffset = scrollRight
        ? (currentOffset + panDelta).clamp(0.0, maxExtent)
        : (currentOffset - panDelta).clamp(0.0, maxExtent);

    _tvHorizCtrl.animateTo(
      targetOffset,
      duration: const Duration(milliseconds: 200),
      curve: Curves.easeOut,
    );
  }

  Widget _buildPanButtonsToolbar() {
    return ListenableBuilder(
      listenable: _tvHorizCtrl,
      builder: (context, _) {
        final bool canScroll = _tvHorizCtrl.hasClients &&
            _tvHorizCtrl.position.hasContentDimensions &&
            _tvHorizCtrl.position.maxScrollExtent > 0;
        final bool canScrollLeft = canScroll && _tvHorizCtrl.offset > 0;
        final bool canScrollRight = canScroll && _tvHorizCtrl.offset < _tvHorizCtrl.position.maxScrollExtent;

        return Focus(
          autofocus: false,
          onKeyEvent: (node, event) {
            if (!canScroll) return KeyEventResult.ignored;
            if (event.logicalKey == LogicalKeyboardKey.arrowLeft) {
              _panTable(false);
              return KeyEventResult.handled;
            } else if (event.logicalKey == LogicalKeyboardKey.arrowRight) {
              _panTable(true);
              return KeyEventResult.handled;
            }
            return KeyEventResult.ignored;
          },
          child: Container(
            decoration: BoxDecoration(
              border: Border.all(color: _border),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                IconButton(
                  icon: const Icon(Icons.chevron_left_rounded, size: 18),
                  tooltip: 'Pan Left (←)',
                  onPressed: canScrollLeft ? () => _panTable(false) : null,
                  visualDensity: VisualDensity.compact,
                ),
                Container(width: 1, height: 20, color: _border),
                IconButton(
                  icon: const Icon(Icons.chevron_right_rounded, size: 18),
                  tooltip: 'Pan Right (→)',
                  onPressed: canScrollRight ? () => _panTable(true) : null,
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ),
        );
      },
    );
  }

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
          onTap: () => _toggleColumnVisibility(true),
          isLeft: true,
        ),
        Container(width: 1, height: 36, color: _border),
        _toggleSegment(
          label: 'All columns',
          icon: Icons.view_column_outlined,
          active: !_showOnlyPopulated,
          onTap: () => _toggleColumnVisibility(false),
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
        duration: Duration(milliseconds: 150),
        padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: active ? _accent : Colors.white,
          borderRadius: BorderRadius.only(
            topLeft:     isLeft  ? Radius.circular(5) : Radius.zero,
            bottomLeft:  isLeft  ? Radius.circular(5) : Radius.zero,
            topRight:    !isLeft ? Radius.circular(5) : Radius.zero,
            bottomRight: !isLeft ? Radius.circular(5) : Radius.zero,
          ),
        ),
        child: Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(icon, size: 14, color: active ? Colors.white : _subtext),
          SizedBox(width: 6),
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
  Widget _buildDataTable(List<QueryDocumentSnapshot> docs, {bool advanced = false}) {
    final visCols   = _visibleColumns(docs);
    final totalCols = 1 + visCols.length; // col 0 = Actions (pinned)
    final totalRows = 1 + docs.length;    // row 0 = header (pinned)

    const double actionsW   = 96.0;
    const double headerH    = 44.0;
    const double dataH      = 44.0;
    const double colPadding = 8.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _TopScrollbarTrackWidget(
          controller: _tvHorizCtrl,
          accentColor: _accent,
          trackColor: _border.withAlpha(80),
        ),
        const SizedBox(height: 6),
        Expanded(
          child: ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: DecoratedBox(
              decoration: BoxDecoration(
                color: _surface,
                border: Border.all(color: _border),
                borderRadius: BorderRadius.circular(8),
              ),
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
              padding: TableSpanPadding(
                  leading: colPadding, trailing: colPadding),
              foregroundDecoration: col == 0
                  ? TableSpanDecoration(
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
                  ? (Theme.of(context).brightness == Brightness.dark ? const Color(0xFF151B26) : const Color(0xFFE2E2DF))
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
            try {
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
            final m   = (doc.data() as Map<String, dynamic>?) ?? {};
            final sel = doc.id == _selectedCoinId;

            void onTap() => _showCoinInspectorDialog(doc.id, m);

            // Actions cell (col 0)
            if (col == 0) {
              return TableViewCell(
                child: InkWell(
                  onTap: onTap,
                  hoverColor: _accent.withAlpha(20),
                  child: Padding(
                    padding: EdgeInsets.symmetric(horizontal: 2),
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
            final value  = _getCellValue(colDef, m, advanced: advanced);

            // -- Cert # column: interactive verification link pop-up -------------------------
            if (colDef.field == _F.gradingCert && value.isNotEmpty) {
              final coinModel = CoinModel.fromMap(m, doc.id);
              final verifyUrl = coinModel.getVerificationUrl();
              final hasUrl = verifyUrl != null;
              final svcName = coinModel.gradingService.isNotEmpty
                  ? coinModel.gradingService
                  : (coinModel.holderType.isNotEmpty ? coinModel.holderType : 'Service');

              return TableViewCell(
                child: Tooltip(
                  message: hasUrl ? 'Verify cert on $svcName' : value,
                  child: InkWell(
                    onTap: hasUrl
                        ? () async {
                            final uri = Uri.parse(verifyUrl);
                            if (await canLaunchUrl(uri)) {
                              await launchUrl(
                                uri,
                                mode: LaunchMode.externalApplication,
                                webOnlyWindowName: '_blank',
                              );
                            }
                          }
                        : onTap,
                    hoverColor: _accent.withAlpha(20),
                    mouseCursor: hasUrl
                        ? SystemMouseCursors.click
                        : MouseCursor.defer,
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Flexible(
                            child: Text(
                              value,
                              overflow: TextOverflow.ellipsis,
                              style: TextStyle(
                                fontSize: 12,
                                color: hasUrl ? _accent : _text,
                                decoration: hasUrl
                                    ? TextDecoration.underline
                                    : TextDecoration.none,
                              ),
                            ),
                          ),
                          if (hasUrl) ...[
                            const SizedBox(width: 4),
                            Icon(Icons.open_in_new_rounded, size: 12, color: _accent),
                          ],
                        ],
                      ),
                    ),
                  ),
                ),
              );
            }

            if (colDef.field == _F.condition && value.isNotEmpty) {
              return TableViewCell(
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: GradeBadgeWidget(
                    gradeCode: value,
                  ),
                ),
              );
            }

            try {
              return TableViewCell(
                child: InkWell(
                  onTap: onTap,
                  hoverColor: _accent.withAlpha(20),
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
            } catch (e, stack) {
              debugPrint('Collection table cell build error at col ${vicinity.column}, row ${vicinity.row}: $e\n$stack');
              return TableViewCell(
                child: Align(
                  alignment: Alignment.centerLeft,
                  child: Text('—', style: TextStyle(fontSize: 12, color: _subtext)),
                ),
              );
            }
          } catch (e, stack) {
            debugPrint('Outer table cell build error: $e\n$stack');
            return TableViewCell(
              child: Align(
                alignment: Alignment.centerLeft,
                child: Text('—', style: TextStyle(fontSize: 12, color: _subtext)),
              ),
            );
          }
        },
      ),         // TableView.builder
    ),           // DecoratedBox
  ),             // ClipRRect
),               // Expanded
],
);
  }



  Widget _buildCardGrid(List<QueryDocumentSnapshot> docs, {bool advanced = false}) {
    return GridView.builder(
      gridDelegate: const SliverGridDelegateWithMaxCrossAxisExtent(
        maxCrossAxisExtent: 220,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.75,
      ),
      itemCount: docs.length,
      itemBuilder: (context, index) {
        final doc = docs[index];
        final m = (doc.data() as Map<String, dynamic>?) ?? {};
        
        final year = m[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
        final mint = m[_F.mintMark]?.toString() ?? '';
        final denom = m[_F.denomination]?.toString() ?? '';
        final series = m[_F.programSeries]?.toString() ?? '';
        final variety = m[_F.variety]?.toString() ?? '';
        final condition = m[_F.condition]?.toString() ?? '';
        final theme = m[_F.themeSubject]?.toString() ?? '';
        
        final yearMint = (mint.isNotEmpty && mint != 'None') ? '$year$mint' : year;
        final displayTitle = '$yearMint ${theme.isNotEmpty ? theme : denom}'.trim();
        
        final valCpg = _parseNumber(m['cpgRetail']);
        final valBid = _parseNumber(m['greysheetBid']);
        final finalVal = advanced ? valCpg : valBid;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (m[_F.aiValue]?.toString() ?? '—');

        final obverseUrl = m[_F.imageObverse]?.toString() ?? '';
        final reverseUrl = m[_F.imageReverse]?.toString() ?? '';
        final displayUrl = obverseUrl.isNotEmpty ? obverseUrl : reverseUrl;

        return Card(
          color: _surface,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(
              color: doc.id == _selectedCoinId ? _accent : _border,
              width: doc.id == _selectedCoinId ? 2.0 : 1.0,
            ),
          ),
          elevation: doc.id == _selectedCoinId ? 4 : 1,
          child: InkWell(
            onTap: () {
              setState(() => _selectedCoinId = doc.id);
              _showCoinInspectorDialog(doc.id, m);
            },
            borderRadius: BorderRadius.circular(12),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        color: Theme.of(context).brightness == Brightness.dark 
                            ? const Color(0xFF0B1120) 
                            : const Color(0xFFF1F5F9),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: displayUrl.isNotEmpty
                          ? Center(
                              child: Container(
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: const Color(0xFFC9A227).withAlpha(40),
                                      blurRadius: 14,
                                      spreadRadius: 1,
                                    ),
                                  ],
                                ),
                                child: Image.network(
                                  displayUrl,
                                  fit: BoxFit.contain,
                                  errorBuilder: (context, error, stackTrace) =>
                                      const Icon(Icons.broken_image_outlined, size: 36),
                                ),
                              ),
                            )
                          : const Center(
                              child: Icon(Icons.image_not_supported_outlined, size: 36),
                            ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    displayTitle,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: _text,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    series.isNotEmpty ? series : (variety.isNotEmpty ? variety : 'General Item'),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(fontSize: 11, color: _subtext),
                  ),
                  const SizedBox(height: 6),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        valueText,
                        style: const TextStyle(
                          fontSize: 13,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFC9A227),
                        ),
                      ),
                      if (condition.isNotEmpty)
                        GradeBadgeWidget(gradeCode: condition),
                    ],
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  /// Sticky header cell with optional sort-direction arrow.
  TableViewCell _tvHeaderCell(
      String label, VoidCallback? onTap, {required bool? sortAsc}) {
    return TableViewCell(
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          mouseCursor: onTap != null
              ? SystemMouseCursors.click
              : SystemMouseCursors.basic,
          child: Padding(
            padding: EdgeInsets.symmetric(horizontal: 4),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Flexible(
                  child: Text(
                    label,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: _text),
                  ),
                ),
                if (sortAsc != null) ...[
                  SizedBox(width: 2),
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
  String _getCellValue(_ColDef col, Map<String, dynamic> m, {bool advanced = false}) {
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
        // Word-form denomination: normalize to official US Mint terms, then capitalise
        final dRaw = rawD.trim();
        if (dRaw.isEmpty) return '';
        if (dRaw.toLowerCase() == 'penny' || dRaw.toLowerCase() == 'cent') {
          return 'One Cent'; // Official US Mint term
        }
        return dRaw[0].toUpperCase() + dRaw.substring(1);
      case _F.condition:
        return _conditionLabel(m[_F.condition]?.toString().trim() ?? '');
      case _F.gradingService:
        final svc = m[_F.gradingService]?.toString().trim() ??
                    m[_F.holderType]?.toString().trim() ?? '';
        return (svc.isEmpty || svc == 'null') ? '' : svc;
      case _F.gradingCert:
        final cert = m[_F.gradingCert]?.toString().trim() ??
                     m['Cert #']?.toString().trim() ??
                     m['Cert No']?.toString().trim() ?? '';
        return (cert.isEmpty || cert == 'null') ? '' : cert;
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
        final coinCpg = _parseNumber(m['cpgRetail']);
        final coinBid = _parseNumber(m['greysheetBid']);
        // Default: CPG Retail (collector/market price).  Advanced: Greysheet Bid (dealer wholesale).
        final gVal = advanced ? coinBid : (coinCpg > 0 ? coinCpg : coinBid);
        if (gVal > 0) {
          return _currencyFmt.format(gVal);
        }
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
    constraints: BoxConstraints(maxWidth: 32, maxHeight: 32),
    onPressed: onTap,
  );

  // --- Empty state (zero coins in collection) -------------------------------
  Widget _buildCollectionEmptyState() {
    return Container(
      margin: EdgeInsets.symmetric(vertical: 32),
      padding: EdgeInsets.all(48),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _border),
        boxShadow: [BoxShadow(color: Colors.black.withAlpha(6), blurRadius: 20, offset: Offset(0, 4))],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Coin icon with gradient ring
          Container(
            width: 88, height: 88,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              gradient: LinearGradient(
                colors: [Color(0xFFF63366), Color(0xFFFF8C42)],
                begin: Alignment.topLeft, end: Alignment.bottomRight,
              ),
              boxShadow: [BoxShadow(color: _accent.withAlpha(60), blurRadius: 20, spreadRadius: 2)],
            ),
            child: Icon(Icons.toll_rounded, size: 44, color: Colors.white),
          ),
          SizedBox(height: 24),
          Text(
            'Your collection is empty',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: _text),
          ),
          SizedBox(height: 8),
          Text(
            'Add your first coin using any of the methods below.\nYou can scan an invoice, enter it manually, import from PCGS,\nor add a whole roll in one step.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 14, color: _subtext, height: 1.6),
          ),
          SizedBox(height: 32),
          Wrap(
            spacing: 12, runSpacing: 12,
            alignment: WrapAlignment.center,
            children: [
              ElevatedButton.icon(
                icon: Icon(Icons.edit_note, size: 18),
                label: Text('Add Manually'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _accent, foregroundColor: Colors.white,
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
                onPressed: () => widget.onNavigate?.call('Add New Coins'),
              ),
              OutlinedButton.icon(
                icon: Icon(Icons.auto_awesome_motion, size: 18),
                label: Text('Browse Add Methods'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _accent,
                  side: BorderSide(color: _accent),
                  padding: EdgeInsets.symmetric(horizontal: 24, vertical: 14),
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
    final denomTrim = denom.trim();
    final denomDisplay = denomTrim.isNotEmpty && !denomTrim.startsWith(r'$')
        ? denomTrim[0].toUpperCase() + denomTrim.substring(1)
        : denomTrim;
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
            backgroundColor: _surface,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            insetPadding: EdgeInsets.symmetric(horizontal: 32, vertical: 24),
            child: ConstrainedBox(
              constraints: BoxConstraints(
                maxWidth: 1100,
                maxHeight: MediaQuery.of(context).size.height * 0.88,
              ),
              child: Column(children: [
                // -- Header -----------------------------------------------
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 20, vertical: 14),
                  decoration: BoxDecoration(
                    color: _surface,
                    border: Border(bottom: BorderSide(color: _border)),
                    borderRadius: BorderRadius.vertical(top: Radius.circular(12)),
                  ),
                  child: Row(children: [
                    Icon(Icons.book_outlined, size: 18, color: _text),
                    SizedBox(width: 8),
                    Text('Coin Inspector -- $title',
                        style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: _text)),
                    Spacer(),
                    // Google Images search — only shown when no photo is active
                    if (!hasActive && refFuture != null) ...[
                      Tooltip(
                        message: 'Opens Google Images: searches for this coin',
                        child: OutlinedButton.icon(
                          onPressed: () => _onSearchGoogle(data),
                          icon: Icon(Icons.image_search, size: 15),
                          label: Text('Google Images'),
                          style: OutlinedButton.styleFrom(
                            foregroundColor: _text, side: BorderSide(color: _border),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
                            padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            textStyle: TextStyle(fontSize: 12),
                          ),
                        ),
                      ),
                      SizedBox(width: 8),
                    ],
                    IconButton(
                      onPressed: () => Navigator.pop(ctx),
                      icon: Icon(Icons.close, size: 20, color: _subtext),
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
                      decoration: BoxDecoration(
                        color: _surface,
                        border: Border(right: BorderSide(color: _border)),
                      ),
                      padding: EdgeInsets.all(16),
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
                                    margin: EdgeInsets.only(bottom: 6),
                                    child: Container(
                                      padding: EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                      decoration: BoxDecoration(
                                        color: Color(0xFF1A237E).withAlpha(20),
                                        borderRadius: BorderRadius.circular(4),
                                        border: Border.all(color: Color(0xFF1A237E), width: 1),
                                      ),
                                      child: Row(mainAxisSize: MainAxisSize.min, children: [
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
                                      SizedBox(width: 8),
                                      _vaultToggleButton('Reverse', !showObv, hasRefRev, () {
                                        setState(() => _vaultShowObverse = false);
                                        setDlg(() {});
                                      }),
                                    ],
                                  ),

                                  SizedBox(height: 12),
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
                                                      : Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                                  errorBuilder: (ctx, err, st) => _vaultPlaceholder(
                                                      showObv ? 'Obverse' : 'Reverse', isError: true),
                                                ),
                                                Positioned(bottom: 8, right: 8,
                                                  child: Container(
                                                    padding: EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                    decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                    child: Row(mainAxisSize: MainAxisSize.min, children: [
                                                      Icon(Icons.zoom_in, size: 12, color: Colors.white),
                                                      SizedBox(width: 3),
                                                      Text('Enlarge', style: TextStyle(fontSize: 10, color: Colors.white)),
                                                    ]),
                                                  ),
                                                ),
                                              ])
                                            : snap.connectionState == ConnectionState.waiting
                                                ? Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2))
                                                : _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse'),
                                      ),
                                    ),
                                  ),
                                  // Attribution
                                  if (hasRef && ref!.attribution != null) ...[
                                    SizedBox(height: 6),
                                    Text(ref.attribution!,
                                        style: TextStyle(fontSize: 9, color: _subtext, fontStyle: FontStyle.italic),
                                        textAlign: TextAlign.center),
                                  ],
                                  SizedBox(height: 12),
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
                                    SizedBox(width: 8),
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
                                SizedBox(width: 8),
                                _vaultToggleButton('Reverse', !showObv, hasRev, () {
                                  setState(() => _vaultShowObverse = false);
                                  setDlg(() {});
                                }),
                              ]),
                              SizedBox(height: 12),
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
                                                  : Center(child: CircularProgressIndicator(color: _accent, strokeWidth: 2)),
                                              errorBuilder: (ctx, err, st) {
                                                debugPrint('Image load error: $err  url: $activeUrl');
                                                return _vaultPlaceholder(showObv ? 'Obverse' : 'Reverse', isError: true);
                                              },
                                            ),
                                            Positioned(bottom: 8, right: 8,
                                              child: Container(
                                                padding: EdgeInsets.symmetric(horizontal: 6, vertical: 3),
                                                decoration: BoxDecoration(color: Colors.black54, borderRadius: BorderRadius.circular(4)),
                                                child: Row(mainAxisSize: MainAxisSize.min, children: [
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
                              SizedBox(height: 12),
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
                                SizedBox(width: 8),
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
                        padding: EdgeInsets.all(24),
                        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                          _buildMetricStrip(data),
                          SizedBox(height: 12),
                          _buildPcgsBar(data),
                          SizedBox(height: 20),
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
      Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
      SizedBox(width: 10),
      Expanded(child: _metricCard('Melt Value', meltStr, Color(0xFF34A853), Icons.blur_circular_outlined)),
      SizedBox(width: 10),
      Expanded(child: _metricCard('Grade', data[_F.condition]?.toString() ?? '--', Color(0xFFF9AB00), Icons.grade_outlined)),
      SizedBox(width: 10),
      Expanded(child: _metricCard(
          'Live eBay',
          _ebayPrices[_selectedCoinId] ?? 'Check >',
          Color(0xFFE53935),
          Icons.shopping_cart_outlined,
          onTap: () => _onSearchEbay(data),
      )),
    ]);
  }

  Widget _metricCard(String label, String value, Color accent, IconData icon, {VoidCallback? onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
      padding: EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: accent.withAlpha(15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: accent.withAlpha(60)),
      ),
      child: Row(children: [
        Icon(icon, color: accent, size: 20),
        SizedBox(width: 10),
        Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(label, style: TextStyle(fontSize: 11, color: accent, fontWeight: FontWeight.w600, letterSpacing: 0.4)),
          SizedBox(height: 2),
          Text(value, style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700, color: _text)),
        ]),
      ]),
    ));
  }

  // --- PCGS feature bar ----------------------------------------------------
  Widget _buildPcgsBar(Map<String, dynamic> data) {
    final svc = data[_F.gradingService]?.toString() ?? '';
    if (!svc.toUpperCase().contains('PCGS')) return SizedBox.shrink();

    final isNfc  = data[_F.isNfcSecure] == true;
    final pop    = data[_F.population]?.toString() ?? '';
    final pcgsNo = data[_F.pcgsNumber]?.toString() ?? '';

    return Container(
      width: double.infinity,
      padding: EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: Color(0xFF003087).withAlpha(12),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Color(0xFF003087).withAlpha(50)),
      ),
      child: Wrap(spacing: 16, runSpacing: 8, crossAxisAlignment: WrapCrossAlignment.center, children: [
        // PCGS label
        Row(mainAxisSize: MainAxisSize.min, children: [
          Icon(Icons.verified_outlined, size: 16, color: Color(0xFF003087)),
          SizedBox(width: 5),
          Text('PCGS Certified', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Color(0xFF003087))),
        ]),
        // NFC badge
        if (isNfc)
          Container(
            padding: EdgeInsets.symmetric(horizontal: 8, vertical: 3),
            decoration: BoxDecoration(
              color: Color(0xFF34A853).withAlpha(20),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: Color(0xFF34A853).withAlpha(80)),
            ),
            child: Row(mainAxisSize: MainAxisSize.min, children: [
              Icon(Icons.nfc, size: 13, color: Color(0xFF34A853)),
              SizedBox(width: 4),
              Text('NFC Secured', style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: Color(0xFF34A853))),
            ]),
          ),
        // Population
        if (pop.isNotEmpty)
          Row(mainAxisSize: MainAxisSize.min, children: [
            Icon(Icons.bar_chart, size: 14, color: _subtext),
            SizedBox(width: 4),
            Text('Pop: $pop', style: TextStyle(fontSize: 12, color: _subtext, fontWeight: FontWeight.w500)),
          ]),
        // CoinFacts link
        if (pcgsNo.isNotEmpty)
          GestureDetector(
            onTap: () async {
              final uri = Uri.parse('https://www.pcgs.com/coinfacts/coin/$pcgsNo');
              if (!await launchUrl(uri, mode: LaunchMode.externalApplication) && mounted) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Could not open browser.')));
              }
            },
            child: Row(mainAxisSize: MainAxisSize.min, children: [
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
      if (cells.isEmpty) return SizedBox.shrink();
      return Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Text(title, style: TextStyle(fontSize: 10, fontWeight: FontWeight.w700, color: _subtext, letterSpacing: 1.0)),
        SizedBox(height: 8),
        Wrap(spacing: 16, runSpacing: 12,
          children: cells.map((f) => _fieldCell(f[0]!, f[1]!)).toList()),
        SizedBox(height: 20),
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
    return t.isNotEmpty ? t[0].toUpperCase() + t.substring(1) : t;
  }

  Widget _fieldCell(String label, String value) => SizedBox(
    width: 160,
    child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(label, style: TextStyle(fontSize: 10, color: _subtext)),
      SizedBox(height: 2),
      Text(value, style: TextStyle(fontSize: 13, color: _text, fontWeight: FontWeight.w500)),
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
        padding: EdgeInsets.symmetric(horizontal: 12),
        decoration: BoxDecoration(
            color: _bg, borderRadius: BorderRadius.circular(4)),
        child: DropdownButtonHideUnderline(
          child: DropdownButton<T>(
            value: value,
            isExpanded: true,
            icon: Icon(Icons.keyboard_arrow_down, color: _text),
            items: items
                .map((v) => DropdownMenuItem<T>(
                    value: v,
                    child: Text(label(v),
                        style: TextStyle(color: _text, fontSize: 14))))
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
                    border: OutlineInputBorder(),
                    isDense: true,
                    contentPadding: EdgeInsets.symmetric(
                        horizontal: 10, vertical: 10),
                  ),
                  style: TextStyle(fontSize: 13),
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
              child: Text('Cancel')),
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
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text('Coin updated.'),
                      backgroundColor: _green));
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text('Save failed: $e'),
                      backgroundColor: _red,
                      duration: Duration(seconds: 6)));
                }
              }
            },
            child: Text('Save'),
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
        title: Text('Delete Coin'),
        content: Text('Remove ${_yearMint(data)} '
            '${data[_F.denomination] ?? ''} from your collection?'),
        actions: [
          TextButton(
              onPressed: () => Navigator.pop(ctx),
              child: Text('Cancel')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
                backgroundColor: _red, foregroundColor: Colors.white),
            onPressed: () async {
              Navigator.pop(ctx);
              // Show snackbar IMMEDIATELY -- don't wait for Firestore round-trip
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(
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
            child: Text('Delete'),
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
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('Could not open browser.'), backgroundColor: _red));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
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
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(
            content: Text('Could not open eBay.'), backgroundColor: _red));
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
          content: Text('Couldn\'t open eBay. Please try again.'), backgroundColor: _red));
      }
    }
  }

  void _showGenerateReportModal() {
    showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => _GenerateReportDialog(userEmail: AuthService.userEmail),
    );
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
                      padding: EdgeInsets.symmetric(
                          horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Color(0xFF1A237E).withAlpha(25),
                        borderRadius: BorderRadius.circular(4),
                        border: Border.all(
                            color: Color(0xFF1A237E), width: 1),
                      ),
                      child: Row(
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
                    Spacer(),
                    _vaultToggleButton('Obverse', _vaultShowObverse,
                        hasRefObv, () {
                      setState(() => _vaultShowObverse = true);
                    }),
                    SizedBox(width: 6),
                    _vaultToggleButton('Reverse', !_vaultShowObverse,
                        hasRefRev, () {
                      setState(() => _vaultShowObverse = false);
                    }),
                  ] else ...[
                    Icon(Icons.add_photo_alternate_outlined,
                        size: 14, color: _subtext),
                    SizedBox(width: 6),
                    Text('Personal Coin Photos',
                        style: TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.w600,
                            color: _subtext)),
                  ],
                ],
              ),
              SizedBox(height: 10),

              // -- Image panel ------------------------------------------------
              GestureDetector(
                onTap: hasRefActive
                    ? () => _showImageLightbox(refUrl,
                          label: _vaultShowObverse ? 'Obverse' : 'Reverse',
                          isMicroscope: false)
                    : null,
                child: AnimatedSwitcher(
                  duration: Duration(milliseconds: 300),
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
                                            color: Color(0xFFF0F2F6),
                                            child: Center(
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
                                  padding: EdgeInsets.symmetric(
                                      horizontal: 6, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: Colors.black54,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                  child: Row(
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
                                color: Color(0xFFF0F2F6),
                                borderRadius: BorderRadius.circular(8),
                              ),
                              child: Center(
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
                SizedBox(height: 6),
                Text(
                  ref.attribution!,
                  style: TextStyle(
                      fontSize: 9,
                      color: _subtext,
                      fontStyle: FontStyle.italic),
                ),
              ],

              SizedBox(height: 10),

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
                  SizedBox(width: 8),
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
                  EdgeInsets.symmetric(horizontal: 8, vertical: 3),
              decoration: BoxDecoration(
                color: isMicroscope
                    ? Color(0xFFFFC107).withAlpha(30)
                    : _accent.withAlpha(30),
                borderRadius: BorderRadius.circular(4),
                border: Border.all(
                    color: isMicroscope
                        ? Color(0xFFFFC107)
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
                        ? Color(0xFFFFC107)
                        : _accent,
                  ),
                  SizedBox(width: 4),
                  Text(
                    isMicroscope ? 'YOUR SCAN' : 'YOUR PHOTO',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: isMicroscope
                          ? Color(0xFFFFC107)
                          : _accent,
                      letterSpacing: 0.8,
                    ),
                  ),
                ],
              ),
            ),
            Spacer(),
            _vaultToggleButton('Obverse', _vaultShowObverse, hasObv, () {
              setState(() => _vaultShowObverse = true);
            }),
            SizedBox(width: 6),
            _vaultToggleButton('Reverse', !_vaultShowObverse, hasRev, () {
              setState(() => _vaultShowObverse = false);
            }),
          ],
        ),
        SizedBox(height: 10),

        GestureDetector(
          onTap: hasActive
              ? () => _showImageLightbox(activeUrl,
                    label: showObverse ? 'Obverse' : 'Reverse',
                    isMicroscope: isMicroscope)
              : null,
          child: AnimatedSwitcher(
            duration: Duration(milliseconds: 300),
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
                                  color: Color(0xFFF0F2F6),
                                  child: Center(
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
                            padding: EdgeInsets.symmetric(
                                horizontal: 6, vertical: 3),
                            decoration: BoxDecoration(
                              color: Colors.black54,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Row(
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

        SizedBox(height: 10),

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
            SizedBox(width: 8),
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
        duration: Duration(milliseconds: 180),
        padding: EdgeInsets.symmetric(horizontal: 10, vertical: 4),
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
        color: Color(0xFFF0F2F6),
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
          SizedBox(height: 8),
          Text(
            isError ? 'Image unavailable' : 'No $side photo yet',
            style: TextStyle(
                fontSize: 12,
                color: isError ? _red.withAlpha(160) : _subtext),
          ),
          if (!isError) ...[
            SizedBox(height: 4),
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
        duration: Duration(milliseconds: 200),
        padding: EdgeInsets.symmetric(vertical: 10),
        decoration: BoxDecoration(
          color: Color(0xFFF0F2F6),
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
                  SizedBox(height: 4),
                  Text('${(progress * 100).toInt()}%',
                      style:
                          TextStyle(fontSize: 10, color: _subtext)),
                ],
              )
            : Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(icon, size: 14, color: _accent),
                  SizedBox(width: 5),
                  Text(label,
                      style: TextStyle(
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
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(16))),
        builder: (_) => SafeArea(
          child: Column(mainAxisSize: MainAxisSize.min, children: [
            SizedBox(height: 8),
            Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2))),
            SizedBox(height: 16),
            ListTile(leading: Icon(Icons.camera_alt, color: Color(0xFFF63366)), title: Text('Take Photo'), onTap: () => Navigator.pop(context, ImageSource.camera)),
            ListTile(leading: Icon(Icons.photo_library, color: Color(0xFF4C8CDA)),  title: Text('Choose from Gallery'), onTap: () => Navigator.pop(context, ImageSource.gallery)),
            SizedBox(height: 8),
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
        // ── Photo-sharing consent ─────────────────────────────────────────────
        // On the user's very first upload: show a one-time opt-out popup.
        // On subsequent uploads: silently honour their stored preference.
        final firstUpload = await PhotoSharingService.shouldShowConsent();
        bool contributionOptedIn;
        if (firstUpload && mounted) {
          contributionOptedIn = await _showPhotoSharingConsent();
          await PhotoSharingService.saveConsent(optedIn: contributionOptedIn);
        } else {
          contributionOptedIn = await PhotoSharingService.isOptedIn();
        }
        // Tag this coin so the backend can queue it for library review
        if (contributionOptedIn && _selectedCoinId != null) {
          try {
            await FirebaseFirestore.instance
                .collection('users')
                .doc(userEmail)
                .collection('coins')
                .doc(_selectedCoinId!)
                .update({
              'contribute_to_library': true,
              'contribute_side':       side,
              'contribute_queued_at':  DateTime.now().toIso8601String(),
            });
          } catch (_) {
            // Non-fatal — library contribution tag is best-effort
          }
        }
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

  /// One-time consent dialog for contributing personal coin photos to the
  /// Numista.AI shared reference library.  Returns true = opt in, false = opt out.
  Future<bool> _showPhotoSharingConsent() async {
    return await showDialog<bool>(
          context: context,
          barrierDismissible: false,
          builder: (ctx) => AlertDialog(
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            titlePadding: EdgeInsets.fromLTRB(20, 20, 20, 0),
            title: Row(
              children: [
                Container(
                  padding: EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Color(0xFFF63366).withAlpha(25),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(Icons.volunteer_activism,
                      color: Color(0xFFF63366), size: 22),
                ),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Help Other Collectors',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                SizedBox(height: 4),
                Text(
                  'Your photo looks great! 🎉',
                  style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
                ),
                SizedBox(height: 10),
                Text(
                  'Would you like to contribute it to the Numista.AI reference '
                  'library? Other collectors will see it when they view the same '
                  'coin — no personal info is shared.',
                  style: TextStyle(fontSize: 13, height: 1.5),
                ),
                SizedBox(height: 14),
                Container(
                  padding: EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Color(0xFF4CAF50).withAlpha(20),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                        color: Color(0xFF4CAF50).withAlpha(100)),
                  ),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.info_outline,
                          color: Color(0xFF388E3C), size: 16),
                      SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          'You\'ll never be asked this again. '  
                          'Change anytime in Settings → Privacy.',
                          style: TextStyle(
                              fontSize: 11,
                              color: Colors.green.shade800,
                              height: 1.4),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            actionsPadding:
                EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            actions: [
              TextButton(
                onPressed: () => Navigator.of(ctx).pop(false),
                child: Text('No thanks',
                    style: TextStyle(color: Colors.grey, fontSize: 13)),
              ),
              ElevatedButton.icon(
                onPressed: () => Navigator.of(ctx).pop(true),
                icon: Icon(Icons.check_circle_outline, size: 18),
                label: Text('Yes, Contribute!'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Color(0xFFF63366),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
        ) ??
        false;
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
          insetPadding: EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Badge
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  if (isMicroscope)
                    Container(
                      margin: EdgeInsets.only(bottom: 8),
                      padding: EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: Color(0xFFFFC107).withAlpha(30),
                        borderRadius: BorderRadius.circular(4),
                        border:
                            Border.all(color: Color(0xFFFFC107)),
                      ),
                      child: Row(
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
                    errorBuilder: (_, _, _) => Padding(
                      padding: EdgeInsets.all(40),
                      child: Icon(Icons.broken_image_outlined,
                          color: Colors.white30, size: 60),
                    ),
                  ),
                ),
              ),
              SizedBox(height: 12),
              Text('$label  *  Tap anywhere to close',
                  style: TextStyle(
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
    if (rollId == null || rollId.isEmpty) return SizedBox.shrink();
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
      margin: EdgeInsets.only(top: 24),
      padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: purple.withAlpha(15),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: purple.withAlpha(60)),
      ),
      child: Row(children: [
        Icon(typeIcon, color: purple, size: 18),
        SizedBox(width: 10),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(typeLabel, style: TextStyle(fontWeight: FontWeight.w700, color: purple, fontSize: 13)),
          Text('Roll ID: $rollId', style: TextStyle(color: purple.withAlpha(160), fontSize: 11)),
        ])),
        TextButton(
          style: TextButton.styleFrom(foregroundColor: purple),
          onPressed: () => setState(() => _searchQuery = rollId),
          child: Text('View All >', style: TextStyle(fontSize: 12)),
        ),
      ]),
    );
  }

  // Shown in the inspector whenever the selected coin has a 'set_id' field
  // (populated by the ingestion pipeline). Falls back silently if not a set.
  Widget _buildCoinSetSection(Map<String, dynamic> data) {
    // Invoice-imported sets store all coin data in set_contents directly.
    // Use SetContentsPanel for these — no additional Firestore lookup needed.
    final rawContents = data['set_contents'];
    if (rawContents is List && rawContents.isNotEmpty) {
      return Padding(
        padding: EdgeInsets.fromLTRB(0, 4, 0, 0),
        child: SetContentsPanel(data: data),
      );
    }

    // Pre-cataloged sets (e.g. Jamul Sovereign, Birth Year) use set_id
    // to look up coin_set_index in Firestore.
    final setId = data['set_id'] as String?;
    if (setId == null || setId.isEmpty) return SizedBox.shrink();

    return Padding(
      padding: EdgeInsets.fromLTRB(0, 16, 0, 0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Divider(color: _border),
          SizedBox(height: 16),
          CoinSetViewer(setId: setId),
        ],
      ),
    );
  }

  // --- Similar Coins widget for the inspector ------------------------------
  Widget _buildSimilarCoinsInspector() {
    if (!_loadingInspectorSimilar && _inspectorSimilar.isEmpty) {
      return SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(height: 24),
        Divider(color: _border),
        SizedBox(height: 16),
        Row(
          children: [
            Icon(Icons.photo_library_outlined, color: _accent, size: 16),
            SizedBox(width: 8),
            Text(
              'Similar in Reference Library',
              style: TextStyle(
                  color: _text,
                  fontSize: 14,
                  fontWeight: FontWeight.w600),
            ),
            if (_loadingInspectorSimilar) ...[
              SizedBox(width: 12),
              SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(
                    color: _accent, strokeWidth: 2),
              ),
            ],
          ],
        ),
        SizedBox(height: 12),
        if (!_loadingInspectorSimilar && _inspectorSimilar.isNotEmpty)
          SizedBox(
            height: 120,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _inspectorSimilar.length,
              separatorBuilder: (_, _) => SizedBox(width: 10),
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
                            errorBuilder: (_, _, _) => Icon(
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
                                padding: EdgeInsets.symmetric(
                                    vertical: 2, horizontal: 4),
                                color: Colors.black54,
                                child: Text(
                                  img.year!,
                                  style: TextStyle(
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
        SizedBox(height: 4),
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
        insetPadding: EdgeInsets.all(24),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(12),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ConstrainedBox(
                constraints: BoxConstraints(maxHeight: 380),
                child: Image.network(
                  img.gcsUrl,
                  fit: BoxFit.contain,
                  errorBuilder: (_, _, _) => Padding(
                    padding: EdgeInsets.all(40),
                    child: Icon(Icons.broken_image_outlined,
                        color: _subtext, size: 56),
                  ),
                ),
              ),
              Padding(
                padding: EdgeInsets.all(16),
                child: Text(img.caption,
                    style: TextStyle(fontSize: 12, color: _subtext)),
              ),
              TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: Text('Close'),
              ),
              SizedBox(height: 8),
            ],
          ),
        ),
      ),
    );
  }
}

// ── Segmented Tab Selection Control ──────────────────────────────────────────
class MyCollectionSegmentedControl extends StatelessWidget {
  final String selectedTab;
  final ValueChanged<String> onTabChanged;

  const MyCollectionSegmentedControl({
    super.key,
    required this.selectedTab,
    required this.onTabChanged,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bgColor = isDark ? Color(0xFF1E293B) : Color(0xFFE2E8F0);
    final selectedColor = isDark ? Color(0xFF0F172A) : Colors.white;
    final textColor = isDark ? Colors.white70 : Color(0xFF475569);
    final activeTextColor = isDark ? Colors.white : Color(0xFF0F172A);

    final tabs = ['All', 'Coins', 'Currency', 'Non-Legal Tender'];

    return Container(
      padding: EdgeInsets.all(4),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: tabs.map((tab) {
          final isSelected = selectedTab == tab;
          return GestureDetector(
            onTap: () => onTabChanged(tab),
            child: AnimatedContainer(
              duration: Duration(milliseconds: 200),
              padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              decoration: BoxDecoration(
                color: isSelected ? selectedColor : Colors.transparent,
                borderRadius: BorderRadius.circular(6),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: Colors.black.withAlpha(20),
                          blurRadius: 4,
                          offset: Offset(0, 2),
                        )
                      ]
                    : [],
              ),
              child: Text(
                tab,
                style: TextStyle(
                  color: isSelected ? activeTextColor : textColor,
                  fontSize: 13,
                  fontWeight: isSelected ? FontWeight.w600 : FontWeight.w500,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }
}

// ── Unified Portfolio Additions Model ─────────────────────────────────────────
class UnifiedCollectionItem {
  final String title;
  final String category;
  final String emoji;
  final String country;
  final DateTime? dateAdded;
  final double value;

  UnifiedCollectionItem({
    required this.title,
    required this.category,
    required this.emoji,
    required this.country,
    this.dateAdded,
    required this.value,
  });
}

// ── Interactive AI Collection Report Modal ─────────────────────────────────────
class _GenerateReportDialog extends StatefulWidget {
  final String userEmail;
  const _GenerateReportDialog({required this.userEmail});

  @override
  State<_GenerateReportDialog> createState() => _GenerateReportDialogState();
}

class _GenerateReportDialogState extends State<_GenerateReportDialog> {
  bool _isLoading = true;
  String? _error;
  EstateReportResult? _result;

  @override
  void initState() {
    super.initState();
    _startGeneration();
  }

  Future<void> _startGeneration() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final ownerName = widget.userEmail.isNotEmpty ? widget.userEmail.split('@').first : 'Collection Owner';
      final identity = EphemeralReportIdentity(
        ownerLegalName: ownerName,
        reportDate: intl.DateFormat('yyyy-MM-dd').format(DateTime.now()),
      );

      final result = await EstateReportService.generateReport(
        uid: widget.userEmail,
        identity: identity,
        mode: 'living_inventory',
        includePhotos: true,
      ).timeout(
        const Duration(seconds: 45),
        onTimeout: () => throw Exception('Report generation timed out. Please try again.'),
      );

      if (mounted) {
        setState(() {
          _result = result;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = e.toString().replaceAll('Exception:', '').trim();
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    const bgCard = Color(0xFF161B27);
    const pink   = Color(0xFFF63366);

    return AlertDialog(
      backgroundColor: bgCard,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: const Row(
        children: [
          Icon(Icons.auto_awesome, color: pink),
          SizedBox(width: 10),
          Text('AI Collection & Inventory Report', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
        ],
      ),
      content: SizedBox(
        width: 480,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_isLoading) ...[
              const Center(
                child: Padding(
                  padding: EdgeInsets.symmetric(vertical: 24),
                  child: Column(
                    children: [
                      CircularProgressIndicator(color: pink),
                      SizedBox(height: 16),
                      Text('Compiling legal-grade PDF report via Cloud Run...', style: TextStyle(color: Colors.white70, fontSize: 13)),
                    ],
                  ),
                ),
              ),
            ] else if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: const Color(0x25F63366), borderRadius: BorderRadius.circular(8)),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: pink),
                    const SizedBox(width: 10),
                    Expanded(child: Text(_error!, style: const TextStyle(color: Colors.white70, fontSize: 13))),
                  ],
                ),
              ),
            ] else if (_result != null) ...[
              const Text('Your AI Collection Inventory Report has been compiled successfully!', style: TextStyle(color: Colors.white70, fontSize: 14)),
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        await EstateReportService.openPdf(_result!.pdfBytes, 'Numista_AI_Collection_Report.pdf');
                      },
                      icon: const Icon(Icons.picture_as_pdf, size: 18),
                      label: const Text('📄 Open PDF'),
                      style: ElevatedButton.styleFrom(backgroundColor: pink, foregroundColor: Colors.white),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    tooltip: 'Copy Attorney Portal Link',
                    icon: const Icon(Icons.link, color: Colors.white),
                    onPressed: () async {
                      await EstateReportService.copyAttorneyLink(widget.userEmail, _result!.reportId);
                      if (mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Attorney Portal link copied to clipboard!'), backgroundColor: pink));
                      }
                    },
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
      actions: [
        if (_error != null)
          TextButton(
            onPressed: _startGeneration,
            child: const Text('Retry', style: TextStyle(color: pink)),
          ),
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Close', style: TextStyle(color: Colors.white70)),
        ),
      ],
    );
  }
}

// --- Custom Top Scrollbar Track Widget ----------------------------------------
class _TopScrollbarTrackWidget extends StatefulWidget {
  final ScrollController controller;
  final Color accentColor;
  final Color trackColor;

  const _TopScrollbarTrackWidget({
    super.key,
    required this.controller,
    required this.accentColor,
    required this.trackColor,
  });

  @override
  State<_TopScrollbarTrackWidget> createState() => _TopScrollbarTrackWidgetState();
}

class _TopScrollbarTrackWidgetState extends State<_TopScrollbarTrackWidget> {
  double? _dragStartLocalX;
  double? _dragStartScrollOffset;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: widget.controller,
      builder: (context, _) {
        if (!widget.controller.hasClients ||
            !widget.controller.position.hasContentDimensions ||
            widget.controller.position.maxScrollExtent <= 0) {
          return const SizedBox.shrink();
        }

        final double maxExtent = widget.controller.position.maxScrollExtent;
        final double viewport = widget.controller.position.viewportDimension;
        final double offset = widget.controller.offset.clamp(0.0, maxExtent);

        final double totalContent = maxExtent + viewport;
        final double thumbRatio = (viewport / totalContent).clamp(0.1, 0.9);

        return LayoutBuilder(
          builder: (context, constraints) {
            final double trackWidth = constraints.maxWidth;
            final double thumbWidth = (trackWidth * thumbRatio).clamp(36.0, trackWidth);
            final double maxThumbOffset = trackWidth - thumbWidth;
            final double scrollRatio = maxExtent > 0 ? (offset / maxExtent).clamp(0.0, 1.0) : 0.0;
            final double thumbLeft = scrollRatio * maxThumbOffset;

            return SizedBox(
              height: 24, // 24px hit target for easy mouse / touch interaction
              child: GestureDetector(
                behavior: HitTestBehavior.opaque,
                onHorizontalDragStart: (details) {
                  _dragStartLocalX = details.localPosition.dx;
                  _dragStartScrollOffset = widget.controller.offset;
                },
                onHorizontalDragUpdate: (details) {
                  if (maxThumbOffset <= 0 || _dragStartLocalX == null || _dragStartScrollOffset == null) return;
                  final double deltaX = details.localPosition.dx - _dragStartLocalX!;
                  final double scrollDelta = (deltaX / maxThumbOffset) * maxExtent;
                  final double targetOffset = (_dragStartScrollOffset! + scrollDelta).clamp(0.0, maxExtent);
                  widget.controller.jumpTo(targetOffset);
                },
                onHorizontalDragEnd: (_) {
                  _dragStartLocalX = null;
                  _dragStartScrollOffset = null;
                },
                onTapDown: (details) {
                  if (maxThumbOffset <= 0) return;
                  final double clickRatio = (details.localPosition.dx - thumbWidth / 2) / maxThumbOffset;
                  final double targetOffset = (clickRatio * maxExtent).clamp(0.0, maxExtent);
                  widget.controller.animateTo(
                    targetOffset,
                    duration: const Duration(milliseconds: 200),
                    curve: Curves.easeOut,
                  );
                },
                child: Center(
                  child: Container(
                    height: 8, // 8px visual track
                    width: trackWidth,
                    decoration: BoxDecoration(
                      color: widget.trackColor,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Stack(
                      children: [
                        Positioned(
                          left: thumbLeft,
                          width: thumbWidth,
                          top: 0,
                          bottom: 0,
                          child: Container(
                            decoration: BoxDecoration(
                              color: widget.accentColor,
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            );
          },
        );
      },
    );
  }
}

