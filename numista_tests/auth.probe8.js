// auth.probe8.js -- find the exact localStorage keys for Morgan onboarding suppression
const { chromium } = require('@playwright/test');
require('dotenv').config();

const PREVIEW_URL = 'https://numista-vault--phase3c-semantics-chfyhjip.web.app';

(async () => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('Navigating to preview...');
  await page.goto(PREVIEW_URL);

  // Sign in
  await page.waitForFunction(() => (window.firebase_core?.getApps?.() ?? []).length > 0, { timeout: 25000 });
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch(e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) { console.error('Sign-in failed:', r.error); await browser.close(); return; }

  await page.reload();
  await page.waitForFunction(() => {
    const pane = document.querySelector('flt-glass-pane');
    return pane && window.getComputedStyle(pane).visibility === 'visible';
  }, { timeout: 25000 });
  await page.waitForTimeout(3000);

  // Before dismissing -- dump all flutter.* localStorage keys
  const beforeKeys = await page.evaluate(() => {
    const all = {};
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith('flutter.')) all[k] = localStorage.getItem(k);
    }
    return all;
  });
  console.log('\n=== BEFORE dismissing onboarding:');
  console.log(JSON.stringify(beforeKeys, null, 2));

  // Dismiss onboarding by clicking "That's me!"
  const thatsMeBtn = page.locator('text=That\'s me!').first();
  if (await thatsMeBtn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await thatsMeBtn.click();
    console.log('\nClicked "That\'s me!"');
    await page.waitForTimeout(2000);
  } else {
    console.log('\nOnboarding dialog NOT visible (may already be dismissed)');
  }

  // After dismissing -- dump all flutter.* localStorage keys again
  const afterKeys = await page.evaluate(() => {
    const all = {};
    for (let i = 0; i < localStorage.length; i++) {
      const k = localStorage.key(i);
      if (k && k.startsWith('flutter.')) all[k] = localStorage.getItem(k);
    }
    return all;
  });
  console.log('\n=== AFTER dismissing onboarding:');
  console.log(JSON.stringify(afterKeys, null, 2));

  // Show what changed
  const newKeys = {};
  const changedKeys = {};
  for (const [k, v] of Object.entries(afterKeys)) {
    if (!(k in beforeKeys)) newKeys[k] = v;
    else if (beforeKeys[k] !== v) changedKeys[k] = { before: beforeKeys[k], after: v };
  }
  console.log('\n=== NEW keys after dismiss:');
  console.log(JSON.stringify(newKeys, null, 2));
  console.log('\n=== CHANGED keys after dismiss:');
  console.log(JSON.stringify(changedKeys, null, 2));

  await browser.close();
  console.log('\nDone.');
})();
