// auth.probe10.js -- try to click onboarding dialog buttons via various methods
const { chromium } = require('@playwright/test');
require('dotenv').config();

const PREVIEW_URL = 'https://numista-vault--phase3c-semantics-chfyhjip.web.app';

(async () => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const browser = await chromium.launch({ headless: true });
  // Fresh context -- no stored data, so dialog should appear
  const context = await browser.newContext();
  const page = await context.newPage();

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

  await page.screenshot({ path: 'probe10-before.png' });
  console.log('Screenshot saved: probe10-before.png');

  // Dump ALL flt-semantics nodes with role and text
  const allNodes = await page.evaluate(() => {
    return Array.from(document.querySelectorAll('flt-semantics')).map(n => ({
      role: n.getAttribute('role'),
      enabled: n.getAttribute('aria-disabled'),
      label: n.getAttribute('aria-label'),
      text: n.textContent?.trim()?.slice(0, 80),
      rect: n.getBoundingClientRect ? 
        { x: Math.round(n.getBoundingClientRect().x), y: Math.round(n.getBoundingClientRect().y),
          w: Math.round(n.getBoundingClientRect().width), h: Math.round(n.getBoundingClientRect().height) } : null,
    }));
  });
  console.log('\n=== ALL flt-semantics nodes:');
  allNodes.forEach((n, i) => {
    if (n.text || n.role) console.log(`[${i}] role=${n.role} rect=${JSON.stringify(n.rect)} text="${n.text}"`);
  });

  // Try clicking any flt-semantics node that contains 'Skip' anywhere in text
  const skipNode = allNodes.find(n => n.text && n.text.includes('Skip'));
  if (skipNode) {
    console.log('\nFound Skip node:', skipNode);
    // Click at center of that rect
    const cx = skipNode.rect.x + skipNode.rect.w / 2;
    const cy = skipNode.rect.y + skipNode.rect.h / 2;
    await page.mouse.click(cx, cy);
    console.log(`Clicked at (${cx}, ${cy})`);
    await page.waitForTimeout(1500);
  } else {
    console.log('\nNo Skip node found. Trying coordinate click on dialog area...');
    // Dialog is center of screen. Skip chip is typically bottom-left of chip row
    // Chip row appears to be around y=470 based on screenshots. 'Skip' is rightmost.
    await page.mouse.click(746, 470);
    console.log('Clicked at (746, 470) -- Skip chip position estimate');
    await page.waitForTimeout(1500);
  }

  await page.screenshot({ path: 'probe10-after.png' });
  console.log('Screenshot saved: probe10-after.png');

  await browser.close();
  console.log('\nDone.');
})();
