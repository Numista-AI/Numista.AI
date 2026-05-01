import 'package:flutter/material.dart';
import '../services/wizard_service.dart';

// ─── WizardOverlay ────────────────────────────────────────────────────────────
// Drop this into a Stack as the last child (so it floats above page content).
// It listens to WizardService.state and animates in/out automatically.
//
// Usage in BaseLayout:
//   Stack(children: [
//     Expanded(child: _buildBody()),
//     WizardOverlay(onCreateAccount: _goToLoginScreen),
//   ])

class WizardOverlay extends StatefulWidget {
  /// Called when the user taps "Create My Free Account" on the final step.
  final VoidCallback? onCreateAccount;

  const WizardOverlay({super.key, this.onCreateAccount});

  @override
  State<WizardOverlay> createState() => _WizardOverlayState();
}

class _WizardOverlayState extends State<WizardOverlay>
    with SingleTickerProviderStateMixin {
  late final AnimationController _controller;
  late final Animation<Offset> _slideAnim;
  late final Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 380),
    );
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.3),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOutCubic));
    _fadeAnim =
        CurvedAnimation(parent: _controller, curve: Curves.easeIn);

    // Animate in whenever the state becomes non-null
    WizardService.state.addListener(_onStateChange);
    if (WizardService.isActive) _controller.forward();
  }

  void _onStateChange() {
    if (!mounted) return;
    if (WizardService.isActive) {
      _controller.forward(from: 0);
    } else {
      _controller.reverse();
    }
  }

  @override
  void dispose() {
    WizardService.state.removeListener(_onStateChange);
    _controller.dispose();
    super.dispose();
  }

  void _handleNext(WizardState wizardState) {
    if (wizardState.isLastStep) {
      WizardService.dismiss(completed: true);
      widget.onCreateAccount?.call();
    } else {
      WizardService.nextStep();
    }
  }

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<WizardState?>(
      valueListenable: WizardService.state,
      builder: (context, wizardState, _) {
        if (wizardState == null) return const SizedBox.shrink();

        return Positioned(
          bottom: 32,
          right: 32,
          width: 390,
          child: SlideTransition(
            position: _slideAnim,
            child: FadeTransition(
              opacity: _fadeAnim,
              child: _WizardCard(
                state: wizardState,
                onNext: () => _handleNext(wizardState),
                onSkip: () => WizardService.dismiss(),
              ),
            ),
          ),
        );
      },
    );
  }
}

// ─── Card UI ──────────────────────────────────────────────────────────────────

class _WizardCard extends StatelessWidget {
  final WizardState state;
  final VoidCallback onNext;
  final VoidCallback onSkip;

  const _WizardCard({
    required this.state,
    required this.onNext,
    required this.onSkip,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      elevation: 0,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: const Color(0xFF1565C0).withValues(alpha: 0.18),
            width: 1.5,
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.12),
              blurRadius: 28,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            _buildMessage(),
            _buildProgress(),
            const SizedBox(height: 8),
            _buildActions(),
          ],
        ),
      ),
    );
  }

  // ── Header: owl + title + step counter + close ──────────────────────────────
  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.fromLTRB(18, 14, 12, 12),
      decoration: BoxDecoration(
        color: const Color(0xFFEFF6FF),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
        border: Border(
          bottom: BorderSide(
            color: const Color(0xFF1565C0).withValues(alpha: 0.10),
          ),
        ),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Owl avatar
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: const Color(0xFF1565C0).withValues(alpha: 0.12),
                  blurRadius: 8,
                ),
              ],
            ),
            child: const Center(
              child: Text('🦉', style: TextStyle(fontSize: 24)),
            ),
          ),
          const SizedBox(width: 12),
          // Title + step label
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  state.step.title,
                  style: const TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: Color(0xFF0F172A),
                    height: 1.3,
                  ),
                ),
                const SizedBox(height: 2),
                Text(
                  'Step ${state.stepIndex + 1} of ${state.totalSteps}',
                  style: const TextStyle(
                    fontSize: 11,
                    color: Color(0xFF64748B),
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ],
            ),
          ),
          // Close button
          GestureDetector(
            onTap: onSkip,
            child: Container(
              padding: const EdgeInsets.all(4),
              child: const Icon(
                Icons.close,
                size: 16,
                color: Color(0xFF94A3B8),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ── Message body ────────────────────────────────────────────────────────────
  Widget _buildMessage() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(18, 14, 18, 8),
      child: Text(
        state.step.message,
        style: const TextStyle(
          fontSize: 14,
          color: Color(0xFF334155),
          height: 1.65,
        ),
      ),
    );
  }

  // ── Progress dots ───────────────────────────────────────────────────────────
  Widget _buildProgress() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(18, 8, 18, 0),
      child: Row(
        children: List.generate(state.totalSteps, (i) {
          final isActive = i == state.stepIndex;
          final isPast = i < state.stepIndex;
          return AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOutCubic,
            width: isActive ? 22 : 7,
            height: 7,
            margin: const EdgeInsets.only(right: 5),
            decoration: BoxDecoration(
              color: isActive
                  ? const Color(0xFF1565C0)
                  : isPast
                      ? const Color(0xFF93C5FD)
                      : const Color(0xFFE2E8F0),
              borderRadius: BorderRadius.circular(4),
            ),
          );
        }),
      ),
    );
  }

  // ── Action buttons ──────────────────────────────────────────────────────────
  Widget _buildActions() {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 4, 12, 14),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Skip tour (left)
          TextButton(
            onPressed: onSkip,
            style: TextButton.styleFrom(
              foregroundColor: const Color(0xFF94A3B8),
              padding:
                  const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
            ),
            child: const Text(
              'Skip Tour',
              style: TextStyle(fontSize: 12),
            ),
          ),
          // Primary CTA (right)
          ElevatedButton(
            onPressed: onNext,
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1565C0),
              foregroundColor: Colors.white,
              elevation: 0,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
              padding:
                  const EdgeInsets.symmetric(horizontal: 18, vertical: 10),
            ),
            child: Text(
              state.step.buttonLabel,
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ─── Nav Pulse Indicator ──────────────────────────────────────────────────────
// Wrap any nav item with this to add a subtle animated "look here!" glow ring
// when the wizard is pointing at it.
//
// Usage:
//   WizardNavPulse(
//     active: WizardService.highlightedRoute == 'My Collection',
//     child: _buildNavItem('My Collection', icon: Icons.collections_bookmark_outlined),
//   )

class WizardNavPulse extends StatefulWidget {
  final bool active;
  final Widget child;

  const WizardNavPulse({super.key, required this.active, required this.child});

  @override
  State<WizardNavPulse> createState() => _WizardNavPulseState();
}

class _WizardNavPulseState extends State<WizardNavPulse>
    with SingleTickerProviderStateMixin {
  late final AnimationController _pulse;
  late final Animation<double> _opacity;

  @override
  void initState() {
    super.initState();
    _pulse = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 900),
    )..repeat(reverse: true);
    _opacity = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _pulse, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _pulse.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (!widget.active) return widget.child;

    return AnimatedBuilder(
      animation: _opacity,
      builder: (context, child) => Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(6),
          boxShadow: [
            BoxShadow(
              color: const Color(0xFF1565C0).withValues(alpha: _opacity.value * 0.45),
              blurRadius: 12,
              spreadRadius: 2,
            ),
          ],
        ),
        child: child,
      ),
      child: widget.child,
    );
  }
}
