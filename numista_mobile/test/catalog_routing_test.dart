import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/main.dart';

void main() {
  group('resolveCatalogRoute (F1 Routing Tests)', () {
    test('direct path /catalog', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/catalog'));
      expect(info.isCatalog, isTrue);
      expect(info.initialNacCode, isNull);
    });

    test('direct path with NAC code /catalog/NAC1.123', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/catalog/NAC1.123'));
      expect(info.isCatalog, isTrue);
      expect(info.initialNacCode, equals('NAC1.123'));
    });

    test('hash fragment #/catalog', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/#/catalog'));
      expect(info.isCatalog, isTrue);
      expect(info.initialNacCode, isNull);
    });

    test('hash fragment with NAC code #/catalog/NAC1.123', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/#/catalog/NAC1.123'));
      expect(info.isCatalog, isTrue);
      expect(info.initialNacCode, equals('NAC1.123'));
    });

    test('hash fragment with query param #/catalog?item=NAC1.123', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/#/catalog?item=NAC1.123'));
      expect(info.isCatalog, isTrue);
      expect(info.initialNacCode, equals('NAC1.123'));
    });

    test('non-catalog route #/claim', () {
      final info = resolveCatalogRoute(Uri.parse('https://example.com/#/claim'));
      expect(info.isCatalog, isFalse);
    });
  });
}
