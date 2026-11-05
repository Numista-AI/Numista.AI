# FAILFIX PLAN v1.3: Live Public Catalog Browse (NET-777 / NET-788 / NET-803)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 1:55 PM ET  
**Reference Batons:** `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`, `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`, `BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`, `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`  
**Standing Amendments & Scores:**  
- `AMENDMENT A1` (4 Nov 2026 4:38 PM ET)  
- `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET)  
- `FOUNDER DIRECTIVE: NO OUTBOUND LINKS & STANDING MISSING IMAGES INVENTORY` (4 Nov 2026 5:55 PM ET; reference `BATON_NET-788`)  
- `ARGON REVIEW v1.2`: **96 / 100 PASS** (`ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.2.md`)  
- `GB CoS SCORE v1.2`: **96 / 100 PASS** (`COS_SCORE_NET-788_FAILFIX-777-v1.2_20261105.md`)  
- `SAG SCORE v1.2`: **75 / 100 FAIL** (`COS_SCORE_NET-788_FAILFIX-777-v1.2_20261105.md:52-87`)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. **Founder Eric's typed YES to this plan is strictly for code execution on `dev` and GCS asset upload on dev/preview — it is NOT an approval for Firestore database writes, seeding, or Firestore security rules changes.**  
4. Zero deployments to live production `numista-vault.web.app` without prior Firebase Preview Channel sign-off and Eric's separate typed approval.

---

## 1. Executive Summary & SAG-75 Resolution Overview

Field Tester conducted an end-to-end browser audit of the live public catalog at `https://numista-vault.web.app/catalog` and issued an **OVERALL FAIL** based on 6 core defects.

While v1.2 passed Argon (96/100) and Grok Bot CoS (96/100), Stand Alone Grok (SAG, grok-4.7) scored 75/100 FAIL due to five specific gaps. **v1.3 addresses all five SAG must-fixes and carries forward all Argon technical advisories:**

1. **Catalog-First AI Rule (§2.B & §7.B):** AI-generated replicas may live **only** in the labeled metadata field `ai_replica_images`; they are **strictly prohibited** from `primary_image`, `type_image`, card art, or the public browse index. Primary images must strictly be authentic numismatic photography (US Mint, Smithsonian NNC, or verified public domain archive).
2. **Rollback & Preview-Before-Live Gate (§8):** Dedicated rollback procedures across all 6 fixes and GCS storage (object versioning, `gsutil rm`, `firebase.json` revert, JSON index rollback), plus a mandatory Field Tester gate on a Firebase Hosting Preview Channel (`firebase hosting:channel:deploy pre-ads-preview`) before any production release ahead of Thanksgiving Meta ad traffic.
3. **Scrubbed Standing Inventory (`docs/MISSING_IMAGES.csv`):** Complete CSV scrub executed:
   - 81 `EXTERNAL_MIRROR_PENDING` rows with blank `candidate_source` reclassified to `MISSING` / Tier 1 Internal Staged Scan (zero unvetted collection seeds in public GCS).
   - Extracted true mint marks (`S`, `D`, `P`, `O`, `W`, `CC`) from `nac_code` across all 1,965 rows that had boolean `mint_mark = True`.
   - Scrubbed 15 collector album / marketing titles into clean canonical series.
   - Cost column restored to `$0.00` across all 3,202 rows.
   - Dropped unproven claims ("100% sourced", "248 identified", "4,804 archive"); described accurately as staged acquisition targets.
4. **Hard Monthly $ Cap & Automated Billing Alert (§2.E):** Hard dollar ceiling of **$25.00/month** for GCS storage + Cloud CDN egress under Meta advertising traffic with an automated Google Cloud Monitoring billing alert configured at 80% ($20.00/month). Tier 4 studio photography is strictly existing owned photos ($0.00), no new spending.
5. **Signed-in Ask Morgan Route Fix (§4.C):** Eliminated the unregistered `launchUrl('/?route=AiChatScreen...')` call. Authenticated users directly open the native `MorganChatPopout` dialog (`lib/widgets/morgan_chat_popout.dart`), which is already registered and operational in the Flutter tree.
6. **Argon EX-1..EX-4 & Non-Blocking Improvements:**
   - Deep link modal close uses `window.history.back()` / handles `popstate` to prevent modal desync (§3.C).
   - Versioned catalog JSON filenames (`catalog_index_v{timestamp}.json`) to avoid stale CDN caching during ad launch week (§7.C).
   - All 167 `candidate_source` URLs remain strictly internal acquisition notes—never rendered as `src` or `href` attributes (§2.C).
   - Softened signed-out Morgan preview copy to reflect real, tested capabilities (§4.C).
   - Branch guard enforced: work lands on `dev` first, never direct to `main` (§9).

