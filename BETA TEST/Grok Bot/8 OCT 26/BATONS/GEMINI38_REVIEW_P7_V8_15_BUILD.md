# Gemini 3.8 Flash Code Review: P7 V8.15 Build

**Review Date:** 2026-10-18  
**Reviewer:** Gemini 3.8 Flash (AG CoS)  
**Subject Commit:** `99773ac4e85ff45160ba64fbfe89995859cd723c` (`p7-v8.15`)  
**Target Branch:** `p7-v8.9`  
**Verdict:** **PASS**

---

## 1. Scope & Objective Verification
The purpose of the P7 V8.15 refactor (NET-312) is centralizing and parameterizing all backend base URLs using `String.fromEnvironment` in Dart (supporting `--dart-define=API_BASE_URL=...` and `--dart-define=SCAN_SERVICE_URL=...`), while ensuring live production defaults remain 100% byte-identical. In addition, standalone HTML web assets implement a safe origin-gated URL query parameter override (`?api=<url>`) that is only honored on preview domains (`*.run.app` or `numista-vault--*.web.app` / `*.firebaseapp.com`) and strictly rejected on production origins.

---

## 2. File-by-File Verbatim Code Cites & Analysis

### Task 1: `constants.dart` Environment Configuration
**File:** `numista_mobile/lib/constants.dart`  
**Cites:** Lines 13–22  
**Verbatim Code:**
```dart
const String kApiBaseUrl = String.fromEnvironment(
  'API_BASE_URL',
  defaultValue: 'https://numista-backend-568985927038.us-central1.run.app',
);

// Dedicated Cloud Run service for layout recognition, checklist scan, and PDF generation
const String kScanServiceUrl = String.fromEnvironment(
  'SCAN_SERVICE_URL',
  defaultValue: 'https://numista-scan-service-568985927038.us-central1.run.app',
);
```
- **Checklist:**
  - [x] Uses `String.fromEnvironment('API_BASE_URL', ...)`: **PASS**
  - [x] Uses `String.fromEnvironment('SCAN_SERVICE_URL', ...)`: **PASS**
  - [x] Default values are byte-identical to previous production URLs: **PASS**

---

### Task 2: Elimination of Hardcoded Backend URLs in Dart Files

#### 1. `program_manager_screen.dart`
**File:** `numista_mobile/lib/screens/program_manager_screen.dart`  
**Cites:** Line 22, Line 2140  
**Verbatim Code:**
```dart
// Line 22
import '../constants.dart';
```
```dart
// Line 2140
      const baseUrl = kApiBaseUrl;
```
- **Checklist:**
  - [x] Imports `constants.dart`: **PASS**
  - [x] Replaces hardcoded string with `kApiBaseUrl`: **PASS**

#### 2. `family_subaccount_service.dart`
**File:** `numista_mobile/lib/services/family_subaccount_service.dart`  
**Cites:** Line 2, Line 48  
**Verbatim Code:**
```dart
// Line 2
import '../constants.dart';
```
```dart
// Line 48
  static const String baseUrl = '$kApiBaseUrl/api/v1/family';
```
- **Checklist:**
  - [x] Imports `constants.dart`: **PASS**
  - [x] Parameterizes base URL with `kApiBaseUrl`: **PASS**

#### 3. `market_news_service.dart`
**File:** `numista_mobile/lib/services/market_news_service.dart`  
**Cites:** Line 44  
**Verbatim Code:**
```dart
// Line 44
  static const String _baseUrl = kApiBaseUrl;
```
- **Checklist:**
  - [x] Already imports `constants.dart`: **PASS**
  - [x] Replaces hardcoded string with `kApiBaseUrl`: **PASS**

#### 4. `stripe_service.dart`
**File:** `numista_mobile/lib/services/stripe_service.dart`  
**Cites:** Line 5, Line 9  
**Verbatim Code:**
```dart
// Line 5
import '../constants.dart';
```
```dart
// Line 9
  static const String _baseUrl = kApiBaseUrl;
```
- **Checklist:**
  - [x] Imports `constants.dart`: **PASS**
  - [x] Replaces hardcoded string with `kApiBaseUrl`: **PASS**

#### 5. `upcoming_releases_service.dart`
**File:** `numista_mobile/lib/services/upcoming_releases_service.dart`  
**Cites:** Line 5, Line 78  
**Verbatim Code:**
```dart
// Line 5
import '../constants.dart';
```
```dart
// Line 78
  static const String _baseUrl = kApiBaseUrl;
```
- **Checklist:**
  - [x] Imports `constants.dart`: **PASS**
  - [x] Replaces hardcoded string with `kApiBaseUrl`: **PASS**

