import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart';
import 'screens/base_layout.dart';

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
        scaffoldBackgroundColor: const Color(0xFFF0F2F6), // Streamlit light background
        primaryColor: const Color(0xFFF63366), // Streamlit red accent
        fontFamily: 'sans-serif', // Simulating standard Streamlit font
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.white,
          foregroundColor: Color(0xFF31333F),
          elevation: 0,
        ),
        textTheme: const TextTheme(
          bodyMedium: TextStyle(color: Color(0xFF31333F)),
          bodyLarge: TextStyle(color: Color(0xFF31333F)),
        ),
      ),
      home: const BaseLayout(),
    );
  }
}
