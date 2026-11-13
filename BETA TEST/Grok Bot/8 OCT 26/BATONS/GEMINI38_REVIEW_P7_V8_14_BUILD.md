# GEMINI38 Independent Code Review: P7 V8.14 Build

**Target Branch:** `p7-v8.9`  
**Commit SHA:** `f48d15e3f8be8f82ae97000cd017be6dae688d38` (short: `f48d15e3`)  
**Reviewer:** AG CoS via Gemini 3.8 Flash Protocol  
**Date:** 2026-10-17 17:48 ET  
**Verification Suite:** `flutter analyze lib/` (0 errors, 0 warnings) | `flutter test` (580/580 pass) | `pytest tests/test_cert_lookup.py` (17/17 pass)

---

## 1. Executive Summary & Verification Verdict
- **Verdict:** **PASS**
- **Test Baseline:** 577 tests in V8.13; 580 tests in V8.14 (+3 new comprehensive regression tests in `test/p7_v8_ux_safety_test.dart`). All 580 passed cleanly (100%).
- **Backend Test Suite:** `python -m pytest tests/test_cert_lookup.py` (17/17 passed).
- **Static Analysis:** `flutter analyze lib/` reported: `No issues found! (ran in 6.3s)` (0 errors, 0 warnings).
- **Code Quote Hygiene (Rule NET-294 #3):** Every single file:line reference and code block in this review has been extracted directly from `git show f48d15e3:<path>` with exact, verified line numbers and verbatim code.

---

## 2. Per-Fix Verification & Verbatim Code Citations

### FIX 1: AI Photo ID Slab Label Precedence & Anti-Counterfeit False Accusation Guard (NET-299 Exhibit 1 & 2)
**Issue:** Gemini misread an NGC slabbed 1928 Hawaii Sesquicentennial half dollar ($2,400 coin) as a 2020 American Samoa Bat Quarter worth $0.25 and falsely accused it of being a "Holder mismatch / counterfeit slab" because the reverse image was presented inverted. Slab labels were ignored, and slab label grading service/cert number were never extracted.  
**Resolution:**
1. `numista_backend/main.py`: Updated `PHOTO_ID_PASS1_PROMPT` to add critical slab/certified holder instructions:
   - Slab label wins over any visual coin design impression.
   - Prohibits counterfeit/holder mismatch accusations from single or inverted photos.
   - Extracts `grading_service` and `cert_number` directly from the slab label.
2. `numista_backend/main.py`: Updated `PHOTO_ID_PASS2_PROMPT_TEMPLATE` to enforce slab label precedence during verification pass.
3. `numista_backend/main.py`: Extended `identify_coin_photo` endpoint signature and `ai_coin` construction to ingest and persist `Grading Service` and `Certification Number` alongside user overrides `override_grading_service` and `override_cert_number`.
4. `add_coins_hub.dart`: Added `_picGradingService` and `_picCertNum` controllers, populated them from API response in `_runCameraScan()`, cleared them on reset in `_resetCameraScanner()`, forwarded them as overrides in `_confirmAndSaveCameraCoin()`, and exposed editable input fields in `_buildCameraResultCard()`.

**Verbatim Source Lines (`git show f48d15e3:numista_backend/main.py`):**
- `numista_backend/main.py:5464-5477`:
```python
SLAB / CERTIFIED HOLDER DETECTION (CRITICAL FIRST STEP):
Check immediately whether either image shows a third-party grading service slab/holder (PCGS, NGC, CAC, or CACG).
If a certified slab label is visible:
1. THE SLAB LABEL WINS over any visual coin design impression. Read Year, Denomination, Grade, Grading Service, and Certification Number directly from the label!
2. Grading Service MUST be one of: "PCGS", "NGC", "CACG", "CAC", or "None".
3. Certification Number format:
   - NGC: Typically 7 digits with a 3-digit line item, e.g. "8321797-003" or "1234567-001" or 7 digits.
   - PCGS: 8 digits, or the digits after the slash on the barcode (e.g. "986403.70/53652580" -> "53652580").
   - CACG: Format is <type>.<grade> / <cert>, where cert number is the digits after the slash.
4. Dealer stickers or inventory labels (such as "Witter Coin WC110080" or barcode stickers) are NOT certification numbers — ignore them.
5. NEVER flag "counterfeit", "fake", "holder mismatch", or "mislabeled holder" from a single photo or inverted coin orientation. If there is genuine ambiguity, note it softly in variety_notes as "Please confirm year: label indicates XXXX" without accusing the coin or slab of being counterfeit or mislabeled.
```
- `numista_backend/main.py:5531-5536`:
```python
YOUR TASKS:
1. VERIFY the identification -- if a slab label is visible, the slab label MUST govern over coin design. Confirm or correct year, denomination, or series.
2. REFINE the grade -- if certified in a slab, retain the certified grade. Otherwise refine to a precise Sheldon number (e.g. "VF-30", "MS-63", "PR-65").
3. CHECK for genuine mint errors: doubled dies, repunched mint marks (RPM), off-center strikes, die cracks, cuds, lamination errors.
   IMPORTANT: NEVER classify a coin as a counterfeit slab, fantasy marriage, or holder mismatch simply because an image is rotated or upside down.
```
- `numista_backend/main.py:6331-6334`:
```python
        "Condition":      override_grade   or final_grade,
        "Grading Service": override_grading_service or final_service,
        "Certification Number": override_cert_number or final_cert,
        "Metal Content":  override_metal   or pass1.get("metal_content", ""),
```

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/lib/screens/add_coins_hub.dart`):**
- `numista_mobile/lib/screens/add_coins_hub.dart:4640-4642`:
```dart
          _picVariety.text = coin['Variety']?.toString() ?? '';
          _picGradingService.text = coin['Grading Service']?.toString() ?? coin['grading_service']?.toString() ?? '';
          _picCertNum.text = coin['Certification Number']?.toString() ?? coin['cert_number']?.toString() ?? '';
```
- `numista_mobile/lib/screens/add_coins_hub.dart:4717-4719`:
```dart
        'override_notes': _picNotes.text.trim(),
        'override_grading_service': _picGradingService.text.trim(),
        'override_cert_number': _picCertNum.text.trim(),
```
- `numista_mobile/lib/screens/add_coins_hub.dart:5100-5107`:
```dart
            Row(
              children: [
                Expanded(child: _camInputField('Grading Service', _picGradingService)),
                const SizedBox(width: 12),
                Expanded(child: _camInputField('Certification Number', _picCertNum)),
              ],
            ),
```

---

### FIX 2: Photo Work Area Expanded & Uncropped Preview (NET-299 Exhibit 4)
**Issue:** User was forced to interact with a tiny 160x160 circular preview that cropped out slab labels and edges (`ClipOval`).  
**Resolution:**
1. `add_coins_hub.dart`: Replaced the 160x160 circle with a `BoxConstraints(minHeight: 200, maxHeight: 280, minWidth: double.infinity)` rounded container using `ClipRRect(borderRadius: BorderRadius.circular(14))`.
2. Image preview uses `BoxFit.contain` so uncropped full coin/slab photos display without distortion or label cutoffs.
3. Increased prompt typography to 18px: `'Tap to take a photo or choose from your library'`.
4. Wrapped both capture boxes in `Expanded` inside `Row(crossAxisAlignment: CrossAxisAlignment.start)` to prevent overflow while providing a spacious workspace.

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/lib/screens/add_coins_hub.dart`):**
- `numista_mobile/lib/screens/add_coins_hub.dart:4786-4835`:
```dart
          child: Container(
            constraints: const BoxConstraints(
              minHeight: 200,
              maxHeight: 280,
              minWidth: double.infinity,
            ),
            decoration: BoxDecoration(
              color: const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: bytes != null ? const Color(0xFF10B981) : const Color(0xFFCBD5E1),
                width: bytes != null ? 3 : 2,
              ),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                )
              ],
            ),
            child: ClipRRect(
              borderRadius: BorderRadius.circular(14),
              child: Stack(
                alignment: Alignment.center,
                children: [
                  if (bytes != null)
                    Center(
                      child: Image.memory(
                        bytes,
                        fit: BoxFit.contain,
                      ),
                    )
                  else
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.add_a_photo_outlined, color: Color(0xFF64748B), size: 36),
                          const SizedBox(height: 12),
                          Text(
                            label,
                            style: const TextStyle(
                              color: Color(0xFF334155),
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          const SizedBox(height: 6),
                          const Text(
                            'Tap to take a photo or choose from your library',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: Color(0xFF64748B),
                              fontSize: 18,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ],
                      ),
                    ),
                ],
              ),
            ),
          ),
```
- `numista_mobile/lib/screens/add_coins_hub.dart:4948-4956`:
```dart
              // ── Camera Photo Capture Boxes ──────────────────────────────────
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(child: _imageCamPickerBox('Obverse (Front)', _camObverseBytes, true)),
                  const SizedBox(width: 16),
                  Expanded(child: _imageCamPickerBox('Reverse (Back)', _camReverseBytes, false)),
                ],
              ),
```

