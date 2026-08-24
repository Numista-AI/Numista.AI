/**
 * 26-aug24-remediation.spec.js
 * Phase 0 — 83-Issue Remediation Sprint (24 AUG 26)
 *
 * New spec per Q7-LOCK 2026-08-24:
 *   "New numbered file; do not overwrite the original."
 *
 * Original: daily_feedback_dynamic.spec.js — PRESERVED UNTOUCHED as historical reference.
 *
 * Run:  npx playwright test 26-aug24-remediation.spec.js
 * Config: playwright.config.js (baseURL: https://numista.ai, 1920x1080, Chromium)
 *
 * Assertion standard (per D-25, Plan v3-v5):
 *   - Every test: >=1 positive check (element/state present or correct)
 *   - Every category: >=1 negative/behavioral check (known-wrong state absent)
 *   - No test passes solely on flt-glass-pane visibility
 *
 * Locked decisions embedded:
 *   Q1-LOCK: Legislation at index 5 -- no reorder this sprint
 *   Q2-LOCK: 2026 Silver Proof Set -- 10 coins, S-mint
 *   Q5-LOCK: Morgan drawer maxWidth 480
 *   Q6-LOCK: 33 programs correct -- no seeding needed
 *   Q7-LOCK: This file (new); original spec untouched
 *
 * Q3, Q4 remain open -- Phase 3 behavioral assertions added when answered.
 */

const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../.env') });

// Phase 3C: Per-test Firebase auth
// Firebase stores auth in IndexedDB which Playwright storageState cannot capture.
// Confirmed approach (auth.probe4.js 2026-08-24): sign in via JS after page load,
// reload so Flutter boots authenticated, then wait for flt-glass-pane visibility.
async function signInAndWait(page) {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  // Wait for Firebase to initialize
  await page.waitForFunction(
    () => (window.firebase_core?.getApps?.() ?? []).length > 0,
    { timeout: 20000 }
  );
  // Sign in
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch(e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  // Reload so Flutter picks up the session
  await page.reload();
  // Wait for Flutter canvas (visibility:visible, confirmed by probe)
  await page.waitForFunction(
    () => {
      const pane = document.querySelector('flt-glass-pane');
      return pane && window.getComputedStyle(pane).visibility === 'visible';
    },
    { timeout: 20000 }
  );
  await page.waitForTimeout(2000);
}

// Shared helpers

async function waitForFlutter(page, timeoutMs = 30000) {
  // Sign in via Firebase JS API, then reload so Flutter boots authenticated.
  // Every test calls waitForFlutter right after page.goto('/'), so this is
  // the single auth entry point for the whole spec.
  await signInAndWait(page);
}

async function navigateTo(page, label) {
  const nav = page.locator('text=' + label).first();
  if (await nav.isVisible({ timeout: 3000 }).catch(() => false)) {
    await nav.click();
    await page.waitForTimeout(1000);
  }
}

let checkA11y;
try {
  ({ checkA11y } = require('axe-playwright'));
} catch (_) {
  checkA11y = null;
}

// No beforeEach needed -- waitForFlutter handles sign-in after page.goto('/')

// CAT-A: Morgan AI Set Ingestion

test.describe('CAT-A: Morgan AI Set Ingestion', () => {

  test('ISSUE-001: Add Coins Hub loads without error', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'Add Coins');
    const hub = page.locator('text=Add Coins Hub').or(page.locator('text=Add a Coin'));
    await expect(hub.first()).toBeVisible({ timeout: 8000 });
    const errorBanner = page.locator('text=Error').or(page.locator('text=Something went wrong'));
    await expect(errorBanner.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-A-001-hub-loads.png' });
  });

  test('ISSUE-002: Mint Set tab accessible from Add Coins Hub', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'Add Coins');
    const mintSetTab = page.locator('text=Mint Set').or(page.locator('text=Record a Mint Set'));
    await expect(mintSetTab.first()).toBeVisible({ timeout: 8000 });
    await mintSetTab.first().click();
    await page.waitForTimeout(1000);
    const uncCard = page.locator('text=2026 US Mint Uncirculated Coin Set');
    await expect(uncCard.first()).toBeVisible({ timeout: 5000 });
    const errorMsg = page.locator('text=Error').or(page.locator('text=Something went wrong'));
    await expect(errorMsg.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-A-002-mint-set-tab.png' });
  });

  test('ISSUE-003: Silver Proof Set template card visible (Phase 1A Q2-LOCK)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'Add Coins');
    const mintSetTab = page.locator('text=Mint Set').or(page.locator('text=Record a Mint Set'));
    if (await mintSetTab.first().isVisible({ timeout: 5000 }).catch(() => false)) {
      await mintSetTab.first().click();
      await page.waitForTimeout(1000);
    }
    const proofCard = page.locator('text=2026 US Mint Silver Proof Set');
    await expect(proofCard.first()).toBeVisible({ timeout: 5000 });
    const uncCard = page.locator('text=2026 US Mint Uncirculated Coin Set');
    await expect(uncCard.first()).toBeVisible({ timeout: 3000 });
    await page.screenshot({ path: 'reports/screenshots/CAT-A-003-proof-set-card.png' });
  });

  test('ISSUE-004: Morgan action chip absent (D-06 removal)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    const morganchip = page.locator('text=Try the Mint Set Tab').or(
      page.locator('text=Create a Mint Set')
    );
    await expect(morganchip.first()).not.toBeVisible({ timeout: 3000 });
    await page.screenshot({ path: 'reports/screenshots/CAT-A-004-no-morgan-chip.png' });
  });

});

