# PLAN V1 — REQ_032B: Alternate "Simple" Site (Track 3b)
Prepared by: Antigravity CoS  
Date: 2026-10-12  
Eric approval: YES, 12 Oct 2026 12:24 PM ET  
Model assigned: Claude Sonnet 4.6 (Thinking)  
Reviewer: Gemini 3.8 Flash  
Status: PLAN ONLY — awaiting Gemini review, then Grok CoS score, then founder Proceed + YES to deploy.  
Source: `FOR_AG_COS_TRACK3B_ALT_SITE_2026-10-12.md`  
Code baseline: branch `dev`, commit `e5f5760c`

---

## 1. Design (as ordered)

**One database. Two front-ends. Same backend.** Classic (current) and Simple (REQ_032 Fix 1-5 applied) read and write the same Firestore collections via the same backend API routes. No data copies, no shadow collections, no new backend routes that bypass REQ_031 auth lockdown or Morgan Gate 0 confirms.

The "Simple" front-end is the REQ_032 UX improvements from Track 3 (Fix 2 bigger text, Fix 3 PIN screen, Fix 4 6-item nav, Fix 5 3-choice Add Coin) applied as a cohesive layout variant, selectable via a server-side feature flag.

---

## 2. Feature Flag — Where It Lives

### 2a. Server-side (source of truth)

**Firestore path:** `users/{email}/settings/ui_variant`  
**Field:** `ui_variant: "classic" | "simple"`  
**Default:** `"classic"` (absent = classic)

The flag is written **only** by a new backend endpoint called by admin tools or by the Phase A/B/C rollout process. It cannot be set by the client directly.

**New backend endpoint:** `POST /api/admin/set_ui_variant` — requires `Depends(require_admin_user)` (deps.py:81). Body: `{email: str, variant: "classic" | "simple"}`. Writes to `users/{email}/settings/ui_variant`.

Phase A only: a second endpoint `POST /api/user/set_ui_variant` — requires only `Depends(get_current_user)`, but **only allowed for emails `eric.seaman@yahoo.com` and `eric@numista.ai`** (server-side allowlist check). All other callers receive 403. This avoids needing an admin session to switch during Phase A testing.

### 2b. Flutter client (reads the flag, never sets it)

On app startup (after auth), the Flutter app fetches:
```dart
// numista_mobile/lib/services/ui_variant_service.dart  (NEW)
class UiVariantService {
  static String _variant = 'classic';

  static Future<void> load(String userEmail) async {
    final doc = await FirebaseFirestore.instance
        .collection('users').doc(userEmail)
        .collection('settings').doc('ui_variant').get();
    _variant = (doc.data()?['ui_variant'] as String?) ?? 'classic';
  }

  static bool get isSimple => _variant == 'simple';
  static bool get isClassic => _variant == 'classic';
}
```

`UiVariantService.load()` is called once in `AuthGate` after the user token is confirmed. The result is cached in-memory for the session. No SharedPreferences write — the flag is always server-truth.

---

## 3. Hosting / URL (pros and cons)

The order asks for pros/cons. Two options:

### Option X — In-app toggle (single URL: numista-vault.web.app)

Users see the same URL. "Classic/Simple" toggle appears in Settings (Phase C only; Phases A/B controlled by server flag only). The two UIs are different `Widget` trees rendered inside the same Flutter app, selected by `UiVariantService.isSimple`.

**Pros:**
- No new Firebase Hosting config, no DNS changes.
- One build, one deployment.
- Feature flag controls rollout with zero client changes needed.
- Both UIs share exactly the same Firebase Auth session and token — no cross-site cookie or CORS issues.

**Cons:**
- The app bundle contains both UIs even in Phase A. (Mitigated: Simple UI is mostly reused widgets from Classic with different layout tokens.)
- URL does not signal "you're on the Simple site" to the user.

### Option Y — Subdomain (beta.numista.ai)

Separate Firebase Hosting target (`beta`) with a `beta.numista.ai` CNAME. Both targets serve the same Flutter build, but the app detects `window.location.hostname.contains('beta')` and forces `isSimple = true` regardless of flag.

**Pros:**
- URL communicates intent to testers ("beta site").
- Classic and Simple are obviously distinct to the user.

**Cons:**
- Requires DNS change and Firebase Hosting target setup (`firebase.json` hosting array).
- During Phase A, Eric must navigate to a different URL.
- Cross-origin: if auth tokens are scoped to `numista-vault.web.app`, a subdomain requires explicit CORS/auth setup.
- More deployment surface — two targets to keep in sync.

**AG CoS recommendation:** **Option X (in-app toggle)** for Phases A and B. The server flag controls visibility; no URL change needed. Option Y can be considered for Phase C (all users) if Eric wants clear branding separation, but that decision can be deferred.

---

## 4. Proof Both UIs Share the Same API Calls

The order requires listing the shared API calls. Since Simple is a layout variant, not a different product, it calls the same endpoints:

