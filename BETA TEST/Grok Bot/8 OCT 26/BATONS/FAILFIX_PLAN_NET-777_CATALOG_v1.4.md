# FAILFIX PLAN v1.4: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 3:05 PM ET  
**Reference Batons:** `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`, `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`, `BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`, `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`, `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`  
**Standing Amendments & Scores:**  
- `AMENDMENT A1` (4 Nov 2026 4:38 PM ET)  
- `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET)  
- `FOUNDER DIRECTIVE: NO OUTBOUND LINKS & STANDING MISSING IMAGES INVENTORY` (4 Nov 2026 5:55 PM ET; reference `BATON_NET-788`)  
- `ARGON REVIEW v1.3`: **98 / 100 PASS** (`ARGON_REVIEW_FAILFIX_PLAN_NET-777_CATALOG_v1.3.md`)  
- `GB CoS SCORE v1.3`: **97 / 100 PASS** (`COS_SCORE_NET-803_FAILFIX-777-v1.3_20261105.md`)  
- `SAG SCORE v1.3`: **92 / 100 FAIL** (`COS_SCORE_NET-803_FAILFIX-777-v1.3_20261105.md:68-87`)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. **Founder Eric's typed YES to this plan is strictly for code execution on `dev` and GCS asset upload on dev/preview — it is NOT an approval for Firestore database writes, seeding, or Firestore security rules changes.**  
4. **Zero deployments to live production `numista-vault.web.app` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval.**  

---

## 1. Executive Summary & SAG-92 Resolution Overview

On the v1.3 plan iteration, Grok Bot CoS awarded a passing **97 / 100 PASS**, and Argon awarded a near-perfect **98 / 100 PASS**. Stand Alone Grok (SAG, grok-4.7) lifted the prior 75 score to **92 / 100 FAIL**, leaving just 3 points to reach the 95 passing threshold. 

SAG identified exactly **two blocking must-fixes** and five non-blocking refinements:
1. **Tier Table Staleness (SAG MF-1):** Section 2.D in v1.3 retained a pre-scrub split (2,273 / 747). In v1.4, Section 2.D is completely synchronized with the live scrubbed CSV inventory: **2,354 Tier 1**, **639 Tier 2**, **181 Tier 3**, **1 Tier 4**, and **27 Tier 5 (Excluded Private Medals)**, totaling exactly **3,202** master records.
2. **`MorganChatPopout` Constructor Signature (SAG MF-2 & CoS EX-v1.3-1):** Fixed the code specification in §4.C to use the verified constructor parameters: `initialQuery` (not `initialPrompt`) and required `onClose: () => Navigator.of(context).pop()`, properly enclosed inside a centered `Dialog` wrapper (`SizedBox(width: 420, height: 600)`).
3. **CSV Private Medal Reclassification & Mint Mark Scrub:**
   - Reclassified 27 post-1929 private medals (Franklin Mint American Negro Commemorative Society series 1969–1974, Great Men of Medicine series 1969–1970, Medallic Art Co Aphrodite 1932, etc.) from `Public Domain` to `In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed)` in Tier 5.
   - Normalized 147 dirty facility strings (`'Bureau of Engraving and Printing'`, `'Philadelphia Mint'`, `'United States Mint'`, etc.) in `mint_mark` into clean valid tokens (`P`, or empty string `''`). 100% of the 3,202 rows now contain strictly valid mint mark tokens in `{'', 'P', 'D', 'S', 'W', 'O', 'CC'}`.
4. **Programmatic Spending Hard Stop (§2.E):** Addressed SAG finding that "email alerts don't stop spend." In addition to Cloud Monitoring alerts at $20.00 (80%), v1.4 specifies an automated Cloud Billing Budget programmatic notification wired to a Cloud Function (`stop-public-egress`) that disables Cloud CDN caching and restricts bucket access if monthly spend ever hits the $25.00 ceiling.
5. **Strict Condition C1 Pre-Federal Flag Filter (§6.B):** Removed the ambiguous `year < 1792` OR clause from Fix 5, strictly filtering on `item['is_pre_federal'] == true || item['pre_federal'] == true` matching Condition C1 across the 9 pre-federal entries.
6. **Outbound `(source)` Link Removal & US-Only Tab Cleanup:**
   - Explicitly cites `origin/dev:numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 1010–1017, removing the clickable `launchUrl(uri)` link and replacing it with non-clickable plain text (`Source: <institution>`).
   - Removes the `Foreign Coins` tab (`catalog_browse_screen.dart:598-603`) to ensure a 100% US coinage, currency, and medal catalog scope for Thanksgiving advertising traffic.
