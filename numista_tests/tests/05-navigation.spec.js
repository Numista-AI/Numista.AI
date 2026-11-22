const { test, expect } = require('@playwright/test');
const { enterDemo } = require('./test-helpers');

async function clickSemanticTarget(page, pattern) {
  const btn = page.locator('flt-semantics[role=button]').filter({ hasText: pattern }).first();
  if (await btn.isVisible({ timeout: 5000 }).catch(() => false)) {
    await btn.click();
    return true;
  }
  const fallbackText = page.getByText(pattern).first();
  await fallbackText.waitFor({ state: 'visible', timeout: 5000 });
  await fallbackText.click();
  return true;
}

async function openAccordionAndNavigate(page, groupLabel, itemLabel) {
  await clickSemanticTarget(page, new RegExp(`^${groupLabel}$`, 'i'));
  await page.waitForTimeout(400);
  await clickSemanticTarget(page, new RegExp(`^${itemLabel}$`, 'i'));
  await page.waitForTimeout(2500);
}

test.describe('05 - Navigation & State Persistence (UX-HOME-SIDEBAR v2.1)', () => {

  test('T01: Browser refresh from demo stays on numista.ai', async ({ page }) => {
    await enterDemo(page);
    await page.reload();
    await page.waitForSelector('flt-glass-pane', { state: 'visible', timeout: 20000 });
    expect(page.url()).toContain('numista.ai');
    const buf = await page.screenshot({ path: 'screenshots/after-refresh.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T02: Sidebar navigates to My Collection and back to Home', async ({ page }) => {
    await enterDemo(page);
    await clickSemanticTarget(page, /^My Collection$/i);
    await page.waitForTimeout(2000);
    await clickSemanticTarget(page, /^Home$/i);
    await page.waitForTimeout(2000);
    const buf = await page.screenshot({ path: 'screenshots/back-to-home-via-sidebar.png', type: 'png' });
    expect(buf.length).toBeGreaterThan(50000);
  });

  test('T03: Rapidly clicking top-level nav items produces zero JS pageerrors', async ({ page }) => {
    await enterDemo(page);
    const pageErrors = [];
    page.on('pageerror', err => pageErrors.push(err.message));
    for (const label of [/^My Collection$/i, /^Coin Programs$/i, /^Wishlist$/i, /^Review$/i, /^Home$/i]) {
      await clickSemanticTarget(page, label);
      await page.waitForTimeout(500);
    }
    expect(pageErrors, 'JS errors after rapid nav: ' + pageErrors.join(' | ')).toHaveLength(0);
  });

  test('T04: Research accordion routes (Coin Search, AI Deepdive) load cleanly in main pane', async ({ page }) => {
    await enterDemo(page, { viewportWidth: 1440, viewportHeight: 900 });
    const exploreDemo = page.getByRole('button', { name: /explore demo vault|browse demo/i });
    await exploreDemo.waitFor({ state: 'visible', timeout: 5000 }).then(() => exploreDemo.click()).catch(() => {});
    const betaModalBtn = page.getByRole('button', { name: /got it, let's explore/i });
    await betaModalBtn.waitFor({ state: 'visible', timeout: 15000 }).then(() => betaModalBtn.click()).catch(() => {});
    await openAccordionAndNavigate(page, 'Research', 'Coin Search');
    await expect(page.getByRole('heading', { name: /Coin Reference Search/i })).toBeVisible({ timeout: 10000 });
    expect((await page.screenshot({ path: 'screenshots/coin-search.png' })).length).toBeGreaterThan(50000);

    await clickSemanticTarget(page, /^AI Deepdive$/i);
    await expect(
      page.getByRole('textbox', { name: /Type your question/i })
    ).toBeVisible({ timeout: 10000 });
    await expect(
      page.getByRole('img', { name: /AI Deepdive/i })
    ).toBeVisible({ timeout: 10000 });
    // Main pane left Coin Search and opened full-screen AI Deepdive (NOT docked Ask Morgan popout)
    await expect(page.getByRole('heading', { name: /Coin Reference Search/i })).toHaveCount(0);
    await expect(
      page.locator('flt-semantics').filter({ hasText: /Undock Morgan into floating window|Dock Morgan to right side/i })
    ).toHaveCount(0);
    expect((await page.screenshot({ path: 'screenshots/ai-deepdive.png' })).length).toBeGreaterThan(50000);
  });

  test('T05: Add to collection CTA opens hub safely', async ({ page }) => {
    await enterDemo(page);
    await clickSemanticTarget(page, /Add to collection/i);
    await page.waitForTimeout(2500);
    expect((await page.screenshot({ path: 'screenshots/add-coins-hub.png' })).length).toBeGreaterThan(50000);
  });
});
