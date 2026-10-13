/**
 * firestore.rules.test.js
 * =======================
 * ADDENDUM B — Firestore field-level rules unit tests
 * Tests the affectedKeys() guards on is_demo, is_demo_cleared, sandbox_cleared.
 *
 * Run: npx @firebase/rules-unit-testing  (from numista_mobile/)
 * Or:  firebase emulators:exec --only firestore "npx jest firestore.rules.test.js"
 *
 * Acceptance criteria from ITEM 6 + v4.1 Addendum B:
 *   [ ] Client SDK attempt to set is_demo: true on own coin returns PERMISSION_DENIED
 *   [ ] Client SDK attempt to change is_demo_cleared on own coin returns PERMISSION_DENIED
 *   [ ] Client SDK attempt to change sandbox_cleared on own profile returns PERMISSION_DENIED
 *   [ ] Client SDK can create a coin with is_demo: false (allowed)
 *   [ ] Client SDK can create a coin without is_demo field (allowed; backfill covers it)
 *   [ ] Client SDK can update other coin fields without touching is_demo (allowed)
 */

const { initializeTestEnvironment, assertFails, assertSucceeds } =
  require("@firebase/rules-unit-testing");
const { doc, setDoc, updateDoc, getDoc } = require("firebase/firestore");
const fs = require("fs");
const path = require("path");

const PROJECT_ID = "studio-9101802118-8c9a8";
const RULES_PATH = path.join(__dirname, "firestore.rules");

let testEnv;
let ownerCtx;
let otherCtx;

beforeAll(async () => {
  testEnv = await initializeTestEnvironment({
    projectId: PROJECT_ID,
    firestore: {
      rules: fs.readFileSync(RULES_PATH, "utf8"),
      host: "127.0.0.1",
      port: 8080,
    },
  });

  // Owner: authenticated user whose email matches the path
  ownerCtx = testEnv.authenticatedContext("owner_uid", { email: "testowner@numista.ai" });

  // Other user: different uid and email
  otherCtx = testEnv.authenticatedContext("other_uid", { email: "other@numista.ai" });
});

afterAll(async () => {
  await testEnv.cleanup();
});

beforeEach(async () => {
  await testEnv.clearFirestore();
});

// ─── Helpers ─────────────────────────────────────────────────────────────────
const ownerEmail = "testowner@numista.ai";
const coinPath = (id) => `users/${ownerEmail}/coins/${id}`;
const profilePath = `users/${ownerEmail}/profile/main`; // 4-segment doc path (collection/doc/collection/doc)

// ─── CREATE rules ──────────────────────────────────────────────────────────────

// Rule change (v2 plan): is_demo and is_demo_cleared must BOTH be present and
// explicitly false on create. get('is_demo', false) != true allowed omitting the
// field — then WHERE is_demo == false hides the coin (empty-vault bug).

test("DENY: owner_create_omitting_is_demo — field absent triggers PERMISSION_DENIED", async () => {
  // This is the critical empty-vault regression test.
  // A coin created without is_demo would survive the old get() rule but be
  // hidden by the WHERE is_demo == false display filter.
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, coinPath("c1")), {
      Year: "1921",
      Denomination: "Dollar",
      source: "manual",
      // is_demo intentionally omitted — MUST be DENIED by new rule
    })
  );
});

test("ALLOW: owner creates coin with is_demo: false and is_demo_cleared: false", async () => {
  const db = ownerCtx.firestore();
  await assertSucceeds(
    setDoc(doc(db, coinPath("c2")), {
      Year: "1941",
      Denomination: "Half Dollar",
      is_demo: false,
      is_demo_cleared: false,
    })
  );
});

test("DENY: owner creates coin with is_demo: true", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, coinPath("c3")), {
      Year: "1944",
      Denomination: "Cent",
      is_demo: true,         // BLOCKED — client may never create a demo coin
      is_demo_cleared: false,
    })
  );
});

test("DENY: owner creates coin with is_demo_cleared: true", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, coinPath("c4")), {
      Year: "1921",
      is_demo: false,
      is_demo_cleared: true,  // BLOCKED — client may never set this on create
    })
  );
});

// ─── UPDATE rules ──────────────────────────────────────────────────────────────

// Seed a coin doc first, then try to update protected fields
async function seedCoin(id, data = {}) {
  await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
    await setDoc(doc(adminCtx.firestore(), coinPath(id)), {
      Year: "1921",
      Denomination: "Dollar",
      is_demo: false,
      is_demo_cleared: false,
      ...data,
    });
  });
}

test("ALLOW: owner updates non-protected coin field (Condition)", async () => {
  await seedCoin("c5");
  const db = ownerCtx.firestore();
  await assertSucceeds(
    updateDoc(doc(db, coinPath("c5")), { Condition: "MS63" })
  );
});

test("DENY: owner attempts to set is_demo: true on own coin", async () => {
  await seedCoin("c6");
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, coinPath("c6")), { is_demo: true })
  );
});

test("DENY: owner attempts to change is_demo from true to false (any value change blocked)", async () => {
  // Seed via admin with is_demo: true so the update is a real value change (true -> false)
  // affectedKeys() only fires when a value actually changes — false->false has no diff.
  await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
    await setDoc(doc(adminCtx.firestore(), coinPath("c7")), {
      Year: "2021", is_demo: true, is_demo_cleared: false,
    });
  });
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, coinPath("c7")), { is_demo: false, Condition: "AU55" })
  );
});

test("DENY: owner attempts to change is_demo_cleared on own coin", async () => {
  await seedCoin("c8");
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, coinPath("c8")), { is_demo_cleared: true })
  );
});

