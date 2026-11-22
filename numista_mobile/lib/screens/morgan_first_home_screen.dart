import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/morgan_first_service.dart';
import 'package:numista_ai/widgets/morgan_full_site_toggle.dart';
import 'package:numista_ai/widgets/morgan_owl_avatar.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;

enum _MorganStep { home, typeCoin, photoScan, confirmCard, fixDetails, done }

class MorganProposedCoin {
  final String proposalId;
  final String name;
  final String year;
  final String denomination;
  final String mintMark;
  final String condition;
  final double confidencePct;
  final String certNumber;
  final String gradingService;
  final Uint8List? frontBytes;

  const MorganProposedCoin({
    required this.proposalId,
    required this.name,
    required this.year,
    required this.denomination,
    required this.mintMark,
    required this.condition,
    required this.confidencePct,
    this.certNumber = '',
    this.gradingService = '',
    this.frontBytes,
  });

  MorganProposedCoin copyWith({
    String? proposalId,
    String? name,
    String? year,
    String? denomination,
    String? mintMark,
    String? condition,
    double? confidencePct,
    String? certNumber,
    String? gradingService,
    Uint8List? frontBytes,
  }) {
    return MorganProposedCoin(
      proposalId: proposalId ?? this.proposalId,
      name: name ?? this.name,
      year: year ?? this.year,
      denomination: denomination ?? this.denomination,
      mintMark: mintMark ?? this.mintMark,
      condition: condition ?? this.condition,
      confidencePct: confidencePct ?? this.confidencePct,
      certNumber: certNumber ?? this.certNumber,
      gradingService: gradingService ?? this.gradingService,
      frontBytes: frontBytes ?? this.frontBytes,
    );
  }
}

class MorganFirstHomeScreen extends StatefulWidget {
  final VoidCallback onSwitchToFullSite;
  final VoidCallback? onSeeMyCoins;
  final Future<Map<String, dynamic>> Function(Map<String, dynamic> coinData)?
      proposeFn;
  final Future<Map<String, dynamic>> Function(String proposalId)? confirmFn;
  final Future<Map<String, dynamic>> Function(
      Uint8List front, Uint8List? back, bool isScan)? identifyPhotoFn;
  final List<String>? availableCameras;

  const MorganFirstHomeScreen({
    super.key,
    required this.onSwitchToFullSite,
    this.onSeeMyCoins,
    this.proposeFn,
    this.confirmFn,
    this.identifyPhotoFn,
    this.availableCameras,
  });

  @override
  State<MorganFirstHomeScreen> createState() => _MorganFirstHomeScreenState();
}

class _MorganFirstHomeScreenState extends State<MorganFirstHomeScreen> {
  static const Color _navy = Color(0xFF0B1A2E);
  static const Color _blue = Color(0xFF1D4F91);
  static const Color _white = Color(0xFFFFFFFF);
  static const Color _softBg = Color(0xFFF3F6FA);

  _MorganStep _step = _MorganStep.home;
  bool _isScanMode = false;
  bool _busy = false;
  String? _errorMsg;

  // Type step
  final TextEditingController _typeCtrl = TextEditingController();

  // Photo / Scan step
  Uint8List? _frontBytes;
  Uint8List? _backBytes;
  bool _hasPlasticLabel = false;
  Uint8List? _labelBytes;
  late String _selectedCamera;
  bool _showCameraHelp = false;

