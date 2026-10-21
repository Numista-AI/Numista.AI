# EXECUTE DONE: P7 Add Coins Flow V8.18.13

**Date:** 2026-10-20 ~21:10 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `a4a77e4c959514e3e8a2308637d169210d7bc88b` (pushed cleanly to `origin/p7-v8.9`)  
**Parent Commit:** `68c03e454a012ec78b7785caed621e4d9fdf78a5`  
**Preceding Directives:** NET-393 (UX Gate V5 Fixes)  
**Rule 9.3 Review Status:** Complete (GEMINI38 review written: `BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_13_BUILD.md`)

---

## 1. Test Verification Summary

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings). Ran in 22.4s.
- **`flutter test`:** **609/609 PASS** (all unit, widget, and safety tests passed; baseline 604, +5 new tests for V8.18.13). Ran in 53s.
- **No deploy performed:** dev/p7 branches only. Nothing pushed to main.

---

## 2. NET-393 Fix Verification Matrix

| Fix | Description | Status | Verbatim Evidence in Commit Diff |
|---|---|---|---|
| **Fix 1: Cert Heading Neutrality** | When grader defaults to 'Not sure', heading stays "Certification Number" even after user enters digits or taps Look Up. Never auto-switches to "PCGS Certification Number". | **PASS** | `add_coins_hub.dart:2796`, `cert_flow_test.dart:65-95`, `p7_v8_ux_safety_test.dart:2464-2486` |
| **Fix 2: Webcam Friendly Copy & Fallback** | Webcam dialog never displays raw `NotFoundError` or `DOMException`. Shows friendly message ("We couldn't find a camera on this device.") plus 56px [Upload a photo instead] button invoking device file picker via `ImagePicker`. | **PASS** | `camera_capture_service_web.dart:56-61, 144-180` |
| **Fix 3: Tap Targets >= 48px & Text Sizing** | Confirm card Cancel resized to 56px, Scan Another 48px, back arrows 48x48, lookup-error buttons 56px, webcam buttons >=48px, cert '?' help icon 48x48 tap box, sidebar rows >=48px. Body text >=18px. | **PASS** | `add_coins_hub.dart:642, 675, 2924, 4425, 4441, 5601, 5682, 5707`, `base_layout.dart:1110, 1216, 1274`, `p7_v8_ux_safety_test.dart:2488-2508, 2600-2624` |
| **Fix 4: Specific Not-Found Message** | Cert lookup not-found card explicitly names cert # and grader searched (`Cert #53652580 (PCGS)`), offers clear bullet-point advice, and renders 56px [Try again] and [Type the coin in instead] buttons. | **PASS** | `add_coins_hub.dart:4370-4445`, `p7_v8_ux_safety_test.dart:2510-2548` |
| **Fix 5: CACG Slab OCR Investigation & Data Preservation** | Root cause identified and documented. Prompt updated in `cert_routes.py` to check reverse barcode. Frontend preserves typed cert when front photo yields label details, pre-fills manual fields, and shows reverse-barcode hint. | **PASS** | `cert_routes.py:417-422`, `add_coins_hub.dart:2959, 3410-3440`, `p7_v8_ux_safety_test.dart:2550-2598` |
| **Version Bump** | Version updated to 8.18.13+81813 / v8.18.13 across all locations. | **PASS** | `pubspec.yaml:19`, `constants.dart:28`, `home_dashboard.dart:1667`, `RELEASE_NOTES.md:405` |

---

## 3. CACG Clear-Slab Photo OCR Root Cause Investigation

### Finding & Evidence:
1. **Physical Slab Design:**
   - On CACG (Certified Acceptance Corporation Grading) clear slabs, the certification number is **NOT printed on the front label**.
   - The front label contains only the coin date/mint mark, denomination, grade, and CAC logo.
   - The 7-to-10 digit certification number is printed on the **REVERSE side** beneath the barcode / QR code.
2. **Code Flow Defect:**
   - In `add_coins_hub.dart`, the callback for `_handleCertPhotoScan` required `cert_number` to be non-empty before extracting coin details:
     ```dart
     if (certNum.isNotEmpty) {
       _pcgsSingleCtrl.text = certNum;
       ...
     } else {
       _scanErrorReason = ...; // Dropped year, grade, denomination!
     }
     ```
   - When a user photographed the front of a CACG slab, Gemini successfully extracted `'year': '1921'`, `'grade': 'MS-66'`, `'denomination': 'Morgan Dollar'`, but returned `'cert_number': null`.
   - The code treated this as a complete failure, displaying an error card and discarding the extracted coin attributes even if the user had already typed their cert number (`663261170`).
