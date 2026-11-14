import 'dart:async';
import 'dart:ui' as ui;
import 'package:flutter/foundation.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/widgets.dart';
import 'package:image/image.dart' as img;
import '../widgets/morgan_privacy_mask.dart';
import 'hardware_service.dart';

/// Describes a live UI control registered for Morgan Co-Pilot targeting & action.
class MorganUiTarget {
  final String id;
  final String label;
  final bool isEnabled;
  final GlobalKey? key;
  final Future<void> Function([Map<String, dynamic>? params])? onInvoke;

  const MorganUiTarget({
    required this.id,
    required this.label,
    this.isEnabled = true,
    this.key,
    this.onInvoke,
  });

  Map<String, dynamic> toSummaryJson() => <String, dynamic>{
        'id': id,
        'label': label,
        'isEnabled': isEnabled,
      };
}

class MorganScreenshotResult {
  final Uint8List? bytes;
  final bool blocked;
  final bool debounced;
  final String? blockReason;

  const MorganScreenshotResult({
    this.bytes,
    this.blocked = false,
    this.debounced = false,
    this.blockReason,
  });
}

/// Singleton registry tracking live active route, hydration status, targets,
/// telemetry, and privacy-respecting screenshot capture (§7.1).
class MorganScreenStateRegistry extends ChangeNotifier {
  static final MorganScreenStateRegistry instance =
      MorganScreenStateRegistry._();

  MorganScreenStateRegistry._() {
    HardwareService.liveMicroscopeState.addListener(_onHardwareStateChanged);
  }

  String currentRoute = 'Home Dashboard';
  String activeSubTab = '';
  bool isScreenHydrated = true;
  final Map<String, MorganUiTarget> visibleTargets =
      <String, MorganUiTarget>{};
  Map<String, dynamic> screenContextData = <String, dynamic>{};

  GlobalKey? repaintBoundaryKey;
  bool allowVisionCapture = true;
  bool visionConsentAccepted = true;
  DateTime? _lastScreenshotAt;

  @visibleForTesting
  Future<Uint8List?> Function()? mockScreenshotCapture;

  @visibleForTesting
  DateTime Function() nowProvider = DateTime.now;

  void _onHardwareStateChanged() {
    final hwState = HardwareService.liveMicroscopeState.value;
    if (currentRoute == 'Microscope Scanner') {
      screenContextData = Map<String, dynamic>.from(hwState);
      isScreenHydrated = hwState['isHydrated'] == true;
      for (final entry in HardwareService.registeredUiInvokers.entries) {
        final keyObj = HardwareService.registeredUiKeys[entry.key];
        visibleTargets[entry.key] = MorganUiTarget(
          id: entry.key,
          label: entry.key,
          isEnabled: true,
          key: keyObj is GlobalKey ? keyObj : null,
          onInvoke: entry.value,
        );
      }
      notifyListeners();
    }
  }

  /// Marks the start of a navigation transition; resets hydration until screen settles.
  void beginRouteTransition(
    String route, {
    String subTab = '',
    bool hydratedImmediately = false,
  }) {
    currentRoute = route;
    activeSubTab = subTab;
    isScreenHydrated = hydratedImmediately;
    visibleTargets.clear();
    screenContextData = <String, dynamic>{};
    if (route == 'Microscope Scanner') {
      _onHardwareStateChanged();
    } else {
      notifyListeners();
    }
  }

  /// Marks the current screen as hydrated and publishes its context & targets.
  void markScreenHydrated({
    String? route,
    String? subTab,
    bool hydrated = true,
    Map<String, dynamic>? contextPatch,
    List<MorganUiTarget>? targets,
  }) {
    if (route != null) {
      currentRoute = route;
    }
    if (subTab != null) {
      activeSubTab = subTab;
    }
    isScreenHydrated = hydrated;
    if (contextPatch != null) {
      screenContextData = Map<String, dynamic>.from(screenContextData)
        ..addAll(contextPatch);
    }
    if (targets != null) {
      for (final t in targets) {
        visibleTargets[t.id] = t;
      }
    }
    notifyListeners();
  }

  void registerTarget(MorganUiTarget target) {
    visibleTargets[target.id] = target;
    notifyListeners();
  }

  void updateContextData(Map<String, dynamic> patch) {
    screenContextData = Map<String, dynamic>.from(screenContextData)
      ..addAll(patch);
    notifyListeners();
  }

  /// Async readiness barrier (§7.1 / MF-3): resolves once `isScreenHydrated` is
  /// true and (if [targetId] is non-null) `visibleTargets[targetId]?.isEnabled`
  /// is true, or returns `null` if [timeout] elapses first.
  Future<MorganUiTarget?> waitForTargetReady(
    String targetId, {
    Duration timeout = const Duration(seconds: 5),
  }) async {
    final existing = visibleTargets[targetId];
    if (isScreenHydrated && existing != null && existing.isEnabled) {
      return existing;
    }

    final completer = Completer<MorganUiTarget?>();
    late final VoidCallback listener;
    late final Timer timer;

    listener = () {
      final candidate = visibleTargets[targetId];
      if (isScreenHydrated &&
          candidate != null &&
          candidate.isEnabled &&
          !completer.isCompleted) {
        timer.cancel();
        removeListener(listener);
        completer.complete(candidate);
      }
    };

    timer = Timer(timeout, () {
      if (!completer.isCompleted) {
        removeListener(listener);
        completer.complete(null);
      }
    });

    addListener(listener);
    return completer.future;
  }

