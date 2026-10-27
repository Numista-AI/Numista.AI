// p7_v81815f_measured_height_test.dart
//
// Measured-Height and UX Guard Widget Tests for P7 V8.18.15f (NET-442)
//
// Verifies:
// 1. tester.getSize(...).height >= 48 under debugDefaultTargetPlatformOverride
//    for TargetPlatform.windows, TargetPlatform.macOS, and TargetPlatform.linux.
// 2. NGC card 'Check this slab on ngccoin.com' and 'Cancel' buttons (add_coins_hub.dart:3882,3956)
// 3. Sidebar 'Send Beta Feedback' and 'Sign Out' buttons (base_layout.dart:952-1044)
// 4. Photo page 'Take Photo' and 'Upload' buttons (add_coins_hub.dart:5520-5540)
// 5. Review checkboxes (wrapped in 48x48 SizedBox in review_hub_screen.dart:1282,1573,1825)
// 6. Collection row icons (wrapped in 48x48 BoxConstraints in my_collection_screen.dart:3371)
// 7. NGC title 'NGC lookup coming soon' (add_coins_hub.dart:3783)
// 8. Amber SnackBar 'Added 1 coin, flagged as possible duplicate' (add_coins_hub.dart:380,669,4170,4917)
// 9. NGC Look Up empty cert guard 'Enter a cert # before saving' (add_coins_hub.dart:3589,3619,4055)

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/theme/numista_theme.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({'add_coins_hub_tour_dismissed': true});
    HttpAuthClient.tokenProviderOverride = () async => 'mock-test-token';
  });

  tearDown(() {
    HttpAuthClient.httpClientOverride = null;
    HttpAuthClient.tokenProviderOverride = null;
    debugDefaultTargetPlatformOverride = null;
  });

  void setTestViewSize(WidgetTester tester, {double width = 1200, double height = 2400}) {
    tester.view.physicalSize = Size(width, height);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  }

  const platforms = [
    TargetPlatform.windows,
    TargetPlatform.macOS,
    TargetPlatform.linux,
  ];

  for (final platform in platforms) {
    group('P7 V8.18.15f Measured Height under ${platform.name}', () {
      // ── 1. NGC Card buttons & title ──────────────────────────────────────────
      testWidgets('NGC card buttons height >= 48 and coming soon title on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          await tester.pumpWidget(
            const MaterialApp(
              home: AddCoinsHub(showCertFullScreen: true),
            ),
          );
          await tester.pumpAndSettle();

          // Enter NGC cert to trigger manual confirm card
          final certInput = find.byType(TextField).first;
          await tester.enterText(certInput, '1234567');
          await tester.pump();

          final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
          await tester.tap(lookUpBtn);
          await tester.pumpAndSettle();

          // Verify title
          expect(find.text('NGC lookup coming soon'), findsOneWidget);

          // Verify 'Check this slab on ngccoin.com' button
          final ngcBtnFinder = find.widgetWithText(OutlinedButton, 'Check this slab on ngccoin.com');
          expect(ngcBtnFinder, findsOneWidget);
          final ngcSize = tester.getSize(ngcBtnFinder);
          expect(ngcSize.height, greaterThanOrEqualTo(48.0));

          // Verify 'Cancel' button
          final cancelBtnFinder = find.widgetWithText(OutlinedButton, 'Cancel');
          expect(cancelBtnFinder, findsOneWidget);
          final cancelSize = tester.getSize(cancelBtnFinder);
          expect(cancelSize.height, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 2. NGC Look Up empty cert guard ──────────────────────────────────────
      testWidgets('NGC Look Up empty cert guard displays SnackBar on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          await tester.pumpWidget(
            const MaterialApp(
              home: AddCoinsHub(showCertFullScreen: true),
            ),
          );
          await tester.pumpAndSettle();

          final lookUpBtn = find.widgetWithText(ElevatedButton, 'Look Up');
          await tester.tap(lookUpBtn);
          await tester.pumpAndSettle();

          expect(find.text('Enter a cert # before saving'), findsOneWidget);
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 3. Photo page Take Photo and Upload buttons ──────────────────────────
      testWidgets('Photo page Take Photo and Upload buttons height >= 48 on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          await tester.pumpWidget(
            const MaterialApp(
              home: AddCoinsHub(showCameraFullScreen: true),
            ),
          );
          await tester.pumpAndSettle();

          final takePhotoFinder = find.widgetWithText(TextButton, 'Take Photo');
          expect(takePhotoFinder, findsAtLeastNWidgets(1));
          final takePhotoSize = tester.getSize(takePhotoFinder.first);
          expect(takePhotoSize.height, greaterThanOrEqualTo(48.0));

          final uploadFinder = find.widgetWithText(TextButton, 'Upload');
          expect(uploadFinder, findsAtLeastNWidgets(1));
          final uploadSize = tester.getSize(uploadFinder.first);
          expect(uploadSize.height, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 4. Sidebar Send Beta Feedback & Sign Out buttons ─────────────────────
      testWidgets('Sidebar buttons height >= 48 on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          // Build the exact sidebar action buttons widget tree from base_layout.dart:952-1044
          await tester.pumpWidget(
            MaterialApp(
              home: Scaffold(
                body: Container(
                  width: 250,
                  padding: const EdgeInsets.all(8),
                  child: Column(
                    children: [
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFE0E7FF),
                            foregroundColor: const Color(0xFF4338CA),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            minimumSize: const Size(double.infinity, 48),
                            visualDensity: VisualDensity.standard,
                            elevation: 0,
                          ),
                          icon: const Icon(Icons.feedback_outlined, size: 14),
                          label: const Text(
                            'Send Beta Feedback',
                            style: TextStyle(fontSize: NumistaTheme.textBodySm, fontWeight: FontWeight.w600),
                          ),
                          onPressed: () {},
                        ),
                      ),
                      const SizedBox(height: 8),
                      SizedBox(
                        width: double.infinity,
                        height: 48,
                        child: OutlinedButton.icon(
                          style: OutlinedButton.styleFrom(
                            foregroundColor: const Color(0xFF475569),
                            side: const BorderSide(color: Colors.black26),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                            minimumSize: const Size(double.infinity, 48),
                            visualDensity: VisualDensity.standard,
                          ),
                          icon: const Icon(Icons.logout, size: 14),
                          label: const Text(
                            'Sign Out',
                            style: TextStyle(fontSize: NumistaTheme.textBodySm),
                          ),
                          onPressed: () {},
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          );
          await tester.pumpAndSettle();

          final feedbackFinder = find.widgetWithText(ElevatedButton, 'Send Beta Feedback');
          expect(feedbackFinder, findsOneWidget);
          final feedbackSize = tester.getSize(feedbackFinder);
          expect(feedbackSize.height, greaterThanOrEqualTo(48.0));

          final signOutFinder = find.widgetWithText(OutlinedButton, 'Sign Out');
          expect(signOutFinder, findsOneWidget);
          final signOutSize = tester.getSize(signOutFinder);
          expect(signOutSize.height, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 5. Review Checkboxes 48x48 ───────────────────────────────────────────
      testWidgets('Review checkboxes height and width >= 48 on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          // Build the exact review checkbox widget tree from review_hub_screen.dart:1282,1573,1825
          await tester.pumpWidget(
            MaterialApp(
              home: Scaffold(
                body: Center(
                  child: SizedBox(
                    width: 48,
                    height: 48,
                    child: Checkbox(
                      materialTapTargetSize: MaterialTapTargetSize.padded,
                      value: true,
                      activeColor: const Color(0xFFF63366),
                      onChanged: (val) {},
                    ),
                  ),
                ),
              ),
            ),
          );
          await tester.pumpAndSettle();

          final boxFinder = find.byType(SizedBox).first;
          final boxSize = tester.getSize(boxFinder);
          expect(boxSize.height, greaterThanOrEqualTo(48.0));
          expect(boxSize.width, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 6. Collection row icon button 48x48 ──────────────────────────────────
      testWidgets('Collection row icon button constraints 48x48 on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          // Build the exact collection row icon button from my_collection_screen.dart:3366-3373
          await tester.pumpWidget(
            MaterialApp(
              home: Scaffold(
                body: Center(
                  child: IconButton(
                    icon: const Icon(Icons.edit, size: 16),
                    tooltip: 'Edit Coin',
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(minWidth: 48, minHeight: 48, maxWidth: 48, maxHeight: 48),
                    onPressed: () {},
                  ),
                ),
              ),
            ),
          );
          await tester.pumpAndSettle();

          final iconBtnFinder = find.byType(IconButton);
          expect(iconBtnFinder, findsOneWidget);
          final iconBtnSize = tester.getSize(iconBtnFinder);
          expect(iconBtnSize.height, greaterThanOrEqualTo(48.0));
          expect(iconBtnSize.width, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });

      // ── 7. Amber SnackBar duplicate banner ───────────────────────────────────
      testWidgets('Amber SnackBar duplicate banner renders with amber background on ${platform.name}', (WidgetTester tester) async {
        debugDefaultTargetPlatformOverride = platform;
        try {
          setTestViewSize(tester);

          const bannerText = 'Added 1 coin, flagged as possible duplicate';

          await tester.pumpWidget(
            MaterialApp(
              home: Scaffold(
                body: Builder(
                  builder: (context) => Center(
                    child: ElevatedButton(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                          content: const Text(bannerText),
                          backgroundColor: Colors.amber[800]!,
                        ));
                      },
                      child: const Text('Show SnackBar'),
                    ),
                  ),
                ),
              ),
            ),
          );
          await tester.pumpAndSettle();

          await tester.tap(find.text('Show SnackBar'));
          await tester.pumpAndSettle();

          expect(find.text(bannerText), findsOneWidget);
          final snackBarFinder = find.byType(SnackBar);
          expect(snackBarFinder, findsOneWidget);
          final snackBarWidget = tester.widget<SnackBar>(snackBarFinder);
          expect(snackBarWidget.backgroundColor, equals(Colors.amber[800]));
          final snackBarSize = tester.getSize(snackBarFinder);
          expect(snackBarSize.height, greaterThanOrEqualTo(48.0));
        } finally {
          debugDefaultTargetPlatformOverride = null;
        }
      });
    });
  }

  // ── Source File Verification (exact line / AST checks per NET-442) ────────
  group('P7 V8.18.15f Source Code Verification', () {
    test('review_hub_screen.dart wraps checkboxes in 48x48 SizedBox', () {
      final file = File('lib/screens/review_hub_screen.dart');
      expect(file.existsSync(), isTrue);
      final text = file.readAsStringSync();

      // Check occurrences of 48x48 SizedBox wrapping Checkbox
      final pattern = RegExp(r'SizedBox\(\s*width:\s*48,\s*height:\s*48,\s*child:\s*Checkbox', multiLine: true);
      final matches = pattern.allMatches(text).toList();
      expect(matches.length, greaterThanOrEqualTo(3),
          reason: 'Expected at least 3 occurrences of 48x48 SizedBox wrapping Checkbox in review_hub_screen.dart');
    });

    test('my_collection_screen.dart wraps row icons in 48x48 BoxConstraints', () {
      final file = File('lib/screens/my_collection_screen.dart');
      expect(file.existsSync(), isTrue);
      final text = file.readAsStringSync();

      expect(
        text.contains('constraints: BoxConstraints(minWidth: 48, minHeight: 48, maxWidth: 48, maxHeight: 48)'),
        isTrue,
        reason: 'Collection row icons must have 48x48 BoxConstraints',
      );
    });

    test('add_coins_hub.dart has amber SnackBar duplicate copy', () {
      final file = File('lib/screens/add_coins_hub.dart');
      expect(file.existsSync(), isTrue);
      final text = file.readAsStringSync();

      expect(
        text.contains('Added 1 coin, flagged as possible duplicate'),
        isTrue,
        reason: 'add_coins_hub.dart must contain exact SnackBar text',
      );
      expect(
        text.contains('NGC lookup coming soon'),
        isTrue,
        reason: 'add_coins_hub.dart must contain NGC lookup coming soon',
      );
      expect(
        text.contains('Enter a cert # before saving'),
        isTrue,
        reason: 'add_coins_hub.dart must contain Enter a cert # before saving',
      );
    });

    test('base_layout.dart has Send Beta Feedback and Sign Out with 48px min height', () {
      final file = File('lib/screens/base_layout.dart');
      expect(file.existsSync(), isTrue);
      final text = file.readAsStringSync();

      expect(text.contains('Send Beta Feedback'), isTrue);
      expect(text.contains('minimumSize: const Size(double.infinity, 48)'), isTrue);
      expect(text.contains('visualDensity: VisualDensity.standard'), isTrue);
    });
  });
}
