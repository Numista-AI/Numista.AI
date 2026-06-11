import 'package:flutter/material.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  Morgan Guide Flow
//  ─────────────────
//  Step-by-step narration panels that overlay the current screen to walk
//  users through a task. Designed for 70+ year-old users:
//    • Large readable text (min 17px)
//    • Huge tap targets (buttons ≥ 56px tall)
//    • One instruction per step — never two ideas at once
//    • Always shows progress ("Step 2 of 4")
//    • Collapsible so the app behind is always reachable
// ══════════════════════════════════════════════════════════════════════════════

// ── Data model ────────────────────────────────────────────────────────────────

/// A single step in a guided flow.
class MorganStep {
  /// What Morgan says — plain English, no jargon.
  final String narration;

  /// Optional smaller hint shown below the narration (e.g. "Look for the blue button").
  final String? hint;

  /// Label for the "Next" button. Defaults to "Next step →".
  final String nextLabel;

  /// If true, the "Next" button is hidden — the user must act on the screen
  /// and Morgan auto-advances (future Phase 3 feature, set to false for now).
  final bool waitForAction;

  const MorganStep({
    required this.narration,
    this.hint,
    this.nextLabel = 'Next step →',
    this.waitForAction = false,
  });
}

/// A complete guided flow (e.g. "Add from invoice").
class MorganGuide {
  final String id;
  final String title;     // Short title shown in the panel header
  final String emoji;
  final List<MorganStep> steps;

  const MorganGuide({
    required this.id,
    required this.title,
    required this.emoji,
    required this.steps,
  });
}

// ── Service (singleton, ValueNotifier-driven) ─────────────────────────────────

/// State of the currently active guide (step index + collapsed flag).
/// Public so [MorganGuideService.current] can be a typed [ValueNotifier].
class GuideState {
  final MorganGuide guide;
  final int step;
  final bool collapsed;
  const GuideState({
    required this.guide,
    required this.step,
    this.collapsed = false,
  });

  GuideState copyWith({int? step, bool? collapsed}) => GuideState(
        guide: guide,
        step: step ?? this.step,
        collapsed: collapsed ?? this.collapsed,
      );
}

/// Manages the currently active Morgan guide.
///
/// BaseLayout listens to [current] and renders [MorganGuidePanel] when non-null.
class MorganGuideService {
  MorganGuideService._();

  static final ValueNotifier<GuideState?> current = ValueNotifier(null);

  static void start(MorganGuide guide) {
    current.value = GuideState(guide: guide, step: 0);
  }

  static void next() {
    final s = current.value;
    if (s == null) return;
    if (s.step < s.guide.steps.length - 1) {
      current.value = s.copyWith(step: s.step + 1, collapsed: false);
    } else {
      current.value = null;
    }
  }

  static void back() {
    final s = current.value;
    if (s == null) return;
    if (s.step > 0) {
      current.value = s.copyWith(step: s.step - 1);
    }
  }

  static void toggleCollapsed() {
    final s = current.value;
    if (s == null) return;
    current.value = s.copyWith(collapsed: !s.collapsed);
  }

  static void exit() => current.value = null;
}

// ── Panel widget ─────────────────────────────────────────────────────────────

/// Floating bottom panel that shows the current Morgan guide step.
///
/// Place this in a [Stack] that overlays the main app content.
/// It is transparent when no guide is active.
class MorganGuidePanel extends StatelessWidget {
  const MorganGuidePanel({super.key});

