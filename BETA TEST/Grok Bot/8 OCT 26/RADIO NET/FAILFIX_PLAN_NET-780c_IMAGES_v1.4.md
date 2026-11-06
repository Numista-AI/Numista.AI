# FAILFIX PLAN v1.4: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 7:25 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`, `BATON_NET-809_REVISE_780b-780c_v1.3_PER-COS-86-SAG-72_2026-11-05-1600.md`, `BATON_NET-812_REVISE_780b-780c_v1.4_PER-COS-83-SAG-58_2026-11-05-1705.md`  
**Standing Amendment:** `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Source Scoring:** `COS_SCORE_NET-809_780b-780c-v1.3_20261105.md` (CoS 83 FAIL), `SAG_SCORE_NET-809_20261105.md` (SAG 58 FAIL) $\rightarrow$ v1.4 Target $\ge 95$  
**Protocol Update:** Argon Reviewer DROPPED per Founder Eric YES 6:07 PM ET 5 Nov FIN OPS. Plan review sequence: AG CoS v4 $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & CoS-83 / SAG-58 Resolution Overview

In the v1.3 review of NET-809, Grok Bot CoS (83 FAIL) and SAG (58 FAIL) validated the 3,202 master census, absence of AJ PII, and $0.00 spend cap. However, both reviewers identified critical blockers:
- In v1.3, `_CollectionCardImage` invoked `CoinImageService.resolveReferenceAsset(data)`, which does not exist in the repository.
- `CanonicalMintAssetService.resolveFromMap(data)` was bypassed, preventing 26EA canonical mint resolution.
- Undefined helper methods (`_buildUserPhotoImage`, `_GenericCoinPlaceholderSvg`) and bare `hasUserUploadedPhotos` were specified.
- The own-origin allowlist was overly restrictive (allowing only `numista-catalog-assets`), rejecting real first-party assets on `storage.googleapis.com/numista-reference-library/` and user uploads on `numista-uploads-studio-*`.
- Rollback cited `a5eeb19b` instead of pre-execute HEAD `4c97c7f0`, and GCS deactivation rollback was asserted under a $0/no-cloud YES.

**Plan v1.4 systematically resolves all findings:**

1. **Implementable Real-API Image Pipeline (§3.1 — CoS & SAG Must-Fix 2 & 3):**
   - Struck imaginary `CoinImageService.resolveReferenceAsset(data)` completely.
   - Grounded the fallback on the real async repository API:
     `CoinImageService.fetchReferenceImages(year:, mint:, denomination:, series:, subject:)` returning `Future<CoinImageResult>`.
   - Wired with Flutter's real `FutureBuilder<CoinImageResult>` handling loading spinner, obverse/reverse resolution, and fallback.
   - Defined local placeholder as:
     `const Center(child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)))`.

2. **Strict 5-Step Resolution Precedence Preserving 26EA (§3.1 — SAG Must-Fix 3):**
   - **Step 1 (User Photos First):** Check `CanonicalMintAssetService.hasUserUploadedPhotos(data)`. If true, extract direct user photo URLs (`imageReverse`, `imageObverse`, `image_url_reverse`, `image_url_obverse`), validate against allowlist, and display via `_buildCoinImage()`.
   - **Step 2 (Canonical Mint Resolution):** Call `CanonicalMintAssetService.resolveFromMap(data)`. If non-null, display canonical obverse/reverse asset via `_buildCoinImage()`. (Ensures 26EA American Eagle and Semiquincentennial assets are properly applied).
   - **Step 3 (Allowlisted Own-Origin Direct URLs):** If non-user direct URL matches own-origin allowlist, display via `_buildCoinImage()`. Rejects external URLs before network fetch.
   - **Step 4 (Internal Reference Library via `FutureBuilder`):** Query `CoinImageService.fetchReferenceImages(...)`. If resolved and allowlisted, display via `_buildCoinImage()`.
   - **Step 5 (Placeholder):** If all above yield null or empty, display defined silhouette icon placeholder.

3. **Expanded Own-Origin Allowlist Matching Real Buckets & CSP (§2.A & §3.2 — CoS Must-Fix 3):**
   - Aligned strictly with `numista_mobile/firebase.json` line 276 CSP (`img-src`).
   - Allowed origins:
     - `https://storage.googleapis.com` with verified bucket paths:
       - `/numista-reference-library/` (official Mint + reference library assets)
       - `/numista-catalog-assets/` (catalog assets)
       - `/numista-uploads-studio-` / `studio-9101802118-8c9a8-uploads` (authenticated user uploads)
     - `'self'` / `numista-vault.web.app`
     - Data URIs: `data:image/`
     - Blob URIs: `blob:`
     - Local asset paths: `/assets/`
   - Explicitly rejects external domains (`upload.wikimedia.org`, `thumb.wikimedia.org`, `numismatics.org`) before any network fetch occurs.
   - Removed `numista.ai` from CSP assumptions (not present in `firebase.json` `img-src`).

