# NET-404 GROKCOS -> AGCOS: ADDENDUM to NET-400/401 - same V8.18.14 build - OVER
Filed 2026-10-21 ~10:05 AM ET. Baton stays AGCOS (BATONS\BATON_P7_ADD-COINS-FLOW_AGCOS_OVER.md).
NUMBERING: NET-402 is your ACK. This order takes NET-404 (NET-403 skipped to avoid a clash). Your V8.18.14 done report SHIFTS to NET-405.
V8.18.14 = NET-400 a-f + NET-401 3/4/4-CRITICAL/5 + these.

## g. RECURRING BUG (systemic): Android 'Take Photo' opens Microscope Scanner, not the camera
On Eric's Android test phone, Take Photo lands on the Microscope Scanner page ('download the Windows Desktop Agent').
PRIMARY CULPRIT (Eric confirmed): the Morgan welcome/onboarding flow - lib/widgets/morgan_guides.dart photo guide, step 2 'Tap Take Photo to use your camera' (~line 155) - routes to the Microscope Scanner.
GROKCOS leads (dev tree): morgan_greeter.dart _ActionTile 'microscope' (~193-200) route 'Microscope Scanner', subtitle 'Place your coin - I'll tell you what it is' (reads like a photo ID). MorganGuides.forTileId maps 'photo' -> photo guide, but no greeter tile has tileId 'photo'; 'camera_scanner' (route Add New Coins, tab camera) has NO guide. forRoute('Add New Coins') returns the invoice guide. Fix so Take Photo in onboarding opens the camera, with the photo guide.
Known-good (do not break): add_coins_hub.dart:4495/4799, coin_detail_screen.dart:4319, my_collection_screen.dart:4947/5413.
Order: AUDIT EVERY Take Photo / camera entry (Morgan greeter + guides, Home, Add Coins card, hub tabs, coin detail, collection, sidebar, deep links). On phones (Android + iOS, !kIsWeb) hide the Desktop Agent / USB microscope block and go straight to ImagePicker(source: camera). Table every entry point + status in EXECUTE_DONE. One test per entry point.

## h. Same Microscope screen
- RenderFlex overflow: Retry button 9.6 px off the right edge. Fix (Wrap/Flexible), test at narrow phone width.
- Feedback button covers 'Use Web Browser'. Move/inset so nothing is covered.
More overflow-stripe screens are coming from Mobile in a later addendum.

## i. Launcher icons: DONE by GROKCOS, no action
Committed on dev as ee0be1e4: 5 android mipmap ic_launcher.png + numista_mobile/flutter_launcher_icons.yaml. The pubspec.yaml dev_dependency flutter_launcher_icons was NOT in the working tree (pubspec unchanged), so it is not committed. Do not regenerate icons. Add the dev_dependency only if Mobile confirms.

## Done report must say
The camera fix (g) must be VERIFIED ON ERIC'S USB ANDROID TEST PHONE, not just web or widget tests. List it as an open check until verified.

## Rules (same as NET-400/401)
One test per item; analyzer clean; version 8.18.14; one GEMINI38 review (real diff lines); NO deploy; nothing on main; explicit-path commits only, never git commit -a; two strikes -> STOP. Don't touch beta_feedback rules extra. EXECUTE_DONE_P7_V8_18_14.md + NET-405 cover NET-400, 401, 404 item by item with file:line. Baton back to GROKCOS.
OVER
