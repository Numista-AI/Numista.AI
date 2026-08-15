import 'package:flutter/material.dart';
import '../services/lateral_transfer_service.dart';

class TransferInboxScreen extends StatefulWidget {
  final String userId;

  const TransferInboxScreen({Key? key, required this.userId}) : super(key: key);

  @override
  _TransferInboxScreenState createState() => _TransferInboxScreenState();
}

class _TransferInboxScreenState extends State<TransferInboxScreen> {
  final LateralTransferService _transferService = LateralTransferService();
  final TextEditingController _transferIdController = TextEditingController();
  final TextEditingController _pinController = TextEditingController();
  bool _isLoading = false;

  Future<void> _claimTransfer() async {
    final transferId = _transferIdController.text.trim();
    final pin = _pinController.text.trim();

    if (transferId.isEmpty || pin.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter both Transfer ID and 6-digit PIN PIN')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final res = await _transferService.claimTransfer(
        userId: widget.userId,
        transferId: transferId,
        claimPin: pin,
      );

      setState(() => _isLoading = false);

      showDialog(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Transfer Adopted Successfully!'),
          content: Text('${res["result"]["items_claimed_count"]} items were added to your collection with updated provenance history.'),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.pop(ctx);
                Navigator.pop(context);
              },
              child: const Text('Done'),
            )
          ],
        ),
      );
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Claim failed: $e'), backgroundColor: Colors.red),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Transfer Claim Inbox'),
        backgroundColor: const Color(0xFF0F172A),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              elevation: 2,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: const [
                        Icon(Icons.qr_code_scanner, color: Color(0xFF0284C7)),
                        SizedBox(width: 8),
                        Text(
                          'Claim Incoming Item Transfer',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Enter the Transfer ID and 6-digit Claim PIN from your Passport Certificate to adopt the item into your vault.',
                      style: TextStyle(color: Color(0xFF64748B), fontSize: 13),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _transferIdController,
                      decoration: InputDecoration(
                        labelText: 'Transfer ID',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _pinController,
                      keyboardType: TextInputType.number,
                      maxLength: 6,
                      decoration: InputDecoration(
                        labelText: '6-Digit Claim PIN',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 48,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : _claimTransfer,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0284C7),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                        child: _isLoading
                            ? const CircularProgressIndicator(color: Colors.white)
                            : const Text('Verify & Adopt Items', style: TextStyle(fontWeight: FontWeight.bold)),
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
}
