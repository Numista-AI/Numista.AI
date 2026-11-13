# FAILFIX PLAN v1.6: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804 / NET-808 / NET-811)
**To:** Antigravity Desk, Grok Bot CoS, Argon (Gemini 3.8), Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 5:30 PM ET  
**Reference Batons:**  
- `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`  
- `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`  
- `BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`  
- `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`  
- `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`  
- `BATON_NET-808_REVISE_FAILFIX_NET-777_CATALOG_v1.5_PER-COS-89-SAG-85_2026-11-05-1600.md`  
- `BATON_NET-811_REVISE_FAILFIX_NET-777_CATALOG_v1.6_PER-COS-87-SAG-84_2026-11-05-1705.md`  
**Standing Amendments & Audit Scores:**  
- `AMENDMENT A1` (4 Nov 2026 4:38 PM ET)  
- `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET)  
- `FOUNDER DIRECTIVE: NO OUTBOUND LINKS & STANDING MISSING IMAGES INVENTORY` (4 Nov 2026 5:55 PM ET; reference `BATON_NET-788`)  
- `ARGON REVIEW v1.5`: **98 / 100 PASS** (`ARGON_REVIEW_FAILFIX_PLAN_CATALOG_v1.5.md`)  
- `GB CoS SCORE v1.5`: **87 / 100 FAIL** (`COS_SCORE_NET-808_FAILFIX-777-v1.5_20261105.md`)  
- `SAG SCORE v1.5`: **84 / 100 FAIL** (`SAG_SCORE_NET-808_20261105.md`)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. **Founder Eric's typed YES to this plan is strictly for code execution on `dev` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or Firestore security rules changes.**  
4. **Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval.**  
5. **Public Catalog Valuations Display Strictly CDN CPG Retail (`cpgRetail`) Only; Zero Wholesale Values.**  
6. **Confirmed Ad Landing Host:** `https://numista.ai` (SPA rewrite routing to `CatalogBrowseScreen`).

---

## 1. Executive Summary & CoS-87 / SAG-84 Must-Fix Resolution Overview

On the v1.5 plan iteration, Argon awarded **98 / 100 PASS**, but real-code repository audits by Grok Bot CoS (**87 / 100 FAIL**) and Stand Alone Grok (**84 / 100 FAIL**) identified specific defects in rollback SHA pinning, egress spend stop mechanics, loader wiring, and `_buildMintageRow` metadata.

In v1.6, every single must-fix is resolved and grounded against current code:

1. **Grounded Rollback Architecture (§9.A — CoS & SAG Must-Fix 1):**
   - **Pre-Execute dev HEAD Recorded:** Struck outdated `18a8b8e5` checkout and restored the true pre-execute `origin/dev` HEAD (`b0b05808` at review time). `18a8b8e5` was only the last catalog-code change; subsequent dev commits are docs.
   - **Full Revert Scope:** Rollback uses `git revert <execute commit set>` back to pre-execute HEAD `b0b05808`. Revert explicitly covers all files touched (`catalog_browse_screen.dart`, `firebase.json`, `main.dart`, new helpers, and catalog JSON payloads).
   - **No Branch Destructive Checkouts:** Eliminated any checkout that could strip dev's 8 catalog rewrite lines or discard intervening commits.
   - **Named Hosting Rollback Preserved:** Paired with named prior Firebase Hosting release restore (`firebase hosting:clone numista-vault:<prior-version-id> numista-vault:live` or Console release restore), or instant preview deletion (`firebase hosting:channel:delete pre-ads-preview`).

2. **Real Egress Stop & Human Operational Control (§3.E — CoS & SAG Must-Fix 2):**
   - **Removed Invented Cloud Function Claims:** Struck all claims that a Cloud Function (`stop-public-egress`) exists or currently disables IAM/CDN.
   - **Acknowledged Billed Path Reality:** Firebase Hosting CDN egress ($0.15/GB above 10 GB free) is the billed path under Meta ad traffic; Cloud Storage bucket IAM alone cannot stop Firebase Hosting traffic.
   - **Unbuilt Infrastructure Labeled:** Labeled `gs://numista-catalog-assets`, Pub/Sub topic, and automated spend-stop functions explicitly as *"Unbuilt — to be provisioned by Cloud Infrastructure Owner"*. Identified active studio bucket today as `numista-uploads-studio-9101802118-8c9a8`.
   - **Named Human Fail-Safe:** Established Founder Eric / Grok Bot CoS as the named human operator. If spend approaches the $20.00 warning threshold, the human operator immediately executes `firebase hosting:channel:delete pre-ads-preview` (for preview) or `firebase hosting:disable` (for live), instantly terminating all billed egress.

