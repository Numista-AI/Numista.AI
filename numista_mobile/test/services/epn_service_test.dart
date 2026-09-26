import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/epn_service.dart';

void main() {
  group('EpnService - buildSearchUrlFromQuery Golden Test Vectors', () {
    test('Vector 1: Maya Angelou Quarter with parenthetical year stripped', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '2022 P American Women Quarters - Maya Angelou Quarter (1965-Date) coin',
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '2022 P American Women Quarters - Maya Angelou Quarter coin');
      expect(uri.queryParameters['_sacat'], '11116');
      expect(uri.queryParameters['customid'], 'numista_wishlist');
      expect(uri.queryParameters['campid'], '5339148752');
    });

    test('Vector 2: 1909-S VDB Lincoln Cent key-date appends PCGS NGC CAC', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '1909-S VDB Lincoln Cent',
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '1909-S VDB Lincoln Cent PCGS NGC CAC');
      expect(uri.queryParameters['_sacat'], '11116');
    });

    test('Vector 3: 1921 Peace Dollar with condition parenthetical stripped and grader appended', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '1921 Peace Dollar (Uncirculated)',
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '1921 Peace Dollar PCGS NGC CAC');
      expect(uri.queryParameters['_sacat'], '11116');
    });

    test('Vector 4: Currency item with malformed grader parenthetical replaced with PMG PCGS', () {
      final url = EpnService.buildSearchUrlFromQuery(
        r"$10 1928 Gold Certificate (PMG, 'PCGS Banknote')",
        itemType: 'currency',
        estimatedValue: 500.0,
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], r'$10 1928 Gold Certificate PMG PCGS');
      expect(uri.queryParameters['_sacat'], '11116');
    });

    test('Vector 5: 1916-D Mercury Dime Fine key date appends PCGS NGC CAC', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '1916-D Mercury Dime Fine',
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '1916-D Mercury Dime Fine PCGS NGC CAC');
      expect(uri.queryParameters['_sacat'], '11116');
    });

    test('Vector 6: 2026 Morgan Silver Dollar (Proof) non-key date strips proof parenthetical', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '2026 Morgan Silver Dollar (Proof)',
        estimatedValue: 95.0,
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '2026 Morgan Silver Dollar');
      expect(uri.queryParameters['_sacat'], '11116');
    });

    test('Vector 7: 1893-S Morgan Silver Dollar Raw key date appends PCGS NGC CAC', () {
      final url = EpnService.buildSearchUrlFromQuery(
        '1893-S Morgan Silver Dollar Raw',
      );
      final uri = Uri.parse(url);
      expect(uri.queryParameters['_nkw'], '1893-S Morgan Silver Dollar Raw PCGS NGC CAC');
      expect(uri.queryParameters['_sacat'], '11116');
    });
  });
}
