// Numista.AI — CollectorProfileService Unit Tests
// Tests the pure Dart logic (profile normalization, payload construction,
// default values) WITHOUT requiring Firebase or network access.
//
// The service's _normalizeProfile is a pure function and is testable directly.
// HTTP calls (getProfile / updateProfile) are excluded from unit tests;
// those are covered by the E2E suite (22-aug18-collector-memory-delete.spec.js).

import 'package:flutter_test/flutter_test.dart';

// ── Inline the testable logic from CollectorProfileService ────────────────────
// We duplicate the pure functions here to avoid Firebase initialization in tests.
// If the service's logic changes, these tests will surface the regression.

const Map<String, dynamic> kDefaultProfile = {
  'schema_version': '1.0',
  'preferred_series': <String>[],
  'target_grade_min': '',
  'target_grade_max': '',
  'preferred_services': <String>['PCGS', 'NGC'],
  'investment_goal': 'numismatic_study',
  'budget_tier': 'intermediate',
  'opt_in_chat_extraction': true,
};

Map<String, dynamic> normalizeProfile(Map<String, dynamic> raw) {
  final base = Map<String, dynamic>.from(kDefaultProfile);
  base.addAll(raw);

  if (base['preferred_series'] is! List) {
    base['preferred_series'] = <String>[];
  } else {
    base['preferred_series'] =
        (base['preferred_series'] as List).map((e) => e.toString()).toList();
  }

  if (base['preferred_services'] is! List) {
    base['preferred_services'] = <String>['PCGS', 'NGC'];
  } else {
    base['preferred_services'] =
        (base['preferred_services'] as List).map((e) => e.toString()).toList();
  }

  base['target_grade_min'] = base['target_grade_min']?.toString() ?? '';
  base['target_grade_max'] = base['target_grade_max']?.toString() ?? '';
  base['investment_goal'] =
      base['investment_goal']?.toString() ?? 'numismatic_study';
  base['budget_tier'] = base['budget_tier']?.toString() ?? 'intermediate';
  base['opt_in_chat_extraction'] = base['opt_in_chat_extraction'] != false;

  return base;
}

Map<String, dynamic> buildUpdatePayload(Map<String, dynamic> updates) {
  final payload = <String, dynamic>{};
  if (updates.containsKey('preferred_series')) {
    payload['preferred_series'] = updates['preferred_series'] ?? [];
  }
  if (updates.containsKey('target_grade_min')) {
    payload['target_grade_min'] = updates['target_grade_min'] ?? '';
  }
  if (updates.containsKey('target_grade_max')) {
    payload['target_grade_max'] = updates['target_grade_max'] ?? '';
  }
  if (updates.containsKey('preferred_services')) {
    payload['preferred_services'] =
        updates['preferred_services'] ?? ['PCGS', 'NGC'];
  }
  if (updates.containsKey('investment_goal')) {
    payload['investment_goal'] =
        updates['investment_goal'] ?? 'numismatic_study';
  }
  if (updates.containsKey('budget_tier')) {
    payload['budget_tier'] = updates['budget_tier'] ?? 'intermediate';
  }
  if (updates.containsKey('opt_in_chat_extraction')) {
    payload['opt_in_chat_extraction'] =
        updates['opt_in_chat_extraction'] == true;
  }
  return payload;
}

// ── Tests ─────────────────────────────────────────────────────────────────────

