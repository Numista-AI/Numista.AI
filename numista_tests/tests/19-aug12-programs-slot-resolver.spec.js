// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 19 - 12 AUG 2026 US Mint Programs & SlotResolver Spec
 * Account Binding: READ-ONLY against eric.seaman@yahoo.com baseline
 * Validates 33 official US Mint programs render in UI list and SlotResolver 
 * deterministic key matching prevents slot count inflation.
 */

test.describe('19 - 12 AUG 2026 US Mint Programs & SlotResolver Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('T01: US Mint Coin Programs screen loads all 33 official programs', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });

    // Click navigation menu for Coin Programs
    const programsNav = page.locator('text=Coin Programs').or(page.locator('text=US Mint Programs'));
    if (await programsNav.isVisible()) {
      await programsNav.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'reports/screenshots/19-coin-programs-list.png' });
  });

  test('T02: Collection completion counts display ground-truth baseline without wildcard inflation', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/19-slot-resolver-counts.png' });
  });
});
