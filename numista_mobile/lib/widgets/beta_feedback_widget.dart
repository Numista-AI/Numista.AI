// lib/widgets/beta_feedback_widget.dart
//
// Draggable FAB button for beta feedback.
// Visible only to beta testers and guest mode users.
// Tapping the FAB fires FeedbackTriggerObserver with reason: manualFAB —
// the observer calls CHECK and opens the MORGAN drawer or fallback form.

import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../services/feedback_trigger_observer.dart';
import '../services/beta_feedback_service.dart' show FeedbackTriggerReason;

class BetaFeedbackWidget extends StatefulWidget {
  final String currentRoute;
  final String pageTitle;

  const BetaFeedbackWidget({
    super.key,
    required this.currentRoute,
    required this.pageTitle,
  });

  @override
  State<BetaFeedbackWidget> createState() => _BetaFeedbackWidgetState();
}

class _BetaFeedbackWidgetState extends State<BetaFeedbackWidget> {
  // Offset from the anchor corner. null = use default position.
  // We track as (dx from right, dy from bottom) so the default
  // position is stable regardless of Scaffold body height.
  double? _offsetRight;
  double? _offsetBottom;

  static const double _defaultRight = 16;
  static const double _defaultBottom = 80;
  static const double _fabWidth = 140;
  static const double _fabHeight = 48;

  void _openFeedbackDrawer() {
    FeedbackTriggerObserver.instance.fire(
      FeedbackTriggerEvent(
        reason: FeedbackTriggerReason.manualFAB,
        route: widget.currentRoute,
        pageTitle: widget.pageTitle,
        userName: AuthService.displayName,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Only render for beta testers or guest mode
    if (!AuthService.isBetaTester && !AuthService.isGuest) {
      return const SizedBox.shrink();
    }

    // LayoutBuilder gives us the Stack's actual paint size, not the screen size.
    return LayoutBuilder(builder: (context, constraints) {
      final w = constraints.maxWidth;
      final h = constraints.maxHeight;

      // Current right/bottom offsets (clamped so FAB stays on-screen)
      final right = (_offsetRight ?? _defaultRight)
          .clamp(0.0, (w - _fabWidth).clamp(0.0, double.infinity));
      final bottom = (_offsetBottom ?? _defaultBottom)
          .clamp(0.0, (h - _fabHeight).clamp(0.0, double.infinity));

      return Positioned(
        right: right,
        bottom: bottom,
        child: GestureDetector(
          onPanUpdate: (details) {
            setState(() {
              // Moving right → decrease right offset; moving left → increase it
              _offsetRight = (right - details.delta.dx)
                  .clamp(0.0, (w - _fabWidth).clamp(0.0, double.infinity));
              _offsetBottom = (bottom - details.delta.dy)
                  .clamp(0.0, (h - _fabHeight).clamp(0.0, double.infinity));
            });
          },
          onPanEnd: (_) {
            // Snap to nearest vertical edge
            final mid = w / 2;
            final curLeft = w - right - _fabWidth;
            setState(() {
              _offsetRight =
                  curLeft < mid ? (w - _fabWidth - 16) : _defaultRight;
            });
          },
          child: Material(
            color: Colors.transparent,
            child: FloatingActionButton.extended(
              heroTag: 'beta_feedback_fab',
              backgroundColor: const Color(0xFF2563EB),
              elevation: 8,
              icon: const Icon(Icons.rate_review_outlined, color: Colors.white),
              label: const Text(
                'Feedback',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.5,
                ),
              ),
              onPressed: _openFeedbackDrawer,
            ),
          ),
        ),
      );
    });
  }
}
