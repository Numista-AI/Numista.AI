# FAILFIX PLAN v1: Broken Cards & Pending Pricing (NET-780b)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 4 November 2026, 5:32 PM ET  
**Reference Baton:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
**Partition:** Split Track B of NET-780 (per Founder Eric 4:58 PM ET split direction)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Eric's typed YES.

---

## 1. Executive Summary & Defect Overview

In Field Tester's audit of `p7-gate` (`shots_net748`), three card rendering bugs were reported in the collection grid:
1. **Card 1: `2026 American Eagle One...` Broken Image:** Displaying a broken image placeholder icon (`06_2026_silver_eagle_broken_icon.webp`).
2. **Card 2: `2023-D 5c` (Jefferson Nickel) Broken Image:** Displaying a broken image / spinner placeholder (`10_2023_cards.webp`).
3. **Card 1 Price Defect:** The 2026 American Eagle card displays the raw text string `'Pending'` in place of a formatted valuation or a styled badge chip.

---

## 2. Root Cause Analysis (Verbatim Code Citations)

### A. Defect 1: 2026 American Eagle One Ounce Broken Image
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
```dart
108:     final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
109:     final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
110:     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
...
117:     final combined = '$prog $theme $title $cond';
118:     if (year == '2026' &&
119:         RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
120:         !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
121:       return '26EA';
122:     }
```
And in `resolveFromMap()` lines 162–165:
```dart
162:     final primaryTitle = <String>[
163:       (data['title'] ?? '').toString().trim(),
164:       (data['name'] ?? '').toString().trim(),
165:       (data['Theme/Subject'] ?? '').toString().trim(),
```
**Mechanism of Failure:**
1. In Firestore collection documents imported from CSV or backup logs, coin title fields are commonly keyed with PascalCase `'Title'` or `'Name'`.
2. Line 110 and line 163 check only lowercase `'title'` and `'name'`. When `'Title'` is present, `title` resolves to empty string `''`.
3. If `Program/Series` was set to e.g. `'Bullion'` or `'US Mint Coins'`, `combined` does not contain `'american eagle'`.
4. As a result, `extractSku` fails to detect SKU `26EA` and returns `''`.
5. Because `resolveFromMap` returns `null`, `_CollectionCardImage` at `my_collection_screen.dart:6377-6380` falls back to `_cleanUrl(data[_F.imageReverse])`.
6. That document field contains a Wikimedia URL (`upload.wikimedia.org`), which is blocked by the CanvasKit CSP headers in `firebase.json:284`, throwing an image load error and rendering the broken image icon.

