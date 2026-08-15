import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class CoaInspectorScreen extends StatefulWidget {
  const CoaInspectorScreen({Key? key}) : super(key: key);

  @override
  State<CoaInspectorScreen> createState() => _CoaInspectorScreenState();
}

class _CoaInspectorScreenState extends State<CoaInspectorScreen> {
  bool _isAnalyzing = false;
  Map<String, dynamic>? _coaResult;

  Future<void> _pickAndAnalyzeCoa() async {
    final result = await FilePicker.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['jpg', 'png', 'pdf', 'jpeg'],
      withData: true,
    );


    if (result == null || result.files.isEmpty) return;

    final file = result.files.first;
    if (file.bytes == null) return;

    setState(() {
      _isAnalyzing = true;
      _coaResult = null;
    });

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/v1/coa/parse'),
      );

      request.files.add(http.MultipartFile.fromBytes(
        'file',
        file.bytes!,
        filename: file.name,
      ));

      final streamedResponse = await request.send();
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        setState(() {
          _coaResult = jsonDecode(response.body);
        });
      } else {
        throw Exception('Server returned ${response.statusCode}');
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('COA Inspection Error: ${e.toString()}'), backgroundColor: Colors.red),
      );
    } finally {
      setState(() => _isAnalyzing = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('COA & Mint Packaging Inspector'),
        backgroundColor: const Color(0xFF1E3A8A),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(20.0),
                child: Column(
                  children: [
                    const Icon(Icons.verified_user_outlined, size: 48, color: Color(0xFF1E3A8A)),
                    const SizedBox(height: 12),
                    const Text(
                      'Certificate of Authenticity Inspector',
                      style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Upload or scan US Mint Certificates of Authenticity to verify serial numbers, mintage caps, and original packaging specs.',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey.shade700),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton.icon(
                      onPressed: _isAnalyzing ? null : _pickAndAnalyzeCoa,
                      icon: _isAnalyzing
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : const Icon(Icons.document_scanner),
                      label: Text(_isAnalyzing ? 'Analyzing COA...' : 'Scan / Upload COA Card'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF1E3A8A),
                        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 20),
            if (_coaResult != null) ...[
              Card(
                color: Colors.green.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.check_circle, color: Colors.green, size: 28),
                          const SizedBox(width: 10),
                          Expanded(
                            child: Text(
                              _coaResult?['program_title'] as String? ?? 'Verified COA Card',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                            ),
                          ),
                          _buildVerdictChip(_coaResult?['verdict'] as String?),
                        ],
                      ),
                      if (_coaResult?['mintage_warning'] != null) ...[
                        const SizedBox(height: 12),
                        Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFEF3C7),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(color: const Color(0xFFF59E0B)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.warning_amber_rounded, color: Color(0xFFD97706), size: 22),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  _coaResult!['mintage_warning'],
                                  style: const TextStyle(color: Color(0xFF92400E), fontSize: 12, fontWeight: FontWeight.w600),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                      const Divider(height: 24),
                      _infoRow('Issuer', _coaResult?['issuer'] as String?),
                      _infoRow('Serial Number', '#${_coaResult?['serial_number'] ?? '—'}'),
                      _infoRow('Mintage Limit', _coaResult?['mintage_limit'] as String?),
                      if (_coaResult?['coin_specs'] != null) ...[
                        _infoRow('Denomination', _coaResult!['coin_specs']['denomination'] as String?),
                        _infoRow('Composition', _coaResult!['coin_specs']['composition'] as String?),
                        _infoRow('Weight', '${_coaResult!['coin_specs']['weight_troy_oz']} troy oz'),
                        _infoRow('Finish', _coaResult!['coin_specs']['finish'] as String?),
                      ],
                      _infoRow('Signature', _coaResult?['signature'] as String?),
                      _infoRow('Cloud Vault Archive', _coaResult?['gcs_path'] as String?),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _infoRow(String title, String? value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
          Text(value ?? '—', style: const TextStyle(fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Widget _buildVerdictChip(String? verdict) {
    if (verdict == 'VALID') {
      return Chip(
        avatar: const Icon(Icons.check_circle, color: Color(0xFF047857), size: 16),
        label: const Text("✓ Valid Mintage Ceiling", style: TextStyle(color: Color(0xFF047857), fontWeight: FontWeight.bold, fontSize: 11)),
        backgroundColor: const Color(0xFFD1FAE5),
      );
    } else if (verdict == 'EXCEEDS') {
      return Chip(
        avatar: const Icon(Icons.warning_amber_rounded, color: Color(0xFFB45309), size: 16),
        label: const Text("⚠️ Exceeds Mintage Ceiling", style: TextStyle(color: Color(0xFFB45309), fontWeight: FontWeight.bold, fontSize: 11)),
        backgroundColor: const Color(0xFFFEF3C7),
      );
    } else {
      return Chip(
        avatar: const Icon(Icons.help_outline, color: Color(0xFF475569), size: 16),
        label: const Text("⚪ Unable to Verify Mintage", style: TextStyle(color: Color(0xFF475569), fontWeight: FontWeight.bold, fontSize: 11)),
        backgroundColor: const Color(0xFFE2E8F0),
      );
    }
  }
}
