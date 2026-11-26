/// Holds a claim token from a `#/claim?t=TOKEN` link until the user is signed in.
///
/// The token lives in the URL fragment (never sent to a server or logged) and is kept IN MEMORY ONLY:
/// not in localStorage and not in SharedPreferences. It is consumed exactly once.
class ClaimLinkService {
  ClaimLinkService._();

  static String? _pendingToken;

  static bool get hasPendingToken => _pendingToken != null && _pendingToken!.isNotEmpty;

  /// Reads `#/claim?t=...` from the app URL. Returns true when a token was captured.
  static bool captureFromUri(Uri uri) {
    final fragment = uri.fragment;
    if (fragment.isEmpty) return false;
    final parsed = Uri.tryParse(fragment.startsWith('/') ? fragment : '/$fragment');
    if (parsed == null) return false;
    final isClaim = parsed.path == '/claim' || parsed.path.startsWith('/claim/');
    final token = parsed.queryParameters['t']?.trim() ?? '';
    if (!isClaim || token.isEmpty) return false;
    _pendingToken = token;
    return true;
  }

  /// Returns the pending token once, then forgets it.
  static String? takePendingToken() {
    final t = _pendingToken;
    _pendingToken = null;
    return t;
  }

  static void clearForTest() => _pendingToken = null;
}
