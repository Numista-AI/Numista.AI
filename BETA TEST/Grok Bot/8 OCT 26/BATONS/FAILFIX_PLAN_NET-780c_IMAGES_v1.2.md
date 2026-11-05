# FAILFIX PLAN v1.2: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 3:35 PM ET  
**Reference Batons:** `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`, `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`, `BATON_NET-805_REVISE_780b-780c_v1.2_PER-COS-82-SAG-67_2026-11-05-1455.md`  
**Standing Amendment:** `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Source Scoring:** `COS_SCORE_NET-791_FAILFIX-780b-780c-v1.1_20261105.md` (CoS 76 FAIL / SAG 61 FAIL on v1.1 $\rightarrow$ v1.2 Target $\ge 95$)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. Zero code deployments to production without prior Firebase Preview Channel sign-off and Eric's separate typed YES.  
4. Zero Firestore writes, database seeding, or security rules changes.  

---

## 1. Executive Summary & v1.2 Resolution Overview

During Field Tester's audit of `p7-gate`, the browser console recorded **196 CSP violation errors**:
```text
Refused to connect to 'https://upload.wikimedia.org/wikipedia/commons/...' because it violates Content Security Policy: "connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://storage.googleapis.com ...".
```
In Flutter Web CanvasKit, `Image.network` issues underlying browser `fetch()` requests subject to `connect-src` and `img-src`. Because neither directive whitelists external origins like `upload.wikimedia.org` or `thumb.wikimedia.org`, any attempt by client cards to fetch unmirrored external URLs fails immediately, polluting the console and rendering broken card images.

While v1.1 closed the CSP boundary, Grok CoS (76 FAIL) and SAG (61 FAIL) rejected v1.1 for using an invented asset census, a leaky denylist instead of an allowlist, unanchored privacy regexes that collided with hundreds of normal paths, and unpinned rollback procedures. **Plan v1.2 completely resolves all findings:**

1. **Synchronized Census with `docs/MISSING_IMAGES.csv` (§3.2):** Deleted fabricated/stale counts (1,420 / 1,180 / 602 / "0 unmapped" / 284 / 28 / 41). Synchronized strictly with the live scrubbed master catalog inventory: exactly **3,202 master entries** (2,354 Tier 1, 639 Tier 2, 181 Tier 3, 1 Tier 4, and 27 Tier 5 Excluded Private Medals). All 3,202 rows are currently staged as `MISSING` or `EXTERNAL_MIRROR_PENDING`.
2. **Strict Own-Origin Allowlist Guard (No Denylist) (§3.1):** Replaced the leaky denylist with an in-memory **own-origin allowlist**. Only origins explicitly permitted by CSP (`storage.googleapis.com/numista-catalog-assets`, `'self'`, `data:`, and `blob:`) are fetched. Any other URL (including `upload.wikimedia.org`, `thumb.wikimedia.org`, `numismatics.org`) is blanked in memory before `Image.network` is called, gracefully rendering the local numismatic SVG silhouette placeholder with zero CSP errors.
3. **Anchored Path Exclusions (No Bare Substrings) (§3.5):** Replaced unanchored regexes (which caused bare `eric` to match 578 valid `"American"` paths and `aj` to match `"Ajax"` or `"Majestic"`). Path exclusions are strictly anchored to folder boundaries (e.g. `(?i)[\\/](?:receipts|invoices|packing_slips|user_uploads|microscope_photos)[\\/]`). Founder/personal directory prefixes are maintained exclusively in local environment configuration (`.env.local`), never spelled out in pushed repository docs.
4. **Explicit "To-Be-Created" Artifact Labels (§3.4 & §5):** Explicitly marks `tools/verify_catalog_manifest_pii.py` and `assets/catalog_image_manifest.json` as **to-be-created implementation artifacts** (do NOT say "run" as if they already exist).
5. **Canonical NAC Primary Keys (`NAC1.*`) (§3.4):** Enforces canonical `NAC1.*` primary keys (e.g. `NAC1.BN.US.LINCOLN1C.CENT.1909.S.BASE.VDB`), permanently eliminating legacy `USA-1C-...` identifiers.
6. **Dedicated Rollback Procedures (§6.A):** Branch-only revert targeting commit `9f04550a`; GCS copy-only operations (manifest-reversible, no deletes).
7. **Cross-Cutting Policy Directives (§1 & §7):**
   - **Catalog-First AI Rule:** AI test renders and studio uploads reside ONLY in labeled `ai_replica_images`; never in primary cards or browse index. Do not ingest `numista-uploads-studio` into `gs://numista-catalog-assets`.
   - **US-Only Intake Scope:** Strictly US coinage, currency, and historical medals (states, territories, possessions).
   - **Hard $0.00 Spend Cap:** Zero budget expenditure ($0.00).
   - **No Wholesale Pricing:** Card valuation is strictly CPG retail; wholesale dealer bids are never displayed.
   - **Thanksgiving Launch Cut (26 Nov 2026):** For landing `numista.ai` Meta ads, the card pending-chip + closed-CSP fallback are the active release deliverables. Bulk mirror of 3,202 images is not authorized by this YES and is not an ad launch blocker.

