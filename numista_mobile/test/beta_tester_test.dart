import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/auth_service.dart';

void main() {
  group('AuthService isBetaFor Pure Helper', () {
    test('1 second before cutoff -> true', () {
      final dt = DateTime.utc(2026, 11, 26, 4, 59, 59);
      expect(AuthService.isBetaFor(creationUtc: dt, isAnonymous: false), isTrue);
    });

    test('exactly at cutoff -> false', () {
      final dt = DateTime.utc(2026, 11, 26, 5, 0, 0);
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
