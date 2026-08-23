import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/guest_seed_service.dart';

/// Unit tests for GuestSeedService demo-flag lifecycle.
///
/// Uses [GuestSeedService.setDemoActiveForTest] to set the static flag
/// without requiring rootBundle (Flutter asset loading) infrastructure.
/// The [GuestSeedService.demoCoinCache] public getter is directly accessible.
void main() {
  setUp(() => GuestSeedService.setDemoActiveForTest(false));

  test('1: deactivateBrowseDemo is idempotent', () {
    GuestSeedService.setDemoActiveForTest(true);
    GuestSeedService.deactivateBrowseDemo();
    GuestSeedService.deactivateBrowseDemo();
    GuestSeedService.deactivateBrowseDemo();
    expect(GuestSeedService.isBrowseDemoMode, isFalse);
    expect(GuestSeedService.demoCoinCache, isEmpty);
  });

  test('2: setDemoActiveForTest activates; deactivate clears both fields', () {
    GuestSeedService.setDemoActiveForTest(true);
    expect(GuestSeedService.isBrowseDemoMode, isTrue);
    GuestSeedService.deactivateBrowseDemo();
    expect(GuestSeedService.isBrowseDemoMode, isFalse);
    expect(GuestSeedService.demoCoinCache, isEmpty);
  });

  test('3: isBrowseDemoMode is a pure getter with no side effects', () {
    GuestSeedService.setDemoActiveForTest(true);
    final r1 = GuestSeedService.isBrowseDemoMode;
    final r2 = GuestSeedService.isBrowseDemoMode;
    final r3 = GuestSeedService.isBrowseDemoMode;
    expect(r1, isTrue);
    expect(r2, isTrue);
    expect(r3, isTrue);
    expect(GuestSeedService.isBrowseDemoMode, isTrue);
  });

  test('4: getDemoCoinsStream after deactivate emits empty snapshot', () async {
    // After deactivate, _demoCoinCache = [].
    // getDemoCoinsStream() builds from the cache.
    // Confirms demo JSON cannot leak into a real user session after clearance.
    GuestSeedService.deactivateBrowseDemo();
    final snap = await GuestSeedService.getDemoCoinsStream().first;
    expect(snap.docs, isEmpty,
        reason: 'getDemoCoinsStream after clear must emit zero docs; '
            'confirms demo JSON cannot leak into a real user session');
  });
}
