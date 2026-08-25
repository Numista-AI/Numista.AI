// auth.probe11.js -- dump dashboard nav buttons after Beta modal close
const { chromium } = require('@playwright/test');
require('dotenv').config();

const PREVIEW_URL = 'https://numista-vault--phase3c-semantics-chfyhjip.web.app';
const UID = 'vyFVKI4NkHSqKaqmhaPdDebLOWb2';

(async () => {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
  const page = await context.newPage();

  await page.goto(PREVIEW_URL);
  await page.waitForFunction(() => (window.firebase_core?.getApps?.() ?? []).length > 0, { timeout: 25000 });
  
  await page.evaluate(async ({ em, pw, uid }) => {
    const auth = window.firebase_auth.getAuth();
    await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
    await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
    // Pre-set MorganPrefs to skip onboarding
    localStorage.setItem(`flutter.morgan_${uid}_setup_done`, 'true');
    localStorage.setItem(`flutter.morgan_${uid}_preferred_name`, '"eric"');
  }, { em: process.env.TEST_USER_EMAIL, pw: process.env.TEST_USER_PASSWORD, uid: UID });

  await page.reload();
  await page.waitForFunction(() => {
    const pane = document.querySelector('flt-glass-pane');
    return pane && window.getComputedStyle(pane).visibility === 'visible';
  }, { timeout: 25000 });
  await page.waitForTimeout(5000);

  // Close Beta Tester modal if present (Escape key)
  const betaHeading = page.locator('flt-semantics').filter({ hasText: 'Welcome, Beta Tester' });
  if (await betaHeading.first().isVisible({ timeout: 3000 }).catch(() => false)) {
    console.log('Beta modal detected -- pressing Escape');
    await page.keyboard.press('Escape');
    await page.waitForTimeout(1500);
  }

  await page.screenshot({ path: 'probe11-dashboard.png' });
  console.log('Screenshot: probe11-dashboard.png');

  // Dump all role=button nodes
  const buttons = await page.evaluate(() =>
    Array.from(document.querySelectorAll('flt-semantics[role=button]')).map(n => ({
      text: n.textContent?.trim()?.slice(0, 80),
      rect: { x: Math.round(n.getBoundingClientRect().x), y: Math.round(n.getBoundingClientRect().y),
              w: Math.round(n.getBoundingClientRect().width), h: Math.round(n.getBoundingClientRect().height) },
    }))
  );
  console.log('\n=== role=button nodes on dashboard:');
  buttons.forEach((b, i) => console.log(`[${i}] text="${b.text}" at (${b.rect.x},${b.rect.y})`));

  // Also check text= locator for common nav labels
  const labels = ['Add Coins', 'Add coins', 'Coins', 'My Collection', 'All', 'Home Dashboard', 'Coin Programs'];
  console.log('\n=== text= locator counts:');
  for (const l of labels) {
    const count = await page.locator('text=' + l).count();
    const vis = count > 0 ? await page.locator('text=' + l).first().isVisible().catch(() => false) : false;
    console.log(`  text="${l}": count=${count}, visible=${vis}`);
  }

  await browser.close();
  console.log('\nDone.');
})();
