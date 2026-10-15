# GEMINI38_REVIEW — P7 V8.3 Build
**Reviewer:** AG CoS (Gemini 3.8)
**Date:** 2026-10-15
**Scope:** V8.3 UX Gate 8-item fix build
**Branch:** dev
**Files modified:** program_manager_screen.dart, add_coins_hub.dart, login_screen.dart, upcoming_releases_service.dart, home_dashboard.dart, estate_planning_screen.dart

---

## Item 1 — Phone checklist: coin name overflow (`program_manager_screen.dart`)

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`
**Lines checked:** 1288–1300

**BEFORE (verbatim):**
```dart
                          if (coin.name.isNotEmpty && coin.name != (coin.year ?? ''))
                            ConstrainedBox(
                              constraints: const BoxConstraints(maxWidth: 180),
                              child: Text(
                                coin.name,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF1E293B),
                                ),
                              ),
                            ),
```

**AFTER (verbatim):**
```dart
                          if (coin.name.isNotEmpty && coin.name != (coin.year ?? ''))
                            Flexible(
                              child: Text(
                                coin.name,
                                overflow: TextOverflow.ellipsis,
                                style: const TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: Color(0xFF1E293B),
                                ),
                              ),
                            ),
```

**Verdict:** PASS — `ConstrainedBox(maxWidth:180)` hard-clipped the name on narrow phones. `Flexible` lets it take remaining Row space; ellipsis handles overflow gracefully.

---

## Item 2 — "Advances overall record" text overflow (`program_manager_screen.dart`)

**File:** `numista_mobile/lib/screens/program_manager_screen.dart`
**Lines checked:** 769–772

**BEFORE (verbatim):**
```dart
          Text(
            'Advances overall record by ${programOverallAdvancement.toStringAsFixed(2)}%',
            style: const TextStyle(fontSize: 10, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
          ),
```

**AFTER (verbatim):**
```dart
          Text(
            'Advances overall record by ${programOverallAdvancement.toStringAsFixed(2)}%',
            style: const TextStyle(fontSize: 10, color: Color(0xFF64748B), fontWeight: FontWeight.w500),
            softWrap: true,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
```

**Verdict:** PASS — prevents render overflow on narrow program cards. GridView already uses `crossAxisCount: isNarrow ? 1 : 3` and `childAspectRatio: isNarrow ? 2.6 : 1.4` (lines 473/476/605/608) — no aspect ratio change needed.

---

## Item 3 — Numeric keyboards (`add_coins_hub.dart`)

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`

### 3a — `flutter/services` import added (lines 1–4)

**BEFORE (verbatim):**
```dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
```

**AFTER (verbatim):**
```dart
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
```

### 3b — `_certManualField` helper: added `keyboardType` + `inputFormatters` params (~line 3239)

**BEFORE (verbatim):**
```dart
  Widget _certManualField(String label, TextEditingController ctrl,
      {String? hint, bool readOnly = false, int maxLines = 1}) {
    ...
        controller: ctrl,
        readOnly: readOnly,
        maxLines: maxLines,
```

**AFTER (verbatim):**
```dart
  Widget _certManualField(String label, TextEditingController ctrl,
      {String? hint, bool readOnly = false, int maxLines = 1,
       TextInputType? keyboardType, List<TextInputFormatter>? inputFormatters}) {
    ...
        controller: ctrl,
        readOnly: readOnly,
        maxLines: maxLines,
        keyboardType: keyboardType,
        inputFormatters: inputFormatters,
```

### 3c — Cert Year call site (~line 3132)

**BEFORE (verbatim):**
```dart
          Expanded(child: _certManualField('Year', _certManualYear, hint: 'e.g. 1921')),
```

**AFTER (verbatim):**
```dart
          Expanded(child: _certManualField('Year', _certManualYear, hint: 'e.g. 1921',
              keyboardType: TextInputType.number,
              inputFormatters: [FilteringTextInputFormatter.digitsOnly])),
```

### 3d — `_camInputField` helper: added `keyboardType` + `inputFormatters` params (~line 4961)

**BEFORE (verbatim):**
```dart
  Widget _camInputField(String label, TextEditingController ctrl, {int maxLines = 1}) {
    ...
        controller: ctrl,
        maxLines: maxLines,
```

**AFTER (verbatim):**
```dart
  Widget _camInputField(String label, TextEditingController ctrl,
      {int maxLines = 1, TextInputType? keyboardType, List<TextInputFormatter>? inputFormatters}) {
    ...
        controller: ctrl,
        maxLines: maxLines,
        keyboardType: keyboardType,
        inputFormatters: inputFormatters,
```

### 3e — Cam Year call site (~line 4906)

**BEFORE (verbatim):**
```dart
            _camInputField('Year', _picYear),
```

**AFTER (verbatim):**
```dart
            _camInputField('Year', _picYear,
                keyboardType: TextInputType.number,
                inputFormatters: [FilteringTextInputFormatter.digitsOnly]),
```

**Verdict:** PASS — year fields now show numeric keypad on mobile. `FilteringTextInputFormatter.digitsOnly` blocks alpha input. Pre-existing: `_mintSetCostCtrl` at line 1635 already had `keyboardType: TextInputType.number`; purchase cost dialog at line 2521 already had numeric keyboard — no changes needed there.

---

## Item 4 — More ways > Manual Entry tab opens full-screen (`add_coins_hub.dart`)

**File:** `numista_mobile/lib/screens/add_coins_hub.dart`
**Lines checked:** TabBarView children (~line 686–696)

**BEFORE (verbatim):**
```dart
                // ITEM 9: Tab order matches priority: upload → camera → manual → cert → sku → roll → world → set
                _buildUploadFilesTab(),
                _buildCameraScannerTab(),
                _buildManualEntryTab(),
                _buildCertLookupTab(),   // P7 FIX: unified PCGS/NGC/CAC tab (was _buildPcgsImportTab)
```

**AFTER (verbatim — key lines):**
```dart
                _buildUploadFilesTab(),
                _buildCameraScannerTab(),
                Builder(
                  builder: (ctx) => GestureDetector(
                    behavior: HitTestBehavior.opaque,
                    onTap: () => Navigator.push(
                      ctx,
                      MaterialPageRoute(
                        builder: (_) => AddCoinsHub(
                          showManualFullScreen: true,
                          initialCoinPreset: widget.initialCoinPreset,
                        ),
                      ),
                    ),
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(32),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.keyboard_outlined, size: 48, color: Color(0xFF64748B)),
                            const SizedBox(height: 16),
                            const Text('Type it in', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xFF1E293B))),
                            const SizedBox(height: 8),
                            const Text('Open the manual entry form to enter full details for your coin.', textAlign: TextAlign.center, style: TextStyle(fontSize: 14, color: Color(0xFF64748B))),
                            const SizedBox(height: 24),
                            ElevatedButton.icon(
                              onPressed: () => Navigator.push(ctx, MaterialPageRoute(builder: (_) => AddCoinsHub(showManualFullScreen: true, initialCoinPreset: widget.initialCoinPreset))),
                              icon: const Icon(Icons.open_in_new, size: 16),
                              label: const Text('Open Manual Entry'),
                              style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF3B82F6), foregroundColor: Colors.white, ...),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ),
                _buildCertLookupTab(),
```

**Verdict:** PASS — Manual Entry tab now shows a CTA card navigating to `AddCoinsHub(showManualFullScreen: true)`, matching Grok CoS condition. The `'Type it in'` quick-add card at lines 647–657 already navigated full-screen — this makes the More Ways tab consistent.

---

## Item 5 — Firestore aggregation guard when unauthenticated

### 5a — `program_manager_screen.dart` (~line 294)

**BEFORE (verbatim):**
```dart
  Future<void> _loadTotalReferenceCount() async {
    try {
```

**AFTER (verbatim):**
```dart
  Future<void> _loadTotalReferenceCount() async {
    if (FirebaseAuth.instance.currentUser == null) return;
    try {
```

### 5b — `estate_planning_screen.dart` (~line 1671)

**BEFORE (verbatim):**
```dart
  Future<void> _loadCoinCount() async {
    try {
```

**AFTER (verbatim):**
```dart
  Future<void> _loadCoinCount() async {
    if (widget.uid.isEmpty) return;
    try {
```

**Verdict:** PASS — guards prevent unauthenticated `.count()` Firestore calls that throw permission-denied in demo mode. Estate planning uses `widget.uid` (not Firebase auth) so uid-empty check is the correct guard there.

---

## Item 6 — Login double scroll (`login_screen.dart`)

**File:** `numista_mobile/lib/screens/login_screen.dart`

### `_buildSignInTab` BEFORE (verbatim):
```dart
  Widget _buildSignInTab() {
    return SingleChildScrollView(
      child: AutofillGroup(
        child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
```

### `_buildSignInTab` AFTER (verbatim):
```dart
  Widget _buildSignInTab() {
    return AutofillGroup(
      child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
```

### `_buildCreateTab` BEFORE (verbatim):
```dart
  Widget _buildCreateTab() {
    return SingleChildScrollView(
      child: AutofillGroup(
        child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
```

### `_buildCreateTab` AFTER (verbatim):
```dart
  Widget _buildCreateTab() {
    return AutofillGroup(
      child: Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
```

**Verdict:** PASS — outer `SingleChildScrollView` at line 268 handles all scrolling. `TabBarView` already has `physics: const NeverScrollableScrollPhysics()` at line 491 — no nested scroll conflict possible. Inner wrappers caused the double-scrollbar; removing them resolves it.

---

## Item 7 — Mint-releases retry spam

### 7a — `upcoming_releases_service.dart` BEFORE (verbatim):
```dart
class UpcomingReleasesService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';
  static const String _cacheKey = 'upcoming_releases_cache';

  static Future<List<UpcomingRelease>> _fetchData(String endpoint) async {
    try {
```

### 7a — AFTER (verbatim):
```dart
class UpcomingReleasesService {
  static const String _baseUrl = 'https://numista-backend-568985927038.us-central1.run.app';
  static const String _cacheKey = 'upcoming_releases_cache';

  // Guard: only attempt a network fetch once per app session.
  // Subsequent calls return from cache directly to avoid repeated server spam.
  static bool _fetchAttempted = false;

  static Future<List<UpcomingRelease>> _fetchData(String endpoint) async {
    if (_fetchAttempted) return _loadCachedReleases();
    _fetchAttempted = true;
    try {
```

### 7b — `home_dashboard.dart` field + initState BEFORE (verbatim):
```dart
  BatchValuationProgress _valuation = const BatchValuationProgress();
  StreamSubscription<BatchValuationProgress>? _valuationSub;

  @override
  void initState() {
    super.initState();
    _fetchSpotPrices();
```

### 7b — AFTER (verbatim):
```dart
  BatchValuationProgress _valuation = const BatchValuationProgress();
  StreamSubscription<BatchValuationProgress>? _valuationSub;

  // ── Upcoming Mint Releases future (stable — created once in initState) ──
  late final Future<List<UpcomingRelease>> _upcomingFuture;

  @override
  void initState() {
    super.initState();
    _upcomingFuture = UpcomingReleasesService.fetchUpcoming();
    _fetchSpotPrices();
```

### 7c — FutureBuilder call site BEFORE (verbatim):
```dart
                  FutureBuilder<List<UpcomingRelease>>(
                    future: UpcomingReleasesService.fetchUpcoming(),
```

### 7c — AFTER (verbatim):
```dart
                  FutureBuilder<List<UpcomingRelease>>(
                    future: _upcomingFuture,
```

**Verdict:** PASS — `_fetchAttempted` prevents repeated server hits. `_upcomingFuture` stored in state avoids FutureBuilder restarting on every `setState`. This is the canonical Flutter pattern for stable async data in `FutureBuilder`.

---

## Item 8 — Demo guard wording (`program_manager_screen.dart`)

**Lines checked:** 1764, 1820 (both occurrences confirmed by grep)

**BEFORE (verbatim — both occurrences):**
```dart
            content: Text('Browse Demo Mode: Sign in to save coins to your collection.'),
```

**AFTER (verbatim — both occurrences):**
```dart
            content: Text('Browse Demo Mode: Create a free account to save coins to your collection.'),
```

**Grep verification:** `Select-String` confirmed exactly 2 occurrences existed; both replaced in a single `AllowMultiple: true` edit.

**Verdict:** PASS — wording now matches onboarding CTA language. "Sign in" implied existing account; "Create a free account" is correct for a demo user.

---

## Build Verification

| Check | Result |
|---|---|
| `flutter analyze` | **No issues found** (0 errors, 0 warnings, ran in 336.2s) |
| `flutter test test/p7_v8_ux_safety_test.dart` | **8/8 PASS** |
| Files modified | 6 |
| Items fixed | 8 of 8 |

**Overall verdict: PASS — ready for Grok CoS build score.**
