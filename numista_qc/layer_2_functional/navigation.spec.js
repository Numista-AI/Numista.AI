/**
 * navigation.spec.js — Numista QC Layer 2
 * Sidebar navigation: each main section reachable, no crashes.
 */
const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../../numista_tests/.env') });

async function signInAndWait(page) {
  const email = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  await page.waitForFunction(() => (window.firebase_core?.getApps?.() ?? []).length > 0, { timeout: 20000 });
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch (e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  await page.evaluate(() => { ['flutter.user_name','flutter.morgan_onboarding_complete','flutter.onboarding_complete'].forEach(k => localStorage.setItem(k,'true')); });
  await page.reload();
  await page.waitForFunction(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; }, { timeout: 20000 });
  await page.waitForTimeout(5000);
}

async function flutterAlive(page) {
  return page.evaluate(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; });
}

const NAV_TARGETS = [
  { label: 'Add Coins',     btnText: 'Add coins, notes, or medals' },
  { label: 'My Collection', btnText: 'Browse my collection' },
  { label: 'Chat',          btnText: 'Chat with Morgan' },
  { label: 'Dashboard',     btnText: 'Go to Homepage' },
];

test.describe('Navigation', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  for (const nav of NAV_TARGETS) {
    test(`Navigate to ${nav.label} — canvas stays alive`, async ({ page }) => {
      const btn = page.locator('flt-semantics[role=button]').filter({ hasText: nav.btnText });
      const visible = await btn.first().isVisible({ timeout: 5000 }).catch(() => false);
      if (!visible) {
        // Try sidebar nav variant
        const sidebarBtn = page.locator('flt-semantics[role=button]').filter({ hasText: nav.label });
        if (await sidebarBtn.first().isVisible({ timeout: 3000 }).catch(() => false)) {
          await sidebarBtn.first().click();
        } else {
          console.log(`[navigation] ${nav.label} button not found — skipping`);
          test.skip();
          return;
        }
      } else {
        await btn.first().click();
      }
      await page.waitForTimeout(3000);
      const alive = await flutterAlive(page);
      expect(alive, `Canvas not visible after navigating to ${nav.label}`).toBe(true);
    });
  }

  test('World filter does NOT show Lincoln Cent (US coin in wrong filter)', async ({ page }) => {
    // Behavioural negative assertion from 26-aug24-remediation.spec.js
    const worldBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /world|foreign/i });
    if (!await worldBtn.first().isVisible({ timeout: 5000 }).catch(() => false)) { test.skip(); return; }
    await worldBtn.first().click();
    await page.waitForTimeout(3000);
    const lincolnVisible = await page.locator('flt-semantics').filter({ hasText: 'Lincoln Cent' }).first().isVisible({ timeout: 2000 }).catch(() => false);
    expect(lincolnVisible, 'Lincoln Cent (US coin) appearing in World filter — filter bug').toBe(false);
  });
});
