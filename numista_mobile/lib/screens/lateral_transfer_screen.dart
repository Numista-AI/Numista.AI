import 'dart:io';
import 'dart:typed_data';
import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:path_provider/path_provider.dart';
import 'package:printing/printing.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/coin_model.dart';
import '../models/transfer_model.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import '../services/lateral_transfer_service.dart';

class LateralTransferScreen extends StatefulWidget {
  final String userId;
  final List<CoinModel> itemsToTransfer;
  final String initialTab; // 'send' or 'claim'

  const LateralTransferScreen({
    super.key,
    required this.userId,
    required this.itemsToTransfer,
    this.initialTab = 'send',
  });

  @override
  State<LateralTransferScreen> createState() => _LateralTransferScreenState();
}

class _LateralTransferScreenState extends State<LateralTransferScreen> {
  final LateralTransferService _transferService = LateralTransferService();
  final TextEditingController _recipientEmailController = TextEditingController();
  final TextEditingController _searchController = TextEditingController();
  final TextEditingController _claimTransferIdController = TextEditingController();
  final TextEditingController _claimPinController = TextEditingController();

  String _activeTab = 'send'; // 'send', 'sell_outside', 'sold_history', 'claim'

  // Mode 3 Direct Sale Fields
  final TextEditingController _salePriceController = TextEditingController();
  final TextEditingController _saleFeesController = TextEditingController(text: '0.00');
  final TextEditingController _saleDateController = TextEditingController();
  final TextEditingController _buyerRefController = TextEditingController();
  final TextEditingController _saleNotesController = TextEditingController();
  String _salesVenue = 'eBay';
  CoinModel? _selectedCoinToSell;
  int _qtyToSell = 1;
  bool _isSelling = false;
  bool _isUndoing = false;

  // Sold Inventory & Undo State (CoS Lock L3)
  List<Map<String, dynamic>> _soldItems = [];
  bool _isLoadingSoldItems = false;
  String? _soldItemsError;

  // Partial transfer quantities (Mode 1 G1)
  final Map<String, int> _itemTransferQuantities = {};

  bool get _isDark => Theme.of(context).brightness == Brightness.dark;
  Color get _scaffoldBg => _isDark ? const Color(0xFF0F172A) : const Color(0xFFF4F4F2);
  Color get _cardBg => _isDark ? const Color(0xFF1E293B) : Colors.white;
  Color get _borderCol => _isDark ? const Color(0xFF334155) : const Color(0xFFE2E8F0);
  Color get _textPrimary => _isDark ? Colors.white : const Color(0xFF0F172A);
  Color get _textSecondary => _isDark ? const Color(0xFFCBD5E1) : const Color(0xFF5A5C69);
  Color get _inputFill => _isDark ? const Color(0xFF1E293B) : const Color(0xFFF8FAFC);

  // Default to FALSE so nothing is scrubbed unless sender explicitly checks the toggle
  bool _hideCostBasis = false;
  bool _hidePrivateNotes = false;
  bool _hideStorageLocation = false;
  bool _hideInvoices = false;

  bool _isLoading = false;
  bool _isClaiming = false;
  bool _isFetchingInventory = false;
  String? _fetchError;

  List<CoinModel> _allCoins = [];
  Set<String> _selectedCoinIds = {};
  String _searchQuery = '';

  TransferModel? _createdTransfer;

  @override
  void initState() {
    super.initState();
    _activeTab = widget.initialTab;
    _saleDateController.text = DateTime.now().toIso8601String().substring(0, 10);
    if (widget.itemsToTransfer.isNotEmpty) {
      _allCoins = List.from(widget.itemsToTransfer);
      _selectedCoinIds = _allCoins.map((c) => c.id).toSet();
      _selectedCoinToSell = _allCoins.first;
    } else {
      _loadInventoryFromFirestore();
    }
    if (_activeTab == 'sold_history') {
      _loadSoldItems();
    }
  }

  @override
  void dispose() {
    _recipientEmailController.dispose();
    _searchController.dispose();
    _claimTransferIdController.dispose();
    _claimPinController.dispose();
    _salePriceController.dispose();
    _saleFeesController.dispose();
    _saleDateController.dispose();
    _buyerRefController.dispose();
    _saleNotesController.dispose();
    super.dispose();
  }

  Future<void> _loadInventoryFromFirestore() async {
    setState(() {
      _isFetchingInventory = true;
      _fetchError = null;
    });

    try {
      List<CoinModel> coins = [];

      // Auth-primary gate: a real non-anonymous Firebase user always reads from
      // Firestore, regardless of the in-memory demo flag. The demo branch is only
      // reached when there is no authenticated user (Browse Demo path, State B).
      final authUser = FirebaseAuth.instance.currentUser;
      final isRealUser = authUser != null && !authUser.isAnonymous;

      if (!isRealUser && GuestSeedService.isBrowseDemoMode) {
        final snap = await GuestSeedService.getDemoCoinsStream().first;
        coins = snap.docs.map((doc) => CoinModel.fromFirestore(doc)).toList();
      } else {
        final userEmailOrUid = widget.userId.trim().isNotEmpty
            ? widget.userId.trim()
            : AuthService.userEmail;

        final path = 'users/$userEmailOrUid/coins';
        var snap = await FirebaseFirestore.instance.collection(path).get();

        if (snap.docs.isEmpty && path != AuthService.coinsPath) {
          snap = await FirebaseFirestore.instance.collection(AuthService.coinsPath).get();
        }

        coins = snap.docs
            .map((doc) => CoinModel.fromFirestore(doc))
            .where((c) => c.transferStatus != 'pending' && c.transferStatus != 'transferred' && c.transferStatus != 'claimed')
            .toList();
      }

      coins.sort((a, b) {
        final tA = a.timestamp ?? DateTime(1970);
        final tB = b.timestamp ?? DateTime(1970);
        return tB.compareTo(tA);
      });

      setState(() {
        _allCoins = coins;
        _selectedCoinIds = coins.map((c) => c.id).toSet();
        _isFetchingInventory = false;
      });
    } catch (e) {
      setState(() {
        _isFetchingInventory = false;
        _fetchError = 'Failed to load inventory items: $e';
      });
    }
  }

