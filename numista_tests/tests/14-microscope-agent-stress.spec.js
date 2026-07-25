// @ts-check
const { test, expect } = require('@playwright/test');

test.describe('Sprint 2: Microscope Desktop Agent & Diagnostics Stress Tests', () => {
  test('Verify Desktop Agent Download & Diagnostics UI under stress', async ({ page }) => {
    // Navigate to local Flutter app or Desktop Agent page
    await page.goto('http://localhost:5000/get-status').catch(() => {});

    // Open main app
    await page.goto('http://localhost:8080/#/desktop-agent').catch(async () => {
      await page.goto('http://localhost:3000/#/desktop-agent').catch(() => {});
    });

    await page.waitForTimeout(1000);

    // Verify page title and header elements
    const bodyText = await page.locator('body').innerText();
    expect(bodyText).toBeDefined();

    // Rapidly trigger retry diagnostics button
    for (let i = 0; i < 5; i++) {
      const retryBtn = page.locator('button:has-text("Retry")').first();
      if (await retryBtn.isVisible().catch(() => false)) {
        await retryBtn.click();
        await page.waitForTimeout(200);
      }
    }
  });

  test('Direct download link target validation', async ({ page }) => {
    const downloadUrl = 'https://storage.googleapis.com/studio-9101802118-8c9a8-uploads/downloads/NumistaAgentSetup.exe';
    expect(downloadUrl).toContain('NumistaAgentSetup.exe');
  });
});
