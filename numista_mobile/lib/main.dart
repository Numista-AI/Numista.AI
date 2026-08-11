import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_options.dart';
import 'screens/base_layout.dart';
import 'screens/login_screen.dart';
import 'screens/welcome_screen.dart';
import 'screens/attorney_portal_screen.dart';
import 'screens/public_wishlist_view_screen.dart';
import 'services/theme_provider.dart';
import 'package:google_fonts/google_fonts.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  ErrorWidget.builder = (FlutterErrorDetails details) {
    return Material(
      color: const Color(0xFF1E2937),
      child: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: SelectableText(
            'UI Error:\n${details.exception}\n\n${details.stack}',
            style: const TextStyle(color: Colors.redAccent, fontSize: 13),
          ),
        ),
      ),
    );
  };

  final uri = Uri.base;

  // ── Public Wishlist deep-link detection ──────────────────────────────────
  final isPublicWishlist = uri.path.contains('/wishlist/') ||
      (uri.pathSegments.isNotEmpty && uri.pathSegments.first == 'wishlist') ||
      uri.queryParameters.containsKey('wishlist');
  if (isPublicWishlist) {
    String token = uri.queryParameters['wishlist'] ?? '';
    if (token.isEmpty && uri.pathSegments.length >= 2 && uri.pathSegments.first == 'wishlist') {
      token = uri.pathSegments[1];
    }
    if (token.isEmpty && uri.path.contains('/wishlist/')) {
      token = uri.path.split('/wishlist/').last.split('?').first.split('#').first;
    }
    if (token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Public Wish List',
        debugShowCheckedModeBanner: false,
        home: PublicWishlistViewScreen(token: token),
      ));
      return;
    }
  }

  // ── Attorney portal deep-link detection ──────────────────────────────────
  // If the URL contains /attorney?uid=...&token=... we skip auth entirely and
  // render the read-only attorney portal instead of the normal app.
  final isAttorneyPortal = uri.path.contains('/attorney') ||
      (uri.queryParameters.containsKey('uid') &&
       uri.queryParameters.containsKey('token'));
  if (isAttorneyPortal) {
    final uid   = uri.queryParameters['uid'] ?? '';
    final token = uri.queryParameters['token'] ?? '';
    if (uid.isNotEmpty && token.isNotEmpty) {
      await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform,
      );
      runApp(MaterialApp(
        title: 'Numista.AI — Estate Report',
        debugShowCheckedModeBanner: false,
        home: AttorneyPortalScreen(uid: uid, token: token),
      ));
      return;
    }
  }
  // ── General Route deep-link detection (e.g., ?route=Review%20Hub) ────────────
  if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
    WelcomeScreen.pendingRoute = uri.queryParameters['route'];
  }

  // On Flutter web, Firebase.initializeApp() can silently hang forever if the
  // network is slow or a service worker interferes. We wrap it in a 12-second
  // timeout so runApp() is always called, even in the worst case.
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    ).timeout(const Duration(seconds: 12));
  } on TimeoutException {
    // Timed out — proceed anyway. The auth StreamBuilder may still resolve
    // once Firebase connects in the background.
    debugPrint('[Numista] Firebase.initializeApp() timed out — proceeding anyway.');
  } catch (e, stack) {
    // Hard failure — show a readable error screen instead of a blank page.
    runApp(MaterialApp(
      debugShowCheckedModeBanner: false,
      home: Scaffold(
        backgroundColor: const Color(0xFF0B1220),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 60),
              const Text('🔥 Firebase Init Failed',
                  style: TextStyle(
                      color: Colors.redAccent,
                      fontSize: 22,
                      fontWeight: FontWeight.bold)),
              const SizedBox(height: 16),
              Text(e.toString(),
                  style: const TextStyle(
                      color: Colors.orangeAccent, fontSize: 14)),
              const SizedBox(height: 24),
              Text(stack.toString(),
                  style: const TextStyle(
                      color: Colors.white54, fontSize: 11)),
            ],
          ),
        ),
      ),
    ));
    return;
  }

  runApp(const NumistaAIApp());
}

class NumistaAIApp extends StatefulWidget {
  const NumistaAIApp({super.key});

  @override
  State<NumistaAIApp> createState() => _NumistaAIAppState();
}

class _NumistaAIAppState extends State<NumistaAIApp> {
  /// Set to true after the user dismisses the welcome screen.
  /// Triggers a rebuild that bypasses the FutureBuilder check.
  bool _welcomeDone = false;

