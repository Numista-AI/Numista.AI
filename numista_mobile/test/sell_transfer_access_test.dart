import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/guest_seed_service.dart';
import 'package:numista_ai/utils/sell_transfer_access.dart';

void main() {
  tearDown(() => GuestSeedService.setDemoActiveForTest(false));

  test('the demo message is the exact approved string', () {
    expect(kSellTransferDemoCta, 'Create a free account to sell or transfer items.');
  });

  group('canSellOrTransferFor (pure rule)', () {
    test('Browse Demo can never sell or transfer', () {
      expect(canSellOrTransferFor(browseDemo: true, signedIn: true, anonymous: false), isFalse);
      expect(canSellOrTransferFor(browseDemo: true, signedIn: false, anonymous: false), isFalse);
    });
    test('no user, or an anonymous user, cannot', () {
      expect(canSellOrTransferFor(browseDemo: false, signedIn: false, anonymous: false), isFalse);
      expect(canSellOrTransferFor(browseDemo: false, signedIn: true, anonymous: true), isFalse);
    });
    test('a registered, signed-in user can', () {
      expect(canSellOrTransferFor(browseDemo: false, signedIn: true, anonymous: false), isTrue);
    });
  });

  test('N1: Browse Demo (setDemoActiveForTest) is evaluated first and never touches Firebase', () {
    GuestSeedService.setDemoActiveForTest(true);
    expect(GuestSeedService.isBrowseDemoMode, isTrue);
    // FirebaseAuth.instance would throw here (Firebase is not initialised in a unit test).
    // Returning false without an exception proves the demo check short-circuits before Firebase.
    expect(canSellOrTransfer(), isFalse);
  });
}