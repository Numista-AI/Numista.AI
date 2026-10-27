import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'camera_capture_service.dart';

Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
  try {
    final picked = await ImagePicker().pickImage(
      source: ImageSource.camera,
      maxWidth: 1600,
      maxHeight: 1600,
      imageQuality: 75,
    );
    if (picked == null) return null;
    try {
      final bytes = await picked.readAsBytes();
      return CameraCaptureResult(bytes: bytes, name: picked.name);
    } catch (e) {
      debugPrint('Mobile camera capture error reading bytes: $e');
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Camera photo could not be read. Please tap to try again.'),
            backgroundColor: Color(0xFFEF4444),
          ),
        );
      }
      return null;
    }
  } catch (e) {
    debugPrint('Mobile camera capture error: $e');
    return null;
  }
}
