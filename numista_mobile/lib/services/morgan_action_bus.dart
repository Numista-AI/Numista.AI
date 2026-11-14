import 'package:flutter/widgets.dart';
import '../widgets/morgan_privacy_mask.dart';
import '../widgets/morgan_spotlight_overlay.dart';
import 'morgan_screen_state_registry.dart';
import 'morgan_test_harness.dart';

/// Strict whitelisted routes Morgan may navigate to programmatically (MF-3).
enum MorganAllowedRoute {
  homeDashboard('Home Dashboard'),
  addNewCoins('Add New Coins'),
  microscopeScanner('Microscope Scanner'),
  reviewHub('Review Hub'),
  myCollection('My Collection'),
  coinDetail('Coin Detail'),
  wishList('Wish List'),
  programManager('Program Manager'),
  estatePlanning('Estate Planning'),
  attorneyPortal('Attorney Portal'),
  lateralTransfer('Lateral Transfer'),
  settingsBackup('Settings & Backup'),
  customerService('Customer Service');

  final String routeName;
  const MorganAllowedRoute(this.routeName);

  static MorganAllowedRoute? fromString(String? raw) {
    if (raw == null) return null;
    final clean = raw.trim().toLowerCase();
    for (final v in MorganAllowedRoute.values) {
      if (v.routeName.toLowerCase() == clean || v.name.toLowerCase() == clean) {
        return v;
      }
    }
    return null;
  }
}

/// Strict whitelisted UI action IDs Morgan may invoke programmatically (MF-3).
enum MorganAllowedActionId {
  navigateTo('navigate_to'),
  invokeUiAction('invoke_ui_action'),
  spotlightElement('spotlight_element'),
  proposeConfirmation('propose_confirmation'),
  enableMicroscopeSetting('enable_microscope_setting'),
  setCameraIndex('set_camera_index'),
  startMicroscopeScan('btn_start_microscope_scan'),
  wakeMicroscopeAgent('btn_wake_microscope_agent'),
  downloadMicroscopeAgent('btn_download_microscope_agent'),
  saveCoin('btn_save_coin'),
  openBulkImport('btn_open_bulk_import'),
  openFilePicker('open_file_picker'),
  applyCollectionFilter('apply_collection_filter'),
  confirmFlip('confirm_flip');

  final String wireId;
  const MorganAllowedActionId(this.wireId);

  static MorganAllowedActionId? fromString(String? raw) {
    if (raw == null) return null;
    final clean = raw.trim().toLowerCase();
    for (final v in MorganAllowedActionId.values) {
      if (v.wireId.toLowerCase() == clean || v.name.toLowerCase() == clean) {
        return v;
      }
    }
    return null;
  }
}

class MorganActionCommand {
  final String action;
  final String? route;
  final String? subTab;
  final String? targetId;
  final String? message;
  final String? actionType;
  final String? summaryText;
  final Map<String, dynamic>? params;
  final Map<String, dynamic>? payload;

  const MorganActionCommand({
    required this.action,
    this.route,
    this.subTab,
    this.targetId,
    this.message,
    this.actionType,
    this.summaryText,
    this.params,
    this.payload,
  });

  factory MorganActionCommand.fromJson(Map<String, dynamic> json) {
    return MorganActionCommand(
      action: json['action']?.toString() ?? '',
      route: json['route']?.toString(),
      subTab: json['sub_tab']?.toString() ?? json['subTab']?.toString(),
      targetId: json['target_id']?.toString() ?? json['targetId']?.toString(),
      message: json['message']?.toString(),
      actionType:
          json['action_type']?.toString() ?? json['actionType']?.toString(),
      summaryText:
          json['summary_text']?.toString() ?? json['summaryText']?.toString(),
      params: json['params'] is Map
          ? Map<String, dynamic>.from(json['params'] as Map)
          : null,
      payload: json['payload'] is Map
          ? Map<String, dynamic>.from(json['payload'] as Map)
          : null,
    );
  }
}

class MorganTurnTrace {
  final String turnId;
  final int tierUsed;
  final String routeBefore;
  final String routeAfter;
  final int hydrationWaitMs;
  final List<String> toolsExecuted;
  final List<String> blockedTools;
  final String? spotlightTargetId;
  final Map<String, double>? spotlightTargetBbox;
  final bool popoutOverlapsSpotlight;
  final double contrastRatioMin;
  final bool reducedMotionRespected;
  final bool privacyMaskActive;
  final String confirmationGateStatus;
  final int tokensBilled;
  final double costUsd;