  /// Waits until `isScreenHydrated == true` without requiring a specific button target.
  Future<bool> waitForHydration({
    Duration timeout = const Duration(seconds: 5),
  }) async {
    if (isScreenHydrated) return true;
    final completer = Completer<bool>();
    late final VoidCallback listener;
    late final Timer timer;

    listener = () {
      if (isScreenHydrated && !completer.isCompleted) {
        timer.cancel();
        removeListener(listener);
        completer.complete(true);
      }
    };

    timer = Timer(timeout, () {
      if (!completer.isCompleted) {
        removeListener(listener);
        completer.complete(false);
      }
    });

    addListener(listener);
    return completer.future;
  }

  /// Compact JSON payload transmitted to Tier 1 `/api/morgan/copilot`.
  Map<String, dynamic> toCompactJson() {
    final masked = MorganPrivacyMask.isRouteSensitive(currentRoute) ||
        MorganPrivacyMask.hasActiveMasks;
    return <String, dynamic>{
      'current_route': currentRoute,
      'active_sub_tab': activeSubTab,
      'is_screen_hydrated': isScreenHydrated,
      'privacy_mask_active': masked,
      'visible_targets': visibleTargets.values
          .map((t) => t.toSummaryJson())
          .toList(growable: false),
      'screen_context_data': masked
          ? <String, dynamic>{'redacted': true}
          : Map<String, dynamic>.from(screenContextData),
    };
  }

  /// Captures a debounced (`>= 3.0s`), `<= 800px`-wide JPEG (quality 70) frame
  /// from [repaintBoundaryKey], hard-blocked whenever `MorganPrivacyMask` is active.
  Future<MorganScreenshotResult> captureAppScreenshot({
    bool forceBypassDebounce = false,
  }) async {
    if (MorganPrivacyMask.isRouteSensitive(currentRoute) ||
        MorganPrivacyMask.hasActiveMasks) {
      return const MorganScreenshotResult(
        blocked: true,
        blockReason: 'privacy_mask_active',
      );
    }

    if (!allowVisionCapture || !visionConsentAccepted) {
      return const MorganScreenshotResult(
        blocked: true,
        blockReason: 'vision_disabled_by_user',
      );
    }

    final now = nowProvider();
    if (!forceBypassDebounce &&
        _lastScreenshotAt != null &&
        now.difference(_lastScreenshotAt!) < const Duration(seconds: 3)) {
      return const MorganScreenshotResult(
        debounced: true,
        blockReason: 'debounce_active',
      );
    }

    final mockHook = mockScreenshotCapture;
    if (mockHook != null) {
      final bytes = await mockHook();
      _lastScreenshotAt = now;
      return MorganScreenshotResult(bytes: bytes);
    }

    final renderObject =
        repaintBoundaryKey?.currentContext?.findRenderObject();
    if (renderObject is! RenderRepaintBoundary) {
      return const MorganScreenshotResult(
        blocked: true,
        blockReason: 'repaint_boundary_unavailable',
      );
    }

    try {
      final ui.Image rawImage = await renderObject.toImage(pixelRatio: 1.0);
      final byteData =
          await rawImage.toByteData(format: ui.ImageByteFormat.png);
      rawImage.dispose();
      if (byteData == null) {
        return const MorganScreenshotResult(
          blocked: true,
          blockReason: 'image_encode_failed',
        );
      }

      final pngBytes = byteData.buffer.asUint8List();
      final decoded = img.decodePng(pngBytes);
      if (decoded == null) {
        return const MorganScreenshotResult(
          blocked: true,
          blockReason: 'png_decode_failed',
        );
      }
      final resized = decoded.width > 800
          ? img.copyResize(decoded, width: 800)
          : decoded;
      final jpg = Uint8List.fromList(img.encodeJpg(resized, quality: 70));
      _lastScreenshotAt = now;
      return MorganScreenshotResult(bytes: jpg);
    } catch (e) {
      debugPrint('[MorganRegistry] captureAppScreenshot failed: $e');
      return const MorganScreenshotResult(
        blocked: true,
        blockReason: 'capture_exception',
      );
    }
  }

  @visibleForTesting
  void resetForTesting() {
    currentRoute = 'Home Dashboard';
    activeSubTab = '';
    isScreenHydrated = true;
    visibleTargets.clear();
    screenContextData.clear();
    allowVisionCapture = true;
    visionConsentAccepted = true;
    _lastScreenshotAt = null;
    mockScreenshotCapture = null;
    nowProvider = DateTime.now;
    notifyListeners();
  }
}
