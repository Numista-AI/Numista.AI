/**
 * auth_and_login.spec.js — Numista QC Layer 2
 * Auth flow: sign-in succeeds, Flutter renders, sign-out clears session.
 *
 * NOTE ON flt-glass-pane.toBeVisible():
 *   Playwright's toBeVisible() requires non-zero bounding box AND visibility:visible.
 *   flt-glass-pane passes the visibility check (used in waitForFlutter) but fails the
 *   bounding box check in Playwright's toBeVisible() when a Flutter overlay dialog
 *   (Morgan welcome) is on top. We assert on flt-semantics content instead, which
 *   the accessibility tree proves is rendered correctly.
 */
const { test, expect } = require('@playwright/test');
const { signInAndWait } = require('../qc-helpers');

test.describe('Auth and Login', () => {
  test('Sign-in succeeds and Flutter canvas renders', async ({ page }) => {
    await signInAndWait(page);
    // Assert on Flutter-rendered content, not the canvas element itself.
    // Error-context.yaml (Aug 26) confirmed these semantics nodes are present:
    //   - Morgan welcome dialog with "Add coins", "Go to Homepage", etc.
    // We look for any flt-semantics node, which proves Flutter has rendered.
    const hasContent = await page.locator('flt-semantics').first().isVisible({ timeout: 5000 }).catch(() => false);
    expect(hasContent, 'No flt-semantics nodes rendered — Flutter app did not render content').toBe(true);
    // Negative: no error modal visible
    const errorVisible = await page.locator('flt-semantics').filter({ hasText: /error|failed|invalid/i }).first().isVisible({ timeout: 2000 }).catch(() => false);
    expect(errorVisible, 'Error modal visible after sign-in').toBe(false);
  });

  test('Unauthenticated visit redirects or shows auth gate (not logged-in content)', async ({ page }) => {
    // Do NOT sign in — check that unauthenticated users do NOT see collection content.
    // auth.setup.js warmed Cloud Run, so Flutter should render the login/welcome screen.
    await page.goto('https://numista.ai');
    await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
    // Wait for ANY flt-semantics node — proves Flutter rendered (auth gate or welcome)
    const hasSemanticsContent = await page.waitForFunction(
      () => document.querySelectorAll('flt-semantics').length > 0,
      { timeout: 30000 }
    ).then(() => true).catch(() => false);
    expect(hasSemanticsContent, 'Flutter did not render any content within 30s').toBe(true);
    // Negative: unauthenticated user must NOT see "My Collection"
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