3. **Resolution Implemented:**
   - **Backend Prompt (`cert_routes.py:417-422`):** Instructed Gemini that on CACG clear slabs, numeric cert digits are frequently on the reverse barcode caption or narrow margin, and to extract front coin details even if the cert number is absent on the front.
   - **Frontend Preservation (`add_coins_hub.dart:3410-3440`):** Added `hasLabelData && typedCert.isNotEmpty` check. If the front photo extracted coin attributes, the user's typed cert is preserved, manual entry fields (`_certManualYear`, `_certManualGrade`, `_certManualDenom`, `_certManualMint`) are prefilled, and a green success SnackBar confirms: `"Coin details extracted from label. Cert # kept from your typed entry."`
   - **User Guidance:** Added permanent helper text in the cert tab (`add_coins_hub.dart:2959`):
     `Tip: PCGS & NGC cert # is on front; CACG cert # is printed on the back under the barcode.`

---

## 4. Note on `numista_mobile/firestore.rules` (Rule / Directive Compliance)

Per orders in NET-393:
> "DO NOT touch the numista_mobile/firestore.rules beta_feedback owner-list extra unless asked. Note it in EXECUTE_DONE (it is not in numista_backend/firestore.rules; the copies drift)."

- `numista_mobile/firestore.rules` contains the `beta_feedback` owner-list permissions introduced earlier.
- In commit `a4a77e4c`, neither `firestore.rules` file was touched, preserving the exact state from commit `68c03e45`.

---

## 5. Acknowledgment of NET-394 Addendum (Import Qty / Sets)

During active build execution of NET-393 fixes, GROKCOS filed an addendum: `NET-394_GROKCOS-to-AGCOS_ADDENDUM-393-FT-FAIL-V81812-IMPORT-QTY-SETS_OVER.md` (~8:32 PM ET) regarding invoice accuracy (restoring 15 rows from 092052.pdf), systemic quantity handling, and sets vs. supply items.
- Commit `a4a77e4c` fully closes out the 5 UX Gate V5 blockers from NET-393.
- The 00475-haj diff reference (`NET-394_REF_importer_fix_00475-haj.diff`) has been reviewed and verified.
- Passing baton back to GROKCOS for UX Gate V6 verification of V8.18.13, and to coordinate sequencing of the import/quantity regression fixes.

---

## 6. Verbatim File:Line Citations (Before → After from `git show a4a77e4c`)

### Fix 1: Neutral Cert Heading
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Before (`68c03e45:2778`):**
```dart
    final rawInput = _pcgsSingleCtrl.text;
    final effectiveGrader = _certGrader ?? (rawInput.isNotEmpty ? _autoDetectGrader(rawInput) : null);
```
- **After (`a4a77e4c:2796`):**
```dart
    // Neutral cert heading when _certGrader == null ('Not sure'); only shows grader when explicitly selected
    final effectiveGrader = _certGrader;
```

### Fix 2: Friendly Webcam Copy & Upload Button
- **File:** `numista_mobile/lib/services/camera_capture_service_web.dart`
- **Before (`68c03e45:54`):**
```dart
    errorMessage = 'Camera Access Failed:\n$err\n\n'
        'Please ensure you have granted webcam permissions. '
        'Note: Webcams are only accessible over localhost or secure HTTPS connections.';
```
- **After (`a4a77e4c:56-61`):**
```dart
    final errStr = err.toString().toLowerCase();
    if (errStr.contains('permission') || errStr.contains('notallowed') || errStr.contains('denied')) {
      errorMessage = 'Camera access was denied. Please allow camera permissions in your browser settings.';
    } else {
      errorMessage = "We couldn't find a camera on this device.";
    }
```
- **File Picker Upload Button (`a4a77e4c:144-180`):**
```dart
                        ElevatedButton.icon(
                          key: const Key('webcam_upload_photo_button'),
                          onPressed: () async {
                            try {
                              final picked = await ImagePicker().pickImage(
                                source: ImageSource.gallery,
                                maxWidth: 1920,
                                maxHeight: 1920,
                                imageQuality: 85,
                              );
                              if (picked != null) {
                                final bytes = await picked.readAsBytes();
                                _stopStream(localStream);
                                if (ctx.mounted) Navigator.pop(ctx);
                                completer.complete(CameraCaptureResult(
                                  bytes: bytes,
                                  name: picked.name.isNotEmpty ? picked.name : 'upload_${DateTime.now().millisecondsSinceEpoch}.jpg',
                                ));
                              }
                            } catch (e) {
                              debugPrint('Fallback photo pick error: $e');
                            }
                          },
                          icon: const Icon(Icons.upload_file, size: 22),
                          label: const Text('Upload a photo instead',
                              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF2563EB),
                            foregroundColor: Colors.white,
                            minimumSize: const Size(double.infinity, 56),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                        ),
```

