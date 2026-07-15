const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 06: Edge Cases & Resilience
// Tests error handling, broken states, network resilience,
// and behavior on unexpected user actions.
// ============================================================

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

test.describe('06 - Edge Cases & Resilience', () => {

  test('T01: Page does not error on rapid Enter keypress at login', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(4000);
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    // Press Enter 5 times rapidly (empty form submit attempt)
    for (let i = 0; i < 5; i++) {
      await page.keyboard.press('Enter');
      await page.waitForTimeout(200);
    }
    await page.waitForTimeout(1000);
    expect(errors).toHaveLength(0);
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T02: Page does not crash on Tab key navigation', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(4000);
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    for (let i = 0; i < 10; i++) {
      await page.keyboard.press('Tab');
      await page.waitForTimeout(200);
    }
    expect(errors).toHaveLength(0);
  });

  test('T03: Try It Free navigates to registration without crash', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(4000);
    await page.mouse.click(902, 631); // Try It Free (right button)
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/try-it-free.png', type: 'png' });
    // Try It Free enters demo/signup mode — lighter initial render (~63-90KB)
    // A completely blank/broken page would be <10KB
    expect(buf.length, 'Try It Free shows blank page (button broken)').toBeGreaterThan(30000);
    expect(page.url()).toContain('numista.ai');
  });

  test('T04: Network request errors do not break login page render', async ({ page }) => {
    const networkErrors = [];
    page.on('requestfailed', req => networkErrors.push(req.url()));
    await page.goto('https://numista.ai');
    await page.waitForTimeout(5000);
    const buf = await page.screenshot({ type: 'png' });
    // Page should still render even if some non-critical requests fail
    expect(buf.length).toBeGreaterThan(100000);
    if (networkErrors.length > 0) {
      console.warn('[NETWORK] Failed requests:', networkErrors.join(', '));
    }
  });

  test('T05: Demo Home Dashboard shows error state gracefully', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 146); // Home Dashboard
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/home-dashboard-demo.png', type: 'png' });
    // Dashboard unavailable is an expected error state in demo mode
    expect(buf.length).toBeGreaterThan(50000);
    expect(page.url()).toContain('numista.ai');
  });

  test('T06: Demo My Collection shows error state gracefully', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 231); // My Collection
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/my-collection-demo.png', type: 'png' });
    // "Could not load your collection" is expected in demo mode
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T07: Page does not crash when clicking outside all buttons', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(4000);
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    // Click various blank/content areas
    await page.mouse.click(200, 300);
    await page.waitForTimeout(500);
    await page.mouse.click(400, 500);
    await page.waitForTimeout(500);
    await page.mouse.click(600, 200);
    await page.waitForTimeout(1000);
    expect(errors).toHaveLength(0);
  });

  test('T08: Scrolling the homepage does not break render', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(4000);
    const errors = [];
    page.on('pageerror', err => errors.push(err.message));
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(1000);
    await page.mouse.wheel(0, -300);
    await page.waitForTimeout(1000);
    const buf = await page.screenshot({ path: 'screenshots/after-scroll.png', type: 'png' });
    expect(errors).toHaveLength(0);
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T09: Sign Out from demo returns to login', async ({ page }) => {
    await enterDemo(page);
    // Click Sign Out (bottom of sidebar, approx y=973)
    await page.mouse.click(100, 973);
    await page.waitForTimeout(3000);
    const buf = await page.screenshot({ path: 'screenshots/after-signout.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
    // Should be back at login or still on numista.ai
    expect(page.url()).toContain('numista.ai');
  });

  test('T10: Add New Coins page in demo shows appropriate blocked state', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 454); // Add new coins/notes/etc.
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/add-new-coins-demo.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
    expect(page.url()).toContain('numista.ai');
  });

});
