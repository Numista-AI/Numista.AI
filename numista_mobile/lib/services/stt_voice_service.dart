import 'dart:async';
import 'package:flutter/foundation.dart';
import 'morgan_test_harness.dart';
import 'morgan_voice_confirmation_parser.dart';
import 'stt_voice_service_stub.dart'
    if (dart.library.js_interop) 'stt_voice_service_web.dart';
import 'tts_voice_service.dart';

class SttUtteranceEvent {
  final String rawTranscript;
  final String normalizedTranscript;
  final double confidence;
  final int? delayAfterTtsMs;
  final bool otherSpeechInWindow;

  const SttUtteranceEvent({
    required this.rawTranscript,
    required this.normalizedTranscript,
    required this.confidence,
    this.delayAfterTtsMs,
    this.otherSpeechInWindow = false,
  });
}

/// Half-duplex Speech-to-Text controller interlocked with [TtsVoiceService].
///
/// Automatically mutes microphone listening while Morgan TTS is speaking and for
/// a 450ms acoustic tail afterward, gracefully degrades when Web Speech API is
/// unavailable, and accepts deterministic test-harness injections (§7.4 & §13.5).
class SttVoiceService extends ChangeNotifier {
  static final SttVoiceService instance = SttVoiceService._();

  final PlatformSttBridge _bridge = createPlatformSttBridge();

  bool _wantListening = false;
  bool _isListening = false;
  bool _isPausedForTts = false;
  bool _inPostTtsTail = false;
  bool _micAllowed = true;
  bool _otherSpeechOccurredInWindow = false;
  String? _lastError;
  int ignoredEchoCount = 0;

  Timer? _tailTimer;
  void Function(SttUtteranceEvent event)? onUtterance;

  SttVoiceService._() {
    TtsVoiceService.isSpeakingNotifier.addListener(_onTtsSpeakingChanged);
    MorganTestHarness.voiceInjectionHook = _handleHarnessInjection;
  }

  bool get isSupported => _bridge.isSupported || MorganTestHarness.isEnabled;
  bool get isListening => _isListening && !isSpeakingLocked;
  bool get isPausedForTts => _isPausedForTts;
  bool get isSpeakingLocked =>
      TtsVoiceService.isSpeakingNotifier.value || _inPostTtsTail;
  bool get micAllowed => _micAllowed;
  String? get lastError => _lastError;

  set micAllowed(bool value) {
    if (_micAllowed == value) return;
    _micAllowed = value;
    if (!value) {
      stopListening();
    }
    notifyListeners();
  }

  void _onTtsSpeakingChanged() {
    final speaking = TtsVoiceService.isSpeakingNotifier.value;
    _tailTimer?.cancel();
    if (speaking) {
      _isPausedForTts = true;
      _inPostTtsTail = false;
      _otherSpeechOccurredInWindow = false;
      if (_isListening) {
        _bridge.stop();
        _isListening = false;
      }
      notifyListeners();
    } else if (_isPausedForTts) {
      _inPostTtsTail = true;
      notifyListeners();
      _tailTimer = Timer(
        const Duration(milliseconds: MorganVoiceConfirmationParser.ttsTailGuardMs),
        () {
          _inPostTtsTail = false;
          _isPausedForTts = false;
          if (_wantListening && _micAllowed) {
            _startPlatformRecognition();
          } else {
            notifyListeners();
          }
        },
      );
    }
  }

  void startListening() {
    if (!_micAllowed) {
      _lastError = 'microphone_disabled_in_settings';
      notifyListeners();
      return;
    }
    _wantListening = true;
    _lastError = null;
    if (isSpeakingLocked) {
      _isPausedForTts = true;
      notifyListeners();
      return;
    }
    _startPlatformRecognition();
  }

  void stopListening() {
    _wantListening = false;
    _tailTimer?.cancel();
    _inPostTtsTail = false;
    _isPausedForTts = false;
    _bridge.stop();
    _isListening = false;
    notifyListeners();
  }

  void _startPlatformRecognition() {
    if (!_bridge.isSupported) {
      _isListening = false;
      _lastError = 'speech_recognition_unavailable';
      notifyListeners();
      return;
    }
    _isListening = true;
    notifyListeners();
    _bridge.start(
      onResult: (transcript, confidence) {
        final endedAt = TtsVoiceService.lastSpeechEndedAt;
        final delayMs = endedAt == null
            ? null
            : DateTime.now().difference(endedAt).inMilliseconds;
        _ingestUtterance(
          transcript,
          confidence: confidence,
          duringTtsPlayback: TtsVoiceService.isSpeakingNotifier.value,
          delayAfterTtsMs: delayMs,
        );
      },
      onEnd: () {
        _isListening = false;
        _wantListening = false;
        notifyListeners();
      },
      onError: (err) {
        _isListening = false;
        _wantListening = false;
        _lastError = err;
        notifyListeners();
      },
    );
  }

  Future<void> _handleHarnessInjection(
    String transcript, {
    bool duringTtsPlayback = false,
    int delayAfterTtsMs = 500,
    double confidence = 0.92,
  }) async {
    _ingestUtterance(
      transcript,
      confidence: confidence,
      duringTtsPlayback: duringTtsPlayback,
      delayAfterTtsMs: delayAfterTtsMs,
    );
  }

  void _ingestUtterance(
    String transcript, {
    required double confidence,
    required bool duringTtsPlayback,
    int? delayAfterTtsMs,
  }) {
    if (!_micAllowed) return;

    if (duringTtsPlayback ||
        TtsVoiceService.isSpeakingNotifier.value ||
        _inPostTtsTail ||
        (delayAfterTtsMs != null &&
            delayAfterTtsMs < MorganVoiceConfirmationParser.ttsTailGuardMs)) {
      ignoredEchoCount++;
      notifyListeners();
      return;
    }

    final normalized =
        MorganVoiceConfirmationParser.normalizeNumismaticTranscript(transcript);
    final event = SttUtteranceEvent(
      rawTranscript: transcript,
      normalizedTranscript: normalized,
      confidence: confidence,
      delayAfterTtsMs: delayAfterTtsMs,
      otherSpeechInWindow: _otherSpeechOccurredInWindow,
    );
    _otherSpeechOccurredInWindow = true;
    onUtterance?.call(event);
    notifyListeners();
  }

  /// Evaluates the latest [event] against [MorganVoiceConfirmationParser] cleanly.
  MorganVoiceConfirmationResult evaluateConfirmationUtterance(
    SttUtteranceEvent event, {
    required bool isConfirmationCardVisible,
    String expectedGateAction = 'add_coin',
  }) {
    return MorganVoiceConfirmationParser.evaluate(
      event.rawTranscript,
      isConfirmationCardVisible: isConfirmationCardVisible,
      expectedGateAction: expectedGateAction,
      duringTtsPlayback: TtsVoiceService.isSpeakingNotifier.value,
      delayAfterTtsMs: event.delayAfterTtsMs,
      confidence: event.confidence,
      otherSpeechOccurredInWindow: false,
    );
  }

  /// Clears intra-window speech tracking when a confirmation card opens.
  void resetConfirmationWindow() {
    _otherSpeechOccurredInWindow = false;
  }

  @visibleForTesting
  void resetForTesting() {
    stopListening();
    _micAllowed = true;
    _lastError = null;
    ignoredEchoCount = 0;
    _otherSpeechOccurredInWindow = false;
    onUtterance = null;
    MorganTestHarness.voiceInjectionHook = _handleHarnessInjection;
    notifyListeners();
  }
}
