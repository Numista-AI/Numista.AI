import 'package:flutter/widgets.dart';

/// Marks sensitive UI regions (Estate Planning PINs, Attorney Portal tokens,
/// Lateral Transfer keys, Settings/Backup) and hard-blocks screenshot capture.
class MorganPrivacyMask extends StatefulWidget {
  final Widget child;
  final bool enabled;
  final String? reason;

  const MorganPrivacyMask({
    super.key,
    required this.child,
    this.enabled = true,
    this.reason,
  });

  static int _activeMaskCount = 0;

  static const Set<String> sensitiveRoutes = <String>{
    'estate planning',
    'attorney portal',
    'lateral transfer',
    'transfer inbox',
    'settings & backup',
    'settings',
  };

  /// Number of mounted, enabled [MorganPrivacyMask] subtrees currently visible.
  static int get activeMaskCount => _activeMaskCount;

  /// Whether any active privacy mask subtree is currently mounted.
  static bool get hasActiveMasks => _activeMaskCount > 0;

  /// Returns `true` if [route] handles PII, PINs, heirs, or account secrets.
  static bool isRouteSensitive(String? route) {
    if (route == null || route.trim().isEmpty) return false;
    final norm = route.trim().toLowerCase();
    if (sensitiveRoutes.contains(norm)) return true;
    return norm.contains('estate') ||
        norm.contains('attorney') ||
        norm.contains('lateral transfer') ||
        norm.contains('settings & backup') ||
        norm.contains('backup');
  }

  @visibleForTesting
  static void resetForTesting() {
    _activeMaskCount = 0;
  }

  @override
  State<MorganPrivacyMask> createState() => _MorganPrivacyMaskState();
}

class _MorganPrivacyMaskState extends State<MorganPrivacyMask> {
  bool _counted = false;

  @override
  void initState() {
    super.initState();
    if (widget.enabled) {
      MorganPrivacyMask._activeMaskCount++;
      _counted = true;
    }
  }

  @override
  void didUpdateWidget(covariant MorganPrivacyMask oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.enabled && !_counted) {
      MorganPrivacyMask._activeMaskCount++;
      _counted = true;
    } else if (!widget.enabled && _counted) {
      MorganPrivacyMask._activeMaskCount =
          (MorganPrivacyMask._activeMaskCount - 1).clamp(0, 1 << 20);
      _counted = false;
    }
  }

  @override
  void dispose() {
    if (_counted) {
      MorganPrivacyMask._activeMaskCount =
          (MorganPrivacyMask._activeMaskCount - 1).clamp(0, 1 << 20);
      _counted = false;
    }
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Semantics(
      container: true,
      label: widget.enabled
          ? 'Privacy protected screen region'
          : 'Unmasked screen region',
      child: widget.child,
    );
  }
}
