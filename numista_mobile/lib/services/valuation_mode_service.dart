import 'package:shared_preferences/shared_preferences.dart';

class ValuationModeService {
  static const _key = 'is_advanced_valuation_mode_enabled';

  /// Returns true if Advanced Numismatist View is enabled.
  /// Defaults to false (Estate/Liquidation View).
  static Future<bool> isAdvancedMode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_key) ?? false;
  }

  /// Saves the Advanced Numismatist View preference.
  static Future<void> setAdvancedMode(bool enabled) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_key, enabled);
  }
}
