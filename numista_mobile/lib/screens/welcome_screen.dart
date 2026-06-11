import 'package:flutter/material.dart';
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

  /// Returns true whenever Morgan should greet the user on startup.
  ///
  /// Default: true for every user on every login.
  /// Users can opt out via Morgan settings → "Don't greet me on startup".
  /// This replaces the old "only show on first visit / empty collection" logic.
  static Future<bool> shouldShow() => MorganGreeter.shouldShow();

  static Future<void> markSeen() => MorganGreeter.markSeen();

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
