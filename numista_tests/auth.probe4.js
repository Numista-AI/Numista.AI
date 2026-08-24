// auth.probe4.js — what does flt-glass-pane look like after sign-in + reload?
const { chromium } = require('@playwright/test');
require('dotenv').config();

(async () => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const browser = await chromium.launch({
    headless: true,
    args: ['--use-gl=angle', '--use-angle=swiftshader', '--ignore-gpu-blocklist'],
  });
  const page = await browser.newPage();
  await page.goto('https://numista.ai');

  // Wait for Firebase to init
  await page.waitForFunction(
    () => (window.firebase_core?.getApps?.() ?? []).length > 0,
    { timeout: 20000 }
  );
  console.log('Firebase ready');

  // Sign in
  const r = await page.evaluate(async ({ em, pw }) => {
    const auth = window.firebase_auth.getAuth();
    await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
    await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
    return 'done';
  }, { em: email, pw: password });
  console.log('Sign in:', r);

  // Reload
  await page.reload();
  console.log('Reloaded');

  // Poll for 15 seconds on flt-glass-pane
  for (let i = 0; i < 15; i++) {
    await page.waitForTimeout(1000);
    const state = await page.evaluate(() => {
      const pane = document.querySelector('flt-glass-pane');
      if (!pane) return 'no element';
      const style = window.getComputedStyle(pane);
      return {
        visibility: style.visibility,
        display: style.display,
        width: pane.offsetWidth,
        height: pane.offsetHeight,
        childCount: pane.children.length,
      };
    });
    console.log(`t+${i+1}s:`, JSON.stringify(state));
    if (state.visibility === 'visible') {
      console.log('Canvas is visible!');
      break;
    }
  }

  // Also check current user
  const user = await page.evaluate(() => {
    const auth = window.firebase_auth?.getAuth?.();
    return auth?.currentUser?.email ?? 'no user';
  });
  console.log('currentUser after reload:', user);

  await browser.close();
})();
