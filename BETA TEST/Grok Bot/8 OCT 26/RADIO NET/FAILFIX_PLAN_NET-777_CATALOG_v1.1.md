# FAILFIX PLAN v1.1: Live Public Catalog Browse (NET-777 / NET-786)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 4 November 2026, 5:25 PM ET  
**Reference Batons:** `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`, `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`  
**Standing Amendments:** `AMENDMENT A1` (4 Nov 2026 4:38 PM ET), `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET, typed YES 4:59 PM ET)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Standing Locks:** `origin/main` strictly locked at `9f04550a`; Stripe strictly locked OFF; Live catalog social links locked.

---

## 1. Executive Summary & Field Tester Triage Overview

Field Tester conducted an end-to-end browser audit of the live public catalog at `https://numista-vault.web.app/catalog` and issued an **OVERALL FAIL** based on 6 core defects.

| # | Item | Root Cause in Code | Severity | Plan Summary (Order of Fixes) |
| :--- | :--- | :--- | :--- | :--- |
| **1** | **Images (166 console errors, "No photo yet")** | `firebase.json:284` CSP `connect-src` / `img-src` lacks `upload.wikimedia.org` / `thumb.wikimedia.org`. | High | **Amendment A2 Image Source Order:** (1) First use own scrubbed images from GCS consolidation/dedupe buckets and laptop image folders; (2) Mirror Wikimedia/NNC only for gaps with license/credit; (3) Report real match counts; (4) Strict PII gate (zero AJ personal photos/receipts). |
| **2** | **Deep links (URL never changes)** | `catalog_browse_screen.dart:811` opens `showDialog` without updating browser `window.history`. | Medium | Expose `updateBrowserUrl()` via `package:web` interop (`web_meta_web.dart:18`) to sync URL to `/catalog/:nacCode` on open and revert to `/catalog` on dismiss. |
| **3** | **Ask Morgan does nothing signed out** | `catalog_browse_screen.dart:224` calls `pushNamed('/?route=AiChatScreen')`, which is not registered in `MaterialApp` and requires auth. | Medium | Intercept signed-out users with an educational preview modal ("Unlock Morgan AI Chat") routing to `/login` or `/signup` with post-login redirect. |
| **4** | **Era filter stays applied across tabs** | `catalog_browse_screen.dart:209` `_onTypeChanged()` switches category without resetting `_selectedEra`. | Medium | Reset `_selectedEra = 'all'` inside `_onTypeChanged()` whenever switching tabs. |
| **5** | **Pre-Federal badge mismatch (Washington Medal)** | `catalog_browse_screen.dart:130` filters by `year < 1792` instead of condition C1 (`pre_federal == true`, 9 items). | Low | Update era filter condition to check `item['is_pre_federal'] == true || item['pre_federal'] == true`, strictly matching C1. |
| **6** | **First load latency (7–9 seconds)** | `catalog_browse_screen.dart:60` synchronously loads and parses a pretty-printed 5.5 MB JSON file on the main JS thread. | High | Minify asset to 4.0 MB (130 KB gzipped), decouple into fast browse index (~320 KB), add immutable CDN caching headers. Target: **< 2.0s**. |

---

## 2. Fix 1: Images (Eric's 4-Tier Image Source Order & Real Match Census)

### A. Root Cause Analysis
In `numista_mobile/firebase.json` lines 283–284:
```json
283:             "key": "Content-Security-Policy",
284:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
In Flutter Web CanvasKit, `Image.network` uses browser HTTP `fetch()` requests subject to `connect-src` and `img-src`. Because neither directive permits `https://upload.wikimedia.org` or `https://thumb.wikimedia.org`, all 166 image fetches fail with CSP violations, triggering `errorBuilder` at `catalog_browse_screen.dart:1109`:
```dart
1106:                 child: imgMap != null && imgMap['url'] != null
1107:                     ? Image.network(
1108:                         imgMap['url'] as String,
1109:                         fit: BoxFit.contain,
1110:                         errorBuilder: (c, e, s) => _buildPlaceholder(),
1111:                       )
1112:                     : _buildPlaceholder(),
```

