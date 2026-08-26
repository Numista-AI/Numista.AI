import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

/// Text scale mode identifiers.
/// Normal = 1.0x (default), Large = 1.3x, ExtraLarge = 1.6x.
enum TextScaleMode { normal, large, extraLarge }

extension TextScaleModeExt on TextScaleMode {
  double get factor {
    switch (this) {
      case TextScaleMode.normal:     return 1.0;
      case TextScaleMode.large:      return 1.3;
      case TextScaleMode.extraLarge: return 1.6;
    }
  }
  String get label {
    switch (this) {
      case TextScaleMode.normal:     return 'Normal';
      case TextScaleMode.large:      return 'Large';
      case TextScaleMode.extraLarge: return 'Extra Large';
    }
  }
}

class ThemeProvider extends ChangeNotifier {
  static final ThemeProvider instance = ThemeProvider._internal();

  ThemeProvider._internal() {
    _loadPrefs();
  }

  // Set default to dark mode per UI/UX stability guidelines
  ThemeMode _themeMode = ThemeMode.dark;

  ThemeMode get themeMode => _themeMode;

  bool get isDarkMode => _themeMode == ThemeMode.dark;

  void toggleTheme() {
    setThemeMode(_themeMode == ThemeMode.light ? ThemeMode.dark : ThemeMode.light);
  }

  void setThemeMode(ThemeMode mode) async {
    if (_themeMode == mode) return;
    _themeMode = mode;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('theme_mode', mode.name);
  }

  // ── Text Scale ────────────────────────────────────────────────────────────
  TextScaleMode _textScaleMode = TextScaleMode.normal;

  TextScaleMode get textScaleMode => _textScaleMode;

  /// Current text scale factor (1.0, 1.3, or 1.6).
  double get textScaleFactor => _textScaleMode.factor;

  void setTextScaleMode(TextScaleMode mode) async {
    if (_textScaleMode == mode) return;
    _textScaleMode = mode;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('text_scale_mode', mode.name);
  }

  void _loadPrefs() async {
    final prefs = await SharedPreferences.getInstance();

    // Theme mode
    final savedTheme = prefs.getString('theme_mode');
    if (savedTheme != null) {
      _themeMode = ThemeMode.values.firstWhere(
        (e) => e.name == savedTheme,
        orElse: () => ThemeMode.dark,
      );
    } else {
      _themeMode = ThemeMode.dark;
    }

    // Text scale mode
    final savedScale = prefs.getString('text_scale_mode');
    if (savedScale != null) {
      _textScaleMode = TextScaleMode.values.firstWhere(
        (e) => e.name == savedScale,
        orElse: () => TextScaleMode.normal,
      );
    }

    notifyListeners();
  }
}
