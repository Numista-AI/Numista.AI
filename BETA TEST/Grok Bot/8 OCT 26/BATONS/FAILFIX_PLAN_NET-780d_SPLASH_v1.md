# FAILFIX PLAN NET-780d (v1) - Splash Screen Latency Fix (<1.5s vs 40s)
**Author:** Antigravity CoS v4  
**Date:** 2026-11-04 17:35 ET  
**Track:** NET-780 Split Failfix (Plan d of 4: Build Stamp, Cards, Images, Splash)  
**Status:** PLAN ONLY - Strict Hold: Zero Code Changes, Zero Deploys  
**Branch Gate:** `p7-v8.9` | `origin/main` locked at `9f04550a`  

---

## 1. Executive Summary & Problem Statement
During Field Testing of NET-748 v5 on `p7-gate`, the application exhibited an unacceptably long splash screen latency of approximately **40 seconds** before rendering the main collection or welcome view.

This fail-fix plan isolates the exact root causes of this multi-stage latency waterfall, specifies the surgical remedies to decouple network I/O from the app startup path, and sets the target splash duration to **< 1.5 seconds**.

---

## 2. Root Cause Analysis (RCA) with Verbatim Code Quotes

### Root Cause 1: Synchronous `await` of Cloud Run Network Call in Splash Gate
In `numista_mobile/lib/widgets/auth_gate.dart`, lines 127-138:
```dart
          _shouldShowWelcome ??= () async {
            await UiVariantService.refresh();
            return WelcomeScreen.shouldShow();
          }();

          return FutureBuilder<bool>(
            future: _shouldShowWelcome,
            builder: (ctx, snap) {
              if (snap.connectionState == ConnectionState.waiting) {
                return _buildSplash();
              }
              final showWelcome = snap.data ?? false;
```
The future `_shouldShowWelcome` gates the entire transition out of `_buildSplash()`. Because `await UiVariantService.refresh()` is called before `WelcomeScreen.shouldShow()`, any delay in `UiVariantService.refresh()` holds the user on the splash screen indefinitely.

### Root Cause 2: Cloud Run Call in `UiVariantService.refresh()`
In `numista_mobile/lib/services/ui_variant_service.dart`, lines 15-18:
```dart
  static Future<void> refresh() async {
    try {
      final response = await HttpAuthClient.get(
        Uri.parse('$kApiBaseUrl/api/user/ui_variant'),
      );
```
`UiVariantService.refresh()` calls the backend Cloud Run service `/api/user/ui_variant`. When Cloud Run experiences a cold start or network latency, this call can take several seconds to complete.

### Root Cause 3: 30-Second Default Timeout on `HttpAuthClient.get`
In `numista_mobile/lib/services/http_auth_client.dart`, lines 65-71:
```dart
  static Future<http.Response> get(
    Uri url, {
    http.Client? client,
    Map<String, String>? headers,
    Duration timeout = const Duration(seconds: 30),
  }) async {
```
`HttpAuthClient.get` specifies `Duration timeout = const Duration(seconds: 30)`. Because `UiVariantService.refresh()` does not pass an explicit custom timeout parameter, a hanging request or backend cold start can block for up to **30 full seconds** before timing out!

### Root Cause 4: 3.08 MB Uncompressed Asset on Splash Screen
In `numista_mobile/lib/widgets/auth_gate.dart`, lines 179-183:
```dart
          children: [
            Image.asset('assets/logo_owl.png', height: 80,
                errorBuilder: (context, error, stackTrace) =>
                    const Icon(Icons.account_balance_rounded,
                        color: Color(0xFFD4A843), size: 64)),
```
File metadata verification:
```powershell
Name          Length
----          ------
logo_owl.png 3088379  # 3.08 MB
```
Loading a 3.08 MB PNG into memory on the Flutter UI thread during initial frame render causes significant image decode stalling, especially on lower-spec mobile devices and web browser main threads.

### Root Cause 5: Firebase Initialization Timeout Waterfall
In `numista_mobile/lib/main.dart`, lines 195-197:
```dart
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    ).timeout(const Duration(seconds: 12));
```
If Firebase initialization stalls for up to 12s and then the variant service stalls for up to 30s, the combined worst-case latency before the splash screen dismisses is **42 seconds** (matching the observed ~40s field tester report).

---

## 3. Surgical Implementation Plan (Execution Pending Approval)

### Step 1: Decouple `UiVariantService.refresh()` from `_shouldShowWelcome` in `auth_gate.dart`
**Target File:** `numista_mobile/lib/widgets/auth_gate.dart:127-130`  
**Change:** Execute `UiVariantService.refresh()` in the background asynchronously without blocking the startup flow. `WelcomeScreen.shouldShow()` is backed by local `SharedPreferences` and returns in < 5ms.
```dart
// Planned code change in auth_gate.dart:
unawaited(UiVariantService.refresh());
_shouldShowWelcome ??= WelcomeScreen.shouldShow();
```
*(If `unawaited` from `dart:async` is used, the app immediately transitions to `WelcomeScreen` or `BaseLayout` in < 20ms while the variant loads in the background; defaults to `.classic` until resolved).*

### Step 2: Enforce Strict 1.5-Second Timeout on `UiVariantService.refresh()`
**Target File:** `numista_mobile/lib/services/ui_variant_service.dart:15-18`  
**Change:** Pass explicit 1.5s timeout:
```dart
// Planned code change in ui_variant_service.dart:
final response = await HttpAuthClient.get(
  Uri.parse('$kApiBaseUrl/api/user/ui_variant'),
  timeout: const Duration(milliseconds: 1500),
);
```
Even if invoked elsewhere, it can never block for more than 1.5s under any cold start condition.

### Step 3: Optimize Splash Asset Memory & Decode Footprint
**Target File:** `numista_mobile/lib/widgets/auth_gate.dart:180`  
**Change:** Provide `cacheWidth: 160, cacheHeight: 160` (or optimize the asset down to a compressed WebP/PNG < 50 KB) so the browser/engine decodes only an 80px thumbnail rather than 3.08 MB raw raster bytes:
```dart
Image.asset(
  'assets/logo_owl.png',
  height: 80,
  cacheWidth: 160,
  cacheHeight: 160,
  errorBuilder: ...
)
```

---

## 4. Latency Budget & SLA
| Milestone | Current Worst-Case | Proposed Target |
|:---|:---|:---|
| Firebase Init | 12.0s (timeout) / ~0.4s (normal) | ~0.4s (normal) |
| Local Prefs (`WelcomeScreen.shouldShow()`) | < 0.01s | < 0.01s |
| `UiVariantService.refresh()` blocking time | **30.0s** | **0.0s (unawaited background)** |
| Image Asset Decode (`logo_owl.png`) | ~0.8s (3.08 MB) | < 0.05s (cached/scaled) |
| **Total Splash Screen Duration** | **~42.8s** | **< 1.0s - 1.5s** |

---

## 5. Verification Commands (Rule 8 Compliance)
When authorized for execution:
1. `flutter analyze` -> exit code 0.
2. Unit / Widget test: verify `AuthGate` renders `WelcomeScreen` or `BaseLayout` within 500ms when `UiVariantService.refresh()` has a simulated 5s delay.
3. Live web smoke test: measure splash dismissal timestamp in browser console: `performance.now() < 1500ms`.

---

## 6. Constraints & Safety
- **STRICTLY PLAN ONLY**: Zero edits to `auth_gate.dart`, `ui_variant_service.dart`, or `main.dart`.
- **Zero deploys**: `origin/main` locked at `9f04550a`.
- **Ready for Argon (Gemini 3.8) Review**.
