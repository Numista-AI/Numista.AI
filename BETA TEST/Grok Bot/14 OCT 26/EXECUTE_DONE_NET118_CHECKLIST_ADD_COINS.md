# EXECUTE_DONE — NET-118: checklist/add_coins Missing Bearer Token

**Commit:** `ab9f596a`
**Branch:** `dev`
**Pushed:** 2026-10-14 ~8:00 PM ET
**Engineer:** Antigravity / Gemini 3.8

---

## Cloud Run Log Evidence (verbatim from NET-118 Grok CoS report)

```
OPTIONS /api/checklist/add_coins → 200 OK
POST /api/checklist/add_coins → 401 Unauthorized
```

CORS middleware returns 401 with no CORS headers → Flutter's `http` surfaces as `ClientException: Failed to fetch`.

---

## Root Cause

`program_manager_screen.dart:1764` used **bare `http.post()`** with no `Authorization` header:

```dart
// BEFORE (broken):
final response = await http.post(
  Uri.parse('$baseUrl/api/checklist/add_coins'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({...}),
);
```

Every other authenticated route in the codebase uses `HttpAuthClient.post` / `HttpAuthClient.get`, which injects the Firebase Bearer token. The `/api/checklist/add_coins` backend route requires authentication; a bare POST has no token, so backend returns 401. Since 401 responses lack CORS headers, Flutter's HTTP client reports "Failed to fetch" instead of exposing the 401 directly.

---

## Fix Applied

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`

**Line 4 (import removed — unused after fix):**
```dart
// REMOVED:
import 'package:http/http.dart' as http;
```

**Line 4 (import added):**
```dart
// ADDED:
import '../services/http_auth_client.dart';
```

**Line 1764 (call changed):**
```dart
// BEFORE:
final response = await http.post(
// AFTER:
// HttpAuthClient.post injects the Firebase Bearer token — bare http.post returned 401
final response = await HttpAuthClient.post(
```

All other add-coin paths in `add_coins_hub.dart` already use `HttpAuthClient` correctly — only this one route was bare.

---

## Test Results

- **flutter analyze:** 0 issues ✅
- **flutter test:** 509/509 ✅

---

## Deploy Note

This is a Flutter web bug affecting the live site (`numista-vault.web.app`). Fix is on `dev` only.

**Deploy requires Eric's typed YES.** Per NET-118 orders: cherry-pick to a branch from `main`, Eric says YES, then deploy. Grok CoS to communicate deploy need to Eric.

---

## Next: NET-120 filed → Grok CoS
