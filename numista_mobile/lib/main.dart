import 'dart:async';
import 'package:flutter/foundation.dart' show kIsWeb, kDebugMode, debugPrint;
import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/welcome_screen.dart';
import 'screens/attorney_portal_screen.dart';
import 'screens/not_found_screen.dart';
import 'screens/public_wishlist_view_screen.dart';
import 'services/theme_provider.dart';
import 'widgets/morgan_feedback_drawer.dart';
import 'services/guest_seed_service.dart';
import 'widgets/auth_gate.dart';
import 'constants.dart';  // ITEM 10: kApiBaseUrl startup guard
import 'package:google_fonts/google_fonts.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Enable Flutter accessibility semantics on web so that Playwright
  // text= / aria-label locators can find flt-semantics nodes.
  // SemanticsBinding.instance is a no-op on non-web platforms.
  if (kIsWeb) {
    SemanticsBinding.instance.ensureSemantics();
  }

  ErrorWidget.builder = (FlutterErrorDetails details) {
    // Log full details to console in debug only — never to UI
    if (kDebugMode) {
      debugPrint('UI Error: ${details.exception}\n${details.stack}');
      FlutterError.dumpErrorToConsole(details);
    }
    return const _ErrorFallbackWidget();
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
  // ── Unknown-path guard (Soft-404 fix) ─────────────────────────────────────
  // Firebase Hosting now returns a real HTTP 404 for garbage URLs.
  // This guard handles the rare case where a valid-looking but unknown path
  // is navigated to *inside* the Flutter app (e.g. a stale bookmark that was
  // once real).
  //
  // Known real paths served by this app shell:
  //   /               — root / home
  //   /wishlist/**    — public wishlist deep links
  //   /attorney_portal — attorney/estate portal (caught above)
  //   /claim          — Phase-2 reservation (L5: routes to home, NOT NotFoundScreen)
  //   /claim/**       — Phase-2 reservation (same)
  //
  // Any other non-empty path not in this set shows NotFoundScreen.
  // Hash-fragment URLs (e.g. /#/claim?...) have uri.path == '/' — they pass
  // through to the normal app flow correctly.
  final path = uri.path;
  final normalizedPath = (path.endsWith('/') && path.length > 1)
      ? path.substring(0, path.length - 1)
      : path;

  final isKnownPath = path.isEmpty ||
      path == '/' ||
      path == '/index.html' ||
      normalizedPath == '/about' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/features' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/login' ||
      normalizedPath == '/signup' ||
      normalizedPath == '/reset-password' ||
      normalizedPath == '/demo' ||
      normalizedPath == '/app' ||
      normalizedPath == '/blog' ||
      path.startsWith('/wishlist') ||
      path.startsWith('/attorney_portal') ||
      path.startsWith('/attorney') ||
      path.startsWith('/claim') || // L5: reserved — falls through to home, not NotFoundScreen
      path.startsWith('/privacy') ||
      path.startsWith('/terms') ||
      path.startsWith('/add_coins') ||
      path.startsWith('/scraper_dashboard') ||
      path.startsWith('/api/');

  if (!isKnownPath) {
    runApp(MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      home: NotFoundScreen(attemptedPath: path),
    ));
    return;
  }

  // Synchronously parse Front Door URL routes
  bool isPendingDemo = false;
  String? pendingPublicRoute;
  int initialAuthTab = 0;
  bool showResetForm = false;

  if (normalizedPath == '/demo') {
    isPendingDemo = true;
  } else if (normalizedPath == '/about' ||
      normalizedPath == '/features' ||
      normalizedPath == '/pricing' ||
      normalizedPath == '/faq' ||
      normalizedPath == '/blog') {
    pendingPublicRoute = normalizedPath == '/blog' ? '/about' : normalizedPath;
  } else if (normalizedPath == '/login') {
    initialAuthTab = 0;
  } else if (normalizedPath == '/signup') {
    initialAuthTab = 1;
  } else if (normalizedPath == '/reset-password') {
    initialAuthTab = 0;
    showResetForm = true;
  }

  // ── General Route deep-link detection (e.g., ?route=Review%20Hub) ────────────
  if (uri.queryParameters.containsKey('route') && uri.queryParameters['route']!.isNotEmpty) {
    WelcomeScreen.pendingRoute = uri.queryParameters['route'];
  }

  // ITEM 10: kApiBaseUrl guard — prevents silent empty-URL HTTP calls.
  // This is a compile-time const so it will never be empty in production,
  // but this guard protects against misconfigured forks or env-var overrides.
  if (kApiBaseUrl.trim().isEmpty) {
    // Throw synchronously so Flutter's error reporter catches it before
    // any HTTP request can fire against an empty URL.
    throw StateError(
      '[Numista] kApiBaseUrl is empty. '
      'Set the backend URL in lib/constants.dart before building.',
    );
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

  runApp(NumistaAIApp(
    isPendingDemo: isPendingDemo,
    pendingPublicRoute: pendingPublicRoute,
    initialAuthTab: initialAuthTab,
    showResetForm: showResetForm,
  ));
}

