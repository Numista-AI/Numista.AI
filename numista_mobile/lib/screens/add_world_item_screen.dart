import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart' as intl;
import 'package:url_launcher/url_launcher.dart';

import '../services/world_item_service.dart';

// ── Colour Palette (matches existing app) ────────────────────────────────────
class _C {
  static const surface = Colors.white;
  static const text    = Color(0xFF31333F);
  static const sub     = Color(0xFF64748B);
  static const accent  = Color(0xFF4C8CDA);
  static const border  = Color(0xFFE2E6E9);
  static const green   = Color(0xFF22C55E);
  static const amber   = Color(0xFFF59E0B);
  static const red     = Color(0xFFDC3545);
  static const fill    = Color(0xFFF8FAFC);
}

// ─────────────────────────────────────────────────────────────────────────────
class AddWorldItemScreen extends StatefulWidget {
  final Function(String)? onNavigate;

  const AddWorldItemScreen({super.key, this.onNavigate});

  @override
  State<AddWorldItemScreen> createState() => _AddWorldItemScreenState();
}

class _AddWorldItemScreenState extends State<AddWorldItemScreen> {
  // ── Step tracking ────────────────────────────────────────────────────────
  // step 0 = type picker
  // step 1 = photo + AI analysis
  // step 2 = manual form + save
  int _step = 0;

  // ── Type picker ──────────────────────────────────────────────────────────
  WorldItemType? _selectedType;

  // ── Photo / AI ───────────────────────────────────────────────────────────
  Uint8List? _imageBytes;
  String     _imageFileName = 'photo.jpg';
  bool       _isAnalysing   = false;
  WorldItemIdentification? _identification;
  // null  = not yet decided
  // true  = user confirmed a Numista match (set _confirmedMatch)
  // false = user skipped Numista
  bool? _numistaDecision;
  NumistaMatch? _confirmedMatch;

  // ── Manual form controllers ──────────────────────────────────────────────
  final _formKey        = GlobalKey<FormState>();
  final _nameCtrl       = TextEditingController();
  final _countryCtrl    = TextEditingController();
  final _eraCtrl        = TextEditingController();
  final _denomCtrl      = TextEditingController();
  final _materialCtrl   = TextEditingController();
  final _conditionCtrl  = TextEditingController();
  final _costCtrl       = TextEditingController();
  final _estValueCtrl   = TextEditingController();
  final _fromCtrl       = TextEditingController();
  final _storageCtrl    = TextEditingController();
  final _notesCtrl      = TextEditingController();
  DateTime? _datePurchased;

  // ── Bullion-specific ─────────────────────────────────────────────────────
  String  _bullionMetal  = 'Silver';
  final _weightCtrl  = TextEditingController();
  final _purityCtrl  = TextEditingController();
  Map<String, double> _spotPrices = {};
  double? _meltValue;

  // ── Save state ────────────────────────────────────────────────────────────
  bool   _isSaving    = false;
  String _saveError   = '';

  // ─────────────────────────────────────────────────────────────────────────
  @override
  void dispose() {
    for (final c in [
      _nameCtrl, _countryCtrl, _eraCtrl, _denomCtrl, _materialCtrl,
      _conditionCtrl, _costCtrl, _estValueCtrl, _fromCtrl, _storageCtrl,
      _notesCtrl, _weightCtrl, _purityCtrl,
    ]) {
      c.dispose();
    }
    super.dispose();
  }

  // ── Pre-fill form from AI result ─────────────────────────────────────────
  void _prefillFromAI(GeminiIdentification g) {
    if (_nameCtrl.text.isEmpty) {
      _nameCtrl.text = g.denomination != null
          ? '${g.country} ${g.denomination} ${g.era}'.trim()
          : '${g.country} ${g.era}'.trim();
    }
    if (_countryCtrl.text.isEmpty && g.country != 'Unknown') {
      _countryCtrl.text = g.country;
    }
    if (_eraCtrl.text.isEmpty && g.era != 'Unknown') {
      _eraCtrl.text = g.era;
    }
    if (_denomCtrl.text.isEmpty && g.denomination != null) {
      _denomCtrl.text = g.denomination!;
    }
    if (_materialCtrl.text.isEmpty && g.material != null) {
      _materialCtrl.text = g.material!;
    }
  }

