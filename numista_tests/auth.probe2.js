// auth.probe2.js — deeper probe of the actual firebase_auth global
const { chromium } = require('@playwright/test');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage();
  await page.goto('https://numista.ai');
  await page.waitForTimeout(6000);

  const result = await page.evaluate(() => {
    const auth = window.firebase_auth;
    if (!auth) return { found: false };
    return {
      found: true,
      type: typeof auth,
      keys: Object.keys(auth),
      hasSignIn: typeof auth.signInWithEmailAndPassword === 'function',
      hasGetAuth: typeof auth.getAuth === 'function',
      hasInitialize: typeof auth.initializeAuth === 'function',
    };
  });
  console.log('firebase_auth probe:', JSON.stringify(result, null, 2));

  // Also check firebase_core
  const coreResult = await page.evaluate(() => {
    const core = window.firebase_core;
    if (!core) return { found: false };
    return {
      found: true,
      keys: Object.keys(core).slice(0, 20),
      hasGetApps: typeof core.getApps === 'function',
      hasGetApp: typeof core.getApp === 'function',
    };
  });
  console.log('firebase_core probe:', JSON.stringify(coreResult, null, 2));

  // Check what login UI is available
  const domResult = await page.evaluate(() => {
    return {
      emailInputs: document.querySelectorAll('input[type=email]').length,
      passwordInputs: document.querySelectorAll('input[type=password]').length,
      textInputs: document.querySelectorAll('input[type=text]').length,
      allInputs: document.querySelectorAll('input').length,
      fltPaneHidden: document.querySelector('flt-glass-pane')?.style?.visibility,
    };
  });
  console.log('DOM probe:', JSON.stringify(domResult, null, 2));

  fs.writeFileSync('auth.probe2.json', JSON.stringify({ result, coreResult, domResult }, null, 2));
  await browser.close();
})();
