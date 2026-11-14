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

  // 2. Request user webcam stream with 1280x720 ideal bounds.
  // Never pass facingMode:'environment' on desktop browsers because Windows
  // routes it to Phone Link Virtual Camera.
  final constraints = {
    'video': {
      'width': {'ideal': 1280},
      'height': {'ideal': 720},
    }
  }.jsify() as web.MediaStreamConstraints;

  _requestPreferredWebCameraStream(constraints).then((streamObj) {
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
              if (errorMessage == null)
                _WebCameraSelectorButton(
                  videoElement: video,
                  onStreamSwitched: (newStream) {
                    localStream = newStream;
                  },
                ),
              SizedBox(
                height: 48,
                child: TextButton(
                  onPressed: () {
                    _stopStream(localStream);
                    final src = video.srcObject;
                    if (src != null) {
                      _stopStream(src as web.MediaStream);
                    }
                    Navigator.pop(ctx);
                    completer.complete(null);
                  },
                  style: TextButton.styleFrom(
                    minimumSize: const Size(100, 48),
                  ),
                  child: const Text('Cancel', style: TextStyle(color: Colors.white70, fontSize: 18)),
                ),
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
                          final src = video.srcObject;
                          if (src != null) {
                            _stopStream(src as web.MediaStream);
                          }
                          Navigator.pop(ctx);
                          completer.complete(CameraCaptureResult(
                            bytes: bytes,
                            name: 'webcam_${DateTime.now().millisecondsSinceEpoch}.jpg',
                          ));
                        } catch (e) {
                          debugPrint('Capture error: $e');
                          _stopStream(localStream);
                          final src = video.srcObject;
                          if (src != null) {
                            _stopStream(src as web.MediaStream);
                          }
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

final RegExp _blockedWebCameraPattern = RegExp(
  r'phone\s*link|link\s*to\s*windows|windows\s*virtual|cross[\s_-]?device|continuity|virtual|droidcam|iriun|epoccam|infrared|\bir\s+camera\b|windows\s*hello',
  caseSensitive: false,
);

final RegExp _preferredMicroscopePattern = RegExp(
  r'microscope|jiusion|tomlov|plugable|celestron|andostar|hayear|usb2\.0|usb\s*2\.0|uvc',
  caseSensitive: false,
);

bool _isBlockedWebCameraLabel(String label) =>
    label.trim().isNotEmpty && _blockedWebCameraPattern.hasMatch(label);

bool _isPreferredWebCameraLabel(String label) =>
    !_isBlockedWebCameraLabel(label) &&
    _preferredMicroscopePattern.hasMatch(label);

Future<List<web.MediaDeviceInfo>> _enumerateSafeWebVideoDevices() async {
  try {
    final raw = await web.window.navigator.mediaDevices.enumerateDevices().toDart;
    final devices = raw.toDart;
    final safe = <web.MediaDeviceInfo>[];
    for (final d in devices) {
      if (d.kind != 'videoinput') continue;
      if (_isBlockedWebCameraLabel(d.label)) continue;
      safe.add(d);
    }
    safe.sort((a, b) {
      final aPref = _isPreferredWebCameraLabel(a.label) ? 0 : 1;
      final bPref = _isPreferredWebCameraLabel(b.label) ? 0 : 1;
      return aPref.compareTo(bPref);
    });
    return safe;
  } catch (e) {
    debugPrint('enumerateDevices failed: $e');
    return const [];
  }
}

Future<web.MediaStream> _requestPreferredWebCameraStream(
  web.MediaStreamConstraints fallbackConstraints,
) async {
  final preSafe = await _enumerateSafeWebVideoDevices();
  final labeledSafe =
      preSafe.where((d) => d.label.trim().isNotEmpty && d.deviceId.isNotEmpty).toList();
  if (labeledSafe.isNotEmpty) {
    final bestId = labeledSafe.first.deviceId;
    try {
      final specific = {
        'video': {
          'width': {'ideal': 1280},
          'height': {'ideal': 720},
          'deviceId': {'exact': bestId},
        }
      }.jsify() as web.MediaStreamConstraints;
      return await web.window.navigator.mediaDevices.getUserMedia(specific).toDart;
    } catch (_) {
      // Fall through to generic constraints
    }
  }

  final stream = await web.window.navigator.mediaDevices
      .getUserMedia(fallbackConstraints)
      .toDart;

  // Verify the granted stream did not bind to Phone Link / Virtual camera.
  try {
    final videoTracks = stream.getVideoTracks().toDart;
    final activeLabel = videoTracks.isNotEmpty ? videoTracks.first.label : '';
    final postSafe = await _enumerateSafeWebVideoDevices();
    final hasPreferredUpgrade = postSafe.any(
      (d) => _isPreferredWebCameraLabel(d.label) && d.label != activeLabel,
    );
    if (_isBlockedWebCameraLabel(activeLabel) || hasPreferredUpgrade) {
      final target = postSafe.where((d) => d.deviceId.isNotEmpty).toList();
      if (target.isNotEmpty) {
        _stopStream(stream);
        final specific = {
          'video': {
            'width': {'ideal': 1280},
            'height': {'ideal': 720},
            'deviceId': {'exact': target.first.deviceId},
          }
        }.jsify() as web.MediaStreamConstraints;
        return await web.window.navigator.mediaDevices
            .getUserMedia(specific)
            .toDart;
      }
    }
  } catch (_) {}

  return stream;
}

class _WebCameraSelectorButton extends StatefulWidget {
  final web.HTMLVideoElement videoElement;
  final void Function(web.MediaStream newStream) onStreamSwitched;

  const _WebCameraSelectorButton({
    required this.videoElement,
    required this.onStreamSwitched,
  });

  @override
  State<_WebCameraSelectorButton> createState() =>
      _WebCameraSelectorButtonState();
}

class _WebCameraSelectorButtonState extends State<_WebCameraSelectorButton> {
  List<web.MediaDeviceInfo> _devices = const [];
  String? _selectedDeviceId;

  @override
  void initState() {
    super.initState();
    _refreshDevices();
  }

  Future<void> _refreshDevices() async {
    final safe = await _enumerateSafeWebVideoDevices();
    if (!mounted) return;
    String? currentId = _selectedDeviceId;
    if (currentId == null && safe.isNotEmpty) {
      final srcObj = widget.videoElement.srcObject;
      if (srcObj != null) {
        final tracks = (srcObj as web.MediaStream).getVideoTracks().toDart;
        final activeLabel = tracks.isNotEmpty ? tracks.first.label : '';
        final match = safe.where((d) => d.label == activeLabel).toList();
        currentId = match.isNotEmpty ? match.first.deviceId : safe.first.deviceId;
      } else {
        currentId = safe.first.deviceId;
      }
    }
    setState(() {
      _devices = safe;
      _selectedDeviceId = currentId;
    });
  }

  Future<void> _switchCamera(String deviceId) async {
    try {
      final existing = widget.videoElement.srcObject;
      if (existing != null) {
        _stopStream(existing as web.MediaStream);
      }
      final constraints = {
        'video': {
          'width': {'ideal': 1280},
          'height': {'ideal': 720},
          'deviceId': {'exact': deviceId},
        }
      }.jsify() as web.MediaStreamConstraints;
      final newStream =
          await web.window.navigator.mediaDevices.getUserMedia(constraints).toDart;
      widget.videoElement.srcObject = newStream;
      widget.onStreamSwitched(newStream);
      if (mounted) {
        setState(() => _selectedDeviceId = deviceId);
      }
    } catch (e) {
      debugPrint('Failed to switch web camera: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    final validDevices = _devices
        .where((d) => d.deviceId.isNotEmpty)
        .toList(growable: false);
    if (validDevices.length <= 1) {
      return const SizedBox.shrink();
    }
    final activeValue =
        validDevices.any((d) => d.deviceId == _selectedDeviceId)
            ? _selectedDeviceId
            : validDevices.first.deviceId;
    return Semantics(
      identifier: 'morgan_web_camera_selector',
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: activeValue,
          dropdownColor: const Color(0xFF1E293B),
          style: const TextStyle(color: Colors.white, fontSize: 15),
          items: validDevices.map((d) {
            final label = d.label.trim().isNotEmpty
                ? d.label
                : 'Camera ${validDevices.indexOf(d) + 1}';
            return DropdownMenuItem<String>(
              value: d.deviceId,
              child: ConstrainedBox(
                constraints: const BoxConstraints(maxWidth: 210),
                child: Text(label, overflow: TextOverflow.ellipsis),
              ),
            );
          }).toList(),
          onChanged: (value) {
            if (value != null && value != _selectedDeviceId) {
              _switchCamera(value);
            }
          },
        ),
      ),
    );
  }
}