7. **Pinned Rollback Targets (§8.A):** Pinned rollback commands directly to commit `9f04550a` (the frozen production baseline) rather than unpinned `HEAD~1`.
8. **Field Tester Expanded Gate (§8.B):** Added explicit checks for pre-federal flag accuracy, zero AI replicas in primary image slots, and zero `href`/`src` rendering on any acquisition notes.

---

## 2. Target Implementation File & Verbatim Citations on `dev`

All changes target the live implementation file on branch `origin/dev`:  
**`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`** (Commit `18a8b8e5d0690303fe4efdebe8ed06e417e55a25`).

| Defect / Area | Exact Lines on `dev` | Current Code on `origin/dev` | v1.4 Plan Fix |
| :--- | :--- | :--- | :--- |
| **Outbound `(source)` Link** | Lines 1010–1017 | `InkWell(onTap: () async { final uri = Uri.tryParse(sourceUrl); if (uri != null) await launchUrl(uri); }, child: const Text('(source)', ...))` | **Delete `InkWell` / `launchUrl`.** Render source metadata strictly as plain non-clickable text: `Text('Source: $sourceInstitution', style: TextStyle(color: Color(0xFF6B6B6B)))`. |
| **Foreign Coins Tab** | Lines 598–603 | `_TypeTab(label: 'Foreign Coins', isSelected: _selectedType == 'foreign', onTap: () => _onTypeChanged('foreign'))` | **Delete `Foreign Coins` `_TypeTab`.** Public catalog is strictly 100% US Coins, Notes, and Medals. |
| **Ask Morgan Navigation** | Lines 223–228 | `void _openAskMorgan({String? initialPrompt}) { Navigator.of(context).pushNamed('/?route=AiChatScreen', ...); }` | **Replace with native dialog.** Signed-out guests get preview modal; signed-in users open `MorganChatPopout(initialQuery: ..., onClose: ...)`. |
| **Era State Persistence** | Lines 205–210 | `void _onTypeChanged(String type) { setState(() { _selectedType = type; _applyFilters(); }); }` | **Reset era on tab switch:** Add `_selectedEra = 'all';` inside `setState`. |
| **Pre-Federal Filter** | Lines 128–130 | `if (_selectedEra == 'pre_federal') { if (year == null \|\| year >= 1792) return false; }` | **Strict Condition C1 flag:** Check `item['is_pre_federal'] == true \|\| item['pre_federal'] == true`. |
| **Item Detail Modal URL** | Lines 810–815 | `void _showItemDetailModal(Map<String, dynamic> item) { showDialog(...); }` | **Push browser history:** Add `web_meta_web.dart` history push for `/catalog/:nacCode` and listen for `popstate`. |

---

## 3. Fix 1: Internal Image Architecture, Scrubbed Standing Inventory & Sourcing

