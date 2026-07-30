import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/foundation.dart';

/// Wraps Firebase Auth for Numista.AI.
/// PIN authentication uses Firebase email/password where the PIN IS the password.
/// 6-digit numeric PINs satisfy Firebase's ≥6-character requirement.
class AuthService {
  static final _auth = FirebaseAuth.instance;

  // ─── Current user convenience ────────────────────────────────────────────
  static User? get currentUser => _auth.currentUser;

  static bool get isGuest => _auth.currentUser?.isAnonymous == true;

  static bool get isBetaTester {
    final user = _auth.currentUser;
    if (user == null) return false;
    // Every user now and in the next 30 days defaults to a Beta Tester.
    // Cutoff: July 27, 2026.
    final limit = DateTime(2026, 7, 27);
    if (DateTime.now().isBefore(limit)) return true;
    return false;
  }

  static String get userEmail {
    final user = _auth.currentUser;
    if (user?.isAnonymous == true) return 'guest';
    return user?.email ?? 'unknown@numista.ai';
  }

  static String get displayName {
    final user = _auth.currentUser;
    if (user?.isAnonymous == true) return 'Guest';
    return user?.displayName?.isNotEmpty == true
        ? user!.displayName!
        : userEmail.split('@').first;
  }

  /// Firestore path for this user's coin collection.
  /// Anonymous users get a UID-based path so each guest session is isolated.
  static String get coinsPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown/coins';
    if (user.isAnonymous) return 'users/${user.uid}/coins';
    return 'users/${user.email ?? user.uid}/coins';
  }

  /// Firestore path for this user's paper money / bank note collection.
  static String get currencyPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown/currency';
    if (user.isAnonymous) return 'users/${user.uid}/currency';
    return 'users/${user.email ?? user.uid}/currency';
  }

  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // ─── Sign In with Email + PIN ─────────────────────────────────────────────
  static Future<AuthResult> signIn(String email, String pin) async {
    try {
      await _auth.signInWithEmailAndPassword(
          email: email.trim(), password: pin.trim());
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    }
  }

  // ─── Create Account ───────────────────────────────────────────────────────
  static Future<AuthResult> createAccount(
      String email, String displayName, String pin) async {
    try {
      final cred = await _auth.createUserWithEmailAndPassword(
          email: email.trim(), password: pin.trim());
      // Store a display name so the sidebar shows a real name
      if (displayName.trim().isNotEmpty) {
        await cred.user?.updateDisplayName(displayName.trim());
      }
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    }
  }

  // ─── Google Sign-In (web popup) ───────────────────────────────────────────
  static Future<AuthResult> signInWithGoogle() async {
    try {
      if (kIsWeb) {
        final provider = GoogleAuthProvider();
        provider.setCustomParameters({'prompt': 'select_account'});
        await _auth.signInWithPopup(provider);
      } else {
        // Fallback for non-web (desktop/mobile) — redirect flow
        final provider = GoogleAuthProvider();
        await _auth.signInWithRedirect(provider);
      }
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.failure('Google sign-in failed. Please try again.');
    }
  }

  // ─── Reset PIN (sends password-reset email) ───────────────────────────────
  static Future<AuthResult> resetPin(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.trim());
      return AuthResult.success(
          message: 'PIN reset email sent to ${email.trim()}. Please check your Inbox (and Trash/Spam folder if not visible). Email comes from auth@numista.ai.');
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    }
  }

  // ─── Guest / Anonymous Sign-In ───────────────────────────────────────────
  static Future<AuthResult> signInAsGuest() async {
    try {
      await _auth.signInAnonymously();
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code));
    } catch (e) {
      return AuthResult.failure('Guest sign-in failed. Please try again.');
    }
  }

  // ─── Sign Out ─────────────────────────────────────────────────────────────
  static Future<void> signOut() => _auth.signOut();

  // ─── Human-friendly Firebase error messages ───────────────────────────────
  static String _friendlyError(String code) {
    switch (code) {
      case 'user-not-found':
        return 'No account found with that email.';
      case 'wrong-password':
      case 'invalid-credential':
        return 'Incorrect email or PIN. Please try again.';
      case 'email-already-in-use':
        return 'An account already exists with that email.';
      case 'weak-password':
        return 'PIN must be exactly 6 digits.';
      case 'invalid-email':
        return 'Please enter a valid email address.';
      case 'too-many-requests':
        return 'Too many failed attempts. Please wait a moment and try again.';
      case 'network-request-failed':
        return 'Network error. Please check your connection.';
      default:
        return 'Something went wrong. Please try again. ($code)';
    }
  }
}

/// Result type returned from all AuthService methods.
class AuthResult {
  final bool ok;
  final String? error;
  final String? message;

  const AuthResult._({required this.ok, this.error, this.message});
  factory AuthResult.success({String? message}) =>
      AuthResult._(ok: true, message: message);
  factory AuthResult.failure(String error) =>
      AuthResult._(ok: false, error: error);
}
