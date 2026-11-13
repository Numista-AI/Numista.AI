import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';

import '../constants.dart';
import '../utils/owned_storage_url.dart';
import 'http_auth_client.dart';

class _CachedSignedUrl {
  final String signedUrl;
  final DateTime expiresAt;

  _CachedSignedUrl(this.signedUrl, this.expiresAt);
}

class _PendingRequest {
  final List<Completer<String?>> completers = [];
  late final Future<String?> future = _createFuture();

  Future<String?> _createFuture() {
    final c = Completer<String?>();
    completers.add(c);
    return c.future;
  }
}

/// Resolves private user `gs://` and legacy Firebase Storage user photo URLs
/// into short-lived (15-min) V4 signed URLs via `POST /api/v1/photos/signed_url`.
///
/// Features:
/// - 12-minute client-side cache TTL (refreshes before 15-min backend expiry)
/// - 25ms coalescing batch window (up to 50 URLs per POST)
/// - In-flight deduplication per canonical URL
/// - Cache eviction and `null` return on HTTP 403 / network failure
class SignedPhotoUrlService {
  SignedPhotoUrlService._();

  static const Duration _cacheTtl = Duration(minutes: 12);
  static const Duration _coalesceWindow = Duration(milliseconds: 25);
  static const int _maxBatchSize = 50;

  @visibleForTesting
  static DateTime Function() clock = DateTime.now;

  static final Map<String, _CachedSignedUrl> _cache = {};
  static final Map<String, _PendingRequest> _inFlight = {};
  static final List<String> _batchQueue = [];
  static Timer? _batchTimer;

  @visibleForTesting
  static void resetForTest() {
    _batchTimer?.cancel();
    _batchTimer = null;
    for (final pending in _inFlight.values) {
      for (final c in pending.completers) {
        if (!c.isCompleted) c.complete(null);
      }
    }
    _inFlight.clear();
    _batchQueue.clear();
    _cache.clear();
    clock = DateTime.now;
  }

  /// Returns true if [url] is a private user photo reference that requires
  /// backend V4 signing before rendering. Public catalog URLs (e.g.
  /// `us_mint_coin_images`, `numista-reference-library`) return false.
  static bool needsSigning(String? url) {
    if (url == null) return false;
    final trimmed = url.trim();
    if (trimmed.isEmpty) return false;
    final lower = trimmed.toLowerCase();

    if (lower.startsWith('gs://')) {
      return isOwnedStorageUrl(trimmed);
    }

    if (!isOwnedStorageUrl(trimmed)) {
      return false;
    }

    // Legacy Firebase / GCS URLs pointing to `/users/...` or `users%2F...`
    final uri = Uri.tryParse(trimmed);
    if (uri == null) return false;
    final decodedPath = Uri.decodeFull(uri.path).toLowerCase();
    return decodedPath.contains('/users/');
  }

  /// Resolve a single [rawUrl]. Public URLs pass through unchanged.
  /// Private user URLs return a cached or freshly minted 15-min signed URL,
  /// or `null` if signing fails or is forbidden.
  static Future<String?> resolve(String? rawUrl) async {
    if (rawUrl == null) return null;
    final trimmed = rawUrl.trim();
    if (trimmed.isEmpty) return null;

    if (!needsSigning(trimmed)) {
      return trimmed;
    }

    final now = clock();
    final cached = _cache[trimmed];
    if (cached != null) {
      if (now.isBefore(cached.expiresAt)) {
        return cached.signedUrl;
      }
      _cache.remove(trimmed);
    }

    final existing = _inFlight[trimmed];
    if (existing != null) {
      return existing.future;
    }

    final pending = _PendingRequest();
    final future = pending.future;
    _inFlight[trimmed] = pending;
    _batchQueue.add(trimmed);

    if (_batchQueue.length >= _maxBatchSize) {
      _batchTimer?.cancel();
      _batchTimer = null;
      unawaited(_flushBatch());
    } else {
      _batchTimer ??= Timer(_coalesceWindow, () {
        _batchTimer = null;
        unawaited(_flushBatch());
      });
    }

    return future;
  }

  static Future<void> _flushBatch() async {
    if (_batchQueue.isEmpty) return;

    while (_batchQueue.isNotEmpty) {
      final count =
          _batchQueue.length > _maxBatchSize ? _maxBatchSize : _batchQueue.length;
      final batch = _batchQueue.sublist(0, count);
      _batchQueue.removeRange(0, count);
      await _executeBatch(batch);
    }
  }

  static Future<void> _executeBatch(List<String> urls) async {
    final Map<String, String> resolved = {};
    try {
      final endpoint = Uri.parse('$kApiBaseUrl/api/v1/photos/signed_url');
      final response = await HttpAuthClient.post(
        endpoint,
        body: jsonEncode({'urls': urls}),
      );

      if (response.statusCode == 200) {
        final decoded = jsonDecode(response.body);
        if (decoded is Map<String, dynamic>) {
          final signedMap = decoded['signed_urls'];
          if (signedMap is Map) {
            for (final entry in signedMap.entries) {
              final k = entry.key?.toString();
              final v = entry.value?.toString();
              if (k != null && v != null && v.isNotEmpty) {
                resolved[k] = v;
              }
            }
          }
        }
      }
    } catch (e) {
      debugPrint('[SignedPhotoUrlService] Batch signing failed: $e');
    }

    final now = clock();
    final expiresAt = now.add(_cacheTtl);
    for (final url in urls) {
      final signed = resolved[url];
      if (signed != null) {
        _cache[url] = _CachedSignedUrl(signed, expiresAt);
      } else {
        _cache.remove(url);
      }

      final pending = _inFlight.remove(url);
      if (pending != null) {
        for (final c in pending.completers) {
          if (!c.isCompleted) c.complete(signed);
        }
      }
    }
  }
}
