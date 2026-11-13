// numista_mobile/lib/services/mint_product_lookup_service.dart

import 'dart:convert';
import 'package:flutter/foundation.dart'; // @visibleForTesting (v1.6)
import 'package:flutter/services.dart';
import '../models/coin_model.dart';
import '../models/mint_product_metadata.dart';

// v1.5 (R2): no cloud_firestore import and no Firestore field. Read-only asset join.

class MintProductLookupService {
  static final MintProductLookupService instance = MintProductLookupService._internal();
  MintProductLookupService._internal();

  Map<String, MintProductMetadata>? _byNacCode;
  List<Map<String, dynamic>>? _rawCatalogEntries;
  bool _isLoading = false;

  /// Test constructor for dependency injection (MF-1)
  MintProductLookupService.forTesting({
    required Map<String, MintProductMetadata> entries,
    List<Map<String, dynamic>>? rawEntries,
  })  : _byNacCode = entries,
        _rawCatalogEntries = rawEntries;

  /// v1.6 (MF-3): uninitialized instance so tests can exercise ensureInitialized().
  @visibleForTesting
  MintProductLookupService.forInitTesting();

  /// Last tolerated init failure (missing asset / bad JSON). Null on success. (v1.6 MF-3)
  Object? lastInitError;

  /// Asynchronous catalog asset loader. Fails closed ONLY for missing assets or bad JSON;
  /// every other exception is rethrown so it cannot be silently swallowed (v1.6 MF-3).
  Future<void> ensureInitialized({AssetBundle? bundle}) async {
    if (_byNacCode != null || _isLoading) return;
    _isLoading = true;
    final b = bundle ?? rootBundle;
    try {
      final catalogJson = jsonDecode(await b.loadString('assets/catalog/catalog_public_v1.json')) as List<dynamic>;
      _rawCatalogEntries = catalogJson.whereType<Map<String, dynamic>>().toList();
      _eligibleRowsByNac = null;

      final overlayJson = jsonDecode(await b.loadString('assets/catalog/mint_product_fields_v1.json')) as Map<String, dynamic>;
      final map = <String, MintProductMetadata>{};
      overlayJson.forEach((nac, data) {
        if (data is Map<String, dynamic>) map[nac.toUpperCase()] = MintProductMetadata.fromJson(data);
      });
      _byNacCode = map;
      lastInitError = null;
    } on FlutterError catch (e) {          // asset not bundled
      lastInitError = e; _byNacCode = {}; _rawCatalogEntries = [];
    } on FormatException catch (e) {       // malformed JSON
      lastInitError = e; _byNacCode = {}; _rawCatalogEntries = [];
    } finally {
      _isLoading = false;
    }
  }

  /// v1.6 (MF-2) + v1.7/v1.8 (MF-5a): eligibility index. ONLY rows with explicit
  /// is_placeholder == false AND US coin type (`type == 'coin'` && `.US.` in nac_code).
  Map<String, Map<String, dynamic>>? _eligibleRowsByNac;

  Map<String, Map<String, dynamic>> get _eligible {
    return _eligibleRowsByNac ??= {
      for (final e in (_rawCatalogEntries ?? const <Map<String, dynamic>>[]))
        if (e['is_placeholder'] == false &&
            (e['nac_code']?.toString().isNotEmpty ?? false) &&
            e['type'] == 'coin' &&
            e['nac_code'].toString().toUpperCase().contains('.US.'))
          e['nac_code'].toString().toUpperCase(): e,
    };
  }

  static bool _isUsCoin(CoinModel coin) {
    final c = coin.country.trim().toLowerCase();
    return c == 'usa' || c == 'united states' || c == 'us' || c == 'u.s.' || c == 'u.s.a.';
  }

