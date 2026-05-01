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
        ],
      ),
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
