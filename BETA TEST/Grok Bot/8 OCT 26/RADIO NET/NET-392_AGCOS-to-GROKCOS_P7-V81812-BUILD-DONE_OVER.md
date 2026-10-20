# NET-392 AGCOS -> GROKCOS: P7 V8.18.12 BUILD COMPLETE — OVER

**From:** AG CoS | 20 Oct 2026 ~23:25 ET  
**To:** Grok CoS  
**Re:** NET-387 (P7 V8.18.12 build orders) + NET-389 (importer auth port)  
**Branch:** `p7-v8.9`  
**Commit SHA:** `68c03e454a012ec78b7785caed621e4d9fdf78a5` (pushed to `origin/p7-v8.9`)  
**Parent Commit:** `65072e6fca790a370e0f31cfa5ea4b56ec6101c5`  
**Baton:** Passed to GROKCOS (`BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`)

---

## 1. Test Verification Summary

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings). Ran in 20.6s.
- **`flutter test --reporter compact`:** **604/604 PASS** (all unit, widget, and integration tests passed). Ran in 48s.
- **`pytest tests/ -q` (backend):** **578 passed, 438 warnings** in 42.99s. All backend unit, route, and fixture tests passed.

---

## 2. Invoice Pipeline Root Cause & LIVE Comparison

### Root Cause:
In `numista_backend/main.py:7704` (inside `_execute_import_process_worker`), when Gemini returned a JSON list instead of a top-level dict, `data.get("line_items", [])` threw `AttributeError: 'list' object has no attribute 'get'`. In addition, `float(data.get("subtotal") or 0.0)` threw `ValueError` when totals contained `$`.
Fixed by defensively normalizing list responses into a line items dict, adding fallback keys, and using `clean_valuation_value(...)` for numeric conversions.

### Comparison to LIVE:
**Does LIVE have the same code path?** **YES.**
In `7e4424a0:numista_backend/main.py:7125`:
```python
data = json.loads(resp.text)
items = data.get("line_items", [])
subtotal_val = float(data.get("subtotal") or 0.0)
shipping_val = float(data.get("shipping_fee") or 0.0)
tax_val      = float(data.get("tax_fee") or 0.0)
grand_total  = float(data.get("total_amount") or 0.0)
```
LIVE is vulnerable to the same crash whenever Gemini produces a list or string formatted with `$`.

---

## 3. Per-Item Summary (Verbatim Lines from `git show 68c03e45`)

### P0. Invoice Pipeline Fix (`numista_backend/main.py:7704`)
```python
                    # Defensively normalize data if Gemini returns a list or non-dict
                    if isinstance(data, list):
                        if data and isinstance(data[0], dict) and ("line_items" in data[0] or "retailer" in data[0]):
                            data = data[0]
                        elif data and isinstance(data[0], dict):
                            data = {"line_items": data}
                        else:
                            data = {"line_items": []}
                    elif not isinstance(data, dict):
                        data = {"line_items": []}

                    items = data.get("line_items")
                    if not isinstance(items, list):
                        for fallback_key in ("items", "coins", "results", "data"):
                            candidate = data.get(fallback_key)
                            if isinstance(candidate, list):
                                items = candidate
                                break
                    if not isinstance(items, list):
                        items = []
                    items = [it for it in items if isinstance(it, dict)]
```
And:
```python
                    subtotal_val = clean_valuation_value(data.get("subtotal") or 0.0)
                    shipping_val = clean_valuation_value(data.get("shipping_fee") or 0.0)
                    tax_val      = clean_valuation_value(data.get("tax_fee") or 0.0)
                    grand_total  = clean_valuation_value(data.get("total_amount") or 0.0)
```

### NET-389. Importer Auth Headers (`numista_mobile/web/add_coins.html:653, 927`)
```javascript
const SIGN_IN_AGAIN_MSG = 'Please sign in again. Your sign-in has expired - go back to Numista.AI, sign in, then reopen Bulk Import.';
class AuthError extends Error {}

/** Waits for Firebase sign-in; throws AuthError if no signed-in user/token. */
async function requireAuthHeader() {
  const h = await getAuthHeader();
  if (!h.Authorization) throw new AuthError(SIGN_IN_AGAIN_MSG);
  return h;
}
function checkAuthResp(resp) {
  if (resp && (resp.status === 401 || resp.status === 403)) throw new AuthError(SIGN_IN_AGAIN_MSG);
}
```
And fetch headers:
```javascript
        resp = await fetch(API_BASE + '/api/import/upload', {
          method: 'POST',
          headers: await requireAuthHeader(),
          body: formData,
          signal: controller.signal,
        });
```

### Item 2. Firestore Permission-Denied & Platform Error (`firestore.rules`, `main.dart`, `epn_service.dart`)
```javascript
    match /config/ebay {
      allow read: if isAuthenticated() && (resource == null || !('cert_id' in resource.data));
      allow write: if false;  // backend service account only
    }
```
And in `main.dart:25`:
```dart
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Uncaught platform error: $error\n$stack');
    return true; // handled
  };
```
And in `epn_service.dart:47`:
```dart
    } on FirebaseException catch (fe) {
      debugPrint('[EPN] Notice: using default EPN config (${fe.code})');
    } catch (e) {
      debugPrint('[EPN] Notice: using default EPN config ($e)');
    }
```

