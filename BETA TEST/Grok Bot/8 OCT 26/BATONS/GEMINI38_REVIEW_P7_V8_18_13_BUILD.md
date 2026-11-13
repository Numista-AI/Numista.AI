# GEMINI 3.8 BUILD REVIEW: P7 V8.18.13 (commit a4a77e4c)

**Reviewer:** AG CoS (Gemini 3.8 Flash)  
**Date:** 2026-10-20 ~21:05 ET  
**Commit Inspected:** `a4a77e4c959514e3e8a2308637d169210d7bc88b` on branch `p7-v8.9`  
**Parent Commit:** `68c03e454a012ec78b7785caed621e4d9fdf78a5`  
**Target Track:** P7 Add Coins Flow V8.18.13 (NET-393 / UX Gate V5 Fixes)  
**Review Standard:** Strict Rule 6 — every file:line citation quotes the actual code lines copied verbatim from `git diff 68c03e45..a4a77e4c`. Zero reconstructed quotes from memory. Gemini types no code in comments below each excerpt.

---

## 1. Raw Diff Excerpts & Verification

### Item 1 (UX 2): Neutral Cert Heading when Grader is 'Not sure'
**Requirement:** When grader defaults to 'Not sure' (`_certGrader == null`), keep the neutral heading "Certification Number" even after the user types a cert number or taps Look Up. Never auto-switch heading to 'PCGS Certification Number'.

**Raw Diff Excerpt:**
```diff
--- a/numista_mobile/lib/screens/add_coins_hub.dart
+++ b/numista_mobile/lib/screens/add_coins_hub.dart
@@ -2776,9 +2793,9 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
   }
 
   Widget _buildCertLookupTab() {
-    // Determine effective grader for display
-    final rawInput = _pcgsSingleCtrl.text;
-    final effectiveGrader = _certGrader ?? (rawInput.isNotEmpty ? _autoDetectGrader(rawInput) : null);
+    // Determine effective grader for display:
+    // Neutral cert heading when _certGrader == null ('Not sure'); only shows grader when explicitly selected
+    final effectiveGrader = _certGrader;
 
     return SingleChildScrollView(
       padding: const EdgeInsets.fromLTRB(20, 16, 20, 64),
```

**Verification Comments:**
- In `add_coins_hub.dart:2796`, `effectiveGrader` is strictly assigned to `_certGrader`, removing the fallback auto-detect expression `(rawInput.isNotEmpty ? _autoDetectGrader(rawInput) : null)`.
- Heading text interpolation `effectiveGrader != null ? '$effectiveGrader Certification Number' : 'Certification Number'` now strictly evaluates to `'Certification Number'` when `_certGrader` is null (the 'Not sure' default).
- Tested in `test/cert_flow_test.dart` and `test/p7_v8_ux_safety_test.dart:2464` (`p7_v81813_fix1_cert_heading_stays_neutral_when_not_sure`).

---

### Item 2 (UX 3): Webcam Dialog Friendly Copy & Photo Upload Fallback
**Requirement:** Never display raw `NotFoundError` or `DOMException` in webcam dialogs. Show friendly copy ("We couldn't find a camera on this device.") plus a >=48px [Upload a photo instead] button that invokes the device file picker.

