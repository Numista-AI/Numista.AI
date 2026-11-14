import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/services/morgan_action_bus.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/services/morgan_test_harness.dart';
import 'package:numista_ai/widgets/morgan_chat_popout.dart';
import 'package:numista_ai/widgets/morgan_copilot_cards.dart';
import 'package:numista_ai/widgets/morgan_settings_panel.dart';
import 'package:numista_ai/widgets/morgan_spotlight_overlay.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    MorganTestHarness.debugEnabledOverride = true;
    MorganActionBus.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganSettingsService.instance.resetForTesting();
    MorganSpotlightController.instance.dismiss();
  });

  tearDown(() {
    MorganSpotlightController.instance.dismiss();
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganSettingsService.instance.resetForTesting();
    MorganActionBus.instance.resetForTesting();
    MorganTestHarness.reset();
    MorganTestHarness.debugEnabledOverride = null;
  });

  group('Morgan Accessibility, WCAG AAA Targets & Keyboard Traversal', () {
    testWidgets(
      'MorganSpotlightOverlay respects disableAnimations and dismisses via Escape key',
      (tester) async {
        final btnKey = GlobalKey();
        final ctrl = MorganSpotlightController.instance;

        await tester.pumpWidget(
          MediaQuery(
            data: const MediaQueryData(
              size: Size(1024, 768),
              disableAnimations: true,
            ),
            child: MaterialApp(
              home: Scaffold(
                body: Stack(
                  children: [
                    Positioned(
                      left: 120,
                      top: 120,
                      child: ElevatedButton(
                        key: btnKey,
                        onPressed: () {},
                        child: const Text('Save Coin'),
                      ),
                    ),
                    MorganSpotlightOverlay(controller: ctrl),
                  ],
                ),
              ),
            ),
          ),
        );

        await ctrl.show(
          targetId: 'btn_save_coin',
          targetKey: btnKey,
          label: 'Save Coin',
          message: 'Tap here to save your coin.',
        );
        await tester.pump();
        expect(ctrl.isActive, isTrue);

        final gotItFinder = find.text('Got It (Esc)');
        expect(gotItFinder, findsOneWidget);

        // Focus button inside overlay and press Escape.
        Focus.of(tester.element(gotItFinder)).requestFocus();
        await tester.pump();
        await tester.sendKeyEvent(LogicalKeyboardKey.escape);
        await tester.pump();

        expect(ctrl.isActive, isFalse);

        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();
      },
    );

    testWidgets(
      'MorganCopilotBannerHost enforces >=56px buttons and cancels Gate 0 on Escape',
      (tester) async {
        bool cancelled = false;
        MorganProactiveRescueObserver.instance.immediateDelayOverride =
            const Duration(milliseconds: 10);

        // Show rescue prompt alongside confirmation gate card.
        MorganScreenStateRegistry.instance.markScreenHydrated(
          route: 'Microscope Scanner',
          contextPatch: {'microscopeConfigured': true, 'serverOnline': false},
        );
        await tester.pump(const Duration(milliseconds: 50));

        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: MorganCopilotBannerHost(
                activeProposal: const MorganGateProposal(
                  actionType: 'add_coin',
                  summaryText: 'Save 1921 Morgan Dollar to My Collection?',
                ),
                onConfirmProposal: (_) async {},
                onCancelProposal: () => cancelled = true,
              ),
            ),
          ),
        );
        await tester.pump();

        for (final label in ['Yes, Save', 'Cancel', 'Fix It For Me', 'I Need More Time']) {
          final textFinder = find.text(label);
          expect(textFinder, findsOneWidget);
          final btnFinder = find.ancestor(
            of: textFinder,
            matching: find.byWidgetPredicate(
              (w) => w is ElevatedButton || w is OutlinedButton,
            ),
          );
          expect(
            tester.getSize(btnFinder).height,
            greaterThanOrEqualTo(56.0),
            reason: '$label must meet >=56px accessible touch target',
          );
        }

        // Cancel button has autofocus: true; Escape cancels proposal cleanly.
        await tester.sendKeyEvent(LogicalKeyboardKey.escape);
        await tester.pump();
        expect(cancelled, isTrue);

        await tester.pumpWidget(const SizedBox.shrink());
        MorganProactiveRescueObserver.instance.resetForTesting();
        await tester.pump();
      },
    );

    testWidgets(
      'showMorganConsentModalIfNeeded renders >=16px body text and 56px action buttons',
      (tester) async {
        await tester.pumpWidget(
          MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (ctx) => ElevatedButton(
                  onPressed: () => showMorganConsentModalIfNeeded(ctx),
                  child: const Text('Open Consent'),
                ),
              ),
            ),
          ),
        );

        await tester.tap(find.text('Open Consent'));
        await tester.pumpAndSettle();

        final bodyFinder = find.textContaining('Morgan can read which screen');
        expect(bodyFinder, findsOneWidget);
        final bodyWidget = tester.widget<Text>(bodyFinder);
        expect(bodyWidget.style?.fontSize ?? 0, greaterThanOrEqualTo(16.0));

        for (final btnLabel in ['Use Text-Only Mode', '✓ Turn On Morgan Co-Pilot']) {
          final f = find.text(btnLabel);
          expect(f, findsOneWidget);
          final btn = find.ancestor(
            of: f,
            matching: find.byWidgetPredicate(
              (w) => w is ElevatedButton || w is OutlinedButton,
            ),
          );
          expect(tester.getSize(btn).height, greaterThanOrEqualTo(56.0));
        }

        await tester.tap(find.text('✓ Turn On Morgan Co-Pilot'));
        await tester.pumpAndSettle();
        expect(MorganSettingsService.instance.consentDecided, isTrue);
        expect(MorganSettingsService.instance.allowVisionRescue, isTrue);
      },
    );

    testWidgets(
      'MorganChatPopout renders 380px Right Dock and Auto-Dodges overlapping spotlights',
      (tester) async {
        // 1. Docked 380px Right Sidebar
        await tester.pumpWidget(
          MaterialApp(
            home: MediaQuery(
              data: const MediaQueryData(size: Size(1280, 800)),
              child: Scaffold(
                body: Row(
                  children: [
                    const Expanded(child: SizedBox()),
                    MorganChatPopout(
                      isDocked: true,
                      onClose: () {},
                      childOverride: const SizedBox.expand(),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pump();
        await tester.pump();

        final dockedFinder = find.byWidgetPredicate(
          (w) => w is Container && w.constraints?.maxWidth == 380,
        );
        expect(dockedFinder, findsOneWidget);
        expect(tester.getSize(dockedFinder).width, 380.0);

        // Unmount docked popout cleanly, then test Floating Auto-Dodge.
        await tester.pumpWidget(const SizedBox.shrink());
        await tester.pump();

        // 2. Floating Auto-Dodge avoids spotlight Rect
        await tester.pumpWidget(
          MaterialApp(
            home: MediaQuery(
              data: const MediaQueryData(size: Size(1280, 800)),
              child: Scaffold(
                body: Stack(
                  children: [
                    MorganChatPopout(
                      isDocked: false,
                      onClose: () {},
                      childOverride: const SizedBox.expand(),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
        await tester.pump();
        await tester.pump();

        const spotRect = Rect.fromLTWH(150, 150, 160, 56);
        final beforeRect = MorganActionBus.instance.popoutRectProvider?.call();
        expect(beforeRect, isNotNull);
        expect(beforeRect!.overlaps(spotRect), isTrue);

        MorganActionBus.instance.onSpotlightPositioned?.call(spotRect);
        await tester.pump();
        await tester.pump(const Duration(milliseconds: 350));

        final afterRect = MorganActionBus.instance.popoutRectProvider?.call();
        expect(afterRect, isNotNull);
        expect(afterRect!.overlaps(spotRect), isFalse);
      },
    );
  });
}
