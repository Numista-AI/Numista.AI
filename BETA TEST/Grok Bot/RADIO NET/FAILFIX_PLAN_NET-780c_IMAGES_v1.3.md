# FAILFIX PLAN v1.3: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 4:35 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`, `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`  
**Standing Amendment:** `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Source Scoring:** `COS_SCORE_NET-805_780b-780c-v1.2_20261105.md` (CoS 86 FAIL / SAG 72 FAIL on v1.2 $\rightarrow$ v1.3 Target $\ge 95$)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & CoS-86 / SAG-72 Resolution Overview

In the v1.2 review, Grok Bot CoS (86 FAIL) and SAG (72 FAIL) confirmed that cert redactions, own-origin allowlist structure, and PII filters were sound, but identified critical defects in image resolution fallback order, archive census verification, rollback target safety, and spend authorization.

**Plan v1.3 systematically resolves all findings:**

1. **Mandatory 4-Tier Image Resolution Order (§3.1 & §4 — CoS & SAG Blocking Must-Fix 3):**
   - In v1.2, a null allowlist result jumped straight to the SVG placeholder, skipping the internal reference library and leaving Card 2 (nickel) blank.
   - **Corrected Pipeline Order:**
     1. **User Photo:** If user-uploaded collection photos exist, render them (never overwritten).
     2. **Allowlisted Own-Origin URL:** If direct URL matches own-origin allowlist (`storage.googleapis.com`, `numista-vault.web.app`, `numista.ai`, `data:`, `blob:`, or root `/assets/`), fetch and display.
     3. **`CoinImageService` Internal Reference Library:** If the direct URL is non-allowlisted (e.g. Wikimedia) or null, pass the item metadata to `CoinImageService` to resolve authentic internal GCS reference imagery (`gs://numista-catalog-assets/reference_images/`). This cleanly resolves Card 2 (2023 Jefferson nickel).
     4. **Local SVG Coin Silhouette Placeholder:** Displayed *only* if `CoinImageService` also returns null or cannot resolve authentic photography.

2. **Repo-Safe Rollback Architecture (§6.A — CoS & SAG Blocking Must-Fix 1):**
   - **Struck `git checkout 9f04550a -- my_collection_screen.dart`.** Commit `9f04550a` is 12 commits behind `p7-v8.9` and would destroy +703 lines of valid work.
   - **Pinned Rollback:** Rollback is pinned strictly to pre-execute `p7-v8.9` commit `a5eeb19b` via `git revert <execute SHA>` or `git checkout a5eeb19b -- <files>`.
   - **GCS Rollback Invariant:** Manifest deactivation guarantees that deactivated manifest keys are never served by client cards or browse screens.

3. **Grounded Inventory Census Matching `docs/MISSING_IMAGES.csv` (§3.2 — CoS & SAG Must-Fix 5):**
   - Struck all unverifiable local machine counts (the `8,836` / `109` / `8,945` split) as unverified.
   - Retained strictly the verified master catalog census: exactly **3,202 master entries** matching `docs/MISSING_IMAGES.csv` (2,354 Tier 1 / 639 Tier 2 / 181 Tier 3 / 1 Tier 4 / 27 Tier 5 Excluded).

4. **Hard $0.00 Spend Cap & Removal of Bulk Mirroring (§3.3, §4, §7 — CoS & SAG Must-Fix 6):**
   - Clarified that this YES authorizes **strictly Dart client code changes** on branch `p7-v8.9` / `dev` (the closed-CSP in-memory guard + reference library fallback).
   - Bulk image mirroring of 3,202 entries is **removed from this YES** and is not authorized. A hard abort is enforced before any `gsutil` or storage mutation call.

5. **Tooling Lifecycle Labeling (§5 — CoS & SAG Non-Blocking):**
   - Explicitly labeled `tools/verify_catalog_manifest_pii.py` as **"create, then run"** so an executor does not assume the script already exists in the tree.

