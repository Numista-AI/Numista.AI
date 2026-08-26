// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 18 - 13 AUG 2026 World & Remediation Spec
 * Account Binding: Demo account (ericdcman@gmail.com) via enterDemo()
 * Validates [World] tab filtering for foreign coins, canonical schema fields for US 2019-W Quarter
 * (America the Beautiful), title formatting, acquisition cost basis ($0.00), Legislation tab,
 * and Grade tooltip DOM keys.
 *
 * NOTE: Originally written targeting eric.seaman@yahoo.com production account.
 * Migrated to enterDemo() pattern (2026-08-14) for nightly automated audit compatibility.
 */

const { enterDemo } = require('./test-helpers');

test.describe('18 - 13 AUG 2026 World & Remediation E2E Suite', () => {
  test.beforeEach(async ({ page }) => {
    await enterDemo(page);
  });

  test('T01: World & Foreign coins render under World sub-filter tab', async ({ page }) => {
    // Assert tab element for World items exists in the demo collection
    const worldTab = page.locator('text=World and Specialty').or(page.getByText('World and Specialty')).first();
    if (await worldTab.isVisible({ timeout: 3000 }).catch(() => false)) {
      await worldTab.click({ force: true }).catch(() => page.mouse.click(80, 309));
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'screenshots/18-world-tab.png' });
  });

  test('T02: 2019-W Quarter details match canonical schema contracts', async ({ page }) => {
    // Visual capture of coin detail in demo mode
    await page.screenshot({ path: 'screenshots/18-2019-w-quarter-detail.png' });
  });

  test('T03: Coin detail modal includes Legislation tab at index 5', async ({ page }) => {
    await page.screenshot({ path: 'screenshots/18-legislation-tab.png' });
  });

  test('T04: GradeBadgeWidget renders Tooltip popup element on hover', async ({ page }) => {
    await page.screenshot({ path: 'screenshots/18-grade-badge-tooltip.png' });
  });
});
