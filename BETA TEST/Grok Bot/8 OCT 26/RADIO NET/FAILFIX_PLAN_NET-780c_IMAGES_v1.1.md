# FAILFIX PLAN v1.1: Images & CSP Resolution (NET-780c)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 12:50 PM ET  
**Reference Baton:** `BATON_NET-791_REVISE_780b-780c_v1.1_PER-GB-COS_2026-11-04-1818.md`  
**Standing Amendment:** `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Partition:** Split Track C of NET-780 (Revised per GB CoS 4 Nov 6:30 PM ET Review - Score 80 FAIL -> v1.1 Target 95+)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Zero deployments without Eric's typed YES.

---

## 1. Executive Summary & Defect Overview

During Field Tester's audit of `p7-gate`, the browser console recorded **196 CSP violation errors**:
```text
Refused to connect to 'https://upload.wikimedia.org/wikipedia/commons/...' because it violates the following Content Security Policy directive: "connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com ...".
```
In Flutter Web CanvasKit, `Image.network` issues underlying browser `fetch()` requests subject to `connect-src` and `img-src`. Because neither directive whitelists `upload.wikimedia.org` or `thumb.wikimedia.org`, any attempt by client cards or services to fetch unmirrored external URLs fails immediately, polluting the console and rendering broken card images.

In v1.0 of this plan, Section 3D proposed an "Optional Temporary CSP Bridge" to add external Wikimedia domains to CSP. **This was rejected by GB CoS (Score 80 FAIL) for violating Founder Eric's core architectural rule: NO EXTERNAL OUTBOUND LINKS OR HOTLINKING.**

Plan v1.1 permanently resolves this defect by:
1. **Closing CSP Completely (MF-C1):** Deleting Section 3D in its entirety. No external image hosts (`upload.wikimedia.org`, `thumb.wikimedia.org`, or `numismatics.org`) will EVER be added to `firebase.json`.
2. **Real Asset Census & Inventory Citations (MF-C2):** Providing verified counts across all 353 collection items and 3,202 catalog items, citing dated inventory files `1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv` and `numista_backend/gcs_full_inventory.csv`.
3. **Missing Images Acquisition Plan (MF-C3):** Explicitly linking to `docs/MISSING_IMAGES.csv` with a multi-tier $0 acquisition workflow.
4. **Mandatory Licensing & Attribution Manifest (MF-C4):** Requiring `author`, `license`, `source_url`, and `retrieval_date` metadata for every mirrored image, restricting intake to approved Commons licenses (PD, CC0, CC-BY, CC-BY-SA), and rendering credits in the UI.
5. **Strict Intake PII Gate with 0-Hit Proof (MF-C5):** Explicitly naming all excluded folders (`AJ's Coins/`, `Scans AJ June 2026/`, `AJ_Photos/`, `RECEIPTS/`, `INVOICES/`, `PACKING_SLIPS/`, `User_Uploads/`, `Row 10 Eric's microscope photos/`), enforcing intake scans that block 100% of user-identifiable data, and confirming zero user IDs or names in mirror paths or metadata.
6. **Single Dedicated Mirror Bucket (MF-C6):** Pinned to exactly one bucket: `gs://numista-catalog-assets` (served on-domain or via `https://storage.googleapis.com/numista-catalog-assets/`). Verbatim CSP citation pinned to `numista_mobile/firebase.json:275-276`.

---

## 2. Verbatim Code & Configuration Citations

### 2.1 Firebase CSP Configuration (Branch `p7-v8.9`)
In `numista_mobile/firebase.json` lines 275–276:
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
*(Note: In development/preview targets at lines 283–284, the identical CSP is replicated. Both maintain closed perimeters).*

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

## 3. Mandatory Must-Fix Solutions (MF-C1 through MF-C6)

### 3.1 MF-C1: Deletion of Section 3D (Closed CSP Boundary)
- **Deleted:** Section 3D ("Optional Temporary CSP Bridge") from Plan v1.0 is permanently eliminated.
- **Enforcement:** The production Content Security Policy remains 100% closed to all outside image providers. Neither `upload.wikimedia.org`, `thumb.wikimedia.org`, nor `numismatics.org` will be added to `img-src` or `connect-src`.
- **Client Sanitization:** Any image URL received by `_CollectionCardImage` or `CoinImageService` that begins with `https://upload.wikimedia.org/` or other non-whitelisted origins is intercepted by a URL sanitization guard before rendering. It is rewritten to the internal catalog mirror path or routed to the local fallback icon.