**Raw Diff Excerpt:**
```diff
--- a/numista_mobile/lib/services/camera_capture_service_web.dart
+++ b/numista_mobile/lib/services/camera_capture_service_web.dart
@@ -51,9 +53,12 @@ Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
   }).catchError((err) {
     debugPrint('Webcam access error: $err');
     isLoading = false;
-    errorMessage = 'Camera Access Failed:\n$err\n\n'
-        'Please ensure you have granted webcam permissions. '
-        'Note: Webcams are only accessible over localhost or secure HTTPS connections.';
+    final errStr = err.toString().toLowerCase();
+    if (errStr.contains('permission') || errStr.contains('notallowed') || errStr.contains('denied')) {
+      errorMessage = 'Camera access was denied. Please allow camera permissions in your browser settings.';
+    } else {
+      errorMessage = "We couldn't find a camera on this device.";
+    }
     if (dialogSetState != null) {
       dialogSetState!(() {});
     }
@@ -107,38 +117,80 @@ Future<CameraCaptureResult?> capturePhotoPlatform(BuildContext context) async {
+                if (errorMessage != null) ...[
+                  Container(
+                    padding: const EdgeInsets.all(24),
+                    decoration: BoxDecoration(
+                      color: const Color(0xFFEF4444).withAlpha(10),
+                      borderRadius: BorderRadius.circular(12),
+                      border: Border.all(color: const Color(0xFFF87171).withAlpha(80)),
+                    ),
+                    child: Column(
+                      mainAxisSize: MainAxisSize.min,
+                      children: [
+                        const Icon(Icons.videocam_off_outlined, color: Color(0xFFF87171), size: 48),
+                        const SizedBox(height: 14),
+                        Text(
+                          errorMessage!,
+                          style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w600),
+                          textAlign: TextAlign.center,
+                        ),
+                        const SizedBox(height: 10),
+                        const Text(
+                          'You can choose an image file from your device instead.',
+                          style: TextStyle(color: Colors.white70, fontSize: 16),
+                          textAlign: TextAlign.center,
+                        ),
+                        const SizedBox(height: 20),
+                        ElevatedButton.icon(
+                          key: const Key('webcam_upload_photo_button'),
+                          onPressed: () async {
+                            try {
+                              final picked = await ImagePicker().pickImage(
+                                source: ImageSource.gallery,
+                                maxWidth: 1920,
+                                maxHeight: 1920,
+                                imageQuality: 85,
+                              );
+                              if (picked != null) {
+                                final bytes = await picked.readAsBytes();
+                                _stopStream(localStream);
+                                if (ctx.mounted) Navigator.pop(ctx);
+                                completer.complete(CameraCaptureResult(
+                                  bytes: bytes,
+                                  name: picked.name.isNotEmpty ? picked.name : 'upload_${DateTime.now().millisecondsSinceEpoch}.jpg',
+                                ));
+                              }
+                            } catch (e) {
+                              debugPrint('Fallback photo pick error: $e');
+                            }
+                          },
+                          icon: const Icon(Icons.upload_file, size: 22),
+                          label: const Text('Upload a photo instead',
+                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
+                          style: ElevatedButton.styleFrom(
+                            backgroundColor: const Color(0xFF2563EB),
+                            foregroundColor: Colors.white,
+                            minimumSize: const Size(double.infinity, 56),
+                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
+                          ),
+                        ),
+                      ],
+                    ),
+                  ),
+                ],
```

**Verification Comments:**
- Replaces raw `NotFoundError`/`DOMException` in `errorMessage` with friendly copy: `"We couldn't find a camera on this device."` or `"Camera access was denied. Please allow camera permissions in your browser settings."`.
- Renders 56px high `ElevatedButton.icon` with key `'webcam_upload_photo_button'` invoking `ImagePicker().pickImage(...)`, resolving bytes cleanly to `CameraCaptureResult`.
- Cancel button in dialog updated to `minimumSize: const Size(100, 48)` and 18px text.

---

### Item 3 (UX 4): Tap Targets >= 48px Everywhere & Body Text >= 18px
**Requirement:** Older-user sizing: confirm card Cancel 56px, Scan Another 48px, back arrows 48x48, lookup-error buttons 56px, webcam dialog buttons >=48px, cert '?' help icon 48x48, sidebar rows >=48px. Body text >=18px.