  /// Synchronous in-memory lookup. Returns null if uninitialized, non-US, ineligible, or no unique match.
  MintProductMetadata? lookupForCoin(CoinModel coin) {
    if (_byNacCode == null) return null;
    if (!_isUsCoin(coin)) return null; // v1.7 MF-5a: fail closed for non-US coins
    final eligible = _eligible;

    // 1. Primary join: NAC must exist as an ELIGIBLE US catalog row AND have an overlay entry.
    final ref = coin.personalRef.trim().toUpperCase();
    if (RegExp(r'^NAC1?\.').hasMatch(ref)) {
      if (!eligible.containsKey(ref)) return null; // placeholder, non-US, or missing row -> fail closed
      return _byNacCode![ref];                      // null if no overlay entry
    }

    // 2. Composite fallback join: all four keys required on BOTH sides.
    final targetYear = int.tryParse(coin.year.replaceAll(RegExp(r'\.0$'), ''));
    final rawMint = coin.mintMark.trim().toUpperCase();
    final targetFacility = rawMint.isEmpty ? 'Philadelphia' : _mintMarkToFacility(rawMint);
    final targetDenom = _normalizeDenom(coin.denomination);
    final targetSeries = coin.programSeries.trim().toLowerCase();
    if (targetYear == null || targetFacility.isEmpty || targetDenom.isEmpty || targetSeries.isEmpty) {
      return null;
    }

    final matches = eligible.values.where((entry) {
      final y = entry['year'];
      final f = entry['mint_facility']?.toString().trim().toLowerCase() ?? '';
      final d = _normalizeDenom(entry['denomination']?.toString() ?? '');
      final sr = entry['series']?.toString().trim().toLowerCase() ?? '';
      if (y is! int || f.isEmpty || d.isEmpty || sr.isEmpty) return false; // incomplete row -> no match
      // v1.7/v1.8 MF-5b (LOCKED): blank mint mark maps to Philadelphia ONLY if catalog row mint_mark_on_coin is null/blank/false
      if (rawMint.isEmpty) {
        final mmOnCoin = entry['mint_mark_on_coin'];
        final isNoMintMark = mmOnCoin == null || mmOnCoin == false || mmOnCoin.toString().trim().isEmpty;
        if (!isNoMintMark) return false;
      }
      return y == targetYear && f == targetFacility.toLowerCase() && d == targetDenom && sr == targetSeries;
    }).toList();

    if (matches.length != 1) return null; // ambiguity guard
    final nac = matches.first['nac_code'].toString().toUpperCase();
    return _byNacCode![nac]; // overlay only; never synthesize metadata from a catalog row
  }

  String _mintMarkToFacility(String mintMark) {
    switch (mintMark.trim().toUpperCase()) {
      case 'D': return 'Denver';
      case 'S': return 'San Francisco';
      case 'W': return 'West Point';
      case 'P': return 'Philadelphia';
      case 'O': return 'New Orleans';
      case 'CC': return 'Carson City';
      default: return '';
    }
  }

  String _normalizeDenom(String denom) {
    final d = denom.trim().toLowerCase();
    if (d == 'dollar' || d == r'$1' || d == r'$1.00' || d == '1d') return '1d';
    if (d == 'half dollar' || d == 'fifty cents' || d == '50 cents' || d == r'$0.50' || d == '50c') return '50c';
    if (d == 'quarter dollar' || d == 'quarter' || d == 'twenty-five cents' || d == '25 cents' || d == r'$0.25' || d == '25c') return '25c';
    if (d == 'dime' || d == 'ten cents' || d == '10 cents' || d == r'$0.10' || d == '10c') return '10c';
    if (d == 'five cents' || d == 'five cent' || d == '5 cents' || d == '5 cent' || d == 'nickel' || d == 'half dime' || d == r'$0.05' || d == '5c') return '5c';
    if (d == 'three cent nickel' || d == 'three cent silver' || d == 'three cents' || d == '3 cents' || d == '3c') return '3c';
    if (d == 'two cents' || d == '2 cents' || d == '2c') return '2c';
    if (d == 'cent' || d == 'one cent' || d == '1 cent' || d == 'penny' || d == r'$0.01' || d == '1c') return '1c';
    return d;
  }
}
