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

  bool _hideCostBasis = true;
  bool _hidePrivateNotes = true;
  bool _hideStorageLocation = true;
  bool _hideInvoices = true;
  bool _isLoading = false;

  TransferModel? _createdTransfer;

  Future<void> _initiateTransfer() async {
    setState(() => _isLoading = true);
    try {
      final transfer = await _transferService.initiateTransfer(
        userId: widget.userId,
        itemIds: widget.itemsToTransfer.map((c) => c.id).toList(),
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
        SnackBar(content: Text('Error initiating transfer: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Lateral Transfer — Passport Protocol'),
        backgroundColor: const Color(0xFF0F172A),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: _createdTransfer != null ? _buildSuccessView() : _buildInitiationForm(),
      ),
    );
  }

  Widget _buildInitiationForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Card(
          color: const Color(0xFFF8FAFC),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
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
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'Select data fields to scrub before item payload is minted for recipient.',
                  style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
                ),
                const Divider(height: 24),
                SwitchListTile(
                  title: const Text('Hide Purchase Cost & Cost Basis'),
                  subtitle: const Text('Scrubs price paid, acquisition date, and financial records'),
                  value: _hideCostBasis,
                  onChanged: (v) => setState(() => _hideCostBasis = v),
                ),
                SwitchListTile(
                  title: const Text('Hide Personal Notes'),
                  subtitle: const Text('Scrubs private user notes and personal references'),
                  value: _hidePrivateNotes,
                  onChanged: (v) => setState(() => _hidePrivateNotes = v),
                ),
                SwitchListTile(
                  title: const Text('Hide Storage & Safe Box Location'),
                  subtitle: const Text('Scrubs safe numbers, bin locations, and vault tags'),
                  value: _hideStorageLocation,
                  onChanged: (v) => setState(() => _hideStorageLocation = v),
                ),
                SwitchListTile(
                  title: const Text('Hide Invoices & Receipts'),
                  subtitle: const Text('Scrubs retailer order IDs and receipt links'),
                  value: _hideInvoices,
                  onChanged: (v) => setState(() => _hideInvoices = v),
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 20),
        const Text('Recipient Email (Optional)', style: TextStyle(fontWeight: FontWeight.bold)),
        const SizedBox(height: 6),
        TextField(
          controller: _recipientEmailController,
          decoration: InputDecoration(
            hintText: 'user@example.com (or leave blank for face-to-face PIN claim)',
            border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
            prefixIcon: const Icon(Icons.email_outlined),
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Selected Items (${widget.itemsToTransfer.length})',
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
        ),
        const SizedBox(height: 8),
        ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: widget.itemsToTransfer.length,
          itemBuilder: (ctx, idx) {
            final coin = widget.itemsToTransfer[idx];
            return ListTile(
              leading: const Icon(Icons.monetization_on, color: Color(0xFF0284C7)),
              title: Text(coin.year.isNotEmpty ? '${coin.year} ${coin.programSeries}' : coin.denomination),
              subtitle: Text('${coin.condition} | ${coin.gradingService}'),
            );
          },
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton(
            onPressed: _isLoading ? null : _initiateTransfer,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF0284C7),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
            child: _isLoading
                ? const CircularProgressIndicator(color: Colors.white)
                : const Text('Generate Passport Token & PDF', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
        ),
      ],
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
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
        ),
        const SizedBox(height: 8),
        const Text(
          'Share the 6-digit Claim PIN below with the recipient or print the Official Passport PDF.',
          textAlign: TextAlign.center,
          style: TextStyle(color: Color(0xFF64748B)),
        ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 24),
          decoration: BoxDecoration(
            color: const Color(0xFFF1F5F9),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: const Color(0xFFCBD5E1)),
          ),
          child: Column(
            children: [
              const Text('CLAIM PIN CODE', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Color(0xFF64748B))),
              const SizedBox(height: 4),
              Text(
                transfer.claimPin,
                style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, letterSpacing: 4, color: Color(0xFF0284C7)),
              ),
              const SizedBox(height: 4),
              const Text('Valid for 60 days', style: TextStyle(fontSize: 11, color: Color(0xFF94A3B8))),
            ],
          ),
        ),
        const SizedBox(height: 24),
        SizedBox(
          width: double.infinity,
          height: 48,
          child: ElevatedButton.icon(
            icon: const Icon(Icons.picture_as_pdf),
            label: const Text('Download Passport PDF (8.5x11 & 3x5 Passcard)'),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0F172A)),
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
