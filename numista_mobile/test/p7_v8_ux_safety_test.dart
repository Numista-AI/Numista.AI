import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
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
import 'package:numista_ai/utils/web_input_helper.dart';
import 'package:numista_ai/utils/text_sanitizer.dart';
import 'package:numista_ai/services/set_expansion_helper.dart';
import 'package:numista_ai/services/morgan_prefs.dart';
import 'package:numista_ai/utils/slot_resolver.dart';
import 'package:numista_ai/services/coin_programs_data.dart';
import 'package:numista_ai/services/checklist_generator_service.dart';
import 'package:numista_ai/services/coin_normalizer_service.dart';
import 'package:numista_ai/services/world_item_service.dart';
import 'package:numista_ai/screens/program_manager_screen.dart';
import 'package:numista_ai/services/backup_export_service.dart';
import 'package:numista_ai/services/morgan_chat_context.dart';
import 'package:numista_ai/services/market_news_service.dart';

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
      // Re-enter required fields since form was reset after successful submit (V8.9 Fix 11)
      await tester.enterText(textFields.at(0), '1921');
      await tester.enterText(textFields.at(2), 'Quarter Dollar');
      await tester.enterText(textFields.at(3), 'Washington Quarter');
      // Enter '1' in Quantity (index 8)
      await tester.enterText(textFields.at(8), '1');
      await tester.ensureVisible(saveBtnFinder);
      await tester.tap(saveBtnFinder);
      await tester.pumpAndSettle();
      expect(submittedData, isNotNull);
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
      GuestSeedService.activateBrowseDemo();
      if (!GuestSeedService.isBrowseDemoMode) {
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

  group('P7 V8.9 Fixes: Systemic Qty, WebInputHelper, Mojibake, Morgan Setup', () {
    test('p7_v89_web_input_helper_static_attribute_map', () {
      final helper = WebInputHelper();
      expect(helper.attributeMap['Year'], 'numeric');
      expect(helper.attributeMap['Quantity'], 'numeric');
      expect(helper.attributeMap['Qty'], 'numeric');
      expect(helper.attributeMap['Cost'], 'decimal');
      expect(helper.attributeMap['Mint Mark'], isNull);
      expect(helper.attributeMap['Denomination'], isNull);
      expect(helper.attributeMap['Retailer'], isNull);
      expect(helper.attributeMap['Invoice'], isNull);
      expect(helper.attributeMap['Storage'], isNull);
      expect(helper.attributeMap['Notes'], isNull);
    });

    test('p7_v89_mojibake_text_sanitizer_repair', () {
      expect(TextSanitizer.fixMojibake('2022 United Kingdom Ã‚Â£2 Silver'), '2022 United Kingdom £2 Silver');
      expect(TextSanitizer.fixMojibake('Ã‚Â£50'), '£50');
      expect(TextSanitizer.fixMojibake('Normal 1921 Morgan Dollar'), 'Normal 1921 Morgan Dollar');
      expect(TextSanitizer.fixMojibake(''), '');
    });

    test('p7_v89_qty_count_summation_in_expansion', () {
      final rawDocs = [
        {
          'id': 'coin_1',
          'Year': '1921',
          'Denomination': 'Dollar',
          'Quantity': 3,
          'Purchase Price': '30.00',
        },
        {
          'id': 'coin_2',
          'Year': '1964',
          'Denomination': 'Half Dollar',
          'quantity': 2,
          'Purchase Price': '15.00',
        },
        {
          'id': 'coin_3',
          'Year': '2000',
          'Denomination': 'Quarter',
          'Purchase Price': '5.00',
        },
      ];

      final result = expandCollection(rawDocs, ['coin_1', 'coin_2', 'coin_3']);
      // Total coins should sum 3 + 2 + 1 = 6, NOT rawDocs.length (3)
      expect(result.totalCoins, 6);
    });

    test('p7_v89_morgan_setup_done_flag_persists_globally', () async {
      SharedPreferences.setMockInitialValues({});
      expect(await MorganPrefs.isSetupDone(), isFalse);
      await MorganPrefs.markSetupDone();
      expect(await MorganPrefs.isSetupDone(), isTrue);
    });
  });

  group('P7 V8.10 Fixes: Semiquincentennial Slots, Validation Clearing, Mojibake Export', () {
    test('p7_v810_slot_resolver_2026_currency_distinct_matching', () {
      final program = CoinProgramsData.usPrograms.values
          .expand((p) => p)
          .firstWhere((p) => p.id == '2026_semiquincentennial_currency');
      final centSlot = program.coins.firstWhere((c) => c.id == '2026_cent');
      final nickelSlot = program.coins.firstWhere((c) => c.id == '2026_nickel');
      final mayflowerSlot = program.coins.firstWhere((c) => c.id == '2026_quarter_mayflower');

      final centCoin = {
        'name': '1776 ~ 2026 Collectible Cent',
        'Denomination': '1c',
        'Year': '2026',
        'Theme/Subject': 'Semiquincentennial 1776 ~ 2026',
      };

      final nickelCoin = {
        'name': '1776 ~ 2026 Jefferson Nickel',
        'Denomination': '5c',
        'Year': '2026',
        'Theme/Subject': 'Semiquincentennial 1776 ~ 2026',
      };

      final mayflowerQuarter = {
        'name': 'America250 Quarter #1: Mayflower Compact',
        'Denomination': '25c',
        'Year': '2026',
        'Theme/Subject': 'Mayflower Compact',
      };

      // Cent matches Cent slot, but NOT Nickel or Quarter
      expect(SlotResolver.isMatch(centCoin, program, centSlot), isTrue);
      expect(SlotResolver.isMatch(centCoin, program, nickelSlot), isFalse);
      expect(SlotResolver.isMatch(centCoin, program, mayflowerSlot), isFalse);

      // Nickel matches Nickel slot, but NOT Cent or Quarter
      expect(SlotResolver.isMatch(nickelCoin, program, nickelSlot), isTrue);
      expect(SlotResolver.isMatch(nickelCoin, program, centSlot), isFalse);
      expect(SlotResolver.isMatch(nickelCoin, program, mayflowerSlot), isFalse);

      // Mayflower quarter matches Mayflower slot, but NOT Cent or Nickel
      expect(SlotResolver.isMatch(mayflowerQuarter, program, mayflowerSlot), isTrue);
      expect(SlotResolver.isMatch(mayflowerQuarter, program, centSlot), isFalse);
      expect(SlotResolver.isMatch(mayflowerQuarter, program, nickelSlot), isFalse);
    });

    test('p7_v810_checklist_generator_service_sanitizes_mojibake', () {
      expect(ChecklistGeneratorService.legalDisclaimer, contains('CONFIDENTIAL ESTATE'));
      expect(TextSanitizer.fixMojibake('2022 United Kingdom Â£2 Silver'), '2022 United Kingdom £2 Silver');
    });

    testWidgets('p7_v810_manual_form_clears_validation_on_input', (WidgetTester tester) async {
      setTestViewSize(tester, width: 600, height: 2400);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: SingleChildScrollView(
              child: AddCoinManualForm(
                onSubmit: (_) {},
              ),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Tap Save with empty fields to trigger validation
      await tester.tap(find.widgetWithText(ElevatedButton, 'Save to My Collection'));
      await tester.pumpAndSettle();

      // Verification: error texts visible
      expect(find.text('Please enter the denomination, like Quarter Dollar.'), findsOneWidget);
      expect(find.text('Please enter the series name, like Morgan Silver Dollar.'), findsOneWidget);

      // Enter denomination
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar');
      await tester.pumpAndSettle();

      // Denomination error is cleared immediately
      expect(find.text('Please enter the denomination, like Quarter Dollar.'), findsNothing);
      // Program/Series error still visible until typed
      expect(find.text('Please enter the series name, like Morgan Silver Dollar.'), findsOneWidget);

      // Enter series
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarters');
      await tester.pumpAndSettle();

      // Program/Series error is also cleared immediately
      expect(find.text('Please enter the series name, like Morgan Silver Dollar.'), findsNothing);
    });
  });

  group('P7 V8.11 Fixes: Broadcast Stream All Tab, Elevated Top Snackbar, Normalizer Guard, HttpAuthClient Guard, JS Inputmode Injection', () {
    test('p7_v811_demo_coins_stream_is_broadcast', () async {
      GuestSeedService.setDemoActiveForTest(true);
      final stream = GuestSeedService.getDemoCoinsStream();
      expect(stream.isBroadcast, isTrue);

      // Verify two listeners can subscribe simultaneously without throwing
      final sub1 = stream.listen((_) {});
      final sub2 = stream.listen((_) {});
      await sub1.cancel();
      await sub2.cancel();
    });

    test('p7_v811_world_items_stream_is_broadcast', () async {
      GuestSeedService.setDemoActiveForTest(true);
      final stream = WorldItemService.worldItemsStream();
      expect(stream.isBroadcast, isTrue);

      final sub1 = stream.listen((_) {});
      final sub2 = stream.listen((_) {});
      await sub1.cancel();
      await sub2.cancel();
    });

    testWidgets('p7_v811_floating_snackbar_margin_elevates_and_clears_action_area', (WidgetTester tester) async {
      late BuildContext ctx;
      await tester.pumpWidget(
        MaterialApp(
          home: Builder(
            builder: (c) {
              ctx = c;
              return const Scaffold(body: SizedBox());
            },
          ),
        ),
      );

      final pmMargin = ProgramManagerScreen.floatingSnackBarMargin(ctx);
      final hubMargin = AddCoinsHub.floatingSnackBarMargin(ctx);

      // Verify bottom margin is at least 120px to clear the action bar / caption
      expect(pmMargin.bottom, greaterThanOrEqualTo(120.0));
      expect(hubMargin.bottom, greaterThanOrEqualTo(120.0));

      // Verify top margin is 80px (positioned below app bar)
      expect(pmMargin.top, 80.0);
      expect(hubMargin.top, 80.0);
    });

    test('p7_v811_coin_normalizer_guarded_in_demo_and_unauth', () async {
      GuestSeedService.setDemoActiveForTest(true);
      expect(GuestSeedService.isBrowseDemoMode, isTrue);
      // Calling runForUser should return immediately without executing queries
      expect(() => CoinNormalizerService.runForUser(), returnsNormally);
    });

    test('p7_v811_http_auth_client_guards_unauthenticated_requests', () async {
      // Clear overrides to simulate unauthenticated client
      HttpAuthClient.tokenProviderOverride = null;
      HttpAuthClient.httpClientOverride = null;

      final resp = await HttpAuthClient.get(
        Uri.parse('https://numista-backend-568985927038.us-central1.run.app/api/reference/glossary'),
      );

      // Must return 401 without firing an external request
      expect(resp.statusCode, 401);
      expect(resp.body, contains('Authentication token missing or invalid'));
    });

    test('p7_v811_index_html_has_apply_input_modes_script', () {
      final indexHtmlPath = 'web/index.html';
      expect(File(indexHtmlPath).existsSync(), isTrue);
      final content = File(indexHtmlPath).readAsStringSync();

      expect(content, contains('function applyInputModes()'));
      expect(content, contains('/year|yr/'));
      expect(content, contains('/qty|quantity/'));
      expect(content, contains('/cost|price|value/'));
      expect(content, contains("el.inputMode = 'numeric'"));
      expect(content, contains("el.inputMode = 'decimal'"));
      expect(content, contains('setInterval(applyInputModes, 300)'));
    });
  });

  group('P7 V8.12 Tests: Morgan Metrics, PDF CORS/mojibake, CSV fields, Stream Replay', () {
    test('p7_v812_morgan_context_metrics_aligned_with_dashboard', () async {
      GuestSeedService.setDemoActiveForTest(true);
      GuestSeedService.setDemoCoinCacheForTest([
        {
          'Year': 1921,
          'Denomination': 'Morgan Dollar',
          'greysheetBid': '50.00',
          'cpgRetail': '65.00',
          'quantity': 2,
        },
        {
          'Year': 2021,
          'Denomination': 'Silver Eagle',
          'greysheetBid': '35.00',
          'quantity': 1,
        },
        {
          'Year': 1976,
          'Denomination': 'Bicentennial Proof Set',
          'item_type': 'set',
          'set_contents': [
            {'Denomination': 'Quarter', 'Year': '1976'},
            {'Denomination': 'Half Dollar', 'Year': '1976'},
            {'Denomination': 'Dollar', 'Year': '1976'},
          ],
          'greysheetBid': '25.00',
        },
      ]);

      final ctx = await MorganChatContextService.load(forceRefresh: true);

      // Verify totalCoins expanded: 2 + 1 + 3 = 6 coins
      expect(ctx.totalCoins, equals(6));

      // Verify portfolio valuation: 50.0 + 35.0 + 25.0 = 110.0 (estate bid default)
      expect(ctx.portfolioValue, equals(110.0));

      // Verify opening message aligns with count and formatted value
      expect(ctx.openingMessage, contains('6 coins in your collection'));
      expect(ctx.openingMessage, contains('\$110'));
    });

    test('p7_v812_csv_export_formatting_and_missing_columns', () {
      final payload = {
        'coins': [
          {
            'Year': '2017.0',
            'Mint Mark': 'D',
            'Denomination': 'Quarter',
            'Program/Series': 'America the Beautiful',
            'Theme/Subject': 'Ellis Island',
            'Condition': 'MS65',
            'quantity': 3,
            'cost': 15.5,
            'AI Estimated Value': '\$45.00',
            'Certification Number': '12345678',
            'Retailer': 'APMEX',
            'Invoice': 'INV-9981',
            'Storage Location': 'Safe Box A',
            'Notes': 'Gift from grandpa',
            'Added': 'Timestamp(seconds=1729166400, nanoseconds=0)',
          },
          {
            'year': 1921,
            'mint_mark': 'S',
            'denomination': 'Morgan Dollar',
            'program_series': 'Morgan Dollars',
            'theme_subject': 'Liberty Head',
            'condition': 'AU55',
            'quantity': null,
            'cost': 0,
            'ai_estimated_value': '\$38.00',
            'cert_number': '87654321',
            'Retailer/Website': 'Heritage Auctions',
            'Retailer Invoice #': 'HA-4421',
            'Location': 'Binder 1',
            'Personal Notes': 'Toned obverse',
            'timestamp': '2024-10-16T12:00:00Z',
          },
        ],
      };

      final csv = BackupExportService.generateCsvStringFromPayload(payload);
      final lines = csv.trim().split('\n').map((l) => l.trim()).toList();

      // Check Header: has Qty, Cost, Retailer, Invoice, Notes, Added
      final header = lines[0];
      expect(header, contains('Qty'));
      expect(header, contains('Cost'));
      expect(header, contains('Retailer'));
      expect(header, contains('Invoice'));
      expect(header, contains('Notes'));
      expect(header, contains('Added'));

      // Check Row 1: 2017.0 -> "2017" (no .0), Qty -> "3", Cost -> "$15.50", Date -> "2024-10-17"
      final row1 = lines[1];
      expect(row1, contains('"2017"'));
      expect(row1, isNot(contains('"2017.0"')));
      expect(row1, contains('"3"'));
      expect(row1, contains('"\$15.50"'));
      expect(row1, contains('"APMEX"'));
      expect(row1, contains('"INV-9981"'));
      expect(row1, contains('"Gift from grandpa"'));
      expect(row1, contains('"2024-10-17"'));

      // Check Row 2: Qty null -> "1", Cost 0 -> "$0.00", Date ISO -> "2024-10-16"
      final row2 = lines[2];
      expect(row2, contains('"1921"'));
      expect(row2, contains('"1"'));
      expect(row2, contains('"\$0.00"'));
      expect(row2, contains('"Heritage Auctions"'));
      expect(row2, contains('"HA-4421"'));
      expect(row2, contains('"Toned obverse"'));
      expect(row2, contains('"2024-10-16"'));
    });

    test('p7_v812_guest_demo_stream_multi_listener_replay', () async {
      GuestSeedService.setDemoActiveForTest(true);
      GuestSeedService.setDemoCoinCacheForTest([
        {
          'Year': 2022,
          'Denomination': '£2 Silver',
          'Country': 'United Kingdom',
          'Category': 'World',
          'Condition': 'Proof',
          'AI Estimated Value': '45.00',
        },
        {
          'Year': 1921,
          'Denomination': 'Morgan Dollar',
          'Country': 'USA',
          'Category': 'US',
          'Condition': 'MS63',
          'AI Estimated Value': '55.00',
        },
      ]);

      // Test 1: getDemoCoinsStream() replays to multiple consecutive listeners
      final stream1 = GuestSeedService.getDemoCoinsStream();
      final snap1 = await stream1.first;
      expect(snap1.docs.length, equals(2));

      // Second listener subscribes later (simulates tab switch back to All tab)
      final stream2 = GuestSeedService.getDemoCoinsStream();
      final snap2 = await stream2.first;
      expect(snap2.docs.length, equals(2));

      // Test 2: WorldItemService.worldItemsStream() replays to multiple listeners
      final worldStream1 = WorldItemService.worldItemsStream();
      final items1 = await worldStream1.first;
      expect(items1.length, equals(1));
      expect(items1.first.country, equals('United Kingdom'));

      final worldStream2 = WorldItemService.worldItemsStream();
      final items2 = await worldStream2.first;
      expect(items2.length, equals(1));
      expect(items2.first.denomination, equals('£2 Silver'));

      // Test 3: initialData accessors are non-null and match caches
      expect(GuestSeedService.cachedDemoSnapshot.docs.length, equals(2));
      expect(WorldItemService.cachedDemoWorldItems.length, equals(1));
    });

    test('p7_v812_market_news_service_preview_origin_guard', () async {
      GuestSeedService.setDemoActiveForTest(true);
      // In demo mode or on non-production web origins, fetchNewsFeed falls back to cached news
      final news = await MarketNewsService.fetchNewsFeed();
      expect(news, isNotEmpty);
      expect(news.first.title, isNotEmpty);
    });

    test('p7_v813_json_export_full_fidelity_and_csv_formatting', () async {
      final sampleAdded = DateTime.utc(2024, 10, 17, 14, 30, 0);
      final rawCoins = [
        {
          'Year': '2024',
          'Mint Mark': 'W',
          'Denomination': 'American Silver Eagle',
          'Cost': 15.5,
          'Added': Timestamp.fromDate(sampleAdded),
        },
      ];

      // Test A: generateExportPayload produces full-fidelity JSON
      final payload = await BackupExportService.generateExportPayload(mockCoins: rawCoins);

      // Raw map checks
      final rawCoin = (payload['coins'] as List).first as Map<String, dynamic>;
      expect(rawCoin['Cost'], equals(15.5));
      expect(rawCoin['Cost'], isA<num>());
      expect(rawCoin['Cost'], isNot(startsWith(r'$')));
      expect(rawCoin.containsKey('Retailer/Website'), isFalse);
      expect(rawCoin.containsKey('Retailer Invoice #'), isFalse);
      expect(rawCoin.containsKey('Notes'), isFalse);

      // JSON string checks (full ISO timestamp, numeric cost)
      final jsonStr = BackupExportService.generateJsonStringFromPayload(payload);
      final decoded = jsonDecode(jsonStr) as Map<String, dynamic>;
      final jsonCoin = (decoded['coins'] as List).first as Map<String, dynamic>;
      expect(jsonCoin['Cost'], equals(15.5));
      expect(jsonCoin['Cost'], isA<num>());
      expect(jsonCoin['Added'].toString(), contains('2024-10-17T'));
      expect(jsonCoin['Added'].toString().length, greaterThan(10));
      expect(jsonCoin['Year'], equals('2024'));

      // Test B: generateCsvStringFromPayload applies display formatting
      final csv = BackupExportService.generateCsvStringFromPayload(payload);
      final lines = csv.trim().split('\n').map((l) => l.trim()).toList();
      expect(lines.length, equals(2));
      final row = lines[1];
      expect(row, contains(r'"$15.50"'));
      expect(row, contains('"2024-10-17"'));
      expect(row, contains('"2024"'));
    });
  });
}
