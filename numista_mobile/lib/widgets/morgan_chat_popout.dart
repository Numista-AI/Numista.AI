import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../screens/ai_chat_screen.dart';

class MorganChatPopout extends StatefulWidget {
  final String? initialQuery;
  final VoidCallback onClose;

  const MorganChatPopout({
    super.key,
    this.initialQuery,
    required this.onClose,
  });

  @override
  State<MorganChatPopout> createState() => _MorganChatPopoutState();
}

class _MorganChatPopoutState extends State<MorganChatPopout> {
  double _width = 380;
  double _height = 550;
  double _top = 100;
  double _left = 100;
  bool _isInitialized = false;
  bool _isMinimized = false;
  double _restoredHeight = 550;

  @override
  void initState() {
    super.initState();
    _loadState();
  }

  Future<void> _loadState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final savedWidth = prefs.getDouble('morgan_popout_width');
      final savedHeight = prefs.getDouble('morgan_popout_height');
      final savedTop = prefs.getDouble('morgan_popout_top');
      final savedLeft = prefs.getDouble('morgan_popout_left');
      final savedMinimized = prefs.getBool('morgan_popout_minimized');
      final savedRestoredHeight = prefs.getDouble('morgan_popout_restored_height');

      if (mounted) {
        setState(() {
          if (savedWidth != null) _width = savedWidth;
          if (savedHeight != null) _height = savedHeight;
          if (savedTop != null) _top = savedTop;
          if (savedLeft != null) _left = savedLeft;
          if (savedMinimized != null) _isMinimized = savedMinimized;
          if (savedRestoredHeight != null) _restoredHeight = savedRestoredHeight;
          _isInitialized = true;
        });
      }
    } catch (e) {
      debugPrint('[MorganChatPopout] Load state failed: $e');
      if (mounted) {
        setState(() {
          _isInitialized = true;
        });
      }
    }
  }

  Future<void> _saveState() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setDouble('morgan_popout_width', _width);
      await prefs.setDouble('morgan_popout_height', _height);
      await prefs.setDouble('morgan_popout_top', _top);
      await prefs.setDouble('morgan_popout_left', _left);
      await prefs.setBool('morgan_popout_minimized', _isMinimized);
      await prefs.setDouble('morgan_popout_restored_height', _restoredHeight);
    } catch (e) {
      debugPrint('[MorganChatPopout] Save state failed: $e');
    }
  }

  void _toggleMinimize() {
    setState(() {
      _isMinimized = !_isMinimized;
      if (_isMinimized) {
        _restoredHeight = _height;
        _height = 60.0;
      } else {
        _height = _restoredHeight;
      }
    });
    _saveState();
  }

  @override
  Widget build(BuildContext context) {
    if (!_isInitialized) {
      return const SizedBox.shrink();
    }

    final screenSize = MediaQuery.of(context).size;

    // Check boundary constraints on screenSize changes
    _top = _top.clamp(0.0, (screenSize.height - 100).clamp(0.0, screenSize.height));
    _left = _left.clamp(0.0, (screenSize.width - 100).clamp(0.0, screenSize.width));

    final popoutCard = Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0B1220), // matching AiChatScreen deep navy background
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.5),
            blurRadius: 24,
            offset: const Offset(0, 8),
          ),
          BoxShadow(
            color: const Color(0xFF2DD4BF).withValues(alpha: 0.1),
            blurRadius: 16,
          ),
        ],
        border: Border.all(color: const Color(0xFF2DD4BF).withValues(alpha: 0.25), width: 1.5),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(14),
        child: Stack(
          children: [
            // Embedded Chat Screen
            Positioned.fill(
              child: AiChatScreen(
                initialQuery: widget.initialQuery,
                isPopout: true,
                isMinimized: _isMinimized,
                onMinimize: _toggleMinimize,
                onClose: widget.onClose,
                onDragUpdate: (details) {
                  setState(() {
                    _top = (_top + details.delta.dy).clamp(0.0, screenSize.height - 100);
                    _left = (_left + details.delta.dx).clamp(0.0, screenSize.width - 100);
                  });
                },
                onDragEnd: _saveState,
              ),
            ),

            // Diagonal Resize handle in the bottom-right corner
            if (!_isMinimized)
              Positioned(
                bottom: 0,
                right: 0,
                width: 24,
                height: 24,
                child: GestureDetector(
                  behavior: HitTestBehavior.translucent,
                  onPanUpdate: (details) {
                    setState(() {
                      _width = (_width + details.delta.dx).clamp(320.0, 480.0); // Q5-LOCK: max 480 px
                      _height = (_height + details.delta.dy).clamp(380.0, screenSize.height * 0.9);
                    });
                  },
                  onPanEnd: (_) => _saveState(),
                  child: CustomPaint(
                    painter: _ResizeHandlePainter(),
                  ),
                ),
              ),
          ],
        ),
      ),
    );

    return Positioned(
      top: _top,
      left: _left,
      width: _width,
      height: _height,
      child: CallbackShortcuts(
        bindings: <ShortcutActivator, VoidCallback>{
          const SingleActivator(LogicalKeyboardKey.escape): widget.onClose,
        },
        child: popoutCard,
      ),
    );
  }
}

class _ResizeHandlePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = const Color(0xFF2DD4BF).withValues(alpha: 0.6)
      ..strokeWidth = 2
      ..strokeCap = StrokeCap.round;

    // Draw diagonal resize handle marks in bottom right corner
    canvas.drawLine(Offset(size.width - 6, size.height - 14), Offset(size.width - 14, size.height - 6), paint);
    canvas.drawLine(Offset(size.width - 6, size.height - 10), Offset(size.width - 10, size.height - 6), paint);
    canvas.drawLine(Offset(size.width - 6, size.height - 6), Offset(size.width - 6, size.height - 6), paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
