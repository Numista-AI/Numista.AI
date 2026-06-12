import 'package:flutter/material.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  Morgan Guide Flow  (v2 — compact speech-bubble style)
//  ──────────────────────────────────────────────────────
//  Each guide step renders as a small floating bubble (≤300 px wide) that
//  hovers near the UI element it's talking about.  Key design goals:
//    • Feels like Morgan whispering a tip, NOT lecturing
//    • Context-aware position per step (top / bottom, left / center / right)
//    • Animated ↓ arrow points at the element being described
//    • Animated progress dots (●○○) instead of a progress bar
//    • Collapsible to a mini pill so the app stays usable
//
//  IMPORTANT: _buildCollapsed / _buildExpanded must return a Positioned(…)
//  directly — never wrap Positioned in a RenderObjectWidget (e.g. AnimatedSlide)
//  because that creates an intermediate render object whose parentData is NOT
//  StackParentData, causing a TypeError crash in dart2js -O4 release builds.
// ══════════════════════════════════════════════════════════════════════════════

// ── Enums ─────────────────────────────────────────────────────────────────────

enum GuidePosition {
  topLeft, topCenter, topRight,
  bottomLeft, bottomCenter, bottomRight,
}

enum ArrowDirection { down, up, left, right, downLeft, downRight }

// ── Data model ────────────────────────────────────────────────────────────────

/// A single step in a guided flow.
class MorganStep {
  /// What Morgan says — plain English, one idea per step.
  final String narration;

  /// Optional small gold hint shown below the narration.
  final String? hint;

  /// Label for the primary "Next" button.
  final String nextLabel;

  /// When true the Next button is disabled — user must act first (future use).
  final bool waitForAction;

  /// Where the bubble floats relative to the content area.
  final GuidePosition position;

  /// Show an animated bouncing arrow pointing at the relevant UI element.
  final bool showArrow;

  /// Which direction the arrow bounces.
  final ArrowDirection arrowDirection;

  const MorganStep({
    required this.narration,
    this.hint,
    this.nextLabel = 'Next →',
    this.waitForAction = false,
    this.position = GuidePosition.bottomRight,
    this.showArrow = false,
    this.arrowDirection = ArrowDirection.down,
  });
}

/// A complete guided flow (e.g. "Browsing your collection").
class MorganGuide {
  final String id;
  final String title;     // Short label in the bubble header
  final String emoji;
  final List<MorganStep> steps;

  const MorganGuide({
    required this.id,
    required this.title,
    required this.emoji,
    required this.steps,
  });
}

// ── Service ───────────────────────────────────────────────────────────────────

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

/// Manages the currently active Morgan guide via a [ValueNotifier].
class MorganGuideService {
  MorganGuideService._();

  static final current = ValueNotifier<GuideState?>(null);

  static void start(MorganGuide guide) =>
      current.value = GuideState(guide: guide, step: 0);

  static void next() {
    final s = current.value;
    if (s == null) return;
    if (s.step >= s.guide.steps.length - 1) {
      current.value = null; // guide complete
    } else {
      current.value = s.copyWith(step: s.step + 1);
    }
  }

  static void back() {
    final s = current.value;
    if (s == null || s.step == 0) return;
    current.value = s.copyWith(step: s.step - 1);
  }

  static void exit() => current.value = null;

  static void toggleCollapsed() {
    final s = current.value;
    if (s == null) return;
    current.value = s.copyWith(collapsed: !s.collapsed);
  }
}

// ── Panel widget ──────────────────────────────────────────────────────────────

class MorganGuidePanel extends StatelessWidget {
  const MorganGuidePanel({super.key});

