import 'morgan_guide_flow.dart';

/// All four Morgan guided flows.
///
/// Each flow is a [MorganGuide] with a list of [MorganStep]s.
/// Language rules:
///   ✅ Plain English — "tap the blue button", not "select the input control"
///   ✅ One idea per step — never two instructions at once
///   ✅ Friendly, patient tone — "I'll wait right here!"
///   ✅ No error codes or tech jargon
///   ✅ Celebrate small wins — "Great!", "Perfect!", "You did it!"
class MorganGuides {
  MorganGuides._();

  // ── 1. Add coins from a receipt or invoice ──────────────────────────────────
  static const MorganGuide invoice = MorganGuide(
    id: 'guide_invoice',
    title: 'Adding coins from a receipt',
    emoji: '📄',
    steps: [
      MorganStep(
        narration:
            "Let's add your coins from a receipt or invoice! "
            "First — do you have a photo of the receipt on this device, "
            "or would you like to take a photo right now?",
        hint: 'Look for the "Upload" or "Take Photo" button on this screen.',
        nextLabel: "I'm ready, let's go →",
      ),
      MorganStep(
        narration:
            "Tap the big blue \"Upload\" button on this screen. "
            "Then find your receipt photo in your photos or files.",
        hint: "If you don't see it, try scrolling down on this screen.",
        nextLabel: 'I uploaded it →',
      ),
      MorganStep(
        narration:
            "I'm reading your receipt now — this usually takes about "
            "10 to 15 seconds. Please wait while I work!",
        hint: "You'll see a loading spinner. It will finish on its own.",
        nextLabel: 'It finished loading →',
      ),
      MorganStep(
        narration:
            "Here are the coins I found on your receipt! "
            "Look them over to make sure they look right.",
        hint: 'If something looks wrong, tap the coin to fix it.',
        nextLabel: 'They look right! →',
      ),
      MorganStep(
        narration:
            "Tap the \"Add to My Collection\" button to save these coins. "
            "I'll add them right away!",
        hint: 'The button is usually at the bottom of the list.',
        nextLabel: "I tapped it →",
      ),
      MorganStep(
        narration:
            "🎉 You did it! Those coins are now saved in your collection. "
            "Would you like to add more, or would you like to see your collection?",
        hint: 'Tap "Done!" to finish, or use the menu on the left to keep going.',
        nextLabel: "All done! →",
      ),
    ],
  );

  // ── 2. Identify a coin with the Microscope ──────────────────────────────────
  static const MorganGuide microscope = MorganGuide(
    id: 'guide_microscope',
    title: 'Using the Microscope',
    emoji: '🔬',
    steps: [
      MorganStep(
        narration:
            "Let's use the microscope! This is a special camera that "
            "connects to your computer to look at coins up close. "
            "Is the microscope plugged in and turned on?",
        hint: 'The microscope should have a small light when it\'s on.',
        nextLabel: "Yes, it's ready →",
      ),
      MorganStep(
        narration:
            "Place your coin face-up, flat under the microscope lens. "
            "Try to center it as best you can.",
        hint: 'The coin should be right under the glass lens of the microscope.',
        nextLabel: "Coin is in place →",
      ),
      MorganStep(
        narration:
            "Now tap the \"Start Scan\" button on this screen. "
            "I'll take a look at your coin!",
        hint: 'Look for the large button in the middle of this screen.',
        nextLabel: 'I tapped Start Scan →',
      ),
      MorganStep(
        narration:
            "Hold still — I'm examining your coin! "
            "This usually takes about 10 seconds.",
        hint: "Try not to bump the microscope while I'm scanning.",
        nextLabel: 'The scan finished →',
      ),
      MorganStep(
        narration:
            "Here's what I think this coin is! "
            "Take a look and see if it matches your coin.",
        hint: 'If it looks wrong, tap "That\'s not right" and I\'ll try again.',
        nextLabel: "Yes, that's it! →",
      ),
      MorganStep(
        narration:
            "Great! Tap \"Save to My Collection\" to add this coin. "
            "I'll save all the details for you.",
        hint: 'The save button is at the bottom of the screen.',
        nextLabel: "Saved! →",
      ),
    ],
  );

