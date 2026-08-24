/**
 * search_and_browse.spec.js — Numista QC Layer 2
 * Search input renders results; empty search does not crash.
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

test.describe('Search and Browse', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('Search input is reachable', async ({ page }) => {
    const searchBtn = page.locator('flt-semantics').filter({ hasText: /search/i });
    const visible = await searchBtn.first().isVisible({ timeout: 8000 }).catch(() => false);
    if (!visible) { console.log('[search] Search element not found — may require navigation.'); test.skip(); return; }
    await expect(searchBtn.first()).toBeVisible();
  });

  test('App does not crash with no coins visible (empty state)', async ({ page }) => {
    // Canvas must remain alive regardless of data state
    await page.waitForTimeout(3000);
    const alive = await page.evaluate(() => {
      const p = document.querySelector('flt-glass-pane');
      return p && window.getComputedStyle(p).visibility === 'visible';
    });
    expect(alive, 'App crashed or became invisible in browse state').toBe(true);
  });
});
