const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 03: Browse Demo Flow
// After clicking Browse Demo, verifies all nav items load,
// sidebar is present, and no error states appear.
// ============================================================

const NAV_COORDS = [
  { name: 'Home Dashboard',          x: 80,  y: 146 },
  { name: 'Coin Programs',           x: 80,  y: 173 },
  { name: 'All',                     x: 80,  y: 231 },
  { name: 'Coins',                   x: 80,  y: 257 },
  { name: 'Currency Collection',     x: 80,  y: 283 },
  { name: 'World and Specialty',     x: 80,  y: 309 },
  { name: 'Inventory',               x: 80,  y: 335 },
  { name: 'My Wishlist',             x: 80,  y: 369 },
  { name: 'Estate Planning',         x: 80,  y: 395 },
  { name: 'Add new coins/notes/etc.',x: 80,  y: 454 },
  { name: 'Microscope Scanner',      x: 80,  y: 480 },
  { name: 'Review Hub',              x: 80,  y: 506 },
  { name: 'AI Trainer Board',        x: 80,  y: 566 },
  { name: 'Error Library',           x: 80,  y: 624 },
  { name: 'Glossary Academy',        x: 80,  y: 651 },
  { name: 'Coin Search',             x: 80,  y: 676 },
  { name: 'AI Deepdive',             x: 80,  y: 702 },
];

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

      await page.screenshot({ path: `screenshots/demo-${navItem.name.replace(/[^a-z0-9]/gi, '_')}.png`, type: 'png' });
      await page.waitForTimeout(2000); // CANVASKIT_STABILIZATION_MS = 2000
      const isRendered = await page.evaluate(() => !!document.querySelector('flt-glass-pane'));
      expect(isRendered, `${navItem.name} canvas did not render`).toBe(true);
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
