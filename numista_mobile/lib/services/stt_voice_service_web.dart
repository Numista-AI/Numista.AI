import 'dart:js_interop';
import 'dart:js_interop_unsafe';

typedef SttResultCallback = void Function(String transcript, double confidence);
typedef SttVoidCallback = void Function();
typedef SttErrorCallback = void Function(String errorCode);

abstract class PlatformSttBridge {
  bool get isSupported;
  void start({
    required SttResultCallback onResult,
    required SttVoidCallback onEnd,
    required SttErrorCallback onError,
  });
  void stop();
}

class _WebSpeechSttBridge implements PlatformSttBridge {
  JSObject? _recognition;

  JSFunction? _getConstructor() {
    if (globalContext.has('SpeechRecognition')) {
      final ctor = globalContext.getProperty<JSAny?>('SpeechRecognition'.toJS);
      if (ctor != null && ctor.typeofEquals('function')) {
        return ctor as JSFunction;
      }
    }
    if (globalContext.has('webkitSpeechRecognition')) {
      final ctor =
          globalContext.getProperty<JSAny?>('webkitSpeechRecognition'.toJS);
      if (ctor != null && ctor.typeofEquals('function')) {
        return ctor as JSFunction;
      }
    }
    return null;
  }

  @override
  bool get isSupported => _getConstructor() != null;

  @override
  void start({
    required SttResultCallback onResult,
    required SttVoidCallback onEnd,
    required SttErrorCallback onError,
  }) {
    final ctor = _getConstructor();
    if (ctor == null) {
      onError('speech_recognition_unsupported');
      return;
    }
    try {
      stop();
      final rec = ctor.callAsConstructor<JSObject>();
      rec.setProperty('lang'.toJS, 'en-US'.toJS);
      rec.setProperty('continuous'.toJS, false.toJS);
      rec.setProperty('interimResults'.toJS, false.toJS);
      rec.setProperty('maxAlternatives'.toJS, 1.toJS);

      rec.setProperty(
        'onresult'.toJS,
        ((JSObject event) {
          try {
            final results = event.getProperty<JSObject?>('results'.toJS);
            if (results == null) return;
            final item = results.callMethod<JSObject?>('item'.toJS, 0.toJS);
            if (item == null) return;
            final alt = item.callMethod<JSObject?>('item'.toJS, 0.toJS);
            if (alt == null) return;
            final transcript =
                (alt.getProperty<JSString?>('transcript'.toJS)?.toDart ?? '')
                    .trim();
            final confidence =
                alt.getProperty<JSNumber?>('confidence'.toJS)?.toDartDouble ??
                    0.9;
            if (transcript.isNotEmpty) {
              onResult(transcript, confidence);
            }
          } catch (e) {
            onError('result_parse_error:$e');
          }
        }).toJS,
      );

      rec.setProperty(
        'onerror'.toJS,
        ((JSObject event) {
          final err =
              event.getProperty<JSString?>('error'.toJS)?.toDart ?? 'unknown';
          onError(err);
        }).toJS,
      );

      rec.setProperty('onend'.toJS, (() => onEnd()).toJS);

      rec.callMethod<JSAny?>('start'.toJS);
      _recognition = rec;
    } catch (e) {
      onError('start_failed:$e');
    }
  }

  @override
  void stop() {
    final rec = _recognition;
    _recognition = null;
    if (rec != null) {
      try {
        rec.callMethod<JSAny?>('stop'.toJS);
      } catch (_) {}
    }
  }
}

PlatformSttBridge createPlatformSttBridge() => _WebSpeechSttBridge();