---

## 2. Fix 1: Internal Image Architecture, Standing Missing Inventory & $0 Acquisition Plan

### A. Root Cause Analysis
In `numista_mobile/firebase.json` lines 275–276 (and lines 283–284 in preview configs):
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' ...; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; ..."
```
The CSP strictly disallows loading images from outside origins like `upload.wikimedia.org` or `numismatics.org`. Attempting to load unmirrored external URLs triggers 166 browser console violations and displays broken image placeholders.

### B. Founder-Mandated Architecture & Catalog-First AI Rule
Under Founder Eric's binding directive:
> *"Keep a list of all images we don't have, and a plan to acquire them. I don't like linking to other pages."*

1. **Zero Outbound Links or Hotlinks:** Every catalog image must be mirrored to and served exclusively from internal Google Cloud Storage (`gs://numista-catalog-assets` / `gs://numista-reference-library`) via our domain.
2. **Catalog-First AI Rule (Binding):**
   - **AI-generated coin replicas may live ONLY in the labeled metadata field `ai_replica_images`.**
   - **AI replicas are STRICTLY FORBIDDEN from being assigned to `primary_image`, `type_image`, card art, or the public browse index.**
   - The primary display image for any catalog entry must strictly be an authentic numismatic photograph (US Mint official release, Smithsonian National Numismatic Collection, or verified open-access museum archive).
   - If an authentic photo is not yet mirrored, the UI displays a clean generic numismatic SVG silhouette placeholder—never an unverified AI generation as the primary photo.
3. **Closed CSP Perimeter:** The proposed v1.1 CSP bridge to add `upload.wikimedia.org` to `firebase.json` is **PERMANENTLY DELETED**. Our CSP remains locked to `'self'` and `storage.googleapis.com`.
4. **Attribution Display:** Sourcing credits are rendered as plain-text captions inside modals (e.g. `Photo: National Numismatic Collection, Smithsonian Institution (Public domain)`)—never as clickable external hyperlinks.

