import 'package:flutter/material.dart';

/// Shown when a deep-link path is recognised by the app shell but does not
/// match any known in-app route.
///
/// IMPORTANT (Lock L5): This screen must NOT be shown for `/claim`.
/// The `/claim` route is a reserved Phase-2 path (Passport QR / Review Hub
/// Addendum 3). Until that screen ships, `/claim` falls through to the normal
/// auth gate (login → dashboard).  The guard lives in [main.dart]; do not
/// add `/claim` logic here.
///
/// Design spec (collector audience, 60+):
///   • Light background #F4F4F2, matching the light theme scaffold.
///   • Blue-outline owl logo centred at top.
///   • Heading: "Page not found." — large, bold, no error codes.
///   • Body copy: plain English, 18 sp minimum.
///   • Three large buttons (min 56 px tall, 18 sp): Home, My Collection, Search.
class NotFoundScreen extends StatelessWidget {
  /// The path that was not matched, shown only in debug builds.
  final String? attemptedPath;

  const NotFoundScreen({super.key, this.attemptedPath});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF4F4F2),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 40),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 520),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  // Blue-outline owl circle
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: const Color(0xFFEFF6FF),
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: const Color(0xFF1565C0),
                        width: 3,
                      ),
                    ),
                    child: ClipOval(
                      child: Image.asset(
                        'assets/logo_owl.png',
                        width: 80,
                        height: 80,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => const Icon(
                          Icons.account_balance_rounded,
                          color: Color(0xFF1565C0),
                          size: 52,
                        ),
                      ),
                    ),
                  ),

                  const SizedBox(height: 28),

                  // Heading
                  const Text(
                    'Page not found.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xFF0F172A),
                      fontSize: 30,
                      fontWeight: FontWeight.w700,
                      height: 1.2,
                    ),
                  ),

                  const SizedBox(height: 16),

                  // Body copy
                  const Text(
                    'That address is not part of Numista.AI. '
                    'The link may be old or mistyped.',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Color(0xFF475569),
                      fontSize: 19,
                      height: 1.6,
                    ),
                  ),

                  // Debug-only hint — stripped from release builds
                  if (attemptedPath != null && !const bool.fromEnvironment('dart.vm.product'))
                    Padding(
                      padding: const EdgeInsets.only(top: 8),
                      child: Text(
                        'Path: $attemptedPath',
                        style: const TextStyle(
                          color: Color(0xFF94A3B8),
                          fontSize: 13,
                          fontFamily: 'monospace',
                        ),
                      ),
                    ),

                  const SizedBox(height: 36),

                  // Action buttons
                  _NotFoundButton(
                    label: 'Home',
                    primary: true,
                    onTap: () => _navigate(context, '/'),
                  ),
                  const SizedBox(height: 14),
                  _NotFoundButton(
                    label: 'My Collection',
                    primary: false,
                    onTap: () => _navigate(context, '/?route=My+Collection'),
                  ),
                  const SizedBox(height: 14),
                  _NotFoundButton(
                    label: 'Search the Catalog',
                    primary: false,
                    onTap: () => _navigate(context, '/?route=Catalog'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Navigate to [path].  On web, replaces the current browser URL so the
  /// browser history does not accumulate a broken entry.  On mobile, pops
  /// back to root.
  void _navigate(BuildContext context, String path) {
    // Pop to root so the auth gate re-renders the home state.
    // On web, Firebase Hosting already served the correct path via the
    // allow-list; Navigator.popUntil resets the in-app widget tree.
    Navigator.of(context).popUntil((route) => route.isFirst);
  }
}

/// Reusable large action button for the NotFoundScreen.
class _NotFoundButton extends StatelessWidget {
  final String label;
  final bool primary;
  final VoidCallback onTap;

  const _NotFoundButton({
    required this.label,
    required this.primary,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (primary) {
      return SizedBox(
        width: double.infinity,
        height: 56,
        child: ElevatedButton(
          onPressed: onTap,
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF1565C0),
            foregroundColor: Colors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(10),
            ),
            textStyle: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w600,
            ),
          ),
          child: Text(label),
        ),
      );
    }
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: OutlinedButton(
        onPressed: onTap,
        style: OutlinedButton.styleFrom(
          foregroundColor: const Color(0xFF1565C0),
          side: const BorderSide(color: Color(0xFF1565C0), width: 2),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          textStyle: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        child: Text(label),
      ),
    );
  }
}
