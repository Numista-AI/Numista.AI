import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class UpcomingRelease {
  final String itemNumber;
  final String title;
  final String price;
  final String status;
  final String releaseDate;
  final String? imageUrl;
  final String productUrl;
  final String program;
  final String badge;
  final String? finish;
  final String? mintLocation;
  final int? mintageLimit;
  final int? householdLimit;
  final String? description;

  UpcomingRelease({
    required this.itemNumber,
    required this.title,
    required this.price,
    required this.status,
    required this.releaseDate,
    this.imageUrl,
    required this.productUrl,
    required this.program,
    required this.badge,
    this.finish,
    this.mintLocation,
    this.mintageLimit,
    this.householdLimit,
    this.description,
  });

  factory UpcomingRelease.fromJson(Map<String, dynamic> json) {
    return UpcomingRelease(
      itemNumber: json['item_number'] ?? '',
      title: json['title'] ?? '',
      price: json['price'] ?? '',
      status: json['status'] ?? 'Not Available',
      releaseDate: json['release_date'] ?? '',
      imageUrl: json['image_url'],
      productUrl: json['product_url'] ?? '',
      program: json['program'] ?? '',
      badge: json['badge'] ?? '',
      finish: json['finish'],
      mintLocation: json['mint_location'],
      mintageLimit: json['mintage_limit'],
      householdLimit: json['household_limit'],
      description: json['description'],
    );
  }

  Map<String, dynamic> toJson() => {
    'item_number': itemNumber,
    'title': title,
    'price': price,
    'status': status,
    'release_date': releaseDate,
    'image_url': imageUrl,
    'product_url': productUrl,
    'program': program,
    'badge': badge,
    'finish': finish,
    'mint_location': mintLocation,
    'mintage_limit': mintageLimit,
    'household_limit': householdLimit,
    'description': description,
  };
}

class UpcomingReleasesService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';
  static const String _cacheKey = 'upcoming_releases_cache';

  static Future<List<UpcomingRelease>> fetchUpcoming() async {
    return _fetchData('/api/mint-releases/upcoming');
  }

  static Future<List<UpcomingRelease>> fetchAll() async {
    return _fetchData('/api/mint-releases/all');
  }

  static Future<List<UpcomingRelease>> _fetchData(String endpoint) async {
    try {
      final response = await http
          .get(Uri.parse('$_baseUrl$endpoint'))
          .timeout(const Duration(seconds: 8));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final list = (data['products'] as List? ?? [])
            .map((item) => UpcomingRelease.fromJson(item))
            .toList();

        if (list.isNotEmpty) {
          final prefs = await SharedPreferences.getInstance();
          final rawJson = jsonEncode(list.map((e) => e.toJson()).toList());
          await prefs.setString(_cacheKey, rawJson);
          return list;
        }
      }
    } catch (e) {
      debugPrint('[UpcomingReleasesService] Fetch failed: $e. Falling back to local cache.');
    }
    return _loadCachedReleases();
  }

  static Future<List<UpcomingRelease>> _loadCachedReleases() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final cachedStr = prefs.getString(_cacheKey);
      if (cachedStr != null && cachedStr.isNotEmpty) {
        final rawList = jsonDecode(cachedStr) as List;
        return rawList.map((e) => UpcomingRelease.fromJson(e)).toList();
      }
    } catch (_) {}

    return [
      UpcomingRelease(
        itemNumber: '26XE',
        title: 'Morgan 2026 Silver Dollar',
        price: '\$169.00',
        status: 'Coming Soon',
        releaseDate: 'Fall 2026',
        productUrl: 'https://catalog.usmint.gov/morgan-2026-silver-dollar-26XE.html',
        program: 'Morgan Silver Dollar',
        badge: 'New',
        finish: 'Uncirculated',
        mintageLimit: 275000,
        householdLimit: 3,
      ),
      UpcomingRelease(
        itemNumber: '26EA',
        title: 'American Eagle 2026 One Ounce Silver Proof Coin',
        price: '\$173.00',
        status: 'Coming Soon',
        releaseDate: 'TBD',
        productUrl: 'https://catalog.usmint.gov',
        program: 'American Eagle',
        badge: '',
        finish: 'Proof',
        mintageLimit: null,
        householdLimit: null,
      ),
      UpcomingRelease(
        itemNumber: '26EB',
        title: 'American Eagle 2026 One Ounce Gold Proof Coin',
        price: '\$5,450.00',
        status: 'Available',
        releaseDate: 'Summer 2026',
        productUrl: 'https://catalog.usmint.gov',
        program: 'American Eagle',
        badge: '',
        finish: 'Proof',
        mintageLimit: 12500,
        householdLimit: 1,
      ),
      UpcomingRelease(
        itemNumber: '26EJ',
        title: 'American Eagle 2026 One Ounce Platinum Proof Coin',
        price: '\$2,445.00',
        status: 'Pre-Order',
        releaseDate: 'Winter 2026',
        productUrl: 'https://catalog.usmint.gov',
        program: 'American Eagle',
        badge: '',
        finish: 'Proof',
        mintageLimit: 10000,
        householdLimit: 1,
      ),
      UpcomingRelease(
        itemNumber: '26BM4',
        title: 'Best of the Mint: 1804 Silver Dollar Tribute',
        price: '\$5,740.00',
        status: 'Coming Soon',
        releaseDate: 'Late 2026',
        productUrl: 'https://catalog.usmint.gov',
        program: 'Best of the Mint',
        badge: 'Exclusive',
        finish: 'Proof',
        mintageLimit: 500,
        householdLimit: 1,
      ),
    ];
  }
}
