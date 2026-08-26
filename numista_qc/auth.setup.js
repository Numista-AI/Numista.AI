/**
 * auth.setup.js — QC Suite one-time authentication setup
 *
 * Mirrors the approach used in numista_tests/tests/auth.setup.js (Phase 3C).
 *
 * PROBLEM: Firebase stores auth tokens in IndexedDB, not cookies/localStorage.
 * Playwright's storageState() cannot capture IndexedDB.
 *
 * SOLUTION: Sign in once here, extract the IndexedDB entries, and save them
 * to fixtures/auth-token.json. Each Layer 2 test then uses qc-helpers.js
 * injectAuthAndLoad() to pre-populate IndexedDB via addInitScript BEFORE
 * the page loads — so Flutter starts up already authenticated.
 *
 * This eliminates per-test sign-in (was 26-75s each → ~5s with injection).
 */

const { test: setup } = require('@playwright/test');
const path = require('path');
const fs   = require('fs');
require('dotenv').config({ path: path.join(__dirname, '../numista_tests/.env') });

const FIXTURES_DIR = path.join(__dirname, 'fixtures');
const TOKEN_FILE   = path.join(FIXTURES_DIR, 'auth-token.json');

const BASE_URL = process.env.PLAYWRIGHT_BASE_URL || 'https://numista.ai';

setup('qc-authenticate', async ({ page }) => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;

  if (!email || !password) {
    throw new Error(
      'TEST_USER_EMAIL or TEST_USER_PASSWORD missing.\n' +
      'Check: C:\\Users\\ericd\\Documents\\MyVertexProject\\numista_tests\\.env'
    );
  }

  if (!fs.existsSync(FIXTURES_DIR)) {
    fs.mkdirSync(FIXTURES_DIR, { recursive: true });
  }

  console.log(`[qc-auth] Authenticating as: ${email}`);
  await page.goto(BASE_URL);
  await page.waitForLoadState('networkidle', { timeout: 30000 });

  // Wait for Firebase SDK to be fully initialized
  await page.waitForFunction(
    () =>
      typeof window.firebase_core !== 'undefined' &&
      typeof window.firebase_auth !== 'undefined' &&
      (window.firebase_core.getApps?.() ?? []).length > 0,
    { timeout: 30000 }
  );
  console.log('[qc-auth] Firebase ready. Signing in...');

  // Sign in and extract IndexedDB auth entries
  const authData = await page.evaluate(async ({ em, pw }) => {
    const auth = window.firebase_auth.getAuth();
    const cred = await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
    const user = cred.user;
    const idToken = await user.getIdToken(false);

    // Extract the IndexedDB entry Firebase uses for persistence
    const dbData = await new Promise((resolve) => {
      const req = indexedDB.open('firebaseLocalStorageDb');
      req.onsuccess = (e) => {
        const db = e.target.result;
        const tx = db.transaction('firebaseLocalStorage', 'readonly');
        const store = tx.objectStore('firebaseLocalStorage');
        const all = store.getAll();
        all.onsuccess = () => resolve(all.result);
        all.onerror  = () => resolve([]);
      };
      req.onerror = () => resolve([]);
    });

    return {
      uid:       user.uid,
      email:     user.email,
      idToken,
      dbEntries: dbData,
      appName:   auth.app.name,
      apiKey:    auth.app.options.apiKey,
    };
  }, { em: email, pw: password });

  if (!authData.uid) {
    throw new Error('[qc-auth] Sign-in succeeded but could not extract user UID.');
  }

  console.log(`[qc-auth] Signed in: uid=${authData.uid}`);
  console.log(`[qc-auth] IndexedDB entries captured: ${authData.dbEntries.length}`);

  const record = {
    timestamp: new Date().toISOString(),
    uid:       authData.uid,
    email:     authData.email,
    idToken:   authData.idToken,
    appName:   authData.appName,
    apiKey:    authData.apiKey,
    dbEntries: authData.dbEntries,
  };

  fs.writeFileSync(TOKEN_FILE, JSON.stringify(record, null, 2));
  console.log(`[qc-auth] Token saved to: ${TOKEN_FILE} (${fs.statSync(TOKEN_FILE).size} bytes)`);
});
