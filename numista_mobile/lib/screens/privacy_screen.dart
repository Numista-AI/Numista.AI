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
                      'Last updated: June 27, 2026',
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
                      boldText: 'Desktop Agent Data: ',
                      text: 'The optional local Desktop Agent accesses your microscope camera (processed entirely locally) and secures account pairing using your email address and an optional device name. High-resolution coin images captured are uploaded directly to your private Google Cloud Storage folder.',
                    ),
                    _BulletPoint(
                      boldText: 'Account & Profile: ',
                      text: 'We utilize Firebase Authentication to securely manage your account via email, optional alias, and a password or 6-digit security PIN.',
                    ),
                    _BulletPoint(
                      boldText: 'Coin Collection Data: ',
                      text: 'We store your cataloged coins, images, grades, costs, and personal notes securely in Firebase Firestore. Optional Reference Library Contribution: If you voluntarily opt-in via our in-app settings, your anonymized coin photos may be contributed to our public global reference library to help the collector community (this is strictly optional and off by default).',
                    ),
                    _BulletPoint(
                      boldText: 'Estate Planning Profiles (Zero-Knowledge): ',
                      text: 'To protect your privacy, we store only your jurisdiction, marital status, and anonymous beneficiary aliases (e.g. "Primary Heir") in our database. Sensitive names and contact details for yourself, your executors, your attorneys, and your heirs are processed strictly in-memory during generation and are never written to our database. Numista.AI does not retain a copy of your completed PDF report on our servers or Google Cloud Storage.',
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '2. Local Loopback Connectivity'),
                    Text(
                      'The Desktop Agent runs a local loopback server on localhost:5000 using local SSL/TLS encryption. This connection stays entirely within your machine\'s memory space (isolated from external internet traffic) and enforces strict CORS policies to restrict requests exclusively to Numista.AI.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '3. How We Use Your Information'),
                    _BulletPoint(
                      boldText: 'Collection Syncing: ',
                      text: 'To upload microscope scans and log coin records to your personal collection database.',
                    ),
                    _BulletPoint(
                      boldText: 'AI Coin Identification: ',
                      text: 'To analyze coin images securely via Google Cloud\'s Gemini enterprise platform to detect coin type, year, mint mark, and varieties.',
                    ),
                    _BulletPoint(
                      boldText: 'Enrichment & Metrics: ',
                      text: 'To enrich collection records with metadata from numismatic databases (such as PCGS) and estimate valuations.',
                    ),
                    _BulletPoint(
                      boldText: 'Estate PDF Reports: ',
                      text: 'To compile your legal instructions and coin inventory into formatted PDFs for your heirs, executors, or attorneys.',
                    ),
                    _BulletPoint(
                      boldText: 'Direct Sharing Facilitation: ',
                      text: 'To generate local email templates and clipboard text packages to easily share your downloaded inventory directly with your legal counsel.',
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '4. Sharing Your Information'),
                    Text(
                      'We do not sell, rent, or trade your personal data. We securely host your data on Google Firebase (Firestore and Cloud Storage). Scanned images are processed securely using Google Cloud\'s Gemini enterprise platform (your data is never used to train public models). No data is shared with third-party advertisers.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    const SizedBox(height: 10),
                    const _BulletPoint(
                      boldText: 'Global Reference Library Index: ',
                      text: 'If you explicitly opt-in to contribute images, your anonymized coin photos (stripped of all user identifiers, costs, and personal notes) are hosted in our public reference library bucket on Google Cloud Storage to populate the canonical catalog for all users.',
                    ),
                    const SizedBox(height: 8),
                    const _BulletPoint(
                      boldText: 'Affiliate Integration Partners: ',
                      text: 'When viewing or interacting with your collection wishlist, the Service integrates with the eBay Partner Network (EPN) to surface live product availability cards. Interacting with these features utilizes standard affiliate tracking identifiers to manage campaign routing, strictly isolated from your personal estate data.',
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '5. Data Security'),
                    Text(
                      'We implement industry-standard security measures including HTTPS/TLS encryption for all data transfers. Database access is isolated per-user via Firebase rules, ensuring only you can read or write to your personal coin collection. Estate reports are rendered via temporary server infrastructure, ensuring that high-value inventory results combined with real personal identities never exist on static disk storage.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '6. Your Choices & Data Deletion'),
                    Text(
                      'You can edit or delete coin records and estate planning profiles in the app at any time. Accounts can be permanently deleted by contacting support, which wipes all collection history, estate profiles, anonymous generation metadata, and images from Firebase. Local Desktop Agent settings can be deleted by removing the AppData configuration directory.',
                      style: TextStyle(color: _text, fontSize: 14, height: 1.5),
                    ),
                    SizedBox(height: 20),

                    _SectionHeader(title: '7. Changes to this Policy'),
                    Text(
                      'We may update this Privacy Policy from time to time. We will notify you of any changes by posting the revised version inside the application and on our website.',
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
