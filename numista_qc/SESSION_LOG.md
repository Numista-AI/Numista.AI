[2026-08-24 18:09:28] QA project: numista-qc
[2026-08-24 18:09:28] Credential email: qc-runner@numista-qc.iam.gserviceaccount.com (not forbidden)
[2026-08-24 18:09:28] Running seed_qc_fixtures.py --check...
[2026-08-25 08:59:07] QA project: numista-qc
[2026-08-25 08:59:09] Running seed_qc_fixtures.py --check...
[2026-08-25 09:01:14] QA project: numista-qc
[2026-08-25 09:01:14] Running seed_qc_fixtures.py --check...
[2026-08-25 09:01:22] Fixtures OK.
[2026-08-25 09:01:22] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 09:01:23] === LAYER 1: UX Visual Guard ===
[2026-08-25 09:08:07] ? injected env (2) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:08:07] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:08:07] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:08:07] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:08:07] 
[2026-08-25 09:08:07] Running 10 tests using 1 worker
[2026-08-25 09:08:07] 
[2026-08-25 09:08:07] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:08:07] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:07] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:08:07] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:07] 
[2026-08-25 09:08:07]   x   1 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (129ms)
[2026-08-25 09:08:07] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:08:07] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:07] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:08:07] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:07] 
[2026-08-25 09:08:08]   x   2 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (retry #1) (117ms)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:08:08]   x   3 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (1.7m)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:08:08]   x   4 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (retry #1) (1.7m)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Sidebar nav item. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Main content header. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Collection card text. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Bottom nav label. Check CORS / CanvasKit config.
[2026-08-25 09:08:08]   x   5 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:108:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (44.0s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Sidebar nav item. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Main content header. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Collection card text. Check CORS / CanvasKit config.
[2026-08-25 09:08:08] [contrast_guard] Canvas read blocked for region: Bottom nav label. Check CORS / CanvasKit config.
[2026-08-25 09:08:08]   x   6 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:108:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (retry #1) (11.1s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:08:08]   x   7 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:160:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (11.3s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:08:08]   x   8 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:160:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (retry #1) (11.6s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:08:08]   x   9 [chromium] › layer_1_ux_visual\layout_guard.spec.js:43:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport (12.1s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:08:08]   x  10 [chromium] › layer_1_ux_visual\layout_guard.spec.js:43:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport (retry #1) (12.5s)
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:08:08] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:08:08]   ok 11 [chromium] › layer_1_ux_visual\layout_guard.spec.js:59:3 › Layout Guard - 1920x1080 Desktop › No negative top/left on flt-glass-pane (not shifted off-screen) (10.7s)
[2026-08-25 09:08:08]   ok 12 [chromium] › layer_1_ux_visual\layout_guard.spec.js:73:3 › Layout Guard - 1920x1080 Desktop › Flutter renders in release mode (not debug banner) (9.8s)
[2026-08-25 09:08:09]   ok 13 [chromium] › layer_1_ux_visual\layout_guard.spec.js:84:3 › Layout Guard - 1920x1080 Desktop › Page title is set (not blank or default) (9.8s)
[2026-08-25 09:08:09] ? injected env (0) from ..\numista_tests\.env // tip: ? encrypted .env [www.dotenvx.com]
[2026-08-25 09:08:09] [theme_switch_guard] Theme toggle button not found at 1920x1080. Skipping toggle test.
[2026-08-25 09:08:09]   -  14 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:71:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle
[2026-08-25 09:08:09]   -  15 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:108:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]   1) [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty 
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     Error: coin_data_audit.py exited 2.
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     Output:
[2026-08-25 09:08:09]     python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     expect(received).toBe(expected) // Object.is equality
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     Expected: 0
[2026-08-25 09:08:09]     Received: 2
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]       65 |       exitCode,
[2026-08-25 09:08:09]       66 |       'coin_data_audit.py exited ' + exitCode + '.\n\nOutput:\n' + output
[2026-08-25 09:08:09]     > 67 |     ).toBe(0);
[2026-08-25 09:08:09]          |       ^
[2026-08-25 09:08:09]       68 |
[2026-08-25 09:08:09]       69 |     expect(
[2026-08-25 09:08:09]       70 |       sentinelWorking,
[2026-08-25 09:08:09]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:67:7
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     Error Context: screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\error-context.md
[2026-08-25 09:08:09] 
[2026-08-25 09:08:09]     attachment #2: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:09]     screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\trace.zip
[2026-08-25 09:08:09]     Usage:
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\trace.zip
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     Error: coin_data_audit.py exited 2.
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     Output:
[2026-08-25 09:08:10]     python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     expect(received).toBe(expected) // Object.is equality
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     Expected: 0
[2026-08-25 09:08:10]     Received: 2
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]       65 |       exitCode,
[2026-08-25 09:08:10]       66 |       'coin_data_audit.py exited ' + exitCode + '.\n\nOutput:\n' + output
[2026-08-25 09:08:10]     > 67 |     ).toBe(0);
[2026-08-25 09:08:10]          |       ^
[2026-08-25 09:08:10]       68 |
[2026-08-25 09:08:10]       69 |     expect(
[2026-08-25 09:08:10]       70 |       sentinelWorking,
[2026-08-25 09:08:10]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:67:7
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     Error Context: screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\error-context.md
[2026-08-25 09:08:10] 
[2026-08-25 09:08:10]     attachment #2: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:10]     screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\trace.zip
[2026-08-25 09:08:10]     Usage:
[2026-08-25 09:08:10] 
[2026-08-25 09:08:11]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\trace.zip
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]   2) [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]     Test timeout of 90000ms exceeded.
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]       80 |
[2026-08-25 09:08:11]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:08:11]     > 82 |     await page.waitForFunction(
[2026-08-25 09:08:11]          |                ^
[2026-08-25 09:08:11]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:08:11]       84 |       { timeout: 20000 }
[2026-08-25 09:08:11]       85 |     );
[2026-08-25 09:08:11]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:11]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\test-failed-1.png
[2026-08-25 09:08:11]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:11] 
[2026-08-25 09:08:11]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:11]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\video.webm
[2026-08-25 09:08:11]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:11] 
[2026-08-25 09:08:12]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\error-context.md
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:12]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:08:12]     Usage:
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]     Test timeout of 90000ms exceeded.
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:08:12] 
[2026-08-25 09:08:12]       80 |
[2026-08-25 09:08:12]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:08:12]     > 82 |     await page.waitForFunction(
[2026-08-25 09:08:12]          |                ^
[2026-08-25 09:08:12]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:08:12]       84 |       { timeout: 20000 }
[2026-08-25 09:08:12]       85 |     );
[2026-08-25 09:08:13]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:13]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\test-failed-1.png
[2026-08-25 09:08:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:13]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\video.webm
[2026-08-25 09:08:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\error-context.md
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:13]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:08:13]     Usage:
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]   3) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:108:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:08:13] 
[2026-08-25 09:08:13]     Error: CANVAS_UNREADABLE: All 4 regions returned null. CanvasKit canvas may be cross-origin blocked. Cannot assert contrast.
[2026-08-25 09:08:14] 
[2026-08-25 09:08:14]       142 |     if (blockedRegions.length === SAMPLE_REGIONS.length) {
[2026-08-25 09:08:14]       143 |       // All regions blocked - canvas not readable. Report as CANVAS_UNREADABLE, not PASS.
[2026-08-25 09:08:14]     > 144 |       throw new Error(
[2026-08-25 09:08:14]           |             ^
[2026-08-25 09:08:14]       145 |         'CANVAS_UNREADABLE: All ' + SAMPLE_REGIONS.length + ' regions returned null. ' +
[2026-08-25 09:08:14]       146 |         'CanvasKit canvas may be cross-origin blocked. Cannot assert contrast.'
[2026-08-25 09:08:14]       147 |       );
[2026-08-25 09:08:14]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:144:13
[2026-08-25 09:08:14] 
[2026-08-25 09:08:14]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:14]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:08:14]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:14] 
[2026-08-25 09:08:14]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:14]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:08:14]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:14] 
[2026-08-25 09:08:14]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:08:14] 
[2026-08-25 09:08:14]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:14]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:08:14]     Usage:
[2026-08-25 09:08:14] 
[2026-08-25 09:08:15]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     Error: CANVAS_UNREADABLE: All 4 regions returned null. CanvasKit canvas may be cross-origin blocked. Cannot assert contrast.
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]       142 |     if (blockedRegions.length === SAMPLE_REGIONS.length) {
[2026-08-25 09:08:15]       143 |       // All regions blocked - canvas not readable. Report as CANVAS_UNREADABLE, not PASS.
[2026-08-25 09:08:15]     > 144 |       throw new Error(
[2026-08-25 09:08:15]           |             ^
[2026-08-25 09:08:15]       145 |         'CANVAS_UNREADABLE: All ' + SAMPLE_REGIONS.length + ' regions returned null. ' +
[2026-08-25 09:08:15]       146 |         'CanvasKit canvas may be cross-origin blocked. Cannot assert contrast.'
[2026-08-25 09:08:15]       147 |       );
[2026-08-25 09:08:15]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:144:13
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:15]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:08:15]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:15]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:08:15]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:15]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:08:15]     Usage:
[2026-08-25 09:08:15] 
[2026-08-25 09:08:15]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:08:15] 
[2026-08-25 09:08:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]   4) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:160:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     Error: CANVAS_UNREADABLE: All regions blocked. Cannot assert contrast.
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]       190 |
[2026-08-25 09:08:16]       191 |     if (blockedRegions.length === SAMPLE_REGIONS.length) {
[2026-08-25 09:08:16]     > 192 |       throw new Error('CANVAS_UNREADABLE: All regions blocked. Cannot assert contrast.');
[2026-08-25 09:08:16]           |             ^
[2026-08-25 09:08:16]       193 |     }
[2026-08-25 09:08:16]       194 |
[2026-08-25 09:08:16]       195 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:08:16]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:192:13
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:08:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:08:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:08:16]     Usage:
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:16] 
[2026-08-25 09:08:16]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:08:16] 
[2026-08-25 09:08:17]     Error: CANVAS_UNREADABLE: All regions blocked. Cannot assert contrast.
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]       190 |
[2026-08-25 09:08:17]       191 |     if (blockedRegions.length === SAMPLE_REGIONS.length) {
[2026-08-25 09:08:17]     > 192 |       throw new Error('CANVAS_UNREADABLE: All regions blocked. Cannot assert contrast.');
[2026-08-25 09:08:17]           |             ^
[2026-08-25 09:08:17]       193 |     }
[2026-08-25 09:08:17]       194 |
[2026-08-25 09:08:17]       195 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:08:17]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:192:13
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:17]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:08:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:17]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:08:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:17]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:08:17]     Usage:
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]   5) [chromium] › layer_1_ux_visual\layout_guard.spec.js:43:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport 
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     Error: Flutter view width < 1800px - layout may be broken
[2026-08-25 09:08:17] 
[2026-08-25 09:08:17]     expect(received).toBeGreaterThan(expected)
[2026-08-25 09:08:17] 
[2026-08-25 09:08:18]     Expected: > 1800
[2026-08-25 09:08:18]     Received:   1280
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]       53 |     });
[2026-08-25 09:08:18]       54 |     expect(pane, 'flt-glass-pane / flutter-view not found in DOM').not.toBeNull();
[2026-08-25 09:08:18]     > 55 |     expect(pane.width, 'Flutter view width < 1800px - layout may be broken').toBeGreaterThan(1800);
[2026-08-25 09:08:18]          |                                                                              ^
[2026-08-25 09:08:18]       56 |     expect(pane.height, 'Flutter view height < 900px - layout may be broken').toBeGreaterThan(900);
[2026-08-25 09:08:18]       57 |   });
[2026-08-25 09:08:18]       58 |
[2026-08-25 09:08:18]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\layout_guard.spec.js:55:78
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:18]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium\test-failed-1.png
[2026-08-25 09:08:18]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:18]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium\video.webm
[2026-08-25 09:08:18]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     Error Context: screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium\error-context.md
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:18]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium\trace.zip
[2026-08-25 09:08:18]     Usage:
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]         npx playwright show-trace screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium\trace.zip
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:08:18] 
[2026-08-25 09:08:18]     Error: Flutter view width < 1800px - layout may be broken
[2026-08-25 09:08:18] 
[2026-08-25 09:08:19]     expect(received).toBeGreaterThan(expected)
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     Expected: > 1800
[2026-08-25 09:08:19]     Received:   1280
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]       53 |     });
[2026-08-25 09:08:19]       54 |     expect(pane, 'flt-glass-pane / flutter-view not found in DOM').not.toBeNull();
[2026-08-25 09:08:19]     > 55 |     expect(pane.width, 'Flutter view width < 1800px - layout may be broken').toBeGreaterThan(1800);
[2026-08-25 09:08:19]          |                                                                              ^
[2026-08-25 09:08:19]       56 |     expect(pane.height, 'Flutter view height < 900px - layout may be broken').toBeGreaterThan(900);
[2026-08-25 09:08:19]       57 |   });
[2026-08-25 09:08:19]       58 |
[2026-08-25 09:08:19]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\layout_guard.spec.js:55:78
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:08:19]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium-retry1\test-failed-1.png
[2026-08-25 09:08:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:08:19]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium-retry1\video.webm
[2026-08-25 09:08:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     Error Context: screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium-retry1\error-context.md
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:08:19]     screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium-retry1\trace.zip
[2026-08-25 09:08:19]     Usage:
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]         npx playwright show-trace screenshots\layer_1_ux_visual-layout_g-4283a-ass-pane-fills-the-viewport-chromium-retry1\trace.zip
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:08:19] 
[2026-08-25 09:08:19]   5 failed
[2026-08-25 09:08:20]     [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty 
[2026-08-25 09:08:20]     [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:08:20]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:108:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:08:20]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:160:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:08:20]     [chromium] › layer_1_ux_visual\layout_guard.spec.js:43:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport 
[2026-08-25 09:08:20]   2 skipped
[2026-08-25 09:08:20]   3 passed (6.4m)
[2026-08-25 09:08:20] LAYER 1: FAIL
[2026-08-25 09:08:20] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 09:12:45] QA project: numista-qc
[2026-08-25 09:12:45] Running seed_qc_fixtures.py --check...
[2026-08-25 09:12:53] Fixtures OK.
[2026-08-25 09:12:53] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 09:12:53] === LAYER 1: UX Visual Guard ===
[2026-08-25 09:26:53] ? injected env (2) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:26:53] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:26:54] 
[2026-08-25 09:26:54] Running 10 tests using 1 worker
[2026-08-25 09:26:54] 
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:26:54] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:54] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:26:54] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:54] 
[2026-08-25 09:26:54]   x   1 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (125ms)
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:26:54] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:54] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:26:54] python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:54] 
[2026-08-25 09:26:54]   x   2 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (retry #1) (184ms)
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:26:54]   x   3 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (1.6m)
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? encrypted .env [www.dotenvx.com]
[2026-08-25 09:26:54]   x   4 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (retry #1) (1.6m)
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:54] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:26:54] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:26:54] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:26:54] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:26:54] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":11,"b":12} ratio=1.03
[2026-08-25 09:26:54]   x   5 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (15.3s)
[2026-08-25 09:26:54] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:55] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:26:55] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:26:55] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:26:55] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:26:55] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":11,"b":12} ratio=1.03
[2026-08-25 09:26:55]   x   6 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (retry #1) (15.4s)
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:26:55] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:26:55] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:26:55] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:26:55] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:26:55] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":11,"b":12} ratio=1.03
[2026-08-25 09:26:55]   x   7 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (15.7s)
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? encrypted .env [www.dotenvx.com]
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:26:55] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:26:55] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:26:55] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:26:55] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:26:55] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":11,"b":12} ratio=1.03
[2026-08-25 09:26:55]   x   8 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (retry #1) (15.2s)
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:26:55]   ok  9 [chromium] › layer_1_ux_visual\layout_guard.spec.js:63:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport (12.4s)
[2026-08-25 09:26:55]   ok 10 [chromium] › layer_1_ux_visual\layout_guard.spec.js:79:3 › Layout Guard - 1920x1080 Desktop › No negative top/left on flt-glass-pane (not shifted off-screen) (17.6s)
[2026-08-25 09:26:55]   ok 11 [chromium] › layer_1_ux_visual\layout_guard.spec.js:93:3 › Layout Guard - 1920x1080 Desktop › Flutter renders in release mode (not debug banner) (18.5s)
[2026-08-25 09:26:55]   ok 12 [chromium] › layer_1_ux_visual\layout_guard.spec.js:104:3 › Layout Guard - 1920x1080 Desktop › Page title is set (not blank or default) (12.0s)
[2026-08-25 09:26:55] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:26:55]   x  13 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:71:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle (1.6m)
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:56]   x  14 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:71:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle (retry #1) (1.7m)
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:56]   x  15 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:108:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle (3.0m)
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:26:56] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:26:56]   x  16 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:108:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle (retry #1) (1.7m)
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]   1) [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty 
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]     Error: coin_data_audit.py exited 2.
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]     Output:
[2026-08-25 09:26:56]     python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]     expect(received).toBe(expected) // Object.is equality
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]     Expected: 0
[2026-08-25 09:26:56]     Received: 2
[2026-08-25 09:26:56] 
[2026-08-25 09:26:56]       65 |       exitCode,
[2026-08-25 09:26:56]       66 |       'coin_data_audit.py exited ' + exitCode + '.\n\nOutput:\n' + output
[2026-08-25 09:26:56]     > 67 |     ).toBe(0);
[2026-08-25 09:26:56]          |       ^
[2026-08-25 09:26:56]       68 |
[2026-08-25 09:26:56]       69 |     expect(
[2026-08-25 09:26:56]       70 |       sentinelWorking,
[2026-08-25 09:26:56]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:67:7
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     Error Context: screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\error-context.md
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     attachment #2: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:26:57]     screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\trace.zip
[2026-08-25 09:26:57]     Usage:
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium\trace.zip
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     Error: coin_data_audit.py exited 2.
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     Output:
[2026-08-25 09:26:57]     python: can't open file 'C:\\Users\\ericd\\Documents\\MyVertexProject\\layer_3_data\\coin_data_audit.py': [Errno 2] No such file or directory
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     expect(received).toBe(expected) // Object.is equality
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]     Expected: 0
[2026-08-25 09:26:57]     Received: 2
[2026-08-25 09:26:57] 
[2026-08-25 09:26:57]       65 |       exitCode,
[2026-08-25 09:26:57]       66 |       'coin_data_audit.py exited ' + exitCode + '.\n\nOutput:\n' + output
[2026-08-25 09:26:57]     > 67 |     ).toBe(0);
[2026-08-25 09:26:57]          |       ^
[2026-08-25 09:26:57]       68 |
[2026-08-25 09:26:57]       69 |     expect(
[2026-08-25 09:26:58]       70 |       sentinelWorking,
[2026-08-25 09:26:58]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:67:7
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]     Error Context: screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\error-context.md
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]     attachment #2: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:26:58]     screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\trace.zip
[2026-08-25 09:26:58]     Usage:
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-40294-have-all-title-fields-empty-chromium-retry1\trace.zip
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]   2) [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]     Test timeout of 90000ms exceeded.
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:26:58] 
[2026-08-25 09:26:58]       80 |
[2026-08-25 09:26:58]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:26:58]     > 82 |     await page.waitForFunction(
[2026-08-25 09:26:58]          |                ^
[2026-08-25 09:26:58]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:26:58]       84 |       { timeout: 20000 }
[2026-08-25 09:26:58]       85 |     );
[2026-08-25 09:26:59]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:26:59]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\test-failed-1.png
[2026-08-25 09:26:59]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:26:59]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\video.webm
[2026-08-25 09:26:59]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\error-context.md
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:26:59]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:26:59]     Usage:
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:26:59] 
[2026-08-25 09:26:59]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:26:59] 
[2026-08-25 09:27:00]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:27:00] 
[2026-08-25 09:27:00]     Test timeout of 90000ms exceeded.
[2026-08-25 09:27:00] 
[2026-08-25 09:27:00]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:27:00] 
[2026-08-25 09:27:00]       80 |
[2026-08-25 09:27:00]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:27:00]     > 82 |     await page.waitForFunction(
[2026-08-25 09:27:00]          |                ^
[2026-08-25 09:27:00]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:27:00]       84 |       { timeout: 20000 }
[2026-08-25 09:27:00]       85 |     );
[2026-08-25 09:27:00]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:27:00] 
[2026-08-25 09:27:00]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:00]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\test-failed-1.png
[2026-08-25 09:27:00]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:00] 
[2026-08-25 09:27:01]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:01]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\video.webm
[2026-08-25 09:27:01]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\error-context.md
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:01]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:27:01]     Usage:
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]   3) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:27:01] 
[2026-08-25 09:27:01]     Error: Contrast failures in Light mode:
[2026-08-25 09:27:01]     [
[2026-08-25 09:27:02]       {
[2026-08-25 09:27:02]         "name": "Sidebar nav item",
[2026-08-25 09:27:02]         "ratio": "1.01",
[2026-08-25 09:27:02]         "fg": {
[2026-08-25 09:27:02]           "r": 1,
[2026-08-25 09:27:02]           "g": 1,
[2026-08-25 09:27:02]           "b": 1
[2026-08-25 09:27:02]         },
[2026-08-25 09:27:02]         "bg": {
[2026-08-25 09:27:02]           "r": 3,
[2026-08-25 09:27:02]           "g": 3,
[2026-08-25 09:27:02]           "b": 4
[2026-08-25 09:27:02]         }
[2026-08-25 09:27:02]       },
[2026-08-25 09:27:02]       {
[2026-08-25 09:27:02]         "name": "Main content header",
[2026-08-25 09:27:02]         "ratio": "1.02",
[2026-08-25 09:27:02]         "fg": {
[2026-08-25 09:27:02]           "r": 2,
[2026-08-25 09:27:03]           "g": 2,
[2026-08-25 09:27:03]           "b": 4
[2026-08-25 09:27:03]         },
[2026-08-25 09:27:03]         "bg": {
[2026-08-25 09:27:03]           "r": 2,
[2026-08-25 09:27:03]           "g": 6,
[2026-08-25 09:27:03]           "b": 14
[2026-08-25 09:27:03]         }
[2026-08-25 09:27:03]       },
[2026-08-25 09:27:03]       {
[2026-08-25 09:27:03]         "name": "Collection card text",
[2026-08-25 09:27:03]         "ratio": "1.00",
[2026-08-25 09:27:03]         "fg": {
[2026-08-25 09:27:03]           "r": 0,
[2026-08-25 09:27:03]           "g": 1,
[2026-08-25 09:27:03]           "b": 2
[2026-08-25 09:27:03]         },
[2026-08-25 09:27:03]         "bg": {
[2026-08-25 09:27:03]           "r": 0,
[2026-08-25 09:27:04]           "g": 1,
[2026-08-25 09:27:04]           "b": 2
[2026-08-25 09:27:04]         }
[2026-08-25 09:27:04]       },
[2026-08-25 09:27:04]       {
[2026-08-25 09:27:04]         "name": "Bottom nav label",
[2026-08-25 09:27:04]         "ratio": "1.03",
[2026-08-25 09:27:04]         "fg": {
[2026-08-25 09:27:04]           "r": 16,
[2026-08-25 09:27:04]           "g": 16,
[2026-08-25 09:27:04]           "b": 16
[2026-08-25 09:27:04]         },
[2026-08-25 09:27:04]         "bg": {
[2026-08-25 09:27:04]           "r": 11,
[2026-08-25 09:27:04]           "g": 11,
[2026-08-25 09:27:04]           "b": 12
[2026-08-25 09:27:04]         }
[2026-08-25 09:27:04]       }
[2026-08-25 09:27:04]     ]
[2026-08-25 09:27:04] 
[2026-08-25 09:27:04]     expect(received).toHaveLength(expected)
[2026-08-25 09:27:04] 
[2026-08-25 09:27:04]     Expected length: 0
[2026-08-25 09:27:04]     Received length: 4
[2026-08-25 09:27:04]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 11, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:27:04] 
[2026-08-25 09:27:05]       176 |     }
[2026-08-25 09:27:05]       177 |
[2026-08-25 09:27:05]     > 178 |     expect(failedRegions, 'Contrast failures in Light mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:27:05]           |                                                                                                          ^
[2026-08-25 09:27:05]       179 |   });
[2026-08-25 09:27:05]       180 | });
[2026-08-25 09:27:05]       181 |
[2026-08-25 09:27:05]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:178:106
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:05]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:27:05]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:05]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:27:05]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:05]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:27:05]     Usage:
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:27:05] 
[2026-08-25 09:27:05]     Error: Contrast failures in Light mode:
[2026-08-25 09:27:05]     [
[2026-08-25 09:27:05]       {
[2026-08-25 09:27:06]         "name": "Sidebar nav item",
[2026-08-25 09:27:06]         "ratio": "1.01",
[2026-08-25 09:27:06]         "fg": {
[2026-08-25 09:27:06]           "r": 1,
[2026-08-25 09:27:06]           "g": 1,
[2026-08-25 09:27:06]           "b": 1
[2026-08-25 09:27:06]         },
[2026-08-25 09:27:06]         "bg": {
[2026-08-25 09:27:06]           "r": 3,
[2026-08-25 09:27:06]           "g": 3,
[2026-08-25 09:27:06]           "b": 4
[2026-08-25 09:27:06]         }
[2026-08-25 09:27:06]       },
[2026-08-25 09:27:06]       {
[2026-08-25 09:27:06]         "name": "Main content header",
[2026-08-25 09:27:06]         "ratio": "1.02",
[2026-08-25 09:27:06]         "fg": {
[2026-08-25 09:27:07]           "r": 2,
[2026-08-25 09:27:07]           "g": 2,
[2026-08-25 09:27:07]           "b": 4
[2026-08-25 09:27:07]         },
[2026-08-25 09:27:07]         "bg": {
[2026-08-25 09:27:07]           "r": 2,
[2026-08-25 09:27:07]           "g": 6,
[2026-08-25 09:27:07]           "b": 14
[2026-08-25 09:27:07]         }
[2026-08-25 09:27:07]       },
[2026-08-25 09:27:07]       {
[2026-08-25 09:27:07]         "name": "Collection card text",
[2026-08-25 09:27:07]         "ratio": "1.00",
[2026-08-25 09:27:07]         "fg": {
[2026-08-25 09:27:07]           "r": 0,
[2026-08-25 09:27:07]           "g": 1,
[2026-08-25 09:27:07]           "b": 2
[2026-08-25 09:27:07]         },
[2026-08-25 09:27:08]         "bg": {
[2026-08-25 09:27:08]           "r": 0,
[2026-08-25 09:27:08]           "g": 1,
[2026-08-25 09:27:08]           "b": 2
[2026-08-25 09:27:08]         }
[2026-08-25 09:27:08]       },
[2026-08-25 09:27:08]       {
[2026-08-25 09:27:08]         "name": "Bottom nav label",
[2026-08-25 09:27:08]         "ratio": "1.03",
[2026-08-25 09:27:08]         "fg": {
[2026-08-25 09:27:08]           "r": 16,
[2026-08-25 09:27:08]           "g": 16,
[2026-08-25 09:27:08]           "b": 16
[2026-08-25 09:27:08]         },
[2026-08-25 09:27:08]         "bg": {
[2026-08-25 09:27:08]           "r": 11,
[2026-08-25 09:27:08]           "g": 11,
[2026-08-25 09:27:08]           "b": 12
[2026-08-25 09:27:08]         }
[2026-08-25 09:27:08]       }
[2026-08-25 09:27:08]     ]
[2026-08-25 09:27:09] 
[2026-08-25 09:27:09]     expect(received).toHaveLength(expected)
[2026-08-25 09:27:09] 
[2026-08-25 09:27:09]     Expected length: 0
[2026-08-25 09:27:09]     Received length: 4
[2026-08-25 09:27:09]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 11, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:27:09] 
[2026-08-25 09:27:09]       176 |     }
[2026-08-25 09:27:09]       177 |
[2026-08-25 09:27:09]     > 178 |     expect(failedRegions, 'Contrast failures in Light mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:27:09]           |                                                                                                          ^
[2026-08-25 09:27:09]       179 |   });
[2026-08-25 09:27:09]       180 | });
[2026-08-25 09:27:09]       181 |
[2026-08-25 09:27:09]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:178:106
[2026-08-25 09:27:09] 
[2026-08-25 09:27:09]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:09]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:27:09]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:09] 
[2026-08-25 09:27:09]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:09]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:27:09]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:10]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:27:10]     Usage:
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]   4) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:27:10] 
[2026-08-25 09:27:10]     Error: Contrast failures in Dark mode:
[2026-08-25 09:27:10]     [
[2026-08-25 09:27:10]       {
[2026-08-25 09:27:10]         "name": "Sidebar nav item",
[2026-08-25 09:27:10]         "ratio": "1.01",
[2026-08-25 09:27:10]         "fg": {
[2026-08-25 09:27:10]           "r": 1,
[2026-08-25 09:27:10]           "g": 1,
[2026-08-25 09:27:10]           "b": 1
[2026-08-25 09:27:10]         },
[2026-08-25 09:27:11]         "bg": {
[2026-08-25 09:27:11]           "r": 3,
[2026-08-25 09:27:11]           "g": 3,
[2026-08-25 09:27:11]           "b": 4
[2026-08-25 09:27:11]         }
[2026-08-25 09:27:11]       },
[2026-08-25 09:27:11]       {
[2026-08-25 09:27:11]         "name": "Main content header",
[2026-08-25 09:27:11]         "ratio": "1.02",
[2026-08-25 09:27:11]         "fg": {
[2026-08-25 09:27:11]           "r": 2,
[2026-08-25 09:27:11]           "g": 2,
[2026-08-25 09:27:11]           "b": 4
[2026-08-25 09:27:11]         },
[2026-08-25 09:27:11]         "bg": {
[2026-08-25 09:27:11]           "r": 2,
[2026-08-25 09:27:11]           "g": 6,
[2026-08-25 09:27:11]           "b": 14
[2026-08-25 09:27:11]         }
[2026-08-25 09:27:11]       },
[2026-08-25 09:27:11]       {
[2026-08-25 09:27:11]         "name": "Collection card text",
[2026-08-25 09:27:11]         "ratio": "1.00",
[2026-08-25 09:27:11]         "fg": {
[2026-08-25 09:27:11]           "r": 0,
[2026-08-25 09:27:11]           "g": 1,
[2026-08-25 09:27:11]           "b": 2
[2026-08-25 09:27:11]         },
[2026-08-25 09:27:11]         "bg": {
[2026-08-25 09:27:12]           "r": 0,
[2026-08-25 09:27:12]           "g": 1,
[2026-08-25 09:27:12]           "b": 2
[2026-08-25 09:27:12]         }
[2026-08-25 09:27:12]       },
[2026-08-25 09:27:12]       {
[2026-08-25 09:27:12]         "name": "Bottom nav label",
[2026-08-25 09:27:12]         "ratio": "1.03",
[2026-08-25 09:27:12]         "fg": {
[2026-08-25 09:27:12]           "r": 16,
[2026-08-25 09:27:12]           "g": 16,
[2026-08-25 09:27:12]           "b": 16
[2026-08-25 09:27:12]         },
[2026-08-25 09:27:12]         "bg": {
[2026-08-25 09:27:12]           "r": 11,
[2026-08-25 09:27:12]           "g": 11,
[2026-08-25 09:27:12]           "b": 12
[2026-08-25 09:27:12]         }
[2026-08-25 09:27:12]       }
[2026-08-25 09:27:12]     ]
[2026-08-25 09:27:12] 
[2026-08-25 09:27:12]     expect(received).toHaveLength(expected)
[2026-08-25 09:27:12] 
[2026-08-25 09:27:12]     Expected length: 0
[2026-08-25 09:27:12]     Received length: 4
[2026-08-25 09:27:12]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 11, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:27:12] 
[2026-08-25 09:27:12]       211 |     }
[2026-08-25 09:27:12]       212 |
[2026-08-25 09:27:12]     > 213 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:27:12]           |                                                                                                         ^
[2026-08-25 09:27:13]       214 |   });
[2026-08-25 09:27:13]       215 | });
[2026-08-25 09:27:13]       216 |
[2026-08-25 09:27:13]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:213:105
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:13]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:27:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:13]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:27:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:13]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:27:13]     Usage:
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:27:13] 
[2026-08-25 09:27:13]     Error: Contrast failures in Dark mode:
[2026-08-25 09:27:13]     [
[2026-08-25 09:27:13]       {
[2026-08-25 09:27:13]         "name": "Sidebar nav item",
[2026-08-25 09:27:13]         "ratio": "1.01",
[2026-08-25 09:27:14]         "fg": {
[2026-08-25 09:27:14]           "r": 1,
[2026-08-25 09:27:14]           "g": 1,
[2026-08-25 09:27:14]           "b": 1
[2026-08-25 09:27:14]         },
[2026-08-25 09:27:14]         "bg": {
[2026-08-25 09:27:14]           "r": 3,
[2026-08-25 09:27:14]           "g": 3,
[2026-08-25 09:27:14]           "b": 4
[2026-08-25 09:27:14]         }
[2026-08-25 09:27:14]       },
[2026-08-25 09:27:14]       {
[2026-08-25 09:27:14]         "name": "Main content header",
[2026-08-25 09:27:14]         "ratio": "1.02",
[2026-08-25 09:27:14]         "fg": {
[2026-08-25 09:27:14]           "r": 2,
[2026-08-25 09:27:14]           "g": 2,
[2026-08-25 09:27:14]           "b": 4
[2026-08-25 09:27:14]         },
[2026-08-25 09:27:14]         "bg": {
[2026-08-25 09:27:14]           "r": 2,
[2026-08-25 09:27:14]           "g": 6,
[2026-08-25 09:27:14]           "b": 14
[2026-08-25 09:27:14]         }
[2026-08-25 09:27:14]       },
[2026-08-25 09:27:14]       {
[2026-08-25 09:27:14]         "name": "Collection card text",
[2026-08-25 09:27:14]         "ratio": "1.00",
[2026-08-25 09:27:14]         "fg": {
[2026-08-25 09:27:14]           "r": 0,
[2026-08-25 09:27:14]           "g": 1,
[2026-08-25 09:27:14]           "b": 2
[2026-08-25 09:27:15]         },
[2026-08-25 09:27:15]         "bg": {
[2026-08-25 09:27:15]           "r": 0,
[2026-08-25 09:27:15]           "g": 1,
[2026-08-25 09:27:15]           "b": 2
[2026-08-25 09:27:15]         }
[2026-08-25 09:27:15]       },
[2026-08-25 09:27:15]       {
[2026-08-25 09:27:15]         "name": "Bottom nav label",
[2026-08-25 09:27:15]         "ratio": "1.03",
[2026-08-25 09:27:15]         "fg": {
[2026-08-25 09:27:15]           "r": 16,
[2026-08-25 09:27:15]           "g": 16,
[2026-08-25 09:27:15]           "b": 16
[2026-08-25 09:27:15]         },
[2026-08-25 09:27:15]         "bg": {
[2026-08-25 09:27:15]           "r": 11,
[2026-08-25 09:27:15]           "g": 11,
[2026-08-25 09:27:15]           "b": 12
[2026-08-25 09:27:15]         }
[2026-08-25 09:27:15]       }
[2026-08-25 09:27:15]     ]
[2026-08-25 09:27:15] 
[2026-08-25 09:27:15]     expect(received).toHaveLength(expected)
[2026-08-25 09:27:15] 
[2026-08-25 09:27:15]     Expected length: 0
[2026-08-25 09:27:15]     Received length: 4
[2026-08-25 09:27:15]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 11, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:27:15] 
[2026-08-25 09:27:15]       211 |     }
[2026-08-25 09:27:16]       212 |
[2026-08-25 09:27:16]     > 213 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:27:16]           |                                                                                                         ^
[2026-08-25 09:27:16]       214 |   });
[2026-08-25 09:27:16]       215 | });
[2026-08-25 09:27:16]       216 |
[2026-08-25 09:27:16]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:213:105
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:27:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:27:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:16]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:27:16]     Usage:
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]   5) [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:71:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle 
[2026-08-25 09:27:16] 
[2026-08-25 09:27:16]     Test timeout of 90000ms exceeded while running "beforeEach" hook.
[2026-08-25 09:27:16] 
[2026-08-25 09:27:17]       64 |
[2026-08-25 09:27:17]       65 | test.describe('Theme Switch Guard', () => {
[2026-08-25 09:27:17]     > 66 |   test.beforeEach(async ({ page }) => {
[2026-08-25 09:27:17]          |        ^
[2026-08-25 09:27:17]       67 |     await page.goto('https://numista.ai');
[2026-08-25 09:27:17]       68 |     await signInAndWait(page);
[2026-08-25 09:27:17]       69 |   });
[2026-08-25 09:27:17]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:66:8
[2026-08-25 09:27:17] 
[2026-08-25 09:27:17]     Error: page.waitForTimeout: Target page, context or browser has been closed
[2026-08-25 09:27:17] 
[2026-08-25 09:27:17]       49 |     if (await modalButtons.first().isVisible({ timeout: 1500 }).catch(() => false)) {
[2026-08-25 09:27:17]       50 |       await modalButtons.first().click().catch(() => {});
[2026-08-25 09:27:17]     > 51 |       await page.waitForTimeout(1000);
[2026-08-25 09:27:17]          |                  ^
[2026-08-25 09:27:17]       52 |     }
[2026-08-25 09:27:17]       53 |   }
[2026-08-25 09:27:17]       54 | }
[2026-08-25 09:27:17]         at signInAndWait (C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:51:18)
[2026-08-25 09:27:17]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:68:5
[2026-08-25 09:27:17] 
[2026-08-25 09:27:17]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:17]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium\test-failed-1.png
[2026-08-25 09:27:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:17] 
[2026-08-25 09:27:17]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:17]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium\video.webm
[2026-08-25 09:27:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     Error Context: screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium\error-context.md
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:18]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium\trace.zip
[2026-08-25 09:27:18]     Usage:
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]         npx playwright show-trace screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium\trace.zip
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     Test timeout of 90000ms exceeded while running "beforeEach" hook.
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]       64 |
[2026-08-25 09:27:18]       65 | test.describe('Theme Switch Guard', () => {
[2026-08-25 09:27:18]     > 66 |   test.beforeEach(async ({ page }) => {
[2026-08-25 09:27:18]          |        ^
[2026-08-25 09:27:18]       67 |     await page.goto('https://numista.ai');
[2026-08-25 09:27:18]       68 |     await signInAndWait(page);
[2026-08-25 09:27:18]       69 |   });
[2026-08-25 09:27:18]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:66:8
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]     Error: page.waitForTimeout: Target page, context or browser has been closed
[2026-08-25 09:27:18] 
[2026-08-25 09:27:18]       49 |     if (await modalButtons.first().isVisible({ timeout: 1500 }).catch(() => false)) {
[2026-08-25 09:27:19]       50 |       await modalButtons.first().click().catch(() => {});
[2026-08-25 09:27:19]     > 51 |       await page.waitForTimeout(1000);
[2026-08-25 09:27:19]          |                  ^
[2026-08-25 09:27:19]       52 |     }
[2026-08-25 09:27:19]       53 |   }
[2026-08-25 09:27:19]       54 | }
[2026-08-25 09:27:19]         at signInAndWait (C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:51:18)
[2026-08-25 09:27:19]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:68:5
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:19]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium-retry1\test-failed-1.png
[2026-08-25 09:27:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:19]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium-retry1\video.webm
[2026-08-25 09:27:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]     Error Context: screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium-retry1\error-context.md
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:19]     screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium-retry1\trace.zip
[2026-08-25 09:27:19]     Usage:
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]         npx playwright show-trace screenshots\layer_1_ux_visual-theme_sw-d3694-me-toggle-with-500ms-settle-chromium-retry1\trace.zip
[2026-08-25 09:27:19] 
[2026-08-25 09:27:19]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:19] 
[2026-08-25 09:27:20]   6) [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:108:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle 
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]     Test timeout of 90000ms exceeded while running "beforeEach" hook.
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]       64 |
[2026-08-25 09:27:20]       65 | test.describe('Theme Switch Guard', () => {
[2026-08-25 09:27:20]     > 66 |   test.beforeEach(async ({ page }) => {
[2026-08-25 09:27:20]          |        ^
[2026-08-25 09:27:20]       67 |     await page.goto('https://numista.ai');
[2026-08-25 09:27:20]       68 |     await signInAndWait(page);
[2026-08-25 09:27:20]       69 |   });
[2026-08-25 09:27:20]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:66:8
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]     Tearing down "context" exceeded the test timeout of 90000ms.
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]     Error: page.waitForTimeout: Target page, context or browser has been closed
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]       49 |     if (await modalButtons.first().isVisible({ timeout: 1500 }).catch(() => false)) {
[2026-08-25 09:27:20]       50 |       await modalButtons.first().click().catch(() => {});
[2026-08-25 09:27:20]     > 51 |       await page.waitForTimeout(1000);
[2026-08-25 09:27:20]          |                  ^
[2026-08-25 09:27:20]       52 |     }
[2026-08-25 09:27:20]       53 |   }
[2026-08-25 09:27:20]       54 | }
[2026-08-25 09:27:20]         at signInAndWait (C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:51:18)
[2026-08-25 09:27:20]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:68:5
[2026-08-25 09:27:20] 
[2026-08-25 09:27:20]     Error: End of central directory record signature not found. Either not a zip file, or file is truncated.
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:21]     screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium\test-failed-1.png
[2026-08-25 09:27:21]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]     Error Context: screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium\error-context.md
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]     Test timeout of 90000ms exceeded while running "beforeEach" hook.
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]       64 |
[2026-08-25 09:27:21]       65 | test.describe('Theme Switch Guard', () => {
[2026-08-25 09:27:21]     > 66 |   test.beforeEach(async ({ page }) => {
[2026-08-25 09:27:21]          |        ^
[2026-08-25 09:27:21]       67 |     await page.goto('https://numista.ai');
[2026-08-25 09:27:21]       68 |     await signInAndWait(page);
[2026-08-25 09:27:21]       69 |   });
[2026-08-25 09:27:21]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:66:8
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]     Error: page.waitForTimeout: Target page, context or browser has been closed
[2026-08-25 09:27:21] 
[2026-08-25 09:27:21]       49 |     if (await modalButtons.first().isVisible({ timeout: 1500 }).catch(() => false)) {
[2026-08-25 09:27:21]       50 |       await modalButtons.first().click().catch(() => {});
[2026-08-25 09:27:21]     > 51 |       await page.waitForTimeout(1000);
[2026-08-25 09:27:21]          |                  ^
[2026-08-25 09:27:21]       52 |     }
[2026-08-25 09:27:21]       53 |   }
[2026-08-25 09:27:21]       54 | }
[2026-08-25 09:27:21]         at signInAndWait (C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:51:18)
[2026-08-25 09:27:22]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js:68:5
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:27:22]     screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium-retry1\test-failed-1.png
[2026-08-25 09:27:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:27:22]     screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium-retry1\video.webm
[2026-08-25 09:27:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]     Error Context: screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium-retry1\error-context.md
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:27:22]     screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium-retry1\trace.zip
[2026-08-25 09:27:22]     Usage:
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]         npx playwright show-trace screenshots\layer_1_ux_visual-theme_sw-fdebf-tely-after-Dark-mode-toggle-chromium-retry1\trace.zip
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:27:22] 
[2026-08-25 09:27:22]   6 failed
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty 
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:71:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle 
[2026-08-25 09:27:22]     [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:108:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle 
[2026-08-25 09:27:22]   4 passed (14.0m)
[2026-08-25 09:27:23] LAYER 1: FAIL
[2026-08-25 09:27:23] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 09:28:16] QA project: numista-qc
[2026-08-25 09:28:16] Running seed_qc_fixtures.py --check...
[2026-08-25 09:28:22] Fixtures OK.
[2026-08-25 09:28:22] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 09:28:22] === LAYER 1: UX Visual Guard ===
[2026-08-25 09:34:11] ? injected env (2) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:34:11] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:34:11] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:34:11] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:34:11] 
[2026-08-25 09:34:11] Running 10 tests using 1 worker
[2026-08-25 09:34:11] 
[2026-08-25 09:34:11] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:34:11] WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
[2026-08-25 09:34:11] E0000 00:00:1787664508.475936   18468 alts_credentials.cc:93] ALTS creds ignored. Not running on GCP and untrusted ALTS is not enabled.
[2026-08-25 09:34:11] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:34:11] [coin_data_audit] No canonical_title_field in manifest ? quad-check active (['title', 'theme_subject', 'series', 'program_series'])
[2026-08-25 09:34:11] [coin_data_audit] Auditing coins...
[2026-08-25 09:34:11]   [TITLE_OK] qc_fixture_estate_coin: non-empty fields=['title', 'series']
[2026-08-25 09:34:11]   [TITLE_OK] qc_fixture_foreign_coin: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 09:34:11]   [TITLE_OK] qc_fixture_title_ok_dollar: non-empty fields=['title', 'series']
[2026-08-25 09:34:11]   [TITLE_OK] qc_fixture_title_ok_quarter: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 09:34:11] [coin_data_audit] Auditing estate boundary...
[2026-08-25 09:34:11] 
[2026-08-25 09:34:11] [coin_data_audit] RESULTS: 5 PASS / 0 WARN / 0 UNEXPECTED FAIL (1 expected sentinel)
[2026-08-25 09:34:11]   PASS  [FIXTURE_SENTINEL_OK]: Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.
[2026-08-25 09:34:11]   PASS  [COINS_AUDITED]: 5 coin documents checked. 1 title failures.
[2026-08-25 09:34:11]   PASS  [ESTATE_CURRENCY_SEPARATED]: 1 currency docs confirmed separate from coins.
[2026-08-25 09:34:11]   PASS  [ESTATE_WORLD_SEPARATED]: 1 world_items docs confirmed separate from coins.
[2026-08-25 09:34:11]   PASS  [FOREIGN_COINS_IN_COINS]: 1 foreign coin(s) correctly in users/{uid}/coins.
[2026-08-25 09:34:11]   EXPECTED FAIL  [COIN_TITLE_FAIL] qc_fixture_title_FAIL_empty: All title fields empty: ['title', 'theme_subject', 'series', 'program_series']. Flutter _buildTitle() will degrade to year+mint only.
[2026-08-25 09:34:12] 
[2026-08-25 09:34:12]   ok  1 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (4.7s)
[2026-08-25 09:34:12]   x   2 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (1.6m)
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:34:12]   x   3 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) (retry #1) (1.6m)
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? suppress logs { quiet: true }
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:34:12] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:34:12] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:34:12] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:34:12] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:34:12] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":12,"b":12} ratio=1.03
[2026-08-25 09:34:12]   x   4 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (15.7s)
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? encrypted .env [www.dotenvx.com]
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:34:12] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:34:12] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:34:12] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:34:12] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:34:12] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":12,"b":12} ratio=1.03
[2026-08-25 09:34:12]   x   5 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (retry #1) (14.4s)
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:34:12] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:34:12] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:34:12] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:34:12] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:34:12] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":12,"b":12} ratio=1.03
[2026-08-25 09:34:12]   x   6 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (14.6s)
[2026-08-25 09:34:12] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:34:13] ? injected env (0) from ..\numista_tests\.env // tip: ? encrypted .env [www.dotenvx.com]
[2026-08-25 09:34:13] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:34:13] [Sidebar nav item] fg={"r":1,"g":1,"b":1} bg={"r":3,"g":3,"b":4} ratio=1.01
[2026-08-25 09:34:13] [Main content header] fg={"r":2,"g":2,"b":4} bg={"r":2,"g":6,"b":14} ratio=1.02
[2026-08-25 09:34:13] [Collection card text] fg={"r":0,"g":1,"b":2} bg={"r":0,"g":1,"b":2} ratio=1.00
[2026-08-25 09:34:13] [Bottom nav label] fg={"r":16,"g":16,"b":16} bg={"r":11,"g":12,"b":12} ratio=1.03
[2026-08-25 09:34:13]   x   7 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (retry #1) (14.7s)
[2026-08-25 09:34:13] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:34:13] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:34:13]   ok  8 [chromium] › layer_1_ux_visual\layout_guard.spec.js:63:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport (12.4s)
[2026-08-25 09:34:13]   ok  9 [chromium] › layer_1_ux_visual\layout_guard.spec.js:79:3 › Layout Guard - 1920x1080 Desktop › No negative top/left on flt-glass-pane (not shifted off-screen) (11.2s)
[2026-08-25 09:34:13]   ok 10 [chromium] › layer_1_ux_visual\layout_guard.spec.js:93:3 › Layout Guard - 1920x1080 Desktop › Flutter renders in release mode (not debug banner) (10.9s)
[2026-08-25 09:34:13]   ok 11 [chromium] › layer_1_ux_visual\layout_guard.spec.js:104:3 › Layout Guard - 1920x1080 Desktop › Page title is set (not blank or default) (11.6s)
[2026-08-25 09:34:13] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:34:13] [theme_switch_guard] Theme toggle button not found at 1920x1080. Skipping toggle test.
[2026-08-25 09:34:13]   -  12 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:75:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle
[2026-08-25 09:34:13]   -  13 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:112:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 09:34:13] 
[2026-08-25 09:34:13] 
[2026-08-25 09:34:13]   1) [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:34:13] 
[2026-08-25 09:34:13]     Test timeout of 90000ms exceeded.
[2026-08-25 09:34:13] 
[2026-08-25 09:34:13]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:34:13] 
[2026-08-25 09:34:13]       80 |
[2026-08-25 09:34:13]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:34:13]     > 82 |     await page.waitForFunction(
[2026-08-25 09:34:13]          |                ^
[2026-08-25 09:34:13]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:34:13]       84 |       { timeout: 20000 }
[2026-08-25 09:34:13]       85 |     );
[2026-08-25 09:34:14]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:34:14] 
[2026-08-25 09:34:14]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:14]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\test-failed-1.png
[2026-08-25 09:34:14]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:14] 
[2026-08-25 09:34:14]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:14]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\video.webm
[2026-08-25 09:34:14]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:14] 
[2026-08-25 09:34:14]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\error-context.md
[2026-08-25 09:34:14] 
[2026-08-25 09:34:14]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:14]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:34:15]     Usage:
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium\trace.zip
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]     Test timeout of 90000ms exceeded.
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]     Error: page.waitForFunction: Test timeout of 90000ms exceeded.
[2026-08-25 09:34:15] 
[2026-08-25 09:34:15]       80 |
[2026-08-25 09:34:15]       81 |     await page.goto('https://numista.ai');
[2026-08-25 09:34:16]     > 82 |     await page.waitForFunction(
[2026-08-25 09:34:16]          |                ^
[2026-08-25 09:34:16]       83 |       () => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; },
[2026-08-25 09:34:16]       84 |       { timeout: 20000 }
[2026-08-25 09:34:16]       85 |     );
[2026-08-25 09:34:16]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\coin_title_guard.spec.js:82:16
[2026-08-25 09:34:16] 
[2026-08-25 09:34:16]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:16]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\test-failed-1.png
[2026-08-25 09:34:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:16] 
[2026-08-25 09:34:16]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:16]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\video.webm
[2026-08-25 09:34:16]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:16] 
[2026-08-25 09:34:17]     Error Context: screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\error-context.md
[2026-08-25 09:34:17] 
[2026-08-25 09:34:17]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:17]     screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:34:17]     Usage:
[2026-08-25 09:34:17] 
[2026-08-25 09:34:17]         npx playwright show-trace screenshots\layer_1_ux_visual-coin_tit-26504-tional---non-authoritative--chromium-retry1\trace.zip
[2026-08-25 09:34:17] 
[2026-08-25 09:34:17]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:17] 
[2026-08-25 09:34:17]   2) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:34:17] 
[2026-08-25 09:34:17]     Error: Contrast failures in Light mode:
[2026-08-25 09:34:17]     [
[2026-08-25 09:34:18]       {
[2026-08-25 09:34:18]         "name": "Sidebar nav item",
[2026-08-25 09:34:18]         "ratio": "1.01",
[2026-08-25 09:34:18]         "fg": {
[2026-08-25 09:34:18]           "r": 1,
[2026-08-25 09:34:18]           "g": 1,
[2026-08-25 09:34:18]           "b": 1
[2026-08-25 09:34:18]         },
[2026-08-25 09:34:18]         "bg": {
[2026-08-25 09:34:18]           "r": 3,
[2026-08-25 09:34:18]           "g": 3,
[2026-08-25 09:34:18]           "b": 4
[2026-08-25 09:34:18]         }
[2026-08-25 09:34:18]       },
[2026-08-25 09:34:19]       {
[2026-08-25 09:34:19]         "name": "Main content header",
[2026-08-25 09:34:19]         "ratio": "1.02",
[2026-08-25 09:34:19]         "fg": {
[2026-08-25 09:34:19]           "r": 2,
[2026-08-25 09:34:19]           "g": 2,
[2026-08-25 09:34:19]           "b": 4
[2026-08-25 09:34:19]         },
[2026-08-25 09:34:19]         "bg": {
[2026-08-25 09:34:19]           "r": 2,
[2026-08-25 09:34:19]           "g": 6,
[2026-08-25 09:34:19]           "b": 14
[2026-08-25 09:34:19]         }
[2026-08-25 09:34:19]       },
[2026-08-25 09:34:19]       {
[2026-08-25 09:34:20]         "name": "Collection card text",
[2026-08-25 09:34:20]         "ratio": "1.00",
[2026-08-25 09:34:20]         "fg": {
[2026-08-25 09:34:20]           "r": 0,
[2026-08-25 09:34:20]           "g": 1,
[2026-08-25 09:34:20]           "b": 2
[2026-08-25 09:34:20]         },
[2026-08-25 09:34:20]         "bg": {
[2026-08-25 09:34:20]           "r": 0,
[2026-08-25 09:34:20]           "g": 1,
[2026-08-25 09:34:20]           "b": 2
[2026-08-25 09:34:20]         }
[2026-08-25 09:34:20]       },
[2026-08-25 09:34:20]       {
[2026-08-25 09:34:21]         "name": "Bottom nav label",
[2026-08-25 09:34:21]         "ratio": "1.03",
[2026-08-25 09:34:21]         "fg": {
[2026-08-25 09:34:21]           "r": 16,
[2026-08-25 09:34:21]           "g": 16,
[2026-08-25 09:34:21]           "b": 16
[2026-08-25 09:34:21]         },
[2026-08-25 09:34:21]         "bg": {
[2026-08-25 09:34:21]           "r": 11,
[2026-08-25 09:34:21]           "g": 12,
[2026-08-25 09:34:21]           "b": 12
[2026-08-25 09:34:21]         }
[2026-08-25 09:34:21]       }
[2026-08-25 09:34:21]     ]
[2026-08-25 09:34:21] 
[2026-08-25 09:34:21]     expect(received).toHaveLength(expected)
[2026-08-25 09:34:21] 
[2026-08-25 09:34:21]     Expected length: 0
[2026-08-25 09:34:21]     Received length: 4
[2026-08-25 09:34:21]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 12, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:34:21] 
[2026-08-25 09:34:21]       176 |     }
[2026-08-25 09:34:21]       177 |
[2026-08-25 09:34:21]     > 178 |     expect(failedRegions, 'Contrast failures in Light mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:34:21]           |                                                                                                          ^
[2026-08-25 09:34:22]       179 |   });
[2026-08-25 09:34:22]       180 | });
[2026-08-25 09:34:22]       181 |
[2026-08-25 09:34:22]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:178:106
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:22]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:34:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:22]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:34:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:22]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:34:22]     Usage:
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:34:22] 
[2026-08-25 09:34:22]     Error: Contrast failures in Light mode:
[2026-08-25 09:34:22]     [
[2026-08-25 09:34:22]       {
[2026-08-25 09:34:22]         "name": "Sidebar nav item",
[2026-08-25 09:34:22]         "ratio": "1.01",
[2026-08-25 09:34:23]         "fg": {
[2026-08-25 09:34:23]           "r": 1,
[2026-08-25 09:34:23]           "g": 1,
[2026-08-25 09:34:23]           "b": 1
[2026-08-25 09:34:23]         },
[2026-08-25 09:34:23]         "bg": {
[2026-08-25 09:34:23]           "r": 3,
[2026-08-25 09:34:23]           "g": 3,
[2026-08-25 09:34:23]           "b": 4
[2026-08-25 09:34:23]         }
[2026-08-25 09:34:23]       },
[2026-08-25 09:34:23]       {
[2026-08-25 09:34:23]         "name": "Main content header",
[2026-08-25 09:34:23]         "ratio": "1.02",
[2026-08-25 09:34:23]         "fg": {
[2026-08-25 09:34:23]           "r": 2,
[2026-08-25 09:34:23]           "g": 2,
[2026-08-25 09:34:23]           "b": 4
[2026-08-25 09:34:23]         },
[2026-08-25 09:34:23]         "bg": {
[2026-08-25 09:34:23]           "r": 2,
[2026-08-25 09:34:23]           "g": 6,
[2026-08-25 09:34:23]           "b": 14
[2026-08-25 09:34:23]         }
[2026-08-25 09:34:23]       },
[2026-08-25 09:34:23]       {
[2026-08-25 09:34:23]         "name": "Collection card text",
[2026-08-25 09:34:23]         "ratio": "1.00",
[2026-08-25 09:34:23]         "fg": {
[2026-08-25 09:34:23]           "r": 0,
[2026-08-25 09:34:24]           "g": 1,
[2026-08-25 09:34:24]           "b": 2
[2026-08-25 09:34:24]         },
[2026-08-25 09:34:24]         "bg": {
[2026-08-25 09:34:24]           "r": 0,
[2026-08-25 09:34:24]           "g": 1,
[2026-08-25 09:34:24]           "b": 2
[2026-08-25 09:34:24]         }
[2026-08-25 09:34:24]       },
[2026-08-25 09:34:24]       {
[2026-08-25 09:34:24]         "name": "Bottom nav label",
[2026-08-25 09:34:24]         "ratio": "1.03",
[2026-08-25 09:34:24]         "fg": {
[2026-08-25 09:34:24]           "r": 16,
[2026-08-25 09:34:24]           "g": 16,
[2026-08-25 09:34:24]           "b": 16
[2026-08-25 09:34:24]         },
[2026-08-25 09:34:24]         "bg": {
[2026-08-25 09:34:24]           "r": 11,
[2026-08-25 09:34:24]           "g": 12,
[2026-08-25 09:34:24]           "b": 12
[2026-08-25 09:34:24]         }
[2026-08-25 09:34:24]       }
[2026-08-25 09:34:24]     ]
[2026-08-25 09:34:24] 
[2026-08-25 09:34:24]     expect(received).toHaveLength(expected)
[2026-08-25 09:34:24] 
[2026-08-25 09:34:24]     Expected length: 0
[2026-08-25 09:34:24]     Received length: 4
[2026-08-25 09:34:24]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 12, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:34:24] 
[2026-08-25 09:34:25]       176 |     }
[2026-08-25 09:34:25]       177 |
[2026-08-25 09:34:25]     > 178 |     expect(failedRegions, 'Contrast failures in Light mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:34:25]           |                                                                                                          ^
[2026-08-25 09:34:25]       179 |   });
[2026-08-25 09:34:25]       180 | });
[2026-08-25 09:34:25]       181 |
[2026-08-25 09:34:25]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:178:106
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:25]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:34:25]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:25]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:34:25]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     Error Context: screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:25]     screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:34:25]     Usage:
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-aa99a-ight-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]   3) [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:34:25] 
[2026-08-25 09:34:25]     Error: Contrast failures in Dark mode:
[2026-08-25 09:34:25]     [
[2026-08-25 09:34:26]       {
[2026-08-25 09:34:26]         "name": "Sidebar nav item",
[2026-08-25 09:34:26]         "ratio": "1.01",
[2026-08-25 09:34:26]         "fg": {
[2026-08-25 09:34:26]           "r": 1,
[2026-08-25 09:34:26]           "g": 1,
[2026-08-25 09:34:26]           "b": 1
[2026-08-25 09:34:26]         },
[2026-08-25 09:34:26]         "bg": {
[2026-08-25 09:34:26]           "r": 3,
[2026-08-25 09:34:26]           "g": 3,
[2026-08-25 09:34:26]           "b": 4
[2026-08-25 09:34:26]         }
[2026-08-25 09:34:26]       },
[2026-08-25 09:34:26]       {
[2026-08-25 09:34:26]         "name": "Main content header",
[2026-08-25 09:34:26]         "ratio": "1.02",
[2026-08-25 09:34:26]         "fg": {
[2026-08-25 09:34:26]           "r": 2,
[2026-08-25 09:34:26]           "g": 2,
[2026-08-25 09:34:26]           "b": 4
[2026-08-25 09:34:26]         },
[2026-08-25 09:34:26]         "bg": {
[2026-08-25 09:34:26]           "r": 2,
[2026-08-25 09:34:26]           "g": 6,
[2026-08-25 09:34:26]           "b": 14
[2026-08-25 09:34:26]         }
[2026-08-25 09:34:26]       },
[2026-08-25 09:34:26]       {
[2026-08-25 09:34:27]         "name": "Collection card text",
[2026-08-25 09:34:27]         "ratio": "1.00",
[2026-08-25 09:34:27]         "fg": {
[2026-08-25 09:34:27]           "r": 0,
[2026-08-25 09:34:27]           "g": 1,
[2026-08-25 09:34:27]           "b": 2
[2026-08-25 09:34:27]         },
[2026-08-25 09:34:27]         "bg": {
[2026-08-25 09:34:27]           "r": 0,
[2026-08-25 09:34:27]           "g": 1,
[2026-08-25 09:34:27]           "b": 2
[2026-08-25 09:34:27]         }
[2026-08-25 09:34:27]       },
[2026-08-25 09:34:27]       {
[2026-08-25 09:34:27]         "name": "Bottom nav label",
[2026-08-25 09:34:27]         "ratio": "1.03",
[2026-08-25 09:34:27]         "fg": {
[2026-08-25 09:34:27]           "r": 16,
[2026-08-25 09:34:27]           "g": 16,
[2026-08-25 09:34:27]           "b": 16
[2026-08-25 09:34:27]         },
[2026-08-25 09:34:27]         "bg": {
[2026-08-25 09:34:27]           "r": 11,
[2026-08-25 09:34:27]           "g": 12,
[2026-08-25 09:34:27]           "b": 12
[2026-08-25 09:34:27]         }
[2026-08-25 09:34:27]       }
[2026-08-25 09:34:27]     ]
[2026-08-25 09:34:27] 
[2026-08-25 09:34:27]     expect(received).toHaveLength(expected)
[2026-08-25 09:34:27] 
[2026-08-25 09:34:28]     Expected length: 0
[2026-08-25 09:34:28]     Received length: 4
[2026-08-25 09:34:28]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 12, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]       211 |     }
[2026-08-25 09:34:28]       212 |
[2026-08-25 09:34:28]     > 213 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:34:28]           |                                                                                                         ^
[2026-08-25 09:34:28]       214 |   });
[2026-08-25 09:34:28]       215 | });
[2026-08-25 09:34:28]       216 |
[2026-08-25 09:34:28]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:213:105
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:28]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\test-failed-1.png
[2026-08-25 09:34:28]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:28]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\video.webm
[2026-08-25 09:34:28]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\error-context.md
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:28]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:34:28]     Usage:
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium\trace.zip
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:28] 
[2026-08-25 09:34:28]     Retry #1 ---------------------------------------------------------------------------------------
[2026-08-25 09:34:29] 
[2026-08-25 09:34:29]     Error: Contrast failures in Dark mode:
[2026-08-25 09:34:29]     [
[2026-08-25 09:34:29]       {
[2026-08-25 09:34:29]         "name": "Sidebar nav item",
[2026-08-25 09:34:29]         "ratio": "1.01",
[2026-08-25 09:34:29]         "fg": {
[2026-08-25 09:34:29]           "r": 1,
[2026-08-25 09:34:29]           "g": 1,
[2026-08-25 09:34:29]           "b": 1
[2026-08-25 09:34:29]         },
[2026-08-25 09:34:29]         "bg": {
[2026-08-25 09:34:29]           "r": 3,
[2026-08-25 09:34:29]           "g": 3,
[2026-08-25 09:34:29]           "b": 4
[2026-08-25 09:34:29]         }
[2026-08-25 09:34:29]       },
[2026-08-25 09:34:29]       {
[2026-08-25 09:34:29]         "name": "Main content header",
[2026-08-25 09:34:29]         "ratio": "1.02",
[2026-08-25 09:34:29]         "fg": {
[2026-08-25 09:34:29]           "r": 2,
[2026-08-25 09:34:29]           "g": 2,
[2026-08-25 09:34:29]           "b": 4
[2026-08-25 09:34:29]         },
[2026-08-25 09:34:29]         "bg": {
[2026-08-25 09:34:29]           "r": 2,
[2026-08-25 09:34:29]           "g": 6,
[2026-08-25 09:34:29]           "b": 14
[2026-08-25 09:34:29]         }
[2026-08-25 09:34:30]       },
[2026-08-25 09:34:30]       {
[2026-08-25 09:34:30]         "name": "Collection card text",
[2026-08-25 09:34:30]         "ratio": "1.00",
[2026-08-25 09:34:30]         "fg": {
[2026-08-25 09:34:30]           "r": 0,
[2026-08-25 09:34:30]           "g": 1,
[2026-08-25 09:34:30]           "b": 2
[2026-08-25 09:34:30]         },
[2026-08-25 09:34:30]         "bg": {
[2026-08-25 09:34:30]           "r": 0,
[2026-08-25 09:34:30]           "g": 1,
[2026-08-25 09:34:30]           "b": 2
[2026-08-25 09:34:30]         }
[2026-08-25 09:34:30]       },
[2026-08-25 09:34:30]       {
[2026-08-25 09:34:30]         "name": "Bottom nav label",
[2026-08-25 09:34:30]         "ratio": "1.03",
[2026-08-25 09:34:30]         "fg": {
[2026-08-25 09:34:30]           "r": 16,
[2026-08-25 09:34:30]           "g": 16,
[2026-08-25 09:34:30]           "b": 16
[2026-08-25 09:34:30]         },
[2026-08-25 09:34:30]         "bg": {
[2026-08-25 09:34:30]           "r": 11,
[2026-08-25 09:34:30]           "g": 12,
[2026-08-25 09:34:30]           "b": 12
[2026-08-25 09:34:30]         }
[2026-08-25 09:34:30]       }
[2026-08-25 09:34:31]     ]
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     expect(received).toHaveLength(expected)
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     Expected length: 0
[2026-08-25 09:34:31]     Received length: 4
[2026-08-25 09:34:31]     Received array:  [{"bg": {"b": 4, "g": 3, "r": 3}, "fg": {"b": 1, "g": 1, "r": 1}, "name": "Sidebar nav item", "ratio": "1.01"}, {"bg": {"b": 14, "g": 6, "r": 2}, "fg": {"b": 4, "g": 2, "r": 2}, "name": "Main content header", "ratio": "1.02"}, {"bg": {"b": 2, "g": 1, "r": 0}, "fg": {"b": 2, "g": 1, "r": 0}, "name": "Collection card text", "ratio": "1.00"}, {"bg": {"b": 12, "g": 12, "r": 11}, "fg": {"b": 16, "g": 16, "r": 16}, "name": "Bottom nav label", "ratio": "1.03"}]
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]       211 |     }
[2026-08-25 09:34:31]       212 |
[2026-08-25 09:34:31]     > 213 |     expect(failedRegions, 'Contrast failures in Dark mode:\n' + JSON.stringify(failedRegions, null, 2)).toHaveLength(0);
[2026-08-25 09:34:31]           |                                                                                                         ^
[2026-08-25 09:34:31]       214 |   });
[2026-08-25 09:34:31]       215 | });
[2026-08-25 09:34:31]       216 |
[2026-08-25 09:34:31]         at C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\contrast_guard.spec.js:213:105
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     attachment #1: screenshot (image/png) ----------------------------------------------------------
[2026-08-25 09:34:31]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\test-failed-1.png
[2026-08-25 09:34:31]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     attachment #2: video (video/webm) --------------------------------------------------------------
[2026-08-25 09:34:31]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\video.webm
[2026-08-25 09:34:31]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     Error Context: screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\error-context.md
[2026-08-25 09:34:31] 
[2026-08-25 09:34:31]     attachment #4: trace (application/zip) ---------------------------------------------------------
[2026-08-25 09:34:31]     screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:34:31]     Usage:
[2026-08-25 09:34:31] 
[2026-08-25 09:34:32]         npx playwright show-trace screenshots\layer_1_ux_visual-contrast-6b573-Dark-mode-on-key-UI-regions-chromium-retry1\trace.zip
[2026-08-25 09:34:32] 
[2026-08-25 09:34:32]     ------------------------------------------------------------------------------------------------
[2026-08-25 09:34:32] 
[2026-08-25 09:34:32]   3 failed
[2026-08-25 09:34:32]     [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative) 
[2026-08-25 09:34:32]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:153:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions 
[2026-08-25 09:34:32]     [chromium] › layer_1_ux_visual\contrast_guard.spec.js:188:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions 
[2026-08-25 09:34:32]   2 skipped
[2026-08-25 09:34:32]   5 passed (5.8m)
[2026-08-25 09:34:32] LAYER 1: FAIL
[2026-08-25 09:34:32] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 09:43:13] QA project: numista-qc
[2026-08-25 09:43:13] Running seed_qc_fixtures.py --check...
[2026-08-25 09:43:17] Fixtures OK.
[2026-08-25 09:43:17] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 09:43:17] === LAYER 1: UX Visual Guard ===
[2026-08-25 09:45:12] ? injected env (2) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:45:12] ? injected env (0) from ..\numista_tests\.env // tip: ? multiple files { path: ['.env.local', '.env'] }
[2026-08-25 09:45:12] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:45:12] ? injected env (0) from ..\numista_tests\.env // tip: ? custom filepath { path: '/custom/path/.env' }
[2026-08-25 09:45:12] 
[2026-08-25 09:45:12] Running 10 tests using 1 worker
[2026-08-25 09:45:12] 
[2026-08-25 09:45:12] ? injected env (0) from ..\numista_tests\.env // tip: ? enable debugging { debug: true }
[2026-08-25 09:45:12] WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
[2026-08-25 09:45:12] E0000 00:00:1787665404.822984   15324 alts_credentials.cc:93] ALTS creds ignored. Not running on GCP and untrusted ALTS is not enabled.
[2026-08-25 09:45:12] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 09:45:12] [coin_data_audit] No canonical_title_field in manifest ? quad-check active (['title', 'theme_subject', 'series', 'program_series'])
[2026-08-25 09:45:12] [coin_data_audit] Auditing coins...
[2026-08-25 09:45:12]   [TITLE_OK] qc_fixture_estate_coin: non-empty fields=['title', 'series']
[2026-08-25 09:45:12]   [TITLE_OK] qc_fixture_foreign_coin: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 09:45:12]   [TITLE_OK] qc_fixture_title_ok_dollar: non-empty fields=['title', 'series']
[2026-08-25 09:45:12]   [TITLE_OK] qc_fixture_title_ok_quarter: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 09:45:12] [coin_data_audit] Auditing estate boundary...
[2026-08-25 09:45:12] 
[2026-08-25 09:45:12] [coin_data_audit] RESULTS: 5 PASS / 0 WARN / 0 UNEXPECTED FAIL (1 expected sentinel)
[2026-08-25 09:45:12]   PASS  [FIXTURE_SENTINEL_OK]: Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.
[2026-08-25 09:45:13]   PASS  [COINS_AUDITED]: 5 coin documents checked. 1 title failures.
[2026-08-25 09:45:13]   PASS  [ESTATE_CURRENCY_SEPARATED]: 1 currency docs confirmed separate from coins.
[2026-08-25 09:45:13]   PASS  [ESTATE_WORLD_SEPARATED]: 1 world_items docs confirmed separate from coins.
[2026-08-25 09:45:13]   PASS  [FOREIGN_COINS_IN_COINS]: 1 foreign coin(s) correctly in users/{uid}/coins.
[2026-08-25 09:45:13]   EXPECTED FAIL  [COIN_TITLE_FAIL] qc_fixture_title_FAIL_empty: All title fields empty: ['title', 'theme_subject', 'series', 'program_series']. Flutter _buildTitle() will degrade to year+mint only.
[2026-08-25 09:45:13] 
[2026-08-25 09:45:13]   ok  1 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:21:3 › Coin Title Guard › Primary: Firestore field check - no coin should have all title fields empty (6.2s)
[2026-08-25 09:45:13] [coin_title_guard] SEMANTICS_UNAVAILABLE: accessibility tree returned no nodes. Primary assertion is authoritative.
[2026-08-25 09:45:13]   -   2 [chromium] › layer_1_ux_visual\coin_title_guard.spec.js:75:3 › Coin Title Guard › Secondary: Flutter accessibility snapshot (conditional - non-authoritative)
[2026-08-25 09:45:13] ? injected env (0) from ..\numista_tests\.env // tip: ? auth for agents [www.vestauth.com]
[2026-08-25 09:45:13] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:45:13] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 09:45:13] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 09:45:13] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 09:45:13] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 09:45:13]   ok  3 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:176:3 › Contrast Guard - Light Mode › WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (13.1s)
[2026-08-25 09:45:13] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 09:45:13] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 09:45:13] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 09:45:13] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 09:45:13] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 09:45:13]   ok  4 [chromium] › layer_1_ux_visual\contrast_guard.spec.js:207:3 › Contrast Guard - Dark Mode › WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (12.6s)
[2026-08-25 09:45:13] ? injected env (0) from ..\numista_tests\.env // tip: ? override existing { override: true }
[2026-08-25 09:45:13]   ok  5 [chromium] › layer_1_ux_visual\layout_guard.spec.js:63:3 › Layout Guard - 1920x1080 Desktop › flt-glass-pane fills the viewport (11.1s)
[2026-08-25 09:45:13]   ok  6 [chromium] › layer_1_ux_visual\layout_guard.spec.js:79:3 › Layout Guard - 1920x1080 Desktop › No negative top/left on flt-glass-pane (not shifted off-screen) (11.5s)
[2026-08-25 09:45:13]   ok  7 [chromium] › layer_1_ux_visual\layout_guard.spec.js:93:3 › Layout Guard - 1920x1080 Desktop › Flutter renders in release mode (not debug banner) (11.8s)
[2026-08-25 09:45:13]   ok  8 [chromium] › layer_1_ux_visual\layout_guard.spec.js:104:3 › Layout Guard - 1920x1080 Desktop › Page title is set (not blank or default) (12.7s)
[2026-08-25 09:45:13] ? injected env (0) from ..\numista_tests\.env // tip: ? secrets for agents [www.dotenvx.com]
[2026-08-25 09:45:13] [theme_switch_guard] Theme toggle button not found at 1920x1080. Skipping toggle test.
[2026-08-25 09:45:13]   -   9 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:78:3 › Theme Switch Guard › App remains visible after theme toggle with 500ms settle
[2026-08-25 09:45:14]   -  10 [chromium] › layer_1_ux_visual\theme_switch_guard.spec.js:115:3 › Theme Switch Guard › Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 09:45:14] 
[2026-08-25 09:45:14]   3 skipped
[2026-08-25 09:45:14]   7 passed (1.9m)
[2026-08-25 09:45:14] LAYER 1: PASS
[2026-08-25 09:45:14] SUITE_RESULT: PASS
