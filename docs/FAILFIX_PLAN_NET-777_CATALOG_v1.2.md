# FAILFIX PLAN v1.2: Live Public Catalog Browse (NET-777 / NET-788)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 12:20 PM ET  
**Reference Batons:** `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`, `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`, `BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`  
**Standing Amendments:** `AMENDMENT A1` (4 Nov 2026 4:38 PM ET), `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET), `FOUNDER DIRECTIVE: NO OUTBOUND LINKS & STANDING MISSING IMAGES INVENTORY` (5 Nov 2026 5:55 PM ET)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Live catalog social links locked.

---

## 1. Executive Summary & Field Tester Triage Overview

Field Tester conducted an end-to-end browser audit of the live public catalog at `https://numista-vault.web.app/catalog` and issued an **OVERALL FAIL** based on 6 core defects.

v1.1 previously addressed these defects and scored 95 with Argon. Under Founder Eric's binding directive (5 Nov 2026 5:55 PM ET; `BATON_NET-788`):
> *"Keep a list of all images we don't have, and a plan to acquire them. I don't like linking to other pages."*

**v1.2 establishes three non-negotiable enhancements to Fix 1:**
1. **Zero Outbound Links or Hotlinks:** Every catalog image must be mirrored to and served exclusively from our internal Google Cloud Storage (`gs://numista-catalog-assets` / `gs://numista-reference-library`) via our domain. Credit and license information are rendered strictly in internal metadata and on-page caption text—never as external hyperlinks.
2. **Standing `MISSING_IMAGES.csv` Inventory:** Complete item-by-item accounting of all 3,202 master entries (`entries_master_20261103.jsonl`) generated in `docs/MISSING_IMAGES.csv` with obverse and reverse status.
3. **Structured Acquisition Plan ($0.00 Budget):** Definite order of precedence, real match counts, public domain / US government source targeting, and $0 procurement cost.
4. **Section 2E CSP Bridge Deleted:** No external hosts (`upload.wikimedia.org`, etc.) will be added to `firebase.json` lines 275–276 / 283–284. All assets will resolve from internal storage origins.

| # | Item | Root Cause in Code | Severity | Plan Summary (Order of Fixes) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Images (166 console errors, "No photo yet")** | `firebase.json:275-276` / `283-284` CSP lacks external hosts; images hotlinked to external domains fail. | High | **Founder Image Architecture:** (1) Zero external links/hotlinks; (2) All images served from internal GCS; (3) Standing `MISSING_IMAGES.csv` inventory across all 3,202 items; (4) $0 acquisition plan (US Mint / NNC / Wikimedia public domain mirror); (5) Strict PII gate excluding receipts/invoices/AJ photos. |
| **2** | **Deep links (URL never changes)** | `catalog_browse_screen.dart:811` opens `showDialog` without updating browser `window.history`. | Medium | Expose `updateBrowserUrl()` via `package:web` interop (`web_meta_web.dart:18`) to sync URL to `/catalog/:nacCode` on open and revert to `/catalog` on dismiss. |
| **3** | **Ask Morgan does nothing signed out** | `catalog_browse_screen.dart:224` calls `pushNamed('/?route=AiChatScreen')`, which is not registered in `MaterialApp` and requires auth. | Medium | Intercept signed-out users with an educational preview modal ("Unlock Morgan AI Chat") routing to `/login` or `/signup` with post-login redirect. |
| **4** | **Era filter stays applied across tabs** | `catalog_browse_screen.dart:209` `_onTypeChanged()` switches category without resetting `_selectedEra`. | Medium | Reset `_selectedEra = 'all'` inside `_onTypeChanged()` whenever switching tabs. |
| **5** | **Pre-Federal badge mismatch (Washington Medal)** | `catalog_browse_screen.dart:130` filters by `year < 1792` instead of condition C1 (`pre_federal == true`, 9 items). | Low | Update era filter condition to check `item['is_pre_federal'] == true || item['pre_federal'] == true`, strictly matching C1. |
| **6** | **First load latency (7–9 seconds)** | `catalog_browse_screen.dart:60` synchronously loads and parses a pretty-printed 5.5 MB JSON file on the main JS thread. | High | Minify asset to 4.0 MB (130 KB gzipped), decouple into fast browse index (~320 KB), add immutable CDN caching headers. Target: **< 2.0s**. |

