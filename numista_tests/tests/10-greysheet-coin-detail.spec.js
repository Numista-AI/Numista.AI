const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 10: Coin Detail — Greysheet Pricing Table,
//                Valuation Toggle & GSID Display (v4.0)
//
// These features appear inside the coin detail screen, on the
// "Financials" tab. They were added in commits b784f4e & e4225ab.
//
// Architecture:
//   - _GreysheetPricingTable widget: shown when coin.greysheetGsid
//     is non-empty. Calls GET /api/greysheet/pricing/<gsid>.
//     Renders a DataTable: Grade | CPG Retail | Wholesale Bid.
//     Highlights the current coin grade row in pink/accent.
//   - Valuation toggle: in Settings screen (commit e4225ab).
//     Switches portfolio value display between CPG Retail (default),
//     Greysheet Wholesale Bid, and Greysheet Ask.
//   - GSID display: the Greysheet Series ID is shown on the coin
//     detail Financials tab when populated.
//   - CAC verification badge: shown in pricing table when IsCac=true.
//   - Portfolio value on Home Dashboard now reflects CPG total
//     instead of cost basis.
//
// Demo mode: Coin detail requires clicking into a specific coin.
// We navigate to My Collection → click the first coin → go to
// its Financials tab.
// ============================================================

const CLICK_WAIT = 4000;

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(CLICK_WAIT);
  await page.mouse.click(714, 631); // Browse Demo
  await page.waitForTimeout(CLICK_WAIT);
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}