### A. Root Cause Analysis
In `numista_mobile/firebase.json` lines 275–276:
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' ...; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; ..."
```
The CSP strictly disallows loading images from outside origins like `upload.wikimedia.org` or `numismatics.org`. Attempting to load unmirrored external URLs triggers browser console violations and displays broken image placeholders.

### B. Founder Directive & Catalog-First AI Rule
Under Founder Eric's binding directive:
> *"Keep a list of all images we don't have, and a plan to acquire them. I don't like linking to other pages."*

1. **Zero Outbound Links or Hotlinks:** Every catalog image must be mirrored to and served exclusively from internal Google Cloud Storage (`gs://numista-catalog-assets`) via our domain.
2. **Catalog-First AI Rule (Binding):**
   - **AI-generated coin replicas may live ONLY in the labeled metadata field `ai_replica_images`.**
   - **AI replicas are STRICTLY FORBIDDEN from being assigned to `primary_image`, `type_image`, card art, or the public browse index.**
   - The primary display image for any catalog entry must strictly be an authentic numismatic photograph (US Mint official release, Smithsonian National Numismatic Collection, or verified open-access museum archive).
   - If an authentic photo is not yet mirrored, the UI displays a clean generic numismatic SVG silhouette placeholder—never an unverified AI generation as the primary photo.
3. **Closed CSP Perimeter:** The CSP remains locked to `'self'` and `storage.googleapis.com`. No external domains are added.
4. **Attribution Display:** Sourcing credits are rendered as plain-text captions inside modals (e.g. `Photo: National Numismatic Collection, Smithsonian Institution (Public domain)`)—never as clickable external hyperlinks.

### C. Live Scrubbed Inventory Breakdown (`docs/MISSING_IMAGES.csv`)
The standing inventory file at `docs/MISSING_IMAGES.csv` contains exactly **3,202 master catalog records**:

1. **Mint Mark Field Normalization (100% Clean):**
   - Resolved all 147 dirty facility strings (`Philadelphia Mint`, `Bureau of Engraving and Printing`, `Medallic Art Company Ltd.`, etc.).
   - Mapped based on NAC canonical mark token (`nac_code.split('.')[6]`):
     - 23 Philadelphia facility rows mapped to `'P'`.
     - 65 private/collector facility rows mapped to `''` (clean empty string).
     - 59 Bureau of Engraving & Printing paper currency rows mapped to `''` (clean empty string).
   - **Final Mint Mark Distribution across all 3,202 rows:**
     - No mint mark (`''`): **1,214**
     - San Francisco (`S`): **730**
     - Denver (`D`): **619**
     - Philadelphia (`P`): **472**
     - New Orleans (`O`): **104**
     - West Point (`W`): **36**
     - Carson City (`CC`): **27**
     - Dirty strings remaining: **0** (100% valid).