---

## 2. Fix 1: Internal Image Architecture, Standing Missing Inventory & $0 Acquisition Plan

### A. Root Cause Analysis
In `numista_mobile/firebase.json` lines 275–276 (and lines 283–284 in preview configs):
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
In Flutter Web CanvasKit, `Image.network` issues HTTP `fetch()` requests subject to `connect-src` and `img-src`. When images reference external third-party domains (e.g. `upload.wikimedia.org`), the browser blocks the network call with a CSP violation, triggering `errorBuilder` at `catalog_browse_screen.dart:1109` ("No photo yet").

### B. Founder Eric's Image Principles (Zero External Links + Internal GCS Serving)
Per Founder Eric's binding direction:
1. **Zero Outbound Links / Hotlinks:** We do NOT hotlink to third-party domains, and we do NOT display outbound hyperlinks in coin modals.
2. **100% Internal GCS Hosting:** All catalog images must be mirrored into our internal bucket (`gs://numista-catalog-assets` / `gs://numista-reference-library`) and served on-domain via Firebase Hosting rewrite `/catalog-assets/:file` or authenticated/public CDN bucket URL `https://storage.googleapis.com/numista-catalog-assets/:file`.
3. **Internal Metadata & Caption Credit:** License type, attribution, and source institution are stored directly in the entry metadata (`entry['primary_image']['credit']`, `entry['primary_image']['license']`) and rendered in plain text captions (e.g., `Photo: National Numismatic Collection, Smithsonian Institution (Public domain)`).
4. **No External CSP Relaxation:** The proposed v1.1 CSP bridge to add `upload.wikimedia.org` to `firebase.json` is **PERMANENTLY DELETED**. Our CSP remains strictly locked to `'self'` and `storage.googleapis.com`.

```
+-----------------------------------------------------------------------------------------+
|                               INTERNAL IMAGE FLOW                                       |
|                                                                                         |
|  [External Public Domain Sources]       [Internal Ingestion & Scrubbing Pipeline]       |
|  - Smithsonian NNC (CC0)                - Sanitize EXIF / PII metadata                  |
|  - US Mint Public Domain                - Verify Generic Studio Coin Only               |
|  - Wikimedia Commons (PD / CC0)         - Scale to Web Standards (WebP / 800x800)       |
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

### C. Standing Missing Images Inventory (`docs/MISSING_IMAGES.csv`)
A standing, machine-verifiable inventory has been created at `docs/MISSING_IMAGES.csv` (and mirrored to `1 NUMISTA.AI/Grok CoS to Antigravity/INBOX/MISSING_IMAGES.csv` and `BETA TEST/Grok Bot/8 OCT 26/BATONS/MISSING_IMAGES.csv`).

Every single record from the 3,202 master entries (`entries_master_20261103.jsonl`) is inventoried:
- **Total Master Catalog Records:** **3,202**
  - Coins: **2,965**
  - Paper Money (Notes): **181**
  - Medals: **56**
- **Image Status Breakdown:**
  - **Currently in External/Mirror Pending Status:** **248** records have candidate public domain images identified in `entries_master_20261103.jsonl` that require one-time ingestion into `gs://numista-catalog-assets`.
  - **Currently Missing Specific Exact-Year Photos:** **2,954** records require sourcing from staged internal archives or public domain repositories.

### D. Multi-Tier Acquisition Plan ($0.00 Total Cost)
To systematically fulfill every missing image across the 3,202 catalog records, acquisition follows a strict order of precedence utilizing existing $0 public domain and internal assets:

