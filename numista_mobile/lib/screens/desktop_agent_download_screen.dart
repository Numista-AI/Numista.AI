import 'dart:async';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/hardware_service.dart';
import '../services/auth_service.dart';

// ─── Design tokens ────────────────────────────────────────────────────────────
const _bg           = Color(0xFF0B1220);
const _card         = Color(0xFF1A2540);
const _electricBlue = Color(0xFF4C8CDA);
const _gold         = Color(0xFFC9A84C);
const _successGreen = Color(0xFF00C853);
const _warningAmber = Color(0xFFFFAB00);
const _errorRed     = Color(0xFFFF5252);
const _muted        = Color(0xFF94A3B8);
const _white        = Colors.white;

// ─── Public GCS download URLs ─────────────────────────────────────────────────
const _kWindowsInstallerUrl =
    'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/'
    'downloads/NumistaAgentSetup.exe';

const _kWindowsStandaloneUrl =
    'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/'
    'downloads/numista-agent.exe';

// ─── Screen ──────────────────────────────────────────────────────────────────
class DesktopAgentDownloadScreen extends StatefulWidget {
  /// If true, shows a "Back" button (used when pushed from MicroscopeScanScreen).
  final bool showBack;

  const DesktopAgentDownloadScreen({super.key, this.showBack = false});

  @override
  State<DesktopAgentDownloadScreen> createState() =>
      _DesktopAgentDownloadScreenState();
}

