// auth.probe9.js -- find onboarding button text in flt-semantics
const { chromium } = require('@playwright/test');
require('dotenv').config();

const PREVIEW_URL = 'https://numista-vault--phase3c-semantics-chfyhjip.web.app';

(async () => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();

  await page.goto(PREVIEW_URL);
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
  await page.waitForTimeout(5000);

  // Dump all flt-semantics inner text content to find the button label
  const texts = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('flt-semantics'))
      .map(n => ({
        role: n.getAttribute('role'),
        label: n.getAttribute('aria-label'),
        text: n.textContent?.trim()?.slice(0, 60),
      }))
      .filter(n => n.role || n.label || n.text);
  });
  console.log('flt-semantics nodes:', JSON.stringify(texts, null, 2));

  // Try specific button locators
  const candidates = [
    "text=That's me!",
    "text=That's me",
    "text=Skip",
    "text=eric",
    "[role=button]",
    "flt-semantics[role=button]",
  ];
  for (const sel of candidates) {
    try {
      const count = await page.locator(sel).count();
      console.log(`\n${sel}: count=${count}`);
      if (count > 0) {
        const txt = await page.locator(sel).first().textContent().catch(() => null);
        const vis = await page.locator(sel).first().isVisible().catch(() => false);
        console.log(`  visible=${vis}, text="${txt}"`);
      }
    } catch(e) {
      console.log(`${sel}: ERROR ${e.message}`);
    }
  }

  await page.screenshot({ path: 'auth.probe9.png' });
  await browser.close();
  console.log('\nDone. Screenshot: auth.probe9.png');
})();