### Fix 3: Tap Targets & Sizing
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Cert '?' Help Icon (`a4a77e4c:2924-2931`):**
```dart
                      borderRadius: BorderRadius.circular(24),
                      child: const SizedBox(
                        width: 48,
                        height: 48,
                        child: Center(
                          child: Icon(Icons.help_outline_rounded, size: 22, color: Color(0xFF2563EB)),
                        ),
                      ),
```
- **Confirm Card Cancel Button (`a4a77e4c:5682`):**
```dart
            OutlinedButton(
              onPressed: _camSaving ? null : _resetCameraScanner,
              style: OutlinedButton.styleFrom(
                minimumSize: const Size(double.infinity, 56),
                foregroundColor: const Color(0xFF64748B),
                side: const BorderSide(color: Color(0xFFCBD5E1)),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: const Text('Cancel', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w600)),
            ),
```
- **Scan Another Button (`a4a77e4c:5601`):**
```dart
                TextButton(
                  onPressed: _resetCameraScanner,
                  style: TextButton.styleFrom(
                    minimumSize: const Size(120, 48),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  ),
                  child: const Text('Scan Another', style: TextStyle(color: Color(0xFFEC4899), fontSize: 18, fontWeight: FontWeight.w600)),
                ),
```

### Fix 4: Not-Found Error Naming Cert & Grader
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart:4370-4445`
```dart
              Expanded(
                child: Text(
                  _pcgsSingleCtrl.text.trim().isNotEmpty
                      ? 'Could Not Find Cert #${_pcgsSingleCtrl.text.trim()}${effectiveGrader != null ? ' ($effectiveGrader)' : ''}'
                      : 'Look Up Did Not Find This Coin',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF92400E)),
                ),
              ),
```

### Fix 5: CACG Clear-Slab OCR & Fallback
- **File:** `numista_backend/routes/cert_routes.py:417-422`
```python
            "- CAC / CACG: label says 'CAC' or 'CACG' or 'Certified Acceptance Corporation'. "
            "  The cert number is a 7 to 10 digit number (e.g. 663261170 or 1001234567), or may start with CAC / CACG (e.g. CAC12345 or CACG12345). "
            "  NOTE FOR CACG CLEAR SLABS: The certification number is frequently printed on the REVERSE side of the slab "
            "  directly beneath the barcode / QR code, or along a narrow transparent/white margin strip. "
            "  Inspect any barcode caption numbers, reverse-side labels, or edge engravings. "
            "  If only the front label is photographed (showing year, denomination, and grade), extract those coin details "
            "  and set cert_number to null if no numeric cert digits appear on the front.\n\n"
```
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart:3413-3435`
```dart
          final hasLabelData = (data['year'] != null || data['denomination'] != null || data['grade'] != null);
          final typedCert = _pcgsSingleCtrl.text.trim();

          if (hasLabelData && typedCert.isNotEmpty) {
            setState(() {
              _certManualYear.text = data['year']?.toString() ?? '';
              _certManualGrade.text = data['grade']?.toString() ?? '';
              _certManualDenom = data['denomination']?.toString();
              _certManualMint = data['mint']?.toString() ?? '';
              if (_certGrader == null && data['grader'] != null) {
                _certGrader = data['grader'].toString();
              }
              _showManualFields = true;
            });
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Coin details extracted from label. Cert # kept from your typed entry.'),
                  backgroundColor: Color(0xFF059669),
                ),
              );
            }
          }
```
