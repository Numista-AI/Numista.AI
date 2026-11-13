import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/services/http_auth_client.dart';
import 'package:numista_ai/services/signed_photo_url_service.dart';
import 'package:numista_ai/utils/owned_storage_url.dart';

void main() {
  setUp(() {
    SignedPhotoUrlService.resetForTest();
    HttpAuthClient.tokenProviderOverride = () async => 'test-id-token';
  });

  tearDown(() {
    SignedPhotoUrlService.resetForTest();
    HttpAuthClient.httpClientOverride = null;
    HttpAuthClient.tokenProviderOverride = null;
  });

  test('1. isOwnedStorageUrl admits allowlisted gs:// URIs and rejects invalid ones', () {
    expect(
      isOwnedStorageUrl(
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c1/obv.jpg',
      ),
      isTrue,
    );
    expect(
      isOwnedStorageUrl(
        'gs://studio-9101802118-8c9a8.firebasestorage.app/users/a@b.com/coins/c1/obv.jpg',
      ),
      isTrue,
    );
    expect(
      isOwnedStorageUrl('gs://evil-bucket/users/a@b.com/coins/c1/obv.jpg'),
      isFalse,
    );
    expect(
      isOwnedStorageUrl(
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/../other/obv.jpg',
      ),
      isFalse,
    );
    expect(
      isOwnedStorageUrl(
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/%2e%2e/other/obv.jpg',
      ),
      isFalse,
    );
    expect(
      isOwnedStorageUrl('gs://numista-uploads-studio-9101802118-8c9a8/'),
      isFalse,
    );
  });

  test('2. caches signed URL for 12 minutes and refreshes after expiry', () async {
    var now = DateTime(2026, 11, 13, 12, 0, 0);
    SignedPhotoUrlService.clock = () => now;

    var postCount = 0;
    const rawUrl =
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c1/obv.jpg';

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      postCount++;
      return http.Response(
        jsonEncode({
          'signed_urls': {rawUrl: 'https://signed.example/v$postCount'},
          'expires_in_seconds': 900,
          'errors': {},
        }),
        200,
      );
    });

    final first = await SignedPhotoUrlService.resolve(rawUrl);
    expect(first, 'https://signed.example/v1');
    expect(postCount, 1);

    // 11 minutes later -> still cached
    now = now.add(const Duration(minutes: 11));
    final second = await SignedPhotoUrlService.resolve(rawUrl);
    expect(second, 'https://signed.example/v1');
    expect(postCount, 1);

    // 13 minutes total -> expired, refreshes
    now = now.add(const Duration(minutes: 2));
    final third = await SignedPhotoUrlService.resolve(rawUrl);
    expect(third, 'https://signed.example/v2');
    expect(postCount, 2);
  });

  test('3. coalesces concurrent calls within 25ms and deduplicates identical URLs', () async {
    var postCount = 0;
    List<String> sentUrls = [];

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      postCount++;
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      sentUrls = List<String>.from(body['urls'] as List);
      return http.Response(
        jsonEncode({
          'signed_urls': {for (final u in sentUrls) u: 'https://signed.example/${u.hashCode}'},
          'expires_in_seconds': 900,
          'errors': {},
        }),
        200,
      );
    });

    const u1 = 'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/1.jpg';
    const u2 = 'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/2.jpg';
    const u3 =
        'https://firebasestorage.googleapis.com/v0/b/studio-9101802118-8c9a8.firebasestorage.app/o/users%2Fa%40b.com%2F3.jpg?alt=media&token=old';

    final results = await Future.wait([
      SignedPhotoUrlService.resolve(u1),
      SignedPhotoUrlService.resolve(u1), // duplicate
      SignedPhotoUrlService.resolve(u2),
      SignedPhotoUrlService.resolve(u3),
    ]);

    expect(postCount, 1);
    expect(sentUrls.length, 3);
    expect(results[0], results[1]);
    expect(results[0], startsWith('https://signed.example/'));
    expect(results[2], startsWith('https://signed.example/'));
    expect(results[3], startsWith('https://signed.example/'));
  });

  test('4. returns null on 403 or network failure without falling back to raw gs://', () async {
    const rawUrl =
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c1/obv.jpg';

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      return http.Response(jsonEncode({'detail': 'Forbidden'}), 403);
    });

    final forbiddenResult = await SignedPhotoUrlService.resolve(rawUrl);
    expect(forbiddenResult, isNull);

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      throw Exception('Network down');
    });

    final errorResult = await SignedPhotoUrlService.resolve(rawUrl);
    expect(errorResult, isNull);
  });

  test('5. public catalog URLs pass through unchanged with zero backend calls', () async {
    var postCount = 0;
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      postCount++;
      return http.Response('{}', 500);
    });

    const publicUrl = 'https://storage.googleapis.com/us_mint_coin_images/2025/eagle.jpg';
    final result = await SignedPhotoUrlService.resolve(publicUrl);
    expect(result, publicUrl);
    expect(postCount, 0);
  });
}
