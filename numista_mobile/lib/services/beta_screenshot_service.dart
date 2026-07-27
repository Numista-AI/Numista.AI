import 'package:firebase_storage/firebase_storage.dart';
import 'package:flutter/foundation.dart';

/// Handles uploading feedback screenshots to Google Cloud Storage (GCS)
/// under gs://studio-9101802118-8c9a8-uploads/beta_screenshots/
class BetaScreenshotService {
  static final FirebaseStorage _storage = FirebaseStorage.instance;

  /// Uploads raw image bytes to GCS and returns the public HTTPS URL.
  /// If upload fails (e.g. offline or low bandwidth), returns null for fallback.
  static Future<String?> uploadScreenshot({
    required Uint8List imageBytes,
    required String userEmail,
  }) async {
    try {
      final timestamp = DateTime.now().millisecondsSinceEpoch;
      final sanitizedEmail = userEmail.replaceAll(RegExp(r'[^a-zA-Z0-9]'), '_');
      final fileName = 'beta_screenshots/fb_${sanitizedEmail}_$timestamp.png';

      final ref = _storage.ref().child(fileName);
      final metadata = SettableMetadata(
        contentType: 'image/png',
        customMetadata: {
          'user_email': userEmail,
          'uploaded_at': DateTime.now().toIso8601String(),
        },
      );

      final uploadTask = await ref.putData(imageBytes, metadata);
      final downloadUrl = await uploadTask.ref.getDownloadURL();
      return downloadUrl;
    } catch (e) {
      debugPrint('BetaScreenshotService: GCS upload failed/fallback — $e');
      return null;
    }
  }
}
