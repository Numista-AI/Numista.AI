import 'package:flutter/material.dart';

// ══════════════════════════════════════════════════════════════════════════════
//  Morgan Guide Flow  (v3 — draggable + searchable speech-bubble style)
//  ──────────────────────────────────────────────────────────────────────────
//  Changes from v2:
//    • MorganGuidePanel is now a StatefulWidget so it can track drag state
//      and inline search results.
//    • Dragging: a ≡ handle in the bubble header lets the user drag it
//      anywhere on screen.  A _dragDelta Offset is accumulated and applied via
//      Transform.translate *inside* the Positioned child — this keeps
//      Positioned as the direct Stack child (no intermediate RenderObjects),
//      avoiding the dart2js -O4 StackParentData crash described below.
//    • Search: MorganStep.showSearch == true reveals an inline TextField and
//      compact result list.  Results come from an onSearch callback on
//      MorganGuidePanel — keeping Firebase out of this widget.
//
//  IMPORTANT: _buildCollapsed / _buildExpanded must return a Positioned(…)
//  directly — never wrap Positioned in a RenderObjectWidget (e.g. AnimatedSlide
//  or LayoutBuilder) because that creates an intermediate render object whose
//  parentData is NOT StackParentData, causing a TypeError crash in dart2js
//  -O4 release builds.  Transform.translate is fine because it wraps the
//  content *inside* Positioned, not the Positioned itself.
// ══════════════════════════════════════════════════════════════════════════════

// ── Enums ─────────────────────────────────────────────────────────────────────

enum GuidePosition {
  topLeft, topCenter, topRight,
  bottomLeft, bottomCenter, bottomRight,
}

enum ArrowDirection { down, up, left, right, downLeft, downRight }

// ── Search result data class ──────────────────────────────────────────────────

/// A single coin / item returned by the Morgan inline search.
class MorganSearchResult {
  final String id;
  final String title;
  final String subtitle;
  final String value;

  const MorganSearchResult({
    required this.id,
    required this.title,
    this.subtitle = '',
    this.value    = '',
  });
}

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

  /// When true, an inline search field is shown inside the bubble so the user
  /// can search their collection without leaving the current screen.
  final bool showSearch;

  const MorganStep({
    required this.narration,
    this.hint,
    this.nextLabel      = 'Next →',
    this.waitForAction  = false,
    this.position       = GuidePosition.bottomRight,
    this.showArrow      = false,
    this.arrowDirection = ArrowDirection.down,
    this.showSearch     = false,
  });
}

/// A complete guided flow (e.g. "Browsing your collection").
class MorganGuide {
  final String id;
  final String title;   // Short label in the bubble header
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

  static void start(MorganGuide guide, [int initialStep = 0]) {
    final step = (initialStep >= 0 && initialStep < guide.steps.length) ? initialStep : 0;
    current.value = GuideState(guide: guide, step: step);
  }

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

class MorganGuidePanel extends StatefulWidget {
  /// Called when the user types in the embedded search field.
  /// Must return matching [MorganSearchResult]s to display inside the bubble.
  /// Keep Firebase / Firestore logic in the caller — not in this widget.
  final Future<List<MorganSearchResult>> Function(String query)? onSearch;

  /// Called when the user taps a search result row.
  /// [id] is the document ID of the matched coin / item.
  final void Function(String id)? onSearchResultTap;

  const MorganGuidePanel({
    super.key,
    this.onSearch,
    this.onSearchResultTap,
  });

  // Shared palette — also used by child private widgets below.
  static const bg   = Color(0xFF0B1F3A);
  static const teal = Color(0xFF2DD4BF);
  static const gold = Color(0xFFD4A843);
  static const sub  = Color(0xFF94A3B8);

  @override
  State<MorganGuidePanel> createState() => _MorganGuidePanelState();
}

class _MorganGuidePanelState extends State<MorganGuidePanel> {
  // ── Drag state ────────────────────────────────────────────────────────────
  /// Offset accumulated from pan gestures on the bubble header.
  /// Applied via Transform.translate inside the Positioned — see file comment.
  Offset _dragDelta = Offset.zero;

  /// True once the user has panned the bubble.  While false, the delta resets
  /// each step so the bubble re-anchors to the step's GuidePosition corner.
  bool _userHasDragged = false;

  /// Tracks the last rendered step key to detect step changes.
  String _lastStepKey = '';

  // ── Search state ──────────────────────────────────────────────────────────
  final _searchCtrl = TextEditingController();
  List<MorganSearchResult> _searchResults = [];
  bool _searching = false;

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  // ── Search handler ────────────────────────────────────────────────────────