// ─── Entitlement field rules on users/{email} user doc ────────────────────────
// NOTE: The old profile subcollection tests (users/{email}/profile) were removed
// because the app never writes to that subcollection directly. sandbox_cleared,
// is_lifetime_family_estate, is_ai_qc_account, and beta_tester all live on the
// users/{email} top-level doc, guarded by _noEntitlementChange() below.
// The dead match /users/{email}/profile rule was removed from firestore.rules.

async function seedUserDoc(data = {}) {
  await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
    await setDoc(doc(adminCtx.firestore(), `users/${ownerEmail}`), {
      display_name: "Test Owner",
      sandbox_cleared: false,
      ...data,
    });
  });
}

test("ALLOW: owner updates display_name on user doc (non-protected field)", async () => {
  await seedUserDoc();
  const db = ownerCtx.firestore();
  await assertSucceeds(
    updateDoc(doc(db, `users/${ownerEmail}`), { display_name: "Eric D." })
  );
});

test("DENY: owner attempts to change sandbox_cleared on own user doc", async () => {
  await seedUserDoc();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, `users/${ownerEmail}`), { sandbox_cleared: true })
  );
});

test("DENY: owner_cannot_self_grant_estate — is_lifetime_family_estate blocked on user doc", async () => {
  await seedUserDoc();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, `users/${ownerEmail}`), { is_lifetime_family_estate: true })
  );
});

test("DENY: owner_cannot_self_grant_estate — is_ai_qc_account blocked on user doc", async () => {
  await seedUserDoc();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, `users/${ownerEmail}`), { is_ai_qc_account: true })
  );
});

test("DENY: owner_cannot_self_grant_estate — beta_tester blocked on user doc", async () => {
  await seedUserDoc();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, `users/${ownerEmail}`), { beta_tester: true })
  );
});

// ─── Cross-user reads ─────────────────────────────────────────────────────────

test("DENY: other user reads owner coins", async () => {
  await seedCoin("c9");
  const db = otherCtx.firestore();
  await assertFails(
    getDoc(doc(db, coinPath("c9")))
  );
});

// ─── T3b Fix 3: Server-only subcollection write protection ──────────────────
// These tests verify that the narrowed wildcard rule does NOT allow the
// client (even the owner) to write to server-only subcollections.

const settingsPath = `users/${ownerEmail}/settings/ui_variant`;
const estateReportsPath = `users/${ownerEmail}/estate_reports/report_001`;
const morganLogPath = `users/${ownerEmail}/morgan_action_log/log_001`;
const trashPath = `users/${ownerEmail}/trash/coin_001`;
const auditLogPath = `users/${ownerEmail}/audit_log/audit_001`;

test("DENY: owner cannot write to settings/ui_variant (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, settingsPath), { variant: "alt" })
  );
});

test("DENY: owner cannot write to estate_reports (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, estateReportsPath), { report: "data" })
  );
});

test("DENY: owner cannot write to morgan_action_log (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, morganLogPath), { action: "add", coin_id: "c1" })
  );
});

test("DENY: owner cannot write to trash (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, trashPath), { Year: "2026", deleted_by: "client" })
  );
});

test("DENY: owner cannot write to audit_log (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, auditLogPath), { event: "login" })
  );
});

test("ALLOW: owner can read settings/ui_variant (read-only for owner)", async () => {
  // Note: this may return permission denied if doc doesn't exist; use assertSucceeds only if emulator allows read on non-existent
  // This test documents the READ is allowed even though write is denied
  const db = ownerCtx.firestore();
  // getDoc on a non-existent document returns empty (not denied) if read is allowed
  const snap = await getDoc(doc(db, settingsPath));
  // No exception = read allowed (snap.exists() will be false)
  expect(snap).toBeDefined();
});

test("ALLOW: owner can still write to coins (writable subcollection)", async () => {
  const db = ownerCtx.firestore();
  await assertSucceeds(
    setDoc(doc(db, coinPath("allowed_coin")), {
      Year: "2026",
      Denomination: "Dime",
      is_demo: false,
      is_demo_cleared: false,
    })
  );
});


// =============================================================================
// ADDENDUM C — Entitlement field protection on users/{email} (T1B + T3b V3)
// Tests that owner cannot set tier/stripe_tier/beta_tester on their own user doc.
// ownerEmail is already declared above (line 58): "testowner@numista.ai"
// =============================================================================

const userDocPath = `users/${ownerEmail}`;

test("DENY: owner cannot set 'tier' on own user doc (P0 entitlement field)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, userDocPath), { display_name: "Alice", tier: "family_estate" })
  );
});

test("DENY: owner cannot set 'stripe_tier' on own user doc", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, userDocPath), { display_name: "Alice", stripe_tier: "enterprise" })
  );
});

test("DENY: owner cannot set 'beta_tester' on own user doc", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, userDocPath), { display_name: "Alice", beta_tester: true })
  );
});

test("DENY: owner cannot set 'is_lifetime_family_estate' on own user doc", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, userDocPath), { display_name: "Alice", is_lifetime_family_estate: true })
  );
});

test("DENY: owner cannot set 'admin' on own user doc", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, userDocPath), { display_name: "Alice", admin: true })
  );
});

test("ALLOW: owner can create own user doc without entitlement fields", async () => {
  // Clear any existing doc first via admin context
  await testEnv.withSecurityRulesDisabled(async (context) => {
    const adminDb = context.firestore();
    const ref = doc(adminDb, userDocPath);
    try { await ref.delete(); } catch (_) {}
  });
  const db = ownerCtx.firestore();
  await assertSucceeds(
    setDoc(doc(db, userDocPath), {
      display_name: "Alice",
      created_at: new Date().toISOString(),
    })
  );
});

test("DENY: coin create with is_demo: true still blocked by coin-level rule", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, coinPath("demo_test")), {
      Year: "2025",
      is_demo: true,
    })
  );
});
