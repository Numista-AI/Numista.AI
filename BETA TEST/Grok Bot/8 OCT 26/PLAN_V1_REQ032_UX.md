# PLAN V1 — REQ_032: Older User UX Fixes
Prepared by: Antigravity CoS  
Date: 2026-10-12  
Model assigned: Claude Sonnet 4.6 (Thinking)  
Status: PLAN ONLY — awaiting Gemini review, then Grok CoS score, then founder Proceed + YES to deploy.  
Source: `IMPLEMENTATION_PLAN_UX_AND_MORGAN_2026-10-08_v2.md` Workstream A (UX fixes), Eric's order: Fix 2 → Fix 3 → Fix 1 (post REQ_034/036) → Fix 4 → Fix 5.  
Code baseline: branch `dev`, commit `e5f5760c`

---

## 1. Goal

The target audience is collectors aged 60+. The current UI has text as small as 9–13px, garbled PIN dots, a navigation menu with 25 items, and an Add Coin flow that exposes too many choices. Gate 0 and REQ_031 touch `ai_chat_screen.dart`; Track 3 coordinates with those tracks on that file only.

Fix 1 (checklist big rows) depends on REQ_034/036 for correct slot counts. Fixes 2, 3, 4, and 5 proceed now.

---

## 2. Fix 2 — Bigger, Darker Text

**Problem:** Body text is hard-coded at 9–13px throughout (no centralized theme tokens). Buttons are not full-width on narrow screens. Minimum accessibility standard: 16px body text, 18px+ primary labels, 44px tap targets.

**Affected files to audit first:**
- `numista_mobile/lib/` — grep for `fontSize: 9`, `fontSize: 10`, `fontSize: 11`, `fontSize: 12`, `fontSize: 13`
- `numista_mobile/lib/theme/` (check if a theme file exists)

**Fix plan:**

**Step 2a — Create centralized theme tokens:**
Create or update `numista_mobile/lib/theme/numista_theme.dart`:

```dart
import 'package:flutter/material.dart';

class NumistaTheme {
  // Text sizes
  static const double textBodySm  = 16.0;  // minimum body text
  static const double textBody    = 18.0;  // standard body
  static const double textLg      = 20.0;  // section labels
  static const double textXl      = 24.0;  // headings
  static const double textCaption = 14.0;  // captions (sparingly)

  // Tap targets
  static const double tapTarget   = 44.0;

  // Color — ensure 4.5:1 contrast ratio minimum
  static const Color textPrimary   = Color(0xFF1A1A1A);  // near-black
  static const Color textSecondary = Color(0xFF4A4A4A);  // dark gray
  static const Color textHint      = Color(0xFF757575);  // WCAG AA minimum on white

  // Full-width button style
  static ButtonStyle primaryButtonStyle = ElevatedButton.styleFrom(
    minimumSize: const Size.fromHeight(56),
    textStyle: const TextStyle(fontSize: textBody, fontWeight: FontWeight.w600),
  );
}
```

**Step 2b — Replace hard-coded font sizes:**
Replace all `fontSize: 9` through `fontSize: 15` with `NumistaTheme.textBodySm` (16) or appropriate token. Do not touch text that is intentionally small (e.g., legal footnotes), but document each exception.

**Step 2c — Full-width buttons:**
On primary action buttons (`ElevatedButton`, `FilledButton`), add `style: NumistaTheme.primaryButtonStyle` or `minimumSize: const Size(double.infinity, 56)`.

**Step 2d — Verify tap targets:**
Audit `GestureDetector` and `InkWell` usages where the child widget is smaller than 44×44 dp. Wrap in `SizedBox(height: 44, width: 44)` or use `IconButton` with `constraints`.

**Acceptance:**
- Grep confirms no `fontSize:` below 14 on primary screens (captions may be 14).
- `flutter analyze lib/` — 0 errors.
- Screenshots before/after on a 360px-wide phone simulator.

---

## 3. Fix 3 — PIN Sign-In Screen

**Problem:** PIN boxes show garbled dot glyphs. The layout doesn't have a clear number keypad, no "Show PIN" toggle, and "Forgot your PIN?" is not prominent.