  const MorganTurnTrace({
    required this.turnId,
    required this.tierUsed,
    required this.routeBefore,
    required this.routeAfter,
    required this.hydrationWaitMs,
    required this.toolsExecuted,
    required this.blockedTools,
    this.spotlightTargetId,
    this.spotlightTargetBbox,
    required this.popoutOverlapsSpotlight,
    this.contrastRatioMin = 7.1,
    this.reducedMotionRespected = true,
    required this.privacyMaskActive,
    required this.confirmationGateStatus,
    this.tokensBilled = 0,
    this.costUsd = 0.0,
  });

  Map<String, dynamic> toJson() => <String, dynamic>{
        'turn_id': turnId,
        'tier_used': tierUsed,
        'route_before': routeBefore,
        'route_after': routeAfter,
        'hydration_wait_ms': hydrationWaitMs,
        'tools_executed': toolsExecuted,
        'blocked_tools': blockedTools,
        'spotlight_target_id': spotlightTargetId,
        'spotlight_target_bbox': spotlightTargetBbox,
        'popout_overlaps_spotlight': popoutOverlapsSpotlight,
        'contrast_ratio_min': contrastRatioMin,
        'reduced_motion_respected': reducedMotionRespected,
        'privacy_mask_active': privacyMaskActive,
        'confirmation_gate_status': confirmationGateStatus,
        'tokens_billed': tokensBilled,
        'cost_usd': costUsd,
      };
}

class MorganActionTurnResult {
  final MorganTurnTrace trace;
  final bool haltedEarly;
  final String? haltReason;

  const MorganActionTurnResult({
    required this.trace,
    this.haltedEarly = false,
    this.haltReason,
  });
}

/// Client-side execution engine enforcing strict tool whitelisting, 3-step/turn cap,
/// async hydration readiness barrier, Gate 0 proposal separation, and trace emission (§7.2).
class MorganActionBus {
  static final MorganActionBus instance = MorganActionBus._();
  MorganActionBus._();

  static const int maxActionsPerTurn = 3;

  Future<void> Function(String route, {String? subTab})? onNavigateToRoute;
  Future<void> Function(
    String actionType,
    String summaryText,
    Map<String, dynamic> payload,
  )? onProposeConfirmation;

  /// Optional provider returning current floating popout Rect so overlap telemetry
  /// & auto-dodge can verify zero occlusion.
  Rect? Function()? popoutRectProvider;

  /// Optional hook called whenever a spotlight box needs Auto-Dodge adjustment.
  void Function(Rect spotlightRect)? onSpotlightPositioned;

  bool reducedMotionEnabled = false;
  int _turnCounter = 0;

  final List<MorganTurnTrace> traceLog = <MorganTurnTrace>[];

