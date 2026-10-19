# GEMINI 3.8 FLASH INDEPENDENT REVIEW: P7 V8.18.1 BUILD

**Reviewer Model:** Gemini 3.8 Flash (via AG CoS Build Auditor)  
**Date:** 2026-10-19  
**Target Commit:** `0f2f06e0` (`fix(p7-v8.18.1): invoice PDF path, scan timeout+403 root cause, 16px text, welcomeDone reset, investigation docs`)  
**Base Commit:** `1137b732`  
**Branch:** `p7-v8.9`  
**Scope:** P7 V8.18.1 targeted fixes from V8.18 FAIL score  

---

## 1. Executive Summary & Verdict

- **Flutter Analyze:** 0 errors, 0 warnings (ran in 14.8s)  
- **Flutter Tests:** 585/585 passed (baseline was 583)  
- **Pytest Suite:** 573 passed, 250 warnings (baseline was 571)  
- **Final Verdict:** **PASS**

---

## 2. Verbatim Code Inspection by File

### 2.1 Font Size Verification (Mandatory Check)
Both targeted sub-16px strings have been updated to 16px.

#### (A) `numista_mobile/lib/screens/settings_screen.dart`
- **Component:** `_buildMicroscopeCard` description
- **Base line (1137b732:588-589):**
```dart
                  'Connects digital USB microscopes via the Numista Desktop Agent on localhost. Keep disabled if you use phone camera or file uploads.',
                  style: TextStyle(fontSize: 13, color: descColor),
```
- **New line (0f2f06e0:588-589):**
```dart
                  'Connect a USB microscope to identify coins up close.',
                  style: TextStyle(fontSize: 16, color: descColor),
```
- **Verification Statement:** settings_screen.dart microscope description: fontSize: 16 (was 13) ✔

#### (B) `numista_mobile/lib/screens/add_coins_hub.dart`
- **Component:** NFC Secured badge in PCGS verification card
- **Base line (1137b732:4218-4219):**
```dart
                  Text('NFC Secured — tap slab label to verify authenticity',
                      style: TextStyle(fontSize: 12, color: Color(0xFF1E40AF), fontWeight: FontWeight.w500)),
```
- **New line (0f2f06e0:4139-4140):**
```dart
                  Text('NFC Secured — tap slab label to verify authenticity',
                      style: TextStyle(fontSize: 16, color: Color(0xFF1E40AF), fontWeight: FontWeight.w500)),
```
- **Verification Statement:** add_coins_hub.dart NFC badge: fontSize: 16 (was 12) ✔

#### (C) Back Arrow Confirmation
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart` (new lines 621-624):
```dart
        appBar: AppBar(
          title: const Text('Add by Cert #'),
          leading: const BackButton(),
        ),
```
- **Verification:** `const BackButton()` utilizes Flutter framework's standard `IconButton` interactive minimum bounding dimension (`kMinInteractiveDimension = 48.0px`). No custom overriding constraints or reduced paddings are set. Verified 48px tap target compliant.

---

### 2.2 Fix 1: Invoice PDF Import Path

- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **New lines (0f2f06e0:1146-1165):**
```dart
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () async {
                        final email = AuthService.userEmail;
                        final path  = buildAddCoinsHtmlPath(email);
                        final uri   = kIsWeb
                            ? Uri.base.resolve(path)
                            : Uri.parse('https://$kAppPublicDomain$path');
                        if (kIsWeb) {
                          await launchUrl(uri, webOnlyWindowName: '_self');
                        } else {
                          await launchUrl(uri, mode: LaunchMode.platformDefault);
                        }
                      },
                      icon: const Icon(Icons.open_in_new, size: 18),
                      label: const Text('Open Invoice Importer →'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFFF0C040),
                        foregroundColor: const Color(0xFF1E293B),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                      ),
                    ),