  void _onSearchChanged(String query) async {
    if (query.trim().isEmpty) {
      if (mounted) setState(() { _searchResults = []; _searching = false; });
      return;
    }
    if (mounted) setState(() => _searching = true);
    final results = await widget.onSearch?.call(query) ?? [];
    if (mounted) setState(() { _searchResults = results; _searching = false; });
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<GuideState?>(
      valueListenable: MorganGuideService.current,
      builder: (context, state, _) {
        if (state == null) {
          // Guide finished — reset everything for next run.
          _dragDelta     = Offset.zero;
          _userHasDragged = false;
          _lastStepKey   = '';
          _searchCtrl.clear();
          _searchResults = [];
          return const SizedBox.shrink();
        }

        // Detect step change.
        final stepKey = '${state.guide.id}_${state.step}';
        if (stepKey != _lastStepKey) {
          _lastStepKey = stepKey;
          if (!_userHasDragged) _dragDelta = Offset.zero;
          _searchCtrl.clear();
          _searchResults = [];
          _searching = false;
        }

        // Return Positioned directly — see file-level note.
        return state.collapsed
            ? _buildCollapsed(state)
            : _buildExpanded(state);
      },
    );
  }

  // ── Collapsed mini-pill ───────────────────────────────────────────────────

  Widget _buildCollapsed(GuideState state) {
    final pill = GestureDetector(
      behavior: HitTestBehavior.opaque,
      onPanUpdate: (d) => setState(() {
        _userHasDragged = true;
        _dragDelta += d.delta;
      }),
      onTap: MorganGuideService.toggleCollapsed,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: MorganGuidePanel.bg,
          borderRadius: BorderRadius.circular(24),
          border: Border.all(
              color: MorganGuidePanel.gold.withAlpha(80), width: 1),
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
                  color: MorganGuidePanel.teal,
                  fontSize: 11,
                  fontWeight: FontWeight.w600),
            ),
            const SizedBox(width: 4),
            const Icon(Icons.add_rounded,
                color: MorganGuidePanel.gold, size: 14),
          ],
        ),
      ),
    );

    return Positioned(
      bottom: 16,
      right: 16,
      child: Transform.translate(offset: _dragDelta, child: pill),
    );
  }

  // ── Expanded speech bubble ────────────────────────────────────────────────

  Widget _buildExpanded(GuideState state) {
    final step   = state.guide.steps[state.step];
    final total  = state.guide.steps.length;
    final isLast = state.step == total - 1;

    final bubble = GestureDetector(
      behavior: HitTestBehavior.translucent,
      onPanUpdate: (d) => setState(() {
        _userHasDragged = true;
        final size = MediaQuery.of(context).size;
        final nextDx = (_dragDelta.dx + d.delta.dx).clamp(-size.width * 0.7, size.width * 0.7);
        final nextDy = (_dragDelta.dy + d.delta.dy).clamp(-size.height * 0.7, size.height * 0.7);
        _dragDelta = Offset(nextDx, nextDy);
      }),
      child: Container(
        width: 300,
        padding: const EdgeInsets.fromLTRB(14, 12, 14, 12),
        decoration: BoxDecoration(
          color: MorganGuidePanel.bg,
          borderRadius: BorderRadius.circular(16),
          border:
              Border.all(color: MorganGuidePanel.gold.withAlpha(70), width: 1),
          boxShadow: [
            BoxShadow(
                color: Colors.black.withAlpha(120),
                blurRadius: 16,
                offset: const Offset(0, 4)),
            BoxShadow(
                color: MorganGuidePanel.teal.withAlpha(15), blurRadius: 12),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [

            // ── Header: drag handle + avatar + title + dots + collapse ─────
            Row(
              children: [
                // Drag handle — visual cue that the bubble is movable
                const Tooltip(
                  message: 'Drag to move Morgan',
                  child: Padding(
                    padding: EdgeInsets.only(right: 6),
                    child: Icon(
                      Icons.drag_indicator_rounded,
                      color: MorganGuidePanel.gold,
                      size: 18,
                    ),
                  ),
                ),
                _MiniOwl(size: 26),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    '${state.guide.emoji}  ${state.guide.title}',
                    style: const TextStyle(
                        color: MorganGuidePanel.gold,
                        fontSize: 10,
                        fontWeight: FontWeight.w700,
                        letterSpacing: 0.2),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                _ProgressDots(current: state.step, total: total),
                const SizedBox(width: 6),
                Tooltip(
                  message: 'Minimize Morgan (-)',
                  child: InkWell(
                    borderRadius: BorderRadius.circular(12),
                    onTap: MorganGuideService.toggleCollapsed,
                    child: const Padding(
                      padding: EdgeInsets.all(4),
                      child: Icon(Icons.remove_rounded,
                          color: MorganGuidePanel.sub, size: 18),
                    ),
                  ),
                ),
                const SizedBox(width: 2),
                Tooltip(
                  message: 'Close Guide',
                  child: InkWell(
                    borderRadius: BorderRadius.circular(12),
                    onTap: MorganGuideService.exit,
                    child: const Padding(
                      padding: EdgeInsets.all(4),
                      child: Icon(Icons.close_rounded,
                          color: Color(0xFF64748B), size: 16),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 8),
          const Divider(color: Color(0xFF1E3A5F), height: 1),
          const SizedBox(height: 10),

          // ── Narration ──────────────────────────────────────────────────
          Text(
            step.narration,
            style: const TextStyle(
                color: Colors.white, fontSize: 14, height: 1.45),
          ),

          // ── Hint ───────────────────────────────────────────────────────
          if (step.hint != null) ...[
            const SizedBox(height: 6),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lightbulb_outline_rounded,
                    color: MorganGuidePanel.gold, size: 12),
                const SizedBox(width: 4),
                Expanded(
                  child: Text(
                    step.hint!,
                    style: const TextStyle(
                        color: MorganGuidePanel.gold,
                        fontSize: 11,
                        height: 1.35),
                  ),
                ),
              ],
            ),
          ],

          // ── Inline search (when showSearch is true) ────────────────────
          if (step.showSearch && widget.onSearch != null) ...[
            const SizedBox(height: 10),

            // Search text field
            SizedBox(
              height: 36,
              child: TextField(
                controller: _searchCtrl,
                style: const TextStyle(color: Colors.white, fontSize: 13),
                onChanged: _onSearchChanged,
                decoration: InputDecoration(
                  filled: true,
                  fillColor: const Color(0xFF0F2744),
                  contentPadding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 0),
                  hintText: 'Search your collection…',
                  hintStyle: TextStyle(
                      color: MorganGuidePanel.sub.withAlpha(140),
                      fontSize: 13),
                  prefixIcon: const Icon(Icons.search,
                      color: MorganGuidePanel.teal, size: 16),
                  suffixIcon: _searchCtrl.text.isNotEmpty
                      ? GestureDetector(
                          onTap: () {
                            _searchCtrl.clear();
                            setState(() => _searchResults = []);
                          },
                          child: const Icon(Icons.close,
                              color: MorganGuidePanel.sub, size: 14),
                        )
                      : null,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(
                        color: MorganGuidePanel.teal.withAlpha(60)),
                  ),
                  enabledBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: BorderSide(
                        color: MorganGuidePanel.teal.withAlpha(60)),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                    borderSide: const BorderSide(
                        color: MorganGuidePanel.teal, width: 1.5),
                  ),
                ),
              ),
            ),

            // Spinner
            if (_searching)
              const Padding(
                padding: EdgeInsets.only(top: 8),
                child: Center(
                  child: SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(
                        color: MorganGuidePanel.teal, strokeWidth: 2),
                  ),
                ),
              )
            // Result rows
            else if (_searchResults.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Column(
                  children: _searchResults
                      .map((r) => _SearchResultTile(
                            result: r,
                            onTap: widget.onSearchResultTap != null
                                ? () => widget.onSearchResultTap!(r.id)
                                : null,
                          ))
                      .toList(),
                ),
              )
            // Empty state
            else if (_searchCtrl.text.isNotEmpty && !_searching)
              Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(
                  'No matches — try a year, name, or series.',
                  style: TextStyle(
                      color: MorganGuidePanel.sub, fontSize: 11),
                ),
              ),
          ],

          const SizedBox(height: 12),

          // ── Navigation row ─────────────────────────────────────────────
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              if (state.step > 0)
                GestureDetector(
                  onTap: MorganGuideService.back,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('← Back',
                        style: TextStyle(
                            color: MorganGuidePanel.sub.withAlpha(180),
                            fontSize: 12)),
                  ),
                )
              else
                GestureDetector(
                  onTap: MorganGuideService.exit,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Text('✕ Exit',
                        style: TextStyle(
                            color: MorganGuidePanel.sub.withAlpha(110),
                            fontSize: 11)),
                  ),
                ),
              ElevatedButton(
                onPressed:
                    step.waitForAction ? null : MorganGuideService.next,
                style: ElevatedButton.styleFrom(
                  backgroundColor: isLast
                      ? const Color(0xFF22C55E)
                      : MorganGuidePanel.teal,
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

    // ── Attach directional arrow ───────────────────────────────────────────
    Widget content;
    if (!step.showArrow) {
      content = bubble;
    } else {
      final arrow = _BouncingArrow(direction: step.arrowDirection);
      switch (step.arrowDirection) {
        case ArrowDirection.left:
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
        default: // down / downLeft / downRight
          content = Column(
            mainAxisSize: MainAxisSize.min,
            children: [bubble, arrow],
          );
      }
    }

    // ── Draggable wrapper: Transform.translate is INSIDE Positioned ────────
    //    (see file-level comment — never wrap Positioned in a RenderObjectWidget)
    final draggable = Transform.translate(
      offset: _dragDelta,
      child: content,
    );

    // ── Position anchor based on step.position ─────────────────────────────
    switch (step.position) {
      case GuidePosition.topLeft:
        return Positioned(top: 16, left: 16, child: draggable);
      case GuidePosition.topRight:
        return Positioned(top: 16, right: 16, child: draggable);
      case GuidePosition.topCenter:
        return Positioned(
          top: 16, left: 0, right: 0,
          child: Align(alignment: Alignment.topCenter, child: draggable),
        );
      case GuidePosition.bottomLeft:
        return Positioned(bottom: 16, left: 16, child: draggable);
      case GuidePosition.bottomRight:
        return Positioned(bottom: 16, right: 16, child: draggable);
      case GuidePosition.bottomCenter:
        return Positioned(
          bottom: 16, left: 0, right: 0,
          child: Align(alignment: Alignment.bottomCenter, child: draggable),
        );
    }
  }
}

