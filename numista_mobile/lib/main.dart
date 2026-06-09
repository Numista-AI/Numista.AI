import 'dart:async';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_options.dart';
import 'screens/base_layout.dart';
import 'screens/login_screen.dart';
import 'screens/welcome_screen.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ── Firebase init with timeout ─────────────────────────────────────────────
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

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF0F2F6),
        primaryColor: const Color(0xFF1565C0),  // Blue -- matches new login screen
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF1565C0),
          brightness: Brightness.light,
        ),
        fontFamily: 'sans-serif',
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF0F172A),
          elevation: 0,
        ),
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFF0F172A)),
          bodyLarge:  TextStyle(color: Color(0xFF0F172A)),
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

            return FutureBuilder<bool>(
              future: WelcomeScreen.shouldShow(),
              builder: (ctx, snap) {
                if (snap.connectionState == ConnectionState.waiting) {
                  return const Scaffold(
                    backgroundColor: Color(0xFFF0F2F6),
                    body: Center(child: CircularProgressIndicator(
                        color: Color(0xFF1565C0), strokeWidth: 3)),
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

          // Not signed in -> show the login screen
          return const LoginScreen();
        },
      ),
    );
  }
}