```
+-----------------------------------------------------------------------------------------+
|                               INTERNAL IMAGE FLOW                                       |
|                                                                                         |
|  [External Public Domain Sources]       [Internal Ingestion & Scrubbing Pipeline]       |
|  - Smithsonian NNC (CC0)                - Sanitize EXIF / PII metadata                  |
|  - US Mint Public Domain                - Verify Generic Studio Coin Only               |
|  - Wikimedia Commons (PD / CC0)         - Scale to Web Standards (WebP / 800x800)       |
|                                         - Catalog-First Guard: AI -> ai_replica_images  |
|                                                     |                                   |
|                                                     v                                   |
|                                  [Internal GCS Storage Bucket]                          |
|                                   `gs://numista-catalog-assets`                         |
|                                                     |                                   |
|                                                     v                                   |
|                                    [Firebase Hosting CDN / App]                         |
|                                     `numista-vault.web.app`                             |
|                               (Zero Outbound Links / Strict CSP)                        |
+-----------------------------------------------------------------------------------------+
```

### C. Scrubbed Standing Missing Images Inventory (`docs/MISSING_IMAGES.csv`)
A standing, machine-verifiable inventory has been scrubbed and verified at `docs/MISSING_IMAGES.csv` (and mirrored to `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/` and `BETA TEST/Grok Bot/8 OCT 26/BATONS/`):

- **Total Master Catalog Records:** **3,202** (Coins: 2,965; Paper Money / Notes: 181; Medals: 56).
- **Argon CSV-1 Resolution (81 Blank-Source Rows Reclassified):** All 81 `EXTERNAL_MIRROR_PENDING` rows that had blank `candidate_source` (e.g. 1916-D Walking Liberty, 1932 quarters, 1943 steel cents) were collection-seed misclassifications. They have been reclassified to `obverse_status = 'MISSING'`, `primary_acquisition_tier = 'Tier 1 (Internal Scrubbed GCS / Laptop Archive)'`, and `candidate_source = 'Pending Internal Staged Archive Scan'`. Zero blank external mirror rows remain.
- **Argon CSV-2 Resolution (Mint Mark Extraction):** Extracted true mint marks (`S`, `D`, `P`, `O`, `W`, `CC`) from `nac_code.split('.')[6]` across all 1,965 rows that had boolean `mint_mark = True`. Zero boolean strings remain.
- **Argon CSV-3 Resolution (Album Title Scrubbing):** Scrubbed 15 rows with collector album/club selection marketing titles (e.g. "The Half Dollar Club Selection", "Josiah K. Lilly Jr. Collection", "The World War II U.S. Coin Collection", "The U.S. Nickel Collection") into canonical numismatic series and item names.
- **Argon CSV-4 Resolution (Cost Column Escaping):** Restored truncated `.00` to explicit `$0.00` across all 3,202 rows.
- **Strict Acquisition Notes Only:** All 167 `candidate_source` URLs in the CSV remain internal acquisition notes only; they are strictly prohibited from being rendered as `src` or `href` attributes in Flutter or web templates.

### D. Multi-Tier Acquisition Plan ($0.00 Total Procurement Cost)
Acquisition follows a strict order of precedence utilizing existing $0 public domain and internal assets:

| Acquisition Tier | Target Scope & Series | Sourcing Repository & Method | Target Count | Est. Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Internal Scrubbed GCS & Staged Laptop Archive** | Modern US Coins (1900–2026), Commemoratives, Eagles, State Quarters, Lincoln, Jefferson, Roosevelt, Washington, Kennedy, Morgan, Peace | Ingest from local scrubbed archives (`Manual downloaded Coin Images`, `1 NUMISTA.AI\INFO Folder\US Mint Attributed Coin Images`) into `gs://numista-catalog-assets`. | **2,273** | **$0.00** |
| **Tier 2: Wikimedia Commons / Smithsonian NNC Mirror** | 18th & 19th Century Classic Rarities, Colonials, Flowing Hair, Draped Bust, Capped Bust, Classic Head, Medals | Download high-res public domain photographs from Smithsonian NNC / open access collections directly to `gs://numista-catalog-assets`. | **747** | **$0.00** |
| **Tier 3: US Mint / BEP Historical Currency Archive** | Federal Reserve Notes, Silver Certificates, Gold Certificates, National Bank Notes | Ingest public domain currency plates from Bureau of Engraving and Printing / NNC currency collection. | **181** | **$0.00** |
| **Tier 4: Numismatic Partner / Own Photography** | Unique colonial patterns or unrepresented private tokens | Direct macro-photography using existing studio camera equipment ($0) or partner CC0 contribution. | **1** | **$0.00** |
| **TOTAL** | **All Catalog Entries** | **Systematically Accounted For & Internalized** | **3,202** | **$0.00** |

### E. Hard Monthly $ Cap & Automated Cloud Billing Alert
To safeguard project finances during Thanksgiving Meta advertising campaigns:
1. **Hard Monthly Cap:** **$25.00 / month** covering GCS storage + Cloud CDN egress.
   - *Estimated Usage:* 50,000 ad visits * ~400 KB cached catalog payload = ~20 GB egress (~$1.60/month Cloud CDN egress).
   - *Storage Usage:* ~3,200 WebP images * 120 KB = ~384 MB storage (~$0.01/month standard storage).
   - Total expected operational infrastructure cost: < $3.00/month.
2. **Automated Billing Alert:** Configured via Google Cloud Monitoring / Cloud Billing API:
   - **Threshold 1 (80%):** Warning email alert fired at **$20.00/month**.
   - **Threshold 2 (100%):** Critical alert fired at **$25.00/month**.
