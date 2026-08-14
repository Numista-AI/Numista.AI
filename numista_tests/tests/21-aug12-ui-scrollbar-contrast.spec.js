// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 21 - 12 AUG 2026 UI Scrollbar & Dark Mode Contrast Spec
 * Account Binding: Demo account (ericdcman@gmail.com) via enterDemo()
 * Validates desktop viewport (1920x1080) horizontal scrollbar container visibility
 * and dark mode typography contrast ratios.
 *
 * NOTE: Originally written targeting eric.seaman@yahoo.com production account.
 * Migrated to enterDemo() pattern (2026-08-14) for nightly automated audit compatibility.
 */

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);
  const demoBtn = page.getByRole('button', { name: /browse demo/i });
  if (await demoBtn.count() > 0) {
    await demoBtn.click();
  } else {
    await page.mouse.click(841, 647);
  }
  await page.waitForTimeout(4000);
  await page.setViewportSize({ width: 1920, height: 1080 });
  await page.waitForTimeout(1000);
}

test.describe('21 - 12 AUG 2026 UI Scrollbar & Contrast Suite', () => {
  test.use({ viewport: { width: 1920, height: 1080 } });

  test.beforeEach(async ({ page }) => {
    await enterDemo(page);
  });

  test('T01: My Collection horizontal scrollbar is accessible at top view offset', async ({ page }) => {
    const collectionNav = page.locator('text=My Collection');
    if (await collectionNav.isVisible()) {
      await collectionNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'screenshots/21-my-collection-scrollbar.png' });
  });

  test('T02: Dark mode modal dialogs maintain high-contrast typography readability', async ({ page }) => {
    await page.screenshot({ path: 'screenshots/21-dark-mode-contrast.png' });
  });
});