class _DesktopAgentDownloadScreenState
    extends State<DesktopAgentDownloadScreen> {
  final HardwareService _hw = HardwareService();

  Timer? _pollTimer;

  // Diagnostics State
  bool _isChecking = true;
  bool _localHostOk = false;
  bool _sslTrustOk = false;
  bool _cameraDetected = false;
  int _cameraCount = 0;
  bool _accountPaired = false;
  String? _agentPairedEmail;

  @override
  void initState() {
    super.initState();
    _runDiagnostics();
    _startAdaptivePolling(const Duration(seconds: 2));
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  void _startAdaptivePolling(Duration interval) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(interval, (_) => _runDiagnostics());
  }

  Future<void> _runDiagnostics() async {
    if (!mounted) return;

    final isRunning = await _hw.isServerRunning();
    HardwareStatus? status;
    Map<String, dynamic> camData = {'cameras': <int>[], 'active': -1};

    if (isRunning) {
      status = await _hw.getStatus();
      camData = await _hw.listCameras();
    }

    if (!mounted) return;

    final cameras = List<int>.from(camData['cameras'] ?? []);
    final userEmail = AuthService.userEmail;
    final pairedEmail = status?.pairedEmail;
    final paired = pairedEmail != null &&
        pairedEmail.isNotEmpty &&
        (userEmail.isEmpty || pairedEmail.toLowerCase() == userEmail.toLowerCase());

    setState(() {
      _isChecking = false;
      _localHostOk = isRunning;
      _sslTrustOk = isRunning && status != null; // HTTPS handshake succeeded
      _cameraCount = cameras.length;
      _cameraDetected = cameras.isNotEmpty;
      _agentPairedEmail = pairedEmail;
      _accountPaired = paired;
    });

    // Adaptive backoff: poll every 2s if online/checking, 8s if agent offline
    final nextInterval =
        isRunning ? const Duration(seconds: 2) : const Duration(seconds: 8);
    if (_pollTimer?.tick != null && _pollTimer!.tick % 4 == 0) {
      _startAdaptivePolling(nextInterval);
    }
  }

  bool get _isFullyConnected =>
      _localHostOk && _sslTrustOk && _cameraDetected && _accountPaired;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: widget.showBack
          ? AppBar(
              backgroundColor: _card,
              foregroundColor: _white,
              title: const Text('Desktop Agent'),
              leading: IconButton(
                icon: const Icon(Icons.arrow_back),
                onPressed: () => Navigator.of(context).pop(),
              ),
            )
          : null,
      body: SingleChildScrollView(
        child: Column(
          children: [
            _buildMorganGuidanceBanner(),
            _buildHero(),
            _buildPrivacyCard(),
            _buildStatusBanner(),
            _buildDiagnosticsCard(),
            _buildSteps(),
            _buildDownloadCard(context),
            _buildFeatureGrid(),
            _buildFooter(),
          ],
        ),
      ),
    );
  }

  // ─── MORGAN Guidance Banner ───────────────────────────────────────────────
  Widget _buildMorganGuidanceBanner() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _gold.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _gold.withValues(alpha: 0.4)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: const BoxDecoration(
              color: _gold,
              shape: BoxShape.circle,
            ),
            child: const Icon(Icons.smart_toy_rounded, color: Colors.black, size: 24),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'MORGAN — AI Assistant Guidance',
                  style: TextStyle(
                    color: _gold,
                    fontSize: 14,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                RichText(
                  text: const TextSpan(
                    style: TextStyle(color: _white, fontSize: 13, height: 1.5),
                    children: [
                      TextSpan(
                        text: 'Using a digital USB microscope? ',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      TextSpan(
                        text:
                            'Download the Desktop Agent below to capture high-res images directly into Numista.AI.\n',
                      ),
                      TextSpan(
                        text: 'Using phone/webcam or file upload? ',
                        style: TextStyle(fontWeight: FontWeight.bold, color: _warningAmber),
                      ),
                      TextSpan(
                        text: 'You do ',
                      ),
                      TextSpan(
                        text: 'not',
                        style: TextStyle(fontWeight: FontWeight.bold, decoration: TextDecoration.underline),
                      ),
                      TextSpan(
                        text: ' need to download anything.',
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Privacy Card ─────────────────────────────────────────────────────────
  Widget _buildPrivacyCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF162032),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _electricBlue.withValues(alpha: 0.3)),
      ),
      child: const Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.shield_rounded, color: _successGreen, size: 24),
          SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Privacy & Security Disclosure',
                  style: TextStyle(
                    color: _white,
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'We are dedicated to keeping this website as anonymous and extra secure as possible. '
                  'We do not process any credit card transactions (a 3rd party, Stripe does), '
                  'so we will never ask you for your credit card. If someone says they are us and asks for your credit card, '
                  'DO NOT GIVE IT TO THEM! If someone says they are us and wants to know your address, DO NOT GIVE IT TO THEM!',
                  style: TextStyle(color: _muted, fontSize: 12, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Hero ──────────────────────────────────────────────────────────────────
  Widget _buildHero() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 24),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0B1220), Color(0xFF1A2540)],
        ),
      ),
      child: Column(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _gold.withValues(alpha: 0.15),
              border: Border.all(color: _gold.withValues(alpha: 0.5), width: 2),
            ),
            child: const Icon(Icons.lens_rounded, color: _gold, size: 36),
          ),
          const SizedBox(height: 12),
          const Text(
            'Numista.AI Desktop Agent',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: _white,
              fontSize: 28,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            'The local hardware bridge between your USB microscope and numista.ai.\n'
            'Install once in 30 seconds — runs silently in your system tray.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: _muted,
              fontSize: 14,
              height: 1.4,
            ),
          ),
        ],
      ),
    );
  }

  // ─── Live Status Banner ─────────────────────────────────────────────────────
  Widget _buildStatusBanner() {
    Color bannerColor;
    IconData bannerIcon;
    String statusTitle;
    String statusSubtitle;

    if (_isChecking) {
      bannerColor = _warningAmber;
      bannerIcon = Icons.sync_rounded;
      statusTitle = 'Checking Agent Connection...';
      statusSubtitle = 'Polling local hardware server at https://localhost:5000';
    } else if (_isFullyConnected) {
      bannerColor = _successGreen;
      bannerIcon = Icons.check_circle_rounded;
      statusTitle = '🟢 Agent Online & Connected';
      statusSubtitle =
          'USB Microscope detected ($_cameraCount camera) • Linked to ${_agentPairedEmail ?? "account"}';
    } else if (_localHostOk) {
      bannerColor = _warningAmber;
      bannerIcon = Icons.warning_amber_rounded;
      statusTitle = '🟡 Agent Running — Partial Diagnostics Warning';
      statusSubtitle = _cameraDetected
          ? 'Unpaired account — open Microscope Scanner page to auto-link'
          : 'Local server active, but no USB camera detected yet';
    } else {
      bannerColor = _errorRed;
      bannerIcon = Icons.phonelink_off_rounded;
      statusTitle = '🔴 Desktop Agent Disconnected';
      statusSubtitle =
          'NumistaAgent executable is not running on this PC. Download setup below.';
    }

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32, vertical: 12),
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
      decoration: BoxDecoration(
        color: bannerColor.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: bannerColor.withValues(alpha: 0.4)),
      ),
      child: Row(
        children: [
          Icon(bannerIcon, color: bannerColor, size: 30),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  statusTitle,
                  style: TextStyle(
                    color: _white,
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  statusSubtitle,
                  style: TextStyle(color: _muted, fontSize: 13),
                ),
              ],
            ),
          ),
          ElevatedButton.icon(
            onPressed: () {
              setState(() => _isChecking = true);
              _runDiagnostics();
            },
            icon: const Icon(Icons.refresh_rounded, size: 18),
            label: const Text('Retry'),
            style: ElevatedButton.styleFrom(
              backgroundColor: _card,
              foregroundColor: _white,
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            ),
          ),
        ],
      ),
    );
  }

  // ─── 4-Step Diagnostics Card ───────────────────────────────────────────────
  Widget _buildDiagnosticsCard() {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32, vertical: 8),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.health_and_safety_rounded, color: _electricBlue, size: 22),
              SizedBox(width: 10),
              Text(
                'Live System Diagnostics',
                style: TextStyle(
                  color: _white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _buildDiagItem(
            step: '1',
            title: 'Local Host Server (https://localhost:5000)',
            isOk: _localHostOk,
            detail: _localHostOk
                ? 'Flask HTTPS hardware daemon responding'
                : 'Server offline or not started',
          ),
          const Divider(color: Colors.white10, height: 20),
          _buildDiagItem(
            step: '2',
            title: 'SSL Certificate Trust',
            isOk: _sslTrustOk,
            detail: _sslTrustOk
                ? 'localhost.crt trusted in Windows Root CA store'
                : 'SSL handshake error — run install_cert.py or setup installer',
          ),
          const Divider(color: Colors.white10, height: 20),
          _buildDiagItem(
            step: '3',
            title: 'USB Microscope Camera Detection',
            isOk: _cameraDetected,
            detail: _cameraDetected
                ? 'Found $_cameraCount camera device(s)'
                : 'No USB camera detected. Plug in your microscope.',
          ),
          const Divider(color: Colors.white10, height: 20),
          _buildDiagItem(
            step: '4',
            title: 'Firestore Account Pairing',
            isOk: _accountPaired,
            detail: _accountPaired
                ? 'Paired to ${_agentPairedEmail ?? "user account"}'
                : 'Unpaired — open Microscope Scanner screen to link automatically',
          ),
        ],
      ),
    );
  }

  Widget _buildDiagItem({
    required String step,
    required String title,
    required bool isOk,
    required String detail,
  }) {
    final statusColor = isOk ? _successGreen : _errorRed;
    final statusIcon = isOk ? Icons.check_circle_rounded : Icons.cancel_rounded;

    return Row(
      children: [
        Container(
          width: 28,
          height: 28,
          decoration: BoxDecoration(
            shape: BoxShape.circle,
            color: statusColor.withValues(alpha: 0.15),
            border: Border.all(color: statusColor.withValues(alpha: 0.5)),
          ),
          child: Center(
            child: Text(
              step,
              style: TextStyle(
                color: statusColor,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ),
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                title,
                style: const TextStyle(
                  color: _white,
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                detail,
                style: TextStyle(color: _muted, fontSize: 12),
              ),
            ],
          ),
        ),
        Icon(statusIcon, color: statusColor, size: 20),
      ],
    );
  }

  // ─── Steps ─────────────────────────────────────────────────────────────────
  Widget _buildSteps() {
    final steps = [
      const _Step(
        icon: Icons.download_rounded,
        color: _electricBlue,
        number: '1',
        title: 'Download',
        body: 'Click the Windows button below to download NumistaAgentSetup.exe',
      ),
      const _Step(
        icon: Icons.double_arrow_rounded,
        color: _gold,
        number: '2',
        title: 'Install',
        body: 'Double-click the installer. It registers the SSL cert automatically.',
      ),
      const _Step(
        icon: Icons.open_in_browser_rounded,
        color: Color(0xFF7C3AED),
        number: '3',
        title: 'Open Scanner',
        body: 'Go to Microscope Scanner. Your account links automatically.',
      ),
      const _Step(
        icon: Icons.check_circle_outline_rounded,
        color: _successGreen,
        number: '4',
        title: 'You\'re Live!',
        body: 'The green coin icon appears in your tray and scanning begins.',
      ),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 32),
      color: _bg,
      child: Column(
        children: [
          const Text(
            'Three steps. Thirty seconds.',
            style: TextStyle(
              color: _white,
              fontSize: 24,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 28),
          LayoutBuilder(builder: (context, constraints) {
            if (constraints.maxWidth > 700) {
              return Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: steps
                    .map((s) => Expanded(child: _buildStep(s)))
                    .toList(),
              );
            }
            return Column(children: steps.map(_buildStep).toList());
          }),
        ],
      ),
    );
  }

  Widget _buildStep(_Step s) {
    return Padding(
      padding: const EdgeInsets.all(10),
      child: Column(
        children: [
          Stack(
            alignment: Alignment.topRight,
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: s.color.withValues(alpha: 0.12),
                  border: Border.all(color: s.color.withValues(alpha: 0.4)),
                ),
                child: Icon(s.icon, color: s.color, size: 28),
              ),
              Container(
                width: 20,
                height: 20,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: s.color,
                ),
                child: Center(
                  child: Text(
                    s.number,
                    style: const TextStyle(
                      color: _white,
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Text(
            s.title,
            style: const TextStyle(
              color: _white,
              fontSize: 14,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            s.body,
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, fontSize: 12, height: 1.4),
          ),
        ],
      ),
    );
  }

  // ─── Download Card ──────────────────────────────────────────────────────────
  Widget _buildDownloadCard(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 32, vertical: 8),
      padding: const EdgeInsets.all(32),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _electricBlue.withValues(alpha: 0.3)),
        boxShadow: [
          BoxShadow(
            color: _electricBlue.withValues(alpha: 0.12),
            blurRadius: 40,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Column(
        children: [
          // Windows Installer Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _launchUrl(_kWindowsInstallerUrl),
              icon: const Icon(Icons.download_rounded, size: 24),
              label: const Text(
                '⊞  Download Setup Installer (NumistaAgentSetup.exe)',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: _white,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _electricBlue,
                padding: const EdgeInsets.symmetric(vertical: 18),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                elevation: 6,
              ),
            ),
          ),
          const SizedBox(height: 16),
          // ─── Windows SmartScreen Helper Card ──────────────────────────────
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.black26,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: _warningAmber.withValues(alpha: 0.3)),
            ),
            child: const Row(
              children: [
                Icon(Icons.shield_outlined, color: _warningAmber, size: 20),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'If Windows shows "Windows protected your PC":\n'
                    'Step 1: Click "More info"   ➔   Step 2: Click "Run anyway"',
                    style: TextStyle(
                      color: _white,
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      height: 1.4,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'NumistaAgentSetup.exe  •  Windows 10/11 (64-bit)',
            style: TextStyle(color: _muted, fontSize: 12),
          ),
          const SizedBox(height: 24),
          const Divider(color: Colors.white12),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.info_outline, color: _muted, size: 16),
              const SizedBox(width: 8),
              Text(
                'Already installed? ',
                style: TextStyle(color: _muted, fontSize: 13),
              ),
              if (widget.showBack)
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: TextButton.styleFrom(
                    foregroundColor: _electricBlue,
                    padding: EdgeInsets.zero,
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: const Text(
                    'Go back to scanner →',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                )
              else
                Text(
                  'Open the Microscope Scanner screen.',
                  style: TextStyle(color: _muted, fontSize: 13),
                ),
            ],
          ),
        ],
      ),
    );
  }

  // ─── Feature Grid ──────────────────────────────────────────────────────────
  Widget _buildFeatureGrid() {
    final features = [
      const _Feat(
        icon: Icons.security_rounded,
        color: _successGreen,
        title: 'SSL Auto-Trusted',
        body: 'Local certificate registered with Windows — no Chrome security flags',
      ),
      const _Feat(
        icon: Icons.power_settings_new_rounded,
        color: _gold,
        title: 'Auto-Start Support',
        body: 'Starts silently with Windows login via system registry',
      ),
      const _Feat(
        icon: Icons.manage_search_rounded,
        color: _electricBlue,
        title: 'Gemini AI Grading',
        body: 'Scans offloaded to Cloud Run backend enriched with PCGS data',
      ),
      const _Feat(
        icon: Icons.cloud_upload_outlined,
        color: Color(0xFF7C3AED),
        title: 'Cloud Sync',
        body: 'Captured coins sync instantly to your Firestore collection',
      ),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 40, horizontal: 32),
      color: const Color(0xFF0F1928),
      child: Column(
        children: [
          const Text(
            'What the Desktop Agent does',
            style: TextStyle(
              color: _white,
              fontSize: 22,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 24),
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            childAspectRatio: 2.5,
            children: features.map(_buildFeat).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildFeat(_Feat f) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _card,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: f.color.withValues(alpha: 0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(f.icon, color: f.color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  f.title,
                  style: const TextStyle(
                    color: _white,
                    fontWeight: FontWeight.w700,
                    fontSize: 13,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  f.body,
                  style: TextStyle(color: _muted, fontSize: 11, height: 1.4),
                  overflow: TextOverflow.fade,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  // ─── Footer ────────────────────────────────────────────────────────────────
  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 32, horizontal: 32),
      color: _bg,
      child: Column(
        children: [
          Text(
            '⚠ Security note: The Desktop Agent is signed by Numista.AI. '
            'Windows SmartScreen may show a prompt on first launch. Click "More info" → "Run anyway" to proceed.',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, fontSize: 12, height: 1.6),
          ),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => _launchUrl('https://numista.ai'),
            child: const Text(
              'numista.ai',
              style: TextStyle(
                color: _electricBlue,
                fontSize: 13,
                decoration: TextDecoration.underline,
              ),
            ),
          ),
        ],
      ),
    );
  }

  static Future<void> _launchUrl(String url) async {
    final uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    }
  }
}

// ─── Helper models ───────────────────────────────────────────────────────────
class _Step {
  final IconData icon;
  final Color color;
  final String number;
  final String title;
  final String body;
  const _Step({
    required this.icon,
    required this.color,
    required this.number,
    required this.title,
    required this.body,
  });
}

class _Feat {
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  const _Feat({
    required this.icon,
    required this.color,
    required this.title,
    required this.body,
  });
}