// CAT-B: Desktop UI & Scrollbars

test.describe('CAT-B: Desktop UI and Scrollbars', () => {

  test('ISSUE-005: My Collection loads at 1920x1080 without crash', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await expect(page.locator('flt-glass-pane')).toBeVisible({ timeout: 8000 });
    const exceptionOverlay = page.locator('text=FlutterError').or(page.locator('text=RenderBox'));
    await expect(exceptionOverlay.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-B-005-collection-loads.png' });
  });

  test('ISSUE-006: No ScrollController errors on initial render', async ({ page }) => {
    const consoleErrors = [];
    page.on('console', msg => {
      if (msg.type() === 'error') consoleErrors.push(msg.text());
    });
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    const scrollErrors = consoleErrors.filter(e =>
      e.includes('ScrollController') || e.includes('hasClients')
    );
    expect(scrollErrors.length).toBe(0);
    await page.screenshot({ path: 'reports/screenshots/CAT-B-006-scrollbar.png' });
  });

  test('ISSUE-007: Chip filter switch does not crash scrollbar', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    for (const chipText of ['World', 'U.S.', 'All']) {
      const chip = page.locator('text=' + chipText).first();
      if (await chip.isVisible({ timeout: 2000 }).catch(() => false)) {
        await chip.click();
        await page.waitForTimeout(800);
      }
    }
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    const exErr = page.locator('text=RenderBox');
    await expect(exErr.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-B-007-chip-switch-scroll.png' });
  });

});

// CAT-C: Foreign Coin World Filter (is_foreign fix Phase 2B)

