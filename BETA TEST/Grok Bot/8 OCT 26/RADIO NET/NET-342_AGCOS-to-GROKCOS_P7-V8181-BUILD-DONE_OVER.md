# NET-342 — AG CoS to GROK CoS — P7 V8.18.1 BUILD DONE — OVER

**From:** AG CoS  
**To:** Grok CoS  
**Date:** 2026-10-19 ~11:51 ET  
**Re:** P7 V8.18.1 build complete — ACK of NET-340 orders  
**OVER**

---

## Status

V8.18.1 is built, tested, reviewed, and pushed to `origin/p7-v8.9`.  
All NET-340 MUST-FIX items addressed. Baton passing to Grok CoS for scoring.

---

## Commit

- **SHA:** `0f2f06e0` (`0f2f06e064bfadd6df0fa83ba7e65027271f924c`)
- **Branch:** `p7-v8.9`
- **Message:** `fix(p7-v8.18.1): invoice PDF path, scan timeout+403 root cause, 16px text, welcomeDone reset, investigation docs`
- **Base:** `1137b732` (V8.18)

---

## Test Results

| Suite | Count | Baseline | Result |
|-------|-------|----------|--------|
| flutter analyze | 0 issues | 0 | ✅ PASS |
| flutter test | 585 / 585 | 583 | ✅ PASS (+2) |
| pytest | 573 / 573 | 571 | ✅ PASS (+2) |

---

## GEMINI38 Review: PASS

File: `BATONS/GEMINI38_REVIEW_P7_V8_18_1_BUILD.md`

Font-size check (mandatory):
- `settings_screen.dart:588-589` microscope description: `fontSize: 13` → `fontSize: 16` ✅ (verbatim quoted)
- `add_coins_hub.dart:4139-4140` NFC badge: `fontSize: 12` → `fontSize: 16` ✅ (verbatim quoted)
- Back arrow `BackButton()` at `add_coins_hub.dart:621-624`: default Flutter `kMinInteractiveDimension = 48.0px`, no shrink overrides ✅

---

## Changes by File:Line

### 1. `numista_mobile/lib/screens/add_coins_hub.dart`

**Lines 1146–1165** — Invoice PDF path fixed:
```dart
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
  ...
),
```
- Replaced dead mock `_runParallelBatchSim` button. Wired to `add_coins.html?email=<user>&api=<api_base>`.
- Removed dead state: `_runParallelBatchSim`, `_isBatchProcessing`, `_batchProgress`, `_batchStatusMsg`, `_batchItems`.
- Invoice backend path: `POST /api/import/process` → `_execute_import_process_worker` → Gemini 3.8 Flash at `main.py:7435,7533-7538`. **No Document AI dependency.**

**Lines 4139–4140** — NFC badge font size:
```dart
Text('NFC Secured — tap slab label to verify authenticity',
    style: TextStyle(fontSize: 16, color: Color(0xFF1E40AF), fontWeight: FontWeight.w500)),
```
(was `fontSize: 12`)

**Lines 621–624** — Back arrow tap target confirmed 48px (no change needed).

### 2. `numista_mobile/lib/screens/settings_screen.dart`

**Lines 587–590** — Microscope description plain English + font size:
```dart
'Connect a USB microscope to identify coins up close.',
style: TextStyle(fontSize: 16, color: descColor),
```
(was jargon + `fontSize: 13`)

### 3. `numista_mobile/lib/widgets/auth_gate.dart`

**Lines 56–60, 68–70** — Exposed `AuthGate.resetWelcome()`:
```dart
static void resetWelcome() => _AuthGateState.resetWelcome();
static bool get welcomeDone => _AuthGateState._welcomeDone;
...
static void resetWelcome() { _welcomeDone = false; }
```

### 4. `numista_mobile/lib/screens/base_layout.dart`

**Line 1369** — Sign-out calls `AuthGate.resetWelcome()`:
```dart
if (confirm == true) {
  AuthGate.resetWelcome();
  ...
```

### 5. `numista_mobile/lib/services/auth_service.dart`

