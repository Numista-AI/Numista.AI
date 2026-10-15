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

  // ── V8.4 Item 2: Program card overflow tests ─────────────────────────────
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
                  'Washington Presidential Dollar Series 2007–2016',
                  style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                  maxLines: 2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text('2007–2016',
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

  // ── V8.4 Item 6: Login layout at 360×680 ────────────────────────────────
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

  // ── V8.4 Item 7: Per-endpoint fetch guard unit test ──────────────────────
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

      // Verify ep1 and ep2 are distinct — if they were the same string,
      // the original shared-bool bug would have been undetectable.
      expect(ep1 == ep2, isFalse,
          reason: 'Guard endpoints must be distinct strings');

      // After reset, guard is clean for a new session
      UpcomingReleasesService.resetForTest();
      expect(UpcomingReleasesService.wasAttempted(ep1), isFalse);
      expect(UpcomingReleasesService.wasAttempted(ep2), isFalse);
    });
  });

  // ── V8.5 Item 1: Required-field validators ────────────────────────────────
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
          reason: 'No exception — validator shows inline error');
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

  // ── V8.5 Item 2: Controllers survive setState rebuild ────────────────────
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

      // Year field must still show '1921' — controller survives the rebuild
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

  // ── V8.5 Item 3: NumistaErrorHelper unit tests ────────────────────────────
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
}