  List<CoinModel> get _filteredCoins {
    final queryText = _searchQuery.trim().toLowerCase();
    if (queryText.isEmpty) return _allCoins;

    final tokens = queryText.split(RegExp(r'\s+')).where((t) => t.isNotEmpty).toList();

    return _allCoins.where((c) {
      final fullSearch = [
        c.year,
        c.programSeries,
        c.denomination,
        c.mintMark,
        c.variety,
        c.themeSubject,
        c.metalContent,
        c.country,
        c.condition,
        c.gradingService,
        c.certificationNumber,
        c.originalDescription,
        c.personalNotes,
        c.storageLocation,
        c.retailer,
      ].join(' ').toLowerCase();

      return tokens.every((token) {
        if (fullSearch.contains(token)) return true;
        if (token.startsWith('\$') && token.length > 1) {
          final rawNum = token.substring(1);
          if (fullSearch.contains(rawNum)) return true;
        }
        return false;
      });
    }).toList();
  }

  List<CoinModel> get _selectedCoins {
    return _allCoins.where((c) => _selectedCoinIds.contains(c.id)).toList();
  }

  Future<void> _initiateTransfer() async {
    final selected = _selectedCoins;
    if (selected.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please select at least one item to transfer.'),
          backgroundColor: Colors.amber,
        ),
      );
      return;
    }

    final userIdToUse = widget.userId.trim().isNotEmpty
        ? widget.userId.trim()
        : AuthService.userEmail;

    setState(() => _isLoading = true);
    try {
      final transfer = await _transferService.initiateTransfer(
        userId: userIdToUse,
        itemIds: selected.map((c) => c.id).toList(),
        recipientEmail: _recipientEmailController.text.trim().isNotEmpty
            ? _recipientEmailController.text.trim()
            : null,
        itemQuantities: _itemTransferQuantities.isNotEmpty ? _itemTransferQuantities : null,
        privacyToggles: {
          'hide_cost_basis': _hideCostBasis,
          'hide_private_notes': _hidePrivateNotes,
          'hide_storage_location': _hideStorageLocation,
          'hide_invoices': _hideInvoices,
        },
      );

      setState(() {
        _createdTransfer = transfer;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error initiating transfer: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  Future<void> _claimTransfer() async {
    final transferId = _claimTransferIdController.text.trim();
    final pin = _claimPinController.text.trim();

    if (transferId.isEmpty || pin.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter both Transfer ID and 6-Digit Claim PIN.')),
      );
      return;
    }

    final userIdToUse = widget.userId.trim().isNotEmpty ? widget.userId.trim() : AuthService.userEmail;

    setState(() => _isClaiming = true);
    try {
      final res = await _transferService.claimTransfer(
        userId: userIdToUse,
        transferId: transferId,
        claimPin: pin,
      );
      setState(() => _isClaiming = false);
      if (!mounted) return;

      final count = res['result']?['items_claimed_count'] ?? 0;

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: _cardBg,
          title: Text('Transfer Adopted Successfully!', style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold)),
          content: Text('$count item(s) were added to your collection vault with full provenance records.',
              style: TextStyle(color: _textSecondary)),
          actions: [
            ElevatedButton(
              onPressed: () {
                Navigator.pop(ctx);
                _claimTransferIdController.clear();
                _claimPinController.clear();
              },
              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0284C7)),
              child: const Text('Done', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
            )
          ],
        ),
      );
    } catch (e) {
      setState(() => _isClaiming = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Claim failed: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _scaffoldBg,
      appBar: AppBar(
        title: Text(
          'Lateral Transfer — Passport Protocol',
          style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold),
        ),
        backgroundColor: _cardBg,
        iconTheme: IconThemeData(color: _textPrimary),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            // Mode Selector: 4-Way Operational Modes
            SingleChildScrollView(
              scrollDirection: Axis.horizontal,
              child: Container(
                margin: const EdgeInsets.only(bottom: 20),
                decoration: BoxDecoration(
                  color: _cardBg,
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: _borderCol),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildTabButton('send', Icons.send_outlined, 'Transfer (Mode 1)'),
                    _buildTabButton('sell_outside', Icons.point_of_sale_outlined, 'Sold Outside (Mode 3)'),
                    _buildTabButton('sold_history', Icons.history_outlined, 'Sold Inventory & Undo'),
                    _buildTabButton('claim', Icons.download_for_offline_outlined, 'Claim Transfer'),
                  ],
                ),
              ),
            ),

            if (_activeTab == 'claim')
              _buildClaimView()
            else if (_activeTab == 'sell_outside')
              _buildSoldOutsideView()
            else if (_activeTab == 'sold_history')
              _buildSoldHistoryView()
            else
              (_createdTransfer != null ? _buildSuccessView() : _buildInitiationForm()),
          ],
        ),
      ),
    );
  }

  Widget _buildInitiationForm() {
    final selectedCount = _selectedCoinIds.length;
    final totalCount = _allCoins.length;
    final filtered = _filteredCoins;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Privacy & Sanitization Card
        Card(
          color: _cardBg,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: _borderCol),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.shield_outlined, color: Color(0xFF0284C7)),
                    const SizedBox(width: 8),
                    Text(
                      'Privacy & Sanitization Settings',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: _textPrimary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'All invoice and financial details are included by default. Toggle switches on below if you wish to scrub specific data.',
                  style: TextStyle(color: _textSecondary, fontSize: 13),
                ),
                Divider(height: 24, color: _borderCol),

                _buildPrivacySwitchTile(
                  title: 'Hide Purchase Cost & Cost Basis',
                  subtitle: 'Scrubs price paid, acquisition date, and financial records',
                  value: _hideCostBasis,
                  onChanged: (v) => setState(() => _hideCostBasis = v),
                ),
                _buildPrivacySwitchTile(
                  title: 'Hide Personal Notes',
                  subtitle: 'Scrubs private user notes and personal references',
                  value: _hidePrivateNotes,
                  onChanged: (v) => setState(() => _hidePrivateNotes = v),
                ),
                _buildPrivacySwitchTile(
                  title: 'Hide Storage & Safe Box Location',
                  subtitle: 'Scrubs safe numbers, bin locations, and vault tags',
                  value: _hideStorageLocation,
                  onChanged: (v) => setState(() => _hideStorageLocation = v),
                ),
                _buildPrivacySwitchTile(
                  title: 'Hide Invoices & Receipts',
                  subtitle: 'Scrubs retailer order IDs and receipt links',
                  value: _hideInvoices,
                  onChanged: (v) => setState(() => _hideInvoices = v),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),

        // Recipient Email
        Text(
          'Recipient Email (Optional)',
          style: TextStyle(fontWeight: FontWeight.bold, color: _textPrimary),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _recipientEmailController,
          style: TextStyle(color: _textPrimary),
          decoration: InputDecoration(
            hintText: 'user@example.com (or leave blank for face-to-face PIN claim)',
            hintStyle: const TextStyle(color: Color(0xFF64748B)),
            filled: true,
            fillColor: _inputFill,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: _borderCol),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: _borderCol),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF0284C7)),
            ),
            prefixIcon: const Icon(Icons.email_outlined, color: Color(0xFF0284C7)),
          ),
        ),
        const SizedBox(height: 24),

        // Item Selector Header & Controls
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Select Items to Transfer ($selectedCount of $totalCount)',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                      color: _textPrimary,
                    ),
                  ),
                  if (totalCount > 0 && selectedCount == totalCount)
                    const Text(
                      'Entire collection selected',
                      style: TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.w600),
                    ),
                ],
              ),
            ),
          ],
        ),
        const SizedBox(height: 10),

        // Selection Action Bar Buttons
        Wrap(
          spacing: 8,
          runSpacing: 8,
          crossAxisAlignment: WrapCrossAlignment.center,
          children: [
            OutlinedButton.icon(
              onPressed: totalCount == 0
                  ? null
                  : () {
                      setState(() {
                        _selectedCoinIds = _allCoins.map((c) => c.id).toSet();
                      });
                    },
              icon: const Icon(Icons.select_all, size: 16, color: Color(0xFF38BDF8)),
              label: Text(
                'Select Entire Collection ($totalCount)',
                style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
              ),
              style: OutlinedButton.styleFrom(
                side: const BorderSide(color: Color(0xFF0284C7)),
                backgroundColor: const Color(0xFF0284C7).withValues(alpha: 0.1),
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
              ),
            ),
            if (_searchQuery.trim().isNotEmpty && filtered.isNotEmpty) ...[
              OutlinedButton.icon(
                onPressed: () {
                  setState(() {
                    for (final c in filtered) {
                      _selectedCoinIds.add(c.id);
                    }
                  });
                },
                icon: const Icon(Icons.filter_alt, size: 16, color: Color(0xFF38BDF8)),
                label: Text(
                  'Select Filtered (${filtered.length})',
                  style: const TextStyle(color: Color(0xFF38BDF8), fontSize: 12, fontWeight: FontWeight.bold),
                ),
                style: OutlinedButton.styleFrom(
                  side: const BorderSide(color: Color(0xFF0284C7)),
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                ),
              ),
            ],
            if (selectedCount > 0)
              TextButton(
                onPressed: () => setState(() => _selectedCoinIds.clear()),
                child: const Text('Deselect All', style: TextStyle(color: Colors.redAccent, fontSize: 12, fontWeight: FontWeight.bold)),
              ),
          ],
        ),
        const SizedBox(height: 12),

        // Search Bar
        TextField(
          controller: _searchController,
          style: TextStyle(color: _textPrimary),
          onChanged: (val) => setState(() => _searchQuery = val),
          decoration: InputDecoration(
            hintText: 'Search by year, series, denomination, gold/silver, grade...',
            hintStyle: const TextStyle(color: Color(0xFF64748B)),
            prefixIcon: const Icon(Icons.search, color: Color(0xFF94A3B8)),
            suffixIcon: _searchQuery.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear, color: Colors.grey),
                    onPressed: () => setState(() {
                      _searchController.clear();
                      _searchQuery = '';
                    }),
                  )
                : null,
            filled: true,
            fillColor: _inputFill,
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: BorderSide(color: _borderCol),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Inventory List / States
        if (_isFetchingInventory)
          const Padding(
            padding: EdgeInsets.all(24.0),
            child: Center(
              child: CircularProgressIndicator(color: Color(0xFF0284C7)),
            ),
          )
        else if (_fetchError != null)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.red.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.redAccent.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.redAccent),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    _fetchError!,
                    style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                  ),
                ),
              ],
            ),
          )
        else if (_allCoins.isEmpty)
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _borderCol),
            ),
            child: Column(
              children: const [
                Icon(Icons.inventory_2_outlined, color: Colors.grey, size: 48),
                SizedBox(height: 8),
                Text(
                  'No items found in your inventory.',
                  style: TextStyle(color: Colors.grey, fontSize: 15, fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 4),
                Text(
                  'Add coins to your collection before generating a Passport Transfer.',
                  style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
                ),
              ],
            ),
          )
        else if (filtered.isEmpty)
          Padding(
            padding: const EdgeInsets.all(24.0),
            child: Center(
              child: Column(
                children: [
                  const Text(
                    'No items match your search filter.',
                    style: TextStyle(color: Colors.grey, fontSize: 14),
                  ),
                  const SizedBox(height: 8),
                  TextButton(
                    onPressed: () => setState(() {
                      _searchController.clear();
                      _searchQuery = '';
                    }),
                    child: const Text('Clear Search Filter', style: TextStyle(color: Color(0xFF38BDF8))),
                  ),
                ],
              ),
            ),
          )
        else
          Container(
            constraints: const BoxConstraints(maxHeight: 360),
            decoration: BoxDecoration(
              color: _cardBg,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: _borderCol),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: filtered.length,
              separatorBuilder: (ctx, i) => Divider(height: 1, color: _borderCol),
              itemBuilder: (ctx, idx) {
                final coin = filtered[idx];
                final isSelected = _selectedCoinIds.contains(coin.id);
                final titleText = coin.year.isNotEmpty
                    ? '${coin.year} ${coin.programSeries} ${coin.denomination}'
                    : (coin.denomination.isNotEmpty ? coin.denomination : 'Numismatic Item');

                return CheckboxListTile(
                  value: isSelected,
                  activeColor: const Color(0xFF0284C7),
                  checkColor: Colors.white,
                  tileColor: isSelected ? const Color(0xFF0284C7).withValues(alpha: 0.1) : Colors.transparent,
                  onChanged: (val) {
                    setState(() {
                      if (val == true) {
                        _selectedCoinIds.add(coin.id);
                      } else {
                        _selectedCoinIds.remove(coin.id);
                      }
                    });
                  },
                  secondary: coin.imageUrlObverse.isNotEmpty
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: Image.network(
                            coin.imageUrlObverse,
                            width: 40,
                            height: 40,
                            fit: BoxFit.cover,
                            errorBuilder: (ctx, err, _) => const Icon(
                              Icons.monetization_on,
                              color: Color(0xFF0284C7),
                            ),
                          ),
                        )
                      : const Icon(Icons.monetization_on, color: Color(0xFF0284C7)),
                  title: Text(
                    titleText,
                    style: TextStyle(color: _textPrimary, fontWeight: FontWeight.w600, fontSize: 14),
                  ),
                  subtitle: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        '${coin.condition} | ${coin.gradingService.isNotEmpty ? coin.gradingService : "Raw"} ${coin.certificationNumber} ${coin.variety}'.trim(),
                        style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                      ),
                      if (isSelected && (int.tryParse(coin.quantity) ?? 1) > 1) ...[
                        const SizedBox(height: 6),
                        Row(
                          children: [
                            Text(
                              'Transfer Qty: ',
                              style: TextStyle(color: _textPrimary, fontSize: 12, fontWeight: FontWeight.bold),
                            ),
                            InkWell(
                              onTap: () {
                                final current = _itemTransferQuantities[coin.id] ?? 1;
                                if (current > 1) {
                                  setState(() => _itemTransferQuantities[coin.id] = current - 1);
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(2),
                                decoration: BoxDecoration(border: Border.all(color: _borderCol), borderRadius: BorderRadius.circular(4)),
                                child: Icon(Icons.remove, size: 14, color: _textPrimary),
                              ),
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 8),
                              child: Text(
                                '${_itemTransferQuantities[coin.id] ?? 1}',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: _textPrimary),
                              ),
                            ),
                            InkWell(
                              onTap: () {
                                final maxQ = int.tryParse(coin.quantity) ?? 1;
                                final current = _itemTransferQuantities[coin.id] ?? 1;
                                if (current < maxQ) {
                                  setState(() => _itemTransferQuantities[coin.id] = current + 1);
                                }
                              },
                              child: Container(
                                padding: const EdgeInsets.all(2),
                                decoration: BoxDecoration(border: Border.all(color: _borderCol), borderRadius: BorderRadius.circular(4)),
                                child: Icon(Icons.add, size: 14, color: _textPrimary),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              '(of ${coin.quantity} total)',
                              style: TextStyle(color: _textSecondary, fontSize: 11),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                );
              },
            ),
          ),

        const SizedBox(height: 20),

        // Validation Warning if 0 items
        if (selectedCount == 0)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            margin: const EdgeInsets.only(bottom: 16),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.amber.withValues(alpha: 0.4)),
            ),
            child: Row(
              children: const [
                Icon(Icons.warning_amber_rounded, color: Colors.amber),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Please select at least 1 item to generate a Passport Token & PDF.',
                    style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold, fontSize: 13),
                  ),
                ),
              ],
            ),
          ),

        // Initiate Button
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton(
            onPressed: (_isLoading || selectedCount == 0) ? null : _initiateTransfer,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0284C7),
              disabledBackgroundColor: Colors.grey.shade800,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: _isLoading
                ? const CircularProgressIndicator(color: Colors.white)
                : Text(
                    'Generate Passport Token & PDF ($selectedCount Items)',
                    style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white),
                  ),
          ),
        ),
      ],
    );
  }

  Widget _buildClaimView() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          color: _cardBg,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: _borderCol),
          ),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.move_to_inbox_outlined, color: Color(0xFF0284C7), size: 28),
                    const SizedBox(width: 10),
                    Text(
                      'Adopt Transferred Items into Your Vault',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: _textPrimary),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Text(
                  'Enter the Transfer ID and 6-digit Claim PIN code from the Passport Certificate to adopt the items directly into your personal collection vault.',
                  style: TextStyle(color: _textSecondary, fontSize: 14, height: 1.4),
                ),
                Divider(height: 28, color: _borderCol),

                Text('Transfer ID', style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: _claimTransferIdController,
                  style: TextStyle(color: _textPrimary),
                  decoration: InputDecoration(
                    hintText: 'e.g. 10cb9dbd7a1d45069329a7e3f4db5443',
                    hintStyle: const TextStyle(color: Color(0xFF64748B)),
                    filled: true,
                    fillColor: _scaffoldBg,
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF0284C7))),
                    prefixIcon: const Icon(Icons.key, color: Color(0xFF0284C7)),
                  ),
                ),
                const SizedBox(height: 16),

                Text('6-Digit Claim PIN', style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold, fontSize: 13)),
                const SizedBox(height: 6),
                TextField(
                  controller: _claimPinController,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  style: TextStyle(color: _textPrimary, fontSize: 18, letterSpacing: 3, fontWeight: FontWeight.bold),
                  decoration: InputDecoration(
                    hintText: '704167',
                    hintStyle: const TextStyle(color: Color(0xFF64748B), letterSpacing: 0, fontSize: 14),
                    filled: true,
                    fillColor: _scaffoldBg,
                    counterStyle: const TextStyle(color: Color(0xFF64748B)),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                    focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: Color(0xFF0284C7))),
                    prefixIcon: const Icon(Icons.pin, color: Color(0xFF0284C7)),
                  ),
                ),
                const SizedBox(height: 20),

                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: ElevatedButton.icon(
                    onPressed: _isClaiming ? null : _claimTransfer,
                    icon: const Icon(Icons.check_circle, color: Colors.white),
                    label: _isClaiming
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text(
                            'Verify & Adopt Transferred Items',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Colors.white),
                          ),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF0284C7),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPrivacySwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      value: value,
      onChanged: onChanged,
      activeThumbColor: const Color(0xFF38BDF8),
      activeTrackColor: const Color(0xFF0284C7).withValues(alpha: 0.4),
      inactiveThumbColor: Colors.grey.shade400,
      inactiveTrackColor: _borderCol,
      title: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: TextStyle(color: _textPrimary, fontWeight: FontWeight.w600, fontSize: 14),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: value ? Colors.amber.withValues(alpha: 0.2) : Colors.green.withValues(alpha: 0.2),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(
                color: value ? Colors.amber.withValues(alpha: 0.5) : Colors.green.withValues(alpha: 0.5),
              ),
            ),
            child: Text(
              value ? 'SCRUBBED' : 'INCLUDED',
              style: TextStyle(
                color: value ? Colors.amber : Colors.greenAccent,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 2.0),
        child: Text(
          subtitle,
          style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
        ),
      ),
    );
  }

  Widget _buildSuccessView() {
    final transfer = _createdTransfer!;

    return Column(
      children: [
        const Icon(Icons.check_circle_outline, color: Colors.green, size: 72),
        const SizedBox(height: 12),
        Text(
          'Transfer Initiated Successfully!',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: _textPrimary),
        ),
        const SizedBox(height: 8),
        Text(
          'Share the 6-digit Claim PIN below with the recipient or download the Certificate of Transfer.',
          textAlign: TextAlign.center,
          style: TextStyle(color: _textSecondary),
        ),
        if (transfer.recipientEmail != null && transfer.recipientEmail!.isNotEmpty) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.green.withValues(alpha: 0.4)),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.mark_email_read_outlined, color: Colors.greenAccent, size: 18),
                const SizedBox(width: 8),
                Flexible(
                  child: Text(
                    'Certificate of Transfer & PIN emailed to ${transfer.recipientEmail} (Locked to recipient account)',
                    style: const TextStyle(color: Colors.greenAccent, fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          decoration: BoxDecoration(
            color: _cardBg,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: _borderCol),
          ),
          child: Column(
            children: [
              const Text(
                'CLAIM PIN CODE',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF94A3B8)),
              ),
              const SizedBox(height: 4),
              Text(
                transfer.claimPin,
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 4,
                  color: Color(0xFF38BDF8),
                ),
              ),
              const SizedBox(height: 4),
              const Text('Valid for 60 days', style: TextStyle(fontSize: 11, color: Color(0xFF64748B))),
            ],
          ),
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.picture_as_pdf, color: Colors.white),
            label: const Text(
              'Download Certificate of Transfer',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0284C7)),
            onPressed: () async {
              try {
                final bytes = await _transferService.fetchCertificatePdfBytes(transfer.transferId);
                // Open the PDF bytes using the universal_io / printing package or web download
                // On web: trigger a Blob download; on mobile: save to temp and open with PDF viewer
                // For now, use the printing package's sharePdf to open the system share sheet
                // ignore: depend_on_referenced_packages
                await _openPdfBytes(Uint8List.fromList(bytes), 'certificate_${transfer.transferId}.pdf');
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Could not download PDF: $e'),
                        backgroundColor: Colors.red),
                  );
                }
              }
            },
          ),
        ),
      ],
    );
  }

  /// Opens PDF bytes: on web uses the Printing package (opens print dialog / download),
  /// on mobile saves to a temp file and opens with the system PDF viewer.
  Future<void> _openPdfBytes(Uint8List bytes, String filename) async {
    if (kIsWeb) {
      await Printing.sharePdf(bytes: bytes, filename: filename);
    } else {
      final dir = await getTemporaryDirectory();
      final file = File('${dir.path}/$filename');
      await file.writeAsBytes(bytes);
      final uri = Uri.file(file.path);
      if (await canLaunchUrl(uri)) {
        await launchUrl(uri, mode: LaunchMode.externalApplication);
      } else {
        // Fallback: share via the print/share sheet
        await Printing.sharePdf(bytes: bytes, filename: filename);
      }
    }
  }

  Widget _buildTabButton(String tabKey, IconData icon, String label) {
    final isSelected = _activeTab == tabKey;
    return GestureDetector(
      onTap: () {
        setState(() => _activeTab = tabKey);
        if (tabKey == 'sold_history') {
          _loadSoldItems();
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? const Color(0xFF0284C7) : Colors.transparent,
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, color: isSelected ? Colors.white : _textPrimary, size: 16),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : _textPrimary,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  double _parseCost(String rawCost) {
    final cleaned = rawCost.replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(cleaned) ?? 0.0;
  }

  Future<void> _loadSoldItems() async {
    final userIdToUse = widget.userId.trim().isNotEmpty
        ? widget.userId.trim()
        : AuthService.userEmail;
    setState(() {
      _isLoadingSoldItems = true;
      _soldItemsError = null;
    });
    try {
      final items = await _transferService.getSoldInventory(userIdToUse);
      setState(() {
        _soldItems = items;
        _isLoadingSoldItems = false;
      });
    } catch (e) {
      setState(() {
        _isLoadingSoldItems = false;
        _soldItemsError = 'Failed to load sold items: $e';
      });
    }
  }

  Future<void> _recordDirectSale() async {
    if (_selectedCoinToSell == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select a coin to sell.'), backgroundColor: Colors.amber),
      );
      return;
    }
    final price = double.tryParse(_salePriceController.text.replaceAll(',', '').replaceAll(r'$', '').trim());
    if (price == null || price <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid gross sale price.'), backgroundColor: Colors.amber),
      );
      return;
    }
    final fees = double.tryParse(_saleFeesController.text.replaceAll(',', '').replaceAll(r'$', '').trim()) ?? 0.0;
    final userIdToUse = widget.userId.trim().isNotEmpty ? widget.userId.trim() : AuthService.userEmail;

    setState(() => _isSelling = true);
    try {
      final result = await _transferService.recordDirectSale(
        userId: userIdToUse,
        coinId: _selectedCoinToSell!.id,
        qtySold: _qtyToSell,
        salePriceUsd: price,
        feesUsd: fees,
        saleDate: _saleDateController.text.trim().isNotEmpty ? _saleDateController.text.trim() : null,
        salesVenue: _salesVenue,
        buyerReference: _buyerRefController.text.trim().isNotEmpty ? _buyerRefController.text.trim() : null,
        notes: _saleNotesController.text.trim().isNotEmpty ? _saleNotesController.text.trim() : null,
      );

      setState(() => _isSelling = false);
      if (!mounted) return;

      final innerResult = result['result'] as Map<String, dynamic>?;
      final profit = (innerResult?['realized_profit'] as num?)?.toDouble() ??
          (result['realized_profit'] as num?)?.toDouble() ??
          0.0;
      final remaining = (innerResult?['remaining_qty'] as num?)?.toInt() ??
          (result['remaining_qty'] as num?)?.toInt() ??
          0;
      final profitFormatted = profit >= 0 ? '+\$${profit.toStringAsFixed(2)}' : '-\$${profit.abs().toStringAsFixed(2)}';

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          backgroundColor: _cardBg,
          title: Row(
            children: [
              const Icon(Icons.check_circle_outline, color: Colors.green),
              const SizedBox(width: 8),
              Text('Sale Recorded!', style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold)),
            ],
          ),
          content: Text(
            'Successfully recorded sale of $_qtyToSell unit(s) outside Numista.AI.\n\n'
            '• Realized Profit: $profitFormatted\n'
            '• Remaining in Vault: $remaining unit(s)\n\n'
            'Record archived in your private Sold Inventory ledger.',
            style: TextStyle(color: _textSecondary, height: 1.4),
          ),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(ctx);
                _loadInventoryFromFirestore();
                setState(() {
                  _selectedCoinToSell = null;
                  _qtyToSell = 1;
                  _salePriceController.clear();
                  _saleFeesController.text = '0.00';
                  _activeTab = 'sold_history';
                });
                _loadSoldItems();
              },
              child: const Text('View Sold History', style: TextStyle(color: Color(0xFF0284C7), fontWeight: FontWeight.bold)),
            ),
          ],
        ),
      );
    } catch (e) {
      setState(() => _isSelling = false);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to record sale: $e'), backgroundColor: Colors.red),
      );
    }
  }

  Future<void> _undoSale(String archiveId) async {
    if (_isUndoing) return;

    final confirm = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _cardBg,
        title: Text('Undo This Sale?', style: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold)),
        content: Text(
          'This will restore the sold quantity back into your active collection vault '
          'and mark this sale record as voided in your archive (CoS Lock L3).\n\n'
          'Are you sure you want to undo this sale?',
          style: TextStyle(color: _textSecondary, height: 1.4),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: Text('Cancel', style: TextStyle(color: _textSecondary)),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(ctx, true),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.amber.shade800),
            child: const Text('Confirm Undo', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );

    if (confirm != true) return;

    final userIdToUse = widget.userId.trim().isNotEmpty ? widget.userId.trim() : AuthService.userEmail;

    setState(() => _isUndoing = true);
    try {
      final res = await _transferService.undoSale(userId: userIdToUse, saleArchiveId: archiveId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(res['result']?['message'] ?? res['message'] ?? 'Sale successfully undone!'),
          backgroundColor: Colors.green,
        ),
      );
      _loadSoldItems();
      _loadInventoryFromFirestore();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to undo sale: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isUndoing = false);
    }
  }

  Widget _buildSoldOutsideView() {
    final coins = _allCoins;
    final selectedCoin = _selectedCoinToSell;
    final maxQty = selectedCoin != null ? (int.tryParse(selectedCoin.quantity) ?? 1) : 1;

    final unitCost = selectedCoin != null ? _parseCost(selectedCoin.purchaseCost.isNotEmpty ? selectedCoin.purchaseCost : selectedCoin.purchaseCost) : 0.0;
    final allocatedCost = unitCost * _qtyToSell;
    final grossPrice = double.tryParse(_salePriceController.text.replaceAll(',', '').replaceAll(r'$', '').trim()) ?? 0.0;
    final fees = double.tryParse(_saleFeesController.text.replaceAll(',', '').replaceAll(r'$', '').trim()) ?? 0.0;
    final netProceeds = grossPrice - fees;
    final profit = netProceeds - allocatedCost;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          color: _cardBg,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: BorderSide(color: _borderCol),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.point_of_sale_outlined, color: Color(0xFF0284C7)),
                    const SizedBox(width: 8),
                    Text(
                      'Mode 3: Sold Outside Numista.AI',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: _textPrimary),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                Text(
                  'Record a final sale made on eBay, at a coin show, or direct to a dealer. '
                  'Quantity is decremented immediately, financials are archived in integer cents, '
                  'and net profit is tracked in your private ledger.',
                  style: TextStyle(color: _textSecondary, fontSize: 13, height: 1.4),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 16),

        Text('Select Item from Your Vault', style: TextStyle(fontWeight: FontWeight.bold, color: _textPrimary, fontSize: 14)),
        const SizedBox(height: 8),
        if (coins.isEmpty)
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: _cardBg, borderRadius: BorderRadius.circular(8), border: Border.all(color: _borderCol)),
            child: Text('No active inventory items found.', style: TextStyle(color: _textSecondary)),
          )
        else
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12),
            decoration: BoxDecoration(
              color: _inputFill,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _borderCol),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                isExpanded: true,
                value: selectedCoin?.id,
                hint: Text('Choose a coin or currency item...', style: TextStyle(color: _textSecondary)),
                dropdownColor: _cardBg,
                items: coins.map((c) {
                  final title = c.year.isNotEmpty
                      ? '${c.year} ${c.programSeries} ${c.denomination}'
                      : (c.denomination.isNotEmpty ? c.denomination : 'Item');
                  final q = int.tryParse(c.quantity) ?? 1;
                  return DropdownMenuItem<String>(
                    value: c.id,
                    child: Text(
                      '$title (Qty: $q, Cost: ${c.purchaseCost.isNotEmpty ? c.purchaseCost : "\$0.00"})',
                      style: TextStyle(color: _textPrimary, fontSize: 13),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                }).toList(),
                onChanged: (val) {
                  if (val == null) return;
                  final match = coins.firstWhere((c) => c.id == val);
                  setState(() {
                    _selectedCoinToSell = match;
                    _qtyToSell = 1;
                  });
                },
              ),
            ),
          ),

        if (selectedCoin != null) ...[
          const SizedBox(height: 16),

          Card(
            color: _cardBg,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: _borderCol),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      selectedCoin.imageUrlObverse.isNotEmpty
                          ? ClipRRect(
                              borderRadius: BorderRadius.circular(4),
                              child: Image.network(
                                selectedCoin.imageUrlObverse,
                                width: 44,
                                height: 44,
                                fit: BoxFit.cover,
                                errorBuilder: (context, error, stackTrace) => const Icon(Icons.monetization_on, color: Color(0xFF0284C7), size: 40),
                              ),
                            )
                          : const Icon(Icons.monetization_on, color: Color(0xFF0284C7), size: 40),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              selectedCoin.year.isNotEmpty
                                  ? '${selectedCoin.year} ${selectedCoin.programSeries} ${selectedCoin.denomination}'
                                  : selectedCoin.denomination,
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14, color: _textPrimary),
                            ),
                            const SizedBox(height: 2),
                            Text(
                              'Vault ID: ${selectedCoin.id} | Available: $maxQty unit(s)',
                              style: TextStyle(fontSize: 12, color: _textSecondary),
                            ),
                            Text(
                              'Unit Cost Basis: \$${unitCost.toStringAsFixed(2)}',
                              style: TextStyle(fontSize: 12, color: _textSecondary, fontWeight: FontWeight.w600),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),
                  Divider(height: 1, color: _borderCol),
                  const SizedBox(height: 14),

                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Quantity to Sell:', style: TextStyle(fontWeight: FontWeight.bold, color: _textPrimary, fontSize: 13)),
                          Text('Remaining in vault: ${maxQty - _qtyToSell}', style: TextStyle(color: _textSecondary, fontSize: 12)),
                        ],
                      ),
                      Container(
                        decoration: BoxDecoration(
                          color: _inputFill,
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: _borderCol),
                        ),
                        child: Row(
                          children: [
                            IconButton(
                              icon: const Icon(Icons.remove, size: 16),
                              color: _qtyToSell > 1 ? _textPrimary : Colors.grey,
                              onPressed: _qtyToSell > 1 ? () => setState(() => _qtyToSell--) : null,
                            ),
                            Padding(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: Text(
                                '$_qtyToSell',
                                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: _textPrimary),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.add, size: 16),
                              color: _qtyToSell < maxQty ? _textPrimary : Colors.grey,
                              onPressed: _qtyToSell < maxQty ? () => setState(() => _qtyToSell++) : null,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text('Sale Financials & Venue', style: TextStyle(fontWeight: FontWeight.bold, color: _textPrimary, fontSize: 14)),
          const SizedBox(height: 8),

          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(_qtyToSell > 1 ? 'Total received for $_qtyToSell coins (\$)*' : 'Gross Sale Price (\$)*', style: TextStyle(color: _textSecondary, fontSize: 12, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    TextField(
                      controller: _salePriceController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      style: TextStyle(color: _textPrimary),
                      decoration: InputDecoration(
                        hintText: 'e.g. 250.00',
                        hintStyle: TextStyle(color: _textSecondary.withValues(alpha: 0.6)),
                        prefixText: '\$ ',
                        prefixStyle: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold),
                        filled: true,
                        fillColor: _inputFill,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                      ),
                      onChanged: (_) => setState(() {}),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Platform / Shipping Fees (\$)', style: TextStyle(color: _textSecondary, fontSize: 12, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    TextField(
                      controller: _saleFeesController,
                      keyboardType: const TextInputType.numberWithOptions(decimal: true),
                      style: TextStyle(color: _textPrimary),
                      decoration: InputDecoration(
                        hintText: 'e.g. 15.00',
                        hintStyle: TextStyle(color: _textSecondary.withValues(alpha: 0.6)),
                        prefixText: '\$ ',
                        prefixStyle: TextStyle(color: _textPrimary, fontWeight: FontWeight.bold),
                        filled: true,
                        fillColor: _inputFill,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                      ),
                      onChanged: (_) => setState(() {}),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Sale Date', style: TextStyle(color: _textSecondary, fontSize: 12, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    TextField(
                      controller: _saleDateController,
                      style: TextStyle(color: _textPrimary),
                      decoration: InputDecoration(
                        hintText: 'YYYY-MM-DD',
                        hintStyle: TextStyle(color: _textSecondary.withValues(alpha: 0.6)),
                        filled: true,
                        fillColor: _inputFill,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Sales Venue', style: TextStyle(color: _textSecondary, fontSize: 12, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 4),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10),
                      decoration: BoxDecoration(
                        color: _inputFill,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: _borderCol),
                      ),
                      child: DropdownButtonHideUnderline(
                        child: DropdownButton<String>(
                          isExpanded: true,
                          value: _salesVenue,
                          dropdownColor: _cardBg,
                          items: const [
                            DropdownMenuItem(value: 'eBay', child: Text('eBay')),
                            DropdownMenuItem(value: 'GreatCollections', child: Text('GreatCollections')),
                            DropdownMenuItem(value: 'Heritage Auctions', child: Text('Heritage Auctions')),
                            DropdownMenuItem(value: 'Coin Show / In-Person', child: Text('Coin Show / In-Person')),
                            DropdownMenuItem(value: 'LCS / Dealer', child: Text('LCS / Dealer')),
                            DropdownMenuItem(value: 'Private Sale', child: Text('Private Sale')),
                            DropdownMenuItem(value: 'Other', child: Text('Other')),
                          ],
                          onChanged: (val) {
                            if (val != null) setState(() => _salesVenue = val);
                          },
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          TextField(
            controller: _buyerRefController,
            style: TextStyle(color: _textPrimary),
            decoration: InputDecoration(
              labelText: 'Buyer Reference / Order Number (Optional)',
              labelStyle: TextStyle(color: _textSecondary),
              hintText: 'e.g. buyer_id or order #1234',
              hintStyle: TextStyle(color: _textSecondary.withValues(alpha: 0.6)),
              filled: true,
              fillColor: _inputFill,
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: _borderCol)),
            ),
          ),
          const SizedBox(height: 16),

          Card(
            color: profit >= 0 ? const Color(0xFF064E3B).withValues(alpha: 0.15) : Colors.red.withValues(alpha: 0.1),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(color: profit >= 0 ? const Color(0xFF059669) : Colors.redAccent),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        'Net Profit Preview (Integer-Cents Math)',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                          color: profit >= 0 ? const Color(0xFF10B981) : Colors.redAccent,
                        ),
                      ),
                      Text(
                        profit >= 0 ? '+\$${profit.toStringAsFixed(2)}' : '-\$${profit.abs().toStringAsFixed(2)}',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                          color: profit >= 0 ? const Color(0xFF10B981) : Colors.redAccent,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Divider(height: 1, color: _borderCol),
                  const SizedBox(height: 8),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Allocated Cost Basis ($_qtyToSell × \$${unitCost.toStringAsFixed(2)}):', style: TextStyle(color: _textSecondary, fontSize: 12)),
                      Text('\$${allocatedCost.toStringAsFixed(2)}', style: TextStyle(color: _textPrimary, fontSize: 12, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Net Proceeds (\$${grossPrice.toStringAsFixed(2)} - \$${fees.toStringAsFixed(2)}):', style: TextStyle(color: _textSecondary, fontSize: 12)),
                      Text('\$${netProceeds.toStringAsFixed(2)}', style: TextStyle(color: _textPrimary, fontSize: 12, fontWeight: FontWeight.bold)),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          SizedBox(
            width: double.infinity,
            height: 48,
            child: ElevatedButton.icon(
              onPressed: _isSelling ? null : _recordDirectSale,
              icon: _isSelling
                  ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Icon(Icons.check, color: Colors.white),
              label: Text(
                _isSelling ? 'Recording Sale...' : 'Record Sale & Update Vault ($_qtyToSell Unit)',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF059669),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
            ),
          ),
        ],
      ],
    );
  }

  Widget _buildSoldHistoryView() {
    if (_isLoadingSoldItems) {
      return const Padding(
        padding: EdgeInsets.all(40.0),
        child: Center(child: CircularProgressIndicator(color: Color(0xFF0284C7))),
      );
    }

    if (_soldItemsError != null) {
      return Card(
        color: _cardBg,
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              Text(_soldItemsError!, style: const TextStyle(color: Colors.redAccent)),
              const SizedBox(height: 10),
              ElevatedButton(onPressed: _loadSoldItems, child: const Text('Retry')),
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
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Sold & Disposed Inventory', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: _textPrimary)),
                const SizedBox(height: 4),
                Text('Audit ledger of liquidated assets outside active collection.', style: TextStyle(color: _textSecondary, fontSize: 12)),
              ],
            ),
            IconButton(
              icon: const Icon(Icons.refresh, color: Color(0xFF0284C7)),
              onPressed: _loadSoldItems,
              tooltip: 'Refresh Sold Items',
            ),
          ],
        ),
        const SizedBox(height: 16),

        if (_soldItems.isEmpty)
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(color: _cardBg, borderRadius: BorderRadius.circular(12), border: Border.all(color: _borderCol)),
            child: Column(
              children: [
                Icon(Icons.inventory_outlined, size: 48, color: _textSecondary),
                const SizedBox(height: 10),
                Text('No items recorded as sold or transferred yet.', style: TextStyle(color: _textSecondary, fontWeight: FontWeight.bold)),
              ],
            ),
          )
        else
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _soldItems.length,
            separatorBuilder: (context, index) => const SizedBox(height: 12),
            itemBuilder: (ctx, idx) {
              final item = _soldItems[idx];
              final title = item['title'] ?? item['coin_title'] ?? item['denomination'] ?? 'Item';
              final dateStr = item['sale_date'] ?? item['sold_at'] ?? item['transferred_at'] ?? '—';
              final venue = item['sales_venue'] ?? item['venue'] ?? 'Direct';
              final status = (item['status'] ?? item['transfer_status'] ?? 'sold').toString().toLowerCase();
              final isVoided = status == 'voided';
              final qty = item['sold_qty'] ?? item['quantity'] ?? 1;
              final salePrice = (item['sale_price_usd'] as num?)?.toDouble() ?? (item['sale_price'] as num?)?.toDouble() ?? 0.0;
              final fees = (item['fees_usd'] as num?)?.toDouble() ?? (item['fees'] as num?)?.toDouble() ?? 0.0;
              final costBasis = (item['allocated_cost_basis'] as num?)?.toDouble() ?? (item['cost_basis'] as num?)?.toDouble() ?? 0.0;
              final profit = (item['realized_profit_usd'] as num?)?.toDouble() ?? (item['realized_profit'] as num?)?.toDouble() ?? 0.0;
              final archiveId = item['doc_id'] ?? item['id'] ?? '';

              return Card(
                color: _cardBg,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: BorderSide(color: isVoided ? Colors.grey.withValues(alpha: 0.3) : _borderCol),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Expanded(
                            child: Text(
                              '$title',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                fontSize: 14,
                                color: isVoided ? _textSecondary : _textPrimary,
                                decoration: isVoided ? TextDecoration.lineThrough : null,
                              ),
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: isVoided ? Colors.grey.withValues(alpha: 0.2) : Colors.green.withValues(alpha: 0.15),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              isVoided ? 'VOIDED / UNDONE' : 'SOLD',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: isVoided ? Colors.grey : Colors.green,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 6),
                      Text(
                        'Date: $dateStr | Venue: $venue | Qty: $qty',
                        style: TextStyle(fontSize: 12, color: _textSecondary),
                      ),
                      const SizedBox(height: 10),
                      Divider(height: 1, color: _borderCol),
                      const SizedBox(height: 10),

                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('Sale: \$${salePrice.toStringAsFixed(2)}  (Fees: \$${fees.toStringAsFixed(2)})', style: TextStyle(fontSize: 12, color: _textSecondary)),
                              Text('Cost Basis: \$${costBasis.toStringAsFixed(2)}', style: TextStyle(fontSize: 12, color: _textSecondary)),
                            ],
                          ),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text('Realized Profit', style: TextStyle(fontSize: 11, color: _textSecondary)),
                              Text(
                                profit >= 0 ? '+\$${profit.toStringAsFixed(2)}' : '-\$${profit.abs().toStringAsFixed(2)}',
                                style: TextStyle(
                                  fontSize: 15,
                                  fontWeight: FontWeight.bold,
                                  color: isVoided ? Colors.grey : (profit >= 0 ? const Color(0xFF10B981) : Colors.redAccent),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),

                      if (!isVoided && archiveId.isNotEmpty) ...[
                        const SizedBox(height: 12),
                        Align(
                          alignment: Alignment.centerRight,
                          child: OutlinedButton.icon(
                            onPressed: _isUndoing ? null : () => _undoSale(archiveId),
                            icon: const Icon(Icons.undo, size: 14, color: Colors.amber),
                            label: Text(_isUndoing ? 'Undoing...' : 'Undo Sale', style: const TextStyle(color: Colors.amber, fontWeight: FontWeight.bold, fontSize: 12)),
                            style: OutlinedButton.styleFrom(
                              side: const BorderSide(color: Colors.amber),
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              );
            },
          ),
      ],
    );
  }
}