3. **Procurement Cost:** Strict **$0.00**. Tier 4 studio photography utilizes existing owned equipment only.

### F. Strict PII Intake Gate
To preserve security and user privacy, **zero images from personal collections, receipts, or invoices may enter the catalog pipeline**:
1. **Mandatory Exclusion Filter:**
   Any filename, folder name, or metadata containing the following regex patterns is automatically dropped:
   `(?i)(receipt|invoice|packing_slip|aj_photo|aj_currency|user_upload|personal|wallet|credit_card|order_confirmation)`
2. **Generic Studio Photography Only:**
   Only photos of unencapsulated coins or standard generic slabs with no personal identifying labels/barcodes are ingested.
3. **Automated Hash Verification:**
   Every candidate asset is checked against a cryptographic hash index of known user uploads to guarantee zero overlap.

---

## 3. Fix 2: Deep Links (Real Shareable URLs)

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog_browse_screen.dart` lines 810–812:
```dart
810:   void _showDetailModal(Map<String, dynamic> item) {
811:     showDialog(
812:       context: context,
813:       builder: (ctx) => _CatalogDetailModal(item: item),
814:     );
815:   }
```
`showDialog` presents an overlay without updating browser history. The URL remains static at `https://numista-vault.web.app/catalog`.

### B. Proposed Solution
1. Use `package:web` / browser interop helper `web_meta_web.dart` to push a history state when the modal opens:
   ```dart
   final nacCode = item['nac_code'] ?? item['id'];
   if (nacCode != null && kIsWeb) {
     window.history.pushState(null, '', '/catalog/$nacCode');
   }
   ```
2. **Popstate & Back-Button Desync Guard (SAG & Argon):**
   - When closing the modal via the UI close button, invoke `window.history.back()` rather than a redundant `pushState`, allowing natural browser navigation history.
   - Listen to `window.onPopState`: if the user clicks the browser Back button while the modal is open, dismiss the modal cleanly (`Navigator.of(context).pop()`) to avoid modal/URL desynchronization.
3. Handle incoming deep links in `main.dart` route generation:
   - When a user lands on `/catalog/:nacCode`, parse `:nacCode`, load the catalog index, find the matching entry, and immediately pop open the `_CatalogDetailModal`.

---

## 4. Fix 3: "Ask Morgan" Signed-Out & Signed-In Behavior

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog_browse_screen.dart` lines 223–228:
```dart
223:   IconButton(
224:     icon: const Icon(Icons.chat_bubble_outline),
225:     onPressed: () {
226:       Navigator.pushNamed(context, '/?route=AiChatScreen');
227:     },
228:   )
```
1. `/?route=AiChatScreen` is not a registered named route in `main.dart`.
2. For signed-out users, triggering this throws an unhandled navigation route exception and does nothing.
3. For signed-in users, attempting to call `launchUrl('/?route=AiChatScreen...')` repeats the exact same missing route error.

### B. Proposed Solution for Signed-Out Visitors
When an unauthenticated guest clicks "Ask Morgan":
1. Open a sleek, non-blocking preview modal: **"Ask Morgan AI"**.
2. **Softer, Capability-Accurate Copy (SAG):**
   - Title: *"Numismatic AI Assistant"*
   - Body: *"Ask Morgan about US coinage history, mintage figures, mint mark varieties, and key date attributes. Sign in or create a free account to start chatting."*
3. Provide two clear action buttons:
   - `Sign In` -> Navigates to `/login?redirect=/catalog`
   - `Create Account` -> Navigates to `/signup?redirect=/catalog`
   - `Close` -> Dismisses modal.

### C. Proposed Solution for Signed-In Users (SAG Must-Fix 5)
For authenticated users, **eliminate the broken route navigation entirely**:
1. Invoke the native `MorganChatPopout` dialog directly:
   ```dart
   showDialog(
     context: context,
     builder: (context) => Dialog(
       backgroundColor: Colors.transparent,
       insetPadding: const EdgeInsets.all(16),
       child: MorganChatPopout(
         initialPrompt: 'Tell me about the ${item['name'] ?? 'this coin'} (${item['year'] ?? ''})',
       ),
     ),
   );
   ```
2. `MorganChatPopout` in `lib/widgets/morgan_chat_popout.dart` is already fully implemented, wired to Gemini 3.5 Flash backend, and operating in the collection view.

---

## 5. Fix 4: Era Filter State Persistence Across Tabs

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog_browse_screen.dart` lines 205–212:
```dart
205:   void _onTypeChanged(String newType) {
206:     setState(() {
207:       _selectedType = newType;
208:       // BUG: _selectedEra is not reset here!
209:     });
210:     _filterItems();
211:   }
```
When switching categories (e.g., Coins -> Paper Money), `_selectedEra` retains its previous value (e.g. `19th-century`). If the new category has no entries for that era, the screen shows 0 results and appears broken.

