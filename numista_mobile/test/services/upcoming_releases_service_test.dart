import 'dart:convert';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:numista_ai/constants.dart';
import 'package:numista_ai/services/upcoming_releases_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  group('UpcomingRelease Model', () {
    test('fromJson parses full fields accurately', () {
      final json = {
        'item_number': '26XE',
        'title': 'Morgan Silver Dollar 2026 Enhanced Uncirculated Coin',
        'price': '\$169.00',
        'status': 'Available',
        'release_date': 'Summer 2026',
        'image_url': 'https://example.com/26xe.jpg',
        'product_url': 'https://www.usmint.gov/26xe.html',
        'program': 'Morgan and Peace Dollars',
        'badge': 'NewLimited',
        'finish': 'Enhanced Uncirculated',
        'mint_location': 'San Francisco (S)',
        'mintage_limit': 250000,
        'household_limit': 2,
        'description': 'Commemorative silver dollar coin.'
      };

      final release = UpcomingRelease.fromJson(json);

      expect(release.itemNumber, '26XE');
      expect(release.title, 'Morgan Silver Dollar 2026 Enhanced Uncirculated Coin');
      expect(release.price, '\$169.00');
      expect(release.status, 'Available');
      expect(release.releaseDate, 'Summer 2026');
      expect(release.imageUrl, 'https://example.com/26xe.jpg');
      expect(release.productUrl, 'https://www.usmint.gov/26xe.html');
      expect(release.program, 'Morgan and Peace Dollars');
      expect(release.badge, 'NewLimited');
      expect(release.finish, 'Enhanced Uncirculated');
      expect(release.mintLocation, 'San Francisco (S)');
      expect(release.mintageLimit, 250000);
      expect(release.householdLimit, 2);
      expect(release.description, 'Commemorative silver dollar coin.');
    });

    test('toJson serializes correctly', () {
      final release = UpcomingRelease(
        itemNumber: '26EA',
        title: 'American Eagle 2026 One Ounce Silver Proof Coin',
        price: '\$173.00',
        status: 'Available',
        releaseDate: 'Spring 2026',
        imageUrl: 'https://example.com/26ea.jpg',
        productUrl: 'https://www.usmint.gov/26ea.html',
        program: 'American Eagle',
        badge: 'Limited',
        finish: 'Proof',
        mintLocation: 'West Point (W)',
        mintageLimit: 50000,
        householdLimit: 1,
        description: 'Proof silver eagle',
      );

      final json = release.toJson();
      expect(json['item_number'], '26EA');
      expect(json['price'], '\$173.00');
      expect(json['mintage_limit'], 50000);
    });

    test('fromJson handles null and missing optional fields with defaults', () {
      final json = {
        'item_number': '26TEST',
        'title': 'Test Coin',
      };

      final release = UpcomingRelease.fromJson(json);
      expect(release.itemNumber, '26TEST');
      expect(release.title, 'Test Coin');
      expect(release.price, '');
      expect(release.status, 'Not Available');
      expect(release.imageUrl, isNull);
      expect(release.mintageLimit, isNull);
    });
  });

  group('UpcomingReleasesService Fallback', () {
    setUp(() {
      SharedPreferences.setMockInitialValues({});
      UpcomingReleasesService.resetForTest();
    });

    test('fallback returns verified 2026 US Mint products with GCS imageUrls when network fails', () async {
      final releases = await http.runWithClient(
        () => UpcomingReleasesService.fetchUpcoming(),
        () => MockClient((request) async {
          return http.Response('Server Error', 500);
        }),
      );
      expect(releases, hasLength(5));
      expect(releases.any((r) => r.itemNumber == '26XE'), isTrue);
      expect(releases.any((r) => r.itemNumber == '26EA'), isTrue);
      for (final r in releases) {
        expect(
          r.imageUrl,
          startsWith('https://storage.googleapis.com/numista-reference-library/reference_library/us_mint_official/2026_products/'),
        );
      }
    });

    test('P5 capture: fetchUpcoming and fetchAll hit exact GET URLs and fallback on empty products', () async {
      final captured = <http.Request>[];
      final mockClient = MockClient((request) async {
        captured.add(request);
        return http.Response(jsonEncode({'products': []}), 200);
      });

      final upcoming = await http.runWithClient(
        () => UpcomingReleasesService.fetchUpcoming(),
        () => mockClient,
      );
      final all = await http.runWithClient(
        () => UpcomingReleasesService.fetchAll(),
        () => mockClient,
      );

      expect(captured, hasLength(2));
      expect(captured[0].method, 'GET');
      expect(captured[0].url.toString(), '$kApiBaseUrl/api/mint-releases/upcoming');
      expect(captured[1].method, 'GET');
      expect(captured[1].url.toString(), '$kApiBaseUrl/api/mint-releases/all');

      expect(upcoming, hasLength(5));
      expect(all, hasLength(5));
      expect(upcoming.every((r) => r.imageUrl != null && r.imageUrl!.isNotEmpty), isTrue);
    });
  });
}