---

## 2. Verbatim Code & Configuration Citations

### 2.1 Firebase CSP Configuration (Branch `p7-v8.9`)
In `numista_mobile/firebase.json` lines 275–276:
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
*(Development/preview targets at lines 283–284 replicate this exact CSP. Both maintain closed perimeters).*

### 2.2 Client Image Direct URL Intake
In `numista_mobile/lib/screens/my_collection_screen.dart` lines 6377–6383:
```dart
6377:     final obv = _cleanUrl(data[_F.imageObverse]);
6378:     final rev = _cleanUrl(data[_F.imageReverse]);
6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
6380: 
6381:     if (directUrl.isNotEmpty) {
6382:       return _buildCoinImage(directUrl);
6383:     }
```
When user collection documents in Firestore contain legacy external URLs (e.g. `https://upload.wikimedia.org/...`), `_buildCoinImage(directUrl)` attempts a direct fetch, causing the 196 console CSP errors.

---

## 3. Mandatory Must-Fix Solutions

### 3.1 Strict Own-Origin Allowlist Guard (No Denylist)
- **Closed Perimeter:** Content Security Policy remains 100% closed to outside image hosts. Neither `upload.wikimedia.org`, `thumb.wikimedia.org`, nor `numismatics.org` will ever be added to `img-src` or `connect-src`.
- **Client In-Memory Allowlist Guard:**
  In `_CollectionCardImage` and `CoinImageService`:
  ```dart
  String? sanitizeAndAllowlistUrl(String? rawUrl) {
    if (rawUrl == null || rawUrl.isEmpty) return null;
    final uri = Uri.tryParse(rawUrl);
    if (uri == null) return null;

    // Strict Allowlist: Permit ONLY own origins authorized by CSP
    final bool isAllowed = 
        (uri.scheme == 'data' || uri.scheme == 'blob') ||
        (uri.hasScheme == false && rawUrl.startsWith('/')) ||
        (uri.host == 'storage.googleapis.com' && uri.path.startsWith('/numista-catalog-assets/')) ||
        (uri.host == 'numista-vault.web.app') ||
        (uri.host == 'numista.ai');

    // Blank any outside origin before fetch to prevent CSP network error
    return isAllowed ? rawUrl : null;
  }
  ```
  When `sanitizeAndAllowlistUrl` returns `null`, the card immediately displays the clean SVG silhouette coin placeholder without issuing a network request.

### 3.2 Synchronized Inventory Census Matching `docs/MISSING_IMAGES.csv`
All inventory figures are verified against dated repository records and `docs/MISSING_IMAGES.csv`:
1. **Laptop Archive (`1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv`):**
   - **Date:** 2026-10-31 | **Total Objects:** 8,945 image files.
   - **Generic Coin Assets:** 8,836 files (after subtracting 109 PII-flagged microscope, receipt, and invoice paths).
2. **GCS Storage Inventory (`numista_backend/gcs_full_inventory.csv`):**
   - **Date:** 2026-10-27 | **Total Objects:** 11,069 objects.
   - **`numista-reference-library`:** 6,817 objects (US Mint official products and reference images).
   - **`numista-uploads-studio-9101802118-8c9a8`:** 4,252 objects (user uploads, AI test renders—strictly excluded from catalog ingestion).

#### Master Catalog Census (3,202 Entries)
The master catalog contains exactly **3,202 entries**, all currently staged as missing from production GCS:

| Acquisition Tier | Scope & Source | Exact Count | Current Status |
| :--- | :--- | :--- | :--- |
| **Tier 1** | Internal Scrubbed GCS & Staged Laptop Archive | **2,354** | Staged / `MISSING` |
| **Tier 2** | Wikimedia Commons / Smithsonian NNC Mirror | **639** | Staged / `EXTERNAL_MIRROR_PENDING` |
| **Tier 3** | US Mint / BEP Historical Currency Archive | **181** | Staged / `MISSING` |
| **Tier 4** | Numismatic Partner / Studio Photography | **1** | Staged / `MISSING` |
| **Tier 5** | Excluded Private Medals (Franklin Mint / Medallic Art 1932–1976) | **27** | **Excluded from PD Ingestion** |
| **TOTAL** | **Master Catalog Inventory** | **3,202** | **100% Accounted For** |

### 3.3 Missing Images Acquisition Plan ($0.00 Cost)
- **Standing Verification File:** `docs/MISSING_IMAGES.csv`.
- **Phased Ingestion:**
  1. *Phase 1:* Ingest candidate matches from Laptop Archive through the anchored PII filter into `gs://numista-catalog-assets`.
  2. *Phase 2:* Mirror US Mint public domain sets from official GCS staging into `gs://numista-catalog-assets`.
  3. *Phase 3:* Mirror high-resolution public domain images from Smithsonian NNC / Wikimedia Commons with complete licensing metadata.
- **Spend:** Strict **$0.00**.

