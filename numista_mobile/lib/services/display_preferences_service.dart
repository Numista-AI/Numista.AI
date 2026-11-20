import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Persists UI display preferences across sessions.
class DisplayPreferencesService {
  DisplayPreferencesService._();
  static final DisplayPreferencesService instance =
      DisplayPreferencesService._();

  static const String prefKeyShowCollectionValue = 'show_collection_value_home';

  /// Default is TRUE per Founder decision (20 Nov 2026).
  final ValueNotifier<bool> showCollectionValue = ValueNotifier<bool>(true);
  bool _loaded = false;

  Future<void> ensureLoaded() async {
    if (_loaded) return;
    try {
      final prefs = await SharedPreferences.getInstance();
      showCollectionValue.value =
          prefs.getBool(prefKeyShowCollectionValue) ?? true;
    } catch (_) {
      // Keep default true if SharedPreferences fails in restricted environments.
    }
    _loaded = true;
  }

  Future<void> setShowCollectionValue(bool value) async {
    showCollectionValue.value = value;
    _loaded = true;
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setBool(prefKeyShowCollectionValue, value);
    } catch (_) {
      // Ignore persistence write errors in test/restricted environments.
    }
  }

  @visibleForTesting
  void resetForTest({bool initialValue = true}) {
    showCollectionValue.value = initialValue;
    _loaded = true;
  }
}
