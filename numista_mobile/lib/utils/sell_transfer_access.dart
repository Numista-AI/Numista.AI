import 'package:firebase_auth/firebase_auth.dart';

import '../services/guest_seed_service.dart';

/// The exact message shown in place of Sell on eBay / Transfer for Browse Demo (PLAN v1.2 section 4.6).
const String kSellTransferDemoCta = 'Create a free account to sell or transfer items.';

/// Pure rule. A user may sell or transfer only when signed in with a REGISTERED (non-anonymous)
/// account and NOT in Browse Demo.
///
/// Deliberately does not reference `AuthService.isGuest`: that getter exists on main (818ef7df) and is
/// deleted by the pending Guest-retirement build (0edf9004), so this compiles on both sides.
bool canSellOrTransferFor({
  required bool browseDemo,
  required bool signedIn,
  required bool anonymous,
}) {
  if (browseDemo) return false;
  if (!signedIn) return false;
  if (anonymous) return false;
  return true;
}

/// Live check. Browse Demo is evaluated FIRST and short-circuits, so Firebase is not touched at all.
bool canSellOrTransfer() {
  if (GuestSeedService.isBrowseDemoMode) return false;
  final user = FirebaseAuth.instance.currentUser;
  return canSellOrTransferFor(
    browseDemo: false,
    signedIn: user != null,
    anonymous: user?.isAnonymous ?? false,
  );
}
