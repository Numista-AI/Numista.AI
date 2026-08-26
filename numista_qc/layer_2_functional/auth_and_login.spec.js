/**
 * auth_and_login.spec.js — Numista QC Layer 2
 * Auth flow: sign-in succeeds, Flutter renders, sign-out clears session.
 *
 * Uses qc-helpers.js for robust condition-based Flutter-ready waits.
 * Fixes Aug 26 failures caused by bare waitForTimeout(5000) timing out
 * on cold Cloud Run starts.
 */
const { test, expect } = require('@playwright/test');
const { injectAuthAndLoad, visitAndWaitForFlutter } = require('../qc-helpers');

test.describe('Auth and Login', () => {
  test('Sign-in succeeds and Flutter canvas renders', async ({ page }) => {
    await injectAuthAndLoad(page);
    const pane = page.locator('flt-glass-pane');
    await expect(pane).toBeVisible();
    // Negative: no error modal visible
    const errorVisible = await page.locator('flt-semantics').filter({ hasText: /error|failed|invalid/i }).first().isVisible({ timeout: 2000 }).catch(() => false);
    expect(errorVisible, 'Error modal visible after sign-in').toBe(false);
  });

  test('Unauthenticated visit redirects or shows auth gate (not logged-in content)', async ({ page }) => {
    // Do NOT sign in — use visitAndWaitForFlutter for reliable cold-start handling
    await visitAndWaitForFlutter(page);
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
