import 'dart:async';
import 'dart:typed_data';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:http/http.dart' as http;
import '../constants.dart';
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
  late AnimationController _pulseController;
  final TextEditingController _locationCtrl = TextEditingController();

  // ─── Similar Coins State ───────────────────────────────────────────────────
  List<ReferenceImage> _similarCoins = [];
  bool _loadingSimilar = false;

  // ─── Camera Selector State ─────────────────────────────────────────────────
  List<int> _availableCameras = [];
  int _activeCameraIdx = -1;
  bool _loadingCameras = false;

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
    _pulseController.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  // ─── Server Ping ────────────────────────────────────────────────────────────
  Future<void> _checkServer() async {
    final online = await _hw.isServerRunning();
    if (mounted) {
      setState(() => _serverOnline = online);
      if (online) {
        _startPolling();
        _loadCameras();
      }
    }
  }

  Future<void> _loadCameras() async {
    if (!mounted) return;
    setState(() => _loadingCameras = true);
    final res = await _hw.listCameras();
    if (mounted) {
      setState(() {
        _availableCameras = List<int>.from(res['cameras'] ?? []);
        _activeCameraIdx = res['active'] as int? ?? -1;
        _loadingCameras = false;
      });
    }
  }

  // ─── Polling ────────────────────────────────────────────────────────────────
  void _startPolling() {
    _pollTimer?.cancel();
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

  Future<void> _confirmFlip() async {
    // Tell the hardware agent to immediately clear the flip lockout and begin
    // scanning the reverse side — no need to wait for the 8-second auto-timer.
    await _hw.confirmFlip();
    // Polling will pick up the updated state on the next tick.
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
            // ── Live camera feed (only shown during an active scan) ──────────
            // The cv2 window on the desktop is the primary focusing display.
            // The web frame here shows the annotated obverse/reverse overlay
            // during scanning so the user can see step progress.
            // ── Desktop focus pop-up instruction banner ──────────────────────
            if (_serverOnline && _status?.isActive == true) ...[
              _buildInstructionCard(),
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

  // ─── Instruction Banner ───────────────────────────────────────────────────
  Widget _buildInstructionCard() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: _darkCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _electricBlue.withValues(alpha: 0.3), width: 1.5),
        boxShadow: [
          BoxShadow(
            color: _electricBlue.withValues(alpha: 0.15),
            blurRadius: 20,
            offset: const Offset(0, 6),
          ),
        ],
      ),
      child: Row(
        children: [
          const Icon(
            Icons.desktop_windows_rounded,
            color: _electricBlue,
            size: 32,
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Focus Microscope Locally',
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  'Please look for a pop-up window on your computer screen to help align and focus the microscope.',
                  style: TextStyle(
                    color: Colors.white.withValues(alpha: 0.7),
                    fontSize: 13,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Scan Controls ────────────────────────────────────────────────────────
  Widget _buildScanControls() {
    final isScanning = _status?.isActive == true;
    return Wrap(
      spacing: 16,
      runSpacing: 16,
      crossAxisAlignment: WrapCrossAlignment.center,
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
        if (_availableCameras.isNotEmpty) ...[
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
            decoration: BoxDecoration(
              color: _darkCard,
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: _electricBlue.withValues(alpha: 0.3)),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<int>(
                value: _activeCameraIdx != -1 && _availableCameras.contains(_activeCameraIdx) ? _activeCameraIdx : null,
                dropdownColor: _darkCard,
                icon: const Icon(Icons.arrow_drop_down, color: _electricBlue),
                hint: const Text('Select Camera', style: TextStyle(color: Colors.grey, fontSize: 14)),
                items: _availableCameras.map((int idx) {
                  String label = 'Camera $idx';
                  if (idx == 0) {
                    label = 'Camera 0 (Built-in Webcam)';
                  } else if (idx == 1 || idx == 2) {
                    label = 'Camera $idx (USB Microscope)';
                  }
                  return DropdownMenuItem<int>(
                    value: idx,
                    child: Text(label, style: const TextStyle(color: Colors.white, fontSize: 14)),
                  );
                }).toList(),
                onChanged: isScanning
                    ? null
                    : (int? newIdx) async {
                        if (newIdx != null) {
                          final ok = await _hw.setCameraIndex(newIdx);
                          if (ok) {
                            setState(() => _activeCameraIdx = newIdx);
                          }
                        }
                      },
              ),
            ),
          ),
          IconButton(
            onPressed: isScanning ? null : _loadCameras,
            icon: _loadingCameras
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(color: _electricBlue, strokeWidth: 2),
                  )
                : const Icon(Icons.refresh, color: _electricBlue),
            tooltip: 'Refresh camera list',
          ),
        ],
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

          // ── Flip-coin: explicit button + auto-timer ring ─────────────────────
          if (isFlipping) ...[
            // Instruction heading
            const Center(
              child: Text(
                'Obverse captured — flip the coin over',
                style: TextStyle(
                  color: _warningAmber,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  letterSpacing: 0.5,
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Explicit flip button — the primary CTA
            Center(
              child: ElevatedButton.icon(
                onPressed: _confirmFlip,
                icon: const Icon(Icons.flip, color: Colors.white, size: 22),
                label: const Text(
                  "I've flipped the coin — Scan Reverse",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _warningAmber,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 28, vertical: 16),
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(10)),
                  elevation: 6,
                ),
              ),
            ),
            const SizedBox(height: 20),

            // Auto-timer ring (secondary — fires if user doesn't tap button)
            const Center(
              child: Text(
                'Or wait for auto-advance:',
                style: TextStyle(color: Colors.white38, fontSize: 11),
              ),
            ),
            const SizedBox(height: 8),
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 80,
                    height: 80,
                    child: CircularProgressIndicator(
                      value: s.flipCountdownPct,
                      strokeWidth: 6,
                      backgroundColor: Colors.white12,
                      valueColor:
                          const AlwaysStoppedAnimation<Color>(_warningAmber),
                    ),
                  ),
                  Text(
                    s.flipTimeRemaining != null
                        ? '${s.flipTimeRemaining!.toStringAsFixed(1)}s'
                        : '…',
                    style: const TextStyle(
                        color: _warningAmber,
                        fontSize: 16,
                        fontWeight: FontWeight.bold),
                  ),
                ],
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
          _buildResultRow('Mint Mark', report['mint_mark']?.toString() ?? '—'),
          _buildResultRow('Series', report['program_series']?.toString() ?? '—'),
          _buildResultRow('Theme', report['theme_subject']?.toString() ?? '—'),
          _buildResultRow('Grade', report['grade']?.toString() ?? '—'),
          _buildResultRow('File ID', report['file_slug']?.toString() ?? '—'),

          // ── Silver / Metal Intelligence Banner ──────────────────────────
          Builder(builder: (_) {
            final pcgsData = PCGSService.parseFromReport(report);
            return _buildSilverPanel(pcgsData);
          }),
          if (report['grade'] != null && report['grade'].toString() != 'Ungraded')
            _MicroscopePricingAdvisor(
              year: report['year']?.toString() ?? '',
              mintMark: report['mint_mark']?.toString() ?? '',
              denomination: report['denomination']?.toString() ?? '',
              programSeries: report['program_series']?.toString() ?? '',
              variety: report['variety']?.toString() ?? '',
              currentGrade: report['grade']?.toString() ?? '',
              isSlabbed: (report['grading_service']?.toString() ?? '').isNotEmpty ||
                  (report['holder_type']?.toString() ?? '').toLowerCase().contains('slab'),
            ),
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

class _MicroscopePricingAdvisor extends StatefulWidget {
  final String year;
  final String mintMark;
  final String denomination;
  final String programSeries;
  final String variety;
  final String currentGrade;
  final bool isSlabbed;

  const _MicroscopePricingAdvisor({
    required this.year,
    required this.mintMark,
    required this.denomination,
    required this.programSeries,
    required this.variety,
    required this.currentGrade,
    this.isSlabbed = false,
  });

  @override
  State<_MicroscopePricingAdvisor> createState() => _MicroscopePricingAdvisorState();
}

class _MicroscopePricingAdvisorState extends State<_MicroscopePricingAdvisor> {
  bool _loading = true;
  String? _gsid;
  List<dynamic> _pricing = [];

  @override
  void initState() {
    super.initState();
    _resolveAndFetch();
  }

  Future<void> _resolveAndFetch() async {
    try {
      // 1. Resolve GSID
      final resolveUrl = Uri.parse('$kApiBaseUrl/api/greysheet/resolve');
      final resolveResp = await http.post(
        resolveUrl,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'year': widget.year,
          'mint_mark': widget.mintMark,
          'denomination': widget.denomination,
          'program_series': widget.programSeries,
          'variety': widget.variety,
        }),
      );

      if (resolveResp.statusCode == 200) {
        final resolveData = jsonDecode(resolveResp.body);
        final gsid = resolveData['gsid']?.toString();
        if (gsid != null && gsid.isNotEmpty) {
          _gsid = gsid;
          // 2. Fetch Pricing table
          final pricingUrl = Uri.parse('$kApiBaseUrl/api/greysheet/pricing/$gsid');
          final pricingResp = await http.get(pricingUrl);
          if (pricingResp.statusCode == 200) {
            final pricingData = jsonDecode(pricingResp.body);
            if (mounted) {
              setState(() {
                _pricing = pricingData['pricing'] ?? [];
                _loading = false;
              });
            }
            return;
          }
        }
      }
    } catch (_) {}
    if (mounted) {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Padding(
        padding: EdgeInsets.symmetric(vertical: 12),
        child: Center(
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: _electricBlue)),
              SizedBox(width: 10),
              Text('Analyzing Greysheet pricing curve...', style: TextStyle(fontSize: 12, color: Colors.grey)),
            ],
          ),
        ),
      );
    }

    if (_pricing.isEmpty) {
      return const SizedBox.shrink();
    }

    // Parse numeric grade for comparison (e.g. "MS65" -> 65)
    final gradeReg = RegExp(r'\d+');
    final match = gradeReg.firstMatch(widget.currentGrade);
    final targetGradeNo = match != null ? int.tryParse(match.group(0)!) : null;

    if (targetGradeNo == null) {
      return const SizedBox.shrink();
    }

    // Filter surrounding grades (±3 sheldon numbers, excluding CAC records)
    final surrounding = _pricing.where((p) {
      final isCac = p['IsCac'] ?? false;
      if (isCac) return false;
      final gradeNo = p['Grade'] as int?;
      if (gradeNo == null) return false;
      return (gradeNo - targetGradeNo).abs() <= 10; // Up to 10 points range
    }).toList();

    // Sort by Sheldon grade numeric value
    surrounding.sort((a, b) => (a['Grade'] as int).compareTo(b['Grade'] as int));

    // Find value of current grade for delta calculation
    double? currentGradeValue;
    for (final p in surrounding) {
      if (p['Grade'] == targetGradeNo) {
        currentGradeValue = double.tryParse((p['CpgVal'] ?? '').toString().replaceAll(',', ''));
        break;
      }
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const SizedBox(height: 16),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text(
              'Sheldon Grade Pricing Advisor',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: _electricBlue,
                letterSpacing: 0.8,
              ),
            ),
            if (_gsid != null)
              Text(
                'GSID: #$_gsid',
                style: const TextStyle(
                  fontSize: 11,
                  color: Colors.grey,
                  fontWeight: FontWeight.w500,
                ),
              ),
          ],
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          decoration: BoxDecoration(
            color: const Color(0xFFF8F9FA),
            borderRadius: BorderRadius.circular(8),
            border: Border.all(color: const Color(0xFFE9ECEF)),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: surrounding.length,
            separatorBuilder: (context, index) => const Divider(height: 1, color: Color(0xFFE9ECEF)),
            itemBuilder: (context, index) {
              final p = surrounding[index];
              final label = p['GradeLabel'] ?? '';
              final cpgValStr = p['CpgVal'] ?? '';
              final gradeNo = p['Grade'] as int;
              
              final isCurrent = gradeNo == targetGradeNo;
              final val = double.tryParse(cpgValStr.replaceAll(',', ''));

              String deltaText = '';
              Color deltaColor = Colors.grey;

              if (val != null && currentGradeValue != null && !isCurrent) {
                final diff = val - currentGradeValue;
                if (diff > 0) {
                  deltaText = '(+\$${diff.toStringAsFixed(0)} value jump!)';
                  deltaColor = _successGreen;
                } else if (diff < 0) {
                  deltaText = '(-\$${diff.abs().toStringAsFixed(0)})';
                  deltaColor = Colors.redAccent;
                }
              }

              return Padding(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Text(
                          label,
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                            color: isCurrent ? _electricBlue : _charcoal,
                          ),
                        ),
                        if (isCurrent) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: _electricBlue.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: const Text(
                              'Identified',
                              style: TextStyle(fontSize: 9, color: _electricBlue, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ],
                    ),
                    Row(
                      children: [
                        if (deltaText.isNotEmpty) ...[
                          Text(
                            deltaText,
                            style: TextStyle(fontSize: 11, color: deltaColor, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(width: 8),
                        ],
                        Text(
                          cpgValStr.isEmpty ? '—' : '\$$cpgValStr',
                          style: TextStyle(
                            fontSize: 13,
                            fontWeight: isCurrent ? FontWeight.bold : FontWeight.normal,
                            color: isCurrent ? _electricBlue : _charcoal,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ),
        if (widget.isSlabbed) ...[
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFE8F5E9),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: const Color(0xFFC8E6C9)),
            ),
            child: const Row(
              children: [
                Icon(Icons.info_outline, color: Color(0xFF2E7D32), size: 16),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Verification Alert: Check physical holder for a green or gold CAC sticker. It adds 20%-50%+ premium value!',
                    style: TextStyle(fontSize: 11, color: Color(0xFF2E7D32), fontWeight: FontWeight.w600),
                  ),
                ),
              ],
            ),
          ),
        ],
      ],
    );
  }
}
