# NET-413 GROKCOS -> AGCOS: ADDENDUM to NET-411 - V8.18.15 - OVER
Filed 2026-10-21 ~10:35 AM ET. Baton stays AGCOS. NUMBERING: V8.18.15 done report = NET-414.
ALL items APP-ONLY, gated per NET-410 (isNativePhone = !kIsWeb && (Platform.isAndroid || Platform.isIOS)). NO web change.

## p. HIGH - Add New Coins landscape overflow
- Phone landscape: bottom overflow 261px. Entry-method list does not scroll, so 'Take a photo' and everything below 'Add by Cert #' is unreachable.
- Fix: wrap the entry list in a scrollable view (SingleChildScrollView / ListView with SafeArea + bottom padding for the bottom nav). Verify PORTRAIT and LANDSCAPE, every entry reachable, bottom nav never covers the last item.
- Blue Feedback button clipped at top-right: keep it fully on screen (SafeArea/insets) in both orientations.
- Tests: widget tests at 360/412/457dp portrait AND landscape equivalents; assert no overflow and the last entry is hit-testable after scroll.

## q. HIGH - Camera photo lost on low-RAM Android (TCL T609C, Android 13)
Repro: Enable Webcam -> system camera -> take photo -> app returns to main menu, no photo. Android killed the activity during the camera intent (392 MB PSS); app restarted with splash; cached JPG missing (NoSuchFileException).
Fix:
 1. Call ImagePicker().retrieveLostData() at startup AND on resume (Android only); if a photo or error is recovered, route it back into Add Coins at the ID step (with the side it was for). Handle a missing file with a friendly retry, never a crash.
 2. PREFERRED: capture in-app with the `camera` plugin on native phones so the activity is never backgrounded; keep ImagePicker as fallback.
 3. Reduce memory on this path: imageQuality/maxWidth on capture, release large images, avoid holding decoded bitmaps, check heavy widgets behind the camera.
 AUDIT every image_picker camera call site (add_coins_hub, coin_detail_screen, my_collection_screen, morgan_greeter, plus any found) and table each with status in EXECUTE_DONE.
Acceptance: on Eric's USB Android test phone, 5 photos IN A ROW each reach the ID step. Open until verified on device. Widget/unit tests for lost-data recovery and missing-file handling.

Rules unchanged (NET-400..411): one test per item, analyzer clean, version 8.18.15, one GEMINI38 review (real diff lines), NO deploy, nothing on main, explicit-path commits only, never git commit -a, two strikes -> STOP. Website must render exactly as today. NET-414 covers p and q item by item with file:line and gate status. Baton back to GROKCOS.
OVER