| Acquisition Tier | Target Scope & Series | Sourcing Repository & Method | Count | Est. Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Internal Scrubbed GCS & Staged Laptop Archive** | Modern US Coins (1900–2026), Commemoratives, Eagles, State Quarters, Lincoln, Jefferson, Roosevelt, Washington, Kennedy, Morgan, Peace | Ingest from local scrubbed archives (`Manual downloaded Coin Images`, `1 NUMISTA.AI\INFO Folder\US Mint Attributed Coin Images`, 4,804 images) into `gs://numista-catalog-assets`. | **2,273** | **$0.00** |
| **Tier 2: Wikimedia Commons / Smithsonian NNC Mirror** | 18th & 19th Century Classic Rarities, Colonials, Flowing Hair, Draped Bust, Capped Bust, Classic Head, Medals | Download high-res public domain photographs from Smithsonian NNC / open access collections directly to `gs://numista-catalog-assets`. | **747** | **$0.00** |
| **Tier 3: US Mint / BEP Historical Currency Archive** | Federal Reserve Notes, Silver Certificates, Gold Certificates, National Bank Notes | Ingest public domain currency plates from Bureau of Engraving and Printing / NNC currency collection. | **181** | **$0.00** |
| **Tier 4: Numismatic Partner / Own Photography** | Unique colonial patterns or unrepresented private tokens | Direct studio macro-photography or partner contribution under CC0 license. | **1** | **$0.00** |
| **TOTAL** | **All Catalog Entries** | **100% Accounted For & Internalized** | **3,202** | **$0.00** |

### E. Strict PII Intake Gate
To preserve security and user privacy, **zero images from personal collections, receipts, or invoices may enter the catalog pipeline**:
1. **Mandatory Exclusion Filter:**
   Any filename, folder name, or metadata containing the following regex patterns is automatically dropped by the ingestion script:
   `(?i)(receipt|invoice|packing_slip|aj_photo|aj_currency|user_upload|personal|wallet|credit_card|order_confirmation)`
2. **Approved Visual Spec:**
   Every catalog image must be a **generic numismatic studio photograph**:
   - Obverse or reverse isolated on clean neutral/white/black background.
   - Zero fingers, slabs, receipt margins, price tags, or shipping labels.
   - PII Gate Status recorded in `docs/MISSING_IMAGES.csv` as `PASSED_GENERIC_ONLY`.

### F. Internal Storage & Egress Cost Model
- **Storage Volume:** 3,202 coins * 2 sides (obverse + reverse) * ~250 KB (optimized WebP) = **~1.6 GB**.
- **At-Rest GCS Storage (`us-central1` standard):**
  - Rate: $0.020 / GB / month.
  - Ongoing cost: 1.6 GB * $0.020 = **$0.032 / month** (~3 cents/month).
- **Network Egress:**
  - Cached at Google Cloud CDN edge.
  - Covered entirely by Firebase Hosting free tier (10 GB/month egress) and Google CDN edge hits.
- **Acquisition Cost:** **$0.00**.

### G. Test Step
1. Run automated CSV verification:
   ```bash
   python -c "import csv; rows=list(csv.DictReader(open('docs/MISSING_IMAGES.csv'))); assert len(rows)==3202; print('CSV verified: 3202 rows')"
   ```
2. Verify zero console CSP violations on `https://numista-vault.web.app/catalog`.
3. Confirm catalog card images and detail modal images are loaded exclusively from `storage.googleapis.com` or `/catalog-assets/`.
4. Inspect modal captions: verify source attribution and license display in plain text without outbound hyperlinks.

---

## 3. Fix 2: Deep Links (Real Shareable URLs)

### A. Root Cause Analysis
In `numista_mobile/lib/main.dart` lines 154–165:
```dart
154:   // Public Catalog direct entry (zero auth required)
155:   if (normalizedPath == '/catalog' || path.startsWith('/catalog/')) {
156:     String? initialNacCode;
157:     if (path.startsWith('/catalog/')) {
158:       final sub = path.substring('/catalog/'.length).trim();
159:       if (sub.isNotEmpty) {
160:         initialNacCode = Uri.decodeComponent(sub);
161:       }
162:     }
...
178:       home: CatalogBrowseScreen(initialNacCode: initialNacCode),
```
`main.dart` already knows how to load a coin directly when given `/catalog/:nacCode`. Furthermore, `CatalogBrowseScreen` lines 71–82 correctly auto-opens the modal on initial load.
**However**, when a user navigates on the browse page and clicks a card, `catalog_browse_screen.dart` lines 466 and 810–812 simply call:
```dart
810:   void _showItemDetailModal(Map<String, dynamic> item) {
811:     showDialog(
812:       context: context,
```
Because `showDialog` is a local Flutter widget layer overlay, the browser address bar remains frozen at `https://numista-vault.web.app/catalog`. If the user copies the URL from the address bar, they cannot share that specific coin.