4. **Rollback Pinned to Pre-Execute HEAD `4c97c7f0` (§5.A — CoS & SAG Must-Fix 1):**
   - Pinned pre-execute SHA to `4c97c7f0`. Rollback command is `git revert <execute commit set>` restoring `p7-v8.9` to `4c97c7f0`.
   - Never checks out `9f04550a` or old file revisions.
   - Removed guaranteed GCS manifest deactivation claim under this $0/no-cloud YES.

5. **Scope Truth & Hard $0 Spend (§3.3 & §6 — CoS Must-Fix 4):**
   - Manifest/registry creation and bulk image scraping/mirroring are strictly out of scope of this YES. They belong to a separately approved ingest plan.
   - Any local verification tool (e.g. `tools/verify_catalog_manifest_pii.py`) is bounded as local-only $0 tooling without cloud mutations.
   - Zero deployments, zero Firestore writes.

---

## 2. Verbatim Code Citations & CSP Perimeter

### A. Firebase CSP Perimeter (Branch `p7-v8.9`)
In `numista_mobile/firebase.json` line 276:
```json
275:            "key": "Content-Security-Policy",
276:            "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
**Verification:** `img-src` allows `'self'`, `data:`, `blob:`, `https://storage.googleapis.com`, `https://*.googleusercontent.com`, `https://*.gstatic.com`, `https://*.run.app`. Third-party domains (such as Wikimedia) are blocked by CanvasKit CSP. `numista.ai` is not listed in `img-src`.

### B. Client Direct URL Intake & Image Resolution
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 6367–6406:
```dart
6367:   @override
6368:   Widget build(BuildContext context) {
6369:     final canon = CanonicalMintAssetService.resolveFromMap(data);
6370:     if (canon != null) {
6371:       final canonUrl = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
6372:       if (canonUrl.isNotEmpty) {
6373:         return _buildCoinImage(canonUrl);
6374:       }
6375:     }
6376: 
6367:     final obv = _cleanUrl(data[_F.imageObverse]);
6378:     final rev = _cleanUrl(data[_F.imageReverse]);
6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildCoinImage(directUrl);
6383:     }
...
6399:     return FutureBuilder<CoinImageResult>(
6400:       future: CoinImageService.fetchReferenceImages(
6401:         year: year,
6402:         mint: mint.isEmpty ? null : mint,
6403:         denomination: denom.isEmpty ? null : denom,
6404:         series: series.isEmpty ? null : series,
6405:         subject: subject.isEmpty ? null : subject,
6406:       ),
```
**Defects in Existing Implementation:**
1. Lines 6369–6375 execute `CanonicalMintAssetService.resolveFromMap(data)` before checking for direct user uploads, which can override personal user photos if `resolveFromMap` does not return null.
2. Lines 6377–6383 feed `directUrl` into `_buildCoinImage(directUrl)` using only `_cleanUrl` (which only checks `!s.startsWith('http')`), allowing un-allowlisted Wikimedia URLs through to trigger CSP errors.

---

## 3. Mandatory Implementation Architecture

### 3.1 5-Step Image Resolution Precedence in `_CollectionCardImage`
In `numista_mobile/lib/screens/my_collection_screen.dart`:

