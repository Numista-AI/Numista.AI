import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/coin_model.dart';

class EpnService {
  static const String _keyCampId = 'epn_campaign_id';
  static const String _keyMkrid  = 'epn_rotation_id';
  static const String _keyAppId  = 'ebay_app_id';
  static const String _keyCertId = 'ebay_cert_id';

  // ── Numista.AI EPN Credentials ─────────────────────────────────────────────
  // Defaults are empty; real values are loaded from Firestore /config/ebay
  // at startup via loadFromFirestore(). This keeps secrets out of client code.
  static const String _defaultCampId = '5339148752'; // public campaign ID (non-secret)
  static const String _defaultMkrid  = '711-53200-19255-0'; // eBay US marketplace
  static const String _defaultAppId  = ''; // loaded from Firestore at startup
  static const String _defaultCertId = ''; // loaded from Firestore at startup

  // ── Load credentials from Firestore /config/ebay ───────────────────────────
  // Call once at app startup (BaseLayout.initState). Credentials are stored
  // in SharedPreferences for subsequent requests within the session.
  static Future<void> loadFromFirestore() async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection('config')
          .doc('ebay')
          .get();
      if (!doc.exists) return;
      final data = doc.data()!;
      final prefs = await SharedPreferences.getInstance();
      final appId  = data['app_id']  as String? ?? '';
      final certId = data['cert_id'] as String? ?? '';
      final campId = data['campaign_id'] as String? ?? _defaultCampId;
      final mkrid  = data['rotation_id'] as String? ?? _defaultMkrid;
      if (appId.isNotEmpty)  await prefs.setString(_keyAppId,  appId);
      if (certId.isNotEmpty) await prefs.setString(_keyCertId, certId);
      if (campId.isNotEmpty) await prefs.setString(_keyCampId, campId);
      if (mkrid.isNotEmpty)  await prefs.setString(_keyMkrid,  mkrid);
      debugPrint('[EPN] Credentials loaded from Firestore');
    } catch (e) {
      debugPrint('[EPN] Failed to load credentials from Firestore: $e');
    }
  }

  // ── Settings persistence ────────────────────────────────────────────────────

  static Future<void> saveSettings(
      String campId, String mkrid, {String? appId, String? certId}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyCampId, campId);
    await prefs.setString(_keyMkrid,  mkrid);
    if (appId  != null) await prefs.setString(_keyAppId,  appId);
    if (certId != null) await prefs.setString(_keyCertId, certId);
  }

  static Future<Map<String, String>> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'campaignId': prefs.getString(_keyCampId) ?? _defaultCampId,
      'rotationId': prefs.getString(_keyMkrid)  ?? _defaultMkrid,
      'appId':      prefs.getString(_keyAppId)  ?? _defaultAppId,
      'certId':     prefs.getString(_keyCertId) ?? _defaultCertId,
    };
  }

  // ── OAuth token (eBay Browse API) ──────────────────────────────────────────

  static Future<String?> _getAccessToken() async {
    final settings = await getSettings();
    final appId  = settings['appId']!;
    final certId = settings['certId']!;

    if (appId.isEmpty || certId.isEmpty) return null;

    final credentials = base64Encode(utf8.encode('$appId:$certId'));

    try {
      final response = await http.post(
        Uri.parse('https://api.ebay.com/identity/v1/oauth2/token'),
        headers: {
          'Content-Type':  'application/x-www-form-urlencoded',
          'Authorization': 'Basic $credentials',
        },
        body: {
          'grant_type': 'client_credentials',
          'scope': 'https://api.ebay.com/oauth/api_scope',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['access_token'] as String?;
      } else {
        debugPrint('eBay OAuth ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('eBay OAuth Error: $e');
    }
    return null;
  }

  // ── Live price fetch via eBay Browse API ───────────────────────────────────

  static Future<List<Map<String, dynamic>>> fetchEbayResults(CoinModel coin) async {
    final token = await _getAccessToken();
    if (token == null) return [];

    final query        = _buildQuery(coin);
    final encodedQuery = Uri.encodeComponent(query);

    // Limit to 5 results for performance; filter to US marketplace
    final url =
        'https://api.ebay.com/buy/browse/v1/item_summary/search'
        '?q=$encodedQuery&limit=5&filter=itemLocationCountry:US';

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization':          'Bearer $token',
          'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        },
      );

      if (response.statusCode == 200) {
        final data   = jsonDecode(response.body);
        final items  = data['itemSummaries'] as List? ?? [];
        return items.cast<Map<String, dynamic>>();
      } else {
        debugPrint('eBay Browse API ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      debugPrint('eBay API Error: $e');
    }
    return [];
  }

  // ── Query builder ──────────────────────────────────────────────────────────

  static String _buildQuery(CoinModel coin) {
    final parts = <String>[];
    if (coin.year.isNotEmpty)         parts.add(coin.year);
    if (coin.mintMark.isNotEmpty)     parts.add(coin.mintMark);
    if (coin.denomination.isNotEmpty) parts.add(coin.denomination);
    if (coin.programSeries.isNotEmpty) parts.add(coin.programSeries);
    if (coin.variety.isNotEmpty)      parts.add(coin.variety);
    parts.add('coin'); // improves eBay search relevance
    return parts.join(' ').trim();
  }

  // ── EPN affiliate URL generator ────────────────────────────────────────────
  // Appending EPN parameters earns Numista.AI a commission (≈1–4%) on any
  // eBay purchase made through these links.

  static Future<String> generateSearchUrl(CoinModel coin, {bool soldOnly = true}) async {
    final settings = await getSettings();
    final campId   = settings['campaignId']!;
    final mkrid    = settings['rotationId']!;

    final query        = _buildQuery(coin);
    final encodedQuery = Uri.encodeComponent(query);

    // Base eBay search with sold listings (most useful for valuation)
    final baseSearch =
        'https://www.ebay.com/sch/i.html'
        '?_nkw=$encodedQuery'
        '${soldOnly ? '&LH_Sold=1&LH_Complete=1' : ''}';

    // EPN tracking parameters — required for commission attribution
    final epnParams =
        'mkevt=1'
        '&mkcid=1'
        '&mkrid=$mkrid'
        '&campid=$campId'
        '&toolid=10001'
        '&siteid=0';

    return '$baseSearch&$epnParams';
  }

  // ── Known Key Dates & High Value Varieties ──────────────────────────────────
  static const Set<String> _keyDateKeywords = {
    '1909-s vdb', '1909-s', '1914-d', '1931-s', '1922 no d', '1955 doubled die',
    '1916-d', '1942/1', '1932-d', '1932-s', '1901-s', '1893-s', '1889-cc',
    '1895 morgan', '1895-o', '1892-s', '1928 peace', '1979-s type 2', '1981-s type 2',
    '1995-w', '2019-w', '1877 cent', '1908-s cent', '1912-s nickel', '1913-s type 2',
    '1921 peace', '1878-cc', '1879-cc', '1890-cc', '1891-cc', '1892-cc'
  };

  /// Returns true if coin query or value qualifies as a high-value / key date ($200+).
  static bool isKeyDateOrHighValue(String query, {double? estimatedValue}) {
    if (estimatedValue != null && estimatedValue >= 200.0) return true;
    final lower = query.toLowerCase();
    return _keyDateKeywords.any((k) => lower.contains(k));
  }

  // ── Sync URL builder for raw query strings (e.g. missing program coins) ──
  // Uses hardcoded defaults so it can be called synchronously without
  // awaiting SharedPreferences — safe because campaign ID is non-secret.
  // _sacat=11116 = eBay Coins & Paper Money category.
  static String buildSearchUrlFromQuery(
    String query, {
    bool soldOnly = false,
    double? estimatedValue,
    String? customId,
  }) {
    String searchTerms = query.trim();
    if (isKeyDateOrHighValue(searchTerms, estimatedValue: estimatedValue)) {
      searchTerms = '$searchTerms PCGS NGC CAC';
    }

    final encodedQuery = Uri.encodeComponent(searchTerms);
    final customIdParam = (customId != null && customId.isNotEmpty)
        ? '&customid=${Uri.encodeComponent(customId)}'
        : '&customid=public_wishlist';

    return 'https://www.ebay.com/sch/i.html'
        '?_nkw=$encodedQuery'
        '&_sacat=11116'
        '${soldOnly ? "&LH_Sold=1&LH_Complete=1" : ""}'
        '&mkevt=1&mkcid=1&mkrid=$_defaultMkrid'
        '&campid=$_defaultCampId&toolid=10001&siteid=0'
        '$customIdParam';
  }
}

