# ARGON REVIEW — `NET-780` Split Failfix Plans v1 (`NET-780a`, `NET-780b`, `NET-780c`, `NET-780d`)

**Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)  
**Date:** 2026-11-04 17:52 ET  
**Baton:** `BETA TEST\Grok Bot\8 OCT 26\RADIO NET\BATON_NET-780_ARGON_REVIEW_FAILFIX_SPLIT_v1.md`  
**Target Plans:**
1. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md` (136 lines)
2. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780b_CARDS_v1.md` (208 lines)
3. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780c_IMAGES_v1.md` (139 lines)
4. `1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780d_SPLASH_v1.md` (149 lines)  
**Mode:** PLAN REVIEW ONLY (`NO EXECUTE` — `origin/main` stays `9f04550a`, live site untouched, Step 1b live Firestore rules deploy & SKU dictionary seed on strict HOLD, Stripe OFF)  
**Overall Verdict:** **PASS WITH 2 EXECUTION-TIME MUST-FIXES IN `NET-780b` — `95 / 100` Composite**
* **`NET-780a` (Build Stamp):** `96 / 100` PASS (0 Blocking Must-Fixes, 1 Path Advisory)
* **`NET-780b` (Broken Cards & Pending Pricing):** `92 / 100` CONDITIONAL PASS (2 Execution-Time Must-Fixes Caught in `kFallbackUsMintSkus` Type/Key & `26EA` Year Inference)
* **`NET-780c` (Images & CSP):** `96 / 100` PASS (0 Blocking Must-Fixes, 1 `connect-src` Advisory)
* **`NET-780d` (Splash Screen Latency):** `97 / 100` PASS (0 Blocking Must-Fixes, 1 Rebuild-Guard Advisory)

---

## 1. Per-Plan Audit & Verbatim Code Verification (Read in This Turn)

### 1.1 Track A: `FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md` — Score: `96 / 100 (PASS)`

* **Verbatim Repo Citations Checked in This Turn:**
  * **`numista_mobile\firebase.json:181-189`**:
    ```json
    181:       {
    182:         "source": "/version.json",
    183:         "headers": [
    184:           {
    185:             "key": "Cache-Control",
    186:             "value": "no-cache, no-store, must-revalidate"
    187:           }
    188:         ]
    189:       },
    ```
    Matches `FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md:28-36` verbatim.
* **Plan Snippet Checked (`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780a_BUILD-STAMP_v1.md:60-65, 96-99, 120-121`):**
  ```python
  60: def stamp_version():
  61:     web_dir = Path("build/web")
  62:     version_file = web_dir / "version.json"
  63:     if not version_file.exists():
  64:         print(f"ERROR: {version_file} not found. Run flutter build web first.", file=sys.stderr)
  65:         sys.exit(1)
  ```
  ```bash
  96: cd numista_mobile
  97: flutter build web --release
  98: python ../tools/stamp_build_version.py
  99: firebase hosting:channel:deploy p7-gate --expires 30d
  ```
  ```bash
  120:    python tools/stamp_build_version.py
  121:    cat numista_mobile/build/web/version.json
  ```
* **Advisory for `NET-780a`:**
  1. **Resolve `version.json` Relative to `__file__` (`line 61` vs `line 120`):** In `line 98`, `stamp_build_version.py` is run from `numista_mobile/` (`Path("build/web/version.json")`), whereas in `line 120` it is run from the repo root (`python tools/stamp_build_version.py`), where `Path("build/web/version.json")` does not exist (`numista_mobile/build/web/version.json`). Resolving `Path(__file__).resolve().parent.parent / "numista_mobile" / "build" / "web" / "version.json"` makes both commands succeed regardless of working directory. Also pin `--project studio-9101802118-8c9a8` on `line 99`.

---

### 1.2 Track B: `FAILFIX_PLAN_NET-780b_CARDS_v1.md` — Score: `92 / 100 (PASS WITH 2 EXECUTION MUST-FIXES)`

* **Verbatim Repo Citations Checked in This Turn:**
  * **`numista_mobile\lib\services\canonical_mint_asset_service.dart:107-122, 162-172, 457-488`**:
    ```dart
    107:     final year = _normYear(data['year'] ?? data['Year']);
    108:     final prog = (data['Program/Series'] ?? data['Program / Series'] ?? data['program_series'] ?? '').toString().toLowerCase();
    109:     final theme = (data['Theme/Subject'] ?? data['theme_subject'] ?? '').toString().toLowerCase();
    110:     final title = (data['title'] ?? data['name'] ?? '').toString().toLowerCase();
    111:     final cond = <Object?>[
    112:       data['Condition'], data['condition'],
    113:       data['Variety'], data['variety'],
    114:       data['Strike Type'], data['strike_type'],
    115:       data['Denomination'], data['denomination'],
    116:     ].where((v) => v != null).map((v) => v.toString().toLowerCase()).join(' ');
    117:     final combined = '$prog $theme $title $cond';
    118:     if (year == '2026' &&
    119:         RegExp(r'\b(american|silver)\s+eagle\b').hasMatch(combined) &&
    120:         !RegExp(r'\b(gold|platinum|palladium)\b').hasMatch(combined)) {
    121:       return '26EA';
    122:     }
    ```
    ```dart
    162:     final primaryTitle = <String>[
    163:       (data['title'] ?? '').toString().trim(),
    164:       (data['name'] ?? '').toString().trim(),
    165:       (data['Theme/Subject'] ?? '').toString().trim(),
    166:       (data['theme_subject'] ?? '').toString().trim(),
    167:       (data['Program / Series'] ?? data['Program/Series'] ?? '').toString().trim(),
    168:       (data['program_series'] ?? '').toString().trim(),
    169:       (data['description'] ?? '').toString().trim(),
    170:     ].where((s) => s.isNotEmpty).join(' ');
    171: 
    172:     final year = _normYear(data['year'] ?? data['Year']);
    ```
    ```dart
    457:     // 3. 2023 American Women Quarters (Synthetic Tracker B26-14..B26-18)
    458:     if (cleanYear == '2023') {
    459:       const awqObv =
    460:           '$_base/2023_series/2023_american_women_quarters_shared_obverse.jpg';
    ```
  * **`numista_mobile\lib\screens\my_collection_screen.dart:2996-3023, 3170-3188`**:
    ```dart
    2996:         final year = _rowField(m, 'year', _F.year).replaceAll(RegExp(r'\.0+$'), '');
    2997:         final mint = _rowField(m, 'mint_mark', _F.mintMark);
    2998:         final denom = _rowField(m, 'denomination', _F.denomination);
    2999:         final series = _rowField(m, 'program_series', _F.programSeries);
    3000:         final variety = _rowField(m, 'variety', _F.variety);
    3001:         final condition = _rowField(m, 'condition', _F.condition);
    3002:         final theme = _rowField(m, 'theme_subject', _F.themeSubject);
    3003:         
    3004:         final yearMint = (mint.isNotEmpty && mint != 'None') ? '$year$mint' : year;
    3005:         var label = theme.isNotEmpty ? theme : denom;
    ...
    3017:         final valCpg = _parseNumber(m['cpgRetail']);
    3018:         final finalVal = valCpg;
    3019:         
    3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
    3021:         final valueText = finalVal > 0 
    3022:             ? fmt.format(finalVal) 
    3023:             : (m[_F.aiValue]?.toString() ?? '—');
    ```
    ```dart
    3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
    3171:                         Container(
    ...
    3178:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
    3179:                         )
    3180:                       else
    3181:                         Text(
    3182:                           valueText,
    ```
  * **`numista_mobile\lib\screens\add_coins_hub.dart:116-124`**:
    ```dart
    116: @visibleForTesting
    117: const Map<String, Map<String, dynamic>> kFallbackUsMintSkus = {
    118:   '26EA': {
    119:     'sku': '26EA',
    120:     'name': 'American Silver Eagle Proof',
    121:     'program_series': 'American Silver Eagle',
    122:     'year': '2026',
    123:     'item_type': 'coin',
    124:   },
    ```
  * **`1 NUMISTA.AI\Grok CoS to Antigravity\INBOX\FAILFIX_PLAN_NET-780b_CARDS_v1.md:160-163`**:
    ```dart
    160:    final canonSku = CanonicalMintAssetService.extractSku(m);
    161:    final fallbackMintPrice = canonSku.isNotEmpty ? (kFallbackUsMintSkus[canonSku]?.issuePrice ?? 0.0) : 0.0;
    162:    
    163:    final finalVal = valCpg > 0 ? valCpg : (fallbackMintPrice > 0 ? fallbackMintPrice : valPurchase);
    ```

* **2 Execution-Time Must-Fixes Caught in `NET-780b`:**
  1. **Must-Fix B1 (`kFallbackUsMintSkus[canonSku]?.issuePrice` Compile Error at `NET-780b:161`):**
     * As shown in `numista_mobile\lib\screens\add_coins_hub.dart:117-124` above, `kFallbackUsMintSkus` is typed as `const Map<String, Map<String, dynamic>>` (a nested `Map`, not a Dart class with an `.issuePrice` getter), does not currently include an `'issue_price'` key on `'26EA'`, and `add_coins_hub.dart` is not imported in `my_collection_screen.dart:1-45`.
     * Writing `kFallbackUsMintSkus[canonSku]?.issuePrice` in `my_collection_screen.dart` will fail `flutter analyze` with a compile error.
     * **Required Fix at Execution:** Add `'issue_price': 95.0` to `'26EA'` in `kFallbackUsMintSkus` (`add_coins_hub.dart:118-124`) or expose `CanonicalMintAssetService.fallbackIssuePrice(String sku)`, and read `_parseNumber(kFallbackUsMintSkus[canonSku]?['issue_price'])`.
  2. **Must-Fix B2 (Year-from-Title Inference & Upload-Guard Check for `2026 American Eagle One...` at `canonical_mint_asset_service.dart:107, 172`):**
     * In `my_collection_screen.dart:3002-3005`, the card title `2026 American Eagle One...` comes from `theme = _rowField(m, 'theme_subject', _F.themeSubject)` (`Theme/Subject`) or `denom` (`Denomination`). Because `Theme/Subject` is already included in `combined` (`canonical_mint_asset_service.dart:109, 117`), why did `extractSku` fail to match `26EA` at `line 118`?
       * Either (a) `data['Year']` / `data['year']` on that document is empty/missing while `'2026'` is embedded at the start of `Theme/Subject` (`"2026 American Eagle One Ounce Silver Proof Coin"`), causing `year == '2026'` at `line 118` to be `false`; OR (b) `data['Title']` / `data['Name']` / `data['Original Description from source']` holds the title; OR (c) `hasUserUploadedPhotos(data)` (`lines 27-50`) returned `true` because `image_url_obverse` / `image_url_reverse` on that invoice-imported item contains a broken or non-microscope URL matching `numista-uploads-studio-`.
     * **Required Fix at Execution:** In `extractSku` (`line 107`) and `resolveFromMap` (`line 172`), in addition to adding `'Title'`, `'Name'`, and `'Original Description from source'`, fall back to extracting a leading/embedded 4-digit year `(2023|2026)` from `combined` / `primaryTitle` when `data['Year']` is empty (`final rawYr = _normYear(data['year'] ?? data['Year']); final year = rawYr.isNotEmpty ? rawYr : (RegExp(r'\b(2023|2026)\b').firstMatch(combined)?.group(1) ?? '');`). Also note that the test path in `NET-780b:196` is `numista_mobile/test/services/canonical_mint_asset_service_test.dart`.

---

### 1.3 Track C: `FAILFIX_PLAN_NET-780c_IMAGES_v1.md` — Score: `96 / 100 (PASS)`

* **Verbatim Repo Citations Checked in This Turn:**
  * **`numista_mobile\lib\screens\my_collection_screen.dart:6377-6383`**:
    ```dart
    6377:     final obv = _cleanUrl(data[_F.imageObverse]);
    6378:     final rev = _cleanUrl(data[_F.imageReverse]);
    6379:     final directUrl = rev.isNotEmpty ? rev : obv;  // Prefer reverse (distinct design)
    6380: 
    6381:     if (directUrl.isNotEmpty) {
    6382:       return _buildCoinImage(directUrl);
    6383:     }
    ```
  * **`numista_mobile\lib\services\canonical_mint_asset_service.dart:154-158`**:
    ```dart
    154:     // MF-B Guard: Non-destructive preservation of user-uploaded / microscope photos.
    155:     // If doc contains user uploads (e.g. Row 10 Eric's microscope photos), return null.
    156:     if (hasUserUploadedPhotos(data)) {
    157:       return null;
    158:     }
    ```
  * **`numista_mobile\firebase.json:275-276`** (`283-284` on `dev`):
    ```json
    275:             "key": "Content-Security-Policy",
    276:             "value": "default-src 'self' https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseapp.com https://*.firebase.com https://storage.googleapis.com https://*.run.app; script-src 'self' 'unsafe-inline' 'unsafe-eval' blob: https://apis.google.com https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.run.app; worker-src blob: 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://*.gstatic.com; font-src 'self' https://fonts.gstatic.com https://*.gstatic.com data:; img-src 'self' data: blob: https://storage.googleapis.com https://*.googleusercontent.com https://*.gstatic.com https://*.run.app; connect-src 'self' blob: https://*.googleapis.com https://*.gstatic.com https://www.gstatic.com https://*.firebaseio.com wss://*.firebaseio.com https://firestore.googleapis.com https://identitytoolkit.googleapis.com https://accounts.google.com https://*.run.app https://numista-backend-568985927038.us-central1.run.app https://localhost:5000; frame-src 'self' https://apis.google.com https://accounts.google.com https://*.google.com https://*.firebaseapp.com https://*.run.app"
    ```
* **Assessment & Advisory for `NET-780c`:**
  * Strictly enforces Founder Eric's 4-tier Image Source Order (`28` own scrubbed images [93.3%], `2` mirrored to GCS [6.7%], `0` unmapped, `0` PII receipts/personal photos, `$0.00049/mo` storage cost).
  * **Advisory:** Add explicit `https://storage.googleapis.com` to `connect-src` in `numista_mobile/firebase.json:276` (matching `img-src`), and wire `fallbackReverseUrl` / `fallbackObverseUrl` into `_CollectionCardImage._buildCoinImage` (`my_collection_screen.dart:6373, 6443`) so if a primary canonical image URL ever fails, `errorBuilder` automatically falls back to `canon.fallbackReverseUrl ?? canon.obverseUrl` before showing `Icons.image_not_supported_outlined`.

---

### 1.4 Track D: `FAILFIX_PLAN_NET-780d_SPLASH_v1.md` — Score: `97 / 100 (PASS)`

* **Verbatim Repo Citations Checked in This Turn:**
  * **`numista_mobile\lib\widgets\auth_gate.dart:128-138, 179-184`**:
    ```dart
    128:           _shouldShowWelcome ??= () async {
    129:             await UiVariantService.refresh();
    130:             return WelcomeScreen.shouldShow();
    131:           }();
    132: 
    133:           return FutureBuilder<bool>(
    134:             future: _shouldShowWelcome,
    135:             builder: (ctx, snap) {
    136:               if (snap.connectionState == ConnectionState.waiting) {
    137:                 return _buildSplash();
    138:               }
    ```
    ```dart
    179:           children: [
    180:             Image.asset('assets/logo_owl.png', height: 80,
    181:                 errorBuilder: (context, error, stackTrace) =>
    182:                     const Icon(Icons.account_balance_rounded,
    183:                         color: Color(0xFFD4A843), size: 64)),
    ```
  * **`numista_mobile\lib\services\ui_variant_service.dart:12-17`**:
    ```dart
    12:   static Future<void> refresh() async {
    13:     try {
    14:       final response = await HttpAuthClient.get(
    15:         Uri.parse('$kApiBaseUrl/api/user/ui_variant'),
    16:       );
    ```
  * **`numista_mobile\lib\services\http_auth_client.dart:66-71`**:
    ```dart
    66:   static Future<http.Response> get(
    67:     Uri url, {
    68:     http.Client? client,
    69:     Map<String, String>? headers,
    70:     Duration timeout = const Duration(seconds: 30),
    71:   }) async {
    ```
  * **`numista_mobile\lib\main.dart:195-197`**:
    ```dart
    195:     await Firebase.initializeApp(
    196:       options: DefaultFirebaseOptions.currentPlatform,
    197:     ).timeout(const Duration(seconds: 12));
    ```
* **Assessment & Advisory for `NET-780d`:**
  * Root cause analysis is 100% verified against the live code (`12s` Firebase init timeout + `30s` `HttpAuthClient.get` default timeout inside `_shouldShowWelcome` = `42s` worst-case splash screen hang, plus `3.08 MB` `logo_owl.png` raster decode).
  * **Advisory for Step 1 (`auth_gate.dart:128-131`):** Guard `unawaited(UiVariantService.refresh());` inside `if (_shouldShowWelcome == null)` so it fires **once per sign-in** rather than on every `AuthGate.build()` rebuild:
    ```dart
    if (_shouldShowWelcome == null) {
      unawaited(UiVariantService.refresh());
      _shouldShowWelcome = WelcomeScreen.shouldShow();
    }
    ```

---

## 2. Standing Locks & Rule 8 Verification Summary

1. **Strict `PLAN ONLY` Confirmed:** Zero source files modified, zero deployments run, `origin/main` locked at `9f04550a`, Stripe locked OFF.
2. **Step 1b & Seeding Hold Confirmed:** Live Firestore rules deploy and live SKU dictionary seeding remain on strict HOLD pending Eric's separate typed YES.
3. **Rule 8 Machine-Checkable Commands Verified:** Each split plan specifies machine-checkable exit criteria (`flutter analyze`, `flutter test`, `curl -s .../version.json`, DevTools CSP count = `0`, splash dismissal `< 1500ms`).
