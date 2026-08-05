import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../models/coin_model.dart';
import '../models/transfer_model.dart';
import '../services/lateral_transfer_service.dart';

class LateralTransferScreen extends StatefulWidget {
  final String userId;
  final List<CoinModel> itemsToTransfer;

  const LateralTransferScreen({
    Key? key,
    required this.userId,
    required this.itemsToTransfer,
  }) : super(key: key);

  @override
  _LateralTransferScreenState createState() => _LateralTransferScreenState();
}

class _LateralTransferScreenState extends State<LateralTransferScreen> {
  final LateralTransferService _transferService = LateralTransferService();
  final TextEditingController _recipientEmailController = TextEditingController();
  final TextEditingController _searchController = TextEditingController();

  bool _hideCostBasis = true;
  bool _hidePrivateNotes = true;
  bool _hideStorageLocation = true;
  bool _hideInvoices = true;
  bool _isLoading = false;
  bool _isFetchingInventory = false;
  String? _fetchError;

  List<CoinModel> _allCoins = [];
  Set<String> _selectedCoinIds = {};
  String _searchQuery = '';

  TransferModel? _createdTransfer;

  @override
  void initState() {
    super.initState();
    if (widget.itemsToTransfer.isNotEmpty) {
      _allCoins = List.from(widget.itemsToTransfer);
      _selectedCoinIds = _allCoins.map((c) => c.id).toSet();
    } else {
      _loadInventoryFromFirestore();
    }
  }

