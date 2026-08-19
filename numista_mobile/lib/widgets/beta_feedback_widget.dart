// lib/widgets/beta_feedback_widget.dart
//
// Draggable FAB button for beta feedback.
// Visible only to beta testers and guest mode users.
// Tapping the FAB fires FeedbackTriggerObserver with reason: manualFAB —
// the observer calls CHECK and opens the MORGAN drawer or fallback form.
// Auto-capture and showModalBottomSheet have been removed.

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
  double? _posX;
  double? _posY;

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

    final screenSize = MediaQuery.of(context).size;
    final defaultX = screenSize.width - 150;
    final defaultY = screenSize.height - 130;

    final curX = (_posX ?? defaultX)
        .clamp(10.0, (screenSize.width - 140).clamp(10.0, double.infinity));
    final curY = (_posY ?? defaultY)
        .clamp(60.0, (screenSize.height - 80).clamp(60.0, double.infinity));

    return Positioned(
      left: curX,
      top: curY,
      child: GestureDetector(
        onPanUpdate: (details) {
          setState(() {
            _posX = curX + details.delta.dx;
            _posY = curY + details.delta.dy;
          });
        },
        onPanEnd: (details) {
          final midX = screenSize.width / 2;
          final snapX = (curX < midX) ? 16.0 : (screenSize.width - 144.0);
          setState(() {
            _posX = snapX;
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