---

## 2. Verbatim Code Citations & CSP Perimeter

### A. Firebase CSP Perimeter (Branch `p7-v8.9`)
In `numista_mobile/firebase.json` lines 275–276:
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' ...; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://storage.googleapis.com ...; ..."
```
The CSP remains 100% closed to outside hosts (`upload.wikimedia.org`, `thumb.wikimedia.org`, `numismatics.org`).

### B. Client Direct URL Intake
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 6377–6383:
```dart
6377:     final obv = _cleanUrl(data[_F.imageObverse]);
6378:     final rev = _cleanUrl(data[_F.imageReverse]);
6379:     final directUrl = rev.isNotEmpty ? rev : obv;
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildCoinImage(directUrl);
6383:     }
```
Direct URLs pointing to unmirrored external hosts trigger browser `fetch()` violations under CanvasKit.

---

## 3. Mandatory Implementation Architecture

### 3.1 4-Tier Image Resolution Order & In-Memory Allowlist Guard
In `_CollectionCardImage` (`my_collection_screen.dart`):

```dart
Widget _buildResolvedCardImage(Map<String, dynamic> data) {
  // 1. User photo check: Never overwrite user's own uploads
  if (hasUserUploadedPhotos(data)) {
    return _buildUserPhotoImage(data);
  }

  // 2. Allowlisted direct URL check
  final obv = _cleanUrl(data[_F.imageObverse]);
  final rev = _cleanUrl(data[_F.imageReverse]);
  final directUrl = rev.isNotEmpty ? rev : obv;
  final allowlistedUrl = sanitizeAndAllowlistUrl(directUrl);
  if (allowlistedUrl != null) {
    return _buildCoinImage(allowlistedUrl);
  }

  // 3. CoinImageService internal reference library resolution
  // (Prevents skipping straight to placeholder; resolves Card 2 Jefferson nickel)
  final referenceAsset = CoinImageService.resolveReferenceAsset(data);
  if (referenceAsset != null && referenceAsset.isNotEmpty) {
    return _buildCoinImage(referenceAsset);
  }

  // 4. Clean local SVG coin silhouette placeholder
  return const _GenericCoinPlaceholderSvg();
}