  @override
  void dispose() {
    _recipientEmailController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadInventoryFromFirestore() async {
    final email = widget.userId.trim();
    if (email.isEmpty) return;

    setState(() {
      _isFetchingInventory = true;
      _fetchError = null;
    });

    try {
      final snap = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('coins')
          .orderBy('timestamp', descending: true)
          .get();

      final coins = snap.docs.map((doc) => CoinModel.fromFirestore(doc)).toList();

      setState(() {
        _allCoins = coins;
        // Select all items by default for convenience
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
    if (_searchQuery.trim().isEmpty) return _allCoins;
    final q = _searchQuery.trim().toLowerCase();
    return _allCoins.where((c) {
      final title = '${c.year} ${c.programSeries} ${c.denomination} ${c.mintMark} ${c.variety} ${c.certificationNumber}'.toLowerCase();
      return title.contains(q);
    }).toList();
  }

  bool get _areAllFilteredSelected {
    final filtered = _filteredCoins;
    if (filtered.isEmpty) return false;
    return filtered.every((c) => _selectedCoinIds.contains(c.id));
  }

  void _toggleSelectAllFiltered(bool? value) {
    final filtered = _filteredCoins;
    setState(() {
      if (value == true) {
        for (final c in filtered) {
          _selectedCoinIds.add(c.id);
        }
      } else {
        for (final c in filtered) {
          _selectedCoinIds.remove(c.id);
        }
      }
    });
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

    setState(() => _isLoading = true);
    try {
      final transfer = await _transferService.initiateTransfer(
        userId: widget.userId,
        itemIds: selected.map((c) => c.id).toList(),
        recipientEmail: _recipientEmailController.text.trim().isNotEmpty
            ? _recipientEmailController.text.trim()
            : null,
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
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Error initiating transfer: $e'),
          backgroundColor: Colors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text(
          'Lateral Transfer — Passport Protocol',
          style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF1E293B),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: _createdTransfer != null ? _buildSuccessView() : _buildInitiationForm(),
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
        // Privacy & Sanitization Card (Dark Theme High-Contrast)
        Card(
          color: const Color(0xFF1E293B),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
            side: const BorderSide(color: Color(0xFF334155)),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: const [
                    Icon(Icons.shield_outlined, color: Color(0xFF0284C7)),
                    SizedBox(width: 8),
                    Text(
                      'Privacy & Sanitization Settings',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                        color: Colors.white,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Select data fields to scrub before item payload is minted for recipient.',
                  style: TextStyle(color: Color(0xFFCBD5E1), fontSize: 13),
                ),
                const Divider(height: 24, color: Color(0xFF334155)),

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
        const Text(
          'Recipient Email (Optional)',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        const SizedBox(height: 6),
        TextField(
          controller: _recipientEmailController,
          style: const TextStyle(color: Colors.white),
          decoration: InputDecoration(
            hintText: 'user@example.com (or leave blank for face-to-face PIN claim)',
            hintStyle: const TextStyle(color: Color(0xFF64748B)),
            filled: true,
            fillColor: const Color(0xFF1E293B),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF334155)),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF334155)),
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
          children: [
            Text(
              'Select Items to Transfer ($selectedCount of $totalCount)',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: Colors.white,
              ),
            ),
            if (filtered.isNotEmpty)
              Row(
                children: [
                  Checkbox(
                    value: _areAllFilteredSelected,
                    activeColor: const Color(0xFF0284C7),
                    checkColor: Colors.white,
                    onChanged: _toggleSelectAllFiltered,
                  ),
                  GestureDetector(
                    onTap: () => _toggleSelectAllFiltered(!_areAllFilteredSelected),
                    child: const Text(
                      'Select All Filtered',
                      style: TextStyle(color: Color(0xFF38BDF8), fontSize: 13, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
          ],
        ),
        const SizedBox(height: 8),

        // Search Bar
        TextField(
          controller: _searchController,
          style: const TextStyle(color: Colors.white),
          onChanged: (val) => setState(() => _searchQuery = val),
          decoration: InputDecoration(
            hintText: 'Search by year, series, denomination, grade...',
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
            fillColor: const Color(0xFF1E293B),
            contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(8),
              borderSide: const BorderSide(color: Color(0xFF334155)),
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
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF334155)),
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
          const Padding(
            padding: EdgeInsets.all(24.0),
            child: Center(
              child: Text(
                'No items match your search filter.',
                style: TextStyle(color: Colors.grey, fontSize: 14),
              ),
            ),
          )
        else
          Container(
            constraints: const BoxConstraints(maxHeight: 320),
            decoration: BoxDecoration(
              color: const Color(0xFF1E293B),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: const Color(0xFF334155)),
            ),
            child: ListView.separated(
              shrinkWrap: true,
              itemCount: filtered.length,
              separatorBuilder: (ctx, i) => const Divider(height: 1, color: Color(0xFF334155)),
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
                            errorBuilder: (_, __, ___) => const Icon(
                              Icons.monetization_on,
                              color: Color(0xFF0284C7),
                            ),
                          ),
                        )
                      : const Icon(Icons.monetization_on, color: Color(0xFF0284C7)),
                  title: Text(
                    titleText,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14),
                  ),
                  subtitle: Text(
                    '${coin.condition} | ${coin.gradingService.isNotEmpty ? coin.gradingService : "Raw"} ${coin.certificationNumber}'.trim(),
                    style: const TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
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

  Widget _buildPrivacySwitchTile({
    required String title,
    required String subtitle,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      value: value,
      onChanged: onChanged,
      activeColor: const Color(0xFF38BDF8),
      activeTrackColor: const Color(0xFF0284C7).withValues(alpha: 0.4),
      inactiveThumbColor: Colors.grey.shade400,
      inactiveTrackColor: const Color(0xFF334155),
      title: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 14),
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
    final pdfUrl = _transferService.getPassportPdfUrl(transfer.transferId);

    return Column(
      children: [
        const Icon(Icons.check_circle_outline, color: Colors.green, size: 72),
        const SizedBox(height: 12),
        const Text(
          'Transfer Initiated Successfully!',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20, color: Colors.white),
        ),
        const SizedBox(height: 8),
        const Text(
          'Share the 6-digit Claim PIN below with the recipient or print the Official Passport PDF.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Color(0xFFCBD5E1)),
        ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          decoration: BoxDecoration(
            color: const Color(0xFF1E293B),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFF334155)),
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
              'Download Passport PDF (8.5x11 & 3x5 Passcard)',
              style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
            ),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0284C7)),
            onPressed: () async {
              final uri = Uri.parse(pdfUrl);
              if (await canLaunchUrl(uri)) {
                await launchUrl(uri, mode: LaunchMode.externalApplication);
              }
            },
          ),
        ),
      ],
    );
  }
}
