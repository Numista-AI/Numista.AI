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

  /// Pure helper — testable without Firebase. Used by isBetaTester getter.
  static bool isBetaFor({required DateTime? creationUtc, required bool isAnonymous}) {
    if (isAnonymous) return false;
    if (creationUtc == null) return false;
    return creationUtc.isBefore(DateTime.utc(2026, 11, 26, 5));
  }

  static bool get isBetaTester {
    final user = _auth.currentUser;
    if (user == null) return false;
    return isBetaFor(
      creationUtc: user.metadata.creationTime?.toUtc(),
      isAnonymous: user.isAnonymous,
    );
  }

  static String get userEmail {
    final user = _auth.currentUser;
    if (user?.isAnonymous == true) return 'guest';
    final rawEmail = user?.email ?? 'unknown@numista.ai';
    return rawEmail.trim().toLowerCase();
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
    final identifier = user.email != null ? user.email!.trim().toLowerCase() : user.uid;
    return 'users/$identifier/coins';
  }

  /// Firestore path for this user's currency collection.
  static String get currencyPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown/currency';
    if (user.isAnonymous) return 'users/${user.uid}/currency';
    final identifier = user.email != null ? user.email!.trim().toLowerCase() : user.uid;
    return 'users/$identifier/currency';
  }

  /// Firestore path for this user's collection stats metadata document.
  static String get statsDocPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown/metadata/collection_stats';
    if (user.isAnonymous) return 'users/${user.uid}/metadata/collection_stats';
    final identifier = user.email != null ? user.email!.trim().toLowerCase() : user.uid;
    return 'users/$identifier/metadata/collection_stats';
  }

  /// Firestore path for this user's root document.
  static String get userDocPath {
    final user = _auth.currentUser;
    if (user == null) return 'users/unknown';
    if (user.isAnonymous) return 'users/${user.uid}';
    final identifier = user.email != null ? user.email!.trim().toLowerCase() : user.uid;
    return 'users/$identifier';
  }

  static Stream<User?> get authStateChanges => _auth.authStateChanges();

  // ─── Sign In with Email + PIN ─────────────────────────────────────────────
  static Future<AuthResult> signIn(String email, String pin,
      {bool passwordMode = false}) async {
    try {
      await _auth.signInWithEmailAndPassword(
          email: email.trim().toLowerCase(), password: pin.trim());
      return AuthResult.success();
    } on FirebaseAuthException catch (e) {
      return AuthResult.failure(_friendlyError(e.code, passwordMode: passwordMode));
    }
  }

  // ─── Create Account ───────────────────────────────────────────────────────
  static Future<AuthResult> createAccount(
      String email, String displayName, String pin) async {
    try {
      final cred = await _auth.createUserWithEmailAndPassword(
          email: email.trim().toLowerCase(), password: pin.trim());
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

  // ─── Reset PIN or Password (sends password-reset email) ─────────────────
  static Future<AuthResult> resetCredential(String email) async {
    try {
      await _auth.sendPasswordResetEmail(email: email.trim());
      return AuthResult.success(
          message: 'If an account exists for ${email.trim()}, a PIN reset link has been sent. Check your Inbox (and Spam folder). Email comes from auth@numista.ai.');
    } on FirebaseAuthException catch (e) {
      if (e.code == 'user-not-found') {
        // Enforce zero account enumeration even if Firebase enumeration protection is disabled
        return AuthResult.success(
            message: 'If an account exists for ${email.trim()}, a PIN reset link has been sent. Check your Inbox (and Spam folder). Email comes from auth@numista.ai.');
      }
      return AuthResult.failure(_friendlyError(e.code));
    }
  }

  /// Legacy alias kept so any code still calling resetPin() continues to work.
  @Deprecated('Use resetCredential() instead')
  static Future<AuthResult> resetPin(String email) => resetCredential(email);

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
  static String friendlyError(String code) => _friendlyError(code);

  static String _friendlyError(String code, {bool passwordMode = false}) {
    switch (code) {
      case 'user-not-found':
      case 'wrong-password':
      case 'invalid-credential':
      case 'invalid-login-credentials':
        return passwordMode
            ? 'Incorrect email or password.'
            : 'Incorrect email or PIN.';
      case 'email-already-in-use':
        return 'An account with that email already exists. Try signing in instead.';
      case 'weak-password':
        return 'PIN must be exactly 6 digits.';
      case 'invalid-email':
        return 'Please enter a valid email address.';
      case 'too-many-requests':
        return 'Too many tries. Please wait a few minutes, or use Forgot your PIN.';
      case 'network-request-failed':
        return 'Network error. Please check your connection.';
      default:
        return 'Something went wrong. Please try again.';
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