| Action | API endpoint | File:line |
|---|---|---|
| Load collection | `GET /api/coins` (or Firestore direct) | `main.py` (identify in impl) |
| Add coin (Classic) | Morgan: `POST /api/deep_dive` → `POST /api/morgan/confirm` (Gate 0) | `main.py:2715` |
| Add coin (Simple) | Same as above — same confirm card, same endpoint |
| Edit coin | `POST /api/morgan/confirm` (Gate 0) | `morgan_routes.py` (new in Gate 0) |
| Checklist add | `POST /api/checklist/add_coins` | `main.py:7783` |
| Import | `POST /api/upload_document` → `POST /api/review/commit_session` | `scan_routes.py:84, 273` |
| Auth | Firebase ID token, `GET_CURRENT_USER` | `routes/deps.py:64` |
| UI variant flag | `GET users/{email}/settings/ui_variant` (Firestore read) | `UiVariantService.load()` |
| Admin set flag | `POST /api/admin/set_ui_variant` | New in this plan |

No new backend data-path routes. Simple UI does not introduce any endpoint that bypasses REQ_031 auth or Morgan Gate 0 confirms.

---

## 5. Implementation Plan

### Step 1 — Backend: feature flag endpoints
File: `numista_backend/routes/admin_routes.py` (or new `numista_backend/routes/variant_routes.py`)

```python
# POST /api/admin/set_ui_variant
@router.post("/admin/set_ui_variant")
async def set_ui_variant(
    payload: SetUiVariantRequest,
    _user: dict = Depends(require_admin_user),
):
    email = payload.email.strip().lower()
    variant = payload.variant  # "classic" | "simple", validated by enum
    db.collection("users").document(email)\
      .collection("settings").document("ui_variant")\
      .set({"ui_variant": variant}, merge=True)
    return {"status": "ok", "email": email, "variant": variant}

# POST /api/user/set_ui_variant  (Phase A only — eric's emails)
PHASE_A_ALLOWLIST = {"eric.seaman@yahoo.com", "eric@numista.ai"}

@router.post("/user/set_ui_variant")
async def user_set_ui_variant(
    payload: SetUiVariantRequest,
    _user: dict = Depends(get_current_user),
):
    caller_email = (_user.get("email") or "").strip().lower()
    if caller_email not in PHASE_A_ALLOWLIST:
        raise HTTPException(status_code=403, detail="Not available in your phase")
    db.collection("users").document(caller_email)\
      .collection("settings").document("ui_variant")\
      .set({"ui_variant": payload.variant}, merge=True)
    return {"status": "ok", "variant": payload.variant}
```

Pydantic model:
```python
from enum import Enum
class UiVariantEnum(str, Enum):
    classic = "classic"
    simple = "simple"

class SetUiVariantRequest(BaseModel):
    email: Optional[str] = None   # admin endpoint only; user endpoint ignores it
    variant: UiVariantEnum
```

### Step 2 — Flutter: UiVariantService

New file: `numista_mobile/lib/services/ui_variant_service.dart`

```dart
import 'package:cloud_firestore/cloud_firestore.dart';

class UiVariantService extends ChangeNotifier {
  static final UiVariantService instance = UiVariantService._();
  UiVariantService._();

  String _variant = 'classic';

  bool get isSimple  => _variant == 'simple';
  bool get isClassic => _variant == 'classic';
  String get variant => _variant;

  Future<void> load(String userEmail) async {
    try {
      final doc = await FirebaseFirestore.instance
          .collection('users').doc(userEmail)
          .collection('settings').doc('ui_variant').get();
      _variant = (doc.data()?['ui_variant'] as String?) ?? 'classic';
    } catch (_) {
      _variant = 'classic';  // fail safe to classic
    }
    notifyListeners();
  }

  void reset() {
    _variant = 'classic';
    notifyListeners();
  }
}
```

### Step 3 — Flutter: wire into AuthGate

In `numista_mobile/lib/auth_gate.dart` (or equivalent), after `get_current_user` resolves:

```dart
// After token confirmed:
final email = user.email ?? '';
await UiVariantService.instance.load(email);
```

Register `UiVariantService.instance` as a `ChangeNotifierProvider` in `main.dart`.

### Step 4 — Flutter: variant-aware routing

In the main scaffold or routing layer, wrap the layout selection:

```dart
Consumer<UiVariantService>(
  builder: (context, uiVariant, _) {
    if (uiVariant.isSimple) {
      return const SimpleScaffold();   // REQ_032 UX fixes applied
    }
    return const ClassicScaffold();    // current layout, untouched
  },
)
```

`SimpleScaffold` is a new widget tree that uses the REQ_032 UX improvements (6-item nav, big text tokens, 3-choice Add Coin, fixed PIN screen). It calls the same API endpoints as `ClassicScaffold`.

### Step 5 — Phase C: Settings toggle

