import 'dart:async';
import 'package:flutter/foundation.dart';
import 'hardware_service.dart';
import 'morgan_action_bus.dart';
import 'morgan_screen_state_registry.dart';
import 'tts_voice_service.dart';

enum MorganRescueSeverity { hardwareImmediate, stallForm25s, stallPhysical45s }

class MorganRescuePrompt {
  final String stepKey;
  final MorganRescueSeverity severity;
  final String title;
  final String message;
  final String fixButtonLabel;
  final List<MorganActionCommand> suggestedActions;
  final bool showWakeAgentButton;

  const MorganRescuePrompt({
    required this.stepKey,
    required this.severity,
    required this.title,
    required this.message,
    this.fixButtonLabel = 'Fix It For Me',
    this.suggestedActions = const [],
    this.showWakeAgentButton = false,
  });
}

/// Watches route hydration, hardware state, and user idle intervals to trigger
/// senior-friendly, non-intrusive proactive Morgan guidance (§7.5).
class MorganProactiveRescueObserver extends ChangeNotifier {
  static final MorganProactiveRescueObserver instance =
      MorganProactiveRescueObserver._();

  MorganProactiveRescueObserver._() {
    MorganScreenStateRegistry.instance.addListener(_evaluateState);
  }

  static const Duration immediateDelay = Duration(seconds: 1);
  static const Duration standardStallDelay = Duration(seconds: 25);
  static const Duration physicalStallDelay = Duration(seconds: 45);

  bool _sessionPausedByUser = false;
  bool isPhysicalHandlingActive = false;
  MorganRescuePrompt? _activePrompt;
  final Set<String> _firedSteps = <String>{};

  Timer? _immediateTimer;
  Timer? _stallTimer;

  @visibleForTesting
  Duration? standardStallOverride;
  @visibleForTesting
  Duration? physicalStallOverride;
  @visibleForTesting
  Duration? immediateDelayOverride;

  bool get sessionPausedByUser => _sessionPausedByUser;
  MorganRescuePrompt? get activePrompt => _activePrompt;

  Duration get _effectiveImmediateDelay =>
      immediateDelayOverride ?? immediateDelay;
  Duration get _effectiveStallDelay {
    final reg = MorganScreenStateRegistry.instance;
    final isPhysical =
        isPhysicalHandlingActive || reg.currentRoute == 'Microscope Scanner';
    if (isPhysical) {
      return physicalStallOverride ?? physicalStallDelay;
    }
    return standardStallOverride ?? standardStallDelay;
  }

  String _currentStepKey() {
    final reg = MorganScreenStateRegistry.instance;
    final err = reg.screenContextData['lastError']?.toString() ?? '';
    return '${reg.currentRoute}::${reg.activeSubTab}::$err';
  }

  /// Called on any pointer, scroll, keyboard, or voice activity.
  void recordUserActivity() {
    if (_sessionPausedByUser) return;
    _restartStallTimer();
  }

  void pauseForSession() {
    _sessionPausedByUser = true;
    _immediateTimer?.cancel();
    _stallTimer?.cancel();
    _activePrompt = null;
    notifyListeners();
  }

  void resumeForSession() {
    _sessionPausedByUser = false;
    _restartStallTimer();
    _evaluateState();
  }

  void dismissActivePrompt() {
    _activePrompt = null;
    notifyListeners();
  }

  /// Runs the suggested recovery actions or wakes the desktop agent on tap.
  Future<void> triggerFixItForMe() async {
    final prompt = _activePrompt;
    if (prompt == null) return;
    _activePrompt = null;
    notifyListeners();

    if (prompt.showWakeAgentButton) {
      final invoker =
          HardwareService.registeredUiInvokers['btn_wake_microscope_agent'];
      if (invoker != null) {
        await invoker();
        return;
      }
      HardwareService.launchDesktopAgent();
      return;
    }

    if (prompt.suggestedActions.isNotEmpty) {
      await MorganActionBus.instance.executeTurn(
        commands: prompt.suggestedActions,
        tierUsed: 1,
      );
    }
  }

