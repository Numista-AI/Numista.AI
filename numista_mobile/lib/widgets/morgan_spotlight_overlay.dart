import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

class MorganSpotlightState {
  final String targetId;
  final GlobalKey? targetKey;
  final Rect? fallbackRect;
  final String label;
  final String message;

  const MorganSpotlightState({
    required this.targetId,
    this.targetKey,
    this.fallbackRect,
    required this.label,
    required this.message,
  });
}

/// Manages active spotlight target & viewport scrolling for [MorganSpotlightOverlay].
class MorganSpotlightController extends ChangeNotifier {
  static final MorganSpotlightController instance = MorganSpotlightController._();

  MorganSpotlightController._();

  MorganSpotlightState? _current;
  MorganSpotlightState? get current => _current;
  bool get isActive => _current != null;

  /// Scrolls [targetKey] into view if needed and highlights it cleanly.
  Future<void> show({
    required String targetId,
    GlobalKey? targetKey,
    Rect? fallbackRect,
    required String label,
    required String message,
  }) async {
    final targetCtx = targetKey?.currentContext;
    if (targetCtx != null && targetCtx.mounted) {
      try {
        await Scrollable.ensureVisible(
          targetCtx,
          duration: const Duration(milliseconds: 220),
          alignment: 0.4,
        );
      } catch (_) {
        // Ignore if not inside a Scrollable.
      }
    }
    _current = MorganSpotlightState(
      targetId: targetId,
      targetKey: targetKey,
      fallbackRect: fallbackRect,
      label: label,
      message: message,
    );
    notifyListeners();
  }

  void dismiss() {
    if (_current == null) return;
    _current = null;
    notifyListeners();
  }

  /// Resolves the live global bounding box of the active spotlight target.
  Rect? resolveGlobalRect() {
    final active = _current;
    if (active == null) return null;
    final ctx = active.targetKey?.currentContext;
    if (ctx != null) {
      final ro = ctx.findRenderObject();
      if (ro is RenderBox && ro.hasSize) {
        final offset = ro.localToGlobal(Offset.zero);
        return offset & ro.size;
      }
    }
    return active.fallbackRect;
  }

  /// Resolves target bounding box local to [ancestorRenderBox] when overlaid inside a Stack.
  Rect? resolveLocalRect(RenderBox? ancestorRenderBox) {
    final active = _current;
    if (active == null) return null;
    final ctx = active.targetKey?.currentContext;
    if (ctx != null) {
      final ro = ctx.findRenderObject();
      if (ro is RenderBox && ro.hasSize) {
        final offset = ro.localToGlobal(Offset.zero, ancestor: ancestorRenderBox);
        return offset & ro.size;
      }
    }
    return active.fallbackRect;
  }
}

/// High-contrast WCAG AAA spotlight overlay with dual-halo gold/black cutout ring,
/// Escape dismissal, tap pass-through, and reduced-motion static fallback (§7.3 & §7.8).
class MorganSpotlightOverlay extends StatefulWidget {
  final MorganSpotlightController controller;
  final bool reducedMotionOverride;

  const MorganSpotlightOverlay({
    super.key,
    required this.controller,
    this.reducedMotionOverride = false,
  });

  @override
  State<MorganSpotlightOverlay> createState() => _MorganSpotlightOverlayState();
}

