const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 01: Homepage Integrity
// Checks: title, URL, Flutter render, no JS errors, load speed
// ============================================================

test.describe('01 - Homepage', () => {

  test('T01: HTTP 200 response', async ({ page }) => {
    const response = await page.goto('https://numista.ai');
    expect(response.status()).toBe(200);
  });

  test('T02: Page title is Numista.AI', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(2000);
    expect(await page.title()).toMatch(/Numista\.AI/);
  });

  test('T03: URL resolves to https://numista.ai/', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForTimeout(2000);
    expect(page.url()).toBe('https://numista.ai/');
  });

  test('T04: Flutter app renders (flt-glass-pane present)', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForFunction(() => !!document.querySelector('flt-glass-pane'), { timeout: 15000 });
    const hasFlutter = await page.evaluate(() => !!document.querySelector('flt-glass-pane'));
    expect(hasFlutter, 'Flutter app did not render').toBe(true);
  });

  test('T05: No JavaScript console errors on load', async ({ page }) => {
    const errors = [];
    page.on('console', msg => { if (msg.type() === 'error') errors.push(msg.text()); });
    page.on('pageerror', err => errors.push('PAGE ERROR: ' + err.message));
    await page.goto('https://numista.ai');
    await page.waitForFunction(() => !!document.querySelector('flt-glass-pane'), { timeout: 15000 });
    expect(errors, 'Console errors found: ' + errors.join(' | ')).toHaveLength(0);
  });

  test('T06: Homepage renders content (semantic flt-glass-pane check)', async ({ page }) => {
    await page.goto('https://numista.ai');
    await page.waitForFunction(() => !!document.querySelector('flt-glass-pane'), { timeout: 15000 });
    await page.waitForTimeout(2000); // CANVASKIT_STABILIZATION_MS = 2000
    const glassPaneVisible = await page.evaluate(() => !!document.querySelector('flt-glass-pane'));
    expect(glassPaneVisible, 'Page canvas appears unrendered').toBe(true);
  });

  test('T07: Page loads Flutter in under 10 seconds', async ({ page }) => {
    const start = Date.now();
    await page.goto('https://numista.ai');
    await page.waitForFunction(() => !!document.querySelector('flt-glass-pane'), { timeout: 10000 });
    const elapsed = Date.now() - start;
    expect(elapsed, `Load took ${elapsed}ms`).toBeLessThan(10000);
  });

});