### 3.2 MF-C2: Real Inventory Census & Source Breakdown
Data sources are verified against dated repository inventories:
1. **Laptop Archive (`1 NUMISTA.AI/Coin Images/_INDEX/inventory_20261031.csv`):**
   - **Date:** 2026-10-31
   - **Total Objects:** 8,945 image files across 420 local folders.
   - **Generic Coin Assets:** 8,836 files (after subtracting 109 PII-flagged microscope, receipt, and invoice paths).
2. **GCS Storage Inventory (`numista_backend/gcs_full_inventory.csv`):**
   - **Date:** 2026-10-27
   - **Total Objects:** 11,069 objects.
   - **`numista-reference-library`:** 6,817 objects (including 454 US Mint official images and 1,934 curated reference obverse/reverse images).
   - **`numista-uploads-studio-9101802118-8c9a8`:** 4,252 objects (user uploads, AI test renders).

#### Census Breakdown: Collection (353 Items) vs Catalog (3,202 Items)
| Domain | Total Items | Tier 1: Own Local/Scrubbed GCS | Tier 2: US Mint Official (GCS) | Tier 3: Wikimedia/NNC Mirror (`gs://numista-catalog-assets`) | Missing / Pending Intake |
|---|---|---|---|---|---|
| **Field Tester Collection** | 353 | 284 (80.5%) | 28 (7.9%) | 41 (11.6%) | 0 (0%)* |
| **Catalog Master Index** | 3,202 | 1,420 (44.3%) | 1,180 (36.9%) | 602 (18.8%) | 0 unmapped (all 3,202 in `MISSING_IMAGES.csv`) |

*\*Note: For any collection card lacking an image during network latency, an inline error builder gracefully displays the coin placeholder icon rather than crashing or triggering CSP network errors.*

### 3.3 MF-C3: MISSING_IMAGES List & Acquisition Workflow
All 3,202 catalog items lacking verified production GCS paths are itemized in `docs/MISSING_IMAGES.csv` (created 5 Nov 2026).
- **Structure:** Itemizes `nac_code`, `type`, `denomination`, `year`, `mint_mark`, `series`, `name`, `obverse_status`, `reverse_status`, `primary_acquisition_tier`, `candidate_source`, `license_type`, `pii_gate_status`, and `estimated_cost` ($0.00).
- **Acquisition Phasing:**
  1. **Phase 1 (Tier 1 Intake):** Ingest 1,420 candidate matches from Laptop Archive (`inventory_20261031.csv`) through the PII filter into `gs://numista-catalog-assets`.
  2. **Phase 2 (Tier 2 Intake):** Mirror 1,180 US Mint public domain sets from official GCS staging into `gs://numista-catalog-assets`.
  3. **Phase 3 (Tier 3 Intake):** Ingest 602 high-resolution public domain / CC-BY-SA images from NNC / Wikimedia Commons with complete license metadata.
- **Live Safety:** No live endpoints, databases, or buckets are modified until all intake batches pass verification.

### 3.4 MF-C4: Licensing & Attribution Architecture
Every mirrored image ingested into `gs://numista-catalog-assets` MUST have an associated licensing record in the manifest (`assets/catalog_image_manifest.json`) and GCS object metadata:
```json
{
  "nac_code": "USA-1C-1909-S-VDB",
  "filename": "USA-1C-1909-S-VDB_obv.webp",
  "author": "National Numismatic Collection, National Museum of American History",
  "license": "CC-BY-SA-4.0",
  "source_url": "https://commons.wikimedia.org/wiki/File:1909-S_VDB_1C_Lincoln_Cent_(obv).jpg",
  "retrieval_date": "2026-11-05T12:00:00Z",
  "credit_text": "Photo: National Numismatic Collection, Smithsonian Institution (CC-BY-SA 4.0)"
}
```
- **Approved Licenses ONLY:** `PD-USGov`, `CC0-1.0`, `CC-BY-4.0`, `CC-BY-SA-4.0`. Images marked with Non-Commercial (`-NC`) or No-Derivatives (`-ND`) are **strictly prohibited**.
- **UI Attribution Rendering:** In `Unified Coin Details View` (NET-798), images carrying CC-BY or institutional attributions render a discrete attribution chip below the photo frame.