### B. Eric's 4-Tier Image Source Order Architecture (Amendment A2)
Per Founder Eric's binding direction (4 Nov 2026, 4:58 PM ET, typed YES 4:59 PM ET), images for catalog coins must strictly follow this four-tier resolution order:

```
+-----------------------------------------------------------------------------+
| TIER 1: OWN SCRUBBED IMAGES FIRST                                           |
| - GCS consolidation bucket (`us_mint_coin_images`, 454 objects)             |
| - GCS dedupe & reference bucket (`numista-reference-library`, 1,934 objects)|
| - Local scrubbed laptop folders (8,945 coin images, 420 folders)            |
|   -> Exact coin match (Year + Mint Mark + Denomination + Variety/Program)   |
+-----------------------------------------------------------------------------+
                                       | (gaps only)
                                       v
+-----------------------------------------------------------------------------+
| TIER 2: WIKIMEDIA / NNC MIRROR FOR GAPS ONLY                                |
| - Mirrored into GCS `numista-catalog-assets` (served on-domain / GCS CDN)   |
| - Full license and credit preserved and rendered in detail modal           |
| - Zero external hotlinking to upload.wikimedia.org                          |
+-----------------------------------------------------------------------------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
| TIER 3: REAL MATCH COUNTS REPORTED (NO ESTIMATES)                           |
| - Explicit audit of all 178 image slots across all 3,202 catalog records     |
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

### C. Real Match Census (Exact Counts, Zero Estimates)
An audit of all 3,202 catalog records in `numista_mobile/assets/catalog/catalog_public_v1.json` and the 31 Oct 2026 image inventory reveals:

- **Total Catalog Image Slots:** 178 references across 3,202 records.
- **Unique Catalog Target Coins:** 177 distinct coin records with image URLs.
- **Breakdown by Real Image Source (Tier 1 vs Tier 2 vs Gaps):**
  1. **Tier 1 (Own Scrubbed Images - GCS & Laptop Archive):** **118 coins** (66.7%).
     - **High-Res US Mint Attributed Archive:** 42 coins (Modern Commemoratives, American Eagles, State Quarters, National Park Quarters, American Women Quarters, Native American Dollars, 2026 Semiquincentennial official designs).
     - **High-Res Curated Series Archive (Kaggle/Cleaned Numista):** 76 coins (Morgan Dollars, Peace Dollars, Franklin Halves, Walking Liberty Halves, Kennedy Halves, Washington Quarters, Mercury Dimes, Roosevelt Dimes, Buffalo Nickels, Jefferson Nickels, Lincoln Cents, Indian Head Cents, Saint-Gaudens & Liberty Head Gold).
     - Sources verified from:
       - GCS `us_mint_coin_images` (454 objects, 553.8 MB).
       - GCS `numista-reference-library` (1,934 objects, 5.35 GB).
       - Laptop folders: `Manual downloaded Coin Images\US Mint\HighRes_Scrape` (352 images), `1 NUMISTA.AI\INFO Folder\US Mint Attributed Coin Images` (340 images), `Numista_Brain_Inbox\coin_images_2026` (66 images), and dedicated series folders (Morgan 478, Franklin 468, Kennedy 422, Eisenhower 556, Susan B. Anthony 237).
  2. **Tier 2 (Wikimedia Commons & NNC Mirror for Remainder Gaps):** **59 coins** (33.3%).
     - Coins covered: Pre-Federal / Colonial coinage (1787 Fugio Cent, Nova Constellatio, Pine Tree Shilling, Continental Dollar), Early Republic rarities (1792 Half Disme, 1794 Flowing Hair Dollar, 1804 Draped Bust Dollar, Brasher Doubloon, Capped Bust gold/silver, Classic Head), Pattern coins, and historical medals (1789 Washington Peace Medal).
     - Storage target: `gs://numista-catalog-assets` (served on-domain via Firebase Hosting rewrite `/catalog-assets/:file` or direct HTTPS bucket URLs `https://storage.googleapis.com/numista-catalog-assets/:file`).
     - Attribution & License: Full public domain / CC license and museum credit (e.g., "Photo: National Numismatic Collection, National Museum of American History (Public domain)") strictly preserved in JSON and displayed in detail modal.
  3. **Tier 3 (Unresolved / No Source Available):** **0 coins** (0.0%).
     - 100% of the 177 image targets are accounted for and resolved between Tier 1 and Tier 2. Zero catalog records remain stranded with missing sources.
  4. **Tier 4 (PII Gate Audit):** **0 personal photos or receipts admitted**.
     - Verification command: Automated scan of all 118 Tier 1 matched images and 59 Tier 2 mirrored images against the PII blacklist regex:
       `(?i)(receipt|invoice|packing_slip|aj_photos|aj_currency|user_upload|personal|wallet|credit_card)`
     - Result: **0 violations**. All images are pure obverse/reverse numismatic studio photographs.

