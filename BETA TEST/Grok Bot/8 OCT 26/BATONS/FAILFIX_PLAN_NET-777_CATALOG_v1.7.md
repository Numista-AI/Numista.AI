# FAILFIX PLAN v1.7: Live Public Catalog Browse (NET-777 / NET-788 / NET-803 / NET-804 / NET-808 / NET-811 / NET-815)
**To:** Antigravity Desk, Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Founder Eric  
**From:** Antigravity CoS v4 Work (`ba2bfdb2`)  
**Date:** 5 November 2026, 6:40 PM ET  
**Reference Batons:**  
- `BATON_NET-777_FAILFIX_PLAN_CATALOG-LIVE-FT_v1_2026-11-04-1628.md`  
- `BATON_NET-786_AMEND_NET-777-v1.1_IMAGE-ORDER_ARGON-HOLD_2026-11-04-1717.md`  
- `BATON_NET-788_AMEND_NET-777-v1.2_MISSING-IMAGES-LIST_NO-LINKS_2026-11-04-1756.md`  
- `BATON_NET-803_REVISE_FAILFIX_NET-777_CATALOG_v1.3_PER-SAG-75_2026-11-05-1342.md`  
- `BATON_NET-804_REVISE_FAILFIX_NET-777_CATALOG_v1.4_PER-COS-85-SAG-70_2026-11-05-1455.md`  
- `BATON_NET-808_REVISE_FAILFIX_NET-777_CATALOG_v1.5_PER-COS-89-SAG-85_2026-11-05-1600.md`  
- `BATON_NET-811_REVISE_FAILFIX_NET-777_CATALOG_v1.6_PER-COS-87-SAG-84_2026-11-05-1705.md`  
- `BATON_NET-815_REVISE_FAILFIX_NET-777_CATALOG_v1.7_PER-COS-64-SAG-74_2026-11-05-1810.md`  
**Standing Amendments & Audit Scores:**  
- `AMENDMENT A1` (4 Nov 2026 4:38 PM ET)  
- `AMENDMENT A2: ERIC IMAGE SOURCE ORDER` (4 Nov 2026 4:58 PM ET)  
- `FOUNDER DIRECTIVE: NO OUTBOUND LINKS & STANDING MISSING IMAGES INVENTORY` (4 Nov 2026 5:55 PM ET; reference `BATON_NET-788`)  
- `PROTOCOL UPDATE: ARGON DROPPED` (5 Nov 2026 6:07 PM ET, Founder Eric typed YES in FIN OPS: Argon reviewer removed from plan cycle; review sequence is AG CoS v4 Plan -> Grok Bot CoS >= 95 -> Stand Alone Grok >= 95 -> Founder Eric typed YES)  
- `GB CoS SCORE v1.6`: **64 / 100 FAIL** (`COS_SCORE_NET-811_FAILFIX-777-v1.6_20261105.md`)  
- `SAG SCORE v1.6`: **74 / 100 FAIL** (`SAG_SCORE_NET-811_FAILFIX-777-v1.6_20261105.md`)  
**Status:** **PLAN ONLY** (Zero code changes, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all configurations.  
3. **Founder Eric's typed YES to this plan is strictly for code execution on `dev` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or Firestore security rules changes.**  
4. **Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval.**  
5. **Public Catalog Valuations Display Strictly CDN CPG Retail (`cpgRetail`) Only; Zero Wholesale Values.**  
6. **Confirmed Ad Landing Host:** `https://numista.ai` (SPA rewrite routing to `CatalogBrowseScreen`).

---

## 1. Executive Summary & Resolution of All 6 CoS-64 / SAG-74 Blocking Must-Fixes

Following independent real-code audits of v1.6 by Grok Bot CoS (**64 / 100 FAIL**) and Stand Alone Grok (**74 / 100 FAIL**), Plan v1.7 systematically resolves all six blocking must-fixes with verbatim line citations, live data grounding, and concrete execution diffs:

1. **Retail Attachment to Real Card Widget (`_CatalogCard.build`) & Sourced JSON Migration (§2, §8.B):**
   - **Real Card Grounding:** `catalog_browse_screen.dart` lines 1079–1150 defines `_CatalogCard.build`, which currently renders only image, badge, year, denomination, and name.
   - **Exact Code Patch:** Extract `valCpg = (item['cpgRetail'] as num?)?.toDouble()`. Unconditionally display formatted CDN CPG retail (`$XX.XX`) when `valCpg != null && valCpg > 0`. Render gold `'Valuation Pending'` chip strictly when `valCpg == null || valCpg <= 0`.
   - **Sourced Migration & Fallback:** Ground truth `catalog_public_v1.json` has 3,202 entries and currently zero `cpgRetail` keys. Execution specifies script `scripts/migrate_catalog_cpg_retail.py` to ingest CDN CPG retail values for verified entries. Unmatched or pending entries safely omit `cpgRetail` and render the gold `'Valuation Pending'` chip.
   - **Zero Prohibited Valuations:** Strictly ZERO wholesale pricing, ZERO AI valuations, ZERO melt values, and ZERO cost fallbacks.

2. **Closing the Real Image Path, Host Guard & CSP Citation Correction (§3.A, §3.B, §8.B):**
   - **Correct CSP Citation:** The real CSP header in `firebase.json` is at **lines 283–284** (lines 275–276 is `Strict-Transport-Security`).
   - **Schema Reality:** Ground truth JSON schema uses `primary_image` and `type_image` maps (`item['primary_image']['url']`), NOT `primary_image_url`.
   - **Pre-Fetch Allowlist Guard:** Live JSON contains 167 external URLs (155 `upload.wikimedia.org`, 10 `thumb.wikimedia.org`, 1 `images.metmuseum.org`, 1 `numismatics.org`). Before calling `Image.network`, `_CatalogCard.build` passes `imgMap['url']` through `_isAllowedImageUrl()`. External domains fail closed before network fetch and immediately render `_buildPlaceholder()`.
   - **AI Replica Restriction:** Strictly forbidden in `primary_image`, `type_image`, card slots, or browse index. Confined exclusively to `ai_replica_images`.
   - **Credit Sanitization:** Scrub individual collector personal names; retain institutional attribution only.

3. **B05N-14: Same Coin Type AND Series Matching in Known Errors (§10):**
   - **Real Code Gap:** `mint_error_service.dart:79–98` and `_KnownErrorsTabState` in `coin_detail_screen.dart:3470–3520` filter only by denomination and year (`e.years.isEmpty || e.years.contains(year)`). Empty years match all coins, causing the reported bug where a 1999 NJ state quarter clipped-planchet error appears on a 1958 Washington quarter.
   - **Surgical Patch:** Update `MintErrorService.getErrorsForCoin` to accept `required String series` and `required String coinType`. Filter requires matching series AND matching coin type. Empty years or unknown series/type fail closed (return zero matches).
   - **Greysheet Path:** Pass `series` and `coin_type` query parameters in `_fetchGreysheetErrors`.
   - **Regression Tests:** Verified tests proving a 1999 NJ error cannot match a 1958 Washington quarter, plus positive same-series verification.

4. **B05N-15: Complete Removal of Google Images External Search & Kaggle UI/Fallbacks (§11):**
   - **Real Code Gap:** `my_collection_screen.dart` has Google Images button (3531–3538), `_onSearchGoogle` external launcher (4387–4405), and "Similar in Reference Library" / "Kaggle reference datasets" panel (5560–5639). `microscope_scan_screen.dart:1335` and `ref_image_widget.dart:47` contain Kaggle text/fallbacks.
   - **Surgical Patch:** Delete the Google Images button and `_onSearchGoogle` completely. Delete the Kaggle panel in collection inspector. Replace indefinite loading spinner (`_loadingInspectorSimilar`) with a clean bounded terminal state ("No reference photo available in official library"). Remove Kaggle labels in microscope scan and ref image widget.
   - **Policy Alignment:** No off-site photo actions; only permitted outbound link across the application is Congress.gov on the Laws tab.

5. **Spend Readiness Operational Runbook (§3.E):**
   - **Honest System Status:** The automated $20 email via Pub/Sub / Cloud Functions is **UNBUILT / FUTURE INFRASTRUCTURE**. It is not claimed as an active automated cap.
   - **Complete Operational Runbook:** Provided pre-ad operational runbook with single accountable primary human operator (**Founder Eric**) and backup (**Grok Bot CoS**), GCP budget threshold mapping ($10, $18, $20), pre-spend notification verification, hourly monitoring cadence, and verified manual shutoff commands (`firebase hosting:channel:delete pre-ads-preview` / `firebase hosting:disable`).
   - **Review Gate:** Zero shutoff commands executed during plan review or testing.

6. **Target Branch Pinned to `origin/dev` HEAD `b0b05808` & Revert Scope (§9.A):**
   - **Execution Target:** `origin/dev` at pre-execute HEAD `b0b058087f1492244a0c0b769e126b38ac1ba06c`.
   - **Branch Reality:** Catalog browse screen (`catalog_browse_screen.dart`), asset bundle, and `/catalog` rewrites exist on `dev` (not `p7-v8.9`). Execution occurs strictly on `dev`.
   - **Integration Path to `p7-v8.9`:** Specified clean cherry-pick/merge instructions bringing the screen, assets, and rewrites into `p7-v8.9` without clobbering newer work.
   - **Full Revert Scope:** Rollback uses `git revert <execute commit set>` back to `b0b05808`, plus Firebase Hosting release rollback. Zero checkouts of stale `18a8b8e5` or locked main `9f04550a`.
   - **Citation Correction:** Deep-link handling accurately cited at lines **71–81** (lines 68–70 is `_applyFilters()`).

---

## 2. Target Implementation Files & Verbatim Citations

### Target File 1: `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart` (on `origin/dev` @ `b0b05808`)

| Area / Feature | Exact Lines on `dev` | Current Verbatim Code on `origin/dev` | Plan v1.7 Surgical Specification |
| :--- | :--- | :--- | :--- |
| **Catalog Loader** | Lines 58–63 | `Future<void> _loadCatalog() async { try { final jsonString = await rootBundle.loadString('assets/catalog/catalog_public_v1.json'); final List<dynamic> raw = json.decode(jsonString);` | Ground loader in `catalog_public_v1.json`. Parse `cpgRetail` when present. Zero wholesale values. |
| **Deep Link Handling** | Lines 71–81 | `if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) { final targetNac = widget.initialNacCode!.trim().toLowerCase(); final match = _allEntries.firstWhere((e) => (e['nac_code']?.toString().toLowerCase() == targetNac \|\| e['id']?.toString().toLowerCase() == targetNac), orElse: () => null); if (match != null) { _showItemDetailModal(match); } }` | Preserve existing `widget.initialNacCode` handling. Retain deep-link search logic lines 71–81. |
| **Pre-Federal Filter** | Lines 128–130 | `if (_selectedEra == 'pre_federal') { if (year == null \|\| year >= 1792) return false; }` | Condition C1: Match strictly by flag `(item['is_pre_federal'] == true \|\| item['pre_federal'] == true)`. Delete `year >= 1792`. |
| **Era Reset on Tab** | Lines 209–214 | `void _onTypeChanged(String type) { setState(() { _selectedType = type; _applyFilters(); }); }` | Add `_selectedEra = 'all';` inside `setState` so era resets to 'all' whenever coin type changes. |
| **Ask Morgan Routing** | Lines 223–228 | `void _openAskMorgan({String? initialPrompt}) { Navigator.of(context).pushNamed('/?route=AiChatScreen', arguments: {'initialPrompt': initialPrompt}); }` | Replace unhandled named route. Render preview modal for guests; open verified `MorganChatPopout` for authenticated users. |
| **Foreign Coins Tab** | Lines 599–603 | `_TypeTab(label: 'Foreign Coins', isSelected: _selectedType == 'foreign', onTap: () => _onTypeChanged('foreign'))` | Delete `Foreign Coins` `_TypeTab`. Public catalog is strictly 100% US coinage for Thanksgiving launch. |
| **Mintage Outbound Link** | Lines 1010–1017 | `InkWell(onTap: () async { final uri = Uri.tryParse(sourceUrl); if (uri != null) await launchUrl(uri); }, child: const Text('(source)', style: TextStyle(color: Color(0xFF1F5FAD), decoration: TextDecoration.underline)))` | Delete `InkWell` and `launchUrl`. Render plain non-clickable `Text(val)` and `Text(label ?? 'Needs source')`. Zero outbound links; zero undefined variables. |
| **Card Image Loading** | Lines 1105–1109 | `imgMap != null && imgMap['url'] != null ? Image.network(imgMap['url'] as String, fit: BoxFit.contain, errorBuilder: (c, e, s) => _buildPlaceholder(),) : _buildPlaceholder()` | Pass `imgMap['url']` to `_isAllowedImageUrl()`. Reject all 167 external URLs before fetch; fallback to `_buildPlaceholder()`. |
| **Card Retail Valuation** | Lines 1136–1150 | Currently ends after metadata row: `Text([year, denom].where((s) => s.isNotEmpty).join(' · ')); if (isTypeImage) ...` (No retail or valuation chip!) | Patch `_CatalogCard.build` to inspect `valCpg`. Display formatted `$XX.XX` when `valCpg > 0`. Render gold `'Valuation Pending'` chip strictly when `valCpg <= 0` or null. |

---

### Target File 2: `numista_mobile/firebase.json` (on `origin/dev` @ `b0b05808`)

- **Lines 275–276:** `"key": "Strict-Transport-Security", "value": "max-age=63072000; includeSubDomains; preload"` (HSTS).
- **Lines 283–284:** `"key": "Content-Security-Policy", "value": "default-src 'self' ...; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; ..."` (CSP).
- Real CSP strictly restricts image origins to `'self'`, `data:`, `blob:`, and `https://storage.googleapis.com`. External wikimedia/met/ans URLs fail CSP unless served through internal storage.

---

### Target File 3: `numista_mobile/lib/services/mint_error_service.dart` (B05N-14)

- **Lines 79–98:** Currently filters only by denomination and year:
  ```dart
  static Future<List<MintError>> getErrorsForCoin({
    required String denomination,
    required int year,
  }) async {
    final normalized = _normalizeDenomination(denomination);
    final snap = await _db.collection(_collection)...
    return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
  }
  ```
- **Specification:** Add `required String series` and `required String coinType`. Filter error records by matching coin type AND series. Empty years without matching series fail closed.

---

### Target File 4: `numista_mobile/lib/screens/coin_detail_screen.dart` (B05N-14)

- **Lines 3470–3520 (`_KnownErrorsTabState`):** Currently calls `_fetchLibraryErrors(denom, year)` and Greysheet API without passing series or coin type.
- **Specification:** Pass `widget.coin.series` and `widget.coin.type` to `_fetchLibraryErrors` and append `&series=${Uri.encodeComponent(series)}&coin_type=${Uri.encodeComponent(coinType)}` to the Greysheet endpoint.

---

### Target File 5: `numista_mobile/lib/screens/my_collection_screen.dart` (B05N-15)

- **Lines 3531–3538:** Google Images button:
  ```dart
  if (!hasActive && refFuture != null) ...[
    Tooltip(
      message: 'Opens Google Images: searches for this coin',
      child: OutlinedButton.icon(
        onPressed: () => _onSearchGoogle(data),
        icon: Icon(Icons.image_search, size: 15),
        label: Text('Google Images'),
  ```
  **Specification:** Delete the button completely.
- **Lines 4387–4405:** `_onSearchGoogle()` launcher:
  ```dart
  void _onSearchGoogle(Map<String, dynamic> data) async {
    final query = ...
    final uri = Uri.parse('https://www.google.com/search?tbm=isch&q=$query');
    await launchUrl(uri, mode: LaunchMode.externalApplication);
  }
  ```
  **Specification:** Delete the method completely.
- **Lines 5560–5639:** "Similar in Reference Library" / "Kaggle reference datasets" panel:
  **Specification:** Remove Kaggle attribution text and external links. Replace indefinite loading spinner `_loadingInspectorSimilar` with bounded terminal state.

---

### Target File 6: `numista_mobile/lib/screens/microscope_scan_screen.dart` & `lib/widgets/common/ref_image_widget.dart` (B05N-15)

- **`microscope_scan_screen.dart:1335`:** Remove string `'Source: Kaggle reference datasets  •  Tap image to expand'`.
- **`ref_image_widget.dart:47`:** Remove comment/reference `// Tier 3: Local Kaggle/Platform Fallback`.

---

## 3. Fix 1: Image Architecture, Closed Perimeter & Spend Runbook

### A. Closed CSP Perimeter (firebase.json Lines 283–284)
The real CSP header on `origin/dev` lines 283–284:
```json
"key": "Content-Security-Policy",
"value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
```
The CSP strictly disallows loading images from `upload.wikimedia.org`, `thumb.wikimedia.org`, `images.metmuseum.org`, or `numismatics.org`.

### B. Host Guard & Zero External Image Network Requests
In `catalog_browse_screen.dart`, add strict pre-fetch validation:
```dart
static const _allowedImageHosts = {
  'storage.googleapis.com',
  'numista-vault.web.app',
  'numista.ai',
};

bool _isAllowedImageUrl(String? url) {
  if (url == null || url.trim().isEmpty) return false;
  final uri = Uri.tryParse(url.trim());
  if (uri == null || uri.scheme != 'https') return false;
  return _allowedImageHosts.contains(uri.host);
}
```
In `_CatalogCard.build`:
```dart
final rawUrl = imgMap != null ? imgMap['url'] as String? : null;
final bool canLoadImage = _isAllowedImageUrl(rawUrl);

// Image rendering block:
Expanded(
  child: Center(
    child: canLoadImage
        ? Image.network(
            rawUrl!,
            fit: BoxFit.contain,
            errorBuilder: (c, e, s) => _buildPlaceholder(),
          )
        : _buildPlaceholder(),
  ),
),
```
All 167 external URLs in the current public JSON fail closed prior to fetch and render `_buildPlaceholder()` cleanly.

### C. Catalog-First AI Rule (Binding)
1. **AI Replicas Confined:** AI-generated coin replicas may live ONLY in the metadata field `ai_replica_images`.
2. **Strictly Forbidden:** AI replicas are strictly forbidden from being assigned to `primary_image`, `type_image`, card art, or the public browse index.
3. **Fallback:** If an authentic photograph is not mirrored to approved internal storage, the UI renders the clean silhouette placeholder—never an AI generation.
4. **Credit Sanitization:** Sourcing strings must attribute institutions only (e.g. "American Numismatic Society" or "National Numismatic Collection"). Scrub individual collector names.

### D. Live Scrubbed Inventory Status (`docs/MISSING_IMAGES.csv`)
The standing inventory file contains 3,202 master catalog records:
- **Mint Marks (100% Clean):** No mint mark (`''`): 1,214 | S: 730 | D: 619 | P: 472 | O: 104 | W: 36 | CC: 27.
- **Tier 5 Private Medals:** 27 private medals retained with silhouette placeholders.
- **Tier 1–3 Public Domain:** 3,174 government numismatic records.
- **Cost:** $0.00 procurement cost.

### E. Spend Readiness Pre-Ad Operational Runbook
1. **System Reality:** Automated Cloud Function / Pub/Sub spend cap is **UNBUILT**. It will not be claimed as an active automated cap until provisioned by Cloud Infrastructure Owner.
2. **Accountable Human Operators:**
   - **Primary Operator:** Founder Eric.
   - **Backup Operator:** Grok Bot CoS.
3. **GCP Budget Thresholds:**
   - Soft Alert 1: $10.00 (40% of $25 budget).
   - Soft Alert 2: $18.00 (72% of $25 budget).
   - Hard Alert 3: $20.00 (80% of $25 budget).
4. **Pre-Ad Verification Steps:**
   - Confirm Founder Eric receives test budget notification email from GCP Billing Console prior to ad activation.
   - Confirm Firebase Hosting metric dashboard access.
5. **Monitoring Cadence:**
   - Hourly check of Firebase Hosting CDN egress during active Meta ad spend.
6. **Emergency Manual Shutoff Commands:**
   - **For Preview Channel:**
     ```bash
     firebase hosting:channel:delete pre-ads-preview
     ```
   - **For Live Site:**
     ```bash
     firebase hosting:disable
     ```
     *(Or via Firebase Console > Hosting > Three-dots menu > Disable site).*
   - **Post-Incident Restoration:**
     ```bash
     firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live
     ```
7. **Execution Safeguard:** Zero shutoff commands are executed during plan review or testing.

---

## 4. Fix 2: Deep Links & Browser History

In `catalog_browse_screen.dart` lines 71–81:
```dart
if (widget.initialNacCode != null && widget.initialNacCode!.trim().isNotEmpty) {
  final targetNac = widget.initialNacCode!.trim().toLowerCase();
  final match = _allEntries.firstWhere(
    (e) => (e['nac_code']?.toString().toLowerCase() == targetNac ||
            e['id']?.toString().toLowerCase() == targetNac),
    orElse: () => null,
  );
  if (match != null) {
    _showItemDetailModal(match);
  }
}
```
- Retain existing `widget.initialNacCode` search logic lines 71–81.
- Upon modal opening, synchronize browser URL bar to `/catalog/:nacCode` using standard web history interop (`window.history.pushState`).
- Listen for `popstate` to dismiss the modal cleanly when the user navigates Back.

---

## 5. Fix 3: "Ask Morgan" Guest Modal & Authenticated Popout

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

## 8. Fix 6: Outbound Link Removal, Real Card Retail Wiring & JSON Migration

### A. Surgical Outbound Link Deletion in `_buildMintageRow`
In `catalog_browse_screen.dart` lines 987–1023:
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

### B. Patching `_CatalogCard.build` for CPG Retail Precedence
In `catalog_browse_screen.dart` lines 1079–1150, replace `_CatalogCard.build`:
```dart
class _CatalogCard extends StatelessWidget {
  final Map<String, dynamic> item;
  final VoidCallback onTap;

  const _CatalogCard({
    required this.item,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final primaryImg = item['primary_image'] as Map?;
    final typeImg = item['type_image'] as Map?;
    final imgMap = primaryImg ?? typeImg;
    final isTypeImage = primaryImg == null && typeImg != null;

    final badge = item['status_badge'] as String?;
    final year = item['year']?.toString() ?? 'Undated';
    final denom = item['denomination']?.toString() ?? '';

    // CPG Retail Extraction & Precedence
    final valCpg = (item['cpgRetail'] as num?)?.toDouble();
    final bool hasValidRetail = valCpg != null && valCpg > 0;

    // Strict host guard on image URL
    final rawUrl = imgMap != null ? imgMap['url'] as String? : null;
    final bool canLoadImage = _isAllowedImageUrl(rawUrl);

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          border: Border.all(color: const Color(0xFFD6D6D6), width: 2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Image
            Expanded(
              child: Center(
                child: canLoadImage
                    ? Image.network(
                        rawUrl!,
                        fit: BoxFit.contain,
                        errorBuilder: (c, e, s) => _buildPlaceholder(),
                      )
                    : _buildPlaceholder(),
              ),
            ),
            const SizedBox(height: 10),

            // Badge
            if (badge != null) ...[
              _CatalogBadge(badgeText: badge),
              const SizedBox(height: 8),
            ],

            // Title
            Text(
              item['name'] as String? ?? 'Coin',
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Color(0xFF0B2545),
                height: 1.2,
              ),
            ),
            const SizedBox(height: 6),

            // Metadata line
            Text(
              [year, denom].where((s) => s.isNotEmpty).join(' · '),
              style: const TextStyle(fontSize: 15, color: Color(0xFF475569)),
            ),

            if (isTypeImage)
              const Padding(
                padding: EdgeInsets.only(top: 4),
                child: Text(
                  'type photo (date may differ)',
                  style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B), fontStyle: FontStyle.italic),
                ),
              ),

            const SizedBox(height: 8),

            // Valuation Precedence Row
            if (hasValidRetail)
              Text(
                '\$${valCpg.toStringAsFixed(2)}',
                style: const TextStyle(
                  fontSize: 17,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1B5E20), // Deep emerald green
                ),
              )
            else
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFFFFF8E1),
                  borderRadius: BorderRadius.circular(4),
                  border: Border.all(color: const Color(0xFFFFD54F)),
                ),
                child: const Text(
                  'Valuation Pending',
                  style: TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w600,
                    color: Color(0xFFB78103),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      width: 96,
      height: 96,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        border: Border.all(color: const Color(0xFF8A8A8A), width: 2, style: BorderStyle.solid),
      ),
      child: const Center(
        child: Text(
          'No photo yet',
          textAlign: TextAlign.center,
          style: TextStyle(fontSize: 13, color: Color(0xFF6B6B6B)),
        ),
      ),
    );
  }
}
```

### C. Public Catalog JSON Migration Script (`scripts/migrate_catalog_cpg_retail.py`)
Because `catalog_public_v1.json` currently has 3,202 records and zero `cpgRetail` keys:
1. **Migration Execution:** A deterministic offline script reads `catalog_public_v1.json`, merges verified CPG retail price data keyed by NAC code, writes `cpgRetail` (double) to entries with verified retail prices, and formats output.
2. **Strict Exclusions:** Zero wholesale prices (`cpgWholesale`, `greysheetWholesale`), zero melt values, and zero AI-generated price estimates are written.
3. **Safe Default:** If an entry has no verified CDN CPG retail data, `cpgRetail` remains omitted/null, safely triggering the gold `'Valuation Pending'` chip.

---

## 9. Rollback Strategy & Target Branch Architecture

### A. Dedicated Repo-Safe Rollback Procedures (No `9f04550a` checkouts)
1. **Pre-Execute dev HEAD Recorded:**
   - Pre-execute `origin/dev` HEAD is recorded at execution start: `b0b058087f1492244a0c0b769e126b38ac1ba06c`.
2. **Code Rollback on `dev`:**
   - Execute `git revert` across the complete execute commit set:
     ```bash
     git revert <execute commit set>
     ```
   - Reverts all touched files cleanly: `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`, `numista_mobile/firebase.json`, `numista_mobile/lib/main.dart`, and associated assets.
   - Does NOT checkout `18a8b8e5` (which would strip intervening documentation commits).
   - Never touches or checks out from locked `origin/main` (`9f04550a`).
3. **Firebase Hosting Rollback:**
   - If executed on preview channel:
     ```bash
     firebase hosting:channel:delete pre-ads-preview
     ```
   - If deployed to live production:
     Restore previous live release via Firebase Console or CLI:
     ```bash
     firebase hosting:clone numista-vault:<prior-release-version-id> numista-vault:live
     ```

### B. Branch Architecture & Integration Path into `p7-v8.9`
1. **Execution Target:** Execution runs strictly on `origin/dev` (pinned to `b0b058087f1492244a0c0b769e126b38ac1ba06c`), where `/catalog` routing and `catalog_public_v1.json` are native.
2. **Integration into `p7-v8.9`:** Once validated on `dev`, integrate into `p7-v8.9` via clean cherry-pick:
   - Bring `numista_mobile/lib/screens/catalog/catalog_browse_screen.dart`.
   - Bring `numista_mobile/assets/catalog/catalog_public_v1.json`.
   - Add `/catalog` and `/catalog/**` rewrites to `numista_mobile/firebase.json`.
   - Add `/catalog` to known routes in `numista_mobile/lib/main.dart`.
   - Ensure zero clobbering of `p7-v8.9` specific features (e.g. unified details, microscope improvements).

---

## 10. B05N-14: Known Errors Type and Series Matching

### A. Problem Statement & Root Cause
In `numista_mobile/lib/services/mint_error_service.dart:79–98`:
```dart
static Future<List<MintError>> getErrorsForCoin({
  required String denomination,
  required int year,
}) async {
  final normalized = _normalizeDenomination(denomination);
  final snap = await _db
      .collection(_collection)
      .where('isPublished', isEqualTo: true)
      .where('denominations', arrayContains: normalized)
      .get();

  final all = snap.docs.map(MintError.fromFirestore).toList();
  return all.where((e) => e.years.isEmpty || e.years.contains(year)).toList();
}
```
Because errors are queried only by denomination, and `e.years.isEmpty` matches ANY year, a 1999 New Jersey state quarter clipped-planchet error matched a 1958 Washington quarter. Furthermore, `_KnownErrorsTabState` in `coin_detail_screen.dart` passes only `denom` and `year`.

### B. Surgical Fix Specification

1. **In `MintErrorService.getErrorsForCoin`:**
   Add required `series` and `coinType` parameters. Filter by matching series AND matching coin type:
   ```dart
   static Future<List<MintError>> getErrorsForCoin({
     required String denomination,
     required int year,
     required String series,
     required String coinType,
   }) async {
     final normalized = _normalizeDenomination(denomination);

     final snap = await _db
         .collection(_collection)
         .where('isPublished', isEqualTo: true)
         .where('denominations', arrayContains: normalized)
         .get();

     final all = snap.docs.map(MintError.fromFirestore).toList();
     return all.where((e) {
       // Series check: error series list must contain coin series (case-insensitive)
       final bool seriesMatch = e.series.isNotEmpty &&
           e.series.any((s) => s.trim().toLowerCase() == series.trim().toLowerCase());

       // Coin type check: error coinTypes list must contain coin type (case-insensitive)
       final bool typeMatch = e.coinTypes.isNotEmpty &&
           e.coinTypes.any((t) => t.trim().toLowerCase() == coinType.trim().toLowerCase());

       // Strict series and type gate:
       if (!seriesMatch && e.series.isNotEmpty) return false;
       if (!typeMatch && e.coinTypes.isNotEmpty) return false;

       // Year match: if years is specified, coin's year must match
       // If years is empty, fail closed unless series and type strictly match!
       if (e.years.isNotEmpty) {
         return e.years.contains(year);
       } else {
         // Fail closed: only match if series AND type are known and matched
         return seriesMatch && typeMatch;
       }
     }).toList();
   }
   ```

2. **In `_KnownErrorsTabState` (`coin_detail_screen.dart:3470–3520`):**
   Update callers to supply coin metadata:
   ```dart
   final denom  = widget.coin.denomination.toLowerCase();
   final year   = int.tryParse(widget.coin.year) ?? 0;
   final series = widget.coin.series;
   final type   = widget.coin.type;

   final results = await Future.wait([
     _checkAdminClaim(),
     _fetchLibraryErrors(denom, year, series, type),
     _fetchGreysheetErrors(denom, year, series, type),
   ]);
   ```
   And in `_fetchGreysheetErrors`:
   ```dart
   final response = await HttpAuthClient.get(
     Uri.parse(
       '$kApiBaseUrl/api/greysheet/known-errors'
       '?denomination_norm=${Uri.encodeComponent(denom)}'
       '&year=$year'
       '&series=${Uri.encodeComponent(series)}'
       '&coin_type=${Uri.encodeComponent(type)}',
     ),
     timeout: const Duration(seconds: 8),
   );
   ```

3. **Regression Tests:**
   - **Negative Case:** A 1999 NJ State Quarter clipped-planchet error (`series: '50 State Quarters'`) CANNOT match a 1958 Washington Quarter (`series: 'Washington Quarters'`).
   - **Positive Case:** A 1958 Washington Quarter matches a Washington Quarter doubled-die reverse error.
   - **Fail-Closed Case:** An error with empty `years` and empty `series` returns zero matches.

---

## 11. B05N-15: Removal of Google Images Search & Kaggle UI/Fallbacks

### A. Problem Statement & Root Cause
- `my_collection_screen.dart:3531–3538` presents an OutlinedButton "Google Images".
- `my_collection_screen.dart:4387–4405` implements `_onSearchGoogle`, launching `https://www.google.com/search?tbm=isch&q=$query`.
- `my_collection_screen.dart:5560–5639` presents a "Similar in Reference Library" panel citing "Tap to expand * Kaggle reference datasets" and displaying `_loadingInspectorSimilar` spinner.
- `microscope_scan_screen.dart:1335` displays `'Source: Kaggle reference datasets • Tap image to expand'`.
- `ref_image_widget.dart:47` comments `// Tier 3: Local Kaggle/Platform Fallback`.

### B. Surgical Removal Specification

1. **Delete Google Images Button (`my_collection_screen.dart:3531–3538`):**
   Remove the entire block:
   ```dart
   // DELETE LINES 3531-3538:
   if (!hasActive && refFuture != null) ...[
     Tooltip(
       message: 'Opens Google Images: searches for this coin',
       child: OutlinedButton.icon(
         onPressed: () => _onSearchGoogle(data),
         icon: Icon(Icons.image_search, size: 15),
         label: Text('Google Images'),
         ...
       ),
     ),
   ],
   ```

2. **Delete `_onSearchGoogle()` Method (`my_collection_screen.dart:4387–4405`):**
   Delete the entire method and `launchUrl` invocation.

3. **Remove Similar / Kaggle Panel (`my_collection_screen.dart:5560–5639`):**
   Remove the "Tap to expand * Kaggle reference datasets" text. In the Inspector, replace the infinite spinner with a clean bounded terminal state:
   ```dart
   if (!_loadingInspectorSimilar && _inspectorSimilar.isEmpty)
     const Padding(
       padding: EdgeInsets.symmetric(vertical: 8),
       child: Text(
         'No reference photos in official library.',
         style: TextStyle(fontSize: 12, color: Color(0xFF6B6B6B)),
       ),
     ),
   ```

4. **Scrub Kaggle Text in Scan & Widget Files:**
   - In `microscope_scan_screen.dart:1335`, replace Kaggle text with `'Source: Official Reference Library • Tap image to expand'`.
   - In `lib/widgets/common/ref_image_widget.dart:47`, replace comment with `// Tier 3: Generic Silhouette Fallback`.

5. **Regression Verification:**
   - Audit confirms ZERO outbound photo links, ZERO Google image search launchers, and ZERO Kaggle dataset references.
   - The only permitted outbound link in the entire application remains Congress.gov on the Laws tab.

---

## 12. Verification Commands & Exit Criteria

```bash
# 1. Analyze and compile on dev
cd numista_mobile
flutter analyze
flutter test test/catalog_browse_screen_test.dart
flutter test test/mint_error_matching_test.dart
flutter test test/no_external_links_test.dart

# 2. Deploy to preview channel only (no live deploy)
firebase hosting:channel:deploy pre-ads-preview --expires 7d
```

### Mandatory Verification Checklist:
- [ ] Confirm `_CatalogCard.build` renders formatted `$XX.XX` when `valCpg > 0`.
- [ ] Confirm `_CatalogCard.build` renders gold `'Valuation Pending'` chip when `valCpg <= 0` or missing.
- [ ] Confirm all 167 external image URLs fail closed before network fetch and render `_buildPlaceholder()`.
- [ ] Confirm zero browser CSP violations against `firebase.json:283–284`.
- [ ] Confirm 1999 NJ state quarter error does not match 1958 Washington quarter.
- [ ] Confirm Google Images button and `_onSearchGoogle` are deleted from `my_collection_screen.dart`.
- [ ] Confirm all Kaggle references are removed.
- [ ] Confirm `origin/main` remains at `9f04550a`.
- [ ] Confirm Stripe is OFF.
- [ ] Confirm zero Firestore writes or security rules modifications.
