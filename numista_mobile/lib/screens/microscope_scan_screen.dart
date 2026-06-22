import 'dart:async';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/hardware_service.dart';
import '../services/auth_service.dart';
import '../services/pcgs_service.dart';
import '../services/reference_library_service.dart';
import 'desktop_agent_download_screen.dart';


// ─── Design Tokens (matches inventory_gallery.dart) ───────────────────────────
const _electricBlue = Color(0xFF4C8CDA);
const _neuralBronze = Color(0xFF8B6B00);
const _charcoal = Color(0xFF31333F);
const _darkCard = Color(0xFF1E1E2E);
const _successGreen = Color(0xFF00C853);
const _warningAmber = Color(0xFFFFAB00);
const _errorRed = Color(0xFFFF5252);

class MicroscopeScanScreen extends StatefulWidget {
  const MicroscopeScanScreen({super.key});

  @override
  State<MicroscopeScanScreen> createState() => _MicroscopeScanScreenState();
}

class _MicroscopeScanScreenState extends State<MicroscopeScanScreen>
    with SingleTickerProviderStateMixin {
  final HardwareService _hw = HardwareService();

  // ─── State ─────────────────────────────────────────────────────────────────
  HardwareStatus? _status;
  bool _serverOnline = false;
  bool _isSaving = false;
  bool _savedOk = false;
  String? _savedFirestoreId;
  Timer? _pollTimer;
  Timer? _frameTimer;
  Uint8List? _liveFrameBytes;
  late AnimationController _pulseController;
  final TextEditingController _locationCtrl = TextEditingController();

  // ─── Similar Coins State ───────────────────────────────────────────────────
  List<ReferenceImage> _similarCoins = [];
  bool _loadingSimilar = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);
    _checkServer();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _frameTimer?.cancel();
    _pulseController.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  // ─── Server Ping ────────────────────────────────────────────────────────────
  Future<void> _checkServer() async {
    final online = await _hw.isServerRunning();
    if (mounted) {
      setState(() => _serverOnline = online);
      if (online) _startPolling();
    }
  }

  // ─── Polling ────────────────────────────────────────────────────────────────
  void _startPolling() {
    _pollTimer?.cancel();
    _frameTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(milliseconds: 500), (_) async {
      final status = await _hw.getStatus();
      if (mounted && status != null) {
        if (status.pairedEmail != AuthService.userEmail) {
          await _hw.pairAgent(AuthService.userEmail);
        }
        final wasComplete = _status?.isScanComplete == true;
        setState(() => _status = status);
        // Stop polling when the scan is fully complete
        if (status.isScanComplete) {
          _pollTimer?.cancel();
          // Trigger reference library fetch on first completion
          if (!wasComplete) _fetchSimilarCoins(status);
        }
      }
    });
    // Frame preview: poll /frame every 300ms while scanning
    _frameTimer = Timer.periodic(const Duration(milliseconds: 300), (_) async {
      final bytes = await _hw.fetchFrame();
      if (mounted && bytes != null) {
        setState(() => _liveFrameBytes = bytes);
      }
    });
  }

  Future<void> _fetchSimilarCoins(HardwareStatus status) async {
    final report = status.lastReport;
    if (report == null) return;
    final denom  = report['denomination']?.toString() ?? '';
    final yearRaw = report['year'];
    final year   = yearRaw is int ? yearRaw : int.tryParse(yearRaw?.toString() ?? '');
    if (denom.isEmpty) return;

    setState(() { _loadingSimilar = true; _similarCoins = []; });
    final imgs = await ReferenceLibraryService.fetchSimilar(
      denomination: denom, year: year);
    if (mounted) setState(() { _similarCoins = imgs; _loadingSimilar = false; });
  }

  // ─── Actions ────────────────────────────────────────────────────────────────
  Future<void> _startScan() async {
    setState(() {
      _savedOk = false;
      _savedFirestoreId = null;
    });
    final ok = await _hw.startScan();
    if (!ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          backgroundColor: _errorRed,
          content: Text(
            'Could not write scan command. Check your Firestore connection.',
            style: TextStyle(color: Colors.white),
          ),
          duration: Duration(seconds: 5),
        ),
      );
      return;
    }
    _startPolling();
  }

  Future<void> _confirmAndSave() async {
    final report = _status?.lastReport;
    if (report == null) return;

    setState(() => _isSaving = true);

    final coinData = {
      'file_slug': report['file_slug'] ?? 'scan_result',
      'year': report['year'],
      'country': report['country'] ?? 'USA',
      'denomination': report['denomination'] ?? '',
      'mint_mark': report['mint_mark'] ?? '',
      'grade': report['grade'] ?? 'Ungraded',
      'program_series': report['program_series'] ?? '',
      'theme_subject': report['theme_subject'] ?? '',
      'report': report['report'] ?? '',
      'source': 'Hardware Agent',
      'storage_location': _locationCtrl.text.trim().isNotEmpty
          ? _locationCtrl.text.trim()
          : 'Hardware Scan',
    };

    final firestoreId = await _hw.addToCollection(coinData);
    if (mounted) {
      setState(() {
        _isSaving = false;
        if (firestoreId != null) {
          _savedOk = true;
          _savedFirestoreId = firestoreId;
        }
      });
      if (firestoreId == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: _errorRed,
            content: Text('Save failed. Check server logs.'),
          ),
        );
      }
    }
  }

  // ─── Build ──────────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 24),
          _buildServerStatus(),
          const SizedBox(height: 32),
          if (_serverOnline) ...[
            _buildScanControls(),
            const SizedBox(height: 24),
            // ── Live camera preview (shown whenever a frame is available) ────────
            // This lets you see and adjust the microscope zoom BEFORE
            // pressing Start Scan, not just during an active scan.
            if (_serverOnline && _liveFrameBytes != null) ...[
              _buildLivePreview(),
              const SizedBox(height: 24),
            ],
            if (_status != null) _buildStatusPanel(),
            if (_status?.isScanComplete == true) ...[
              const SizedBox(height: 32),
              _buildResultPanel(),
              // ── Similar Coins panel ──────────────────────────────────────
              if (_loadingSimilar || _similarCoins.isNotEmpty) ...[
                const SizedBox(height: 24),
                _buildSimilarCoinsPanel(),
              ],
            ],
          ],
          if (_savedOk) ...[
            const SizedBox(height: 32),
            _buildSuccessBanner(),
          ],
        ],
      ),
    );
  }

  // ─── Header ─────────────────────────────────────────────────────────────────
  Widget _buildHeader() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Microscope Scanner',
          style: TextStyle(
            fontSize: 36,
            fontWeight: FontWeight.w900,
            color: _charcoal,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          'Jiusion / Tomlov USB Microscope  •  Gemini AI Vision',
          style: TextStyle(
            fontSize: 13,
            color: _charcoal.withValues(alpha: 0.5),
            fontStyle: FontStyle.italic,
          ),
        ),
      ],
    );
  }

  // ─── Server Status Banner ────────────────────────────────────────────────────
  Widget _buildServerStatus() {
    if (_serverOnline) {
      // ── Online state: compact green pill ────────────────────────────────────
      return Container(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 20),
        decoration: BoxDecoration(
          color: _successGreen.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: _successGreen.withValues(alpha: 0.4)),
        ),
        child: Row(
          children: [
            const Icon(Icons.circle, size: 12, color: _successGreen),
            const SizedBox(width: 10),
            const Text(
              'Hardware Server Online  •  localhost:5000',
              style: TextStyle(
                color: _successGreen,
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
            const Spacer(),
            TextButton.icon(
              onPressed: _checkServer,
              icon: const Icon(Icons.refresh, size: 16),
              label: const Text('Retry'),
              style: TextButton.styleFrom(foregroundColor: _successGreen),
            ),
          ],
        ),
      );
    }

    // ── Offline state: rich explainer card with download button ──────────────
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _errorRed.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _errorRed.withValues(alpha: 0.25)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Status pill
          Row(
            children: [
              const Icon(Icons.circle_outlined, size: 12, color: _errorRed),
              const SizedBox(width: 10),
              const Text(
                'Hardware Server Offline',
                style: TextStyle(
                  color: _errorRed,
                  fontWeight: FontWeight.w700,
                  fontSize: 13,
                ),
              ),
              const Spacer(),
              TextButton.icon(
                onPressed: _checkServer,
                icon: const Icon(Icons.refresh, size: 16),
                label: const Text('Retry'),
                style: TextButton.styleFrom(foregroundColor: _errorRed),
              ),
            ],
          ),
          const SizedBox(height: 12),
          const Divider(height: 1),
          const SizedBox(height: 16),

          // Explainer
          const Text(
            'To use the Microscope Scanner, install the free Desktop Agent on this computer.',
            style: TextStyle(color: _charcoal, fontSize: 14, height: 1.5),
          ),
          const SizedBox(height: 8),
          Text(
            'The Desktop Agent runs silently in your system tray and bridges your '  
            'USB microscope to numista.ai over a local HTTPS connection. '
            'Install takes about 30 seconds.',
            style: TextStyle(
              color: _charcoal.withValues(alpha: 0.6),
              fontSize: 12,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 20),

          // Download button
          ElevatedButton.icon(
            onPressed: () {
              Navigator.of(context).push(
                MaterialPageRoute(
                  builder: (_) =>
                      const DesktopAgentDownloadScreen(showBack: true),
                ),
              );
            },
            icon: const Icon(Icons.download_rounded, color: Colors.white, size: 20),
            label: const Text(
              'Download Desktop Agent',
              style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 14),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: _electricBlue,
              padding:
                  const EdgeInsets.symmetric(horizontal: 24, vertical: 14),
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
              elevation: 3,
            ),
          ),
          const SizedBox(height: 10),
          Text(
            'Free • Windows 10/11 • ~30 sec install',
            style: TextStyle(
              color: _charcoal.withValues(alpha: 0.45),
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  // ─── Live Camera Preview ─────────────────────────────────────────────────
  Widget _buildLivePreview() {
    final isScanning = _status?.isActive == true;
    final badgeColor  = isScanning ? _errorRed   : const Color(0xFF00BCD4); // red = LIVE, cyan = PREVIEW
    final badgeLabel  = isScanning ? 'LIVE'       : 'PREVIEW';
    final borderColor = isScanning ? _electricBlue : const Color(0xFF00BCD4);

    return Container(
      decoration: BoxDecoration(
        color: Colors.black,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: borderColor.withValues(alpha: 0.4), width: 2),
        boxShadow: [
          BoxShadow(
            color: borderColor.withValues(alpha: 0.2),
            blurRadius: 24,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      clipBehavior: Clip.antiAlias,
      child: Stack(
        children: [
          // Live frame image
          Image.memory(
            _liveFrameBytes!,
            fit: BoxFit.contain,
            width: double.infinity,
            gaplessPlayback: true, // prevents flicker between frames
          ),
          // State badge (LIVE or PREVIEW)
          Positioned(
            top: 12,
            right: 12,
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
              decoration: BoxDecoration(
                color: badgeColor.withValues(alpha: 0.85),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.fiber_manual_record, size: 8, color: Colors.white),
                  SizedBox(width: 4),
                  Text(badgeLabel,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 1.2)),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─── Scan Controls ────────────────────────────────────────────────────────
  Widget _buildScanControls() {
    final isScanning = _status?.isActive == true;
    return Row(
      children: [
        _buildActionButton(
          label: isScanning ? 'Scanning...' : '▶  Start Microscope Scan',
          color: isScanning ? _electricBlue.withValues(alpha: 0.5) : _electricBlue,
          icon: isScanning
              ? const SizedBox(
                  width: 18,
                  height: 18,
                  child: CircularProgressIndicator(
                      color: Colors.white, strokeWidth: 2))
              : const Icon(Icons.camera_alt_outlined, color: Colors.white, size: 20),
          onPressed: isScanning ? null : _startScan,
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required String label,
    required Color color,
    required Widget icon,
    VoidCallback? onPressed,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: icon,
      label: Text(label,
          style: const TextStyle(
              color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 18),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        elevation: 4,
      ),
    );
  }

  // ─── Live Status Panel ────────────────────────────────────────────────────
  Widget _buildStatusPanel() {
    final s = _status!;
    final isFlipping = s.waitingForFlip;
    final isCounting = s.isCountingDown;
    final isComplete = s.isScanComplete;

    final stepColor = isComplete
        ? _successGreen
        : isFlipping
            ? _warningAmber
            : isCounting
                ? _successGreen
                : _electricBlue;

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _darkCard,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: stepColor.withValues(alpha: 0.15),
            blurRadius: 28,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // ── Step header ─────────────────────────────────────────────────────
          Row(
            children: [
              AnimatedBuilder(
                animation: _pulseController,
                builder: (context, _) => Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: stepColor.withValues(
                        alpha: s.isActive
                            ? 0.4 + (_pulseController.value * 0.6)
                            : 1.0),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Text(
                isComplete
                    ? '✓  SCAN COMPLETE'
                    : isFlipping
                        ? '⟳  FLIP COIN NOW'
                        : isCounting
                            ? '🟢  HOLD STILL'
                            : 'STEP: ${s.currentStep}',
                style: TextStyle(
                    color: stepColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    letterSpacing: 1.2),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // ── Pre-capture countdown ring ───────────────────────────────────────
          if (isCounting) ...[
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: s.captureCountdownPct,
                      strokeWidth: 8,
                      backgroundColor: Colors.white12,
                      valueColor:
                          const AlwaysStoppedAnimation<Color>(_successGreen),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        s.captureCountdownRemaining!.toStringAsFixed(1),
                        style: const TextStyle(
                            color: _successGreen,
                            fontSize: 34,
                            fontWeight: FontWeight.w900),
                      ),
                      const Text('seconds',
                          style: TextStyle(
                              color: Colors.white38,
                              fontSize: 11,
                              letterSpacing: 1.0)),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            const Center(
              child: Text(
                'Any movement resets the countdown',
                style: TextStyle(
                    color: Colors.white38,
                    fontSize: 11,
                    fontStyle: FontStyle.italic),
              ),
            ),
            const SizedBox(height: 20),
          ],

          // ── Flip-coin countdown ring ─────────────────────────────────────────
          if (isFlipping) ...[
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 120,
                    height: 120,
                    child: CircularProgressIndicator(
                      value: s.flipCountdownPct,
                      strokeWidth: 8,
                      backgroundColor: Colors.white12,
                      valueColor:
                          const AlwaysStoppedAnimation<Color>(_warningAmber),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.flip, color: _warningAmber, size: 26),
                      const SizedBox(height: 4),
                      Text(
                        s.flipTimeRemaining != null
                            ? '${s.flipTimeRemaining!.toStringAsFixed(1)}s'
                            : '…',
                        style: const TextStyle(
                            color: _warningAmber,
                            fontSize: 22,
                            fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 8),
            const Center(
              child: Text(
                'Flip and place the coin in the circle',
                style: TextStyle(color: Colors.white54, fontSize: 12),
              ),
            ),
            const SizedBox(height: 20),
          ],

          // ── Status message (shown when not actively counting down) ────────────
          if (!isCounting && !isFlipping) ...[
            Text(
              s.statusMessage,
              style: TextStyle(
                  color: Colors.white70,
                  fontSize: 14,
                  fontStyle: s.statusMessage == 'READY!'
                      ? FontStyle.normal
                      : FontStyle.italic),
            ),
            const SizedBox(height: 20),
          ],

          // ── Sharpness meter ──────────────────────────────────────────────────
          _buildMeter(
            label: 'Sharpness',
            value: s.sharpnessPct,
            current: s.sharpness,
            max: s.maxSharpness,
            color: s.sharpnessPct > 0.8
                ? _successGreen
                : s.sharpnessPct > 0.5
                    ? _warningAmber
                    : _errorRed,
          ),
          const SizedBox(height: 12),

          // ── Motion pill ──────────────────────────────────────────────────────
          Row(
            children: [
              Text('Motion:',
                  style: TextStyle(
                      color: Colors.white54,
                      fontSize: 12,
                      letterSpacing: 0.8)),
              const SizedBox(width: 8),
              Text(
                s.motion.toStringAsFixed(2),
                style: TextStyle(
                    color: s.motion < 2.0 ? _successGreen : _warningAmber,
                    fontWeight: FontWeight.bold,
                    fontSize: 13),
              ),
              const SizedBox(width: 8),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: (s.motion < 2.0 ? _successGreen : _warningAmber)
                      .withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  s.motion < 2.0 ? 'STABLE' : 'MOVING',
                  style: TextStyle(
                      color: s.motion < 2.0 ? _successGreen : _warningAmber,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2),
                ),
              ),
            ],
          ),

          // ── Error display ────────────────────────────────────────────────────
          if (s.error != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: _errorRed.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: _errorRed, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(s.error!,
                        style:
                            const TextStyle(color: _errorRed, fontSize: 12)),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }


  Widget _buildMeter({
    required String label,
    required double value,
    required int current,
    required int max,
    required Color color,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label.toUpperCase(),
                style: const TextStyle(
                    color: Colors.white54, fontSize: 11, letterSpacing: 1.2)),
            Text('$current / $max',
                style: const TextStyle(color: Colors.white54, fontSize: 11)),
          ],
        ),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value,
            backgroundColor: Colors.white12,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  // ─── Scan Result Panel ────────────────────────────────────────────────────
  Widget _buildResultPanel() {
    final report = _status!.lastReport!;
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _successGreen.withValues(alpha: 0.4)),
        boxShadow: [
          BoxShadow(
            color: _successGreen.withValues(alpha: 0.08),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'AI Identification Result',
            style: TextStyle(
                color: _charcoal,
                fontSize: 20,
                fontWeight: FontWeight.w800),
          ),
          const Divider(height: 24),
          _buildResultRow('Year', report['year']?.toString() ?? '—'),
          _buildResultRow('Country', report['country']?.toString() ?? '—'),
          _buildResultRow('Denomination', report['denomination']?.toString() ?? '—'),
          _buildResultRow('Series', report['program_series']?.toString() ?? '—'),
          _buildResultRow('Theme', report['theme_subject']?.toString() ?? '—'),
          _buildResultRow('Grade', report['grade']?.toString() ?? '—'),
          _buildResultRow('File ID', report['file_slug']?.toString() ?? '—'),

          // ── Silver / Metal Intelligence Banner ──────────────────────────
          Builder(builder: (_) {
            final pcgsData = PCGSService.parseFromReport(report);
            return _buildSilverPanel(pcgsData);
          }),
          if (report['report'] != null) ...[
            const SizedBox(height: 16),
            const Text('Gemini Analysis:',
                style: TextStyle(
                    color: _charcoal,
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    letterSpacing: 0.8)),
            const SizedBox(height: 8),
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFFD3E3FD),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                report['report'].toString(),
                style: const TextStyle(color: Color(0xFF003884), fontSize: 13),
              ),
            ),
          ],
          const SizedBox(height: 24),
          const Text('Storage Location', style: TextStyle(color: _charcoal, fontSize: 13, fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          TextField(
            controller: _locationCtrl,
            decoration: InputDecoration(
              hintText: 'e.g., Safe Box 1, Album C...',
              filled: true,
              fillColor: Colors.black.withValues(alpha: 0.03),
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide.none),
              contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            ),
          ),
          const SizedBox(height: 24),
          Row(
            children: [
              _buildActionButton(
                label: _isSaving ? 'Saving...' : '✚  Add to Collection',
                color: _isSaving
                    ? _successGreen.withValues(alpha: 0.5)
                    : _successGreen,
                icon: _isSaving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                            color: Colors.white, strokeWidth: 2))
                    : const Icon(Icons.add_box_outlined,
                        color: Colors.white, size: 20),
                onPressed: (_isSaving || _savedOk) ? null : _confirmAndSave,
              ),
              const SizedBox(width: 16),
              TextButton.icon(
                onPressed: () => setState(() {
                  _savedOk = false;
                  _savedFirestoreId = null;
                }),
                icon: const Icon(Icons.refresh, size: 18, color: _charcoal),
                label: const Text('Discard & Rescan',
                    style: TextStyle(color: _charcoal)),
              ),
            ],
          ),
        ],
      ),
    );
  }

  // ─── Silver / Metal Intelligence Panel ──────────────────────────────────────
  Widget _buildSilverPanel(PCGSCoinData data) {
    final isSilver = data.isSilver;
    final panelColor = isSilver
        ? const Color(0xFF9E9E9E).withValues(alpha: 0.12) // Silver grey tint
        : _charcoal.withValues(alpha: 0.05);
    final borderColor = isSilver
        ? const Color(0xFFB0BEC5).withValues(alpha: 0.6)
        : _charcoal.withValues(alpha: 0.15);
    final accentColor = isSilver ? const Color(0xFF78909C) : _charcoal;
    final badgeColor  = isSilver ? const Color(0xFF546E7A) : const Color(0xFF9E9E9E);

    return Padding(
      padding: const EdgeInsets.only(top: 16, bottom: 4),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: panelColor,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: borderColor),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ── Verdict badge ──────────────────────────────────────────────
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                  decoration: BoxDecoration(
                    color: badgeColor,
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        isSilver ? '🥈' : '🔵',
                        style: const TextStyle(fontSize: 16),
                      ),
                      const SizedBox(width: 6),
                      Text(
                        isSilver ? 'SILVER COIN' : 'NOT SILVER',
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.w800,
                          fontSize: 13,
                          letterSpacing: 1.0,
                        ),
                      ),
                    ],
                  ),
                ),
                if (isSilver) ...[ 
                  const SizedBox(width: 10),
                  Text(
                    'Worth more than face value!',
                    style: TextStyle(
                      color: accentColor,
                      fontSize: 12,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 12),

            // ── Metal content ──────────────────────────────────────────────
            if (data.metalContent.isNotEmpty && data.metalContent != 'Unknown') ...[
              _buildMetalRow('Metal', data.metalContent, accentColor),
              const SizedBox(height: 6),
            ],

            // ── Melt value ────────────────────────────────────────────────
            if (isSilver && data.meltValueEstimate != '—') ...[
              _buildMetalRow(
                'Melt Value',
                '${data.meltValueEstimate}  (${data.silverTroyOz.toStringAsFixed(5)} troy oz Ag)',
                accentColor,
              ),
              const SizedBox(height: 6),
            ],

            // ── PCGS number ────────────────────────────────────────────────
            if (data.pcgsNumber != null) ...[
              _buildMetalRow('PCGS #', data.pcgsNumber.toString(), accentColor),
              const SizedBox(height: 6),
            ],

            // ── PCGS price guide ──────────────────────────────────────────
            if (data.pcgsPriceGuide != null) ...[
              _buildMetalRow('Price Guide', data.pcgsPriceGuide!, accentColor),
            ],

            // ── PCGS population ───────────────────────────────────────────
            if (data.populationSummary != null) ...[
              const SizedBox(height: 6),
              _buildMetalRow('Population', data.populationSummary!, accentColor),
            ],

            // ── Fallback if PCGS unavailable ──────────────────────────────
            if (data.pcgsNumber == null)
              Text(
                'PCGS CoinFacts lookup not available for this variety.',
                style: TextStyle(
                  color: accentColor.withValues(alpha: 0.6),
                  fontSize: 11,
                  fontStyle: FontStyle.italic,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetalRow(String label, String value, Color accentColor) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 90,
          child: Text(
            label,
            style: TextStyle(
              color: accentColor,
              fontSize: 12,
              fontWeight: FontWeight.w600,
            ),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: TextStyle(color: accentColor, fontSize: 12),
          ),
        ),
      ],
    );
  }

  Widget _buildResultRow(String label, String value) {

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(label,
                style: const TextStyle(
                    color: _charcoal,
                    fontSize: 13,
                    fontWeight: FontWeight.w600)),
          ),
          Text(value,
              style: TextStyle(
                  color: label == 'Year' ? _neuralBronze : _charcoal,
                  fontSize: 15,
                  fontWeight:
                      label == 'Year' ? FontWeight.bold : FontWeight.normal)),
        ],
      ),
    );
  }

  // ─── Similar Coins Panel ─────────────────────────────────────────────────
  Widget _buildSimilarCoinsPanel() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _darkCard,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: _electricBlue.withValues(alpha: 0.10),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.photo_library_outlined,
                  color: _electricBlue, size: 18),
              const SizedBox(width: 8),
              const Text(
                'Similar Coins in Reference Library',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.w700,
                  fontSize: 15,
                  letterSpacing: 0.4,
                ),
              ),
              const Spacer(),
              if (_loadingSimilar)
                const SizedBox(
                  width: 16,
                  height: 16,
                  child: CircularProgressIndicator(
                    color: _electricBlue,
                    strokeWidth: 2,
                  ),
                ),
            ],
          ),
          const SizedBox(height: 14),
          if (_loadingSimilar)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 20),
              child: Center(
                child: Text(
                  'Searching reference library…',
                  style: TextStyle(color: Colors.white38, fontSize: 12,
                      fontStyle: FontStyle.italic),
                ),
              ),
            )
          else if (_similarCoins.isEmpty)
            const Padding(
              padding: EdgeInsets.symmetric(vertical: 12),
              child: Text(
                'No matching reference images found for this denomination/year.',
                style: TextStyle(color: Colors.white38, fontSize: 12,
                    fontStyle: FontStyle.italic),
              ),
            )
          else
            SizedBox(
              height: 130,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _similarCoins.length,
                separatorBuilder: (_, _) => const SizedBox(width: 10),
                itemBuilder: (ctx, i) =>
                    _buildRefThumb(ctx, _similarCoins[i], i),
              ),
            ),
          if (_similarCoins.isNotEmpty) ...[
            const SizedBox(height: 10),
            Text(
              'Source: Kaggle reference datasets  •  Tap image to expand',
              style: TextStyle(
                fontSize: 10,
                color: Colors.white.withValues(alpha: 0.28),
                fontStyle: FontStyle.italic,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildRefThumb(BuildContext ctx, ReferenceImage img, int idx) {
    return GestureDetector(
      onTap: () => _showRefImageDialog(ctx, img, idx),
      child: Container(
        width: 110,
        decoration: BoxDecoration(
          color: Colors.black26,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white12),
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: Stack(
            fit: StackFit.expand,
            children: [
              Image.network(
                img.gcsUrl,
                fit: BoxFit.cover,
                loadingBuilder: (_, child, progress) => progress == null
                    ? child
                    : Container(
                        color: Colors.white10,
                        child: const Center(
                          child: CircularProgressIndicator(
                            color: _electricBlue,
                            strokeWidth: 2,
                          ),
                        ),
                      ),
                errorBuilder: (_, _, _) => const Icon(
                    Icons.broken_image_outlined,
                    color: Colors.white30,
                    size: 32),
              ),
              // Year badge at bottom
              if (img.year != null && img.year!.isNotEmpty &&
                  img.year != 'Unknown')
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: Container(
                    padding: const EdgeInsets.symmetric(
                        vertical: 3, horizontal: 6),
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        begin: Alignment.bottomCenter,
                        end: Alignment.topCenter,
                        colors: [Colors.black87, Colors.transparent],
                      ),
                    ),
                    child: Text(
                      img.year!,
                      style: const TextStyle(
                          color: Colors.white,
                          fontSize: 11,
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
  }

  void _showRefImageDialog(BuildContext ctx, ReferenceImage img, int idx) {
    showDialog(
      context: ctx,
      builder: (_) => Dialog(
        backgroundColor: Colors.transparent,
        insetPadding: const EdgeInsets.all(24),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(16),
          child: Container(
            color: const Color(0xFF1A1A2E),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // ── Image ───────────────────────────────────────────────────
                ConstrainedBox(
                  constraints: const BoxConstraints(maxHeight: 400),
                  child: Image.network(
                    img.gcsUrl,
                    fit: BoxFit.contain,
                    errorBuilder: (_, _, _) => const Padding(
                      padding: EdgeInsets.all(40),
                      child: Icon(Icons.broken_image_outlined,
                          color: Colors.white30, size: 60),
                    ),
                  ),
                ),
                // ── Caption ─────────────────────────────────────────────────
                Padding(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        img.caption,
                        style: const TextStyle(
                            color: Colors.white70, fontSize: 12),
                      ),
                      if (img.licenseUrl != null) ...[
                        const SizedBox(height: 6),
                        GestureDetector(
                          onTap: () async {
                            final uri = Uri.tryParse(img.licenseUrl!);
                            if (uri != null) await launchUrl(uri);
                          },
                          child: Text(
                            img.licenseUrl!,
                            style: const TextStyle(
                              color: _electricBlue,
                              fontSize: 11,
                              decoration: TextDecoration.underline,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
                // ── Dismiss ─────────────────────────────────────────────────
                TextButton(
                  onPressed: () => Navigator.pop(ctx),
                  child: const Text('Close',
                      style: TextStyle(color: _electricBlue)),
                ),
                const SizedBox(height: 8),
              ],
            ),
          ),
        ),
      ),
    );
  }

  // ─── Success Banner ───────────────────────────────────────────────────────
  Widget _buildSuccessBanner() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _successGreen.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _successGreen.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          const Icon(Icons.check_circle, color: _successGreen, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Coin Added to Your Vault!',
                  style: TextStyle(
                      color: _successGreen,
                      fontWeight: FontWeight.bold,
                      fontSize: 16),
                ),
                const SizedBox(height: 4),
                Text(
                  'It will appear in your Inventory Gallery momentarily via Firestore real-time sync.',
                  style:
                      TextStyle(color: _successGreen.withValues(alpha: 0.8), fontSize: 13),
                ),
                if (_savedFirestoreId != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    'ID: $_savedFirestoreId',
                    style: const TextStyle(
                        color: Colors.black38, fontSize: 11, fontFamily: 'monospace'),
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }
}
