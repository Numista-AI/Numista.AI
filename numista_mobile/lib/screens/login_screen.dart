import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:file_picker/file_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../constants.dart';
import '../services/auth_service.dart';
import '../services/guest_seed_service.dart';
import 'base_layout.dart';
import 'privacy_screen.dart';
import 'terms_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen>
    with SingleTickerProviderStateMixin {

  late final TabController _tabCtrl;
  static const _signInTab = 0;

  // ─── Form controllers ─────────────────────────────────────────────────────
  final _emailCtrl       = TextEditingController();
  final _pinCtrl         = TextEditingController();
  final _nameCtrl        = TextEditingController();
  final _emailCreateCtrl = TextEditingController();
  final _pinCreateCtrl   = TextEditingController();
  final _resetEmailCtrl  = TextEditingController();

  bool _loading          = false;
  bool _pinSignInVisible = false;   // Show/hide on Sign In tab
  bool _pinCreateVisible = false;   // Show/hide on Create Account tab (independent)
  bool _showResetForm    = false;
  bool _termsAccepted    = false;   // Must be true before Create My Vault button enables
  String? _error;
  String? _successMsg;

  // ─── Colour tokens — light/professional theme ────────────────────────────
  static const _bg       = Color(0xFFF0F2F6); // App body gray
  static const _surface  = Colors.white;
  static const _blue     = Color(0xFF1565C0); // Primary blue (matches owl)
  static const _blueSoft = Color(0xFFE3F2FD); // Light blue fills
  static const _text     = Color(0xFF0F172A); // Near-black
  static const _sub      = Color(0xFF64748B); // Medium gray
  static const _grey     = Color(0xFF94A3B8); // Hint gray
  static const _border   = Color(0xFFCBD5E1); // Input borders
  static const _inputBg  = Color(0xFFF8FAFC); // Input fill
  static const _green    = Color(0xFF16A34A);

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
    _tabCtrl.addListener(() {
      if (!_tabCtrl.indexIsChanging) {
        setState(() { _error = null; _successMsg = null; });
      }
    });
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    _emailCtrl.dispose();
    _pinCtrl.dispose();
    _nameCtrl.dispose();
    _emailCreateCtrl.dispose();
    _pinCreateCtrl.dispose();
    _resetEmailCtrl.dispose();
    super.dispose();
  }

  // ─── Actions ─────────────────────────────────────────────────────────────
  Future<void> _signIn() async {
    final email = _emailCtrl.text.trim();
    final pin   = _pinCtrl.text.trim();
    if (email.isEmpty || pin.isEmpty) {
      setState(() => _error = 'Please enter your email and PIN.');
      return;
    }
    if (pin.length != 6) {
      setState(() => _error = 'Your PIN must be exactly 6 digits.');
      return;
    }
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signIn(email, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

  Future<void> _createAccount() async {
    final email = _emailCreateCtrl.text.trim();
    final name  = _nameCtrl.text.trim();
    final pin   = _pinCreateCtrl.text.trim();
    if (email.isEmpty || pin.isEmpty) {
      setState(() => _error = 'Please fill in your email and choose a PIN.');
      return;
    }
    if (pin.length != 6 || int.tryParse(pin) == null) {
      setState(() => _error = 'PIN must be exactly 6 digits (numbers only).');
      return;
    }
    if (!_termsAccepted) {
      setState(() => _error = 'Please accept the Terms of Use and Privacy Policy to continue.');
      return;
    }
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.createAccount(
        email, name.isEmpty ? email.split('@').first : name, pin);
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

  Future<void> _googleSignIn() async {
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInWithGoogle();
    if (mounted) setState(() { _loading = false; _error = result.error; });
  }

  Future<void> _signInAsGuest() async {
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.signInAsGuest();
    if (mounted) {
      setState(() { _loading = false; _error = result.error; });
      if (result.ok && AuthService.currentUser != null) {
        await GuestSeedService.seedIfNeeded(AuthService.currentUser!.uid);
      }
    }
  }

  Future<void> _browseDemo() async {
    setState(() => _loading = true);
    await GuestSeedService.activateBrowseDemo();
    if (mounted) {
      setState(() => _loading = false);
      // Navigate directly to the app in demo mode (no Firebase auth needed)
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (_) => const BaseLayout(isDemoMode: true)),
      );
    }
  }

  Future<void> _sendResetLink() async {
    final email = _resetEmailCtrl.text.trim();
    if (email.isEmpty) {
      setState(() => _error = 'Please enter your email address.');
      return;
    }
    setState(() { _loading = true; _error = null; });
    final result = await AuthService.resetPin(email);
    if (mounted) {
      setState(() {
        _loading    = false;
        _error      = result.error;
        _successMsg = result.message;
        if (result.ok) _showResetForm = false;
      });
    }
  }

  // ─── Build ───────────────────────────────────────────────────────────────
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: LayoutBuilder(
        builder: (context, constraints) {
          // Wide screen (tablet / desktop): side-by-side panels
          if (constraints.maxWidth >= 800) {
            return Row(
              children: [
                Expanded(flex: 5, child: _buildBrandPanel()),
                Expanded(
                  flex: 4,
                  child: Container(
                    color: _surface,
                    child: SingleChildScrollView(
                      padding: const EdgeInsets.symmetric(horizontal: 48, vertical: 64),
                      child: ConstrainedBox(
                        constraints: const BoxConstraints(maxWidth: 420),
                        child: _showResetForm ? _buildResetForm() : _buildAuthForm(),
                      ),
                    ),
                  ),
                ),
              ],
            );
          }

          // Narrow screen (phone): stacked layout
          return Container(
            color: _surface,
            child: SafeArea(
              child: SingleChildScrollView(
                child: Column(
                  children: [
                    // ── Compact mobile header ──────────────────────────────
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
                      decoration: const BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [Color(0xFFF0F4FA), Color(0xFFE8EFF8)],
                        ),
                      ),
                      child: Column(
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Image.asset('assets/logo_owl.png', height: 52),
                              const SizedBox(width: 14),
                              const Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    'NUMISTA.AI',
                                    style: TextStyle(
                                      color: _text,
                                      fontSize: 24,
                                      fontWeight: FontWeight.w900,
                                      letterSpacing: 1.5,
                                    ),
                                  ),
                                  Text(
                                    'AI-Powered Coin Collection Manager',
                                    style: TextStyle(color: _sub, fontSize: 12),
                                  ),
                                ],
                              ),
                            ],
                          ),
                          const SizedBox(height: 16),
                          // Mini stats strip
                          Container(
                            padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 20),
                            decoration: BoxDecoration(
                              color: _surface,
                              borderRadius: BorderRadius.circular(10),
                              border: Border.all(color: _border),
                            ),
                            child: const Row(
                              mainAxisAlignment: MainAxisAlignment.spaceAround,
                              children: [
                                _StatBadge(value: '100+', label: 'Coin\nTypes'),
                                _StatDivider(),
                                _StatBadge(value: '1,900+', label: 'Reference\nCoins'),
                                _StatDivider(),
                                _StatBadge(value: 'AI+', label: 'Community\nVerified'),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),

                    // ── Auth form ──────────────────────────────────────────
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 28),
                      child: _showResetForm ? _buildResetForm() : _buildAuthForm(),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }


  // ─── Left Brand Panel ─────────────────────────────────────────────────────
  Widget _buildBrandPanel() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [Color(0xFFF0F4FA), Color(0xFFE8EFF8)],
        ),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.symmetric(horizontal: 60, vertical: 48),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Logo
            Image.asset('assets/logo_owl.png', height: 90),
            const SizedBox(height: 20),

            // Headline
            const Text(
              'NUMISTA.AI',
              style: TextStyle(
                color: _text,
                fontSize: 40,
                fontWeight: FontWeight.w900,
                letterSpacing: 2,
              ),
            ),
            const SizedBox(height: 6),
            const Text(
              'AI-Powered Coin Collection Manager',
              style: TextStyle(color: _sub, fontSize: 16),
            ),
            const SizedBox(height: 32),

            // Feature bullets
            ...const [
              ('🤖', 'AI-estimated values for every coin in your collection'),
              ('📊', 'Organize thousands of coins instantly'),
              ('🔬', 'Microscope scanner for precision grading'),
              ('📋', 'Estate planning reports in seconds'),
              ('🎁', 'Smart wishlists & eBay price tracking'),
              ('🧑‍🏫', 'Human AI Trainer Review Board — community-powered accuracy'),
            ].map((f) => Padding(
              padding: const EdgeInsets.only(bottom: 14),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: _blueSoft,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Center(
                      child: Text(f.$1, style: const TextStyle(fontSize: 16)),
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        f.$2,
                        style: const TextStyle(color: _text, fontSize: 14, height: 1.4),
                      ),
                    ),
                  ),
                ],
              ),
            )),

            const SizedBox(height: 32),

            // Stats strip
            Container(
              padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 24),
              decoration: BoxDecoration(
                color: _surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: _border),
                boxShadow: [
                  BoxShadow(color: Colors.black.withAlpha(10), blurRadius: 8, offset: const Offset(0, 2)),
                ],
              ),
              child: const Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _StatBadge(value: '100+', label: 'Coin Types\nRecognized'),
                  _StatDivider(),
                  _StatBadge(value: '1,900+', label: 'Reference\nCoins'),
                  _StatDivider(),
                  _StatBadge(value: 'AI+', label: 'Community\nVerified'),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // ─── Auth Form ────────────────────────────────────────────────────────────
  Widget _buildAuthForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        // Tab bar
        Container(
          decoration: BoxDecoration(
            color: _bg,
            borderRadius: BorderRadius.circular(10),
          ),
          child: TabBar(
            controller: _tabCtrl,
            indicator: BoxDecoration(
              color: _blue,
              borderRadius: BorderRadius.circular(8),
            ),
            indicatorSize: TabBarIndicatorSize.tab,
            labelColor: Colors.white,
            unselectedLabelColor: _sub,
            labelStyle: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14),
            dividerColor: Colors.transparent,
            tabs: const [Tab(text: 'Sign In'), Tab(text: 'Create Account')],
          ),
        ),
        const SizedBox(height: 28),

        // Error / success banners
        if (_error != null) ...[ _banner(_error!, isError: true), const SizedBox(height: 16) ],
        if (_successMsg != null) ...[ _banner(_successMsg!, isError: false), const SizedBox(height: 16) ],

        // Tab views — sized to content, no fixed height needed
        AnimatedSize(
          duration: const Duration(milliseconds: 200),
          child: SizedBox(
            height: _tabCtrl.index == _signInTab ? 280 : 360,
            child: TabBarView(
              controller: _tabCtrl,
              physics: const NeverScrollableScrollPhysics(),
              children: [ _buildSignInTab(), _buildCreateTab() ],
            ),
          ),
        ),

        const SizedBox(height: 20),
        _divider('or'),
        const SizedBox(height: 20),

        // Google Sign-In
        _googleButton(),

        const SizedBox(height: 12),

        // Free Scan Preview
        ElevatedButton.icon(
          onPressed: _loading ? null : () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (_) => const FreeScanPreviewScreen()),
            );
          },
          icon: const Icon(Icons.camera_alt_outlined, size: 20),
          label: const Text('Free Scan Preview', style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFF59E0B), // Amber
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            padding: const EdgeInsets.symmetric(vertical: 16),
            elevation: 0,
          ),
        ),

        const SizedBox(height: 12),
        // Forgot PIN
        Center(
          child: TextButton(
            onPressed: () => setState(() { _showResetForm = true; _error = null; }),
            child: Text('Forgot your PIN?', style: TextStyle(color: _grey, fontSize: 13)),
          ),
        ),

        const SizedBox(height: 20),
        _divider('explore without an account'),
        const SizedBox(height: 20),

        // ── Guest Entry Options ─────────────────────────────────────────
        Row(
          children: [
            // Browse Demo — read-only
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _loading ? null : _browseDemo,
                icon: const Icon(Icons.search_rounded, size: 18),
                label: const Text('Browse Demo'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _sub,
                  side: const BorderSide(color: _border),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w500),
                ),
              ),
            ),
            const SizedBox(width: 12),
            // Try It Free — anonymous auth + wizard
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _loading ? null : _signInAsGuest,
                icon: _loading
                    ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Icon(Icons.rocket_launch_rounded, size: 18),
                label: const Text('Try It Free'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF0D9488), // teal — distinct from blue sign-in
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  textStyle: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Center(
          child: Text(
            'Browse Demo: read-only  •  Try It Free: all features, no commitment',
            style: TextStyle(color: _grey, fontSize: 11),
            textAlign: TextAlign.center,
          ),
        ),
      ],
    );
  }

  Widget _buildSignInTab() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _label('Email Address'),
          const SizedBox(height: 6),
          _textField(controller: _emailCtrl, hint: 'your@email.com', keyboardType: TextInputType.emailAddress),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _label('6-Digit PIN')),
              const Text(
                'Instead of a password',
                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 11, fontStyle: FontStyle.italic),
              ),
            ],
          ),
          const SizedBox(height: 6),
          _pinField(_pinCtrl, _pinSignInVisible, () => setState(() => _pinSignInVisible = !_pinSignInVisible)),
          const SizedBox(height: 20),
          _primaryButton(label: _loading ? 'Signing in…' : 'Sign In', onTap: _loading ? null : _signIn),
        ],
      ),
    );
  }

  Widget _buildCreateTab() {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _label('Your Name (optional)'),
          const SizedBox(height: 6),
          _textField(controller: _nameCtrl, hint: 'Eric  (or leave blank)', keyboardType: TextInputType.name),
          const SizedBox(height: 12),
          _label('Email Address'),
          const SizedBox(height: 6),
          _textField(controller: _emailCreateCtrl, hint: 'your@email.com', keyboardType: TextInputType.emailAddress),
          const SizedBox(height: 12),
          _label('Choose a 6-Digit PIN'),
          const SizedBox(height: 6),
          _pinField(_pinCreateCtrl, _pinCreateVisible, () => setState(() => _pinCreateVisible = !_pinCreateVisible)),
          const SizedBox(height: 16),
          // Terms of Use + Privacy Policy acceptance
          InkWell(
            onTap: () => setState(() => _termsAccepted = !_termsAccepted),
            borderRadius: BorderRadius.circular(6),
            child: Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Checkbox(
                    value: _termsAccepted,
                    activeColor: _blue,
                    visualDensity: VisualDensity.compact,
                    onChanged: (v) => setState(() => _termsAccepted = v ?? false),
                  ),
                  const SizedBox(width: 4),
                  Expanded(
                    child: Padding(
                      padding: const EdgeInsets.only(top: 10),
                      child: RichText(
                        text: TextSpan(
                          style: const TextStyle(color: _sub, fontSize: 12, height: 1.4),
                          children: [
                            const TextSpan(text: 'I agree to the Numista.AI '),
                            WidgetSpan(
                              child: GestureDetector(
                                onTap: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const TermsScreen()),
                                  );
                                },
                                child: const Text('Terms of Use',
                                    style: TextStyle(color: _blue, fontSize: 12,
                                        decoration: TextDecoration.underline)),
                              ),
                            ),
                            const TextSpan(text: ' and '),
                            WidgetSpan(
                              child: GestureDetector(
                                onTap: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(builder: (_) => const PrivacyScreen()),
                                  );
                                },
                                child: const Text('Privacy Policy',
                                    style: TextStyle(color: _blue, fontSize: 12,
                                        decoration: TextDecoration.underline)),
                              ),
                            ),
                            const TextSpan(text: '.'),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          _primaryButton(
            label: _loading ? 'Creating account...' : 'Create My Account and Vault',
            onTap: (_loading || !_termsAccepted) ? null : _createAccount,
          ),
          const SizedBox(height: 8),
          if (!_termsAccepted)
            const Text(
              'Please accept the Terms of Use and Privacy Policy above to create your account.',
              style: TextStyle(color: _grey, fontSize: 11),
              textAlign: TextAlign.center,
            ),
        ],
      ),
    );
  }

  // ─── Reset PIN Form ───────────────────────────────────────────────────────
  Widget _buildResetForm() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        const Text('Reset Your PIN',
            style: TextStyle(color: _text, fontSize: 26, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        const Text("Enter your email and we'll send you a link to reset your PIN.",
            style: TextStyle(color: _sub, fontSize: 14)),
        const SizedBox(height: 32),
        if (_error != null) ...[ _banner(_error!, isError: true), const SizedBox(height: 16) ],
        if (_successMsg != null) ...[ _banner(_successMsg!, isError: false), const SizedBox(height: 16) ],
        _label('Email Address'),
        const SizedBox(height: 6),
        _textField(controller: _resetEmailCtrl, hint: 'your@email.com', keyboardType: TextInputType.emailAddress),
        const SizedBox(height: 24),
        _primaryButton(label: _loading ? 'Sending…' : 'Send Reset Link', onTap: _loading ? null : _sendResetLink),
        const SizedBox(height: 16),
        TextButton(
          onPressed: () => setState(() { _showResetForm = false; _error = null; _successMsg = null; }),
          child: const Text('← Back to Sign In', style: TextStyle(color: _sub)),
        ),
      ],
    );
  }

  // ─── Widget helpers ───────────────────────────────────────────────────────
  Widget _label(String text) => Text(text,
      style: const TextStyle(color: _sub, fontSize: 12, fontWeight: FontWeight.w600, letterSpacing: 0.5));

  Widget _textField({required TextEditingController controller, required String hint, TextInputType? keyboardType}) =>
      TextField(
        controller: controller,
        keyboardType: keyboardType,
        style: const TextStyle(color: _text, fontSize: 14),
        decoration: InputDecoration(
          hintText: hint,
          hintStyle: TextStyle(color: _grey.withAlpha(160), fontSize: 14),
          filled: true,
          fillColor: _inputBg,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _border)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _border)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _blue, width: 1.5)),
        ),
      );

  Widget _pinField(TextEditingController ctrl, bool visible, VoidCallback onToggle) => TextField(
        controller: ctrl,
        obscureText: !visible,
        maxLength: 6,
        keyboardType: TextInputType.number,
        inputFormatters: [FilteringTextInputFormatter.digitsOnly],
        style: const TextStyle(color: _text, fontSize: 20, letterSpacing: 8),
        textAlign: TextAlign.center,
        decoration: InputDecoration(
          hintText: '● ● ● ● ● ●',
          hintStyle: TextStyle(color: _grey.withAlpha(140), letterSpacing: 6, fontSize: 14),
          counterText: '',
          filled: true,
          fillColor: _inputBg,
          contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _border)),
          enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _border)),
          focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: const BorderSide(color: _blue, width: 1.5)),
          suffixIcon: IconButton(
            icon: Icon(visible ? Icons.visibility_off : Icons.visibility, color: _grey, size: 18),
            onPressed: onToggle,
          ),
        ),
      );

  Widget _primaryButton({required String label, required VoidCallback? onTap}) =>
      ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: _blue,
          foregroundColor: Colors.white,
          disabledBackgroundColor: _blue.withAlpha(100),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(vertical: 16),
          textStyle: const TextStyle(fontSize: 15, fontWeight: FontWeight.w700),
        ),
        child: _loading
            ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
            : Text(label),
      );

  Widget _googleButton() => OutlinedButton.icon(
        onPressed: _loading ? null : _googleSignIn,
        icon: const Text('G ', style: TextStyle(color: Color(0xFF4285F4), fontSize: 18, fontWeight: FontWeight.bold)),
        label: const Text('Continue with Google'),
        style: OutlinedButton.styleFrom(
          foregroundColor: _text,
          side: const BorderSide(color: _border),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
          padding: const EdgeInsets.symmetric(vertical: 14),
          textStyle: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500),
        ),
      );

  Widget _divider(String label) => Row(children: [
        const Expanded(child: Divider(color: _border)),
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12),
          child: Text(label, style: TextStyle(color: _grey.withAlpha(180), fontSize: 11)),
        ),
        const Expanded(child: Divider(color: _border)),
      ]);

  Widget _banner(String msg, {required bool isError}) => Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: isError ? const Color(0xFFDC2626).withAlpha(15) : _green.withAlpha(15),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: isError ? const Color(0xFFDC2626).withAlpha(60) : _green.withAlpha(60)),
        ),
        child: Text(msg, style: TextStyle(color: isError ? const Color(0xFFDC2626) : _green, fontSize: 13)),
      );
}