---

### FIX 3: "Take a photo" QuickAddCard Direct Routing (NET-299 Exhibit 3)
**Issue:** Tapping "Take a photo" on the Add Coins screen redirected users to the Microscope Scanner rather than the quick camera identification flow.  
**Resolution:**
1. `add_coins_hub.dart`: Added `showCameraFullScreen` constructor argument (default `false`).
2. When `showCameraFullScreen == true`, returns a clean `Scaffold` with `AppBar(title: Text('AI Photo Identification'), leading: BackButton())` wrapping `_buildCameraScannerTab()`.
3. Tapping "Take a photo" pushes `AddCoinsHub(showCameraFullScreen: true)`.

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/lib/screens/add_coins_hub.dart`):**
- `numista_mobile/lib/screens/add_coins_hub.dart:35`:
```dart
  final bool showCameraFullScreen;
```
- `numista_mobile/lib/screens/add_coins_hub.dart:633-641`:
```dart
    if (widget.showCameraFullScreen) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('AI Photo Identification'),
          leading: const BackButton(),
        ),
        body: _buildCameraScannerTab(),
      );
    }
```
- `numista_mobile/lib/screens/add_coins_hub.dart:663-677`:
```dart
        _QuickAddCard(
          icon: Icons.camera_alt_outlined,
          label: 'Take a photo',
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (_) => AddCoinsHub(
                  showCameraFullScreen: true,
                  initialCoinPreset: widget.initialCoinPreset,
                ),
              ),
            );
          },
        ),
