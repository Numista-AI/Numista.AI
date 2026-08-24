// auth.probe.js — Phase 3C pre-flight
// Run once before writing auth.setup.js to confirm which Firebase global
// is available in the Flutter web app.
//
// Usage: node auth.probe.js
// Output: auth.probe.json in the current directory

const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage();

  console.log('Navigating to https://numista.ai ...');
  await page.goto('https://numista.ai');

  // Wait for Flutter to load and Firebase to initialize
  await page.waitForTimeout(6000);

  const result = await page.evaluate(() => {
    const pane = document.querySelector('flt-glass-pane');
    return {
      hasFirebaseCompat   : typeof window.firebase?.auth === 'function',
      hasFirebaseModular  : typeof window._firebaseAuth !== 'undefined',
      hasFlutterPane      : !!pane,
      flutterPaneVisible  : pane ? (pane.offsetHeight > 0) : false,
      windowKeys          : Object.keys(window).filter(k =>
        k.toLowerCase().includes('firebase') || k.toLowerCase().includes('auth')
      ),
    };
  });

  console.log('\nAuth surface probe results:');
  console.log(JSON.stringify(result, null, 2));

  const outPath = path.join(__dirname, 'auth.probe.json');
  fs.writeFileSync(outPath, JSON.stringify({ timestamp: new Date().toISOString(), ...result }, null, 2));
  console.log(`\nResults saved to: ${outPath}`);

  if (result.hasFirebaseCompat) {
    console.log('\nPath: Firebase compat global (window.firebase.auth()) — auth.setup.js will use Path 1.');
  } else if (result.hasFirebaseModular) {
    console.log('\nPath: Modular auth global (window._firebaseAuth) — auth.setup.js will use Path 2.');
  } else {
    console.log('\nPath: No Firebase global found — auth.setup.js will use DOM fallback (Path 3).');
    console.log('Note: DOM fallback requires HTML login inputs (not canvas-rendered).');
  }

  await browser.close();
})();
