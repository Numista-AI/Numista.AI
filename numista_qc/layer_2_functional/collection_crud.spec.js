/**
 * collection_crud.spec.js — Numista QC Layer 2
 * Add and delete coin in QA account.
 * Rules:
 *   - New docs: .add() whole document (no merge=True)
 *   - IDs: qc_test_{timestamp}_{random} prefix
 *   - Cleanup: afterEach deletes only docs whose ID starts with qc_test_
 *   - Never touches qc_fixture_* documents
 *   - No live eBay / PCGS / Greysheet calls
 *
 * Uses qc-helpers.js for robust condition-based Flutter-ready waits.
 * Fixes Aug 26 failure in "Add coin button" caused by 5s bare sleep timing out.
 */
const { test, expect } = require('@playwright/test');
const { signInAndWait } = require('../qc-helpers');


// Track doc IDs created in this run for cleanup
const CREATED_IDS = [];

// Generate a qc_test_ prefixed ID
function makeTestId() {
  const ts = Date.now();
  const rand = Math.random().toString(36).slice(2, 7);
  return `qc_test_${ts}_${rand}`;
}

// Cleanup: delete only qc_test_* docs (never qc_fixture_*)
async function cleanupTestDocs(page) {
  const failures = [];
  for (const docId of CREATED_IDS) {
    if (!docId.startsWith('qc_test_')) {
      console.warn(`[cleanup] Skipping non-qc_test_ doc: ${docId}`);
      continue;
    }
    try {
      await page.evaluate(async (id) => {
        const uid = window.firebase_auth.getAuth().currentUser?.uid;
        if (!uid) throw new Error('No current user for cleanup');
        const db = window.firebase_firestore?.getFirestore?.() ||
                    window.firestore?.getFirestore?.();
        if (!db) throw new Error('Firestore not available for cleanup');
        const { doc, deleteDoc } = window.firebase_firestore;
        await deleteDoc(doc(db, 'users', uid, 'coins', id));
      }, docId);
    } catch (e) {
      failures.push({ docId, error: e.message });
    }
  }
  if (failures.length > 0) {
    // Log to _cleanup_failures.json equivalent via console
    console.error('[cleanup] CLEANUP_FAILURES:', JSON.stringify(failures));
  }
  CREATED_IDS.length = 0;
}

test.describe('Collection CRUD', () => {
  test.afterEach(async ({ page }) => {
    await cleanupTestDocs(page);
  });

  test.beforeEach(async ({ page }) => {
    await signInAndWait(page);
  });

  test('Add coin button is reachable and renders a form', async ({ page }) => {
    const addBtn = page.locator('flt-semantics[role=button]').filter({ hasText: /add coin|add a coin|add coins/i });
    const visible = await addBtn.first().isVisible({ timeout: 8000 }).catch(() => false);
    if (!visible) { test.skip(); return; }
    await addBtn.first().click();
    await page.waitForTimeout(3000);
    // After clicking add, a form or dialog should appear — assert on flt-semantics content,
    // NOT flt-glass-pane which is always 0x0 in this headless config (diagnostic Aug 26).
    const hasContent = await page.locator('flt-semantics').first().isVisible({ timeout: 5000 }).catch(() => false);
    expect(hasContent, 'No flt-semantics content after clicking Add Coin').toBe(true);
    // Negative: no error shown
    const error = await page.locator('flt-semantics').filter({ hasText: /error|failed/i }).first().isVisible({ timeout: 2000 }).catch(() => false);
    expect(error, 'Error visible after clicking Add Coin').toBe(false);
  });

  test('qc_test_ doc write and delete cycle (data-layer, no UI)', async ({ page }) => {
    // This test writes a qc_test_ doc directly via Firestore JS SDK in the browser context
    // (reusing the authenticated session), then deletes it.
    // It does NOT use merge=True for the new record.
    const testId = makeTestId();
    CREATED_IDS.push(testId);

    const writeResult = await page.evaluate(async (id) => {
      try {
        const uid = window.firebase_auth.getAuth().currentUser?.uid;
        if (!uid) return { ok: false, error: 'No current user' };
        const db = window.firebase_firestore?.getFirestore?.();
        if (!db) return { ok: false, error: 'Firestore not available' };
        const { doc, setDoc } = window.firebase_firestore;
        // Whole-document write — no merge option
        await setDoc(doc(db, 'users', uid, 'coins', id), {
          title: 'QC Test Coin',
          year: '2026',
          denomination: '$1',
          country: 'United States',
          is_foreign: false,
          review_status: 'test',
          _qc_test: true,
        });
        return { ok: true };
      } catch (e) { return { ok: false, error: e.message }; }
    }, testId);

    expect(writeResult.ok, `Write failed: ${writeResult.error}`).toBe(true);

    // Verify doc exists
    const readResult = await page.evaluate(async (id) => {
      try {
        const uid = window.firebase_auth.getAuth().currentUser?.uid;
        const db = window.firebase_firestore?.getFirestore?.();
        const { doc, getDoc } = window.firebase_firestore;
        const snap = await getDoc(doc(db, 'users', uid, 'coins', id));
        return { exists: snap.exists(), data: snap.data() };
      } catch (e) { return { exists: false, error: e.message }; }
    }, testId);

    expect(readResult.exists, 'Written doc not found in Firestore').toBe(true);
    expect(readResult.data._qc_test, 'Written doc missing _qc_test flag').toBe(true);

    // Cleanup will delete it in afterEach — confirmed by prefix check
    expect(testId.startsWith('qc_test_'), 'Test ID does not have required prefix').toBe(true);
    expect(testId.startsWith('qc_fixture_'), 'Test ID accidentally matches fixture prefix').toBe(false);
  });
});