  // Shared palette
  static const _bg   = Color(0xFF0B1F3A);
  static const _teal = Color(0xFF2DD4BF);
  static const _gold = Color(0xFFD4A843);
  static const _sub  = Color(0xFF94A3B8);

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<GuideState?>(
      valueListenable: MorganGuideService.current,
      builder: (context, state, _) {
        if (state == null) return const SizedBox.shrink();

        // Return Positioned directly — do NOT wrap in any RenderObjectWidget.
        // See file-level note for the reason.
        return state.collapsed
            ? _buildCollapsed(state)
            : _buildExpanded(state);
      },
    );
  }

  // ── Collapsed mini-pill ──────────────────────────────────────────────────

  Widget _buildCollapsed(GuideState state) {
    return Positioned(
      bottom: 16,
      right: 16,
      child: GestureDetector(
        onTap: MorganGuideService.toggleCollapsed,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: _bg,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: _gold.withAlpha(80), width: 1),
            boxShadow: [
              BoxShadow(
                  color: Colors.black.withAlpha(100), blurRadius: 10),
            ],
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              _MiniOwl(size: 22),
              const SizedBox(width: 6),
              Text(
                'Step ${state.step + 1}/${state.guide.steps.length}',
                style: const TextStyle(
                    color: _teal,
                    fontSize: 11,
                    fontWeight: FontWeight.w600),
              ),
              const SizedBox(width: 4),
              const Icon(Icons.expand_less_rounded, color: _gold, size: 14),
            ],
          ),
        ),
      ),
    );
  }

  // ── Expanded speech bubble ────────────────────────────────────────────────

  Widget _buildExpanded(GuideState state) {
    final step      = state.guide.steps[state.step];
    final total     = state.guide.steps.length;
    final isLast    = state.step == total - 1;

    // ── Bubble card ──────────────────────────────────────────────────────
    final bubble = Container(
      width: 300,
      padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
      decoration: BoxDecoration(
        color: _bg,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _gold.withAlpha(70), width: 1),
        boxShadow: [
          BoxShadow(
              color: Colors.black.withAlpha(120),
              blurRadius: 16,
              offset: const Offset(0, 4)),
          BoxShadow(color: _teal.withAlpha(15), blurRadius: 12),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [

          // ── Header: avatar + title + dots + collapse ─────────────────
          Row(
            children: [
              _MiniOwl(size: 26),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  '${state.guide.emoji}  ${state.guide.title}',
                  style: const TextStyle(
                      color: _gold,
                      fontSize: 10,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 0.2),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              _ProgressDots(current: state.step, total: total),
              const SizedBox(width: 6),
              GestureDetector(
                onTap: MorganGuideService.toggleCollapsed,
                child: const Padding(
                  padding: EdgeInsets.all(2),
                  child: Icon(Icons.expand_more_rounded,
                      color: _sub, size: 18),
                ),
              ),
            ],
          ),

          const SizedBox(height: 8),
          const Divider(color: Color(0xFF1E3A5F), height: 1),
          const SizedBox(height: 10),

          // ── Narration ─────────────────────────────────────────────────
          Text(
            step.narration,
            style: const TextStyle(
                color: Colors.white, fontSize: 14, height: 1.45),
          ),

          // ── Hint ──────────────────────────────────────────────────────
          if (step.hint != null) ...[
            const SizedBox(height: 6),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lightbulb_outline_rounded,
                    color: _gold, size: 12),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    step.hint!,
                    style: const TextStyle(
                        color: _gold, fontSize: 11, height: 1.35),
                  ),
                ),
              ],
            ),
          ],

          const SizedBox(height: 12),

          // ── Navigation row ────────────────────────────────────────────
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              // Back / Exit (left side — compact text tap target)
              if (state.step > 0)
                GestureDetector(
                  onTap: MorganGuideService.back,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('← Back',
                        style: TextStyle(
                            color: _sub.withAlpha(180), fontSize: 12)),
                  ),
                )
              else
                GestureDetector(
                  onTap: MorganGuideService.exit,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('✕ Exit',
                        style: TextStyle(
                            color: _sub.withAlpha(110), fontSize: 11)),
                  ),
                ),

              // Next / Done (right side — pill button)
              ElevatedButton(
                onPressed:
                    step.waitForAction ? null : MorganGuideService.next,
                style: ElevatedButton.styleFrom(
                  backgroundColor:
                      isLast ? const Color(0xFF22C55E) : _teal,
                  foregroundColor: Colors.black87,
                  padding: const EdgeInsets.symmetric(
                      horizontal: 16, vertical: 8),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(20)),
                  elevation: 0,
                ),
                child: Text(
                  isLast ? '🎉 Done!' : step.nextLabel,
                  style: const TextStyle(
                      fontSize: 13, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
        ],
      ),
    );

    // ── Attach arrow: vertical directions go above/below; horizontal go beside ─
    Widget content;
    if (!step.showArrow) {
      content = bubble;
    } else {
      final arrow = _BouncingArrow(direction: step.arrowDirection);
      switch (step.arrowDirection) {
        case ArrowDirection.left:
          // Arrow sits to the LEFT of the bubble, pointing at the element
          content = Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [arrow, const SizedBox(width: 6), bubble],
          );
          break;
        case ArrowDirection.right:
          content = Row(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [bubble, const SizedBox(width: 6), arrow],
          );
          break;
        case ArrowDirection.up:
          content = Column(
            mainAxisSize: MainAxisSize.min,
            children: [arrow, bubble],
          );
          break;
        default:
          // down / downLeft / downRight — arrow below bubble
          content = Column(
            mainAxisSize: MainAxisSize.min,
            children: [bubble, arrow],
          );
      }
    }

    // ── Place the Positioned wrapper based on step.position ───────────────
    //
    // topCenter / bottomCenter: use left:0 + right:0 + Align so the fixed-
    // width bubble is horizontally centred without hard-coding pixel offsets.
    switch (step.position) {
      case GuidePosition.topLeft:
        return Positioned(top: 16, left: 16, child: content);
      case GuidePosition.topRight:
        return Positioned(top: 16, right: 16, child: content);
      case GuidePosition.topCenter:
        return Positioned(
          top: 16, left: 0, right: 0,
          child: Align(alignment: Alignment.topCenter, child: content),
        );
      case GuidePosition.bottomLeft:
        return Positioned(bottom: 16, left: 16, child: content);
      case GuidePosition.bottomRight:
        return Positioned(bottom: 16, right: 16, child: content);
      case GuidePosition.bottomCenter:
        return Positioned(
          bottom: 16, left: 0, right: 0,
          child: Align(alignment: Alignment.topCenter, child: content),
        );
    }
  }
}

