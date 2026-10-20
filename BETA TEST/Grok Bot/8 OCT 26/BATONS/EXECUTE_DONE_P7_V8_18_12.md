# EXECUTE DONE: P7 Add Coins Flow V8.18.12

**Date:** 2026-10-20 ~23:25 ET  
**Author:** AG CoS  
**Branch:** `p7-v8.9`  
**Commit SHA:** `68c03e454a012ec78b7785caed621e4d9fdf78a5` (pushed to `origin/p7-v8.9`)  
**Parent Commit:** `65072e6fca790a370e0f31cfa5ea4b56ec6101c5`  
**Preceding Directives:** NET-387 + NET-389  
**Rule 9.3 Review Status:** Complete (GEMINI38 review written: `BETA TEST\Grok Bot\8 OCT 26\BATONS\GEMINI38_REVIEW_P7_V8_18_12_BUILD.md`)

---

## 1. Test Verification Summary

- **`flutter analyze lib/`:** **0 issues found** (0 errors, 0 warnings). Ran in 20.6s.
- **`flutter test --reporter compact`:** **604/604 PASS** (all unit, widget, and integration tests passed). Ran in 48s.
- **`pytest tests/ -q` (backend):** **578 passed, 438 warnings** in 42.99s. All backend unit and fixture tests passed.

---

## 2. NET-387 + NET-389 Fix Verification Matrix

| Fix | Description | Status | Verbatim Evidence in Commit Diff |
|---|---|---|---|
| **P0: Invoice Pipeline Crash** | Backend receipts parser 'list' has no attribute 'get' and float parsing crash fixed. Defensively normalizes lists into dicts and cleans valuation values. | **PASS** | `numista_backend/main.py:7704-7740`, `checklist_parser.py:290-300`, `document_classifier_service.py:57-61`, `test_invoice_fixtures.py:56-125` |
| **Item 2: Console Errors & EPN Guard** | Catch uncaught platform errors on Web and prevent Firestore 403 `permission-denied` on `/config/ebay` and `/config/*` queries. | **PASS** | `numista_backend/firestore.rules:140-145`, `numista_mobile/firestore.rules:177-182`, `numista_mobile/lib/main.dart:25-28`, `epn_service.dart:35-49` |
| **Item 3: Cert Flow UX** | Fallback in-app [Try again] and [Type the coin in instead], no external dead link; neutral heading when grader is Not sure or empty; typed cert updates pending confirm; friendly card for blurred photo; CAC/CACG 7-10 digit prompt. | **PASS** | `add_coins_hub.dart:2781, 2896, 2995, 3384, 4330-4375`, `cert_routes.py:416-418` |
| **Item 4: Camera Friendly Copy** | Replace raw NotFoundError copy with friendly copy plus [Choose a photo instead]. | **PASS** | `add_coins_hub.dart:3214-3228, 3061-3140` |
| **Item 5: Older-User Sizing** | Tap targets >=48px (FilterChips in 48px box, Confirm & Save 56px, Scan Another 48px); >=16px text; Cancel buttons on confirm card; Variety not cut off (maxLines: 2); Mint shown as 'W (West Point)'; 'reverse unobserved' replaced with plain English. | **PASS** | `add_coins_hub.dart:2830, 3762, 5069, 5078, 5522, 5568, 5592, 5600` |
| **Item 6: Manual Add Coin Input Lag** | Preserve selection in `UpperCaseTextFormatter`; debounce DOM mutations by 120ms with attribute diffing in `web/index.html`; retain instant validation clearing. | **PASS** | `add_coin_manual_form.dart:340, 580-585`, `web/index.html:168-200` |
| **Item 7: Settings Toggle Rename** | Rename 'Greysheet Bid' to 'Estate / Liquidation View'. | **PASS** | `settings_screen.dart:1529, 1549` |
| **NET-389: Importer Auth Headers** | Add `requireAuthHeader` and `checkAuthResp` in `add_coins.html` to eliminate 401 CORS failure on bulk imports. | **PASS** | `numista_mobile/web/add_coins.html:653-664, 927, 964, 1036, 1086, 1150` |
| **Version Bump** | Update version to 8.18.12+81812 / v8.18.12 across app and pubspec. | **PASS** | `pubspec.yaml:19`, `constants.dart:28`, `home_dashboard.dart:1667` |

---

## 3. Invoice Pipeline Root Cause & LIVE Comparison

### Root Cause:
- **File & Lines:** `numista_backend/main.py:7704` (in `_execute_import_process_worker`)
- **What was wrong:** When Gemini returned a JSON list containing line items instead of a top-level dictionary (e.g. `[{"Program/Series": ...}]`), the code called `data.get("line_items", [])`. Because `data` was a `list`, this threw `AttributeError: 'list' object has no attribute 'get'`. Additionally, fields like `subtotal`, `shipping_fee`, and `tax_fee` were wrapped in `float(data.get(...) or 0.0)`, which threw `ValueError` when formatted with currency symbols (e.g. `"$1,050.00"`).
- **What changed:**
  1. Normalized `data` defensively: if `data` is a `list`, extracted `data[0]` if it represents an invoice dict, or wrapped `{"line_items": data}`.
  2. Fallback key resolution across `items`, `coins`, `results`, and `data`.
  3. Replaced direct `float(...)` with `clean_valuation_value(...)` which strips currency symbols and commas before converting to float.
  4. Applied matching list defensive checks to `checklist_parser.py:290` and `document_classifier_service.py:57`.
  5. Added regression unit tests in `test_invoice_fixtures.py` for list normalization and multi-item proportional fee allocations.

