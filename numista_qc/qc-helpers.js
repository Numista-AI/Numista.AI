/**
 * qc-helpers.js — Shared helpers for Numista QC Suite (all layers)
 *
 * WHY THIS EXISTS:
 *   Layer 2 specs (auth_and_login, collection_crud, navigation, etc.) all
 *   copy-pasted a signInAndWait() function ending with waitForTimeout(5000).
 *   On cold Cloud Run starts, 5s is insufficient — Flutter may still be
 *   initializing. This caused 3 failures in the Aug 26 QC run:
 *     - auth_and_login: "Sign-in succeeds and Flutter canvas renders"
 *     - auth_and_login: "Unauthenticated visit redirects or shows auth gate"
 *     - collection_crud: "Add coin button is reachable and renders a form"
 *
 * USAGE in a QC spec:
 *   const { signInAndWait, waitForFlutter } = require('../qc-helpers');
 */

require('dotenv').config({ path: require('path').join(__dirname, '../numista_tests/.env') });

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';

/**
 * waitForFlutter — waits until flt-glass-pane is visible using a
 * condition-based waitForFunction (not a bare sleep). Exits as soon as
 * Flutter is ready, so it's faster on warm runs and reliable on cold starts.
 *
 * @param {import('@playwright/test').Page} page
 * @param {number} [timeout=25000] — ms to wait before giving up
 */
async function waitForFlutter(page, timeout = 25000) {
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flt-glass-pane');
      return p && window.getComputedStyle(p).visibility === 'visible' && p.offsetWidth > 0;
    },
    { timeout }
  );
}

/**
 * signInAndWait — authenticate with Firebase, set onboarding localStorage flags,
 * reload the page, then wait for Flutter to actually render.
 *
 * Replaces the bare waitForTimeout(5000) pattern that was causing cold-start
 * failures (flt-glass-pane not ready when assertions ran immediately after).
 *
 * @param {import('@playwright/test').Page} page
 * @param {{ email?: string, password?: string, flutterTimeout?: number }} [opts]
 */
async function signInAndWait(page, opts = {}) {
  const email    = opts.email    || process.env.TEST_USER_EMAIL;
  const password = opts.password || process.env.TEST_USER_PASSWORD;
  const flutterTimeout = opts.flutterTimeout || 20000;

  if (!email || !password) {
    throw new Error(
      'TEST_USER_EMAIL or TEST_USER_PASSWORD missing. ' +
      'Check numista_tests/.env or pass opts.email / opts.password.'
    );
  }

  // Step 1: Wait for the page to fully load (Firebase scripts included)
  // networkidle = no network requests for 500ms → Firebase SDKs are loaded
  await page.waitForLoadState('networkidle', { timeout: 30000 });

  // Step 2: Wait for Firebase SDK to initialize (app registered)
  await page.waitForFunction(
    () => (window.firebase_core?.getApps?.() ?? []).length > 0,
    { timeout: 15000 }
  );

  // Step 3: Sign in via Firebase JS SDK in the browser context
  const r = await page.evaluate(async ({ em, pw }) => {
    try {
      const auth = window.firebase_auth.getAuth();
      await window.firebase_auth.setPersistence(auth, window.firebase_auth.browserLocalPersistence);
      await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
      return { ok: true };
    } catch (e) {
      return { ok: false, error: e.message };
    }
  }, { em: email, pw: password });

  if (!r.ok) {
    throw new Error('Firebase auth failed: ' + r.error);
  }

  // Step 3: Set onboarding flags so the app skips wizard dialogs
  await page.evaluate(() => {
    ['flutter.user_name', 'flutter.morgan_onboarding_complete', 'flutter.onboarding_complete']
      .forEach(k => localStorage.setItem(k, 'true'));
  });

  // Step 5: Reload and wait for Flutter canvas — condition-based, not a bare sleep
  await page.reload();
  // Wait for page to re-load after reload before checking Flutter
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  try {
    await waitForFlutter(page, flutterTimeout);
  } catch {
    // Diagnostic screenshot on failure — don't suppress the real error
    await page.screenshot({ path: 'screenshots/signInAndWait-timeout-diagnostic.png' }).catch(() => {});
    throw new Error(
      `Flutter canvas (flt-glass-pane) did not become visible within ${flutterTimeout}ms after sign-in reload. ` +
      'Check screenshots/signInAndWait-timeout-diagnostic.png'
    );
  }
}

/**
 * visitAndWaitForFlutter — navigate to a URL and wait for Flutter to render.
 * For unauthenticated flows where sign-in is not needed.
 *
 * @param {import('@playwright/test').Page} page
 * @param {string} [url] — defaults to BASE_URL
 * @param {number} [timeout=25000]
 */
async function visitAndWaitForFlutter(page, url = BASE_URL, timeout = 25000) {
  await page.goto(url);
  // Wait for flt-glass-pane to be present in DOM (may not yet be 'visible')
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flt-glass-pane');
      return p && p.offsetWidth > 0;
    },
    { timeout }
  );
}

module.exports = { signInAndWait, waitForFlutter, visitAndWaitForFlutter, BASE_URL };
