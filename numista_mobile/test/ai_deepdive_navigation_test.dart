import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/base_layout.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';

Future<void> _settle(WidgetTester tester) async {
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 50));
}

void _setupHarnessCleanup() {
  final prevOnError = FlutterError.onError;
  FlutterError.onError = (FlutterErrorDetails details) {
    final msg = details.exceptionAsString();
    if (msg.contains('A RenderFlex overflowed')) {
      return;
    }
    prevOnError?.call(details);
  };
  addTearDown(() {
    FlutterError.onError = prevOnError;
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
  });
}

Widget _buildHarness({
  required Size size,
}) {
  return MaterialApp(
    home: MediaQuery(
      data: MediaQueryData(size: size),
      child: BaseLayout(
        isDemoMode: true,
        testSkipFirebase: true,
        testRouteBuilder: (route, aiInitialQuery, myCollectionTab) {
          return Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text('ROUTE:$route'),
                if (aiInitialQuery != null) Text('QUERY:$aiInitialQuery'),
                Text('TAB:$myCollectionTab'),
              ],
            ),
          );
        },
        testPopoutBuilder: (initialQuery, onClose) {
          return Container(
            width: 320,
            color: Colors.white,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Text('MORGAN_POPOUT'),
                if (initialQuery != null) Text('POPOUT_QUERY:$initialQuery'),
                TextButton(
                  onPressed: onClose,
                  child: const Text('CLOSE_POPOUT'),
                ),
              ],
            ),
          );
        },
      ),
    ),
  );
}

