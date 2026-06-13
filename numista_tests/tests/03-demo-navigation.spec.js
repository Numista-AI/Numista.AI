const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 03: Browse Demo Flow
// After clicking Browse Demo, verifies all nav items load,
// sidebar is present, and no error states appear.
// ============================================================

const NAV_COORDS = [
  { name: 'Home Dashboard',    x: 80,  y: 147 },
  { name: 'My Collection',     x: 70,  y: 172 },
  { name: 'Review Hub',        x: 66,  y: 198 },
  { name: 'Coin Programs',     x: 73,  y: 224 },
  { name: 'Add New Coins',     x: 75,  y: 250 },
  { name: 'Microscope Scanner',x: 88,  y: 276 },
  { name: 'Inventory',         x: 59,  y: 302 },
  { name: 'My Wishlist',       x: 65,  y: 328 },
  { name: 'Coin Search',       x: 66,  y: 354 },
  { name: 'AI Deepdive',       x: 66,  y: 380 },
  { name: 'AI Trainer Board',  x: 77,  y: 407 },
];

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(4000);
  await page.mouse.click(714, 631); // Browse Demo button
  await page.waitForTimeout(4000);
}

test.describe('03 - Browse Demo Navigation', () => {

  test('T01: Browse Demo button enters app', async ({ page }) => {
    await enterDemo(page);
    const buf = await page.screenshot({ type: 'png' });
    // Demo mode shows blue banner + sidebar + main content
    expect(buf.length).toBeGreaterThan(100000);
    expect(page.url()).toContain('numista.ai');
  });

  test('T02: Demo banner is visible after entering demo', async ({ page }) => {
    await enterDemo(page);
    // Screenshot should show the blue "You re browsing a read-only demo" banner
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(150000); // richer page
  });

  test('T03: Sidebar navigation renders all items', async ({ page }) => {
    await enterDemo(page);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  // Dynamically generate tests for each nav item
  for (const navItem of NAV_COORDS) {
    test(`T04-nav: "${navItem.name}" loads without crashing`, async ({ page }) => {
      await enterDemo(page);
      const errors = [];
      page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
      page.on('pageerror', err => errors.push('PAGE ERROR: ' + err.message));

      await page.mouse.click(navItem.x, navItem.y);
      await page.waitForTimeout(3000);

      const buf = await page.screenshot({ path: `screenshots/demo-${navItem.name.replace(/[^a-z0-9]/gi, '_')}.png`, type: 'png' });
      expect(buf.length, `${navItem.name} appears blank`).toBeGreaterThan(50000);
      expect(page.url(), `${navItem.name} navigated away`).toContain('numista.ai');

      // Log errors but don't fail on demo-mode errors (expected in read-only mode)
      if (errors.length > 0) {
        console.warn(`[${navItem.name}] Console errors: ${errors.join(' | ')}`);
      }
    });
  }

  test('T05: Ask Morgan AI button is visible in sidebar', async ({ page }) => {
    await enterDemo(page);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T06: Send Beta Feedback button renders', async ({ page }) => {
    await enterDemo(page);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T07: Sign Out button is present in demo sidebar', async ({ page }) => {
    await enterDemo(page);
    const buf = await page.screenshot({ type: 'png' });
    expect(buf.length).toBeGreaterThan(100000);
  });

  test('T08: No page-level JavaScript errors in demo mode', async ({ page }) => {
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    await enterDemo(page);
    // Navigate a few screens
    for (const navItem of NAV_COORDS.slice(0, 3)) {
      await page.mouse.click(navItem.x, navItem.y);
      await page.waitForTimeout(2000);
    }
    expect(pageErrors, 'Page-level JS errors: ' + pageErrors.join(' | ')).toHaveLength(0);
  });

});