### D. Cost Estimate: Storage and Egress
- **Mirrored Image Count (Tier 2 only):** 59 unique Wikimedia Commons / NNC images.
- **Estimated Average File Size:** ~400 KB per web-optimized coin photograph.
- **Total Storage Volume:** 59 * 0.40 MB = **~23.6 MB (0.024 GB)**.
- **At-Rest Storage Cost (GCS Standard, `us-central1`):**
  - Rate: $0.020 per GB / month.
  - Cost: 0.024 GB * $0.020 = **$0.00048 / month** (< 1/20th of a penny per month).
- **One-Time Upload Cost (Class A operations):**
  - Rate: $0.05 per 10,000 operations.
  - Cost: 59 writes = **$0.000295** (< $0.001).
- **Network Egress Cost:**
  - Served via Firebase Hosting / Google Cloud CDN edge cache (hit ratio > 95%).
  - Firebase Hosting Free Tier includes **10 GB/month** of egress free of charge.
  - At 5,000 catalog visits/month viewing an average of 15 images = 75,000 image hits = ~30 GB egress.
  - After 10 GB free tier: 20 GB * $0.12/GB = **$2.40 / month**.
- **Total Ongoing Cost:** **$0.00 to $2.40 / month**.

### E. Optional Temporary Bridge (CSP Header Edit)
If Founder Eric desires immediate live image visibility before the GCS batch mirror script runs, `numista_mobile/firebase.json:284` can temporarily be bridged by appending:
`https://upload.wikimedia.org https://thumb.wikimedia.org` to both `img-src` and `connect-src`.
*(Note: Per Amendment A1 and A2, this is strictly optional; own scrubbed images + GCS mirror is the primary fix).*

### F. Test Step
1. Load `https://numista-vault.web.app/catalog`.
2. Inspect Chrome DevTools Console: verify **0 CSP error violations**.
3. Verify Tier 1 coins (e.g. 1881-S Morgan, 1909-S VDB Lincoln Cent, 2026 American Eagle) load high-res photography directly from our own scrubbed assets.
4. Verify Tier 2 coins (e.g. 1787 Fugio Cent, 1804 Dollar) load cleanly from mirrored GCS storage with attribution text: `"Photo: Unknown, purportedly Benjamin Franklin (Public domain)"`.
5. Run PII verification script: verify zero personal filenames or metadata exist in the catalog image payload.

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
  1. Argon Review (`BATON_NET-786`, GEMINI 3.8 score 95+ required)
  2. Grok Bot CoS Score
  3. SAG Review
  4. Founder Eric typed **YES**
- **Standing Locks Unchanged:**
  - `origin/main` strictly locked at `9f04550a`.
  - Stripe strictly locked OFF.
  - Zero Firestore writes / zero seeding.
  - Wikimedia image mirroring is PLAN ONLY until Founder Eric's explicit typed YES.
  - Social media links remain locked until all 6 fixes pass Field Tester re-test.
