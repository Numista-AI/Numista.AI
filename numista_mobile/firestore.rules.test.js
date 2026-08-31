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
const profilePath = `users/${ownerEmail}/profile`;

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

test("DENY: owner attempts to set is_demo: false on update (even false is blocked)", async () => {
  await seedCoin("c7", { is_demo: false });
  const db = ownerCtx.firestore();
  await assertFails(
    // affectedKeys() triggers on any change to the key, including false -> false
    // (this test verifies the key is in the blocked set, not just the value)
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

// ─── PROFILE sandbox_cleared rules ────────────────────────────────────────────

async function seedProfile(data = {}) {
  await testEnv.withSecurityRulesDisabled(async (adminCtx) => {
    await setDoc(doc(adminCtx.firestore(), profilePath), {
      name: "Test Owner",
      sandbox_cleared: false,
      ...data,
    });
  });
}

test("ALLOW: owner updates profile display_name (non-protected field)", async () => {
  await seedProfile();
  const db = ownerCtx.firestore();
  await assertSucceeds(
    updateDoc(doc(db, profilePath), { display_name: "Eric D." })
  );
});

test("DENY: owner attempts to change sandbox_cleared on own profile", async () => {
  await seedProfile();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, profilePath), { sandbox_cleared: true })
  );
});

// ─── Estate entitlement flag rules (v2.1 B-ADD-1) ────────────────────────────
// These three flags may only be set by Admin SDK (set_owner_entitlements.py).
// An owner patching them directly could forge tier access or attorney eligibility.

test("DENY: owner_cannot_self_grant_estate — is_lifetime_family_estate blocked", async () => {
  await seedProfile();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, profilePath), { is_lifetime_family_estate: true })
  );
});

test("DENY: owner_cannot_self_grant_estate — is_ai_qc_account blocked", async () => {
  await seedProfile();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, profilePath), { is_ai_qc_account: true })
  );
});

test("DENY: owner_cannot_self_grant_estate — beta_tester blocked", async () => {
  await seedProfile();
  const db = ownerCtx.firestore();
  await assertFails(
    updateDoc(doc(db, profilePath), { beta_tester: true })
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