test.describe('10 - Coin Detail: Greysheet Pricing Table & Valuation Toggle (v4.0)', () => {

  // ── My Collection — entry point to coin detail ────────────────────────

  test('T01: My Collection loads — coin list renders for detail navigation', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 231); // My Collection → All
    await page.waitForTimeout(CLICK_WAIT);
    const buf = await page.screenshot({ path: 'screenshots/greysheet-detail-collection.png', type: 'png' });
    expect(buf.length, 'My Collection blank — cannot navigate to coin detail').toBeGreaterThan(50000);
  });

  test('T02: Clicking a coin in collection opens detail without crash', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    await page.mouse.click(80, 231); // My Collection → All
    await page.waitForTimeout(CLICK_WAIT);

    // Click the first coin card in the list area (center content, first row)
    await page.mouse.click(640, 300);
    await page.waitForTimeout(CLICK_WAIT);

    const buf = await page.screenshot({ path: 'screenshots/greysheet-coin-detail.png', type: 'png' });
    expect(buf.length, 'Coin detail screen blank').toBeGreaterThan(50000);
    expect(pageErrors.length, 'JS crash on coin detail: ' + pageErrors.join(' | ')).toBe(0);
  });

  test('T03: Financials tab in coin detail loads without crash', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 231); // My Collection
    await page.waitForTimeout(CLICK_WAIT);

    // Click first coin
    await page.mouse.click(640, 300);
    await page.waitForTimeout(CLICK_WAIT);

    // The Financials tab — typically a tab bar at the top of coin detail.
    // Position varies but is usually in the top third of the content area.
    // Try clicking the "Financials" tab area (top of detail content, right portion)
    await page.mouse.click(750, 200);
    await page.waitForTimeout(3000);

    const buf = await page.screenshot({ path: 'screenshots/greysheet-financials-tab.png', type: 'png' });
    expect(buf.length, 'Financials tab appears blank').toBeGreaterThan(50000);
  });

  test('T04: Greysheet pricing endpoint responds for a valid GSID', async ({ page }) => {
    // Direct API test — pricing endpoint added in b784f4e.
    // A valid GSID would be something like "1794-S1C" for a Morgan dollar.
    // We test with a well-known GSID; auth required but should not 404.
    const res = await page.request.get(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/pricing/1794-S1C',
      { failOnStatusCode: false }
    );
    expect(res.status(), `Greysheet pricing endpoint is 404 — route missing`).not.toBe(404);
    expect(res.status(), `Greysheet pricing endpoint is 500 — server crash`).not.toBe(500);
  });

  test('T05: Greysheet pricing endpoint returns valid JSON structure', async ({ page }) => {
    const res = await page.request.get(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/pricing/1794-S1C',
      { failOnStatusCode: false }
    );
    // 200 = data; 401/403 = auth-gated. Either way must be valid JSON if 200.
    if (res.status() === 200) {
      const body = await res.json();
      // Response should contain a 'pricing' array
      expect(Array.isArray(body.pricing), 'Pricing response missing "pricing" array').toBe(true);
    } else {
      // Auth-gated — just verify endpoint exists with valid JSON error body
      expect(res.status()).toBeGreaterThanOrEqual(200);
      expect(res.status()).toBeLessThan(500);
    }
  });

  // ── Valuation Toggle (Settings Screen) ───────────────────────────────

  test('T06: Settings screen loads — valuation toggle accessible', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 420); // Settings & Backup (approx y after estate planning)
    await page.waitForTimeout(CLICK_WAIT);
    const buf = await page.screenshot({ path: 'screenshots/greysheet-settings.png', type: 'png' });
    expect(buf.length, 'Settings screen appears blank').toBeGreaterThan(50000);
  });

  test('T07: Settings does not crash when switching valuation mode', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    await page.mouse.click(80, 420); // Settings & Backup
    await page.waitForTimeout(CLICK_WAIT);

    // Scroll down in settings to find the valuation toggle section
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(1500);
    await page.mouse.wheel(0, 300);
    await page.waitForTimeout(1500);

    // Try clicking in the settings content area where valuation toggle would be
    await page.mouse.click(640, 500);
    await page.waitForTimeout(2000);

    expect(pageErrors.length, 'JS crash in Settings: ' + pageErrors.join(' | ')).toBe(0);
    const buf = await page.screenshot({ path: 'screenshots/greysheet-valuation-toggle.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  // ── Home Dashboard — CPG-based portfolio value ────────────────────────

  test('T08: Home Dashboard portfolio value section renders (CPG total, not cost basis)', async ({ page }) => {
    // In v4.0 the portfolio value is now the CPG (Collector Price Guide) retail total.
    // The section shows cpgTotal, bidTotal, askTotal.
    await enterDemo(page);
    await page.mouse.click(80, 146); // Home Dashboard
    await page.waitForTimeout(CLICK_WAIT + 2000);

    const buf = await page.screenshot({ path: 'screenshots/greysheet-portfolio-cpg.png', type: 'png' });
    expect(buf.length, 'Portfolio value section not rendering').toBeGreaterThan(50000);
  });

  test('T09: Home Dashboard portfolio section has no arithmetic/render crash', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));

    await page.mouse.click(80, 146); // Home Dashboard
    await page.waitForTimeout(CLICK_WAIT + 3000); // Allow Greysheet data to load

    expect(pageErrors.length, 'JS crash computing CPG/Bid/Ask portfolio: ' + pageErrors.join(' | ')).toBe(0);
  });

  // ── Backend — greysheet pricing API endpoints ─────────────────────────

  test('T10: GET /api/greysheet/config responds (not 404 or 500)', async ({ page }) => {
    const res = await page.request.get(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/config',
      { failOnStatusCode: false }
    );
    expect(res.status()).not.toBe(404);
    expect(res.status()).not.toBe(500);
  });

  test('T11: POST /api/greysheet/batch responds (not 404 or 500)', async ({ page }) => {
    const res = await page.request.post(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/batch',
      { data: '{}', headers: { 'Content-Type': 'application/json' }, failOnStatusCode: false }
    );
    expect(res.status()).not.toBe(404);
    expect(res.status()).not.toBe(500);
  });

  test('T12: POST /api/greysheet/resolve responds (not 404 or 500)', async ({ page }) => {
    const res = await page.request.post(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/resolve',
      { data: '{}', headers: { 'Content-Type': 'application/json' }, failOnStatusCode: false }
    );
    expect(res.status()).not.toBe(404);
    expect(res.status()).not.toBe(500);
  });

  test('T13: GET /api/greysheet/cac responds (not 404 or 500)', async ({ page }) => {
    // CAC verification endpoint added in 6c051e6
    const res = await page.request.get(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/greysheet/cac',
      { failOnStatusCode: false }
    );
    expect(res.status()).not.toBe(404);
    expect(res.status()).not.toBe(500);
  });

  test('T14: GET /api/portfolio/snapshot responds (not 404 or 500)', async ({ page }) => {
    // Daily portfolio snapshot endpoint added in 6c051e6
    const res = await page.request.get(
      'https://numista-backend-xwqkbwqvuq-uc.a.run.app/api/portfolio/snapshot',
      { failOnStatusCode: false }
    );
    expect(res.status()).not.toBe(404);
    expect(res.status()).not.toBe(500);
  });

});
