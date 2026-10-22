# GEMINI 3.8 BUILD REVIEW: P7 V8.18.15b (Follow-up Build)

**Reviewer:** AG CoS (Gemini 3.8 Flash)  
**Date:** 2026-10-22 ~15:25 ET  
**Commit Inspected:** `c096574095b0c5f8856e0908833c8d346f9dba5b` on branch `p7-v8.9` (parent: `a7c83d7d16023aada321643a4b92329118c11270`)  
**Target Track:** P7 Add Coins Flow V8.18.15b (Tap targets 48px, NGC exact copy, cert photo 1024 tokens + timeout + json_repair, invoice pdf retailer & date parsing, deduplication rules without silent drops, review snackbars)  
**Review Standard:** Strict Rule 6 — every file:line citation quotes the actual code lines copied verbatim from the working tree diff. Zero reconstructed quotes from memory. Gemini types no code in comments below each excerpt. Rule 9.3: One review per build version.

---

## 1. Verbatim Diff Excerpts & Verification

### Item 1: Tap Targets >= 48px on Sidebar Action Buttons
**Requirement:** Tap targets $\ge$ 48px across BaseLayout sidebar buttons (`Send Beta Feedback` and `Sign Out`).

**Raw Diff Excerpt:**
```dart
// File: numista_mobile/lib/screens/base_layout.dart:955-961
                          foregroundColor: Theme.of(context).brightness == Brightness.dark ? const Color(0xFFFFD700) : const Color(0xFF4338CA),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
+                         minimumSize: const Size(double.infinity, 48),
                          elevation: 0,
                        ),
                        icon: Icon(Icons.feedback_outlined, size: 14, color: Theme.of(context).brightness == Brightness.dark ? const Color(0xFFFFD700) : const Color(0xFF4338CA)),
```
```dart
// File: numista_mobile/lib/screens/base_layout.dart:1029-1035
                          side: BorderSide(color: isDark ? Colors.white24 : Colors.black26),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
+                         minimumSize: const Size(double.infinity, 48),
                        ),
                        icon: const Icon(Icons.logout, size: 14),
                        label: Text(
```

**Verification Comments:**
- In `numista_mobile/lib/screens/base_layout.dart:958` and `1033`, `minimumSize: const Size(double.infinity, 48)` was added to the `ElevatedButton.styleFrom` and `OutlinedButton.styleFrom` for `Send Beta Feedback` and `Sign Out`.
- Satisfies the older-user $\ge 48$px touch target requirement across sidebar buttons.

---

### Item 2: NGC Card Exact Copy
**Requirement:** Update NGC unsupported lookup card copy to exact string: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."` in `numista_mobile/lib/screens/add_coins_hub.dart`.

**Raw Diff Excerpt:**
```dart
// File: numista_mobile/lib/screens/add_coins_hub.dart:3750-3756
                 const SizedBox(height: 8),
                 Text(
                   grader == 'NGC'
-                      ? 'Cert #$certNo (NGC) was not found. Direct NGC cert lookup is not supported. Please scan the slab photo or enter details manually below.'
+                      ? "We can't look up NGC numbers automatically yet. Snap the label or type the details below."
                       : 'Cert #$certNo ($grader) was not found. $grader cert lookup is not available. Please scan the slab photo or enter details manually below.',
                   style: const TextStyle(fontSize: 18, color: Color(0xFF78350F), height: 1.4),
                 ),
```

**Verification Comments:**
- In `numista_mobile/lib/screens/add_coins_hub.dart:3753`, the exact string requested is rendered when `grader == 'NGC'`.
- Verified via Flutter widget test in `numista_mobile/test/p7_v8_ux_safety_test.dart` ("V8.18.15b: NGC unsupported lookup copy matches exact string").

---

### Item 3: Cert Photo OCR 1024 Tokens, 25s Timeout & json_repair Fallback
**Requirement:** Update slab photo OCR in `numista_backend/routes/cert_routes.py` to use `max_output_tokens=1024`, a 25s executor timeout, `json_repair` fallback handling for truncated/malformed replies, and guidance for PCGS/CACG reverse label cert numbers.