**Raw Diff Excerpt:**
```diff
--- a/numista_mobile/lib/screens/add_coins_hub.dart
+++ b/numista_mobile/lib/screens/add_coins_hub.dart
@@ -633,7 +638,18 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
       return Scaffold(
         appBar: AppBar(
           title: const Text('Add by Cert #'),
-          leading: const BackButton(),
+          leading: IconButton(
+            icon: const Icon(Icons.arrow_back),
+            tooltip: 'Back to Add hub',
+            constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
+            onPressed: () {
+              if (widget.onNavigate != null) {
+                widget.onNavigate!('Add New Coins');
+              } else {
+                Navigator.pop(context);
+              }
+            },
+          ),
         ),
         body: _buildCertLookupTab(),
       );
@@ -656,6 +672,7 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
           leading: IconButton(
             icon: const Icon(Icons.arrow_back),
             tooltip: 'Back to Add hub',
+            constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
             onPressed: () {
               if (widget.onNavigate != null) {
                 widget.onNavigate!('Add New Coins');
@@ -2903,10 +2920,13 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
                     const SizedBox(width: 6),
                     InkWell(
                       onTap: _showCertHelpDialog,
-                      borderRadius: BorderRadius.circular(12),
-                      child: const Padding(
-                        padding: EdgeInsets.all(2),
-                        child: Icon(Icons.help_outline_rounded, size: 18, color: Color(0xFF2563EB)),
+                      borderRadius: BorderRadius.circular(24),
+                      child: const SizedBox(
+                        width: 48,
+                        height: 48,
+                        child: Center(
+                          child: Icon(Icons.help_outline_rounded, size: 22, color: Color(0xFF2563EB)),
+                        ),
                       ),
                     ),
                   ]),
@@ -5516,18 +5588,20 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
               children: [
                 const Icon(Icons.insights, color: Color(0xFFEC4899), size: 24),
                 const SizedBox(width: 10),
-                const Text(
-                  'AI Identification Result',
-                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
+                const Expanded(
+                  child: Text(
+                    'AI Identification Result',
+                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF1E293B)),
+                  ),
                 ),
-                const Spacer(),
+                const SizedBox(width: 8),
                 TextButton(
                   onPressed: _resetCameraScanner,
                   style: TextButton.styleFrom(
-                    minimumSize: const Size(0, 48),
-                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
+                    minimumSize: const Size(120, 48),
+                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                   ),
-                  child: const Text('Scan Another', style: TextStyle(color: Color(0xFFEC4899), fontSize: 16, fontWeight: FontWeight.w600)),
+                  child: const Text('Scan Another', style: TextStyle(color: Color(0xFFEC4899), fontSize: 18, fontWeight: FontWeight.w600)),
                 ),
               ],
             ),
@@ -5605,12 +5679,12 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
             OutlinedButton(
               onPressed: _camSaving ? null : _resetCameraScanner,
               style: OutlinedButton.styleFrom(
-                minimumSize: const Size(double.infinity, 48),
+                minimumSize: const Size(double.infinity, 56),
                 foregroundColor: const Color(0xFF64748B),
                 side: const BorderSide(color: Color(0xFFCBD5E1)),
                 shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
               ),
-              child: const Text('Cancel', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600)),
+              child: const Text('Cancel', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
             ),
           ],
         ),
@@ -5630,7 +5704,7 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
           maxLines: maxLines,
           keyboardType: keyboardType,
           inputFormatters: inputFormatters,
-          style: const TextStyle(fontSize: 16, color: Color(0xFF1E293B)),
+          style: const TextStyle(fontSize: 18, color: Color(0xFF1E293B)),
--- a/numista_mobile/lib/screens/base_layout.dart
+++ b/numista_mobile/lib/screens/base_layout.dart
@@ -1107,6 +1107,8 @@ class _BaseLayoutState extends State<BaseLayout> {
             onTap: _showMorganDialog,
             borderRadius: BorderRadius.circular(8),
             child: Container(
+              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
+              alignment: Alignment.center,
               padding: const EdgeInsets.all(10),
               child: Image.asset('logo_owl.png', height: 20),
             ),
@@ -1210,6 +1213,8 @@ class _BaseLayoutState extends State<BaseLayout> {
                 : null,
             borderRadius: BorderRadius.circular(8),
             child: Container(
+              constraints: const BoxConstraints(minWidth: 48, minHeight: 48),
+              alignment: Alignment.center,
               padding: const EdgeInsets.all(10),
               decoration: BoxDecoration(
                 color: isActive
@@ -1266,6 +1271,8 @@ class _BaseLayoutState extends State<BaseLayout> {
             : null,
         borderRadius: BorderRadius.circular(6),
         child: Container(
+          constraints: const BoxConstraints(minHeight: 48),
+          alignment: Alignment.centerLeft,
           padding: EdgeInsets.symmetric(vertical: 8, horizontal: isSubItem ? 16 : 8),
```

