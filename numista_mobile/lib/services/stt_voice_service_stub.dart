typedef SttResultCallback = void Function(String transcript, double confidence);
typedef SttVoidCallback = void Function();
typedef SttErrorCallback = void Function(String errorCode);

class PlatformSttBridge {
  bool get isSupported => false;
  void start({
    required SttResultCallback onResult,
    required SttVoidCallback onEnd,
    required SttErrorCallback onError,
  }) {}
  void stop() {}
}

PlatformSttBridge createPlatformSttBridge() => PlatformSttBridge();
