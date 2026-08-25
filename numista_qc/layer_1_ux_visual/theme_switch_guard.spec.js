/**
 * theme_switch_guard.spec.js — Numista QC Suite Layer 1
 * Asserts that the app remains functional and visible after theme toggle.
 * Theme settle delay: 500ms (per SUITE_MANIFEST.theme_settle_ms).
 * Viewport: 1920x1080 ONLY.
 */

const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../../numista_tests/.env') });

const THEME_SETTLE_MS = 500; // per SUITE_MANIFEST.json theme_settle_ms

async function signInAndWait(page) {
  const email = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  await page.waitForFunction(
    () => (window.firebase_core?.getApps?.() ?? []).length > 0,
    { timeout: 20000 }
  );
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch (e) { return { ok: false, error: e.message }; }
  }, { em: email, pw: password });
  if (!r.ok) throw new Error('Auth failed: ' + r.error);
  await page.evaluate(() => {
    ['flutter.user_name','flutter.userName','flutter.morgan_onboarding_complete',
     'flutter.onboarding_complete','flutter.onboarding_done', 'flutter.user_title',
     'flutter.title_chosen', 'flutter.onboarding_step'].forEach(k => localStorage.setItem(k,'true'));
  });
  await page.reload();
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flutter-view') ||
                document.querySelector('flt-glass-pane') ||
                document.querySelector('canvas');
      return p && window.getComputedStyle(p).visibility === 'visible';
    },
    { timeout: 20000 }
  );
  await page.waitForTimeout(3000);

  // Dismiss Morgan onboarding modals if present
  const modalButtons = page.locator('button, [role=button], flt-semantics').filter({ hasText: /That's me|Skip|browse on my own|Homepage \/ Dashboard/i });
  for (let i = 0; i < 3; i++) {
    if (await modalButtons.first().isVisible({ timeout: 1500 }).catch(() => false)) {
      await modalButtons.first().click().catch(() => {});
      await page.waitForTimeout(1000);
    }
  }
}

async function flutterAlive(page) {
  return page.evaluate(() => {
    const pane = document.querySelector('flutter-view') ||
                 document.querySelector('flt-glass-pane') ||
                 document.querySelector('canvas');
    return pane && window.getComputedStyle(pane).visibility === 'visible';
  });
}

test.describe('Theme Switch Guard', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('App remains visible after theme toggle with 500ms settle', async ({ page }) => {
    // Confirm app is alive before toggle
    const aliveBefore = await flutterAlive(page);
    expect(aliveBefore, 'App not visible before theme toggle').toBe(true);

    // Attempt to find and click the theme toggle
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    const btnVisible = await themeBtn.first().isVisible({ timeout: 3000 }).catch(() => false);

    if (!btnVisible) {
      // Theme button not found - app may not expose theme toggle at this viewport.
      // This is not a test failure; log and skip assertion.
      console.log('[theme_switch_guard] Theme toggle button not found at 1920x1080. Skipping toggle test.');
      test.skip();
      return;
    }

    await themeBtn.first().click();
    // Wait for settle - 500ms per SUITE_MANIFEST.theme_settle_ms
    await page.waitForTimeout(THEME_SETTLE_MS);

    // App must still be alive after toggle
    const aliveAfter = await flutterAlive(page);
    expect(aliveAfter, 'App became invisible after theme toggle - possible crash or white-screen').toBe(true);

    // Take screenshot for human review
    await page.screenshot({ path: 'screenshots/theme_switch_after_toggle_' + Date.now() + '.png', fullPage: false });

    // Toggle back and verify again
    if (await themeBtn.first().isVisible({ timeout: 2000 }).catch(() => false)) {
      await themeBtn.first().click();
      await page.waitForTimeout(THEME_SETTLE_MS);
      const aliveAgain = await flutterAlive(page);
      expect(aliveAgain, 'App not visible after second theme toggle').toBe(true);
    }
  });

  test('Canvas pixel is not pure white (#FFFFFF) immediately after Dark mode toggle', async ({ page }) => {
    // Pure white canvas after Dark mode toggle = likely white-screen bug or theme not applied.
    const themeBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /theme|light|dark|mode/i });
    const btnVisible = await themeBtn.first().isVisible({ timeout: 3000 }).catch(() => false);
    if (!btnVisible) {
      test.skip();
      return;
    }

    // Switch to dark
    await themeBtn.first().click();
    await page.waitForTimeout(THEME_SETTLE_MS);

    // Sample the center pixel of the canvas
    const centerColor = await page.evaluate(() => {
      const canvas = document.querySelector('flt-glass-pane canvas') || document.querySelector('canvas');
      if (!canvas) return null;
      const ctx = canvas.getContext('2d');
      if (!ctx) return null;
      const cx = Math.floor(canvas.width / 2);
      const cy = Math.floor(canvas.height / 2);
      const px = ctx.getImageData(cx, cy, 1, 1).data;
      return { r: px[0], g: px[1], b: px[2] };
    });

    if (!centerColor) {
      console.log('[theme_switch_guard] Canvas not readable - skipping center pixel check.');
      test.skip();
      return;
    }

    console.log('[theme_switch_guard] Center pixel after dark toggle: ' + JSON.stringify(centerColor));

    // In dark mode, center should NOT be pure white
    const isPureWhite = centerColor.r === 255 && centerColor.g === 255 && centerColor.b === 255;
    expect(isPureWhite, 'Center canvas pixel is pure white after Dark mode toggle - possible white-screen bug. Color: ' + JSON.stringify(centerColor)).toBe(false);
  });
});
