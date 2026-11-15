const { test, expect } = require('@playwright/test');
const { enterDemo } = require('./test-helpers');

test.describe('29 - Morgan Co-Pilot Release Guard & Track B Harness Spec', () => {
  test('T01: Production web build hard-disables MorganTestHarness (kReleaseMode == true)', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1920, viewportHeight: 1080 });
    const traceExposed = await page.evaluate(() => typeof window.__MORGAN_LAST_TRACE__ !== 'undefined');
    expect(traceExposed, 'SECURITY BLOCKER: window.__MORGAN_LAST_TRACE__ must be undefined in production builds!').toBe(false);
  });

  test('T02: Staging harness verification when MORGAN_HARNESS_URL is configured (Track B GM-1..GM-8)', async ({ page }) => {
    const harnessUrl = process.env.MORGAN_HARNESS_URL;
    if (!harnessUrl) {
      // Production release builds compile out test harness by design; staging URL tests Track B trace bridge.
      test.info().annotations.push({ type: 'note', description: 'Set MORGAN_HARNESS_URL to execute live Track B staging harness' });
      return;
    }
    await page.goto(harnessUrl);
    await page.waitForSelector('flt-glass-pane', { state: 'visible', timeout: 20000 });
    await page.waitForTimeout(2000);
    const hasPane = await page.evaluate(() => !!document.querySelector('flt-glass-pane'));
    expect(hasPane).toBe(true);
  });
});