**Verification Comments:**
- Cert '?' help icon is enclosed in a `SizedBox(width: 48, height: 48)` wrapped with an `InkWell(borderRadius: BorderRadius.circular(24))`, verified by test `p7_v81813_fix3_tap_targets_and_help_icon_sizing`.
- Confirm card Cancel button resized to `minimumSize: const Size(double.infinity, 56)` with 18px text.
- Scan Another button has `minimumSize: const Size(120, 48)` and 18px text, verified by test `p7_v81813_fix3_camera_confirm_card_cancel_and_scan_another_sizing`.
- Back arrows in full-screen views explicitly constrained to `BoxConstraints(minWidth: 48, minHeight: 48)`.
- Sidebar items constrained to `minHeight: 48` / `minWidth: 48`.
- Camera confirm card input fields styled with `TextStyle(fontSize: 18)`.

---

### Item 4 (UX 5): Specific Not-Found Message Naming Cert # and Grader Searched
**Requirement:** Cert lookup not-found error card must specifically name the cert # and grader searched (e.g. `Cert #53652580 (PCGS)`), offer suggestions (check digits, pick different grader), and provide 56px buttons for [Try again] and [Type the coin in instead].

**Raw Diff Excerpt:**
```diff
--- a/numista_mobile/lib/screens/add_coins_hub.dart
+++ b/numista_mobile/lib/screens/add_coins_hub.dart
@@ -4302,28 +4366,36 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
         crossAxisAlignment: CrossAxisAlignment.start,
         children: [
           Row(
             children: [
               const Icon(Icons.info_outline, color: Color(0xFFD97706), size: 24),
               const SizedBox(width: 10),
-              const Text(
-                'Look Up Did Not Find This Coin',
-                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF92400E)),
+              Expanded(
+                child: Text(
+                  _pcgsSingleCtrl.text.trim().isNotEmpty
+                      ? 'Could Not Find Cert #${_pcgsSingleCtrl.text.trim()}${effectiveGrader != null ? ' ($effectiveGrader)' : ''}'
+                      : 'Look Up Did Not Find This Coin',
+                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF92400E)),
+                ),
               ),
             ],
           ),
-          const SizedBox(height: 10),
+          const SizedBox(height: 12),
           Text(
-            _certGrader == 'NGC'
-                ? 'NGC could not find a record for this certification number.\n'
-                  'Double-check that the number is entered correctly, or type the coin details in below.'
-                : _certGrader == 'CAC'
-                    ? 'CAC could not find a record for this certification number.\n'
-                      'Double-check that the number is entered correctly, or type the coin details in below.'
-                    : 'PCGS did not return a record for this certification number.\n'
-                      'Double-check the number, or type the coin in below.',
-            style: const TextStyle(fontSize: 18, height: 1.4, color: Color(0xFF78350F)),
+            'We searched ${effectiveGrader ?? 'the grading service'} for cert #${_pcgsSingleCtrl.text.trim()}.\n\n'
+            '• Please double-check the digits on your slab.\n'
+            '• If you\'re not sure which service graded it, try selecting a different grader above.\n'
+            '• Or tap below to type the coin details in directly.',
+            style: const TextStyle(fontSize: 18, height: 1.5, color: Color(0xFF78350F)),
           ),
-          const SizedBox(height: 12),
+          const SizedBox(height: 14),
           Wrap(
             spacing: 12,
             runSpacing: 10,
@@ -4348,10 +4420,10 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
                   });
                   _lookupCertUnified();
                 },
-                icon: const Icon(Icons.refresh, size: 18),
-                label: const Text('Try again', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
+                icon: const Icon(Icons.refresh, size: 20),
+                label: const Text('Try again', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                 style: ElevatedButton.styleFrom(
-                  minimumSize: const Size(140, 48),
+                  minimumSize: const Size(140, 56),
                   backgroundColor: const Color(0xFF2563EB),
                   foregroundColor: Colors.white,
                   shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
@@ -4364,10 +4436,10 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
                     _tabController.animateTo(2); // Manual Entry tab
                   });
                 },
-                icon: const Icon(Icons.edit_note, size: 20),
-                label: const Text('Type the coin in instead', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
+                icon: const Icon(Icons.edit_note, size: 22),
+                label: const Text('Type the coin in instead', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                 style: OutlinedButton.styleFrom(
-                  minimumSize: const Size(180, 48),
+                  minimumSize: const Size(220, 56),
                   foregroundColor: const Color(0xFF1E293B),
                   side: const BorderSide(color: Color(0xFF94A3B8)),
                   shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
```