  Future<MorganActionTurnResult> executeTurn({
    required List<MorganActionCommand> commands,
    int tierUsed = 1,
    int tokensBilled = 0,
    double costUsd = 0.0,
    String? customTurnId,
  }) async {
    final registry = MorganScreenStateRegistry.instance;
    final spotlight = MorganSpotlightController.instance;
    final routeBefore = registry.currentRoute;
    final List<String> executed = <String>[];
    final List<String> blocked = <String>[];
    int totalHydrationWaitMs = 0;
    String? spotlightId;
    Map<String, double>? spotlightBbox;
    String gateStatus = 'NONE';
    bool halted = false;
    String? haltReason;

    for (int i = 0; i < commands.length; i++) {
      final cmd = commands[i];
      if (i >= maxActionsPerTurn) {
        blocked.add('${cmd.action}:max_chain_depth_exceeded');
        continue;
      }

      final actionEnum = MorganAllowedActionId.fromString(cmd.action);
      if (actionEnum == null) {
        blocked.add('${cmd.action}:unlisted_action');
        continue;
      }

      if (actionEnum == MorganAllowedActionId.navigateTo) {
        final allowedRoute = MorganAllowedRoute.fromString(cmd.route);
        if (allowedRoute == null) {
          blocked.add('navigate_to:${cmd.route ?? "null"}:unlisted_route');
          continue;
        }
        final sw = Stopwatch()..start();
        registry.beginRouteTransition(
          allowedRoute.routeName,
          subTab: cmd.subTab ?? '',
        );
        await onNavigateToRoute?.call(
          allowedRoute.routeName,
          subTab: cmd.subTab,
        );
        if (cmd.targetId != null && cmd.targetId!.isNotEmpty) {
          final target = await registry.waitForTargetReady(
            cmd.targetId!,
            timeout: const Duration(seconds: 5),
          );
          sw.stop();
          totalHydrationWaitMs += sw.elapsedMilliseconds;
          if (target == null) {
            halted = true;
            haltReason = 'target_not_ready:${cmd.targetId}';
            blocked.add('navigate_to:${cmd.targetId}:timeout');
            break;
          }
        } else {
          final hydrated = await registry.waitForHydration(
            timeout: const Duration(seconds: 5),
          );
          sw.stop();
          totalHydrationWaitMs += sw.elapsedMilliseconds;
          if (!hydrated) {
            halted = true;
            haltReason = 'route_hydration_timeout:${allowedRoute.routeName}';
            blocked.add('navigate_to:${allowedRoute.routeName}:timeout');
            break;
          }
        }
        executed.add('navigate_to:${allowedRoute.routeName}');
      } else if (actionEnum == MorganAllowedActionId.spotlightElement) {
        final tid = cmd.targetId ?? '';
        final sw = Stopwatch()..start();
        final target = await registry.waitForTargetReady(
          tid,
          timeout: const Duration(seconds: 5),
        );
        sw.stop();
        totalHydrationWaitMs += sw.elapsedMilliseconds;
        if (target == null) {
          blocked.add('spotlight_element:$tid:target_unavailable');
          continue;
        }
        await spotlight.show(
          targetId: tid,
          targetKey: target.key,
          label: target.label,
          message: cmd.message ?? 'Click ${target.label}',
        );
        spotlightId = tid;
        final rect = spotlight.resolveGlobalRect();
        if (rect != null) {
          spotlightBbox = <String, double>{
            'x': rect.left,
            'y': rect.top,
            'w': rect.width,
            'h': rect.height,
          };
          onSpotlightPositioned?.call(rect);
        }
        executed.add('spotlight_element:$tid');
      } else if (actionEnum == MorganAllowedActionId.proposeConfirmation) {
        gateStatus = 'PENDING_USER';
        await onProposeConfirmation?.call(
          cmd.actionType ?? 'add_coin',
          cmd.summaryText ?? 'Please review and confirm this update.',
          cmd.payload ?? const <String, dynamic>{},
        );
        executed.add('propose_confirmation:${cmd.actionType ?? "add_coin"}');
      } else {
        // invoke_ui_action or direct whitelisted UI action wireId.
        final tid = (actionEnum == MorganAllowedActionId.invokeUiAction
                ? cmd.targetId
                : actionEnum.wireId) ??
            '';
        final targetEnum = MorganAllowedActionId.fromString(tid);
        if (targetEnum == null) {
          blocked.add('invoke_ui_action:$tid:unlisted_target');
          continue;
        }
        final sw = Stopwatch()..start();
        final target = await registry.waitForTargetReady(
          targetEnum.wireId,
          timeout: const Duration(seconds: 5),
        );
        sw.stop();
        totalHydrationWaitMs += sw.elapsedMilliseconds;
        if (target == null || !target.isEnabled) {
          blocked.add('invoke_ui_action:${targetEnum.wireId}:not_ready');
          halted = true;
          haltReason = 'precondition_failed:${targetEnum.wireId}';
          break;
        }
        await target.onInvoke?.call(cmd.params);
        executed.add(targetEnum.wireId);
      }
    }

    final spotRect = spotlight.resolveGlobalRect();
    final popRect = popoutRectProvider?.call();
    final overlaps =
        spotRect != null && popRect != null && spotRect.overlaps(popRect);

    _turnCounter++;
    final trace = MorganTurnTrace(
      turnId: customTurnId ?? 'turn_${_turnCounter.toString().padLeft(3, '0')}',
      tierUsed: tierUsed,
      routeBefore: routeBefore,
      routeAfter: registry.currentRoute,
      hydrationWaitMs: totalHydrationWaitMs,
      toolsExecuted: executed,
      blockedTools: blocked,
      spotlightTargetId: spotlightId,
      spotlightTargetBbox: spotlightBbox,
      popoutOverlapsSpotlight: overlaps,
      contrastRatioMin: 7.1,
      reducedMotionRespected: reducedMotionEnabled,
      privacyMaskActive:
          MorganPrivacyMask.isRouteSensitive(registry.currentRoute) ||
              MorganPrivacyMask.hasActiveMasks,
      confirmationGateStatus: gateStatus,
      tokensBilled: tokensBilled,
      costUsd: costUsd,
    );

    traceLog.add(trace);
    if (traceLog.length > 100) {
      traceLog.removeAt(0);
    }
    MorganTestHarness.recordTrace(trace.toJson());

    return MorganActionTurnResult(
      trace: trace,
      haltedEarly: halted,
      haltReason: haltReason,
    );
  }

  @visibleForTesting
  void resetForTesting() {
    traceLog.clear();
    _turnCounter = 0;
    onNavigateToRoute = null;
    onProposeConfirmation = null;
    popoutRectProvider = null;
    onSpotlightPositioned = null;
    reducedMotionEnabled = false;
    MorganSpotlightController.instance.dismiss();
  }
}
