import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:image_picker/image_picker.dart';
import '../services/auth_service.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/services.dart' show rootBundle;
import '../widgets/add_coin_manual_form.dart';
import '../widgets/extraction_success_dialog.dart';
import '../widgets/scan_result_dialog.dart';
import '../services/wishlist_service.dart';
import '../services/checklist_scan_service.dart';
import '../models/coin_model.dart';
import '../models/program_model.dart';
import '../services/reference_service.dart';
import '../services/coin_programs_data.dart';
import 'package:printing/printing.dart';
import '../services/checklist_generator_service.dart';
import '../services/pcgs_import_service.dart';
import '../widgets/roll_entry_dialog.dart';
import 'package:url_launcher/url_launcher.dart';

class AddCoinsHub extends StatefulWidget {
  final Function(String)? onNavigate;
  const AddCoinsHub({super.key, this.onNavigate});

  @override
  State<AddCoinsHub> createState() => _AddCoinsHubState();
}

class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _isProcessing = false;
  double _processingProgress = 0;
  String _statusMessage = '';

  // Checklist scanner state
  CoinProgram? _selectedScanProgram;
  bool _isScanning = false;
  String _scanStatus = '';

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

  // Backend API URL
  final String _apiUrl = "https://numista-backend-568985927038.us-central1.run.app";

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 7, vsync: this);
    _loadSavedPcgsToken();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _pcgsTokenCtrl.dispose();
    _pcgsCertCtrl.dispose();
    _pcgsSingleCtrl.dispose();
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

  Future<void> _processFiles({required List<PlatformFile> files, required bool isInvoice}) async {
    setState(() {
      _isProcessing = true;
      _processingProgress = 0;
      _statusMessage = 'Starting processing...';
    });

    int totalItems = 0;
    final endpoint = isInvoice ? '/api/process_invoice' : '/api/import_spreadsheet';

    try {
      for (int i = 0; i < files.length; i++) {
        final file = files[i];
        if (!mounted) return;
        setState(() {
          _statusMessage = 'Processing ${file.name} (${i + 1}/${files.length})...';
          _processingProgress = i / files.length;
        });

        var request = http.MultipartRequest('POST', Uri.parse('$_apiUrl$endpoint'));
        request.fields['user_email'] = AuthService.userEmail;
        
        if (file.bytes != null) {
          request.files.add(http.MultipartFile.fromBytes(
            'file',
            file.bytes!,
            filename: file.name,
          ));
        }

        var streamedResponse = await request.send();
        var response = await http.Response.fromStream(streamedResponse);

        if (response.statusCode == 200) {
          final data = jsonDecode(response.body);
          totalItems += (data['extracted_items'] ?? data['count'] ?? 0) as int;
        }
      }

      if (!mounted) return;
      setState(() {
        _isProcessing = false;
        _processingProgress = 1.0;
      });

      _showSuccessDialog(totalItems);

    } catch (e) {
      if (!mounted) return;
      setState(() => _isProcessing = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('File processing failed. Please check the file format and try again.'),
          backgroundColor: Colors.red[700],
        ),
      );
    }
  }

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
              _buildSingleScanTab(),
              _buildBulkUploadTab(),
              _buildManualEntryTab(),
              _buildExcelImportTab(),
              _buildChecklistTab(),
              _buildPcgsImportTab(),
              _buildRollEntryTab(),
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
          Tab(text: 'Single Invoice Scan', icon: Icon(Icons.receipt_long, size: 20)),
          Tab(text: 'Bulk Upload', icon: Icon(Icons.auto_awesome_motion, size: 20)),
          Tab(text: 'Manual Entry', icon: Icon(Icons.edit_note, size: 20)),
          Tab(text: 'Excel/CSV Upload', icon: Icon(Icons.table_view, size: 20)),
          Tab(text: 'By Checklist', icon: Icon(Icons.fact_check, size: 20)),
          Tab(text: 'Import from PCGS', icon: Icon(Icons.shield_outlined, size: 20)),
          Tab(text: 'Roll / Batch', icon: Icon(Icons.currency_exchange, size: 20)),
        ],
      ),
    );
  }

  Widget _buildSingleScanTab() {
    return _buildUploadArea(
      title: 'Interactive Single Invoice Scan',
      description: 'Upload one PDF. AI will extract coins, varieties, and transaction data.',
      icon: Icons.cloud_upload_outlined,
      buttonLabel: 'Browse PDF',
      onPressed: () async {
        FilePickerResult? result = await FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['pdf'], withData: true);
        if (result != null) _processFiles(files: result.files, isInvoice: true);
      },
    );
  }

  Widget _buildBulkUploadTab() {
    return _buildUploadArea(
      title: 'Batch Processor',
      description: 'Upload multiple PDF invoices at once. We will process them in the background.',
      icon: Icons.topic_outlined,
      buttonLabel: 'Select Multiple PDFs',
      onPressed: () async {
        FilePickerResult? result = await FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['pdf'], withData: true, allowMultiple: true);
        if (result != null) _processFiles(files: result.files, isInvoice: true);
      },
    );
  }

  Widget _buildExcelImportTab() {
    return _buildUploadArea(
      title: 'Spreadsheet Ingestor',
      description: 'Upload Excel or CSV files. Vertex AI will auto-map your columns to our Golden Schema.',
      icon: Icons.grid_on,
      buttonLabel: 'Upload Spreadsheet',
      onPressed: () async {
        FilePickerResult? result = await FilePicker.pickFiles(type: FileType.custom, allowedExtensions: ['csv', 'xlsx', 'xls'], withData: true);
        if (result != null) _processFiles(files: result.files, isInvoice: false);
      },
    );
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
              const Text('Roll / Batch Entry', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
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

  Widget _buildChecklistTab() {
    return StreamBuilder<Map<String, List<CoinProgram>>>(
      stream: ReferenceService.getGroupedProgramsStream(),
      builder: (context, snapshot) {
        // Show spinner while Firestore is loading — don't fall back prematurely
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
              child: CircularProgressIndicator(color: Color(0xFFF63366)));
        }

        // Show error if stream failed
        if (snapshot.hasError) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_off_rounded,
                      size: 40, color: Color(0xFFF63366)),
                  const SizedBox(height: 12),
                  const Text('Could not load programs',
                      style: TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 6),
                  Text('${snapshot.error}',
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                          color: Color(0xFF64748B), fontSize: 12)),
                ],
              ),
            ),
          );
        }

        // Only use local fallback if Firestore truly returned nothing
        final allProgramsMap = (snapshot.data?.isNotEmpty == true)
            ? snapshot.data!
            : CoinProgramsData.usPrograms;
        final allPrograms = allProgramsMap.values.expand((e) => e).toList()
          ..sort((a, b) => a.name.compareTo(b.name));

        final isNarrow = MediaQuery.of(context).size.width < 600;

        return SingleChildScrollView(
          padding: EdgeInsets.all(isNarrow ? 16 : 32),
          child: Center(
            child: ConstrainedBox(
              constraints: BoxConstraints(maxWidth: isNarrow ? double.infinity : 700),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // ── Header ─────────────────────────────────────────────────
                  const Text('Checklist Scanner',
                      style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1E293B))),
                  const SizedBox(height: 8),
                  const Text(
                    'Print a checklist, check off your coins, then scan it back in. '
                    'Owned coins update your collection and missing coins go to your Wish List automatically.',
                    style: TextStyle(color: Color(0xFF64748B), fontSize: 14),
                  ),
                  const SizedBox(height: 32),

                  // ── Program Selector ────────────────────────────────────────
                  Container(
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(16),
                      border: Border.all(color: const Color(0xFFE2E6E9)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Step 1 — Select a Coin Program',
                            style: TextStyle(
                                fontSize: 15,
                                fontWeight: FontWeight.w700,
                                color: Color(0xFF1E293B))),
                        const SizedBox(height: 16),
                        DropdownButtonFormField<CoinProgram>(
                          // Safely resolve the selected value from the current list.
                          // If the stream emitted new objects and the old selection
                          // is no longer present, fall back to null to avoid assertion.
                          initialValue: _selectedScanProgram != null &&
                                  allPrograms.any((p) => p == _selectedScanProgram)
                              ? _selectedScanProgram
                              : null,
                          decoration: InputDecoration(
                            labelText: 'Coin Program',
                            border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(10)),
                            contentPadding: const EdgeInsets.symmetric(
                                horizontal: 16, vertical: 14),
                          ),
                          isExpanded: true,
                          items: allPrograms
                              .map((p) => DropdownMenuItem(
                                  value: p, child: Text(p.name)))
                              .toList(),
                          onChanged: (p) =>
                              setState(() => _selectedScanProgram = p),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  // ── Action Cards ────────────────────────────────────────────
                  Row(
                    children: [
                      // Print card
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.print_rounded,
                          color: const Color(0xFF2563EB),
                          title: 'Print Checklist',
                          subtitle:
                              'Generate a PDF checklist for the selected program.',
                          buttonLabel: 'Print PDF',
                          enabled: _selectedScanProgram != null,
                          onPressed: _selectedScanProgram == null
                              ? null
                              : () => _printChecklist(_selectedScanProgram!),
                        ),
                      ),
                      const SizedBox(width: 16),
                      // Scan card
                      Expanded(
                        child: _ActionCard(
                          icon: Icons.document_scanner_rounded,
                          color: const Color(0xFF10B981),
                          title: 'Scan Checklist',
                          subtitle:
                              'Photograph your completed checklist to sync your collection.',
                          buttonLabel:
                              _isScanning ? _scanStatus : 'Scan Now',
                          enabled:
                              _selectedScanProgram != null && !_isScanning,
                          isLoading: _isScanning,
                          onPressed: _selectedScanProgram == null || _isScanning
                              ? null
                              : () => _scanChecklist(_selectedScanProgram!),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // ── How it works ────────────────────────────────────────────
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: const Color(0xFFF0F9FF),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFBAE6FD)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Row(children: [
                          Icon(Icons.info_outline,
                              color: Color(0xFF0284C7), size: 18),
                          SizedBox(width: 8),
                          Text('How it works',
                              style: TextStyle(
                                  fontWeight: FontWeight.w700,
                                  color: Color(0xFF0C4A6E),
                                  fontSize: 14)),
                        ]),
                        const SizedBox(height: 12),
                        for (final step in [
                          ('1', 'Select a coin program above'),
                          ('2', 'Print the checklist PDF'),
                          ('3',
                              'Check off the coins you own with a pen'),
                          ('4',
                              'Tap "Scan Now" and photograph the page'),
                          ('5',
                              'Owned coins sync to your collection — unowned coins go to your Wish List'),
                        ])
                          Padding(
                            padding: const EdgeInsets.only(bottom: 6),
                            child: Row(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Container(
                                  width: 22,
                                  height: 22,
                                  alignment: Alignment.center,
                                  decoration: BoxDecoration(
                                    color: const Color(0xFF0284C7),
                                    borderRadius: BorderRadius.circular(11),
                                  ),
                                  child: Text(step.$1,
                                      style: const TextStyle(
                                          color: Colors.white,
                                          fontSize: 11,
                                          fontWeight: FontWeight.bold)),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Text(step.$2,
                                      style: const TextStyle(
                                          color: Color(0xFF0C4A6E),
                                          fontSize: 13)),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
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

  Future<void> _printChecklist(CoinProgram program) async {
    Uint8List? logoBytes;
    try {
      final data = await rootBundle.load('assets/logo_owl.png');
      logoBytes = data.buffer.asUint8List();
    } catch (_) {}
    final bytes = await ChecklistGeneratorService.generateChecklist(
        program,
        logoBytes: logoBytes);
    await Printing.layoutPdf(
      onLayout: (_) => bytes,
      name: '${program.name}_Checklist.pdf',
    );
  }

  Future<void> _scanChecklist(CoinProgram program) async {
    final userId = AuthService.currentUser?.uid;
    if (userId == null || userId.isEmpty) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('Please sign in to scan a checklist.'),
            backgroundColor: Colors.red),
      );
      return;
    }

    // ── Step 1: Ask how many pages ───────────────────────────────────────────
    final totalPages = await _pickPageCount();
    if (totalPages == null || !mounted) return;

    final picker = ImagePicker();
    final Map<String, dynamic> allCoins = {};
    double totalConfidence = 0;
    int pagesScanned = 0;

    // ── Step 2: Loop through each page ──────────────────────────────────────
    for (int pageNum = 1; pageNum <= totalPages; pageNum++) {
      if (!mounted) return;

      // Show prompt before picking each page
      final source = await _pickImageSource(
        title: totalPages == 1
            ? 'Scan Checklist'
            : 'Scan Page $pageNum of $totalPages',
      );
      if (source == null) break; // user cancelled this page

      final picked = await picker.pickImage(
        source: source,
        imageQuality: 92,
        maxWidth: 3000,
        maxHeight: 3000,
      );
      if (picked == null) break;

      setState(() {
        _isScanning = true;
        _scanStatus = totalPages == 1
            ? 'Analyzing...'
            : 'Analyzing page $pageNum of $totalPages...';
      });

      try {
        final result = await ChecklistScanService.scanChecklist(
          imageFile: File(picked.path),
          programId: program.id,
          userId: userId,
          pageNumber: pageNum,
          totalPages: totalPages,
        );

        if (!result.success) {
          if (!mounted) return;
          setState(() => _isScanning = false);
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
                content: Text('Page $pageNum failed: ${result.errorMessage ?? 'Unknown error'}'),
                backgroundColor: Colors.red.shade700),
          );
          return;
        }

        // Merge coins from this page into accumulated results
        allCoins.addAll(result.coins);
        totalConfidence += result.pageConfidence ?? 0;
        pagesScanned++;
      } catch (e) {
        if (!mounted) return;
        setState(() => _isScanning = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
              content: Text('Page $pageNum error: $e'),
              backgroundColor: Colors.red.shade700),
        );
        return;
      }
    }

    if (!mounted) return;
    setState(() => _isScanning = false);

    if (pagesScanned == 0) return;

    // ── Step 3: Show combined results ────────────────────────────────────────
    final combined = ScanResult(
      programId: program.id,
      userId: userId,
      coins: allCoins,
      pageConfidence: pagesScanned > 0 ? totalConfidence / pagesScanned : 0,
      firestoreWritten: true,
      wishlistAdded: 0, // individual pages already wrote to Firestore
    );

    await ScanResultDialog.show(
      context,
      result: combined,
      programName: program.name,
    );
  }

  /// Shows a bottom sheet to select how many checklist pages to scan.
  Future<int?> _pickPageCount() async {
    if (!mounted) return null;
    return showModalBottomSheet<int>(
      context: context,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 16),
            const Text('How many pages is your checklist?',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            const Text('Each page will be photographed separately.',
                style: TextStyle(fontSize: 13, color: Colors.grey)),
            const SizedBox(height: 16),
            for (final n in [1, 2, 3])
              ListTile(
                leading: CircleAvatar(
                  backgroundColor: const Color(0xFF0284C7),
                  child: Text('$n',
                      style: const TextStyle(
                          color: Colors.white, fontWeight: FontWeight.bold)),
                ),
                title: Text(n == 1 ? '1 page' : '$n pages',
                    style: const TextStyle(fontWeight: FontWeight.w600)),
                onTap: () => Navigator.pop(context, n),
              ),
            const SizedBox(height: 8),
          ],
        ),
      ),
    );
  }

  Future<ImageSource?> _pickImageSource({String title = 'Scan Checklist'}) async {
    if (!mounted) return null;
    return showModalBottomSheet<ImageSource>(
      context: context,
      shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(20))),
      builder: (_) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const SizedBox(height: 12),
            Container(
                width: 40,
                height: 4,
                decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2))),
            const SizedBox(height: 16),
            Text(title,
                style:
                    const TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFF10B981),
                child: Icon(Icons.camera_alt, color: Colors.white),
              ),
              title: const Text('Take Photo'),
              subtitle: const Text('Use camera for best results'),
              onTap: () => Navigator.pop(context, ImageSource.camera),
            ),
            ListTile(
              leading: const CircleAvatar(
                backgroundColor: Color(0xFF2563EB),
                child: Icon(Icons.photo_library, color: Colors.white),
              ),
              title: const Text('Choose from Gallery'),
              subtitle: const Text('Select a previously taken photo'),
              onTap: () => Navigator.pop(context, ImageSource.gallery),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadArea({required String title, required String description, required IconData icon, required String buttonLabel, required VoidCallback onPressed}) {
    return Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 800),
        child: Container(
          margin: const EdgeInsets.all(32),
          padding: const EdgeInsets.all(48),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(color: const Color(0xFFE2E6E9)),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 64, color: const Color(0xFF64748B).withAlpha(100)),
              const SizedBox(height: 24),
              Text(title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
              const SizedBox(height: 12),
              Text(description, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xFF64748B), fontSize: 16)),
              const SizedBox(height: 32),
              ElevatedButton.icon(
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF63366),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 20),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                ),
                onPressed: onPressed,
                icon: const Icon(Icons.add),
                label: Text(buttonLabel, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
              ),
              const SizedBox(height: 16),
              const Text('Limit 200MB per file • PDF', style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProcessingOverlay() {
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
                  child: CircularProgressIndicator(color: Color(0xFFF63366), strokeWidth: 5),
                ),
                const SizedBox(height: 24),
                Text(_statusMessage, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                const SizedBox(height: 12),
                SizedBox(
                  width: 300,
                  child: LinearProgressIndicator(value: _processingProgress, color: const Color(0xFFF63366), backgroundColor: const Color(0xFFE2E6E9)),
                ),
                const SizedBox(height: 8),
                Text('${(_processingProgress * 100).toInt()}%', style: const TextStyle(color: Color(0xFF64748B))),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Compact action card used in the Checklist tab for Print / Scan actions.
class _ActionCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String subtitle;
  final String buttonLabel;
  final bool enabled;
  final bool isLoading;
  final VoidCallback? onPressed;

  const _ActionCard({
    required this.icon,
    required this.color,
    required this.title,
    required this.subtitle,
    required this.buttonLabel,
    required this.enabled,
    this.isLoading = false,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
            color: enabled ? color.withValues(alpha: 0.3) : const Color(0xFFE2E6E9)),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withValues(alpha: 0.04),
              blurRadius: 8,
              offset: const Offset(0, 2)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withValues(alpha: enabled ? 0.12 : 0.05),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon,
                color: enabled ? color : Colors.grey.shade400, size: 24),
          ),
          const SizedBox(height: 12),
          Text(title,
              style: TextStyle(
                  fontSize: 15,
                  fontWeight: FontWeight.w700,
                  color: enabled
                      ? const Color(0xFF1E293B)
                      : Colors.grey.shade400)),
          const SizedBox(height: 4),
          Text(subtitle,
              style: TextStyle(
                  fontSize: 12,
                  color: enabled
                      ? const Color(0xFF64748B)
                      : Colors.grey.shade300)),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: enabled ? onPressed : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: color,
                foregroundColor: Colors.white,
                disabledBackgroundColor: Colors.grey.shade200,
                elevation: 0,
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
                padding: const EdgeInsets.symmetric(vertical: 12),
              ),
              child: isLoading
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                          strokeWidth: 2, color: Colors.white))
                  : Text(buttonLabel,
                      style: const TextStyle(fontWeight: FontWeight.w600)),
            ),
          ),
        ],
      ),
    );
  }
}
