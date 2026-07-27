import 'package:flutter/foundation.dart';
import 'package:web/web.dart' as web;
import 'dart:js_interop';

/// Cross-platform Text-to-Speech service prioritizing Web & Desktop Web synthesis.
/// Uses Web Speech API (window.speechSynthesis) on Web and provides full rate/pitch control.
class TtsVoiceService {
  TtsVoiceService._();

  static bool _isPlaying = false;
  static String? _currentlySpeakingText;
  static double _speechRate = 0.48; // Measured natural tone (0.48 = ~150 wpm)
  static double _pitch = 1.0;
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

    if (kIsWeb) {
      try {
        final synth = web.window.speechSynthesis;
        final utterance = web.SpeechSynthesisUtterance(cleanText);
        utterance.rate = _speechRate;
        utterance.pitch = _pitch;
        utterance.lang = 'en-US';

        _isPlaying = true;
        _currentlySpeakingText = text;

        // Callback when utterance ends
        utterance.onend = ((web.Event e) {
          _isPlaying = false;
          _currentlySpeakingText = null;
          if (onComplete != null) onComplete();
        }).toJS;

        utterance.onerror = ((web.Event e) {
          _isPlaying = false;
          _currentlySpeakingText = null;
        }).toJS;

        synth.speak(utterance);
      } catch (e) {
        debugPrint('[TtsVoiceService] Web Speech API error: $e');
        _isPlaying = false;
        _currentlySpeakingText = null;
      }
    } else {
      debugPrint('[TtsVoiceService] Non-web TTS platform fallback log: $cleanText');
    }
  }

  /// Stops current speech playback.
  static Future<void> stop() async {
    if (kIsWeb) {
      try {
        web.window.speechSynthesis.cancel();
      } catch (e) {
        debugPrint('[TtsVoiceService] Error cancelling speech: $e');
      }
    }
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
