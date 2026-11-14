import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/services/hardware_service.dart';
import 'package:numista_ai/services/morgan_action_bus.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/services/morgan_test_harness.dart';
import 'package:numista_ai/services/tts_voice_service.dart';
import 'package:numista_ai/widgets/morgan_privacy_mask.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({});
    MorganTestHarness.debugEnabledOverride = true;
    MorganTestHarness.reset();
    HardwareService.clearMockHardwareState();
    MorganActionBus.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganPrivacyMask.resetForTesting();
    TtsVoiceService.isSpeakingNotifier.value = false;
  });

  tearDown(() {
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganActionBus.instance.resetForTesting();
    MorganPrivacyMask.resetForTesting();
    HardwareService.clearMockHardwareState();
    MorganTestHarness.reset();
    MorganTestHarness.debugEnabledOverride = null;
  });

  group('MorganScreenStateRegistry readiness & privacy', () {
    test('waitForTargetReady waits until hydrated + enabled and times out cleanly',
        () async {
      final reg = MorganScreenStateRegistry.instance;
      reg.beginRouteTransition('Review Hub');

      final futureTarget = reg.waitForTargetReady(
        'btn_save_coin',
        timeout: const Duration(milliseconds: 250),
      );

      // Hydrate asynchronously before timeout.
      Future<void>.delayed(const Duration(milliseconds: 25), () {
        reg.markScreenHydrated(
          route: 'Review Hub',
          hydrated: true,
          targets: const [
            MorganUiTarget(
              id: 'btn_save_coin',
              label: 'Save Coin',
              isEnabled: true,
            ),
          ],
        );
      });

      final resolved = await futureTarget;
      expect(resolved, isNotNull);
      expect(resolved!.id, 'btn_save_coin');

      // Now verify timeout returns null when target never becomes ready.
      reg.beginRouteTransition('Review Hub');
      final timedOut = await reg.waitForTargetReady(
        'btn_missing',
        timeout: const Duration(milliseconds: 40),
      );
      expect(timedOut, isNull);
    });

    test('MorganPrivacyMask blocks screenshots on sensitive routes and enforces 3s debounce',
        () async {
      final reg = MorganScreenStateRegistry.instance;
      DateTime clock = DateTime.utc(2026, 11, 14, 12, 0, 0);
      reg.nowProvider = () => clock;
      reg.mockScreenshotCapture = () async => Uint8List.fromList([0xFF, 0xD8, 0x01]);

      for (final route in [
        'Estate Planning',
        'Attorney Portal',
        'Lateral Transfer',
        'Settings & Backup',
      ]) {
        reg.markScreenHydrated(
          route: route,
          contextPatch: {'secret_pin': '1234'},
        );
        final shot = await reg.captureAppScreenshot();
        expect(shot.blocked, isTrue, reason: '$route must block screenshots');
        expect(shot.blockReason, 'privacy_mask_active');
        final compact = reg.toCompactJson();
        expect(compact['privacy_mask_active'], isTrue);
        expect(compact['screen_context_data'], {'redacted': true});
      }

      // Non-sensitive route works with 3.0s debounce.
      reg.markScreenHydrated(route: 'Review Hub', contextPatch: {'coin': '1921'});
      final first = await reg.captureAppScreenshot();
      expect(first.blocked, isFalse);
      expect(first.bytes, isNotNull);

      clock = clock.add(const Duration(milliseconds: 1500));
      final debounced = await reg.captureAppScreenshot();
      expect(debounced.debounced, isTrue);
      expect(debounced.blockReason, 'debounce_active');

      clock = clock.add(const Duration(milliseconds: 2000));
      final third = await reg.captureAppScreenshot();
      expect(third.blocked, isFalse);
      expect(third.bytes, isNotNull);
    });

    testWidgets('Mounted MorganPrivacyMask widget hard-blocks screenshots on safe route',
        (tester) async {
      final reg = MorganScreenStateRegistry.instance;
      reg.mockScreenshotCapture = () async => Uint8List.fromList([1, 2, 3]);
      reg.markScreenHydrated(route: 'Home Dashboard');

      await tester.pumpWidget(
        const MaterialApp(
          home: Scaffold(
            body: MorganPrivacyMask(
              reason: 'transfer_pin',
              child: Text('PIN 9999'),
            ),
          ),
        ),
      );
      expect(MorganPrivacyMask.hasActiveMasks, isTrue);
      final blocked = await reg.captureAppScreenshot();
      expect(blocked.blocked, isTrue);
      expect(blocked.blockReason, 'privacy_mask_active');

      await tester.pumpWidget(const SizedBox.shrink());
      expect(MorganPrivacyMask.hasActiveMasks, isFalse);
      final unblocked = await reg.captureAppScreenshot();
      expect(unblocked.blocked, isFalse);
      MorganProactiveRescueObserver.instance.resetForTesting();
    });
  });

  group('MorganActionBus & MorganTestHarness trace', () {
    test('enforces max-3 actions per turn, blocks unlisted tools, and emits trace',
        () async {
      final reg = MorganScreenStateRegistry.instance;
      final bus = MorganActionBus.instance;
      int invokedCount = 0;

      reg.markScreenHydrated(
        route: 'Review Hub',
        targets: [
          MorganUiTarget(
            id: 'btn_save_coin',
            label: 'Save',
            isEnabled: true,
            onInvoke: ([_]) async => invokedCount++,
          ),
          MorganUiTarget(
            id: 'btn_open_bulk_import',
            label: 'Bulk Import',
            isEnabled: true,
            onInvoke: ([_]) async => invokedCount++,
          ),
        ],
      );

      bus.onNavigateToRoute = (route, {subTab}) async {
        reg.markScreenHydrated(
          route: route,
          targets: [
            MorganUiTarget(
              id: 'btn_save_coin',
              label: 'Save',
              isEnabled: true,
              onInvoke: ([_]) async => invokedCount++,
            ),
            MorganUiTarget(
              id: 'btn_open_bulk_import',
              label: 'Bulk Import',
              isEnabled: true,
              onInvoke: ([_]) async => invokedCount++,
            ),
          ],
        );
      };

      // Turn 1: 4 valid actions -> 4th blocked by max_chain_depth_exceeded.
      final res1 = await bus.executeTurn(
        customTurnId: 'turn_cap_check',
        commands: const [
          MorganActionCommand(action: 'navigate_to', route: 'Review Hub'),
          MorganActionCommand(action: 'spotlight_element', targetId: 'btn_save_coin'),
          MorganActionCommand(action: 'invoke_ui_action', targetId: 'btn_open_bulk_import'),
          MorganActionCommand(action: 'invoke_ui_action', targetId: 'btn_save_coin'),
        ],
      );

      expect(res1.trace.toolsExecuted.length, 3);
      expect(res1.trace.blockedTools, ['invoke_ui_action:max_chain_depth_exceeded']);
      expect(invokedCount, 1);
      expect(MorganTestHarness.lastTrace?['turn_id'], 'turn_cap_check');

      // Turn 2: unlisted action & unlisted route rejected.
      final res2 = await bus.executeTurn(
        commands: const [
          MorganActionCommand(action: 'drop_all_tables'),
          MorganActionCommand(action: 'navigate_to', route: 'Admin Backdoor'),
          MorganActionCommand(action: 'propose_confirmation', actionType: 'add_coin', summaryText: 'Save?'),
        ],
      );
      expect(res2.trace.blockedTools, [
        'drop_all_tables:unlisted_action',
        'navigate_to:Admin Backdoor:unlisted_route',
      ]);
      expect(res2.trace.confirmationGateStatus, 'PENDING_USER');
    });
  });

  group('MorganProactiveRescueObserver tiered timing & pause', () {
    test('fires hardware <2s once per step, distinguishes 25s vs 45s stalls, and honors pauseForSession',
        () async {
      final reg = MorganScreenStateRegistry.instance;
      final observer = MorganProactiveRescueObserver.instance;
      observer.immediateDelayOverride = const Duration(milliseconds: 20);
      observer.standardStallOverride = const Duration(milliseconds: 35);
      observer.physicalStallOverride = const Duration(milliseconds: 80);

      // 1. Hardware offline on Microscope Scanner fires immediate rescue once.
      reg.markScreenHydrated(
        route: 'Microscope Scanner',
        contextPatch: {'microscopeConfigured': true, 'serverOnline': false},
      );
      await Future<void>.delayed(const Duration(milliseconds: 45));
      expect(observer.activePrompt, isNotNull);
      expect(observer.activePrompt!.severity, MorganRescueSeverity.hardwareImmediate);

      // Dismiss and re-trigger same step -> must NOT spam twice.
      observer.dismissActivePrompt();
      reg.updateContextData({'serverOnline': false});
      await Future<void>.delayed(const Duration(milliseconds: 35));
      expect(observer.activePrompt, isNull);

      // 2. Physical 45s threshold vs 25s form stall.
      observer.resetForTesting();
      observer.immediateDelayOverride = const Duration(milliseconds: 20);
      observer.standardStallOverride = const Duration(milliseconds: 35);
      observer.physicalStallOverride = const Duration(milliseconds: 90);

      reg.markScreenHydrated(
        route: 'Microscope Scanner',
        contextPatch: {'microscopeConfigured': true, 'serverOnline': true},
      );
      await Future<void>.delayed(const Duration(milliseconds: 50));
      expect(observer.activePrompt, isNull,
          reason: 'Microscope physical handling window must exceed 25s stall');
      await Future<void>.delayed(const Duration(milliseconds: 60));
      expect(observer.activePrompt, isNotNull);
      expect(observer.activePrompt!.severity, MorganRescueSeverity.stallPhysical45s);

      // 3. "I Need More Time" pauseForSession stops all future prompts in session.
      observer.pauseForSession();
      expect(observer.sessionPausedByUser, isTrue);
      expect(observer.activePrompt, isNull);

      reg.markScreenHydrated(route: 'Review Hub');
      await Future<void>.delayed(const Duration(milliseconds: 60));
      expect(observer.activePrompt, isNull);
    });
  });
}
