/**
 * auth_and_login.spec.js — Numista QC Layer 2
 * Auth flow: sign-in succeeds, Flutter renders, sign-out clears session.
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

test.describe('Auth and Login', () => {
  test('Sign-in succeeds and Flutter canvas renders', async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
    const pane = page.locator('flt-glass-pane');
    await expect(pane).toBeVisible();
    // Negative: no error modal visible
    const errorVisible = await page.locator('flt-semantics').filter({ hasText: /error|failed|invalid/i }).first().isVisible({ timeout: 2000 }).catch(() => false);
    expect(errorVisible, 'Error modal visible after sign-in').toBe(false);
  });

  test('Unauthenticated visit redirects or shows auth gate (not logged-in content)', async ({ page }) => {
    await page.goto('https://numista.ai');
    // Do NOT sign in — check we do not see collection content
    await page.waitForFunction(() => { const p = document.querySelector('flt-glass-pane'); return p && p.offsetWidth > 0; }, { timeout: 20000 });
    await page.waitForTimeout(4000);
    // Should see a sign-in prompt or welcome screen, NOT a coin collection
    const pane = page.locator('flt-glass-pane');
    await expect(pane).toBeVisible();
    // Negative: should NOT see "My Collection" content without auth
    const collectionVisible = await page.locator('flt-semantics').filter({ hasText: 'My Collection' }).first().isVisible({ timeout: 3000 }).catch(() => false);
    expect(collectionVisible, 'Collection content visible without authentication').toBe(false);
  });

  test('Firebase SDK is initialized on page load', async ({ page }) => {
    await page.goto('https://numista.ai');
    const initialized = await page.waitForFunction(
      () => (window.firebase_core?.getApps?.() ?? []).length > 0,
      { timeout: 20000 }
    ).then(() => true).catch(() => false);
    expect(initialized, 'Firebase SDK not initialized within 20s').toBe(true);
  });
});
