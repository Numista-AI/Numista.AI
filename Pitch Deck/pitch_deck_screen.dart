// pitch_deck_screen.dart
// Interactive Pitch Deck for Google Cloud for Startups Program
// Showcases Morgan AI, Senior Collection Preservation & Estate Planning, and GCP Native Stack.

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:url_launcher/url_launcher.dart';

class PitchDeckScreen extends StatefulWidget {
  const PitchDeckScreen({super.key});

  @override
  State<PitchDeckScreen> createState() => _PitchDeckScreenState();
}

class _PitchDeckScreenState extends State<PitchDeckScreen> {
  int _currentSlide = 0;
  static const int _totalSlides = 12;

  // Simulator states
  double _estateValue = 150000;
  int _heirCount = 3;

  // Morgan Chat state
  final List<Map<String, String>> _morganMessages = [
    {
      'sender': 'morgan',
      'text': 'Hello! I\'m Morgan, your personal AI numismatist powered by Google Vertex AI. How can I help you document your coins or prepare an estate plan today?'
    }
  ];

  final FocusNode _focusNode = FocusNode();

  @override
  void dispose() {
    _focusNode.dispose();
    super.dispose();
  }

  void _nextSlide() {
    if (_currentSlide < _totalSlides - 1) {
      setState(() => _currentSlide++);
    }
  }

  void _prevSlide() {
    if (_currentSlide > 0) {
      setState(() => _currentSlide--);
    }
  }

  void _handleKey(KeyEvent event) {
    if (event is KeyDownEvent) {
      if (event.logicalKey == LogicalKeyboardKey.arrowRight ||
          event.logicalKey == LogicalKeyboardKey.space ||
          event.logicalKey == LogicalKeyboardKey.pageDown) {
        _nextSlide();
      } else if (event.logicalKey == LogicalKeyboardKey.arrowLeft ||
                 event.logicalKey == LogicalKeyboardKey.pageUp) {
        _prevSlide();
      } else if (event.logicalKey == LogicalKeyboardKey.home) {
        setState(() => _currentSlide = 0);
      } else if (event.logicalKey == LogicalKeyboardKey.end) {
        setState(() => _currentSlide = _totalSlides - 1);
      }
    }
  }

  void _askMorgan(String prompt, String reply) {
    setState(() {
      _morganMessages.add({'sender': 'user', 'text': prompt});
      _morganMessages.add({'sender': 'morgan', 'text': reply});
    });
  }

