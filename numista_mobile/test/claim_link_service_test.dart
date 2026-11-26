import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/claim_link_service.dart';

void main() {
  setUp(ClaimLinkService.clearForTest);

  test('captures the token from a hash-fragment claim link', () {
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/#/claim?t=abc_DEF-123')), isTrue);
    expect(ClaimLinkService.hasPendingToken, isTrue);
    expect(ClaimLinkService.takePendingToken(), 'abc_DEF-123');
  });

  test('the token is consumed exactly once', () {
    ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/#/claim?t=once'));
    expect(ClaimLinkService.takePendingToken(), 'once');
    expect(ClaimLinkService.takePendingToken(), isNull);
    expect(ClaimLinkService.hasPendingToken, isFalse);
  });

  test('ignores links that are not claim links or carry no token', () {
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/')), isFalse);
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/#/wishlist?t=zzz')), isFalse);
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/#/claim')), isFalse);
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/#/claim?t=')), isFalse);
    expect(ClaimLinkService.hasPendingToken, isFalse);
  });

  test('a token in the query string (not the fragment) is ignored: only the fragment is trusted', () {
    expect(ClaimLinkService.captureFromUri(Uri.parse('https://numista.ai/claim?t=nope')), isFalse);
  });
}