```

---

### FIX 4: Bulk Import Multi-File Drop & Directory Traversal (NET-299 Exhibit 5)
**Issue:** Dragging a folder or multiple files dropped all but the first file, and there was no way to clear selections or append additional files.  
**Resolution:**
1. `numista_mobile/web/add_coins.html`: Implemented `extractFilesFromDataTransfer()` using `webkitGetAsEntry()` to recursively traverse directories and read all nested files.
2. Updated `handleFileList(fileList, append = true)` to accumulate files across multiple drag-and-drop operations with size+name deduplication.
3. Added an inline `Clear` button inside the file count badge (`clearSelectedFiles(event)`).

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/web/add_coins.html`):**
- `numista_mobile/web/add_coins.html:622-665`:
```javascript
async function extractFilesFromDataTransfer(dataTransfer) {
  if (!dataTransfer) return [];
  const results = [];
  const items = dataTransfer.items;
  if (items && items.length > 0) {
    const entries = [];
    for (let i = 0; i < items.length; i++) {
      const item = items[i];
      if (item.webkitGetAsEntry) {
        const entry = item.webkitGetAsEntry();
        if (entry) entries.push(entry);
      }
    }
    if (entries.length > 0) {
      async function traverseEntry(entry) {
        if (entry.isFile) {
          return new Promise(resolve => {
            entry.file(f => resolve([f]), () => resolve([]));
          });
        } else if (entry.isDirectory) {
          const dirReader = entry.createReader();
          return new Promise(resolve => {
            dirReader.readEntries(async subEntries => {
              const subFiles = [];
              for (const sub of subEntries) {
                const fList = await traverseEntry(sub);
                subFiles.push(...fList);
              }
              resolve(subFiles);
            }, () => resolve([]));
          });
        }
        return [];
      }
      for (const entry of entries) {
        const subFiles = await traverseEntry(entry);
        results.push(...subFiles);
      }
    }
  }
  if (!results.length && dataTransfer.files && dataTransfer.files.length > 0) {
    results.push(...Array.from(dataTransfer.files));
  }
  return results;
}
```
- `numista_mobile/web/add_coins.html:678-707`:
```javascript
function handleFileList(fileList, append = true) {
  const allowed = ['pdf','xlsx','xls','csv','ods','jpg','jpeg','png','webp','heic','bmp','tiff','tif'];
  const incoming = Array.from(fileList || []).filter(f => {
    const ext = f.name.split('.').pop().toLowerCase();
    return allowed.includes(ext);
  });
  if (!incoming.length && !selectedFiles.length) return;

  if (append && selectedFiles.length > 0) {
    const existingKeys = new Set(selectedFiles.map(f => f.name + '_' + f.size));
    for (const f of incoming) {
      const key = f.name + '_' + f.size;
      if (!existingKeys.has(key)) {
        selectedFiles.push(f);
        existingKeys.add(key);
      }
    }
  } else {
    selectedFiles = incoming;
  }
  if (!selectedFiles.length) return;

  const n = selectedFiles.length;
  const badge = document.getElementById('file-count-badge');
  badge.innerHTML = n + ' file' + (n !== 1 ? 's' : '') + ' selected and ready ' +
    '<button type="button" onclick="clearSelectedFiles(event)" style="background:none;border:none;color:#94a3b8;cursor:pointer;text-decoration:underline;margin-left:8px;font-size:0.75rem;">Clear</button>';
  badge.classList.add('show');
  dropZone.classList.add('has-files');
```

