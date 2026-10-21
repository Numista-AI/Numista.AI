import 'package:flutter/foundation.dart';
import 'package:image_picker/image_picker.dart';
import '../utils/platform_gate.dart';

class RecoveredCameraData {
  final Uint8List bytes;
  final String name;
  final String path;

  RecoveredCameraData({
    required this.bytes,
    required this.name,
    required this.path,
  });
}

class CameraRecoveryService {
  static ImagePicker picker = ImagePicker();
  static RecoveredCameraData? latestRecovered;
  static String? lastError;

  /// Check for any lost image data from an activity restart on Android.
  static Future<RecoveredCameraData?> retrieveLostData() async {
    if (!isNativePhone) return null;
    try {
      final LostDataResponse response = await picker.retrieveLostData();
      if (response.isEmpty) {
        return null;
      }
      final file = response.file;
      if (file != null) {
        try {
          final bytes = await file.readAsBytes();
          final recovered = RecoveredCameraData(
            bytes: bytes,
            name: file.name,
            path: file.path,
          );
          latestRecovered = recovered;
          lastError = null;
          debugPrint('CameraRecoveryService: successfully recovered lost photo: ${file.name} (${bytes.length} bytes)');
          return recovered;
        } catch (e) {
          lastError = 'Photo file could not be read: $e';
          debugPrint('CameraRecoveryService error reading file: $e');
          return null;
        }
      }
      if (response.exception != null) {
        lastError = response.exception!.message ?? response.exception.toString();
        debugPrint('CameraRecoveryService lost data exception: ${response.exception}');
      }
    } catch (e) {
      debugPrint('CameraRecoveryService check failed: $e');
    }
    return null;
  }
}
