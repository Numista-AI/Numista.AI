// auth.setup.js — Phase 3C (v7 — IndexedDB-aware approach)
//
// PROBLEM: Firebase modular SDK stores auth tokens in IndexedDB ('firebaseLocalStorage')
// Playwright's storageState() only captures cookies + localStorage, NOT IndexedDB.
//
// SOLUTION: After sign-in, manually extract the token from IndexedDB using
// page.evaluate(), save it as JSON, then inject it into each test via addInitScript.
//
// This means the remediation spec will use a beforeEach fixture that:
//   1. Reads fixtures/auth-token.json
//   2. Uses page.addInitScript to pre-populate IndexedDB before the page loads
//   3. The page loads with Firebase already having a valid auth token

const { test: setup } = require('@playwright/test');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.join(__dirname, '../.env') });

const TOKEN_FILE = path.join(__dirname, '../fixtures/auth-token.json');

setup('authenticate', async ({ page }) => {
  const email    = process.env.TEST_USER_EMAIL;
  const password = process.env.TEST_USER_PASSWORD;

  if (!email || !password) {
    throw new Error(
      'TEST_USER_EMAIL or TEST_USER_PASSWORD missing from numista_tests/.env'
    );
  }

  const fixturesDir = path.dirname(TOKEN_FILE);
  if (!fs.existsSync(fixturesDir)) {
    fs.mkdirSync(fixturesDir, { recursive: true });
  }

  console.log(`Authenticating as: ${email}`);
  await page.goto('/');

  // Wait for Firebase to initialize
  await page.waitForFunction(
    () =>
      typeof window.firebase_core !== 'undefined' &&
      typeof window.firebase_auth !== 'undefined' &&
      (window.firebase_core.getApps?.() ?? []).length > 0,
    { timeout: 30000 }
  );
  console.log('Firebase ready. Signing in...');

  // Sign in and extract ALL relevant IndexedDB keys
  const authData = await page.evaluate(async ({ em, pw }) => {
    const auth = window.firebase_auth.getAuth();
    const cred = await window.firebase_auth.signInWithEmailAndPassword(auth, em, pw);
    const user = cred.user;

    // Get the ID token
    const idToken = await user.getIdToken(/* forceRefresh= */ false);

    // Extract the IndexedDB entry that Firebase persists
    // Firebase stores: firebaseLocalStorageDb > firebaseLocalStorage > table
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
      uid: user.uid,
      email: user.email,
      idToken,
      dbEntries: dbData,
      appName: auth.app.name,
      apiKey: auth.app.options.apiKey,
    };
  }, { em: email, pw: password });

  if (!authData.uid) {
    throw new Error('Sign-in succeeded but could not extract user data.');
  }
  console.log(`Signed in: uid=${authData.uid}, email=${authData.email}`);
  console.log(`IndexedDB entries captured: ${authData.dbEntries.length}`);

  // Save token data for injection into tests
  const record = {
    timestamp: new Date().toISOString(),
    uid: authData.uid,
    email: authData.email,
    idToken: authData.idToken,
    appName: authData.appName,
    apiKey: authData.apiKey,
    dbEntries: authData.dbEntries,
  };
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(record, null, 2));
  console.log(`Token data saved to: ${TOKEN_FILE} (${fs.statSync(TOKEN_FILE).size} bytes)`);
});
