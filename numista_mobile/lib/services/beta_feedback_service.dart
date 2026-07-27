import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/foundation.dart';
import 'auth_service.dart';
import 'beta_screenshot_service.dart';

class BetaFeedbackPayload {
  final String route;
  final String pageTitle;
  final String category;
  final int easeOfUseRating;
  final int funRating;
  final int utilityRating;
  final String comment;
  final Uint8List? screenshotBytes;
  final String viewportResolution;

  BetaFeedbackPayload({
    required this.route,
    required this.pageTitle,
    required this.category,
    required this.easeOfUseRating,
    required this.funRating,
    required this.utilityRating,
    required this.comment,
    this.screenshotBytes,
    this.viewportResolution = '1920x1080',
  });
}

class BetaFeedbackService {
  static final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  /// Submits a feedback payload to Firestore under `beta_feedback/{id}`.
  static Future<bool> submitFeedback(BetaFeedbackPayload payload) async {
    try {
      final userEmail = AuthService.userEmail.isNotEmpty
          ? AuthService.userEmail
          : 'anonymous_tester';
      final userId = AuthService.currentUser?.uid ?? '';

      String? screenshotUrl;
      if (payload.screenshotBytes != null) {
        screenshotUrl = await BetaScreenshotService.uploadScreenshot(
          imageBytes: payload.screenshotBytes!,
          userEmail: userEmail,
        );
      }

      final docRef = _firestore.collection('beta_feedback').doc();
      final data = <String, dynamic>{
        'feedback_id': docRef.id,
        'user_email': userEmail,
        'user_id': userId,
        'route': payload.route,
        'page_title': payload.pageTitle,
        'app_version': '0.9.5-beta',
        'viewport_resolution': payload.viewportResolution,
        'category': payload.category,
        'ratings': {
          'ease_of_use': payload.easeOfUseRating,
          'fun_value': payload.funRating,
          'utility_value': payload.utilityRating,
        },
        'comment': payload.comment,
        'screenshot_url': screenshotUrl,
        'status': 'OPEN',
        'created_at': FieldValue.serverTimestamp(),
      };

      await docRef.set(data);
      return true;
    } catch (e) {
      debugPrint('BetaFeedbackService: Submit feedback failed — $e');
      return false;
    }
  }

  /// Admin method: Fetches all feedback submissions sorted by creation date.
  static Stream<QuerySnapshot<Map<String, dynamic>>> getFeedbackStream() {
    return _firestore
        .collection('beta_feedback')
        .orderBy('created_at', descending: true)
        .snapshots();
  }

  /// Admin method: Updates status of a feedback item (OPEN, TRIAGED, RESOLVED).
  static Future<void> updateFeedbackStatus(String feedbackId, String newStatus) async {
    await _firestore
        .collection('beta_feedback')
        .doc(feedbackId)
        .update({'status': newStatus});
  }
}