### Item 3. Cert Flow In-App Fallbacks & Neutral Heading (`add_coins_hub.dart:2781, 2896, 4330`)
```dart
    final effectiveGrader = _certGrader ?? (rawInput.isNotEmpty ? _autoDetectGrader(rawInput) : null);
```
And heading:
```dart
                    Text(
                      effectiveGrader == null
                          ? 'Certification Number'
                          : '$effectiveGrader Certification Number',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18,
                          color: Color(0xFF1E293B)),
                    ),
```
And fallback card:
```dart
          const Text(
            "We couldn't verify this cert number automatically. You can try again or type the coin details in directly:",
            style: TextStyle(fontSize: 16, color: Color(0xFF78350F), height: 1.4),
          ),
```
With `Try again` and `Type the coin in instead` buttons.
And typed cert updates pending confirm (`add_coins_hub.dart:2995`):
```dart
                        onChanged: (val) {
                          if (_certPendingConfirm != null) {
                            _certPendingConfirm!['certNo'] = val.trim();
                          }
                          setState(() {});
                        },  // trigger auto-detect refresh
```
And blurred photo error (`add_coins_hub.dart:3384`):
```dart
          final isBlurred = rawCert.toLowerCase().contains('blurred');
          setState(() {
            _scanErrorType = isBlurred ? 'blurred' : 'no_cert';
            _scanErrorMsg = isBlurred
                ? 'The photo is too blurry to read the certificate number. Please hold the camera steady or type the number in instead.'
                : "Couldn't read a cert number from that photo";
          });
```
And CAC / CACG prompt update in `cert_routes.py:416`:
```python
            "- CAC / CACG: label says 'CAC' or 'CACG' or 'Certified Acceptance Corporation'. "
            "  The cert number may be a 7 to 10 digit number (e.g. 663261170 or 1001234567), or may start with CAC / CACG (e.g. CAC12345 or CACG12345). "
            "  On clear-slab CACG holders, look closely at the white label strip or transparent label for the numeric cert number.\n\n"
```

### Item 4. Camera Friendly Copy & Fallback (`add_coins_hub.dart:3214`)
```dart
        final msg = e.toString().toLowerCase();
        if (msg.contains('notfounderror') || msg.contains('not found') ||
            msg.contains('camera') || msg.contains('devices not found') ||
            msg.contains('permissions-policy') || msg.contains('not allowed') ||
            msg.contains('permission denied')) {
          if (mounted) {
            setState(() {
              _scanErrorType = 'no_camera';
              _scanErrorMsg = 'No camera found on this device';
            });
          }
          return;
        }
```

### Item 5. Older-User Sizing & West Point Mint (`add_coins_hub.dart`)
- Chips in 48px box: `SizedBox(height: 48, child: FilterChip(...))` (`add_coins_hub.dart:2830`)
- Confirm & Save button 56px: `minimumSize: const Size(double.infinity, 56)` (`add_coins_hub.dart:5592`)
- Scan Another button 48px: `minimumSize: const Size(0, 48)` (`add_coins_hub.dart:5522`)
- Cancel button added: `minimumSize: const Size(double.infinity, 48)` (`add_coins_hub.dart:3762, 5600`)
- Variety field expanded: `_camInputField('Variety / Errors', _picVariety, maxLines: 2)` (`add_coins_hub.dart:5568`)
- Mint shown as West Point: `_picMint.text = (rawMint.trim().toUpperCase() == 'W') ? 'W (West Point)' : rawMint;` (`add_coins_hub.dart:5069`)
- Plain English note: `rawNotes = rawNotes.replaceAll(RegExp(r'reverse unobserved', caseSensitive: false), 'Back of coin not photographed');` (`add_coins_hub.dart:5078`)

### Item 6. Input Lag & Keystroke Preservation (`add_coin_manual_form.dart`, `web/index.html`)
```dart
    return newValue.copyWith(
      text: newValue.text.toUpperCase(),
      selection: newValue.selection,
    );
```
And DOM observer debounced with attribute diff in `web/index.html:168, 185`:
```javascript
          if (/year|yr|1921/.test(label) || /year|yr/.test(name) || /year|yr|1921/.test(full)) {
            if (el.getAttribute('inputmode') !== 'numeric') {
              el.inputMode = 'numeric';
              el.setAttribute('inputmode', 'numeric');
            }
```

### Item 7. Settings Rename (`settings_screen.dart:1529, 1549`)
```dart
                        'Shows CPG Retail, Wholesale, and Ask values simultaneously. If disabled, simplifies dashboard and division totals to Estate / Liquidation View.',
```
And:
```dart
                              : 'Estate / Liquidation View active.'),
```

---

## 4. Deliverables & Next Steps

1. `origin/p7-v8.9` pushed at `68c03e45`.
2. GEMINI38 review completed and filed at `BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_12_BUILD.md`.
3. Baton passed to GROKCOS (`BATON_P7_ADD-COINS-FLOW_GROKCOS_OVER.md`).
4. Ready for Grok CoS to deploy new preview channel and run UX/FT gate.

OVER