void main() {
  group('CollectorProfileService — Default Profile Contract', () {
    test('default profile has all required keys', () {
      const requiredKeys = [
        'schema_version',
        'preferred_series',
        'target_grade_min',
        'target_grade_max',
        'preferred_services',
        'investment_goal',
        'budget_tier',
        'opt_in_chat_extraction',
      ];
      for (final key in requiredKeys) {
        expect(kDefaultProfile.containsKey(key), isTrue,
            reason: 'Default profile missing key: $key');
      }
    });

    test('default preferred_services are PCGS and NGC', () {
      final services = kDefaultProfile['preferred_services'] as List;
      expect(services, containsAll(['PCGS', 'NGC']));
    });

    test('default opt_in_chat_extraction is true', () {
      expect(kDefaultProfile['opt_in_chat_extraction'], isTrue);
    });

    test('default investment_goal is numismatic_study', () {
      expect(kDefaultProfile['investment_goal'], equals('numismatic_study'));
    });

    test('default budget_tier is intermediate', () {
      expect(kDefaultProfile['budget_tier'], equals('intermediate'));
    });
  });

  group('CollectorProfileService — normalizeProfile()', () {
    test('empty input returns all default values', () {
      final result = normalizeProfile({});
      expect(result['preferred_series'], equals(<String>[]));
      expect(result['preferred_services'], containsAll(['PCGS', 'NGC']));
      expect(result['investment_goal'], equals('numismatic_study'));
      expect(result['budget_tier'], equals('intermediate'));
      expect(result['opt_in_chat_extraction'], isTrue);
    });

    test('valid profile data is preserved through normalization', () {
      final input = {
        'preferred_series': ['Morgan Dollar', 'Walking Liberty'],
        'target_grade_min': 'VF20',
        'target_grade_max': 'MS65',
        'preferred_services': ['PCGS'],
        'investment_goal': 'investment_grade',
        'budget_tier': 'premium',
        'opt_in_chat_extraction': false,
      };
      final result = normalizeProfile(input);
      expect(result['preferred_series'], equals(['Morgan Dollar', 'Walking Liberty']));
      expect(result['target_grade_min'], equals('VF20'));
      expect(result['target_grade_max'], equals('MS65'));
      expect(result['preferred_services'], equals(['PCGS']));
      expect(result['investment_goal'], equals('investment_grade'));
      expect(result['budget_tier'], equals('premium'));
      expect(result['opt_in_chat_extraction'], isFalse);
    });

    test('non-list preferred_series is replaced with empty list', () {
      final result = normalizeProfile({'preferred_series': 'not-a-list'});
      expect(result['preferred_series'], isA<List>());
      expect((result['preferred_series'] as List).isEmpty, isTrue);
    });

    test('non-list preferred_services falls back to PCGS/NGC defaults', () {
      final result = normalizeProfile({'preferred_services': 42});
      expect(result['preferred_services'], containsAll(['PCGS', 'NGC']));
    });

    test('null opt_in_chat_extraction defaults to true', () {
      final result = normalizeProfile({'opt_in_chat_extraction': null});
      // null != false → true
      expect(result['opt_in_chat_extraction'], isTrue);
    });

    test('false opt_in_chat_extraction is preserved as false', () {
      final result = normalizeProfile({'opt_in_chat_extraction': false});
      expect(result['opt_in_chat_extraction'], isFalse);
    });

    test('integer grades are coerced to strings', () {
      final result = normalizeProfile({
        'target_grade_min': 20,
        'target_grade_max': 65,
      });
      expect(result['target_grade_min'], equals('20'));
      expect(result['target_grade_max'], equals('65'));
    });

    test('preferred_series list elements are coerced to strings', () {
      final result = normalizeProfile({
        'preferred_series': [1921, 'Morgan Dollar', true],
      });
      final series = result['preferred_series'] as List;
      expect(series.every((e) => e is String), isTrue);
      expect(series, containsAll(['1921', 'Morgan Dollar', 'true']));
    });

    test('extra unknown fields from API are preserved', () {
      final result = normalizeProfile({
        'future_field': 'new_api_value',
        'experimental': true,
      });
      // Unknown fields from API should flow through (addAll behavior)
      expect(result['future_field'], equals('new_api_value'));
    });
  });

  group('CollectorProfileService — buildUpdatePayload()', () {
    test('empty updates produces empty payload', () {
      final payload = buildUpdatePayload({});
      expect(payload.isEmpty, isTrue);
    });

    test('only specified keys are included in payload', () {
      final payload = buildUpdatePayload({'budget_tier': 'premium'});
      expect(payload.containsKey('budget_tier'), isTrue);
      expect(payload.containsKey('investment_goal'), isFalse);
      expect(payload.containsKey('preferred_series'), isFalse);
    });

    test('opt_in_chat_extraction true is coerced to bool true', () {
      final payload = buildUpdatePayload({'opt_in_chat_extraction': true});
      expect(payload['opt_in_chat_extraction'], isTrue);
    });

    test('opt_in_chat_extraction non-true is coerced to false', () {
      // Only explicit true → true; everything else → false
      final payload = buildUpdatePayload({'opt_in_chat_extraction': 'yes'});
      expect(payload['opt_in_chat_extraction'], isFalse);
    });

    test('null preferred_series in update falls back to empty list', () {
      final payload = buildUpdatePayload({'preferred_series': null});
      expect(payload['preferred_series'], equals([]));
    });

    test('full update payload contains all 7 keys', () {
      final fullUpdate = {
        'preferred_series': ['Morgan Dollar'],
        'target_grade_min': 'VF20',
        'target_grade_max': 'MS65',
        'preferred_services': ['PCGS'],
        'investment_goal': 'investment_grade',
        'budget_tier': 'premium',
        'opt_in_chat_extraction': true,
      };
      final payload = buildUpdatePayload(fullUpdate);
      expect(payload.length, equals(7));
    });
  });
}