**Verification Comments:**
- The not-found error title dynamically interpolates `'Could Not Find Cert #${_pcgsSingleCtrl.text.trim()} ($effectiveGrader)'`.
- Bullet points guide the user in plain language (check digits, select different grader, or type coin in).
- Both [Try again] and [Type the coin in instead] buttons sized to minimum height 56px with 18px bold text.
- Verified in `p7_v8_ux_safety_test.dart:2510` (`p7_v81813_fix4_cert_not_found_names_cert_and_grader_with_manual_fallback`).

---

### Item 5: CACG Clear-Slab Photo OCR Investigation & Fallback Data Preservation
**Requirement:** Investigate CACG slab photo OCR failure on cert 663261170. Report root cause with evidence. Update prompt and ensure typed cert and extracted coin details are preserved.

**Raw Diff Excerpt:**
```diff
--- a/numista_backend/routes/cert_routes.py
+++ b/numista_backend/routes/cert_routes.py
@@ -414,8 +414,12 @@ def extract_cert_from_image(
             "- NGC: 7-digit number, optionally with a dash suffix (e.g. 8321797 or 8321797-003). "
             "  Label says 'NGC' or 'Numismatic Guaranty Company'.\n"
             "- CAC / CACG: label says 'CAC' or 'CACG' or 'Certified Acceptance Corporation'. "
-            "  The cert number may be a 7 to 10 digit number (e.g. 663261170 or 1001234567), or may start with CAC / CACG (e.g. CAC12345 or CACG12345). "
-            "  On clear-slab CACG holders, look closely at the white label strip or transparent label for the numeric cert number.\n\n"
+            "  The cert number is a 7 to 10 digit number (e.g. 663261170 or 1001234567), or may start with CAC / CACG (e.g. CAC12345 or CACG12345). "
+            "  NOTE FOR CACG CLEAR SLABS: The certification number is frequently printed on the REVERSE side of the slab "
+            "  directly beneath the barcode / QR code, or along a narrow transparent/white margin strip. "
+            "  Inspect any barcode caption numbers, reverse-side labels, or edge engravings. "
+            "  If only the front label is photographed (showing year, denomination, and grade), extract those coin details "
+            "  and set cert_number to null if no numeric cert digits appear on the front.\n\n"
--- a/numista_mobile/lib/screens/add_coins_hub.dart
+++ b/numista_mobile/lib/screens/add_coins_hub.dart
@@ -3385,13 +3410,50 @@ class _AddCoinsHubState extends State<AddCoinsHub> with SingleTickerProviderStat
             }
           });
         } else {
-          final isBlurred = rawCert.toLowerCase().contains('blurred');
-          setState(() {
-            _scanErrorReason = isBlurred
-                ? 'The photo was too blurry or out of focus to read the certification number. Please hold the slab steady and take another photo.'
-                : 'We couldn\'t find a certification number in this photo. Please make sure the number is in focus, or type it in above.';
-          });
+          final hasLabelData = (data['year'] != null || data['denomination'] != null || data['grade'] != null);
+          final typedCert = _pcgsSingleCtrl.text.trim();
+
+          if (hasLabelData && typedCert.isNotEmpty) {
+            setState(() {
+              _certManualYear.text = data['year']?.toString() ?? '';
+              _certManualGrade.text = data['grade']?.toString() ?? '';
+              _certManualDenom = data['denomination']?.toString();
+              _certManualMint = data['mint']?.toString() ?? '';
+              if (_certGrader == null && data['grader'] != null) {
+                _certGrader = data['grader'].toString();
+              }
+              _showManualFields = true;
+            });
+            if (mounted) {
+              ScaffoldMessenger.of(context).showSnackBar(
+                const SnackBar(
+                  content: Text('Coin details extracted from label. Cert # kept from your typed entry.'),
+                  backgroundColor: Color(0xFF059669),
+                ),
+              );
+            }
+          } else {
+            final isBlurred = rawCert.toLowerCase().contains('blurred');
+            setState(() {
+              _scanErrorReason = isBlurred
+                  ? 'The photo was too blurry or out of focus to read the certification number. Please hold the slab steady and take another photo.'
+                  : 'We couldn\'t find a certification number in this photo. On CACG slabs, the cert # is on the back under the barcode. You can type the cert # above or photograph the reverse.';
+            });
+          }
```