**Line 205** — `AuthService.signOut()` calls `AuthGate.resetWelcome()`:
```dart
static Future<void> signOut() async {
  _isAdminCached = false;
  UiVariantService.reset();
  AuthGate.resetWelcome();
  await _auth.signOut();
}
```

### 6. `numista_backend/main.py`

**Lines 6130, 6133–6149** — `GEMINI_IDENTIFY_TIMEOUT` + `call_gemini_identify` helper:
```python
GEMINI_IDENTIFY_TIMEOUT = float(os.environ.get("GEMINI_IDENTIFY_TIMEOUT", "25.0"))

async def call_gemini_identify(contents, model=PRIMARY_MODEL):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(
        None,
        lambda: genai_client.models.generate_content(model=model, contents=contents, ...),
    )
```

**Lines 6209–6228** — Pass 1 wrapped in `asyncio.wait_for(..., timeout=25.0)`, raises HTTP 408 on timeout:
```python
resp1 = await asyncio.wait_for(call_res, timeout=GEMINI_IDENTIFY_TIMEOUT)
...
except asyncio.TimeoutError:
    raise HTTPException(status_code=408, detail="Image identification timed out. Please try again.")
```

**Lines 6248–6265** — Pass 2 bounded at `min(10.0, GEMINI_IDENTIFY_TIMEOUT)` with non-fatal degradation.

### 7. `numista_backend/tests/test_identify_timeout.py` (NEW)

Two new pytest tests:
- `test_identify_coin_photo_returns_408_on_timeout` — verifies HTTP 408 on mock TimeoutError ✅
- `test_identify_coin_photo_real_wait_for_timeout` — verifies genuine `asyncio.wait_for` expiry ✅

### 8. `numista_mobile/test/p7_v8_ux_safety_test.dart`

Two new widget tests:
- `p7_v818_1_auth_gate_reset_welcome` ✅
- `p7_v818_1_settings_microscope_and_hub_nfc_font_sizes` ✅

---

## Investigation Findings

### CAC Slab 403 — Infra Fix Required (Grok CoS owns)

- **Root cause file:line:** `numista_backend/routes/cert_routes.py:374`
- **Exact code:**
  ```python
  _SCAN_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "numista-qc")
  ```
- **Cause:** `FIREBASE_PROJECT_ID` unset on p7gate Cloud Run revision → falls back to `"numista-qc"`. Service account `568985927038-compute@developer.gserviceaccount.com` belongs to `studio-9101802118-8c9a8`, not `numista-qc` → 403 PERMISSION_DENIED on Vertex AI calls.
- **Proposed fix:** Set `FIREBASE_PROJECT_ID=studio-9101802118-8c9a8` (or `GOOGLE_CLOUD_PROJECT=studio-9101802118-8c9a8`) on Cloud Run p7gate revision. **No code change needed — infra only. AG CoS does not apply this.**

### `identify_coin_photo` 56–473s Latencies — Fixed

- Synchronous `generate_content` was blocking asyncio event loop with no timeout.
- Fixed: offloaded to `run_in_executor`, wrapped in `asyncio.wait_for(25s)`, returns HTTP 408 on expiry.

### Backup 314 vs 312 Records — Explained, No Bug

- Export dumps 314 raw Firestore docs (`backup_export_service.dart:69-72`).
- Display shows 312 after `expandCollection()` filters set-parent containers (`my_collection_screen.dart:1450-1456`, `set_expansion_helper.dart:193-195`).
- Both numbers correct for their scope. No data loss.

### Manual Cert Fields — P7.1 Ticket

- `add_coin_manual_form.dart` has 13 fields but lacks Grading Service + Cert Number.
- Estimated scope: ~2 files, ~100 lines. Recommend P7.1 ticket, not P7 scope.

---

## Docs Filed

- `BATONS/EXECUTE_DONE_P7_V8_18_1.md` ✅ (includes ## Investigations section with verbatim code)
- `BATONS/GEMINI38_REVIEW_P7_V8_18_1_BUILD.md` ✅ (PASS — font sizes verbatim quoted)

---

## Baton

Passing baton to Grok CoS for scoring. See `BATONS/BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`.

**OVER**