**Affected file:** `numista_mobile/lib/screens/login_screen.dart` (and the PIN entry widget — identify its exact location).

**Fix plan:**

**Step 3a — Audit current PIN widget:**
Read `login_screen.dart` to find the PIN entry widget. Identify the garbled glyph bug (likely a font mismatch or character encoding issue with the dot/circle glyph).

**Step 3b — Replace or fix the PIN widget:**
Design the PIN entry as six large `Container` boxes (50×50 dp, 8dp gap) that show a filled circle on entry and a blank box when empty. Do not use a text field with `obscureText` for each box (that causes the glyph issue); use a custom painter or `Icon(Icons.circle)` instead.

```dart
// For each slot:
Container(
  width: 50,
  height: 50,
  decoration: BoxDecoration(
    border: Border.all(color: Colors.grey.shade400, width: 2),
    borderRadius: BorderRadius.circular(8),
    color: _enteredDigits > slotIndex ? Colors.black87 : Colors.white,
  ),
)
```

**Step 3c — Number keypad:**
Display a 3×4 grid keypad (1–9, blank, 0, backspace). Each key is at least 72×72 dp. The keypad replaces the system keyboard so it cannot be dismissed accidentally.

**Step 3d — Show PIN toggle:**
Below the PIN boxes, a `TextButton` with text "Show PIN" / "Hide PIN". When showing, replace the filled circles with the actual digit characters (`TextStyle(fontSize: 28, fontWeight: FontWeight.w700)`).

**Step 3e — Forgot PIN:**
A prominent `TextButton("Forgot your PIN?")` at the bottom of the form, minimum 44dp tap target, font size 18, color `NumistaTheme.textPrimary`. Routes to `/reset-password`.

**Step 3f — Keep REQ_025 lockout:**
The 5-guess lockout logic is already implemented in the backend. Ensure the Flutter widget counts failed attempts and disables the keypad with a countdown (`"Too many attempts. Try again in X seconds."`).

**Acceptance:**
- No garbled glyphs on any simulator/device.
- Show/Hide PIN works.
- Keypad tap targets ≥ 72dp.
- `flutter test test/reset_password_route_test.dart` — passes (already written in REQ_027G).
- `flutter analyze lib/` — 0 errors.

---

## 4. Fix 1 — Checklist Big Rows (DEFERRED — awaiting REQ_034/036)

This fix is BLOCKED on REQ_034 (slot count accuracy) and REQ_036 (name matching). Do not implement until both are complete and Grok CoS scores them PASS.

**What will change when unblocked:**
- One big row per coin slot: full program name, year, mint (min 56dp row height).
- Tap targets: P / D / S buttons, each at least 44×44 dp.
- Progress summary: "7 of 19 collected, 12 to go" (not the current "System of Record completion %").
- Fix the demo "View Checklist" mislink on program cards.

**Placeholder test:** `flutter test test/checklist_row_test.dart` — stub test marked `skip: 'REQ_034/036 not merged'`.

---

## 5. Fix 4 — Navigation Menu (25 → 6 Items)

**Problem:** The navigation menu has 25 items. Older users cannot find what they need.

**Affected file:** Identify the navigation widget — likely `numista_mobile/lib/widgets/navigation_drawer.dart` or a `BottomNavigationBar` in the main scaffold. Read the file first.

**Fix plan:**

**Step 4a — Identify current nav structure:**
Read `numista_mobile/lib/main.dart` and the main scaffold widget to find where navigation items are defined.

**Step 4b — New structure (6 top-level items):**
```
1. Home
2. My Coins
3. Add a Coin
4. Coin Programs
5. Help & Ask Morgan
6. More ▼
```

Everything else moves under "More". Nothing is removed — only reorganized. The "More" section opens a bottom sheet or a secondary menu with the remaining items grouped by category.

**Step 4c — "Help & Ask Morgan" item:**
Routes to the Morgan chat screen. Label must be readable at 18px.

**Step 4d — Tap targets and labels:**
Each nav item: minimum 56dp tall, label 16px+, icon 24dp+.

**Acceptance:**
- Navigation drawer/bar shows exactly 6 top-level items.
- All 25 original destinations are still accessible (regression check).
- `flutter analyze lib/` — 0 errors.
- Screenshots before/after.

