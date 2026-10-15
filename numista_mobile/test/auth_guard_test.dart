// auth_guard_test.dart
//
// Guard test: ensures no bare http.get/post/put/delete/patch/MultipartRequest
// to our backend base URL exists outside of HttpAuthClient.
// If this test fails, a developer added a bare backend call.

import 'dart:io';
import 'package:flutter_test/flutter_test.dart';

void main() {
  const kBackendHosts = [
    'numista-backend-568985927038.us-central1.run.app',
    'numista-backend-qntvrqvxma-uc.a.run.app',
    'kApiBaseUrl',
    '_apiUrl',
    'baseUrl',
    'kApiBaseUrl',
  ];

  // Routes that are legitimately public (no auth needed):
  const kPublicPaths = [
    '/api/spot_prices',
    '/api/numista_data',
    '/api/health',
    // add others from _PUBLIC_PATHS in main.py
  ];

  test('No bare http.* backend calls exist outside HttpAuthClient', () {
    final libDir = Directory('lib');
    final dartFiles = libDir
        .listSync(recursive: true)
        .whereType<File>()
        .where((f) => f.path.endsWith('.dart'))
        .toList();

    final violations = <String>[];
    final bareCallPattern = RegExp(
        r'(?<!HttpAuthClient\.)\b(http\.get|http\.post|http\.put|http\.delete|http\.patch)\s*\(');
    final multipartPattern = RegExp(r"http\.MultipartRequest\s*\(");

    for (final file in dartFiles) {
      final lines = file.readAsLinesSync();
      for (var i = 0; i < lines.length; i++) {
        final line = lines[i];
        // Skip comments
        if (line.trimLeft().startsWith('//')) continue;
        if (line.trimLeft().startsWith('*')) continue;

        final hasBareCall = bareCallPattern.hasMatch(line) || multipartPattern.hasMatch(line);
        if (!hasBareCall) continue;

        // Check if this line references a backend host or a variable that might
        // (look ahead 3 lines for the URL)
        final context = lines.skip(i).take(4).join(' ');
        final hitsBackend = kBackendHosts.any((host) => context.contains(host));
        final isPublic = kPublicPaths.any((path) => context.contains(path));
        final isExternal = context.contains('ebay.com') ||
            context.contains('numista.com') ||
            context.contains('pcgs.com') ||
            context.contains('api.coingecko') ||
            context.contains('googleapis.com');

        if (hitsBackend && !isPublic && !isExternal) {
          violations.add('${file.path}:${i + 1}: ${line.trim()}');
        }
      }
    }

    expect(violations, isEmpty,
        reason: 'Bare backend HTTP calls found (use HttpAuthClient instead):\n${violations.join("\n")}');
  });
}
