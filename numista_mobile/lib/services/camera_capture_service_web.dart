import 'dart:async';
import 'dart:convert';
import 'dart:js_interop';
import 'dart:ui_web' as ui_web;
import 'package:flutter/material.dart';
import 'package:web/web.dart' as web;
import 'camera_capture_service.dart';

Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
  final completer = Completer<CameraCaptureResult?>();

  // 1. Create HTML5 Video Element
  final video = web.document.createElement('video') as web.HTMLVideoElement;
  video.autoplay = true;
  video.playsInline = true;
  video.style.width = '100%';
  video.style.height = '100%';
  video.style.objectFit = 'cover';

  web.MediaStream? localStream;

  // 2. Request user webcam stream with 1280x720 ideal bounds
  final constraints = {
    'video': {
      'width': {'ideal': 1280},
      'height': {'ideal': 720},
      'facingMode': 'environment'
    }
  }.jsify() as web.MediaStreamConstraints;

  web.window.navigator.mediaDevices.getUserMedia(constraints).toDart.then((streamObj) {
    localStream = streamObj;
    video.srcObject = streamObj;
  }).catchError((err) {
    debugPrint('Webcam access error: $err');
  });

  // 3. Register Platform View with unique timestamp type ID
  final String viewType = 'webcam-view-${DateTime.now().millisecondsSinceEpoch}';
  ui_web.platformViewRegistry.registerViewFactory(
    viewType,
    (int viewId) => video,
  );

  // 4. Display Webcam Dialog
  showDialog(
    context: context,
    barrierDismissible: false,
    builder: (ctx) {
      return AlertDialog(
        backgroundColor: const Color(0xFF0F172A),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Row(
          children: [
            Icon(Icons.photo_camera, color: Color(0xFFEC4899)),
            SizedBox(width: 10),
            Text('Quick Webcam Capture',
                style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Align your coin inside the circular framing helper.',
              style: TextStyle(color: Colors.white70, fontSize: 12),
            ),
            const SizedBox(height: 16),
            Stack(
              alignment: Alignment.center,
              children: [
                // Live Stream Window
                Container(
                  width: 300,
                  height: 300,
                  decoration: const BoxDecoration(
                    color: Colors.black,
                    shape: BoxShape.circle,
                  ),
                  child: ClipOval(
                    child: HtmlElementView(viewType: viewType),
                  ),
                ),
                // Visual Circle Alignment Guide overlay
                Container(
                  width: 290,
                  height: 290,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: Colors.white.withValues(alpha: 0.5),
                      width: 2.0,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              _stopStream(localStream);
              Navigator.pop(ctx);
              completer.complete(null);
            },
            child: const Text('Cancel', style: TextStyle(color: Colors.white60)),
          ),
          ElevatedButton.icon(
            onPressed: () {
              try {
                // Grab resolution or default to standard bounds
                final width = video.videoWidth > 0 ? video.videoWidth : 1280;
                final height = video.videoHeight > 0 ? video.videoHeight : 720;

                final canvas = web.document.createElement('canvas') as web.HTMLCanvasElement;
                canvas.width = width;
                canvas.height = height;

                final renderCtx = canvas.getContext('2d') as web.CanvasRenderingContext2D;
                // Render the current frame of the video into the canvas context
                renderCtx.drawImage(video, 0, 0);

                // Export to high-quality JPEG bytes
                final dataUrl = canvas.toDataURL('image/jpeg', 0.85.toJS);
                final base64Data = dataUrl.split(',').last;
                final bytes = base64Decode(base64Data);

                _stopStream(localStream);
                Navigator.pop(ctx);
                completer.complete(CameraCaptureResult(
                  bytes: bytes,
                  name: 'webcam_${DateTime.now().millisecondsSinceEpoch}.jpg',
                ));
              } catch (e) {
                debugPrint('Capture error: $e');
                _stopStream(localStream);
                Navigator.pop(ctx);
                completer.complete(null);
              }
            },
            icon: const Icon(Icons.camera_alt),
            label: const Text('Capture Frame'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEC4899),
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
          ),
        ],
      );
    },
  );

  return completer.future;
}

void _stopStream(web.MediaStream? stream) {
  if (stream == null) return;
  try {
    final list = stream.getTracks().toDart;
    for (final track in list) {
      track.stop();
    }
  } catch (e) {
    debugPrint('Error stopping stream: $e');
  }
}
