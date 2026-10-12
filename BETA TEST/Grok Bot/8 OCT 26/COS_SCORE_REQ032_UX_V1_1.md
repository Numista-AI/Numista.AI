# COS SCORE - T3 REQ_032 UX PLAN V1.1 (PLAN_V1.1_REQ032_UX_REAL_PATHS.md)
Scored by: Grok CoS, 12 Oct 2026 ~5:15 PM ET. Code checked: dev HEAD a774152f (T1 lockdown commit).
PASS = build on dev only. No deploy, no live data writes, no sync_canon without Eric's typed YES.

## Verdict: PASS

## Spot-checks (lines actually opened)
1. Sidebar 29 / 26 non-admin - CONFIRMED. base_layout.dart:749 `_buildNavItem('Home Dashboard', ...)` through :837 `_buildNavItem('... Numista Lookup', ...)`; 29 nav items. Admin block :803-804 `if (email == 'jseaman1204@gmail.com' || email.endsWith('@numista.ai')) ...[` wraps :805 Admin Grade Flags, :814 (Beta Feedback Inbox), :821 Admin: Support Portal = 3 admin-only -> 26 non-admin.
2. Fix 5 in add_coins_hub.dart - CONFIRMED. screens\add_coins_hub.dart exists; add_coin_screen.dart does not.
3. PIN glyph in login_screen.dart:32-104 - PARTLY. :32 `final _pinCtrl = TextEditingController();` and :88-90 `_signIn()` / `_pinCtrl.text.trim()` are right, but the field that renders the glyphs is NOT in 32-104: it is :580-582 (`_passwordField(_pinCtrl...` / `_pinField(_pinCtrl...`), with :794 `obscureText: !visible,` :795 `maxLength: 6,` (and :878 obscureText in the password field). Edit those lines.
4. base_layout.dart:717-1554 fonts under 14px - CONFIRMED. :717 fontSize: 11, :721 fontSize: 9, :1196 fontSize: 13, :1214 fontSize: 10, :1320 fontSize: 10.5, :1549 fontSize: 11, :1554 fontSize: 9 (plus 12px at 895/906/1348/1358/1385/1395). :1281 22px is fine.

## Build conditions (carry forward from COS_SCORE_REQ032_UX.md)
- Fonts via new theme tokens file, not hand-edits per widget.
- PIN: replace the field at login_screen.dart:580-582/794-795 with the 6-box widget; backend 5-guess lockout untouched; keep the 6-digit sanitizer at :598-599.
- Regression test: all 29 routes reachable (26 non-admin + 3 admin).
- Coordinate ai_chat_screen.dart with T2; rebase on T1 (a774152f) first.
- Fix 1 still deferred (REQ_034/036).

Ball: AG CoS - build on dev, WILCO.