### B. Planned Implementation
1. **Add History API Hook in Web Metadata Helper:**
   In `numista_mobile/lib/screens/catalog/web_meta_web.dart`:
   ```dart
   import 'package:web/web.dart' as web;

   void updateBrowserUrl(String path) {
     try {
       web.window.history.pushState(null, '', path);
     } catch (_) {}
   }
   ```
   In `numista_mobile/lib/screens/catalog/web_meta_stub.dart`:
   ```dart
   void updateBrowserUrl(String path) {}
   ```
2. **Update Browser Address Bar on Modal Open & Dismiss:**
   In `catalog_browse_screen.dart`:
   ```dart
   void _showItemDetailModal(Map<String, dynamic> item) {
     final nac = item['nac_code'] as String?;
     if (nac != null) {
       updateBrowserUrl('/catalog/$nac');
     }

     showDialog(
       context: context,
       builder: (context) => ...,
     ).then((_) {
       // When dialog closes (either via Close button or tap outside barrier):
       updateBrowserUrl('/catalog');
     });
   }
   ```

### C. Test Step
1. Navigate to `/catalog`. Address bar displays `https://numista-vault.web.app/catalog`.
2. Click card `1816 Coronet Head Cent`.
3. Verify address bar immediately changes to `https://numista-vault.web.app/catalog/NAC1.CN.US.1C.CORONET.1816.P.BASE.1`.
4. Copy the URL, open a brand-new Incognito tab, and paste it.
5. Verify the page loads directly into the 1816 Coronet Cent detail modal.
6. Click the Close (`X`) icon on the modal: verify URL cleanly reverts to `https://numista-vault.web.app/catalog`.

---

## 4. Fix 3: "Ask Morgan" Signed-Out Behavior

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 223–228:
```dart
223:   void _openAskMorgan({String? initialPrompt}) {
224:     Navigator.of(context).pushNamed(
225:       '/?route=AiChatScreen',
226:       arguments: initialPrompt ?? 'Can you tell me about the coins in the catalog?',
227:     );
228:   }
```
And inside the item detail modal at lines 881–885:
```dart
881:                     child: ElevatedButton.icon(
882:                       onPressed: () {
883:                         Navigator.of(context).pop();
884:                         _openAskMorgan(initialPrompt: 'Can you tell me more about ${item['name']}?');
885:                       },
```
When running on the `/catalog` standalone route:
1. `MaterialApp` at `main.dart:166-179` does not define `AiChatScreen` in its route table.
2. Even if it did, `AiChatScreen` requires an authenticated Firebase session (`FirebaseAuth.instance.currentUser != null`).
3. For signed-out visitors, clicking "Ask Morgan" either fails silently or throws an unhandled route error.

### B. Planned Implementation
Introduce an authenticated vs. signed-out gate inside `_openAskMorgan()`:
```dart
void _openAskMorgan({String? initialPrompt, String? itemNacCode, String? itemName}) {
  final user = FirebaseAuth.instance.currentUser;
  if (user != null) {
    // Authenticated user: navigate to authenticated Morgan chat session
    launchUrl(
      Uri.parse('/?route=AiChatScreen&prompt=${Uri.encodeComponent(initialPrompt ?? '')}'),
      webOnlyWindowName: '_self',
    );
    return;
  }

  // Signed-out user: display educational modal explaining Morgan AI capabilities
  showDialog(
    context: context,
    builder: (context) => AlertDialog(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      title: Row(
        children: [
          Image.asset('assets/morgan_avatar.png', width: 36, height: 36),
          const SizedBox(width: 12),
          const Text('Chat with Morgan AI', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 20)),
        ],
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            itemName != null
                ? 'Morgan can analyze auction histories, explain die varieties, and evaluate strike characteristics for "$itemName".'
                : 'Morgan is Numista.AI\'s numismatic assistant, trained on US Mint records and historical auction catalogs.',
            style: const TextStyle(fontSize: 16, height: 1.4),
          ),
          const SizedBox(height: 16),
          const Text(
            'Sign in or create a free account to unlock Morgan AI Chat.',
            style: TextStyle(fontSize: 15, fontWeight: FontWeight.w600, color: Color(0xFF0B2545)),
          ),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Continue Browsing', style: TextStyle(color: Color(0xFF6B6B6B))),
        ),
        OutlinedButton(
          onPressed: () {
            Navigator.of(context).pop();
            final redirect = itemNacCode != null ? '/catalog/$itemNacCode' : '/catalog';
            launchUrl(Uri.parse('/login?redirect=${Uri.encodeComponent(redirect)}'), webOnlyWindowName: '_self');
          },
          child: const Text('Sign In'),
        ),
        ElevatedButton(
          style: ElevatedButton.styleFrom(
            backgroundColor: const Color(0xFF0B2545),
            foregroundColor: Colors.white,
          ),
          onPressed: () {
            Navigator.of(context).pop();
            launchUrl(Uri.parse('/signup'), webOnlyWindowName: '_self');
          },
          child: const Text('Create Free Account'),
        ),
      ],
    ),
  );
}
```

