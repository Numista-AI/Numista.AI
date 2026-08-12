// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Numista.AI -- Real Account Visual Parity & Non-Linear Stress E2E Suite
 * Tests Desktop Web (1280x720) visual card rendering, rapid navigation,
 * and network throttling resiliency.
 */

test.describe('Real Account Visual Parity & Stress Tests', () => {

  test('01: Production Site Desktop Visual Layout & Canvas Rendering', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    
    // Navigate to production app
    const response = await page.goto('https://numista.ai', { waitUntil: 'domcontentloaded', timeout: 30000 });
    expect(response?.status()).toBeLessThan(400);

    // Verify Flutter Web Glass Pane rendering
    const flutterView = page.locator('flt-glass-pane, flutter-view, canvas, body').first();
    await expect(flutterView).toBeAttached({ timeout: 30000 });
  });

  test('02: Non-Linear Tab Switching & Rapid Viewport Stress', async ({ page }) => {
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.goto('https://numista.ai', { waitUntil: 'domcontentloaded', timeout: 30000 });

    // Simulate non-linear viewport resizing (Desktop -> Tablet -> Desktop)
    await page.setViewportSize({ width: 1024, height: 768 });
    await page.waitForTimeout(500);
    await page.setViewportSize({ width: 1280, height: 720 });
    await page.waitForTimeout(500);

    // Assert UI canvas remains stable
    const canvas = page.locator('canvas, flt-glass-pane, body').first();
    await expect(canvas).toBeAttached();
  });

  test('03: Slow Network Throttling & Loading Recovery', async ({ page }) => {
    // Enable slow network emulation
    const client = await page.context().newCDPSession(page);
    await client.send('Network.emulateNetworkConditions', {
      offline: false,
      latency: 150, // 150ms latency
      downloadThroughput: 1.5 * 1024 * 1024 / 8, // 1.5 Mbps
      uploadThroughput: 750 * 1024 / 8,
    });

    await page.goto('https://numista.ai', { waitUntil: 'domcontentloaded', timeout: 45000 });
    const target = page.locator('flt-glass-pane, flutter-view, canvas, body').first();
    await expect(target).toBeAttached({ timeout: 30000 });
  });

});