class NumistaAIApp extends StatefulWidget {
  final bool isPendingDemo;
  final String? pendingPublicRoute;
  final int initialAuthTab;
  final bool showResetForm;

  const NumistaAIApp({
    super.key,
    this.isPendingDemo = false,
    this.pendingPublicRoute,
    this.initialAuthTab = 0,
    this.showResetForm = false,
  });

  @override
  State<NumistaAIApp> createState() => _NumistaAIAppState();
}

class _NumistaAIAppState extends State<NumistaAIApp> {
  late bool _isPendingDemo;
  late String? _pendingPublicRoute;

  @override
  void initState() {
    super.initState();
    _isPendingDemo = widget.isPendingDemo;
    _pendingPublicRoute = widget.pendingPublicRoute;
    if (_isPendingDemo) {
      GuestSeedService.activateBrowseDemo();
    }
  }

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
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFC9A227);
                }
                return const Color(0xFF94A3B8);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFFE2E8F0)),
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
            scrollbarTheme: ScrollbarThemeData(
              thumbVisibility: WidgetStateProperty.all(true),
              trackVisibility: WidgetStateProperty.all(true),
              thickness: WidgetStateProperty.all(12.0),
              radius: const Radius.circular(6.0),
              thumbColor: WidgetStateProperty.resolveWith((states) {
                if (states.contains(WidgetState.hovered)) {
                  return const Color(0xFFFFD700);
                }
                return const Color(0xFF475569);
              }),
              trackColor: WidgetStateProperty.all(const Color(0xFF1E293B)),
            ),
            textTheme: GoogleFonts.interTextTheme(ThemeData.dark().textTheme).apply(
              bodyColor: const Color(0xFFE8EAF0),
              displayColor: const Color(0xFFE8EAF0),
            ),
          ),
          // ITEM 3: Wrap every route in the text scaler + Morgan feedback drawer.
          // ThemeProvider.textScaleFactor is 1.0 / 1.3 / 1.6 per user setting.
          // MediaQuery.withClampedTextScaling clamps between minScaleFactor and
          // maxScaleFactor — we pin both to the chosen value so OS accessibility
          // settings do not override the in-app control on desktop web.
          builder: (context, child) {
            final scaleFactor = ThemeProvider.instance.textScaleFactor;
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: TextScaler.linear(scaleFactor),
              ),
              child: FeedbackDrawerOverlay(child: child ?? const SizedBox.shrink()),
            );
          },
      // --- Auth Gate ---------------------------------------------------------
      // StreamBuilder on authStateChanges: handles unauthenticated states,
      // public routes, demo mode, and transitions to BaseLayout on login.
      home: AuthGate(
        isDemo: _isPendingDemo,
        publicRoute: _pendingPublicRoute,
        initialAuthTab: widget.initialAuthTab,
        showResetForm: widget.showResetForm,
      ),
    );
      },
    );
  }
}

/// Fallback widget shown when ErrorWidget.builder is triggered.
/// Plain Material widget — no Navigator, no platform-specific APIs.
/// Report Issue: displays copyable support email address.
class _ErrorFallbackWidget extends StatelessWidget {
  const _ErrorFallbackWidget();

  @override
  Widget build(BuildContext context) {
    return Material(
      color: const Color(0xFF1E2937),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 480),
          child: Padding(
            padding: const EdgeInsets.all(32),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.error_outline,
                    color: Color(0xFFC9A227), size: 48),
                const SizedBox(height: 16),
                const Text(
                  'Something went wrong loading this screen.',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFE8EAF0),
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  'Please refresh the page. If this keeps happening, '
                  'contact support at the address below.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Color(0xFF8B92B4), fontSize: 14),
                ),
                const SizedBox(height: 6),
                const SelectableText(
                  'support@numista.ai',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Color(0xFFC9A227),
                    fontSize: 14,
                    decoration: TextDecoration.underline,
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
