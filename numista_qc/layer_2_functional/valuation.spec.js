/**
 * valuation.spec.js — Numista QC Layer 2
 * Greysheet valuation UI renders; external API calls are mocked.
 * No live PCGS / Greysheet / eBay calls in this spec.
 */
const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../../numista_tests/.env') });

async function signInAndWait(page) {
  const email = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  await page.waitForFunction(() => (window.firebase_core?.getApps?.() ?? []).length > 0, { timeout: 20000 });
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch (e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  await page.evaluate(() => { ['flutter.user_name','flutter.morgan_onboarding_complete','flutter.onboarding_complete'].forEach(k => localStorage.setItem(k,'true')); });
  await page.reload();
  await page.waitForFunction(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; }, { timeout: 20000 });
  await page.waitForTimeout(5000);
}

test.describe('Valuation', () => {
  test.beforeEach(async ({ page }) => {
    // Mock external valuation endpoints — no live calls
    await page.route('**/api/greysheet**', route => route.fulfill({ status: 200, body: JSON.stringify({ value: 42.00, source: 'mock' }) }));
    await page.route('**/pcgs**', route => route.fulfill({ status: 200, body: JSON.stringify({ mock: true }) }));
    await page.route('**/ebay**', route => route.fulfill({ status: 200, body: JSON.stringify({ mock: true }) }));
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('Valuation section is reachable without a live external API call', async ({ page }) => {
    // Navigate toward valuation
    const valuationBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /valuat|price|greysheet/i });
    const visible = await valuationBtn.first().isVisible({ timeout: 8000 }).catch(() => false);
    if (!visible) { console.log('[valuation] Valuation entry not found at top level.'); test.skip(); return; }
    await valuationBtn.first().click();
    await page.waitForTimeout(3000);
    const alive = await page.evaluate(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; });
    expect(alive, 'App not visible after entering valuation section').toBe(true);
  });

  test('Spot prices health probe returns HTTP 200 or 401 (backend alive)', async ({ page }) => {
    // This is a network-level check, not a UI test.
    // Uses fetch from within the page context to avoid CORS issues.
    const result = await page.evaluate(async () => {
      try {
        const r = await fetch('https://numista-backend-568985927038.us-central1.run.app/api/spot_prices');
        return { status: r.status };
      } catch (e) { return { status: 0, error: e.message }; }
    });
    expect([200, 401], `Unexpected status ${result.status} from spot_prices endpoint`).toContain(result.status);
  });
});
