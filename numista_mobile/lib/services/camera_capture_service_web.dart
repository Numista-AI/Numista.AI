import 'dart:async';
import 'dart:convert';
import 'dart:js_interop';
import 'dart:ui_web' as ui_web;
import 'package:flutter/material.dart';
import 'package:web/web.dart' as web;
import 'camera_capture_service.dart';
import 'package:image_picker/image_picker.dart';


Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
  final completer = Completer<CameraCaptureResult?>();

  // 1. Create HTML5 Video Element
  final video = web.document.createElement('video') as web.HTMLVideoElement;
  video.autoplay = true;
  video.playsInline = true;
  video.muted = true;
  video.style.width = '100%';
  video.style.height = '100%';
  video.style.objectFit = 'cover';

  // Force autoplay policy attributes
  video.setAttribute('autoplay', 'true');
  video.setAttribute('playsinline', 'true');
  video.setAttribute('muted', 'true');

  web.MediaStream? localStream;
  String? errorMessage;
  bool isLoading = true;
  StateSetter? dialogSetState;

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
    
    // Explicitly call play() to trigger video rendering
    video.play();
    
    isLoading = false;
    if (dialogSetState != null) {
      dialogSetState!(() {});
    }
  }).catchError((err) {
    debugPrint('Webcam access error: $err');
    isLoading = false;
    final errStr = err.toString().toLowerCase();
    if (errStr.contains('permission') || errStr.contains('notallowed') || errStr.contains('denied')) {
      errorMessage = 'Camera access was denied. Please allow camera permissions in your browser settings.';
    } else {
      errorMessage = "We couldn't find a camera on this device.";
    }
    if (dialogSetState != null) {
      dialogSetState!(() {});
    }
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
      return StatefulBuilder(
        builder: (dialogCtx, setState) {
          dialogSetState = setState;

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
                if (errorMessage == null) ...[
                  const Text(
                    'Align your coin inside the circular framing helper.',
                    style: TextStyle(color: Colors.white70, fontSize: 16),
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
                          child: isLoading
                              ? const Center(
                                  child: CircularProgressIndicator(color: Color(0xFFEC4899)),
                                )
                              : HtmlElementView(viewType: viewType),
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
                ] else ...[
                  Container(
                    width: 320,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withAlpha(10),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: const Color(0xFFF87171).withAlpha(80)),
                    ),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.videocam_off_outlined, color: Color(0xFFF87171), size: 48),
                        const SizedBox(height: 14),
                        Text(
                          errorMessage!,
                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 10),
                        const Text(
                          'You can choose an image file from your device instead.',
                          style: TextStyle(color: Colors.white70, fontSize: 16),
                          textAlign: TextAlign.center,
                        ),
                        const SizedBox(height: 20),
                        ElevatedButton.icon(
                          key: const Key('webcam_upload_photo_button'),
                          onPressed: () async {
                            try {
                              final picked = await ImagePicker().pickImage(
                                source: ImageSource.gallery,
                                maxWidth: 1920,
                                maxHeight: 1920,
                                imageQuality: 85,
                              );
                              if (picked != null) {
                                final bytes = await picked.readAsBytes();
                                _stopStream(localStream);
                                if (ctx.mounted) Navigator.pop(ctx);
                                completer.complete(CameraCaptureResult(
                                  bytes: bytes,
                                  name: picked.name.isNotEmpty ? picked.name : 'upload_${DateTime.now().millisecondsSinceEpoch}.jpg',
                                ));
                              }
                            } catch (e) {
                              debugPrint('Fallback photo pick error: $e');
                            }
                          },
                          icon: const Icon(Icons.upload_file, size: 22),
                          label: const Text('Upload a photo instead',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            minimumSize: const Size(double.infinity, 56),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            actions: [
              TextButton(
                onPressed: () {
                  _stopStream(localStream);
                  Navigator.pop(ctx);
                  completer.complete(null);
                },
                style: TextButton.styleFrom(
                  minimumSize: const Size(100, 48),
                ),
                child: const Text('Cancel', style: TextStyle(color: Colors.white70, fontSize: 18)),
              ),
              if (errorMessage == null)
                ElevatedButton.icon(
                onPressed: (isLoading || errorMessage != null)
                    ? null
                    : () {
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
                  disabledBackgroundColor: Colors.grey.shade800,
                  disabledForegroundColor: Colors.white30,
                  minimumSize: const Size(160, 48),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          );
        },
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