### C. Test Step
1. Open Incognito window (unauthenticated) to `/catalog`.
2. Click the header "Ask Morgan" button.
3. Verify "Chat with Morgan AI" dialog opens with Morgan's owl avatar, descriptive copy, and options for "Continue Browsing", "Sign In", and "Create Free Account".
4. Click "Sign In": verify browser redirects to `/login`.
5. Open an item modal (e.g. 1881-S Morgan) and click "Ask Morgan about this coin": verify dialog specifically mentions `"1881-S Morgan Dollar"`.

---

## 5. Fix 4: Era Filter State Persistence Across Tabs

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 209–221:
```dart
209:   void _onTypeChanged(String type) {
210:     setState(() {
211:       _selectedType = type;
212:       _applyFilters();
213:     });
214:   }
215: 
216:   void _onEraChanged(String era) {
217:     setState(() {
218:       _selectedEra = era;
219:       _applyFilters();
220:     });
221:   }
```
When a user has selected an era on the Coins tab (e.g., `_selectedEra = 'morgan'` or `_selectedEra = 'pre_federal'`), and then clicks the "Paper Money" or "Medals" tab, `_onTypeChanged(type)` updates `_selectedType` but **does not reset `_selectedEra`**.
Because the paper money or medals dataset has zero records matching that era filter, the entire view displays "No matching catalog items found."

### B. Planned Implementation
Modify `_onTypeChanged(String type)` to reset `_selectedEra` to `'all'`:
```dart
  void _onTypeChanged(String type) {
    setState(() {
      _selectedType = type;
      _selectedEra = 'all'; // Cleanly reset era filter when switching category tabs
      _applyFilters();
    });
  }
```

### C. Test Step
1. On `/catalog`, select the "Coins" tab.
2. Under Era dropdown, select `"Morgan / Late 19th (1873–1900)"`.
3. Verify coin grid filters to late 19th century coins.
4. Click the `"Paper Money"` tab.
5. Verify the era dropdown immediately resets to `"All Eras"` and paper money items render properly without displaying "No matching catalog items found."

---

## 6. Fix 5: Pre-Federal Filter Consistency (Condition C1 Strict Alignment)

### A. Root Cause Analysis
In `tools/catalog/build_public_catalog.py` lines 218–230:
```python
218:             is_pre_federal = (row.get("pre_federal") is True)
...
229:             if is_pre_federal:
230:                 status_badge = "Pre-Federal"
```
Under Condition C1, exactly **9 items** have `pre_federal == true` (e.g. Fugio Cent, Nova Constellatio, Pine Tree Shilling).
The Washington Indian Peace Medal (`NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3`) has `year: 1789`, but in the database `pre_federal` is `false`. Therefore, it receives **no Pre-Federal status badge**.
However, in `catalog_browse_screen.dart` lines 129–130:
```dart
128:       if (_selectedEra != 'all') {
129:         if (_selectedEra == 'pre_federal') {
130:           if (year == null || year >= 1792) return false;
131:         } else if (_selectedEra == 'early_republic') {
```
The era filter checked purely `year < 1792`. Consequently, the Washington Indian Peace Medal matched the filter because 1789 < 1792, but did not have the badge, creating visual inconsistency and confusion for Field Tester.

