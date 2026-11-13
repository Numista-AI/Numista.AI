import 'dart:convert';
import 'dart:io';

import 'package:numista_ai/utils/catalog_image_guard.dart';

String _escapeHtml(String value) {
  return value
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;')
      .replaceAll("'", '&#39;');
}

String _injectHeadTags(
  String templateHtml, {
  required String title,
  required String description,
  required String canonicalUrl,
  String? robots,
  String? ogTitle,
  String? ogDescription,
  String? ogImageUrl,
  String? ogImageAlt,
}) {
  var html = templateHtml;

  // Replace existing <title>...</title> if present
  final titleRegex = RegExp(r'<title>.*?</title>', dotAll: true, caseSensitive: false);
  final escapedTitle = _escapeHtml(title);
  if (titleRegex.hasMatch(html)) {
    html = html.replaceFirst(titleRegex, '<title>$escapedTitle</title>');
  }

  // Strip any existing canonical, description, robots, og:*, twitter:* tags before injecting
  html = html.replaceAll(
    RegExp(r'<meta\s+name="(?:description|robots|twitter:[^"]+)"[^>]*>\s*', caseSensitive: false),
    '',
  );
  html = html.replaceAll(
    RegExp(r'<meta\s+property="og:[^"]+"[^>]*>\s*', caseSensitive: false),
    '',
  );
  html = html.replaceAll(
    RegExp(r'<link\s+rel="canonical"[^>]*>\s*', caseSensitive: false),
    '',
  );

  final buffer = StringBuffer();
  buffer.writeln('  <meta name="description" content="${_escapeHtml(description)}">');
  buffer.writeln('  <link rel="canonical" href="${_escapeHtml(canonicalUrl)}">');
  if (robots != null && robots.isNotEmpty) {
    buffer.writeln('  <meta name="robots" content="${_escapeHtml(robots)}">');
  }
  buffer.writeln('  <meta property="og:type" content="website">');
  buffer.writeln('  <meta property="og:url" content="${_escapeHtml(canonicalUrl)}">');
  buffer.writeln('  <meta property="og:title" content="${_escapeHtml(ogTitle ?? title)}">');
  buffer.writeln('  <meta property="og:description" content="${_escapeHtml(ogDescription ?? description)}">');

  if (ogImageUrl != null && isApprovedCatalogImageUrl(ogImageUrl)) {
    buffer.writeln('  <meta property="og:image" content="${_escapeHtml(ogImageUrl)}">');
    if (ogImageAlt != null && ogImageAlt.isNotEmpty) {
      buffer.writeln('  <meta property="og:image:alt" content="${_escapeHtml(ogImageAlt)}">');
    }
    buffer.writeln('  <meta name="twitter:card" content="summary_large_image">');
    buffer.writeln('  <meta name="twitter:image" content="${_escapeHtml(ogImageUrl)}">');
  } else {
    buffer.writeln('  <meta name="twitter:card" content="summary">');
  }

  buffer.writeln('  <meta name="twitter:title" content="${_escapeHtml(ogTitle ?? title)}">');
  buffer.writeln('  <meta name="twitter:description" content="${_escapeHtml(ogDescription ?? description)}">');

  final headClose = RegExp(r'</head>', caseSensitive: false);
  if (headClose.hasMatch(html)) {
    html = html.replaceFirst(headClose, '${buffer.toString()}</head>');
  } else {
    html = '${buffer.toString()}$html';
  }
  return html;
}

String _buildCoinDescription(Map<String, dynamic> item) {
  final parts = <String>[];
  final year = item['year']?.toString().trim();
  final denom = item['denomination']?.toString().trim();
  final series = item['series']?.toString().trim();
  final composition = item['composition']?.toString().trim();

  if (year != null && year.isNotEmpty) parts.add('Year: $year');
  if (denom != null && denom.isNotEmpty) parts.add('Denomination: $denom');
  if (series != null && series.isNotEmpty) parts.add('Series: $series');
  if (composition != null && composition.isNotEmpty) parts.add('Composition: $composition');

  if (parts.isEmpty) {
    return 'U.S. Numismatics Reference Catalog entry on Numista.AI.';
  }
  return 'U.S. Numismatics Reference Catalog — ${parts.join(' · ')}.';
}