String? sanitizeAndAllowlistUrl(String? rawUrl) {
  if (rawUrl == null || rawUrl.isEmpty) return null;
  final uri = Uri.tryParse(rawUrl);
  if (uri == null) return null;

  final bool isAllowed = 
      (uri.scheme == 'data' || uri.scheme == 'blob') ||
      (uri.hasScheme == false && rawUrl.startsWith('/')) ||
      (uri.host == 'storage.googleapis.com' && uri.path.startsWith('/numista-catalog-assets/')) ||
      (uri.host == 'numista-vault.web.app') ||
      (uri.host == 'numista.ai');

  return isAllowed ? rawUrl : null;
}
```

### 3.2 Master Catalog Census (`docs/MISSING_IMAGES.csv`)
The standing inventory is 100% synchronized with `docs/MISSING_IMAGES.csv`: exactly **3,202 master entries**:

| Acquisition Tier | Scope & Source | Exact Count | Current Status |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Internal Scrubbed GCS & Staged Laptop Archive | **2,354** | Staged / `MISSING` |
| **Tier 2** | Wikimedia Commons / Smithsonian NNC Mirror | **639** | Staged / `EXTERNAL_MIRROR_PENDING` |
| **Tier 3** | US Mint / BEP Historical Currency Archive | **181** | Staged / `MISSING` |
| **Tier 4** | Numismatic Partner / Studio Photography | **1** | Staged / `MISSING` |
| **Tier 5** | Excluded Private Medals (Franklin Mint / Medallic Art 1932–1976) | **27** | **Excluded from PD Ingestion** |
| **TOTAL** | **Master Catalog Inventory** | **3,202** | **100% Accounted For** |

*(Note: Prior references to local directory counts 8,836 / 109 / 8,945 are classified as unverified and excluded from audit baselines).*

### 3.3 Hard $0.00 Spend Cap & Execution Boundaries
- This YES authorizes **strictly client code fixes** on `p7-v8.9`/`dev`.
- Bulk image mirroring is explicitly removed from this YES and will be executed under a separate authorization.
- Hard abort is enforced before any `gsutil` or storage mutation command.

### 3.4 Licensing & Attribution Manifest (Canonical `NAC1.*` Keys)
Every mirrored image ingested into internal storage must have an associated licensing record in `assets/catalog_image_manifest.json` (*to be created*):
- Primary key: Canonical `NAC1.*` string.
- Approved licenses ONLY: `PD-USGov`, `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`.
- Prohibited licenses: `-NC` (Non-Commercial) and `-ND` (No-Derivatives).
- UI Attribution: Plain text captions only.

### 3.5 Anchored PII Intake Gate
Pre-ingestion regex filter:
```python
PII_EXCLUDE_REGEX = re.compile(
    r'(?i)[\\/](?:receipts|invoices|packing_slips|user_uploads|microscope_photos|personal_collections)[\\/]'
)
```
- Zero collisions with `"American"`, `"Ajax"`, or `"Majestic"`.
- Personal directory prefixes maintained strictly in `.env.local`.

---

## 4. Implementation Steps

1. **Client URL Sanitization & Fallback Order (`my_collection_screen.dart`):**
   Implement `_buildResolvedCardImage` following the strict 4-step sequence (User photo $\rightarrow$ Allowlisted own-origin $\rightarrow$ `CoinImageService` reference library $\rightarrow$ SVG placeholder).
2. **Manifest Tooling & Registry (`tools/` & `assets/`):**
   Create `tools/verify_catalog_manifest_pii.py` to validate metadata and generate `assets/catalog_image_manifest.json` with canonical `NAC1.*` keys.

---

## 5. Verification & Test Steps

1. **Allowlist & Fallback Unit Tests:**
   - Input `https://upload.wikimedia.org/...` $\rightarrow$ `sanitizeAndAllowlistUrl` returns `null` $\rightarrow$ passes to `CoinImageService` $\rightarrow$ resolves reference asset or fallback placeholder with 0 CSP network fetch.
   - Input `https://storage.googleapis.com/numista-catalog-assets/...` $\rightarrow$ returns URL (fetched).
2. **Tooling Execution (Create, Then Run):**
   Create, then run `python tools/verify_catalog_manifest_pii.py` against candidate batches: confirm 0 personal identifiers, 0 receipt paths, and 100% valid `NAC1.*` keys.
3. **Browser Console Check on `p7-gate`:**
   Inspect console on collection grid: confirm **0 CSP violation errors** (down from 196).

---

## 6. Dedicated Rollback Procedures & Standing Locks

### A. Dedicated Rollback Procedures
1. **Repo-Safe Code Revert:**
   Revert target files cleanly to pre-execute `p7-v8.9` commit `a5eeb19b`:
   ```bash
   git revert <execute SHA>
   ```
   Or to discard uncommitted working tree changes:
   ```bash
   git checkout a5eeb19b -- numista_mobile/lib/screens/my_collection_screen.dart
   ```
   *(Locked main commit `9f04550a` is strictly forbidden as a file restore target).*
2. **GCS Manifest Rollback Invariant:**
   Deactivated manifest keys are guaranteed to never be served by client cards or catalog browse screens.
3. **Execution Boundary:** This YES authorizes strictly code fixes on branch `p7-v8.9`/`dev`. Zero deployments to production `numista-vault.web.app` without Preview Channel sign-off and separate typed YES.

### B. Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF.
- Zero Firestore database writes, seeding, or security rules changes.
- Hard $0.00 spend cap (hard abort before any storage mutation call).