**Raw Diff Excerpt:**
```python
# File: numista_backend/routes/cert_routes.py:413-421
             "You are examining an image of a certified coin grading slab label. "
             "Extract the certification number, grading company, and coin details printed on the label.\n\n"
             "Grading companies and their cert # formats:\n"
-            "- PCGS: 8-digit number (e.g. 53652580). Label says 'PCGS' or 'Professional Coin Grading Service'.\n"
+            "- PCGS: 8-digit number (e.g. 53652580). Label says 'PCGS' or 'Professional Coin Grading Service'. "
+            "  NOTE: On some PCGS slabs, the cert number and barcode are printed on the REVERSE side label. "
+            "  If the front label shows coin details but no cert number, extract the details and set cert_number to null.\n"
             "- NGC: 7-digit number, optionally with a dash suffix (e.g. 8321797 or 8321797-003). "
             "  Label says 'NGC' or 'Numismatic Guaranty Company'.\n"
```
```python
# File: numista_backend/routes/cert_routes.py:440-466
+        def _call_model():
+            return _scan_client.models.generate_content(
+                model=model_name,
+                contents=[prompt, image_part],
+                config=_genai_types.GenerateContentConfig(
+                    response_mime_type="application/json",
+                    max_output_tokens=1024,
+                ),
+            )
+
+        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
+            future = executor.submit(_call_model)
+            response = future.result(timeout=25.0)
+
         text = response.text.strip()
-        data = json.loads(text)
+        try:
+            data = json.loads(text)
+        except Exception:
+            try:
+                import json_repair
+                repaired = json_repair.repair_json(text)
+                data = json.loads(repaired) if isinstance(repaired, str) else repaired
+            except Exception as jerr:
+                logger.warning(f"json_repair failed: {jerr}")
+                data = {}
```

**Verification Comments:**
- In `numista_backend/routes/cert_routes.py:440-466`, `max_output_tokens` increased from 256 to 1024, call wrapped in `ThreadPoolExecutor` with `timeout=25.0`, and truncated JSON response is repaired via `json_repair`.
- `json-repair>=0.64.0` added to `numista_backend/requirements.txt`.
- Verified by unit test `numista_backend/tests/test_cert_lookup.py:test_extract_cert_from_image_truncated_json_repair`.

---

### Item 4: U.S. Mint Invoice Parsing & Web Polling Timeout
**Requirement:** Parse Retailer (defaulting "United States Mint" for US Mint order PDFs), Invoice #, and Date accurately while preserving Qty > 1. Update `add_coins.html` polling to 60s timeout with countdown and server error messages.

**Raw Diff Excerpt:**
```python
# File: numista_backend/main.py:7542-7545
-            "invoice_number":       (it.get("Retailer Invoice #") or data.get("invoice_number") or "").strip(),
-            "retailer":             (it.get("Retailer/Website") or data.get("retailer") or "").strip(),
-            "purchase_date":        (it.get("invoice_date") or data.get("invoice_date") or "").strip(),
+            "invoice_number":       (it.get("Retailer Invoice #") or it.get("invoice_number") or data.get("invoice_number") or "").strip(),
+            "retailer":             (it.get("Retailer/Website") or it.get("retailer") or data.get("retailer") or ("United States Mint" if "usmint" in raw_lower or "united states mint" in raw_lower or "26ea" in raw_lower or "26xl" in raw_lower else "")).strip(),
+            "purchase_date":        (it.get("invoice_date") or it.get("Invoice Date") or it.get("Date") or data.get("invoice_date") or data.get("date") or "").strip(),
```
```python
# File: numista_backend/main.py:7865-7893
                     Required JSON output structure:
                     {{
-                        "retailer": "Dealer or store name",
-                        "invoice_number": "Invoice or order number",
+                        "retailer": "Dealer or store name (use 'United States Mint' if document is from US Mint / shop.usmint.gov)",
+                        "invoice_number": "Invoice, order, or customer reference number",
                         "invoice_date": "YYYY-MM-DD",
                         "subtotal": 0.00,
                         "shipping_fee": 0.00,
@@ -7867,14 +7880,16 @@ def _execute_import_process_worker(user_email: str, session_id: str, mask_pii: b
                                 "qty": 1,
                                 "is_supply": false,
                                 "Certification Number": "Cert number if graded",
-                                "Personal Notes": "Any item description or catalog number"
+                                "Personal Notes": "Any item description, catalog number, or stock item number (e.g. 26EA, 26XL)"
                             }}
                         ]
                     }}
                     Field Instructions:
+                    - "retailer": If document header or body indicates "United States Mint" or "www.usmint.gov", set to "United States Mint".
+                    - "invoice_number": Extract invoice number, order number, or packing slip number.
                     - "invoice_date": Output in ISO 8601 YYYY-MM-DD format.
                     - "Cost": Sticker price / unit price of the line item before global fees.
-                    - "qty": Integer quantity if more than 1 identical coin is on this line (default 1).
+                    - "qty": Integer quantity if more than 1 identical coin is on this line (default 1). Preserve quantity accurately.
```
```html
<!-- File: numista_mobile/web/add_coins.html:1031-1055, 1073-1087 -->
+  const startTime = Date.now();
+  const MAX_POLL_MS = 60000; // 60s timeout
   pollInterval = setInterval(async () => {
     try {
+      const elapsed = Date.now() - startTime;
+      if (elapsed >= MAX_POLL_MS) {
+        clearInterval(pollInterval);
+        showError('Processing timed out after 60 seconds. Please check your Review Queue or try uploading again.', true);
+        document.getElementById('progress-label').textContent = 'Timed out (60s)';
+        return;
+      }
...
+      if (!r.ok) {
+        let errDetail = 'Server returned ' + r.status;
+        try {
+          const ej = await r.json();
+          if (ej && (ej.detail || ej.message)) errDetail = ej.detail || ej.message;
+        } catch (_) {}
+        showError('Status check error: ' + errDetail, true);
+        return;
+      }
...
+      } else if (data.status === 'error') {
+        clearInterval(pollInterval);
+        const errMsg = data.error || data.detail || 'AI processing encountered an error.';
+        showError(errMsg, true);
+        document.getElementById('progress-label').textContent = 'Processing error: ' + errMsg;
+      } else if (data.status === 'linking') {
+        document.getElementById('progress-label').textContent = 'Linking receipts to coins...';
+      } else {
+        const remainingSec = Math.max(0, Math.ceil((MAX_POLL_MS - elapsed) / 1000));
+        document.getElementById('progress-label').innerHTML =
+          '<span class="pulse-dot"></span> AI processing (' + remainingSec + 's remaining)...';
       }
```

