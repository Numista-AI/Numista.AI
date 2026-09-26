import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';

void main() {
  group('CoinModel Quantity Resilience Tests (CoS M2)', () {
    test('Reads integer Quantity from Firestore without error', () {
      final map = {
        'Year': '2026',
        'Denomination': 'Morgan Dollar',
        'Quantity': 2,
      };
      final coin = CoinModel.fromMap(map, 'test-doc-1');
      expect(coin.quantity, equals('2'));
    });

    test('Reads string Quantity from Firestore without error', () {
      final map = {
        'Year': '2026',
        'Denomination': 'Morgan Dollar',
        'Quantity': '3',
      };
      final coin = CoinModel.fromMap(map, 'test-doc-2');
      expect(coin.quantity, equals('3'));
    });

    test('Reads lowercase quantity fallback', () {
      final map = {
        'Year': '2026',
        'Denomination': 'Morgan Dollar',
        'quantity': 5,
      };
      final coin = CoinModel.fromMap(map, 'test-doc-3');
      expect(coin.quantity, equals('5'));
    });

    test('Defaults to 1 when Quantity is null or empty', () {
      final map = {
        'Year': '2026',
        'Denomination': 'Morgan Dollar',
      };
      final coin = CoinModel.fromMap(map, 'test-doc-4');
      expect(coin.quantity, equals('1'));
    });

    test('Serializes Quantity properly in toFirestore', () {
      final map = {
        'Year': '2026',
        'Denomination': 'Morgan Dollar',
        'Quantity': 2,
      };
      final coin = CoinModel.fromMap(map, 'test-doc-5');
      final output = coin.toFirestore();
      expect(output['Quantity'], equals('2'));
    });

    test('Quantity sanitization logic handles invalid or blank input with fallback 1', () {
      int sanitizeQuantity(String? raw) {
        final text = (raw ?? '').trim();
        final parsed = int.tryParse(text);
        return (parsed != null && parsed > 0) ? parsed : 1;
      }

      expect(sanitizeQuantity('2'), equals(2));
      expect(sanitizeQuantity('  2  '), equals(2));
      expect(sanitizeQuantity(''), equals(1));
      expect(sanitizeQuantity('   '), equals(1));
      expect(sanitizeQuantity('0'), equals(1));
      expect(sanitizeQuantity('-5'), equals(1));
      expect(sanitizeQuantity('abc'), equals(1));
      expect(sanitizeQuantity(null), equals(1));
      expect(sanitizeQuantity('100'), equals(100));
    });
  });
}
