import 'package:flutter/foundation.dart';
import 'hardware_service.dart';
import 'morgan_trace_bridge_stub.dart'
    if (dart.library.js_interop) 'morgan_trace_bridge_web.dart';

typedef MorganVoiceInjectionHook = Future<void> Function(
  String transcript, {
  bool duringTtsPlayback,
  int delayAfterTtsMs,
  double confidence,
});

/// Deterministic test harness for Playwright / Grok Bot automated testing (§13.5).
///
/// Strictly compiled/activated ONLY in debug/profile or `--dart-define=MORGAN_TEST_HARNESS=true`
/// non-release builds; hard-disabled in release mode (`kReleaseMode == true`).
class MorganTestHarness {
  MorganTestHarness._();

  static const bool _defineFlag = bool.fromEnvironment('MORGAN_TEST_HARNESS');

  /// Test override for unit/widget tests running in debug VM.
  @visibleForTesting
  static bool? debugEnabledOverride;

  /// True only in non-release builds when debug mode or `MORGAN_TEST_HARNESS` is active.
  static bool get isEnabled {
    if (kReleaseMode) {
      return false;
    }
    if (debugEnabledOverride != null) {
      return debugEnabledOverride!;
    }
    return kDebugMode || _defineFlag;
  }

  static Map<String, dynamic>? _lastTrace;
  static final List<Map<String, dynamic>> _traceHistory =
      <Map<String, dynamic>>[];

  static MorganVoiceInjectionHook? voiceInjectionHook;

  static Map<String, dynamic>? get lastTrace => _lastTrace;
  static List<Map<String, dynamic>> get traceHistory =>
      List<Map<String, dynamic>>.unmodifiable(_traceHistory);

  /// Hook 1 (§13.5): Inject synthetic DirectShow cameras, offline/online state,
  /// and deterministic Laplacian sharpness without physical hardware.
  static void setMockHardwareState({
    bool serverOnline = false,
    bool? agentInstalled,
    List<Map<String, dynamic>>? cameraDetails,
    int activeCameraIdx = -1,
    double sharpness = 0.0,
    String? scanStep,
    String? lastError,
  }) {
    if (!isEnabled) {
      throw StateError('MorganTestHarness is disabled in production builds.');
    }
    HardwareService.setMockHardwareState(
      enabled: true,
      serverOnline: serverOnline,
      agentInstalled: agentInstalled,
      cameraDetails: cameraDetails,
      activeCameraIdx: activeCameraIdx,
      sharpness: sharpness,
      scanStep: scanStep,
      lastError: lastError,
    );
    HardwareService.publishMicroscopeState({
      'isHydrated': true,
      'microscopeConfigured': true,
      'serverOnline': serverOnline,
      'agentInstalledBefore': ?agentInstalled,
      'availableCameras': ?cameraDetails,
      'activeCameraIdx': activeCameraIdx,
      'sharpness': sharpness,
      'scanStep': ?scanStep,
      'lastError': lastError,
    });
  }

  /// Hook 2 (§13.5): Feed synthetic voice utterances with deterministic TTS timing.
  static Future<void> injectVoiceUtterance(
    String transcript, {
    bool duringTtsPlayback = false,
    int delayAfterTtsMs = 500,
    double confidence = 0.92,
  }) async {
    if (!isEnabled) {
      throw StateError('MorganTestHarness is disabled in production builds.');
    }
    final hook = voiceInjectionHook;
    if (hook != null) {
      await hook(
        transcript,
        duringTtsPlayback: duringTtsPlayback,
        delayAfterTtsMs: delayAfterTtsMs,
        confidence: confidence,
      );
    }
  }

  /// Hook 3 (§13.5): Record structured turn trace & publish to `window.__MORGAN_LAST_TRACE__`.
  static void recordTrace(Map<String, dynamic> trace) {
    final copy = Map<String, dynamic>.from(trace);
    _lastTrace = copy;
    _traceHistory.add(copy);
    if (_traceHistory.length > 100) {
      _traceHistory.removeAt(0);
    }
    if (isEnabled) {
      publishLastTraceToWindow(copy);
    }
  }

  static void reset() {
    _lastTrace = null;
    _traceHistory.clear();
    HardwareService.clearMockHardwareState();
  }
}
