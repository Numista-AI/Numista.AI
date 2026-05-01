import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'firebase_options.dart';
import 'screens/base_layout.dart';
import 'screens/login_screen.dart';


Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
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

          // Signed in → show the main app
          if (snapshot.hasData && snapshot.data != null) {
            return const BaseLayout();
          }

          // Not signed in → show the login screen
          return const LoginScreen();
        },
      ),
    );
  }
}