  void _evaluateState() {
    if (_sessionPausedByUser) return;

    final reg = MorganScreenStateRegistry.instance;
    if (!reg.isScreenHydrated) return;

    final data = reg.screenContextData;
    final route = reg.currentRoute;

    // 1. Hardware Mismatch / Error (< 2s immediate intervention, one-shot per step).
    if (route == 'Microscope Scanner') {
      if (data['microscopeConfigured'] == false) {
        HardwareService.setMicroscopeConfigured(true);
      }

      // Auto-switch from Phone Link or webcam if a USB microscope is connected.
      final rawCams = data['availableCameras'];
      final activeIdx = data['activeCameraIdx'] as int? ?? -1;
      if (data['serverOnline'] == true && rawCams is List) {
        final cams =
            rawCams.whereType<Map>().map((m) => Map<String, dynamic>.from(m));
        final activeCam =
            cams.where((c) => c['index'] == activeIdx).toList();
        final usbCam =
            cams.where((c) => c['is_recommended'] == true && c['blocked'] != true).toList();
        if (usbCam.isNotEmpty &&
            (activeCam.isEmpty ||
                activeCam.first['blocked'] == true ||
                activeCam.first['kind'] != 'usb_microscope')) {
          final targetIdx = usbCam.first['index'] as int? ?? -1;
          final invoker =
              HardwareService.registeredUiInvokers['set_camera_index'];
          if (targetIdx >= 0 && invoker != null) {
            invoker({'index': targetIdx});
          }
        }
      }

      if (data['serverOnline'] == false) {
        final stepKey = '$route::offline::${data['agentInstalledBefore']}';
        if (!_firedSteps.contains(stepKey)) {
          _scheduleImmediatePrompt(
            MorganRescuePrompt(
              stepKey: stepKey,
              severity: MorganRescueSeverity.hardwareImmediate,
              title: data['agentInstalledBefore'] == true
                  ? 'Microscope Helper Is Asleep'
                  : 'Need Help Connecting Your Microscope?',
              message: data['agentInstalledBefore'] == true
                  ? 'Your Microscope Helper is installed on this PC, just paused. Tap below and I will wake it right up.'
                  : 'I noticed your Microscope Helper is not answering yet. Would you like me to help wake it up or open setup?',
              fixButtonLabel: data['agentInstalledBefore'] == true
                  ? '🔌 Wake Up Microscope Helper'
                  : 'Fix It For Me',
              showWakeAgentButton: data['agentInstalledBefore'] == true,
              suggestedActions: const [
                MorganActionCommand(
                  action: 'spotlight_element',
                  targetId: 'btn_wake_microscope_agent',
                  message: 'Tap here to wake your Microscope Helper.',
                ),
              ],
            ),
          );
          return;
        }
      }
    }

    final lastError = data['lastError']?.toString() ?? '';
    if (lastError.isNotEmpty) {
      final stepKey = '$route::error::$lastError';
      if (!_firedSteps.contains(stepKey)) {
        _scheduleImmediatePrompt(
          MorganRescuePrompt(
            stepKey: stepKey,
            severity: MorganRescueSeverity.hardwareImmediate,
            title: 'I Spotted a Hiccup',
            message:
                'Something didn\'t finish cleanly ($lastError). Would you like me to help fix it?',
          ),
        );
        return;
      }
    }

    _restartStallTimer();
  }

  void _scheduleImmediatePrompt(MorganRescuePrompt prompt) {
    _immediateTimer?.cancel();
    _immediateTimer = Timer(_effectiveImmediateDelay, () {
      _presentIfSafe(prompt);
    });
  }

  void _restartStallTimer() {
    if (_sessionPausedByUser) return;
    _stallTimer?.cancel();
    final delay = _effectiveStallDelay;
    final severity = delay == (physicalStallOverride ?? physicalStallDelay)
        ? MorganRescueSeverity.stallPhysical45s
        : MorganRescueSeverity.stallForm25s;

    _stallTimer = Timer(delay, () {
      final reg = MorganScreenStateRegistry.instance;
      if (_sessionPausedByUser || !reg.isScreenHydrated) return;
      final key = '${_currentStepKey()}::stall';
      if (_firedSteps.contains(key)) return;
      _presentIfSafe(
        MorganRescuePrompt(
          stepKey: key,
          severity: severity,
          title: 'Take Your Time — Need a Hand?',
          message: reg.currentRoute == 'Microscope Scanner'
              ? 'Take all the time you need positioning the coin under the lens. Tap below if you\'d like me to guide the next step.'
              : 'Looks like you paused on ${reg.currentRoute}. Want me to highlight the next button or do it with you?',
        ),
      );
    });
  }

  void _presentIfSafe(MorganRescuePrompt prompt) {
    if (_sessionPausedByUser || _firedSteps.contains(prompt.stepKey)) return;
    if (TtsVoiceService.isSpeakingNotifier.value) {
      // Wait for TTS to finish before popping proactive rescue.
      Future<void>.delayed(const Duration(milliseconds: 500), () {
        _presentIfSafe(prompt);
      });
      return;
    }
    _firedSteps.add(prompt.stepKey);
    _activePrompt = prompt;
    notifyListeners();
  }

  @visibleForTesting
  void resetForTesting() {
    _immediateTimer?.cancel();
    _stallTimer?.cancel();
    _sessionPausedByUser = false;
    isPhysicalHandlingActive = false;
    _activePrompt = null;
    _firedSteps.clear();
    standardStallOverride = null;
    physicalStallOverride = null;
    immediateDelayOverride = null;
    notifyListeners();
  }
}
