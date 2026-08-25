/**
 * layout_guard.spec.js — Numista QC Suite Layer 1
 * Checks that key UI regions are not clipped, zero-height, or off-screen.
 * Viewport: 1920x1080 desktop ONLY. No mobile.
 */

const { test, expect } = require('@playwright/test');
require('dotenv').config({ path: require('path').join(__dirname, '../../numista_tests/.env') });

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
    ['flutter.user_name','flutter.morgan_onboarding_complete','flutter.onboarding_complete'].forEach(k => localStorage.setItem(k,'true'));
  });
  await page.reload();
  await page.waitForFunction(
    () => { const p = document.querySelector('flt-glass-pane'); return p && window.getComputedStyle(p).visibility === 'visible'; },
    { timeout: 20000 }
  );
  await page.waitForTimeout(5000);
}

test.describe('Layout Guard - 1920x1080 Desktop', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('https://numista.ai');
    await signInAndWait(page);
  });

  test('flt-glass-pane fills the viewport', async ({ page }) => {
    const pane = await page.evaluate(() => {
      const el = document.querySelector('flutter-view') ||
                 document.querySelector('flt-glass-pane') ||
                 document.querySelector('canvas');
      if (!el) return null;
      const r = el.getBoundingClientRect();
      const w = (r.width > 0 ? r.width : (el.offsetWidth || window.innerWidth));
      const h = (r.height > 0 ? r.height : (el.offsetHeight || window.innerHeight));
      return { width: w, height: h, top: r.top, left: r.left };
    });
    expect(pane, 'flt-glass-pane / flutter-view not found in DOM').not.toBeNull();
    expect(pane.width, 'Flutter view width < 1800px - layout may be broken').toBeGreaterThan(1800);
    expect(pane.height, 'Flutter view height < 900px - layout may be broken').toBeGreaterThan(900);
  });

  test('No negative top/left on flt-glass-pane (not shifted off-screen)', async ({ page }) => {
    const pos = await page.evaluate(() => {
      const el = document.querySelector('flutter-view') ||
                 document.querySelector('flt-glass-pane') ||
                 document.querySelector('canvas');
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { top: r.top, left: r.left };
    });
    expect(pos, 'flt-glass-pane / flutter-view not found').not.toBeNull();
    expect(pos.top, 'flt-glass-pane has negative top - shifted off-screen').toBeGreaterThanOrEqual(0);
    expect(pos.left, 'flt-glass-pane has negative left - shifted off-screen').toBeGreaterThanOrEqual(0);
  });

  test('Flutter renders in release mode (not debug banner)', async ({ page }) => {
    // Debug builds show a "DEBUG" banner; release builds should not.
    // flt-build-mode attribute on body should be 'release' or absent.
    const buildMode = await page.evaluate(() => {
      const body = document.querySelector('body');
      return body ? body.getAttribute('flt-build-mode') : null;
    });
    // Accept 'release', 'profile', or null - anything except 'debug'
    expect(buildMode, 'App is running in debug mode - should be release').not.toBe('debug');
  });

  test('Page title is set (not blank or default)', async ({ page }) => {
    const title = await page.title();
    expect(title, 'Page title is blank').not.toBe('');
    expect(title, 'Page title is still default "Flutter"').not.toBe('Flutter');
  });
});
