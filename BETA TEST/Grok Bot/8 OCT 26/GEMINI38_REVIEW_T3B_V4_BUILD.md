# GEMINI38_REVIEW_T3B_V4_BUILD.md
**Reviewer:** Antigravity CoS (Gemini)  
**Date:** 2026-10-13  
**Commit reviewed:** `39125bac`  
**Track:** T3b V4 — REQ_032B Alternate Site / Rules Hardening V4  
**Verdict:** ✅ PASS — All 5 sensitive subcollections excluded from owner wildcard, explicit server-only blocks enforced, 10 new emulator tests added, 38/38 emulator tests green.

---

## 1. Exclusion of Sensitive Subcollections from Owner Wildcard

**File:** `numista_mobile/firestore.rules:109-117`

**Verbatim code checked:**
```javascript
    // Subcollections the owner CAN read+write (wishlist, review_queue, etc.)
    // coins and profile are excluded because they have more-specific blocks above.
    // server-only subcollections are excluded so writes are blocked.
    match /users/{email}/{sub}/{docId} {
      allow read, write: if isOwner(email)
        && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency']);
    }
    // Nested docs within writable subcollections
    match /users/{email}/{sub}/{docId}/{rest=**} {
      allow read, write: if isOwner(email)
        && !(sub in ['settings', 'estate_reports', 'morgan_action_log', 'trash', 'audit_log', 'coins', 'profile', 'morgan_proposals', 'subaccounts', 'subscription', 'transferred_coins', 'transferred_currency']);
    }
```

**Review findings:**
- ✅ `morgan_proposals`, `subaccounts`, `subscription`, `transferred_coins`, `transferred_currency` are explicitly added to the negative check list.
- ✅ Wildcard write permissions no longer override server-only protection for these collections.
- ✅ Identical update applied to mirror file `numista_backend/firestore.rules:110-118`.

---

## 2. Server-Only Subcollection Blocks (Read-Only for Owner, Client Write Denied)

**File:** `numista_mobile/firestore.rules:139-158`

**Verbatim code checked:**
```javascript
    match /users/{email}/morgan_proposals/{docId} {
      allow read: if isOwner(email);
      allow write: if false;
    }
    match /users/{email}/subaccounts/{docId} {
      allow read: if isOwner(email);
      allow write: if false;
    }
    match /users/{email}/subscription/{docId} {
      allow read: if isOwner(email);
      allow write: if false;
    }
    match /users/{email}/transferred_coins/{docId} {
      allow read: if isOwner(email);
      allow write: if false;
    }
    match /users/{email}/transferred_currency/{docId} {
      allow read: if isOwner(email);
      allow write: if false;
    }
```

**Review findings:**
- ✅ Direct client writes (`allow write: if false;`) are completely blocked. Only the backend Admin SDK (service account) can write or mutate proposals, subaccounts, subscription records, and transferred asset records.
- ✅ Owner read is preserved (`allow read: if isOwner(email);`) so UI can display proposals, subaccounts, and subscriptions.
- ✅ Mirror file `numista_backend/firestore.rules:140-159` matches verbatim.

---

## 3. Firestore Rules Emulator Tests (10 New Tests, 38/38 Total)

**File:** `numista_mobile/firestore.rules.test.js:288-355`

**Verbatim code checked:**
```javascript
test("DENY: owner cannot write to morgan_proposals (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, morganProposalsPath), { proposal: "test" })
  );
});

test("DENY: owner cannot write to subaccounts (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, subaccountsPath), { role: "sub" })
  );
});

test("DENY: owner cannot write to subscription (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, subscriptionPath), { status: "active" })
  );
});

test("DENY: owner cannot write to transferred_coins (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, transferredCoinsPath), { coinId: "c1" })
  );
});

test("DENY: owner cannot write to transferred_currency (server-only)", async () => {
  const db = ownerCtx.firestore();
  await assertFails(
    setDoc(doc(db, transferredCurrencyPath), { currencyId: "cur1" })
  );
});

test("ALLOW: owner can read settings/ui_variant (read-only for owner)", async () => {
  const db = ownerCtx.firestore();
  const snap = await getDoc(doc(db, settingsPath));
  expect(snap).toBeDefined();
});

test("ALLOW: owner can read morgan_proposals (read-only for owner)", async () => {
  const db = ownerCtx.firestore();
  const snap = await getDoc(doc(db, morganProposalsPath));
  expect(snap).toBeDefined();
});

test("ALLOW: owner can read subaccounts (read-only for owner)", async () => {
  const db = ownerCtx.firestore();
  const snap = await getDoc(doc(db, subaccountsPath));
  expect(snap).toBeDefined();
});

test("ALLOW: owner can read subscription (read-only for owner)", async () => {
  const db = ownerCtx.firestore();
  const snap = await getDoc(doc(db, subscriptionPath));
  expect(snap).toBeDefined();
});

test("ALLOW: owner can read transferred_coins (read-only for owner)", async () => {
  const db = ownerCtx.firestore();
  const snap = await getDoc(doc(db, transferredCoinsPath));
  expect(snap).toBeDefined();
});
```

**Emulator Execution Result:**
```
PASS ./firestore.rules.test.js (21.618 s)
Test Suites: 1 passed, 1 total
Tests:       38 passed, 38 total
Snapshots:   0 total
Time:        21.618 s
```

**Review findings:**
- ✅ All 10 new tests pass under Jest in the local Firestore emulator.
- ✅ 5 write tests confirm client writes fail (`assertFails`).
- ✅ 5 read tests confirm owner reads succeed without permission-denied errors.
- ✅ Total test count increased from 28 to 38; all 38 pass.

---

## Summary

| Component | File:Lines | Status |
|---|---|---|
| Wildcard exclusion list | `numista_mobile/firestore.rules:109-117` | ✅ PASS |
| Server-only subcollections | `numista_mobile/firestore.rules:139-158` | ✅ PASS |
| Backend mirror sync | `numista_backend/firestore.rules:110-159` | ✅ PASS |
| Emulator security tests | `numista_mobile/firestore.rules.test.js:288-355` | ✅ 38/38 PASS |

**Verdict:** ✅ PASS. Ready for Grok CoS build scoring.