2. **Private Post-1929 Medals Reclassification (Tier 5):**
   - Reclassified 27 private medals dated between 1932 and 1976 (Franklin Mint American Negro Commemorative Society series, Great Men of Medicine series, Medallic Art Co Aphrodite, World's Fair medals) from `Public Domain` to:
     - `license_type`: `In Copyright (Private Mint / Post-1929 - Excluded from PD Ingestion until Licensed)`
     - `candidate_source`: `Private Mint Archive / Excluded`
     - `primary_acquisition_tier`: `Tier 5 (Excluded - Private Mint / Awaiting License)`
     - `estimated_cost`: `$0.00`
3. **Modern US Mint Official Medals (17 U.S.C. § 105):**
   - Corrected 13 official US Mint medals dated 1982–2023 (e.g. Proof Set Medal 1982, Congressional Gold Medals for Billy Graham, Steve Gleason, NASA Hidden Figures, American Liberty medals) to `Public Domain (US Govt Work)`.
4. **Strict Internal Acquisition Notes:**
   - All 167 `candidate_source` URLs in the CSV remain internal acquisition notes only; they are strictly prohibited from being rendered as `src` or `href` attributes in Flutter or web templates.
5. **PII Gate Status:** 3,202 / 3,202 rows verified `PASSED_GENERIC_ONLY`. Zero personal identifiers.

### D. Synchronized Multi-Tier Acquisition Plan ($0.00 Procurement Cost)

The acquisition table is now 100% synchronized with the live scrubbed CSV:

| Acquisition Tier | Target Scope & Series | Sourcing Repository & Method | Exact Count | Est. Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Internal Scrubbed GCS & Staged Archive** | Modern US Coins (1900–2026), Commemoratives, Eagles, State Quarters, Lincoln, Jefferson, Roosevelt, Washington, Kennedy, Morgan, Peace | Ingest from local scrubbed archives (`Manual downloaded Coin Images`, `1 NUMISTA.AI\INFO Folder\US Mint Attributed Coin Images`) into `gs://numista-catalog-assets`. | **2,354** | **$0.00** |
| **Tier 2: Wikimedia Commons / Smithsonian NNC Mirror** | 18th & 19th Century Classic Rarities, Colonials, Flowing Hair, Draped Bust, Capped Bust, Classic Head, Historical Medals (Pre-1929) | Download high-res public domain photographs from Smithsonian NNC / open access collections directly to `gs://numista-catalog-assets`. | **639** | **$0.00** |
| **Tier 3: US Mint / BEP Historical Currency Archive** | Federal Reserve Notes, Silver Certificates, Gold Certificates, National Bank Notes | Ingest public domain currency plates from Bureau of Engraving and Printing / NNC currency collection. | **181** | **$0.00** |
| **Tier 4: Numismatic Partner / Own Photography** | Unique colonial pattern (NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3) | Direct macro-photography using existing studio camera equipment ($0) or partner CC0 contribution. | **1** | **$0.00** |
| **Tier 5: Excluded from PD Ingestion** | Private Medals (Franklin Mint ANCS, Great Men of Medicine, Medallic Art Co 1932–1976) | **Excluded from public domain ingestion.** Retained as reference entries with generic numismatic silhouette placeholders until commercial licensing agreement. | **27** | **$0.00** |
| **TOTAL** | **All Catalog Entries** | **Systematically Accounted For & Internalized** | **3,202** | **$0.00** |

### E. Hard Monthly $ Cap & Programmatic Spend Stop

To ensure project spend cannot exceed authorized levels under Meta ad traffic:
1. **Hard Monthly Cap:** **$25.00 / month** covering GCS storage + Cloud CDN egress.
   - *Estimated Usage:* 50,000 ad visits * ~400 KB cached catalog payload = ~20 GB egress (~$1.60/month Cloud CDN egress).
   - *Storage Usage:* ~3,200 WebP images * 120 KB = ~384 MB storage (~$0.01/month standard storage).
   - *Firebase Hosting Egress:* First 10 GB free, $0.15/GB thereafter (~$1.50/month). Total expected operational cost: < $4.00/month.
2. **Automated Alerting:**
   - **Threshold 1 (80%):** Warning email alert fired via Google Cloud Monitoring at **$20.00/month** to Founder Eric and AG CoS on-call.
3. **Programmatic Hard Stop Mechanism (SAG Resolution):**
   - Google Cloud Billing Budget configured with a Pub/Sub notification topic: `projects/numista-ai/topics/billing-budget-alerts`.
   - A dedicated Cloud Function (`stop-public-egress`) subscribes to the topic. If `costAmount >= 25.00`, the function automatically invokes Cloud Storage IAM to disable public object access on `gs://numista-catalog-assets` (or points Cloud CDN to static placeholder SVG), preventing runaway egress billing.
4. **Procurement Cost:** Strict **$0.00**.

---

## 4. Fix 2: Deep Links & Browser History

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 810–812:
`showDialog` presents an overlay without updating browser history. The URL remains static at `https://numista-vault.web.app/catalog`.

### B. Proposed Solution
1. Use `package:web` / browser interop helper `web_meta_web.dart` to push a history state when the modal opens:
   ```dart
   final nacCode = item['nac_code'] ?? item['id'];
   if (nacCode != null && kIsWeb) {
     window.history.pushState(null, '', '/catalog/$nacCode');
   }
   ```
2. **Popstate & Back-Button Guard:**
   - When closing the modal via the UI close button, invoke `window.history.back()`.
   - Listen to `window.onPopState`: if the user clicks the browser Back button while the modal is open, dismiss the modal cleanly (`Navigator.of(context).pop()`) to keep the URL and UI synchronized.
3. Handle incoming deep links in `main.dart`:
   - When a user lands on `/catalog/:nacCode`, parse `:nacCode`, load the catalog index, find the matching entry, and immediately pop open the `_CatalogDetailModal`.

---

## 5. Fix 3: "Ask Morgan" Signed-Out & Signed-In Behavior

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 223–228:
```dart
  void _openAskMorgan({String? initialPrompt}) {
    Navigator.of(context).pushNamed(
      '/?route=AiChatScreen',
      arguments: initialPrompt ?? 'Can you tell me about the coins in the catalog?',
    );
  }
```
1. `/?route=AiChatScreen` is not a registered named route in `main.dart`.
2. Calling this throws an unhandled navigation route exception for both guests and signed-in users.

### B. Solution for Signed-Out Visitors
When an unauthenticated guest clicks "Ask Morgan":
1. Open a sleek preview modal: **"Ask Morgan AI"**.
2. **Capability-Accurate Copy:**
   - Title: *"Numismatic AI Assistant"*
   - Body: *"Ask Morgan about US coinage history, mintage figures, mint mark varieties, and key date attributes. Sign in or create a free account to start chatting."*
3. Action buttons: `Sign In` (`/login?redirect=/catalog`), `Create Account` (`/signup?redirect=/catalog`), and `Close`.

### C. Solution for Authenticated Users (Verified Constructor Spec)
For authenticated users, replace the broken route push with the native `MorganChatPopout` widget, using its exact verified constructor arguments:

```dart
void _openAskMorganForCoin(Map<String, dynamic> item) {
  final coinName = item['name'] ?? 'this coin';
  final coinYear = item['year'] != null ? ' (${item['year']})' : '';
  
  showDialog(
    context: context,
    builder: (dialogCtx) => Dialog(
      backgroundColor: Colors.transparent,
      insetPadding: const EdgeInsets.all(16),
      child: SizedBox(
        width: 420,
        height: 600,
        child: MorganChatPopout(
          initialQuery: 'Tell me about the $coinName$coinYear',
          onClose: () => Navigator.of(dialogCtx).pop(),
          onNavigateToCollection: () {
            Navigator.of(dialogCtx).pop();
            Navigator.of(context).pushNamed('/collection');
          },
        ),
      ),
    ),
  );
}
```

*Verbatim Verification (`lib/widgets/morgan_chat_popout.dart:11-16`):*
- `this.initialQuery` (String?)
- `required this.onClose` (VoidCallback)
- `this.onNavigateToCollection` (VoidCallback?)

---

## 6. Fix 4: Era Filter State Reset on Tab Switch

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 205–210:
`_onTypeChanged(String type)` updates `_selectedType` without resetting `_selectedEra`. If switching from Coins (where `seated` era was selected) to Notes, 0 results are returned.

### B. Proposed Solution
Reset `_selectedEra = 'all'` inside `_onTypeChanged()`:
```dart
  void _onTypeChanged(String type) {
    setState(() {
      _selectedType = type;
      _selectedEra = 'all'; // Reset era filter on tab switch
      _applyFilters();
    });
  }
```

---

## 7. Fix 5: Pre-Federal Filter Strict Alignment (Condition C1)

### A. Root Cause Analysis
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 128–130:
```dart
if (_selectedEra == 'pre_federal') {
  if (year == null || year >= 1792) return false;
}
```
Filtering by `year < 1792` causes items like the 1799 Washington Before Boston Medal or 1792 pattern dismes to misclassify, diverging from Condition C1 in `entries_master_20261103.jsonl` (which flags `pre_federal == true` across exactly 9 historical entries).

### B. Proposed Solution (Strict Flag-Only)
Per SAG recommendation, eliminate the `year < 1792` OR clause and filter strictly by explicit pre-federal metadata flags:
```dart
if (_selectedEra == 'pre_federal') {
  final bool isPreFederal = (item['is_pre_federal'] == true) || 
                            (item['pre_federal'] == true);
  if (!isPreFederal) return false;
}
```

---

## 8. Fix 6: Outbound Link Removal & First-Load Performance (< 2.0s Target)

### A. Outbound `(source)` Link Removal
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` lines 1010–1017:
Replace the clickable `launchUrl(uri)` inkwell with non-clickable plain text:
```dart
// OLD (dev:1010-1017):
// InkWell(
//   onTap: () async {
//     final uri = Uri.tryParse(sourceUrl);
//     if (uri != null) await launchUrl(uri);
//   },
//   child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
// )

// NEW:
Text(
  'Source: ${sourceInstitution ?? 'Public Record'}',
  style: const TextStyle(fontSize: 14, color: Color(0xFF6B6B6B)),
)
```

### B. Two-Tier Indexing Architecture
1. **Tier A: Fast Browse Index (`catalog_index_v20261105.json` ~320 KB):**
   Contains only fields necessary to render catalog grid cards:
   `id`, `nac_code`, `name`, `year`, `mint_mark`, `denomination`, `series`, `primary_image_url`, `is_pre_federal`.
   - **Catalog-First AI Rule Enforced:** Ingestion pipeline validates that `primary_image_url` strictly originates from `gs://numista-catalog-assets` authentic photography.
2. **Tier B: Detail Payloads (`catalog_details/{nac_code}.json` ~2 KB each):**
   Full provenance, mintage statistics, varieties, and `ai_replica_images` are fetched on demand only when a user opens the detail modal.
3. **Cache-Control & Versioned Filenames:**
   - In `firebase.json`:
     ```json
     {
       "source": "/assets/catalog_index_*.json",
       "headers": [
         {"key": "Cache-Control", "value": "public, max-age=86400, stale-while-revalidate=3600"}
       ]
     }
     ```

---

## 9. Rollback Strategy & Preview-Before-Live Gate

To guarantee zero downtime and zero regressions ahead of Thanksgiving Meta ad campaigns:

### A. Dedicated Pinned Rollback Procedures
1. **GCS Asset Ingestion Rollback:**
   - Object Versioning enabled on `gs://numista-catalog-assets`:
     ```bash
     gsutil versioning set on gs://numista-catalog-assets
     ```
   - Rollback of individual corrupted or PII-flagged assets:
     ```bash
     gsutil rm gs://numista-catalog-assets/coins/bad_asset.webp
     # Restore prior generation if needed:
     gsutil cp gs://numista-catalog-assets/coins/bad_asset.webp#<GENERATION_ID> gs://numista-catalog-assets/coins/bad_asset.webp
     ```
2. **Firebase Hosting Configuration Rollback (`firebase.json`):**
   - Revert pinned cleanly to the production baseline commit `9f04550a`:
     ```bash
     git checkout 9f04550a -- numista_mobile/firebase.json
     ```
3. **Catalog Index Rollback:**
   - Revert `catalog_browse_screen.dart` asset path directly to the proven baseline index `assets/catalog/catalog_public_v1.json` at git commit `9f04550a`.

### B. Mandatory Preview-Before-Live Gate
**No code or asset deployment will touch production `numista-vault.web.app` directly.**
1. **Deploy to Preview Channel:**
   ```bash
   cd numista_mobile
   firebase hosting:channel:deploy pre-ads-preview --expires 7d
   ```
2. **Field Tester E2E Verification Checklist:**
   Field Tester conducts complete validation on `https://numista-vault--pre-ads-preview-<hash>.web.app/catalog`:
   - [ ] Confirm zero CSP errors in browser console.
   - [ ] Verify image display and plain-text attributions.
   - [ ] Verify **zero outbound links** (no clickable `(source)` links anywhere).
   - [ ] Verify **`Foreign Coins` tab is removed** (US-only catalog scope).
   - [ ] Verify **pre-federal filter strictly displays Condition C1 items** (flag-only).
   - [ ] Verify **AI replicas are strictly absent from primary cards and browse index**.
   - [ ] Verify **zero `href` or `src` attributes render the 167 acquisition-note URLs**.
   - [ ] Test deep link navigation (`/catalog/:nacCode`) and browser Back button (`popstate`).
   - [ ] Test Ask Morgan modal signed-out and `MorganChatPopout` signed-in.
   - [ ] Verify era filter tab switching resets cleanly (`_selectedEra = 'all'`).
   - [ ] Measure first load paint latency (< 2.0s).
3. **Founder Gate:** Only upon Field Tester sign-off and **Founder Eric's separate, explicit typed YES** will the channel be merged to live production.

---

## 10. Review Chain & Standing Locks

### Review Sequence:
1. **Argon (Gemini 3.8 Auditor):** Re-scores `v1.4` against all SAG must-fixes and Argon execution safeguards.
2. **Grok Bot CoS:** Reviews and scores (`>= 95` target).
3. **Stand Alone Grok (SAG, grok-4.7):** Reviews and scores (`>= 95` target).
4. **Founder Eric:** Final review and explicit typed **YES**.

### Branch Hygiene:
- All development and plan commits must land on `dev` (or active feature branch `p7-v8.9`).
- Under no circumstances will code changes be committed directly to `origin/main` (Rule 7).
- `origin/main` remains strictly locked at `9f04550a`.

---

## 11. Summary Matrix: SAG-92 Resolution

| SAG Finding | Issue Description | SAG Impact | Plan v1.4 Resolution Section | Status |
| :---: | :--- | :---: | :--- | :---: |
| **Must-Fix 1** | Stale §2.D tier table (2,273 / 747 pre-scrub) | Blocking (92) | **§2.D:** Rewritten to exact live CSV counts: 2,354 / 639 / 181 / 1 / 27 = 3,202. | **RESOLVED** |
| **Must-Fix 2** | `MorganChatPopout` constructor signature mismatch (`initialPrompt` vs `initialQuery`) | Blocking (92) | **§5.C:** Corrected to verified `initialQuery` + required `onClose` in centered `Dialog` wrapper. | **RESOLVED** |
| **Refinement 1** | Email alerts don't stop spend; need programmatic hard stop | Non-blocking | **§2.E:** Added Pub/Sub + Cloud Function `stop-public-egress` at $25.00 hard cap. | **RESOLVED** |
| **Refinement 2** | Fix 5 ORs `year < 1792`; prefer flag-only for Condition C1 | Non-blocking | **§7.B:** Strict flag-only filter: `item['is_pre_federal'] == true \|\| item['pre_federal'] == true`. | **RESOLVED** |
| **Refinement 3** | FT list omits pre-federal, AI-never-primary, and no-`href`/`src` on notes | Non-blocking | **§9.B:** Added all 3 checks explicitly to Field Tester preview checklist. | **RESOLVED** |
| **Refinement 4** | `git checkout HEAD~1` unpinned; pin to `9f04550a` | Non-blocking | **§9.A:** Pinned rollback commands directly to `9f04550a`. | **RESOLVED** |
| **Refinement 5** | Pre-1929 tag on 1970s medals; license text confirmation | Non-blocking | **§3.C & CSV:** Reclassified 27 private medals to `In Copyright (Excluded from PD Ingestion)`. | **RESOLVED** |
| **Directive** | Outbound `(source)` link violates zero-outbound-link rule | Binding | **§2 & §8.A:** Removed `launchUrl` in `catalog_browse_screen.dart:1010-1017`. Plain text source only. | **RESOLVED** |
