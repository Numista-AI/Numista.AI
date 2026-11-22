import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/services/analytics_calculator.dart';

void main() {
  group('AnalyticsCalculator', () {
    test('parseAiValue rejects zero sentinels and Pending', () {
      expect(AnalyticsCalculator.parseAiValue('\$0.00'), 0.0);
      expect(AnalyticsCalculator.parseAiValue('0'), 0.0);
      expect(AnalyticsCalculator.parseAiValue('Pending'), 0.0);
      expect(AnalyticsCalculator.parseAiValue('\$45.00 - \$60.00'), 45.0);
    });

    test('plated/base-metal guard prevents melt floor bump', () {
      final plated = CoinModel(
        id: 'p1',
        year: '2020',
        denomination: 'Dollar',
        metalContent: 'Silver Plated',
        aiEstimatedValue: '\$10.00',
      );
      final summary =
          AnalyticsCalculator.buildSummary([plated], advancedMode: true);
      expect(summary.totalFineAgOz, 0.0);
      final sim = AnalyticsCalculator.simulateSpot(
        summary,
        simGold: 3500.0,
        simSilver: 100.0,
      );
      expect(sim.simulatedTotal, 10.0);
    });

    test('set double-counting guard skips parent set when children exist', () {
      final parentSet = CoinModel(
        id: 'set_1',
        isSet: true,
        programSeries: 'Proof Set',
        cpgRetail: 100.0,
      );
      final child = CoinModel(
        id: 'child_1',
        parentSetId: 'set_1',
        denomination: 'Half Dollar',
        metalContent: '90% Silver',
        cpgRetail: 60.0,
      );
      final summary = AnalyticsCalculator.buildSummary(
        [parentSet, child],
        advancedMode: true,
      );
      expect(summary.totalCoins, 1);
      expect(summary.totalPrimaryValue, 60.0);
    });

    test('canonical duplicate grouping merges 25C and Quarter Dollar', () {
      final c1 = CoinModel(
        id: 'q1',
        country: 'USA',
        year: '1932',
        mintMark: 'P',
        denomination: '25C',
        cpgRetail: 25.0,
      );
      final c2 = CoinModel(
        id: 'q2',
        country: 'USA',
        year: '1932',
        mintMark: 'P',
        denomination: 'Quarter Dollar',
        cpgRetail: 35.0,
      );
      final summary =
          AnalyticsCalculator.buildSummary([c1, c2], advancedMode: true);
      expect(summary.duplicateGroups.length, 1);
      expect(summary.duplicateGroups.first.looseCount, 2);
      expect(summary.totalDuplicateRecoverable, 30.0);
    });

    test('Net Liquidation applies 13% default fee and 95% bullion melt floor',
        () {
      final bullion = CoinModel(
        id: 'b1',
        denomination: 'Dollar',
        programSeries: 'American Silver Eagle',
        metalContent: '999 Fine Silver',
        cpgRetail: 30.0,
        meltValue: '\$30.00',
      );
      final summary =
          AnalyticsCalculator.buildSummary([bullion], advancedMode: true);
      // 30 * (1 - 0.13) = 26.10, floored at 0.95 * 30 = 28.50
      expect(summary.totalNetLiquidation, closeTo(28.50, 0.01));
    });

    test('CSV export includes header and escapes commas', () {
      final coin = CoinModel(
        id: 'c1',
        year: '1921',
        mintMark: 'P',
        denomination: 'Dollar',
        programSeries: 'Morgan, Peace',
        cpgRetail: 50.0,
      );
      final summary =
          AnalyticsCalculator.buildSummary([coin], advancedMode: true);
      final csv = AnalyticsCalculator.exportSummaryCsv(summary);
      expect(csv, contains('Year,Mint,Denomination'));
      expect(csv, contains('"Morgan, Peace"'));
    });
  });
}