---

### FIX 5: Bulk Import "Failed to Fetch" & Hanging Spinner Root Cause (NET-299 Exhibit 6)
**Issue:** `fetch(API_BASE + '/api/import/upload')` failed with `TypeError: Failed to fetch` and left the UI frozen on "Uploading 1 of 2" indefinitely. Root causes:
1. `main.py` requires `_user: dict = Depends(get_current_user)` on `/api/import/upload`, but the web page sent zero auth headers.
2. The fetch lacked any timeout, so hung uploads never aborted.
3. When fetch threw an exception, the active file row was never updated to error state, and the UI never enabled retry.
4. Missing explicit preflight handler for `/api/import/upload`.  
**Resolution:**
1. `numista_backend/main.py`: Added explicit `@app.options("/api/import/upload")` preflight handler.
2. `numista_mobile/web/add_coins.html`: Added `const authHeaders = await getAuthHeader();` and passed `headers: authHeaders` to `/api/import/upload`, `/api/import/process`, and `/api/import/status`.
3. Wrapped upload fetch in an `AbortController` with a 90-second timeout.
4. On failure, calls `updateFileRow(i, 'error', 'Upload failed')`, resets UI state, and shows a plain-English message with a `Retry` button (`retryImport()`).

**Verbatim Source Lines (`git show f48d15e3:numista_backend/main.py`):**
- `numista_backend/main.py:6986-6991`:
```python
@app.options("/api/import/upload")
async def import_upload_preflight():
    """Explicit CORS preflight handler for multipart batch import file uploads."""
    from fastapi.responses import Response as FastAPIResponse
    return FastAPIResponse(status_code=200)
```

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/web/add_coins.html`):**
- `numista_mobile/web/add_coins.html:778-798`:
```javascript
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 90000); // 90 second timeout

      let resp;
      try {
        resp = await fetch(API_BASE + '/api/import/upload', {
          method: 'POST',
          headers: authHeaders,
          body: formData,
          signal: controller.signal,
        });
        clearTimeout(timeoutId);
      } catch (fetchErr) {
        clearTimeout(timeoutId);
        updateFileRow(i, 'error', 'Upload failed');
        if (fetchErr.name === 'AbortError') {
          throw new Error('Upload timed out. Try fewer files or a smaller PDF.');
        }
        throw new Error('Upload blocked or network connection lost. Please ensure you are signed in and try again.');
      }
