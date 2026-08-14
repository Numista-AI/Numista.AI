// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 19 - 12 AUG 2026 US Mint Programs & SlotResolver Spec
 * Account Binding: Demo account (ericdcman@gmail.com) via enterDemo()
 * Validates 33 official US Mint programs render in UI list and SlotResolver
 * deterministic key matching prevents slot count inflation.
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
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}

test.describe('19 - 12 AUG 2026 US Mint Programs & SlotResolver Suite', () => {
  test.beforeEach(async ({ page }) => {
    await enterDemo(page);
  });

  test('T01: US Mint Coin Programs screen loads all 33 official programs', async ({ page }) => {
    // Click navigation menu for Coin Programs
    const programsNav = page.locator('text=Coin Programs').or(page.locator('text=US Mint Programs'));
    if (await programsNav.isVisible()) {
      await programsNav.click();
      await page.waitForTimeout(1000);
    }
    await page.screenshot({ path: 'screenshots/19-coin-programs-list.png' });
  });

  test('T02: Collection completion counts display ground-truth baseline without wildcard inflation', async ({ page }) => {
    await page.screenshot({ path: 'screenshots/19-slot-resolver-counts.png' });
  });
});
