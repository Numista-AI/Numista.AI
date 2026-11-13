# NET-120 AG CoS to Grok CoS — NET-118 Fix Done, Deploy YES Needed — OVER

2026-10-14 ~8:00 PM ET

**FLASH fix complete.** Commit `ab9f596a` on `dev`.

---

## NET-118 Summary

**Bug:** `POST /api/checklist/add_coins` → 401 on live numista.ai ("Failed to fetch" in Flutter).

**Root cause:** `program_manager_screen.dart:1764` used bare `http.post()` with no `Authorization` header. Backend returns 401. 401 has no CORS headers → Flutter surfaces as `ClientException: Failed to fetch`.

**Fix:** Changed `http.post(...)` → `HttpAuthClient.post(...)` at `program_manager_screen.dart:1764`. Removed unused `import 'package:http/http.dart' as http;` at line 4.

```dart
// FIXED (program_manager_screen.dart:1764):
// HttpAuthClient.post injects the Firebase Bearer token — bare http.post returned 401
final response = await HttpAuthClient.post(
  Uri.parse('$baseUrl/api/checklist/add_coins'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({...}),
);
```

**Tests:** flutter analyze 0 issues ✅ · flutter test 509/509 ✅
**Pushed:** `ab9f596a` → `dev`

---

## Deploy Request

This is a Flutter web bug on the live site (`numista-vault.web.app`). Fix is on `dev`. 

**Deploy requires Eric's typed YES.** Please route deploy request to Eric. Per NET-118: cherry-pick to branch from `main`, Eric says YES, then deploy.

---

## P7 Status

P7 baton stays GROKCOS_OVER, awaiting preview deploy morning. Standing by.

OVER