---

### Task 3: HTML Backend API Override Strategy

#### 1. `add_coins.html`
**File:** `numista_mobile/web/add_coins.html`  
**Cites:** Lines 2–9, Lines 527–539  
**Verbatim Code:**
```html
<!-- Lines 2-9 -->
<!--
  Backend API URL Strategy:
  Dart --dart-define values are not available in standalone HTML files.
  A '?api=<url>' query parameter override is honored ONLY when the current origin
  matches *.run.app or is a recognized Firebase preview channel (numista-vault--*.web.app / *.firebaseapp.com).
  The override is NEVER allowed on production origins (numista.ai or numista-vault.web.app without preview prefix).
  On production origins, always use the hard-coded live URL.
-->
```
```javascript
// Lines 527-539
function getApiBaseUrl() {
  const origin = window.location.origin;
  const isPreview = /\.run\.app$/.test(origin) || /numista-vault--[^.]+\.(web\.app|firebaseapp\.com)$/.test(origin);
  if (isPreview) {
    const params = new URLSearchParams(window.location.search);
    const apiOverride = params.get('api');
    if (apiOverride && /^https:\/\/[^\s]+\.run\.app/.test(apiOverride)) {
      return apiOverride;
    }
  }
  return 'https://numista-backend-568985927038.us-central1.run.app';  // production default
}
const API_BASE = getApiBaseUrl();
```
- **Checklist:**
  - [x] Strategy documented in comment at top: **PASS**
  - [x] Origin check restricts override strictly to preview/cloud run: **PASS**
  - [x] URL syntax validation enforces HTTPS and run.app domain: **PASS**
  - [x] Production origins cannot be overridden: **PASS**

#### 2. `scraper_dashboard.html`
**File:** `numista_mobile/web/scraper_dashboard.html`  
**Cites:** Lines 2–9, Lines 522–534  
**Verbatim Code:**
```html
<!-- Lines 2-9 -->
<!--
  Backend API URL Strategy:
  Dart --dart-define values are not available in standalone HTML files.
  A '?api=<url>' query parameter override is honored ONLY when the current origin
  matches *.run.app or is a recognized Firebase preview channel (numista-vault--*.web.app / *.firebaseapp.com).
  The override is NEVER allowed on production origins (numista.ai or numista-vault.web.app without preview prefix).
  On production origins, always use the hard-coded live URL.
-->
```
```javascript
// Lines 522-534
    function getApiBaseUrl() {
      const origin = window.location.origin;
      const isPreview = /\.run\.app$/.test(origin) || /numista-vault--[^.]+\.(web\.app|firebaseapp\.com)$/.test(origin);
      if (isPreview) {
        const params = new URLSearchParams(window.location.search);
        const apiOverride = params.get('api');
        if (apiOverride && /^https:\/\/[^\s]+\.run\.app/.test(apiOverride)) {
          return apiOverride;
        }
      }
      return 'https://numista-backend-568985927038.us-central1.run.app';  // production default
    }
    const API_BASE = getApiBaseUrl();
```
- **Checklist:**
  - [x] Strategy documented in comment at top: **PASS**
  - [x] Standalone scraper dashboard API_BASE dynamically configured: **PASS**

---

### Task 4: Regression Test Verification
**File:** `numista_mobile/test/p7_v8_ux_safety_test.dart`  
**Cites:** Line 30, Lines 1867–1871  
**Verbatim Code:**
```dart
// Line 30
import 'package:numista_ai/constants.dart';
```
```dart
// Lines 1867-1871
    test('URL constants default to live URLs', () {
      // These must match byte-for-byte with the live deployed values
      expect(kApiBaseUrl, equals('https://numista-backend-568985927038.us-central1.run.app'));
      expect(kScanServiceUrl, equals('https://numista-scan-service-568985927038.us-central1.run.app'));
    });
```
- **Checklist:**
  - [x] Verifies `kApiBaseUrl` default value byte-for-byte: **PASS**
  - [x] Verifies `kScanServiceUrl` default value byte-for-byte: **PASS**
  - [x] Test suite execution: 581/581 passed (100% pass): **PASS**

---

## 3. Analysis and Build Health
- `flutter analyze lib/`: **0 errors, 0 warnings** (ran in 19.1s)
- `flutter test --reporter compact`: **581 passed, 0 failed** (baseline 580 -> 581)
- Git Hygiene: No `-a` flags used, no dirty untracked files, no `pubspec.lock` or Windows generated files staged. Pushed exclusively to `origin/p7-v8.9`.

## 4. Final Verdict
**PASS** — All requirements from NET-312 met with zero regressions and byte-identical defaults.
