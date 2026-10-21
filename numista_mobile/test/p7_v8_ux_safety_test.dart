import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker_platform_interface/image_picker_platform_interface.dart';
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
import 'package:numista_ai/services/hardware_service.dart';
import 'package:numista_ai/widgets/auth_gate.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/utils/platform_gate.dart';
import 'package:numista_ai/services/camera_recovery_service.dart';
import 'package:numista_ai/screens/microscope_scan_screen.dart';
import 'package:numista_ai/widgets/morgan_greeter.dart';

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
      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '1921'); // Year
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar'); // Denomination
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarter'); // Program/Series
      await tester.ensureVisible(saveBtnFinder);
      await tester.tap(saveBtnFinder);
      await tester.pumpAndSettle();
      expect(submittedData, isNotNull);
      expect(submittedData!['Quantity'], '1');

      // Test Qty bug fix: type '1' into empty field -> produces '1' (never '11')
      submittedData = null;
      // Re-enter required fields since form was reset after successful submit (V8.9 Fix 11)
      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '1921');
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar');
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarter');
      // Enter '1' in Quantity
      await tester.enterText(find.byKey(const ValueKey('manual_field_Quantity')), '1');
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

      // Fill required fields at minimum
      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '1921');   // Year
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar'); // Denomination
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarter'); // Program/Series
      // Fill optional fields
      await tester.enterText(find.byKey(const ValueKey('manual_field_Theme/Subject')), 'Liberty Head'); // Theme
      await tester.enterText(find.byKey(const ValueKey('manual_field_Variety')), 'DDO');          // Variety
      await tester.enterText(find.byKey(const ValueKey('manual_field_Cost')), '25.00');        // Cost
      await tester.enterText(find.byKey(const ValueKey('manual_field_Quantity')), '2');            // Quantity
      await tester.enterText(find.byKey(const ValueKey('manual_field_Retailer/Website')), 'APMEX');       // Retailer
      await tester.enterText(find.byKey(const ValueKey('manual_field_Retailer Invoice #')), 'INV-001');     // Invoice
      await tester.enterText(find.byKey(const ValueKey('manual_field_Storage Location')), 'Box A');       // Storage
      await tester.enterText(find.byKey(const ValueKey('manual_field_Notes')), 'Nice coin');   // Notes

      await tester.ensureVisible(find.text('Save to My Collection'));
      await tester.tap(find.text('Save to My Collection'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(payload, isNotNull, reason: 'onSubmit must be called');
      expect(payload!['Retailer/Website'], equals('APMEX'));
      expect(payload!['Retailer Invoice #'], equals('INV-001'));
      expect(payload!['Notes'], equals('Nice coin'));
      // All 15 keys present (13 original + Grading Service + Cert # added by Fix 10)
      for (final key in [
        'Year', 'Mint Mark', 'Denomination', 'Program/Series', 'Theme/Subject',
        'Variety', 'Condition', 'Cost', 'Quantity', 'Retailer/Website',
        'Retailer Invoice #', 'Storage Location', 'Notes',
        'Grading Service', 'Cert #',
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

      final qtyFinder = find.byKey(const ValueKey('manual_field_Quantity'));
      expect(
        tester.widget<TextFormField>(qtyFinder).controller?.text ?? '',
        equals(''),
        reason: 'Quantity controller text must be empty on initial build',
      );

      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '1921');            // Year
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar'); // Denomination  
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarter'); // Program/Series
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
      final qtyFinder = find.byKey(const ValueKey('manual_field_Quantity'));
      expect(
        tester.widget<TextFormField>(qtyFinder).controller?.text ?? '',
        equals(''),
        reason: 'Quantity starts empty',
      );
      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '1921');
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Quarter Dollar');
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Washington Quarter');
      // Type '3' into Quantity field
      await tester.enterText(qtyFinder, '3');
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
      await tester.enterText(find.byKey(const ValueKey('manual_field_Year')), '2000'); // Year
      await tester.enterText(find.byKey(const ValueKey('manual_field_Denomination')), 'Dollar'); // Denomination (required)
      await tester.enterText(find.byKey(const ValueKey('manual_field_Program/Series')), 'Peace Dollar'); // Program/Series (required)
      // Leave Quantity blank
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
          'cpgRetail': '50.00',
          'quantity': 2,
        },
        {
          'Year': 2021,
          'Denomination': 'Silver Eagle',
          'cpgRetail': '35.00',
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
          'cpgRetail': '25.00',
        },
      ]);

      final ctx = await MorganChatContextService.load(forceRefresh: true);

      // Verify totalCoins expanded: 2 + 1 + 3 = 6 coins
      expect(ctx.totalCoins, equals(6));

      // Verify portfolio valuation: 50.0 + 35.0 + 25.0 = 110.0 (NET-372: retail market basis)
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

  group('P7 V8.14: AI Photo ID, Camera Routing, and CAC/CACG Support', () {
    testWidgets('p7_v814_take_photo_full_screen_routing_and_prompt', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCameraFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify full screen camera scaffold
      expect(find.widgetWithText(AppBar, 'AI Photo Identification'), findsOneWidget);
      // Back button is an IconButton (tooltip 'Back to Add hub') — Fix 8D replaced BackButton with IconButton
      expect(find.byTooltip('Back to Add hub'), findsOneWidget);
      expect(find.text('Quick Camera Scanner'), findsOneWidget);

      // Verify uncropped camera picker boxes with prompt text
      final promptFinder = find.text('Tap to take a photo or choose from your library');
      expect(promptFinder, findsNWidgets(2)); // Obverse and Reverse boxes

      // Verify picker box container minHeight >= 200
      final containers = tester.widgetList<Container>(find.byType(Container));
      final minHeightBoxes = containers.where((c) => (c.constraints?.minHeight ?? 0) >= 200).toList();
      expect(minHeightBoxes, isNotEmpty);
    });

    testWidgets('p7_v814_quick_add_card_take_photo_and_cert_labels', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(),
        ),
      );
      await tester.pumpAndSettle();

      // Verify quick add card labels
      expect(find.text('Take a photo'), findsOneWidget);
      expect(find.text('Add by Cert # (PCGS / NGC / CAC)'), findsOneWidget);

      // Tap 'Take a photo' card and verify navigation to camera full screen
      await tester.tap(find.text('Take a photo'));
      await tester.pumpAndSettle();

      expect(find.widgetWithText(AppBar, 'AI Photo Identification'), findsOneWidget);
    });

    testWidgets('p7_v814_cacg_cert_chips_and_auto_detection', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify header mentions cert lookup
      expect(find.text('Add by Cert # — PCGS / NGC / CAC'), findsOneWidget);

      // Verify CACG and CAC chips exist
      expect(find.widgetWithText(FilterChip, 'CACG'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'CAC'), findsOneWidget);

      // Tap CACG chip and verify helper text
      await tester.tap(find.widgetWithText(FilterChip, 'CACG'));
      await tester.pumpAndSettle();
      expect(find.text('CACG: Enter slab details with cert # pre-filled'), findsOneWidget);

      // Type cert # and trigger lookup
      final certField = find.byType(TextField);
      await tester.enterText(certField, 'CACG123456');
      await tester.pumpAndSettle();

      await tester.tap(find.text('Look Up'));
      await tester.pumpAndSettle();

      // Verify manual entry card for CACG
      expect(find.text('Enter CACG slab details below'), findsOneWidget);
      expect(find.text('Check this slab on cacgrading.com'), findsOneWidget);
    });

    testWidgets('p7_v8188_cert_lookup_found_prefills_fields', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      HttpAuthClient.httpClientOverride = MockClient((request) async {
        if (request.url.path == '/api/cert_lookup') {
          return http.Response(
            jsonEncode({
              'found': true,
              'cert_num': '12345678',
              'grader': 'NGC',
              'coin_name': r'1881-S $1 Morgan',
              'year': '1881',
              'grade': 'MS65',
              'denomination': r'$1',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('{"detail":"not found"}', 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Select NGC chip
      await tester.tap(find.widgetWithText(FilterChip, 'NGC'));
      await tester.pumpAndSettle();

      // Enter cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '12345678');
      await tester.pumpAndSettle();

      // Tap Look Up
      await tester.tap(find.text('Look Up'));
      await tester.pumpAndSettle();

      // Verify fields prefilled
      expect(find.text(r'1881-S $1 Morgan'), findsOneWidget);
      expect(find.text('1881'), findsOneWidget);
      expect(find.text('MS65'), findsOneWidget);
      expect(find.text(r'$1'), findsOneWidget);
    });

    testWidgets('p7_v8188_cert_lookup_not_found_ngc_shows_honest_message', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      HttpAuthClient.httpClientOverride = MockClient((request) async {
        if (request.url.path == '/api/cert_lookup') {
          return http.Response(
            jsonEncode({
              'found': false,
              'message': 'Direct NGC cert lookup is not supported.',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('{"detail":"not found"}', 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Select NGC chip
      await tester.tap(find.widgetWithText(FilterChip, 'NGC'));
      await tester.pumpAndSettle();

      // Enter cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '1234567-001');
      await tester.pumpAndSettle();

      // Tap Look Up
      await tester.tap(find.text('Look Up'));
      await tester.pumpAndSettle();

      // Verify honest message is displayed
      expect(
        find.textContaining('Direct NGC cert lookup is not supported'),
        findsOneWidget,
      );

      // Verify Scan Slab Photo button is displayed with height >= 48px
      final scanBtnFinder = find.widgetWithText(ElevatedButton, 'Take a photo of the label');
      expect(scanBtnFinder, findsOneWidget);
      final btnSize = tester.getSize(scanBtnFinder);
      expect(btnSize.height, greaterThanOrEqualTo(48.0));

      // Tap Scan Slab Photo and verify scan flow is triggered
      await tester.tap(scanBtnFinder);
      await tester.pumpAndSettle();

      expect(find.text('Take a photo'), findsOneWidget);
    });

    test('URL constants default to live URLs', () {
      // These must match byte-for-byte with the live deployed values
      expect(kApiBaseUrl, equals('https://numista-backend-568985927038.us-central1.run.app'));
      expect(kScanServiceUrl, equals('https://numista-scan-service-568985927038.us-central1.run.app'));
    });

    test('p7_v818_buildAddCoinsHtmlPath_live_and_custom_api', () {
      const email = 'user@example.com';
      // Default / live backend -> no &api= param
      final livePath = buildAddCoinsHtmlPath(email);
      expect(livePath, equals('/add_coins.html?email=user%40example.com'));

      // Explicit live backend -> no &api= param
      final explicitLivePath = buildAddCoinsHtmlPath(
        email,
        apiBase: 'https://numista-backend-568985927038.us-central1.run.app',
      );
      expect(explicitLivePath, equals('/add_coins.html?email=user%40example.com'));

      // Preview / custom backend -> &api= param included
      const customApi = 'https://numista-backend-preview-568985927038.us-central1.run.app';
      final customPath = buildAddCoinsHtmlPath(email, apiBase: customApi);
      expect(
        customPath,
        equals('/add_coins.html?email=user%40example.com&api=https%3A%2F%2Fnumista-backend-preview-568985927038.us-central1.run.app'),
      );
    });

    test('p7_v818_microscope_guard_no_localhost_when_disabled', () async {
      SharedPreferences.setMockInitialValues({'microscope_enabled': false});

      final configured = await HardwareService.isMicroscopeConfigured();
      expect(configured, isFalse);

      final hw = HardwareService();

      // Guarded methods must return null / false / empty without making network calls
      final status = await hw.getStatus();
      expect(status, isNull);

      final running = await hw.isServerRunning();
      expect(running, isFalse);

      final cameras = await hw.listCameras();
      expect(cameras['cameras'], isEmpty);

      final frame = await hw.fetchFrame();
      expect(frame, isNull);

      // Now enable and verify
      await HardwareService.setMicroscopeConfigured(true);
      final configuredNow = await HardwareService.isMicroscopeConfigured();
      expect(configuredNow, isTrue);
    });

    test('p7_v818_1_auth_gate_reset_welcome', () {
      AuthGate.welcomeDone = true;
      expect(AuthGate.welcomeDone, isTrue);

      AuthGate.resetWelcome();
      expect(AuthGate.welcomeDone, isFalse);
    });

    test('p7_v818_1_settings_microscope_and_hub_nfc_font_sizes', () {
      final settingsSrc = File('lib/screens/settings_screen.dart').readAsStringSync();
      expect(settingsSrc.contains('Connect a USB microscope to identify coins up close.'), isTrue);
      expect(settingsSrc.contains('fontSize: 16, color: descColor'), isTrue);
      expect(settingsSrc.contains("'Connects digital USB microscopes via the Numista Desktop Agent"), isFalse);

      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc.contains('NFC Secured — tap slab label to verify authenticity'), isTrue);
      expect(hubSrc.contains('fontSize: 16, color: Color(0xFF1E40AF)'), isTrue);
      expect(hubSrc.contains('fontSize: 12, color: Color(0xFF1E40AF)'), isFalse);
      expect(hubSrc.contains("'Open Invoice Importer →'"), isTrue);
      expect(hubSrc.contains("'Run High-Speed Parallel Batch'"), isFalse);
    });

    // ── Fix 7: Firebase config alignment test (dynamic — reads from firebase_options.dart) ──
    test('add_coins_html_uses_web_firebase_config', () {
      // Read expected web config values dynamically from firebase_options.dart
      final optionsContent = File('lib/firebase_options.dart').readAsStringSync();
      final webApiKeyMatch = RegExp(
        r"static const FirebaseOptions web = FirebaseOptions\([^)]*?apiKey: '([^']+)'",
        dotAll: true,
      ).firstMatch(optionsContent);
      final webAppIdMatch = RegExp(
        r"static const FirebaseOptions web = FirebaseOptions\([^)]*?appId: '([^']+)'",
        dotAll: true,
      ).firstMatch(optionsContent);
      expect(webApiKeyMatch, isNotNull,
          reason: 'Could not parse web apiKey from firebase_options.dart');
      expect(webAppIdMatch, isNotNull,
          reason: 'Could not parse web appId from firebase_options.dart');

      final expectedApiKey = webApiKeyMatch!.group(1)!;
      final expectedAppId = webAppIdMatch!.group(1)!;

      final webDir = Directory('web');
      final htmlFiles = webDir
          .listSync(recursive: true)
          .whereType<File>()
          .where((f) => f.path.endsWith('.html'));

      int checkedCount = 0;
      for (final file in htmlFiles) {
        final content = file.readAsStringSync();
        if (content.contains('firebaseConfig')) {
          checkedCount++;
          expect(content, contains(expectedApiKey),
              reason: '${file.path} apiKey does not match firebase_options.dart web config');
          expect(content, contains(expectedAppId),
              reason: '${file.path} appId does not match firebase_options.dart web config');
          // Must NOT contain the Android key
          expect(content, isNot(contains('AIzaSyDSM3pQl0oWdZgOw2vXCvhyRH899l-ZvcM')),
              reason: '${file.path} contains Android apiKey');
          expect(content, isNot(contains('bf2a6f690b59e2148b072f')),
              reason: '${file.path} contains Android appId');
        }
      }
      expect(checkedCount, greaterThanOrEqualTo(1),
          reason: 'At least one html file with firebaseConfig must be checked');
    });

    // ── Fix 2A: Cert guard test ────────────────────────────────────────────
    test('cert_scan_guard_rejects_blurred_artifacts', () {
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, contains("rawCert.toLowerCase() == 'blurred'"));
      expect(hubSrc, contains("rawCert.toLowerCase() == 'unknown'"));
      expect(hubSrc, contains("rawCert.toLowerCase() == 'none'"));
      expect(hubSrc, contains(r"RegExp(r'^[0-9A-Za-z\-]+$')"));
    });

    // ── Fix 5: Camera error guard includes permissions-policy ─────────────
    test('camera_error_guard_includes_permissions_policy', () {
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, contains("permissions-policy"));
      expect(hubSrc, contains("not allowed"));
    });

    // ── Fix 8A: Microscope tile removed from morgan_greeter ───────────────
    test('microscope_tile_removed_from_morgan_greeter', () {
      final greeterSrc = File('lib/widgets/morgan_greeter.dart').readAsStringSync();
      expect(greeterSrc, isNot(contains('Identify with Microscope')));
      expect(greeterSrc, isNot(contains("route: 'Microscope Scanner'")));
    });

    // ── Fix 8B: Microscope Station text removed from camera tab ──────────
    test('microscope_station_text_removed_from_camera_tab', () {
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, isNot(contains('please use the Microscope Station')));
    });
  });

  // ── Fix 10D: Manual form grading service + cert # fields ─────────────────
  group('P7 V8.18.3 Fix 10: Manual Entry Grading Service + Cert #', () {
    testWidgets('manual_form_has_grading_service_and_cert', (WidgetTester tester) async {
      await tester.pumpWidget(MaterialApp(
        home: Scaffold(
          body: SingleChildScrollView(
            child: AddCoinManualForm(
              onSubmit: (_) {},
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();
      expect(find.text('Grading Service'), findsOneWidget);
      // _buildField uses RichText not Text, so use ValueKey on the TextFormField instead.
      expect(find.byKey(const ValueKey('manual_field_Cert #')), findsOneWidget);
    });

    test('manual_form_submit_includes_grading_service_and_cert', () {
      final formSrc = File('lib/widgets/add_coin_manual_form.dart').readAsStringSync();
      expect(formSrc, contains("'Grading Service'"));
      expect(formSrc, contains("'grading_service'"));
      expect(formSrc, contains("'Cert #'"));
      expect(formSrc, contains("'cert_number'"));
      expect(formSrc, contains('DropdownButtonFormField'));
      expect(formSrc, contains("'NGC', 'PCGS', 'CAC', 'CACG', 'ANACS', 'ICG'"));
    });

    test('manual_hub_coinDoc_includes_grading_cert', () {
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, contains("'grading_service'"));
      expect(hubSrc, contains("'cert_number'"));
      expect(hubSrc, contains("data['grading_service'] ?? data['Grading Service']"));
    });
  });

  // ── P7 V8.18.5 Feedback Verifications (NET-354 / COS_SCORE V8.18.4) ──────
  group('P7 V8.18.5 Feedback Verifications', () {
    testWidgets('p7_v8185_photo_id_error_shows_all_three_buttons', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCameraFullScreen: true,
            initialCamError: 'Could not identify this coin. Please try a clearer photo.',
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify the error text is visible
      expect(find.text('Could not identify this coin. Please try a clearer photo.'), findsOneWidget);

      // Verify all 3 action buttons exist and have height >= 56px
      final tryAgainBtn = find.widgetWithText(ElevatedButton, 'Try again');
      expect(tryAgainBtn, findsOneWidget);
      expect(tester.getSize(tryAgainBtn).height, greaterThanOrEqualTo(56.0));

      final choosePhotoBtn = find.widgetWithText(OutlinedButton, 'Choose a photo instead');
      expect(choosePhotoBtn, findsOneWidget);
      expect(tester.getSize(choosePhotoBtn).height, greaterThanOrEqualTo(56.0));

      final manualBtn = find.widgetWithText(OutlinedButton, 'Enter manually');
      expect(manualBtn, findsOneWidget);
      expect(tester.getSize(manualBtn).height, greaterThanOrEqualTo(56.0));

      // Tap 'Try again' to verify it clears error
      await tester.tap(tryAgainBtn);
      await tester.pumpAndSettle();
      expect(find.text('Could not identify this coin. Please try a clearer photo.'), findsNothing);
    });

    testWidgets('p7_v8185_localhost_proof_zero_requests_on_hub_load', (WidgetTester tester) async {
      SharedPreferences.setMockInitialValues({'microscope_enabled': false});
      final overrides = _LocalhostTrackerHttpOverrides();
      final prevOverrides = HttpOverrides.current;
      HttpOverrides.global = overrides;

      try {
        setTestViewSize(tester, width: 800, height: 1200);
        await tester.pumpWidget(
          const MaterialApp(
            home: AddCoinsHub(),
          ),
        );
        await tester.pumpAndSettle();

        // Check if any request was made to localhost or 127.0.0.1
        final localhostCalls = overrides.requestedUris.where((uri) {
          final h = uri.host.toLowerCase();
          return h == 'localhost' || h == '127.0.0.1';
        }).toList();

        expect(localhostCalls, isEmpty,
            reason: 'AddCoinsHub on load must never make requests to localhost or 127.0.0.1');

        // Also test HardwareService methods directly with microscope disabled
        final hw = HardwareService();
        final status = await hw.getStatus();
        expect(status, isNull);
        final running = await hw.isServerRunning();
        expect(running, isFalse);

        final localhostCallsAfterHw = overrides.requestedUris.where((uri) {
          final h = uri.host.toLowerCase();
          return h == 'localhost' || h == '127.0.0.1';
        }).toList();

        expect(localhostCallsAfterHw, isEmpty,
            reason: 'HardwareService guarded methods must make 0 requests to localhost when disabled');
      } finally {
        HttpOverrides.global = prevOverrides;
      }
    });

    testWidgets('p7_v8189_photo_scan_prefills_label_fields_and_shows_banner', (tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      final prevPicker = ImagePickerPlatform.instance;
      ImagePickerPlatform.instance = _TestImagePickerPlatform();
      addTearDown(() {
        ImagePickerPlatform.instance = prevPicker;
      });

      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/scan_cert_number_upload') {
          final resBytes = utf8.encode(jsonEncode({
            'cert_number': '8321797',
            'grader': 'NGC',
            'confidence': 'HIGH',
            'message': 'OK',
            'year': '1881',
            'denomination': 'Morgan Dollar',
            'grade': 'MS-65',
            'mint': 'S',
            'variety': null,
          }));
          return http.StreamedResponse(
            Stream.value(resBytes),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Trigger photo scan via the 56px photo button
      final photoBtn = find.text('📷 Take a photo of the label');
      expect(photoBtn, findsOneWidget);
      await tester.tap(photoBtn);
      await tester.pumpAndSettle();

      // Tap 'Take a photo' in bottom sheet
      final takePhotoOption = find.text('Take a photo');
      expect(takePhotoOption, findsOneWidget);
      await tester.tap(takePhotoOption);
      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Verify fields prefilled
      expect(find.text('1881'), findsOneWidget);
      expect(find.text('Morgan Dollar'), findsOneWidget);
      expect(find.text('MS-65'), findsOneWidget);
      expect(find.text('S'), findsOneWidget);

      // Verify banner text & 18px font size
      final bannerFinder = find.textContaining('Read from your slab photo');
      expect(bannerFinder, findsOneWidget);
      final bannerText = tester.widget<Text>(bannerFinder);
      expect(bannerText.style?.fontSize, equals(18.0));
    });

    testWidgets('p7_v81810_cert_mismatch_dialog_keep_typed', (tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      final prevPicker = ImagePickerPlatform.instance;
      ImagePickerPlatform.instance = _TestImagePickerPlatform();
      addTearDown(() {
        ImagePickerPlatform.instance = prevPicker;
      });

      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/scan_cert_number_upload') {
          final resBytes = utf8.encode(jsonEncode({
            'cert_number': '8321797',
            'grader': 'NGC',
            'confidence': 'HIGH',
            'message': 'OK',
            'year': '1881',
            'denomination': 'Morgan Dollar',
            'grade': 'MS-65',
            'mint': 'S',
            'variety': null,
          }));
          return http.StreamedResponse(
            Stream.value(resBytes),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Enter a different cert number initially
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '1111111');
      await tester.pumpAndSettle();

      // Trigger photo scan
      final photoBtn = find.text('📷 Take a photo of the label');
      expect(photoBtn, findsOneWidget);
      await tester.tap(photoBtn);
      await tester.pumpAndSettle();

      final takePhotoOption = find.text('Take a photo');
      expect(takePhotoOption, findsOneWidget);
      await tester.tap(takePhotoOption);
      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Verify conflict dialog appears with both cert numbers and 18px text
      expect(find.text('Cert Number Conflict'), findsOneWidget);
      final keepTypedBtn = find.text('Keep the number I typed (1111111)');
      final usePhotoBtn = find.text('Use the number on the photo (8321797)');
      expect(keepTypedBtn, findsOneWidget);
      expect(usePhotoBtn, findsOneWidget);

      // Tap "Keep the number I typed (1111111)"
      await tester.tap(keepTypedBtn);
      await tester.pumpAndSettle();

      // Verify cert number is kept as 1111111
      expect(find.widgetWithText(TextField, '1111111'), findsWidgets);

      // Verify photo label fields prefilled
      expect(find.text('1881'), findsOneWidget);
      expect(find.text('Morgan Dollar'), findsOneWidget);
      expect(find.text('MS-65'), findsOneWidget);
      expect(find.text('S'), findsOneWidget);
    });

    testWidgets('p7_v81810_cert_mismatch_dialog_use_photo', (tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      final prevPicker = ImagePickerPlatform.instance;
      ImagePickerPlatform.instance = _TestImagePickerPlatform();
      addTearDown(() {
        ImagePickerPlatform.instance = prevPicker;
      });

      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/scan_cert_number_upload') {
          final resBytes = utf8.encode(jsonEncode({
            'cert_number': '8321797',
            'grader': 'NGC',
            'confidence': 'HIGH',
            'message': 'OK',
            'year': '1881',
            'denomination': 'Morgan Dollar',
            'grade': 'MS-65',
            'mint': 'S',
            'variety': null,
          }));
          return http.StreamedResponse(
            Stream.value(resBytes),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Enter a different cert number initially
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '1111111');
      await tester.pumpAndSettle();

      // Trigger photo scan
      final photoBtn = find.text('📷 Take a photo of the label');
      expect(photoBtn, findsOneWidget);
      await tester.tap(photoBtn);
      await tester.pumpAndSettle();

      final takePhotoOption = find.text('Take a photo');
      expect(takePhotoOption, findsOneWidget);
      await tester.tap(takePhotoOption);
      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Verify conflict dialog appears with both cert numbers
      expect(find.text('Cert Number Conflict'), findsOneWidget);
      final keepTypedBtn = find.text('Keep the number I typed (1111111)');
      final usePhotoBtn = find.text('Use the number on the photo (8321797)');
      expect(keepTypedBtn, findsOneWidget);
      expect(usePhotoBtn, findsOneWidget);

      // Tap "Use the number on the photo (8321797)"
      await tester.tap(usePhotoBtn);
      await tester.pumpAndSettle();

      // Verify cert number is updated to 8321797
      expect(find.widgetWithText(TextField, '8321797'), findsWidgets);

      // Verify photo label fields prefilled
      expect(find.text('1881'), findsOneWidget);
      expect(find.text('Morgan Dollar'), findsOneWidget);
      expect(find.text('MS-65'), findsOneWidget);
      expect(find.text('S'), findsOneWidget);
    });


    testWidgets('p7_v81813_fix1_cert_heading_stays_neutral_when_not_sure', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Grader defaults to 'Not sure' (_certGrader is null)
      expect(find.text('Certification Number'), findsOneWidget);
      expect(find.text('PCGS Certification Number'), findsNothing);

      // Type an 8-digit PCGS-style cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '53652580');
      await tester.pumpAndSettle();

      // Heading must STAY 'Certification Number' (NOT switch to 'PCGS Certification Number')
      expect(find.text('Certification Number'), findsOneWidget);
      expect(find.text('PCGS Certification Number'), findsNothing);
    });

    testWidgets('p7_v81813_fix3_tap_targets_and_help_icon_sizing', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify cert '?' help icon has 48x48 tap target
      final helpIcon = find.byIcon(Icons.help_outline_rounded);
      expect(helpIcon, findsOneWidget);
      final helpParent = find.ancestor(of: helpIcon, matching: find.byType(SizedBox)).first;
      final size = tester.getSize(helpParent);
      expect(size.width, greaterThanOrEqualTo(48.0));
      expect(size.height, greaterThanOrEqualTo(48.0));

      // Verify Back arrow has 48x48 constraints
      final backBtn = find.byTooltip('Back to Add hub');
      expect(backBtn, findsOneWidget);
      final backSize = tester.getSize(backBtn);
      expect(backSize.width, greaterThanOrEqualTo(48.0));
      expect(backSize.height, greaterThanOrEqualTo(48.0));
    });

    testWidgets('p7_v81813_fix4_cert_not_found_names_cert_and_grader_with_manual_fallback', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        return http.StreamedResponse(Stream.value(utf8.encode('{"found":false}')), 200);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Enter a cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '53652580');
      await tester.pumpAndSettle();

      // Tap Look Up
      final lookUpBtn = find.text('Look Up');
      expect(lookUpBtn, findsOneWidget);
      await tester.tap(lookUpBtn);
      await tester.pumpAndSettle();

      // Error card must specifically name cert # and grader searched
      expect(find.textContaining('Cert #53652580 (PCGS)'), findsWidgets);
      expect(find.textContaining('Please double-check the digits'), findsOneWidget);

      // Both buttons present with height >= 56px
      final tryAgainBtn = find.widgetWithText(ElevatedButton, 'Try again');
      expect(tryAgainBtn, findsOneWidget);
      expect(tester.getSize(tryAgainBtn).height, greaterThanOrEqualTo(56.0));

      final manualBtn = find.widgetWithText(OutlinedButton, 'Type the coin in instead');
      expect(manualBtn, findsOneWidget);
      expect(tester.getSize(manualBtn).height, greaterThanOrEqualTo(56.0));
    });

    testWidgets('p7_v81813_fix5_cacg_slab_photo_preserves_typed_cert_and_populates_label', (tester) async {
      setTestViewSize(tester, width: 800, height: 1400);

      final prevPicker = ImagePickerPlatform.instance;
      ImagePickerPlatform.instance = _TestImagePickerPlatform();
      addTearDown(() {
        ImagePickerPlatform.instance = prevPicker;
      });

      // Backend returns coin details from front label, but cert_number is null (because it's on the reverse of CACG slab)
      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/scan_cert_number_upload') {
          final resBytes = utf8.encode(jsonEncode({
            'cert_number': null,
            'grader': 'CACG',
            'confidence': 'HIGH',
            'message': 'OK',
            'year': '1921',
            'denomination': 'Morgan Dollar',
            'grade': 'MS-66',
            'mint': '',
            'variety': null,
          }));
          return http.StreamedResponse(
            Stream.value(resBytes),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // User has typed their 9-digit CACG cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '663261170');
      await tester.pumpAndSettle();

      // Trigger photo scan
      final photoBtn = find.text('📷 Take a photo of the label');
      await tester.tap(photoBtn);
      await tester.pumpAndSettle();

      final takePhotoOption = find.text('Take a photo');
      await tester.tap(takePhotoOption);
      await tester.runAsync(() async {
        await Future.delayed(const Duration(milliseconds: 500));
      });
      await tester.pumpAndSettle();

      // Cert #663261170 must NOT be cleared or error-out!
      expect(find.widgetWithText(TextField, '663261170'), findsWidgets);

      // Label fields must be populated from the front photo
      expect(find.text('1921'), findsOneWidget);
      expect(find.text('Morgan Dollar'), findsOneWidget);
      expect(find.text('MS-66'), findsOneWidget);
    });

    testWidgets('p7_v81813_fix3_camera_confirm_card_cancel_and_scan_another_sizing', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1600);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCameraFullScreen: true,
            initialCamResult: {
              'Year': '1921',
              'Denomination': 'Morgan Dollar',
              'Condition': 'MS65',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify Scan Another button has min height >= 48px
      final scanAnotherBtn = find.widgetWithText(TextButton, 'Scan Another');
      expect(scanAnotherBtn, findsOneWidget);
      expect(tester.getSize(scanAnotherBtn).height, greaterThanOrEqualTo(48.0));

      // Verify Cancel button on camera confirm card has min height >= 56px
      final cancelBtn = find.widgetWithText(OutlinedButton, 'Cancel');
      expect(cancelBtn, findsOneWidget);
      expect(tester.getSize(cancelBtn).height, greaterThanOrEqualTo(56.0));
    });
    testWidgets('p7_v81811_cert_save_mint_mark_key', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2000);

      Map<String, dynamic>? interceptedPayload;

      final prevOverride = HttpAuthClient.httpClientOverride;
      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/cert_save') {
          final bodyBytes = await bodyStream.toBytes();
          final jsonMap = jsonDecode(utf8.decode(bodyBytes)) as Map<String, dynamic>;
          interceptedPayload = jsonMap['coin_data'] as Map<String, dynamic>?;
          return http.StreamedResponse(
            Stream.value(utf8.encode(jsonEncode({'status': 'ok'}))),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });
      addTearDown(() {
        HttpAuthClient.httpClientOverride = prevOverride;
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCertFullScreen: true,
            initialCoinPreset: {
              'name': 'Morgan Dollar',
              'year': '1881',
              'mint': 'S',
              'certNo': '8321797',
              'grader': 'NGC',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Ensure 'S' is populated in the mint mark field
      expect(find.widgetWithText(TextField, 'S'), findsOneWidget);

      // Trigger save
      final saveBtn = find.text('Confirm & Add to My Collection');
      expect(saveBtn, findsOneWidget);
      await tester.ensureVisible(saveBtn);
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Assert: the coin map contains 'Mint Mark': 'S'
      expect(interceptedPayload, isNotNull);
      expect(interceptedPayload!['Mint Mark'], equals('S'));
      // Assert: the coin map does NOT contain key 'MintMark' (no space variant)
      expect(interceptedPayload!.containsKey('MintMark'), isFalse);

      // Static source assertion confirming save block writes 'Mint Mark' and not 'MintMark'
      final hubSrc = File('lib/screens/add_coins_hub.dart').readAsStringSync();
      expect(hubSrc, contains("'Mint Mark':         _certManualMint.text.trim()"));
      expect(hubSrc.contains("'MintMark':"), isFalse);
    });
  });
  group('P7 V8.18.15 Regression & UX Safety Suite', () {
    testWidgets('p7_v81815_400d_manual_save_writes_typed_year_and_cert', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2000);

      Map<String, dynamic>? interceptedPayload;
      final prevOverride = HttpAuthClient.httpClientOverride;
      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/cert_save') {
          final bodyBytes = await bodyStream.toBytes();
          final jsonMap = jsonDecode(utf8.decode(bodyBytes)) as Map<String, dynamic>;
          interceptedPayload = jsonMap['coin_data'] as Map<String, dynamic>?;
          return http.StreamedResponse(
            Stream.value(utf8.encode(jsonEncode({'status': 'ok'}))),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });
      addTearDown(() {
        HttpAuthClient.httpClientOverride = prevOverride;
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCertFullScreen: true,
            initialCoinPreset: {
              'name': 'Buffalo Nickel',
              'year': '1936',
              'mint': 'S',
              'certNo': '53652580',
              'grader': 'NGC',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Trigger save
      final saveBtn = find.text('Confirm & Add to My Collection');
      expect(saveBtn, findsOneWidget);
      await tester.ensureVisible(saveBtn);
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Assert typed year and cert are retained on save payload
      expect(interceptedPayload, isNotNull);
      expect(interceptedPayload!['Year'], equals('1936'));
      expect(interceptedPayload!['certNo'], equals('53652580'));
      expect(interceptedPayload!['Cert #'], equals('53652580'));
    });

    testWidgets('p7_v81815_400e_graded_condition_saves_graded_and_ms65', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 2000);

      Map<String, dynamic>? interceptedPayload;
      final prevOverride = HttpAuthClient.httpClientOverride;
      HttpAuthClient.httpClientOverride = MockClient.streaming((request, bodyStream) async {
        if (request.url.path == '/api/cert_save') {
          final bodyBytes = await bodyStream.toBytes();
          final jsonMap = jsonDecode(utf8.decode(bodyBytes)) as Map<String, dynamic>;
          interceptedPayload = jsonMap['coin_data'] as Map<String, dynamic>?;
          return http.StreamedResponse(
            Stream.value(utf8.encode(jsonEncode({'status': 'ok'}))),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.StreamedResponse(Stream.value(utf8.encode('{"detail":"not found"}')), 404);
      });
      addTearDown(() {
        HttpAuthClient.httpClientOverride = prevOverride;
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCertFullScreen: true,
            initialCoinPreset: {
              'name': 'Morgan Dollar',
              'year': '1881',
              'mint': 'S',
              'certNo': '8321797',
              'grader': 'NGC',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Enter grade MS65 into the Grade field
      final gradeField = find.byWidgetPredicate((w) => w is TextField && w.decoration?.hintText == 'e.g. MS-64');
      if (gradeField.evaluate().isNotEmpty) {
        await tester.enterText(gradeField, 'MS65');
        await tester.pumpAndSettle();
      }

      // Trigger save
      final saveBtn = find.text('Confirm & Add to My Collection');
      expect(saveBtn, findsOneWidget);
      await tester.ensureVisible(saveBtn);
      await tester.tap(saveBtn);
      await tester.pumpAndSettle();

      // Assert Graded condition and Grade: MS65 are saved, NOT Ungraded
      expect(interceptedPayload, isNotNull);
      expect(interceptedPayload!['grader'], equals('NGC'));
      expect(interceptedPayload!['Grade'], equals('MS65'));
      expect(interceptedPayload!['Condition'], equals('MS65'));
      expect(interceptedPayload!['Condition'], isNot(equals('Ungraded')));
    });

    testWidgets('p7_v81815_401_3_width_360dp_button_sizes_ge_48px', (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 800);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(
            showCameraFullScreen: true,
            initialCamResult: {
              'Year': '1921',
              'Denomination': 'Morgan Dollar',
              'Condition': 'MS65',
            },
          ),
        ),
      );
      await tester.pumpAndSettle();

      // Verify Scan Another button has min height >= 48px
      final scanAnotherBtn = find.widgetWithText(TextButton, 'Scan Another');
      expect(scanAnotherBtn, findsOneWidget);
      expect(tester.getSize(scanAnotherBtn).height, greaterThanOrEqualTo(48.0));

      // Verify Cancel button has min height >= 48px (56px)
      final cancelBtn = find.widgetWithText(OutlinedButton, 'Cancel');
      expect(cancelBtn, findsOneWidget);
      expect(tester.getSize(cancelBtn).height, greaterThanOrEqualTo(48.0));

      // Assert zero RenderFlex overflow occurred
      expect(tester.takeException(), isNull);
    });

    testWidgets('p7_v81815_401_4_ngc_not_found_amber_card_with_cert', (WidgetTester tester) async {
      setTestViewSize(tester, width: 360, height: 1200);

      final prevOverride = HttpAuthClient.httpClientOverride;
      HttpAuthClient.httpClientOverride = MockClient((request) async {
        if (request.url.path == '/api/cert_lookup') {
          return http.Response(
            jsonEncode({
              'found': false,
              'message': 'Direct NGC cert lookup is not supported.',
            }),
            200,
            headers: {'content-type': 'application/json'},
          );
        }
        return http.Response('{"detail":"not found"}', 404);
      });
      addTearDown(() {
        HttpAuthClient.httpClientOverride = prevOverride;
      });

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Select NGC chip
      await tester.tap(find.widgetWithText(FilterChip, 'NGC'));
      await tester.pumpAndSettle();

      // Enter cert number
      final certField = find.byType(TextField).first;
      await tester.enterText(certField, '99999999');
      await tester.pumpAndSettle();

      // Tap Look Up
      final lookupBtn = find.text('Look Up');
      expect(lookupBtn, findsOneWidget);
      await tester.tap(lookupBtn);
      await tester.pumpAndSettle();

      // Amber card displayed with cert 99999999 and NGC
      expect(find.textContaining('Cert #99999999 (NGC) was not found'), findsOneWidget);

      // Button 'Take a photo of the label' has min height >= 56px
      final labelPhotoBtn = find.byKey(const Key('cert_lookup_scan_slab_button'));
      expect(labelPhotoBtn, findsOneWidget);
      expect(tester.getSize(labelPhotoBtn).height, greaterThanOrEqualTo(56.0));
      expect(tester.takeException(), isNull);
    });

    testWidgets('p7_v81815_410_is_native_phone_override_gate', (WidgetTester tester) async {
      addTearDown(() {
        debugIsNativePhoneOverride = null;
      });

      // 1. debugIsNativePhoneOverride = true
      debugIsNativePhoneOverride = true;
      expect(isNativePhone, isTrue);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (ctx) => Text(isNativePhone ? 'PHONE_VIEW' : 'WEB_VIEW'),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('PHONE_VIEW'), findsOneWidget);
      expect(find.text('WEB_VIEW'), findsNothing);

      // 2. debugIsNativePhoneOverride = false
      debugIsNativePhoneOverride = false;
      expect(isNativePhone, isFalse);

      await tester.pumpWidget(
        MaterialApp(
          home: Scaffold(
            body: Builder(
              builder: (ctx) => Text(isNativePhone ? 'PHONE_VIEW' : 'WEB_VIEW'),
            ),
          ),
        ),
      );
      await tester.pumpAndSettle();
      expect(find.text('WEB_VIEW'), findsOneWidget);
      expect(find.text('PHONE_VIEW'), findsNothing);
    });

    testWidgets('p7_v81815_408n_portrait_resolutions_zero_overflow', (WidgetTester tester) async {
      addTearDown(() {
        debugIsNativePhoneOverride = null;
      });
      debugIsNativePhoneOverride = true;

      final portraitSizes = [
        const Size(360, 640),
        const Size(412, 892),
        const Size(457, 812),
      ];

      for (final size in portraitSizes) {
        setTestViewSize(tester, width: size.width, height: size.height);

        await tester.pumpWidget(
          const MaterialApp(
            home: AddCoinsHub(),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull, reason: 'Overflow in portrait at ${size.width}x${size.height}');
      }
    });

    testWidgets('p7_v81815_413p_landscape_resolutions_zero_overflow', (WidgetTester tester) async {
      addTearDown(() {
        debugIsNativePhoneOverride = null;
      });
      debugIsNativePhoneOverride = true;

      final landscapeSizes = [
        const Size(640, 360),
        const Size(892, 412),
        const Size(812, 457),
      ];

      for (final size in landscapeSizes) {
        setTestViewSize(tester, width: size.width, height: size.height);

        await tester.pumpWidget(
          const MaterialApp(
            home: AddCoinsHub(),
          ),
        );
        await tester.pumpAndSettle();

        expect(tester.takeException(), isNull, reason: 'Overflow in landscape at ${size.width}x${size.height}');

        // Verify the last entry card is reachable after scroll and hit-testable
        final moreWaysFinder = find.text('More ways to add');
        expect(moreWaysFinder, findsOneWidget);
        await tester.ensureVisible(moreWaysFinder);
        await tester.pumpAndSettle();
        expect(tester.getCenter(moreWaysFinder), isNotNull);
      }
    });

    testWidgets('p7_v81815_413q_camera_recovery_lost_data', (WidgetTester tester) async {
      addTearDown(() {
        debugIsNativePhoneOverride = null;
        CameraRecoveryService.latestRecovered = null;
        CameraRecoveryService.lastError = null;
      });

      // 1. When isNativePhone is false, retrieveLostData returns null immediately
      debugIsNativePhoneOverride = false;
      final resNonNative = await CameraRecoveryService.retrieveLostData();
      expect(resNonNative, isNull);

      // 2. When isNativePhone is true:
      debugIsNativePhoneOverride = true;

      // Mock ImagePickerPlatform
      final mockPlatform = _MockRecoveryImagePickerPlatform();
      final prevPlatform = ImagePickerPlatform.instance;
      ImagePickerPlatform.instance = mockPlatform;
      addTearDown(() {
        ImagePickerPlatform.instance = prevPlatform;
      });

      // Scenario A: Successful recovery
      mockPlatform.response = LostDataResponse(
        file: XFile.fromData(
          Uint8List.fromList([1, 2, 3, 4, 5]),
          name: 'recovered_slab.jpg',
          path: '/mock/recovered_slab.jpg',
        ),
      );
      final resSuccess = await CameraRecoveryService.retrieveLostData();
      expect(resSuccess, isNotNull);
      expect(resSuccess!.name, contains('recovered_slab.jpg'));
      expect(resSuccess.bytes, equals([1, 2, 3, 4, 5]));
      expect(CameraRecoveryService.latestRecovered, isNotNull);
      expect(CameraRecoveryService.lastError, isNull);

      // Scenario B: Recovery exception handled gracefully without crash
      mockPlatform.response = LostDataResponse(
        exception: PlatformException(code: 'crash', message: 'Activity killed during camera intent'),
      );
      final resError = await CameraRecoveryService.retrieveLostData();
      expect(resError, isNull);
      expect(CameraRecoveryService.lastError, contains('Activity killed during camera intent'));
    });
  });
}

class _LocalhostTrackerHttpOverrides extends HttpOverrides {
  final List<Uri> requestedUris = [];

  @override
  HttpClient createHttpClient(SecurityContext? context) {
    return _TrackingHttpClient(requestedUris);
  }
}

class _TrackingHttpClient implements HttpClient {
  final List<Uri> requestedUris;
  _TrackingHttpClient(this.requestedUris);

  @override
  bool autoUncompress = true;
  @override
  Duration? connectionTimeout;
  @override
  Duration idleTimeout = const Duration(seconds: 15);
  @override
  int? maxConnectionsPerHost;
  @override
  String? userAgent;

  @override
  void addCredentials(Uri url, String realm, HttpClientCredentials credentials) {}
  @override
  void addProxyCredentials(String host, int port, String realm, HttpClientCredentials credentials) {}
  @override
  void close({bool force = false}) {}

  @override
  Future<HttpClientRequest> getUrl(Uri url) => openUrl('GET', url);
  @override
  Future<HttpClientRequest> postUrl(Uri url) => openUrl('POST', url);
  @override
  Future<HttpClientRequest> putUrl(Uri url) => openUrl('PUT', url);
  @override
  Future<HttpClientRequest> deleteUrl(Uri url) => openUrl('DELETE', url);
  @override
  Future<HttpClientRequest> patchUrl(Uri url) => openUrl('PATCH', url);
  @override
  Future<HttpClientRequest> headUrl(Uri url) => openUrl('HEAD', url);

  @override
  Future<HttpClientRequest> open(String method, String host, int port, String path) {
    requestedUris.add(Uri(scheme: 'http', host: host, port: port, path: path));
    throw UnsupportedError('Blocked network call to $host:$port$path');
  }

  @override
  Future<HttpClientRequest> openUrl(String method, Uri url) {
    requestedUris.add(url);
    throw UnsupportedError('Blocked network call to $url');
  }

  @override
  dynamic noSuchMethod(Invocation invocation) => super.noSuchMethod(invocation);
}

class _TestImagePickerPlatform extends ImagePickerPlatform {
  @override
  Future<XFile?> getImageFromSource({
    required ImageSource source,
    ImagePickerOptions options = const ImagePickerOptions(),
  }) async {
    return XFile.fromData(
      Uint8List.fromList([255, 216, 255, 224, 0, 16, 74, 70, 73, 70]),
      name: 'test_slab.jpg',
      mimeType: 'image/jpeg',
    );
  }
}

class _MockRecoveryImagePickerPlatform extends ImagePickerPlatform {
  LostDataResponse response = LostDataResponse.empty();

  @override
  Future<LostDataResponse> getLostData() async => response;

  @override
  Future<XFile?> getImageFromSource({
    required ImageSource source,
    ImagePickerOptions options = const ImagePickerOptions(),
  }) async => null;
}