---

## 6. Fix 5 — Add a Coin (3 Choices)

**Problem:** The Add Coin flow has too many options, uses jargon ("schema"), and overwhelms older users.

**Affected file:** Identify from `main.dart` or the navigation routes.

**Fix plan:**

**Step 5a — New primary screen:**
```
Take a photo
Type it in
Upload a list
```
Each option is a large card (min 80dp tall, 18px+ label, icon 32dp+, full-width).

**Step 5b — "More ways" section:**
A `TextButton("More ways to add")` below the three cards. Tapping it expands additional options (barcode scan, import from CSV, etc.). The label "More ways" is self-explanatory — no "schema" or technical terms.

**Step 5c — Plain language throughout:**
Audit any labels in the Add Coin flow for jargon. Replace: "schema" → "format", "denomination" → "coin type" (in user-facing labels only — keep the internal field name), "program_id" never shown to the user.

**Step 5d — Coordinate with Morgan Gate 0:**
The "Type it in" path may eventually become the Morgan chat path (Phase 2). Do not couple them now — the current non-Morgan path stays as-is. The coordination point is `ai_chat_screen.dart`: if Morgan Gate 0 adds a new screen entry point, Fix 5 must not break it.

**Acceptance:**
- Add Coin screen shows exactly 3 primary choices.
- No jargon in user-facing labels.
- All existing add paths still work (regression).
- `flutter analyze lib/` — 0 errors.

---

## 7. Files Changed (estimated)

| File | Change |
|---|---|
| `numista_mobile/lib/theme/numista_theme.dart` | CREATE — centralized tokens |
| `numista_mobile/lib/screens/login_screen.dart` | Fix PIN widget, keypad, Show PIN, Forgot PIN |
| All files with `fontSize: 9-15` | Replace with theme tokens |
| All files with small buttons | Add full-width / 44dp constraints |
| `numista_mobile/lib/widgets/navigation_drawer.dart` (or equivalent) | 6-item nav |
| `numista_mobile/lib/screens/add_coin_screen.dart` (or equivalent) | 3-choice screen |

---

## 8. Test Strategy

```dart
// Fix 2: no sub-14 font sizes
// (static analysis + grep, not a widget test)

// Fix 3: PIN screen
// numista_mobile/test/login_screen_pin_test.dart (new)
// - pump LoginScreen
// - tap '1' on keypad → first box filled
// - tap 'Show PIN' → digit shows
// - tap 'Forgot your PIN?' → navigates to /reset-password
// - tap 5 wrong PINs → lockout message shown

// Fix 4: navigation
// numista_mobile/test/navigation_test.dart (new)
// - count BottomNavigationBar/DrawerItems → exactly 6
// - each of the 25 original destinations still reachable

// Fix 5: add coin
// numista_mobile/test/add_coin_screen_test.dart (new)
// - count primary option cards → exactly 3
// - no text containing 'schema'
```

---

## 9. Acceptance Criteria

- [ ] No text below 14px anywhere (`flutter analyze` + grep)
- [ ] No garbled PIN glyphs
- [ ] Navigation shows 6 top-level items
- [ ] Add Coin shows 3 primary choices, no jargon
- [ ] `flutter analyze lib/` — 0 errors, 0 warnings
- [ ] `flutter test --reporter compact` — all pass (419+)
- [ ] Screenshots provided before/after for each fix
- [ ] Dev only — no deploy without founder's YES

---

## 10. Dependency and Coordination Notes

- **Track 1 (REQ_031):** no shared files — independent.
- **Track 2 (Morgan Gate 0):** shared file is `ai_chat_screen.dart` only. Coordinate: Gate 0 adds `morgan_confirm` wiring; Fix 5 changes the Add Coin entry point. Do not merge conflicting changes to that file without rebasing.
- **REQ_034/036:** Fix 1 is hard-blocked on those. The stub test is the placeholder.
- **REQ_025:** PIN lockout logic — do not change the 5-guess backend behaviour, only the Flutter counter display.

---

*No code written. Awaiting Gemini review, then Grok CoS score, then founder Proceed.*
