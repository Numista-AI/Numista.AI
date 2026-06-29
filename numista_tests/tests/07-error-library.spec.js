const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 07: Error Library Verification
// Checks:
//   1. Authenticates a test session (via Enter Demo / Browse Demo).
//   2. Navigates to Numismatic Academy > Error Library.
//   3. Asserts "Missing or insufficient permissions" is not visible.
//   4. Asserts the coin error library content loads successfully.
// ============================================================

const CLICK_WAIT = 4000;

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);
  await page.mouse.click(714, 631); // Browse Demo button (authenticates a test user session)
  await page.waitForTimeout(4000);
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}

test.describe('07 - Error Library Screen Verification', () => {

  test('T01: Error Library loads reference data without permission errors', async ({ page }) => {
    // 1. Enter demo (logs in as demo user satisfying authenticated check)
    await enterDemo(page);

    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      }
    });
    page.on('pageerror', err => {
      errors.push('PAGE ERROR: ' + err.message);
    });

    // 2. Navigate to Error Library (x: 80, y: 624)
    await page.mouse.click(80, 624);
    await page.waitForTimeout(CLICK_WAIT);

    // 3. Take a verification screenshot
    const buf = await page.screenshot({ path: 'screenshots/error-library-verify.png', type: 'png' });

    // Assert that the page rendered properly and is not blank
    expect(buf.length, 'Error Library appears blank or crashed').toBeGreaterThan(50000);

    // 4. Assert absence of permission-denied messages
    // Flutter Web overlays standard text in the DOM or draws it. We check both Console errors and DOM text.
    const hasPermissionDeniedText = await page.evaluate(() => {
      const bodyText = document.body.innerText || '';
      return bodyText.includes('insufficient permissions') || 
             bodyText.includes('permission-denied') ||
             bodyText.includes('Error loading library:');
    });
    expect(hasPermissionDeniedText, 'Found permission denied error text on screen').toBe(false);

    // Ensure no new Firestore permission errors were thrown in the console
    const hasConsolePermissionErrors = errors.some(e => e.includes('permission-denied') || e.includes('insufficient permissions'));
    expect(hasConsolePermissionErrors, 'Found permission denied console errors: ' + errors.join(' | ')).toBe(false);
  });

});
