// lib/widgets/beta_feedback_widget.dart
//
// Draggable FAB for beta feedback.
// Sits inside base_layout.dart's Stack as a Positioned child.
// Uses right/bottom offsets (relative to Stack edges) — no LayoutBuilder,
// no MediaQuery size. Positioned is a ParentDataWidget; it must be a
// direct Stack descendant to work; wrapping it in LayoutBuilder breaks that.

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
  // Offsets from the Stack's right and bottom edges.
  // Null = default position. Positioned handles clamping implicitly.
  double? _right;
  double? _bottom;

  static const double _defaultRight = 16.0;
  static const double _defaultBottom = 80.0;

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
    if (!AuthService.isBetaTester && !AuthService.isGuest) {
      return const SizedBox.shrink();
    }

    // Return Positioned directly — no LayoutBuilder wrapper.
    // Positioned is a ParentDataWidget<StackParentData>; it must be a
    // descendant of a Stack to apply positioning. LayoutBuilder would
    // intercept applyParentData, silently breaking the Stack relationship.
    return Positioned(
      right: _right ?? _defaultRight,
      bottom: _bottom ?? _defaultBottom,
      child: GestureDetector(
        onPanUpdate: (details) {
          setState(() {
            // right decreases when moving right, increases when moving left
            _right = ((_right ?? _defaultRight) - details.delta.dx)
                .clamp(0.0, 500.0);
            // bottom decreases when moving down, increases when moving up
            _bottom = ((_bottom ?? _defaultBottom) - details.delta.dy)
                .clamp(0.0, 700.0);
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
  }
}