**Verification Comments:**
- In `numista_backend/main.py`, normalization and worker prompt explicitly capture US Mint retailer defaults, invoice numbers, purchase dates, and preserve `qty`.
- In `numista_mobile/web/add_coins.html`, 60-second countdown is displayed, and errors include HTTP status / server error messages.
- Verified in `numista_backend/tests/test_invoice_fixtures.py:test_us_mint_invoice_normalization`.

---

### Item 5: Review Commit Deduplication Rules & Review Hub Snackbars
**Requirement:** Attribute matches (Year+Mint+Denom) must never delete a queue item without committing it; commit coin with `possible_duplicate=True` and `duplicate_flag`. Invoice# + Item No matches must not drop multiple items in the same review batch when Qty > 1 was split. Review hub snackbar must display clear committed and skipped counts.

**Raw Diff Excerpt:**
```python
# File: numista_backend/main.py:3555-3595
                 is_definite_dupe = False
                 is_possible_dupe = False
                 inv_no = (data.get('Retailer Invoice #') or data.get('invoice_number') or '').strip()
                 item_no = (data.get('Retailer Item No.') or '').strip()
                 if inv_no and item_no:
                     try:
                         q = user_ref.collection('coins') \
                             .where('Retailer Invoice #', '==', inv_no) \
                             .where('Retailer Item No.', '==', item_no) \
                             .limit(1).get()
-                        is_dupe = len(q) > 0
+                        if len(q) > 0 and q[0].id not in request.review_ids:
+                            is_definite_dupe = True
                     except Exception:
                         pass
 
                 # Attribute match (Year + Mint Mark + Denomination)
-                if not is_dupe and data.get('Year') and data.get('Denomination'):
+                if not is_definite_dupe and data.get('Year') and data.get('Denomination'):
                     try:
                         # Denomination may be stored as 'Dollar', '1 Dollar', etc.
                         raw_denom = (data.get('Denomination') or '').strip()
                         denom_variants = [raw_denom]
                         if raw_denom.lower() == 'dollar':
                             denom_variants.extend(['1 Dollar', '$1', 'Dollar', 'Silver Dollar'])
                         elif raw_denom.lower() in ('cent', '1 cent'):
                             denom_variants.extend(['Cent', '1 Cent', 'Penny', '1C'])
                         q2 = user_ref.collection('coins') \
                             .where('Year', '==', str(data['Year'])) \
                             .where('Mint Mark', '==', str(data.get('Mint Mark', ''))) \
                             .where('Denomination', 'in', denom_variants[:10]) \
                             .limit(1).get()
-                        is_dupe = len(q2) > 0
+                        if len(q2) > 0 and q2[0].id not in request.review_ids:
+                            is_possible_dupe = True
                     except Exception:
                         pass
 
-                if is_dupe:
+                if is_definite_dupe:
                     batch.delete(queue_ref.document(doc_id))
                     skipped_count += 1
                     batch_op_count += 1
                 else:
                     # (Field normalization already applied above, before dupe queries)
 
+                    # Mark attribute duplicates clearly without dropping
+                    if is_possible_dupe:
+                        data['possible_duplicate'] = True
+                        data['duplicate_flag'] = 'Attribute match (Year, Mint, Denomination)'
+
                     # Legal System of Record Golden Schema defaults
```
```dart
// File: numista_mobile/lib/screens/review_hub_screen.dart:55-72, 130-148
       if (response.statusCode == 200) {
         if (!mounted) return;
+        int committed = _selectedIds.length;
+        int skipped = 0;
+        try {
+          final resData = jsonDecode(response.body);
+          if (resData is Map) {
+            if (resData.containsKey('committed')) committed = (resData['committed'] as num).toInt();
+            if (resData.containsKey('skipped')) skipped = (resData['skipped'] as num).toInt();
          }
+        } catch (_) {}
+
+        final snackText = skipped > 0
+            ? 'Added $committed coin${committed != 1 ? 's' : ''}. $skipped looked like coin${skipped != 1 ? 's' : ''} you already have; check them in Review.'
+            : 'Added $committed coin${committed != 1 ? 's' : ''}.';
+
         ScaffoldMessenger.of(context).showSnackBar(
-          SnackBar(content: Text('Successfully committed ${_selectedIds.length} items!')),
+          SnackBar(content: Text(snackText)),
         );
```