  static const _bg   = Color(0xFF0D1B2E);
  static const _surf = Color(0xFF162033);
  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<GuideState?>(
      valueListenable: MorganGuideService.current,
      builder: (context, state, _) {
        if (state == null) return const SizedBox.shrink();

        return AnimatedSlide(
          offset: Offset.zero,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOutCubic,
          child: state.collapsed
              ? _buildCollapsed(context, state)
              : _buildExpanded(context, state),
        );
      },
    );
  }

  // ── Collapsed tab ──────────────────────────────────────────────────────────
  Widget _buildCollapsed(BuildContext context, GuideState state) {
    return Positioned(
      bottom: 16,
      right: 16,
      child: GestureDetector(
        onTap: MorganGuideService.toggleCollapsed,
        child: Container(
          padding:
              const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: _bg,
            borderRadius: BorderRadius.circular(30),
            border: Border.all(color: _gold.withAlpha(80), width: 1.5),
            boxShadow: [
              BoxShadow(
                  color: _teal.withAlpha(40),
                  blurRadius: 12,
                  spreadRadius: 1),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _MiniOwl(),
              const SizedBox(width: 8),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    'Step ${state.step + 1} of ${state.guide.steps.length}',
                    style: const TextStyle(
                        color: _teal,
                        fontSize: 11,
                        fontWeight: FontWeight.w600),
                  ),
                  const Text(
                    'Tap to open guide',
                    style: TextStyle(color: _sub, fontSize: 10),
                  ),
                ],
              ),
              const SizedBox(width: 6),
              const Icon(Icons.expand_less_rounded,
                  color: _gold, size: 18),
            ],
          ),
        ),
      ),
    );
  }

  // ── Expanded panel ─────────────────────────────────────────────────────────
  Widget _buildExpanded(BuildContext context, GuideState state) {
    final step = state.guide.steps[state.step];
    final totalSteps = state.guide.steps.length;
    final isLast = state.step == totalSteps - 1;

    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: Container(
        decoration: BoxDecoration(
          color: _bg,
          borderRadius:
              const BorderRadius.vertical(top: Radius.circular(20)),
          border: Border(
              top: BorderSide(color: _gold.withAlpha(60), width: 1.5)),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withAlpha(120),
                blurRadius: 20,
                offset: const Offset(0, -4)),
          ],
        ),
        child: SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.fromLTRB(20, 16, 20, 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // ── Drag handle + header ─────────────────────────────────
                Row(
                  children: [
                    _MiniOwl(),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '${state.guide.emoji}  ${state.guide.title}',
                            style: const TextStyle(
                                color: _gold,
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                                letterSpacing: 0.3),
                          ),
                          Text(
                            'Step ${state.step + 1} of $totalSteps',
                            style: const TextStyle(
                                color: _sub, fontSize: 11),
                          ),
                        ],
                      ),
                    ),
                    // Collapse button
                    GestureDetector(
                      onTap: MorganGuideService.toggleCollapsed,
                      child: const Padding(
                        padding: EdgeInsets.all(4),
                        child: Icon(Icons.expand_more_rounded,
                            color: _sub, size: 22),
                      ),
                    ),
                  ],
                ),

                // ── Progress bar ─────────────────────────────────────────
                const SizedBox(height: 12),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: (state.step + 1) / totalSteps,
                    backgroundColor: _surf,
                    color: _teal,
                    minHeight: 4,
                  ),
                ),
                const SizedBox(height: 16),

                // ── Morgan narration bubble ───────────────────────────────
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: _surf,
                    borderRadius: BorderRadius.circular(14),
                    border:
                        Border.all(color: _teal.withAlpha(50), width: 1),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        step.narration,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 17,        // Large for older users
                          height: 1.55,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                      if (step.hint != null) ...[
                        const SizedBox(height: 8),
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(Icons.lightbulb_outline_rounded,
                                color: _gold, size: 14),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                step.hint!,
                                style: const TextStyle(
                                    color: _gold,
                                    fontSize: 13,
                                    height: 1.4),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                const SizedBox(height: 16),

                // ── Navigation buttons ────────────────────────────────────
                Row(
                  children: [
                    // Back button (hidden on first step)
                    if (state.step > 0)
                      Expanded(
                        flex: 2,
                        child: SizedBox(
                          height: 52,
                          child: OutlinedButton(
                            onPressed: MorganGuideService.back,
                            style: OutlinedButton.styleFrom(
                              foregroundColor: _sub,
                              side: BorderSide(
                                  color: _sub.withAlpha(80)),
                              shape: RoundedRectangleBorder(
                                  borderRadius:
                                      BorderRadius.circular(12)),
                            ),
                            child: const Text('← Back',
                                style: TextStyle(fontSize: 15)),
                          ),
                        ),
                      ),
                    if (state.step > 0) const SizedBox(width: 10),

                    // Next / Done button
                    Expanded(
                      flex: 3,
                      child: SizedBox(
                        height: 56,          // Extra tall — easy to tap
                        child: ElevatedButton(
                          onPressed: step.waitForAction
                              ? null
                              : MorganGuideService.next,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: isLast
                                ? const Color(0xFF22C55E) // green on last step
                                : _teal,
                            foregroundColor: Colors.black87,
                            disabledBackgroundColor:
                                _surf,
                            shape: RoundedRectangleBorder(
                                borderRadius:
                                    BorderRadius.circular(12)),
                            elevation: 0,
                          ),
                          child: Text(
                            isLast ? '🎉 Done!' : step.nextLabel,
                            style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),

                // ── Exit guide link ───────────────────────────────────────
                const SizedBox(height: 8),
                GestureDetector(
                  onTap: MorganGuideService.exit,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text(
                      '✕  Exit guide',
                      style: TextStyle(
                          color: _sub.withAlpha(140),
                          fontSize: 12),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

// ── Mini owl avatar (used inside the panel) ───────────────────────────────────
class _MiniOwl extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      width: 34,
      height: 34,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
            color: const Color(0xFFD4A843).withAlpha(150), width: 1.5),
      ),
      child: ClipOval(
        child: Image.asset(
          'assets/morgan_avatar.png',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) => const Icon(
              Icons.smart_toy_rounded,
              color: Color(0xFF2DD4BF),
              size: 18),
        ),
      ),
    );
  }
}