3. **Wiring the Real Loader (§2, §8 — CoS & SAG Must-Fix 3):**
   - **Actual Loader Target:** `CatalogBrowseScreen._loadCatalog()` loads `assets/catalog/catalog_public_v1.json` via `rootBundle.loadString` (lines 58–60).
   - **Grounded Schema & Retail Rules:** Specified that `catalog_public_v1.json` (and its index migration) includes `cpgRetail` when sourced; zero wholesale pricing is served.
   - **Positive Retail Never Hidden:** In the card widget, when `valCpg > 0`, formatted `fmt.format(valCpg)` is rendered unconditionally. The gold `'Valuation Pending'` chip is rendered strictly when `valCpg <= 0`. A positive retail price is never suppressed by pending status flags.
   - **Catalog-First AI Rule:** No primary image is invented; authentic photos only. If unmirrored, render the clean SVG silhouette.

4. **Correct Mintage Metadata & Outbound Link Removal (§2, §8.A — CoS & SAG Must-Fix 4):**
   - **Real Variables in `_buildMintageRow` (lines 987–1023):** Ground truth variables are `val` (`mintage?['value']`), `label` (`mintage?['label']`), and `sourceUrl` (`mintage?['source_url']`). `sourceInstitution` is not defined.
   - **Surgical Outbound Link Deletion:** Deleted the entire `InkWell` and `launchUrl(uri)` block on lines 1010–1017. Render mintage strictly as plain non-clickable text: `Text(val, style: ...)` and `Text(label ?? 'Needs source', style: ...)`. Zero external links; zero undefined variables.

5. **Deep-Link & Constructor Alignment (§4, §5 — CoS & SAG Non-Blocking):**
   - Deep-linking extends the screen's existing `widget.initialNacCode` handling (lines 68–75) rather than inventing an ungrounded secondary modal path.
   - Verified `MorganChatPopout` constructor is identical across both `p7-v8.9` and `origin/dev`.

---

## 2. Target Implementation File & Verbatim Citations on `dev`

Target file on branch `origin/dev`:  
**`numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`** (Pre-execute HEAD `b0b058087f1492244a0c0b769e126b38ac1ba06c`).

| Defect / Area | Exact Lines on `dev` | Current Code on `origin/dev` | v1.6 Plan Specification | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Outbound `(source)` Link** | Lines 1010–1017 | `InkWell(onTap: () async { final uri = Uri.tryParse(sourceUrl); if (uri != null) await launchUrl(uri); }, child: const Text('(source)', ...))` | **Delete `InkWell` / `launchUrl`.** Render mintage value and label strictly as plain non-clickable text. Do not reference undefined `sourceInstitution`. | **SPECIFIED — to be removed at execute** |
| **Foreign Coins Tab** | Lines 599–603 | `_TypeTab(label: 'Foreign Coins', isSelected: _selectedType == 'foreign', onTap: () => _onTypeChanged('foreign'))` | **Delete `Foreign Coins` `_TypeTab`.** Public catalog is strictly 100% US Coins, Notes, and Medals for Thanksgiving ad launch. | **SPECIFIED — to be removed at execute** |
| **Catalog Loader & Schema** | Lines 58–63 | `final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json'); final List<dynamic> raw = json.decode(jsonString);` | **Wire real loader:** Load entries with `cpgRetail` populated from CDN CPG retail data; zero wholesale. Enforce positive retail display over pending flags. | **SPECIFIED — to be wired at execute** |
| **Deep Link Handling** | Lines 68–75 | `if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) { final targetNac = widget.initialNacCode!.trim().toLowerCase(); ... }` | **Retain existing `initialNacCode` logic:** Open `_showItemDetailModal(match)` when `match` is found on initial load. | **VERIFIED ON DEV — preserved** |
| **Ask Morgan Navigation** | Lines 223–228 | `void _openAskMorgan({String? initialPrompt}) { Navigator.of(context).pushNamed('/?route=AiChatScreen', ...); }` | **Replace with native dialog.** Signed-out guests get preview modal; signed-in users open `MorganChatPopout` (confirmed on dev). | **SPECIFIED — to be replaced at execute** |
| **Era State Persistence** | Lines 209–214 | `void _onTypeChanged(String type) { setState(() { _selectedType = type; _applyFilters(); }); }` | **Reset era on tab switch:** Add `_selectedEra = 'all';` inside `setState`. | **SPECIFIED — to be updated at execute** |
| **Pre-Federal Filter** | Lines 128–130 | `if (_selectedEra == 'pre_federal') { if (year == null \|\| year >= 1792) return false; }` | **Strict Condition C1 flag:** Check `item['is_pre_federal'] == true \|\| item['pre_federal'] == true`. Drop `year < 1792`. | **SPECIFIED — to be updated at execute** |

