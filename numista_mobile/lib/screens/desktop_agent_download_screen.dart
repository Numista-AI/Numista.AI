import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

// ─── Design tokens ────────────────────────────────────────────────────────────
const _bg          = Color(0xFF0B1220);
const _card        = Color(0xFF1A2540);
const _electricBlue = Color(0xFF4C8CDA);
const _gold        = Color(0xFFC9A84C);
const _successGreen = Color(0xFF00C853);
const _muted       = Color(0xFF94A3B8);
const _white       = Colors.white;

// ─── Public GCS download URL ─────────────────────────────────────────────────
// This is the NumistaAgentSetup.exe uploaded to the public GCS bucket.
const _kWindowsDownloadUrl =
    'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/'
    'downloads/NumistaAgentSetup.exe';

// ─── Screen ──────────────────────────────────────────────────────────────────
class DesktopAgentDownloadScreen extends StatelessWidget {
  /// If true, shows a "Back" button (used when pushed from MicroscopeScanScreen).
  final bool showBack;

  const DesktopAgentDownloadScreen({super.key, this.showBack = false});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: showBack
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
            _buildHero(),
            _buildSteps(),
            _buildDownloadCard(context),
            _buildFeatureGrid(),
            _buildFooter(),
          ],
        ),
      ),
    );
  }

  // ─── Hero ──────────────────────────────────────────────────────────────────
  Widget _buildHero() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 60, horizontal: 32),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFF0B1220), Color(0xFF1A2540)],
        ),
      ),
      child: Column(
        children: [
          // Coin icon
          Container(
            width: 96,
            height: 96,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: _gold.withValues(alpha: 0.15),
              border: Border.all(color: _gold.withValues(alpha: 0.5), width: 2),
            ),
            child: const Icon(Icons.lens_rounded, color: _gold, size: 52),
          ),
          const SizedBox(height: 24),
          const Text(
            'Numista.AI Desktop Agent',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: _white,
              fontSize: 36,
              fontWeight: FontWeight.w900,
              letterSpacing: -0.5,
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'The local bridge between your USB microscope and numista.ai.\n'
            'Install once in 30 seconds — it runs silently in the background forever.',
            textAlign: TextAlign.center,
            style: TextStyle(
              color: _muted,
              fontSize: 16,
              height: 1.6,
            ),
          ),
        ],
      ),
    );
  }

  // ─── Steps ─────────────────────────────────────────────────────────────────
  Widget _buildSteps() {
    final steps = [
      _Step(icon: Icons.download_rounded,   color: _electricBlue,
            number: '1', title: 'Download',
            body: 'Click the Windows button below to download NumistaAgentSetup.exe'),
      _Step(icon: Icons.double_arrow_rounded, color: _gold,
            number: '2', title: 'Install',
            body: 'Double-click the installer. No admin password required.'),
      _Step(icon: Icons.email_outlined,     color: Color(0xFF7C3AED),
            number: '3', title: 'Enter Email',
            body: 'A setup window appears asking for your Numista.AI account email.'),
      _Step(icon: Icons.check_circle_outline_rounded, color: _successGreen,
            number: '4', title: 'Done!',
            body: 'The gold coin appears in your system tray. Return here — you\'ll see 🟢 Online.'),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 32),
      color: _bg,
      child: Column(
        children: [
          const Text(
            'Four steps. Thirty seconds.',
            style: TextStyle(
              color: _white,
              fontSize: 24,
              fontWeight: FontWeight.w800,
            ),
          ),
          const SizedBox(height: 32),
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
      padding: const EdgeInsets.all(12),
      child: Column(
        children: [
          Stack(
            alignment: Alignment.topRight,
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: s.color.withValues(alpha: 0.12),
                  border: Border.all(color: s.color.withValues(alpha: 0.4)),
                ),
                child: Icon(s.icon, color: s.color, size: 30),
              ),
              Container(
                width: 22,
                height: 22,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: s.color,
                ),
                child: Center(
                  child: Text(s.number,
                      style: const TextStyle(
                          color: _white, fontSize: 11,
                          fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(s.title,
              style: const TextStyle(
                  color: _white, fontSize: 15, fontWeight: FontWeight.w700)),
          const SizedBox(height: 6),
          Text(s.body,
              textAlign: TextAlign.center,
              style: TextStyle(color: _muted, fontSize: 13, height: 1.5)),
        ],
      ),
    );
  }

  // ─── Download card ──────────────────────────────────────────────────────────
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
          // Windows button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _launchUrl(_kWindowsDownloadUrl),
              icon: const Icon(Icons.download_rounded, size: 24),
              label: const Text(
                '⊞  Download for Windows',
                style: TextStyle(
                    fontSize: 17, fontWeight: FontWeight.bold, color: _white),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: _electricBlue,
                padding: const EdgeInsets.symmetric(vertical: 20),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
                elevation: 6,
              ),
            ),
          ),
          const SizedBox(height: 12),
          Text(
            'NumistaAgentSetup.exe  •  ~150 MB  •  Windows 10/11',
            style: TextStyle(color: _muted, fontSize: 12),
          ),
          const SizedBox(height: 24),
          const Divider(color: Colors.white12),
          const SizedBox(height: 16),
          // Already installed? block
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.info_outline, color: _muted, size: 16),
              const SizedBox(width: 8),
              Text(
                'Already installed? ',
                style: TextStyle(color: _muted, fontSize: 13),
              ),
              if (showBack)
                TextButton(
                  onPressed: () => Navigator.of(context).pop(),
                  style: TextButton.styleFrom(
                    foregroundColor: _electricBlue,
                    padding: EdgeInsets.zero,
                    minimumSize: Size.zero,
                    tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  ),
                  child: const Text(
                    'Go back and retry →',
                    style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                  ),
                )
              else
                Text('Open the Microscope Scanner screen.',
                    style: TextStyle(color: _muted, fontSize: 13)),
            ],
          ),
          const SizedBox(height: 12),
          // Mac coming soon note
          Text(
            'macOS version coming soon',
            style: TextStyle(color: _muted.withValues(alpha: 0.5), fontSize: 12),
          ),
        ],
      ),
    );
  }

  // ─── Feature grid ──────────────────────────────────────────────────────────
  Widget _buildFeatureGrid() {
    final features = [
      _Feat(icon: Icons.security_rounded,   color: _successGreen,
            title: 'SSL Trusted',
            body: 'Certificate automatically added to Windows — no Chrome flags needed'),
      _Feat(icon: Icons.power_settings_new_rounded, color: _gold,
            title: 'Auto-Start',
            body: 'Starts silently with Windows login via the registry'),
      _Feat(icon: Icons.manage_search_rounded, color: _electricBlue,
            title: 'Gemini AI Grading',
            body: 'Every scan is analyzed by Gemini Vision and enriched with PCGS data'),
      _Feat(icon: Icons.cloud_upload_outlined, color: Color(0xFF7C3AED),
            title: 'Cloud Sync',
            body: 'Identified coins upload automatically to your Firestore collection'),
    ];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 48, horizontal: 32),
      color: const Color(0xFF0F1928),
      child: Column(
        children: [
          const Text('What the Desktop Agent does',
              style: TextStyle(
                  color: _white, fontSize: 22, fontWeight: FontWeight.w800)),
          const SizedBox(height: 28),
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
          Icon(f.icon, color: f.color, size: 26),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(f.title,
                    style: const TextStyle(
                        color: _white,
                        fontWeight: FontWeight.w700,
                        fontSize: 13)),
                const SizedBox(height: 4),
                Text(f.body,
                    style: TextStyle(color: _muted, fontSize: 11, height: 1.4),
                    overflow: TextOverflow.fade),
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
            '⚠  Security note: The Desktop Agent is signed by Numista.AI. '
            'Windows SmartScreen may show a warning on first run because the '
            'certificate is new. Click "More info" → "Run anyway" to proceed.',
            textAlign: TextAlign.center,
            style: TextStyle(color: _muted, fontSize: 12, height: 1.6),
          ),
          const SizedBox(height: 16),
          GestureDetector(
            onTap: () => _launchUrl('https://numista.ai'),
            child: Text(
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
  const _Step(
      {required this.icon,
      required this.color,
      required this.number,
      required this.title,
      required this.body});
}

class _Feat {
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  const _Feat(
      {required this.icon,
      required this.color,
      required this.title,
      required this.body});
}