class _MorganSpotlightOverlayState extends State<MorganSpotlightOverlay>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulseController;
  final FocusNode _calloutFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1400),
    );
    widget.controller.addListener(_syncAnimation);
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _syncAnimation();
  }

  void _syncAnimation() {
    if (!mounted) return;
    final reduceMotion =
        widget.reducedMotionOverride || MediaQuery.disableAnimationsOf(context);
    if (widget.controller.isActive && !reduceMotion) {
      if (!_pulseController.isAnimating) {
        _pulseController.repeat(reverse: true);
      }
    } else {
      _pulseController.stop();
      _pulseController.value = 0.0;
    }
    setState(() {});
  }

  @override
  void dispose() {
    widget.controller.removeListener(_syncAnimation);
    _pulseController.dispose();
    _calloutFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = widget.controller.current;
    if (state == null) {
      return const SizedBox.shrink();
    }

    final reduceMotion =
        widget.reducedMotionOverride || MediaQuery.disableAnimationsOf(context);
    final ancestorBox = context.findRenderObject() as RenderBox?;
    final targetRect = widget.controller.resolveLocalRect(ancestorBox);

    if (targetRect == null || targetRect.isEmpty) {
      return const SizedBox.shrink();
    }

    final paddedRect = targetRect.inflate(12);
    final screenSize = MediaQuery.sizeOf(context);

    // Position high-contrast callout cleanly above or below target rect.
    const double badgeWidth = 300;
    final bool placeBelow = paddedRect.bottom + 120 < screenSize.height;
    final double badgeTop = placeBelow
        ? paddedRect.bottom + 12
        : math.max(16, paddedRect.top - 110);
    final double badgeLeft = math.max(
      16,
      math.min(paddedRect.left, screenSize.width - badgeWidth - 16),
    );

    return CallbackShortcuts(
      bindings: <ShortcutActivator, VoidCallback>{
        const SingleActivator(LogicalKeyboardKey.escape): () =>
            widget.controller.dismiss(),
      },
      child: FocusTraversalGroup(
        policy: OrderedTraversalPolicy(),
        child: Listener(
          behavior: HitTestBehavior.translucent,
          onPointerDown: (event) {
            if (paddedRect.contains(event.localPosition)) {
              widget.controller.dismiss();
            }
          },
          child: Stack(
            children: [
              // Backdrop dim + dual-halo gold/black ring (does not swallow clicks on target button).
              Positioned.fill(
                child: IgnorePointer(
                  ignoring: true,
                  child: AnimatedBuilder(
                    animation: _pulseController,
                    builder: (context, _) {
                      final pulseExpand =
                          reduceMotion ? 0.0 : (_pulseController.value * 4.0);
                      return Semantics(
                        identifier: 'morgan_spotlight_ring',
                        label:
                            'Morgan spotlight on ${state.label}: ${state.message}',
                        liveRegion: true,
                        child: CustomPaint(
                          painter: _SpotlightBackdropPainter(
                            cutoutRect: paddedRect,
                            pulseExpand: pulseExpand,
                            isReducedMotion: reduceMotion,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              // High-contrast callout pill (>= 7.0:1 #0F172A on #F5C451 gold).
              Positioned(
                top: badgeTop,
                left: badgeLeft,
                width: badgeWidth,
                child: Material(
                  color: const Color(0xFFF5C451),
                  elevation: 8,
                  borderRadius: BorderRadius.circular(14),
                  child: Container(
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(14),
                      border: Border.all(
                        color: const Color(0xFF000000),
                        width: 2,
                      ),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('🦉 ', style: TextStyle(fontSize: 20)),
                            Expanded(
                              child: Text(
                                state.message,
                                style: const TextStyle(
                                  color: Color(0xFF0F172A),
                                  fontSize: 16,
                                  fontWeight: FontWeight.w700,
                                  height: 1.35,
                                ),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Semantics(
                          identifier: 'morgan_spotlight_dismiss_btn',
                          button: true,
                          label: 'Got it, hide highlight',
                          child: ConstrainedBox(
                            constraints: const BoxConstraints(minHeight: 56),
                            child: ElevatedButton(
                              focusNode: _calloutFocusNode,
                              onPressed: widget.controller.dismiss,
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF0F172A),
                                foregroundColor: const Color(0xFFF8FAFC),
                                textStyle: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              child: const Text('Got It (Esc)'),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SpotlightBackdropPainter extends CustomPainter {
  final Rect cutoutRect;
  final double pulseExpand;
  final bool isReducedMotion;

  const _SpotlightBackdropPainter({
    required this.cutoutRect,
    required this.pulseExpand,
    required this.isReducedMotion,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final fullPath = Path()..addRect(Offset.zero & size);
    final holeRRect = RRect.fromRectAndRadius(
      cutoutRect,
      const Radius.circular(14),
    );
    final holePath = Path()..addRRect(holeRRect);
    final dimPath = Path.combine(PathOperation.difference, fullPath, holePath);

    canvas.drawPath(
      dimPath,
      Paint()..color = Colors.black.withValues(alpha: 0.48),
    );

    // Outer 2px black border + inner 4px #FFD700 gold halo (>= 4.5:1 over dark/light UI).
    final expandedRect = cutoutRect.inflate(isReducedMotion ? 0 : pulseExpand);
    final outerBorder = RRect.fromRectAndRadius(
      expandedRect.inflate(2),
      const Radius.circular(16),
    );
    canvas.drawRRect(
      outerBorder,
      Paint()
        ..color = const Color(0xFF000000)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 2.0,
    );

    final innerGold = RRect.fromRectAndRadius(
      expandedRect,
      const Radius.circular(14),
    );
    canvas.drawRRect(
      innerGold,
      Paint()
        ..color = const Color(0xFFFFD700)
        ..style = PaintingStyle.stroke
        ..strokeWidth = 4.0,
    );
  }

  @override
  bool shouldRepaint(covariant _SpotlightBackdropPainter oldDelegate) {
    return oldDelegate.cutoutRect != cutoutRect ||
        oldDelegate.pulseExpand != pulseExpand ||
        oldDelegate.isReducedMotion != isReducedMotion;
  }
}
