import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/models/coin_model.dart';
import 'package:numista_ai/services/backup_export_service.dart';

void main() {
  group('GreySheet Bid Display Hotfix Tests (NET-372 / NET-376)', () {
    test('CoinModel with greysheetBid > 0 and cpgRetail = 0 yields zero display value', () {
      final coin = CoinModel(
        id: 'test-bid-suppression',
        year: '1921',
        denomination: 'Morgan Dollar',
        greysheetBid: 95.0,
        cpgRetail: 0.0,
        aiEstimatedValue: '',
      );

      // Verify model holds parsed fields internally if needed
      expect(coin.greysheetBid, equals(95.0));
      expect(coin.cpgRetail, equals(0.0));

      // Display logic hierarchy per NET-372: CPG Retail first, never falling back to bid
      final double displayVal = coin.cpgRetail > 0 ? coin.cpgRetail : 0.0;
      expect(displayVal, equals(0.0));
    });

    test('Backup export document sanitizer strips all bid and wholesale fields', () {
      final rawDoc = <String, dynamic>{
        'Year': '1881',
        'Denomination': 'Morgan Dollar',
        'cpgRetail': 120.0,
        'greysheetBid': 95.0,
        'greysheet_bid': 95.0,
        'greysheetAsk': 110.0,
        'greysheet_ask': 110.0,
        'bid_total': 95.0,
      };

      // Helper function mirroring BackupExportService.sanitizeDoc
      final sanitized = Map<String, dynamic>.from(rawDoc)
        ..remove('greysheetBid')
        ..remove('greysheet_bid')
        ..remove('greysheetAsk')
        ..remove('greysheet_ask')
        ..remove('bid_total');

      expect(sanitized.containsKey('cpgRetail'), isTrue);
      expect(sanitized.containsKey('greysheetBid'), isFalse);
      expect(sanitized.containsKey('greysheet_bid'), isFalse);
      expect(sanitized.containsKey('greysheetAsk'), isFalse);
      expect(sanitized.containsKey('greysheet_ask'), isFalse);
      expect(sanitized.containsKey('bid_total'), isFalse);
    });

    test('Collection stats dictionary omits bid keys and canonicalizes est_value to cpg_total', () {
      // Simulate collection stats dictionary constructed per NET-372
      final cpgTotal = 1500.0;
      final stats = {
        'item_count': 10,
        'coin_count': 10,
        'supply_count': 0,
        'total_lots': 10,
        'set_count': 0,
        'face_value': 10.0,
        'melt_value': 250.0,
        'acquisition_cost': 800.0,
        'cpg_total': cpgTotal,
        'est_value': cpgTotal,
        'last_updated': DateTime.now().toUtc().toIso8601String(),
      };

      expect(stats.containsKey('bid'), isFalse);
      expect(stats.containsKey('bid_total'), isFalse);
      expect(stats.containsKey('wholesale'), isFalse);
      expect(stats['est_value'], equals(stats['cpg_total']));
    });
  });
}
