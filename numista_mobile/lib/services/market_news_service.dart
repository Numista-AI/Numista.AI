import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class MarketNewsArticle {
  final String title;
  final String link;
  final String source;
  final String published;
  final String summary;

  MarketNewsArticle({
    required this.title,
    required this.link,
    required this.source,
    required this.published,
    required this.summary,
  });

  factory MarketNewsArticle.fromJson(Map<String, dynamic> json) {
    return MarketNewsArticle(
      title: json['title'] ?? '',
      link: json['link'] ?? '',
      source: json['source'] ?? 'Numismatic News',
      published: json['published'] ?? '',
      summary: json['summary'] ?? '',
    );
  }

  Map<String, dynamic> toJson() => {
    'title': title,
    'link': link,
    'source': source,
    'published': published,
    'summary': summary,
  };
}

class MarketNewsService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';
  static const String _cacheKey = 'cached_numismatic_news_v1';

  /// Fetches news articles from backend /api/news/feed proxy with local SharedPreferences fallback.
  static Future<List<MarketNewsArticle>> fetchNewsFeed() async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl/api/news/feed'))
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final list = (data['articles'] as List? ?? [])
            .map((item) => MarketNewsArticle.fromJson(item))
            .toList();

        if (list.isNotEmpty) {
          // Cache locally
          final prefs = await SharedPreferences.getInstance();
          final rawJson = jsonEncode(list.map((e) => e.toJson()).toList());
          await prefs.setString(_cacheKey, rawJson);
          return list;
        }
      }
    } catch (e) {
      debugPrint('[MarketNewsService] Feed fetch failed: $e. Falling back to local cache.');
    }

    // Fallback to local cache
    return _loadCachedNews();
  }

  static Future<List<MarketNewsArticle>> _loadCachedNews() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedStr = prefs.getString(_cacheKey);
      if (cachedStr != null && cachedStr.isNotEmpty) {
        final rawList = jsonDecode(cachedStr) as List;
        return rawList.map((e) => MarketNewsArticle.fromJson(e)).toList();
      }
    } catch (_) {}

    // Final fallback articles
    return [
      MarketNewsArticle(
        title: "2026 Semiquincentennial Circulating Coin Designs Unveiled",
        link: "https://www.usmint.gov",
        source: "U.S. Mint",
        published: "Sun, 26 Jul 2026",
        summary: "The U.S. Mint releases official specifications for the 250th Anniversary coin series.",
      ),
      MarketNewsArticle(
        title: "Morgan & Peace Silver Dollar Market Values Stabilize in Q3",
        link: "https://www.greysheet.com",
        source: "Greysheet",
        published: "Sun, 26 Jul 2026",
        summary: "Wholesale prices across MS63 to MS66 grades hold steady amid strong collector demand.",
      )
    ];
  }
}
