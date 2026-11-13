import 'package:firebase_remote_config/firebase_remote_config.dart';
import 'package:flutter/foundation.dart';

/// Centralized AI model configuration for Numista.AI mobile/web clients.
///
/// Reads model IDs from Firebase Remote Config so models can be rolled back
/// or upgraded immediately without an App Store / Play Store binary release.
/// Static constants serve only as offline / uninitialized fallback defaults.
class AiConfig {
  AiConfig._();

  static const String defaultFlashModel = 'gemini-4-hydrogen';
  static const String defaultProModel = 'gemini-4-argon';
  static const String defaultLiteModel = 'gemini-3.5-flash-lite';
  static const String defaultImageModel = 'gemini-3.1-flash-image';
  static const String defaultImageProModel = 'gemini-3-pro-image';
  static const String defaultEmbeddingModel = 'gemini-embedding-2';

  static const Map<String, Object> _defaults = <String, Object>{
    'gemini_flash_model': defaultFlashModel,
    'gemini_pro_model': defaultProModel,
    'gemini_lite_model': defaultLiteModel,
    'gemini_image_model': defaultImageModel,
    'gemini_image_pro_model': defaultImageProModel,
    'gemini_embedding_model': defaultEmbeddingModel,
  };

  static bool _initialized = false;

  /// Non-blocking initialization: sets Remote Config defaults and fetches updates.
  static Future<void> init() async {
    if (_initialized) return;
    _initialized = true;
    try {
      final rc = FirebaseRemoteConfig.instance;
      await rc.setConfigSettings(
        RemoteConfigSettings(
          fetchTimeout: const Duration(seconds: 10),
          minimumFetchInterval: const Duration(hours: 1),
        ),
      );
      await rc.setDefaults(_defaults);
      await rc.fetchAndActivate();
    } catch (e) {
      debugPrint('AiConfig Remote Config init fallback active: $e');
    }
  }

  static String _get(String key, String fallback) {
    try {
      final value = FirebaseRemoteConfig.instance.getString(key).trim();
      return value.isNotEmpty ? value : fallback;
    } catch (_) {
      return fallback;
    }
  }

  static String get flashModel => _get('gemini_flash_model', defaultFlashModel);
  static String get proModel => _get('gemini_pro_model', defaultProModel);
  static String get liteModel => _get('gemini_lite_model', defaultLiteModel);
  static String get imageModel => _get('gemini_image_model', defaultImageModel);
  static String get imageProModel =>
      _get('gemini_image_pro_model', defaultImageProModel);
  static String get embeddingModel =>
      _get('gemini_embedding_model', defaultEmbeddingModel);
}
