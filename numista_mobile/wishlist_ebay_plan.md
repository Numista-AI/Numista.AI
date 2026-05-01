# Action Plan: v3.1 Priorities & Wishlist Monetization

## 1. Technical Debt Resolution (First Priority)
Before adding new features, we must secure the foundation of the Flutter migration.
- **Dependency Audit:** Run `flutter pub outdated` and `flutter pub upgrade` to resolve the 5 incompatible package constraints in `pubspec.yaml`.
- **Validation:** Run a successful build and verify the hardware scanner can still communicate with the Flutter frontend without any compilation warnings.

---

## 2. The Wishlist Port (Phase 3 Feature)
We will port the legacy React Wishlist logic (`WishlistPage.tsx`) over to Flutter (`wishlist_screen.dart`), backed by a new Firestore `wishlist` collection. 

**Core Functionality:**
- Add items by Year, Denomination, and Series.
- Specify Target Condition and Max Budget.
- **Smart Ownership Detection:** Automatically flag wishlist items as "In Collection" and turn them green if a matching coin is scanned by the microscope.

## 3. The "Shareable Gift List" & eBay Monetization Strategy
This represents a major opportunity to implement a passive monetary stream.

**The Concept:**
Users can click a "Share Wishlist" button that generates a read-only, public link (e.g., `numista.ai/wishlist/eric-d`). 
They can email this link to family members (like parents, aunts/uncles) before birthdays or Christmas.

**The Monetization Flow:**
1. Family member opens the beautiful web UI of the user's wishlist.
2. They see a specific coin the user wants (e.g., "1932 Washington Quarter, BU Condition, Max $50").
3. They click a prominent button: **[ Find this on eBay ]**.
4. The button utilizes the **eBay Partner Network (EPN)** affiliate program. The resulting link searches eBay for the exact coin, automatically applying condition filters and price caps.
5. If the family member purchases *anything* on eBay during that session, the Numista.AI platform earns a percentage commission (typically 1-4% of the sale).

**Implementation Steps:**
- **UI:** Add a "Share" floating action button on the Flutter Wishlist screen.
- **Backend:** Create a lightweight web-render route that reads a user's wishlist (omitting private data like cost basis of other coins).
- **Integration:** Format external URLs dynamically to inject the user's search queries into an eBay affiliate link.
