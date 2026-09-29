import 'package:flutter/material.dart';
import 'base_layout.dart';
import 'login_screen.dart';
import '../services/guest_seed_service.dart';

/// Clean public shell providing branded informational views (/about, /features, /pricing, /faq).
class PublicInfoShell extends StatelessWidget {
  final String targetRoute;

  const PublicInfoShell({super.key, required this.targetRoute});

  static const Color _bg = Color(0xFFF8FAFC);
  static const Color _surface = Colors.white;
  static const Color _text = Color(0xFF0F172A);
  static const Color _border = Color(0xFFE2E8F0);
  static const Color _bronze = Color(0xFF8C7355);
  static const Color _blue = Color(0xFF1E3A8A);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: PreferredSize(
        preferredSize: const Size.fromHeight(68),
        child: Container(
          decoration: BoxDecoration(
            color: _surface,
            border: Border(bottom: BorderSide(color: _border)),
          ),
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: SafeArea(
            bottom: false,
            child: Row(
              children: [
                IconButton(
                  icon: const Icon(Icons.arrow_back_rounded, color: _text),
                  tooltip: 'Back to Vault',
                  onPressed: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                ),
                const SizedBox(width: 8),
                InkWell(
                  onTap: () {
                    Navigator.of(context).pushReplacement(
                      MaterialPageRoute(builder: (_) => const LoginScreen()),
                    );
                  },
                  borderRadius: BorderRadius.circular(8),
                  child: Row(
                    children: [
                      Image.asset(
                        'assets/logo_owl.png',
                        height: 36,
                        errorBuilder: (ctx, err, st) => const Icon(
                          Icons.account_balance_rounded,
                          color: _bronze,
                          size: 32,
                        ),
                      ),
                      const SizedBox(width: 10),
                      const Text(
                        'NUMISTA.AI',
                        style: TextStyle(
                          color: _text,
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          letterSpacing: 1.2,
                        ),
                      ),
                    ],
                  ),
                ),
                const Spacer(),
                Wrap(
                  spacing: 8,
                  runSpacing: 4,
                  alignment: WrapAlignment.end,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    TextButton.icon(
                      onPressed: () async {
                        await GuestSeedService.activateBrowseDemo();
                        if (context.mounted) {
                          Navigator.of(context).pushReplacement(
                            MaterialPageRoute(
                              builder: (_) => const BaseLayout(isDemoMode: true),
                            ),
                          );
                        }
                      },
                      icon: const Icon(Icons.explore_outlined, size: 16, color: _bronze),
                      label: const Text(
                        'Explore Demo Vault',
                        style: TextStyle(
                          color: _bronze,
                          fontWeight: FontWeight.bold,
                          fontSize: 13,
                        ),
                      ),
                    ),
                    ElevatedButton(
                      style: ElevatedButton.styleFrom(
                        backgroundColor: _blue,
                        foregroundColor: Colors.white,
                        elevation: 0,
                        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(8),
                        ),
                      ),
                      onPressed: () {
                        Navigator.of(context).pushReplacement(
                          MaterialPageRoute(
                            builder: (_) => const LoginScreen(initialTab: 1),
                          ),
                        );
                      },
                      child: const Text('Join Beta', style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 860),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
              child: _buildRouteContent(context),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRouteContent(BuildContext context) {
    switch (targetRoute) {
      case '/features':
        return const _FeaturesView();
      case '/pricing':
        return const _PricingView();
      case '/faq':
        return const _FaqView();
      case '/about':
      default:
        return const _AboutView();
    }
  }
}

// ─── 1. About View ────────────────────────────────────────────────────────────
class _AboutView extends StatelessWidget {
  const _AboutView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('ABOUT NUMISTA.AI'),
        const SizedBox(height: 12),
        const Text(
          'Built for Collectors, Powered by Rigorous Inventory Systems',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 12),
        const Text(
          'Numista.AI brings structured property management and artificial intelligence to coin collection cataloging.',
          style: TextStyle(
            color: Color(0xFF475569),
            fontSize: 17,
            height: 1.5,
          ),
        ),
        const SizedBox(height: 32),
        _contentCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: const [
              Text(
                'Numista.AI was founded by a retired U.S. Army Supply NCO with over 20 years of military property accountability and large-scale inventory management experience.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
              SizedBox(height: 16),
              Text(
                'As a newer coin collector (entering the hobby within the past year), our founder recognized that traditional collection tracking often relies on fragmented spreadsheets, handwritten notebooks, or disconnected reference binders. Numista.AI applies proven inventory management discipline to numismatics—combining AI photo identification, automated Greysheet-based market value estimates, and organized vault documentation so collectors know exactly what they have, what it\'s worth, and where it is stored.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }
}

// ─── 2. Features View ─────────────────────────────────────────────────────────
class _FeaturesView extends StatelessWidget {
  const _FeaturesView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('PRODUCT CAPABILITIES'),
        const SizedBox(height: 12),
        const Text(
          'Tools for Cataloging and Preserving Your Collection',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 28),
        _featureItem(
          icon: Icons.camera_alt_outlined,
          title: 'AI Photo Identification',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'Upload or snap photos of your coins for automated denomination, series, year, and mint mark recognition.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.trending_up_rounded,
          title: 'Greysheet-Based Value Estimates',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'View reference pricing and market value estimates linked directly to your cataloged inventory.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.show_chart_rounded,
          title: 'Total Collection Value Tracking',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: "Track your collection's total value over time as you add coins and market prices update.",
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.open_in_new_rounded,
          title: 'eBay Sold Listings Integration',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'One-tap link to recent eBay sold listings for any coin in your collection.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.chat_bubble_outline_rounded,
          title: 'Morgan Numismatic Assistant',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'An AI assistant to help research coin history, metal compositions, mintage statistics, and collection details.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.verified_user_outlined,
          title: 'AI Trainer Review Board',
          status: 'AVAILABLE NOW',
          statusColor: const Color(0xFF059669),
          desc: 'Community and expert numismatic review board continuously trains and verifies AI identification models.',
        ),
        const SizedBox(height: 16),
        _featureItem(
          icon: Icons.picture_as_pdf_outlined,
          title: 'Estate Documentation & Reports',
          status: 'COMING SOON',
          statusColor: const Color(0xFFD97706),
          desc: 'Estate PDF reports are coming soon in beta for personal records, insurance documentation, and family review.',
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }

  Widget _featureItem({
    required IconData icon,
    required String title,
    required String status,
    required Color statusColor,
    required String desc,
  }) {
    return _contentCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: const Color(0xFF8C7355), size: 24),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        title,
                        style: const TextStyle(
                          color: Color(0xFF0F172A),
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: statusColor.withAlpha(25),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(color: statusColor.withAlpha(75)),
                      ),
                      child: Text(
                        status,
                        style: TextStyle(
                          color: statusColor,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.5,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 6),
                Text(
                  desc,
                  style: const TextStyle(color: Color(0xFF475569), fontSize: 14, height: 1.5),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// ─── 3. Pricing View ──────────────────────────────────────────────────────────
class _PricingView extends StatelessWidget {
  const _PricingView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('BETA PRICING'),
        const SizedBox(height: 12),
        const Text(
          'Free During Beta — Pricing TBA',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 28),
        _contentCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF059669).withAlpha(25),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: const Color(0xFF059669).withAlpha(90)),
                    ),
                    child: const Text(
                      'OPEN PUBLIC BETA',
                      style: TextStyle(
                        color: Color(0xFF059669),
                        fontWeight: FontWeight.bold,
                        fontSize: 11,
                        letterSpacing: 1.0,
                      ),
                    ),
                  ),
                  const Spacer(),
                  const Text(
                    '\$0 / month',
                    style: TextStyle(
                      color: Color(0xFF0F172A),
                      fontSize: 22,
                      fontWeight: FontWeight.w900,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 20),
              const Text(
                'Numista.AI is currently in open public beta. During this phase, collection tracking, AI photo identification, and market value estimates are completely free for registered participants.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
              const SizedBox(height: 16),
              const Text(
                'Long-term pricing and plans will be announced prior to general release. Existing beta accounts will be grandfathered—you will not be asked to pay for your active beta access.',
                style: TextStyle(color: Color(0xFF0F172A), fontSize: 15, height: 1.6),
              ),
            ],
          ),
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }
}

// ─── 4. FAQ View ──────────────────────────────────────────────────────────────
class _FaqView extends StatelessWidget {
  const _FaqView();

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _tagBadge('QUESTIONS & ANSWERS'),
        const SizedBox(height: 12),
        const Text(
          'Frequently Asked Questions',
          style: TextStyle(
            color: Color(0xFF0F172A),
            fontSize: 32,
            fontWeight: FontWeight.bold,
            height: 1.25,
          ),
        ),
        const SizedBox(height: 28),
        _faqTile(
          question: '1. How is my collection data kept private?',
          answer: 'Your vault is private to your account. We do not make your collection records public. For full details on our data protection practices, see our Privacy Policy.',
        ),
        _faqTile(
          question: '2. How accurate is AI photo identification?',
          answer: 'Numista provides AI photo identification based on high-resolution reference coin models and historical data. It is designed as a cataloging and research assistant, and is not a professional third-party grading service (such as PCGS or NGC).',
        ),
        _faqTile(
          question: '3. Can I export / print an estate report?',
          answer: 'Estate PDF reports are coming soon in beta. Numista is developing structured export tools so you can generate professional collection summaries for personal records, insurance documentation, and family estate planning.',
        ),
        _faqTile(
          question: '4. What works in public beta, and how do I send feedback?',
          answer: 'Most core features—including collection cataloging, photo lookup, and Greysheet value estimates—work today, while select advanced features are still being polished. You can submit feedback through the Ask Morgan chat or participate in our sidebar AI Trainer Board, where community members review and rate AI coin classifications.',
        ),
        _faqTile(
          question: '5. Does Guest / Demo save my coins?',
          answer: 'No. The Demo Vault runs entirely in-memory with sample coins for exploration. Any changes made during a demo session are not saved. To build and preserve your personal collection vault, create a free beta account.',
        ),
        const SizedBox(height: 32),
        _actionRow(context),
      ],
    );
  }

  Widget _faqTile({required String question, required String answer}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 14),
      child: _contentCard(
        child: Theme(
          data: ThemeData(dividerColor: Colors.transparent),
          child: ExpansionTile(
            tilePadding: EdgeInsets.zero,
            childrenPadding: const EdgeInsets.only(top: 8),
            title: Text(
              question,
              style: const TextStyle(
                color: Color(0xFF0F172A),
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            children: [
              Text(
                answer,
                style: const TextStyle(color: Color(0xFF475569), fontSize: 14, height: 1.6),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

// ─── Helpers ──────────────────────────────────────────────────────────────────
Widget _tagBadge(String label) {
  return Container(
    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
    decoration: BoxDecoration(
      color: const Color(0xFF8C7355).withAlpha(20),
      borderRadius: BorderRadius.circular(6),
    ),
    child: Text(
      label,
      style: const TextStyle(
        color: Color(0xFF8C7355),
        fontSize: 11,
        fontWeight: FontWeight.w700,
        letterSpacing: 1.1,
      ),
    ),
  );
}

Widget _contentCard({required Widget child}) {
  return Container(
    width: double.infinity,
    padding: const EdgeInsets.all(24),
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(12),
      border: Border.all(color: const Color(0xFFE2E8F0)),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withAlpha(8),
          blurRadius: 10,
          offset: const Offset(0, 2),
        ),
      ],
    ),
    child: child,
  );
}

Widget _actionRow(BuildContext context) {
  return Wrap(
    spacing: 12,
    runSpacing: 12,
    children: [
      ElevatedButton.icon(
        style: ElevatedButton.styleFrom(
          backgroundColor: const Color(0xFF1E3A8A),
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () {
          Navigator.of(context).pushReplacement(
            MaterialPageRoute(builder: (_) => const LoginScreen(initialTab: 1)),
          );
        },
        icon: const Icon(Icons.rocket_launch_outlined, size: 18),
        label: const Text('Create Free Beta Account', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      OutlinedButton.icon(
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF8C7355),
          side: const BorderSide(color: Color(0xFF8C7355)),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
        ),
        onPressed: () async {
          await GuestSeedService.activateBrowseDemo();
          if (context.mounted) {
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const BaseLayout(isDemoMode: true)),
            );
          }
        },
        icon: const Icon(Icons.explore_outlined, size: 18),
        label: const Text('Explore Demo Vault', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
    ],
  );
}