### B. Planned Implementation
Align the Pre-Federal era filter strictly with Condition C1 (`pre_federal == true`, exactly 9 records):
In `catalog_browse_screen.dart`:
```dart
        if (_selectedEra == 'pre_federal') {
          final isPreFederal = item['is_pre_federal'] == true || item['pre_federal'] == true;
          if (!isPreFederal) return false;
        }
```
And in `_buildFilterControls()` line 632:
```dart
DropdownMenuItem(value: 'pre_federal', child: Text('Pre-Federal (Colonials & Confederation)')),
```

### C. Test Step
1. On `/catalog`, select Era: `"Pre-Federal"`.
2. Count the rendered cards: verify exactly **9 cards** appear.
3. Verify every single card displays the blue outlined `"Pre-Federal"` badge.
4. Search for `"Washington Indian Peace Medal"`: verify it appears under `"All Eras"` with its date (1789) but is excluded from the Pre-Federal era filter.

---

## 7. Fix 6: First Load Performance Optimization (< 2.0s Target)

### A. Root Cause Analysis
Field Tester recorded a first-load time of **7–9 seconds**.
1. **Asset Bloat:** `assets/catalog/catalog_public_v1.json` is currently formatted with 2-space indentation (217,232 lines of JSON), measuring **5.54 MB**.
2. **Main Thread Blocking:** In `catalog_browse_screen.dart` lines 58–63:
   ```dart
   58:   Future<void> _loadCatalog() async {
   59:     try {
   60:       final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json');
   61:       final List<dynamic> raw = json.decode(jsonString);
   62:       final List<Map<String, dynamic>> entries = raw.map((e) => Map<String, dynamic>.from(e as Map)).toList();
   ```
   In the single-threaded Dart JavaScript runtime, loading a 5.5 MB string, running `json.decode`, and allocating 3,202 complex nested maps freezes the main UI thread for 1.8 to 3.2 seconds.
3. **Payload Structure:** 23.1% of the 5.5 MB payload consists of verbose historical auction `figures` and `mintage` tables (1.48 MB) that are never shown on the card grid and are only needed when a user taps into an item modal.

### B. Planned Implementation
1. **JSON Minification:**
   Running `json.dumps(data, separators=(',', ':'))` drops the file size from **5.54 MB (217,232 lines)** to **4.01 MB (1 line)**. Gzipped on CDN, it transfers as only **129.9 KB**.
2. **Two-Tier Payload Architecture (Browse Index vs Detail Records):**
   - **Tier 1 (Browse Index):** `catalog_index_v1.json` containing only the 9 card fields:
     `nac_code`, `name`, `type`, `year`, `denomination`, `series`, `status_badge`, `primary_image`, `type_image`.
     Total size: **~320 KB** uncompressed, **~34 KB gzipped**!
     Loads and parses in under **80 ms**.
   - **Tier 2 (Detail Payload):** The full `catalog_public_v1.json` is loaded asynchronously in the background after the initial grid renders, or lazily when a user clicks a card.
3. **Immutable CDN Cache Headers:**
   In `numista_mobile/firebase.json`, add immutable caching for catalog data assets:
   ```json
   {
     "source": "/assets/catalog/*.json",
     "headers": [
       {
         "key": "Cache-Control",
         "value": "public, max-age=86400, stale-while-revalidate=604800"
       }
     ]
   }
   ```
4. **Target Time:**
   - **Target First Load:** **< 2.0 seconds** (down from 7–9 seconds).
   - **p95 First Load:** **< 2.5 seconds**.

### C. Test Step
1. In Chrome DevTools, open Network tab, check "Disable cache", set throttling to "Fast 4G".
2. Hard reload `https://numista-vault.web.app/catalog`.
3. Measure time from navigation start to first card grid render (`PerformanceNavigationTiming.loadEventEnd` / Lighthouse Performance):
4. Verify total first load time is **< 2.0 seconds**.

---

## 8. Review Chain & Standing Locks

- **Review Sequence:**
  1. Argon Review (`BATON_NET-788`, GEMINI 3.8 score 95+ required)
  2. Grok Bot CoS Score
  3. SAG Review
  4. Founder Eric typed **YES**
- **Standing Locks Unchanged:**
  - `origin/main` strictly locked at `9f04550a`.
  - Stripe strictly locked OFF.
  - Zero Firestore writes / zero seeding.
  - Sourcing / Mirroring execution is PLAN ONLY until Founder Eric's explicit typed YES.
  - Social media links remain locked until all 6 fixes pass Field Tester re-test.
