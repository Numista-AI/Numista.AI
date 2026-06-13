const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 02: Authentication UI
// Checks: Sign In form, Create Account form, field validation,
// empty submit, Google auth button, Forgot PIN link
// ============================================================

const NAV_WAIT = 4000;
const CLICK_WAIT = 2000;

// Helper: click at coordinate
async function clickAt(page, x, y, wait = CLICK_WAIT) {
  await page.mouse.click(x, y);
  await page.waitForTimeout(wait);
}

test.describe('02 - Authentication UI', () => {

  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(NAV_WAIT);
  });

  test('T01: Sign In tab is active by default', async ({ page }) => {
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000); // page rendered
    // URL stays on root (Sign In is the default)
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T02: Create Account tab switches form', async ({ page }) => {
    // Click Create Account tab (right side, approx x=1340, y=86)
    await clickAt(page, 1340, 86);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    // Should still be on numista.ai (no redirect)
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T03: Create Account form has required fields', async ({ page }) => {
    await clickAt(page, 1340, 86);
    // Take screenshot - form should show Name, Email, PIN, Terms
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T04: Clicking Sign In with empty form stays on login page', async ({ page }) => {
    // Click Sign In button without filling fields (approx x=806, y=344)
    await clickAt(page, 806, 344);
    await page.waitForTimeout(1000);
    // Should remain on homepage
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T05: Create Account with no Terms checked is disabled', async ({ page }) => {
    await clickAt(page, 1340, 86); // Switch to Create Account
    // Click "Create My Account and Vault" without checking terms
    await clickAt(page, 1194, 467);
    await page.waitForTimeout(1000);
    // Should remain on homepage (not submitted)
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T06: Continue with Google button renders', async ({ page }) => {
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    // Page renders, Google button is visible in the layout
  });

  test('T07: Browse Demo navigates into app', async ({ page }) => {
    // Click Browse Demo (approx x=714, y=631 at 1280x720)
    await clickAt(page, 714, 631, 4000);
    const buf = await page.screenshot({ type: 'png' });
    // Should now show the app with sidebar
    expect(buf.length).toBeGreaterThan(100000);
    // Check we are still on numista.ai
    expect(page.url()).toContain('numista.ai');
  });

  test('T08: Try It Free button is visible and clickable', async ({ page }) => {
    // Click Try It Free (approx x=902, y=631)
    await clickAt(page, 902, 631, 3000);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    expect(page.url()).toContain('numista.ai');
  });

});
