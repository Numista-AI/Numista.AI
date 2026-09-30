import 'package:flutter/foundation.dart';
import 'tts_voice_stub.dart'
    if (dart.library.js_interop) 'tts_voice_web.dart' as tts_impl;

/// Cross-platform Text-to-Speech service prioritizing Web & Desktop Web synthesis.
/// Uses Web Speech API (window.speechSynthesis) on Web and provides full rate/pitch control.
class TtsVoiceService {
  TtsVoiceService._();

  static bool _isPlaying = false;
  static String? _currentlySpeakingText;
  static double _speechRate = 0.48; // Measured natural tone (0.48 = ~150 wpm)
  static final double _pitch = 1.0;
  static bool _autoPlay = false;

  static bool get isPlaying => _isPlaying;
  static String? get currentlySpeakingText => _currentlySpeakingText;
  static double get speechRate => _speechRate;
  static bool get autoPlay => _autoPlay;

  static void setAutoPlay(bool value) {
    _autoPlay = value;
  }

  static void setSpeechRate(double rate) {
    _speechRate = rate.clamp(0.2, 1.5);
  }

  /// Speaks text. Strips markdown symbols for clean audio output.
  static Future<void> speak(String text, {VoidCallback? onComplete}) async {
    final cleanText = _stripMarkdown(text);
    if (cleanText.isEmpty) return;

    await stop();

    _isPlaying = true;
    _currentlySpeakingText = text;

    tts_impl.webSpeak(
      cleanText,
      _speechRate,
      _pitch,
      () {
        _isPlaying = false;
        _currentlySpeakingText = null;
        if (onComplete != null) onComplete();
      },
      () {
        _isPlaying = false;
        _currentlySpeakingText = null;
      },
    );
  }

  /// Stops current speech playback.
  static Future<void> stop() async {
    tts_impl.webStop();
    _isPlaying = false;
    _currentlySpeakingText = null;
  }

  /// Toggles speech for a specific message string.
  static Future<void> toggleSpeak(String text, {VoidCallback? onStateChange}) async {
    if (_isPlaying && _currentlySpeakingText == text) {
      await stop();
    } else {
      await speak(text, onComplete: onStateChange);
    }
    if (onStateChange != null) onStateChange();
  }

  /// Clean Markdown bold, italics, links, and bullet markers for TTS.
  static String _stripMarkdown(String md) {
    return md
        .replaceAll(RegExp(r'\*\*|\*|__|`|#+'), '')
        .replaceAll(RegExp(r'\[([^\]]+)\]\([^)]+\)'), r'$1')
        .replaceAll(RegExp(r'^\s*•\s*', multiLine: true), '')
        .replaceAll(RegExp(r'^\s*-\s*', multiLine: true), '')
        .trim();
  }
}
