import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../screens/login_screen.dart';
import '../screens/base_layout.dart';
import '../screens/welcome_screen.dart';
import '../screens/public_info_screens.dart';
import '../services/guest_seed_service.dart';

/// Top-level authentication and routing gate for Numista.AI.
///
/// Encapsulates the Firebase [authStateChanges] stream. When unauthenticated,
/// displays [PublicInfoShell] for public routes, [BaseLayout] in demo mode
/// for demo visitors, or [LoginScreen] for login/signup. When authenticated,
/// transitions seamlessly to [BaseLayout] (or [WelcomeScreen] on first run).
class AuthGate extends StatefulWidget {
  final bool isDemo;
  final String? publicRoute;
  final int initialAuthTab;
  final Stream<User?>? authStream;

  const AuthGate({
    super.key,
    this.isDemo = false,
    this.publicRoute,
    this.initialAuthTab = 0,
    this.authStream,
  });

  /// Navigates to [AuthGate] and purges all previous routes from the stack.
  /// This ensures any auth state transitions (login, signup, signout, demo exit)
  /// immediately render BaseLayout or LoginScreen without leaving the user
  /// stranded on an orphaned route.
  static void navigateTo(
    BuildContext context, {
    bool isDemo = false,
    String? publicRoute,
    int initialAuthTab = 0,
    Stream<User?>? authStream,
  }) {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(
        builder: (_) => AuthGate(
          isDemo: isDemo,
          publicRoute: publicRoute,
          initialAuthTab: initialAuthTab,
          authStream: authStream,
        ),
      ),
      (route) => false,
    );
  }

  @override
  State<AuthGate> createState() => _AuthGateState();
}

class _AuthGateState extends State<AuthGate> {
  bool _welcomeDone = false;
  Future<bool>? _shouldShowWelcome;

  @override
  void initState() {
    super.initState();
    if (widget.isDemo) {
      GuestSeedService.activateBrowseDemo();
    }
  }

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<User?>(
      stream: widget.authStream ?? FirebaseAuth.instance.authStateChanges(),
      builder: (context, snapshot) {
        // Still waiting for Firebase to initialise — show branded splash
        if (snapshot.connectionState == ConnectionState.waiting) {
          return _buildSplash();
        }

        // Signed in -> show welcome screen on first launch, then main app
        if (snapshot.hasData && snapshot.data != null) {
          // INVARIANT: a real Firebase user must never see demo data.
          if (GuestSeedService.isBrowseDemoMode) {
            GuestSeedService.deactivateBrowseDemo();
            debugPrint(
                '[AUTH] Demo mode cleared for real user ${snapshot.data!.uid}');
          }
          assert(!GuestSeedService.isBrowseDemoMode,
              'INTEGRITY: Browse Demo still active after deactivateBrowseDemo(). '
              'User: ${snapshot.data!.uid}. deactivateBrowseDemo() has a logic defect.');

          if (_welcomeDone) {
            return const BaseLayout();
          }

          _shouldShowWelcome ??= WelcomeScreen.shouldShow();

          return FutureBuilder<bool>(
            future: _shouldShowWelcome,
            builder: (ctx, snap) {
              if (snap.connectionState == ConnectionState.waiting) {
                return _buildSplash();
              }
              final showWelcome = snap.data ?? false;
              if (showWelcome) {
                return WelcomeScreen(
                  onDone: () => setState(() => _welcomeDone = true),
                );
              }
              return const BaseLayout();
            },
          );
        }

        // User signed out — reset the cached future so next login is fresh.
        _shouldShowWelcome = null;
        _welcomeDone = false;

        // Not signed in:
        // 1. If public route requested, show PublicInfoShell
        if (widget.publicRoute != null) {
          return PublicInfoShell(targetRoute: widget.publicRoute!);
        }

        // 2. If demo mode requested or active, show BaseLayout in demo mode
        if (widget.isDemo || GuestSeedService.isBrowseDemoMode) {
          return const BaseLayout(isDemoMode: true);
        }

        // 3. Otherwise show LoginScreen
        return LoginScreen(initialTab: widget.initialAuthTab);
      },
    );
  }

  Widget _buildSplash() {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1220),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/logo_owl.png', height: 80,
                errorBuilder: (context, error, stackTrace) =>
                    const Icon(Icons.account_balance_rounded,
                        color: Color(0xFFD4A843), size: 64)),
            const SizedBox(height: 24),
            const Text('Numista.AI',
                style: TextStyle(
                    color: Colors.white,
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    letterSpacing: -0.5)),
            const SizedBox(height: 6),
            const Text('Your AI Coin Vault',
                style: TextStyle(
                    color: Color(0xFF94A3B8), fontSize: 13)),
            const SizedBox(height: 36),
            const SizedBox(
              width: 28, height: 28,
              child: CircularProgressIndicator(
                color: Color(0xFF2DD4BF),
                strokeWidth: 2.5,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
