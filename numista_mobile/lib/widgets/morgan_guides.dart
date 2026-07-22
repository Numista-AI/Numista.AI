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
///   ✅ Narrations ≤ 2 short sentences — keeps the compact 300px bubble tidy
///   ✅ Positions set on every step so the bubble stays out of the active area
class MorganGuides {
  MorganGuides._();

  // ── 1. Add coins from a receipt or invoice ──────────────────────────────────
  static const MorganGuide invoice = MorganGuide(
    id: 'guide_invoice',
    title: 'Adding coins from a receipt',
    emoji: '📄',
    steps: [
      // Step 1: intro — user is looking at the Add New Coins tab bar
      MorganStep(
        narration:
            "I can read your receipt and add coins automatically!\n"
            "Pick the 'Single Invoice Scan' tab to get started.",
        hint: 'The tabs are at the top of this screen.',
        nextLabel: "Ready! →",
        position: GuidePosition.bottomRight,
      ),
      // Step 2: upload — red Browse PDF button is center-screen
      MorganStep(
        narration: "Tap the red Browse PDF button and choose your receipt file.",
        hint: "The button is in the center of this screen.",
        nextLabel: 'I tapped Browse PDF →',
        position: GuidePosition.topRight,
        showArrow: true,
        arrowDirection: ArrowDirection.down,
      ),
      // Step 3: processing — loading overlay is visible
      MorganStep(
        narration:
            "I'm reading your receipt — about 10–15 seconds.\n"
            "Watch the progress bar!",
        hint: "The loading screen will disappear when I'm finished.",
        nextLabel: 'It finished →',
        position: GuidePosition.topRight,
      ),
      // Step 4: ExtractionSuccessDialog — shows count + "Go to Review Hub"
      MorganStep(
        narration:
            "I've sent your coins to the Review Hub!\n"
            "Tap 'Go to Review Hub' to see what I found.",
        hint: "You can review and fix any details before saving.",
        nextLabel: "I'm in the Review Hub →",
        position: GuidePosition.bottomRight,
      ),
      // Step 5: Review Hub — user selects and commits items
      MorganStep(
        narration:
            "Select the coins you want to keep,\n"
            "then tap 'Commit Selected' to save them.",
        hint: "Use the top checkbox to select everything at once.",
        nextLabel: "I committed them →",
        position: GuidePosition.bottomRight,
      ),
      // Step 6: celebration
      MorganStep(
        narration: "🎉 Done! Those coins are now saved in your collection.",
        hint: 'Use the menu on the left to keep going.',
        nextLabel: "All done! →",
        position: GuidePosition.bottomCenter,
      ),
    ],
  );

  // ── 2. Identify a coin with the Microscope ──────────────────────────────────
  static const MorganGuide microscope = MorganGuide(
    id: 'guide_microscope',
    title: 'Using the Microscope',
    emoji: '🔬',
    steps: [
      // Step 1: intro — check microscope is connected
      MorganStep(
        narration:
            "Let's use the microscope!\n"
            "Is it plugged in and powered on? Look for a small indicator light.",
        hint: 'The microscope connects to your computer via USB.',
        nextLabel: "It's ready →",
        position: GuidePosition.bottomRight,
      ),
      // Step 2: place coin under lens
      MorganStep(
        narration: "Place your coin face-up, centered under the lens.",
        hint: 'The coin should sit right under the glass lens.',
        nextLabel: "Coin is placed →",
        position: GuidePosition.bottomRight,
      ),
      // Step 3: start scan — blue button is in the scan controls (left area)
      MorganStep(
        narration: "Now tap ▶ Start Microscope Scan — I'll take a close look!",
        hint: 'Look for the blue Start Scan button on this screen.',
        nextLabel: 'I tapped Start Scan →',
        position: GuidePosition.topRight,
        showArrow: true,
        arrowDirection: ArrowDirection.down,
      ),
      // Step 4: scanning in progress
      MorganStep(
        narration:
            "Hold still — I'm examining your coin!\n"
            "This usually takes about 10 seconds.",
        hint: "Try not to bump the microscope while I'm scanning.",
        nextLabel: 'Scan finished →',
        position: GuidePosition.topRight,
      ),
      // Step 5: review AI results
      MorganStep(
        narration:
            "Here's what I think this is!\n"
            "Does it match your coin?",
        hint: "Tap 'That's not right' and I'll try again.",
        nextLabel: "Yes, that's it! →",
        position: GuidePosition.bottomRight,
      ),
      // Step 6: save to collection
      MorganStep(
        narration: "Tap 'Save to My Collection' — all details are saved automatically!",
        hint: 'The Save button is near the bottom of the screen.',
        nextLabel: "Saved! →",
        position: GuidePosition.bottomRight,
      ),
    ],
  );

