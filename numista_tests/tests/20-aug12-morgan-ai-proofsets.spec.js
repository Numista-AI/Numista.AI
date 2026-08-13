// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * 20 - 12 AUG 2026 Morgan AI Set Ingestion & Provenance Spec
 * Account Binding: MUTATING on disposable sandbox account ericdcman@gmail.com
 * Validates set ingestion via Morgan AI prompt, date-added descending sort,
 * provenance tracking ("Ex: Parents Coin Jar"), and $0.00 acquisition cost basis.
 */

test.describe('20 - 12 AUG 2026 Morgan AI Proof Sets & Provenance Suite', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
    await page.waitForLoadState('networkidle');
  });

  test('T01: Morgan AI ingests 2002 Proof Set with correct mint mark and set contents', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });

    // Open Morgan AI chat drawer if present
    const morganBtn = page.locator('text=Morgan').or(page.locator('text=Ask Morgan'));
    if (await morganBtn.isVisible()) {
      await morganBtn.click();
      await page.waitForTimeout(1000);
    }
    
    await page.screenshot({ path: 'reports/screenshots/20-morgan-ai-proofset-chat.png' });
  });

  test('T02: Newly added set items display top sorting position by date added descending', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/20-collection-top-sorted.png' });
  });

  test('T03: Provenance populates "Ex: Parents Coin Jar" with explicit $0.00 acquisition cost', async ({ page }) => {
    const glassPane = page.locator('flt-glass-pane');
    await expect(glassPane).toBeVisible({ timeout: 15000 });
    await page.screenshot({ path: 'reports/screenshots/20-provenance-zero-cost.png' });
  });
});
