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

  test('6. retries once on 429 with jittered delay (250-750ms) and succeeds on 200', () async {
    const rawUrl =
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c6/obv.jpg';
    var attempts = 0;
    final recordedDelays = <Duration>[];
    SignedPhotoUrlService.delayFn = (d) async => recordedDelays.add(d);
    SignedPhotoUrlService.jitterNextInt = (max) => 100; // 250 + 100 = 350ms
    addTearDown(() => SignedPhotoUrlService.resetForTest());

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      attempts++;
      if (attempts == 1) {
        return http.Response(jsonEncode({'detail': 'Rate limited'}), 429);
      }
      return http.Response(
        jsonEncode({'signed_urls': {rawUrl: 'https://signed.example/retry-ok.jpg'}}),
        200,
      );
    });

    final result = await SignedPhotoUrlService.resolve(rawUrl);
    expect(attempts, 2);
    expect(result, 'https://signed.example/retry-ok.jpg');
    expect(recordedDelays, [const Duration(milliseconds: 350)]);
  });

  test('7. 403 fails fast without retry, fires onSigningError, and invalidate() clears cache', () async {
    const rawUrl =
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c7/obv.jpg';
    var attempts = 0;
    Object? capturedError;
    String? capturedReason;
    SignedPhotoUrlService.delayFn = (_) async {};
    SignedPhotoUrlService.onSigningError = (err, stack, {reason}) {
      capturedError = err;
      capturedReason = reason;
    };
    addTearDown(() => SignedPhotoUrlService.resetForTest());

    HttpAuthClient.httpClientOverride = MockClient((request) async {
      attempts++;
      return http.Response(jsonEncode({'detail': 'Forbidden'}), 403);
    });

    final failResult = await SignedPhotoUrlService.resolve(rawUrl);
    expect(failResult, isNull);
    expect(attempts, 1);
    expect(capturedError.toString(), contains('403'));
    expect(capturedReason, 'batch_signed_url_failed');

    // Now return 200, verify cache + invalidate()
    attempts = 0;
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      attempts++;
      return http.Response(
        jsonEncode({'signed_urls': {rawUrl: 'https://signed.example/v$attempts.jpg'}}),
        200,
      );
    });

    expect(await SignedPhotoUrlService.resolve(rawUrl), 'https://signed.example/v1.jpg');
    expect(await SignedPhotoUrlService.resolve(rawUrl), 'https://signed.example/v1.jpg');
    expect(attempts, 1);

    SignedPhotoUrlService.invalidate(rawUrl);
    expect(await SignedPhotoUrlService.resolve(rawUrl), 'https://signed.example/v2.jpg');
    expect(attempts, 2);
  });

  test('8. cache bounds at 500 entries and evicts oldest entry on 501st', () async {
    SignedPhotoUrlService.delayFn = (_) async {};
    addTearDown(() => SignedPhotoUrlService.resetForTest());

    var networkCalls = 0;
    HttpAuthClient.httpClientOverride = MockClient((request) async {
      networkCalls++;
      final body = jsonDecode(request.body) as Map<String, dynamic>;
      final urls = (body['urls'] as List).cast<String>();
      return http.Response(
        jsonEncode({
          'signed_urls': {
            for (final u in urls) u: 'https://signed.example/call_$networkCalls',
          },
        }),
        200,
      );
    });

    String urlFor(int i) =>
        'gs://numista-uploads-studio-9101802118-8c9a8/users/a@b.com/coins/c_$i/obv.jpg';

    for (var i = 0; i < 501; i++) {
      await SignedPhotoUrlService.resolve(urlFor(i));
    }
    expect(networkCalls, 501);

    // urlFor(1) should still be cached (no network call)
    final cached1 = await SignedPhotoUrlService.resolve(urlFor(1));
    expect(cached1, 'https://signed.example/call_2');
    expect(networkCalls, 501);

    // urlFor(0) was evicted and must re-fetch
    final evicted0 = await SignedPhotoUrlService.resolve(urlFor(0));
    expect(evicted0, 'https://signed.example/call_502');
    expect(networkCalls, 502);
  });

  test('9. public URL bypass makes zero tokenProviderOverride calls', () async {
    var tokenCalls = 0;
    HttpAuthClient.tokenProviderOverride = () async {
      tokenCalls++;
      return 'test-token';
    };
    const publicUrl = 'https://storage.googleapis.com/us_mint_coin_images/2025/public.jpg';
    final result = await SignedPhotoUrlService.resolve(publicUrl);
    expect(result, publicUrl);
    expect(tokenCalls, 0);
  });
}
