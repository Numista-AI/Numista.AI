import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/upcoming_releases_service.dart';

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
    test('fallback returns verified 2026 US Mint products when network fails', () async {
      final releases = await UpcomingReleasesService.fetchUpcoming();
      expect(releases, isNotEmpty);
      expect(releases.any((r) => r.itemNumber == '26XE'), isTrue);
      expect(releases.any((r) => r.itemNumber == '26EA'), isTrue);
    });
  });
}