  // ── 3. Take a photo to identify a coin ─────────────────────────────────────
  static const MorganGuide photo = MorganGuide(
    id: 'guide_photo',
    title: 'Identify a coin from a photo',
    emoji: '📷',
    steps: [
      MorganStep(
        narration:
            "I can identify almost any coin from a photo! "
            "First, place your coin on a flat surface — "
            "a table with good lighting works best.",
        hint: 'Bright, even lighting helps me see the coin clearly.',
        nextLabel: "Coin is ready →",
      ),
      MorganStep(
        narration:
            "Now tap \"Take Photo\" to use your camera, "
            "or \"Upload from Device\" if you already have a photo saved.",
        hint: 'Either button works — just pick whichever is easier for you.',
        nextLabel: 'I took the photo →',
      ),
      MorganStep(
        narration:
            "I'm looking at your coin now — give me just a moment!",
        hint: 'The screen will update on its own when I\'m done.',
        nextLabel: 'Results appeared →',
      ),
      MorganStep(
        narration:
            "Here's what I found! I'll show you the coin name, "
            "year, and estimated value. Does that match your coin?",
        hint: 'If I got it wrong, tap "That\'s not right" and I\'ll try again.',
        nextLabel: "Yes, that's correct! →",
      ),
      MorganStep(
        narration:
            "Tap \"Save to My Collection\" to add this coin. "
            "All the details will be saved automatically!",
        hint: 'The green Save button is near the bottom.',
        nextLabel: "It's saved! →",
      ),
    ],
  );

  // ── 4. Browse the collection ────────────────────────────────────────────────
  static const MorganGuide collection = MorganGuide(
    id: 'guide_collection',
    title: 'Browsing your collection',
    emoji: '🗂️',
    steps: [
      // Step 1: bubble at top-right, big gold ← arrow to its left pointing at the search box
      MorganStep(
        narration:
            "Looking for a specific coin?\n"
            "Type its name in the 🔍 Search box.\n\n"
            "Try 'Dime', '1964', or 'Morgan Silver Dollar'.",
        hint: "The Search box is to the left — tap it and start typing.",
        nextLabel: 'Got it →',
        position: GuidePosition.topRight,
        showArrow: true,
        arrowDirection: ArrowDirection.left,
      ),
      // Step 2: coin list is centre-screen; bubble bottom-right stays out of the way
      MorganStep(
        narration:
            "All your coins are listed here.\n"
            "Tap any coin to see its full details — "
            "value, grade, photos, and more!",
        hint: 'Try tapping a coin that interests you.',
        nextLabel: 'I tapped a coin →',
        position: GuidePosition.bottomRight,
      ),
      // Step 3: detail page
      MorganStep(
        narration:
            "This page shows everything I know — "
            "estimated value, mint, condition, and history.",
        hint: 'Scroll down to see all the details.',
        nextLabel: 'Got it →',
        position: GuidePosition.bottomRight,
      ),
      // Step 4: AI Deep Dive button
      MorganStep(
        narration:
            "See the \"AI Deep Dive\" button?\n"
            "Tap it to ask me anything about this coin!",
        hint: 'History, value, varieties — I love talking about coins.',
        nextLabel: "That's great! →",
        position: GuidePosition.bottomRight,
      ),
      // Step 5: farewell, centred for emphasis
      MorganStep(
        narration:
            "You're all set! 🎉\n"
            "I'm always here if you need me — "
            "just tap \"Ask Morgan\"!",
        nextLabel: 'Thanks, Morgan! →',
        position: GuidePosition.bottomCenter,
      ),
    ],
  );

  /// Returns the guide matching a given route name, or null if none.
  static MorganGuide? forRoute(String route) {
    switch (route) {
      case 'Add New Coins':
        return invoice;         // invoice & photo both go to Add New Coins
      case 'Microscope Scanner':
        return microscope;
      case 'My Collection':
        return collection;
      default:
        return null;
    }
  }

  /// Returns the correct guide for the specific tile ID.
  static MorganGuide? forTileId(String tileId) {
    switch (tileId) {
      case 'invoice':
        return invoice;
      case 'photo':
        return photo;
      case 'microscope':
        return microscope;
      case 'collection':
        return collection;
      default:
        return null;
    }
  }
}