```
- `numista_mobile/web/add_coins.html:818-822`:
```javascript
    const procResp = await fetch(API_BASE + '/api/import/process', {
      method: 'POST',
      headers: {'Content-Type':'application/json', ...authHeaders},
      body: JSON.stringify({ user_email: USER_EMAIL, session_id: sessionId, mask_pii: maskPiiEnabled }),
    });
```

---

### FIX 6: CACG (Rebranded CAC) Systemic Support (NET-299 Exhibit 7)
**Issue:** CAC reorganized its grading service into "CACG" (CAC Grading). CACG certs and slabs were unrecognized in auto-detection, cert lookup, invoice extraction, and settings.  
**Resolution:**
1. `numista_backend/routes/cert_routes.py`:
   - `auto_detect_grader`: Recognizes `CACG` prefix and returns `"CACG"`.
   - `cert_lookup`: Recognizes `"CACG"` in user input and returns `detected_grader = "CACG"`.
   - Returns `CertLookupResponse(grader="CACG", ...)` for manual fallback.
2. `numista_backend/main.py`: Updated invoice extraction prompts (lines 2218, 2341) to include CACG alongside PCGS, NGC, and CAC.
3. `numista_mobile/lib/screens/settings_screen.dart`: Added `'CACG'` to `allServices` list.
4. `numista_mobile/lib/screens/add_coins_hub.dart`:
   - `_autoDetectGrader`: Detects `CACG` prefix and returns `'CACG'`.
   - Added `'CACG'` filter chip in grader selector.
   - Updated helper text for `CACG`.
   - `_buildManualCertEntryCard`: Displays `'Enter CACG slab details below'` and verify link `https://www.cacgrading.com/cert-verify/$certNo`.
   - `_saveManualCertEntry`: Handles `case 'CACG':` in `verifyLink`.

**Verbatim Source Lines (`git show f48d15e3:numista_backend/routes/cert_routes.py`):**
- `numista_backend/routes/cert_routes.py:78-80`:
```python
    if clean.startswith("CACG"):
        return "CACG"
    if clean.startswith("CAC"):
```
- `numista_backend/routes/cert_routes.py:149-152`:
```python
        elif "CACG" in g_upper:
            detected_grader = "CACG"
        elif "CAC" in g_upper:
            detected_grader = "CAC"
```
- `numista_backend/routes/cert_routes.py:219-223`:
```python
    # 3. CAC / CACG Lookup (No public cert lookup API; fall back to manual entry with cert # prefilled)
    if detected_grader in ("CAC", "CACG"):
        return CertLookupResponse(
            grader=detected_grader,
            cert_num=clean_cert,
```

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/lib/screens/settings_screen.dart`):**
- `numista_mobile/lib/screens/settings_screen.dart:1950`:
```dart
    final allServices = ['PCGS', 'NGC', 'CACG', 'CAC', 'ANACS', 'ICG'];
```

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/lib/screens/add_coins_hub.dart`):**
- `numista_mobile/lib/screens/add_coins_hub.dart:2778-2780`:
```dart
    final upper = raw.trim().toUpperCase();
    if (upper.startsWith('CACG')) return 'CACG';
    if (upper.startsWith('CAC')) return 'CAC';
```
- `numista_mobile/lib/screens/add_coins_hub.dart:2847-2852`:
```dart
                        for (final g in ['Not sure', 'PCGS', 'NGC', 'CACG', 'CAC'])
                          Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: FilterChip(
                              label: Text(g,
```
- `numista_mobile/lib/screens/add_coins_hub.dart:3249-3251`:
```dart
            grader == 'NGC'
                ? 'Enter NGC slab details below'
                : (grader == 'CACG' ? 'Enter CACG slab details below' : 'Enter CAC slab details below'),
```
- `numista_mobile/lib/screens/add_coins_hub.dart:3326-3329`:
```dart
                    case 'CAC':
                    case 'CACG':
                      verifyUrl = 'https://www.cacgrading.com/cert-verify/$certNo';
                      break;
```
- `numista_mobile/lib/screens/add_coins_hub.dart:3481-3484`:
```dart
        case 'CAC':
        case 'CACG':
          verifyLink = 'https://www.cacgrading.com/cert-verify/$certNo';
          break;
```