### B. Defect 2: 2023-D 5c (Jefferson Nickel) Broken Image
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` Section 3 (lines 457–485):
```dart
457:     // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
458:     if (cleanYear == '2023') {
459:       const awqObv =
460:           '$_base/2023_series/2023_american_women_quarters_shared_obverse.jpg';
...
476:       for (final entry in awqRevs.entries) {
477:         if (cleanTitle.contains(entry.key)) {
...
484:         }
485:       }
```
**Mechanism of Failure:**
1. Section 2 (lines 341–455) handles 2026 circulating coins, including `isNickel` for 2026 nickels at lines 446–454.
2. Section 3 handles `if (cleanYear == '2023')`, but **only** iterates through the 5 American Women Quarters (Bessie Coleman, Edith Kanaka'ole, Eleanor Roosevelt, Jovita Idar, Maria Tallchief).
3. Section 3 contains zero handler for 2023 Jefferson Nickels (`5c`, `nickel`).
4. Therefore, `resolveFromMap()` returns `null` for `2023-D 5c`.
5. `_CollectionCardImage` falls back to `CoinImageService.fetchReferenceImages()`, which fails under CanvasKit CSP or finds no matching reference, rendering the broken card spinner/icon.

### C. Defect 3: 2026 American Eagle Price Displays Raw 'Pending'
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 3017–3023:
```dart
3017:         final valCpg = _parseNumber(m['cpgRetail']);
3018:         final finalVal = valCpg;
3019:         
3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
3021:         final valueText = finalVal > 0 
3022:             ? fmt.format(finalVal) 
3023:             : (m[_F.aiValue]?.toString() ?? '—');
```
And lines 3170–3185:
```dart
3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
3171:                         Container(
3172:                           padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
3173:                           decoration: BoxDecoration(
3174:                             color: const Color(0xFFC9A227).withAlpha(25),
3175:                             borderRadius: BorderRadius.circular(4),
3176:                             border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
3177:                           ),
3178:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
3179:                         )
3180:                       else
3181:                         Text(
3182:                           valueText,
3183:                           style: const TextStyle(
3184:                             fontSize: 13,
3185:                             fontWeight: FontWeight.bold,
```
**Mechanism of Failure:**
1. A 2026 ASE proof coin has no historical CPG retail auction guide entry, so `valCpg == 0`.
2. Line 3023 evaluates `m[_F.aiValue]?.toString() ?? '—'`. When AI enrichment has not completed or is in-progress, `m[_F.aiValue]` contains the literal string `'Pending'`.
3. In line 3170, the badge condition is `valueText == '—' || m['enrichment_status'] == 'pending'`.
4. Because `valueText` is `'Pending'` (not `'—'`), and if `m['enrichment_status']` is null or capitalized, the check evaluates to `false`!
5. It drops into the `else` branch (line 3180) and renders `Text('Pending')` as raw unstyled body text!
6. Furthermore, for standard US Mint products like `26EA`, the official US Mint Issue Price ($95.00) in `kFallbackUsMintSkus['26EA']` or `purchase_price` should be used as fallback valuation when CPG is unavailable.

---

## 3. Planned Implementation

### A. Fix 1: Robust PascalCase and Title Extraction in `CanonicalMintAssetService`
In `numista_mobile/lib/services/canonical_mint_asset_service.dart`:
1. Update `extractSku` line 110:
   ```dart
   final title = (data['Title'] ?? data['title'] ?? data['Name'] ?? data['name'] ?? '').toString().toLowerCase();
   ```
2. Update `resolveFromMap` lines 162–165:
   ```dart
   final primaryTitle = <String>[
     (data['Title'] ?? data['title'] ?? '').toString().trim(),
     (data['Name'] ?? data['name'] ?? '').toString().trim(),
     (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().trim(),
   ```
3. Ensure SKU `26EA` reliably resolves to:
   - `obverseUrl`: `$_mintBase/2026_products/26EA_image_1.jpg`
   - `reverseUrl`: `$_mintBase/2026_products/26EA_image_2.jpg`
   - In `my_collection_screen.dart:6371`, `canon.reverseUrl` points directly to the valid on-domain Mint asset `26EA_image_2.jpg`.

### B. Fix 2: Add 2023 Jefferson Nickel Asset Resolution
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` Section 3 (line 485):
Add standard 2023 circulating coin support for Jefferson Nickels:
```dart
    if (cleanYear == '2023') {
      final isNickel = RegExp(r'\b(5c|5¢|nickel)\b').hasMatch(cleanDenom) ||
          RegExp(r'\bnickel\b').hasMatch(cleanTitle);
      if (isNickel) {
        final effMint = cleanMint == 'D' ? 'D' : 'P';
        return CanonicalMintAssetPair(
          sku: '2023-NICKEL-$effMint',
          obverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Obverse-Unc-$effMint.jpg',
          reverseUrl: '$_base/bulk_programs/nickel/SemiQ-Nickel-Reverse-Unc.jpg',
          isGenuine2026: false,
        );
      }
      // ... existing AWQ logic ...
    }
```
*(Uses existing standard Jefferson nickel obverse/reverse assets from `bulk_programs/nickel/`)*.

### C. Fix 3: Price Display Guard & Mint Issue Price Fallback
In `numista_mobile/lib/screens/my_collection_screen.dart`:
1. **Fallback Valuation Lookup (lines 3017–3024):**
   ```dart
   final valCpg = _parseNumber(m['cpgRetail']);
   final valPurchase = _parseNumber(m['purchase_price'] ?? m['cost']);
   final canonSku = CanonicalMintAssetService.extractSku(m);
   final fallbackMintPrice = canonSku.isNotEmpty ? (kFallbackUsMintSkus[canonSku]?.issuePrice ?? 0.0) : 0.0;
   
   final finalVal = valCpg > 0 ? valCpg : (fallbackMintPrice > 0 ? fallbackMintPrice : valPurchase);
   
   final fmt = intl.NumberFormat.currency(symbol: '\$');
   final rawAiVal = m[_F.aiValue]?.toString().trim() ?? '';
   final valueText = finalVal > 0 
       ? fmt.format(finalVal) 
       : (rawAiVal.isNotEmpty && rawAiVal.toLowerCase() != 'pending' ? rawAiVal : '—');
   ```
2. **Badge Rendering Guard (line 3170):**
   ```dart
   final isPendingValuation = valueText == '—' || 
       valueText.toLowerCase().contains('pending') || 
       (m['enrichment_status']?.toString().toLowerCase() == 'pending');

   if (isPendingValuation)
     Container(
       padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
       decoration: BoxDecoration(
         color: const Color(0xFFC9A227).withAlpha(25),
         borderRadius: BorderRadius.circular(4),
         border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
       ),
       child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
     )
   else
     Text(valueText, ...)
   ```

---

## 4. Verification & Test Steps

1. **Unit Test Execution:**
   Run existing asset service tests plus 2 new tests in `numista_mobile/test/canonical_mint_asset_service_test.dart`:
   - Test: `extractSku` correctly extracts `26EA` when title is stored in `'Title'` PascalCase.
   - Test: `resolveFromMap` correctly resolves `2023-D 5c` to `2023-NICKEL-D` with non-empty obverse and reverse URLs.
2. **UI Verification on `p7-gate`:**
   - Load collection view on `p7-gate`.
   - Inspect Card `2026 American Eagle One Ounce Silver Proof Coin`: verify high-resolution Mint reverse photo renders; verify price displays either `$95.00` (Mint issue price) or gold outlined `'Valuation Pending'` chip, never bare unstyled `'Pending'`.
   - Inspect Card `2023-D 5c`: verify Jefferson nickel reverse image renders cleanly without spinner/broken placeholder.

---

## 5. Review & Standing Locks
- **PLAN ONLY.** Zero code modifications committed, zero deployments executed.
- `origin/main` locked at `9f04550a`. Stripe locked OFF.