// ─── Helper widgets ────────────────────────────────────────────────────────

class _StatBadge extends StatelessWidget {
  final String value;
  final String label;
  const _StatBadge({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF1565C0))),
        const SizedBox(height: 4),
        Text(label, style: const TextStyle(fontSize: 11, color: Color(0xFF64748B), height: 1.3), textAlign: TextAlign.center),
      ],
    );
  }
}

class _StatDivider extends StatelessWidget {
  const _StatDivider();
  @override
  Widget build(BuildContext context) =>
      Container(width: 1, height: 36, color: const Color(0xFFCBD5E1));
}

// ─────────────────────────────────────────────────────────────────────────────
// FREE SCAN PREVIEW SCREEN
// ─────────────────────────────────────────────────────────────────────────────
class FreeScanPreviewScreen extends StatefulWidget {
  const FreeScanPreviewScreen({super.key});

  @override
  State<FreeScanPreviewScreen> createState() => _FreeScanPreviewScreenState();
}

class _FreeScanPreviewScreenState extends State<FreeScanPreviewScreen> {
  Uint8List? _obverseBytes;
  Uint8List? _reverseBytes;
  String? _obverseName;
  String? _reverseName;

  bool _loading = false;
  String? _error;
  Map<String, dynamic>? _result;

  Future<void> _pickImage(bool isObverse) async {
    try {
      final res = await FilePicker.pickFiles(
        type: FileType.image,
        allowMultiple: false,
        withData: true,
      );
      if (res == null || res.files.isEmpty) return;
      final f = res.files.first;
      if (f.bytes == null) return;

      setState(() {
        if (isObverse) {
          _obverseBytes = f.bytes;
          _obverseName = f.name;
        } else {
          _reverseBytes = f.bytes;
          _reverseName = f.name;
        }
        _result = null; // Clear previous result
        _error = null;
      });
    } catch (e) {
      setState(() => _error = 'Failed to pick image: $e');
    }
  }

