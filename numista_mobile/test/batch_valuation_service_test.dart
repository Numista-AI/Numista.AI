import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/batch_valuation_service.dart';

void main() {
  group('BatchValuationService — Bug A1: Collection Routing (Coins vs Currency)', () {
    test('currency task routes to currencyPath and never to coinsPath', () {
      final currencyTask = BatchValuationService.buildCurrencyTask('note-123', {
        'Year': '1928',
        'Denomination': r'$20',
        'Condition': 'VF-30',
        'Country': 'USA',
        'Description': '1928 Gold Certificate',
        'Series/Issuer': 'Federal Reserve',
      });

      expect(currencyTask, isNotNull);
      expect(currencyTask!.collection, equals('currency'));
      expect(currencyTask.itemType, equals('banknote'));
      expect(currencyTask.docId, equals('note-123'));

      final targetCollection = BatchValuationService.collectionPathForTask(
        currencyTask.collection,
        coinsPathOverride: 'users/collector@numista.ai/coins',
        currencyPathOverride: 'users/collector@numista.ai/currency',
      );
      expect(targetCollection, equals('users/collector@numista.ai/currency'));
    });

    test('coin and set tasks route to coinsPath', () {
      final coinTask = BatchValuationService.buildCoinTask('coin-456', {
        'Year': '1881',
        'Mint Mark': 'S',
        'Denomination': r'$1',
        'Condition': 'MS-65',
        'Program/Series': 'Morgan Dollar',
        'Metal Content': '90% Silver',
      });

      expect(coinTask, isNotNull);
      expect(coinTask!.collection, equals('coins'));
      expect(coinTask.itemType, equals('coin'));
      expect(coinTask.name, equals(r'1881-S $1'));

      final targetCollection = BatchValuationService.collectionPathForTask(
        coinTask.collection,
        coinsPathOverride: 'users/collector@numista.ai/coins',
        currencyPathOverride: 'users/collector@numista.ai/currency',
      );
      expect(targetCollection, equals('users/collector@numista.ai/coins'));
    });

    test('already-valued coins and banknotes are skipped (return null)', () {
      expect(
        BatchValuationService.buildCoinTask('coin-1', {'ai_value_status': 'valued'}),
        isNull,
      );
      expect(
        BatchValuationService.buildCurrencyTask('note-1', {'ai_value_status': 'valued'}),
        isNull,
      );
    });
  });

  group('BatchValuationService — Bug A2: Golden Schema AI Estimated Value Sync', () {
    test('buildValuationPayload populates both ai_estimated_value and AI Estimated Value', () {
      final fixedTime = DateTime.utc(2026, 10, 24, 12, 0, 0);
      final payload = BatchValuationService.buildValuationPayload(
        {
          'ai_value_status': 'valued',
          'estimated_value': r'$145.00',
          'numeric_median': 145,
          'low': 130.0,
          'high': 160.0,
          'source': 'text_estimator',
          'basis': 'PCGS MS-65 recent comps',
          'confidence': 'HIGH',
          'needs_photo': false,
        },
        now: fixedTime,
      );

      expect(payload['ai_value_status'], equals('valued'));
      expect(payload['ai_estimated_value'], equals(r'$145.00'));
      expect(payload['AI Estimated Value'], equals(r'$145.00'));
      expect(payload['estimated_value'], equals(145.0));
      expect(payload['ai_value_low'], equals(130.0));
      expect(payload['ai_value_high'], equals(160.0));
      expect(payload['ai_value_confidence'], equals('HIGH'));
      expect(payload['ai_needs_photo'], isFalse);
      expect(payload['ai_value_as_of'], equals('2026-10-24T12:00:00.000Z'));
    });

    test('buildValuationPayload defaults to Pending when estimated_value is absent', () {
      final payload = BatchValuationService.buildValuationPayload({});
      expect(payload['ai_value_status'], equals('valued'));
      expect(payload['ai_estimated_value'], equals('Pending'));
      expect(payload['AI Estimated Value'], equals('Pending'));
      expect(payload.containsKey('estimated_value'), isFalse);
    });
  });

  group('BatchValuationService — Bug A3: Resume Progress Math Integrity', () {
    test('fresh start initializes completed=0 and total=pendingTaskCount', () {
      final progress = BatchValuationService.computeInitialRunProgress(
        previous: const BatchValuationProgress(),
        pendingTaskCount: 50,
        totalCollectionCount: 50,
      );

      expect(progress.total, equals(50));
      expect(progress.completed, equals(0));
      expect(progress.failed, equals(0));
      expect(progress.isRunning, isTrue);
      expect(progress.isPaused, isFalse);
      expect(progress.pct, equals(0.0));
      expect(progress.label, equals('0 of 50 estimated'));
    });

    test('resuming paused run reconstructs total = completed + pendingTaskCount (no overflow)', () {
      // Simulate 60 valued + 2 failed out of 100 before pause -> 40 unvalued tasks remain in Firestore
      const pausedState = BatchValuationProgress(
        total: 100,
        completed: 60,
        failed: 2,
        isRunning: false,
        isPaused: true,
      );

      final resumed = BatchValuationService.computeInitialRunProgress(
        previous: pausedState,
        pendingTaskCount: 40,
        totalCollectionCount: 100,
      );

      expect(resumed.total, equals(100));
      expect(resumed.completed, equals(60));
      expect(resumed.failed, equals(0));
      expect(resumed.remaining, equals(40));
      expect(resumed.pct, closeTo(0.60, 1e-6));
      expect(resumed.pct, lessThanOrEqualTo(1.0));
      expect(resumed.label, equals('60 of 100 estimated'));
    });

    test('starting a new batch after prior batch finished resets completed to 0', () {
      const finishedState = BatchValuationProgress(
        total: 100,
        completed: 100,
        failed: 0,
        isRunning: false,
        isPaused: false,
      );

      final nextBatch = BatchValuationService.computeInitialRunProgress(
        previous: finishedState,
        pendingTaskCount: 5,
        totalCollectionCount: 105,
      );

      expect(nextBatch.total, equals(5));
      expect(nextBatch.completed, equals(0));
      expect(nextBatch.failed, equals(0));
      expect(nextBatch.label, equals('0 of 5 estimated'));
    });

    test('zero pending tasks marks collection as fully estimated', () {
      final done = BatchValuationService.computeInitialRunProgress(
        previous: const BatchValuationProgress(),
        pendingTaskCount: 0,
        totalCollectionCount: 120,
      );

      expect(done.total, equals(120));
      expect(done.completed, equals(120));
      expect(done.isRunning, isFalse);
      expect(done.isDone, isTrue);
      expect(done.label, equals('All 120 estimated'));
    });
  });
}