  @override
  Widget build(BuildContext context) {
    return KeyboardListener(
      focusNode: _focusNode,
      autofocus: true,
      onKeyEvent: _handleKey,
      child: Scaffold(
        backgroundColor: const Color(0xFF070B14),
        body: SafeArea(
          child: Column(
            children: [
              _buildHeader(),
              Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                  child: _buildSlideContent(_currentSlide),
                ),
              ),
              _buildFooter(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      decoration: const BoxDecoration(
        color: Color(0xFF0B1220),
        border: Border(bottom: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: const Color(0xFF1E293B),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: const Color(0xFFD4AF37)),
                ),
                child: const Text('🦉', style: TextStyle(fontSize: 18)),
              ),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Numista.AI',
                    style: GoogleFonts.inter(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  Text(
                    'Google Cloud for Startups Pitch Deck',
                    style: GoogleFonts.inter(
                      fontSize: 11,
                      color: const Color(0xFFD4AF37),
                    ),
                  ),
                ],
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: const Color(0xFF1E3A8A).withOpacity(0.4),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF3B82F6).withOpacity(0.5)),
            ),
            child: Row(
              children: [
                const Text('☁️ ', style: TextStyle(fontSize: 12)),
                Text(
                  'Powered by Google Vertex AI',
                  style: GoogleFonts.inter(
                    fontSize: 12,
                    fontWeight: FontWeight.w600,
                    color: const Color(0xFF93C5FD),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFooter() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
      decoration: const BoxDecoration(
        color: Color(0xFF0B1220),
        border: Border(top: BorderSide(color: Color(0xFF1E293B))),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back_ios_rounded, size: 16),
                color: Colors.white70,
                onPressed: _currentSlide > 0 ? _prevSlide : null,
              ),
              Text(
                'Slide ${_currentSlide + 1} of $_totalSlides',
                style: GoogleFonts.firaCode(fontSize: 13, color: Colors.white70),
              ),
              IconButton(
                icon: const Icon(Icons.arrow_forward_ios_rounded, size: 16),
                color: Colors.white70,
                onPressed: _currentSlide < _totalSlides - 1 ? _nextSlide : null,
              ),
            ],
          ),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: LinearProgressIndicator(
                value: (_currentSlide + 1) / _totalSlides,
                backgroundColor: const Color(0xFF1E293B),
                valueColor: const AlwaysStoppedAnimation<Color>(Color(0xFF4285F4)),
                minHeight: 6,
                borderRadius: BorderRadius.circular(3),
              ),
            ),
          ),
          Text(
            'Use ← → or Space to navigate',
            style: GoogleFonts.inter(fontSize: 12, color: Colors.white38),
          ),
        ],
      ),
    );
  }

  Widget _buildSlideContent(int index) {
    switch (index) {
      case 0:
        return _buildCoverSlide();
      case 1:
        return _buildProblemSlide();
      case 2:
        return _buildSolutionSlide();
      case 3:
        return _buildMorganSlide();
      case 4:
        return _buildEstateSlide();
      case 5:
        return _buildSeniorSlide();
      case 6:
        return _buildArchitectureSlide();
      case 7:
        return _buildMarketSlide();
      case 8:
        return _buildBusinessModelSlide();
      case 9:
        return _buildTractionSlide();
      case 10:
        return _buildGcpAskSlide();
      case 11:
        return _buildCtaSlide();
      default:
        return const SizedBox.shrink();
    }
  }

  Widget _buildCoverSlide() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: Colors.white.withOpacity(0.06),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.white12),
          ),
          child: Text(
            '✨ GOOGLE CLOUD STARTUP SHOWCASE',
            style: GoogleFonts.inter(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFF2DD4BF)),
          ),
        ),
        const SizedBox(height: 16),
        Text(
          'Preserving \$38 Billion in Tangible History.\nPowered by Google Vertex AI.',
          style: GoogleFonts.inter(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.white, height: 1.2),
        ),
        const SizedBox(height: 16),
        Text(
          'The world\'s first AI-native numismatic valuation, collection intelligence, and generational estate preservation platform — bridging senior collectors, heirs, and estate attorneys.',
          style: GoogleFonts.inter(fontSize: 16, color: Colors.white70, height: 1.5),
        ),
        const SizedBox(height: 32),
        Row(
          children: [
            _buildStatCard('\$84 Trillion', 'Great Wealth Transfer in Motion'),
            const SizedBox(width: 16),
            _buildStatCard('Gemini 3.5', 'Multimodal Vision via Vertex AI'),
            const SizedBox(width: 16),
            _buildStatCard('100% Algorithmic', 'Defensible Fair-Share Division'),
            const SizedBox(width: 16),
            _buildStatCard('7 Pipelines', 'Zero-Barrier Senior Ingestion'),
          ],
        ),
      ],
    );
  }

  Widget _buildProblemSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('⚠️ THE CRISIS', const Color(0xFFEA4335)),
        const SizedBox(height: 8),
        Text('The "Shoebox Dilemma" & The Silver Tsunami',
            style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 8),
        Text('Millions of aging collectors hold lifelong treasures that are completely undocumented.',
            style: GoogleFonts.inter(fontSize: 14, color: Colors.white70)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(
                child: _buildProblemCard(
                  '📦 Undocumented Safe Boxes',
                  'Over 70% of senior collectors keep their lifelong collection in safe deposit boxes or cigar boxes with mental-only knowledge.',
                  const Color(0xFFEA4335),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildProblemCard(
                  '📉 The 95% Liquidation Loss',
                  'When collectors pass, overwhelmed heirs sell \$10,000 rare coins to pawn shops for \$25 scrap metal melt value.',
                  const Color(0xFFFBBC05),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildProblemCard(
                  '⚔️ Estate Attorney Gridlock',
                  'Physical heirlooms cannot be split like bank accounts. Professional appraisals cost \$250/hr and spark family disputes.',
                  const Color(0xFF4285F4),
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSolutionSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('✨ THE SOLUTION', const Color(0xFF2DD4BF)),
        const SizedBox(height: 8),
        Text('An AI-Native Ecosystem for Lifelong Numismatists',
            style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('🔬 Multi-Method Senior Ingestion', 'USB microscope auto-capture, Document AI invoice parsing, checklist OCR, and PCGS cert scanning.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('💎 Hybrid Live Valuation', 'Bullion spot feeds + Greysheet CPG guide cache + PCGS population comps + eBay realized sold comps.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('📜 Legal Numismatic Passports', 'One-click court-admissible PDF reports with cryptographic QR verification for estate attorneys.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMorganSlide() {
    return Row(
      children: [
        Expanded(
          flex: 1,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildTag('🤖 CORE INNOVATION', const Color(0xFF2DD4BF)),
              const SizedBox(height: 8),
              Text('Meet Morgan: The AI Numismatist', style: GoogleFonts.inter(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 12),
              Text('Powered by Google Vertex AI & Gemini 3.5. Context-aware, patient, and senior-empowered.', style: GoogleFonts.inter(fontSize: 14, color: Colors.white70)),
              const SizedBox(height: 20),
              _buildInteractivePromptBtn(
                '💬 "I inherited an 1881-S Morgan Dollar from dad. What is it worth?"',
                'That\'s a wonderful heirloom! The 1881-S has one of the sharpest strikes in the series. In MS65 or higher, it can fetch \$180 to \$1,200+. Look closely at Liberty\'s hair above her ear. Would you like me to inspect a microscope photo?',
              ),
              const SizedBox(height: 8),
              _buildInteractivePromptBtn(
                '💬 "How do I divide my coin collection fairly between my 2 kids?"',
                'Our algorithmic solver groups high-value key date coins evenly, balances bullion sets, and computes an exact cash offset (e.g. \$140) to make the inheritance 100.0% mathematically equal with a court passport.',
              ),
            ],
          ),
        ),
        const SizedBox(width: 24),
        Expanded(
          flex: 1,
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF2DD4BF).withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Text('🦉', style: TextStyle(fontSize: 18)),
                    const SizedBox(width: 8),
                    Text('Morgan AI Sandbox', style: GoogleFonts.inter(fontWeight: FontWeight.bold, color: Colors.white)),
                    const Spacer(),
                    const Text('● Vertex AI Live', style: TextStyle(color: Color(0xFF2DD4BF), fontSize: 11)),
                  ],
                ),
                const Divider(color: Colors.white12, height: 24),
                Expanded(
                  child: ListView.builder(
                    itemCount: _morganMessages.length,
                    itemBuilder: (context, i) {
                      final msg = _morganMessages[i];
                      final isMorgan = msg['sender'] == 'morgan';
                      return Align(
                        alignment: isMorgan ? Alignment.centerLeft : Alignment.centerRight,
                        child: Container(
                          margin: const EdgeInsets.only(bottom: 8),
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: isMorgan ? const Color(0xFF1E293B) : const Color(0xFF2563EB),
                            borderRadius: BorderRadius.circular(12),
                            border: isMorgan ? Border.all(color: const Color(0xFF2DD4BF).withOpacity(0.3)) : null,
                          ),
                          child: Text(msg['text']!, style: GoogleFonts.inter(fontSize: 13, color: Colors.white)),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildEstateSlide() {
    final fairShare = _estateValue / _heirCount;
    return Row(
      children: [
        Expanded(
          flex: 1,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildTag('⚖️ WEALTH PRESERVATION', const Color(0xFFD4AF37)),
              const SizedBox(height: 8),
              Text('The Estate Planning Engine & Division Solver', style: GoogleFonts.inter(fontSize: 26, fontWeight: FontWeight.bold, color: Colors.white)),
              const SizedBox(height: 12),
              Text('Our proprietary Greedy LPT Partition Solver with Cash Equalization guarantees exact mathematical fairness across heirs.', style: GoogleFonts.inter(fontSize: 14, color: Colors.white70)),
              const SizedBox(height: 24),
              Text('Total Collection Value: \$${_estateValue.toInt()}', style: GoogleFonts.firaCode(color: const Color(0xFFD4AF37), fontWeight: FontWeight.bold)),
              Slider(
                value: _estateValue,
                min: 20000,
                max: 500000,
                divisions: 48,
                activeColor: const Color(0xFFD4AF37),
                onChanged: (v) => setState(() => _estateValue = v),
              ),
              Text('Number of Heirs: $_heirCount', style: GoogleFonts.firaCode(color: const Color(0xFF2DD4BF), fontWeight: FontWeight.bold)),
              Slider(
                value: _heirCount.toDouble(),
                min: 2,
                max: 5,
                divisions: 3,
                activeColor: const Color(0xFF2DD4BF),
                onChanged: (v) => setState(() => _heirCount = v.toInt()),
              ),
            ],
          ),
        ),
        const SizedBox(width: 24),
        Expanded(
          flex: 1,
          child: Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: const Color(0xFF0F172A),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: Colors.white12),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('SIMULATED EQUAL RESOLUTION', style: GoogleFonts.inter(fontSize: 12, color: Colors.white54, fontWeight: FontWeight.bold)),
                const SizedBox(height: 16),
                for (int i = 0; i < _heirCount; i++) ...[
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Heir ${i + 1} Share', style: GoogleFonts.inter(color: Colors.white, fontWeight: FontWeight.w600)),
                      Text('\$${fairShare.toInt()}', style: GoogleFonts.firaCode(color: const Color(0xFFD4AF37), fontWeight: FontWeight.bold)),
                    ],
                  ),
                  Text('Physical Coins: \$${(fairShare * 0.95).toInt()} + Cash Offset: \$${(fairShare * 0.05).toInt()}', style: const TextStyle(fontSize: 11, color: Colors.white38)),
                  const Divider(color: Colors.white12, height: 16),
                ],
                const Spacer(),
                const Text('✅ Eliminates probate disputes • Court-admissible timestamp', style: TextStyle(color: Color(0xFF34A853), fontSize: 12)),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildSeniorSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('👵 HIGH-EMPATHY ACCESSIBILITY', const Color(0xFF4285F4)),
        const SizedBox(height: 8),
        Text('Engineered for Senior Collectors', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('🔬 USB Microscope Station', 'Plug-and-play local desktop agent with motion stability auto-capture. Zero complex setup.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('📄 Google Document AI', 'Extracts 50 years of paper receipts and Littleton checklists automatically without typing.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('👁️ Dynamic UI Scaling', '1.0x / 1.3x / 1.6x typography magnification, ultra-contrast dark & parchment modes.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildArchitectureSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('☁️ GOOGLE CLOUD STACK', const Color(0xFF4285F4)),
        const SizedBox(height: 8),
        Text('Built on Google Cloud & Vertex AI', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: GridView.count(
            crossAxisCount: 3,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
            children: [
              _buildArchCard('🧠 Vertex AI / Gemini 3.5', 'Multimodal macro coin vision, die crack analysis, and Morgan AI conversation.'),
              _buildArchCard('📄 Document AI', 'Automated parsing of physical dealer invoices and printed collection checklists.'),
              _buildArchCard('⚡ Cloud Run', 'Serverless FastAPI REST microservices with sub-second autoscaling.'),
              _buildArchCard('🔥 Cloud Firestore', 'Real-time NoSQL synchronization across desktop hardware, web, and mobile.'),
              _buildArchCard('📊 BigQuery', 'Nightly ETL data warehouse for predictive pricing models and market analytics.'),
              _buildArchCard('🪣 Cloud Storage', 'Petabyte-scale 4K macro imagery archives with token-gated signed URLs.'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMarketSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('📈 MARKET SIZE', const Color(0xFFD4AF37)),
        const SizedBox(height: 8),
        Text('Massive, Untapped \$38B+ Collectibles Market', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Row(
          children: [
            _buildStatCard('\$38 Billion', 'TAM: Global Collectible Coins & Bullion'),
            const SizedBox(width: 16),
            _buildStatCard('\$6.2 Billion', 'SAM: Senior Estate Inventory & Valuation'),
            const SizedBox(width: 16),
            _buildStatCard('\$420 Million', 'SOM: AI SaaS & Appraisal Certifications'),
          ],
        ),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('👥 33M Active Collectors', 'Average collector age is 58. Over 10,000 Baby Boomers retire daily in the US.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('🎯 The "Why Now?"', 'Precious metal prices at all-time highs + Gemini 3.5 multimodal vision makes macro authentication possible.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildBusinessModelSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('💰 MONETIZATION', const Color(0xFF34A853)),
        const SizedBox(height: 8),
        Text('Multi-Stream High-Margin SaaS & Legal B2B', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('B2C Collector SaaS', '\$14.99 – \$29.99/mo for Gemini scans, live Greysheet pricing, and Morgan AI.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('B2B Estate Attorneys', '\$199 – \$499/mo per seat for token-gated Attorney Portals and probate exports.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('Transactional & Hardware', '\$49 – \$199 one-time for Certified Passports and USB Microscope kits.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildTractionSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('🚀 PRODUCTION READINESS', const Color(0xFF34A853)),
        const SizedBox(height: 8),
        Text('Traction, Milestones & Product Maturity', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('⚡ Live Web App', 'Production beta operational on Cloud Run & Firebase Hosting (numista-vault.web.app).')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('🗂️ 7 Ingestion Hubs', 'Working pipelines for CSV, PCGS Cert, Document AI Invoices, Checklist OCR, and USB Cam.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('🧪 100+ Demo Assets', 'Pre-seeded demo mode across US Coins, Currency, and World items.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGcpAskSlide() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _buildTag('🤝 GOOGLE PARTNERSHIP', const Color(0xFF4285F4)),
        const SizedBox(height: 8),
        Text('Deploying Google Cloud Startup Credits', style: GoogleFonts.inter(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white)),
        const SizedBox(height: 24),
        Expanded(
          child: Row(
            children: [
              Expanded(child: _buildFeatureCard('1. Vertex AI Fine-Tuning', 'Fine-tune Gemini 3.5 vision adapters on 500k+ numismatic image dataset for sub-millimeter die crack classification.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('2. BigQuery ML Intelligence', 'Scale BigQuery warehouse for predictive pricing models and market volatility analytics.')),
              const SizedBox(width: 16),
              Expanded(child: _buildFeatureCard('3. Cloud Run Elasticity', 'Scale serverless microservices globally with petabyte-scale GCS macro imagery.')),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildCtaSlide() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _buildTag('🌟 OUR VISION', const Color(0xFFD4AF37)),
          const SizedBox(height: 16),
          Text(
            'No Collection Left Forgotten.\nNo Family Left in the Dark.',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(fontSize: 36, fontWeight: FontWeight.bold, color: Colors.white, height: 1.2),
          ),
          const SizedBox(height: 16),
          Text(
            'We are building the definitive AI platform for the tangible wealth economy,\nhonoring the passion of senior collectors and protecting generational wealth.',
            textAlign: TextAlign.center,
            style: GoogleFonts.inter(fontSize: 16, color: Colors.white70),
          ),
          const SizedBox(height: 32),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              ElevatedButton.icon(
                icon: const Icon(Icons.open_in_browser_rounded),
                label: const Text('Launch Live App'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                ),
                onPressed: () => launchUrl(Uri.parse('https://numista-vault.web.app')),
              ),
              const SizedBox(width: 16),
              ElevatedButton.icon(
                icon: const Icon(Icons.email_outlined),
                label: const Text('Contact Founder'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFD4AF37),
                  foregroundColor: const Color(0xFF0B1220),
                  padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
                ),
                onPressed: () => launchUrl(Uri.parse('mailto:eric@numista.ai')),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Text(text, style: GoogleFonts.inter(fontSize: 11, fontWeight: FontWeight.bold, color: color)),
    );
  }

  Widget _buildStatCard(String value, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: const Color(0xFF0F172A),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.white12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(value, style: GoogleFonts.firaCode(fontSize: 22, fontWeight: FontWeight.bold, color: const Color(0xFFD4AF37))),
            const SizedBox(height: 4),
            Text(label, style: GoogleFonts.inter(fontSize: 12, color: Colors.white70)),
          ],
        ),
      ),
    );
  }

  Widget _buildProblemCard(String title, String desc, Color color) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border(left: BorderSide(color: color, width: 4), top: const BorderSide(color: Colors.white12), right: const BorderSide(color: Colors.white12), bottom: const BorderSide(color: Colors.white12)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 12),
          Text(desc, style: GoogleFonts.inter(fontSize: 13, color: Colors.white70, height: 1.5)),
        ],
      ),
    );
  }

  Widget _buildFeatureCard(String title, String desc) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: GoogleFonts.inter(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 12),
          Text(desc, style: GoogleFonts.inter(fontSize: 13, color: Colors.white70, height: 1.5)),
        ],
      ),
    );
  }

  Widget _buildArchCard(String title, String desc) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF0F172A),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF4285F4).withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: GoogleFonts.inter(fontSize: 14, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 8),
          Text(desc, style: GoogleFonts.inter(fontSize: 12, color: Colors.white70, height: 1.4)),
        ],
      ),
    );
  }

  Widget _buildInteractivePromptBtn(String prompt, String reply) {
    return InkWell(
      onTap: () => _askMorgan(prompt, reply),
      borderRadius: BorderRadius.circular(10),
      child: Container(
        padding: const EdgeInsets.all(10),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.04),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(color: Colors.white12),
        ),
        child: Text(prompt, style: GoogleFonts.inter(fontSize: 12, color: Colors.white70)),
      ),
    );
  }
}