---

## 3. Fix 1: Internal Image Architecture, Scrubbed Standing Inventory & Sourcing

### A. Closed CSP Perimeter
In `numista_mobile/firebase.json` lines 275–276:
```json
275:             "key": "Content-Security-Policy",
276:             "value": "default-src 'self' ...; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; ..."
```
The CSP strictly disallows loading images from outside origins like `upload.wikimedia.org` or `numismatics.org`. Attempting to load unmirrored external URLs triggers browser console violations.

### B. Founder Directive & Catalog-First AI Rule
Under Founder Eric's binding directive:
> *"Keep a list of all images we don't have, and a plan to acquire them. I don't like linking to other pages."*

1. **Zero Outbound Links or Hotlinks:** Every catalog image must be mirrored to and served exclusively from internal Google Cloud Storage via our domain.
2. **Catalog-First AI Rule (Binding):**
   - **AI-generated coin replicas may live ONLY in the labeled metadata field `ai_replica_images`.**
   - **AI replicas are STRICTLY FORBIDDEN from being assigned to `primary_image`, `type_image`, card art, or the public browse index.**
   - The primary display image for any catalog entry must strictly be an authentic numismatic photograph (US Mint official release, Smithsonian National Numismatic Collection, or verified open-access museum archive).
   - If an authentic photo is not yet mirrored, the UI displays a clean generic numismatic SVG silhouette placeholder—never an unverified AI generation as the primary photo.
3. **Closed CSP Perimeter:** The CSP remains locked to `'self'` and `storage.googleapis.com`. No external domains are added.
4. **Attribution Display:** Sourcing credits are rendered as plain-text captions inside modals—never as clickable external hyperlinks.
5. **Valuation Source Rule:** Public catalog valuations display strictly CDN CPG retail (`cpgRetail`) only; zero wholesale values.

### C. Live Scrubbed Inventory Breakdown (`docs/MISSING_IMAGES.csv`)
The standing inventory file at `docs/MISSING_IMAGES.csv` contains exactly **3,202 master catalog records**:

1. **Mint Mark Field Normalization (100% Clean):**
   - Clean distribution across all 3,202 rows: No mint mark (`''`): **1,214** | San Francisco (`S`): **730** | Denver (`D`): **619** | Philadelphia (`P`): **472** | New Orleans (`O`): **104** | West Point (`W`): **36** | Carson City (`CC`): **27**. Dirty strings: **0**.
2. **Private Post-1929 Medals Reclassification (Tier 5):**
   - 27 private medals (Franklin Mint American Negro Commemorative Society series, Great Men of Medicine, Medallic Art Co 1932–1976) classified as Tier 5 (Excluded from public domain ingestion; retained with silhouette placeholders).
3. **Modern US Mint Official Medals (17 U.S.C. § 105):**
   - 13 official US Mint medals dated 1982–2023 classified as Public Domain (US Govt Work).
4. **Strict Internal Acquisition Notes:**
   - All 167 `candidate_source` URLs in the CSV remain internal acquisition notes only; never rendered as `src` or `href` in Flutter or web templates.
5. **PII Gate Status:** 3,202 / 3,202 rows verified `PASSED_GENERIC_ONLY`. Zero personal identifiers.

### D. Synchronized Multi-Tier Acquisition Plan ($0.00 Procurement Cost)

