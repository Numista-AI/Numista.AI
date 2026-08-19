// lib/services/feedback_trigger_observer.dart
//
// Singleton that receives named service events and decides whether to open
// the MORGAN feedback drawer or the fallback form.
//
// Events are emitted by existing services (scan, import, add-coin flow, etc.)
// via FeedbackTriggerObserver.instance.fire(...).

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'beta_feedback_service.dart';
import '../constants/feedback_constants.dart';

// ---------------------------------------------------------------------------
// Event
// ---------------------------------------------------------------------------

class FeedbackTriggerEvent {
  final FeedbackTriggerReason reason;
  final String route;
  final String pageTitle;
  final String userName;

  const FeedbackTriggerEvent({
    required this.reason,
    required this.route,
    required this.pageTitle,
    required this.userName,
  });
}

// ---------------------------------------------------------------------------
// App-state flags (set by the widgets/services that own each state)
// ---------------------------------------------------------------------------

class FeedbackBlockState {
  FeedbackBlockState._();

  static bool importInProgress = false;
  static bool hardwareCaptureActive = false; // set by numista_hardware listener when wired (Phase 3)
  static bool pcgsScanActive = false;
  static bool slabLookupPending = false;
}

// ---------------------------------------------------------------------------
// Callback types
// ---------------------------------------------------------------------------

typedef OpenDrawerCallback = void Function(
  FeedbackTriggerEvent event,
  CheckResult checkResult,
);
typedef OpenFallbackCallback = void Function(
  FeedbackTriggerEvent event,
  String? message,
);

// ---------------------------------------------------------------------------
// Observer
// ---------------------------------------------------------------------------

class FeedbackTriggerObserver {
  FeedbackTriggerObserver._();
  static final FeedbackTriggerObserver instance = FeedbackTriggerObserver._();

  // ── Drawer state (source of truth for loop guard) ────────────────────────
  bool _drawerOpen = false;
  bool get drawerOpen => _drawerOpen;

  void setDrawerOpen(bool open) {
    _drawerOpen = open;
  }

  // ── Callbacks registered by FeedbackDrawerOverlay ────────────────────────
  OpenDrawerCallback? _onOpenDrawer;
  OpenFallbackCallback? _onOpenFallback;

  void registerCallbacks({
    required OpenDrawerCallback onOpenDrawer,
    required OpenFallbackCallback onOpenFallback,
  }) {
    _onOpenDrawer = onOpenDrawer;
    _onOpenFallback = onOpenFallback;
  }

  // ── Pending milestone queue (delivered at next-idle) ─────────────────────
  FeedbackTriggerEvent? _pendingMilestone;
  Timer? _idleTimer;

  // ── Primary entry point ──────────────────────────────────────────────────

  /// Called by FAB and service events to request a feedback session.
  Future<void> fire(FeedbackTriggerEvent event) async {
    // 1. Loop guard — drawer is already open
    if (_drawerOpen) {
      debugPrint('[FeedbackTrigger] Suppressed — drawer already open.');
      return;
    }

    // 2. Loop guard — trigger source IS the feedback drawer itself
    //    Guard on route only for known drawer route names (belt and suspenders).
    if (event.route.contains('feedback') || event.route.contains('morgan_drawer')) {
      debugPrint('[FeedbackTrigger] Loop guard — source is feedback context, fallback only.');
      _onOpenFallback?.call(event, null);
      return;
    }

    // 3. Blocked contexts
    if (_isBlocked(event.reason)) {
      debugPrint('[FeedbackTrigger] Suppressed — blocked context active.');
      return;
    }

    // 4. Milestone events queue to next-idle
    if (event.reason == FeedbackTriggerReason.milestoneAchieved) {
      _queueMilestoneAtNextIdle(event);
      return;
    }

    // 5. Call CHECK mode callable
    await _checkAndOpen(event);
  }

  // ── Internal helpers ─────────────────────────────────────────────────────

  bool _isBlocked(FeedbackTriggerReason reason) {
    return FeedbackBlockState.importInProgress ||
        FeedbackBlockState.hardwareCaptureActive ||
        FeedbackBlockState.pcgsScanActive ||
        FeedbackBlockState.slabLookupPending;
  }

  Future<void> _checkAndOpen(FeedbackTriggerEvent event) async {
    CheckResult result;
    try {
      result = await BetaFeedbackService.checkThrottle(event.reason);
    } catch (e) {
      debugPrint('[FeedbackTrigger] CHECK failed: $e — suppressing.');
      return;
    }

    if (!result.allowed) {
      // Throttled or locked — silent no-op for behavioral triggers
      debugPrint('[FeedbackTrigger] CHECK denied: ${result.reason}');
      return;
    }

    if (!result.interviewMode) {
      // Rate-limited — open fallback with friendly message
      _onOpenFallback?.call(
        event,
        "You've had a few conversations today — file a quick note instead.",
      );
      return;
    }

    // Interview allowed — open the drawer
    _onOpenDrawer?.call(event, result);
  }

  void _queueMilestoneAtNextIdle(FeedbackTriggerEvent event) {
    _pendingMilestone = event;
    _idleTimer?.cancel();
    _idleTimer = Timer(
      Duration(milliseconds: FeedbackConstants.kNextIdleMinQuietMs),
      () async {
        if (_pendingMilestone == null) return;
        if (_drawerOpen || _isBlocked(event.reason)) {
          // Not idle yet — reschedule
          _queueMilestoneAtNextIdle(_pendingMilestone!);
          return;
        }
        final pending = _pendingMilestone!;
        _pendingMilestone = null;
        await _checkAndOpen(pending);
      },
    );
  }
}
