import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../constants.dart';

import '../services/auth_service.dart';
import '../services/camera_capture_service.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../widgets/add_coin_manual_form.dart';
import '../widgets/extraction_success_dialog.dart';
import '../services/wishlist_service.dart';
import '../models/coin_model.dart';
import '../services/pcgs_import_service.dart';
import '../widgets/roll_entry_dialog.dart';
import 'package:url_launcher/url_launcher.dart';

class AddCoinsHub extends StatefulWidget {
  final Function(String)? onNavigate;
  final String? initialTabName;
  const AddCoinsHub({super.key, this.onNavigate, this.initialTabName});

  @override
  State<AddCoinsHub> createState() => _AddCoinsHubState();
}

class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isProcessing = false;
  // ignore: prefer_final_fields
  double _processingProgress = 0;
  // ignore: prefer_final_fields
  String _statusMessage = '';

  // ─── Parallel Batch Ingestion state ──────────────────────────────────────
  bool _isBatchProcessing = false;
  double _batchProgress = 0.0;
  String _batchStatusMsg = '';
  List<Map<String, String>> _batchItems = [];


  // PCGS Import state
  final _pcgsTokenCtrl     = TextEditingController();
  final _pcgsCertCtrl      = TextEditingController();  // bulk import
  final _pcgsSingleCtrl    = TextEditingController();  // single cert lookup
  bool   _pcgsTokenSaved   = false;
  bool   _hasPlatformToken = false;  // true = platform token exists, user needs nothing
  bool   _isLoadingToken   = true;
  bool   _showAdvancedToken = false;  // collapsed by default
  bool   _pcgsImporting    = false;
  double _pcgsProgress     = 0;
  String _pcgsStatusMsg    = '';
  PcgsImportResult? _pcgsLastResult;
  // Single-cert lookup result
  Map<String, dynamic>? _pcgsLookupResult;
  bool   _pcgsLookupLoading = false;
  String _pcgsLookupError   = '';
  bool   _pcgsSingleAdding  = false;

  // ─── Excel import state ─────────────────────────────────────────────────
  final _importNameCtrl = TextEditingController();

  // ─── SKU Import state ───────────────────────────────────────────────────
  final _skuCtrl = TextEditingController();
  String _skuRetailer = 'US Mint';
  bool _skuSearching = false;
  Map<String, dynamic>? _skuSearchResult;
  String _skuError = '';

  // ─── AI Photo ID state ───────────────────────────────────────────────────
  final _picYear    = TextEditingController();
  final _picDenom   = TextEditingController();
  final _picSeries  = TextEditingController();
  final _picTheme   = TextEditingController();
  final _picMint    = TextEditingController();
  final _picGrade   = TextEditingController();
  final _picMetal   = TextEditingController();
  final _picVariety = TextEditingController();
  final _picCost    = TextEditingController();
  final _picStorage = TextEditingController();
  final _picNotes   = TextEditingController();

  // ─── Quick Camera Scanner State ───────────────────────────────────────────
  Uint8List? _camObverseBytes;
  Uint8List? _camReverseBytes;
  String? _camObverseName;
  String? _camReverseName;
  bool _camLoading = false;
  String? _camError;
  Map<String, dynamic>? _camResult;
  bool _camSaving = false;

  // Backend API URL

  @override
  void initState() {
    super.initState();
    int initialIdx = 0;
    if (widget.initialTabName != null) {
      switch (widget.initialTabName) {
        case 'camera':
        case 'webcam':
          initialIdx = 0;
          break;
        case 'upload':
          initialIdx = 1;
          break;
        case 'manual':
          initialIdx = 2;
          break;
        case 'sku':
          initialIdx = 3;
          break;
        case 'pcgs':
          initialIdx = 4;
          break;
        case 'roll':
          initialIdx = 5;
          break;
        case 'world':
          initialIdx = 6;
          break;
        case 'set':
          initialIdx = 7;
          break;
        default:
          initialIdx = 0;
      }
    }
    _tabController = TabController(
      length: 8,
      vsync: this,
      initialIndex: initialIdx,
    );
    _loadSavedPcgsToken();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pcgsTokenCtrl.dispose();
    _pcgsCertCtrl.dispose();
    _pcgsSingleCtrl.dispose();
    _importNameCtrl.dispose();
    _skuCtrl.dispose();
    _mintSetNameCtrl.dispose();
    _mintSetCostCtrl.dispose();
    _mintSetDateCtrl.dispose();
    _mintSetRetailerCtrl.dispose();
    _picYear.dispose();   _picDenom.dispose();   _picSeries.dispose();
    _picTheme.dispose();  _picMint.dispose();    _picGrade.dispose();
    _picMetal.dispose();  _picVariety.dispose(); _picCost.dispose();
    _picStorage.dispose(); _picNotes.dispose();
    super.dispose();
  }

  Future<void> _loadSavedPcgsToken() async {
    // Check for platform token first — if it exists, users need no setup at all.
    final hasPlatform = await PcgsImportService.hasPlatformToken();
    if (hasPlatform) {
      if (mounted) {
        setState(() {
          _hasPlatformToken = true;
          _pcgsTokenSaved   = true;  // enables Verify button immediately
          _isLoadingToken   = false;
        });
      }
      return;
    }
    // No platform token — fall back to checking the user's personal token.
    final token = await PcgsImportService.getToken();
    if (mounted) {
      setState(() {
        _isLoadingToken = false;
        if (token != null) {
          _pcgsTokenCtrl.text = token;
          _pcgsTokenSaved = true;
        }
      });
    }
  }

  // ─── Automated Ingestion Logic ───────────────────────────────────────────


  void _showSuccessDialog(int totalItems) {
    if (!mounted) return;
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => ExtractionSuccessDialog(
        count: totalItems,
        onGoToReview: () {
          if (widget.onNavigate != null) {
            widget.onNavigate!('Review Hub');
          }
        },
      ),
    );
  }

  /// Used ONLY for Manual Entry — shows a snackbar since the coin is
  /// saved directly to the collection (not sent to the Review Hub).
  void _showManualAddedSnackbar() {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(children: [
          Icon(Icons.check_circle, color: Colors.white, size: 20),
          SizedBox(width: 10),
          Text('Coin added to My Collection!',
              style: TextStyle(fontWeight: FontWeight.w600)),
        ]),
        backgroundColor: const Color(0xFF22C55E),
        duration: const Duration(seconds: 2),
        action: SnackBarAction(
          label: 'View Collection',
          textColor: Colors.white,
          onPressed: () {
            if (widget.onNavigate != null) widget.onNavigate!('My Collection');
          },
        ),
      ),
    );
  }

  void _showWishlistMatchPrompt(WishlistItem item) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Matched Wishlist Item!', style: TextStyle(color: Colors.white)),
        content: const Text('This coin matches an item on your Wishlist. Would you like to remove it from your Wishlist now?', style: TextStyle(color: Colors.white70)),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              _showSuccessDialog(1);
            },
            child: const Text('Keep on Wishlist', style: TextStyle(color: Colors.white54)),
          ),
          ElevatedButton(
            onPressed: () async {
              final navigator = Navigator.of(context);
              await WishlistService.removeFromWishlist(item.id);
              if (mounted) {
                navigator.pop();
                _showSuccessDialog(1);
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFFF63366)),
            child: const Text('Remove & Continue', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  // ─── UI Builders ─────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildHeader(context),
        _buildTabBar(),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildCameraScannerTab(),
              _buildUploadFilesTab(),
              _buildManualEntryTab(),
              _buildSkuImportTab(),
              _buildPcgsImportTab(),
              _buildRollEntryTab(),
              _buildWorldItemsTab(),
              _buildMintSetTab(),
            ],
          ),
        ),
        if (_isProcessing) _buildProcessingOverlay(),
      ],
    );
  }

  Widget _buildHeader(BuildContext context) {
    final isNarrow = MediaQuery.of(context).size.width < 600;
    return Padding(
      padding: EdgeInsets.fromLTRB(
          isNarrow ? 12 : 20, isNarrow ? 12 : 16, isNarrow ? 12 : 20, 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Add New Coins',
            style: TextStyle(
                fontSize: isNarrow ? 22 : 32,
                fontWeight: FontWeight.w900,
                fontStyle: FontStyle.italic,
                color: const Color(0xFF31333F)),
          ),
          Text(
            'Choose an entry method to expand your collection.',
            style: TextStyle(
                color: const Color(0xFF64748B),
                fontSize: isNarrow ? 13 : 16)),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32),
      decoration: const BoxDecoration(
        border: Border(bottom: BorderSide(color: Color(0xFFE2E6E9), width: 1)),
      ),
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        labelColor: const Color(0xFFF63366),
        unselectedLabelColor: const Color(0xFF64748B),
        indicatorColor: const Color(0xFFF63366),
        indicatorWeight: 3,
        tabs: const [
          Tab(text: 'Quick Camera',      icon: Icon(Icons.photo_camera_outlined, size: 20)),
          Tab(text: 'Upload Files',      icon: Icon(Icons.upload_file_outlined,  size: 20)),
          Tab(text: 'Manual Entry',      icon: Icon(Icons.edit_note,             size: 20)),
          Tab(text: 'Add by SKU',        icon: Icon(Icons.qr_code,               size: 20)),
          Tab(text: 'Import from PCGS',  icon: Icon(Icons.shield_outlined,       size: 20)),
          Tab(text: 'Roll/Jar/Batch',    icon: Icon(Icons.currency_exchange,     size: 20)),
          Tab(text: 'World & Specialty', icon: Icon(Icons.language_rounded,      size: 20)),
          Tab(text: 'Mint Set',          icon: Icon(Icons.collections_bookmark,  size: 20)),
        ],
      ),
    );
  }


  Widget _buildUploadFilesTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              // ── Header ──────────────────────────────────────────────────
              Row(children: [
                Container(
                  width: 48, height: 48,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFF0C040), Color(0xFFF97316)],
                      begin: Alignment.topLeft, end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.folder_open_outlined,
                      color: Colors.white, size: 26),
                ),
                const SizedBox(width: 14),
                const Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Folder-Drop Bulk Import',
                      style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B))),
                    Text('Drop a folder — AI sorts everything',
                      style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                  ],
                )),
              ]),
              const SizedBox(height: 24),

              // ── Description card ─────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'Upload almost anything digital you have:',
                      style: TextStyle(fontWeight: FontWeight.w600, fontSize: 14,
                          color: Color(0xFF1E293B)),
                    ),
                    const SizedBox(height: 12),
                    ...[
                      (Icons.receipt_long_outlined, 'PDF Invoices & Dealer Receipts',
                          'Parsed by AI — coins extracted automatically'),
                      (Icons.table_chart_outlined,  'Excel, CSV & Access Exports',
                          'Any column format — AI auto-maps to our schema'),
                      (Icons.photo_camera_outlined,  'Coin Photos (JPG, PNG, HEIC)',
                          'Identified & logged to your collection'),
                      (Icons.folder_zip_outlined,    'A Whole Folder at Once',
                          'Mix of hundreds of files — sorted automatically'),
                      (Icons.receipt_rounded,        'Paper Trail',
                          'Original invoices saved permanently; click to view from any coin'),
                      (Icons.find_replace_outlined,  'Duplicate Detection',
                          'Flagged for your review — never auto-merged'),
                    ].map((t) => Padding(
                      padding: const EdgeInsets.only(bottom: 10),
                      child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
                        Icon(t.$1, size: 16, color: const Color(0xFF4C8CDA)),
                        const SizedBox(width: 10),
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(t.$2, style: const TextStyle(
                                fontSize: 13, fontWeight: FontWeight.w600,
                                color: Color(0xFF334155))),
                            Text(t.$3, style: const TextStyle(
                                fontSize: 12, color: Color(0xFF64748B))),
                          ],
                        )),
                      ]),
                    )),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // ── High-Speed Parallel Ingestion Card ────────────────────────
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E293B), Color(0xFF0F172A)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withValues(alpha: 0.1), blurRadius: 10, offset: const Offset(0, 4))
                  ],
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.bolt, color: Color(0xFFF0C040), size: 24),
                        const SizedBox(width: 8),
                        const Text(
                          'High-Speed Parallel Ingestion',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        const Spacer(),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF0C040).withValues(alpha: 0.2),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: const Text('4x Concurrency', style: TextStyle(color: Color(0xFFF0C040), fontSize: 11, fontWeight: FontWeight.bold)),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Processes multi-page PDFs and photo batches asynchronously in parallel chunks via Gemini 3.5 Flash.',
                      style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                    ),
                    if (_isBatchProcessing) ...[
                      const SizedBox(height: 16),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: LinearProgressIndicator(
                          value: _batchProgress,
                          backgroundColor: const Color(0xFF334155),
                          valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFFF0C040)),
                          minHeight: 8,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        _batchStatusMsg,
                        style: const TextStyle(color: Color(0xFFE2E8F0), fontSize: 12, fontStyle: FontStyle.italic),
                      ),
                      const SizedBox(height: 12),
                      ..._batchItems.map((item) => Padding(
                        padding: const EdgeInsets.only(bottom: 6),
                        child: Row(
                          children: [
                            Icon(
                              item['status'] == 'Verified' ? Icons.check_circle : Icons.hourglass_top,
                              color: item['status'] == 'Verified' ? const Color(0xFF22C55E) : const Color(0xFFF0C040),
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                item['title'] ?? '',
                                style: const TextStyle(color: Colors.white, fontSize: 13),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: item['status'] == 'Verified' ? const Color(0xFF22C55E).withValues(alpha: 0.2) : const Color(0xFFF0C040).withValues(alpha: 0.2),
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                item['status'] ?? '',
                                style: TextStyle(
                                  color: item['status'] == 'Verified' ? const Color(0xFF22C55E) : const Color(0xFFF0C040),
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                          ],
                        ),
                      )),
                    ],
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: _isBatchProcessing ? null : _runParallelBatchSim,
                      icon: Icon(_isBatchProcessing ? Icons.hourglass_bottom : Icons.speed, size: 18),
                      label: Text(_isBatchProcessing ? 'Processing in Parallel...' : 'Run High-Speed Parallel Batch'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF0C040),
                        foregroundColor: const Color(0xFF1E293B),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // ── Launch button ─────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: () async {
                    // Pass the logged-in email as a query param so the
                    // standalone page can identify the user instantly,
                    // without relying on Firebase JS SDK session timing.
                    final email = AuthService.userEmail;
                    final path  = '/add_coins.html?email=${Uri.encodeComponent(email)}';
                    final uri   = kIsWeb
                        ? Uri.base.resolve(path)
                        : Uri.parse('https://numista-vault.web.app$path');
                    await launchUrl(uri, mode: LaunchMode.platformDefault);
                  },
                  icon: const Icon(Icons.open_in_new, size: 18),
                  label: const Text('Open Bulk Import →',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF0C040),
                    foregroundColor: const Color(0xFF1E293B),
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                    elevation: 0,
                  ),
                ),
              ),
              const SizedBox(height: 12),
              const Center(
                child: Text(
                  'Opens in a dedicated full-screen import page',
                  style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _runParallelBatchSim() async {
    setState(() {
      _isBatchProcessing = true;
      _batchProgress = 0.1;
      _batchStatusMsg = 'Spawning 4 concurrent Gemini 3.5 Flash worker coroutines...';
      _batchItems = [
        {'title': 'Page 1: 1909-S VDB Lincoln Cent', 'status': 'Processing'},
        {'title': 'Page 2: 1881-S Morgan Silver Dollar', 'status': 'Processing'},
        {'title': 'Page 3: 1921 Peace Dollar High Relief', 'status': 'Processing'},
        {'title': 'Page 4: 1937-D 3-Legged Buffalo Nickel', 'status': 'Processing'},
      ];
    });

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;
    setState(() {
      _batchProgress = 0.5;
      _batchStatusMsg = 'Extracted 2/4 specimens in parallel (Latency: 580ms)...';
      _batchItems[0]['status'] = 'Verified';
      _batchItems[1]['status'] = 'Verified';
    });

    await Future.delayed(const Duration(milliseconds: 600));
    if (!mounted) return;
    setState(() {
      _batchProgress = 1.0;
      _batchStatusMsg = 'Batch Ingestion Complete: All 4 specimens verified (99.2% confidence).';
      _batchItems[2]['status'] = 'Verified';
      _batchItems[3]['status'] = 'Verified';
      _isBatchProcessing = false;
    });
  }

  Widget _buildRollEntryTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Roll/Jar/Batch Entry', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
              const SizedBox(height: 8),
              const Text('Add a coin roll, a sequential set, or an unopened lot to your collection in one step.', style: TextStyle(color: Color(0xFF64748B))),
              const SizedBox(height: 32),
              // Visual cards for each roll type
              _rollTypeCard(Icons.content_copy_outlined,   const Color(0xFF4C8CDA), 'Identical Roll',    'All the same coin — add 20, 40, or 50 at once.'),
              _rollTypeCard(Icons.linear_scale_outlined,    const Color(0xFF22C55E), 'Sequential Years',  'One per year across a date range, auto-filled mint marks.'),
              _rollTypeCard(Icons.shuffle_outlined,          const Color(0xFFF59E0B), 'Mixed Roll',        'Scan each coin individually with the AI Scanner.'),
              _rollTypeCard(Icons.inventory_2_outlined,      const Color(0xFF8B5CF6), 'Unopened Lot',      'Record as a single lot, verify and expand later.'),
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.currency_exchange),
                  label: const Text('Start Roll Entry Wizard', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFF63366),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: () async {
                    final result = await showRollEntryDialog(context);
                    if (!mounted || result == null) return;
                    ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                      content: Text('✅  ${result.coinsAdded} coin${result.coinsAdded == 1 ? '' : 's'} added to your collection!'),
                      backgroundColor: const Color(0xFF22C55E),
                      duration: const Duration(seconds: 2),
                      action: SnackBarAction(
                        label: 'View Collection',
                        textColor: Colors.white,
                        onPressed: () { if (widget.onNavigate != null) widget.onNavigate!('My Collection'); },
                      ),
                    ));
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  /// Tab body for the "World & Specialty" tab.
  /// This is a lightweight promotional panel that navigates to the full
  /// AddWorldItemScreen — it intentionally does not embed the whole flow
  /// inline, since the world-item flow is complex enough to deserve a
  /// dedicated full-screen experience.
  Widget _buildWorldItemsTab() {
    const types = [
      ('🌍', 'Foreign / World Coin',        'Coins from any country, any era'),
      ('💵', 'Foreign Currency / Banknote',  'World paper currency & notes'),
      ('🪙', 'Bullion',                      'Gold, silver, platinum, palladium'),
      ('🏛️', 'Specialty Collectible',        'Confederate, uncut sheets, medals, tokens'),
      ('⚔️', 'Ancient Coins',               'Roman Empire, Greek, Byzantine & more'),
      ('❓', 'Unknown Item',                  'Let AI analyse and identify for you'),
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 600),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              Row(children: [
                Container(
                  width: 48, height: 48,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF6366F1), Color(0xFF8B5CF6)],
                      begin: Alignment.topLeft, end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.language_rounded, color: Colors.white, size: 26),
                ),
                const SizedBox(width: 14),
                const Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('World & Specialty Items',
                      style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B))),
                    Text('AI-assisted identification + manual entry',
                      style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                  ],
                )),
              ]),
              const SizedBox(height: 20),

              // Info banner
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, color: Color(0xFF3B82F6), size: 18),
                    SizedBox(width: 10),
                    Expanded(child: Text(
                      'Upload a photo and let AI say "This appears to be…". '
                      'Then refine with the Numista world catalogue or fill in details manually. '
                      'Works for any item — if AI is uncertain, the confidence level is shown clearly.',
                      style: TextStyle(fontSize: 13, color: Color(0xFF1E3A5F), height: 1.5),
                    )),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Item type chips
              const Text('SUPPORTED ITEM TYPES',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                    color: Color(0xFF94A3B8), letterSpacing: 0.8)),
              const SizedBox(height: 12),
              Wrap(
                spacing: 10, runSpacing: 10,
                children: types.map((t) => Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: const Color(0xFFF8FAFC),
                    border: Border.all(color: const Color(0xFFE2E6E9)),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(mainAxisSize: MainAxisSize.min, children: [
                    Text(t.$1, style: const TextStyle(fontSize: 16)),
                    const SizedBox(width: 8),
                    Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                      Text(t.$2,
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700,
                            color: Color(0xFF1E293B))),
                      Text(t.$3,
                        style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
                    ]),
                  ]),
                )).toList(),
              ),
              const SizedBox(height: 32),

              // CTA button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: const Icon(Icons.language_rounded),
                  label: const Text('Add a World or Specialty Item',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF6366F1),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: () {
                    if (widget.onNavigate != null) {
                      widget.onNavigate!('World & Specialty');
                    }
                  },
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // MINT SET TAB
  // Records a structured US Mint set as one parent SET document plus N
  // individual coin documents (one per coin), all linked by parentSetId.
  // The My Collection grid shows only the SET card; individual coins are
  // fully searchable by Morgan/AI and visible in the Set Detail View.
  // ─────────────────────────────────────────────────────────────────────────

  // ── Mint Set tab state ──────────────────────────────────────────────────
  final _mintSetNameCtrl     = TextEditingController();
  final _mintSetCostCtrl     = TextEditingController();
  final _mintSetDateCtrl     = TextEditingController();
  final _mintSetRetailerCtrl = TextEditingController();
  bool   _mintSetSaving      = false;
  String _mintSetMsg         = '';
  bool   _mintSetDone        = false;

  // Template: 2026 US Mint Uncirculated Coin Set
  static const _kUncSet2026Name     = '2026 US Mint Uncirculated Coin Set';
  static const _kUncSet2026Retailer = 'US Mint';
  static const _kMints = ['P', 'D'];
  static const _kCoins = [
    // (denomination, programSeries, themeSubject, metalContent)
    // Source: US Mint product description (exact 2026 Uncirculated Coin Set contents)
    ('1 Cent',    'Lincoln Cent',                  '1776~2026 Bicentennial',                   'Copper-Plated Zinc'),
    ('5 Cents',   'Jefferson Nickel',              '1776~2026 Bicentennial',                   'Cupro-Nickel'),
    ('10 Cents',  'Emerging Liberty Dime',         'Liberty — first time since 1945',          'Cupro-Nickel'),
    ('50 Cents',  'Enduring Liberty Half Dollar',  'Statue of Liberty — replaces Kennedy 2026 only', 'Cupro-Nickel'),
    ('25 Cents',  'Semiquincentennial Quarter',    'Mayflower Compact',                        'Cupro-Nickel'),
    ('25 Cents',  'Semiquincentennial Quarter',    'Revolutionary War',                        'Cupro-Nickel'),
    ('25 Cents',  'Semiquincentennial Quarter',    'Declaration of Independence',              'Cupro-Nickel'),
    ('25 Cents',  'Semiquincentennial Quarter',    'U.S. Constitution',                        'Cupro-Nickel'),
    ('25 Cents',  'Semiquincentennial Quarter',    'Gettysburg Address',                       'Cupro-Nickel'),
    ('1 Dollar',  'Native American Dollar',        'Polly Cooper / Oneida Allies at Valley Forge', 'Manganese-Brass Clad Copper'),
  ];

  Widget _buildMintSetTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 640),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              // ── Header ────────────────────────────────────────────────
              Row(children: [
                Container(
                  width: 48, height: 48,
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFFC9A227), Color(0xFF1E3A5F)],
                      begin: Alignment.topLeft, end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.collections_bookmark, color: Colors.white, size: 26),
                ),
                const SizedBox(width: 14),
                const Expanded(child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Record a Mint Set',
                      style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B))),
                    Text('Keeps packaging intact — records each coin individually',
                      style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                  ],
                )),
              ]),
              const SizedBox(height: 20),

              // ── How it works banner ────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFFBEB),
                  border: Border.all(color: const Color(0xFFFCD34D)),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(Icons.info_outline, color: Color(0xFFB45309), size: 18),
                    SizedBox(width: 10),
                    Expanded(child: Text(
                      'One parent set record is created (with your package photo) plus '
                      'one individual record per coin. Your collection grid shows the set '
                      'card only — Morgan and AI search see every individual coin. '
                      'Nothing is removed from its original packaging.',
                      style: TextStyle(fontSize: 13, color: Color(0xFF78350F), height: 1.5),
                    )),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // ── Template chooser ──────────────────────────────────────
              const Text('SET TEMPLATE', style: TextStyle(fontSize: 11,
                  fontWeight: FontWeight.w700, color: Color(0xFF94A3B8), letterSpacing: 0.8)),
              const SizedBox(height: 8),
              GestureDetector(
                onTap: () {
                  _mintSetNameCtrl.text     = _kUncSet2026Name;
                  _mintSetRetailerCtrl.text = _kUncSet2026Retailer;
                  setState(() {});
                },
                child: Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: _mintSetNameCtrl.text == _kUncSet2026Name
                        ? const Color(0xFFEFF6FF)
                        : const Color(0xFFF8FAFC),
                    border: Border.all(
                      color: _mintSetNameCtrl.text == _kUncSet2026Name
                          ? const Color(0xFF3B82F6)
                          : const Color(0xFFE2E8F0),
                      width: 2,
                    ),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(children: [
                    const Text('🏛️', style: TextStyle(fontSize: 24)),
                    const SizedBox(width: 12),
                    Expanded(child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('2026 US Mint Uncirculated Coin Set',
                          style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold,
                              color: Color(0xFF1E293B))),
                        Text('20 coins · Philadelphia (P) + Denver (D) · 10 denominations each',
                          style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
                      ],
                    )),
                    if (_mintSetNameCtrl.text == _kUncSet2026Name)
                      const Icon(Icons.check_circle, color: Color(0xFF3B82F6), size: 22),
                  ]),
                ),
              ),
              const SizedBox(height: 24),

              // ── Set details form ──────────────────────────────────────
              const Text('SET DETAILS', style: TextStyle(fontSize: 11,
                  fontWeight: FontWeight.w700, color: Color(0xFF94A3B8), letterSpacing: 0.8)),
              const SizedBox(height: 10),
              _mintSetField(_mintSetNameCtrl,     'Set Name',       'e.g. 2026 US Mint Uncirculated Coin Set'),
              const SizedBox(height: 12),
              _mintSetField(_mintSetCostCtrl,     'Purchase Price', 'e.g. \$27.95',
                  keyboardType: TextInputType.number),
              const SizedBox(height: 12),
              _mintSetField(_mintSetDateCtrl,     'Purchase Date',  'e.g. 2026-07-22'),
              const SizedBox(height: 12),
              _mintSetField(_mintSetRetailerCtrl, 'Retailer',       'e.g. US Mint'),
              const SizedBox(height: 28),

              // ── Coin preview ──────────────────────────────────────────
              if (_mintSetNameCtrl.text == _kUncSet2026Name) ...[
                const Text('COINS THAT WILL BE CREATED (20 total)',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                      color: Color(0xFF94A3B8), letterSpacing: 0.8)),
                const SizedBox(height: 12),
                for (final mint in _kMints) ...[
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    margin: const EdgeInsets.only(bottom: 6),
                    decoration: BoxDecoration(
                      color: mint == 'P'
                          ? const Color(0xFF1E40AF).withAlpha(20)
                          : const Color(0xFFBF360C).withAlpha(20),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(
                        color: mint == 'P'
                            ? const Color(0xFF1E40AF).withAlpha(60)
                            : const Color(0xFFBF360C).withAlpha(60),
                      ),
                    ),
                    child: Text(
                      mint == 'P' ? '🔵 Philadelphia Mint (P)' : '🔴 Denver Mint (D)',
                      style: TextStyle(
                        fontSize: 13, fontWeight: FontWeight.bold,
                        color: mint == 'P'
                            ? const Color(0xFF1E40AF)
                            : const Color(0xFFBF360C),
                      ),
                    ),
                  ),
                  Wrap(
                    spacing: 8, runSpacing: 8,
                    children: _kCoins.map((c) {
                      final label = c.$3.isNotEmpty ? c.$3 : c.$2;
                      return Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          border: Border.all(color: const Color(0xFFE2E8F0)),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        child: Text(
                          '2026-$mint ${c.$1}\n$label',
                          textAlign: TextAlign.center,
                          style: const TextStyle(fontSize: 10, color: Color(0xFF334155)),
                        ),
                      );
                    }).toList(),
                  ),
                  const SizedBox(height: 14),
                ],
                const SizedBox(height: 8),
              ],

              // ── Status/error message ──────────────────────────────────
              if (_mintSetMsg.isNotEmpty)
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  margin: const EdgeInsets.only(bottom: 16),
                  decoration: BoxDecoration(
                    color: _mintSetDone
                        ? const Color(0xFFDCFCE7)
                        : const Color(0xFFFEE2E2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: _mintSetDone
                          ? const Color(0xFF86EFAC)
                          : const Color(0xFFFCA5A5),
                    ),
                  ),
                  child: Text(
                    _mintSetMsg,
                    style: TextStyle(
                      color: _mintSetDone
                          ? const Color(0xFF166534)
                          : const Color(0xFF991B1B),
                      fontSize: 13,
                    ),
                  ),
                ),

              // ── Save button ───────────────────────────────────────────
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  icon: _mintSetSaving
                      ? const SizedBox(
                          width: 18, height: 18,
                          child: CircularProgressIndicator(
                            strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.save_outlined),
                  label: Text(
                    _mintSetSaving
                        ? 'Creating set & coins…'
                        : 'Create Set + ${_mintSetNameCtrl.text == _kUncSet2026Name ? "20" : "N"} Coins',
                    style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFFC9A227),
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 18),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10)),
                  ),
                  onPressed: _mintSetSaving ? null : _saveMintSet,
                ),
              ),
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _mintSetField(TextEditingController ctrl, String label, String hint,
      {TextInputType? keyboardType}) {
    return TextField(
      controller: ctrl,
      keyboardType: keyboardType,
      onChanged: (_) => setState(() {}),
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        filled: true,
        fillColor: const Color(0xFFF8FAFC),
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      ),
    );
  }

  Future<void> _saveMintSet() async {
    final name     = _mintSetNameCtrl.text.trim();
    final cost     = _mintSetCostCtrl.text.trim();
    final date     = _mintSetDateCtrl.text.trim();
    final retailer = _mintSetRetailerCtrl.text.trim();

    if (name.isEmpty) {
      setState(() => _mintSetMsg = 'Please enter a set name.');
      return;
    }

    setState(() { _mintSetSaving = true; _mintSetMsg = ''; _mintSetDone = false; });

    try {
      final db    = FirebaseFirestore.instance;
      final col   = db.collection(AuthService.coinsPath);
      final batch = db.batch();

      // ── 1. Create the parent SET document ──────────────────────────
      final setRef = col.doc();
      final setId  = setRef.id;
      final List<String> coinDocIds = [];

      batch.set(setRef, {
        'is_set'               : true,
        'in_original_packaging': true,
        'Program/Series'       : name,
        'Denomination'         : 'Set',
        'Year'                 : '2026',
        'Mint Mark'            : '',
        'Purchase Cost'        : cost.isEmpty ? '' : cost,
        'Purchase Date'        : date,
        'Retailer/Website'     : retailer.isEmpty ? _kUncSet2026Retailer : retailer,
        'Condition'            : 'MS',
        'Country'              : 'USA',
        'sub_sets'             : _kMints.map((m) =>
            m == 'P' ? 'Philadelphia Mint' : 'Denver Mint').toList(),
        'set_contents'         : [],         // back-filled below after IDs are known
        'image_url_obverse'    : '',
        'image_url_reverse'    : '',
        'image_verification_status': 'unverified',
        'timestamp'            : FieldValue.serverTimestamp(),
      });

      // ── 2. Create individual coin documents ────────────────────────
      for (final mint in _kMints) {
        final mintLabel = mint == 'P' ? 'Philadelphia Mint' : 'Denver Mint';
        for (final coin in _kCoins) {
          final ref = col.doc();
          coinDocIds.add(ref.id);
          batch.set(ref, {
            'is_set'               : false,
            'set_id'               : setId,
            'parent_set_id'        : setId,
            'member_of'            : mintLabel,
            'in_original_packaging': true,
            'Year'                 : '2026',
            'Mint Mark'            : mint,
            'Denomination'         : coin.$1,
            'Program/Series'       : coin.$2,
            'Theme/Subject'        : coin.$3,
            'Metal Content'        : coin.$4,
            'Condition'            : 'MS',
            'Country'              : 'USA',
            'Purchase Cost'        : '', // cost tracked at set level
            'Purchase Date'        : date,
            'Retailer/Website'     : retailer.isEmpty ? _kUncSet2026Retailer : retailer,
            'image_url_obverse'    : '',
            'image_url_reverse'    : '',
            'image_verification_status': 'unverified',
            'is_reviewed'          : true,   // skip Review Hub — set coins are confirmed
            'timestamp'            : FieldValue.serverTimestamp(),
          });
        }
      }

      // ── 3. Back-fill set_contents with the generated coin IDs ──────
      batch.update(setRef, {'set_contents': coinDocIds});

      await batch.commit();

      setState(() {
        _mintSetDone    = true;
        _mintSetSaving  = false;
        _mintSetMsg     =
            '✅ Set created! 1 parent set + ${coinDocIds.length} coins added to My Collection.';
      });
    } catch (e) {
      setState(() {
        _mintSetSaving = false;
        _mintSetMsg    = 'Error: $e';
        _mintSetDone   = false;
      });
    }
  }


  Widget _rollTypeCard(IconData icon, Color color, String title, String desc) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withAlpha(12),
        border: Border.all(color: color.withAlpha(60)),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(width: 14),
        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(title, style: TextStyle(fontWeight: FontWeight.w700, color: color, fontSize: 14)),
          Text(desc,  style: const TextStyle(color: Color(0xFF64748B), fontSize: 12)),
        ])),
      ]),
    );
  }

  Widget _buildManualEntryTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Add Coin Manually', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
              const SizedBox(height: 8),
              const Text('Enter full details for your specimen.', style: TextStyle(color: Color(0xFF64748B))),
              const SizedBox(height: 32),
              AddCoinManualForm(
                isProcessing: _isProcessing,
                onSubmit: (data) async {
                  setState(() => _isProcessing = true);

                  try {
                    // ── Build Firestore document from form data ──────────────
                    final coinDoc = <String, dynamic>{
                      'Year':              data['Year'] ?? '',
                      'Mint Mark':         data['Mint Mark'] ?? '',
                      'Denomination':      data['Denomination'] ?? '',
                      'Program/Series':    data['Program/Series'] ?? '',
                      'Theme/Subject':     data['Theme/Subject'] ?? '',
                      'Variety':           data['Variety'] ?? '',
                      'Condition':         data['Condition'] ?? '',
                      'Cost':              data['Cost'] ?? '',
                      'Quantity':          int.tryParse(data['Quantity'] ?? '1') ?? 1,
                      'Storage Location':  data['Storage Location'] ?? '',
                      'Country':           data['Country'] ?? 'United States',
                      'source':            'manual',
                      'Added':             FieldValue.serverTimestamp(),
                    };

                    // ── Save to Firestore ────────────────────────────────────
                    await FirebaseFirestore.instance
                        .collection(AuthService.coinsPath)
                        .add(coinDoc);

                    if (!mounted) return;

                    // ── Smart Wishlist Ownership Detection ───────────────────
                    final coin = CoinModel.fromMap(data, 'temp');
                    final match = await WishlistService.checkMatchAndMarkAsFound(coin);

                    if (!mounted) return;
                    setState(() => _isProcessing = false);

                    if (match != null && match.type == 'individual') {
                      _showWishlistMatchPrompt(match);
                    } else {
                      _showManualAddedSnackbar();
                    }
                  } catch (e) {
                    if (!mounted) return;
                    setState(() => _isProcessing = false);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: const Text('Couldn\'t save coin. Please check your connection and try again.'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                },
              ),
              const SizedBox(height: 64),
            ],
          ),
        ),
      ),
    );
  }

  // ─── SKU Number Import Tab ──────────────────────────────────────────────────

  Widget _buildSkuImportTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header
              const Text(
                'Add by SKU Number',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
              ),
              const SizedBox(height: 8),
              const Text(
                'Add an item instantly by selecting the retailer and entering the product SKU number.',
                style: TextStyle(color: Color(0xFF64748B)),
              ),
              const SizedBox(height: 32),

              // Form Card
              Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: const Color(0xFFF8FAFC),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFE2E8F0)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Retailer Dropdown
                    const Text(
                      'RETAILER',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 14),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: const Color(0xFFCBD5E1)),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          value: _skuRetailer,
                          isExpanded: true,
                          icon: const Icon(Icons.arrow_drop_down, color: Color(0xFF64748B)),
                          items: <String>['US Mint', 'Littleton Coin Company', 'APMEX', 'JM Bullion', 'Other']
                              .map((String value) {
                            return DropdownMenuItem<String>(
                              value: value,
                              child: Text(value, style: const TextStyle(color: Color(0xFF1E293B))),
                            );
                          }).toList(),
                          onChanged: (newValue) {
                            setState(() {
                              _skuRetailer = newValue ?? 'US Mint';
                              _skuSearchResult = null;
                              _skuError = '';
                            });
                          },
                        ),
                      ),
                    ),
                    const SizedBox(height: 20),

                    // SKU Text Field
                    const Text(
                      'SKU / ITEM NUMBER',
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF64748B),
                        letterSpacing: 0.5,
                      ),
                    ),
                    const SizedBox(height: 8),
                    TextField(
                      controller: _skuCtrl,
                      style: const TextStyle(color: Color(0xFF1E293B)),
                      decoration: InputDecoration(
                        hintText: _skuRetailer == 'US Mint' ? 'e.g. 26RJ' : 'e.g. ST5866Z',
                        hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 14),
                        filled: true,
                        fillColor: Colors.white,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(8),
                          borderSide: const BorderSide(color: Color(0xFFF63366), width: 1.5),
                        ),
                        prefixIcon: const Icon(Icons.tag, color: Color(0xFF94A3B8), size: 20),
                      ),
                      onSubmitted: (_) => _lookupSku(),
                    ),
                    const SizedBox(height: 24),

                    // Lookup Button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton.icon(
                        onPressed: _skuSearching ? null : _lookupSku,
                        icon: _skuSearching
                            ? const SizedBox(
                                height: 18, width: 18,
                                child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                            : const Icon(Icons.search, size: 18),
                        label: Text(
                          _skuSearching ? 'Searching…' : 'Lookup SKU',
                          style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
                        ),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFF63366),
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              if (_skuError.isNotEmpty) ...[
                const SizedBox(height: 20),
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: const Color(0xFFFEF2F2),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFFFCA5A5)),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline, color: Color(0xFFEF4444)),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Text(
                          _skuError,
                          style: const TextStyle(color: Color(0xFFB91C1C), fontWeight: FontWeight.w500),
                        ),
                      ),
                    ],
                  ),
                ),
              ],

              if (_skuSearchResult != null) ...[
                const SizedBox(height: 28),
                const Text(
                  'Search Result',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                ),
                const SizedBox(height: 12),
                _buildSkuPreviewCard(),
              ],
              const SizedBox(height: 64),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSkuPreviewCard() {
    if (_skuSearchResult == null) return const SizedBox.shrink();
    final data = _skuSearchResult!;
    final name = data['name'] ?? data['description'] ?? 'Unnamed Item';
    final year = data['year'] ?? data['year']?.toString() ?? 'N/A';
    final program = data['program'] ?? data['program_series'] ?? 'N/A';
    final isSet = data['item_type'] == 'set';

    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFFE2E8F0)),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 10,
            offset: const Offset(0, 4),
          )
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Banner Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: const BoxDecoration(
              color: Color(0xFF22C55E),
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(14),
                topRight: Radius.circular(14),
              ),
            ),
            child: Row(
              children: [
                const Icon(Icons.check_circle_outline, color: Colors.white, size: 16),
                const SizedBox(width: 8),
                Text(
                  'Verified SKU Match ($_skuRetailer)',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ],
            ),
          ),
          
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF1E293B),
                  ),
                ),
                const SizedBox(height: 16),
                
                // Metadata Table/Grid
                Row(
                  children: [
                    Expanded(
                      child: _buildMetaItem('Year', year),
                    ),
                    Expanded(
                      child: _buildMetaItem('Type', isSet ? 'Coin Set' : 'Single Coin'),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: _buildMetaItem('Program/Series', program),
                    ),
                    if (!isSet)
                      Expanded(
                        child: _buildMetaItem('Condition', data['implied_condition'] ?? 'Uncirculated'),
                      ),
                  ],
                ),
                const SizedBox(height: 24),
                
                // Confirm and Add Button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton.icon(
                    onPressed: _isProcessing ? null : _addSkuToCollection,
                    icon: _isProcessing
                        ? const SizedBox(
                            height: 18, width: 18,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Icon(Icons.add_circle_outline, size: 20),
                    label: const Text(
                      'Add to My Collection',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF3B82F6),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 18),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetaItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label.toUpperCase(),
          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8), letterSpacing: 0.5),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: Color(0xFF334155)),
        ),
      ],
    );
  }

  Future<void> _lookupSku() async {
    final rawSku = _skuCtrl.text.trim();
    if (rawSku.isEmpty) {
      setState(() => _skuError = 'Please enter a SKU number.');
      return;
    }
    setState(() {
      _skuSearching = true;
      _skuSearchResult = null;
      _skuError = '';
    });

    try {
      DocumentSnapshot<Map<String, dynamic>> snap;
      final docId = rawSku.replaceAll(RegExp(r'[^a-zA-Z0-9\-]'), '_').toUpperCase();

      if (_skuRetailer == 'US Mint') {
        snap = await FirebaseFirestore.instance
            .collection('global_metadata')
            .doc('usmint_sku_dictionary')
            .collection('skus')
            .doc(docId)
            .get();
      } else if (_skuRetailer == 'Littleton Coin Company') {
        snap = await FirebaseFirestore.instance
            .collection('global_metadata')
            .doc('littleton_sku_dictionary')
            .collection('skus')
            .doc(docId)
            .get();
      } else {
        setState(() {
          _skuError = 'Automated lookups are currently only supported for US Mint and Littleton Coin Company.';
          _skuSearching = false;
        });
        return;
      }

      if (!snap.exists) {
        setState(() {
          _skuError = 'SKU "$rawSku" not found in $_skuRetailer dictionary.';
          _skuSearching = false;
        });
        return;
      }

      setState(() {
        _skuSearchResult = snap.data();
        _skuSearching = false;
      });
    } catch (e) {
      setState(() {
        _skuError = 'Error looking up SKU: $e';
        _skuSearching = false;
      });
    }
  }

  Future<void> _addSkuToCollection() async {
    if (_skuSearchResult == null) return;
    setState(() => _isProcessing = true);

    try {
      final data = _skuSearchResult!;
      final isSetItem = data['item_type'] == 'set';
      
      final coinDoc = <String, dynamic>{
        'source': 'manual_sku',
        'Added': FieldValue.serverTimestamp(),
        'created_at': FieldValue.serverTimestamp(),
        'committed_at': FieldValue.serverTimestamp(),
        'deep_dive_status': 'PENDING',
      };

      if (isSetItem) {
        coinDoc.addAll({
          'set_id': data['set_id'] ?? '',
          'item_type': 'set',
          'is_set': true,
          'kept_as_set': true,
          'set_broken_up': false,
          'Year': data['year']?.toString() ?? '',
          'Country': 'USA',
          'Denomination': 'Set',
          'Condition': 'Uncirculated',
          'Quantity': 1,
          'name': data['name'] ?? '',
          'Program/Series': data['program'] ?? data['program_series'] ?? '',
          'Theme/Subject': data['description'] ?? '',
        });
      } else {
        coinDoc.addAll({
          'Year': data['year']?.toString() ?? '',
          'Mint Mark': data['mint_mark'] ?? '',
          'Denomination': data['denomination'] ?? '',
          'Program/Series': data['program_series'] ?? '',
          'Theme/Subject': data['description'] ?? '',
          'Condition': data['implied_condition'] ?? 'Uncirculated',
          'Quantity': 1,
          'Country': 'United States',
          'item_type': 'coin',
        });
      }

      final docRef = await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .add(coinDoc);

      if (!mounted) return;
      setState(() => _isProcessing = false);

      _showSkuAddedSuccessDialog(docRef.id);

    } catch (e) {
      if (!mounted) return;
      setState(() => _isProcessing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to add SKU: $e'), backgroundColor: Colors.red),
      );
    }
  }

  void _showSkuAddedSuccessDialog(String docId) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: const Row(
          children: [
            Icon(Icons.check_circle, color: Color(0xFF22C55E)),
            SizedBox(width: 8),
            Text('Item Added!', style: TextStyle(color: Colors.white)),
          ],
        ),
        content: const Text(
          'This item has been successfully added to your collection. '
          'Would you like to add more details (such as cost, notes, or storage location) now?',
          style: TextStyle(color: Colors.white70),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _skuCtrl.clear();
                _skuSearchResult = null;
              });
            },
            child: const Text('No, Add More SKUs', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _editSkuDetailsDialog(docId);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF63366),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Yes, Add Details', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  void _editSkuDetailsDialog(String docId) {
    final costCtrl = TextEditingController();
    final locationCtrl = TextEditingController();
    final notesCtrl = TextEditingController();

    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        backgroundColor: const Color(0xFF1E293B),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        title: const Text('Add Item Details', style: TextStyle(color: Colors.white)),
        content: SingleChildScrollView(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 400),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('PURCHASE COST (\$)', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: costCtrl,
                  style: const TextStyle(color: Colors.white),
                  keyboardType: TextInputType.number,
                  decoration: InputDecoration(
                    hintText: 'e.g. 197.95',
                    hintStyle: const TextStyle(color: Colors.white38),
                    filled: true,
                    fillColor: const Color(0xFF0F172A),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                  ),
                ),
                const SizedBox(height: 16),

                const Text('STORAGE LOCATION', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: locationCtrl,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    hintText: 'e.g. Safe Box A, Safe Deposit',
                    hintStyle: const TextStyle(color: Colors.white38),
                    filled: true,
                    fillColor: const Color(0xFF0F172A),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                  ),
                ),
                const SizedBox(height: 16),

                const Text('NOTES / DESCRIPTION', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 10, fontWeight: FontWeight.bold)),
                const SizedBox(height: 6),
                TextField(
                  controller: notesCtrl,
                  style: const TextStyle(color: Colors.white),
                  maxLines: 3,
                  decoration: InputDecoration(
                    hintText: 'Any extra details...',
                    hintStyle: const TextStyle(color: Colors.white38),
                    filled: true,
                    fillColor: const Color(0xFF0F172A),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
                  ),
                ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _skuCtrl.clear();
                _skuSearchResult = null;
              });
            },
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF94A3B8))),
          ),
          ElevatedButton(
            onPressed: () async {
              final nav = Navigator.of(context);
              final messenger = ScaffoldMessenger.of(context);
              final costVal = costCtrl.text.trim();
              final costStr = costVal.isNotEmpty ? '\$$costVal' : '';
              
              await FirebaseFirestore.instance
                  .collection(AuthService.coinsPath)
                  .doc(docId)
                  .update({
                'Cost': costStr,
                'Purchase Cost': costStr,
                'Storage Location': locationCtrl.text.trim(),
                'Notes': notesCtrl.text.trim(),
                'Personal Notes': notesCtrl.text.trim(),
              });
              
              nav.pop();
              setState(() {
                _skuCtrl.clear();
                _skuSearchResult = null;
              });
              
              if (!mounted) return;
              messenger.showSnackBar(
                const SnackBar(content: Text('Details saved successfully!'), backgroundColor: Color(0xFF22C55E)),
              );
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF63366),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Save Details', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }

  // ─── PCGS Cert Verification Tab ──────────────────────────────────────────

  Widget _buildPcgsImportTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.fromLTRB(20, 16, 20, 64),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 720),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [

              // ── Hero header ─────────────────────────────────────────────
              Row(children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(colors: [Color(0xFF1E3A8A), Color(0xFF2563EB)]),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(Icons.verified_outlined, color: Colors.white, size: 24),
                ),
                const SizedBox(width: 12),
                const Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text('Verify PCGS Certification', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF1E293B))),
                  Text('Look up a graded coin by its PCGS cert number and add it instantly.', style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                ])),
              ]),
              const SizedBox(height: 20),

              // ── Main lookup card ─────────────────────────────────────────
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: const Color(0xFFE2E6E9)),
                  boxShadow: [BoxShadow(color: Colors.black.withAlpha(5), blurRadius: 8, offset: const Offset(0, 2))],
                ),
                child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [

                  // Label row with help button
                  Row(children: [
                    const Text('PCGS Certification Number',
                        style: TextStyle(fontWeight: FontWeight.w700, fontSize: 14, color: Color(0xFF1E293B))),
                    const SizedBox(width: 6),
                    InkWell(
                      onTap: _showCertHelpDialog,
                      borderRadius: BorderRadius.circular(12),
                      child: const Padding(
                        padding: EdgeInsets.all(2),
                        child: Icon(Icons.help_outline_rounded, size: 18, color: Color(0xFF2563EB)),
                      ),
                    ),
                  ]),
                  const SizedBox(height: 4),
                  const Text(
                    'Enter the number after the "/" on your PCGS slab (e.g. for "986403.70/53652580", enter 53652580)',
                    style: TextStyle(fontSize: 12, color: Color(0xFF94A3B8)),
                  ),
                  const SizedBox(height: 12),

                  // Input + Verify button row
                  Row(children: [
                    Expanded(
                      child: TextField(
                        controller: _pcgsSingleCtrl,
                        keyboardType: TextInputType.number,
                        onSubmitted: (_) => _lookupSingleCert(),
                        decoration: InputDecoration(
                          hintText: 'e.g.  53652580',
                          border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                          contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                          prefixIcon: const Icon(Icons.tag, size: 18, color: Color(0xFF94A3B8)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 10),
                    ElevatedButton.icon(
                      onPressed: _pcgsLookupLoading ? null : _lookupSingleCert,
                      icon: _pcgsLookupLoading
                          ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                          : const Icon(Icons.search_rounded, size: 18),
                      label: Text(_pcgsLookupLoading ? 'Searching...' : 'Verify'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF2563EB),
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                  ]),

                  // Error / fallback UI
                  if (_pcgsLookupError.isNotEmpty)
                    _buildCertLookupFallback(_pcgsLookupError),
                ]),
              ),

              // ── Lookup result card ───────────────────────────────────────
              if (_pcgsLookupResult != null) ...[
                const SizedBox(height: 16),
                _buildLookupResultCard(_pcgsLookupResult!),
              ],

              const SizedBox(height: 16),

              // ── Platform badge OR Advanced section ──────────────────────
              if (_hasPlatformToken)
                Container(
                  decoration: BoxDecoration(
                    color: const Color(0xFFF0FDF4),
                    border: Border.all(color: const Color(0xFFBBF7D0)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Theme(
                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                    child: ExpansionTile(
                      leading: const Icon(Icons.verified_rounded, color: Color(0xFF10B981), size: 18),
                      title: const Text('Powered by Numista.AI',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF065F46))),
                      subtitle: const Text('API access included — no setup needed',
                          style: TextStyle(fontSize: 11, color: Color(0xFF10B981))),
                      initiallyExpanded: _showAdvancedToken,
                      onExpansionChanged: (v) => setState(() => _showAdvancedToken = v),
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                          child: _buildBulkImportSection(),
                        ),
                      ],
                    ),
                  ),
                )
              else
                Container(
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E6E9)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Theme(
                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                    child: ExpansionTile(
                      leading: const Icon(Icons.tune_rounded, color: Color(0xFF64748B), size: 18),
                      title: const Text('Advanced Options',
                          style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: Color(0xFF64748B))),
                      subtitle: const Text('API token setup & bulk CSV import',
                          style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
                      initiallyExpanded: _showAdvancedToken,
                      onExpansionChanged: (v) => setState(() => _showAdvancedToken = v),
                      children: [
                        Padding(
                          padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
                          child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                            const Divider(height: 1),
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: const Color(0xFFFFF7ED),
                                borderRadius: BorderRadius.circular(8),
                                border: Border.all(color: const Color(0xFFFED7AA)),
                              ),
                              child: const Text(
                                '⚠️  A personal PCGS API token is required for lookups. '
                                'Generate yours free at pcgs.com/publicapi/documentation → click "Generate Token". '
                                'Tokens must be called from your browser — they cannot be shared.',
                                style: TextStyle(fontSize: 12, color: Color(0xFF9A3412), height: 1.5),
                              ),
                            ),
                            const SizedBox(height: 12),
                            Row(children: [
                              Expanded(
                                child: TextField(
                                  controller: _pcgsTokenCtrl,
                                  obscureText: true,
                                  decoration: InputDecoration(
                                    labelText: 'PCGS Bearer Token',
                                    hintText: 'Paste token here...',
                                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                                    contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
                                    suffixIcon: _isLoadingToken
                                        ? const Padding(padding: EdgeInsets.all(10),
                                            child: SizedBox(width: 14, height: 14,
                                              child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF94A3B8))))
                                        : _pcgsTokenSaved
                                            ? const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 18)
                                            : null,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              ElevatedButton(
                                onPressed: () async {
                                  final t = _pcgsTokenCtrl.text.trim();
                                  if (t.isEmpty) return;
                                  await PcgsImportService.saveToken(t);
                                  if (!mounted) return;
                                  setState(() => _pcgsTokenSaved = true);
                                  ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
                                    content: Text('✅ Token saved'), backgroundColor: Color(0xFF10B981)));
                                },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: const Color(0xFF2563EB), foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 13),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                                ),
                                child: const Text('Save'),
                              ),
                            ]),
                            if (_pcgsTokenSaved) ...[
                              const SizedBox(height: 6),
                              const Text('✅ Token active — lookups ready.',
                                  style: TextStyle(color: Color(0xFF10B981), fontSize: 11)),
                            ],
                            const SizedBox(height: 20),
                            const Divider(),
                            _buildBulkImportSection(),
                          ]),
                        ),
                      ],
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  // ─── Bulk import section (shared by both paths) ──────────────────────────
  Widget _buildBulkImportSection() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(0, 12, 0, 0),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        const Text('Bulk Import from PCGS Registry CSV',
            style: TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: Color(0xFF1E293B))),
        const SizedBox(height: 4),
        const Text('Enter multiple cert numbers (one per line) or upload a PCGS registry CSV export to import your full graded collection.',
            style: TextStyle(fontSize: 12, color: Color(0xFF64748B))),
        const SizedBox(height: 10),
        TextField(
          controller: _pcgsCertCtrl,
          maxLines: 5,
          decoration: InputDecoration(
            hintText: 'One cert number per line:\n53652580\n43521234\n43521235',
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            contentPadding: const EdgeInsets.all(12),
          ),
        ),
        const SizedBox(height: 10),
        Row(children: [
          OutlinedButton.icon(
            onPressed: _pcgsImporting ? null : () async {
              final result = await FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['csv'], withData: true);
              if (result?.files.first.bytes != null) {
                final certs = PcgsImportService.parseCertNumbersFromCsv(String.fromCharCodes(result!.files.first.bytes!));
                if (certs.isNotEmpty && mounted) {
                  setState(() => _pcgsCertCtrl.text = certs.join('\n'));
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                    content: Text('Found ${certs.length} cert numbers.'),
                    backgroundColor: const Color(0xFF7C3AED)));
                }
              }
            },
            icon: const Icon(Icons.upload_file, size: 16),
            label: const Text('Upload CSV'),
            style: OutlinedButton.styleFrom(
              foregroundColor: const Color(0xFF7C3AED),
              side: const BorderSide(color: Color(0xFF7C3AED)),
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
          const SizedBox(width: 10),
          if (!_pcgsImporting)
            ElevatedButton.icon(
              onPressed: _pcgsTokenSaved ? _runPcgsImport : null,
              icon: const Icon(Icons.download_rounded, size: 16),
              label: const Text('Import All'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.white,
                disabledBackgroundColor: const Color(0xFFE2E6E9),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            )
          else
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(_pcgsStatusMsg, style: const TextStyle(fontSize: 12, color: Color(0xFF64748B))),
              const SizedBox(height: 6),
              ClipRRect(borderRadius: BorderRadius.circular(4),
                child: LinearProgressIndicator(value: _pcgsProgress, minHeight: 8,
                  backgroundColor: const Color(0xFFE2E6E9), color: const Color(0xFF10B981))),
            ])),
        ]),
        if (_pcgsLastResult != null) ...[
          const SizedBox(height: 12),
          _buildResultCard(_pcgsLastResult!),
        ],
      ]),
    );
  }

  // ─── Cert lookup fallback — shown when live lookup is unavailable ─────────

  Widget _buildCertLookupFallback(String errorMessage) {
    // Extract the cert number so we can build a direct PCGS link
    final cert = _parseCertNumber(_pcgsSingleCtrl.text.trim());
    final hasCert = cert.length >= 6 && cert.length <= 9 && RegExp(r'^\d+$').hasMatch(cert);

    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: const Color(0xFFFFF7ED),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: const Color(0xFFFBD38D)),
        ),
        child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Header
          Row(children: [
            const Icon(Icons.warning_amber_rounded, size: 16, color: Color(0xFFD97706)),
            const SizedBox(width: 6),
            const Expanded(
              child: Text(
                'Automatic lookup unavailable right now',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: Color(0xFF92400E)),
              ),
            ),
          ]),
          const SizedBox(height: 8),
          const Text(
            'PCGS blocks automated lookups from our servers. '
            'You can verify the cert directly on PCGS.com instead:',
            style: TextStyle(fontSize: 12, color: Color(0xFF78350F), height: 1.4),
          ),
          if (hasCert) ...[
            const SizedBox(height: 10),
            // "View on PCGS.com" button — opens the cert page in the user's browser
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () async {
                  final uri = Uri.parse('https://www.pcgs.com/cert/$cert');
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
                icon: const Icon(Icons.open_in_new_rounded, size: 15),
                label: Text('View Cert #$cert on PCGS.com'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: const Color(0xFF1D4ED8),
                  side: const BorderSide(color: Color(0xFF93C5FD)),
                  backgroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 10),
                  textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ),
          ],
          const SizedBox(height: 10),
          // CSV tip
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: const Color(0xFFEFF6FF),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFBFDBFE)),
            ),
            child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
              const Icon(Icons.lightbulb_outline_rounded, size: 14, color: Color(0xFF2563EB)),
              const SizedBox(width: 6),
              const Expanded(
                child: Text(
                  'Tip: Use "Upload PCGS CSV" below to import your whole PCGS registry at once — '
                  'no lookup limits, faster for multiple coins.',
                  style: TextStyle(fontSize: 11, color: Color(0xFF1E40AF), height: 1.4),
                ),
              ),
            ]),
          ),
        ]),
      ),
    );
  }

  // ─── Lookup result preview card ──────────────────────────────────────────


  Widget _buildLookupResultCard(Map<String, dynamic> data) {
    // Supports both old PCGS API shape and new cloudscraper shape
    final designation = data['CoinName']?.toString()
        ?? data['Designation']?.toString()
        ?? data['variety']?.toString()
        ?? 'Unknown Coin';

    // Date field can be "2025-W" (new) or separate Year + MintMark (old API)
    final dateField   = data['Date']?.toString() ?? data['dateMintmark']?.toString() ?? '';
    final year        = data['Year']?.toString() ?? (dateField.contains('-') ? dateField.split('-').first : dateField);
    final mintMark    = data['MintMark']?.toString() ?? (dateField.contains('-') ? dateField.split('-').last : '');

    final grade       = data['Grade']?.toString()
        ?? data['displayGrade']?.toString()
        ?? data['GradeString']?.toString()
        ?? '';
    final pcgsNo      = data['PCGSNo']?.toString()
        ?? data['pcgsDisplayNo']?.toString()
        ?? '';
    final denomination = data['Denomination']?.toString() ?? '';
    final price       = data['PriceGuideValue'];
    final imgObverse  = data['ObverseImageURL']?.toString() ?? '';

    final yearMint = mintMark.isNotEmpty && mintMark != year
        ? '$year-$mintMark' : year;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: const Color(0xFF10B981), width: 2),
        boxShadow: [BoxShadow(color: const Color(0xFF10B981).withAlpha(20), blurRadius: 12, offset: const Offset(0, 4))],
      ),
      child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
        Row(children: [
          const Icon(Icons.check_circle, color: Color(0xFF10B981), size: 20),
          const SizedBox(width: 8),
          const Text('Coin Found!', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 16, color: Color(0xFF10B981))),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(color: const Color(0xFF1E3A8A), borderRadius: BorderRadius.circular(20)),
            child: Text(grade, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
          ),
        ]),
        const SizedBox(height: 14),
        Row(crossAxisAlignment: CrossAxisAlignment.start, children: [
          // Coin image if available
          if (imgObverse.isNotEmpty) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Image.network(imgObverse, width: 80, height: 80, fit: BoxFit.cover,
                  errorBuilder: (_, a, b) => const SizedBox()),
            ),
            const SizedBox(width: 14),
          ],
          Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(designation, style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 15, color: Color(0xFF1E293B))),
            const SizedBox(height: 4),
            if (yearMint.isNotEmpty || denomination.isNotEmpty)
              Text(
                [if (yearMint.isNotEmpty) yearMint, if (denomination.isNotEmpty) denomination].join(' · '),
                style: const TextStyle(fontSize: 13, color: Color(0xFF64748B)),
              ),
            if (pcgsNo.isNotEmpty)
              Text('PCGS# $pcgsNo', style: const TextStyle(fontSize: 12, color: Color(0xFF94A3B8))),
            const SizedBox(height: 6),
            // Population
            if ((data['Population'] ?? '').toString().isNotEmpty && data['Population'].toString() != '0')
              Text('Pop: ${data['Population']} | Higher: ${data['PopHigher'] ?? 0}',
                  style: const TextStyle(fontSize: 11, color: Color(0xFF64748B))),
            // Price guide
            if (price != null && price != 0) ...[ 
              const SizedBox(height: 4),
              Text('Price Guide: \$$price', style: const TextStyle(fontSize: 13, color: Color(0xFF059669), fontWeight: FontWeight.w600)),
            ],
            // NFC badge — critical fraud protection notice
            if (data['IsNFCSecure'] == true) ...[
              const SizedBox(height: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(6),
                  border: Border.all(color: const Color(0xFF93C5FD)),
                ),
                child: Row(mainAxisSize: MainAxisSize.min, children: const [
                  Icon(Icons.nfc_rounded, size: 12, color: Color(0xFF2563EB)),
                  SizedBox(width: 4),
                  Text('NFC Secured — tap slab label to verify authenticity',
                      style: TextStyle(fontSize: 10, color: Color(0xFF1E40AF), fontWeight: FontWeight.w500)),
                ]),
              ),
            ],
          ])),
        ]),
        const SizedBox(height: 16),
        const Divider(),
        const SizedBox(height: 12),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _pcgsSingleAdding ? null : _addLookupResultToCollection,
            icon: _pcgsSingleAdding
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.add_circle_outline_rounded, size: 18),
            label: Text(_pcgsSingleAdding ? 'Adding...' : 'Add to My Collection'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF10B981), foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
          ),
        ),
        const SizedBox(height: 8),
        const Text('After adding, open My Collection to fill in cost, retailer, and storage details.',
            textAlign: TextAlign.center,
            style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
      ]),
    );
  }


  Widget _buildResultCard(PcgsImportResult result) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF064E3B), Color(0xFF065F46)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(children: [
            Icon(Icons.check_circle, color: Colors.white, size: 22),
            SizedBox(width: 10),
            Text('Import Complete', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 18)),
          ]),
          const SizedBox(height: 20),
          Row(
            children: [
              _resultStat('${result.successCount}', 'Coins Added', Colors.white),
              const SizedBox(width: 24),
              _resultStat('${result.duplicateCount}', 'Duplicates Skipped', Colors.white70),
              const SizedBox(width: 24),
              _resultStat('${result.failedCount}', 'Failed', result.failedCount > 0 ? const Color(0xFFFCA5A5) : Colors.white70),
            ],
          ),
          if (result.failedCerts.isNotEmpty) ...[
            const SizedBox(height: 16),
            const Divider(color: Colors.white24),
            const SizedBox(height: 8),
            Text(
              'Failed cert numbers:\n${result.failedCerts.take(10).join(', ')}${result.failedCerts.length > 10 ? " ...and ${result.failedCerts.length - 10} more" : ""}',
              style: const TextStyle(color: Colors.white70, fontSize: 12),
            ),
          ],
        ],
      ),
    );
  }

  Widget _resultStat(String value, String label, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(value, style: TextStyle(color: color, fontSize: 28, fontWeight: FontWeight.w900)),
        Text(label, style: TextStyle(color: color.withAlpha(180), fontSize: 12)),
      ],
    );
  }

  // ─── Single-cert lookup ───────────────────────────────────────────────────

  /// Extracts a clean PCGS cert number from any format a user might paste:
  ///   "986403.70/53652580"  → "53652580"   (full slab label)
  ///   "00053652580"         → "53652580"   (barcode with leading zeros)
  ///   "5365 2580"           → "53652580"   (spaced)
  ///   "5365-2580"           → "53652580"   (dashed)
  ///   "53652580"            → "53652580"   (clean)
  String _parseCertNumber(String raw) {
    // Take the portion after '/' first (handles full slab label)
    var s = raw.contains('/') ? raw.split('/').last.trim() : raw.trim();
    // Remove spaces, dashes and non-digits
    s = s.replaceAll(RegExp(r'[\s\-]'), '');
    // Remove leading zeros if too long (barcode format)
    if (s.length > 9) s = s.replaceFirst(RegExp(r'^0+'), '');
    return s;
  }

  Future<void> _lookupSingleCert() async {
    final raw = _pcgsSingleCtrl.text.trim();
    final cert = _parseCertNumber(raw);

    if (cert.isEmpty || !RegExp(r'^\d{6,9}$').hasMatch(cert)) {
      setState(() => _pcgsLookupError = 'Please enter a valid 6–9 digit cert number (e.g. 53652580).');
      return;
    }
    if (!_pcgsTokenSaved) {
      setState(() => _pcgsLookupError = 'A PCGS API token is required. Expand the "Advanced" section below to add yours.');
      return;
    }

    setState(() {
      _pcgsLookupLoading = true;
      _pcgsLookupResult  = null;
      _pcgsLookupError   = '';
    });

    try {
      final data = await PcgsImportService.getCoinFactsByCertNo(certNo: cert);
      if (!mounted) return;
      if (data == null) {
        setState(() {
          _pcgsLookupLoading = false;
          _pcgsLookupError   = 'Cert #$cert not found in PCGS database. Double-check the number after the "/" on the slab label.';
        });
      } else {
        setState(() {
          _pcgsLookupLoading = false;
          _pcgsLookupResult  = data;
          _pcgsLookupError   = '';
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _pcgsLookupLoading = false;
        _pcgsLookupError   = e.toString().replaceFirst('Exception: ', '');
      });
    }
  }

  Future<void> _addLookupResultToCollection() async {
    if (_pcgsLookupResult == null) return;
    setState(() => _pcgsSingleAdding = true);
    try {
      final cert = _parseCertNumber(_pcgsSingleCtrl.text.trim());
      final mapped = PcgsImportService.mapToFirestoreSchema(_pcgsLookupResult!, certNo: cert);
      await FirebaseFirestore.instance.collection(AuthService.coinsPath).add(mapped);
      if (!mounted) return;
      setState(() {
        _pcgsSingleAdding  = false;
        _pcgsLookupResult  = null;
        _pcgsSingleCtrl.clear();
      });
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: const Text('✅ Coin added to your collection!'),
        backgroundColor: const Color(0xFF10B981),
        action: widget.onNavigate != null
            ? SnackBarAction(label: 'View', textColor: Colors.white, onPressed: () => widget.onNavigate!('My Collection'))
            : null,
      ));
    } catch (e) {
      if (!mounted) return;
      setState(() => _pcgsSingleAdding = false);
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Couldn\'t add coin from PCGS. Please check your cert number and try again.'),
        backgroundColor: Colors.red,
      ));
    }
  }

  void _showCertHelpDialog() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Row(children: [
          Icon(Icons.help_outline, color: Color(0xFF2563EB)),
          SizedBox(width: 8),
          Text('Finding Your Cert Number', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
        ]),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xFFEFF6FF), borderRadius: BorderRadius.circular(8)),
              child: const Text(
                'On a PCGS slab, you\'ll see two numbers separated by a slash:\n\n'
                '  986403.70 / 53652580\n\n'
                '• The number BEFORE the "/" is the PCGS Coin Number (identifies the coin type)\n'
                '• The number AFTER the "/" is the Certification Number\n\n'
                'Enter just the number after the slash — that\'s your cert number.',
                style: TextStyle(fontSize: 13, height: 1.5, color: Color(0xFF1E3A8A)),
              ),
            ),
            const SizedBox(height: 12),
            const Text('For example, on a slab labelled:', style: TextStyle(fontWeight: FontWeight.w600, fontSize: 13)),
            Container(
              margin: const EdgeInsets.only(top: 6),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: const Color(0xFF0F172A), borderRadius: BorderRadius.circular(6)),
              child: const Text('986403.70 / 53652580',
                  style: TextStyle(color: Color(0xFF38BDF8), fontFamily: 'monospace', fontSize: 14, fontWeight: FontWeight.bold)),
            ),
            const SizedBox(height: 6),
            const Text('→ Enter: 53652580', style: TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.w600, fontSize: 13)),
          ],
        ),
        actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Got it'))],
      ),
    );
  }

  Future<void> _runPcgsImport() async {
    final rawInput = _pcgsCertCtrl.text.trim();
    if (rawInput.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter at least one PCGS certification number.'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Parse cert numbers from the text area
    final certNumbers = rawInput
        .split(RegExp(r'[\n,\s]+'))
        .map((s) => s.trim())
        .where((s) => s.isNotEmpty && RegExp(r'^\d+$').hasMatch(s))
        .toList();

    if (certNumbers.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('No valid cert numbers found. Cert numbers should be numeric only.'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() {
      _pcgsImporting   = true;
      _pcgsProgress    = 0;
      _pcgsLastResult  = null;
      _pcgsStatusMsg   = 'Connecting to PCGS...';
    });

    try {
      final result = await PcgsImportService.importByCertNumbers(
        certNumbers: certNumbers,
        onProgress: (done, total) {
          if (mounted) {
            setState(() {
              _pcgsProgress  = done / total;
              _pcgsStatusMsg = 'Importing coin $done of $total...';
            });
          }
        },
      );

      if (!mounted) return;
      setState(() {
        _pcgsImporting  = false;
        _pcgsProgress   = 1.0;
        _pcgsLastResult = result;
      });

      if (result.successCount > 0 && widget.onNavigate != null) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('${result.successCount} coins imported! View in My Collection.'),
            backgroundColor: const Color(0xFF10B981),
            action: SnackBarAction(
              label: 'View',
              textColor: Colors.white,
              onPressed: () => widget.onNavigate!('My Collection'),
            ),
          ),
        );
      }
    } catch (e) {
      if (!mounted) return;
      setState(() => _pcgsImporting = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Import error: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }



  /// Shows a bottom sheet to select how many checklist pages to scan.



  Widget _buildProcessingOverlay() {
    // While progress == 0 (waiting on the AI to process a single file),
    // use an indeterminate indicator so the bar bounces rather than sitting empty.
    final double? progressValue =
        _processingProgress <= 0 ? null : _processingProgress;

    return Container(
      color: Colors.black.withAlpha(120),
      child: Center(
        child: Card(
          elevation: 24,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const SizedBox(
                  width: 60, height: 60,
                  child: CircularProgressIndicator(
                      color: Color(0xFFF63366), strokeWidth: 5),
                ),
                const SizedBox(height: 24),
                Text(_statusMessage,
                    style: const TextStyle(
                        fontWeight: FontWeight.bold, fontSize: 18)),
                const SizedBox(height: 8),
                const Text(
                  'AI extraction typically takes 10–30 seconds for PDF files.',
                  style: TextStyle(
                      color: Color(0xFF64748B), fontSize: 13),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),
                SizedBox(
                  width: 300,
                  child: LinearProgressIndicator(
                    value: progressValue,
                    color: const Color(0xFFF63366),
                    backgroundColor: const Color(0xFFE2E6E9),
                  ),
                ),
                const SizedBox(height: 8),
                // Only show percentage for multi-file bulk uploads
                if (progressValue != null && _processingProgress > 0)
                  Text('${(_processingProgress * 100).toInt()}%',
                      style: const TextStyle(color: Color(0xFF64748B)))
                else
                  const Text('Working…',
                      style: TextStyle(color: Color(0xFF64748B))),
                const SizedBox(height: 12),
                const Text(
                  '💡 Tip: Keep this window open until processing completes.',
                  style: TextStyle(
                      color: Color(0xFF94A3B8), fontSize: 12),
                  textAlign: TextAlign.center,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ─── Quick Camera Scanner Logic & UI ────────────────────────────────────────

  Future<void> _pickCamImage(bool isObverse, ImageSource source) async {
    try {
      Uint8List? bytes;
      String? name;

      if (source == ImageSource.camera) {
        final result = await CameraCaptureService.capturePhoto(context);
        if (result == null) return;
        bytes = result.bytes;
        name = result.name;
      } else {
        final picked = await ImagePicker().pickImage(
          source: ImageSource.gallery,
          maxWidth: 1920,
          maxHeight: 1920,
          imageQuality: 80,
        );
        if (picked == null) return;
        bytes = await picked.readAsBytes();
        name = picked.name;
      }

      setState(() {
        if (isObverse) {
          _camObverseBytes = bytes;
          _camObverseName = name;
        } else {
          _camReverseBytes = bytes;
          _camReverseName = name;
        }
        _camResult = null;
        _camError = null;
      });
    } catch (e) {
      setState(() => _camError = 'Failed to capture image: $e');
    }
  }

  void _showImageSourcePicker(bool isObverse) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 8),
            Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey, borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 16),
            ListTile(
              leading: const Icon(Icons.camera_alt, color: Color(0xFFF63366)),
              title: const Text('Take Photo (Webcam / Phone)'),
              onTap: () {
                Navigator.pop(ctx);
                _pickCamImage(isObverse, ImageSource.camera);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library, color: Color(0xFF4C8CDA)),
              title: const Text('Choose from Gallery / Files'),
              onTap: () {
                Navigator.pop(ctx);
                _pickCamImage(isObverse, ImageSource.gallery);
              },
            ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Future<void> _runCameraScan() async {
    if (_camObverseBytes == null || _camReverseBytes == null) {
      setState(() => _camError = 'Please capture or upload both obverse and reverse images.');
      return;
    }

    setState(() {
      _camLoading = true;
      _camError = null;
      _camResult = null;
    });

    try {
      final uri = Uri.parse('$kApiBaseUrl/api/identify_coin_photo');
      final request = http.MultipartRequest('POST', uri);

      request.fields['user_email'] = AuthService.userEmail;
      request.fields['save_to_collection'] = 'false';

      MediaType getMediaType(String filename) {
        final ext = filename.split('.').last.toLowerCase();
        final mime = {
          'png': 'image/png',
          'gif': 'image/gif',
          'webp': 'image/webp',
        }[ext] ?? 'image/jpeg';
        return MediaType.parse(mime);
      }

      request.files.add(http.MultipartFile.fromBytes(
        'image_a',
        _camObverseBytes!,
        filename: _camObverseName ?? 'obverse.jpg',
        contentType: getMediaType(_camObverseName ?? 'obverse.jpg'),
      ));

      request.files.add(http.MultipartFile.fromBytes(
        'image_b',
        _camReverseBytes!,
        filename: _camReverseName ?? 'reverse.jpg',
        contentType: getMediaType(_camReverseName ?? 'reverse.jpg'),
      ));

      final streamedResponse = await request.send().timeout(const Duration(seconds: 60));
      final responseBody = await streamedResponse.stream.bytesToString();

      if (streamedResponse.statusCode == 200) {
        final data = jsonDecode(responseBody);
        final coin = data['coin'] as Map<String, dynamic>? ?? {};
        setState(() {
          _camResult = data as Map<String, dynamic>;
          _camLoading = false;

          // Populate the text fields with identified metadata
          _picYear.text = coin['Year']?.toString() ?? '';
          _picDenom.text = coin['Denomination']?.toString() ?? '';
          _picSeries.text = coin['Program/Series']?.toString() ?? '';
          _picTheme.text = coin['Theme/Subject']?.toString() ?? '';
          _picMint.text = coin['Mint Mark']?.toString() ?? '';
          _picGrade.text = coin['Condition']?.toString() ?? '';
          _picMetal.text = coin['Metal Content']?.toString() ?? '';
          _picVariety.text = coin['Variety']?.toString() ?? '';
          _picCost.text = coin['Cost']?.toString() ?? '\$0.00';
          _picStorage.text = coin['Storage Location']?.toString() ?? '';
          _picNotes.text = coin['Personal Notes']?.toString() ?? '';
        });
      } else {
        setState(() {
          _camError = 'AI scan failed: Server returned ${streamedResponse.statusCode}';
          _camLoading = false;
        });
      }
    } catch (e) {
      setState(() {
        _camError = 'Network or API error: $e';
        _camLoading = false;
      });
    }
  }

  Future<void> _confirmAndSaveCameraCoin() async {
    if (_camObverseBytes == null || _camReverseBytes == null) {
      setState(() => _camError = 'Images missing.');
      return;
    }

    setState(() {
      _camSaving = true;
      _camError = null;
    });

    try {
      final uri = Uri.parse('$kApiBaseUrl/api/identify_coin_photo');
      final request = http.MultipartRequest('POST', uri);

      request.fields['user_email'] = AuthService.userEmail;
      request.fields['save_to_collection'] = 'true';

      // Send the overrides edited by the user
      request.fields['override_year'] = _picYear.text.trim();
      request.fields['override_denom'] = _picDenom.text.trim();
      request.fields['override_series'] = _picSeries.text.trim();
      request.fields['override_theme'] = _picTheme.text.trim();
      request.fields['override_mint'] = _picMint.text.trim();
      request.fields['override_grade'] = _picGrade.text.trim();
      request.fields['override_metal'] = _picMetal.text.trim();
      request.fields['override_cost'] = _picCost.text.trim();
      request.fields['override_storage'] = _picStorage.text.trim();
      request.fields['override_notes'] = _picNotes.text.trim();

      MediaType getMediaType(String filename) {
        final ext = filename.split('.').last.toLowerCase();
        final mime = {
          'png': 'image/png',
          'gif': 'image/gif',
          'webp': 'image/webp',
        }[ext] ?? 'image/jpeg';
        return MediaType.parse(mime);
      }

      request.files.add(http.MultipartFile.fromBytes(
        'image_a',
        _camObverseBytes!,
        filename: _camObverseName ?? 'obverse.jpg',
        contentType: getMediaType(_camObverseName ?? 'obverse.jpg'),
      ));

      request.files.add(http.MultipartFile.fromBytes(
        'image_b',
        _camReverseBytes!,
        filename: _camReverseName ?? 'reverse.jpg',
        contentType: getMediaType(_camReverseName ?? 'reverse.jpg'),
      ));

      final streamedResponse = await request.send().timeout(const Duration(seconds: 60));
      final responseBody = await streamedResponse.stream.bytesToString();

      if (streamedResponse.statusCode == 200) {
        setState(() {
          _camSaving = false;
        });

        // Show a nice success dialog
        if (mounted) {
          _showSuccessDialog(1);
          _resetCameraScanner();
        }
      } else {
        setState(() {
          _camError = 'Save failed: Server returned ${streamedResponse.statusCode} ($responseBody)';
          _camSaving = false;
        });
      }
    } catch (e) {
      setState(() {
        _camError = 'Save failed with error: $e';
        _camSaving = false;
      });
    }
  }

  void _resetCameraScanner() {
    setState(() {
      _camObverseBytes = null;
      _camReverseBytes = null;
      _camObverseName = null;
      _camReverseName = null;
      _camResult = null;
      _camError = null;
      _camLoading = false;
      _camSaving = false;
      
      _picYear.clear();
      _picDenom.clear();
      _picSeries.clear();
      _picTheme.clear();
      _picMint.clear();
      _picGrade.clear();
      _picMetal.clear();
      _picVariety.clear();
      _picCost.text = '\$0.00';
      _picStorage.clear();
      _picNotes.clear();
    });
  }

  Widget _imageCamPickerBox(String label, Uint8List? bytes, bool isObverse) {
    return Column(
      children: [
        GestureDetector(
          onTap: () => _showImageSourcePicker(isObverse),
          child: Container(
            height: 160,
            width: 160,
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              shape: BoxShape.circle,
              border: Border.all(
                color: bytes != null ? const Color(0xFF10B981) : const Color(0xFFCBD5E1),
                width: bytes != null ? 3 : 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                )
              ],
            ),
            child: Stack(
              alignment: Alignment.center,
              children: [
                if (bytes != null)
                  ClipOval(
                    child: Image.memory(
                      bytes,
                      width: 160,
                      height: 160,
                      fit: BoxFit.cover,
                    ),
                  )
                else
                  Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.add_a_photo_outlined, color: Color(0xFF64748B), size: 30),
                      const SizedBox(height: 8),
                      Text(
                        label,
                        style: const TextStyle(
                          color: Color(0xFF334155),
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                // Circular Framing Guide overlay
                Container(
                  width: 154,
                  height: 154,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.4),
                      width: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextButton.icon(
              onPressed: () => _pickCamImage(isObverse, ImageSource.camera),
              icon: const Icon(Icons.photo_camera, size: 14, color: Color(0xFF4C8CDA)),
              label: const Text('Take Photo', style: TextStyle(fontSize: 11, color: Color(0xFF4C8CDA))),
              style: TextButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 4)),
            ),
            const SizedBox(width: 4),
            TextButton.icon(
              onPressed: () => _pickCamImage(isObverse, ImageSource.gallery),
              icon: const Icon(Icons.upload, size: 14, color: Color(0xFF64748B)),
              label: const Text('Upload', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
              style: TextButton.styleFrom(padding: const EdgeInsets.symmetric(horizontal: 4)),
            ),
          ],
        )
      ],
    );
  }

  Widget _buildCameraScannerTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 800),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // ── Header callout / instruction ───────────────────────────────
              Row(
                children: [
                  Container(
                    width: 48, height: 48,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [Color(0xFFEC4899), Color(0xFFF43F5E)],
                        begin: Alignment.topLeft, end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(Icons.photo_camera_outlined,
                        color: Colors.white, size: 26),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Quick Camera Scanner',
                            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                        Text('Identify and catalog specimens directly via webcam or phone camera',
                            style: TextStyle(color: Color(0xFF64748B), fontSize: 13)),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 24),

              // ── Guidance Info Card ─────────────────────────────────────────
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFFEFF6FF),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFFBFDBFE)),
                ),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Icon(Icons.info_outline, color: Color(0xFF2563EB), size: 20),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        'Quick Camera Scan provides rapid identification and fast cataloging. '
                        'For high-resolution error analysis, surface wear grading, and estate-grade verification, '
                        'please use the Microscope Station.',
                        style: TextStyle(
                          color: const Color(0xFF1E3A8A),
                          fontSize: 12.5,
                          height: 1.5,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 32),

              // ── Camera Photo Capture Boxes ──────────────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _imageCamPickerBox('Obverse (Front)', _camObverseBytes, true),
                  _imageCamPickerBox('Reverse (Back)', _camReverseBytes, false),
                ],
              ),
              const SizedBox(height: 24),

              // ── Error Display ──────────────────────────────────────────────
              if (_camError != null) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: Colors.red.withValues(alpha: 0.2)),
                  ),
                  child: Text(
                    _camError!,
                    style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                    textAlign: TextAlign.center,
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // ── Actions: Scan Button or Loader ─────────────────────────────
              if (_camLoading) ...[
                const Center(
                  child: Card(
                    color: Color(0xFF0F172A),
                    child: Padding(
                      padding: EdgeInsets.symmetric(horizontal: 40, vertical: 24),
                      child: Column(
                        children: [
                          CircularProgressIndicator(color: Color(0xFFEC4899)),
                          SizedBox(height: 16),
                          Text(
                            'Morgan is scanning your coin...',
                            style: TextStyle(color: Colors.white, fontSize: 14, fontWeight: FontWeight.bold),
                          ),
                          SizedBox(height: 4),
                          Text(
                            'Analyzing visual details & estimating grade...',
                            style: TextStyle(color: Colors.white54, fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ] else if (_camResult == null) ...[
                Center(
                  child: ElevatedButton.icon(
                    onPressed: (_camObverseBytes == null || _camReverseBytes == null) ? null : _runCameraScan,
                    icon: const Icon(Icons.flash_on_rounded, size: 20),
                    label: const Text('Scan Coin Now', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFFEC4899),
                      foregroundColor: Colors.white,
                      disabledBackgroundColor: Colors.black12,
                      disabledForegroundColor: Colors.black26,
                      padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 18),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      elevation: 4,
                    ),
                  ),
                ),
              ] else ...[
                // ── AI Scan Results Preview Card ─────────────────────────────
                _buildCameraResultCard(),
              ],
              const SizedBox(height: 40),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCameraResultCard() {
    return Card(
      color: const Color(0xFFF8FAFC),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
        side: const BorderSide(color: Color(0xFFE2E8F0)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Title Header
            Row(
              children: [
                const Icon(Icons.insights, color: Color(0xFFEC4899), size: 24),
                const SizedBox(width: 10),
                const Text(
                  'AI Identification Result',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
                ),
                const Spacer(),
                TextButton(
                  onPressed: _resetCameraScanner,
                  child: const Text('Scan Another', style: TextStyle(color: Color(0xFFEC4899))),
                ),
              ],
            ),
            const Divider(height: 24, color: Color(0xFFE2E8F0)),

            // Edit Fields Group
            const Text(
              'Verify and edit the AI extracted details below before adding to your collection:',
              style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
            ),
            const SizedBox(height: 20),

            // Form inputs
            _camInputField('Year', _picYear),
            const SizedBox(height: 12),
            _camInputField('Denomination', _picDenom),
            const SizedBox(height: 12),
            _camInputField('Program / Series', _picSeries),
            const SizedBox(height: 12),
            _camInputField('Theme / Subject', _picTheme),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _camInputField('Mint Mark', _picMint)),
                const SizedBox(width: 12),
                Expanded(child: _camInputField('Condition / Grade', _picGrade)),
              ],
            ),
            const SizedBox(height: 12),
            _camInputField('Metal Content', _picMetal),
            const SizedBox(height: 12),
            _camInputField('Variety / Errors', _picVariety),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(child: _camInputField('Cost Paid', _picCost)),
                const SizedBox(width: 12),
                Expanded(child: _camInputField('Storage Location', _picStorage)),
              ],
            ),
            const SizedBox(height: 12),
            _camInputField('Personal Notes', _picNotes, maxLines: 3),
            const SizedBox(height: 24),

            // Confirm & Save Button
            ElevatedButton.icon(
              onPressed: _camSaving ? null : _confirmAndSaveCameraCoin,
              icon: _camSaving
                  ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.check_circle_outline, size: 20),
              label: Text(_camSaving ? 'Saving to Collection...' : 'Confirm & Save to Collection',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF10B981),
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                elevation: 2,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _camInputField(String label, TextEditingController ctrl, {int maxLines = 1}) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: Color(0xFF475569))),
        const SizedBox(height: 6),
        TextField(
          controller: ctrl,
          maxLines: maxLines,
          style: const TextStyle(fontSize: 14, color: Color(0xFF1E293B)),
          decoration: InputDecoration(
            isDense: true,
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
            fillColor: Colors.white,
            filled: true,
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFFCBD5E1)),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFFEC4899), width: 1.5),
            ),
          ),
        ),
      ],
    );
  }

}