| Acquisition Tier | Target Scope & Series | Sourcing Repository & Method | Exact Count | Est. Cost |
| :--- | :--- | :--- | :--- | :--- |
| **Tier 1: Internal Scrubbed GCS & Staged Archive** | Modern US Coins (1900–2026), Commemoratives, Eagles, State Quarters, Lincoln, Jefferson, Roosevelt, Washington, Kennedy, Morgan, Peace | Ingest from local scrubbed archives into internal bucket. | **2,354** | **$0.00** |
| **Tier 2: Wikimedia Commons / Smithsonian NNC Mirror** | 18th & 19th Century Classic Rarities, Colonials, Flowing Hair, Draped Bust, Capped Bust, Classic Head, Historical Medals (Pre-1929) | Download high-res public domain photographs from Smithsonian NNC / open access collections directly to internal bucket. | **639** | **$0.00** |
| **Tier 3: US Mint / BEP Historical Currency Archive** | Federal Reserve Notes, Silver Certificates, Gold Certificates, National Bank Notes | Ingest public domain currency plates from Bureau of Engraving and Printing / NNC currency collection. | **181** | **$0.00** |
| **Tier 4: Numismatic Partner / Own Photography** | Unique colonial pattern (NAC1.MD.US.GEORGEWASH.MEDAL.1789.XX.BASE.3) | Direct macro-photography using existing studio camera equipment ($0) or partner CC0 contribution. | **1** | **$0.00** |
| **Tier 5: Excluded from PD Ingestion** | Private Medals (Franklin Mint ANCS, Great Men of Medicine, Medallic Art Co 1932–1976) | **Excluded from public domain ingestion.** Retained as reference entries with generic numismatic silhouette placeholders until commercial licensing. | **27** | **$0.00** |
| **TOTAL** | **All Catalog Entries** | **Systematically Accounted For & Internalized** | **3,202** | **$0.00** |

### E. Hard Monthly $ Cap, Billed Egress Realities & Human Manual Shutoff

1. **Hard Monthly Cap:** **$25.00 / month** covering GCS storage + Cloud CDN + Firebase Hosting egress.
   - *Estimated Usage:* 50,000 ad visits * ~400 KB cached catalog payload = ~20 GB egress (~$1.60/month Cloud CDN egress).
   - *Storage Usage:* ~3,200 WebP images * 120 KB = ~384 MB storage (~$0.01/month standard storage).
   - *Firebase Hosting Bandwidth:* First 10 GB free, $0.15/GB thereafter (~$1.50/month for ~20 GB). Total expected operational cost: < $4.00/month.
2. **Infrastructure Identification & Provisioning Scope:**
   - Active studio storage bucket today: `numista-uploads-studio-9101802118-8c9a8`.
   - Dedicated catalog storage bucket `gs://numista-catalog-assets`, Pub/Sub topic `projects/numista-ai/topics/billing-budget-alerts`, and programmatic IAM spend-stop Cloud Functions are **Unbuilt — to be provisioned by Cloud Infrastructure Owner (Founder Eric / Grok Bot CoS)**. No unbuilt resources are treated as active in code.
3. **Billed Egress Reality:**
   - Firebase Hosting CDN egress ($0.15/GB above 10 GB free tier) is the active billed path under Meta ad traffic.
   - Cloud Storage bucket IAM permissions cannot halt Firebase Hosting traffic.
4. **Named Human Operator & Manual Shutoff Procedure (Operational Fail-Safe):**
   - **Named Operator:** Founder Eric / Grok Bot CoS.
   - **Threshold Alert:** Automated billing alert email at **$20.00/month**.
   - **Manual Shutoff Protocol:** If monthly spend nears the $25.00 ceiling, the named human operator immediately executes:
     - For Preview Channel: `firebase hosting:channel:delete pre-ads-preview` (instantly removes preview channel and terminates egress).
     - For Live Production: `firebase hosting:disable` (instantly disables the site) or disables via Firebase Console > Hosting > Three-dots menu > Disable site.
5. **Procurement Cost:** Strict **$0.00**.

---

## 4. Fix 2: Deep Links & Browser History

### A. Grounded Integration with Existing Screen Code
In `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`:
- Lines 68–75 already inspect `widget.initialNacCode` on load.
- When `match` is found, the screen opens the detail modal.
- For web history synchronization, invoke browser history push upon modal open:
  ```dart
  final nacCode = item['nac_code'] ?? item['id'];
  if (nacCode != null && kIsWeb) {
    // Synchronize browser URL bar to /catalog/:nacCode
    // Uses standard window.history API via dart:html / package:web interop
  }
  ```
- Listen for `popstate` to dismiss the modal cleanly if the user presses the browser Back button.

---

## 5. Fix 3: "Ask Morgan" Signed-Out & Signed-In Behavior

### A. Root Cause Analysis
In `catalog_browse_screen.dart` lines 223–228:
`Navigator.of(context).pushNamed('/?route=AiChatScreen', ...)` throws an unhandled navigation route exception because that route name is unregistered.

