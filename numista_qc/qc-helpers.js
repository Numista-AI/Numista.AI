/**
 * qc-helpers.js — Shared helpers for Numista QC Suite (all layers)
 *
 * Auth strategy (Layer 2):
 *   auth.setup.js runs ONCE per test suite invocation, saves the Firebase
 *   IndexedDB auth token to fixtures/auth-token.json.
 *
 *   Each Layer 2 test calls injectAuthAndLoad(page) which:
 *     1. Reads fixtures/auth-token.json
 *     2. Adds an init script that pre-populates IndexedDB BEFORE the page loads
 *     3. Navigates to the app — Firebase finds the token in IndexedDB on startup
 *     4. Waits for flt-glass-pane to be visible (condition-based, not a bare sleep)
 *
 *   This replaces the old per-test signInAndWait() pattern (26-75s each) with
 *   a ~5-10s injection approach.
 *
 * USAGE in a Layer 2 QC spec:
 *   const { injectAuthAndLoad, waitForFlutter } = require('../qc-helpers');
 *   test.beforeEach(async ({ page }) => { await injectAuthAndLoad(page); });
 *
 * USAGE in a Layer 1 QC spec (no auth needed):
 *   const { visitAndWaitForFlutter } = require('../qc-helpers');
 */

const path = require('path');
const fs   = require('fs');
require('dotenv').config({ path: path.join(__dirname, '../numista_tests/.env') });

const TOKEN_FILE = path.join(__dirname, 'fixtures', 'auth-token.json');
const BASE_URL   = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';

// ─── Low-level waits ────────────────────────────────────────────────────────

/**
 * waitForFlutter — condition-based wait for flt-glass-pane visibility.
 * Exits as soon as Flutter is rendered. Do NOT replace with waitForTimeout().
 *
 * @param {import('@playwright/test').Page} page
 * @param {number} [timeout=20000]
 */
async function waitForFlutter(page, timeout = 20000) {
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flt-glass-pane');
      return p && window.getComputedStyle(p).visibility === 'visible';
    },
    { timeout }
  );
}

// ─── Auth injection (Layer 2) ────────────────────────────────────────────────

/**
 * injectAuthAndLoad — load auth-token.json and inject Firebase IndexedDB entries
 * via addInitScript, then navigate. Flutter starts up pre-authenticated.
 *
 * This is ~5-10s vs the old per-test sign-in chain of 26-75s.
 *
 * @param {import('@playwright/test').Page} page
 * @param {{ url?: string, flutterTimeout?: number }} [opts]
 */
async function injectAuthAndLoad(page, opts = {}) {
  const url           = opts.url           || BASE_URL;
  const flutterTimeout = opts.flutterTimeout || 20000;

  // Read the token written by auth.setup.js
  if (!fs.existsSync(TOKEN_FILE)) {
    throw new Error(
      `[qc-helpers] fixtures/auth-token.json not found.\n` +
      `Run auth.setup.js first, or ensure the 'setup' project ran before chromium.\n` +
      `Expected path: ${TOKEN_FILE}`
    );
  }
  const authRecord = JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf8'));

  if (!authRecord.dbEntries || authRecord.dbEntries.length === 0) {
    throw new Error(
      '[qc-helpers] auth-token.json has no IndexedDB entries. ' +
      'Re-run auth.setup.js to refresh the token.'
    );
  }

  // Inject IndexedDB entries BEFORE page load via addInitScript
  // This runs synchronously in the page context before any scripts execute
  await page.addInitScript(({ entries, appName }) => {
    // Called before page scripts — schedules IndexedDB write on first tick
    const writeEntries = () => {
      const req = indexedDB.open('firebaseLocalStorageDb', 1);
      req.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains('firebaseLocalStorage')) {
          db.createObjectStore('firebaseLocalStorage', { keyPath: 'fbase_key' });
        }
      };
      req.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction('firebaseLocalStorage', 'readwrite');
        const store = tx.objectStore('firebaseLocalStorage');
        entries.forEach(entry => store.put(entry));
      };
    };
    writeEntries();

    // Also set localStorage onboarding flags so Flutter skips wizard dialogs
    ['flutter.user_name', 'flutter.morgan_onboarding_complete',
     'flutter.onboarding_complete', 'flutter.beta_tester_welcome_seen_v2']
      .forEach(k => localStorage.setItem(k, 'true'));
  }, { entries: authRecord.dbEntries, appName: authRecord.appName });

  // Navigate — Firebase finds the token in IndexedDB immediately on startup
  await page.goto(url);

  // Wait for Flutter canvas to be visible
  try {
    await waitForFlutter(page, flutterTimeout);
  } catch {
    await page.screenshot({ path: 'screenshots/injectAuthAndLoad-timeout.png' }).catch(() => {});
    throw new Error(
      `[qc-helpers] Flutter canvas not visible within ${flutterTimeout}ms after auth injection. ` +
      'Check screenshots/injectAuthAndLoad-timeout.png — token may have expired.'
    );
  }
}

// ─── Unauthenticated navigation (Layer 1, Layer 3) ──────────────────────────

/**
 * visitAndWaitForFlutter — navigate and wait for Flutter to render.
 * No auth. Use for Layer 1 UX tests and unauthenticated flow tests.
 *
 * @param {import('@playwright/test').Page} page
 * @param {string} [url] — defaults to BASE_URL
 * @param {number} [timeout=20000]
 */
async function visitAndWaitForFlutter(page, url = BASE_URL, timeout = 20000) {
  await page.goto(url);
  await page.waitForFunction(
    () => {
      const p = document.querySelector('flt-glass-pane');
      return p && p.offsetWidth > 0;
    },
    { timeout }
  );
}

// ─── Legacy alias (kept for backward compat with any direct callers) ─────────
// Deprecated: use injectAuthAndLoad() instead. Will be removed in a future cleanup.
async function signInAndWait(page) {
  console.warn('[qc-helpers] signInAndWait() is deprecated. Use injectAuthAndLoad() instead.');
  await injectAuthAndLoad(page);
}

module.exports = { injectAuthAndLoad, waitForFlutter, visitAndWaitForFlutter, signInAndWait, BASE_URL };
