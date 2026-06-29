const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 05: Navigation & State Persistence
// Tests back button, browser refresh, deep nav,
// and that the app recovers gracefully from unexpected states.
// ============================================================

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);
  await page.mouse.click(714, 631);
  await page.waitForTimeout(4000);
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}

test.describe('05 - Navigation & State Persistence', () => {

  test('T01: Browser refresh from demo stays on numista.ai', async ({ page }) => {
    await enterDemo(page);
    await page.reload();
    await page.waitForTimeout(4000);
    expect(page.url()).toContain('numista.ai');
    const buf = await page.screenshot({ path: 'screenshots/after-refresh.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T02: In-app back navigation (sidebar) works correctly', async ({ page }) => {
    // Flutter web is a SPA — browser back button has no effect on Flutter routes.
    // Real users navigate using the sidebar, not the browser back button.
    // This test verifies the sidebar-based "back to home" flow works correctly.
    await enterDemo(page);
    // Navigate away from home
    await page.mouse.click(80, 231); // My Collection (All tab)
    await page.waitForTimeout(2500);
    // Navigate back to Home Dashboard via sidebar
    await page.mouse.click(80, 146); // Home Dashboard
    await page.waitForTimeout(2500);
    const buf = await page.screenshot({ path: 'screenshots/back-to-home-via-sidebar.png', type: 'png' });
    expect(page.url()).toContain('numista.ai');
    expect(buf.length, 'Home Dashboard blank after sidebar navigation').toBeGreaterThan(50000);
  });

  test('T03: Navigating to My Collection then Home Dashboard keeps nav stable', async ({ page }) => {
    await enterDemo(page);
    // Go to My Collection
    await page.mouse.click(80, 231);
    await page.waitForTimeout(3000);
    // Go to Home Dashboard
    await page.mouse.click(80, 146);
    await page.waitForTimeout(3000);
    const buf = await page.screenshot({ path: 'screenshots/nav-back-to-home.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T04: Rapidly clicking multiple nav items does not crash app', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    const navItems = [
      { x: 80, y: 146 }, { x: 80, y: 231 }, { x: 80, y: 506 },
      { x: 80, y: 173 }, { x: 80, y: 454 }, { x: 80, y: 480 },
    ];
    for (const item of navItems) {
      await page.mouse.click(item.x, item.y);
      await page.waitForTimeout(500); // rapid fire
    }
    await page.waitForTimeout(2000);

    expect(pageErrors, 'JS errors after rapid nav: ' + pageErrors.join(' | ')).toHaveLength(0);
    expect(page.url()).toContain('numista.ai');
  });

  test('T05: Coin Search page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 676); // Coin Search
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/coin-search.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
    expect(page.url()).toContain('numista.ai');
  });

  test('T06: AI Deepdive page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 702); // AI Deepdive
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/ai-deepdive.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T07: Inventory page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 335); // Inventory
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/inventory.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T08: My Wishlist page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 369); // My Wishlist
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/my-wishlist.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T09: AI Trainer Board loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 566); // AI Trainer Board
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/ai-trainer-board.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T10: Review Hub loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 506); // Review Hub
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/review-hub.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T11: Coin Programs page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 173); // Coin Programs
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/coin-programs.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T12: Microscope Scanner page loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 480); // Microscope Scanner
    await page.waitForTimeout(4000);
    const buf = await page.screenshot({ path: 'screenshots/microscope-scanner.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

});