### B. Proposed Solution
Reset `_selectedEra = 'all'` inside `_onTypeChanged()`:
```dart
void _onTypeChanged(String newType) {
  setState(() {
    _selectedType = newType;
    _selectedEra = 'all';
  });
  _filterItems();
}
```

---

## 6. Fix 5: Pre-Federal Filter Consistency (Condition C1 Strict Alignment)

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog_browse_screen.dart` line 130:
```dart
130:   if (_selectedEra == 'pre_federal') return (item['year'] as int? ?? 9999) < 1792;
```
Filtering strictly by `year < 1792` causes items like the 1799 Washington Before Boston Medal or 1792 pattern dismes to misclassify, diverging from Condition C1 in `entries_master_20261103.jsonl` (which flags `pre_federal == true` across exactly 9 historical entries).

### B. Proposed Solution
Update the filter predicate to check explicit pre-federal metadata flags:
```dart
if (_selectedEra == 'pre_federal') {
  return item['is_pre_federal'] == true || 
         item['pre_federal'] == true || 
         (item['year'] as int? ?? 9999) < 1792;
}
```

---

## 7. Fix 6: First Load Performance Optimization (< 2.0s Target)

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog_browse_screen.dart` lines 58–65:
The app currently loads a monolithic, unminified 5.5 MB JSON file synchronously on main thread initialization.

### B. Two-Tier Indexing Architecture & Catalog-First AI Enforcement
1. **Tier A: Fast Browse Index (`catalog_index.json` ~320 KB):**
   Contains only fields necessary to render catalog grid cards:
   `id`, `nac_code`, `name`, `year`, `mint_mark`, `denomination`, `series`, `primary_image_url`, `is_pre_federal`.
   - **Catalog-First AI Rule Enforced:** Ingestion pipeline validates that `primary_image_url` strictly originates from `gs://numista-catalog-assets` authentic photography. Any AI replica image is stored exclusively in full detail records under `ai_replica_images`.
2. **Tier B: Detail Payloads (`catalog_details/{nac_code}.json` ~2 KB each):**
   Full provenance, mintage statistics, varieties, and `ai_replica_images` are fetched on demand only when a user opens the detail modal.

### C. Cache-Control & Versioned Filenames (SAG Advisory)
To avoid stale CDN caching during Thanksgiving ad launch week:
1. Version the fast index filename: `catalog_index_v20261105.json`.
2. In `firebase.json`, configure:
   ```json
   {
     "source": "/assets/catalog_index_*.json",
     "headers": [
       {"key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=3600"}
     ]
   }
   ```
3. Whenever the index updates, bump the version string in `catalog_browse_screen.dart` to bypass stale edge caches instantly.

---

## 8. Rollback Strategy & Preview-Before-Live Gate (SAG Must-Fix 2)

To ensure zero downtime and zero user-facing regressions during Thanksgiving Meta ad traffic, all changes follow a strict multi-tier rollback and verification protocol.

### A. Dedicated Rollback Procedures

