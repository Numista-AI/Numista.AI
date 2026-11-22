import 'package:flutter/material.dart';

/// Two-part Morgan | Full site toggle (Plan v3.2 §4):
/// - 56px tall, #1D4F91 blue on #FFFFFF white, AAA contrast
/// - Both parts have words and icons
/// - Active part is solid #1D4F91 blue with white text
class MorganFullSiteToggle extends StatelessWidget {
  final bool isMorganActive;
  final VoidCallback onSelectMorgan;
  final VoidCallback onSelectFullSite;
  final bool expandFullWidth;

  const MorganFullSiteToggle({
    super.key,
    required this.isMorganActive,
    required this.onSelectMorgan,
    required this.onSelectFullSite,
    this.expandFullWidth = false,
  });

  static const Color _navy = Color(0xFF0B1A2E);
  static const Color _blue = Color(0xFF1D4F91);
  static const Color _white = Color(0xFFFFFFFF);

  @override
  Widget build(BuildContext context) {
    final morganBtn = _buildSegment(
      key: const Key('toggle_morgan_mode'),
      label: 'Morgan',
      icon: Icons.auto_awesome_outlined,
      active: isMorganActive,
      onTap: onSelectMorgan,
      isLeft: true,
    );
    final fullSiteBtn = _buildSegment(
      key: const Key('toggle_full_site_mode'),
      label: 'Full site',
      icon: Icons.grid_view_rounded,
      active: !isMorganActive,
      onTap: onSelectFullSite,
      isLeft: false,
    );

    return Container(
      height: 56,
      decoration: BoxDecoration(
        color: _white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: _blue, width: 2),
      ),
      child: Row(
        mainAxisSize: expandFullWidth ? MainAxisSize.max : MainAxisSize.min,
        children: expandFullWidth
            ? [Expanded(child: morganBtn), Expanded(child: fullSiteBtn)]
            : [morganBtn, fullSiteBtn],
      ),
    );
  }

  Widget _buildSegment({
    required Key key,
    required String label,
    required IconData icon,
    required bool active,
    required VoidCallback onTap,
    required bool isLeft,
  }) {
    return InkWell(
      key: key,
      onTap: onTap,
      borderRadius: BorderRadius.horizontal(
        left: isLeft ? const Radius.circular(10) : Radius.zero,
        right: !isLeft ? const Radius.circular(10) : Radius.zero,
      ),
      child: Container(
        height: 52,
        padding: const EdgeInsets.symmetric(horizontal: 10),
        decoration: BoxDecoration(
          color: active ? _blue : _white,
          borderRadius: BorderRadius.horizontal(
            left: isLeft ? const Radius.circular(9) : Radius.zero,
            right: !isLeft ? const Radius.circular(9) : Radius.zero,
          ),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 22, color: active ? _white : _navy),
            const SizedBox(width: 6),
            Flexible(
              child: FittedBox(
                fit: BoxFit.scaleDown,
                child: Text(
                  label,
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w700,
                    color: active ? _white : _navy,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Top bar shown on the Full site when Morgan-First is eligible (Plan v3.2 §4).
class FullSiteMorganBar extends StatelessWidget {
  final VoidCallback onBackToMorgan;

  const FullSiteMorganBar({super.key, required this.onBackToMorgan});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: const BoxDecoration(
        color: Color(0xFFF3F6FA),
        border: Border(
          bottom: BorderSide(color: Color(0xFF1D4F91), width: 1.5),
        ),
      ),
      child: Wrap(
        alignment: WrapAlignment.spaceBetween,
        crossAxisAlignment: WrapCrossAlignment.center,
        spacing: 12,
        runSpacing: 8,
        children: [
          const Text(
            'You are on the Full site.',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w700,
              color: Color(0xFF0B1A2E),
            ),
          ),
          ElevatedButton.icon(
            key: const Key('back_to_morgan_button'),
            onPressed: onBackToMorgan,
            icon: const Icon(Icons.arrow_back, size: 22, color: Color(0xFFFFFFFF)),
            label: const Text(
              'Back to Morgan',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.w700,
                color: Color(0xFFFFFFFF),
              ),
            ),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF1D4F91),
              minimumSize: const Size(180, 56),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(10),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