```dart
class _CollectionCardImage extends StatelessWidget {
  final Map<String, dynamic> data;
  const _CollectionCardImage({required this.data});

  /// Validates that a URL matches approved own-origin first-party infrastructure.
  /// Rejects third-party hosts (e.g. upload.wikimedia.org) before any network fetch.
  static String? _sanitizeAndAllowlistUrl(dynamic val) {
    if (val == null) return null;
    final s = val.toString().trim();
    if (s.isEmpty || s.startsWith('gs://')) return null;

    // Allow data and blob URIs
    if (s.startsWith('data:image/') || s.startsWith('blob:')) return s;

    // Allow local assets
    if (s.startsWith('/assets/') || s.startsWith('assets/')) return s;

    final uri = Uri.tryParse(s);
    if (uri == null || !uri.hasScheme || !uri.hasAuthority) return null;
    if (uri.scheme != 'http' && uri.scheme != 'https') return null;

    final host = uri.host.toLowerCase();
    final path = uri.path.toLowerCase();

    // 1. Google Cloud Storage approved buckets
    if (host == 'storage.googleapis.com') {
      if (path.startsWith('/numista-reference-library/') ||
          path.startsWith('/numista-catalog-assets/') ||
          path.startsWith('/numista-uploads-studio-') ||
          path.startsWith('/studio-9101802118-8c9a8-uploads/')) {
        return s;
      }
      return null;
    }

    // 2. Firebase hosting own-origin
    if (host == 'numista-vault.web.app' || host == 'numista-vault.firebaseapp.com') {
      return s;
    }

    // Explicitly reject all other hosts (e.g. upload.wikimedia.org, numismatics.org)
    return null;
  }

  Widget _buildPlaceholder() {
    return const Center(
      child: Icon(Icons.image_not_supported_outlined, size: 36, color: Color(0xFF8B92B4)),
    );
  }

  @override
  Widget build(BuildContext context) {
    // STEP 1: Preserve user-uploaded collection photos first (never overwrite)
    if (CanonicalMintAssetService.hasUserUploadedPhotos(data)) {
      final userRev = _sanitizeAndAllowlistUrl(data[_F.imageReverse] ?? data['image_url_reverse'] ?? data['stored_rev']);
      final userObv = _sanitizeAndAllowlistUrl(data[_F.imageObverse] ?? data['image_url_obverse'] ?? data['stored_obv']);
      final userUrl = userRev ?? userObv;
      if (userUrl != null) {
        return _buildCoinImage(userUrl);
      }
    }

    // STEP 2: Canonical Mint resolution (26EA American Eagle, Semiquincentennial, etc.)
    final canon = CanonicalMintAssetService.resolveFromMap(data);
    if (canon != null) {
      final canonRaw = canon.reverseUrl.isNotEmpty ? canon.reverseUrl : canon.obverseUrl;
      final canonUrl = _sanitizeAndAllowlistUrl(canonRaw);
      if (canonUrl != null) {
        return _buildCoinImage(canonUrl);
      }
    }

    // STEP 3: Direct URL check with strict own-origin allowlist
    final obv = _sanitizeAndAllowlistUrl(data[_F.imageObverse]);
    final rev = _sanitizeAndAllowlistUrl(data[_F.imageReverse]);
    final directUrl = rev ?? obv;
    if (directUrl != null) {
      return _buildCoinImage(directUrl);
    }

    // STEP 4: CoinImageService internal reference library resolution (async FutureBuilder)
    String dualRead(String snakeKey, String legacyKey) {
      final s = data[snakeKey]?.toString();
      if (s != null && s.trim().isNotEmpty && s.trim() != 'None' && s.trim() != 'null') return s.trim();
      final l = data[legacyKey]?.toString();
      if (l != null && l.trim().isNotEmpty && l.trim() != 'None' && l.trim() != 'null') return l.trim();
      return '';
    }
    final year = dualRead('year', _F.year).replaceAll(RegExp(r'\.0$'), '');
    final mint = dualRead('mint_mark', _F.mintMark);
    final denom = dualRead('denomination', _F.denomination);
    final series = dualRead('program_series', _F.programSeries);
    final subject = dualRead('theme_subject', _F.themeSubject);

    return FutureBuilder<CoinImageResult>(
      future: CoinImageService.fetchReferenceImages(
        year: year,
        mint: mint.isEmpty ? null : mint,
        denomination: denom.isEmpty ? null : denom,
        series: series.isEmpty ? null : series,
        subject: subject.isEmpty ? null : subject,
      ),
      builder: (context, snapshot) {
        final ref = snapshot.data;
        final rawRefUrl = (ref?.reverseUrl?.isNotEmpty == true)
            ? ref!.reverseUrl!
            : (subject.isEmpty && ref?.obverseUrl?.isNotEmpty == true)
                ? ref!.obverseUrl!
                : '';
        final refUrl = _sanitizeAndAllowlistUrl(rawRefUrl);

        if (refUrl != null) {
          return _buildCoinImage(refUrl);
        }

        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Center(
            child: SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Color(0xFFC9A227),
              ),
            ),
          );
        }

        // STEP 5: Generic coin silhouette placeholder
        return _buildPlaceholder();
      },
    );
  }
}
```