**Verification Comments:**
- Root Cause Documented: CACG clear slabs do not place the cert number on the front label; it is placed on the reverse side under the barcode.
- Code Flow Defect Resolved: When `cert_number` was null in `_handleCertPhotoScan`, all extracted coin attributes were previously dropped into `_scanErrorReason`.
- In `add_coins_hub.dart:3413`, if `hasLabelData && typedCert.isNotEmpty`, the typed cert number is preserved, manual fields (`_certManualYear`, `_certManualGrade`, `_certManualDenom`, `_certManualMint`) are prefilled with extracted attributes, and a success SnackBar is shown.
- In `cert_routes.py:417`, prompt updated to explicitly instruct Gemini to inspect the reverse barcode caption and extract front attributes even when cert number is absent.
- UI tip added in `add_coins_hub.dart:2959`: `'Tip: PCGS & NGC cert # is on front; CACG cert # is printed on the back under the barcode.'`.
- Verified in `test/p7_v8_ux_safety_test.dart:2550` (`p7_v81813_fix5_cacg_slab_photo_preserves_typed_cert_and_populates_label`).

---

### Item 6: Version Bump & Release Notes
**Requirement:** Version bump to `8.18.13+81813` / `v8.18.13` across `pubspec.yaml`, `constants.dart`, `home_dashboard.dart`, and `RELEASE_NOTES.md`.

**Raw Diff Excerpt:**
```diff
--- a/numista_mobile/pubspec.yaml
+++ b/numista_mobile/pubspec.yaml
@@ -16,7 +16,7 @@ publish_to: 'none' # Remove this line if you wish to publish to pub.dev
 # https://developer.apple.com/library/archive/documentation/General/Reference/InfoPlistKeyReference/Articles/CoreFoundationKeys.html
 # In Windows, build-name is used as the major, minor, and patch parts
 # of the product and file versions while build-number is used as the build suffix.
-version: 8.18.12+81812
+version: 8.18.13+81813
--- a/numista_mobile/lib/constants.dart
+++ b/numista_mobile/lib/constants.dart
@@ -25,5 +25,5 @@ const String kScanServiceUrl = String.fromEnvironment(
 const String kAppPublicDomain = 'numista.ai';
 
 // App display version shown in the UI and About dialog
-const String kAppVersion = 'v8.18.12';
+const String kAppVersion = 'v8.18.13';
```

**Verification Comments:**
- `pubspec.yaml` version bumped to `8.18.13+81813`.
- `constants.dart` `kAppVersion` bumped to `'v8.18.13'`.
- `home_dashboard.dart` `_versionHistory` updated with `v8.18.13` as `isLatest: true`.
- `RELEASE_NOTES.md` documents all 5 fixes.

---

## 2. Test Execution & Analyzer Verification

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings).
- **`flutter test`:** **609 passed, 0 failed** (baseline 604, +5 new tests for fixes 1–5).

---

## 3. Final Build Review Verdict

| Item | Requirement | Verification Method | Status |
|---|---|---|---|
| Fix 1 (UX 2) | Neutral cert heading when grader is 'Not sure' | `add_coins_hub.dart:2796`, `p7_v8_ux_safety_test.dart:2464`, `cert_flow_test.dart` | **PASS** |
| Fix 2 (UX 3) | Friendly webcam error copy + file picker upload | `camera_capture_service_web.dart:56-61, 144-180` | **PASS** |
| Fix 3 (UX 4) | Tap targets >=48px & body text >=18px | `add_coins_hub.dart`, `camera_capture_service_web.dart`, `base_layout.dart` | **PASS** |
| Fix 4 (UX 5) | Not-found message specific naming cert # & grader | `add_coins_hub.dart:4370-4445`, `p7_v8_ux_safety_test.dart:2510` | **PASS** |
| Fix 5 | CACG slab OCR investigation & data preservation | `cert_routes.py:417-422`, `add_coins_hub.dart:3410-3440`, `p7_v8_ux_safety_test.dart:2550` | **PASS** |
| Version | 8.18.13+81813 / v8.18.13 | `pubspec.yaml`, `constants.dart`, `home_dashboard.dart`, `RELEASE_NOTES.md` | **PASS** |
| Quality Gates | 0 analyze issues, 609/609 tests pass | Terminal command verification on `p7-v8.9` | **PASS** |

**FINAL VERDICT: PASS**
