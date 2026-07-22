import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'camera_capture_service.dart';

Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
  try {
    final picked = await ImagePicker().pickImage(
      source: ImageSource.camera,
      maxWidth: 1920,
      maxHeight: 1920,
      imageQuality: 80,
    );
    if (picked == null) return null;
    final bytes = await picked.readAsBytes();
    return CameraCaptureResult(bytes: bytes, name: picked.name);
  } catch (e) {
    debugPrint('Mobile camera capture error: $e');
    return null;
  }
}
