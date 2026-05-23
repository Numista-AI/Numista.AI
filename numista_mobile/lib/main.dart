import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_options.dart';
import 'screens/base_layout.dart';
import 'screens/login_screen.dart';
import 'screens/welcome_screen.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // ── Diagnostic wrapper ─────────────────────────────────────────────────────
  // Catches any crash before runApp() so a blank screen shows the real error.
  // Remove this try/catch once startup issues are resolved.
  try {
    await Firebase.initializeApp(
        options: DefaultFirebaseOptions.currentPlatform);
  } catch (e, stack) {
    runApp(MaterialApp(
      home: Scaffold(
        backgroundColor: const Color(0xFF1A1A2E),
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
                  style: const TextStyle(color: Colors.orangeAccent, fontSize: 14)),
              const SizedBox(height: 24),
              Text(stack.toString(),
                  style: const TextStyle(color: Colors.white54, fontSize: 11)),
            ],
          ),
        ),
      ),
    ));
    return;
  }

  runApp(const NumistaAIApp());
}

class NumistaAIApp extends StatelessWidget {
  const NumistaAIApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Numista.AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF0F2F6),
        primaryColor: const Color(0xFF1565C0),  // Blue — matches new login screen
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
      // ─── Auth Gate ───────────────────────────────────────────────────────
      // StreamBuilder on authStateChanges: shows LoginScreen until Firebase
      // confirms a signed-in user, then drops into the main app.
      home: StreamBuilder<User?>(
        stream: FirebaseAuth.instance.authStateChanges(),
        builder: (context, snapshot) {
          // Still waiting for Firebase to initialise
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Scaffold(
              backgroundColor: Color(0xFFF0F2F6),
              body: Center(
                child: CircularProgressIndicator(
                  color: Color(0xFF1565C0),
                  strokeWidth: 3,
                ),
              ),
            );
          }

          // Signed in -> show welcome screen on first launch, then main app
          if (snapshot.hasData && snapshot.data != null) {
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
                      // Replace the welcome screen with the main app
                      Navigator.of(ctx).pushReplacement(
                        MaterialPageRoute(builder: (_) => const BaseLayout()),
                      );
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
