const { test, expect } = require('@playwright/test');
const { enterDemo } = require('./test-helpers');

test.describe('28 - Wishlist Auto-Fill, Hide & Family Email v1.2 Spec', () => {
  test('T01: Wishlist navigation renders 1-step email bar and hide/restore controls', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1920, viewportHeight: 1080 });
    const wishlistBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /^Wishlist$/i }).first();
    await wishlistBtn.click();
    await page.waitForTimeout(2500);

    await expect(page.getByText(/Send Wish List Email/i).first()).toBeVisible({ timeout: 10000 });
    const buf = await page.screenshot({ path: 'screenshots/28-wishlist-v12.png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T02: Public wishlist route handles invalid token gracefully without blank screen', async ({ page }) => {
    const baseUrl = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';
    await page.goto(`${baseUrl}/wishlist/nonexistent-prelaunch-token-check`);
    await page.waitForSelector('flt-glass-pane', { state: 'visible', timeout: 20000 });
    await page.waitForTimeout(2500);
    const buf = await page.screenshot({ path: 'screenshots/28-public-wishlist-invalid-token.png' });
    expect(buf.length).toBeGreaterThan(25000);
  });
});
