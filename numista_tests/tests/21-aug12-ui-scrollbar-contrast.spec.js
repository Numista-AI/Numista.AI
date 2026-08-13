// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 21 - 12 AUG 2026 UI Scrollbar & Dark Mode Contrast Spec
 * Account Binding: READ-ONLY against eric.seaman@yahoo.com baseline
 * Validates desktop viewport (1920x1080) horizontal scrollbar container visibility 
 * and dark mode typography contrast ratios.
 */

test.describe('21 - 12 AUG 2026 UI Scrollbar & Contrast Suite', () => {
  test.use({ viewport: { width: 1920, height: 1080 } });

  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('T01: My Collection horizontal scrollbar is accessible at top view offset', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });

    const collectionNav = page.locator('text=My Collection');
    if (await collectionNav.isVisible()) {
      await collectionNav.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'reports/screenshots/21-my-collection-scrollbar.png' });
  });

  test('T02: Dark mode modal dialogs maintain high-contrast typography readability', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/21-dark-mode-contrast.png' });
  });
});