**Verification Comments:**
- In `numista_backend/main.py:3555-3595`, attribute matches are flagged with `possible_duplicate=True` and committed to `coins`, never silently dropped.
- In `numista_backend/main.py:3565`, items from the current review batch (`q[0].id not in request.review_ids`) are not flagged as duplicates of each other, allowing split Qty items to commit.
- In `numista_mobile/lib/screens/review_hub_screen.dart`, both commit paths parse response JSON and render clear messages.
- Verified in `numista_backend/tests/test_req031_auth.py:test_review_commit_attribute_dupe_committed_with_flag` and `test_review_commit_split_invoice_qty_both_committed`.
- Verified in `numista_mobile/test/p7_v8_ux_safety_test.dart` ("V8.18.15b: Review Hub snackbar format generates clear message for committed and skipped").

---

## 2. Test Execution Summary

| Test Suite | Result | Details |
|---|---|---|
| `flutter test test/p7_v8_ux_safety_test.dart --name "V8.18.15b"` | **2/2 PASS** | NGC copy matches exact string; review hub snackbar formats correctly. |
| `flutter analyze lib/` | **0 errors, 0 warnings** | Clean pass in 5.9s. |
| `py -m pytest numista_backend/tests/` | **606/606 PASS** | All 606 backend tests passing (including 3 new regression tests). |

---

## 3. Per-Condition Checklist

- [x] Item 1: Tap targets >= 48px on sidebar buttons `Send Beta Feedback` and `Sign Out`.
- [x] Item 2: NGC card copy matches exact string: `"We can't look up NGC numbers automatically yet. Snap the label or type the details below."`
- [x] Item 3: Cert photo OCR `max_output_tokens=1024`, 25s executor timeout, `json_repair` fallback, reverse label guidance.
- [x] Item 4: U.S. Mint invoice parsing preserves retailer, invoice#, date, Qty > 1; web polling has 60s timeout with countdown and detailed error messages.
- [x] Item 5: Attribute dupe matches never delete without committing; split Qty batch rows not flagged as dupes of each other; review hub snackbars explain committed & skipped.
- [x] LF line endings verified across all modified files.
- [x] No live Firestore writes; no pushes to `main`.

---

## 4. Final Verdict

**PASS** — All V8.18.15b requirements are completely verified with verbatim diff excerpts, 0 analyzer errors, and 100% green test suites across Flutter and Python.