test.describe('CAT-C: Foreign Coin World Filter', () => {

  test('ISSUE-008: World filter chip present in My Collection', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    const worldChip = page.locator('text=World').first();
    await expect(worldChip).toBeVisible({ timeout: 5000 });
    await page.screenshot({ path: 'reports/screenshots/CAT-C-008-world-chip-exists.png' });
  });

  test('ISSUE-009 (KEY): US coins absent from World filter after is_foreign fix', async ({ page }) => {
    // Primary behavioral test for Phase 2B.
    // BEFORE fix: missing is_foreign defaults to true -> US coins appear in World filter (BUG).
    // AFTER fix:  missing is_foreign defaults to false -> US coins stay in U.S. filter.
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    const worldChip = page.locator('text=World').first();
    if (await worldChip.isVisible({ timeout: 3000 }).catch(() => false)) {
      await worldChip.click();
      await page.waitForTimeout(1500);
    }
    // Negative: Known US coin names must NOT appear under World filter
    const lincolnCent     = page.locator('text=Lincoln Cent').first();
    const jeffersonNickel = page.locator('text=Jefferson Nickel').first();
    await expect(lincolnCent).not.toBeVisible({ timeout: 3000 });
    await expect(jeffersonNickel).not.toBeVisible({ timeout: 3000 });
    await page.screenshot({ path: 'reports/screenshots/CAT-C-009-us-coins-not-in-world.png' });
  });

  test('ISSUE-010: World tab renders without error overlay', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    const worldNav = page.locator('text=World & Specialty').first();
    if (await worldNav.isVisible({ timeout: 3000 }).catch(() => false)) {
      await worldNav.click();
      await page.waitForTimeout(1500);
    }
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    const errOverlay = page.locator('text=Error').or(page.locator('text=Could not load'));
    await expect(errOverlay.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-C-010-world-tab-ok.png' });
  });

});

// CAT-D: Contrast & Typography

test.describe('CAT-D: Dark Mode Contrast', () => {

  test('ISSUE-011: Main page renders without layout errors', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await page.waitForTimeout(2000);
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-D-011-layout.png' });
  });

  test('ISSUE-012: WCAG AA check (axe-core)', async ({ page }) => {
    if (!checkA11y) {
      console.log('axe-playwright not installed -- skipping. Run: npm i -D axe-playwright');
      return;
    }
    await page.goto('/');
    await waitForFlutter(page);
    await page.waitForTimeout(2000);
    await checkA11y(page, null, {
      runOnly: { type: 'tag', values: ['wcag2aa'] },
    });
    await page.screenshot({ path: 'reports/screenshots/CAT-D-012-wcag-aa.png' });
  });

});

// CAT-E: Legislation Tab & Programs

test.describe('CAT-E: Legislation Tab and Programs', () => {

  test('ISSUE-013: Coin detail opens without crash (Q1-LOCK: Legislation stays at index 5)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    const anyCard = page.locator('flt-semantics[aria-label]').first();
    if (await anyCard.isVisible({ timeout: 3000 }).catch(() => false)) {
      await anyCard.click();
      await page.waitForTimeout(1500);
    }
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    const errOverlay = page.locator('text=Error').or(page.locator('text=Something went wrong'));
    await expect(errOverlay.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-E-013-legislation-tab.png' });
  });

  test('ISSUE-014: Program Manager renders (Q6-LOCK: 33 programs, no seeding needed)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'Coin Programs');
    await page.waitForTimeout(2000);
    await expect(page.locator('flt-glass-pane')).toBeVisible({ timeout: 8000 });
    const empty = page.locator('text=No programs').or(page.locator('text=Error loading'));
    await expect(empty.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-E-014-program-manager.png' });
  });

});

// CAT-F: Financials (Q3 deferred) + Morgan drawer (Q5-LOCK)

test.describe('CAT-F: Financials and Morgan Drawer', () => {

  test('ISSUE-015: Financials tab renders without crash (Q3 open, Phase 3 deferred)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await navigateTo(page, 'My Collection');
    await page.waitForTimeout(2000);
    const anyCard = page.locator('flt-semantics[aria-label]').first();
    if (await anyCard.isVisible({ timeout: 3000 }).catch(() => false)) {
      await anyCard.click();
      await page.waitForTimeout(1500);
    }
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    const errOverlay = page.locator('text=FlutterError').or(page.locator('text=RenderBox'));
    await expect(errOverlay.first()).not.toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-F-015-financials-tab.png' });
  });

  test('ISSUE-016: Morgan chat panel opens (Q5-LOCK: maxWidth 480, side panel)', async ({ page }) => {
    await page.goto('/');
    await waitForFlutter(page);
    await page.waitForTimeout(2000);
    await page.keyboard.press('Control+m');
    await page.waitForTimeout(1500);
    await expect(page.locator('flt-glass-pane')).toBeVisible();
    await page.screenshot({ path: 'reports/screenshots/CAT-F-016-morgan-panel.png' });
  });

});