// ── Bouncing Arrow ────────────────────────────────────────────────────────────

class _BouncingArrow extends StatefulWidget {
  final ArrowDirection direction;
  const _BouncingArrow({this.direction = ArrowDirection.down});

  @override
  State<_BouncingArrow> createState() => _BouncingArrowState();
}

class _BouncingArrowState extends State<_BouncingArrow>
    with SingleTickerProviderStateMixin {
  late final AnimationController _ctrl;
  late final Animation<double> _anim;

  @override
  void initState() {
    super.initState();
    _ctrl = AnimationController(
        vsync: this, duration: const Duration(milliseconds: 600));
    _anim = Tween<double>(begin: 0, end: 10).animate(
        CurvedAnimation(parent: _ctrl, curve: Curves.easeInOut));
    _ctrl.repeat(reverse: true);
  }

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final double d = _anim.value;
    Offset offset;
    IconData icon;
    double size;
    Color color;

    switch (widget.direction) {
      // ── Horizontal: big bold gold arrow ────────────────────────────────
      case ArrowDirection.left:
        offset = Offset(-d, 0);
        icon = Icons.arrow_back_rounded;
        size = 48;
        color = const Color(0xFFD4A843); // gold — matches user's yellow arrow
        break;
      case ArrowDirection.right:
        offset = Offset(d, 0);
        icon = Icons.arrow_forward_rounded;
        size = 48;
        color = const Color(0xFFD4A843);
        break;
      // ── Diagonal ───────────────────────────────────────────────────────
      case ArrowDirection.downLeft:
        offset = Offset(-d * 0.7, d * 0.7);
        icon = Icons.south_west;
        size = 32;
        color = const Color(0xFF2DD4BF);
        break;
      case ArrowDirection.downRight:
        offset = Offset(d * 0.7, d * 0.7);
        icon = Icons.south_east;
        size = 32;
        color = const Color(0xFF2DD4BF);
        break;
      // ── Vertical ───────────────────────────────────────────────────────
      case ArrowDirection.up:
        offset = Offset(0, -d);
        icon = Icons.keyboard_arrow_up_rounded;
        size = 32;
        color = const Color(0xFF2DD4BF);
        break;
      case ArrowDirection.down:
      default:
        offset = Offset(0, d);
        icon = Icons.keyboard_arrow_down_rounded;
        size = 32;
        color = const Color(0xFF2DD4BF);
        break;
    }

    return AnimatedBuilder(
      animation: _anim,
      builder: (_, __) => Transform.translate(
        offset: offset,
        child: Icon(icon, color: color, size: size),
      ),
    );
  }
}

// ── Progress Dots ─────────────────────────────────────────────────────────────

class _ProgressDots extends StatelessWidget {
  final int current;
  final int total;
  const _ProgressDots({required this.current, required this.total});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: List.generate(total, (i) {
        final active = i == current;
        return AnimatedContainer(
          duration: const Duration(milliseconds: 220),
          width: active ? 14 : 5,
          height: 5,
          margin: const EdgeInsets.symmetric(horizontal: 2),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(3),
            color: active
                ? const Color(0xFF2DD4BF)
                : const Color(0xFF1E3A5F),
          ),
        );
      }),
    );
  }
}

// ── Mini Owl Avatar ───────────────────────────────────────────────────────────

class _MiniOwl extends StatelessWidget {
  final double size;
  const _MiniOwl({this.size = 30});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(
            color: const Color(0xFFD4A843).withAlpha(150), width: 1),
      ),
      child: ClipOval(
        child: Image.asset(
          'assets/morgan_avatar.png',
          fit: BoxFit.cover,
          errorBuilder: (context, error, stackTrace) => Icon(
              Icons.smart_toy_rounded,
              color: const Color(0xFF2DD4BF),
              size: size * 0.55),
        ),
      ),
    );
  }
}
