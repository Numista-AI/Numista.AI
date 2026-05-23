import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Shown once after a new user creates their account.
/// Sets a SharedPreferences flag so it never shows again.
class WelcomeScreen extends StatelessWidget {
  final VoidCallback onDone;
  const WelcomeScreen({super.key, required this.onDone});

  static const String _prefKey = 'welcome_seen';

  /// Call this from main.dart / BaseLayout to check if the welcome screen
  /// should be shown. Returns true only on first launch after account creation.
  static Future<bool> shouldShow() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool(_prefKey) ?? false);
  }

  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, true);
  }

  static const _bg      = Color(0xFF0F172A);   // deep navy
  static const _accent  = Color(0xFF3B82F6);   // blue
  static const _gold    = Color(0xFFF59E0B);   // amber/gold
  static const _surface = Color(0xFF1E293B);   // card surface
  static const _text    = Colors.white;
  static const _sub     = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 520),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // ── Logo / Icon ─────────────────────────────────────────
                  Container(
                    width: 96,
                    height: 96,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      gradient: const LinearGradient(
                        colors: [Color(0xFF1D4ED8), Color(0xFF3B82F6)],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      boxShadow: [
                        BoxShadow(color: _accent.withAlpha(80), blurRadius: 24, spreadRadius: 2),
                      ],
                    ),
                    child: const Icon(Icons.account_balance_wallet_rounded,
                        color: Colors.white, size: 48),
                  ),
                  const SizedBox(height: 28),

                  // ── Headline ────────────────────────────────────────────
                  const Text(
                    'Welcome to Numista.AI',
                    style: TextStyle(
                      color: _text,
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                      letterSpacing: -0.5,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 10),
                  const Text(
                    'Your AI-powered coin collection manager.\nLet\'s get your vault set up.',
                    style: TextStyle(color: _sub, fontSize: 15, height: 1.5),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 36),

                  // ── Feature cards ───────────────────────────────────────
                  _FeatureCard(
                    icon: Icons.add_circle_outline_rounded,
                    color: _accent,
                    title: 'Add Your First Coin',
                    body: 'Tap "Add Coins" to enter a coin manually, scan a PCGS cert, or upload a spreadsheet.',
                  ),
                  const SizedBox(height: 12),
                  _FeatureCard(
                    icon: Icons.image_search_rounded,
                    color: _gold,
                    title: 'Reference Images',
                    body: 'The inspector shows a reference image for every coin from our Mint image library.',
                  ),
                  const SizedBox(height: 12),
                  _FeatureCard(
                    icon: Icons.shopping_cart_outlined,
                    color: const Color(0xFF10B981),
                    title: 'Live eBay Pricing',
                    body: 'Tap "Check >" on any coin to get live sold-listing prices and our affiliate links.',
                  ),
                  const SizedBox(height: 36),

                  // ── CTA ─────────────────────────────────────────────────
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton(
                      style: FilledButton.styleFrom(
                        backgroundColor: _accent,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                      onPressed: () async {
                        await markSeen();
                        onDone();
                      },
                      child: const Text(
                        "Let's Go!",
                        style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextButton(
                    onPressed: () async {
                      await markSeen();
                      onDone();
                    },
                    child: const Text('Skip for now',
                        style: TextStyle(color: _sub, fontSize: 13)),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _FeatureCard extends StatelessWidget {
  final IconData icon;
  final Color color;
  final String title;
  final String body;
  const _FeatureCard({required this.icon, required this.color,
    required this.title, required this.body});

  static const _surface = Color(0xFF1E293B);
  static const _text    = Colors.white;
  static const _sub     = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withAlpha(60)),
      ),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: color.withAlpha(30),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 22),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title,
                    style: const TextStyle(color: _text, fontSize: 14,
                        fontWeight: FontWeight.w600)),
                const SizedBox(height: 3),
                Text(body,
                    style: const TextStyle(color: _sub, fontSize: 12, height: 1.4)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
