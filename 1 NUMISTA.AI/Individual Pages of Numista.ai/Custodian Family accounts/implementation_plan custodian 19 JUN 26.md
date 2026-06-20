# Custodian Accounts — Implementation Plan

## The Goal

Allow a **Custodian** (e.g., you — Eric) to help manage another person's Numista.AI collection
(e.g., Aunt AJ, your father) without ever needing to know their PIN. Each person keeps their own
account, their own login, their own data. The custodian simply "switches into" a managed account
to add/edit coins on their behalf.

---

## How It Works (User Story)

```
Aunt AJ logs into her account → goes to Settings → "Manage Custodians"
→ She types: eric@numista.ai → Clicks "Grant Access"
→ Eric gets a notification/confirmation

Later... Eric logs into HIS account → Sidebar shows:
  📦 My Vault (eric@numista.ai)
  👤 Managing: Aunt AJ (jseaman1204@gmail.com)  ← new banner/switcher
→ Eric clicks "Manage Aunt AJ's Vault"
→ The app reads/writes to Aunt AJ's Firestore path instead
→ A prominent orange banner: "Viewing Aunt AJ's Collection — Your account: eric@numista.ai"
→ Eric can add coins, do invoice scans, manage collection — all to Aunt AJ's data
→ "Return to My Vault" button always visible
```

---

## Firestore Schema

### New Collection: `custodian_grants`
```
custodian_grants/{grantId}
  owner_email:     "jseaman1204@gmail.com"   // Aunt AJ
  owner_name:      "Aunt AJ"
  custodian_email: "eric@numista.ai"          // Eric
  status:          "active" | "pending" | "revoked"
  granted_at:      Timestamp
  revoked_at:      Timestamp? (null if active)
  permissions:     ["read", "write"]          // future-proofed for read-only mode
```

### Updated: `users/{email}` profile doc
```
users/{email}
  ... (existing fields) ...
  custodian_of: ["jseaman1204@gmail.com", "dad@example.com"]  // denormalized for quick sidebar load
```

**Why two places?** The grant doc is the source of truth (auditable, revocable). The denormalized
list on the custodian's profile doc allows the sidebar to load managed accounts instantly on login
without a separate query.

---

## Architecture: The "Active Vault" Concept

The key challenge: `AuthService.coinsPath` and `AuthService.userEmail` are used in **28+ files**
across the entire app. We cannot change every call site.

**Solution: Add an `activeVault` override to `AuthService`.**

```dart
// In AuthService:
static String? _activeVaultEmail;  // null = use own account

static String get activeVaultEmail => _activeVaultEmail ?? userEmail;
static bool get isManagingAnotherVault => _activeVaultEmail != null;

// Override coinsPath transparently:
static String get coinsPath {
  final email = activeVaultEmail;
  if (email == 'guest') return 'users/${currentUser!.uid}/coins';
  return 'users/$email/coins';
}

static Future<void> switchToVault(String ownerEmail) async { ... }
static void returnToMyVault() { _activeVaultEmail = null; }
```

**This means zero changes are needed to the 28+ call sites.** Every screen that already reads
`AuthService.coinsPath` or `AuthService.userEmail` will automatically read/write the correct vault.

---

## Files to Create / Modify

### New Files

---

#### [NEW] `lib/services/custodian_service.dart`
The core service. Handles all Firestore reads/writes for the grant system:
- `grantAccess(ownerEmail, custodianEmail)` — owner creates a grant
- `revokeAccess(grantId)` — owner removes a grant
- `getManagedVaults(custodianEmail)` — returns list of vaults the custodian can manage
- `getGrantsForOwner(ownerEmail)` — returns list of custodians who can access the owner's vault
- `verifyGrant(ownerEmail, custodianEmail)` — security check before switching vaults

---

#### [NEW] `lib/screens/custodian_settings_screen.dart`
A new screen (accessible from Settings) with two sections:

**Section 1 — "People Who Help Me" (Owner view)**
- Shows current custodians with their status (active/revoked)
- "Add a Custodian" → type their email → "Grant Access" button
- "Revoke" button per custodian with a confirmation dialog

**Section 2 — "Vaults I Manage" (Custodian view)**
- Shows accounts I have been granted access to
- "Manage Their Vault" button → triggers `AuthService.switchToVault()`

---

#### [NEW] `lib/widgets/active_vault_banner.dart`
A persistent orange/amber banner that appears at the top of **every screen** when managing
another person's vault:
```
┌─────────────────────────────────────────────────────┐
│  🔑 Managing: Aunt AJ's Vault  [Return to My Vault] │
└─────────────────────────────────────────────────────┘
```
- Amber background, clearly visible
- Always shows whose vault is active
- One-tap return to own vault

---

### Modified Files

---

#### [MODIFY] `lib/services/auth_service.dart`
- Add `_activeVaultEmail` static field
- Add `activeVaultEmail` getter
- Add `isManagingAnotherVault` getter
- Modify `coinsPath` to use `activeVaultEmail`
- Add `switchToVault(String ownerEmail)` — validates grant exists, sets override
- Add `returnToMyVault()` — clears override
- Add `signOut()` override to always clear `_activeVaultEmail` on sign-out

