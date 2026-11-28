import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';

/// Shared Chapter 0 sharded catalog asset loader (Plan 8f01c991).
///
/// Primary path: loads `assets/catalog/catalog_manifest_v1.json` + lightweight
/// `catalog_search_index_v1.json` once into memory, then lazy-loads individual
/// `chunks/era_<slug>[_pN].json` files on demand when opening entry details and
/// `children/varieties_v1.json` when expanding normalized child varieties.
///
/// Fallback path: if `catalog_manifest_v1.json` is absent (legacy bundles or
/// synthetic unit-test fixtures), transparently loads `assets/catalog/catalog_public_v1.json`.
class CatalogAssetLoader {
  static const String assetDirPrefix = 'assets/catalog/';
  static const String manifestAssetPath = '${assetDirPrefix}catalog_manifest_v1.json';
  static const String legacyMonolithAssetPath = '${assetDirPrefix}catalog_public_v1.json';

  static final CatalogAssetLoader instance = CatalogAssetLoader._();

  CatalogAssetLoader._();

  /// Creates an isolated loader instance (e.g., for custom AssetBundle injection or tests).
  CatalogAssetLoader();

  AssetBundle? _cachedBundle;
  bool _loaded = false;
  bool _isSharded = false;
  Map<String, dynamic>? _manifest;
  List<Map<String, dynamic>> _indexEntries = const [];
  final Map<String, Map<String, dynamic>> _indexByNac = {};
  final Map<String, Map<String, dynamic>> _indexByAlias = {};
  final Map<String, Map<String, Map<String, dynamic>>> _chunkCacheByRel = {};
  Map<String, List<Map<String, dynamic>>>? _varietiesByParent;

  bool get isSharded => _isSharded;
  Map<String, dynamic>? get manifest => _manifest;

  @visibleForTesting
  void resetForTesting() {
    _cachedBundle = null;
    _loaded = false;
    _isSharded = false;
    _manifest = null;
    _indexEntries = const [];
    _indexByNac.clear();
    _indexByAlias.clear();
    _chunkCacheByRel.clear();
    _varietiesByParent = null;
  }

  void _populateIndexLookup(List<Map<String, dynamic>> entries) {
    _indexByNac.clear();
    _indexByAlias.clear();
    for (final entry in entries) {
      final nac = (entry['nac_code'] as String? ?? '').trim().toUpperCase();
      if (nac.isNotEmpty) {
        _indexByNac[nac] = entry;
      }
      final aliases = entry['nac_aliases'];
      if (aliases is List) {
        for (final a in aliases) {
          if (a is String && a.trim().isNotEmpty) {
            _indexByAlias[a.trim().toUpperCase()] = entry;
          }
        }
      }
    }
  }

  /// Loads the catalog browse/search index (sharded manifest+index primary, monolith fallback).
  /// Rethrows [FlutterError] or [FormatException] when neither source can be loaded.
  Future<List<Map<String, dynamic>>> loadIndex({AssetBundle? bundle}) async {
    final b = bundle ?? rootBundle;
    if (_loaded && identical(_cachedBundle, b)) {
      return _indexEntries;
    }

    resetForTesting();
    _cachedBundle = b;

    // 1. Primary path: sharded manifest + index files
    String? rawManifest;
    try {
      rawManifest = await b.loadString(manifestAssetPath);
    } on FlutterError {
      rawManifest = null;
    }

    if (rawManifest != null) {
      final decodedManifest = jsonDecode(rawManifest);
      if (decodedManifest is Map<String, dynamic> &&
          decodedManifest['schema_version'] == 'catalog_sharded_v1') {
        final indexObj = decodedManifest['index'];
        final rawFiles = indexObj is Map ? indexObj['files'] : null;
        if (rawFiles is List && rawFiles.isNotEmpty) {
          final merged = <Map<String, dynamic>>[];
          for (final rel in rawFiles) {
            if (rel is! String || rel.trim().isEmpty) continue;
            final rawIdx = await b.loadString('$assetDirPrefix${rel.trim()}');
            final decodedIdx = jsonDecode(rawIdx);
            if (decodedIdx is! List) {
              throw FormatException('Expected JSON array in index file: $rel');
            }
            for (final item in decodedIdx) {
              if (item is Map) {
                merged.add(Map<String, dynamic>.from(item));
              }
            }
          }
          _manifest = decodedManifest;
          _isSharded = true;
          _indexEntries = merged;
          _populateIndexLookup(merged);
          _loaded = true;
          return _indexEntries;
        }
      }
    }

    // 2. Transparent fallback: legacy monolithic catalog_public_v1.json
    final rawLegacy = await b.loadString(legacyMonolithAssetPath);
    final decodedLegacy = jsonDecode(rawLegacy);
    List<dynamic> rawList;
    if (decodedLegacy is List) {
      rawList = decodedLegacy;
    } else if (decodedLegacy is Map && decodedLegacy['items'] is List) {
      rawList = decodedLegacy['items'] as List<dynamic>;
    } else {
      throw const FormatException('Unexpected catalog_public_v1.json root type');
    }

    final entries = rawList
        .whereType<Map>()
        .map((e) => Map<String, dynamic>.from(e))
        .toList();

    _manifest = null;
    _isSharded = false;
    _indexEntries = entries;
    _populateIndexLookup(entries);
    _loaded = true;
    return _indexEntries;
  }

