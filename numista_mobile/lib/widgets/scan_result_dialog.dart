import 'package:flutter/material.dart';
import '../services/checklist_scan_service.dart';

/// Shown after a checklist scan completes successfully.
/// Displays a summary card with counts and confidence, plus a "Done" action.
class ScanResultDialog extends StatelessWidget {
  final ScanResult result;
  final String programName;

  const ScanResultDialog({
    super.key,
    required this.result,
    required this.programName,
  });

  static Future<bool?> show(
    BuildContext context, {
    required ScanResult result,
    required String programName,
  }) {
    return showDialog<bool>(
      context: context,
      barrierDismissible: false,
      builder: (_) => ScanResultDialog(result: result, programName: programName),
    );
  }

  @override
  Widget build(BuildContext context) {
    final confidence = result.pageConfidence;
    final confidencePct = confidence != null
        ? '${(confidence * 100).toStringAsFixed(0)}%'
        : 'N/A';
    final confidenceColor = confidence == null
        ? Colors.grey
        : confidence >= 0.90
            ? const Color(0xFF10B981)  // green
            : confidence >= 0.75
                ? const Color(0xFFF59E0B)  // amber
                : const Color(0xFFEF4444); // red

    return Dialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 24),
      child: Container(
        constraints: BoxConstraints(
          maxWidth: 440,
          maxHeight: MediaQuery.of(context).size.height * 0.88,
        ),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withValues(alpha: 0.15),
              blurRadius: 30,
              offset: const Offset(0, 8),
            ),
          ],
        ),
        child: ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // ── Header ──────────────────────────────────────────────────────
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFF1E3A5F), Color(0xFF2563EB)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                ),
                child: Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.white.withValues(alpha: 0.15),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Icon(Icons.document_scanner,
                          color: Colors.white, size: 26),
                    ),
                    const SizedBox(width: 14),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('Scan Complete',
                              style: TextStyle(
                                  color: Colors.white,
                                  fontSize: 18,
                                  fontWeight: FontWeight.w800)),
                          const SizedBox(height: 2),
                          Text(
                            programName,
                            style: TextStyle(
                                color: Colors.white.withValues(alpha: 0.8),
                                fontSize: 13),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),

              // ── Scrollable body ──────────────────────────────────────────────
              Flexible(
                child: SingleChildScrollView(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          _StatCard(
                            icon: Icons.check_circle_rounded,
                            iconColor: const Color(0xFF10B981),
                            label: 'Coins Checked',
                            value: '${result.ownedCount}',
                            bgColor: const Color(0xFFF0FDF4),
                          ),
                          const SizedBox(width: 12),
                          _StatCard(
                            icon: Icons.radio_button_unchecked,
                            iconColor: const Color(0xFF64748B),
                            label: 'Not Checked',
                            value: '${result.notOwnedCount}',
                            bgColor: const Color(0xFFF8FAFC),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          _StatCard(
                            icon: Icons.help_outline_rounded,
                            iconColor: const Color(0xFFF59E0B),
                            label: 'Unreadable',
                            value: '${result.unreadableCount}',
                            bgColor: const Color(0xFFFFFBEB),
                            subtitle: result.unreadableCount > 0
                                ? 'Try better lighting'
                                : null,
                          ),
                          const SizedBox(width: 12),
                          _StatCard(
                            icon: Icons.analytics_outlined,
                            iconColor: confidenceColor,
                            label: 'AI Confidence',
                            value: confidencePct,
                            bgColor: const Color(0xFFF0F9FF),
                          ),
                        ],
                      ),

                      const SizedBox(height: 16),

                      // Firestore confirmation banner
                      Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 16, vertical: 12),
                        decoration: BoxDecoration(
                          color: const Color(0xFFF0FDF4),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: const Color(0xFFBBF7D0)),
                        ),
                        child: Row(
                          children: [
                            const Icon(Icons.cloud_done_rounded,
                                color: Color(0xFF10B981), size: 20),
                            const SizedBox(width: 10),
                            Expanded(
                              child: Text(
                                result.firestoreWritten
                                    ? 'Collection updated successfully! Your checked coins are now synced.'
                                    : 'Scan complete — collection sync pending.',
                                style: const TextStyle(
                                    color: Color(0xFF166534),
                                    fontSize: 13,
                                    fontWeight: FontWeight.w500),
                              ),
                            ),
                          ],
                        ),
                      ),

                      if (result.wishlistAdded > 0) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 12),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFAF5FF),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFE9D5FF)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.bookmark_add_rounded,
                                  color: Color(0xFF7C3AED), size: 20),
                              const SizedBox(width: 10),
                              Expanded(
                                child: Text(
                                  '${result.wishlistAdded} coin${result.wishlistAdded == 1 ? '' : 's'} added to your Wish List.',
                                  style: const TextStyle(
                                      color: Color(0xFF4C1D95),
                                      fontSize: 13,
                                      fontWeight: FontWeight.w500),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],

                      if (result.unreadableCount > 0) ...[
                        const SizedBox(height: 10),
                        Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 16, vertical: 10),
                          decoration: BoxDecoration(
                            color: const Color(0xFFFFFBEB),
                            borderRadius: BorderRadius.circular(10),
                            border: Border.all(color: const Color(0xFFFDE68A)),
                          ),
                          child: Row(
                            children: [
                              const Icon(Icons.tips_and_updates_outlined,
                                  color: Color(0xFFD97706), size: 18),
                              const SizedBox(width: 10),
                              const Expanded(
                                child: Text(
                                  'Tip: For best results, use bright, even lighting and hold the camera directly above the checklist.',
                                  style: TextStyle(
                                      color: Color(0xFF92400E), fontSize: 12),
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ],
                  ),
                ),
              ),

              // ── Action Buttons (always visible at bottom) ────────────────────
              Padding(
                padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
                child: Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => Navigator.of(context).pop(false),
                        style: OutlinedButton.styleFrom(
                          foregroundColor: const Color(0xFF475569),
                          side: const BorderSide(color: Color(0xFFE2E8F0)),
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: const Text('Scan Another Page'),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () => Navigator.of(context).pop(true),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF2563EB),
                          foregroundColor: Colors.white,
                          elevation: 0,
                          shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(10)),
                          padding: const EdgeInsets.symmetric(vertical: 14),
                        ),
                        child: const Text('Done',
                            style: TextStyle(fontWeight: FontWeight.w700)),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final Color bgColor;
  final String label;
  final String value;
  final String? subtitle;

  const _StatCard({
    required this.icon,
    required this.iconColor,
    required this.bgColor,
    required this.label,
    required this.value,
    this.subtitle,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: bgColor,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.black.withValues(alpha: 0.05)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(icon, color: iconColor, size: 22),
            const SizedBox(height: 8),
            Text(value,
                style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w800,
                    color: Color(0xFF0F172A))),
            Text(label,
                style: const TextStyle(
                    fontSize: 12,
                    color: Color(0xFF64748B),
                    fontWeight: FontWeight.w500)),
            if (subtitle != null) ...[
              const SizedBox(height: 2),
              Text(subtitle!,
                  style: const TextStyle(
                      fontSize: 10, color: Color(0xFFF59E0B))),
            ],
          ],
        ),
      ),
    );
  }
}
