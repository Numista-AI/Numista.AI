// Public catalog image allow-list guard (NET-814 v2.0.1).
// Passing this guard is NECESSARY, not sufficient: per-image release/provenance gates still apply.

/// Pre-parse raw-string dot-segment check. MUST run before Uri.tryParse,
/// because Dart's Uri normalizes `.` / `..` out of pathSegments.
bool _hasRawDotSegment(String url) {
  final pathPart = url.split(RegExp(r'[?#]')).first;
  return pathPart.split('/').any((seg) => seg == '.' || seg == '..');
}

bool isApprovedCatalogImageUrl(String rawUrl) {
  final url = rawUrl.trim();
  // Reject raw backslashes, query strings (?), and fragments (#) before parsing (CR3 D2).
  if (url.isEmpty ||
      url.contains('\\') ||
      url.contains('?') ||
      url.contains('#')) {
    return false;
  }
  if (_hasRawDotSegment(url)) return false;
  final lower = url.toLowerCase();
  // Reject encoded traversal, path separators, ?, and # before any parsing (CR3 N2).
  if (lower.contains('%2e') ||
      lower.contains('%2f') ||
      lower.contains('%5c') ||
      lower.contains('%3f') ||
      lower.contains('%23')) {
    return false;
  }

  // Bundled local catalog assets only, no traversal or bare directory prefix.
  if (url.startsWith('assets/catalog/images/')) {
    final segs = url.split('/');
    return segs.length >= 4 &&
        !segs.any((seg) => seg.isEmpty || seg == '.' || seg == '..');
  }

  final uri = Uri.tryParse(url);
  if (uri == null || uri.scheme != 'https' || !lower.startsWith('https://')) {
    return false;
  }
  if (uri.hasQuery || uri.hasFragment) return false;
  final authority = url.substring('https://'.length).split('/').first;
  if (authority.contains('@') || authority.contains(':')) return false;
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;
  if (uri.host.toLowerCase() != 'storage.googleapis.com') {
    return false; // firebasestorage.googleapis.com (private originals) rejected
  }

  final seg = uri.pathSegments;
  if (seg.length < 2 || seg.any((p) => p.isEmpty || p == '.' || p == '..')) {
    return false;
  }

  switch (seg.first) {
    case 'us_mint_coin_images':
    case 'numista-reference-library':
      return true;
    case 'numista-uploads-studio-9101802118-8c9a8':
      // Only the promoted public reference destination (must include object path).
      return seg.length >= 3 && seg[1] == 'reference';
    default:
      return false;
  }
}

/// Allow-listed HTTPS provenance source hosts for clickable source_url links (CR3 P5).
const Set<String> _approvedSourceHosts = <String>{
  'usmint.gov',
  'www.usmint.gov',
  'commons.wikimedia.org',
};

/// Returns true only when [rawUrl] is an https URL targeting an exact approved
/// source host with no userinfo and no explicit port (including :443).
bool isApprovedSourceUrl(String? rawUrl) {
  if (rawUrl == null) return false;
  final url = rawUrl.trim();
  if (url.isEmpty || url.contains('\\')) return false;
  if (!url.toLowerCase().startsWith('https://')) return false;

  final uri = Uri.tryParse(url);
  if (uri == null || uri.scheme != 'https') return false;
  final afterScheme = url.substring('https://'.length);
  final authority = afterScheme.split(RegExp(r'[/?#]')).first;
  if (authority.isEmpty || authority.contains('@') || authority.contains(':')) {
    return false;
  }
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;
  return _approvedSourceHosts.contains(uri.host.toLowerCase());
}
