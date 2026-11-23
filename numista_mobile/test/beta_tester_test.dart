import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/auth_service.dart';

void main() {
  group('AuthService isBetaFor Pure Helper', () {
    test('14 Dec 2026 evening UTC (pre-cutoff) -> true', () {
      final dt = DateTime.utc(2026, 12, 14, 23, 59, 59);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isTrue);
    });

    test('1 second before cutoff (14 Dec 2026 11:59:59 PM ET) -> true', () {
      final dt = DateTime.utc(2026, 12, 15, 4, 59, 59);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isTrue);
    });

    test('exactly at cutoff (15 Dec 2026 12:00:00 AM ET) -> false', () {
      final dt = DateTime.utc(2026, 12, 15, 5, 0, 0);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isFalse);
    });

    test('isAnonymous: true -> false', () {
      final dt = DateTime.utc(2026, 10, 1);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: true), isFalse);
    });

    test('creationUtc: null -> false', () {
      expect(AuthService.isBetaFor(creationUtc: null, isAnonymous: false), isFalse);
    });

    test('early tester -> true', () {
      final dt = DateTime.utc(2026, 10, 1);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isTrue);
    });

    test('post-cutoff -> false', () {
      final dt = DateTime.utc(2027, 1, 1);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isFalse);
    });
  });
}
