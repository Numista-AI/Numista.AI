import 'package:shared_preferences/shared_preferences.dart';
import 'package:firebase_auth/firebase_auth.dart';

/// Persistent Morgan AI preferences stored in SharedPreferences.
///
/// All keys are user-scoped (prefixed with the Firebase UID) so multiple
/// accounts on the same device each have independent settings.
class MorganPrefs {
  MorganPrefs._();

  // ── Key helpers ─────────────────────────────────────────────────────────────
  static String _uid() =>
      FirebaseAuth.instance.currentUser?.uid ?? 'guest';

  static String _key(String k) => 'morgan_${_uid()}_$k';

  // ── Preferred name ───────────────────────────────────────────────────────────
  /// The name Morgan uses when addressing this user (e.g. "Eric", "Sir").
  static Future<String?> getPreferredName() async {
    final p = await SharedPreferences.getInstance();
    return p.getString(_key('preferred_name'));
  }

  static Future<void> setPreferredName(String name) async {
    final p = await SharedPreferences.getInstance();
    await p.setString(_key('preferred_name'), name);
  }

  // ── Setup complete flag ──────────────────────────────────────────────────────
  /// True once the user has completed the one-time name setup dialog.
  static Future<bool> isSetupDone() async {
    final p = await SharedPreferences.getInstance();
    return p.getBool(_key('setup_done')) ?? false;
  }

  static Future<void> markSetupDone() async {
    final p = await SharedPreferences.getInstance();
    await p.setBool(_key('setup_done'), true);
  }

  // ── Show on startup ──────────────────────────────────────────────────────────
  /// Whether Morgan greets the user on every login. Default: true.
  /// Users can opt out via Morgan settings ("Don't greet me on startup").
  static Future<bool> showOnStartup() async {
    final p = await SharedPreferences.getInstance();
    return p.getBool(_key('show_on_startup')) ?? true;
  }

  static Future<void> setShowOnStartup(bool value) async {
    final p = await SharedPreferences.getInstance();
    await p.setBool(_key('show_on_startup'), value);
  }

  // ── Voice enabled (Phase 4 placeholder) ─────────────────────────────────────
  static Future<bool> isVoiceEnabled() async {
    final p = await SharedPreferences.getInstance();
    return p.getBool(_key('voice_enabled')) ?? false;
  }

  static Future<void> setVoiceEnabled(bool value) async {
    final p = await SharedPreferences.getInstance();
    await p.setBool(_key('voice_enabled'), value);
  }

  // ── Computed display name ────────────────────────────────────────────────────
  /// Returns the Morgan-preferred name, falling back to:
  ///   Firebase displayName first word → email prefix → 'there'
  static Future<String> getDisplayName() async {
    final saved = await getPreferredName();
    if (saved != null && saved.isNotEmpty) return saved;
    final user = FirebaseAuth.instance.currentUser;
    final raw = user?.displayName?.trim().isNotEmpty == true
        ? user!.displayName!.trim()
        : (user?.email?.split('@').first ?? 'there');
    return raw.split(' ').first;
  }

  /// Clears all Morgan preferences for this user.
  /// Safe to call from user-facing settings (not restricted to debug mode).
  static Future<void> clearAll() async {
    final p = await SharedPreferences.getInstance();
    final uid = _uid();
    final keys = p.getKeys().where((k) => k.startsWith('morgan_${uid}_')).toList();
    for (final k in keys) {
      await p.remove(k);
    }
  }
}
