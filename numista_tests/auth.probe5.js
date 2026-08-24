// auth.probe5.js -- check Flutter accessibility tree
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

  // Wait for Firebase to init and sign in
  await page.waitForFunction(() => (window.firebase_core?.getApps?.() ?? []).length > 0, { timeout: 20000 });
  await page.evaluate(async ({ em, pw }) => {
    const auth = window.firebase_auth.getAuth();
    await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
    await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
  }, { em: email, pw: password });
  await page.reload();
  await page.waitForFunction(() => {
    const pane = document.querySelector('flt-glass-pane');
    return pane && window.getComputedStyle(pane).visibility === 'visible';
  }, { timeout: 20000 });
  await page.waitForTimeout(3000);

  // Check for flt-semantics elements and their text content
  const semantics = await page.evaluate(() => {
    const nodes = document.querySelectorAll('flt-semantics');
    return Array.from(nodes).slice(0, 30).map(n => ({
      tag: n.tagName,
      label: n.getAttribute('aria-label'),
      role: n.getAttribute('role'),
      text: n.textContent?.slice(0, 80),
    }));
  });
  console.log('flt-semantics nodes (first 30):');
  semantics.forEach(n => console.log(JSON.stringify(n)));

  // Try to find text with various strategies
  const addCoinsEl = await page.evaluate(() => {
    // Strategy 1: aria-label contains 'Add'
    const byAria = Array.from(document.querySelectorAll('[aria-label]'))
      .filter(el => el.getAttribute('aria-label')?.toLowerCase().includes('add'))
      .map(el => ({ aria: el.getAttribute('aria-label'), tag: el.tagName }));

    // Strategy 2: text content
    const byText = Array.from(document.querySelectorAll('*'))
      .filter(el => el.childElementCount === 0 && el.textContent?.toLowerCase().includes('add coins'))
      .map(el => ({ tag: el.tagName, text: el.textContent?.slice(0, 60) }));

    return { byAria, byText };
  });
  console.log('\nElements with "Add" aria-label:', JSON.stringify(addCoinsEl.byAria, null, 2));
  console.log('\nElements with "add coins" text:', JSON.stringify(addCoinsEl.byText, null, 2));

  await browser.close();
})();
