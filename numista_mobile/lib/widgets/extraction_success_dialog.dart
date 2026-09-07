import 'package:flutter/material.dart';
import 'morgan_guide_flow.dart';

/// Shown after a PDF/file extraction attempt completes.
///
/// Handles three distinct states:
///   • count > 0  — success: coins found, sent to Review Hub
///   • count == 0 — soft failure: AI processed the file but found no coin items
///                  (common for non-coin invoices, scanned images with no text, etc.)
class ExtractionSuccessDialog extends StatelessWidget {
  final int count;
  final VoidCallback onGoToReview;

  const ExtractionSuccessDialog({
    super.key,
    required this.count,
    required this.onGoToReview,
  });

  @override
  Widget build(BuildContext context) {
    final bool hasItems = count > 0;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final bg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final text = isDark ? Colors.white : const Color(0xFF0F172A);
    final subtext = isDark ? Colors.white70 : const Color(0xFF0F172A).withAlpha(180);
    final text60 = isDark ? Colors.white60 : const Color(0xFF0F172A).withAlpha(150);
    final text54 = isDark ? Colors.white54 : const Color(0xFF0F172A).withAlpha(140);

    return AlertDialog(
      backgroundColor: bg,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Icon(
            hasItems ? Icons.check_circle_rounded : Icons.search_off_rounded,
            color: hasItems ? const Color(0xFF22C55E) : const Color(0xFFFFB300),
            size: 28,
          ),
          const SizedBox(width: 12),
          Text(
            hasItems ? 'Coins Sent to Review!' : 'Nothing Found',
            style: TextStyle(
              color: text,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
        ],
      ),
      content: hasItems
          ? Text(
              'I found $count item${count == 1 ? '' : 's'} and sent ${count == 1 ? 'it' : 'them'} '
              'to the Review Hub. Check them over and tap "Commit" to save.',
              style: TextStyle(color: subtext, height: 1.5),
            )
          : Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "I processed the file but couldn't find any coin or numismatic items.",
                  style: TextStyle(color: subtext, height: 1.5),
                ),
                const SizedBox(height: 12),
                Text(
                  'Common reasons:',
                  style: TextStyle(
                      color: text60,
                      fontWeight: FontWeight.w600,
                      fontSize: 13),
                ),
                const SizedBox(height: 4),
                Text(
                  '• The PDF is a scanned image (no selectable text)\n'
                  '• The invoice only contains supplies or non-coin items\n'
                  '• The file is password-protected or corrupted',
                  style: TextStyle(color: text54, fontSize: 13, height: 1.6),
                ),
                const SizedBox(height: 10),
                Text(
                  'Try a different file, or use the Manual Entry tab to add coins one at a time.',
                  style: TextStyle(color: text60, fontSize: 13, height: 1.5),
                ),
              ],
            ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            hasItems ? 'Add More' : 'Try Another File',
            style: TextStyle(color: text54),
          ),
        ),
        if (hasItems)
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              final guideState = MorganGuideService.current.value;
              if (guideState?.guide.id == 'guide_invoice') {
                MorganGuideService.next();
              }
              onGoToReview();
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFF63366),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(8)),
            ),
            child: const Text('Go to Review Hub'),
          ),
      ],
    );
  }
}
