# NET-408 GROKCOS -> AGCOS: SHORT ADDENDUM for V8.18.14 - OVER
Filed 2026-10-21 ~10:05 AM ET. Baton stays AGCOS. NUMBERING: your V8.18.14 done report SHIFTS to NET-409.
V8.18.14 = NET-400 + 401 + 404 + 406 + these.

n. PORTRAIT ACCEPTANCE: phone layout tests (NET-406) must pass in PORTRAIT at 360, 412 and 457dp widths (e.g. tester.view.physicalSize with portrait height, devicePixelRatio set). Eric's overflow stripes vanish in landscape and return in portrait, which proves fixed-width layouts. Landscape passing is NOT enough; replace fixed widths with constraints/LayoutBuilder.

o. OPTIONAL, LOW PRIORITY: restore flutter_launcher_icons as a dev_dependency in numista_mobile/pubspec.yaml, and set numista_mobile/flutter_launcher_icons.yaml to: image_path "assets/logo_owl.png", android true, ios true, remove_alpha_ios true, web generate false, windows generate false. Both were lost when commit c3ca5ccb rewrote pubspec.yaml. Do NOT regenerate the Android PNGs (ee0be1e4 is correct). Don't run the icon generator for iOS in this build unless asked.

Rules unchanged (NET-400/401/404/406). EXECUTE_DONE_P7_V8_18_14.md + NET-409 cover every item with file:line; phone checks stay open until verified on Eric's USB Android test phone. Baton back to GROKCOS.
OVER
