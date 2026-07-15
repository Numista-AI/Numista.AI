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
  // Use a text selector so layout shifts don't break demo entry.
  // Falls back to coordinate click if the button text isn't in the DOM
  // (Flutter canvas renders text as pixels, not DOM nodes).
  const demoBtn = page.getByRole('button', { name: /browse demo/i });
  if (await demoBtn.count() > 0) {
    await demoBtn.click();
  } else {
    // Fallback: click the visual position of the Browse Demo button.
    // Coordinates are relative to the default 1280x720 viewport.
    await page.mouse.click(841, 647);
  }
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

    // Ensure no Firestore or Firebase errors were thrown in the console (e.g. failed-precondition, permission-denied)
    const criticalErrors = errors.filter(e => 
      e.includes('cloud_firestore') || 
      e.includes('failed-precondition') || 
      e.includes('permission-denied') ||
      e.includes('insufficient permissions') ||
      e.includes('firebase')
    );
    expect(criticalErrors.length, 'Found critical console errors: ' + criticalErrors.join(' | ')).toBe(0);
  });

});
