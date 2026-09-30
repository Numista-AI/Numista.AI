import 'package:flutter/foundation.dart';

void webSpeak(String cleanText, double rate, double pitch, VoidCallback? onComplete, VoidCallback? onError) {
  debugPrint('[TtsVoiceService] Voice playback is not available on mobile yet.');
  if (onError != null) {
    onError();
  }
}

void webStop() {}