  /// Resolves an entry by canonical `nac_code` or retired `nac_aliases` and lazy-loads
  /// its single era chunk (when sharded) to return the full hydrated catalog map.
  Future<Map<String, dynamic>?> loadFullEntry(
    String rawNacOrAlias, {
    AssetBundle? bundle,
  }) async {
    final key = rawNacOrAlias.trim().toUpperCase();
    if (key.isEmpty) return null;

    final b = bundle ?? rootBundle;
    await loadIndex(bundle: b);

    final indexHit = _indexByNac[key] ?? _indexByAlias[key];
    if (indexHit == null) return null;

    if (!_isSharded) {
      return indexHit;
    }

    final canonicalNac =
        (indexHit['nac_code'] as String? ?? '').trim().toUpperCase();
    final chunkRel = (indexHit['chunk'] as String? ?? '').trim();
    if (chunkRel.isEmpty) {
      return indexHit;
    }

    var chunkMap = _chunkCacheByRel[chunkRel];
    if (chunkMap == null) {
      final rawChunk = await b.loadString('$assetDirPrefix$chunkRel');
      final decoded = jsonDecode(rawChunk);
      if (decoded is! List) {
        throw FormatException('Expected JSON array in chunk file: $chunkRel');
      }
      final loadedMap = <String, Map<String, dynamic>>{};
      for (final item in decoded) {
        if (item is Map) {
          final m = Map<String, dynamic>.from(item);
          final n = (m['nac_code'] as String? ?? '').trim().toUpperCase();
          if (n.isNotEmpty) {
            loadedMap[n] = m;
          }
        }
      }
      _chunkCacheByRel[chunkRel] = loadedMap;
      chunkMap = loadedMap;
    }

    return chunkMap[canonicalNac] ?? indexHit;
  }

  /// Lazy-loads normalized child varieties for [parentNac1] from `children/varieties_v1.json`
  /// (falling back to inline `varieties[]` in monolithic mode).
  Future<List<Map<String, dynamic>>> loadVarietiesForParent(
    String parentNac1, {
    AssetBundle? bundle,
  }) async {
    final key = parentNac1.trim().toUpperCase();
    if (key.isEmpty) return const [];

    final b = bundle ?? rootBundle;
    await loadIndex(bundle: b);

    if (_isSharded) {
      if (_varietiesByParent == null) {
        final childTables = _manifest?['child_tables'];
        final varietiesMeta =
            childTables is Map ? childTables['varieties'] : null;
        final relPath =
            varietiesMeta is Map ? (varietiesMeta['path'] as String? ?? '').trim() : '';
        final grouped = <String, List<Map<String, dynamic>>>{};
        if (relPath.isNotEmpty) {
          try {
            final rawVar = await b.loadString('$assetDirPrefix$relPath');
            final decoded = jsonDecode(rawVar);
            if (decoded is List) {
              for (final item in decoded) {
                if (item is Map) {
                  final m = Map<String, dynamic>.from(item);
                  final p =
                      (m['parent_nac1'] as String? ?? '').trim().toUpperCase();
                  if (p.isNotEmpty) {
                    grouped.putIfAbsent(p, () => []).add(m);
                  }
                }
              }
            }
          } on FlutterError {
            // Optional child file missing -> fail empty
          }
        }
        _varietiesByParent = grouped;
      }
      return _varietiesByParent![key] ?? const [];
    }

    final entry = _indexByNac[key] ?? _indexByAlias[key];
    final rawInline = entry?['varieties'];
    if (rawInline is List) {
      return rawInline
          .whereType<Map>()
          .map((e) => Map<String, dynamic>.from(e))
          .toList();
    }
    return const [];
  }
}
