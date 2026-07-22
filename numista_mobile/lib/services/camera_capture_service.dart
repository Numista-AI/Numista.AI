import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'camera_capture_service_web.dart'
    if (dart.library.io) 'camera_capture_service_mobile.dart' as platform;

class CameraCaptureResult {
  final Uint8List bytes;
  final String name;
  const CameraCaptureResult({required this.bytes, required this.name});
}

class CameraCaptureService {
  static Future<CameraCaptureResult?> capturePhoto(BuildContext context) async {
    return platform.capturePhotoPlatform(context);
  }
}
