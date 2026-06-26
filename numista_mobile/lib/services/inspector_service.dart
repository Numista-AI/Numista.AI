import 'package:shared_preferences/shared_preferences.dart';
import 'auth_service.dart';

class InspectorService {
  static const _key = 'is_inspector_mode_enabled';

  /// Returns true if Inspector Mode is enabled.
  /// Defaults to true for Beta Testers if no preference has been saved yet.
  static Future<bool> isEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    if (!prefs.containsKey(_key)) {
      final isTester = AuthService.isBetaTester;
      if (isTester) {
        await setEnabled(true);
        return true;
      }
      return false;
    }
    return prefs.getBool(_key) ?? false;
  }

  /// Saves the Inspector Mode state to SharedPreferences.
  static Future<void> setEnabled(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, enabled);
  }
}