### B. Solution for Signed-Out Visitors
When an unauthenticated guest clicks "Ask Morgan":
1. Open a clean preview modal: **"Ask Morgan AI"**.
2. **Capability-Accurate Copy:**
   - Title: *"Numismatic AI Assistant"*
   - Body: *"Ask Morgan about US coinage history, mintage figures, mint mark varieties, and key date attributes. Sign in or create a free account to start chatting."*
3. Action buttons: `Sign In` (`/login?redirect=/catalog`), `Create Account` (`/signup?redirect=/catalog`), and `Close`.

### C. Solution for Authenticated Users (Verified Constructor Spec)
Both `p7-v8.9` and `origin/dev` share the identical `MorganChatPopout` constructor (`lib/widgets/morgan_chat_popout.dart`):
```dart
const MorganChatPopout({
  super.key,
  this.initialQuery,
  required this.onClose,
  this.onNavigateToCollection,
});
```
Implementation in `catalog_browse_screen.dart`:
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

---

## 6. Fix 4: Era Filter State Reset on Tab Switch

In `catalog_browse_screen.dart` lines 209–214:
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

In `catalog_browse_screen.dart` lines 128–130:
Eliminate the `year < 1792` OR clause and filter strictly by explicit pre-federal metadata flags:
```dart
if (_selectedEra == 'pre_federal') {
  final bool isPreFederal = (item['is_pre_federal'] == true) || 
                            (item['pre_federal'] == true);
  if (!isPreFederal) return false;
}
```

---

## 8. Fix 6: Outbound Link Removal & Loader Data Wiring

### A. Surgical Outbound Link Deletion in `_buildMintageRow`
In `catalog_browse_screen.dart` lines 987–1023:
```dart
// CURRENT dev:1010-1017:
// InkWell(
//   onTap: () async {
//     final uri = Uri.tryParse(sourceUrl);
//     if (uri != null) await launchUrl(uri);
//   },
//   child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)),
// )
```
**Specification:** Delete the `InkWell` and `launchUrl` call completely.
```dart
  Widget _buildMintageRow(Map<String, dynamic> item) {
    final mintage = item['mintage'] as Map?;
    final val = mintage?['value']?.toString();
    final label = mintage?['label'] as String?;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(
            width: 140,
            child: Text(
              'Mintage:',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF475569)),
            ),
          ),
          Expanded(
            child: val != null && val.isNotEmpty
                ? Text(val, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Color(0xFF0B2545)))
                : Text(label ?? 'Needs source', style: const TextStyle(fontSize: 16, color: Color(0xFF6B6B6B))),
          ),
        ],
      ),
    );
  }
```
*Zero outbound links; zero undefined variables.*

### B. Real Loader Wiring & Valuation Rules
In `_loadCatalog()` (lines 58–63):
1. **Source Data:** Loads `assets/catalog/catalog_public_v1.json`.
2. **CPG Retail Only:** Each entry exposes `cpgRetail` (double) when sourced. Zero wholesale prices are present or displayed.
3. **Valuation Display Precedence (Card Grid):**
   ```dart
   final double? valCpg = (entry['cpgRetail'] as num?)?.toDouble();
   if (valCpg != null && valCpg > 0) {
     // Display formatted CPG Retail price: fmt.format(valCpg)
     // NEVER hidden by pending AI or enrichment flags
   } else {
     // Render gold 'Valuation Pending' chip strictly when valCpg <= 0 or null
   }
   ```
4. **Primary Image Invariant:** If `primary_image_url` is missing or empty, render the SVG silhouette placeholder. Never substitute an AI replica into the primary card slot.

---

## 9. Rollback Strategy & Preview-Before-Live Gate

### A. Dedicated Repo-Safe Rollback Procedures (No `9f04550a` checkouts)
1. **Pre-Execute dev HEAD Recorded:**
   - Pre-execute `origin/dev` HEAD is recorded at execution start (`b0b05808` at review time).
