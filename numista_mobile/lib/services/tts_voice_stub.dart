import 'package:flutter/foundation.dart';

void webSpeak(String cleanText, double rate, double pitch, VoidCallback? onComplete, VoidCallback? onError) {
  debugPrint('[TtsVoiceService] Non-web TTS fallback: $cleanText');
  if (onComplete != null) onComplete();
}

void webStop() {}