  // ── 3. Take a photo to identify a coin ─────────────────────────────────────
  static const MorganGuide photo = MorganGuide(
    id: 'guide_photo',
    title: 'Identify a coin from a photo',
    emoji: '📷',
    steps: [
      // Step 1: intro — set up the coin
      MorganStep(
        narration:
            "I can identify almost any coin from a photo!\n"
            "Place it on a flat, well-lit surface first.",
        hint: 'Good lighting helps me see the details clearly.',
        nextLabel: "Coin is ready →",
        position: GuidePosition.bottomRight,
      ),
      // Step 2: take or upload photo
      MorganStep(
        narration:
            "Tap Take Photo to use your camera,\n"
            "or Upload from Device if you have a photo saved.",
        hint: 'Either works — pick whichever is easier.',
        nextLabel: 'Photo is ready →',
        position: GuidePosition.bottomRight,
      ),
      // Step 3: processing
      MorganStep(
        narration: "Looking at your coin now — give me a moment! 🔍",
        hint: "The screen updates automatically when I'm done.",
        nextLabel: 'Results appeared →',
        position: GuidePosition.topRight,
      ),
      // Step 4: results shown
      MorganStep(
        narration:
            "Here's what I found — name, year, and estimated value.\n"
            "Does that look right?",
        hint: "Tap 'That's not right' and I'll try again.",
        nextLabel: "Yes, that's it! →",
        position: GuidePosition.bottomRight,
      ),
      // Step 5: save
      MorganStep(
        narration: "Tap 'Save to My Collection' — all details save automatically!",
        hint: 'The green Save button is near the bottom.',
        nextLabel: "It's saved! →",
        position: GuidePosition.bottomRight,
      ),
    ],
  );

  // ── 4. Browse the collection ────────────────────────────────────────────────
  static const MorganGuide collection = MorganGuide(
    id: 'guide_collection',
    title: 'Browsing your collection',
    emoji: '🗂️',
    steps: [
      // Step 1: bubble at top-right with inline search — no separate search
      // box exists on the 'All' dashboard, so Morgan provides search directly.
      MorganStep(
        narration:
            "Looking for a specific coin?\n"
            "Type its name below and I'll search your whole collection!",
        hint: "Works for coins, currency, and world items.",
        nextLabel: 'Got it →',
        position: GuidePosition.topRight,
        showSearch: true,
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
      // Step 3: coin detail page
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

  // ── 5. Coin Programs & Checklists ──────────────────────────────────────────
  static const MorganGuide programs = MorganGuide(
    id: 'guide_programs',
    title: 'Coin Programs & Checklists',
    emoji: '📋',
    steps: [
      // Step 1: Select a program
      MorganStep(
        narration:
            "Welcome to Coin Programs!\n"
            "Pick a program from the list to see its checklist of coins.",
        hint: "Tap on any program card like 'Presidential Dollars' to begin.",
        nextLabel: "Ready! →",
        position: GuidePosition.bottomRight,
      ),
      // Step 2: Check the coins you want to add
      MorganStep(
        narration:
            "Check the boxes next to the coins you have or want to track.",
        hint: "Scroll down to see the entire checklist for this program.",
        nextLabel: "Checked them →",
        position: GuidePosition.bottomRight,
      ),
      // Step 3: Add selected coins
      MorganStep(
        narration:
            "Tap the blue 'Add Selected Coins' button at the bottom.",
        hint: "I'll save all selected coins directly to your collection tracker.",
        nextLabel: "Add coins →",
        position: GuidePosition.bottomRight,
      ),
      // Step 4: Celebration
      MorganStep(
        narration:
            "🎉 Success! Those checklist coins are now saved in your collection.",
        hint: "You can view them at any time in 'My Collection'.",
        nextLabel: "All done! →",
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
      case 'Coin Programs':
        return programs;
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
      case 'programs':
        return programs;
      default:
        return null;
    }
  }
}