  void _prefillFromNumista(NumistaMatch m) {
    if (_nameCtrl.text.isEmpty && m.title != null) {
      _nameCtrl.text = m.title!;
    }
    if (_countryCtrl.text.isEmpty && m.issuer != null) {
      _countryCtrl.text = m.issuer!;
    }
    if (_eraCtrl.text.isEmpty && m.yearRange.isNotEmpty) {
      _eraCtrl.text = m.yearRange;
    }
    if (_materialCtrl.text.isEmpty && m.composition != null) {
      _materialCtrl.text = m.composition!;
    }
  }

  // ── Photo picker ─────────────────────────────────────────────────────────
  Future<void> _pickImage() async {
    final result = await FilePicker.pickFiles(
      type: FileType.image,
      allowMultiple: false,
      withData: true,
    );
    if (result == null || result.files.isEmpty) return;
    final f = result.files.first;
    if (f.bytes == null) return;
    setState(() {
      _imageBytes    = f.bytes;
      _imageFileName = f.name;
      // Clear previous identification when a new image is chosen
      _identification  = null;
      _numistaDecision = null;
      _confirmedMatch  = null;
    });
  }

  // ── AI identification call ────────────────────────────────────────────────
  Future<void> _runAIIdentification() async {
    setState(() => _isAnalysing = true);
    final result = await WorldItemService.identify(
      imageBytes:    _imageBytes,
      imageFileName: _imageFileName,
      countryHint:   _countryCtrl.text,
      yearHint:      _eraCtrl.text,
      itemTypeHint:  _selectedType ?? WorldItemType.unknown,
      notesHint:     _notesCtrl.text,
    );
    if (!mounted) return;
    setState(() {
      _isAnalysing    = false;
      _identification = result;
    });
    if (result != null) {
      _prefillFromAI(result.gemini);
    }
  }

  // ── Bullion melt value ────────────────────────────────────────────────────
  Future<void> _fetchSpotAndCalcMelt() async {
    final prices = await WorldItemService.fetchSpotPrices();
    if (!mounted) return;
    setState(() => _spotPrices = prices);
    _recalcMelt();
  }

  void _recalcMelt() {
    final wt  = double.tryParse(_weightCtrl.text);
    final pur = double.tryParse(_purityCtrl.text);
    if (wt == null || pur == null || _spotPrices.isEmpty) {
      setState(() => _meltValue = null);
      return;
    }
    setState(() {
      _meltValue = WorldItemService.computeBullionMeltValue(
        weightOz:   wt,
        purity:     pur,
        metal:      _bullionMetal,
        spotPrices: _spotPrices,
      );
    });
  }

  // ── Save ──────────────────────────────────────────────────────────────────
  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    _formKey.currentState!.save();

    setState(() { _isSaving = true; _saveError = ''; });

    final gemini = _identification?.gemini;
    final isBullion = _selectedType == WorldItemType.bullion;

    final item = WorldItem(
      itemCategory:           _selectedType ?? WorldItemType.unknown,
      aiIdentification:       gemini?.identification ?? '',
      aiConfidence:           gemini?.confidence ?? 0.0,
      aiConfidenceFlagged:    gemini?.confidence != null && gemini!.confidence < 0.90,
      numistaId:              _confirmedMatch?.numistaId,
      numistaTitle:           _confirmedMatch?.title,
      numistaConfirmedByUser: _confirmedMatch != null,
      numistaCatalogueUrl:    _confirmedMatch?.catalogueUrl,
      name:           _nameCtrl.text.trim(),
      country:        _countryCtrl.text.trim(),
      era:            _eraCtrl.text.trim(),
      denomination:   _denomCtrl.text.trim(),
      material:       _materialCtrl.text.trim(),
      condition:      _conditionCtrl.text.trim(),
      purchasePrice:  double.tryParse(_costCtrl.text.replaceAll(r'$', '').trim()),
      datePurchased:  _datePurchased,
      purchasedFrom:  _fromCtrl.text.trim(),
      estimatedValue: double.tryParse(_estValueCtrl.text.replaceAll(r'$', '').trim()),
      storageLocation: _storageCtrl.text.trim(),
      notes:          _notesCtrl.text.trim(),
      bullionWeightOz: isBullion ? double.tryParse(_weightCtrl.text) : null,
      bullionPurity:   isBullion ? double.tryParse(_purityCtrl.text) : null,
      bullionMetal:    isBullion ? _bullionMetal : null,
      spotValueAtEntry: isBullion ? _meltValue : null,
    );

