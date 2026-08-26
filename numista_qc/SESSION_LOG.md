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
[2026-08-25 16:25:02] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 16:25:02] QA project: numista-qc
[2026-08-25 16:25:02] Running seed_qc_fixtures.py --check...
[2026-08-25 16:25:16] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 16:25:16] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 16:25:16] Model ID scan: no deprecated patterns found.
[2026-08-25 16:25:16] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 16:25:16] === Flutter Checks (analyze + test) ===
[2026-08-25 16:27:04] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 16:27:04] QA project: numista-qc
[2026-08-25 16:27:04] Running seed_qc_fixtures.py --check...
[2026-08-25 16:27:14] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 16:27:14] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 16:30:33] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 16:30:33] QA project: numista-qc
[2026-08-25 16:30:33] Running seed_qc_fixtures.py --check...
[2026-08-25 16:30:38] Fixtures OK.
[2026-08-25 16:30:38] Checking Cloud Run secrets (non-blocking)...
[2026-08-25 16:30:41] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 16:30:41] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 16:31:04] Model ID scan: no deprecated patterns found.
[2026-08-25 16:31:04] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 16:31:04] === Flutter Checks (analyze + test) ===
[2026-08-25 16:34:17] Analyzing numista_mobile...                                     
[2026-08-25 16:34:17] 
[2026-08-25 16:34:17] warning - Unused import: 'package:file_picker/file_picker.dart' - ..\numista_mobile\lib\screens\customer_service_screen.dart:5:8 - unused_import
[2026-08-25 16:34:17]    info - 'dart:html' is deprecated and shouldn't be used. Use package:web and dart:js_interop instead - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:1 - deprecated_member_use
[2026-08-25 16:34:17] warning - Unused import: 'dart:html' - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:8 - unused_import
[2026-08-25 16:34:17] warning - Unused import: 'dart:typed_data' - ..\numista_mobile\lib\screens\customer_service_screen.dart:8:8 - unused_import
[2026-08-25 16:34:17]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:51:7 - use_null_aware_elements
[2026-08-25 16:34:17]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:132:7 - use_null_aware_elements
[2026-08-25 16:34:17]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:133:7 - use_null_aware_elements
[2026-08-25 16:34:17]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:134:7 - use_null_aware_elements
[2026-08-25 16:34:17] 
[2026-08-25 16:34:17] 8 issues found. (ran in 190.1s)
[2026-08-25 16:34:17] flutter analyze: FAIL
[2026-08-25 16:34:20] Error: No pubspec.yaml file found.
[2026-08-25 16:34:20] This command should be run from the root of your Flutter project.
[2026-08-25 16:34:20] flutter test: FAIL
[2026-08-25 16:34:20] === LAYER 1: UX Visual Guard ===
[2026-08-25 16:37:55] Gùç injected env (2) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:37:55] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:37:55] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:37:55] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ multiple files { path: ['.env.local', '.env'] }
[2026-08-25 16:37:55] 
[2026-08-25 16:37:55] Running 10 tests using 1 worker
[2026-08-25 16:37:55] 
[2026-08-25 16:37:55] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ multiple files { path: ['.env.local', '.env'] }
[2026-08-25 16:37:55] WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
[2026-08-25 16:37:55] E0000 00:00:1787690096.109157    7172 alts_credentials.cc:93] ALTS creds ignored. Not running on GCP and untrusted ALTS is not enabled.
[2026-08-25 16:37:55] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 16:37:55] [coin_data_audit] No canonical_title_field in manifest n++ quad-check active (['title', 'theme_subject', 'series', 'program_series'])
[2026-08-25 16:37:55] [coin_data_audit] Auditing coins...
[2026-08-25 16:37:56]   [TITLE_OK] qc_fixture_estate_coin: non-empty fields=['title', 'series']
[2026-08-25 16:37:56]   [TITLE_OK] qc_fixture_foreign_coin: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 16:37:56]   [TITLE_OK] qc_fixture_title_ok_dollar: non-empty fields=['title', 'series']
[2026-08-25 16:37:56]   [TITLE_OK] qc_fixture_title_ok_quarter: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 16:37:56] [coin_data_audit] Auditing estate boundary...
[2026-08-25 16:37:56] 
[2026-08-25 16:37:56] [coin_data_audit] RESULTS: 5 PASS / 0 WARN / 0 UNEXPECTED FAIL (1 expected sentinel)
[2026-08-25 16:37:56]   PASS  [FIXTURE_SENTINEL_OK]: Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.
[2026-08-25 16:37:56]   PASS  [COINS_AUDITED]: 5 coin documents checked. 1 title failures.
[2026-08-25 16:37:56]   PASS  [ESTATE_CURRENCY_SEPARATED]: 1 currency docs confirmed separate from coins.
[2026-08-25 16:37:56]   PASS  [ESTATE_WORLD_SEPARATED]: 1 world_items docs confirmed separate from coins.
[2026-08-25 16:37:56]   PASS  [FOREIGN_COINS_IN_COINS]: 1 foreign coin(s) correctly in users/{uid}/coins.
[2026-08-25 16:37:56]   EXPECTED FAIL  [COIN_TITLE_FAIL] qc_fixture_title_FAIL_empty: All title fields empty: ['title', 'theme_subject', 'series', 'program_series']. Flutter _buildTitle() will degrade to year+mint only.
[2026-08-25 16:37:56] 
[2026-08-25 16:37:56]   ok  1 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:21:3 GÇ¦ Coin Title Guard GÇ¦ Primary: Firestore field check - no coin should have all title fields empty (6.3s)
[2026-08-25 16:37:56] [coin_title_guard] SEMANTICS_UNAVAILABLE: accessibility tree returned no nodes. Primary assertion is authoritative.
[2026-08-25 16:37:56]   -   2 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:75:3 GÇ¦ Coin Title Guard GÇ¦ Secondary: Flutter accessibility snapshot (conditional - non-authoritative)
[2026-08-25 16:37:56] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:37:56] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 16:37:56] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 16:37:56] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 16:37:56] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 16:37:56] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 16:37:56]   ok  3 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:176:3 GÇ¦ Contrast Guard - Light Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (22.8s)
[2026-08-25 16:37:56] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 16:37:56] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 16:37:56] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 16:37:56] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 16:37:56] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 16:37:56]   ok  4 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:207:3 GÇ¦ Contrast Guard - Dark Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (21.7s)
[2026-08-25 16:37:56] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ enable debugging { debug: true }
[2026-08-25 16:37:56]   ok  5 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:63:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ flt-glass-pane fills the viewport (19.8s)
[2026-08-25 16:37:57]   ok  6 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:79:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ No negative top/left on flt-glass-pane (not shifted off-screen) (18.9s)
[2026-08-25 16:37:57]   ok  7 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:93:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ Flutter renders in release mode (not debug banner) (16.6s)
[2026-08-25 16:37:57]   ok  8 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:104:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ Page title is set (not blank or default) (20.1s)
[2026-08-25 16:37:57] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:37:57] [theme_switch_guard] Theme toggle button not found at 1920x1080. Skipping toggle test.
[2026-08-25 16:37:57]   -   9 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:78:3 GÇ¦ Theme Switch Guard GÇ¦ App remains visible after theme toggle with 500ms settle
[2026-08-25 16:37:57]   -  10 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:115:3 GÇ¦ Theme Switch Guard GÇ¦ Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 16:37:57] 
[2026-08-25 16:37:57]   3 skipped
[2026-08-25 16:37:57]   7 passed (3.1m)
[2026-08-25 16:37:57] 
[2026-08-25 16:37:57] To open last HTML report run:
[2026-08-25 16:37:57] [36m[39m
[2026-08-25 16:37:57] [36m  npx playwright show-report playwright-report[39m
[2026-08-25 16:37:57] [36m[39m
[2026-08-25 16:37:57] LAYER 1: PASS
[2026-08-25 16:37:57] numista_qc block appended to SCAN_REPORT.md
[2026-08-25 16:37:57] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 16:42:58] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 16:42:58] QA project: numista-qc
[2026-08-25 16:42:58] Running seed_qc_fixtures.py --check...
[2026-08-25 16:43:06] Fixtures OK.
[2026-08-25 16:43:06] Checking Cloud Run secrets (non-blocking)...
[2026-08-25 16:43:09] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 16:43:09] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 16:43:35] Model ID scan: no deprecated patterns found.
[2026-08-25 16:43:35] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 16:43:35] === Flutter Checks (analyze + test) ===
[2026-08-25 16:49:15] Analyzing numista_mobile...                                     
[2026-08-25 16:49:15] 
[2026-08-25 16:49:15] warning - Unused import: 'package:file_picker/file_picker.dart' - ..\numista_mobile\lib\screens\customer_service_screen.dart:5:8 - unused_import
[2026-08-25 16:49:15]    info - 'dart:html' is deprecated and shouldn't be used. Use package:web and dart:js_interop instead - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:1 - deprecated_member_use
[2026-08-25 16:49:15] warning - Unused import: 'dart:html' - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:8 - unused_import
[2026-08-25 16:49:15] warning - Unused import: 'dart:typed_data' - ..\numista_mobile\lib\screens\customer_service_screen.dart:8:8 - unused_import
[2026-08-25 16:49:15]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:51:7 - use_null_aware_elements
[2026-08-25 16:49:15]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:132:7 - use_null_aware_elements
[2026-08-25 16:49:15]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:133:7 - use_null_aware_elements
[2026-08-25 16:49:15]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:134:7 - use_null_aware_elements
[2026-08-25 16:49:15] 
[2026-08-25 16:49:15] 8 issues found. (ran in 336.3s)
[2026-08-25 16:49:15] flutter analyze: FAIL (errors found)
[2026-08-25 16:49:41] 00:00 +0: loading C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart
[2026-08-25 16:49:41] 00:00 +0: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains redundant tab navigation instructions
[2026-08-25 16:49:41] 00:00 +1: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains outdated color button references
[2026-08-25 16:49:41] 00:00 +2: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit MorganGuideService supports context-aware initialStep
[2026-08-25 16:49:41] 00:00 +3: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default profile has all required keys
[2026-08-25 16:49:41] 00:00 +4: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default preferred_services are PCGS and NGC
[2026-08-25 16:49:41] 00:00 +5: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default opt_in_chat_extraction is true
[2026-08-25 16:49:41] 00:00 +6: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default investment_goal is numismatic_study
[2026-08-25 16:49:41] 00:00 +7: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default budget_tier is intermediate
[2026-08-25 16:49:41] 00:00 +8: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() empty input returns all default values
[2026-08-25 16:49:41] 00:00 +9: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() valid profile data is preserved through normalization
[2026-08-25 16:49:41] 00:00 +10: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_series is replaced with empty list
[2026-08-25 16:49:41] 00:00 +11: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_services falls back to PCGS/NGC defaults
[2026-08-25 16:49:41] 00:00 +12: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() null opt_in_chat_extraction defaults to true
[2026-08-25 16:49:41] 00:00 +13: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() false opt_in_chat_extraction is preserved as false
[2026-08-25 16:49:41] 00:00 +14: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() integer grades are coerced to strings
[2026-08-25 16:49:41] 00:00 +15: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() preferred_series list elements are coerced to strings
[2026-08-25 16:49:41] 00:00 +16: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() extra unknown fields from API are preserved
[2026-08-25 16:49:41] 00:00 +17: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() empty updates produces empty payload
[2026-08-25 16:49:41] 00:00 +18: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() only specified keys are included in payload
[2026-08-25 16:49:41] 00:00 +19: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction true is coerced to bool true
[2026-08-25 16:49:41] 00:00 +20: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction non-true is coerced to false
[2026-08-25 16:49:42] 00:00 +21: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() null preferred_series in update falls back to empty list
[2026-08-25 16:49:42] 00:00 +22: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() full update payload contains all 7 keys
[2026-08-25 16:49:42] 00:01 +23: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models CoinEstateData handles custody fields and serialization correctly
[2026-08-25 16:49:42] 00:01 +24: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateAuditRecord initializes SHA-256 spot-check audit data
[2026-08-25 16:49:42] 00:01 +25: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateDocumentRegisterRecord formats NUM-DOC-YYYY-XXXXX correctly
[2026-08-25 16:49:42] 00:03 +26: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 1: deactivateBrowseDemo is idempotent
[2026-08-25 16:49:42] 00:03 +27: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 2: setDemoActiveForTest activates; deactivate clears both fields
[2026-08-25 16:49:42] 00:03 +28: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 3: isBrowseDemoMode is a pure getter with no side effects
[2026-08-25 16:49:42] 00:03 +29: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 4: getDemoCoinsStream after deactivate emits empty snapshot
[2026-08-25 16:49:42] 00:03 +30: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Calculates accurate Sheldon numerical scores
[2026-08-25 16:49:42] 00:03 +31: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Maps adjectival and unnumbered grades correctly
[2026-08-25 16:49:42] 00:03 +32: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Docks problem/details coins appropriately
[2026-08-25 16:49:42] 00:03 +33: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Sorts multi-item inventory deterministically
[2026-08-25 16:49:42] 00:03 +34: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Resolves inventory against program slots accurately
[2026-08-25 16:49:42] 00:03 +35: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Generates deterministic SHA-256 Snapshot ID matching format regex
[2026-08-25 16:49:42] 00:04 +36: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Blank Master PDF bytes without crashing
[2026-08-25 16:49:42] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] 00:04 +37: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Personalized SoR PDF bytes with legal disclaimer and snapshot hash
[2026-08-25 16:49:42] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] 00:04 +38: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Handles partial snapshot warning without breaking PDF compilation
[2026-08-25 16:49:42] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:49:42] 00:04 +39: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER-PROOF = true
[2026-08-25 16:49:42] 00:04 +40: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF = false (!isSilver gate)
[2026-08-25 16:49:42] 00:04 +41: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 16:49:42] 00:04 +42: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER = false (!isProof)
[2026-08-25 16:49:43] 00:04 +43: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:49:43] 00:04 +44: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:49:43] 00:04 +45: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER = false (!isProof)
[2026-08-25 16:49:43] 00:04 +46: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER = true
[2026-08-25 16:49:43] 00:04 +47: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:49:43] 00:04 +48: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-PROOF-T1 = false
[2026-08-25 16:49:43] 00:04 +49: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:49:43] 00:04 +50: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:49:43] 00:04 +51: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER = false
[2026-08-25 16:49:43] 00:04 +52: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER = true
[2026-08-25 16:49:43] 00:04 +53: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER-PROOF = false
[2026-08-25 16:49:43] 00:04 +54: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-PROOF = false (no 1972 clad S proof slot)
[2026-08-25 16:49:43] 00:04 +55: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER = false (not silver)
[2026-08-25 16:49:43] 00:04 +56: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER-PROOF = false
[2026-08-25 16:49:43] 00:04 +57: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-PROOF = true
[2026-08-25 16:49:43] 00:04 +58: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER-PROOF = false (not silver)
[2026-08-25 16:49:43] 00:04 +59: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER = false
[2026-08-25 16:49:43] 00:04 +60: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:49:43] 00:04 +61: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-PROOF = false (!isSilver)
[2026-08-25 16:49:43] 00:04 +62: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER = true
[2026-08-25 16:49:43] 00:04 +63: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 16:49:43] 00:04 +64: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T2 = false (!isSilver gate)
[2026-08-25 16:49:43] 00:04 +65: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:49:43] 00:04 +66: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:49:43] 00:04 +67: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:49:43] 00:04 +68: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T2 = false (!isSilver)
[2026-08-25 16:49:43] 00:04 +69: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER = false (!isProof)
[2026-08-25 16:49:43] 00:04 +70: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T1 = true (double-match, Option B)
[2026-08-25 16:49:43] 00:04 +71: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T2 = true (double-match, Option B)
[2026-08-25 16:49:44] 00:04 +72: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER-PROOF = false (not silver)
[2026-08-25 16:49:44] 00:04 +73: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER = false
[2026-08-25 16:49:44] 00:04 +74: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-PROOF = true
[2026-08-25 16:49:44] 00:04 +75: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER-PROOF = false
[2026-08-25 16:49:44] 00:04 +76: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER = false
[2026-08-25 16:49:44] 00:04 +77: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-PROOF-T1 = true (isProof && !isSilver)
[2026-08-25 16:49:44] 00:04 +78: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-SILVER-PROOF = false (isSilver is false)
[2026-08-25 16:49:44] 00:05 +79: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only PROOF = true
[2026-08-25 16:49:44] 00:05 +80: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-SILVER-PROOF = false (not S-mint)
[2026-08-25 16:49:44] 00:05 +81: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-PROOF = false (not S-mint)
[2026-08-25 16:49:44] 00:05 +82: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only P = true
[2026-08-25 16:49:44] 00:05 +83: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only PROOF = false (!isProof)
[2026-08-25 16:49:44] 00:05 +84: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only D = true
[2026-08-25 16:49:44] 00:05 +85: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only PROOF = false
[2026-08-25 16:49:44] 00:05 +86: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only P = false (wrong mint)
[2026-08-25 16:49:45] 00:05 +87: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only SMS = true
[2026-08-25 16:49:45] 00:05 +88: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only P = false (!isSMS gate)
[2026-08-25 16:49:45] 00:05 +89: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only D = false (no D slot)
[2026-08-25 16:49:45] 00:05 +90: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only P = true
[2026-08-25 16:49:45] 00:05 +91: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only SMS = false (!isSMS)
[2026-08-25 16:49:45] 00:05 +92: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only D = false (no D slot)
[2026-08-25 16:49:45] 00:05 +93: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only SMS = true
[2026-08-25 16:49:45] 00:05 +94: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only P = false
[2026-08-25 16:49:45] 00:05 +95: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only D = true
[2026-08-25 16:49:45] 00:05 +96: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only P = false (no P slot for 1968)
[2026-08-25 16:49:45] 00:05 +97: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:49:45] 00:05 +98: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver gate)
[2026-08-25 16:49:45] 00:05 +99: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only PROOF = false (S-mint)
[2026-08-25 16:49:45] 00:05 +100: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:49:45] 00:05 +101: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 16:49:45] 00:05 +102: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 6 GÇö 1975 coin: S-PROOF returns false (no valid slot exists) S-PROOF predicate would be true if reached (routing blocked by year guard)
[2026-08-25 16:49:45] 00:05 +103: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (year guard normalises to 1976)
[2026-08-25 16:49:45] 00:05 +104: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 16:49:45] 00:05 +105: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 16:49:45] 00:05 +106: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 16:49:46] 00:05 +107: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER = false
[2026-08-25 16:49:46] 00:05 +108: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER = true
[2026-08-25 16:49:46] 00:05 +109: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:49:46] 00:05 +110: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-PROOF = false (!isSilver... wait, isSilver=true, isProof=false)
[2026-08-25 16:49:46] 00:05 +111: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 16:49:46] 00:05 +112: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 16:49:46] 00:05 +113: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:49:46] 00:05 +114: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 16:49:46] 00:05 +115: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11b GÇö 1992-S Silver PR69 (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:49:46] 00:06 +177: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1 and S-PROOF-T2 both match the same S-mint clad proof item (double-slot design)
[2026-08-25 16:49:46] 00:06 +178: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof S-mint + Reverse Proof strike GåÆ matches REVERSE-PROOF
[2026-08-25 16:49:46] 00:06 +179: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof W-mint + Reverse Proof GåÆ matches REVERSE-PROOF
[2026-08-25 16:49:46] 00:06 +180: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof Reverse Proof in variety field GåÆ matches
[2026-08-25 16:49:46] 00:06 +181: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof Regular Proof (no Reverse) GåÆ does NOT match REVERSE-PROOF
[2026-08-25 16:49:46] 00:06 +182: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks P-UNC: P mint item matches
[2026-08-25 16:49:47] 00:06 +183: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks P-UNC: D mint item does not match
[2026-08-25 16:49:47] 00:06 +184: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks D-UNC: D mint matches
[2026-08-25 16:49:47] 00:06 +185: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks W-UNC: W mint matches
[2026-08-25 16:49:47] 00:06 +186: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state quarters" series
[2026-08-25 16:49:47] 00:06 +187: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state and territory quarters"
[2026-08-25 16:49:47] 00:06 +188: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Cents matches "lincoln cent" (singular)
[2026-08-25 16:49:47] 00:06 +189: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Cents matches "lincoln head penny"
[2026-08-25 16:49:47] 00:06 +190: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Wheat Pennies matches "wheat cent"
[2026-08-25 16:49:47] 00:06 +191: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Memorial Cents matches "memorial" series
[2026-08-25 16:49:47] 00:06 +192: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Shield Cents matches "shield" series
[2026-08-25 16:49:47] 00:06 +193: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Presidential Dollars matches "presidential" series
[2026-08-25 16:49:47] 00:06 +194: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Sacagawea & Native American matches "native american"
[2026-08-25 16:49:47] 00:06 +195: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Empty dbSeries always returns false
[2026-08-25 16:49:47] 00:06 +196: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Completely unrelated series returns false
[2026-08-25 16:49:47] 00:06 +197: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring MS-65 returns 65
[2026-08-25 16:49:47] 00:06 +198: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring AU-58 returns 58
[2026-08-25 16:49:47] 00:06 +199: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring VF-20 returns 20
[2026-08-25 16:49:47] 00:06 +200: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Proof/PF returns 65
[2026-08-25 16:49:47] 00:06 +201: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Details coin docks 5 points
[2026-08-25 16:49:47] 00:06 +202: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Null grade returns -1
[2026-08-25 16:49:47] 00:06 +203: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Empty string returns -1
[2026-08-25 16:49:47] 00:06 +204: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring BU/Uncirculated adjectival grade returns 63
[2026-08-25 16:49:47] 00:06 +205: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring XF adjectival grade returns 42
[2026-08-25 16:49:47] 00:06 +206: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:49:47] 00:06 +207: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:49:47] 00:06 +208: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1b. 2021-D no Program/Series
[2026-08-25 16:49:47] 00:06 +209: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1c. 2021 ATB series
[2026-08-25 16:49:47] 00:06 +210: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1d. Undated Washington Quarter coin (empty Year)
[2026-08-25 16:49:47] 00:06 +211: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 2 GÇö 1965 raw unmarked GåÆ NMM not SMS P/NMM = true
[2026-08-25 16:49:47] 00:06 +212: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 2 GÇö 1965 raw unmarked GåÆ NMM not SMS SMS = false
[2026-08-25 16:49:48] 00:07 +213: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3 GÇö 1965 SP67 GåÆ SMS only NOT NMM (double-stamp fix) SMS = true
[2026-08-25 16:49:48] 00:07 +214: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3 GÇö 1965 SP67 GåÆ SMS only NOT NMM (double-stamp fix) P/NMM = false (!isSMS gate)
[2026-08-25 16:49:48] 00:07 +215: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) SMS = true
[2026-08-25 16:49:48] 00:07 +216: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) P/NMM = false
[2026-08-25 16:49:48] 00:07 +217: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM PROOF = true
[2026-08-25 16:49:48] 00:07 +218: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM P/NMM = false (!isProof)
[2026-08-25 16:49:48] 00:07 +219: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:49:48] 00:07 +220: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 16:49:48] 00:07 +221: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER = false (!isProof)
[2026-08-25 16:49:48] 00:07 +222: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:49:48] 00:07 +223: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false
[2026-08-25 16:49:48] 00:07 +224: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (PR69 triggers isProof)
[2026-08-25 16:49:48] 00:07 +225: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER = false
[2026-08-25 16:49:48] 00:07 +226: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false
[2026-08-25 16:49:48] 00:07 +227: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 7 GÇö 1938-D GåÆ no Classic slot 1938-D owns nothing
[2026-08-25 16:49:48] 00:07 +228: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 8 GÇö Integer year handled by toString() year int 2021 GåÆ 0 owned Classic slots
[2026-08-25 16:49:48] 00:07 +229: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity (setUpAll)
[2026-08-25 16:49:48] 00:07 +229: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Dataset contains exactly 100 items
[2026-08-25 16:49:48] 00:07 +230: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Certified-to-Raw ratio meets 60/40 estate credibility requirement
[2026-08-25 16:49:48] =ƒôè Demo Dataset Ratio: 60 Certified / 40 Raw
[2026-08-25 16:49:48] 00:07 +231: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Multi-View dataset distribution covers Coins, Currency, and World items
[2026-08-25 16:49:48] =ƒîÉ Multi-View Items: 90 US Coins, 5 Banknotes, 5 World Items
[2026-08-25 16:49:48] 00:07 +232: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Zero missing or null critical fields across all 100 items
[2026-08-25 16:49:48] 00:07 +233: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity (tearDownAll)
[2026-08-25 16:49:48] 00:07 +233: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing PCGS URL formatting & whitespace trimming
[2026-08-25 16:49:48] 00:07 +234: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing NGC URL formatting & slash stripping
[2026-08-25 16:49:48] 00:07 +235: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing ANACS URL formatting
[2026-08-25 16:49:48] 00:07 +236: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing CAC Sticker vs CACG primary slab URL routing
[2026-08-25 16:49:48] 00:07 +237: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing Raw / Uncertified / Malformed cert strings return null safely
[2026-08-25 16:49:48] 00:07 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (setUpAll)
[2026-08-25 16:49:49] 00:07 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark 5,000-row collection generation check
[2026-08-25 16:49:49] 00:07 +239: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Year completes in < 30ms
[2026-08-25 16:49:49] GÅ¦n+Å 5,000-row Year sort time: 19.06 ms
[2026-08-25 16:49:49] 00:07 +240: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Condition (Sheldon Scale) completes in < 30ms
[2026-08-25 16:49:49] GÅ¦n+Å 5,000-row Condition sort time: 3.023 ms
[2026-08-25 16:49:49] 00:07 +241: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Cert # completes in < 30ms
[2026-08-25 16:49:49] GÅ¦n+Å 5,000-row Cert # sort time: 5.28 ms
[2026-08-25 16:49:49] 00:07 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (tearDownAll)
[2026-08-25 16:49:49] 00:07 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Rapid nextStep concurrency check (100 calls)
[2026-08-25 16:49:49] 00:07 +243: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Reset and re-start guest tour
[2026-08-25 16:49:49] 00:08 +244: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Estate / Liquidation Mode satisfies exact mathematical parity
[2026-08-25 16:49:49] 00:08 +245: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Retail Mode satisfies exact mathematical parity
[2026-08-25 16:49:49] 00:08 +246: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Collection Stats Schema Contract matches required fields
[2026-08-25 16:49:49] 00:08 +247: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Unauthenticated path guard blocks query with unknown in path
[2026-08-25 16:49:49] 00:08 +248: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/widget_test.dart: App smoke test placeholder
[2026-08-25 16:49:49] 00:09 +249: All tests passed!
[2026-08-25 16:49:49] flutter test: PASS
[2026-08-25 16:49:49] === LAYER 1: UX Visual Guard ===
[2026-08-25 16:50:06] Gùç injected env (2) from ..\numista_tests\.env // tip: Gîÿ enable debugging { debug: true }
[2026-08-25 16:50:06] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:50:06] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:50:06] SyntaxError: C:\Users\ericd\Documents\MyVertexProject\numista_qc\layer_1_ux_visual\theme_switch_guard.spec.js: Unexpected token (164:66)
[2026-08-25 16:50:06] 
[2026-08-25 16:50:06]   162 |
[2026-08-25 16:50:06]   163 |     // Switch to dark GÇö use whichever toggle element was found
[2026-08-25 16:50:06] > 164 |     if (await themeBtn.first().isVisible({ timeout: 500 }).catch(() =&gt; false)) {
[2026-08-25 16:50:06]       |                                                                   ^
[2026-08-25 16:50:06]   165 |       await themeBtn.first().click();
[2026-08-25 16:50:06]   166 |     } else {
[2026-08-25 16:50:06]   167 |       await themeSwitch.first().click();
[2026-08-25 16:50:07] 
[2026-08-25 16:50:07]    at layer_1_ux_visual\theme_switch_guard.spec.js:164
[2026-08-25 16:50:07] 
[2026-08-25 16:50:07]   162 |
[2026-08-25 16:50:07]   163 |     // Switch to dark GÇö use whichever toggle element was found
[2026-08-25 16:50:07] > 164 |     if (await themeBtn.first().isVisible({ timeout: 500 }).catch(() =&gt; false)) {
[2026-08-25 16:50:07]       |                                                                  ^
[2026-08-25 16:50:07]   165 |       await themeBtn.first().click();
[2026-08-25 16:50:07]   166 |     } else {
[2026-08-25 16:50:07]   167 |       await themeSwitch.first().click();
[2026-08-25 16:50:07] 
[2026-08-25 16:50:07] 
[2026-08-25 16:50:07] To open last HTML report run:
[2026-08-25 16:50:07] [36m[39m
[2026-08-25 16:50:07] [36m  npx playwright show-report playwright-report[39m
[2026-08-25 16:50:07] [36m[39m
[2026-08-25 16:50:07] LAYER 1: FAIL
[2026-08-25 16:50:07] numista_qc block appended to SCAN_REPORT.md
[2026-08-25 16:50:07] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 16:55:25] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 16:55:25] QA project: numista-qc
[2026-08-25 16:55:25] Running seed_qc_fixtures.py --check...
[2026-08-25 16:55:31] Fixtures OK.
[2026-08-25 16:55:31] Checking Cloud Run secrets (non-blocking)...
[2026-08-25 16:55:33] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 16:55:33] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 16:55:52] Model ID scan: no deprecated patterns found.
[2026-08-25 16:55:52] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 16:55:52] === Flutter Checks (analyze + test) ===
[2026-08-25 16:56:01] Analyzing numista_mobile...                                     
[2026-08-25 16:56:01] 
[2026-08-25 16:56:02] warning - Unused import: 'package:file_picker/file_picker.dart' - ..\numista_mobile\lib\screens\customer_service_screen.dart:5:8 - unused_import
[2026-08-25 16:56:02]    info - 'dart:html' is deprecated and shouldn't be used. Use package:web and dart:js_interop instead - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:1 - deprecated_member_use
[2026-08-25 16:56:02] warning - Unused import: 'dart:html' - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:8 - unused_import
[2026-08-25 16:56:02] warning - Unused import: 'dart:typed_data' - ..\numista_mobile\lib\screens\customer_service_screen.dart:8:8 - unused_import
[2026-08-25 16:56:02]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:51:7 - use_null_aware_elements
[2026-08-25 16:56:02]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:132:7 - use_null_aware_elements
[2026-08-25 16:56:02]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:133:7 - use_null_aware_elements
[2026-08-25 16:56:02]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:134:7 - use_null_aware_elements
[2026-08-25 16:56:02] 
[2026-08-25 16:56:02] 8 issues found. (ran in 6.2s)
[2026-08-25 16:56:02] flutter analyze: FAIL (errors found)
[2026-08-25 16:56:13] 00:00 +0: loading C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart
[2026-08-25 16:56:13] 00:00 +0: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains redundant tab navigation instructions
[2026-08-25 16:56:13] 00:00 +1: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains outdated color button references
[2026-08-25 16:56:13] 00:00 +2: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit MorganGuideService supports context-aware initialStep
[2026-08-25 16:56:13] 00:00 +3: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default profile has all required keys
[2026-08-25 16:56:13] 00:00 +4: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default preferred_services are PCGS and NGC
[2026-08-25 16:56:13] 00:00 +5: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default opt_in_chat_extraction is true
[2026-08-25 16:56:13] 00:00 +6: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default investment_goal is numismatic_study
[2026-08-25 16:56:13] 00:00 +7: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default budget_tier is intermediate
[2026-08-25 16:56:13] 00:00 +8: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() empty input returns all default values
[2026-08-25 16:56:13] 00:00 +9: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() valid profile data is preserved through normalization
[2026-08-25 16:56:13] 00:00 +10: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_series is replaced with empty list
[2026-08-25 16:56:13] 00:00 +11: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_services falls back to PCGS/NGC defaults
[2026-08-25 16:56:13] 00:00 +12: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() null opt_in_chat_extraction defaults to true
[2026-08-25 16:56:14] 00:00 +13: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() false opt_in_chat_extraction is preserved as false
[2026-08-25 16:56:14] 00:00 +14: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() integer grades are coerced to strings
[2026-08-25 16:56:14] 00:00 +15: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() preferred_series list elements are coerced to strings
[2026-08-25 16:56:14] 00:00 +16: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() extra unknown fields from API are preserved
[2026-08-25 16:56:14] 00:00 +17: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() empty updates produces empty payload
[2026-08-25 16:56:14] 00:00 +18: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() only specified keys are included in payload
[2026-08-25 16:56:14] 00:00 +19: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction true is coerced to bool true
[2026-08-25 16:56:14] 00:00 +20: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction non-true is coerced to false
[2026-08-25 16:56:14] 00:00 +21: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() null preferred_series in update falls back to empty list
[2026-08-25 16:56:14] 00:00 +22: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() full update payload contains all 7 keys
[2026-08-25 16:56:14] 00:01 +23: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models CoinEstateData handles custody fields and serialization correctly
[2026-08-25 16:56:14] 00:01 +24: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateAuditRecord initializes SHA-256 spot-check audit data
[2026-08-25 16:56:14] 00:01 +25: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateDocumentRegisterRecord formats NUM-DOC-YYYY-XXXXX correctly
[2026-08-25 16:56:14] 00:01 +26: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 1: deactivateBrowseDemo is idempotent
[2026-08-25 16:56:14] 00:01 +27: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 2: setDemoActiveForTest activates; deactivate clears both fields
[2026-08-25 16:56:14] 00:01 +28: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 3: isBrowseDemoMode is a pure getter with no side effects
[2026-08-25 16:56:14] 00:01 +29: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 4: getDemoCoinsStream after deactivate emits empty snapshot
[2026-08-25 16:56:14] 00:02 +30: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Calculates accurate Sheldon numerical scores
[2026-08-25 16:56:14] 00:02 +31: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Maps adjectival and unnumbered grades correctly
[2026-08-25 16:56:14] 00:02 +32: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Docks problem/details coins appropriately
[2026-08-25 16:56:14] 00:02 +33: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Sorts multi-item inventory deterministically
[2026-08-25 16:56:14] 00:02 +34: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Resolves inventory against program slots accurately
[2026-08-25 16:56:14] 00:02 +35: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Generates deterministic SHA-256 Snapshot ID matching format regex
[2026-08-25 16:56:14] 00:02 +36: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Blank Master PDF bytes without crashing
[2026-08-25 16:56:14] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:14] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:14] 00:02 +37: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Personalized SoR PDF bytes with legal disclaimer and snapshot hash
[2026-08-25 16:56:14] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:14] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:14] 00:02 +38: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Handles partial snapshot warning without breaking PDF compilation
[2026-08-25 16:56:14] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:14] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 16:56:15] 00:02 +39: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER-PROOF = true
[2026-08-25 16:56:15] 00:02 +40: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF = false (!isSilver gate)
[2026-08-25 16:56:15] 00:02 +41: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 16:56:15] 00:02 +42: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER = false (!isProof)
[2026-08-25 16:56:15] 00:02 +43: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:56:15] 00:02 +44: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:56:15] 00:02 +45: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER = false (!isProof)
[2026-08-25 16:56:15] 00:02 +46: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER = true
[2026-08-25 16:56:15] 00:02 +47: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:56:15] 00:02 +48: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-PROOF-T1 = false
[2026-08-25 16:56:15] 00:02 +49: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:56:15] 00:02 +50: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:56:15] 00:02 +51: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER = false
[2026-08-25 16:56:15] 00:02 +52: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER = true
[2026-08-25 16:56:15] 00:02 +53: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER-PROOF = false
[2026-08-25 16:56:15] 00:02 +54: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-PROOF = false (no 1972 clad S proof slot)
[2026-08-25 16:56:15] 00:02 +55: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER = false (not silver)
[2026-08-25 16:56:15] 00:02 +56: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER-PROOF = false
[2026-08-25 16:56:15] 00:02 +57: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-PROOF = true
[2026-08-25 16:56:15] 00:02 +58: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER-PROOF = false (not silver)
[2026-08-25 16:56:15] 00:02 +59: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER = false
[2026-08-25 16:56:15] 00:02 +60: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:56:15] 00:02 +61: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-PROOF = false (!isSilver)
[2026-08-25 16:56:15] 00:02 +62: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER = true
[2026-08-25 16:56:15] 00:02 +63: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 16:56:15] 00:02 +64: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T2 = false (!isSilver gate)
[2026-08-25 16:56:15] 00:02 +65: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:56:15] 00:02 +66: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER-PROOF = true
[2026-08-25 16:56:15] 00:02 +67: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 16:56:15] 00:02 +68: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T2 = false (!isSilver)
[2026-08-25 16:56:15] 00:02 +69: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER = false (!isProof)
[2026-08-25 16:56:16] 00:02 +70: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T1 = true (double-match, Option B)
[2026-08-25 16:56:16] 00:02 +71: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T2 = true (double-match, Option B)
[2026-08-25 16:56:16] 00:02 +72: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER-PROOF = false (not silver)
[2026-08-25 16:56:16] 00:02 +73: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER = false
[2026-08-25 16:56:16] 00:02 +74: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-PROOF = true
[2026-08-25 16:56:16] 00:02 +75: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER-PROOF = false
[2026-08-25 16:56:16] 00:02 +76: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER = false
[2026-08-25 16:56:16] 00:02 +77: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-PROOF-T1 = true (isProof && !isSilver)
[2026-08-25 16:56:16] 00:02 +78: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-SILVER-PROOF = false (isSilver is false)
[2026-08-25 16:56:16] 00:02 +79: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only PROOF = true
[2026-08-25 16:56:16] 00:02 +80: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-SILVER-PROOF = false (not S-mint)
[2026-08-25 16:56:16] 00:02 +81: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-PROOF = false (not S-mint)
[2026-08-25 16:56:16] 00:02 +82: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only P = true
[2026-08-25 16:56:16] 00:03 +83: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only PROOF = false (!isProof)
[2026-08-25 16:56:16] 00:03 +84: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only D = true
[2026-08-25 16:56:16] 00:03 +85: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only PROOF = false
[2026-08-25 16:56:17] 00:03 +86: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only P = false (wrong mint)
[2026-08-25 16:56:17] 00:03 +87: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only SMS = true
[2026-08-25 16:56:17] 00:03 +88: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only P = false (!isSMS gate)
[2026-08-25 16:56:17] 00:03 +89: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only D = false (no D slot)
[2026-08-25 16:56:17] 00:03 +90: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only P = true
[2026-08-25 16:56:17] 00:03 +91: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only SMS = false (!isSMS)
[2026-08-25 16:56:17] 00:03 +92: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only D = false (no D slot)
[2026-08-25 16:56:17] 00:03 +93: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only SMS = true
[2026-08-25 16:56:17] 00:03 +94: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only P = false
[2026-08-25 16:56:17] 00:03 +95: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only D = true
[2026-08-25 16:56:17] 00:03 +96: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only P = false (no P slot for 1968)
[2026-08-25 16:56:17] 00:03 +97: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:56:17] 00:03 +98: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver gate)
[2026-08-25 16:56:17] 00:03 +99: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only PROOF = false (S-mint)
[2026-08-25 16:56:17] 00:03 +100: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:56:17] 00:03 +101: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 16:56:17] 00:03 +102: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 6 GÇö 1975 coin: S-PROOF returns false (no valid slot exists) S-PROOF predicate would be true if reached (routing blocked by year guard)
[2026-08-25 16:56:17] 00:03 +103: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (year guard normalises to 1976)
[2026-08-25 16:56:17] 00:03 +104: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 16:56:17] 00:03 +105: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 16:56:17] 00:03 +106: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 16:56:17] 00:03 +107: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER = false
[2026-08-25 16:56:17] 00:03 +108: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER = true
[2026-08-25 16:56:18] 00:03 +109: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER-PROOF = false (!isProof)
[2026-08-25 16:56:18] 00:03 +110: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-PROOF = false (!isSilver... wait, isSilver=true, isProof=false)
[2026-08-25 16:56:18] 00:03 +111: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 16:56:18] 00:03 +112: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 16:56:18] 00:03 +113: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:56:18] 00:03 +114: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 16:56:18] 00:03 +115: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11b GÇö 1992-S Silver PR69 (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 16:56:18] 00:03 +116: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11b GÇö 1992-S Silver PR69 (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 16:56:18] 00:03 +117: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 12 GÇö 2025-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 16:56:18] 00:03 +118: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 12 GÇö 2025-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false
[2026-08-25 16:56:18] 00:03 +119: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 13 GÇö 2025-S Silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:56:18] 00:03 +120: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 13 GÇö 2025-S Silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 16:56:18] 00:03 +121: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Empty country field passes (domestic default)
[2026-08-25 16:56:18] 00:03 +122: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = United States passes
[2026-08-25 16:56:18] 00:03 +123: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = USA passes
[2026-08-25 16:56:18] 00:03 +124: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = US passes
[2026-08-25 16:56:18] 00:03 +125: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Explicit non-US country is rejected
[2026-08-25 16:56:18] 00:03 +126: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Foreign coin (Mexico) is rejected
[2026-08-25 16:56:18] 00:03 +127: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard UK coin is rejected
[2026-08-25 16:56:18] 00:03 +128: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Quarter program rejects non-quarter denomination
[2026-08-25 16:56:18] 00:03 +129: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Quarter program accepts quarter denomination
[2026-08-25 16:56:18] 00:03 +130: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Cent program rejects penny-less denomination
[2026-08-25 16:56:18] 00:03 +131: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Cent program accepts penny denomination
[2026-08-25 16:56:18] 00:03 +132: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Nickel program rejects quarter denomination
[2026-08-25 16:56:18] 00:03 +133: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Dime program rejects cent denomination
[2026-08-25 16:56:18] 00:03 +134: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Year mismatch rejects slot
[2026-08-25 16:56:18] 00:03 +135: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Year match passes slot
[2026-08-25 16:56:18] 00:03 +136: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Empty slot year passes any item year
[2026-08-25 16:56:18] 00:03 +137: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver metal + no proof GåÆ matches S-SILVER
[2026-08-25 16:56:18] 00:03 +138: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver in variety (no proof token) GåÆ matches S-SILVER
[2026-08-25 16:56:18] 00:03 +139: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + proof strike GåÆ does NOT match S-SILVER (goes to S-SILVER-PROOF)
[2026-08-25 16:56:19] 00:03 +140: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + PROOF in variety field GåÆ does NOT match S-SILVER
[2026-08-25 16:56:19] 00:03 +141: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + PR69 grade GåÆ does NOT match S-SILVER (grade-based proof detection)
[2026-08-25 16:56:19] 00:03 +142: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) D-mint + silver GåÆ does NOT match S-SILVER (wrong mint)
[2026-08-25 16:56:19] 00:03 +143: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + no silver content GåÆ does NOT match S-SILVER
[2026-08-25 16:56:19] 00:03 +144: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + proof strike GåÆ matches S-SILVER-PROOF
[2026-08-25 16:56:19] 00:03 +145: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + PR69 grade GåÆ matches S-SILVER-PROOF (grade-based proof detection)
[2026-08-25 16:56:19] 00:03 +146: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + PF70 grade GåÆ matches S-SILVER-PROOF
[2026-08-25 16:56:19] 00:03 +147: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + Silver Proof Set in variety GåÆ matches S-SILVER-PROOF
[2026-08-25 16:56:19] 00:03 +148: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + NO proof GåÆ does NOT match S-SILVER-PROOF (goes to S-SILVER)
[2026-08-25 16:56:19] 00:03 +149: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + clad + proof GåÆ does NOT match S-SILVER-PROOF (no silver)
[2026-08-25 16:56:19] 00:03 +150: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) D-mint + silver + proof GåÆ does NOT match S-SILVER-PROOF (wrong mint)
[2026-08-25 16:56:19] 00:03 +151: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) Reverse proof S-mint silver also matches S-SILVER-PROOF (isProof=true from PROOF in strikeType)
[2026-08-25 16:56:19] 00:03 +152: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark matches P-UNC variety (Philadelphia no mint mark)
[2026-08-25 16:56:19] 00:03 +153: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark does NOT match D-UNC variety
[2026-08-25 16:56:19] 00:03 +154: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) NONE mint mark is treated as Philadelphia (matches P-UNC)
[2026-08-25 16:56:19] 00:03 +155: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Philadelphia spelled out matches P-UNC
[2026-08-25 16:56:19] 00:03 +156: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark coin with Proof strike does NOT match P-UNC (goes to PROOF)
[2026-08-25 16:56:19] 00:03 +157: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark coin with PR65 grade does NOT match P-UNC (grade-based proof)
[2026-08-25 16:56:19] 00:03 +158: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) 1965-67 SMS coin does NOT match P-UNC (routes to SMS slot)
[2026-08-25 16:56:19] 00:03 +159: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) 1965-67 SMS coin with SP67 grade does NOT match P-UNC
[2026-08-25 16:56:19] 00:03 +160: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with 250 in Theme/Subject passes privy gate (P-UNC resolves true)
[2026-08-25 16:56:19] 00:03 +161: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with AMERICA250 in official title passes privy gate
[2026-08-25 16:56:19] 00:03 +162: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with SEMIQUINCENTENNIAL passes privy gate
[2026-08-25 16:56:19] 00:03 +164: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with just Anniversary (no 250) is rejected by privy gate
[2026-08-25 16:56:19] 00:03 +165: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate PRIVY alone in variety text is rejected by privy gate
[2026-08-25 16:56:19] 00:03 +166: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + proof strike GåÆ matches S-PROOF
[2026-08-25 16:56:19] 00:03 +167: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + proof in variety field GåÆ matches S-PROOF
[2026-08-25 16:56:19] 00:03 +168: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + no proof GåÆ does NOT match S-PROOF
[2026-08-25 16:56:19] 00:03 +169: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD D-mint + proof GåÆ does NOT match S-PROOF (wrong mint)
[2026-08-25 16:56:19] 00:03 +170: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + clad proof GåÆ matches (startsWith S-PROOF-)
[2026-08-25 16:56:19] 00:03 +171: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T2: S-mint + clad proof GåÆ matches (startsWith S-PROOF-)
[2026-08-25 16:56:19] 00:03 +172: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + silver proof GåÆ does NOT match (silver routes to S-SILVER-PROOF)
[2026-08-25 16:56:19] 00:03 +173: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T2: S-mint + silver proof GåÆ does NOT match
[2026-08-25 16:56:19] 00:03 +174: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: D-mint + proof GåÆ does NOT match (wrong mint)
[2026-08-25 16:56:20] 00:03 +175: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + BU (no proof) GåÆ does NOT match
[2026-08-25 16:56:20] 00:03 +176: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: PR68 grade on S-mint clad GåÆ matches (grade-based proof detection)
[2026-08-25 16:56:20] 00:03 +177: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +178: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +179: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +180: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +181: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +182: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +183: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +184: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 16:56:20] 00:03 +185: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks D-UNC: D mint matches
[2026-08-25 16:56:20] 00:03 +186: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1b. 2021-D no Program/Series
[2026-08-25 16:56:20] 00:03 +187: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks W-UNC: W mint matches
[2026-08-25 16:56:20] 00:03 +188: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1c. 2021 ATB series
[2026-08-25 16:56:20] 00:03 +189: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state quarters" series
[2026-08-25 16:56:20] 00:03 +190: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1d. Undated Washington Quarter coin (empty Year)
[2026-08-25 16:56:20] 00:03 +191: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state and territory quarters"
[2026-08-25 16:56:20] 00:03 +192: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 2 GÇö 1965 raw unmarked GåÆ NMM not SMS P/NMM = true
[2026-08-25 16:56:20] 00:03 +193: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 2 GÇö 1965 raw unmarked GåÆ NMM not SMS P/NMM = true
[2026-08-25 16:56:20] 00:03 +194: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Cents matches "lincoln head penny"
[2026-08-25 16:56:20] 00:03 +195: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 2 GÇö 1965 raw unmarked GåÆ NMM not SMS SMS = false
[2026-08-25 16:56:20] 00:03 +196: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Wheat Pennies matches "wheat cent"
[2026-08-25 16:56:20] 00:03 +197: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3 GÇö 1965 SP67 GåÆ SMS only NOT NMM (double-stamp fix) SMS = true
[2026-08-25 16:56:20] 00:03 +198: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Memorial Cents matches "memorial" series
[2026-08-25 16:56:20] 00:03 +199: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3 GÇö 1965 SP67 GåÆ SMS only NOT NMM (double-stamp fix) P/NMM = false (!isSMS gate)
[2026-08-25 16:56:20] 00:03 +200: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Shield Cents matches "shield" series
[2026-08-25 16:56:20] 00:03 +201: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) SMS = true
[2026-08-25 16:56:20] 00:03 +202: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Presidential Dollars matches "presidential" series
[2026-08-25 16:56:20] 00:03 +203: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) P/NMM = false
[2026-08-25 16:56:20] 00:03 +204: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Sacagawea & Native American matches "native american"
[2026-08-25 16:56:20] 00:03 +205: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM PROOF = true
[2026-08-25 16:56:20] 00:03 +206: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Empty dbSeries always returns false
[2026-08-25 16:56:21] 00:03 +207: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM P/NMM = false (!isProof)
[2026-08-25 16:56:21] 00:03 +208: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Completely unrelated series returns false
[2026-08-25 16:56:21] 00:03 +209: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:56:21] 00:03 +210: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring MS-65 returns 65
[2026-08-25 16:56:21] 00:03 +211: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 16:56:21] 00:03 +212: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER = false (!isProof)
[2026-08-25 16:56:21] 00:03 +213: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER = false (!isProof)
[2026-08-25 16:56:21] 00:03 +214: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring VF-20 returns 20
[2026-08-25 16:56:21] 00:03 +215: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 16:56:21] 00:03 +216: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false
[2026-08-25 16:56:21] 00:03 +217: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Proof/PF returns 65
[2026-08-25 16:56:21] 00:03 +218: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (PR69 triggers isProof)
[2026-08-25 16:56:21] 00:03 +219: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Details coin docks 5 points
[2026-08-25 16:56:21] 00:03 +220: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER = false
[2026-08-25 16:56:21] 00:03 +221: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Null grade returns -1
[2026-08-25 16:56:21] 00:03 +222: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false
[2026-08-25 16:56:21] 00:03 +223: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Empty string returns -1
[2026-08-25 16:56:21] 00:03 +224: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring BU/Uncirculated adjectival grade returns 63
[2026-08-25 16:56:21] 00:03 +225: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 7 GÇö 1938-D GåÆ no Classic slot 1938-D owns nothing
[2026-08-25 16:56:21] 00:03 +226: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring XF adjectival grade returns 42
[2026-08-25 16:56:21] 00:03 +227: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 8 GÇö Integer year handled by toString() year int 2021 GåÆ 0 owned Classic slots
[2026-08-25 16:56:21] 00:03 +228: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Higher MS score ranks above lower
[2026-08-25 16:56:21] 00:04 +233: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing PCGS URL formatting & whitespace trimming
[2026-08-25 16:56:21] 00:04 +234: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing NGC URL formatting & slash stripping
[2026-08-25 16:56:21] 00:04 +235: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing ANACS URL formatting
[2026-08-25 16:56:21] 00:04 +236: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing CAC Sticker vs CACG primary slab URL routing
[2026-08-25 16:56:21] 00:04 +237: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing Raw / Uncertified / Malformed cert strings return null safely
[2026-08-25 16:56:21] 00:04 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (setUpAll)
[2026-08-25 16:56:21] 00:04 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark 5,000-row collection generation check
[2026-08-25 16:56:21] 00:04 +239: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Year completes in < 30ms
[2026-08-25 16:56:21] GÅ¦n+Å 5,000-row Year sort time: 4.796 ms
[2026-08-25 16:56:21] 00:04 +240: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Condition (Sheldon Scale) completes in < 30ms
[2026-08-25 16:56:21] GÅ¦n+Å 5,000-row Condition sort time: 1.429 ms
[2026-08-25 16:56:22] 00:04 +241: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Cert # completes in < 30ms
[2026-08-25 16:56:22] GÅ¦n+Å 5,000-row Cert # sort time: 2.691 ms
[2026-08-25 16:56:22] 00:04 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (tearDownAll)
[2026-08-25 16:56:22] 00:04 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Rapid nextStep concurrency check (100 calls)
[2026-08-25 16:56:22] 00:04 +243: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Reset and re-start guest tour
[2026-08-25 16:56:22] 00:04 +244: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Estate / Liquidation Mode satisfies exact mathematical parity
[2026-08-25 16:56:22] 00:04 +245: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Retail Mode satisfies exact mathematical parity
[2026-08-25 16:56:22] 00:04 +246: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Collection Stats Schema Contract matches required fields
[2026-08-25 16:56:22] 00:04 +247: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Unauthenticated path guard blocks query with unknown in path
[2026-08-25 16:56:22] 00:04 +248: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/widget_test.dart: App smoke test placeholder
[2026-08-25 16:56:22] 00:05 +249: All tests passed!
[2026-08-25 16:56:22] flutter test: PASS
[2026-08-25 16:56:22] === LAYER 1: UX Visual Guard ===
[2026-08-25 16:59:13] Gùç injected env (2) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:59:13] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:59:13] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:59:13] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê secrets for agents [www.dotenvx.com]
[2026-08-25 16:59:13] 
[2026-08-25 16:59:13] Running 10 tests using 1 worker
[2026-08-25 16:59:13] 
[2026-08-25 16:59:13] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 16:59:13] WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
[2026-08-25 16:59:13] E0000 00:00:1787691387.805939   17680 alts_credentials.cc:93] ALTS creds ignored. Not running on GCP and untrusted ALTS is not enabled.
[2026-08-25 16:59:13] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 16:59:13] [coin_data_audit] No canonical_title_field in manifest n++ quad-check active (['title', 'theme_subject', 'series', 'program_series'])
[2026-08-25 16:59:13] [coin_data_audit] Auditing coins...
[2026-08-25 16:59:13]   [TITLE_OK] qc_fixture_estate_coin: non-empty fields=['title', 'series']
[2026-08-25 16:59:13]   [TITLE_OK] qc_fixture_foreign_coin: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 16:59:13]   [TITLE_OK] qc_fixture_title_ok_dollar: non-empty fields=['title', 'series']
[2026-08-25 16:59:13]   [TITLE_OK] qc_fixture_title_ok_quarter: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 16:59:13] [coin_data_audit] Auditing estate boundary...
[2026-08-25 16:59:13] 
[2026-08-25 16:59:13] [coin_data_audit] RESULTS: 5 PASS / 0 WARN / 0 UNEXPECTED FAIL (1 expected sentinel)
[2026-08-25 16:59:13]   PASS  [FIXTURE_SENTINEL_OK]: Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.
[2026-08-25 16:59:13]   PASS  [COINS_AUDITED]: 5 coin documents checked. 1 title failures.
[2026-08-25 16:59:13]   PASS  [ESTATE_CURRENCY_SEPARATED]: 1 currency docs confirmed separate from coins.
[2026-08-25 16:59:13]   PASS  [ESTATE_WORLD_SEPARATED]: 1 world_items docs confirmed separate from coins.
[2026-08-25 16:59:13]   PASS  [FOREIGN_COINS_IN_COINS]: 1 foreign coin(s) correctly in users/{uid}/coins.
[2026-08-25 16:59:13]   EXPECTED FAIL  [COIN_TITLE_FAIL] qc_fixture_title_FAIL_empty: All title fields empty: ['title', 'theme_subject', 'series', 'program_series']. Flutter _buildTitle() will degrade to year+mint only.
[2026-08-25 16:59:13] 
[2026-08-25 16:59:13]   ok  1 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:21:3 GÇ¦ Coin Title Guard GÇ¦ Primary: Firestore field check - no coin should have all title fields empty (4.5s)
[2026-08-25 16:59:13] [coin_title_guard] SEMANTICS_UNAVAILABLE: accessibility tree returned no nodes. Primary assertion is authoritative.
[2026-08-25 16:59:13]   -   2 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:75:3 GÇ¦ Coin Title Guard GÇ¦ Secondary: Flutter accessibility snapshot (conditional - non-authoritative)
[2026-08-25 16:59:13] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ enable debugging { debug: true }
[2026-08-25 16:59:13] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 16:59:13] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 16:59:13] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 16:59:13] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 16:59:13] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 16:59:13]   ok  3 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:176:3 GÇ¦ Contrast Guard - Light Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (14.1s)
[2026-08-25 16:59:14] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 16:59:14] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 16:59:14] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 16:59:14] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 16:59:14] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 16:59:14]   ok  4 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:207:3 GÇ¦ Contrast Guard - Dark Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (15.9s)
[2026-08-25 16:59:14] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ enable debugging { debug: true }
[2026-08-25 16:59:14]   ok  5 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:63:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ flt-glass-pane fills the viewport (19.8s)
[2026-08-25 16:59:14]   ok  6 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:79:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ No negative top/left on flt-glass-pane (not shifted off-screen) (18.5s)
[2026-08-25 16:59:14]   ok  7 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:93:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ Flutter renders in release mode (not debug banner) (19.4s)
[2026-08-25 16:59:14]   ok  8 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:104:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ Page title is set (not blank or default) (18.8s)
[2026-08-25 16:59:14] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ custom filepath { path: '/custom/path/.env' }
[2026-08-25 16:59:14] [theme_switch_guard] Theme toggle button not found at 1920x1080 (checked home + Settings). Skipping toggle test.
[2026-08-25 16:59:14]   -   9 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:78:3 GÇ¦ Theme Switch Guard GÇ¦ App remains visible after theme toggle with 500ms settle
[2026-08-25 16:59:14]   -  10 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:144:3 GÇ¦ Theme Switch Guard GÇ¦ Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 16:59:14] 
[2026-08-25 16:59:14]   3 skipped
[2026-08-25 16:59:14]   7 passed (2.8m)
[2026-08-25 16:59:14] 
[2026-08-25 16:59:14] To open last HTML report run:
[2026-08-25 16:59:14] [36m[39m
[2026-08-25 16:59:14] [36m  npx playwright show-report playwright-report[39m
[2026-08-25 16:59:14] [36m[39m
[2026-08-25 16:59:14] LAYER 1: PASS
[2026-08-25 16:59:14] numista_qc block appended to SCAN_REPORT.md
[2026-08-25 16:59:14] SUITE_RESULT: FAIL - check SESSION_LOG.md for details
[2026-08-25 17:10:15] QA UID: rxXrMBPy34N2q2ZHywCEItGHu2E2
[2026-08-25 17:10:15] QA project: numista-qc
[2026-08-25 17:10:15] Running seed_qc_fixtures.py --check...
[2026-08-25 17:10:26] WARN [CLOUD_RUN_UNREACHABLE]: gcloud call failed (non-fatal). Check manually if persistent.
[2026-08-25 17:10:26] Scanning for deprecated Gemini model IDs (non-blocking)...
[2026-08-25 17:11:24] Model ID scan: no deprecated patterns found.
[2026-08-25 17:11:24] GOOGLE_CLOUD_PROJECT set to numista-qc
[2026-08-25 17:11:24] === Flutter Checks (analyze + test) ===
[2026-08-25 17:15:00] Analyzing numista_mobile...                                     
[2026-08-25 17:15:00] 
[2026-08-25 17:15:00] warning - Unused import: 'package:file_picker/file_picker.dart' - ..\numista_mobile\lib\screens\customer_service_screen.dart:5:8 - unused_import
[2026-08-25 17:15:00]    info - 'dart:html' is deprecated and shouldn't be used. Use package:web and dart:js_interop instead - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:1 - deprecated_member_use
[2026-08-25 17:15:00] warning - Unused import: 'dart:html' - ..\numista_mobile\lib\screens\customer_service_screen.dart:7:8 - unused_import
[2026-08-25 17:15:00] warning - Unused import: 'dart:typed_data' - ..\numista_mobile\lib\screens\customer_service_screen.dart:8:8 - unused_import
[2026-08-25 17:15:00]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:51:7 - use_null_aware_elements
[2026-08-25 17:15:00]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:132:7 - use_null_aware_elements
[2026-08-25 17:15:00]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:133:7 - use_null_aware_elements
[2026-08-25 17:15:00]    info - Use the null-aware marker '?' rather than a null check via an 'if' - ..\numista_mobile\lib\services\ticket_service.dart:134:7 - use_null_aware_elements
[2026-08-25 17:15:00] 
[2026-08-25 17:15:00] 8 issues found. (ran in 210.8s)
[2026-08-25 17:15:00] flutter analyze: PASS (warnings/infos logged above)
[2026-08-25 17:15:27] 00:00 +0: loading C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart
[2026-08-25 17:15:27] 00:00 +0: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains redundant tab navigation instructions
[2026-08-25 17:15:27] 00:00 +1: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit No step contains outdated color button references
[2026-08-25 17:15:27] 00:00 +2: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/audit_morgan_guides_test.dart: Morgan Guides Proactive Audit MorganGuideService supports context-aware initialStep
[2026-08-25 17:15:27] 00:00 +3: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default profile has all required keys
[2026-08-25 17:15:27] 00:00 +4: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default preferred_services are PCGS and NGC
[2026-08-25 17:15:27] 00:00 +5: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default opt_in_chat_extraction is true
[2026-08-25 17:15:27] 00:01 +6: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default investment_goal is numismatic_study
[2026-08-25 17:15:27] 00:01 +7: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö Default Profile Contract default budget_tier is intermediate
[2026-08-25 17:15:27] 00:01 +8: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() empty input returns all default values
[2026-08-25 17:15:27] 00:01 +9: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() valid profile data is preserved through normalization
[2026-08-25 17:15:27] 00:01 +10: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_series is replaced with empty list
[2026-08-25 17:15:27] 00:01 +11: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() non-list preferred_services falls back to PCGS/NGC defaults
[2026-08-25 17:15:27] 00:01 +12: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() null opt_in_chat_extraction defaults to true
[2026-08-25 17:15:28] 00:01 +13: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() false opt_in_chat_extraction is preserved as false
[2026-08-25 17:15:28] 00:01 +14: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() integer grades are coerced to strings
[2026-08-25 17:15:28] 00:01 +15: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() preferred_series list elements are coerced to strings
[2026-08-25 17:15:28] 00:01 +16: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö normalizeProfile() extra unknown fields from API are preserved
[2026-08-25 17:15:28] 00:01 +17: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() empty updates produces empty payload
[2026-08-25 17:15:28] 00:01 +18: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() only specified keys are included in payload
[2026-08-25 17:15:28] 00:01 +19: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction true is coerced to bool true
[2026-08-25 17:15:28] 00:01 +20: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() opt_in_chat_extraction non-true is coerced to false
[2026-08-25 17:15:28] 00:01 +21: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() null preferred_series in update falls back to empty list
[2026-08-25 17:15:28] 00:01 +22: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/collector_profile_service_test.dart: CollectorProfileService GÇö buildUpdatePayload() full update payload contains all 7 keys
[2026-08-25 17:15:28] 00:02 +23: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models CoinEstateData handles custody fields and serialization correctly
[2026-08-25 17:15:28] 00:02 +24: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateAuditRecord initializes SHA-256 spot-check audit data
[2026-08-25 17:15:28] 00:02 +25: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/estate_models_test.dart: US Army Property Management Inspired Estate Models EstateDocumentRegisterRecord formats NUM-DOC-YYYY-XXXXX correctly
[2026-08-25 17:15:28] 00:04 +26: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 1: deactivateBrowseDemo is idempotent
[2026-08-25 17:15:28] 00:04 +27: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 2: setDemoActiveForTest activates; deactivate clears both fields
[2026-08-25 17:15:28] 00:04 +28: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 3: isBrowseDemoMode is a pure getter with no side effects
[2026-08-25 17:15:28] 00:04 +29: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/guest_seed_service_demo_flag_test.dart: 4: getDemoCoinsStream after deactivate emits empty snapshot
[2026-08-25 17:15:28] 00:06 +30: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Calculates accurate Sheldon numerical scores
[2026-08-25 17:15:28] 00:06 +31: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Maps adjectival and unnumbered grades correctly
[2026-08-25 17:15:28] 00:06 +32: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Docks problem/details coins appropriately
[2026-08-25 17:15:28] 00:06 +33: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SheldonGradeRanker Tests Sorts multi-item inventory deterministically
[2026-08-25 17:15:28] 00:06 +34: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Resolves inventory against program slots accurately
[2026-08-25 17:15:28] 00:06 +35: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: SlotResolver & Snapshot ID Tests Generates deterministic SHA-256 Snapshot ID matching format regex
[2026-08-25 17:15:28] 00:06 +36: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Blank Master PDF bytes without crashing
[2026-08-25 17:15:28] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:28] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:29] 00:06 +37: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Generates Personalized SoR PDF bytes with legal disclaimer and snapshot hash
[2026-08-25 17:15:29] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:29] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:29] 00:06 +38: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/services/checklist_generator_test.dart: ChecklistGeneratorService PDF Generation Tests Handles partial snapshot warning without breaking PDF compilation
[2026-08-25 17:15:29] Helvetica has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:29] Helvetica-Bold has no Unicode support see https://github.com/DavBfr/dart_pdf/wiki/Fonts-Management
[2026-08-25 17:15:29] 00:06 +39: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER-PROOF = true
[2026-08-25 17:15:29] 00:06 +40: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF = false (!isSilver gate)
[2026-08-25 17:15:29] 00:06 +41: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 17:15:29] 00:06 +42: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1 GÇö 1971-S silver proof (strike_type=PROOF) S-SILVER = false (!isProof)
[2026-08-25 17:15:29] 00:06 +43: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 17:15:29] 00:06 +44: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-PROOF-T1 = false (!isSilver)
[2026-08-25 17:15:29] 00:06 +45: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 1b GÇö 1971-S PR69 silver (empty strike_type) S-SILVER = false (!isProof)
[2026-08-25 17:15:29] 00:06 +46: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER = true
[2026-08-25 17:15:29] 00:06 +47: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-SILVER-PROOF = false (!isProof)
[2026-08-25 17:15:29] 00:07 +48: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 2 GÇö 1971-S silver BU (MS65) S-PROOF-T1 = false
[2026-08-25 17:15:29] 00:07 +49: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER-PROOF = true
[2026-08-25 17:15:29] 00:07 +50: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 17:15:29] 00:07 +51: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 3 GÇö 1972-S silver proof S-SILVER = false
[2026-08-25 17:15:29] 00:07 +52: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER = true
[2026-08-25 17:15:29] 00:07 +53: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 4 GÇö 1972-S silver BU S-SILVER-PROOF = false
[2026-08-25 17:15:29] 00:07 +54: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-PROOF = false (no 1972 clad S proof slot)
[2026-08-25 17:15:30] 00:07 +55: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER = false (not silver)
[2026-08-25 17:15:30] 00:07 +56: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 5 GÇö 1972-S clad (no metal field) GåÆ no S slot S-SILVER-PROOF = false
[2026-08-25 17:15:30] 00:07 +57: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-PROOF = true
[2026-08-25 17:15:30] 00:07 +58: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER-PROOF = false (not silver)
[2026-08-25 17:15:30] 00:07 +59: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 6 GÇö 1973-S clad proof (no metal) S-SILVER = false
[2026-08-25 17:15:30] 00:07 +60: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-SILVER-PROOF = true
[2026-08-25 17:15:30] 00:07 +61: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 7 GÇö 1973-S silver proof S-PROOF = false (!isSilver)
[2026-08-25 17:15:30] 00:07 +62: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER = true
[2026-08-25 17:15:30] 00:07 +63: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T1 = false (!isSilver gate)
[2026-08-25 17:15:30] 00:07 +64: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-PROOF-T2 = false (!isSilver gate)
[2026-08-25 17:15:30] 00:07 +65: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 8 GÇö 1976-S silver BU (T1 only) S-SILVER-PROOF = false (!isProof)
[2026-08-25 17:15:30] 00:07 +66: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER-PROOF = true
[2026-08-25 17:15:30] 00:07 +67: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T1 = false (!isSilver)
[2026-08-25 17:15:30] 00:07 +68: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-PROOF-T2 = false (!isSilver)
[2026-08-25 17:15:30] 00:07 +69: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 9 GÇö 1976-S silver proof S-SILVER = false (!isProof)
[2026-08-25 17:15:30] 00:07 +70: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T1 = true (double-match, Option B)
[2026-08-25 17:15:30] 00:07 +71: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-PROOF-T2 = true (double-match, Option B)
[2026-08-25 17:15:30] 00:07 +72: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER-PROOF = false (not silver)
[2026-08-25 17:15:30] 00:07 +73: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 10 GÇö 1976-S clad proof GåÆ both S-PROOF-T1 and S-PROOF-T2 (Option B) S-SILVER = false
[2026-08-25 17:15:31] 00:07 +74: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-PROOF = true
[2026-08-25 17:15:31] 00:07 +75: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER-PROOF = false
[2026-08-25 17:15:31] 00:07 +76: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 11 GÇö 1977-S clad proof S-SILVER = false
[2026-08-25 17:15:31] 00:07 +77: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-PROOF-T1 = true (isProof && !isSilver)
[2026-08-25 17:15:31] 00:07 +78: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_eisenhower_test.dart: Test 12 GÇö startsWith fix: 1976-S PR67 never hits S-SILVER-PROOF S-SILVER-PROOF = false (isSilver is false)
[2026-08-25 17:15:31] 00:08 +79: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only PROOF = true
[2026-08-25 17:15:31] 00:08 +80: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-SILVER-PROOF = false (not S-mint)
[2026-08-25 17:15:31] 00:08 +81: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1 GÇö 1964 Philly proof GåÆ PROOF only S-PROOF = false (not S-mint)
[2026-08-25 17:15:32] 00:08 +82: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only P = true
[2026-08-25 17:15:32] 00:08 +83: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1b GÇö 1964-P business strike GåÆ P only PROOF = false (!isProof)
[2026-08-25 17:15:32] 00:08 +84: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only D = true
[2026-08-25 17:15:32] 00:08 +85: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only PROOF = false
[2026-08-25 17:15:32] 00:08 +86: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 1c GÇö 1964-D business strike GåÆ D only P = false (wrong mint)
[2026-08-25 17:15:32] 00:08 +87: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only SMS = true
[2026-08-25 17:15:32] 00:08 +88: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only P = false (!isSMS gate)
[2026-08-25 17:15:32] 00:08 +89: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2 GÇö 1965 SMS grade (SP67) GåÆ SMS only D = false (no D slot)
[2026-08-25 17:15:33] 00:08 +90: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only P = true
[2026-08-25 17:15:33] 00:08 +91: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only SMS = false (!isSMS)
[2026-08-25 17:15:33] 00:08 +92: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 2b GÇö 1965 NMM business strike (MS65) GåÆ P only D = false (no D slot)
[2026-08-25 17:15:33] 00:08 +93: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only SMS = true
[2026-08-25 17:15:33] 00:08 +94: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 3 GÇö 1967 SMS GåÆ SMS only P = false
[2026-08-25 17:15:33] 00:08 +95: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only D = true
[2026-08-25 17:15:33] 00:08 +96: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 4 GÇö 1968-D 40% Ag BU GåÆ D only P = false (no P slot for 1968)
[2026-08-25 17:15:33] 00:08 +97: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 17:15:33] 00:08 +98: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver gate)
[2026-08-25 17:15:33] 00:08 +99: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5 GÇö 1968-S 40% Ag proof GåÆ S-SILVER-PROOF only PROOF = false (S-mint)
[2026-08-25 17:15:33] 00:08 +100: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 17:15:33] 00:08 +101: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 5b GÇö 1968-S PR65 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 17:15:33] 00:08 +102: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 6 GÇö 1975 coin: S-PROOF returns false (no valid slot exists) S-PROOF predicate would be true if reached (routing blocked by year guard)
[2026-08-25 17:15:33] 00:08 +103: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (year guard normalises to 1976)
[2026-08-25 17:15:33] 00:08 +104: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 7 GÇö 1776-1976-S Silver PR (dual-date) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 17:15:33] 00:08 +105: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 17:15:34] 00:08 +106: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 17:15:34] 00:08 +107: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 8 GÇö 1976-S Clad proof GåÆ S-PROOF only S-SILVER = false
[2026-08-25 17:15:34] 00:08 +108: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER = true
[2026-08-25 17:15:34] 00:08 +109: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-SILVER-PROOF = false (!isProof)
[2026-08-25 17:15:34] 00:08 +110: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 9 GÇö 1976-S Silver BU GåÆ S-SILVER only S-PROOF = false (!isSilver... wait, isSilver=true, isProof=false)
[2026-08-25 17:15:34] 00:08 +111: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 17:15:34] 00:08 +112: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 10 GÇö 1992-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false (not silver)
[2026-08-25 17:15:34] 00:08 +113: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 17:15:34] 00:08 +114: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11 GÇö 1992-S Silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 17:15:34] 00:08 +115: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11b GÇö 1992-S Silver PR69 (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (isProof via grade)
[2026-08-25 17:15:34] 00:08 +116: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 11b GÇö 1992-S Silver PR69 (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false (!isSilver)
[2026-08-25 17:15:34] 00:08 +117: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 12 GÇö 2025-S Clad proof GåÆ S-PROOF only S-PROOF = true
[2026-08-25 17:15:34] 00:08 +118: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 12 GÇö 2025-S Clad proof GåÆ S-PROOF only S-SILVER-PROOF = false
[2026-08-25 17:15:34] 00:08 +119: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 13 GÇö 2025-S Silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 17:15:34] 00:08 +120: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_kennedy_test.dart: Test 13 GÇö 2025-S Silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 17:15:34] 00:09 +121: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Empty country field passes (domestic default)
[2026-08-25 17:15:34] 00:09 +122: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = United States passes
[2026-08-25 17:15:34] 00:09 +123: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = USA passes
[2026-08-25 17:15:34] 00:09 +124: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Country = US passes
[2026-08-25 17:15:34] 00:09 +125: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Explicit non-US country is rejected
[2026-08-25 17:15:34] 00:09 +126: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard Foreign coin (Mexico) is rejected
[2026-08-25 17:15:35] 00:09 +127: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Country Guard UK coin is rejected
[2026-08-25 17:15:35] 00:09 +128: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Quarter program rejects non-quarter denomination
[2026-08-25 17:15:35] 00:09 +129: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Quarter program accepts quarter denomination
[2026-08-25 17:15:35] 00:09 +130: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Cent program rejects penny-less denomination
[2026-08-25 17:15:35] 00:09 +131: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Cent program accepts penny denomination
[2026-08-25 17:15:35] 00:09 +132: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Nickel program rejects quarter denomination
[2026-08-25 17:15:35] 00:09 +133: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Denomination Alignment Guard Dime program rejects cent denomination
[2026-08-25 17:15:35] 00:09 +134: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Year mismatch rejects slot
[2026-08-25 17:15:35] 00:09 +135: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Year match passes slot
[2026-08-25 17:15:35] 00:09 +136: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö Year Alignment Guard Empty slot year passes any item year
[2026-08-25 17:15:35] 00:09 +137: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver metal + no proof GåÆ matches S-SILVER
[2026-08-25 17:15:35] 00:09 +138: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver in variety (no proof token) GåÆ matches S-SILVER
[2026-08-25 17:15:35] 00:09 +139: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + proof strike GåÆ does NOT match S-SILVER (goes to S-SILVER-PROOF)
[2026-08-25 17:15:35] 00:09 +140: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + PROOF in variety field GåÆ does NOT match S-SILVER
[2026-08-25 17:15:35] 00:09 +141: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + silver + PR69 grade GåÆ does NOT match S-SILVER (grade-based proof detection)
[2026-08-25 17:15:35] 00:09 +142: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) D-mint + silver GåÆ does NOT match S-SILVER (wrong mint)
[2026-08-25 17:15:35] 00:09 +143: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER (BU silver only, 1976-S) S-mint + no silver content GåÆ does NOT match S-SILVER
[2026-08-25 17:15:35] 00:09 +144: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + proof strike GåÆ matches S-SILVER-PROOF
[2026-08-25 17:15:35] 00:09 +145: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + PR69 grade GåÆ matches S-SILVER-PROOF (grade-based proof detection)
[2026-08-25 17:15:35] 00:10 +146: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + PF70 grade GåÆ matches S-SILVER-PROOF
[2026-08-25 17:15:35] 00:10 +147: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + Silver Proof Set in variety GåÆ matches S-SILVER-PROOF
[2026-08-25 17:15:35] 00:10 +148: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + silver + NO proof GåÆ does NOT match S-SILVER-PROOF (goes to S-SILVER)
[2026-08-25 17:15:35] 00:10 +149: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) S-mint + clad + proof GåÆ does NOT match S-SILVER-PROOF (no silver)
[2026-08-25 17:15:35] 00:10 +150: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) D-mint + silver + proof GåÆ does NOT match S-SILVER-PROOF (wrong mint)
[2026-08-25 17:15:35] 00:10 +151: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-SILVER-PROOF (50 State Quarter silver proof) Reverse proof S-mint silver also matches S-SILVER-PROOF (isProof=true from PROOF in strikeType)
[2026-08-25 17:15:36] 00:10 +152: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark matches P-UNC variety (Philadelphia no mint mark)
[2026-08-25 17:15:36] 00:10 +153: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark does NOT match D-UNC variety
[2026-08-25 17:15:36] 00:10 +154: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) NONE mint mark is treated as Philadelphia (matches P-UNC)
[2026-08-25 17:15:36] 00:10 +155: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Philadelphia spelled out matches P-UNC
[2026-08-25 17:15:36] 00:10 +156: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark coin with Proof strike does NOT match P-UNC (goes to PROOF)
[2026-08-25 17:15:36] 00:10 +157: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) Empty mint mark coin with PR65 grade does NOT match P-UNC (grade-based proof)
[2026-08-25 17:15:36] 00:10 +158: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) 1965-67 SMS coin does NOT match P-UNC (routes to SMS slot)
[2026-08-25 17:15:36] 00:10 +159: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: No Mint Mark (NMM, pre-1980 classic series) 1965-67 SMS coin with SP67 grade does NOT match P-UNC
[2026-08-25 17:15:36] 00:10 +160: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with 250 in Theme/Subject passes privy gate (P-UNC resolves true)
[2026-08-25 17:15:36] 00:10 +161: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with AMERICA250 in official title passes privy gate
[2026-08-25 17:15:36] 00:10 +162: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with SEMIQUINCENTENNIAL passes privy gate
[2026-08-25 17:15:36] 00:10 +163: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate Item with no 250/SEMIQUINCENTENNIAL/AMERICA250 token is rejected by privy gate
[2026-08-25 17:15:36] 00:10 +165: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: requiresPrivy Gate PRIVY alone in variety text is rejected by privy gate
[2026-08-25 17:15:36] 00:10 +166: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + proof strike GåÆ matches S-PROOF
[2026-08-25 17:15:36] 00:10 +167: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + proof in variety field GåÆ matches S-PROOF
[2026-08-25 17:15:36] 00:10 +168: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD S-mint + no proof GåÆ does NOT match S-PROOF
[2026-08-25 17:15:36] 00:10 +169: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF and S-CLAD D-mint + proof GåÆ does NOT match S-PROOF (wrong mint)
[2026-08-25 17:15:36] 00:10 +170: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + clad proof GåÆ matches (startsWith S-PROOF-)
[2026-08-25 17:15:36] 00:10 +171: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T2: S-mint + clad proof GåÆ matches (startsWith S-PROOF-)
[2026-08-25 17:15:36] 00:10 +172: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + silver proof GåÆ does NOT match (silver routes to S-SILVER-PROOF)
[2026-08-25 17:15:36] 00:10 +173: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T2: S-mint + silver proof GåÆ does NOT match
[2026-08-25 17:15:36] 00:10 +174: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: D-mint + proof GåÆ does NOT match (wrong mint)
[2026-08-25 17:15:36] 00:10 +175: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: S-mint + BU (no proof) GåÆ does NOT match
[2026-08-25 17:15:37] 00:10 +176: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1: PR68 grade on S-mint clad GåÆ matches (grade-based proof detection)
[2026-08-25 17:15:37] 00:10 +177: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: S-PROOF-T1 / S-PROOF-T2 (Eisenhower Type variants) S-PROOF-T1 and S-PROOF-T2 both match the same S-mint clad proof item (double-slot design)
[2026-08-25 17:15:37] 00:10 +178: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof S-mint + Reverse Proof strike GåÆ matches REVERSE-PROOF
[2026-08-25 17:15:37] 00:10 +179: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof W-mint + Reverse Proof GåÆ matches REVERSE-PROOF
[2026-08-25 17:15:37] 00:10 +180: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof Reverse Proof in variety field GåÆ matches
[2026-08-25 17:15:37] 00:10 +181: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Reverse Proof Regular Proof (no Reverse) GåÆ does NOT match REVERSE-PROOF
[2026-08-25 17:15:37] 00:10 +182: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks P-UNC: P mint item matches
[2026-08-25 17:15:37] 00:10 +183: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks P-UNC: D mint item does not match
[2026-08-25 17:15:37] 00:10 +184: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks D-UNC: D mint matches
[2026-08-25 17:15:37] 00:10 +185: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SlotResolver GÇö matchesVariety: Standard Mint Marks W-UNC: W mint matches
[2026-08-25 17:15:37] 00:10 +186: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state quarters" series
[2026-08-25 17:15:37] 00:10 +187: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases 50 State Quarters matches "state and territory quarters"
[2026-08-25 17:15:37] 00:10 +188: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Cents matches "lincoln cent" (singular)
[2026-08-25 17:15:37] 00:10 +189: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Cents matches "lincoln head penny"
[2026-08-25 17:15:37] 00:10 +190: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Wheat Pennies matches "wheat cent"
[2026-08-25 17:15:37] 00:10 +191: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Memorial Cents matches "memorial" series
[2026-08-25 17:15:37] 00:10 +192: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Lincoln Shield Cents matches "shield" series
[2026-08-25 17:15:37] 00:10 +193: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Presidential Dollars matches "presidential" series
[2026-08-25 17:15:37] 00:10 +194: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Sacagawea & Native American matches "native american"
[2026-08-25 17:15:37] 00:10 +195: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Empty dbSeries always returns false
[2026-08-25 17:15:37] 00:10 +196: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: CoinProgram GÇö matchesDbSeries Rule 24 Aliases Completely unrelated series returns false
[2026-08-25 17:15:37] 00:10 +197: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 17:15:37] 00:10 +198: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 17:15:38] 00:10 +199: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 17:15:38] 00:10 +200: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 17:15:38] 00:10 +201: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1a. 2021-P Washington Quarter series MS-63
[2026-08-25 17:15:38] 00:10 +202: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Details coin docks 5 points
[2026-08-25 17:15:38] 00:10 +203: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1b. 2021-D no Program/Series
[2026-08-25 17:15:38] 00:10 +204: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1b. 2021-D no Program/Series
[2026-08-25 17:15:38] 00:10 +205: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring Empty string returns -1
[2026-08-25 17:15:38] 00:10 +206: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1c. 2021 ATB series
[2026-08-25 17:15:38] 00:10 +207: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_phase4a_test.dart: SheldonGradeRanker GÇö Numerical Grade Scoring BU/Uncirculated adjectival grade returns 63
[2026-08-25 17:15:38] 00:10 +208: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 1 GÇö SNAP four-coin fixture GåÆ 0 owned 1d. Undated Washington Quarter coin (empty Year)
[2026-08-25 17:15:38] 00:10 +215: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) SMS = true
[2026-08-25 17:15:38] 00:10 +216: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 3b GÇö 1967 SP-67 hyphen GåÆ SMS only (widened regex) P/NMM = false
[2026-08-25 17:15:38] 00:10 +217: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM PROOF = true
[2026-08-25 17:15:38] 00:10 +218: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 4 GÇö 1950 PR65 unmarked GåÆ PROOF not NMM P/NMM = false (!isProof)
[2026-08-25 17:15:38] 00:10 +219: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 17:15:38] 00:10 +220: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false (!isSilver)
[2026-08-25 17:15:38] 00:10 +221: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 5 GÇö 1976-S silver proof GåÆ S-SILVER-PROOF only S-SILVER = false (!isProof)
[2026-08-25 17:15:38] 00:10 +222: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-SILVER-PROOF = true
[2026-08-25 17:15:38] 00:10 +223: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6 GÇö 1992-S silver proof GåÆ S-SILVER-PROOF only S-PROOF = false
[2026-08-25 17:15:38] 00:10 +224: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER-PROOF = true (PR69 triggers isProof)
[2026-08-25 17:15:38] 00:10 +225: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-SILVER = false
[2026-08-25 17:15:38] 00:11 +226: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 6b GÇö 1992-S PR69 silver (empty strike_type) GåÆ S-SILVER-PROOF S-PROOF = false
[2026-08-25 17:15:39] 00:11 +227: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 7 GÇö 1938-D GåÆ no Classic slot 1938-D owns nothing
[2026-08-25 17:15:39] 00:11 +228: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/slot_resolver_washington_test.dart: Test 8 GÇö Integer year handled by toString() year int 2021 GåÆ 0 owned Classic slots
[2026-08-25 17:15:39] 00:11 +229: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity (setUpAll)
[2026-08-25 17:15:39] 00:11 +229: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Dataset contains exactly 100 items
[2026-08-25 17:15:39] 00:11 +230: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Certified-to-Raw ratio meets 60/40 estate credibility requirement
[2026-08-25 17:15:39] =ƒôè Demo Dataset Ratio: 60 Certified / 40 Raw
[2026-08-25 17:15:39] 00:11 +231: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Multi-View dataset distribution covers Coins, Currency, and World items
[2026-08-25 17:15:39] =ƒîÉ Multi-View Items: 90 US Coins, 5 Banknotes, 5 World Items
[2026-08-25 17:15:39] 00:11 +232: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity Zero missing or null critical fields across all 100 items
[2026-08-25 17:15:39] 00:11 +233: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 1: 100 Demo Coin Asset Integrity (tearDownAll)
[2026-08-25 17:15:39] 00:11 +233: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing PCGS URL formatting & whitespace trimming
[2026-08-25 17:15:39] 00:11 +234: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing NGC URL formatting & slash stripping
[2026-08-25 17:15:39] 00:11 +235: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing ANACS URL formatting
[2026-08-25 17:15:39] 00:11 +236: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 2: Cert Verification URL Edge-Case Fuzzing CAC Sticker vs CACG primary slab URL routing
[2026-08-25 17:15:39] 00:11 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (setUpAll)
[2026-08-25 17:15:39] 00:11 +238: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark 5,000-row collection generation check
[2026-08-25 17:15:39] 00:11 +239: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Year completes in < 30ms
[2026-08-25 17:15:39] GÅ¦n+Å 5,000-row Year sort time: 8.181 ms
[2026-08-25 17:15:39] 00:11 +240: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Condition (Sheldon Scale) completes in < 30ms
[2026-08-25 17:15:39] GÅ¦n+Å 5,000-row Condition sort time: 5.932 ms
[2026-08-25 17:15:39] 00:11 +241: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark Benchmark: Sorting 5,000 coins by Cert # completes in < 30ms
[2026-08-25 17:15:40] GÅ¦n+Å 5,000-row Cert # sort time: 4.459 ms
[2026-08-25 17:15:40] 00:11 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 3: 5,000-Row Collection Table Sorting Scale Benchmark (tearDownAll)
[2026-08-25 17:15:40] 00:11 +242: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Rapid nextStep concurrency check (100 calls)
[2026-08-25 17:15:40] 00:11 +243: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/sprint_1_stress_test.dart: Sprint 1 Stress Test Suite 4: Wizard Service State Machine & Concurrency Reset and re-start guest tour
[2026-08-25 17:15:40] 00:12 +244: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Estate / Liquidation Mode satisfies exact mathematical parity
[2026-08-25 17:15:40] 00:12 +245: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Retail Mode satisfies exact mathematical parity
[2026-08-25 17:15:40] 00:12 +246: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Collection Stats Schema Contract matches required fields
[2026-08-25 17:15:40] 00:12 +247: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/valuation_mode_test.dart: Valuation Mode Parity & Basis Calculations Unauthenticated path guard blocks query with unknown in path
[2026-08-25 17:15:40] 00:13 +248: C:/Users/ericd/Documents/MyVertexProject/numista_mobile/test/widget_test.dart: App smoke test placeholder
[2026-08-25 17:15:40] 00:14 +249: All tests passed!
[2026-08-25 17:15:40] flutter test: PASS
[2026-08-25 17:15:40] === LAYER 1: UX Visual Guard ===
[2026-08-25 17:20:16] Gùç injected env (2) from ..\numista_tests\.env // tip: Gîÿ enable debugging { debug: true }
[2026-08-25 17:20:16] Gùç injected env (0) from ..\numista_tests\.env // tip: Gùê encrypted .env [www.dotenvx.com]
[2026-08-25 17:20:16] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ override existing { override: true }
[2026-08-25 17:20:16] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ custom filepath { path: '/custom/path/.env' }
[2026-08-25 17:20:16] 
[2026-08-25 17:20:16] Running 10 tests using 1 worker
[2026-08-25 17:20:16] 
[2026-08-25 17:20:16] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ suppress logs { quiet: true }
[2026-08-25 17:20:16] WARNING: All log messages before absl::InitializeLog() is called are written to STDERR
[2026-08-25 17:20:16] E0000 00:00:1787692551.211822   19816 alts_credentials.cc:93] ALTS creds ignored. Not running on GCP and untrusted ALTS is not enabled.
[2026-08-25 17:20:16] [coin_title_guard] coin_data_audit.py output:
[2026-08-25 17:20:16] [coin_data_audit] No canonical_title_field in manifest n++ quad-check active (['title', 'theme_subject', 'series', 'program_series'])
[2026-08-25 17:20:16] [coin_data_audit] Auditing coins...
[2026-08-25 17:20:16]   [TITLE_OK] qc_fixture_estate_coin: non-empty fields=['title', 'series']
[2026-08-25 17:20:16]   [TITLE_OK] qc_fixture_foreign_coin: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 17:20:16]   [TITLE_OK] qc_fixture_title_ok_dollar: non-empty fields=['title', 'series']
[2026-08-25 17:20:16]   [TITLE_OK] qc_fixture_title_ok_quarter: non-empty fields=['title', 'theme_subject', 'series', 'program_series']
[2026-08-25 17:20:16] [coin_data_audit] Auditing estate boundary...
[2026-08-25 17:20:16] 
[2026-08-25 17:20:16] [coin_data_audit] RESULTS: 5 PASS / 0 WARN / 0 UNEXPECTED FAIL (1 expected sentinel)
[2026-08-25 17:20:16]   PASS  [FIXTURE_SENTINEL_OK]: Intentionally-broken fixture correctly triggered COIN_TITLE_FAIL.
[2026-08-25 17:20:16]   PASS  [COINS_AUDITED]: 5 coin documents checked. 1 title failures.
[2026-08-25 17:20:16]   PASS  [ESTATE_CURRENCY_SEPARATED]: 1 currency docs confirmed separate from coins.
[2026-08-25 17:20:16]   PASS  [ESTATE_WORLD_SEPARATED]: 1 world_items docs confirmed separate from coins.
[2026-08-25 17:20:16]   PASS  [FOREIGN_COINS_IN_COINS]: 1 foreign coin(s) correctly in users/{uid}/coins.
[2026-08-25 17:20:17]   EXPECTED FAIL  [COIN_TITLE_FAIL] qc_fixture_title_FAIL_empty: All title fields empty: ['title', 'theme_subject', 'series', 'program_series']. Flutter _buildTitle() will degrade to year+mint only.
[2026-08-25 17:20:17] 
[2026-08-25 17:20:17]   ok  1 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:21:3 GÇ¦ Coin Title Guard GÇ¦ Primary: Firestore field check - no coin should have all title fields empty (7.9s)
[2026-08-25 17:20:17] [coin_title_guard] SEMANTICS_UNAVAILABLE: accessibility tree returned no nodes. Primary assertion is authoritative.
[2026-08-25 17:20:17]   -   2 [chromium] GÇ¦ layer_1_ux_visual\coin_title_guard.spec.js:75:3 GÇ¦ Coin Title Guard GÇ¦ Secondary: Flutter accessibility snapshot (conditional - non-authoritative)
[2026-08-25 17:20:17] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîÿ multiple files { path: ['.env.local', '.env'] }
[2026-08-25 17:20:17] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 17:20:17] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 17:20:17] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 17:20:17] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 17:20:17] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 17:20:17]   ok  3 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:176:3 GÇ¦ Contrast Guard - Light Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Light mode on key UI regions (26.6s)
[2026-08-25 17:20:17] [contrast_guard] Sampling path: screenshot (CanvasKit/WebGL compatible)
[2026-08-25 17:20:17] [Sidebar Navigation] fg={"r":255,"g":255,"b":255} bg={"r":14,"g":17,"b":23} ratio=18.90
[2026-08-25 17:20:17] [Sidebar Coins] fg={"r":157,"g":158,"b":161} bg={"r":14,"g":17,"b":23} ratio=7.05
[2026-08-25 17:20:17] [Ask Morgan Header] fg={"r":240,"g":253,"b":244} bg={"r":11,"g":17,"b":32} ratio=17.99
[2026-08-25 17:20:17] [Top Programs Card] fg={"r":255,"g":255,"b":255} bg={"r":49,"g":51,"b":63} ratio=12.53
[2026-08-25 17:20:17]   ok  4 [chromium] GÇ¦ layer_1_ux_visual\contrast_guard.spec.js:207:3 GÇ¦ Contrast Guard - Dark Mode GÇ¦ WCAG AA contrast >= 4.5:1 in Dark mode on key UI regions (31.4s)
[2026-08-25 17:20:17] Gùç injected env (0) from ..\numista_tests\.env // tip: Gîü auth for agents [www.vestauth.com]
[2026-08-25 17:20:17]   ok  5 [chromium] GÇ¦ layer_1_ux_visual\layout_guard.spec.js:63:3 GÇ¦ Layout Guard - 1920x1080 Desktop GÇ¦ flt-glass-pane fills the viewport (25.6s)
[2026-08-25 17:20:17]   ok  9 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:78:3 GÇ¦ Theme Switch Guard GÇ¦ App remains visible after theme toggle with 500ms settle (45.3s)
[2026-08-25 17:20:17] [theme_switch_guard] Canvas not readable - skipping center pixel check.
[2026-08-25 17:20:17]   -  10 [chromium] GÇ¦ layer_1_ux_visual\theme_switch_guard.spec.js:144:3 GÇ¦ Theme Switch Guard GÇ¦ Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle
[2026-08-25 17:20:17] 
[2026-08-25 17:20:18]   2 skipped
[2026-08-25 17:20:18]   8 passed (4.5m)
[2026-08-25 17:20:18] 
[2026-08-25 17:20:18] To open last HTML report run:
[2026-08-25 17:20:18] [36m[39m
[2026-08-25 17:20:18] [36m  npx playwright show-report playwright-report[39m
[2026-08-25 17:20:18] [36m[39m
[2026-08-25 17:20:18] LAYER 1: PASS
[2026-08-25 17:20:18] numista_qc block appended to SCAN_REPORT.md
[2026-08-25 17:20:18] SUITE_RESULT: PASS
