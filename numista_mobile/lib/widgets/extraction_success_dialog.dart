import 'package:flutter/material.dart';

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

    return AlertDialog(
      backgroundColor: const Color(0xFF1E293B),
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
            style: const TextStyle(
              color: Colors.white,
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
              style: const TextStyle(color: Colors.white70, height: 1.5),
            )
          : const Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  "I processed the file but couldn't find any coin or numismatic items.",
                  style: TextStyle(color: Colors.white70, height: 1.5),
                ),
                SizedBox(height: 12),
                Text(
                  'Common reasons:',
                  style: TextStyle(
                      color: Colors.white60,
                      fontWeight: FontWeight.w600,
                      fontSize: 13),
                ),
                SizedBox(height: 4),
                Text(
                  '• The PDF is a scanned image (no selectable text)\n'
                  '• The invoice only contains supplies or non-coin items\n'
                  '• The file is password-protected or corrupted',
                  style: TextStyle(color: Colors.white54, fontSize: 13, height: 1.6),
                ),
                SizedBox(height: 10),
                Text(
                  'Try a different file, or use the Manual Entry tab to add coins one at a time.',
                  style: TextStyle(color: Colors.white60, fontSize: 13, height: 1.5),
                ),
              ],
            ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: Text(
            hasItems ? 'Add More' : 'Try Another File',
            style: const TextStyle(color: Colors.white54),
          ),
        ),
        if (hasItems)
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
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