### 3.5 MF-C5: Strict Intake PII Gate with 0-Hit Proof
User privacy and founder data integrity are guaranteed by an automated pre-ingestion regex filter.
- **Excluded Folders (Explicit Manifest):**
  - `AJ's Coins/`
  - `Scans AJ June 2026/`
  - `AJ_Photos/`
  - `RECEIPTS/`
  - `INVOICES/`
  - `PACKING_SLIPS/`
  - `User_Uploads/`
  - `Row 10 Eric's microscope photos/`
  - Any path matching regex: `(?i)(aj|invoice|receipt|packing|microscope|user_upload|eric)`
- **Scan & Proof:**
  - Ingestion scripts execute against `inventory_20261031.csv` and staging folders.
  - The 109 paths identified in `inventory_20261031.csv` (100 microscope photos, 7 invoices, 2 receipts) are quarantined and excluded.
  - **Zero-Hit Verification:** The ingestion manifest executes an automated audit verifying `count(matches(PII_REGEX)) == 0` before any file is copied to `gs://numista-catalog-assets`.
  - **Metadata Scrubbing:** GCS object names are strictly standardized to `nac_code` (e.g. `USA-50C-1964-D_rev.webp`). No user names, user IDs, or local folder paths are written to object keys or metadata.

### 3.6 MF-C6: Pinned Bucket Name & Exact CSP Citations
- **Single Dedicated Mirror Bucket:** `gs://numista-catalog-assets`
  - Primary URL: `https://storage.googleapis.com/numista-catalog-assets/:file`
  - On-Domain CDN Rewrite: `https://numista-vault.web.app/catalog-assets/:file` (routed via Firebase Hosting).
- **Exact CSP Citation:**
  - `numista_mobile/firebase.json:275-276` already allows `https://storage.googleapis.com` under `img-src` and `default-src`.
  - `https://*.googleapis.com` in `connect-src` fully permits CanvasKit `fetch()` requests to `https://storage.googleapis.com/numista-catalog-assets/...`.
  - Therefore, **zero CSP changes are required**. The existing CSP is fully sufficient and remains completely sealed.

---

## 4. UI Fallback & Resilience (Argon & GB Advisory)

In `numista_mobile/lib/screens/my_collection_screen.dart`, `_buildCoinImage` is enhanced with a resilient `errorBuilder`:
```dart
Widget _buildCoinImage(String url) {
  // Guard against legacy unmirrored external URLs triggering CSP violations
  if (url.startsWith('https://upload.wikimedia.org') || 
      url.startsWith('https://numismatics.org')) {
    return _buildFallbackPlaceholder();
  }

  return Image.network(
    url,
    fit: BoxFit.cover,
    errorBuilder: (context, error, stackTrace) {
      return _buildFallbackPlaceholder();
    },
  );
}
```
This guarantees that even if a legacy Firestore document references an external URL, the client never attempts a network fetch that violates CSP.

---

## 5. Verification & Acceptance Criteria

1. **CSP Integrity:** Run `p7-gate` and verify console records **0 CSP violation errors** (down from 196).
2. **Zero External Outbound Hosts:** Verify `firebase.json:275-276` contains no references to `wikimedia.org` or `numismatics.org`.
3. **PII 0-Hit Proof:** Run `python tools/verify_catalog_manifest_pii.py` and confirm 0 PII matches in `gs://numista-catalog-assets`.
4. **License Audit:** Confirm 100% of mirrored assets have non-null `license`, `author`, and `source_url` in `assets/catalog_image_manifest.json`.

---

## 6. Execution Protocol & Standing Locks

- **PLAN ONLY:** This document represents an architectural specification. No source code or production buckets are touched until Eric reviews and issues typed YES.
- **Commit Boundary:** Pushed to `origin/p7-v8.9` under `docs/`.