  Future<void> _runScan() async {
    if (_obverseBytes == null || _reverseBytes == null) {
      setState(() => _error = 'Please select both Obverse and Reverse photos.');
      return;
    }

    setState(() {
      _loading = true;
      _error = null;
      _result = null;
    });

    try {
      final uri = Uri.parse('$kApiBaseUrl/api/identify_coin_photo');
      final request = http.MultipartRequest('POST', uri);

      request.fields['user_email'] = 'guest@numista.ai';
      request.fields['save_to_collection'] = 'false';

      // Helper to parse content type
      MediaType getMediaType(String filename) {
        final ext = filename.split('.').last.toLowerCase();
        final mime = {
          'png': 'image/png',
          'gif': 'image/gif',
          'webp': 'image/webp',
        }[ext] ?? 'image/jpeg';
        return MediaType.parse(mime);
      }

      request.files.add(http.MultipartFile.fromBytes(
        'image_a',
        _obverseBytes!,
        filename: _obverseName ?? 'obverse.jpg',
        contentType: getMediaType(_obverseName ?? 'obverse.jpg'),
      ));

      request.files.add(http.MultipartFile.fromBytes(
        'image_b',
        _reverseBytes!,
        filename: _reverseName ?? 'reverse.jpg',
        contentType: getMediaType(_reverseName ?? 'reverse.jpg'),
      ));

      final streamedResponse = await request.send().timeout(const Duration(seconds: 45));
      final responseBody = await streamedResponse.stream.bytesToString();

      if (streamedResponse.statusCode == 200) {
        final data = jsonDecode(responseBody);
        setState(() {
          _result = data as Map<String, dynamic>;
          _loading = false;
        });
      } else {
        setState(() {
          _error = 'Scan failed: Server returned status code ${streamedResponse.statusCode}';
          _loading = false;
        });
      }
    } catch (e) {
      setState(() {
        _error = 'Network or API error: $e';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A), // Premium Dark
      appBar: AppBar(
        backgroundColor: const Color(0xFF1E293B),
        title: const Text('Free AI Scan Preview', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back, color: Colors.white),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'Test Our AI Coin Scanner',
              style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 6),
            const Text(
              'Upload obverse (front) and reverse (back) photos to see AI identification in action.',
              style: TextStyle(color: Colors.white60, fontSize: 13),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 28),

            // Photo picker row
            Row(
              children: [
                Expanded(
                  child: _imagePickerBox('Obverse (Front)', _obverseBytes, () => _pickImage(true)),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _imagePickerBox('Reverse (Back)', _reverseBytes, () => _pickImage(false)),
                ),
              ],
            ),
            const SizedBox(height: 28),

            if (_error != null) ...[
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.red.withAlpha(20),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withAlpha(50)),
                ),
                child: Text(_error!, style: const TextStyle(color: Colors.redAccent, fontSize: 13)),
              ),
              const SizedBox(height: 16),
            ],

