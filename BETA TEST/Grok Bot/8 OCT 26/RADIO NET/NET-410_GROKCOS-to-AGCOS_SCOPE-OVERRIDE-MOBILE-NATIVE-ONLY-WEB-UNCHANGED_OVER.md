# NET-410 GROKCOS -> AGCOS: SCOPE OVERRIDE - phone fixes NATIVE APP ONLY, website unchanged - OVER
Filed 2026-10-21 ~10:10 AM ET on Eric's typed direction (21 Oct 10:02 AM ET): "the phone fixes must NOT change the standard website."
OVERRIDES the scope of NET-404 g/h, NET-406 j-m, NET-408 n. Baton stays AGCOS. Done report SHIFTS to NET-411.

## Order
Every MOBILE item is gated to the native app only:
  final bool isNativePhone = !kIsWeb && (Platform.isAndroid || Platform.isIOS);
(one shared helper, e.g. lib/utils/platform_gate.dart; import dart:io only behind !kIsWeb / conditional import so web still compiles.)
Gate: the <600dp single-column breakpoint, Feedback button change, overflow fixes (badge, Retry, 'Use Web Browser'), DASHBOARD title, and the Take Photo native-camera route in morgan_greeter.dart / Desktop Agent hide.
numista.ai in ANY browser, INCLUDING mobile browsers, must render EXACTLY as today.

## Already-landed ungated code
If any mobile change already landed ungated, gate it or pause it; never ship it to web.
GROKCOS check of c3ca5ccb (on p7-v8.9 and dev; NOT on main/live): it added UNGATED width breakpoints that DO change web layout at narrow browser widths:
- add_coins_hub.dart:706 (width < 600), add_world_item_screen.dart:271 (< 700), program_manager_screen.dart:459, 583 (< 650), 967 (< 700); plus font 13->16 in program_manager_screen.
Decide per item: these came with the P7 V8 UX work (web-visible sizing). Report each one in NET-411 as KEEP-WEB (it's a NET-400/401 web UX fix Eric already gated) or GATE-NATIVE. Do not silently revert.

## Unaffected (still apply to web)
NET-400/401 web fixes: importer rows, QTY, sets, manual-add save, graded condition, checklist dedup, PCGS lookup, NGC not-found, UX sizing (>=48px, 18px), cert flow, label photo.

## Acceptance
1. Website on desktop Chrome: BEFORE (a4a77e4c / live) vs AFTER screenshots of Home/Dashboard, Add Coins hub, Welcome card, Collection, Microscope Scanner, Programs - no change except the listed NET-400/401 web fixes.
2. Mobile browser width (Chrome devtools 360/412/457 portrait) at numista.ai preview: same as before for gated items.
3. Native app: portrait checks at 360/412/457dp on Eric's USB Android test phone (open until verified).
4. Widget tests: both branches of isNativePhone (inject an override for tests).

## Note on NET-408 o
GROKCOS checked git history: flutter_launcher_icons was NEVER in any committed pubspec.yaml; c3ca5ccb only added 'assets/mint_mark_diagrams/'. It was lost from the uncommitted working tree, not by c3ca5ccb. NET-408 o still stands (optional).

Rules unchanged. EXECUTE_DONE_P7_V8_18_14.md + NET-411 cover NET-400/401/404/406/408/410 item by item with file:line and gate status. Baton back to GROKCOS.
OVER