Future<void> main() async {
  final indexFile = File('build/web/index.html');
  if (!indexFile.existsSync()) {
    stderr.writeln('ERROR: build/web/index.html not found. Run flutter build web --release first.');
    exit(1);
  }
  final templateHtml = await indexFile.readAsString();

  final catalogFile = File('assets/catalog/catalog_public_v1.json');
  if (!catalogFile.existsSync()) {
    stderr.writeln('ERROR: assets/catalog/catalog_public_v1.json not found.');
    exit(1);
  }
  final List<dynamic> catalog = jsonDecode(await catalogFile.readAsString()) as List<dynamic>;

  // 1. /catalog/index.html
  final catalogRootDir = Directory('build/web/catalog')..createSync(recursive: true);
  await File('${catalogRootDir.path}/index.html').writeAsString(
    _injectHeadTags(
      templateHtml,
      title: 'Numista.AI Public Catalog — U.S. Numismatics Reference',
      description: 'Explore 3,202 U.S. coins, banknotes, and medals in the Numista.AI Public Reference Catalog.',
      canonicalUrl: 'https://numista.ai/catalog',
    ),
  );

  // 2. /catalog/<nac>/index.html for all 3,202 records
  int generatedCoins = 0;
  for (final raw in catalog) {
    final item = Map<String, dynamic>.from(raw as Map);
    final nac = (item['nac_code'] as String? ?? '').trim();
    if (nac.isEmpty || nac.contains('/') || nac.contains('\\') || nac.contains('..')) {
      continue;
    }
    final name = (item['name'] as String? ?? nac).trim();
    final primaryImg = item['primary_image'] as Map?;
    final primaryUrl = primaryImg?['url'] as String?;
    final approvedImg = (primaryUrl != null && isApprovedCatalogImageUrl(primaryUrl)) ? primaryUrl : null;

    final coinDir = Directory('build/web/catalog/$nac')..createSync(recursive: true);
    await File('${coinDir.path}/index.html').writeAsString(
      _injectHeadTags(
        templateHtml,
        title: 'Numista.AI Reference Catalog – $name',
        description: _buildCoinDescription(item),
        canonicalUrl: 'https://numista.ai/catalog/$nac',
        ogTitle: 'Numista.AI Reference Catalog – $name',
        ogImageUrl: approvedImg,
        ogImageAlt: approvedImg != null ? name : null,
      ),
    );
    generatedCoins++;
  }

  // 3. /pricing/index.html (Fail-Closed Free Beta Copy ONLY)
  final pricingDir = Directory('build/web/pricing')..createSync(recursive: true);
  await File('${pricingDir.path}/index.html').writeAsString(
    _injectHeadTags(
      templateHtml,
      title: 'Numista.AI Pricing — Free During Beta — Pricing TBA',
      description: 'Free During Beta — Pricing TBA (\$0 / month). Numista.AI is currently in open public beta and completely free for registered participants. Existing beta accounts will be grandfathered—you will not be asked to pay for your active beta access.',
      canonicalUrl: 'https://numista.ai/pricing',
    ),
  );

  // 4. /catalog_unknown.html (Soft-404 elimination target with server-visible noindex, follow)
  await File('build/web/catalog_unknown.html').writeAsString(
    _injectHeadTags(
      templateHtml,
      title: 'Numista.AI Public Catalog — Reference Item Not Found',
      description: 'The requested reference code was not found in the Numista.AI U.S. Numismatics Public Catalog.',
      canonicalUrl: 'https://numista.ai/catalog',
      robots: 'noindex, follow',
    ),
  );

  stdout.writeln('Generated $generatedCoins catalog entry HTML pages, /catalog/index.html, /pricing/index.html, and /catalog_unknown.html.');
}
