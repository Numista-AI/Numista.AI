import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../services/auth_service.dart';
import '../widgets/morgan_greeter.dart';

/// WelcomeScreen is the entry point called from main.dart.
/// It now delegates entirely to MorganGreeter for a rich, guided experience.
///
/// The [onDone] callback accepts an optional route string:
///   - non-null  → navigate to that BaseLayout route after dismissal
///   - null      → just enter the app on the Home Dashboard
class WelcomeScreen extends StatelessWidget {
  /// Called when Morgan routes the user somewhere (or they dismiss).
  /// The parent (main.dart) calls setState(_welcomeDone = true).
  final VoidCallback onDone;

  /// Optionally carry the chosen route up to BaseLayout.
  /// Set by the MorganGreeter tile tap, consumed in BaseLayout.initState.
  static String? pendingRoute;

  const WelcomeScreen({super.key, required this.onDone});

  static const String _prefKey = 'welcome_seen';

  /// Call this from main.dart / BaseLayout to check if the welcome screen
  /// should be shown. Returns true only on first launch after account creation.
  /// Returns false for existing users who already have coins in their collection.
  static Future<bool> shouldShow() async {
    final prefs = await SharedPreferences.getInstance();
    // Already dismissed in this browser/device
    if (prefs.getBool(_prefKey) ?? false) return false;

    // Check if user already has coins — if so, skip welcome and mark seen
    try {
      final snap = await FirebaseFirestore.instance
          .collection(AuthService.coinsPath)
          .limit(1)
          .get();
      if (snap.docs.isNotEmpty) {
        // Existing user — silently mark seen so it never shows again
        await prefs.setBool(_prefKey, true);
        return false;
      }
    } catch (_) {
      // If Firestore check fails, fall through and show welcome
    }

    return true;
  }

  static Future<void> markSeen() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefKey, true);
  }

  @override
  Widget build(BuildContext context) {
    // Delegate entirely to MorganGreeter.
    // When the user picks an action tile, we stash the route in pendingRoute
    // so BaseLayout.initState() can deep-link to it, then call onDone() to
    // dismiss this screen and enter the main app.
    return MorganGreeter(
      isFirstVisit: true,
      onAction: (route) {
        pendingRoute = route;   // consumed by BaseLayout
        onDone();               // triggers main.dart setState → BaseLayout
      },
    );
  }
}