  // Confirm / Fix details
  MorganProposedCoin? _proposed;
  final TextEditingController _fixNameCtrl = TextEditingController();
  final TextEditingController _fixYearCtrl = TextEditingController();
  final TextEditingController _fixMintCtrl = TextEditingController();
  final TextEditingController _fixCondCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    final cams = _cameras;
    _selectedCamera = cams.first;
  }

  List<String> get _cameras =>
      widget.availableCameras ??
      const ['Default Camera', 'USB Microscope Camera'];

  @override
  void dispose() {
    _typeCtrl.dispose();
    _fixNameCtrl.dispose();
    _fixYearCtrl.dispose();
    _fixMintCtrl.dispose();
    _fixCondCtrl.dispose();
    super.dispose();
  }

  Future<Map<String, dynamic>> _callPropose(Map<String, dynamic> data) {
    if (widget.proposeFn != null) return widget.proposeFn!(data);
    return MorganFirstService.proposeAddCoin(data);
  }

  Future<Map<String, dynamic>> _callConfirm(String proposalId) {
    if (widget.confirmFn != null) return widget.confirmFn!(proposalId);
    return MorganFirstService.confirmProposal(proposalId);
  }

  Map<String, dynamic> _parseTypedCoin(String raw) {
    final text = raw.trim();
    final yearMatch = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(text);
    final year = yearMatch?.group(1) ?? '';
    String mint = '';
    final lower = text.toLowerCase();
    if (lower.contains('denver') || RegExp(r'\bd\b').hasMatch(lower)) {
      mint = 'D';
    } else if (lower.contains('san francisco') ||
        RegExp(r'\bs\b').hasMatch(lower)) {
      mint = 'S';
    } else if (lower.contains('carson city') ||
        RegExp(r'\bcc\b').hasMatch(lower)) {
      mint = 'CC';
    } else if (lower.contains('philadelphia') ||
        RegExp(r'\bp\b').hasMatch(lower)) {
      mint = 'P';
    }
    String cond = 'Circulated';
    if (lower.contains('uncirculated') || lower.contains('mint state')) {
      cond = 'Uncirculated';
    } else if (lower.contains('about fine') || lower.contains('fine')) {
      cond = 'Fine';
    } else if (lower.contains('good')) {
      cond = 'Good';
    }
    return {
      'Year': year,
      'Denomination': text,
      'Mint Mark': mint,
      'Condition': cond,
      'name': text,
      'confidence': 85,
    };
  }

  Future<void> _submitTypedCoin() async {
    final text = _typeCtrl.text.trim();
    if (text.isEmpty || _busy) return;
    setState(() {
      _busy = true;
      _errorMsg = null;
    });
    try {
      final parsed = _parseTypedCoin(text);
      final prop = await _callPropose(parsed);
      final propId = (prop['proposal_id'] ?? '').toString();
      if (!mounted) return;
      setState(() {
        _proposed = MorganProposedCoin(
          proposalId: propId,
          name: parsed['name'] as String,
          year: parsed['Year'] as String,
          denomination: parsed['Denomination'] as String,
          mintMark: parsed['Mint Mark'] as String,
          condition: parsed['Condition'] as String,
          confidencePct: (parsed['confidence'] as num).toDouble(),
        );
        _step = _MorganStep.confirmCard;
      });
    } catch (e) {
      if (mounted) setState(() => _errorMsg = 'Could not prepare coin: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _pickImage(String slot) async {
    final picker = ImagePicker();
    final picked = await picker.pickImage(source: ImageSource.gallery);
    if (picked == null) return;
    final bytes = await picked.readAsBytes();
    if (!mounted) return;
    setState(() {
      if (slot == 'front') _frontBytes = bytes;
      if (slot == 'back') _backBytes = bytes;
      if (slot == 'label') _labelBytes = bytes;
    });
  }

  Future<void> _submitPhotoOrScan() async {
    if (_frontBytes == null || _busy) return;
    setState(() {
      _busy = true;
      _errorMsg = null;
    });
    try {
      Map<String, dynamic> idResult;
      if (widget.identifyPhotoFn != null) {
        idResult = await widget.identifyPhotoFn!(
            _frontBytes!, _backBytes, _isScanMode);
      } else {
        final req = http.MultipartRequest(
          'POST',
          Uri.parse('$kApiBaseUrl/api/identify_coin_photo'),
        );
        req.fields['user_email'] = '';
        req.fields['save_to_collection'] = 'false';
        req.files.add(http.MultipartFile.fromBytes(
          'image_a',
          _frontBytes!,
          filename: 'front.jpg',
        ));
        if (_backBytes != null) {
          req.files.add(http.MultipartFile.fromBytes(
            'image_b',
            _backBytes!,
            filename: 'back.jpg',
          ));
        }
        final token = await HttpAuthClient.getIdToken();
        if (token != null && token.isNotEmpty) {
          req.headers['Authorization'] = 'Bearer $token';
        }
        final streamed = await req.send();
        final resp = await http.Response.fromStream(streamed);
        if (resp.statusCode != 200) {
          throw Exception('Identify failed (${resp.statusCode})');
        }
        idResult = jsonDecode(resp.body) as Map<String, dynamic>;
      }

      final year = (idResult['Year'] ?? idResult['year'] ?? '').toString();
      final denom = (idResult['Denomination'] ??
              idResult['denomination'] ??
              idResult['name'] ??
              'Coin')
          .toString();
      final mint =
          (idResult['Mint Mark'] ?? idResult['mint_mark'] ?? '').toString();
      final cond =
          (idResult['Condition'] ?? idResult['condition'] ?? 'Circulated')
              .toString();
      final confRaw = idResult['confidence'] ?? idResult['confidence_pct'] ?? 85;
      final confPct = (confRaw is num)
          ? (confRaw <= 1 ? confRaw * 100.0 : confRaw.toDouble())
          : 85.0;
      final certNo = (idResult['cert_number'] ?? '').toString();
      final grader = (idResult['grading_service'] ?? '').toString();

      final prop = await _callPropose({
        'Year': year,
        'Denomination': denom,
        'Mint Mark': mint,
        'Condition': cond,
      });
      if (!mounted) return;
      setState(() {
        _proposed = MorganProposedCoin(
          proposalId: (prop['proposal_id'] ?? '').toString(),
          name: '$year $denom'.trim(),
          year: year,
          denomination: denom,
          mintMark: mint,
          condition: cond,
          confidencePct: confPct,
          certNumber: certNo,
          gradingService: grader,
          frontBytes: _frontBytes,
        );
        _step = _MorganStep.confirmCard;
      });
    } catch (e) {
      if (mounted) setState(() => _errorMsg = 'Could not identify coin: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _confirmAdd() async {
    final p = _proposed;
    if (p == null || _busy) return;
    setState(() {
      _busy = true;
      _errorMsg = null;
    });
    try {
      await _callConfirm(p.proposalId);
      if (!mounted) return;
      setState(() {
        _proposed = null;
        _frontBytes = null;
        _backBytes = null;
        _labelBytes = null;
        _typeCtrl.clear();
        _step = _MorganStep.done;
      });
    } catch (e) {
      if (mounted) setState(() => _errorMsg = 'Could not add coin: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  void _openFixDetails() {
    final p = _proposed;
    if (p == null) return;
    _fixNameCtrl.text = p.name;
    _fixYearCtrl.text = p.year;
    _fixMintCtrl.text = p.mintMark;
    _fixCondCtrl.text = p.condition;
    setState(() => _step = _MorganStep.fixDetails);
  }

  Future<void> _saveFixedDetailsAndReturnToCard() async {
    final p = _proposed;
    if (p == null || _busy) return;
    setState(() => _busy = true);
    try {
      final newName = _fixNameCtrl.text.trim();
      final newYear = _fixYearCtrl.text.trim();
      final newMint = _fixMintCtrl.text.trim();
      final newCond = _fixCondCtrl.text.trim();
      final prop = await _callPropose({
        'Year': newYear,
        'Denomination': newName,
        'Mint Mark': newMint,
        'Condition': newCond,
      });
      if (!mounted) return;
      setState(() {
        _proposed = p.copyWith(
          proposalId: (prop['proposal_id'] ?? p.proposalId).toString(),
          name: newName,
          year: newYear,
          mintMark: newMint,
          condition: newCond,
        );
        _step = _MorganStep.confirmCard;
      });
    } catch (e) {
      if (mounted) setState(() => _errorMsg = 'Could not update details: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _confirmSkipDialog() async {
    final shouldDiscard = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: _white,
        title: const Text(
          'Throw away this photo?',
          style: TextStyle(fontSize: 22, fontWeight: FontWeight.w800, color: _navy),
        ),
        content: const Text(
          'This coin will not be saved to your collection.',
          style: TextStyle(fontSize: 18, color: _navy),
        ),
        actions: [
          OutlinedButton(
            key: const Key('skip_keep_btn'),
            onPressed: () => Navigator.of(ctx).pop(false),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(120, 56),
              side: const BorderSide(color: _blue, width: 1.5),
            ),
            child: const Text('No, keep it',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: _navy)),
          ),
          ElevatedButton(
            key: const Key('skip_discard_btn'),
            onPressed: () => Navigator.of(ctx).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: _blue,
              minimumSize: const Size(140, 56),
            ),
            child: const Text('Yes, throw it away',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700, color: _white)),
          ),
        ],
      ),
    );

    if (shouldDiscard == true && mounted) {
      setState(() {
        _proposed = null;
        _frontBytes = null;
        _backBytes = null;
        _labelBytes = null;
        _typeCtrl.clear();
        _step = _MorganStep.home;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _white,
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            final isPhone = constraints.maxWidth < 600;
            return Center(
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 960),
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildTopBar(isPhone),
                      const SizedBox(height: 24),
                      if (_errorMsg != null) ...[
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFFF3F3),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFB91C1C)),
                          ),
                          child: Text(
                            _errorMsg!,
                            style: const TextStyle(fontSize: 18, color: _navy),
                          ),
                        ),
                        const SizedBox(height: 16),
                      ],
                      _buildStepBody(isPhone),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Widget _buildTopBar(bool isPhone) {
    final brand = Row(
      mainAxisSize: MainAxisSize.min,
      children: const [
        MorganOwlAvatar(size: 56, borderWidth: 2, borderColor: _blue),
        SizedBox(width: 12),
        Text(
          'Numista.AI',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.w800,
            color: _navy,
          ),
        ),
      ],
    );

    final toggle = MorganFullSiteToggle(
      isMorganActive: true,
      expandFullWidth: isPhone,
      onSelectMorgan: () {},
      onSelectFullSite: widget.onSwitchToFullSite,
    );

    if (isPhone) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          brand,
          const SizedBox(height: 12),
          toggle,
        ],
      );
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [brand, toggle],
    );
  }

  Widget _buildStepBody(bool isPhone) {
    switch (_step) {
      case _MorganStep.home:
        return _buildHome(isPhone);
      case _MorganStep.typeCoin:
        return _buildTypeStep();
      case _MorganStep.photoScan:
        return _buildPhotoScanStep();
      case _MorganStep.confirmCard:
        return _buildConfirmCard();
      case _MorganStep.fixDetails:
        return _buildFixDetailsStep();
      case _MorganStep.done:
        return _buildDoneStep(isPhone);
    }
  }

  Widget _buildHome(bool isPhone) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          "Hello. I'm Morgan.",
          style: TextStyle(fontSize: 32, fontWeight: FontWeight.w800, color: _navy),
        ),
        const SizedBox(height: 8),
        const Text(
          'Your coins are safe. Values stay hidden.',
          style: TextStyle(fontSize: 20, color: _navy),
        ),
        const SizedBox(height: 24),
        _buildThreeTileGrid(isPhone),
      ],
    );
  }

  /// Balanced 3-tile layout (AG-4 Upload tile cleanly hidden).
  Widget _buildThreeTileGrid(bool isPhone) {
    final tiles = [
      _buildActionTile(
        key: const Key('tile_photo'),
        icon: Icons.photo_camera_outlined,
        title: 'Photo',
        subtitle: 'Use your camera',
        onTap: () => setState(() {
          _isScanMode = false;
          _step = _MorganStep.photoScan;
        }),
      ),
      _buildActionTile(
        key: const Key('tile_scan'),
        icon: Icons.biotech_outlined,
        title: 'Scan',
        subtitle: 'Use a microscope',
        onTap: () => setState(() {
          _isScanMode = true;
          _step = _MorganStep.photoScan;
        }),
      ),
      _buildActionTile(
        key: const Key('tile_type'),
        icon: Icons.edit_note_outlined,
        title: 'Type',
        subtitle: 'Write it in',
        onTap: () => setState(() => _step = _MorganStep.typeCoin),
      ),
    ];

    if (isPhone) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          tiles[0],
          const SizedBox(height: 12),
          tiles[1],
          const SizedBox(height: 12),
          tiles[2],
        ],
      );
    }

    return Row(
      children: [
        Expanded(child: tiles[0]),
        const SizedBox(width: 14),
        Expanded(child: tiles[1]),
        const SizedBox(width: 14),
        Expanded(child: tiles[2]),
      ],
    );
  }

  Widget _buildActionTile({
    required Key key,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return OutlinedButton(
      key: key,
      onPressed: onTap,
      style: OutlinedButton.styleFrom(
        backgroundColor: _white,
        minimumSize: const Size(120, 120),
        padding: const EdgeInsets.all(20),
        side: const BorderSide(color: _blue, width: 2),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 36, color: _blue),
          const SizedBox(height: 10),
          Text(
            title,
            style: const TextStyle(
                fontSize: 22, fontWeight: FontWeight.w800, color: _navy),
          ),
          const SizedBox(height: 4),
          Text(
            subtitle,
            style: const TextStyle(fontSize: 18, color: _navy),
          ),
        ],
      ),
    );
  }

  Widget _buildTypeStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Tell me about your coin',
          style: TextStyle(fontSize: 28, fontWeight: FontWeight.w800, color: _navy),
        ),
        const SizedBox(height: 8),
        const Text(
          'Example: 1921 Morgan dollar, Denver, about fine',
          style: TextStyle(fontSize: 18, color: _navy),
        ),
        const SizedBox(height: 16),
        TextField(
          key: const Key('morgan_type_input'),
          controller: _typeCtrl,
          onSubmitted: (_) => _submitTypedCoin(),
          style: const TextStyle(fontSize: 20, color: _navy),
          decoration: InputDecoration(
            hintText: 'Type your question',
            hintStyle: const TextStyle(fontSize: 18, color: _navy),
            contentPadding: const EdgeInsets.all(18),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: _blue, width: 2),
            ),
            focusedBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: _blue, width: 2.5),
            ),
          ),
        ),
        const SizedBox(height: 18),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            ElevatedButton(
              key: const Key('type_submit_btn'),
              onPressed: _busy ? null : _submitTypedCoin,
              style: ElevatedButton.styleFrom(
                backgroundColor: _blue,
                minimumSize: const Size(180, 56),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10)),
              ),
              child: Text(
                _busy ? 'Checking...' : 'Check this coin',
                style: const TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _white),
              ),
            ),
            OutlinedButton(
              onPressed: () => setState(() => _step = _MorganStep.home),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(120, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
              child: const Text('Back',
                  style: TextStyle(
                      fontSize: 18, fontWeight: FontWeight.w700, color: _navy)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildPhotoScanStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          _isScanMode ? 'Scan with microscope' : 'Take or choose photos',
          style: const TextStyle(
              fontSize: 28, fontWeight: FontWeight.w800, color: _navy),
        ),
        const SizedBox(height: 12),
        if (_isScanMode) ...[
          const Text(
            'Choose camera',
            style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            key: const Key('choose_camera_dropdown'),
            initialValue: _selectedCamera,
            items: _cameras
                .map((c) => DropdownMenuItem(
                      value: c,
                      child: Text(c,
                          style: const TextStyle(fontSize: 18, color: _navy)),
                    ))
                .toList(),
            onChanged: (v) {
              if (v != null) setState(() => _selectedCamera = v);
            },
            decoration: InputDecoration(
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(10),
                borderSide: const BorderSide(color: _blue, width: 1.5),
              ),
            ),
          ),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => setState(() => _showCameraHelp = !_showCameraHelp),
            child: const Text(
              "Why can't I see my camera?",
              style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w700,
                  color: _blue,
                  decoration: TextDecoration.underline),
            ),
          ),
          if (_showCameraHelp)
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: _softBg,
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: _blue),
              ),
              child: const Text(
                'Check that your USB microscope is plugged in and browser camera permission is allowed. You can also use Type anytime.',
                style: TextStyle(fontSize: 18, color: _navy),
              ),
            ),
          const SizedBox(height: 14),
        ],
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            OutlinedButton.icon(
              key: const Key('pick_front_btn'),
              onPressed: () => _pickImage('front'),
              icon: Icon(
                  _frontBytes != null
                      ? Icons.check_circle
                      : Icons.photo_camera_outlined,
                  color: _blue),
              label: Text(
                _frontBytes != null ? 'Front photo ready' : '1. Front photo',
                style: const TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
              ),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(180, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
            ),
            OutlinedButton.icon(
              key: const Key('pick_back_btn'),
              onPressed: () => _pickImage('back'),
              icon: Icon(
                  _backBytes != null
                      ? Icons.check_circle
                      : Icons.photo_camera_outlined,
                  color: _blue),
              label: Text(
                _backBytes != null
                    ? 'Back photo ready'
                    : '2. Back photo (optional)',
                style: const TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
              ),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(200, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),
        CheckboxListTile(
          value: _hasPlasticLabel,
          onChanged: (v) => setState(() => _hasPlasticLabel = v ?? false),
          title: const Text(
            'Is this coin in a plastic case with a label?',
            style: TextStyle(fontSize: 18, color: _navy),
          ),
          controlAffinity: ListTileControlAffinity.leading,
        ),
        if (_hasPlasticLabel)
          OutlinedButton.icon(
            onPressed: () => _pickImage('label'),
            icon: Icon(
                _labelBytes != null
                    ? Icons.check_circle
                    : Icons.qr_code_scanner,
                color: _blue),
            label: Text(
              _labelBytes != null
                  ? 'Label photo ready'
                  : '3. Label photo (optional)',
              style: const TextStyle(
                  fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
            ),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(220, 56),
              side: const BorderSide(color: _blue, width: 1.5),
            ),
          ),
        const SizedBox(height: 20),
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            ElevatedButton(
              key: const Key('identify_photo_btn'),
              onPressed: (_frontBytes != null && !_busy)
                  ? _submitPhotoOrScan
                  : null,
              style: ElevatedButton.styleFrom(
                backgroundColor: _blue,
                minimumSize: const Size(200, 56),
              ),
              child: Text(
                _busy ? 'Looking...' : 'Look at this coin',
                style: const TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _white),
              ),
            ),
            OutlinedButton(
              onPressed: () => setState(() => _step = _MorganStep.typeCoin),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(160, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
              child: const Text('Type instead',
                  style: TextStyle(
                      fontSize: 18, fontWeight: FontWeight.w700, color: _navy)),
            ),
            OutlinedButton(
              onPressed: () => setState(() => _step = _MorganStep.home),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(120, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
              child: const Text('Back',
                  style: TextStyle(
                      fontSize: 18, fontWeight: FontWeight.w700, color: _navy)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildConfirmCard() {
    final p = _proposed;
    if (p == null) return const SizedBox.shrink();

    final confWords = MorganFirstService.confidenceWords(p.confidencePct);
    final subline = MorganFirstService.confidenceSubline(p.confidencePct);
    final canAdd = MorganFirstService.canAddForConfidence(p.confidencePct);
    final highlightFix = MorganFirstService.highlightFixFirst(p.confidencePct);

    final addBtn = ElevatedButton(
      key: const Key('confirm_add_btn'),
      onPressed: _busy ? null : _confirmAdd,
      style: ElevatedButton.styleFrom(
        backgroundColor: _blue,
        minimumSize: const Size(220, 56),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
      child: Text(
        _busy ? 'Adding...' : 'Add to collection',
        style: const TextStyle(
            fontSize: 20, fontWeight: FontWeight.w800, color: _white),
      ),
    );

    final fixBtn = highlightFix
        ? ElevatedButton(
            key: const Key('confirm_fix_btn'),
            onPressed: _openFixDetails,
            style: ElevatedButton.styleFrom(
              backgroundColor: _blue,
              minimumSize: const Size(170, 56),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Fix details',
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _white)),
          )
        : OutlinedButton(
            key: const Key('confirm_fix_btn'),
            onPressed: _openFixDetails,
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(170, 56),
              side: const BorderSide(color: _blue, width: 1.5),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Fix details',
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _navy)),
          );

    return Container(
      key: const Key('morgan_confirm_card'),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _blue, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (p.frontBytes != null) ...[
            ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: Image.memory(p.frontBytes!,
                  height: 160, fit: BoxFit.contain),
            ),
            const SizedBox(height: 14),
          ],
          Text(
            p.name.isNotEmpty ? p.name : '${p.year} ${p.denomination}'.trim(),
            style: const TextStyle(
                fontSize: 26, fontWeight: FontWeight.w800, color: _navy),
          ),
          const SizedBox(height: 8),
          Text(
            confWords,
            key: const Key('confirm_confidence_text'),
            style: const TextStyle(
                fontSize: 20, fontWeight: FontWeight.w700, color: _blue),
          ),
          if (subline != null) ...[
            const SizedBox(height: 4),
            Text(subline, style: const TextStyle(fontSize: 18, color: _navy)),
          ],
          const SizedBox(height: 12),
          Text(
            'Mint mark: ${p.mintMark.isEmpty ? "None / Unknown" : p.mintMark}   •   Condition: ${p.condition}',
            style: const TextStyle(fontSize: 18, color: _navy),
          ),
          const SizedBox(height: 8),
          const Text(
            "A slab label (cert number) always beats Morgan's photo guess.",
            style: TextStyle(fontSize: 18, color: _navy),
          ),
          if (p.certNumber.isNotEmpty) ...[
            const SizedBox(height: 10),
            OutlinedButton.icon(
              onPressed: () {
                final uri = p.gradingService.toUpperCase().contains('NGC')
                    ? Uri.parse(
                        'https://www.ngccoin.com/certlookup/${p.certNumber}/')
                    : Uri.parse(
                        'https://www.pcgs.com/cert/${p.certNumber}');
                launchUrl(uri, mode: LaunchMode.externalApplication);
              },
              icon: const Icon(Icons.open_in_new, color: _blue),
              label: const Text(
                'Check this slab on the PCGS / NGC site',
                style: TextStyle(
                    fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
              ),
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(240, 56),
                side: const BorderSide(color: _blue, width: 1.5),
              ),
            ),
          ],
          const SizedBox(height: 20),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              if (canAdd && !highlightFix) addBtn,
              if (!canAdd) ...[
                ElevatedButton(
                  key: const Key('confirm_retake_btn'),
                  onPressed: () =>
                      setState(() => _step = _MorganStep.photoScan),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _blue,
                    minimumSize: const Size(160, 56),
                  ),
                  child: const Text('Retake',
                      style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: _white)),
                ),
                OutlinedButton(
                  key: const Key('confirm_type_fallback_btn'),
                  onPressed: () =>
                      setState(() => _step = _MorganStep.typeCoin),
                  style: OutlinedButton.styleFrom(
                    minimumSize: const Size(140, 56),
                    side: const BorderSide(color: _blue, width: 1.5),
                  ),
                  child: const Text('Type',
                      style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w700,
                          color: _navy)),
                ),
              ],
              if (canAdd) fixBtn,
              if (canAdd && highlightFix) addBtn,
              OutlinedButton(
                key: const Key('confirm_skip_btn'),
                onPressed: _confirmSkipDialog,
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(160, 56),
                  side: const BorderSide(color: _blue, width: 1.5),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                ),
                child: const Text('Skip this coin',
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: _navy)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFixDetailsStep() {
    return Container(
      key: const Key('morgan_fix_details'),
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _white,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _blue, width: 2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Fix details',
            style: TextStyle(
                fontSize: 26, fontWeight: FontWeight.w800, color: _navy),
          ),
          const SizedBox(height: 14),
          TextField(
            key: const Key('fix_name_input'),
            controller: _fixNameCtrl,
            style: const TextStyle(fontSize: 18, color: _navy),
            decoration: const InputDecoration(
              labelText: 'Coin name / denomination',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            key: const Key('fix_year_input'),
            controller: _fixYearCtrl,
            style: const TextStyle(fontSize: 18, color: _navy),
            decoration: const InputDecoration(
              labelText: 'Year',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            key: const Key('fix_mint_input'),
            controller: _fixMintCtrl,
            style: const TextStyle(fontSize: 18, color: _navy),
            decoration: const InputDecoration(
              labelText: 'Mint mark',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 12),
          TextField(
            key: const Key('fix_condition_input'),
            controller: _fixCondCtrl,
            style: const TextStyle(fontSize: 18, color: _navy),
            decoration: const InputDecoration(
              labelText: 'Condition',
              border: OutlineInputBorder(),
            ),
          ),
          const SizedBox(height: 18),
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              ElevatedButton(
                key: const Key('fix_done_btn'),
                onPressed: _busy ? null : _saveFixedDetailsAndReturnToCard,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _blue,
                  minimumSize: const Size(200, 56),
                ),
                child: const Text('Back to confirm card',
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: _white)),
              ),
              OutlinedButton(
                onPressed: () =>
                    setState(() => _step = _MorganStep.confirmCard),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(120, 56),
                  side: const BorderSide(color: _blue, width: 1.5),
                ),
                child: const Text('Cancel',
                    style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w700,
                        color: _navy)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildDoneStep(bool isPhone) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Added. Next coin?',
          key: Key('morgan_done_heading'),
          style: TextStyle(
              fontSize: 30, fontWeight: FontWeight.w800, color: _navy),
        ),
        const SizedBox(height: 16),
        _buildThreeTileGrid(isPhone),
        const SizedBox(height: 20),
        OutlinedButton.icon(
          key: const Key('see_my_coins_btn'),
          onPressed: widget.onSeeMyCoins ?? widget.onSwitchToFullSite,
          icon: const Icon(Icons.collections_bookmark_outlined, color: _blue),
          label: const Text(
            'See my coins',
            style: TextStyle(
                fontSize: 18, fontWeight: FontWeight.w700, color: _navy),
          ),
          style: OutlinedButton.styleFrom(
            minimumSize: const Size(200, 56),
            side: const BorderSide(color: _blue, width: 2),
          ),
        ),
      ],
    );
  }
}