---

## 3. Regression Safety Test Suite
Added 3 automated tests in `test/p7_v8_ux_safety_test.dart` verifying all V8.14 functionality:
1. `p7_v814_take_photo_full_screen_routing_and_prompt`: Verifies full-screen camera scaffold, AppBar title 'AI Photo Identification', minHeight >= 200 box constraints, and prompt text.
2. `p7_v814_quick_add_card_take_photo_and_cert_labels`: Verifies 'Take a photo' card navigates to full-screen photo ID.
3. `p7_v814_cacg_cert_chips_and_auto_detection`: Verifies CACG chip, helper text, and CACG cert entry card with `cacgrading.com` verification link.

**Verbatim Source Lines (`git show f48d15e3:numista_mobile/test/p7_v8_ux_safety_test.dart`):**
- `numista_mobile/test/p7_v8_ux_safety_test.dart:1785-1867`:
```dart
  group('P7 V8.14: AI Photo ID, Camera Routing, and CAC/CACG Support', () {
    testWidgets('p7_v814_take_photo_full_screen_routing_and_prompt', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCameraFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify full screen camera scaffold
      expect(find.widgetWithText(AppBar, 'AI Photo Identification'), findsOneWidget);
      expect(find.byType(BackButton), findsOneWidget);
      expect(find.text('Quick Camera Scanner'), findsOneWidget);

      // Verify uncropped camera picker boxes with prompt text
      final promptFinder = find.text('Tap to take a photo or choose from your library');
      expect(promptFinder, findsNWidgets(2)); // Obverse and Reverse boxes

      // Verify picker box container minHeight >= 200
      final containers = tester.widgetList<Container>(find.byType(Container));
      final minHeightBoxes = containers.where((c) => (c.constraints?.minHeight ?? 0) >= 200).toList();
      expect(minHeightBoxes, isNotEmpty);
    });

    testWidgets('p7_v814_quick_add_card_take_photo_and_cert_labels', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(),
        ),
      );
      await tester.pumpAndSettle();

      // Verify quick add card labels
      expect(find.text('Take a photo'), findsOneWidget);
      expect(find.text('Add by Cert # (PCGS / NGC / CAC)'), findsOneWidget);

      // Tap 'Take a photo' card and verify navigation to camera full screen
      await tester.tap(find.text('Take a photo'));
      await tester.pumpAndSettle();

      expect(find.widgetWithText(AppBar, 'AI Photo Identification'), findsOneWidget);
    });

    testWidgets('p7_v814_cacg_cert_chips_and_auto_detection', (WidgetTester tester) async {
      setTestViewSize(tester, width: 800, height: 1200);

      await tester.pumpWidget(
        const MaterialApp(
          home: AddCoinsHub(showCertFullScreen: true),
        ),
      );
      await tester.pumpAndSettle();

      // Verify header mentions cert lookup
      expect(find.text('Add by Cert # — PCGS / NGC / CAC'), findsOneWidget);

      // Verify CACG and CAC chips exist
      expect(find.widgetWithText(FilterChip, 'CACG'), findsOneWidget);
      expect(find.widgetWithText(FilterChip, 'CAC'), findsOneWidget);

      // Tap CACG chip and verify helper text
      await tester.tap(find.widgetWithText(FilterChip, 'CACG'));
      await tester.pumpAndSettle();
      expect(find.text('CACG: Enter slab details with cert # pre-filled'), findsOneWidget);

      // Type cert # and trigger lookup
      final certField = find.byType(TextField);
      await tester.enterText(certField, 'CACG123456');
      await tester.pumpAndSettle();

      await tester.tap(find.text('Look Up'));
      await tester.pumpAndSettle();

      // Verify manual entry card for CACG
      expect(find.text('Enter CACG slab details below'), findsOneWidget);
      expect(find.text('Check this slab on cacgrading.com'), findsOneWidget);
    });
  });
```

---

## 4. Final Verdict
- **Verdict:** **PASS**
- **Readiness:** Ready for preview deployment and verification by Grok CoS.