    final docId = await WorldItemService.save(item);
    if (!mounted) return;

    if (docId != null) {
      setState(() => _isSaving = false);
      _showSuccessSnackbar();
      // Return to previous screen
      if (widget.onNavigate != null) widget.onNavigate!('My Collection');
    } else {
      setState(() {
        _isSaving  = false;
        _saveError = 'Could not save item. Please try again.';
      });
    }
  }

  void _showSuccessSnackbar() {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Row(children: [
          Icon(Icons.check_circle, color: Colors.white, size: 20),
          SizedBox(width: 10),
          Text('Item saved to your collection!',
              style: TextStyle(fontWeight: FontWeight.w600)),
        ]),
        backgroundColor: _C.green,
        duration: const Duration(seconds: 3),
        action: SnackBarAction(
          label: 'View',
          textColor: Colors.white,
          onPressed: () { if (widget.onNavigate != null) widget.onNavigate!('My Collection'); },
        ),
      ),
    );
  }

  // ── Build ─────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    final isNarrow = MediaQuery.of(context).size.width < 700;
    return SingleChildScrollView(
      padding: EdgeInsets.all(isNarrow ? 16 : 32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 700),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildPageHeader(),
              const SizedBox(height: 24),
              _buildStepIndicator(),
              const SizedBox(height: 28),
              if (_step == 0) _buildTypePicker(),
              if (_step == 1) _buildPhotoAndAIStep(),
              if (_step == 2) _buildManualFormStep(),
            ],
          ),
        ),
      ),
    );
  }

  // ── Page header ───────────────────────────────────────────────────────────
  Widget _buildPageHeader() {
    return Row(
      children: [
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
        const Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Add World & Specialty Item',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900,
                    color: _C.text)),
              Text('Foreign coins, currency, bullion, collectibles & more',
                style: TextStyle(color: _C.sub, fontSize: 13)),
            ],
          ),
        ),
      ],
    );
  }

  // ── Step indicator ────────────────────────────────────────────────────────
  Widget _buildStepIndicator() {
    final steps = ['Item Type', 'AI Analysis', 'Details & Save'];
    return Row(
      children: List.generate(steps.length, (i) {
        final done    = i < _step;
        final active  = i == _step;
        return Expanded(
          child: Row(children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    width: 28, height: 28,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: done ? _C.green : active ? _C.accent : _C.border,
                    ),
                    child: Center(
                      child: done
                          ? const Icon(Icons.check, color: Colors.white, size: 16)
                          : Text('${i + 1}',
                              style: TextStyle(
                                color: active ? Colors.white : _C.sub,
                                fontWeight: FontWeight.w700, fontSize: 12)),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(steps[i],
                    style: TextStyle(
                      fontSize: 11, fontWeight: active ? FontWeight.w700 : FontWeight.w400,
                      color: active ? _C.accent : _C.sub)),
                ],
              ),
            ),
            if (i < steps.length - 1)
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.only(bottom: 20),
                  child: Divider(
                    color: i < _step ? _C.green : _C.border,
                    thickness: 2,
                  ),
                ),
              ),
          ]),
        );
      }),
    );
  }

  // ────────────────────────────────────────────────────────────────────────
  // STEP 0 — Type Picker
  // ────────────────────────────────────────────────────────────────────────
  Widget _buildTypePicker() {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('What type of item is this?',
            style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, color: _C.text)),
          const SizedBox(height: 4),
          const Text('Choose the category that best describes your item.',
            style: TextStyle(color: _C.sub, fontSize: 13)),
          const SizedBox(height: 20),
          ...WorldItemType.values.map((t) => _typeOption(t)),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: _selectedType == null ? null : () => setState(() => _step = 1),
              style: ElevatedButton.styleFrom(
                backgroundColor: _C.accent, foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                disabledBackgroundColor: _C.border,
              ),
              child: const Text('Continue →',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _typeOption(WorldItemType t) {
    final selected = _selectedType == t;
    return GestureDetector(
      onTap: () => setState(() => _selectedType = t),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 150),
        margin: const EdgeInsets.only(bottom: 10),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: selected ? const Color(0xFFEFF6FF) : _C.fill,
          border: Border.all(
            color: selected ? _C.accent : _C.border,
            width: selected ? 2 : 1,
          ),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Row(
          children: [
            Text(t.emoji, style: const TextStyle(fontSize: 22)),
            const SizedBox(width: 14),
            Expanded(
              child: Text(t.displayLabel,
                style: TextStyle(
                  fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                  color: selected ? _C.accent : _C.text,
                  fontSize: 15,
                )),
            ),
            if (selected)
              const Icon(Icons.check_circle, color: _C.accent, size: 20),
          ],
        ),
      ),
    );
  }

  // ────────────────────────────────────────────────────────────────────────
  // STEP 1 — Photo Upload + AI Analysis
  // ────────────────────────────────────────────────────────────────────────
  Widget _buildPhotoAndAIStep() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Back button
        TextButton.icon(
          onPressed: () => setState(() { _step = 0; _identification = null; }),
          icon: const Icon(Icons.arrow_back_ios, size: 14),
          label: const Text('Change type'),
          style: TextButton.styleFrom(foregroundColor: _C.sub),
        ),
        const SizedBox(height: 8),

        // Photo upload card
        _card(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(children: [
                const Icon(Icons.camera_alt_outlined, color: _C.accent, size: 20),
                const SizedBox(width: 8),
                const Text('Photo (recommended)',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700, color: _C.text)),
              ]),
              const SizedBox(height: 6),
              Text('Upload an image to let AI identify your item. Or skip and fill in details manually.',
                style: const TextStyle(color: _C.sub, fontSize: 13)),
              const SizedBox(height: 16),
              if (_imageBytes != null) ...[
                ClipRRect(
                  borderRadius: BorderRadius.circular(8),
                  child: Image.memory(_imageBytes!,
                    height: 200, width: double.infinity, fit: BoxFit.contain),
                ),
                const SizedBox(height: 12),
              ],
              Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: _isAnalysing ? null : _pickImage,
                      icon: const Icon(Icons.upload_file_outlined, size: 18),
                      label: Text(_imageBytes == null ? 'Choose Image' : 'Change Image'),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: _C.accent,
                        side: const BorderSide(color: _C.accent),
                        padding: const EdgeInsets.symmetric(vertical: 14),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ),
                  if (_imageBytes != null) ...[
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _isAnalysing ? null : _runAIIdentification,
                        icon: _isAnalysing
                            ? const SizedBox(
                                width: 16, height: 16,
                                child: CircularProgressIndicator(
                                    color: Colors.white, strokeWidth: 2))
                            : const Icon(Icons.auto_awesome, size: 18),
                        label: Text(_isAnalysing ? 'Analysing…' : 'Identify with AI'),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _C.accent, foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 14),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),

        // AI result panel
        if (_identification != null) ...[
          const SizedBox(height: 16),
          _buildAIResultBanner(_identification!),
        ],

        // Numista match picker
        if (_identification != null &&
            !_identification!.showDisclaimer &&
            _identification!.numistaMatches.isNotEmpty &&
            _numistaDecision == null) ...[
          const SizedBox(height: 16),
          _buildNumistaMatchPicker(_identification!.numistaMatches),
        ],

        const SizedBox(height: 20),
        // Proceed button (always visible once type is picked)
        SizedBox(
          width: double.infinity,
          child: ElevatedButton(
            onPressed: () {
              // If user hasn't made a Numista decision yet, auto-skip
              if (_numistaDecision == null && _identification != null &&
                  !_identification!.showDisclaimer &&
                  _identification!.numistaMatches.isNotEmpty) {
                setState(() => _numistaDecision = false);
              }
              setState(() => _step = 2);
              if (_selectedType == WorldItemType.bullion) {
                _fetchSpotAndCalcMelt();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: _C.accent, foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
            ),
            child: const Text('Continue to Details →',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
          ),
        ),
        const SizedBox(height: 8),
        Center(
          child: TextButton(
            onPressed: () => setState(() { _step = 2;
              if (_selectedType == WorldItemType.bullion) _fetchSpotAndCalcMelt();
            }),
            child: const Text('Skip photo — fill in manually',
                style: TextStyle(color: _C.sub)),
          ),
        ),
      ],
    );
  }

  // ── AI result banner ──────────────────────────────────────────────────────
  Widget _buildAIResultBanner(WorldItemIdentification id) {
    final g = id.gemini;
    final level = g.level;
    Color bgColor, borderColor, iconColor;
    IconData icon;
    String statusLabel;

    switch (level) {
      case ConfidenceLevel.high:
        bgColor = const Color(0xFFECFDF5);
        borderColor = const Color(0xFF6EE7B7);
        iconColor = _C.green;
        icon = Icons.verified_rounded;
        statusLabel = 'AI Identified';
        break;
      case ConfidenceLevel.medium:
        bgColor = const Color(0xFFFFFBEB);
        borderColor = const Color(0xFFFCD34D);
        iconColor = _C.amber;
        icon = Icons.warning_amber_rounded;
        statusLabel = 'AI Estimate';
        break;
      case ConfidenceLevel.low:
        bgColor = const Color(0xFFFEF2F2);
        borderColor = const Color(0xFFFCA5A5);
        iconColor = _C.red;
        icon = Icons.error_outline_rounded;
        statusLabel = 'Low Confidence';
        break;
    }

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border.all(color: borderColor),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header row
          Row(
            children: [
              Icon(icon, color: iconColor, size: 18),
              const SizedBox(width: 8),
              Text('🤖 AI Identification',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800,
                    color: _C.text)),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text('${g.confidencePercent} — $statusLabel',
                  style: TextStyle(fontSize: 11, fontWeight: FontWeight.w700,
                      color: iconColor)),
              ),
            ],
          ),
          const SizedBox(height: 10),
          // Identification text
          Text(g.identification,
            style: const TextStyle(fontSize: 14, color: _C.text, height: 1.5)),

          // Disclaimer for sub-threshold confidence
          if (id.showDisclaimer) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.7),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.info_outline, size: 16, color: iconColor),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'AI estimate below verification threshold (${g.confidencePercent} confidence). '
                      'Please fill in what you know below. Verify with a numismatic expert for valuation or sale.',
                      style: TextStyle(fontSize: 12, color: _C.sub, height: 1.4),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ── Numista match picker ──────────────────────────────────────────────────
  Widget _buildNumistaMatchPicker(List<NumistaMatch> matches) {
    return _card(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(children: [
            Image.network(
              'https://en.numista.com/images/logo-numista.png',
              height: 20, errorBuilder: (ctx, err, st) => const Icon(Icons.book_outlined, size: 20),
            ),
            const SizedBox(width: 8),
            const Text('Possible Catalogue Matches',
              style: TextStyle(fontSize: 14, fontWeight: FontWeight.w800, color: _C.text)),
          ]),
          const SizedBox(height: 4),
          const Text('Is one of these your item? Select to confirm.',
            style: TextStyle(fontSize: 12, color: _C.sub)),
          const SizedBox(height: 14),
          ...matches.map((m) => _numistaMatchCard(m)),
          const SizedBox(height: 8),
          TextButton(
            onPressed: () => setState(() => _numistaDecision = false),
            child: const Text('None of these — skip Numista lookup',
                style: TextStyle(color: _C.sub, fontSize: 13)),
          ),
        ],
      ),
    );
  }

  Widget _numistaMatchCard(NumistaMatch m) {
    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: _C.fill,
        border: Border.all(color: _C.border),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          // Thumbnail
          if (m.imageObverse != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(6),
              child: Image.network(m.imageObverse!,
                width: 60, height: 60, fit: BoxFit.contain,
                errorBuilder: (ctx, err, st) =>
                    const Icon(Icons.monetization_on_outlined, size: 40, color: _C.border)),
            )
          else
            Container(
              width: 60, height: 60,
              decoration: BoxDecoration(
                color: _C.border,
                borderRadius: BorderRadius.circular(6),
              ),
              child: const Icon(Icons.monetization_on_outlined, color: _C.sub),
            ),
          const SizedBox(width: 12),
          // Details
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(m.title ?? 'Unknown',
                  style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13, color: _C.text),
                  maxLines: 2, overflow: TextOverflow.ellipsis),
                if ((m.issuer ?? '').isNotEmpty || m.yearRange.isNotEmpty)
                  Text('${m.issuer ?? ''}${m.yearRange.isNotEmpty ? ' · ${m.yearRange}' : ''}',
                    style: const TextStyle(fontSize: 12, color: _C.sub)),
                if ((m.composition ?? '').isNotEmpty)
                  Text(m.composition!,
                    style: const TextStyle(fontSize: 12, color: _C.sub)),
                if (m.catalogueUrl != null)
                  GestureDetector(
                    onTap: () => launchUrl(Uri.parse(m.catalogueUrl!)),
                    child: const Text('View on Numista →',
                      style: TextStyle(fontSize: 11, color: _C.accent)),
                  ),
              ],
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _numistaDecision = true;
                _confirmedMatch  = m;
              });
              _prefillFromNumista(m);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: _C.green, foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(6)),
              textStyle: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
            ),
            child: const Text('This is\nmy item'),
          ),
        ],
      ),
    );
  }

  // ── Numista confirmed banner ──────────────────────────────────────────────
  Widget _buildNumistaConfirmedBanner(NumistaMatch m) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: const Color(0xFFECFDF5),
        border: Border.all(color: const Color(0xFF6EE7B7)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          const Icon(Icons.check_circle, color: _C.green, size: 18),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Numista Match Confirmed: ${m.title ?? ''}',
                  style: const TextStyle(fontWeight: FontWeight.w700,
                      fontSize: 13, color: _C.text)),
                if (m.catalogueUrl != null)
                  GestureDetector(
                    onTap: () => launchUrl(Uri.parse(m.catalogueUrl!)),
                    child: const Text('View catalogue entry →',
                      style: TextStyle(fontSize: 12, color: _C.accent)),
                  ),
              ],
            ),
          ),
          TextButton(
            onPressed: () => setState(() {
              _numistaDecision = null;
              _confirmedMatch  = null;
            }),
            child: const Text('Change', style: TextStyle(color: _C.sub, fontSize: 12)),
          ),
        ],
      ),
    );
  }

  // ────────────────────────────────────────────────────────────────────────
  // STEP 2 — Manual Entry Form + Save
  // ────────────────────────────────────────────────────────────────────────
  Widget _buildManualFormStep() {
    final isBullion = _selectedType == WorldItemType.bullion;
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Back button
          TextButton.icon(
            onPressed: () => setState(() => _step = 1),
            icon: const Icon(Icons.arrow_back_ios, size: 14),
            label: const Text('Back to AI Analysis'),
            style: TextButton.styleFrom(foregroundColor: _C.sub),
          ),
          const SizedBox(height: 8),

          // AI identification recap (compact) + Numista confirmed banner
          if (_identification != null)
            _buildAIRecapChip(_identification!.gemini),
          if (_confirmedMatch != null)
            _buildNumistaConfirmedBanner(_confirmedMatch!),

          // ── Identity ────────────────────────────────────────────────────
          _card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _sectionHeader('Item Identity', Icons.tag_outlined),
                _field('Item Name / Description', _nameCtrl,
                  hint: 'e.g. 1921 German 3 Mark Silver'),
                Row(children: [
                  Expanded(child: _field('Country of Origin', _countryCtrl,
                    hint: 'e.g. Germany, Unknown')),
                  const SizedBox(width: 12),
                  Expanded(child: _field('Year / Era', _eraCtrl,
                    hint: 'e.g. 1921, c.250 AD')),
                ]),
                Row(children: [
                  Expanded(child: _field('Denomination', _denomCtrl,
                    hint: 'e.g. 3 Mark, 5 Francs')),
                  const SizedBox(width: 12),
                  Expanded(child: _field('Material / Composition', _materialCtrl,
                    hint: 'e.g. Silver, Gold, Bronze')),
                ]),
              ],
            ),
          ),

          // ── Bullion fields ───────────────────────────────────────────────
          if (isBullion) ...[
            const SizedBox(height: 16),
            _card(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _sectionHeader('Bullion Details', Icons.show_chart_rounded),
                  // Metal selector
                  const Text('Metal', style: TextStyle(fontSize: 12,
                      fontWeight: FontWeight.w600, color: _C.sub)),
                  const SizedBox(height: 6),
                  SegmentedButton<String>(
                    segments: const [
                      ButtonSegment(value: 'Gold',      label: Text('Gold')),
                      ButtonSegment(value: 'Silver',    label: Text('Silver')),
                      ButtonSegment(value: 'Platinum',  label: Text('Platinum')),
                      ButtonSegment(value: 'Palladium', label: Text('Palladium')),
                    ],
                    selected: {_bullionMetal},
                    onSelectionChanged: (s) {
                      setState(() => _bullionMetal = s.first);
                      _recalcMelt();
                    },
                    style: ButtonStyle(
                      backgroundColor: WidgetStateProperty.resolveWith((states) {
                        if (states.contains(WidgetState.selected)) return _C.accent;
                        return _C.fill;
                      }),
                      foregroundColor: WidgetStateProperty.resolveWith((states) {
                        if (states.contains(WidgetState.selected)) return Colors.white;
                        return _C.sub;
                      }),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(children: [
                    Expanded(
                      child: _field('Weight (troy oz)', _weightCtrl,
                        hint: 'e.g. 1.0',
                        keyboardType: TextInputType.number,
                        onChanged: (_) => _recalcMelt()),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: _field('Purity', _purityCtrl,
                        hint: 'e.g. 0.999 or 0.9167',
                        keyboardType: TextInputType.number,
                        onChanged: (_) => _recalcMelt()),
                    ),
                  ]),
                  // Live melt value widget
                  if (_meltValue != null || _spotPrices.isNotEmpty)
                    _buildBullionMeltWidget(),
                ],
              ),
            ),
          ],

          // ── Condition ────────────────────────────────────────────────────
          const SizedBox(height: 16),
          _card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _sectionHeader('Condition', Icons.grade_outlined),
                _field('Condition / Grade', _conditionCtrl,
                  hint: 'e.g. VF-30, AU-55, Raw, Circulated'),
              ],
            ),
          ),

          // ── Purchase ─────────────────────────────────────────────────────
          const SizedBox(height: 16),
          _card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _sectionHeader('Purchase Details', Icons.receipt_long_outlined),
                Row(children: [
                  Expanded(child: _field('Purchase Price', _costCtrl,
                    hint: 'e.g. 45.00',
                    keyboardType: TextInputType.number,
                    prefix: '\$')),
                  const SizedBox(width: 12),
                  Expanded(child: _field('Estimated Value', _estValueCtrl,
                    hint: 'e.g. 75.00',
                    keyboardType: TextInputType.number,
                    prefix: '\$')),
                ]),
                _field('Purchased From', _fromCtrl,
                  hint: 'e.g. Heritage Auctions, eBay'),
                // Date picker
                _buildDatePicker(),
              ],
            ),
          ),

          // ── Storage & Notes ──────────────────────────────────────────────
          const SizedBox(height: 16),
          _card(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _sectionHeader('Storage & Notes', Icons.inventory_2_outlined),
                _field('Storage Location', _storageCtrl,
                  hint: 'e.g. Box 3, Slot 7, Safe'),
                _field('Notes', _notesCtrl,
                  hint: 'Any additional notes, provenance, or history',
                  maxLines: 3),
              ],
            ),
          ),

          // ── Error / Save ─────────────────────────────────────────────────
          const SizedBox(height: 24),
          if (_saveError.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Text(_saveError,
                style: const TextStyle(color: _C.red, fontSize: 13)),
            ),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _isSaving ? null : _save,
              icon: _isSaving
                  ? const SizedBox(
                      width: 18, height: 18,
                      child: CircularProgressIndicator(
                          color: Colors.white, strokeWidth: 2))
                  : const Icon(Icons.save_outlined, size: 20),
              label: Text(
                _isSaving ? 'Saving…' : 'Save to My Collection',
                style: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _C.accent, foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                disabledBackgroundColor: _C.border,
              ),
            ),
          ),
          const SizedBox(height: 40),
        ],
      ),
    );
  }

  // ── AI identification recap chip (compact) ────────────────────────────────
  Widget _buildAIRecapChip(GeminiIdentification g) {
    final level = g.level;
    Color chipColor;
    Color textColor;
    switch (level) {
      case ConfidenceLevel.high:
        chipColor = const Color(0xFFECFDF5);
        textColor = _C.green;
        break;
      case ConfidenceLevel.medium:
        chipColor = const Color(0xFFFFFBEB);
        textColor = _C.amber;
        break;
      case ConfidenceLevel.low:
        chipColor = const Color(0xFFFEF2F2);
        textColor = _C.red;
        break;
    }
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: chipColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(children: [
        const Text('🤖 ', style: TextStyle(fontSize: 14)),
        Expanded(child: Text(g.identification,
          style: const TextStyle(fontSize: 12, color: _C.text, height: 1.4),
          maxLines: 2, overflow: TextOverflow.ellipsis)),
        const SizedBox(width: 8),
        Text(g.confidencePercent,
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.w800, color: textColor)),
      ]),
    );
  }

  // ── Bullion live melt value widget ────────────────────────────────────────
  Widget _buildBullionMeltWidget() {
    final fmt = intl.NumberFormat.currency(symbol: r'$');
    final wt  = double.tryParse(_weightCtrl.text);
    final pur = double.tryParse(_purityCtrl.text);
    final spot = _spotPrices[_bullionMetal] ?? 0.0;
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFFF0FDF4),
        border: Border.all(color: const Color(0xFF86EFAC)),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(children: [
            Text('🪙 ', style: TextStyle(fontSize: 14)),
            Text('Live Bullion Value',
              style: TextStyle(fontWeight: FontWeight.w800, fontSize: 13, color: _C.text)),
          ]),
          const SizedBox(height: 6),
          if (spot > 0)
            Text(
              '${wt?.toStringAsFixed(4) ?? '?'} oz × '
              '${pur?.toStringAsFixed(4) ?? '?'} purity × '
              '${fmt.format(spot)}/oz',
              style: const TextStyle(fontSize: 12, color: _C.sub)),
          const SizedBox(height: 4),
          Text(
            _meltValue != null
                ? 'Melt Value: ${fmt.format(_meltValue!)}'
                : 'Enter weight and purity to calculate',
            style: TextStyle(
              fontSize: 15,
              fontWeight: FontWeight.w800,
              color: _meltValue != null ? _C.green : _C.sub,
            ),
          ),
          if (spot > 0)
            Text(
              'Spot: ${fmt.format(spot)}/oz · Updated live via Yahoo Finance',
              style: const TextStyle(fontSize: 11, color: _C.sub)),
        ],
      ),
    );
  }

  // ── Date picker ───────────────────────────────────────────────────────────
  Widget _buildDatePicker() {
    final fmt = intl.DateFormat('MMM d, yyyy');
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: GestureDetector(
        onTap: () async {
          final picked = await showDatePicker(
            context: context,
            initialDate: _datePurchased ?? DateTime.now(),
            firstDate: DateTime(1800),
            lastDate: DateTime.now(),
            builder: (ctx, child) => Theme(
              data: Theme.of(ctx).copyWith(
                colorScheme: const ColorScheme.light(primary: _C.accent),
              ),
              child: child!,
            ),
          );
          if (picked != null) setState(() => _datePurchased = picked);
        },
        child: AbsorbPointer(
          child: TextFormField(
            decoration: _inputDeco('Date Purchased', 'Tap to select date'),
            controller: TextEditingController(
              text: _datePurchased != null ? fmt.format(_datePurchased!) : '',
            ),
          ),
        ),
      ),
    );
  }

  // ── Shared form helpers ───────────────────────────────────────────────────
  Widget _field(
    String label,
    TextEditingController ctrl, {
    String hint = '',
    TextInputType keyboardType = TextInputType.text,
    String? prefix,
    int maxLines = 1,
    void Function(String)? onChanged,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: TextFormField(
        controller: ctrl,
        keyboardType: keyboardType,
        maxLines: maxLines,
        onChanged: onChanged,
        decoration: _inputDeco(label, hint, prefix: prefix),
      ),
    );
  }

  InputDecoration _inputDeco(String label, String hint, {String? prefix}) {
    return InputDecoration(
      labelText: label,
      hintText: hint,
      prefixText: prefix,
      labelStyle: const TextStyle(color: _C.sub, fontSize: 13),
      hintStyle: const TextStyle(color: Color(0xFFADB5BD), fontSize: 13),
      filled: true,
      fillColor: _C.fill,
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
      border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _C.border)),
      enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _C.border)),
      focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(8),
          borderSide: const BorderSide(color: _C.accent, width: 1.5)),
    );
  }

  Widget _sectionHeader(String title, IconData icon) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: Row(children: [
        Icon(icon, size: 16, color: const Color(0xFF94A3B8)),
        const SizedBox(width: 6),
        Text(title.toUpperCase(),
          style: const TextStyle(
            fontSize: 11, fontWeight: FontWeight.w700,
            color: _C.sub, letterSpacing: 0.5)),
        const SizedBox(width: 8),
        const Expanded(child: Divider(color: _C.border)),
      ]),
    );
  }

  Widget _card({required Widget child}) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      margin: const EdgeInsets.only(bottom: 0),
      decoration: BoxDecoration(
        color: _C.surface,
        border: Border.all(color: _C.border),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(
          color: Colors.black.withValues(alpha: 0.04),
          blurRadius: 6, offset: const Offset(0, 2))],
      ),
      child: child,
    );
  }
}
