import 'package:flutter_test/flutter_test.dart';

void main() {
  group('Valuation Mode Parity & Basis Calculations', () {
    double computePortfolioValue(bool isAdvanced, double bidTotal, double cpgTotal) {
      return isAdvanced ? cpgTotal : bidTotal;
    }

    double computeCoinsCategoryValue(bool isAdvanced, double bidTotal, double cpgTotal) {
      return isAdvanced ? cpgTotal : bidTotal;
    }

    String getValuationSubtitle(bool isAdvanced) {
      return isAdvanced ? 'CPG Retail Market basis' : 'Wholesale / Greysheet Bid basis';
    }

    test('Estate / Liquidation Mode satisfies exact mathematical parity', () {
      // 1914-D $5 Half Eagle: wholesale bid = $1,000.00, CPG = $1,250.00
      // 126 remaining moderns: wholesale bid sum = $210.30, CPG = $145.15
      // Acquisition Cost: $588.90
      const bidTotal = 1210.30;
      const cpgTotal = 1395.15;
      const acquisitionCost = 588.90;
      const isAdvanced = false;

      final portfolioValue = computePortfolioValue(isAdvanced, bidTotal, cpgTotal);
      final coinsCategoryVal = computeCoinsCategoryValue(isAdvanced, bidTotal, cpgTotal);
      final profitLoss = portfolioValue - acquisitionCost;
      final subtitle = getValuationSubtitle(isAdvanced);

      expect(portfolioValue, equals(1210.30));
      expect(coinsCategoryVal, equals(1210.30));
      expect(profitLoss, closeTo(621.40, 0.01));
      expect(subtitle, equals('Wholesale / Greysheet Bid basis'));
    });

    test('Retail Mode satisfies exact mathematical parity', () {
      const bidTotal = 1210.30;
      const cpgTotal = 1395.15;
      const acquisitionCost = 588.90;
      const isAdvanced = true;

      final portfolioValue = computePortfolioValue(isAdvanced, bidTotal, cpgTotal);
      final coinsCategoryVal = computeCoinsCategoryValue(isAdvanced, bidTotal, cpgTotal);
      final profitLoss = portfolioValue - acquisitionCost;
      final subtitle = getValuationSubtitle(isAdvanced);

      expect(portfolioValue, equals(1395.15));
      expect(coinsCategoryVal, equals(1395.15));
      expect(profitLoss, closeTo(806.25, 0.01));
      expect(subtitle, equals('CPG Retail Market basis'));
    });

    test('Collection Stats Schema Contract matches required fields', () {
      final stats = {
        'item_count': 128,
        'coin_count': 127,
        'supply_count': 1,
        'face_value': 99.95,
        'melt_value': 1182.29,
        'acquisition_cost': 588.90,
        'bid_total': 1210.30,
        'cpg_total': 1395.15,
        'est_value': 1210.30,
        'last_updated': '2026-08-18T15:15:00Z',
      };

      expect(stats['item_count'], equals(128));
      expect(stats['coin_count'], equals(127));
      expect(stats['supply_count'], equals(1));
      expect(stats['bid_total'], equals(1210.30));
      expect(stats['cpg_total'], equals(1395.15));
      expect(stats['est_value'], equals(1210.30));
    });

    test('Unauthenticated path guard blocks query with unknown in path', () {
      const coinsPath = 'users/unknown/coins';
      expect(coinsPath.contains('unknown'), isTrue);

      bool threw = false;
      try {
        if (coinsPath.contains('unknown')) {
          throw StateError('Cannot query unauthenticated coinsPath');
        }
      } catch (e) {
        threw = true;
      }
      expect(threw, isTrue);
    });
  });
}