```
- **Analysis:** Replaces previous unfunctional simulation button `_runParallelBatchSim` with the functional invoice importer path (`buildAddCoinsHtmlPath(email)`). This directs the user straight to `add_coins.html?email=...&api=...` which is the Gemini-driven multi-page PDF and invoice ingestion interface. Dead mock state (`_isBatchProcessing`, `_batchProgress`, `_batchStatusMsg`, `_batchItems`, `_runParallelBatchSim`) has been completely excised.

---

### 2.3 Fix 2: Server-Side 25s Timeout & 408 on `/api/identify_coin_photo`

- **File:** `numista_backend/main.py`
- **New lines (0f2f06e0:6130-6150):**
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))


async def call_gemini_identify(contents, model=PRIMARY_MODEL):
    """
    Executes Gemini generate_content call in a worker thread to keep the asyncio event loop unblocked.
    """
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: genai_client.models.generate_content(
            model=model,
            contents=contents,
            config=genai_types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.1,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            ),
        ),
    )
```
- **New lines (0f2f06e0:6209-6228):**
```python
        call_res = call_gemini_identify(pass1_contents, PRIMARY_MODEL)
        if asyncio.iscoroutine(call_res) or isinstance(call_res, asyncio.Future):
            resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_TIMEOUT)
        else:
            resp1 = call_res
        if isinstance(resp1, dict):
            pass1 = resp1
        else:
            raw1 = resp1.text.strip()
            if raw1.startswith("```"):
                raw1 = raw1.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            pass1 = json.loads(raw1)
        logger.info(f"Coin ID pass 1: {pass1.get('year')} {pass1.get('denomination')} conf={pass1.get('confidence')}")
    except asyncio.TimeoutError:
        raise HTTPException(status_code=408, detail="Image identification timed out. Please try again.")
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Coin ID pass 1 error")
        raise HTTPException(status_code=500, detail=f"AI identification failed: {e}")
```
- **Analysis:** Prevents Gemini / Vertex AI network stalls from hanging the server worker thread indefinitely (which previously reached 56s-473s). Caps Pass 1 at 25.0s, returning an explicit HTTP 408 with `"Image identification timed out. Please try again."`. Pass 2 is bounded at `min(10.0, GEMINI_IDENTIFY_TIMEOUT)` with non-fatal degradation to Pass 1 results.

---

### 2.4 Fix 4: Reset `_welcomeDone` on Sign-Out

- **File:** `numista_mobile/lib/widgets/auth_gate.dart`
- **New lines (0f2f06e0:56-60, 68-70):**
```dart
  /// Resets the welcome screen completion state (e.g. upon user sign-out).
  static void resetWelcome() => _AuthGateState.resetWelcome();
  static bool get welcomeDone => _AuthGateState._welcomeDone;
  static set welcomeDone(bool val) => _AuthGateState._welcomeDone = val;
...
  static void resetWelcome() {
    _welcomeDone = false;
  }
```
- **File:** `numista_mobile/lib/screens/base_layout.dart`
- **New line (0f2f06e0:1369):**
```dart
    if (confirm == true) {
      AuthGate.resetWelcome();
      if (isDemo) {
```
- **File:** `numista_mobile/lib/services/auth_service.dart`
- **New line (0f2f06e0:205):**
```dart
  static Future<void> signOut() async {
    _isAdminCached = false;
    UiVariantService.reset();
    AuthGate.resetWelcome();
    await _auth.signOut();
  }
```
- **Analysis:** Guarantees that logging out in the same browser session resets the in-memory `_welcomeDone` gate so the subsequent signed-in user experiences the initial onboarding welcome flow.

---

## 3. Test Suite Integrity

- `numista_backend/tests/test_identify_timeout.py`:
  - `test_identify_coin_photo_returns_408_on_timeout` PASSED (verifies HTTP 408 on mock TimeoutError)
  - `test_identify_coin_photo_real_wait_for_timeout` PASSED (verifies genuine `asyncio.wait_for` expiry at 0.05s)
- `numista_mobile/test/p7_v8_ux_safety_test.dart`:
  - `p7_v818_1_auth_gate_reset_welcome` PASSED
  - `p7_v818_1_settings_microscope_and_hub_nfc_font_sizes` PASSED

---

## 4. Final Verdict

**VERDICT: PASS**  
The build conforms to all requirements, passes all test baselines (585/585 flutter, 573 pytest), maintains 0 analyze warnings/errors, and fulfills all font size and functional constraints.
