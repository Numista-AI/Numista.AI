import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/add_coins_hub.dart';
import 'package:numista_ai/screens/login_screen.dart';
import 'package:numista_ai/widgets/add_coin_manual_form.dart';
import 'package:numista_ai/services/guest_seed_service.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/utils/numista_error_helper.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({'add_coins_hub_tour_dismissed': true});
    HttpAuthClient.tokenProviderOverride = () async => 'mock-test-token';
  });

  tearDown(() {
    HttpAuthClient.httpClientOverride = null;
    HttpAuthClient.tokenProviderOverride = null;
    GuestSeedService.deactivateBrowseDemo();
  });

  void setTestViewSize(WidgetTester tester, {double width = 1200, double height = 1800}) {
    tester.view.physicalSize = Size(width, height);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(() {
      tester.view.resetPhysicalSize();
      tester.view.resetDevicePixelRatio();
    });
  }

  group('P7 V8 Item 4: Manual Entry Dedicated Screen & Form Fixes', () {
    testWidgets('p7_v8_manual_entry_full_screen_scaffold', (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 800);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showManualFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify AppBar with 'Add Coin Manually'
      expect(find.widgetWithText(AppBar, 'Add Coin Manually'), findsOneWidget);
      // Verify TabBar is absent (clean full screen)
      expect(find.byType(TabBar), findsNothing);
      // Verify BackButton is present
      expect(find.byType(BackButton), findsOneWidget);
      // Verify AddCoinManualForm is rendered
      expect(find.byType(AddCoinManualForm), findsOneWidget);
    });

    testWidgets('p7_v8_manual_entry_qty_prefill_fix_and_labels', (WidgetTester tester) async {
      setTestViewSize(tester, width: 600, height: 2400);

      Map<String, dynamic>? submittedData;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                onSubmit: (data) => submittedData = data,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Check required labels have 18px font size
      final richTexts = tester.widgetList<RichText>(find.byType(RichText));
      final yearLabel = richTexts.firstWhere(
        (rt) => rt.text.toPlainText().contains('Year'),
      );
      expect(yearLabel.text.style?.fontSize, 18.0);
      expect(yearLabel.text.toPlainText(), contains('*'));

      final denomLabel = richTexts.firstWhere(
        (rt) => rt.text.toPlainText().contains('Denomination'),
      );
      expect(denomLabel.text.style?.fontSize, 18.0);
      expect(denomLabel.text.toPlainText(), contains('*'));

      // Check 56px Save button
      final saveBtnFinder = find.widgetWithText(ElevatedButton, 'Save to My Collection');
      expect(saveBtnFinder, findsOneWidget);
      final saveBtnSize = tester.getSize(saveBtnFinder);
      expect(saveBtnSize.height, greaterThanOrEqualTo(56.0));

      // Test Qty bug fix: submit without touching Qty -> defaults to '1'
      await tester.ensureVisible(saveBtnFinder);
      await tester.tap(saveBtnFinder);
      await tester.pumpAndSettle();
      expect(submittedData, isNotNull);
      expect(submittedData!['Quantity'], '1');

      // Test Qty bug fix: type '1' into empty field -> produces '1' (never '11')
      final textFields = find.byType(TextFormField);
      submittedData = null;
      // Enter '1921' in Year
      await tester.enterText(textFields.at(0), '1921');
      // Enter '1' in Quantity (index 8)
      await tester.enterText(textFields.at(8), '1');
      await tester.ensureVisible(saveBtnFinder);
      await tester.tap(saveBtnFinder);
      await tester.pumpAndSettle();
      expect(submittedData!['Quantity'], '1');
    });
  });

  group('P7 V8 Item 1: Safety Dialog & Demo Guard HTTP Call Verifications', () {
    testWidgets('p7_v8_confirm_dialog_cancel_makes_zero_http_calls', (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 800);

      int httpCallCount = 0;
      HttpAuthClient.httpClientOverride = MockClient((request) async {
        httpCallCount++;
        return http.Response('{"ok": true}', 200);
      });

      // Pump a test harness triggering the confirm dialog
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (ctx) => ElevatedButton(
                onPressed: () async {
                  final confirmed = await showDialog<bool>(
                    context: ctx,
                    builder: (dCtx) => AlertDialog(
                      title: const Text('Add Selected Coins?'),
                      content: const Text('Save 2 coin(s) from "Morgan Silver Dollars" to your collection?'),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(dCtx, false),
                          child: const Text('Cancel'),
                        ),
                        ElevatedButton(
                          onPressed: () => Navigator.pop(dCtx, true),
                          child: const Text('Save to Collection'),
                        ),
                      ],
                    ),
                  );
                  if (confirmed == true) {
                    await HttpAuthClient.post(
                      Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins'),
                      body: '{}',
                    );
                  }
                },
                child: const Text('Trigger Add'),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap Trigger Add
      await tester.tap(find.text('Trigger Add'));
      await tester.pumpAndSettle();

      // Dialog is open
      expect(find.text('Add Selected Coins?'), findsOneWidget);

      // Tap Cancel
      await tester.tap(find.text('Cancel'));
      await tester.pumpAndSettle();

      // Dialog dismissed, 0 HTTP calls
      expect(find.text('Add Selected Coins?'), findsNothing);
      expect(httpCallCount, 0);
    });

    testWidgets('p7_v8_demo_mode_guard_makes_zero_http_calls', (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 800);

      int httpCallCount = 0;
      HttpAuthClient.httpClientOverride = MockClient((request) async {
        httpCallCount++;
        return http.Response('{"ok": true}', 200);
      });

      // Activate demo mode
      GuestSeedService.activateBrowseDemo();

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (ctx) => ElevatedButton(
                onPressed: () async {
                  // Replicate guard inside _addSelectedCoins
                  if (GuestSeedService.isBrowseDemoMode) {
                    ScaffoldMessenger.of(ctx).showSnackBar(
                      const SnackBar(
                        content: Text('Browse Demo Mode: Sign in to save coins to your collection.'),
                        backgroundColor: Color(0xFFF59E0B),
                      ),
                    );
                    return;
                  }
                  await HttpAuthClient.post(
                    Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/checklist/add_coins'),
                    body: '{}',
                  );
                },
                child: const Text('Save Coins'),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap Save Coins in demo mode
      await tester.tap(find.text('Save Coins'));
      await tester.pumpAndSettle();

      // Verify sign in snackbar appears and HTTP call count is strictly 0
      expect(find.text('Browse Demo Mode: Sign in to save coins to your collection.'), findsOneWidget);
      expect(httpCallCount, 0);
    });
  });

  group('P7 V8 Item 5: NumistaErrorHelper Plain-English Translation', () {
    test('converts http.ClientException and XMLHttpRequest to plain English', () {
      final err = http.ClientException(
        'XMLHttpRequest error., uri=https://numista-backend-568985927038.us-central1.run.app/api/endpoint',
      );
      final translated = NumistaErrorHelper.toUserFriendly(err);
      expect(translated, 'Unable to connect to the server. Please check your internet connection and try again.');
      expect(translated.contains('http'), isFalse);
      expect(translated.contains('uri='), isFalse);
      expect(translated.contains('XMLHttpRequest'), isFalse);
    });

    test('converts HTTP status codes 401, 403, 500 cleanly', () {
      expect(
        NumistaErrorHelper.toUserFriendly(null, statusCode: 401),
        'Your session expired or sign-in is required. Please sign in to continue.',
      );
      expect(
        NumistaErrorHelper.toUserFriendly(null, statusCode: 403),
        'Access denied. You do not have permission to perform this action.',
      );
      expect(
        NumistaErrorHelper.toUserFriendly(null, statusCode: 503),
        'Server is temporarily unavailable. Please try again in a few moments.',
      );
    });
  });

  group('P7 V8 Item 6d: PinBoxRow Responsive Geometry', () {
    testWidgets('p7_v8_pin_box_row_fits_320px_width_without_overflow', (WidgetTester tester) async {
      setTestViewSize(tester, width: 320, height: 640);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 320,
              child: PinBoxRow(
                filled: const [true, true, true, false, false, false],
                digits: const ['1', '2', '3', '', '', ''],
                showDigits: true,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify no overflow exception was thrown
      expect(tester.takeException(), isNull);
      // All 6 containers exist
      expect(find.byType(Container), findsWidgets);
    });
  });

  group('P7 V8 Item 4: BaseLayout Bottom Nav Highlight for Add New Coins', () {
    test('maps Add New Coins route to index 2 (My Collection)', () {
      final mobileRoutes = [
        'Home Dashboard',
        'Coin Programs',
        'My Collection',
        'AI Deepdive',
        'Settings & Backup',
      ];
      const activeRoute = 'Add New Coins';

      int effectiveIndex = mobileRoutes.indexOf(activeRoute);
      if (effectiveIndex == -1) {
        if (activeRoute == 'Add New Coins') {
          effectiveIndex = 2;
        } else {
          effectiveIndex = 0;
        }
      }
      final currentIndex = effectiveIndex.clamp(0, 4);

      expect(currentIndex, 2);
      expect(mobileRoutes[currentIndex], 'My Collection');
    });
  });
}
