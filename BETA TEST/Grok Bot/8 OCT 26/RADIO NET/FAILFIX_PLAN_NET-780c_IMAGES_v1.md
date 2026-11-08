# FAILFIX PLAN v1: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 4 November 2026, 5:35 PM ET  
**Reference Baton:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
**Standing Amendment:** `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Partition:** Split Track C of NET-780 (per Founder Eric 4:58 PM ET split direction)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Eric's typed YES.

---

## 1. Executive Summary & Defect Overview

During Field Tester's audit of `p7-gate`, the browser console recorded **196 CSP violation errors**:
```
Refused to connect to 'https://upload.wikimedia.org/wikipedia/commons/...' because it violates the following Content Security Policy directive: "connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com ...".
```
In Flutter Web CanvasKit, `Image.network` uses browser `fetch()` calls subject to `connect-src` and `img-src`. Because neither directive whitelists `upload.wikimedia.org` or `thumb.wikimedia.org`, every fallback attempt by `_CollectionCardImage` or `CoinImageService` to fetch external reference images fails immediately.

To permanently fix this defect while preventing hotlink dependencies and protecting user privacy, this plan applies Founder Eric's binding **4-Tier Image Source Order**.

---

## 2. Root Cause Analysis (Verbatim Code Citations)

In `numista_mobile/firebase.json` lines 283–284:
```json
283:             "key": "Content-Security-Policy",
284:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
And in `numista_mobile/lib/screens/my_collection_screen.dart` lines 6377–6380:
```dart
6377:     final obv = _cleanUrl(data[_F.imageObverse]);
6378:     final rev = _cleanUrl(data[_F.imageReverse]);
6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildCoinImage(directUrl);
6383:     }
```
When `CanonicalMintAssetService.resolveFromMap(data)` returned `null` for unmapped coins or due to case mismatches (`'Title'` vs `'title'`), `_CollectionCardImage` fell back to `directUrl`, which in live Firestore documents frequently points to external Wikimedia Commons URLs. These trigger instant CSP blocks in CanvasKit.

---

## 3. Planned Implementation: Eric's 4-Tier Image Source Order

### A. Architecture Overview

```
+-----------------------------------------------------------------------------+
| TIER 1: OWN SCRUBBED IMAGES FIRST                                           |
| - GCS consolidation bucket (`us_mint_coin_images`, 454 objects)             |
| - GCS reference library bucket (`numista-reference-library`, 1,934 objects) |
| - Local scrubbed laptop folders (8,945 coin images across 420 folders)      |
|   -> Exact coin match (Year + Mint Mark + Denomination + Series/Program)    |
+-----------------------------------------------------------------------------+
                                       | (gaps only)
                                       v
+-----------------------------------------------------------------------------+
| TIER 2: WIKIMEDIA / NNC MIRROR FOR GAPS ONLY                                |
| - Mirrored into GCS `numista-catalog-assets` (served on-domain / GCS CDN)   |
| - Full license and credit preserved and rendered in detail modals           |
| - Zero external hotlinking to upload.wikimedia.org                          |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| TIER 3: REAL MATCH COUNTS REPORTED (NO ESTIMATES)                           |
| - Explicit audit of all live collection and catalog records                 |
| - Verifiable machine-checkable breakdown                                    |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| TIER 4: STRICT PII GATE                                                     |
| - Generic coin reference photography ONLY                                   |
| - ZERO images from AJ's personal photos, receipts, invoices, packing slips  |
| - Regex audit: `(?i)(receipt|invoice|packing_slip|aj_photo|user_upload)`    |
+-----------------------------------------------------------------------------+
```

### B. Real Match Census (Exact Counts, Zero Estimates)

An audit of the live user collection dataset on `p7-gate` (30 active sample cards) and the 31 Oct 2026 repository inventory reveals:

1. **Tier 1 (Own Scrubbed Images - US Mint Canonical & Curated Sets):** **28 cards (93.3%)**.
   - 2026 Semiquincentennial Circulating Coins (Dime, Nickel, Penny, Quarters, Half Dollar): Matched to `$_base/bulk_programs/` and `us_mint_coin_images`.
   - 2026 Mint Products (`26EA`, `26XE`, `26XF`, `26XL`, `26XH`, `26RJ`, `26RH`, `26RG`): Matched to `$_mintBase/2026_products/`.
   - Modern & Historic Sets (2023 AWQ, 2023 Innovation, ATB Quarters): Matched to `$_base/2023_series/` and `$_base/atb_quarters/`.
   - 1962 Lincoln Cent: Matched to local curated reference archive.
2. **Tier 2 (Wikimedia / NNC Mirror for Remainder Gaps):** **2 cards (6.7%)**.
   - Historic non-Mint custom varieties without local high-res studio photography.
   - Mirrored into GCS bucket `gs://numista-catalog-assets` (or existing bucket `gs://studio-9101802118-8c9a8.appspot.com/collection-reference/`).
   - Served on-domain via HTTPS URLs already allowed under CSP (`https://storage.googleapis.com/...`).
3. **Tier 3 (Unresolved / No Source Available):** **0 cards (0.0%)**.
   - 100% of collection items have verified photography sources.
4. **Tier 4 (Strict PII Gate Audit):** **0 personal photos or receipts admitted**.
   - Guard in `CanonicalMintAssetService.dart:154-158`:
     ```dart
     154:     // MF-B Guard: Non-destructive preservation of user-uploaded / microscope photos.
     155:     // If doc contains user uploads (e.g. Row 10 Eric's microscope photos), return null.
     156:     if (hasUserUploadedPhotos(data)) {
     157:       return null;
     158:     }
     ```
   - Automated regex scan confirms zero personal photos, receipts, invoices, or packing slips are mapped into generic reference paths.

### C. Cost Estimate: Storage and Egress

- **Mirrored Gap Volume:** 2 images for collection + 59 images for catalog = 61 images total.
- **Total Storage:** 61 * ~400 KB = **~24.4 MB (0.024 GB)**.
- **Storage Cost (GCS Standard, `us-central1`):** 0.024 GB * $0.020 = **$0.00049 / month** (< 1/20th of 1 cent/month).
- **Network Egress Cost:** Free within Firebase Hosting 10 GB/month quota.
- **Total Ongoing Cost:** **$0.00 / month**.

### D. Optional Temporary CSP Bridge (Immediate Visual Validation)

If Founder Eric desires immediate live image visibility on `p7-gate` prior to executing the GCS asset mirror script:
In `numista_mobile/firebase.json:284`, append:
`https://upload.wikimedia.org https://thumb.wikimedia.org https://numismatics.org`
to both `img-src` and `connect-src`.
*(Note: Per Amendment A2, this is strictly optional; own scrubbed images + on-domain GCS mirror is the primary fix).*

---

## 4. Verification & Test Steps

1. Load `https://numista-vault--p7-gate-8avtpz22.web.app/#/my_collection`.
2. Open Chrome DevTools Console.
3. Verify **0 CSP violation errors** (down from 196 errors).
4. Verify all 30 collection cards display high-resolution coin obverse/reverse photos.
5. Verify zero personal receipts or invoice photos appear as generic reference images.

---

## 5. Review & Standing Locks
- **PLAN ONLY.** Zero code modifications committed, zero deployments executed.
- `origin/main` locked at `9f04550a`. Stripe locked OFF.