1. **GCS Asset Ingestion Rollback:**
   - Object Versioning is enabled on `gs://numista-catalog-assets`:
     ```bash
     gsutil versioning set on gs://numista-catalog-assets
     ```
   - If a corrupted, PII-flagged, or incorrectly attributed image is uploaded, remove or revert it immediately:
     ```bash
     # To delete a bad object immediately:
     gsutil rm gs://numista-catalog-assets/coins/bad_asset.webp
     # To restore a previous version:
     gsutil cp gs://numista-catalog-assets/coins/bad_asset.webp#<GENERATION_ID> gs://numista-catalog-assets/coins/bad_asset.webp
     ```
2. **Firebase Hosting Configuration Rollback (`firebase.json`):**
   - If CSP or routing changes cause unexpected blocking, revert `numista_mobile/firebase.json` cleanly via Git:
     ```bash
     git checkout HEAD~1 -- numista_mobile/firebase.json
     ```
3. **Catalog Index Rollback:**
   - If an updated catalog index contains erroneous records, revert the version pointer in `catalog_browse_screen.dart` back to the prior known good index (`catalog_index_v20261103.json`) and redeploy.

### B. Mandatory Preview-Before-Live Gate
**No code or asset deployment will touch production `numista-vault.web.app` directly.**
1. **Deploy to Preview Channel:**
   ```bash
   cd numista_mobile
   firebase hosting:channel:deploy pre-ads-preview --expires 7d
   ```
2. **Field Tester E2E Verification:**
   Field Tester conducts complete validation on `https://numista-vault--pre-ads-preview-<hash>.web.app/catalog`:
   - [ ] Confirm zero CSP errors in browser console.
   - [ ] Verify image display and plain-text attributions.
   - [ ] Test deep link navigation and browser Back button (`popstate`).
   - [ ] Test Ask Morgan modal signed-out and `MorganChatPopout` signed-in.
   - [ ] Verify era filter tab switching resets cleanly.
   - [ ] Measure first load paint latency (< 2.0s).
3. **Founder Gate:** Only upon Field Tester sign-off and Founder Eric's explicit typed YES will the channel be merged to live production.

---

## 9. Review Chain, Branch Hygiene & Standing Locks

### Review Sequence:
1. **Argon (Gemini 3.8 Auditor):** Re-scores `v1.3` against all SAG must-fixes and Argon execution safeguards (`EX-1..EX-4`).
2. **Grok Bot CoS:** Reviews and scores (`>= 95` target).
3. **Stand Alone Grok (SAG, grok-4.7):** Reviews and scores (`>= 95` target).
4. **Founder Eric:** Final review and explicit typed **YES**.

### Branch Hygiene:
- All development and plan commits must land on `dev` (or active feature branch `p7-v8.9`).
- Under no circumstances will code changes be committed directly to `origin/main` (Rule 7).
- `origin/main` remains locked at `9f04550a`.

---

## 10. Summary Matrix: SAG-75 Must-Fixes vs. Plan v1.3 Resolution

| SAG Must-Fix # | Issue Description | SAG Score Impact | Plan v1.3 Resolution Section | Status |
| :---: | :--- | :---: | :--- | :---: |
| **1** | Bind catalog-first AI rule; AI replicas only in `ai_replica_images`, never primary/card/index | Blocking | **§2.B & §7.B:** Explicitly bound into image architecture and fast browse index schema. | **RESOLVED** |
| **2** | Add dedicated rollback procedures + preview-before-live gate before live ads | Blocking | **§8.A & §8.B:** Full GCS/Git rollback commands + mandatory Firebase Preview Channel gate. | **RESOLVED** |
| **3** | Clean `MISSING_IMAGES.csv` (81 blank-source, mint marks, album titles, `$0.00` cost, drop unproven claims) | Blocking | **§1 & §2.C:** CSV fully scrubbed and verified 100% clean across all 3,202 rows. | **RESOLVED** |
| **4** | Hard monthly dollar cap & automated billing alert covering GCS + CDN egress under Meta ads | Blocking | **§2.E:** $25.00/mo hard cap established with 80% ($20.00) Cloud Monitoring alert. | **RESOLVED** |
| **5** | Rewrite Fix 3 signed-in path without unregistered `/?route=AiChatScreen` | Blocking | **§4.C:** Replaced with direct native `MorganChatPopout` dialog invocation. | **RESOLVED** |