### Comparison to LIVE:
- **Does LIVE have the same code path?** **YES.**
- In `7e4424a0:numista_backend/main.py:7125`:
```python
data = json.loads(resp.text)
items = data.get("line_items", [])
added_this_file = 0
total_val = 0.0
col_ref = db.collection("users").document(user_email).collection("review_queue")
batch = db.batch()
file_stem = fname.rsplit(".", 1)[0]
receipt_id = f"rec_{safe_file_stem}"
line_items_out = []

subtotal_val = float(data.get("subtotal") or 0.0)
shipping_val = float(data.get("shipping_fee") or 0.0)
tax_val      = float(data.get("tax_fee") or 0.0)
grand_total  = float(data.get("total_amount") or 0.0)
```
LIVE is vulnerable to the identical crash whenever Gemini returns a JSON list or a string containing dollar signs for financial totals.

---

## 4. Verbatim File:Line Citations (Before → After from `git show 68c03e45`)

### Item 1: Invoice Pipeline Fix
- **File:** `numista_backend/main.py`
- **Before (`65072e6f:7704`):**
```python
                    items = data.get("line_items", [])
```
- **After (`68c03e45:7704-7726`):**
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

### Item 2: Firestore Rules Config Guard
- **File:** `numista_backend/firestore.rules` & `numista_mobile/firestore.rules`
- **Before (`65072e6f:140`):**
```javascript
    match /config/ebay {
      allow read: if isAuthenticated() && !('cert_id' in resource.data);
      allow write: if false;  // backend service account only
    }
```
- **After (`68c03e45:140`):**
```javascript
    match /config/ebay {
      allow read: if isAuthenticated() && (resource == null || !('cert_id' in resource.data));
      allow write: if false;  // backend service account only
    }
```

### Item 3: Cert Lookup Fallback In-App Dialogs
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Before (`65072e6f:4306-4328`):**
```dart
          const Text(
            'You can check the cert directly on PCGS.com instead:',
            style: TextStyle(fontSize: 18, color: Color(0xFF78350F), height: 1.4),
          ),
          if (hasCert) ...[
            const SizedBox(height: 10),
            // "View on PCGS.com" button — opens the cert page in the user's browser
            SizedBox(
              width: double.infinity,
              child: OutlinedButton.icon(
                onPressed: () async {
                  final uri = Uri.parse('https://www.pcgs.com/cert/$cert');
                  if (await canLaunchUrl(uri)) {
                    await launchUrl(uri, mode: LaunchMode.externalApplication);
                  }
                },
                icon: const Icon(Icons.open_in_new_rounded, size: 18),
                label: Text('View Cert #$cert on PCGS.com'),
```
- **After (`68c03e45:4330-4375`):**
```dart
          const Text(
            "We couldn't verify this cert number automatically. You can try again or type the coin details in directly:",
            style: TextStyle(fontSize: 16, color: Color(0xFF78350F), height: 1.4),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 12,
            runSpacing: 10,
            children: [
              ElevatedButton.icon(
                onPressed: () {
                  setState(() {
                    _pcgsLookupError = '';
                  });
                  _lookupCertUnified();
                },
                icon: const Icon(Icons.refresh, size: 18),
                label: const Text('Try again', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size(140, 48),
                  backgroundColor: const Color(0xFF2563EB),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
              OutlinedButton.icon(
                onPressed: () {
                  setState(() {
                    _pcgsLookupError = '';
                    _tabController.animateTo(2); // Manual Entry tab
                  });
                },
                icon: const Icon(Icons.edit_note, size: 20),
                label: const Text('Type the coin in instead', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                style: OutlinedButton.styleFrom(
                  minimumSize: const Size(180, 48),
                  foregroundColor: const Color(0xFF1E293B),
                  side: const BorderSide(color: Color(0xFF94A3B8)),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                ),
              ),
            ],
          ),
```

### Item 5: Neutral Heading When Grader is Not Sure
- **File:** `numista_mobile/lib/screens/add_coins_hub.dart`
- **Before (`65072e6f:2895`):**
```dart
                  Row(children: [
                    Text(
                      '$effectiveGrader Certification Number',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18,
                          color: Color(0xFF1E293B)),
                    ),
```
- **After (`68c03e45:2896`):**
```dart
                  Row(children: [
                    Text(
                      effectiveGrader == null
                          ? 'Certification Number'
                          : '$effectiveGrader Certification Number',
                      style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 18,
                          color: Color(0xFF1E293B)),
                    ),
```

### Item 7: Settings Toggle Rename
- **File:** `numista_mobile/lib/screens/settings_screen.dart`
- **Before (`65072e6f:1529`):**
```dart
                        'Shows CPG Retail, Greysheet Bid, and Ask values simultaneously. If disabled, simplifies dashboard and division totals to Estate/Liquidation View (Greysheet Bid).',
```
- **After (`68c03e45:1529`):**
```dart
                        'Shows CPG Retail, Wholesale, and Ask values simultaneously. If disabled, simplifies dashboard and division totals to Estate / Liquidation View.',
```

### Item 8: Importer Auth in `add_coins.html`
- **File:** `numista_mobile/web/add_coins.html`
- **Before (`65072e6f:914`):**
```javascript
        resp = await fetch(API_BASE + '/api/import/upload', {
          method: 'POST',
          headers: authHeaders,
          body: formData,
          signal: controller.signal,
        });
```
- **After (`68c03e45:927`):**
```javascript
        resp = await fetch(API_BASE + '/api/import/upload', {
          method: 'POST',
          headers: await requireAuthHeader(),
          body: formData,
          signal: controller.signal,
        });
```