2. **Code Rollback on `dev`:**
   - Execute `git revert` across the complete execute commit set:
     ```bash
     git revert <execute commit set>
     ```
   - Reverts all touched files cleanly: `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, `numista_mobile/firebase.json`, `numista_mobile/lib/main.dart`, and associated assets.
   - Does NOT checkout `18a8b8e5` (which would strip intervening documentation commits).
   - Never touches or checks out from `9f04550a`.
3. **Firebase Hosting Rollback:**
   - If executed on preview channel:
     ```bash
     firebase hosting:channel:delete pre-ads-preview
     ```
   - If deployed to live production:
     Restore previous live release via Firebase Console (Hosting > Release History > Rollback to prior release) or CLI:
     ```bash
     firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live
     ```

### B. Mandatory Preview-Before-Live Gate
**No code or asset deployment touches production `numista.ai` or `numista-vault.web.app` directly.**
1. **Deploy to Preview Channel:**
   ```bash
   cd numista_mobile
   firebase hosting:channel:deploy pre-ads-preview --expires 7d
   ```
2. **Field Tester E2E Verification Checklist:**
   Field Tester conducts complete validation on `https://numista-vault--pre-ads-preview-<hash>.web.app/catalog`:
   - [ ] Confirm zero CSP errors in browser console.
   - [ ] Verify image display and plain-text attributions.
   - [ ] Verify **zero outbound links** (confirm `(source)` link is removed and non-clickable).
   - [ ] Verify **`Foreign Coins` tab is removed** (confirm 100% US-only catalog scope).
   - [ ] Verify **pre-federal filter strictly displays Condition C1 items** (flag-only).
   - [ ] Verify **public card values display strictly CDN CPG retail (`cpgRetail`) only; zero wholesale values**.
   - [ ] Verify **positive CPG retail price is never hidden behind pending flags**.
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
1. **Argon (Gemini 3.8 Auditor):** Scores `v1.6` against all CoS/SAG must-fixes.
2. **Grok Bot CoS:** Reviews and scores (`>= 95` target).
3. **Stand Alone Grok (SAG, grok-4.7):** Reviews and scores (`>= 95` target).
4. **Founder Eric:** Final review and explicit typed **YES**.

### Branch Hygiene:
- All development and plan commits must land on `dev` (or active feature branch `p7-v8.9`).
- Under no circumstances will code changes be committed directly to `origin/main` (Rule 7).
- `origin/main` remains strictly locked at `9f04550a`.

---

## 11. Summary Matrix: CoS-87 / SAG-84 Must-Fix Resolution

| Finding | Issue Description | Source & Impact | Plan v1.6 Resolution Section | Execution Status |
| :---: | :--- | :---: | :--- | :---: |
| **Must-Fix 1** | Rollback pinned to stale commit `18a8b8e5` instead of current `origin/dev` HEAD `b0b05808`; checkout omitted other files | CoS 87 / SAG 84 (Blocking) | **§1, §9.A:** Pinned rollback to actual pre-execute `origin/dev` HEAD (`b0b05808` at review). Uses `git revert <execute commit set>` covering all touched files. No checkouts from 18a8b8e5. | **SPECIFIED IN PLAN** |
| **Must-Fix 2** | Spend stop claimed nonexistent `stop-public-egress` function; bucket IAM cannot stop Firebase Hosting traffic ($0.15/GB) | CoS 87 / SAG 84 (Blocking) | **§1, §3.E:** Struck claims of active IAM/CDN function; acknowledged Hosting CDN egress is the billed path; labeled target resources as unbuilt; named human operator + manual `firebase hosting:disable` / channel delete procedure. | **SPECIFIED IN PLAN** |
| **Must-Fix 3** | Loader in code loads `assets/catalog/catalog_public_v1.json`, not wired to proposed schema; positive retail hidden by pending | CoS 87 / SAG 84 (Blocking) | **§1, §2, §8.B:** Grounded plan in actual loader; specified `cpgRetail` present when sourced; enforced rule that positive retail is never hidden behind pending status; authentic photos only. | **SPECIFIED IN PLAN** |
| **Must-Fix 4** | `(source)` link replacement cited undefined `sourceInstitution` not present in `_buildMintageRow` | CoS 87 / SAG 84 (Blocking) | **§1, §2, §8.A:** Cited exact variables in `_buildMintageRow` (`val`, `label`, `sourceUrl`). Deleted `InkWell` and `launchUrl` completely; plain text mintage display; zero undefined variables. | **SPECIFIED IN PLAN** |
| **Refinement 1** | Deep-link handling should extend existing `initialNacCode` (lines 68–75) | CoS / SAG (Non-blocking) | **§1, §2, §4.A:** Grounded deep-link opening in existing `widget.initialNacCode` handling. | **RESOLVED IN PLAN** |
| **Refinement 2** | Confirm `MorganChatPopout` constructor exists on dev | SAG (Non-blocking) | **§1, §2, §5.C:** Verified constructor is identical on both `p7-v8.9` and `origin/dev`. | **RESOLVED IN PLAN** |
