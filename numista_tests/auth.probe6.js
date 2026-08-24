// auth.probe6.js -- check Flutter accessibility tree after pressing Tab
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

  // Sign in
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

  // Press Tab to activate Flutter accessibility
  await page.keyboard.press('Tab');
  await page.waitForTimeout(2000);

  // Check for flt-semantics elements now
  const result1 = await page.evaluate(() => {
    const nodes = document.querySelectorAll('flt-semantics');
    return {
      count: nodes.length,
      first10: Array.from(nodes).slice(0, 10).map(n => ({
        label: n.getAttribute('aria-label'),
        role: n.getAttribute('role'),
        text: n.textContent?.slice(0, 80),
      }))
    };
  });
  console.log('After Tab press:');
  console.log('flt-semantics count:', result1.count);
  result1.first10.forEach(n => console.log(JSON.stringify(n)));

  if (result1.count > 0) {
    // Try to find Add Coins
    const addCoins = await page.evaluate(() => {
      return Array.from(document.querySelectorAll('[aria-label]'))
        .filter(el => el.getAttribute('aria-label')?.toLowerCase().includes('add'))
        .map(el => ({ aria: el.getAttribute('aria-label'), role: el.getAttribute('role') }));
    });
    console.log('\nElements with "add" aria-label:', JSON.stringify(addCoins, null, 2));

    // Check if text locator works now
    const countByText = await page.locator('text=Add Coins').count();
    console.log('\ntext=Add Coins count after Tab:', countByText);

    const countByText2 = await page.locator('text=Add coins').count();
    console.log('text=Add coins count after Tab:', countByText2);
  }

  await browser.close();
})();