### 3.2 Master Inventory Census Alignment
The repository image census is grounded strictly on `docs/MISSING_IMAGES.csv`:
- **Total Master Entries:** Exactly **3,202 entries**.
- **Breakdown:** 2,354 Tier 1 (US Mint) / 639 Tier 2 (PCGS/NGC) / 181 Tier 3 (Numista/Heritage) / 1 Tier 4 (Auction Archives) / 27 Tier 5 Excluded.
- All non-allowlisted images in this census are safely intercepted at client runtime by Step 3 / Step 4, falling back to authentic internal reference library assets or the local placeholder, guaranteeing zero CanvasKit CSP violations.

### 3.3 Scope & Tooling Boundaries
1. **$0.00 Local Tooling Boundary:** Any validation script (e.g. `tools/verify_catalog_manifest_pii.py`) must be executed strictly locally in read-only mode against repo files. No network calls, no GCS writes, no Cloud Run calls.
2. **Bulk Ingest / Mirroring Out of Scope:** Manifest ingestion, bulk scraping, and Cloud Storage upload jobs are explicitly deferred to a dedicated, separately approved ingest plan.

---

## 4. Verification Test Cases

| Test ID | Input Scenario | Expected Pipeline Behavior | Assertion Command |
|---|---|---|---|
| **T-780c-1** | User-uploaded photo in `image_url_reverse` on `numista-uploads-studio-*` | STEP 1 preserves photo; `_buildCoinImage` called with user URL | `flutter test test/collection_card_image_test.dart -n "user photo preserved first"` |
| **T-780c-2** | 2026 American Eagle record matching SKU `26EA` | STEP 2 applies `resolveFromMap`; canonical mint URL rendered | `flutter test test/collection_card_image_test.dart -n "canonical 26EA resolved"` |
| **T-780c-3** | External Wikimedia URL `https://upload.wikimedia.org/...` | STEP 3 allowlist rejects URL; STEP 4 queries `CoinImageService`; NO external fetch | `flutter test test/collection_card_image_test.dart -n "wikimedia url rejected by allowlist"` |
| **T-780c-4** | 2023-D Jefferson Nickel (Card 2) | Resolves authentic reference image from `numista-reference-library` via STEP 4 | `flutter test test/collection_card_image_test.dart -n "2023 nickel resolves reference image"` |
| **T-780c-5** | Unresolvable coin metadata | STEP 5 renders `Icons.image_not_supported_outlined` placeholder | `flutter test test/collection_card_image_test.dart -n "unresolved falls back to placeholder"` |

---

## 5. Rollback Architecture & Failsafes

### A. Rollback Protocol
- **Pre-Execute Pinned SHA:** `p7-v8.9` at commit `4c97c7f0`.
- **Rollback Command:**
  ```bash
  git revert --no-edit <EXECUTE_COMMIT_SHAS>
  ```
- If clean tree restoration is needed prior to commit:
  ```bash
  git checkout 4c97c7f0 -- numista_mobile/lib/screens/my_collection_screen.dart
  ```
- **Strict Invariants:**
  1. Never run `git checkout 9f04550a -- <files>` (would destroy +703 lines of valid work).
  2. Never checkout stale `a5eeb19b` as branch rollback.
  3. No cloud mutations or GCS manifest operations exist under this YES; no cloud deactivation rollback is needed or claimed.

### B. Spend & Safety Fence
- Authorizes **strictly Dart client modifications** on branch `p7-v8.9`.
- **$0.00 Total Spend Cap:** No external API queries, no Google Cloud mutations, no Firebase Hosting deployments.
- `origin/main` strictly locked at `9f04550a`. Stripe strictly OFF.

---

## 6. Sign-off Matrix

| Reviewer | Target Score | Review Chain Order |
|---|---|---|
| **Antigravity CoS v4** | Author | Step 1 (Filed) |
| **Grok Bot CoS** | $\ge 95$ | Step 2 (Mandatory Gate) |
| **Stand Alone Grok (SAG, grok-4.7)** | $\ge 95$ | Step 3 (Mandatory Independent Gate) |
| **Argon (Gemini 3.8)** | **DROPPED** | Per Founder Eric YES 6:07 PM ET 5 Nov FIN OPS |
| **Founder Eric** | Typed YES | Step 4 (Sole Authorization for Code Execution) |
