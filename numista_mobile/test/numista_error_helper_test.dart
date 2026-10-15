import 'package:firebase_core/firebase_core.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/utils/numista_error_helper.dart';

void main() {
  group('NumistaErrorHelper', () {
    test('XMLHttpRequest → server no answer', () {
      final msg = NumistaErrorHelper.toUserFriendly('XMLHttpRequest error');
      expect(msg, contains('server'));
      expect(msg, isNot(contains('internet')));
    });

    test('Failed to fetch → server no answer', () {
      final msg = NumistaErrorHelper.toUserFriendly('Failed to fetch');
      expect(msg, contains('server'));
    });

    test('SocketException → offline', () {
      final msg = NumistaErrorHelper.toUserFriendly('SocketException: Connection refused');
      expect(msg, contains('internet'));
    });

    test('ClientException typed → server no answer', () {
      // Use string path since http.ClientException needs a real import
      final msg = NumistaErrorHelper.toUserFriendly('ClientException: Failed');
      expect(msg, contains('server'));
    });

    test('statusCode 401 → sign in', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 401);
      expect(msg, contains('sign'));
    });

    test('statusCode 403 → access denied', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 403);
      expect(msg, contains('permission'));
    });

    test('statusCode 500 → server error', () {
      final msg = NumistaErrorHelper.toUserFriendly(null, statusCode: 500);
      expect(msg, contains('unavailable'));
    });

    test('FirebaseException unavailable → server no answer', () {
      final msg = NumistaErrorHelper.toUserFriendly(
        FirebaseException(plugin: 'cloud_firestore', code: 'unavailable'),
      );
      expect(msg, contains('server'));
    });

    test('FirebaseException permission-denied → sign-in message', () {
      final msg = NumistaErrorHelper.toUserFriendly(
        FirebaseException(plugin: 'cloud_firestore', code: 'permission-denied'),
      );
      expect(msg, contains('sign in'));
    });

    test('toUserFriendlyWithContext names the action', () {
      final msg = NumistaErrorHelper.toUserFriendlyWithContext(
          'SocketException: Failed', action: 'save your coin');
      expect(msg, startsWith("Couldn't save your coin"));
      expect(msg, contains('internet'));
    });
  });
}
