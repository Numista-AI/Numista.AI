import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/coin_model.dart';

class EpnService {
  static const String _keyCampId = 'epn_campaign_id';
  static const String _keyMkrid = 'epn_rotation_id';
  static const String _keyAppId = 'ebay_app_id';
  static const String _keyCertId = 'ebay_cert_id';
  
  // Numista.AI EPN Credentials (Campaign ID confirmed active in partner.ebay.com)
  static const String _defaultCampId = '5339148752'; // Numista.AI — approved April 10, 2026
  static const String _defaultMkrid = '711-53200-19255-0'; // eBay US Marketplace

  static Future<void> saveSettings(String campId, String mkrid, {String? appId, String? certId}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyCampId, campId);
    await prefs.setString(_keyMkrid, mkrid);
    if (appId != null) await prefs.setString(_keyAppId, appId);
    if (certId != null) await prefs.setString(_keyCertId, certId);
  }

  static Future<Map<String, String>> getSettings() async {
    final prefs = await SharedPreferences.getInstance();
    return {
      'campaignId': prefs.getString(_keyCampId) ?? _defaultCampId,
      'rotationId': prefs.getString(_keyMkrid) ?? _defaultMkrid,
      'appId': prefs.getString(_keyAppId) ?? '',
      'certId': prefs.getString(_keyCertId) ?? '',
    };
  }

  static Future<String?> _getAccessToken() async {
    final settings = await getSettings();
    final appId = settings['appId']!;
    final certId = settings['certId']!;

    if (appId.isEmpty || certId.isEmpty) return null;

    final credentials = base64Encode(utf8.encode('$appId:$certId'));
    
    try {
      final response = await http.post(
        Uri.parse('https://api.ebay.com/identity/v1/oauth2/token'),
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Authorization': 'Basic $credentials',
        },
        body: {
          'grant_type': 'client_credentials',
          'scope': 'https://api.ebay.com/oauth/api_scope',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['access_token'];
      }
    } catch (e) {
      debugPrint('eBay OAuth Error: $e');
    }
    return null;
  }

  static Future<List<Map<String, dynamic>>> fetchEbayResults(CoinModel coin) async {
    final token = await _getAccessToken();
    if (token == null) return [];

    final query = _buildQuery(coin);
    final encodedQuery = Uri.encodeComponent(query);
    
    // Browse API search - limit 5 for performance
    final url = 'https://api.ebay.com/buy/browse/v1/item_summary/search?q=$encodedQuery&limit=5';

    try {
      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $token',
          'X-EBAY-C-MARKETPLACE-ID': 'EBAY_US',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final List items = data['itemSummaries'] ?? [];
        return items.cast<Map<String, dynamic>>();
      }
    } catch (e) {
      debugPrint('eBay API Error: $e');
    }
    return [];
  }

  static String _buildQuery(CoinModel coin) {
    String query = '';
    if (coin.year.isNotEmpty) query += '${coin.year} ';
    if (coin.mintMark.isNotEmpty) query += '${coin.mintMark} ';
    if (coin.denomination.isNotEmpty) query += '${coin.denomination} ';
    if (coin.programSeries.isNotEmpty) query += '${coin.programSeries} ';
    if (coin.variety.isNotEmpty) query += '${coin.variety} ';
    return query.trim();
  }

  static Future<String> generateSearchUrl(CoinModel coin) async {
    final settings = await getSettings();
    final campId = settings['campaignId']!;
    final mkrid = settings['rotationId']!;
    
    final query = _buildQuery(coin);
    final encodedQuery = Uri.encodeComponent(query);
    
    final targetUrl = 'https://www.ebay.com/sch/i.html?_nkw=$encodedQuery';
    return '$targetUrl&mkevt=1&mkcid=1&mkrid=$mkrid&campid=$campId&toolid=10001';
  }
}