// ── Search Result Tile ────────────────────────────────────────────────────────

class _SearchResultTile extends StatelessWidget {
  final MorganSearchResult result;
  final VoidCallback? onTap;

  const _SearchResultTile({required this.result, this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 4),
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 7),
        decoration: BoxDecoration(
          color: const Color(0xFF0F2744),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
              color: MorganGuidePanel.teal.withAlpha(40)),
        ),
        child: Row(
          children: [
            const Icon(Icons.monetization_on_rounded,
                color: MorganGuidePanel.gold, size: 14),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    result.title,
                    style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.w600),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  if (result.subtitle.isNotEmpty)
                    Text(
                      result.subtitle,
                      style: const TextStyle(
                          color: MorganGuidePanel.sub, fontSize: 10),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                ],
              ),
            ),
            if (result.value.isNotEmpty)
              Text(
                result.value,
                style: const TextStyle(
                    color: MorganGuidePanel.teal,
                    fontSize: 11,
                    fontWeight: FontWeight.w600),
              ),
          ],
        ),
      ),
    );
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
    return AnimatedBuilder(
      animation: _anim,
      builder: (_, child) {
        final double d = _anim.value;
        Offset offset;
        IconData icon;
        double size;
        Color color;

        switch (widget.direction) {
          case ArrowDirection.left:
            offset = Offset(-d, 0);
            icon   = Icons.arrow_back_rounded;
            size   = 48;
            color  = const Color(0xFFD4A843);
            break;
          case ArrowDirection.right:
            offset = Offset(d, 0);
            icon   = Icons.arrow_forward_rounded;
            size   = 48;
            color  = const Color(0xFFD4A843);
            break;
          case ArrowDirection.downLeft:
            offset = Offset(-d * 0.7, d * 0.7);
            icon   = Icons.south_west;
            size   = 32;
            color  = const Color(0xFF2DD4BF);
            break;
          case ArrowDirection.downRight:
            offset = Offset(d * 0.7, d * 0.7);
            icon   = Icons.south_east;
            size   = 32;
            color  = const Color(0xFF2DD4BF);
            break;
          case ArrowDirection.up:
            offset = Offset(0, -d);
            icon   = Icons.keyboard_arrow_up_rounded;
            size   = 32;
            color  = const Color(0xFF2DD4BF);
            break;
          case ArrowDirection.down:
            offset = Offset(0, d);
            icon   = Icons.keyboard_arrow_down_rounded;
            size   = 32;
            color  = const Color(0xFF2DD4BF);
        }

        return Transform.translate(
          offset: offset,
          child: Icon(icon, color: color, size: size),
        );
      },
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
