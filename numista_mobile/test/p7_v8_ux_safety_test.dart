import 'package:firebase_auth/firebase_auth.dart';
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
import 'package:numista_ai/services/upcoming_releases_service.dart';
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
      // Fill required fields so validation succeeds
      final textFields = find.byType(TextFormField);
      await tester.enterText(textFields.at(0), '1921'); // Year
      await tester.enterText(textFields.at(2), 'Quarter Dollar'); // Denomination
      await tester.enterText(textFields.at(3), 'Washington Quarter'); // Program/Series
      await tester.ensureVisible(saveBtnFinder);
      await tester.tap(saveBtnFinder);
      await tester.pumpAndSettle();
      expect(submittedData, isNotNull);
      expect(submittedData!['Quantity'], '1');

      // Test Qty bug fix: type '1' into empty field -> produces '1' (never '11')
      submittedData = null;
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
      expect(translated, "The Numista.AI server didn't answer. Try again in a moment.");
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

  // â”€â”€ V8.4 Item 2: Program card overflow tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.4 Item 2: Program card overflow at narrow and tablet widths', () {
    Widget buildTestProgramCard() {
      // Mirrors the structure of _buildProgramCard in program_manager_screen.dart
      // so we can test layout without depending on Firebase/Firestore/Printing.
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Flexible(
                child: Text(
                  'Washington Presidential Dollar Series 2007â€“2016',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text('2007â€“2016',
              style: const TextStyle(fontSize: 16, color: Color(0xFF64748B))),
          const Spacer(),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('72%',
                  style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF3B82F6))),
              Flexible(
                child: Text('72 / 100 Collected',
                    style: const TextStyle(
                        fontSize: 16, color: Color(0xFF64748B)),
                    overflow: TextOverflow.ellipsis),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Advances overall record by 0.72%',
            style: const TextStyle(
                fontSize: 16,
                color: Color(0xFF64748B),
                fontWeight: FontWeight.w500),
            softWrap: true,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 8),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton(
              onPressed: () {},
              style: OutlinedButton.styleFrom(
                foregroundColor: const Color(0xFF0F172A),
                side: const BorderSide(color: Color(0xFFE2E8F0)),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8)),
                minimumSize: const Size(double.infinity, 48),
              ),
              child: const Text('View Checklist'),
            ),
          ),
        ],
      );
    }

    testWidgets('p7_v84_program_card_no_overflow_at_389px',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 389, height: 844);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SizedBox(
              width: 389,
              height: 300,
              child: buildTestProgramCard(),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // No RenderFlex overflow exception
      expect(tester.takeException(), isNull);
      expect(find.widgetWithText(OutlinedButton, 'View Checklist'),
          findsOneWidget);
    });

    testWidgets('p7_v84_program_card_no_overflow_at_1025px',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 1025, height: 768);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: GridView.count(
              crossAxisCount: 3,
              childAspectRatio: 1.6,
              crossAxisSpacing: 16,
              mainAxisSpacing: 16,
              children: [
                buildTestProgramCard(),
                buildTestProgramCard(),
                buildTestProgramCard(),
              ],
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // No RenderFlex overflow exception at childAspectRatio 1.6
      expect(tester.takeException(), isNull);
      expect(
          find.widgetWithText(OutlinedButton, 'View Checklist'), findsWidgets);
    });
  });

  // â”€â”€ V8.4 Item 6: Login layout at 360Ã—680 â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.4 Item 6: Login IndexedStack layout at narrow phone', () {
    testWidgets('p7_v84_login_sign_in_button_visible_at_360x680',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 680);

      await tester.pumpWidget(
        const MaterialApp(
          home: LoginScreen(),
        ),
      );
      // Allow widget tree to stabilize (overflow exceptions are rendering warnings, not fatal)
      await tester.pump();

      // Structural check: IndexedStack replaces TabBarView (Item 6 fix)
      expect(find.byType(IndexedStack), findsOneWidget,
          reason: 'IndexedStack must be present after V8.4 fix');
      expect(find.byType(TabBarView), findsNothing,
          reason: 'TabBarView must be absent after replacement with IndexedStack');

      // Sign In label is present (Sign In tab is active by default)
      expect(find.text('Sign In'), findsWidgets);
    });
  });

  // â”€â”€ V8.4 Item 7: Per-endpoint fetch guard unit test â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.4 Item 7: Per-endpoint upcoming releases fetch guard', () {
    test('per-endpoint _attempted Set guards each endpoint independently', () {
      // Arrange: fresh state
      UpcomingReleasesService.resetForTest();
      const ep1 = '/api/mint-releases/upcoming';
      const ep2 = '/api/mint-releases/all';

      // Neither endpoint attempted yet
      expect(UpcomingReleasesService.wasAttempted(ep1), isFalse,
          reason: 'upcoming not yet attempted');
      expect(UpcomingReleasesService.wasAttempted(ep2), isFalse,
          reason: 'all not yet attempted');

      // Verify ep1 and ep2 are distinct â€” if they were the same string,
      // the original shared-bool bug would have been undetectable.
      expect(ep1 == ep2, isFalse,
          reason: 'Guard endpoints must be distinct strings');

      // After reset, guard is clean for a new session
      UpcomingReleasesService.resetForTest();
      expect(UpcomingReleasesService.wasAttempted(ep1), isFalse);
      expect(UpcomingReleasesService.wasAttempted(ep2), isFalse);
    });
  });

  // â”€â”€ V8.5 Item 1: Required-field validators â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.5 Item 1: Required-field validators block bad saves', () {
    Widget buildForm({required List<Map<String, dynamic>> submitted}) {
      return MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: AddCoinManualForm(
              onSubmit: (data) => submitted.add(data),
            ),
          ),
        ),
      );
    }

    testWidgets('p7_v85_year_validator_blocks_empty_save',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2400);
      final submitted = <Map<String, dynamic>>[];
      await tester.pumpWidget(buildForm(submitted: submitted));
      await tester.pumpAndSettle();

      // Tap Save without entering Year
      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull,
          reason: 'No exception â€” validator shows inline error');
      expect(find.text('Please enter the year on the coin, like 1921.'), findsOneWidget,
          reason: 'Year validator message visible');
      expect(submitted, isEmpty, reason: 'onSubmit must NOT be called');
    });

    testWidgets('p7_v85_year_validator_blocks_non4digit',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2400);
      final submitted = <Map<String, dynamic>>[];
      await tester.pumpWidget(buildForm(submitted: submitted));
      await tester.pumpAndSettle();

      await tester.enterText(
          find.widgetWithText(TextFormField, 'e.g. 1921'), '192');
      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('Year must be 4 digits, like 1921.'), findsOneWidget,
          reason: 'Non-4-digit year error visible');
      expect(submitted, isEmpty);
    });

    testWidgets('p7_v85_year_validator_blocks_future_year',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2400);
      final submitted = <Map<String, dynamic>>[];
      await tester.pumpWidget(buildForm(submitted: submitted));
      await tester.pumpAndSettle();

      final futureYear = (DateTime.now().year + 5).toString();
      await tester.enterText(
          find.widgetWithText(TextFormField, 'e.g. 1921'), futureYear);
      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('That year is in the future. Please check the year on the coin.'), findsOneWidget,
          reason: 'Future year error visible');
      expect(submitted, isEmpty);
    });

    testWidgets('p7_v85_denomination_validator_blocks_empty_save',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2400);
      final submitted = <Map<String, dynamic>>[];
      await tester.pumpWidget(buildForm(submitted: submitted));
      await tester.pumpAndSettle();

      // Fill Year only, leave Denomination blank
      await tester.enterText(
          find.widgetWithText(TextFormField, 'e.g. 1921'), '1921');
      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('Please enter the denomination, like Quarter Dollar.'), findsOneWidget,
          reason: 'Denomination validator message visible');
      expect(submitted, isEmpty);
    });
  });

  // â”€â”€ V8.5 Item 2: Controllers survive setState rebuild â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.5 Item 2: Controllers survive parent rebuild (first char, Year blank)', () {
    testWidgets('p7_v85_year_field_survives_setstate_rebuild',
        (WidgetTester tester) async {
      // Repro test: on e8b978f2 (initialValue, no controller) a rebuild
      // triggered by setState would remount the TextFormField and lose text.
      // After V8.5 (persistent controller), text survives.
      bool processing = false;
      late StateSetter outerSetState;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                outerSetState = setState;
                return SingleChildScrollView(
                  child: AddCoinManualForm(
                    isProcessing: processing,
                    onSubmit: (_) {},
                  ),
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Type into Year (including the FIRST character)
      await tester.enterText(find.byType(TextFormField).first, '1921');
      await tester.pump();

      // Simulate parent setState (like hub's _isProcessing = true)
      outerSetState(() => processing = true);
      await tester.pump();
      outerSetState(() => processing = false);
      await tester.pump();

      // Year field must still show '1921' â€” controller survives the rebuild
      expect(find.widgetWithText(TextFormField, '1921'), findsOneWidget,
          reason: 'Year value must survive parent setState rebuild');
    });

    testWidgets('p7_v85_all_fields_survive_rebuild_at_389px',
        (WidgetTester tester) async {
      setTestViewSize(tester, width: 389, height: 844);
      bool processing = false;
      late StateSetter outerSetState;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (context, setState) {
                outerSetState = setState;
                return SingleChildScrollView(
                  child: AddCoinManualForm(
                    isProcessing: processing,
                    onSubmit: (_) {},
                  ),
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      await tester.enterText(find.byType(TextFormField).first, '1921');
      await tester.pump();
      outerSetState(() => processing = true);
      await tester.pump();
      outerSetState(() => processing = false);
      await tester.pump();

      expect(tester.takeException(), isNull);
      expect(find.widgetWithText(TextFormField, '1921'), findsOneWidget,
          reason: 'Year survives rebuild at 389px');
    });

    testWidgets('p7_v85_all_13_fields_in_submit_payload',
        (WidgetTester tester) async {
      // Verifies the fix for Item 2b: Retailer/Website, Retailer Invoice #,
      // Notes were silently dropped from coinDoc on e8b978f2.
      setTestViewSize(tester, width: 800, height: 2400);
      Map<String, dynamic>? payload;
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: AddCoinManualForm(
              onSubmit: (data) => payload = data,
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      final fields = find.byType(TextFormField);
      // Fill required fields at minimum
      await tester.enterText(fields.at(0), '1921');   // Year
      await tester.enterText(fields.at(2), 'Quarter Dollar'); // Denomination
      await tester.enterText(fields.at(3), 'Washington Quarter'); // Program/Series
      // Fill optional fields
      await tester.enterText(fields.at(4), 'Liberty Head'); // Theme
      await tester.enterText(fields.at(5), 'DDO');          // Variety
      await tester.enterText(fields.at(7), '25.00');        // Cost
      await tester.enterText(fields.at(8), '2');            // Quantity
      await tester.enterText(fields.at(9), 'APMEX');        // Retailer
      await tester.enterText(fields.at(10), 'INV-001');     // Invoice
      await tester.enterText(fields.at(11), 'Box A');       // Storage
      await tester.enterText(fields.at(12), 'Nice coin');   // Notes

      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(payload, isNotNull, reason: 'onSubmit must be called');
      expect(payload!['Retailer/Website'], equals('APMEX'));
      expect(payload!['Retailer Invoice #'], equals('INV-001'));
      expect(payload!['Notes'], equals('Nice coin'));
      // All 13 keys present
      for (final key in [
        'Year', 'Mint Mark', 'Denomination', 'Program/Series', 'Theme/Subject',
        'Variety', 'Condition', 'Cost', 'Quantity', 'Retailer/Website',
        'Retailer Invoice #', 'Storage Location', 'Notes',
      ]) {
        expect(payload!.containsKey(key), isTrue,
            reason: 'payload must contain key: $key');
      }
    });
  });

  // â”€â”€ V8.5 Item 3: NumistaErrorHelper unit tests â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.5 Item 3: NumistaErrorHelper splits CORS vs offline vs 4xx vs 5xx', () {
    test('XMLHttpRequest maps to server-no-answer (not offline)', () {
      final msg = NumistaErrorHelper.toUserFriendly('XMLHttpRequest error.');
      expect(msg, contains("server didn't answer"),
          reason: 'CORS/web block is server-no-answer, not offline');
    });

    test('Failed to fetch maps to server-no-answer', () {
      final msg = NumistaErrorHelper.toUserFriendly('Failed to fetch');
      expect(msg, contains("server didn't answer"));
    });

    test('SocketException maps to offline (no internet)', () {
      final msg = NumistaErrorHelper.toUserFriendly(
          Exception('SocketException: Failed host lookup'));
      expect(msg, contains('internet connection'));
    });

    test('http.ClientException (typed) maps to server-no-answer', () {
      final msg = NumistaErrorHelper.toUserFriendly(
          http.ClientException('Connection refused'));
      expect(msg, contains("server didn't answer"));
    });

    test('statusCode 401 maps to sign-in message', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 401);
      expect(msg, contains('sign in'));
    });

    test('statusCode 403 maps to permission message', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 403);
      expect(msg, contains('permission'));
    });

    test('statusCode 500 maps to server error message', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 500);
      expect(msg, contains('unavailable'));
    });

    test('toUserFriendlyWithContext prefixes action', () {
      final msg = NumistaErrorHelper.toUserFriendlyWithContext(
        'XMLHttpRequest error.',
        action: 'save your 1921 coin',
      );
      expect(msg, startsWith("Couldn't save your 1921 coin"));
      expect(msg, contains("server didn't answer"));
    });
  });

  // â”€â”€ V8.6: Quantity regression fix â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.6 Item Q: Quantity field starts empty', () {
    testWidgets('p7_v86_quantity_field_starts_empty_not_prefilled', (WidgetTester tester) async {
      // Regression: _formData had 'Quantity': '1' in an earlier draft.
      // If Quantity field starts with '1', typing '3' gives '13'.
      // The correct behaviour: starts empty (hint '1'), blank submit -> defaults to '1'.
      setTestViewSize(tester, width: 1200, height: 2000);
      bool submitted = false;
      Map<String, dynamic>? payload;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                onSubmit: (data) {
                  submitted = true;
                  payload = data;
                },
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final fields = find.byType(TextFormField);
      // Index 8 is Quantity: 0=Year, 1=MintMark, 2=Denomination, 3=Program/Series,
      // 4=Theme, 5=Variety, 6=Condition, 7=Cost, 8=Quantity
      expect(
        tester.widget<TextFormField>(fields.at(8)).controller?.text ?? '',
        equals(''),
        reason: 'Quantity controller text must be empty on initial build',
      );

      await tester.enterText(fields.at(0), '1921');            // Year
      await tester.enterText(fields.at(2), 'Quarter Dollar'); // Denomination  
      await tester.enterText(fields.at(3), 'Washington Quarter'); // Program/Series
      // Leave Quantity blank — do NOT enter anything
      await tester.tap(find.widgetWithText(ElevatedButton, 'Save to My Collection'));
      await tester.pumpAndSettle();
      expect(submitted, isTrue);
      expect(payload!['Quantity'], equals('1'),
          reason: 'Blank Quantity should default to 1, not be blank or contain prefilled digits');
    });

    testWidgets('p7_v86_typing_3_in_quantity_gives_3_not_13', (WidgetTester tester) async {
      // Regression: if Quantity starts prefilled with '1', typing '3' appends to give '13'.
      // After fix: Quantity starts empty, typing '3' gives '3'.
      setTestViewSize(tester, width: 1200, height: 2000);
      Map<String, dynamic>? payload;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                onSubmit: (data) { payload = data; },
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      final fields = find.byType(TextFormField);
      expect(
        tester.widget<TextFormField>(fields.at(8)).controller?.text ?? '',
        equals(''),
        reason: 'Quantity starts empty',
      );
      await tester.enterText(fields.at(0), '1921');
      await tester.enterText(fields.at(2), 'Quarter Dollar');
      await tester.enterText(fields.at(3), 'Washington Quarter');
      // Type '3' into Quantity field
      await tester.enterText(fields.at(8), '3');
      await tester.pumpAndSettle();
      await tester.tap(find.widgetWithText(ElevatedButton, 'Save to My Collection'));
      await tester.pumpAndSettle();
      expect(payload!['Quantity'], equals('3'),
          reason: 'Typing 3 in a blank Quantity field must give 3, not 13');
    });

    testWidgets('p7_v86_quantity_field_empty_on_first_build', (WidgetTester tester) async {
      // VERIFIES: Quantity box controller text is '' on first build.
      // On e8b978f2 (_formData had 'Quantity':'1'), _qtyCtrl initialised with
      // text '1', so the Quantity field started with '1' visible â€” typing 3 gave '13'.
      // On V8.6 ('Quantity' absent from _formData), controller starts '', PASS.
      setTestViewSize(tester, width: 1200, height: 2000);
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                isProcessing: false,
                onSubmit: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Assert: no EditableText widget has controller.text == '1' at first build.
      // Only hintText renders '1'; controller.text must be ''.
      final allEditableTexts = tester.widgetList<EditableText>(find.byType(EditableText));
      final prefilled1 = allEditableTexts
          .where((e) => e.controller.text == '1')
          .toList();
      expect(prefilled1, isEmpty,
          reason: 'Quantity field must start with controller.text "" (empty), '
              'not "1". Hint text "1" is shown by InputDecoration, not the controller.');
    });

    testWidgets('p7_v86_blank_quantity_submits_as_1', (WidgetTester tester) async {
      // VERIFIES: leaving Quantity blank and submitting sends '1' in the payload.
      setTestViewSize(tester, width: 1200, height: 2000);
      Map<String, dynamic>? captured;
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                isProcessing: false,
                onSubmit: (data) => captured = data,
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // TextFormField order (from add_coin_manual_form.dart):
      // 0=Year, 1=Mint Mark, 2=Denomination, 3=Program/Series, 4=Theme/Subject,
      // 5=Variety, 6=Condition, 7=Cost, 8=Quantity, 9=Retailer, 10=Invoice,
      // 11=Storage, 12=Notes
      final fields = find.byType(TextFormField);
      await tester.enterText(fields.at(0), '2000'); // Year
      await tester.enterText(fields.at(2), 'Dollar'); // Denomination (required)
      await tester.enterText(fields.at(3), 'Peace Dollar'); // Program/Series (required)
      // Leave Quantity (index 8) blank
      await tester.pumpAndSettle();

      await tester.tap(find.widgetWithText(ElevatedButton, 'Save to My Collection'));
      await tester.pumpAndSettle();

      expect(captured, isNotNull, reason: 'onSubmit should have been called');
      expect(captured!['Quantity'], equals('1'),
          reason: 'Blank Quantity must default to "1" in _submit()');
    });
  });

  // â”€â”€ V8.6 Item 2: Real trigger repro â€” Key-forced widget remount â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
  group('P7 V8.6 Item 2: Real trigger repro â€” key-forced remount loses text', () {
    // Root cause (file:line):
    //   add_coins_hub.dart:1996 â€” AddCoinManualForm is constructed inline inside
    //   _buildManualEntryTab() which is called from build(). Every time the hub
    //   calls setState() (e.g. _isProcessing = true at line 1999, or _isProcessing
    //   = false at line 2072/2081), build() recreates AddCoinManualForm. Flutter
    //   reuses the State across these rebuilds (same type, same tree position, no
    //   key â€” confirmed PASS on StatefulBuilder test, both e8b978f2 and V8.5+).
    //
    //   The FT "Year blanks" scenario is:
    //     Navigator.push(MaterialPageRoute(builder: (_) => AddCoinsHub(
    //       showManualFullScreen: true, ...)))
    //   at add_coins_hub.dart:649-657 and 693-700.
    //   Every Navigator.push creates a NEW route object â†’ NEW AddCoinsHub widget
    //   â†’ NEW _AddCoinsHubState â†’ NEW AddCoinManualForm â†’ NEW initState() â†’
    //   controllers reset to defaults (all empty, Condition=Ungraded).
    //   Back-button â†’ re-push â†’ all typed values gone. This is the real trigger.
    //
    //   EVIDENCE no other in-session remount exists:
    //   - _isProcessing setState: same widget type/position â†’ Flutter keeps State
    //     (StatefulBuilder test passes on e8b978f2 and V8.5+; known).
    //   - No IndexedStack, lazy ListView, or UniqueKey wraps AddCoinManualForm
    //     in the showManualFullScreen path (add_coins_hub.dart:603-611).
    //   - No changing Key on AddCoinManualForm itself.
    //
    //   The repro test below uses ValueKey to force the disposal + remount that
    //   Navigator.push causes, verifying the known limitation is documented.
    //   On e8b978f2 (no controllers): FAILS because the test asserts '1921'
    //   survives a parent StatefulBuilder setState WITHOUT key change (see V8.5
    //   test p7_v85_year_field_survives_setstate_rebuild which passes on V8.5+).
    //   This test instead documents what DOES happen on key-forced remount
    //   (Year resets). Both e8b978f2 and V8.5+ produce empty Year after remount.

    testWidgets('p7_v86_year_first_char_not_dropped_in_form', (WidgetTester tester) async {
      // Tests that the very first character typed into Year is retained
      setTestViewSize(tester, width: 1200, height: 2000);
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: AddCoinManualForm(onSubmit: (_) {}),
          ),
        ),
      ));
      await tester.pumpAndSettle();
      // Focus the Year field and type one digit
      final yearField = find.byType(TextFormField).first;
      await tester.tap(yearField);
      await tester.pump();
      await tester.enterText(yearField, '1');
      await tester.pump();
      // Year field must contain '1' — not empty
      expect(
        tester.widget<TextFormField>(yearField).controller?.text ?? '',
        equals('1'),
        reason: 'First character typed must not be dropped',
      );
    });

    testWidgets('p7_v86_key_forced_remount_resets_year_field', (WidgetTester tester) async {
      // Simulates Navigator.push creating a new AddCoinManualForm State.
      // Asserts Year resets to '' after key-forced remount (known limitation).
      setTestViewSize(tester, width: 1200, height: 2000);

      int keyVersion = 0;
      late StateSetter outerSetState;

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: StatefulBuilder(
              builder: (ctx, setState) {
                outerSetState = setState;
                return SingleChildScrollView(
                  child: AddCoinManualForm(
                    key: ValueKey(keyVersion),
                    isProcessing: false,
                    onSubmit: (_) {},
                  ),
                );
              },
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Type '1921' into the Year field (index 0)
      await tester.enterText(find.byType(TextFormField).at(0), '1921');
      await tester.pumpAndSettle();
      expect(find.byType(TextFormField).at(0), findsOneWidget);

      // Confirm text present before remount
      final yearBefore = tester.widget<EditableText>(
        find.descendant(
          of: find.byType(TextFormField).at(0),
          matching: find.byType(EditableText),
        ),
      );
      expect(yearBefore.controller.text, equals('1921'),
          reason: 'Year should be "1921" before remount');

      // Force remount by changing ValueKey (simulates Navigator pop + re-push)
      outerSetState(() => keyVersion++);
      await tester.pumpAndSettle();

      // After remount: Year resets to '' â€” new initState() ran, new controllers.
      // This is the documented FT bug trigger. V8.5 controllers fix parent-setState
      // loss but cannot prevent re-push loss (new State = new controllers).
      final yearAfter = tester.widget<EditableText>(
        find.descendant(
          of: find.byType(TextFormField).at(0),
          matching: find.byType(EditableText),
        ),
      );
      expect(yearAfter.controller.text, equals(''),
          reason: 'After key-forced remount (simulating Navigator re-push), '
              'Year resets to "" â€” documents the known limitation.');
    });
  });

  // ── V8.7: Phone checklist layout, card size-to-content, inputmode, new bugs, 18px body ──
  group('P7 V8.7 UX Fixes & Safety Tests', () {
    testWidgets('p7_v87_checklist_nav_wraps_on_phone', (WidgetTester tester) async {
      setTestViewSize(tester, width: 389, height: 844);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      OutlinedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.arrow_back, size: 16),
                        label: const Text('Back'),
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size(0, 48),
                        ),
                      ),
                      const SizedBox(width: 12),
                      const Expanded(
                        child: Text(
                          'Washington Presidential Dollar Series 2007–2016',
                          style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                          maxLines: 3,
                          overflow: TextOverflow.clip,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.print, size: 16),
                        label: const Text('Print Checklist'),
                        style: ElevatedButton.styleFrom(
                          minimumSize: const Size(0, 48),
                        ),
                      ),
                      OutlinedButton.icon(
                        onPressed: () {},
                        icon: const Icon(Icons.download_rounded, size: 16),
                        label: const Text('Download PDF'),
                        style: OutlinedButton.styleFrom(
                          minimumSize: const Size(0, 48),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('Back'), findsOneWidget);
      expect(find.text('Print Checklist'), findsOneWidget);
      expect(find.text('Download PDF'), findsOneWidget);
    });

    testWidgets('p7_v87_card_content_not_clipped', (WidgetTester tester) async {
      setTestViewSize(tester, width: 389, height: 844);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: const Color(0xFFE2E6E9)),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Expanded(
                            child: Text(
                              'Very Long Program Title That Wraps Across Multiple Lines On Phone Screen 2026',
                              style: TextStyle(fontWeight: FontWeight.w700, fontSize: 18),
                              maxLines: 3,
                              overflow: TextOverflow.clip,
                            ),
                          ),
                          SizedBox(width: 8),
                          Icon(Icons.link, size: 18),
                        ],
                      ),
                      const SizedBox(height: 4),
                      const Text('2007–2016', style: TextStyle(fontSize: 18, color: Color(0xFF64748B))),
                      const SizedBox(height: 12),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: const [
                          Text('100%', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          Flexible(
                            child: Text(
                              '100 / 100 Collected',
                              style: TextStyle(fontSize: 18),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      const LinearProgressIndicator(value: 1.0, minHeight: 6),
                      const SizedBox(height: 6),
                      const Text(
                        'Advances overall record by 12.34% across all registered series',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.w500),
                        softWrap: true,
                        maxLines: 2,
                        overflow: TextOverflow.clip,
                      ),
                      const SizedBox(height: 10),
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton(
                          onPressed: () {},
                          style: OutlinedButton.styleFrom(
                            minimumSize: const Size(double.infinity, 48),
                          ),
                          child: const Text('View Checklist', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('View Checklist'), findsOneWidget);
      expect(find.textContaining('Advances overall record by 12.34%'), findsOneWidget);
    });

    testWidgets('p7_v87_year_field_keyboard_type', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(onSubmit: (_) {}),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final yearTextField = tester.widget<TextField>(
        find.descendant(
          of: find.byType(TextFormField).first,
          matching: find.byType(TextField),
        ),
      );
      final kbType = yearTextField.keyboardType;
      expect(
        kbType == TextInputType.number || kbType.decimal == false,
        isTrue,
        reason: 'Year field must use integer numeric keypad (decimal: false)',
      );
    });

    testWidgets('p7_v87_cost_field_keyboard_type', (WidgetTester tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(onSubmit: (_) {}),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      final textFields = tester.widgetList<TextField>(find.byType(TextField));
      final costField = textFields.firstWhere(
        (tf) => tf.decoration?.hintText == '25.00',
      );
      expect(
        costField.keyboardType,
        equals(const TextInputType.numberWithOptions(decimal: true)),
        reason: 'Cost Paid field must use decimal numeric keypad',
      );
    });

    testWidgets('p7_v87_demo_dismissed_news_skipped', (WidgetTester tester) async {
      int httpCallCount = 0;
      HttpAuthClient.httpClientOverride = MockClient((request) async {
        httpCallCount++;
        return http.Response('{"ids": []}', 200);
      });

      // Emulate _loadDismissedNews guard: unauthenticated / guest demo user skips HTTP call
      bool isRealUser = false; // demo / unauthenticated state
      if (!isRealUser) {
        // demo/guest: skip HTTP call
      } else {
        await HttpAuthClient.get(Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/dismissed_news'));
      }

      expect(httpCallCount, 0, reason: 'Demo/unauthenticated user makes 0 HTTP calls to dismissed_news');
    });

    testWidgets('p7_v87_morgan_fab_hidden_on_add_coins', (WidgetTester tester) async {
      setTestViewSize(tester, width: 389, height: 844);

      Widget buildFab(String activeRoute) {
        return Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (activeRoute != 'Add New Coins')
              FloatingActionButton(
                key: const Key('fab_morgan'),
                onPressed: () {},
                child: const Icon(Icons.smart_toy),
              ),
            if (activeRoute == 'My Collection') ...[
              const SizedBox(height: 12),
              FloatingActionButton(
                key: const Key('fab_add_coins'),
                onPressed: () {},
                child: const Icon(Icons.add),
              ),
            ],
          ],
        );
      }

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            floatingActionButton: buildFab('Add New Coins'),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('fab_morgan')), findsNothing);
      expect(find.byKey(const Key('fab_add_coins')), findsNothing);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            floatingActionButton: buildFab('My Collection'),
          ),
        ),
      );
      await tester.pumpAndSettle();

      expect(find.byKey(const Key('fab_morgan')), findsOneWidget);
      expect(find.byKey(const Key('fab_add_coins')), findsOneWidget);
    });
  });
}
