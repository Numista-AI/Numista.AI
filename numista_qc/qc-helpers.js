/**
 * qc-helpers.js — Shared helpers for Numista QC Suite (all layers)
 *
 * WHY THERE IS NO IndexedDB INJECTION:
 *   numista.ai is a Flutter web app. Firebase SDK globals (window.firebase_auth,
 *   window.firebase_core) are exposed by Dart JS-interop code that runs INSIDE
 *   Flutter AFTER the engine boots. The index.html has NO Firebase <script> tags.
 *   page.addInitScript() fires before Flutter boots, so Firebase is never available
 *   at injection time. IndexedDB injection cannot work here.
 *
 * WHAT WE DO INSTEAD:
 *   - auth.setup.js runs once per suite invocation as a Cloud Run WARMUP step.
 *     It navigates to numista.ai and signs in — this ensures Cloud Run is warm
 *     for all subsequent tests (~3-5s per-test sign-in vs 26-75s cold start).
 *   - Each Layer 2 test calls signInAndWait(page) which does a fresh sign-in per
 *     test. With a warm Cloud Run, this takes ~15-25s total.
 *   - The 120s timeout in playwright.config.js gives comfortable headroom.
 *
 * USAGE in a Layer 2 spec (requires auth):
 *   const { signInAndWait } = require('../qc-helpers');
 *   test.beforeEach(async ({ page }) => { await signInAndWait(page); });
 *
 * USAGE in a Layer 1 spec (no auth):
 *   const { visitAndWaitForFlutter } = require('../qc-helpers');
 */

require('dotenv').config({ path: require('path').join(__dirname, '../numista_tests/.env') });

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';

// ─── Low-level waits ─────────────────────────────────────────────────────────

/**
 * waitForFlutter — waits until Flutter has rendered content into the DOM.
 *
 * IMPORTANT: flt-glass-pane is ALWAYS 0×0 pixels in this headless GPU config
 * (visibility:visible but zero dimensions — confirmed by diagnostic Aug 26).
 * Playwright's toBeVisible() requires non-zero bounding box, so flt-glass-pane
 * is useless as a visibility signal. We wait for flt-semantics nodes instead,
 * which ARE visible and confirm Flutter has rendered interactive content.
 *
 * @param {import('@playwright/test').Page} page
 * @param {number} [timeout=20000]
 */
async function waitForFlutter(page, timeout = 20000) {
  await page.waitForFunction(
    () => document.querySelectorAll('flt-semantics').length > 0,
    { timeout }
  );
}

// ─── Auth (Layer 2) ───────────────────────────────────────────────────────────

/**
 * signInAndWait — navigate, wait for Firebase SDK (exposed by Flutter/Dart),
 * sign in, set onboarding localStorage flags, reload, then wait for Flutter
 * canvas to render.
 *
 * Why per-test sign-in and not IndexedDB injection:
 *   Firebase SDK globals (window.firebase_auth, window.firebase_core) are
 *   exposed by Dart JS-interop AFTER Flutter boots. There are no Firebase
 *   <script> tags in index.html. IndexedDB injection via addInitScript fires
 *   before Dart/Flutter runs and cannot pre-populate auth state.
 *
 * Performance: auth.setup.js in playwright.config.js warms Cloud Run before
 *   these tests run, bringing sign-in time from 26-75s (cold) to ~15-25s (warm).
 *   With the 120s test timeout this is reliable.
 *
 * @param {import('@playwright/test').Page} page
 * @param {{ url?: string, flutterTimeout?: number }} [opts]
 */
async function signInAndWait(page, opts = {}) {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;
  const url      = opts.url           || BASE_URL;
  const flutterTimeout = opts.flutterTimeout || 20000;

  if (!email || !password) {
    throw new Error(
      '[qc-helpers] TEST_USER_EMAIL or TEST_USER_PASSWORD not set.\n' +
      'Check: numista_tests/.env'
    );
  }

  // Step 1: Navigate and wait for full page load (Firebase SDK scripts via Flutter)
  await page.goto(url);
  await page.waitForLoadState('networkidle', { timeout: 30000 });

  // Step 2: Wait for Firebase SDK to be exposed on window by Dart/Flutter
  // NOTE: window.firebase_auth is set by Dart JS-interop, not by HTML script tags.
  // This resolves only after Flutter has fully booted and Dart code has run.
  await page.waitForFunction(
    () =>
      typeof window.firebase_core !== 'undefined' &&
      typeof window.firebase_auth !== 'undefined' &&
      (window.firebase_core.getApps?.() ?? []).length > 0,
    { timeout: 30000 }
  );

  // Step 3: Sign in via Firebase JS SDK
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
    throw new Error('[qc-helpers] Firebase sign-in failed: ' + r.error);
  }

  // Step 4: Set onboarding flags so Flutter skips wizard dialogs
  await page.evaluate(() => {
    [
      'flutter.user_name',
      'flutter.morgan_onboarding_complete',
      'flutter.onboarding_complete',
      'flutter.beta_tester_welcome_seen_v2',
    ].forEach(k => localStorage.setItem(k, 'true'));
  });

  // Step 5: Reload so Flutter boots with the authenticated session, then wait
  await page.reload();
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  try {
    await waitForFlutter(page, flutterTimeout);
  } catch {
    await page.screenshot({ path: 'screenshots/signInAndWait-timeout.png' }).catch(() => {});
    throw new Error(
      `[qc-helpers] Flutter canvas not visible within ${flutterTimeout}ms after sign-in reload.\n` +
      'Check screenshots/signInAndWait-timeout.png'
    );
  }
}

// ─── Unauthenticated navigation (Layer 1, unauthenticated flows) ─────────────

/**
 * visitAndWaitForFlutter — navigate to URL and wait for Flutter canvas.
 * No sign-in. For Layer 1 UX tests and unauthenticated flow checks.
 *
 * @param {import('@playwright/test').Page} page
 * @param {string} [url]
 * @param {number} [timeout=20000]
 */
async function visitAndWaitForFlutter(page, url = BASE_URL, timeout = 20000) {
  await page.goto(url);
  await page.waitForLoadState('networkidle', { timeout: 30000 }).catch(() => {});
  // Wait for Flutter canvas to exist and render
  // NOTE: On unauthenticated load, flt-glass-pane may remain 'hidden' until Flutter
  // decides which route to show. Use offsetWidth check (less strict than visibility).
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flt-glass-pane');
      return p && p.offsetWidth > 0;
    },
    { timeout }
  );
}

// ─── Deprecated injection stub (for any old call sites) ──────────────────────
async function injectAuthAndLoad(page, opts) {
  console.warn('[qc-helpers] injectAuthAndLoad() → falling back to signInAndWait(). See qc-helpers.js for why injection cannot work.');
  await signInAndWait(page, opts);
}

module.exports = { signInAndWait, injectAuthAndLoad, waitForFlutter, visitAndWaitForFlutter, BASE_URL };
