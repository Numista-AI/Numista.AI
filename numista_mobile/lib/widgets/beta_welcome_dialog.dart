import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'beta_checklist_widget.dart';

class BetaWelcomeDialog extends StatelessWidget {
  const BetaWelcomeDialog({super.key});

  static const String _prefKey = 'beta_tester_welcome_seen_v2';

  /// Check if the user should be automatically shown the Welcome Beta Tester modal.
  static Future<bool> shouldAutoShow() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool(_prefKey) ?? false);
  }

  /// Mark welcome dialog as seen.
  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, true);
  }

  /// Show the Welcome Beta Tester Modal.
  static Future<void> show(BuildContext context) async {
    await markSeen();
    if (!context.mounted) return;
    showDialog(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => const BetaWelcomeDialog(),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bg = isDark ? const Color(0xFF0F172A) : Colors.white;
    final card = isDark ? const Color(0xFF1E293B) : const Color(0xFFF8FAFC);
    final text = isDark ? Colors.white : const Color(0xFF0F172A);
    final sub = isDark ? const Color(0xFF94A3B8) : const Color(0xFF5A5C69);
    final text70 = isDark ? Colors.white70 : const Color(0xFF0F172A).withAlpha(180);

    return Dialog(
      backgroundColor: bg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        constraints: const BoxConstraints(maxWidth: 550),
        padding: const EdgeInsets.all(28),
        child: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header Badge & Close Button
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: const Color(0xFF2563EB).withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF3B82F6)),
                    ),
                    child: const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.stars, color: Color(0xFF60A5FA), size: 16),
                        SizedBox(width: 6),
                        Text(
                          'OFFICIAL BETA TESTER PROGRAM',
                          style: TextStyle(
                            color: Color(0xFF60A5FA),
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 0.5,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.grey),
                    onPressed: () => Navigator.pop(context),
                  ),
                ],
              ),
              const SizedBox(height: 16),

              // Title
              Text(
                'Welcome, Beta Tester! 👋🎉',
                style: TextStyle(
                  color: text,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                'Official Test Phase Active through October 1, 2026',
                style: TextStyle(
                  color: sub,
                  fontSize: 13,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 20),

              // Thank You Message
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: card,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.white10),
                ),
                child: Text(
                  'Thank you for joining our early access collector community! '
                  'Your hands-on experience and real-world feedback are vital to making Numista.AI '
                  'the most accurate, delightful, and easy-to-use coin collection app ever built.',
                  style: TextStyle(color: text70, fontSize: 14, height: 1.5),
                ),
              ),
              const SizedBox(height: 20),

              // What We're Looking For
              const Text(
                '🔍 What We Are Looking For:',
                style: TextStyle(color: Color(0xFF38BDF8), fontSize: 15, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 10),
              _bulletPoint(context, 'Ease of Use & Clarity — Is navigating the app intuitive and clear?'),
              _bulletPoint(context, 'AI Accuracy — Did camera scans & cert lookups identify your coins correctly?'),
              _bulletPoint(context, 'Variety & Edge Cases — Testing paper currency, world coins, and roll imports.'),
              _bulletPoint(context, 'Fun & Utility — Is managing your portfolio engaging and useful for your collection?'),
              const SizedBox(height: 24),

              // 18-Step Track Callout
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: isDark ? const [Color(0xFF1E3A8A), Color(0xFF0F172A)] : const [Color(0xFFDBEAFE), Color(0xFFEFF6FF)],
                  ),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: const Color(0xFF3B82F6).withValues(alpha: 0.5)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.checklist_rtl_rounded, color: Color(0xFF60A5FA), size: 32),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '18-Step Beta Testing Track',
                            style: TextStyle(color: text, fontSize: 15, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'We created a guided 18-task checklist to walk you through every major feature.',
                            style: TextStyle(color: sub, fontSize: 12),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 28),

              // Action Buttons
              Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  ElevatedButton.icon(
                    onPressed: () {
                      Navigator.pop(context);
                      BetaChecklistWidget.showChecklistModal(context);
                    },
                    icon: const Icon(Icons.playlist_add_check, size: 20),
                    label: const Text('📋 Open 18-Step Beta Checklist'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF2563EB),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 14),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                    ),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton(
                    onPressed: () => Navigator.pop(context),
                    style: OutlinedButton.styleFrom(
                      foregroundColor: Colors.white70,
                      side: const BorderSide(color: Colors.white24),
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    ),
                    child: const Text('Got It, Let\'s Explore! →'),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  static Widget _bulletPoint(BuildContext context, String text) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final textCol = isDark ? Colors.white.withValues(alpha: 0.87) : const Color(0xFF0F172A).withValues(alpha: 0.87);
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(color: Color(0xFF38BDF8), fontSize: 16, fontWeight: FontWeight.bold)),
          Expanded(
            child: Text(text, style: TextStyle(color: textCol, fontSize: 13, height: 1.4)),
          ),
        ],
      ),
    );
  }
}
