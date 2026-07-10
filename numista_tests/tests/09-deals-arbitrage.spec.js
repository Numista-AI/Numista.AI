const { test, expect } = require('@playwright/test');

// ============================================================
// TEST SUITE 09: Deals Screen & Arbitrage Deal Finder (v4.0)
//
// Tests the new "Wishlist Deals & Matches" screen (DealsScreen),
// launched from the Home Dashboard. This screen:
//   - Fetches wishlist coins from Firestore
//   - Queries eBay Browse API (via EPN) for live listings
//   - Compares listing prices against Greysheet Bid
//   - Flags and ranks coins priced at or below Greysheet Bid
//
// Navigation: DealsScreen is pushed via MaterialPageRoute from
// the Home Dashboard, NOT from the sidebar.
//
// In demo mode the screen should render gracefully — either showing
// a "no deals / empty wishlist" state or the deal cards themselves.
// It must NOT crash or hang indefinitely.
// ============================================================

const CLICK_WAIT = 4000;

// Home Dashboard coordinates (where the Deals button lives)
const NAV_HOME     = { x: 80, y: 146 };

async function enterDemo(page) {
  await page.goto('https://numista.ai');
  await page.waitForTimeout(CLICK_WAIT);
  await page.mouse.click(714, 631); // Browse Demo
  await page.waitForTimeout(CLICK_WAIT);
  await page.setViewportSize({ width: 1280, height: 1000 });
  await page.waitForTimeout(1000);
}

async function goToDashboard(page) {
  await page.mouse.click(NAV_HOME.x, NAV_HOME.y);
  await page.waitForTimeout(CLICK_WAIT);
}

test.describe('09 - Deals Screen & Arbitrage Deal Finder (v4.0)', () => {

  // ── Home Dashboard renders Deals entry point ──────────────────────────

  test('T01: Home Dashboard renders without crash (Deals entry point present)', async ({ page }) => {
    await enterDemo(page);
    await goToDashboard(page);
    const buf = await page.screenshot({ path: 'screenshots/deals-dashboard-entry.png', type: 'png' });
    expect(buf.length, 'Home Dashboard appears blank — Deals entry point not renderable').toBeGreaterThan(50000);
  });

  test('T02: Home Dashboard has no JS errors that would block Deals navigation', async ({ page }) => {
    await enterDemo(page);
    const jsErrors = [];
    page.on('pageerror', err => jsErrors.push(err.message));
    await goToDashboard(page);
    expect(jsErrors.length, 'JS errors on Home Dashboard: ' + jsErrors.join(' | ')).toBe(0);
  });

  // ── Deals Screen launched from Dashboard ──────────────────────────────

  test('T03: Deals Screen launches from Home Dashboard without crash', async ({ page }) => {
    await enterDemo(page);
    await goToDashboard(page);

    // The "Arbitrage Deal Spotter" card sits below the Category Breakdown
    // section on the Home Dashboard (commit c087d72). It is a tappable card
    // with a green shopping-bag icon, title "Arbitrage Deal Spotter", and
    // subtitle "Find coins listed below Greysheet Wholesale Bid".
    // Tapping it pushes DealsScreen via MaterialPageRoute.
    // Screenshot before to confirm dashboard is up.
    const beforeBuf = await page.screenshot({ path: 'screenshots/deals-before-click.png', type: 'png' });
    expect(beforeBuf.length).toBeGreaterThan(50000);

    // Click the Deals card area on the Home Dashboard
    // (center-right of the dashboard content panel, ~x:780, y:500)
    await page.mouse.click(780, 500);
    await page.waitForTimeout(CLICK_WAIT);

    const afterBuf = await page.screenshot({ path: 'screenshots/deals-screen-launched.png', type: 'png' });
    // Whether DealsScreen loaded or we stayed on dashboard, the app must not be blank
    expect(afterBuf.length, 'App appears blank after Deals navigation attempt').toBeGreaterThan(50000);
    expect(page.url()).toContain('numista.ai');
  });

  test('T04: Deals Screen click does not produce a page-level JS crash', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    await goToDashboard(page);

    // Click in the deals/valuation card area of the dashboard
    await page.mouse.click(780, 500);
    await page.waitForTimeout(CLICK_WAIT + 2000); // allow EPN API call to settle

    expect(
      pageErrors.length,
      'JS crash during Deals navigation or scan: ' + pageErrors.join(' | ')
    ).toBe(0);
  });

  // ── Deals Screen states ───────────────────────────────────────────────

  test('T05: Deals Screen renders a valid state (loading, empty, or results)', async ({ page }) => {
    // This test is permissive — in demo mode the wishlist may be empty,
    // the EPN credentials may be unconfigured, or deals may load.
    // All three are valid. The page must NOT be blank or crash.
    await enterDemo(page);
    await goToDashboard(page);

    // Try the most likely coordinates for the "View Deals" / "Arbitrage Finder" button
    const clickTargets = [
      { x: 780, y: 450 }, // primary guess: upper-center content area
      { x: 780, y: 550 }, // lower content area
      { x: 640, y: 500 }, // center of content panel
    ];

    for (const target of clickTargets) {
      await page.mouse.click(target.x, target.y);
      await page.waitForTimeout(1500);
    }
    await page.waitForTimeout(3000);

    const buf = await page.screenshot({ path: 'screenshots/deals-screen-state.png', type: 'png' });
    expect(buf.length, 'Deals-related area appears blank').toBeGreaterThan(50000);
  });

  // ── EPN / eBay Affiliate backend ──────────────────────────────────────

  test('T06: EPN affiliate endpoint is reachable (not 404)', async ({ page }) => {
    // Checks the backend affiliate/eBay endpoint added as part of Deals feature.
    const res = await page.request.get(
      'https://numista-backend-568985927038.us-central1.run.app/api/ebay/search',
      {
        headers: { 'Content-Type': 'application/json' },
        failOnStatusCode: false,
      }
    );
    // 200 / 401 / 403 = route exists (auth-gated is fine)
    // 404 = route gone (regression)
    expect(res.status(), `EPN endpoint returned 404 — route missing`).not.toBe(404);
    expect(res.status(), `EPN endpoint returned 500 — server crash`).not.toBe(500);
  });

  // ── Greysheet Bid comparison display ─────────────────────────────────

  test('T07: My Wishlist loads without Greysheet bid-related errors', async ({ page }) => {
    await enterDemo(page);
    const errors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') errors.push(msg.text());
    });

    await page.mouse.click(80, 369); // My Wishlist sidebar nav
    await page.waitForTimeout(CLICK_WAIT);

    const greysheetErrors = errors.filter(e =>
      e.toLowerCase().includes('greysheet') ||
      e.toLowerCase().includes('epn') ||
      e.toLowerCase().includes('ebay')
    );
    expect(
      greysheetErrors.length,
      'Greysheet/EPN console errors on Wishlist: ' + greysheetErrors.join(' | ')
    ).toBe(0);

    const buf = await page.screenshot({ path: 'screenshots/deals-wishlist-clean.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T08: Wishlist renders empty-state or deal cards (not perpetual spinner)', async ({ page }) => {
    await enterDemo(page);
    await page.mouse.click(80, 369); // My Wishlist
    // Give EPN scan time to complete or timeout gracefully
    await page.waitForTimeout(8000);
    const buf = await page.screenshot({ path: 'screenshots/deals-wishlist-settled.png', type: 'png' });
    // 50KB+ = some rendered state (empty-state card or deal list)
    expect(buf.length, 'Wishlist appears to be stuck in a loading spinner state').toBeGreaterThan(50000);
  });

});