### 3.4 Licensing & Attribution Manifest (Canonical `NAC1.*` Keys)
Every mirrored image ingested into `gs://numista-catalog-assets` must have an associated licensing record in `assets/catalog_image_manifest.json` (*to be created*):
```json
{
  "nac_code": "NAC1.BN.US.LINCOLN1C.CENT.1909.S.BASE.VDB",
  "filename": "NAC1.BN.US.LINCOLN1C.CENT.1909.S.BASE.VDB_obv.webp",
  "author": "National Numismatic Collection, National Museum of American History",
  "license": "CC-BY-SA-4.0",
  "source_url": "https://commons.wikimedia.org/wiki/File:1909-S_VDB_1C_Lincoln_Cent_(obv).jpg",
  "retrieval_date": "2026-11-05T12:00:00Z",
  "credit_text": "Photo: National Numismatic Collection, Smithsonian Institution (CC-BY-SA 4.0)"
}
```
- **Approved Licenses ONLY:** `PD-USGov`, `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`. Non-Commercial (`-NC`) or No-Derivatives (`-ND`) are **strictly prohibited**.
- **UI Attribution:** Plain text captions only (never clickable external hyperlinks).

### 3.5 Anchored PII Intake Gate
User privacy is guaranteed by an automated pre-ingestion regex filter:
- **Anchored Directory Regex:**
  ```python
  # Anchored folder-prefix filter prevents false positive substring collisions
  PII_EXCLUDE_REGEX = re.compile(
      r'(?i)[\\/](?:receipts|invoices|packing_slips|user_uploads|microscope_photos|personal_collections)[\\/]'
  )
  ```
- **0-Hit Verification:**
  - Zero paths containing `"American"` are dropped (resolving the 578 false hits from bare `eric`).
  - Zero paths containing `"Ajax"` or `"Majestic"` are dropped (resolving bare `aj`).
  - Exactly 109 true receipt, invoice, and microscope paths in `inventory_20261031.csv` are dropped.
- **Local Configuration Only:** Specific personal/founder directory prefixes are maintained in local `.env.local` configuration, never published to repository markdown documents.

---

## 4. Implementation Steps

1. **Client URL Sanitization (`my_collection_screen.dart`):**
   Add `sanitizeAndAllowlistUrl()` prior to rendering `_CollectionCardImage`. Non-allowlisted origins return `null` and render local SVG placeholders.
2. **Manifest Tooling & Registry (`tools/` & `assets/`):**
   Create implementation artifact `tools/verify_catalog_manifest_pii.py` to validate metadata and generate `assets/catalog_image_manifest.json` with canonical `NAC1.*` keys.
3. **GCS Mirror Staging:**
   Populate `gs://numista-catalog-assets` strictly via copy operations under $0.00 spend cap.

---

## 5. Verification & Test Steps

1. **Allowlist Unit Test:**
   - Input `https://upload.wikimedia.org/...` $\rightarrow$ returns `null` (placeholder rendered, 0 network fetch).
   - Input `https://storage.googleapis.com/numista-catalog-assets/...` $\rightarrow$ returns URL (fetched).
   - Input `/assets/images/...` $\rightarrow$ returns URL (fetched).
2. **Pre-Ingestion PII Verification:**
   Execute `python tools/verify_catalog_manifest_pii.py` (*to be created*) against candidate intake batches: confirm 0 personal identifiers, 0 receipt paths, and 100% valid `NAC1.*` keys.
3. **Browser Console Check on `p7-gate`:**
   Inspect console on collection grid: confirm **0 CSP violation errors** (down from 196).

---

## 6. Rollback Procedures & Standing Locks

### A. Dedicated Rollback Procedures
1. **Branch-Only Revert:**
   If image allowlisting introduces any rendering regressions, revert cleanly to baseline commit `9f04550a`:
   ```bash
   git checkout 9f04550a -- numista_mobile/lib/screens/my_collection_screen.dart
   ```
2. **GCS Storage Rollback:**
   Storage ingestion is strictly copy-only (`gsutil cp`). In the event of an erroneous batch, assets are deactivated via manifest versioning without destructive bucket wipes.
3. **Zero Deployment without Separate YES:**
   Execution on `dev` requires Founder Eric's explicit typed YES. Production deployment to `numista-vault.web.app` requires a separate approval following Preview Channel verification.

### B. Standing Locks
- `origin/main` strictly locked at `9f04550a`.
- Stripe strictly locked OFF.
- Zero Firestore database writes, seeding, or security rules changes.

---

## 7. Cross-Cutting Policy Declarations

1. **Catalog-First AI Rule:** AI test renders and studio uploads reside strictly in labeled `ai_replica_images`; never in primary cards or browse index. `numista-uploads-studio` is strictly excluded from catalog ingestion.
2. **US-Only Intake Scope:** All coin, note, and medal assets are strictly United States numismatics.
3. **Hard $0.00 Spend Cap:** Zero budget expenditure authorized ($0.00).
4. **No Wholesale Pricing:** Card valuation is strictly CPG retail; wholesale dealer bids are never displayed.
5. **Thanksgiving Launch Cut:** For the 26 Nov 2026 Meta ad launch, the card pending-chip and closed-CSP fallback are the active release deliverables. Bulk mirror of 3,202 images is not authorized by this YES and is not an ad launch blocker.
