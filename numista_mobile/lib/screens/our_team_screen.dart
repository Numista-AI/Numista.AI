import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class OurTeamScreen extends StatelessWidget {
  const OurTeamScreen({super.key});

  Future<void> _launchURL(String url) async {
    final Uri uri = Uri.parse(url);
    try {
      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        throw Exception('Could not launch \$url');
      }
    } catch (e) {
      debugPrint('Error launching URL: \$e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(32.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          const Text(
            'Our Team',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.w900,
              fontStyle: FontStyle.italic,
              color: Color(0xFF31333F),
            ),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: const Color(0xFF0F9D58),
              borderRadius: BorderRadius.circular(6),
            ),
            child: const Text(
              'MEET THE FOUNDER',
              style: TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.w700,
                letterSpacing: 0.5,
              ),
            ),
          ),
          const SizedBox(height: 32),

          // Main Content Card
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFFE2E6E9)),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Profile Image / Placeholder
                Column(
                  children: [
                    Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8F9FB),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: const Color(0xFFE2E6E9)),
                        image: const DecorationImage(
                          image: NetworkImage('https://placehold.co/400x400?text=ES'),
                          fit: BoxFit.cover,
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text(
                      'Eric Seaman',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF0F172A),
                      ),
                    ),
                    const Text(
                      'Founder & Lead Developer',
                      style: TextStyle(
                        fontSize: 14,
                        color: Color(0xFF64748B),
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () => _launchURL('https://www.linkedin.com/in/ericdseaman'),
                      icon: const Icon(Icons.link, size: 16),
                      label: const Text('LinkedIn Profile'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0077B5),
                        foregroundColor: Colors.white,
                        elevation: 0,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(width: 48),

                // Biography Text
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Mission & Founding Story',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 24),
                      _buildBioParagraph(
                        'In May 2025 I retired after 26 years of service in the US Army. For 20 of those years property accountability was my primary focus; I was responsible for the tracking, managing and stewardship of millions of dollars in mission-critical assets.',
                      ),
                      _buildBioParagraph(
                        'After retiring, I took part in Google\'s Veteran\'s Launchpad and received training, and later certification, as a Generative AI (Artificial Intelligence) Leader. Subsequently, I was visiting a beloved family member at the time and took the Google AI training in their library, surrounded by their coin collection, 50+ years in the making.',
                      ),
                      _buildBioParagraph(
                        'When that beloved family member asked me to help them organize their coin collection, my supply sergeant instincts (and newfound enthusiasm for AI) took over and I realized that the same discipline I used to manage military inventory could be powered by AI to help collectors intelligently catalog, research, and manage their treasures.',
                      ),
                      _buildBioParagraph(
                        'While coins are the focus of Numista.AI, the concept will be expanded to include the limitless amount of assets and collectibles out there; baseball cards, paintings, family heirlooms, just about anything that people love to collect and are passionate about.',
                      ),
                      const SizedBox(height: 24),
                      const Divider(color: Color(0xFFE2E6E9)),
                      const SizedBox(height: 24),
                      const Text(
                        'Property Accountability x Generative AI',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF0F172A),
                        ),
                      ),
                      const SizedBox(height: 8),
                      const Text(
                        'Numista.AI bridges 26 years of logistics expertise with cutting-edge Large Language Models to provide professional-grade asset management for private collectors.',
                        style: TextStyle(
                          color: Color(0xFF64748B),
                          height: 1.6,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 32),

          // ── Morgan ─────────────────────────────────────────────────────────
          Container(
            padding: const EdgeInsets.all(32),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF0B1220), Color(0xFF112240)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                  color: const Color(0xFFD4A843).withAlpha(60), width: 1.5),
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF2DD4BF).withAlpha(20),
                  blurRadius: 16,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Morgan avatar
                Column(
                  children: [
                    Container(
                      width: 200,
                      height: 200,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        gradient: const LinearGradient(
                          colors: [Color(0xFFD4A843), Color(0xFF5A3E0A)],
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                        ),
                        border: Border.all(
                            color: const Color(0xFFD4A843).withAlpha(150),
                            width: 3),
                      ),
                      child: ClipOval(
                        child: Image.asset(
                          'assets/morgan_avatar.png',
                          fit: BoxFit.cover,
                          errorBuilder: (ctx, err, stack) => const Icon(
                              Icons.smart_toy_rounded,
                              size: 80, color: Colors.white),
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    const Text('Morgan',
                        style: TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Colors.white)),
                    const Text('AI Numismatic Guide',
                        style: TextStyle(
                            fontSize: 14,
                            color: Color(0xFF2DD4BF),
                            fontWeight: FontWeight.w500)),
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 4),
                      decoration: BoxDecoration(
                        color: const Color(0xFF2DD4BF).withAlpha(25),
                        borderRadius: BorderRadius.circular(6),
                        border: Border.all(
                            color: const Color(0xFF2DD4BF).withAlpha(80)),
                      ),
                      child: const Text('Powered by Gemini',
                          style: TextStyle(
                              color: Color(0xFF2DD4BF),
                              fontSize: 10,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 0.5)),
                    ),
                  ],
                ),
                const SizedBox(width: 48),

                // Biography
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Meet Morgan',
                          style: TextStyle(
                              fontSize: 24,
                              fontWeight: FontWeight.bold,
                              color: Colors.white)),
                      const SizedBox(height: 24),
                      _buildDarkParagraph(
                        'Morgan is the Athenian Owl of Numista.AI — named after the iconic silver coin that served as the trusted currency of the ancient world. Just as that coin was recognised everywhere for its reliability, Morgan is here whenever you need a knowledgeable, patient guide through your collection.',
                      ),
                      _buildDarkParagraph(
                        'Designed with our primary users in mind — experienced collectors who grew up before the smartphone era — Morgan speaks plain English, explains numismatic terms as she uses them, and never makes you feel like you asked a silly question.',
                      ),
                      _buildDarkParagraph(
                        'Morgan can walk you through adding your first coin, identify what you own, surface your most valuable pieces, help you understand what a coin is worth and why, and answer general numismatic questions — all grounded in your actual collection data.',
                      ),
                      const SizedBox(height: 24),
                      const Divider(color: Color(0x30FFFFFF)),
                      const SizedBox(height: 20),
                      const Text('What Morgan Can Do',
                          style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Colors.white)),
                      const SizedBox(height: 12),
                      ...[
                        ('chat_bubble_rounded', 'Answer questions about your collection in plain English'),
                        ('school_rounded', 'Walk you through every feature with step-by-step guides'),
                        ('star_rounded', 'Find your most valuable or rarest coins instantly'),
                        ('person_rounded', 'Learn your name and greet you personally'),
                        ('settings_rounded', 'Customise her behaviour via Morgan Settings'),
                      ].map((item) => Padding(
                        padding: const EdgeInsets.only(bottom: 10),
                        child: Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Container(
                              width: 28, height: 28,
                              decoration: BoxDecoration(
                                color: const Color(0xFF2DD4BF).withAlpha(25),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Icon(
                                _iconFromName(item.$1),
                                color: const Color(0xFF2DD4BF), size: 14),
                            ),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(item.$2,
                                  style: const TextStyle(
                                      color: Color(0xFFCBD5E1),
                                      fontSize: 14,
                                      height: 1.5)),
                            ),
                          ],
                        ),
                      )),
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

  IconData _iconFromName(String name) {
    switch (name) {
      case 'chat_bubble_rounded': return Icons.chat_bubble_rounded;
      case 'school_rounded':      return Icons.school_rounded;
      case 'star_rounded':        return Icons.star_rounded;
      case 'person_rounded':      return Icons.person_rounded;
      case 'settings_rounded':    return Icons.settings_rounded;
      default:                    return Icons.check_circle_rounded;
    }
  }

  Widget _buildDarkParagraph(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(text,
          style: const TextStyle(
              fontSize: 15,
              color: Color(0xFFCBD5E1),
              height: 1.65)),
    );
  }

  Widget _buildBioParagraph(String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        text,
        style: const TextStyle(
          fontSize: 16,
          color: Color(0xFF334155),
          height: 1.6,
        ),
      ),
    );
  }
}
