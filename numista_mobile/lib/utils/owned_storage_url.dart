/// Public top-level security guard for image URLs rendered in Numista.AI.
/// Admits only verified first-party and official Google Cloud / Firebase storage URLs.
/// Blocks unowned third-party storage, wildcards, and protocol-relative bypasses.
bool isOwnedStorageUrl(String? url) {
  if (url == null) return false;
  final trimmed = url.trim();
  if (trimmed.isEmpty || trimmed.contains(r'\')) return false;
  final lower = trimmed.toLowerCase();
  // v2.1 MF-SAG-I3: encoded dot / backslash / encoded-slash-dot traversal rejected before parsing
  if (lower.contains('%2e') || lower.contains('%5c') || lower.contains('%2f.')) return false;
  // v2.2: raw literal dot segments rejected BEFORE Uri.tryParse (Dart Uri normalizes them away)
  if (trimmed.split(RegExp(r'[?#]')).first.split('/').any((p) => p == '.' || p == '..')) return false;

  bool badSegs(Iterable<String> segs) =>
      segs.expand((p) => p.split('/')).any((p) => p.isEmpty || p == '.' || p == '..');

  // 1. Relative same-origin paths: single leading '/', no '//', no dot segments
  // Deliberate same-origin relative-path exception for Image.network; not reachable via network URLs.
  if (trimmed.startsWith('/')) {
    if (trimmed.startsWith('//')) return false;
    final segs = trimmed.substring(1).split('/');
    return !segs.any((p) => p.isEmpty || p == '.' || p == '..');
  }

  // 2. Strict HTTPS parsing
  final uri = Uri.tryParse(trimmed);
  if (uri == null || uri.scheme != 'https') return false;
  if (uri.userInfo.isNotEmpty || uri.hasPort) return false;

  final host = uri.host.toLowerCase();
  final segs = uri.pathSegments; // decoded
  if (segs.isEmpty || segs.any((p) => p.isEmpty) || badSegs(segs)) return false;

  // 3. Form A: Firebase Storage download URL for the real project bucket (requires object segment segs[4])
  if (host == 'firebasestorage.googleapis.com') {
    return segs.length >= 5 && segs[0] == 'v0' && segs[1] == 'b' &&
        segs[2] == 'studio-9101802118-8c9a8.firebasestorage.app' && segs[3] == 'o';
  }

  // 4. Form B: Google Cloud Storage, exact bucket root (first decoded segment), re-checked after validation
  if (host == 'storage.googleapis.com') {
    const roots = {
      'us_mint_coin_images',
      'numista-reference-library',
      'studio-9101802118-8c9a8-uploads',
      'numista-uploads-studio-9101802118-8c9a8',
      'studio-9101802118-8c9a8.firebasestorage.app',
    };
    return segs.length >= 2 && roots.contains(segs.first);
  }

  return false;
}
