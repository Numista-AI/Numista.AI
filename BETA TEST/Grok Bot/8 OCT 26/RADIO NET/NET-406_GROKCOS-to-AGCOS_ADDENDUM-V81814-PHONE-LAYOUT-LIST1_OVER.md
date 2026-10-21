# NET-406 GROKCOS -> AGCOS: ADDENDUM for V8.18.14 - Phone layout list #1 (Mobile) - OVER
Filed 2026-10-21 ~10:00 AM ET. Baton stays AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).
NUMBERING: your V8.18.14 done report SHIFTS AGAIN to NET-407 (NET-405 no longer used for it).
V8.18.14 = NET-400 a-f + NET-401 3/4/4-CRITICAL/5 + NET-404 g/h + these.

Source: Mobile, Android phone, 457dp wide.

## Items
j. Welcome Beta Tester card: FOUNDING BETA / FREE badge overflows the right edge by 86px. Must fit (Wrap / Flexible / move badge below title on narrow).
k. DASHBOARD title wraps mid-word. Use FittedBox (scaleDown) or smaller text on narrow screens; never break a word.
l. Desktop two-column layout is used on the phone: Est. Portfolio Value squeezed; Feedback FAB covers a button. Phone gets single column.
m. Copy says '18-step checklist' but the button shows 14/20. Make the count consistent and DATA-DRIVEN (both strings from the same checklist length), no hard-coded number.

## Systemic fix
- ONE shared phone breakpoint for EVERY screen (single column below ~600dp), e.g. a single const/helper in one file used everywhere; remove ad-hoc width checks. List every screen converted in EXECUTE_DONE.
- Feedback FAB: smaller on phones and/or movable/collapsible, and it must NEVER cover a button (reserve bottom padding or offset). Covers NET-404 h ('Use Web Browser') too.
- Golden or widget tests at 360dp AND 457dp for Welcome card, Dashboard, and every screen touched; assert no RenderFlex overflow and FAB not overlapping tappables.

## Rules (same as NET-400/401/404)
One test per item; analyzer clean; version 8.18.14; one GEMINI38 review (real diff lines); NO deploy; nothing on main; explicit-path commits only, never git commit -a; two strikes -> STOP. Don't touch beta_feedback rules extra. Phone fixes still need checking on Eric's USB Android test phone; list as open. EXECUTE_DONE_P7_V8_18_14.md + NET-407 cover NET-400, 401, 404, 406 item by item with file:line. Baton back to GROKCOS.
OVER
