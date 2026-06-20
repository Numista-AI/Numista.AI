// lib/services/photo_sharing_service.dart
//
// Manages the one-time user consent for contributing personal coin photos
// to the Numista.AI reference library.
//
// Design:
//   • First-upload-ever popup defaults to OPT-IN (user must actively opt out).
//   • Popup only fires once; preference is stored in SharedPreferences locally
//     and mirrored to Firestore so it follows the user across devices.
//   • The 'contribute_to_library' flag is written onto the Firestore coin doc
//     every time an upload happens (based on the stored preference), so the
//     backend kaggle_vision_ingest companion script can later promote opted-in
//     Tier-1 images to the shared reference index.
//
// Usage:
//   final shouldShowPopup = await PhotoSharingService.shouldShowConsent();
//   if (shouldShowPopup) { /* show dialog */ }
//   await PhotoSharingService.saveConsent(optedIn: true);
//   final opted = await PhotoSharingService.isOptedIn();

import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'auth_service.dart';

class PhotoSharingService {
  // ── SharedPreferences keys ─────────────────────────────────────────────────
  static const String _kConsentShown = 'photo_sharing_consent_shown';
  static const String _kOptedIn      = 'photo_sharing_opted_in';

  // ── Public API ─────────────────────────────────────────────────────────────

  /// Returns true if the one-time consent popup has not yet been shown.
  static Future<bool> shouldShowConsent() async {
    final prefs = await SharedPreferences.getInstance();
    return !(prefs.getBool(_kConsentShown) ?? false);
  }

  /// Returns the user's current preference (true = contribute, false = keep private).
  /// Defaults to true (opted in) if the user has never been asked.
  static Future<bool> isOptedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(_kOptedIn) ?? true;
  }

  /// Saves the consent decision locally and to Firestore.
  /// Should be called after the user responds to the consent popup,
  /// or when they toggle the preference in Settings.
  static Future<void> saveConsent({required bool optedIn}) async {
    // 1. Write locally
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_kConsentShown, true);
    await prefs.setBool(_kOptedIn, optedIn);

    // 2. Mirror to Firestore so the preference syncs across devices
    final email = AuthService.userEmail;
    if (email.isEmpty) return;
    try {
      await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('settings')
          .doc('photo_sharing')
          .set({
        'opted_in':          optedIn,
        'consent_shown':     true,
        'last_updated':      FieldValue.serverTimestamp(),
        'consent_version':   1, // bump when T&Cs change to re-prompt
      }, SetOptions(merge: true));
    } catch (_) {
      // Non-fatal — local pref is the source of truth
    }
  }

  /// Loads the user's preference from Firestore (used on fresh install /
  /// after clearing app data).  Falls back to SharedPreferences if unavailable.
  static Future<void> syncFromFirestore() async {
    final email = AuthService.userEmail;
    if (email.isEmpty) return;
    try {
      final doc = await FirebaseFirestore.instance
          .collection('users')
          .doc(email)
          .collection('settings')
          .doc('photo_sharing')
          .get();
      if (!doc.exists) return;
      final data = doc.data() ?? {};
      final shown   = data['consent_shown'] as bool? ?? false;
      final optedIn = data['opted_in']      as bool? ?? true;

      final prefs = await SharedPreferences.getInstance();
      if (shown) {
        await prefs.setBool(_kConsentShown, true);
        await prefs.setBool(_kOptedIn, optedIn);
      }
    } catch (_) {
      // Non-fatal
    }
  }

  /// Returns true when a coin's year+program has no existing Tier-1/2 reference
  /// image in the coin_image_index, meaning the user's photo is genuinely needed.
  ///
  /// This is used to make the consent popup more meaningful ("your photo is
  /// actually better than what we have") rather than firing indiscriminately.
  static Future<bool> referenceImageNeeded({
    required String programSlug,
    required String year,
  }) async {
    if (programSlug.isEmpty || year.isEmpty) return false;
    try {
      // Try both obverse and reverse — if either is missing we'd love the photo
      for (final side in ['obverse', 'reverse']) {
        final docId = '${year}_${programSlug}_$side';
        final snap = await FirebaseFirestore.instance
            .collection('coin_image_index')
            .doc(docId)
            .get();
        if (!snap.exists) return true; // definitely missing
        final tier = (snap.data() ?? {})[side]?['source_tier'] as int? ?? 5;
        if (tier >= 3) return true; // Tier 3-4 (low quality) — user photo helps
      }
      return false; // Tier 1-2 already in index for both sides
    } catch (_) {
      return false; // On error, don't show popup
    }
  }
}