  /// Cached Future for WelcomeScreen.shouldShow().
  ///
  /// IMPORTANT: FutureBuilder resets to ConnectionState.waiting whenever its
  /// `future` argument changes.  Because the StreamBuilder fires 2-3 rebuilds
  /// on a single login (Firebase auth can emit the user object more than once),
  /// passing `WelcomeScreen.shouldShow()` directly creates a NEW Future every
  /// rebuild — the FutureBuilder never leaves ConnectionState.waiting, so the
  /// app is stuck on the gray loading spinner forever.
  ///
  /// Fix: create the Future once, cache it here, and reuse it for every
  /// FutureBuilder rebuild that belongs to the same sign-in session.
  /// Reset to null on sign-out so the next login gets a fresh check.
  Future<bool>? _shouldShowWelcome;

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: ThemeProvider.instance,
      builder: (context, _) {
        return MaterialApp(
          title: 'Numista.AI',
          debugShowCheckedModeBanner: false,
          themeMode: ThemeProvider.instance.themeMode,
          theme: ThemeData(
            brightness: Brightness.light,
            scaffoldBackgroundColor: const Color(0xFFF4F4F2), // Premium parchment/platinum-silver bg
            primaryColor: const Color(0xFF8C7355), // Antique bronze
            cardColor: const Color(0xFFFFFFFF),
            dividerColor: const Color(0xFFE2E8F0),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFF8C7355),
              brightness: Brightness.light,
              primary: const Color(0xFF8C7355),
              secondary: const Color(0xFFC9A227),
              surface: const Color(0xFFFFFFFF),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Colors.white,
              foregroundColor: Color(0xFF0F172A),
              elevation: 0,
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.light().textTheme).apply(
              bodyColor: const Color(0xFF0F172A),
              displayColor: const Color(0xFF0F172A),
            ),
          ),
          darkTheme: ThemeData(
            brightness: Brightness.dark,
            scaffoldBackgroundColor: const Color(0xFF0B1120), // Deep navy-black bg
            primaryColor: const Color(0xFFC9A227), // Metallic gold
            cardColor: const Color(0xFF1E2937), // Rich slate cards
            dividerColor: const Color(0xFF2D3143),
            colorScheme: ColorScheme.fromSeed(
              seedColor: const Color(0xFFC9A227),
              brightness: Brightness.dark,
              primary: const Color(0xFFC9A227),
              secondary: const Color(0xFFD4AF37),
              surface: const Color(0xFF1E2937),
              error: const Color(0xFFDC3545),
            ),
            fontFamily: 'sans-serif',
            appBarTheme: const AppBarTheme(
              backgroundColor: Color(0xFF1E2937),
              foregroundColor: Colors.white,
              elevation: 0,
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
              bodyColor: const Color(0xFFE8EAF0),
              displayColor: const Color(0xFFE8EAF0),
            ),
          ),
      // --- Auth Gate ---------------------------------------------------------
      // StreamBuilder on authStateChanges: shows LoginScreen until Firebase
      // confirms a signed-in user, then drops into the main app.
      home: StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          // Still waiting for Firebase to initialise — show branded splash
          if (snapshot.connectionState == ConnectionState.waiting) {
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

          // Signed in -> show welcome screen on first launch, then main app
          if (snapshot.hasData && snapshot.data != null) {
            // If user already dismissed the welcome screen this session,
            // go straight to the main app without re-checking SharedPrefs.
            if (_welcomeDone) {
              return const BaseLayout();
            }

            // Cache the Future so FutureBuilder doesn't reset to
            // ConnectionState.waiting on every StreamBuilder rebuild.
            // Firebase auth fires 2-3 events per login; without caching,
            // each rebuild swaps in a brand-new Future and the gray spinner
            // screen persists indefinitely.
            _shouldShowWelcome ??= WelcomeScreen.shouldShow();

            return FutureBuilder<bool>(
              future: _shouldShowWelcome,
              builder: (ctx, snap) {
                if (snap.connectionState == ConnectionState.waiting) {
                  // Show the same branded dark splash as the Firebase init
                  // screen so the user never sees a jarring gray flash while
                  // SharedPreferences reads the "show on startup" preference.
                  return Scaffold(
                    backgroundColor: const Color(0xFF0B1220),
                    body: Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Image.asset('assets/logo_owl.png', height: 80,
                              errorBuilder: (ctx, err, st) => const Icon(
                                    Icons.account_balance_rounded,
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
                final showWelcome = snap.data ?? false;
                if (showWelcome) {
                  return WelcomeScreen(
                    onDone: () {
                      // Trigger a rebuild -- the _welcomeDone flag bypasses the
                      // FutureBuilder and shows BaseLayout directly.
                      setState(() => _welcomeDone = true);
                    },
                  );
                }
                return const BaseLayout();
              },
            );
          }

          // User signed out — reset the cached future so next login is fresh.
          _shouldShowWelcome = null;
          _welcomeDone = false;

          // Not signed in -> show the login screen
          return const LoginScreen();
        },
      ),
    );
      },
    );
  }
}
