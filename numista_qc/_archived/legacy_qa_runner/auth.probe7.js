// auth.probe7.js -- verify flt-semantics on preview build with SemanticsBinding
const { chromium } = require('@playwright/test');
require('dotenv').config();

const PREVIEW_URL = 'https://numista-vault--phase3c-semantics-chfyhjip.web.app';

(async () => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  console.log('Navigating to preview:', PREVIEW_URL);
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
  console.log('Signed in. Reloading...');
  await page.reload();
  await page.waitForFunction(() => {
    const pane = document.querySelector('flt-glass-pane');
    return pane && window.getComputedStyle(pane).visibility === 'visible';
  }, { timeout: 25000 });
  await page.waitForTimeout(3000);

  // Count flt-semantics nodes
  const result = await page.evaluate(() => {
    const nodes = document.querySelectorAll('flt-semantics');
    const withLabel = document.querySelectorAll('[aria-label]');
    return {
      semanticsCount: nodes.length,
      ariaLabelCount: withLabel.length,
      first10: Array.from(withLabel).slice(0, 10).map(n => ({
        label: n.getAttribute('aria-label'),
        role: n.getAttribute('role'),
      })),
    };
  });

  console.log('\n=== flt-semantics count:', result.semanticsCount);
  console.log('=== aria-label count:', result.ariaLabelCount);
  console.log('=== First 10 aria-label elements:');
  result.first10.forEach(n => console.log(JSON.stringify(n)));

  // Try text= locator
  const addCoinsCount = await page.locator('text=Add Coins').count();
  const addCoinsLower = await page.locator('text=Add coins').count();
  console.log('\ntext="Add Coins" count:', addCoinsCount);
  console.log('text="Add coins" count:', addCoinsLower);

  await browser.close();
  console.log('\nDone.');
})();
