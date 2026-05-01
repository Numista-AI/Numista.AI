import 'package:flutter/material.dart';

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
    return AlertDialog(
      title: const Row(
        children: [
          Icon(Icons.check_circle, color: Colors.green),
          SizedBox(width: 12),
          Text('Success!'),
        ],
      ),
      content: Text('Successfully extracted $count items and sent them to the Review Hub.'),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('Add More'),
        ),
        ElevatedButton(
          onPressed: () {
            Navigator.pop(context);
            onGoToReview();
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFFF63366),
            foregroundColor: Colors.white,
          ),
          child: const Text('Go to Review Hub'),
        ),
      ],
    );
  }
}
