import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;
import 'dart:js_interop';

void webSpeak(String cleanText, double rate, double pitch, VoidCallback? onComplete, VoidCallback? onError) {
  try {
    final synth = web.window.speechSynthesis;
    final utterance = web.SpeechSynthesisUtterance(cleanText);
    utterance.rate = rate;
    utterance.pitch = pitch;
    utterance.lang = 'en-US';

    utterance.onend = ((web.Event e) {
      if (onComplete != null) onComplete();
    }).toJS;

    utterance.onerror = ((web.Event e) {
      if (onError != null) onError();
    }).toJS;

    synth.speak(utterance);
  } catch (e) {
    debugPrint('[TtsVoiceService] Web Speech API error: $e');
    if (onError != null) onError();
  }
}

void webStop() {
  try {
    web.window.speechSynthesis.cancel();
  } catch (e) {
    debugPrint('[TtsVoiceService] Error cancelling speech: $e');
  }
}