            if (_loading) ...[
              const Card(
                color: Color(0xFF1E293B),
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Column(
                    children: [
                      CircularProgressIndicator(color: Color(0xFFF59E0B)),
                      SizedBox(height: 16),
                      Text('Morgan is scanning your coin...', style: TextStyle(color: Colors.white70, fontSize: 14)),
                      SizedBox(height: 6),
                      Text('Analyzing details & estimating value', style: TextStyle(color: Colors.white38, fontSize: 11)),
                    ],
                  ),
                ),
              ),
            ] else if (_result != null) ...[
              _buildResultCard(),
            ] else ...[
              ElevatedButton.icon(
                onPressed: (_obverseBytes == null || _reverseBytes == null) ? null : _runScan,
                icon: const Icon(Icons.flash_on_rounded),
                label: const Text('Scan Coin Now', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFFF59E0B),
                  foregroundColor: Colors.white,
                  disabledBackgroundColor: Colors.white10,
                  disabledForegroundColor: Colors.white30,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
              ),
            ],
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _imagePickerBox(String label, Uint8List? bytes, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 160,
        decoration: BoxDecoration(
          color: const Color(0xFF1E293B),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.white10),
        ),
        child: bytes != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.memory(bytes, fit: BoxFit.cover),
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.add_a_photo_outlined, color: Colors.white38, size: 36),
                  const SizedBox(height: 10),
                  Text(label, style: const TextStyle(color: Colors.white60, fontSize: 13, fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  const Text('Tap to upload', style: TextStyle(color: Colors.white30, fontSize: 11)),
                ],
              ),
      ),
    );
  }

  Widget _buildResultCard() {
    final r = _result!;
    final title = [
      r['Year']?.toString() ?? '',
      if (r['Mint Mark'] != null && r['Mint Mark'].toString().isNotEmpty) '(${r['Mint Mark']})',
      r['Denomination']?.toString() ?? 'Unknown Coin'
    ].where((s) => s.isNotEmpty).join(' ');

    return Card(
      color: const Color(0xFF1E293B),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle_rounded, color: Colors.green, size: 24),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    title,
                    style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            const Divider(color: Colors.white10, height: 24),
            _buildResultRow('Series', r['Program/Series'] ?? 'N/A'),
            _buildResultRow('Grade', r['Condition'] ?? 'Ungraded'),
            _buildResultRow('AI Value', r['AI Estimated Value'] ?? 'Pending'),
            _buildResultRow('Metal', r['Metal Content'] ?? 'N/A'),
            const SizedBox(height: 24),

            // CTA container
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xFF0F172A),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF334155)),
              ),
              child: Column(
                children: [
                  const Text(
                    '🔒 Want to save this coin?',
                    style: TextStyle(color: Color(0xFFF59E0B), fontSize: 14, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'Create a free account to track your collection, log values, and export estate plans.',
                    style: TextStyle(color: Colors.white70, fontSize: 12),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 16),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        Navigator.of(context).pop(); // Back to Login page
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0D9488),
                        foregroundColor: Colors.white,
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                        padding: const EdgeInsets.symmetric(vertical: 12),
                      ),
                      child: const Text('Create Free Account', style: TextStyle(fontWeight: FontWeight.bold)),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.white38, fontSize: 13)),
          Text(value, style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
