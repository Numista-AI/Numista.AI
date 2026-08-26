/**
 * test-helpers.js — Shared Playwright helpers for Numista.AI E2E suites
 *
 * WHY THIS EXISTS:
 *   All demo-mode spec files originally copy-pasted their own enterDemo()
 *   function using a hard-coded waitForTimeout(4000). This caused 'flt-glass-pane
 *   hidden' timeouts when Cloud Run cold-starts take 5-8+ seconds (observed
 *   in nightly runs: Suite 18 T01 timeout on Aug 25-26, 83 failures in
 *   daily_feedback_dynamic.spec.js).
 *
 *   This module provides a single robust enterDemo() that waits for the
 *   Flutter canvas to actually be present before returning. All new suites
 *   should use this instead of copy-pasting the 4s bare-sleep pattern.
 *
 * USAGE in a spec file:
 *   const { enterDemo } = require('./test-helpers');
 *   test.beforeEach(async ({ page }) => { await enterDemo(page); });
 */

const DEMO_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';

/**
 * enterDemo — navigate to numista.ai, click Browse Demo, and wait until the
 * Flutter canvas (flt-glass-pane) is visible and ready.
 *
 * Replaces the bare waitForTimeout(4000) pattern that was timing out on
 * cold-start runs. The selector wait is condition-based and exits as soon
 * as Flutter is ready, so it's both faster (warm) and more reliable (cold).
 *
 * @param {import('@playwright/test').Page} page
 * @param {{ timeout?: number, viewportWidth?: number, viewportHeight?: number }} [opts]
 */
async function enterDemo(page, opts = {}) {
  const {
    timeout = 20000,
    viewportWidth = 1920,
    viewportHeight = 1080,
  } = opts;

  await page.setViewportSize({ width: viewportWidth, height: viewportHeight });
  await page.goto(DEMO_URL);

  // Step 1: Wait for the page to have something rendered (not a blank screen)
  await page.waitForLoadState('domcontentloaded');

  // Step 2: Wait for the Browse Demo button (up to 8s) then click it
  //   - Tries role selector first (most reliable when Flutter has rendered text)
  //   - Falls back to coordinate click at the known button position
  const demoBtn = page.getByRole('button', { name: /browse demo/i });
  try {
    await demoBtn.waitFor({ state: 'visible', timeout: 8000 });
    await demoBtn.click();
  } catch {
    // Flutter rendered text as pixels — fall back to coordinate click
    await page.mouse.click(841, 647);
  }

  // Step 3: Wait for the Flutter glass pane to be visible — this is the
  // definitive signal that the Flutter app has fully initialized.
  // On warm runs this resolves in ~1s; on cold-start Cloud Run it may take 8-15s.
  try {
    await page.waitForSelector('flt-glass-pane', {
      state: 'visible',
      timeout,
    });
  } catch {
    // flt-glass-pane not visible within timeout — take a diagnostic screenshot
    // and continue (don't throw, so the individual test can report its own failure)
    await page.screenshot({ path: 'screenshots/enterDemo-timeout-diagnostic.png' }).catch(() => {});
  }
}

module.exports = { enterDemo, DEMO_URL };
