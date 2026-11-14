import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:numista_ai/screens/microscope_scan_screen.dart';
import 'package:numista_ai/services/hardware_service.dart';
import 'package:numista_ai/services/morgan_proactive_rescue_observer.dart';
import 'package:numista_ai/services/morgan_screen_state_registry.dart';
import 'package:numista_ai/services/morgan_test_harness.dart';

void main() {
  setUp(() {
    SharedPreferences.setMockInitialValues({'microscope_enabled': false});
    MorganTestHarness.debugEnabledOverride = true;
    HardwareService.clearMockHardwareState();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganProactiveRescueObserver.instance.resetForTesting();
    HardwareService.agentUriLauncher = null;
    HardwareService.lastLaunchedAgentUri = null;
  });

  tearDown(() {
    HardwareService.agentUriLauncher = null;
    HardwareService.lastLaunchedAgentUri = null;
    HardwareService.clearMockHardwareState();
    MorganProactiveRescueObserver.instance.resetForTesting();
    MorganScreenStateRegistry.instance.resetForTesting();
    MorganTestHarness.reset();
    MorganTestHarness.debugEnabledOverride = null;
  });

  group('MicroscopeScanScreen Zero-Dead-End & DirectShow Camera Filter', () {
    testWidgets(
      'auto-enables microscope setting, shows 56px Wake button when previously installed, polls 4s and falls back to Download',
      (tester) async {
        int launchCount = 0;
        HardwareService.agentUriLauncher = () async {
          launchCount++;
          return true;
        };

        HardwareService.setMockHardwareState(
          enabled: false,
          serverOnline: false,
          agentInstalled: true,
        );

        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(body: MicroscopeScanScreen()),
          ),
        );
        // Let async _checkServer complete.
        await tester.pump(const Duration(milliseconds: 100));
        await tester.pump(const Duration(milliseconds: 100));

        // Verify microscope setting auto-enabled (never dead-ends on blank disabled view).
        expect(await HardwareService.isMicroscopeConfigured(), isTrue);

        final wakeText = find.textContaining('Wake Up Microscope Helper');
        expect(wakeText, findsOneWidget);

        final wakeButtonFinder = find.ancestor(
          of: wakeText,
          matching: find.byWidgetPredicate((w) => w is ElevatedButton),
        );
        expect(wakeButtonFinder, findsOneWidget);
        expect(tester.getSize(wakeButtonFinder).height, greaterThanOrEqualTo(56.0));

        // Tap Wake button -> fires URI scheme launch and polls 8x500ms (4.0s).
        await tester.tap(wakeText);
        await tester.pump();
        expect(launchCount, 1);
        expect(HardwareService.lastLaunchedAgentUri?.scheme, 'numista-agent');

        for (int i = 0; i < 9; i++) {
          await tester.pump(const Duration(milliseconds: 500));
        }

        // Fallback download button appears cleanly after 4.0s timeout.
        expect(find.textContaining('Download Microscope Helper'), findsOneWidget);

        // Dispose widget cleanly so pulse controller & rescue timers cancel.
        await tester.pumpWidget(const SizedBox.shrink());
        MorganProactiveRescueObserver.instance.resetForTesting();
        await tester.pump();
      },
    );

    testWidgets(
      'displays real DirectShow USB camera names and excludes blocked Phone Link virtual camera',
      (tester) async {
        HardwareService.setMockHardwareState(
          enabled: true,
          serverOnline: true,
          agentInstalled: true,
          activeCameraIdx: 2,
          cameraDetails: const [
            {
              'index': 0,
              'name': 'Phone Link Virtual Camera',
              'kind': 'phone_virtual',
              'is_recommended': false,
              'blocked': true,
            },
            {
              'index': 1,
              'name': 'Integrated Camera',
              'kind': 'integrated_webcam',
              'is_recommended': false,
              'blocked': false,
            },
            {
              'index': 2,
              'name': 'USB2.0 PC CAMERA',
              'kind': 'usb_microscope',
              'is_recommended': true,
              'blocked': false,
            },
          ],
        );

        await tester.pumpWidget(
          const MaterialApp(
            home: Scaffold(body: MicroscopeScanScreen()),
          ),
        );
        await tester.pump(const Duration(milliseconds: 150));
        await tester.pump(const Duration(milliseconds: 150));

        expect(find.textContaining('USB2.0 PC CAMERA'), findsWidgets);
        expect(find.textContaining('Phone Link Virtual Camera'), findsNothing);

        // Dispose to cancel periodic 500ms poll timer before FakeAsync invariant check.
        await tester.pumpWidget(const SizedBox.shrink());
        MorganProactiveRescueObserver.instance.resetForTesting();
        await tester.pump();
      },
    );
  });
}