When Phase C is ready (Eric's YES), add a `ListTile` to Settings:
```
Classic / Simple  [toggle or DropdownButton]
```
The toggle calls `POST /api/user/set_ui_variant` (which by Phase C is open to all users, server allowlist removed). The flag is written server-side; the app reloads `UiVariantService.load()` and re-renders.

---

## 6. Tests Required

### Backend (new file: `numista_backend/tests/test_ui_variant.py`)

```python
# Admin sets variant for any user
def test_admin_set_variant_ok():
    # mock require_admin_user → admin user
    # POST /api/admin/set_ui_variant {email: "user@x.com", variant: "simple"}
    # assert Firestore write to users/user@x.com/settings/ui_variant
    # assert response 200

# Non-admin cannot call admin endpoint
def test_non_admin_set_variant_rejected():
    # mock get_current_user → non-admin
    # POST /api/admin/set_ui_variant
    # assert 403

# Phase A allowlist: eric emails can self-set
def test_eric_can_self_set():
    # mock get_current_user → {email: "eric@numista.ai"}
    # POST /api/user/set_ui_variant {variant: "simple"}
    # assert 200

# Phase A allowlist: other users cannot self-set
def test_non_eric_cannot_self_set():
    # mock get_current_user → {email: "user@example.com"}
    # POST /api/user/set_ui_variant
    # assert 403

# Flag off = classic returned
def test_absent_flag_returns_classic():
    # Firestore returns no ui_variant field
    # assert UiVariantService loads "classic"
```

### Flutter (new file: `numista_mobile/test/ui_variant_service_test.dart`)

```dart
// Flag off (no Firestore doc) → isClassic
test('absent flag defaults to classic', () async { ... });

// Flag "simple" → isSimple
test('simple flag returns isSimple true', () async { ... });

// Same coin visible in both UIs after edit
// (integration test — verify coin document unchanged, UI reads same data)
test('both UIs read same Firestore coin after edit', () async { ... });
```

### Key acceptance tests (from order):
1. **Flag off = no access:** user without `simple` flag sees Classic. ✓ (no UI change)
2. **Both UIs show the same coin after an edit:** edit via Classic → switch flag to Simple → same coin data shown. This is guaranteed by the shared Firestore collection — only a test reading the document directly is needed.

---

## 7. Rollout Phases

| Phase | Who | How flag is set | Trigger |
|---|---|---|---|
| A | `eric.seaman@yahoo.com`, `eric@numista.ai` only | `POST /api/user/set_ui_variant` | Now, on dev |
| B | Beta testers (creation_timestamp < cutoff) | `POST /api/admin/set_ui_variant` per user or batch | After Eric's YES |
| C | All users | Settings toggle → `POST /api/user/set_ui_variant` (allowlist removed) | After Eric's YES |

**Server sets the flag. Users cannot grant themselves access before Phase C.**

---

## 8. Files Changed

| File | Action |
|---|---|
| `numista_backend/routes/variant_routes.py` | CREATE — `set_ui_variant` admin + user endpoints |
| `numista_backend/tests/test_ui_variant.py` | CREATE — backend tests |
| `numista_mobile/lib/services/ui_variant_service.dart` | CREATE — client flag reader |
| `numista_mobile/lib/auth_gate.dart` | UPDATE — call `UiVariantService.load()` after auth |
| `numista_mobile/lib/main.dart` | UPDATE — add ChangeNotifierProvider |
| `numista_mobile/lib/widgets/simple_scaffold.dart` | CREATE — Simple UI layout (skeleton; REQ_032 Fix 2-5 applied here) |
| `numista_mobile/test/ui_variant_service_test.dart` | CREATE — Flutter tests |

---

## 9. Acceptance Criteria

- [ ] `POST /api/admin/set_ui_variant` requires admin token (pytest)
- [ ] `POST /api/user/set_ui_variant` allows only eric's emails in Phase A (pytest)
- [ ] Flutter app in Simple mode calls identical API endpoints as Classic (verified by test)
- [ ] Same coin document visible in both UIs after edit (test)
- [ ] `flutter analyze lib/` — 0 errors
- [ ] Full pytest suite passes (407 clean)
- [ ] Dev only — no deploy without Eric's typed YES
- [ ] REQ_031 hotfix ships before Track 3b builds begin (per order)

---

## 10. Open Questions for Grok CoS

1. Should Phase A self-set (`/api/user/set_ui_variant`) persist after Phase A or be removed at Phase B? Recommendation: keep it for Eric permanently, expand allowlist for Phase C.
2. Should `SimpleScaffold` be a separate Dart file per screen (recommended for clarity) or a widget wrapper that overrides theme tokens globally?
3. Any concern with loading the variant flag from Firestore on every app start (one extra read)? Could cache in `SharedPreferences` with a TTL, but server-truth is safer for flag control.

---

*No code written. Awaiting Gemini review, then Grok CoS score, then Eric's Proceed.*
