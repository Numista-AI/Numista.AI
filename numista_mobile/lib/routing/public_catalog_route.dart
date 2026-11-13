// Pure routing helper extracted from main.dart for headless unit testing
// and direct public catalog entry (/catalog, /catalog/<nac>, ?item=<nac>).

String? extractInitialNac(Uri uri) {
  String path = uri.path;
  String? nacFromQuery;

  // Support Flutter Web hash-fragment URLs (e.g. /#/catalog/<nac> or /#/catalog?item=<nac>)
  if (uri.fragment.isNotEmpty) {
    String frag = uri.fragment;
    if (frag.startsWith('/')) {
      final qIdx = frag.indexOf('?');
      if (qIdx != -1) {
        final queryStr = frag.substring(qIdx + 1);
        nacFromQuery = Uri(query: queryStr).queryParameters['item'];
        frag = frag.substring(0, qIdx);
      }
      if (frag == '/catalog' || frag.startsWith('/catalog/')) {
        path = frag;
      }
    }
  }

  final normalizedPath = path.endsWith('/') && path.length > 1
      ? path.substring(0, path.length - 1)
      : path;

  if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
    String? initialNacCode;
    if (path.startsWith('/catalog/')) {
      final sub = path.substring('/catalog/'.length).trim();
      if (sub.isNotEmpty) {
        try {
          initialNacCode = Uri.decodeComponent(sub);
        } on ArgumentError {
          initialNacCode = sub;
        }
      }
    }
    initialNacCode ??= nacFromQuery;
    initialNacCode ??= uri.queryParameters['item'];
    return initialNacCode;
  }
  return null;
}

bool isCatalogUri(Uri uri) {
  String path = uri.path;
  if (uri.fragment.isNotEmpty && uri.fragment.startsWith('/')) {
    final qIdx = uri.fragment.indexOf('?');
    final fragPath = qIdx != -1 ? uri.fragment.substring(0, qIdx) : uri.fragment;
    if (fragPath == '/catalog' || fragPath.startsWith('/catalog/')) {
      path = fragPath;
    }
  }
  final normalizedPath = path.endsWith('/') && path.length > 1
      ? path.substring(0, path.length - 1)
      : path;
  return normalizedPath == '/catalog' || path.startsWith('/catalog/');
}
