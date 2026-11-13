import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/screens/review_hub_screen.dart';

void main() {
  group('formatCurrency - Commercial Half-Up String Rounding Contract', () {
    test('rounds 64.97 / 2 (32.485) half-up to exactly 32.49', () {
      expect(ReviewHubScreen.formatCurrency(64.97 / 2), equals('32.49'));
    });

    test('rounds 61.00 / 25 (2.44) to exactly 2.44', () {
      expect(ReviewHubScreen.formatCurrency(61.00 / 25), equals('2.44'));
    });

    test('rounds 169.00 / 2 (84.50) to exactly 84.50', () {
      expect(ReviewHubScreen.formatCurrency(169.00 / 2), equals('84.50'));
    });

    test('rounds 100.005 half-up to exactly 100.01', () {
      expect(ReviewHubScreen.formatCurrency(100.005), equals('100.01'));
    });

    test('handles negative amount -64.97 / 2 (-32.485) as -32.49', () {
      expect(ReviewHubScreen.formatCurrency(-64.97 / 2), equals('-32.49'));
    });

    test('formats zero as 0.00', () {
      expect(ReviewHubScreen.formatCurrency(0), equals('0.00'));
    });

    test('formats standard integer and decimal values', () {
      expect(ReviewHubScreen.formatCurrency(25), equals('25.00'));
      expect(ReviewHubScreen.formatCurrency(19.99), equals('19.99'));
      expect(ReviewHubScreen.formatCurrency(19.994), equals('19.99'));
      expect(ReviewHubScreen.formatCurrency(19.995), equals('20.00'));
    });
  });
}
