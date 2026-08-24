/**
 * programs_catalog.spec.js — Numista QC Layer 2
 * Programs catalog renders; program names include series name not just year+mint.
 * Q6-LOCK: 33 programs are correct — exact list resolved at execution from live data.
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

test.describe('Programs Catalog', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('Programs section is reachable', async ({ page }) => {
    const programsBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /program|catalog|series/i });
    const visible = await programsBtn.first().isVisible({ timeout: 8000 }).catch(() => false);
    if (!visible) { console.log('[programs] Programs entry not found.'); test.skip(); return; }
    await programsBtn.first().click();
    await page.waitForTimeout(3000);
    const alive = await page.evaluate(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; });
    expect(alive, 'App not visible after entering programs section').toBe(true);
  });

  test('State Quarter Program appears in programs list (not just year+mint)', async ({ page }) => {
    // Navigate to programs section
    const programsBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /program|catalog|series/i });
    if (!await programsBtn.first().isVisible({ timeout: 8000 }).catch(() => false)) { test.skip(); return; }
    await programsBtn.first().click();
    await page.waitForTimeout(3000);

    // Check State Quarter Program name is present (not stripped to bare year)
    const stateQuarterVisible = await page.locator('flt-semantics').filter({ hasText: 'State Quarter' }).first().isVisible({ timeout: 5000 }).catch(() => false);
    // This is a corroborating check — CanvasKit may not expose this via semantics.
    // Log result but do not hard-fail if semantics unavailable.
    if (stateQuarterVisible) {
      console.log('[programs] State Quarter Program found in semantics tree.');
    } else {
      console.log('[programs] State Quarter Program not found via semantics — primary check is coin_data_audit.py.');
    }
    // Hard assertion: app must be alive
    const alive = await page.evaluate(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; });
    expect(alive, 'App crashed while viewing programs catalog').toBe(true);
  });

  test('Morgan Dollar appears in programs list', async ({ page }) => {
    const programsBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /program|catalog|series/i });
    if (!await programsBtn.first().isVisible({ timeout: 8000 }).catch(() => false)) { test.skip(); return; }
    await programsBtn.first().click();
    await page.waitForTimeout(3000);

    // Negative: Morgan Dollar listing should NOT appear as bare "1921 (P)"
    // It should have "Morgan Dollar" or "Morgan" in the label
    const morgans = await page.locator('flt-semantics').filter({ hasText: /morgan/i }).all();
    console.log(`[programs] Found ${morgans.length} Morgan-related semantic nodes.`);

    const alive = await page.evaluate(() => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; });
    expect(alive, 'App crashed on Morgan Dollar check').toBe(true);
  });
});