---

#### [MODIFY] `lib/screens/base_layout.dart`
- Inject `ActiveVaultBanner` at the top of the content area when
  `AuthService.isManagingAnotherVault == true`
- Add vault switcher to the sidebar's account section (shows managed vaults from CustodianService)

---

#### [MODIFY] `lib/screens/settings_screen.dart`
- Add a new **"Family & Custodians"** section card
- Button: "Manage Custodian Access" → navigates to `CustodianSettingsScreen`
- Shows quick summary: "X custodians have access to your vault" or "You manage X vaults"

---

## Security Rules (Firestore)

```javascript
// Custodian grants — only involved parties can read/write
match /custodian_grants/{grantId} {
  allow read: if request.auth.token.email == resource.data.owner_email
               || request.auth.token.email == resource.data.custodian_email;
  allow create: if request.auth.token.email == request.resource.data.owner_email;
  allow update: if request.auth.token.email == resource.data.owner_email; // owner can revoke
}

// Vault access — allow custodian to read/write owner's coins if active grant exists
// (This requires a Firestore function or server-side validation for security)
match /users/{userEmail}/coins/{coinId} {
  allow read, write: if request.auth.token.email == userEmail
    || exists(/databases/$(database)/documents/custodian_grants/$(
        userEmail + '_' + request.auth.token.email))
       && get(/databases/.../custodian_grants/...).data.status == 'active';
}
```

> [!IMPORTANT]
> The Firestore security rules for vault cross-access need careful design. The app-side grant
> verification in `switchToVault()` provides a UX guard, but the Firestore rules are the real
> security boundary. We'll implement both layers.

---

## UI Design Notes

### Settings Screen — New Card
```
┌─── Family & Custodians ──────────────────────────────┐
│  👨‍👩‍👧 1 person helps manage your vault               │
│  🔑 You manage 0 other vaults                        │
│                    [Manage Custodian Access →]        │
└──────────────────────────────────────────────────────┘
```

### Custodian Settings Screen — Owner Tab
```
People Who Help Me (Custodians)
────────────────────────────────
eric@numista.ai    ● Active    [Revoke]
────────────────────────────────
+ Add a custodian
  [email field]   [Grant Access]

Note: Custodians can add and edit coins in your vault.
They CANNOT change your PIN, delete your account, or see
your payment information.
```

### Custodian Settings Screen — Custodian Tab
```
Vaults You Manage
────────────────────────────────
Aunt AJ (jseaman1204@gmail.com)
● Access granted Apr 9, 2026
[Manage Their Vault →]
```

### Sidebar Switcher (base_layout.dart)
When the user has managed vaults, the sidebar account section becomes a dropdown:
```
● eric@numista.ai (You)
  jseaman1204@gmail.com (Aunt AJ) →
```

---

## Open Questions

> [!IMPORTANT]
> **1. Invitation flow** — Should granting access send an email to the custodian notifying them?
> Or is a silent grant OK for now (custodian just sees the vault appear next time they log in)?

> [!IMPORTANT]
> **2. Permissions granularity** — For v1, custodians get full read+write access. Should we
> plan for a future "read-only" mode (e.g., let an attorney view but not edit)?
> (This is already future-proofed in the schema with the `permissions` array.)

> [!NOTE]
> **3. Hard-wired admin shortcut** — `settings_screen.dart` currently has `jseaman1204@gmail.com`
> hard-coded as your "Danger Zone" target. Once this feature is live, you can remove that
> hard-code — you'll just use the custodian switcher to manage Aunt AJ's vault properly.

---

## Verification Plan

### Automated
- `flutter analyze` — zero issues
- `flutter build web` — clean build

### Manual Test Flow
1. Log in as `eric@numista.ai` → go to Settings → confirm new "Family & Custodians" card appears
2. Log in as `jseaman1204@gmail.com` (Aunt AJ) → go to Custodian Settings → add `eric@numista.ai` as custodian
3. Log back in as `eric@numista.ai` → confirm Aunt AJ's vault appears in sidebar
4. Click "Manage Their Vault" → confirm orange banner appears
5. Add a test coin → confirm it writes to `users/jseaman1204@gmail.com/coins` not your own
6. Click "Return to My Vault" → confirm banner disappears, own data resumes
7. Log back in as Aunt AJ → confirm she can revoke access → Eric's sidebar no longer shows her vault

---

## Implementation Order

1. `custodian_service.dart` (backend logic, no UI dependency)
2. `auth_service.dart` (add vault switching, zero breaking changes)
3. `active_vault_banner.dart` (widget, no logic dependency)
4. `base_layout.dart` (inject banner + sidebar switcher)
5. `custodian_settings_screen.dart` (full UI for managing grants)
6. `settings_screen.dart` (add navigation card)
7. Firestore security rules update