void main() {
  setUp(() {
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  tearDown(() {
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 1: Desktop (1440x900) expanded sidebar AI Deepdive opens DeepDive screen, NOT Ask Morgan popout',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);

    await tester.tap(find.text('Research'));
    await _settle(tester);

    await tester.tap(find.text('Coin Search'));
    await _settle(tester);
    expect(find.text('ROUTE:Coin Search'), findsOneWidget);

    await tester.tap(find.text('AI Deepdive'));
    await _settle(tester);

    expect(find.text('ROUTE:AI Deepdive'), findsOneWidget);
    expect(find.text('ROUTE:Coin Search'), findsNothing);
    expect(find.text('MORGAN_POPOUT'), findsNothing);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'AI Deepdive');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 2: Desktop (1440x900) Ask Morgan popout stays separate and closes when navigating to AI Deepdive',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);

    await tester.tap(find.text('Research'));
    await _settle(tester);
    await tester.tap(find.text('Coin Search'));
    await _settle(tester);

    // Open dedicated Ask Morgan popout via sidebar Ask Morgan button
    await tester.tap(find.text('Ask Morgan'));
    await _settle(tester);

    expect(find.text('MORGAN_POPOUT'), findsOneWidget);
    expect(find.text('ROUTE:Coin Search'), findsOneWidget);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');

    // Navigating to AI Deepdive closes the popout and mounts main-pane DeepDive
    await tester.tap(find.text('AI Deepdive'));
    await _settle(tester);

    expect(find.text('ROUTE:AI Deepdive'), findsOneWidget);
    expect(find.text('MORGAN_POPOUT'), findsNothing);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'AI Deepdive');

    // Collapsed-rail + Ctrl+M sub-step: switch back to Coin Search, collapse sidebar,
    // trigger Ctrl+M to open Ask Morgan popout without changing currentRoute, then expand
    // and navigate to AI Deepdive to close popout and land in main pane.
    await tester.tap(find.text('Coin Search'));
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');

    // Invoke Collapse Sidebar button (Ahem test font can overflow the header Row horizontally).
    final collapseBtn = tester
        .widget<IconButton>(find.widgetWithIcon(IconButton, Icons.chevron_left));
    collapseBtn.onPressed!();
    await _settle(tester);
    expect(find.byTooltip('Expand Sidebar'), findsOneWidget);
    expect(find.byTooltip('Ask Morgan AI'), findsOneWidget);

    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await _settle(tester);
    await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
    await tester.sendKeyDownEvent(LogicalKeyboardKey.keyM);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.keyM);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);
    await _settle(tester);

    expect(find.text('MORGAN_POPOUT'), findsOneWidget);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');

    await tester.tap(find.byTooltip('Expand Sidebar'));
    await _settle(tester);
    await tester.ensureVisible(find.text('AI Deepdive'));
    await _settle(tester);
    await tester.tap(find.text('AI Deepdive'));
    await _settle(tester);

    expect(find.text('ROUTE:AI Deepdive'), findsOneWidget);
    expect(find.text('MORGAN_POPOUT'), findsNothing);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'AI Deepdive');
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 3: Review Hub -> sidebar Coin Search updates currentRoute and 25s stall nudge names Coin Search, never Review Hub',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    MorganProactiveRescueObserver.instance.standardStallOverride =
        const Duration(milliseconds: 40);

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);

    // Navigate to Review Hub and simulate ReviewHubScreen contextPatch
    await tester.tap(find.text('Review'));
    await _settle(tester);
    MorganScreenStateRegistry.instance.markScreenHydrated(
      route: 'Review Hub',
      hydrated: true,
      contextPatch: {'selectedCount': 2},
    );
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Review Hub');

    // Switch to Coin Search via Research accordion in sidebar
    await tester.tap(find.text('Research'));
    await _settle(tester);
    await tester.tap(find.text('Coin Search'));
    await tester.pump();

    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);
    expect(MorganScreenStateRegistry.instance.screenContextData, isEmpty);

    // Wait past 40ms stall override
    await tester.pump(const Duration(milliseconds: 60));

    final prompt = MorganProactiveRescueObserver.instance.activePrompt;
    expect(prompt, isNotNull);
    expect(
      prompt!.message,
      'Looks like you paused on Coin Search. Want me to highlight the next button or do it with you?',
    );
    expect(prompt.message.contains('Coin Search'), isTrue);
    expect(prompt.message.contains('Review Hub'), isFalse);
  });

  testWidgets(
      'Fixture 4: Top-level sidebar items, Ctrl+K, and PopScope Back dismiss popout first then pop history with markScreenHydrated',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Home Dashboard');

    await tester.tap(find.text('My Collection'));
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Collection');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);

    await tester.tap(find.text('Wishlist'));
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Wishlist');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);

    // Move focus inside CallbackShortcuts subtree via Tab, then dispatch Ctrl+K -> Coin Search
    await tester.sendKeyEvent(LogicalKeyboardKey.tab);
    await _settle(tester);
    await tester.sendKeyDownEvent(LogicalKeyboardKey.controlLeft);
    await tester.sendKeyDownEvent(LogicalKeyboardKey.keyK);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.keyK);
    await tester.sendKeyUpEvent(LogicalKeyboardKey.controlLeft);
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);

    // Open Ask Morgan popout via sidebar button, then Back should close popout first
    await tester.tap(find.text('Ask Morgan'));
    await _settle(tester);
    expect(find.text('MORGAN_POPOUT'), findsOneWidget);

    await tester.binding.handlePopRoute();
    await _settle(tester);
    expect(find.text('MORGAN_POPOUT'), findsNothing);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');

    // Second Back pops _routeHistory to My Wishlist
    await tester.binding.handlePopRoute();
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Wishlist');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 5: Phone (390x844) Menu drill-in to AI Deepdive navigates main pane and hydrates registry',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(390, 844));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(390, 844)));
    await _settle(tester);

    await tester.tap(find.text('Menu'));
    await _settle(tester);

    await tester.tap(find.text('Research'));
    await _settle(tester);

    await tester.tap(find.text('AI Deepdive'));
    await _settle(tester);

    expect(find.text('ROUTE:AI Deepdive'), findsOneWidget);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'AI Deepdive');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 6: _routeHistory caps at 50 entries and drops oldest routes',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Home Dashboard');

    // Push Coin Programs, then 50 alternating navigations so Home Dashboard and
    // Coin Programs are evicted by the 50-entry _routeHistory cap.
    await tester.tap(find.text('Coin Programs'));
    await tester.pump();
    for (int i = 0; i < 25; i++) {
      await tester.tap(find.text('My Collection'));
      await tester.pump();
      await tester.tap(find.text('Wishlist'));
      await tester.pump();
    }
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Wishlist');

    // Popping 49 times walks back to the earliest retained entry (My Collection).
    for (int i = 0; i < 49; i++) {
      await tester.binding.handlePopRoute();
      await tester.pump();
    }
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Collection');

    // A 50th pop cannot go further back to Coin Programs or Home Dashboard.
    await tester.binding.handlePopRoute();
    await tester.pump();
    expect(MorganScreenStateRegistry.instance.currentRoute, 'My Collection');
    MorganProactiveRescueObserver.instance.resetForTesting();
  });

  testWidgets(
      'Fixture 7: Aliased route navigation resolves to canonical route and hydrates registry',
      (tester) async {
    _setupHarnessCleanup();

    await tester.binding.setSurfaceSize(const Size(1440, 900));
    addTearDown(() => tester.binding.setSurfaceSize(null));

    await tester.pumpWidget(_buildHarness(size: const Size(1440, 900)));
    await _settle(tester);

    await tester.tap(find.text('Research'));
    await _settle(tester);

    // Tapping 'Numista Lookup' dispatches the aliased route '🔍 Numista Lookup'
    await tester.tap(find.text('Numista Lookup'));
    await _settle(tester);

    expect(find.text('ROUTE:Coin Search'), findsOneWidget);
    expect(MorganScreenStateRegistry.instance.currentRoute, 'Coin Search');
    expect(MorganScreenStateRegistry.instance.isScreenHydrated, isTrue);
    MorganProactiveRescueObserver.instance.resetForTesting();
  });
}
