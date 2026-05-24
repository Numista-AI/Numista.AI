import 'package:flutter/material.dart';

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  static const _bg      = Color(0xFFF0F2F6);
  static const _surface = Colors.white;
  static const _blue    = Color(0xFF1565C0);
  static const _text    = Color(0xFF0F172A);
  static const _sub     = Color(0xFF64748B);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      appBar: AppBar(
        title: const Text(
          'Privacy Policy',
          style: TextStyle(
            color: _text,
            fontWeight: FontWeight.bold,
            fontSize: 20,
          ),
        ),
        backgroundColor: _surface,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.close_rounded, color: _text),
          onPressed: () => Navigator.of(context).pop(),
        ),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(1),
          child: Container(color: const Color(0xFFE2E8F0), height: 1),
        ),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 680),
            child: Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                color: _surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFFCBD5E1)),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withAlpha(5),
                    blurRadius: 10,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Numista.AI Privacy Policy',
                      style: TextStyle(
                        color: _text,
                        fontSize: 22,
                        fontWeight: FontWeight.w900,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      'Last updated: May 24, 2026',
                      style: TextStyle(color: _sub, fontSize: 13),
                    ),
                    Divider(height: 32, color: Color(0xFFE2E8F0)),
                    
                    Text(
                      'Numista.AI ("we", "our", or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, and share information when you use our mobile and web application.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '1. Information We Collect'),
                    _BulletPoint(
                      boldText: 'Account Information: ',
                      text: 'When you create an account, you provide us with your email address, name (optional), and a security PIN.',
                    ),
                    _BulletPoint(
                      boldText: 'Coin Collection Data: ',
                      text: 'We store information about the coins you add to your collection, including images, grades, costs, and notes. This data is stored securely in Firebase Firestore.',
                    ),
                    _BulletPoint(
                      boldText: 'Usage Data: ',
                      text: 'We collect standard analytical data to improve the application performance and user experience.',
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '2. How We Use Your Information'),
                    _BulletPoint(
                      boldText: 'Provide & Maintain: ',
                      text: 'To run the service and sync your coin collection data across all your logged-in devices.',
                    ),
                    _BulletPoint(
                      boldText: 'AI Estimations: ',
                      text: 'To calibrate and improve our coin valuation models.',
                    ),
                    _BulletPoint(
                      boldText: 'Communications: ',
                      text: 'To email you regarding updates, system announcements, or security alerts.',
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '3. Sharing Your Information'),
                    Text(
                      'We do not sell, rent, or trade your personal data. We only share information with third-party service providers (such as Google Firebase) necessary to execute core app features, or if legally required to comply with law enforcement.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '4. Data Security'),
                    Text(
                      'We implement industry-standard security measures to safeguard your information. However, no electronic transmission or storage method is 100% secure, and we cannot guarantee absolute security.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '5. Your Choices & Data Deletion'),
                    Text(
                      'You can update, edit, or delete your account and coin collection database directly in the application settings at any time. When you choose to delete your account, your data is wiped permanently from Firebase.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '6. Changes to this Policy'),
                    Text(
                      'We may update this Privacy Policy from time to time. We will notify you of any changes by posting the revised version inside the application.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 28),

                    Divider(height: 1, color: Color(0xFFE2E8F0)),
                    SizedBox(height: 20),
                    Text(
                      'Contact Us',
                      style: TextStyle(
                        color: _text,
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    SizedBox(height: 6),
                    Text(
                      'If you have any questions about this Privacy Policy, please contact us at support@numista.ai.',
                      style: TextStyle(color: _sub, fontSize: 13, height: 1.4),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  const _SectionHeader({required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 10),
      child: Text(
        title,
        style: const TextStyle(
          color: PrivacyScreen._blue,
          fontSize: 16,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }
}

class _BulletPoint extends StatelessWidget {
  final String boldText;
  final String text;
  const _BulletPoint({required this.boldText, required this.text});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(left: 12, bottom: 8),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Padding(
            padding: EdgeInsets.only(top: 6, right: 8),
            child: Icon(Icons.circle, size: 5, color: PrivacyScreen._sub),
          ),
          Expanded(
            child: RichText(
              text: TextSpan(
                style: const TextStyle(color: PrivacyScreen._text, fontSize: 14, height: 1.4),
                children: [
                  TextSpan(
                    text: boldText,
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  TextSpan(text: text),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
