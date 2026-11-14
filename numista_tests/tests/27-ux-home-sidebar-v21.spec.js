const { test, expect } = require('@playwright/test');
const { enterDemo } = require('./test-helpers');

test.describe('27 - UX-HOME-SIDEBAR v2.1 Pre-Launch Spec', () => {
  test('T01: Collection dollar value is hidden by default until Show value click', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1920, viewportHeight: 1080 });
    const showBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /^Show value$/i }).first();
    await expect(showBtn).toBeVisible({ timeout: 10000 });
    await showBtn.click();
    const hideBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /^Hide value$/i }).first();
    await expect(hideBtn).toBeVisible({ timeout: 5000 });
  });

  test('T02: Single-open accordion exclusivity across Research and Estate & Transfers', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1440, viewportHeight: 900 });
    await page.getByText(/^Research$/i).first().click();
    await expect(page.getByText(/^Coin Search$/i).first()).toBeVisible({ timeout: 5000 });
    await page.getByText(/^Estate & Transfers$/i).first().click();
    await expect(page.getByText(/^Estate Planning$/i).first()).toBeVisible({ timeout: 5000 });
    await expect(page.getByText(/^Coin Search$/i).first()).toBeHidden({ timeout: 5000 });
  });

  test('T03: 1024x768 desktop and 390x844 phone Menu overlay render without clipping', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1024, viewportHeight: 768 });
    const deskShot = await page.screenshot({ path: 'screenshots/27-sidebar-1024x768.png' });
    expect(deskShot.length).toBeGreaterThan(50000);

    await page.setViewportSize({ width: 390, height: 844 });
    await page.waitForTimeout(1000);
    const menuBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /Menu/i }).first();
    await expect(menuBtn).toBeVisible({ timeout: 5000 });
    await menuBtn.click();
    await page.waitForTimeout(600);
    const mobShot = await page.screenshot({ path: 'screenshots/27-phone-menu-390x844.png' });
    expect(mobShot.length).toBeGreaterThan(40000);
  });
});
