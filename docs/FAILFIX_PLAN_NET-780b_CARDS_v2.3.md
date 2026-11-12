# FAILFIX PLAN v2.3: Broken Cards & Pending Pricing (NET-780b)
**To:** Grok Bot CoS, Stand Alone Grok (SAG, grok-4.7), Antigravity Desk, Founder Eric  
**From:** AG CoS (v2.3; closes SAG 86 FAIL must-fixes MF-1..MF-4 + polish from `REVISE_NET-817_CARDS_v2.2_to_v2.3_VERIFIED_20261108-1155.md`). v2.1–v2.2: GB CoS fresh writer; v2.0 and earlier: Antigravity Chief of Staff v5 (`cfe23a7a-d721-44f9-b9d5-d2b74602b687`).  
**Date:** 12 November 2026, ~18:25 ET  
**Pin:** `4d17ca5ef1f73c0e5f5c9dca3a96f00ab9a15235` (all quotes re-read with `git show 4d17ca5e:<path>`).  
**Reference Batons & Scores:**  
- `BATON_NET-780_FAILFIX_PLAN_NET-748-v5-FT_v1_2026-11-04-1658.md`  
- `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (**Cards 95/100 PASS**, Images 78/100 FAIL, Combined 86/100 FAIL)  
- `RADIO_NET-838_GROKCOS-to-AGCOS_REVISE-817-v2.0_20261107.md`  
- `BATON_NET-817_REVISE_CARDS-IMAGES_v2.0_TO-AGCOS-V5_cfe23a7a_ATTEMPT2_PER-COS-86_20261107.md`  
**Directives & Audit Authority:**  
- `GB CoS SCORE v1.9` & `RADIO_NET-838`: Preserves the **95/100 PASS** Cards v1.9 plan verbatim in the v2.0 package, plus adds the optional standalone `MeltValueService.parseFaceValue` unit test in §6.1 covering `Half Dime`, `Three Cent Nickel`, and `Five Cents` for the shared `home_dashboard` call site.  
- `PROTOCOL UPDATE: ARGON DROPPED ENTIRELY`: Founder Eric typed YES. Review sequence is strictly: AG CoS v5 Plan $\rightarrow$ Grok Bot CoS ($\ge 95$) $\rightarrow$ Stand Alone Grok ($\ge 95$) $\rightarrow$ Founder Eric typed YES.  
**Status:** **PLAN ONLY** (Zero code changes, zero test execution, zero builds, zero deployments, zero Firestore writes/seeding).  
**Explicit Standing Locks & Clearances:**  
1. `origin/main` strictly locked at `9f04550a`.  
2. Stripe strictly locked OFF across all code and configurations.  
3. Execution strictly scoped to branch `p7-v8.9` against verified code baseline commit `4d17ca5e` (`c294fd3c`, the last code commit touching `numista_mobile/` on `p7-v8.9`; branch `dev` @ `b0b05808` lacks `canonical_mint_asset_service.dart`).  
4. Founder Eric's typed YES to this plan is strictly for code execution on `p7-v8.9` and preview channel deployment — it is NOT an approval for Firestore database writes, seeding, or security rules changes. Separate scoped Eric typed YES is required for any database writes.  
5. Zero deployments to live production `numista-vault.web.app` or `numista.ai` without prior Firebase Preview Channel sign-off and Eric's separate, explicit typed approval. Target is **p7-gate preview** (`preview-catalog`) only.  
6. **Alerts only, NEVER budget caps:** all spending caps (including $25 limit and hard $0.00 spend cap) are permanently eliminated per Eric's standing rule; billing alerts set at $20/mo.  
7. Zero AJ PII across all plans, logs, mocks, and code.  

---

## 0b. v2.3 Close-Out of SAG 86 FAIL Must-Fixes (`REVISE_NET-817_CARDS_v2.2_to_v2.3_VERIFIED_20261108-1155.md`)

| # | SAG 86 finding | v2.3 change | Evidence (`git show 4d17ca5e:…` / Runtime) |
|---|---|---|---|
| **MF-1 (FALSE → Hardened)** | Lookbehind `(?<![\d.])` claimed "not runtime-proven" | Dart `RegExp` uses ECMAScript semantics (Dart VM and JS web both support `(?<!…)` lookbehind, verified under Node ECMAScript engine by GB CoS). Kept pattern unchanged and added explicit `RegExp` constructor/eval test in §6.2 so any `FormatException` fails loudly. | GB CoS verified: `1c/1¢/penny/cent/one cent/Lincoln cent` → cent; `5 cent/5c/nickel/Five Cents` → nickel; `15¢/25c/25 cent/15c/2.5c` → neither; three-cent-first handles `Three Cent Nickel`. |
| **MF-2 (REAL)** | Rollback script used `CARDS=<Cards-commit-hash>` (shell redirection) | Replaced with `CARDS_SHA="${CARDS_SHA:?set CARDS_SHA}"` and optional `IMAGES_SHA="${IMAGES_SHA:-}"` — no angle-bracket placeholders. **git revert only, no `reset --hard`.** | §4.D |
| **MF-3 (REAL)** | USD face fallback not US-scoped | Gated `resolveFaceValue` on `isUsOrigin(data)` reusing the exact US origin discriminator from `my_collection_screen.dart` (`_F.country` at `:48`, `_coinOriginFilter` at `:155–156`, `usAllowList` / `usDenoms` / `isForeign`). Added negative widget test for a non-US row whose denom contains `"cent"` (e.g. Canada `1 Cent`). | `my_collection_screen.dart:48`, `:155–156`, `usAllowList`/`isForeign` |
| **MF-4 (REAL)** | False citation `_currencyFmt` at `:108` | Corrected `:108` (`String? _selectedCoinId;`) to `:248` (`static final _currencyFmt =`) and uses `:3337, :3343`. | `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` (`:108`, `:248`, `:3337`, `:3343`) |
| **Polish** | Line span, preflight clean index, Case 7 string, negative regex tokens | §4.C regex lines corrected `431–435` → `431–434` (apply by exact old text since `canonicalYear` shifts lines); §4.A asserts `HEAD == p7-v8.9` and clean index; Case 7 asserts `'$about twelve'` explicitly; §6.2 adds tokens (`'15¢'`, `'15 cent'`, `'35 cent'`, `'100 cent'`) that reach the new regex (noting `'25c'`/`'50c'` are caught by earlier branches). | §4.A, §4.C, §6.1, §6.2 |

## 0a. v2.2 Close-Out of CoS-94 Must-Fix MF-SAG-C3 (round 3, 08:12 ET; ONLY this item changed)

| # | CoS-94 finding | v2.2 change | Evidence (sRGB WCAG 2.x luminance, computed on the box) |
|---|---|---|---|
| **C3-1** | `#D4AF37` on `#1E2937` = 6.9956:1, fails the >=7.0 assertion | Threshold kept at AAA 7.0 (not loosened). Dark text color changed to **`#E0BC4A`** (a lighter tone of the same gold): 8.03:1 on `#1E2937`, 10.01:1 on `#0D1520`. Component, test and prose updated together. | `#E0BC4A`/`#1E2937` 8.0289; `#E0BC4A`/`#0D1520` 10.0081. |
| **C3-2a** | Dark chip fill was translucent (`withAlpha(25)`); composited fill would fail 7.0 | Dark chip fill made **opaque `#0D1520`** (the cited virtual-child surface, `my_collection_screen.dart:3031`), so text-on-chip is 10.01:1 and no alpha composition is needed. Border stays translucent gold (non-text). | Old fill composited over `#1E2937` = `#303637`; `#D4AF37` on it = 5.85:1 (would fail). |
| **C3-2b** | Test compared against local constants, not the rendered background | Case 6 now mounts the row inside a keyed `Container(key: Key('udv_card_surface'), color: surface)` for each cited surface (`:211` `_surface`, `:3031` virtual-child) in each theme, reads the **pumped** surface `BoxDecoration`/`color` and the **pumped** chip `BoxDecoration.color`, alpha-composites the chip fill over the pumped surface (`_over`), and asserts text contrast against both. | Test-internal; not executed. |
| **C3-3** | Light chip ratio stated as 5.05 | Corrected to **4.96:1** (`#856404` on `#FFF3CD` = 4.9592), still >= 4.5 AA. | 4.9592191191; white 5.4946; `#F5F5F0` 5.0241. |

## 0. v2.1 Close-Out of SAG Must-Fixes (ONLY these items changed)

| # | SAG must-fix | v2.1 change | Evidence (`git show 4d17ca5e:…`) |
| :--- | :--- | :--- | :--- |
| **MF-SAG-C1** | §2.D/§3.C quotes not verbatim; hunk would not apply | §2.D and §3.C now quote the real `:430–435`. Hunk replaces ONLY `:431–434` (`isCent`/`isNickel`); `:435 if (isCent && !isQuarter && !isHalf) {` untouched; no `isDime` added. The 2026 guard is `:341 if (cleanYear == '2026') {`; dime is the earlier `.contains('dime')` branch at `:342–345`. Apply step aborts (no partial commit) if the old text does not match exactly. | `canonical_mint_asset_service.dart` `:430` `// MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.` … `:435` as above; `:341–345` as above. |
| **MF-SAG-C2** | Rollback had no branch guard; Cards-only revert would break Images callers | §4.D: assert HEAD is `p7-v8.9` (never `main`), clean tree, preflight SHAs; if the Images commit exists, revert Images first, then Cards; push `p7-v8.9` only after every local revert succeeds. | Plan-internal. |
| **MF-SAG-C3** | Contrast test used hardcoded/uncited surfaces, ambiguous ancestor, deprecated channel getters | `0xFF1E2937` is now **cited**: `my_collection_screen.dart:211` `Color get _surface => … ? const Color(0xFF1E2937) : Colors.white;`; virtual-child surfaces `0xFF0D1520` / `0xFFF5F5F0` at `:3031`. Chip background read from the chip `Container` found by `Key('valuation_pending_chip')` (key added to the widget), not `ancestor(...).first`. Channels use `(c.r * 255).round()` etc. (Color `.r/.g/.b` doubles; pin `pubspec.yaml` `sdk: ^3.11.3`). | `:211`, `:3031`, pubspec `sdk: ^3.11.3`. |
| **MF-SAG-C4** | Range formatting claimed tested but no case | Case 7 added: `'12.00 - 15.00'` and `'$12.00 - $15.00'` both render `$12.00 - $15.00`; a non-numeric AI string (`'about twelve'`) must not render `$0.00`. | Table regex `:3347` `^(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)$` (no `$`); widget regex adds optional `\$?`. |
| **MF-SAG-C5** | §1 called §2.A an exact deletion diff | Relabeled: §2.A is a **verified span list, not a diff**. Default NET-817 scope deletes nothing there; deletion only if a later gate explicitly assigns it (then a real hunk + "no remaining references" grep is required). | — |

## 1. Executive Summary & Itemized Must-Fix Closeout Table (Preserved 95/100 PASS + Optional `parseFaceValue` Test)

Plan v2.0 preserves every item marked **Closed** in `COS_SCORE_NET-817_CARDS_IMAGES_v1.9_20261107.md` (`MF-B1'`, `MF-B2'`, `MF-B3'`, `MF-C1`, `MF-C2'`, `MF-C3'`, `MF-C4`, `MF-C5'`, `MF-C6'`, `MF-C7`) and adds the optional standalone `MeltValueService.parseFaceValue` unit test in §6.1:

| Must-Fix # | Must-Fix Description | Plan v2.0 Resolution & Verbatim Grounding at `4d17ca5e` | Plan Section |
| :--- | :--- | :--- | :--- |
| **MF-B1'** | **Resolve Orphaned Kaggle/Google Inspector Deletions & Correct Verbatim Quotes (CLOSED — Preserved):** Do not point at parked NET-816 v1.11 as active owner. Fix stale quotes for `:3531–3548`, `:4387–4406`, and `:4408–4426`. | **Explicit Re-Homing / Self-Contained Gate:** Records that NET-816 v1.11 is **PARKED** and Catalog Chunk 1 (`9bbe20e4`) is scoped strictly to 2 catalog items (`catalog_service.dart` / `catalog_browse_screen.dart`), NOT `my_collection_screen.dart`. Therefore: (a) NET-817's card/image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) are **100% independent** of the inspector/Google-button lines and do not touch them by default; AND (b) if CoS explicitly assigns the orphaned inspector/Google-button removal to NET-817 at execution gate, §2.A provides a verified span list (v2.1: NOT a diff; see §0 MF-SAG-C5) (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`). All quotes are corrected verbatim from `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` (`OutlinedButton.icon` + `void _onSearchGoogle(Map<String, dynamic> data) async` + `void _onSearchEbay(Map<String, dynamic> data) async` calling `EpnService.generateSearchUrl(coin, soldOnly: true)`). | §2.A, §4.B |
| **MF-B2'** | **Pin Code Commit (`4d17ca5e`), Not Docs HEAD (`ebf1eed8`), & Honest DTG (CLOSED — Preserved):** Pre-flight must check `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` and stamp real wall-clock filing time. | Pre-flight gate (§4.A) pins `4d17ca5e` via `git diff --quiet 4d17ca5e HEAD -- numista_mobile/` so docs-only commits on `p7-v8.9` never invalidate the code baseline while any unexpected code drift aborts immediately. DTG stamped from observed wall-clock (`2026-11-07 16:33 ET`). | Header, §4.A |
| **MF-B3'** | **Include Required Imports in `my_collection_screen.dart` Diff (CLOSED — Preserved):** Add `collection_card_valuation_row.dart` and `collection_card_image.dart` imports and confirm `intl` / `melt_value_service.dart` remain used. | §3.B includes the exact verbatim import block from `my_collection_screen.dart:1–45` at `4d17ca5e` and adds `import '../widgets/collection_card_valuation_row.dart';` (Cards) and `import '../widgets/collection_card_image.dart';` (Images) at line 45. Confirms `import 'package:intl/intl.dart' as intl;` (line 2) and `import '../services/melt_value_service.dart';` (line 31) remain actively used elsewhere in `my_collection_screen.dart` (e.g., `_currencyFmt` at `:3337, :3343` and melt calculations). | §3.B |
| **MF-C2'** | **Read the Real AI Value Key (`'AI Estimated Value'`) & Pending-Chip Semantics (CLOSED — Preserved):** `my_collection_screen.dart:72` defines `static const aiValue = 'AI Estimated Value';`. Match `:3345–3355` filtering and range formatting. Document pending-chip behavior vs `:3170`. | `CollectionCardValuationRow` reads `data['AI Estimated Value'] ?? data['ai_estimated_value'] ?? data['ai_value'] ?? data['aiValue']`. Consistent with table column `:3345–3355`, it treats `'Pending'`, `'null'`, `'—'`, `'none'`, `'nan'`, and `''` (case-insensitive) as absent, and supports range strings (`'12.00 - 15.00'` $\rightarrow$ `'\$12.00 - \$15.00'`). Explicitly documents and tests the intentional B05N-8 behavior change relative to shipped `:3170`. | §2.B, §3.B, §6.1 |
| **MF-C3'** | **Fix Face Value for Canonical Denominations (`'Five Cents'`, `'Half Dime'`, `'Three Cent Nickel'`) + Standalone `parseFaceValue` Unit Test (CLOSED — Preserved + Polished):** Patch `MeltValueService.parseFaceValue` (`:76–88`) and `CollectionCardValuationRow.resolveFaceValue`, plus add direct unit test for `MeltValueService.parseFaceValue`. | Implements two-layer defense: (1) Surgical patch to `MeltValueService.parseFaceValue` (`lib/services/melt_value_service.dart:76–88`) ordering `'half dime'` before `'dime'`, `'three cent'` before `'nickel'`, and adding word-form `'fifty cent'`, `'twenty-five cent'`/`'twenty five cent'`, `'ten cent'`, `'five cent'`, and `'one cent'`; AND (2) `CollectionCardValuationRow.resolveFaceValue(rawDenom)` pre-maps `DenominationCanon` constants before delegating to `MeltValueService.parseFaceValue`. Includes both widget table test AND standalone `MeltValueService.parseFaceValue` unit test in §6.1 covering `Half Dime`, `Three Cent Nickel`, `Five Cents`, `Cent`, `Dime`, `Quarter Dollar`, `Half Dollar`, and `Dollar` for the shared `home_dashboard` call site. | §2.C, §3.B, §3.D, §6.1 |
| **MF-C5'** | **Don't Break `'1 cent'` in `CanonicalMintAssetService` & Use Discriminating Test Fixtures (CLOSED — Preserved):** | Updates `canonical_mint_asset_service.dart:431–435` with `1 cents?` and `5 cents?` in the leading group and tests with neutral `'title': '2026 Coin'`. | §2.D, §3.C, §6.2 |
| **MF-C6'** | **Assert Rendered Widget Colors (CLOSED — Preserved):** | Pumps `CollectionCardValuationRow` in dark and light `ThemeData`, extracts rendered `Text.style.color` and `BoxDecoration.color`, and asserts contrast $\ge 7.0$ (dark) and $\ge 4.5$ (light, including against `0xFFFFF3CD`). | §3.B, §6.1 |

---

## 2. Root Cause Analysis & Verbatim Code Citations (`git show 4d17ca5e:...`)

### A. Kaggle & Google Images Inspector Elements & Correct Verbatim Quotes (MF-B1')
Verifying `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart` line-by-line:

1. **State variables at lines 150–151:**
   ```dart
   149:   // --- Similar Coins state (inspector) ------------------------------------
   150:   List<ReferenceImage> _inspectorSimilar = [];
   151:   bool _loadingInspectorSimilar = false;
   152:   // _inspectorSimilarCoinId removed — tracking via _selectedCoinId is sufficient
   ```
2. **Call site in `_openCoinInspector` at line 3454:**
   ```dart
   3451:       _selectedCoinId   = coinId;
   3452:       _vaultShowObverse = true;
   3453:     });
   3454:     _fetchInspectorSimilar(data);
   ```
3. **Google Images button in inspector at lines 3531–3548 (Note: `OutlinedButton.icon` calling `_onSearchGoogle(data)`):**
   ```dart
   3531:                     // Google Images search — only shown when no photo is active
   3532:                     if (!hasActive && refFuture != null) ...[
   3533:                       Tooltip(
   3534:                         message: 'Opens Google Images: searches for this coin',
   3535:                         child: OutlinedButton.icon(
   3536:                           onPressed: () => _onSearchGoogle(data),
   3537:                           icon: Icon(Icons.image_search, size: 15),
   3538:                           label: Text('Google Images'),
   3539:                           style: OutlinedButton.styleFrom(
   3540:                             foregroundColor: _text, side: BorderSide(color: _border),
   3541:                             shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(4)),
   3542:                             padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
   3543:                             textStyle: TextStyle(fontSize: 12),
   3544:                           ),
   3545:                         ),
   3546:                       ),
   3547:                       SizedBox(width: 8),
   3548:                     ],
   ```
4. **UI call in inspector at line 3820:**
   ```dart
   3818:                           _buildCoinSetSection(data, onPhotoUploaded: () => setDlg(() {})),
   3819:                           _buildRollBanner(data),
   3820:                           _buildSimilarCoinsInspector(),
   3821:                         ]),
   ```
5. **Google Images handler at lines 4387–4406 (`void _onSearchGoogle(Map<String, dynamic> data) async`):**
   ```dart
   4387:   void _onSearchGoogle(Map<String, dynamic> data) async {
   4388:     final year  = data[_F.year]?.toString().replaceAll(RegExp(r'\.0$'), '') ?? '';
   4389:     final mint  = data[_F.mintMark]?.toString() ?? '';
   4390:     final denom = data[_F.denomination]?.toString() ?? '';
   4391:     final query = Uri.encodeComponent('$year${mint.isNotEmpty ? '-$mint' : ''} $denom coin value'.trim());
   4392:     final uri = Uri.parse('https://www.google.com/search?tbm=isch&q=$query');
   4393:     try {
   4394:       if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
   4395:         if (mounted) {
   4396:           ScaffoldMessenger.of(context).showSnackBar(SnackBar(
   4397:             content: Text('Could not open browser.'), backgroundColor: _red));
   4398:         }
   4399:       }
   4400:     } catch (e) {
   4401:       if (mounted) {
   4402:         ScaffoldMessenger.of(context).showSnackBar(SnackBar(
   4403:           content: Text('Couldn\'t open the browser. Please try again.'), backgroundColor: _red));
   4404:       }
   4405:     }
   4406:   }
   ```
6. **Outbound eBay SOLD search at lines 4408–4426 (MUST BE PRESERVED):**
   ```dart
   4408:   /// Opens eBay SOLD listings in the browser using an EPN affiliate link
   4409:   /// so Numista.AI earns commission on any resulting purchase.
   4410:   void _onSearchEbay(Map<String, dynamic> data) async {
   4411:     try {
   4412:       final coin = CoinModel.fromMap(data, _selectedCoinId ?? '');
   4413:       final url  = await EpnService.generateSearchUrl(coin, soldOnly: true);
   4414:       final uri  = Uri.parse(url);
   ```
7. **Inspector loader at lines 5252–5278 and UI/dialog at lines 5549–5684:**
   ```dart
   5252:   Future<void> _fetchInspectorSimilar(Map<String, dynamic> data) async {
   ...
   5278:   }
   ...
   5549:   Widget _buildSimilarCoinsInspector() {
   ...
   5647:   void _showRefImageDialog(BuildContext ctx, ReferenceImage img) {
   ...
   5684:   }
   ```

**Resolution of Ownership (`MF-B1'`):**
- NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) is scoped strictly to 2 catalog items (`catalog_service.dart` and `catalog_browse_screen.dart`), NOT `my_collection_screen.dart`.
- **Default Execution Scope for NET-817:** Neither `FAILFIX_PLAN_NET-780b_CARDS_v2.0.md` nor `FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md` depends on deleting lines `150–151`, `3454`, `3531–3548`, `3820`, `4387–4406`, `5252–5278`, or `5549–5684`. Those inspector/Google-button deletions are **recorded as out-of-scope for NET-817 and awaiting CoS re-homing to a dedicated inspector/cleanup chunk**.
- **Optional Self-Contained Deletion Gate:** If CoS/Eric explicitly directs NET-817 to execute the inspector/Google-button removal as part of the Cards commit (Step 1), all 7 spans (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`) are deleted atomically in a single commit in NET-780b while strictly preserving `_onSearchEbay` at `:4408–4426`.

---

### B. Cards Valuation Anchors, Real AI Key (`_F.aiValue`), & Pending Chip Semantics (MF-C1, MF-C2')
In `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`:
- **Field constant at line 72:**
  ```dart
  71:   // Internal/Legacy
  72:   static const aiValue          = 'AI Estimated Value';
  ```
- **Card valuation variables at lines 3017–3023 (leaving line 3015 `displayTitle` untouched):**
  ```dart
  3015:             : (themeStartsYear ? label : '$yearMint $label').trim();
  3016: 
  3017:         final valCpg = _parseNumber(m['cpgRetail']);
  3018:         final finalVal = valCpg;
  3019:         
  3020:         final fmt = intl.NumberFormat.currency(symbol: '\$');
  3021:         final valueText = finalVal > 0 
  3022:             ? fmt.format(finalVal) 
  3023:             : (m[_F.aiValue]?.toString() ?? '—');
  ```
- **Card valuation row at lines 3167–3192:**
  ```dart
  3167:                   Row(
  3168:                     mainAxisAlignment: MainAxisAlignment.spaceBetween,
  3169:                     children: [
  3170:                       if (valueText == '—' || m['enrichment_status'] == 'pending')
  3171:                         Container(
  3172:                           padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
  3173:                           decoration: BoxDecoration(
  3174:                             color: const Color(0xFFC9A227).withAlpha(25),
  3175:                             borderRadius: BorderRadius.circular(4),
  3176:                             border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
  3177:                           ),
  3178:                           child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
  3179:                         )
  3180:                       else
  3181:                         Text(
  3182:                           valueText,
  3183:                           style: const TextStyle(
  3184:                             fontSize: 13,
  3185:                             fontWeight: FontWeight.bold,
  3186:                             color: Color(0xFFC9A227),
  3187:                           ),
  3188:                         ),
  3189:                       if (condition.isNotEmpty)
  3190:                         GradeBadgeWidget(gradeCode: condition),
  3191:                     ],
  3192:                   ),
  ```
- **Table view AI Value column at lines 3338–3355:**
  ```dart
  3338:       case _F.aiValue:
  3339:         final coinCpg = _parseNumber(m['cpgRetail']);
  3340:         // NET-372: CPG Retail only, bid removed from display
  3341:         final gVal = coinCpg;
  3342:         if (gVal > 0) {
  3343:           return _currencyFmt.format(gVal);
  3344:         }
  3345:         final av = m[_F.aiValue]?.toString().trim() ?? '';
  3346:         if (av == 'Pending' || av == 'null' || av.isEmpty) return '';
  3347:         final rangeMatch = RegExp(r'^(\d+(?:\.\d+)?)\s*[-–]\s*(\d+(?:\.\d+)?)$').firstMatch(av);
  3348:         if (rangeMatch != null) {
  3349:           final v1 = double.tryParse(rangeMatch.group(1)!);
  3350:           final v2 = double.tryParse(rangeMatch.group(2)!);
  3351:           if (v1 != null && v2 != null) {
  3352:             return '\$${v1.toStringAsFixed(2)} - \$${v2.toStringAsFixed(2)}';
  3353:           }
  3354:         }
  3355:         return av.startsWith('\$') ? av : '\$$av';
  ```

---

### C. Canonical Denomination Face Value Bug in `MeltValueService.parseFaceValue` (MF-C3')
Verifying `git show 4d17ca5e:numista_mobile/lib/constants/denomination_canon.dart` lines 3–9:
```dart
3: class DenominationCanon {
4:   static const String cent          = 'Cent';
5:   static const String fiveCents     = 'Five Cents';
6:   static const String dime          = 'Dime';
7:   static const String quarterDollar = 'Quarter Dollar';
8:   static const String halfDollar    = 'Half Dollar';
9:   static const String dollar        = 'Dollar';
```
And `git show 4d17ca5e:numista_mobile/lib/services/melt_value_service.dart` lines 76–88:
```dart
76:     // 2. Sub-Dollar & Standard Silver/Base Denominations
77:     else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
78:     else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
79:     else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
80:     else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
81:     else if (s.contains('half dime')) { value = 0.05; }
82:     else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
83:     else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
84:     else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
85:     else if (s.contains('half cent')) { value = 0.005; }
86:     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
87:     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
```

---

### D. Denomination Regex Boundary in `CanonicalMintAssetService` (MF-C5')
In `git show 4d17ca5e:numista_mobile/lib/services/canonical_mint_asset_service.dart` lines 430–435 (v2.1, verbatim):
```dart
430:       // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
435:       if (isCent && !isQuarter && !isHalf) {
```
(The 2026 guard is `:341 if (cleanYear == '2026') {`; dime handling is the earlier `.contains('dime')` return at `:342–345`. There is no `isDime` and no `y` in this method.)

---

## 3. Targeted Production Code Implementation

### A. Additive `canonicalYear` Helper in `canonical_mint_asset_service.dart` (MF-C7 — Closed, Preserved)
In `numista_mobile/lib/services/canonical_mint_asset_service.dart` at `4d17ca5e`, lines 72–79 read verbatim:
```dart
72:   static String _normYear(Object? y) {
73:     final s = (y ?? '').toString().trim();
74:     final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
75:     return m != null ? m.group(1)! : s;
76:   }
77: 
78:   static String extractSku(Map<String, dynamic> data) {
```
Inserted additively at line 77 (between `_normYear` and `extractSku`), leaving `resolveFromMap` (`:153`) untouched:
```dart
<<<<
  static String _normYear(Object? y) {
    final s = (y ?? '').toString().trim();
    final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
    return m != null ? m.group(1)! : s;
  }

  static String extractSku(Map<String, dynamic> data) {
====
  static String _normYear(Object? y) {
    final s = (y ?? '').toString().trim();
    final m = RegExp(r'^(\d{4})(?:\.0+)?$').firstMatch(s);
    return m != null ? m.group(1)! : s;
  }

  /// MF-C7: Extracts normalized 4-digit canonical year from coin metadata.
  /// Strictly additive at line 77. Leaves resolveFromMap completely unchanged.
  /// Intentionally excludes Personal Notes to prevent neighbor note bleed.
  static String canonicalYear(Map<String, dynamic> data) {
    for (final k in const <String>[
      'year',
      'Year',
      'coin_year',
      'canonical_year',
      'issue_year',
      'mintDate',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString().trim();
        if (s.isNotEmpty) {
          final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
          if (dualMatch != null) return dualMatch.group(1)!;

          final norm = _normYear(s);
          if (RegExp(r'^\d{4}$').hasMatch(norm)) return norm;
        }
      }
    }

    for (final k in const <String>[
      'title',
      'name',
      'Theme/Subject',
      'theme_subject',
      'Program/Series',
      'program_series',
      'description',
    ]) {
      final v = data[k];
      if (v != null) {
        final s = v.toString();
        final dualMatch = RegExp(r'(?:1776|1976)[-–~](\d{4})').firstMatch(s);
        if (dualMatch != null) return dualMatch.group(1)!;

        final m = RegExp(r'\b(1[789]\d{2}|20\d{2})\b').firstMatch(s);
        if (m != null) return m.group(1)!;
      }
    }

    return '';
  }

  static String extractSku(Map<String, dynamic> data) {
>>>>
```

---

### B. Production Widget `CollectionCardValuationRow` & `my_collection_screen.dart` Wiring (MF-B3', MF-C1, MF-C2', MF-C3', MF-C4, MF-C6')

#### 1. New Production File: `numista_mobile/lib/widgets/collection_card_valuation_row.dart`
```dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart' as intl;
import 'package:numista_ai/constants/denomination_canon.dart';
import 'package:numista_ai/services/melt_value_service.dart';
import 'package:numista_ai/widgets/grade_badge_widget.dart';

/// Production valuation row extracted for testability and WCAG contrast compliance.
///
/// Implements B05N-8 valuation precedence and MF-C2'/MF-C3' requirements:
/// 1. CPG Retail override (`valCpg > 0`) -> Formatted currency (`$12.50`), no pending chip
///    (intentional B05N-8 change vs shipped `:3170`: verified CPG retail is authoritative
///    even when `enrichment_status == 'pending'`).
/// 2. AI Estimate (`data['AI Estimated Value'] ?? data['ai_estimated_value'] ?? data['ai_value'] ?? data['aiValue']`) ->
///    Filtered against sentinels (`Pending`, `null`, `—`, `none`, `nan`, empty).
///    Supports range strings (`12.00 - 15.00` -> `$12.00 - $15.00`) matching table column `:3345-3355`.
///    Shows `'Value pending AI estimate'` chip iff `enrichment_status == 'pending'`.
/// 3. Fallback -> Face value from denomination via `resolveFaceValue` + `MeltValueService.parseFaceValue`.
///    If `faceValue > 0` -> formatted face value with `'Value pending AI estimate'` chip.
///    If `faceValue <= 0` -> `'—'` with `'Value pending AI estimate'` chip (never `'$0.00'`).
///
/// WCAG Contrast across themes (MF-C6'):
/// - Dark Mode (v2.2): `#E0BC4A` against `#1E2937` (8.03:1) and `#0D1520` (10.01:1; also the opaque dark chip fill) -> PASSES AAA (>= 7.0:1).
/// - Light Mode: `#856404` against `#FFFFFF` (5.49:1), `#F5F5F0` (5.02:1), and light chip fill `#FFF3CD` (4.96:1) -> PASSES AA (>= 4.5:1).
class CollectionCardValuationRow extends StatelessWidget {
  final Map<String, dynamic> data;
  final String condition;

  const CollectionCardValuationRow({
    super.key,
    required this.data,
    this.condition = '',
  });

  static double _parseNumber(dynamic val) {
    if (val == null) return 0.0;
    if (val is num) return val.toDouble();
    final clean = val.toString().replaceAll(RegExp(r'[^\d.]'), '');
    return double.tryParse(clean) ?? 0.0;
  }

  /// Reads AI value across the canonical Firestore key `'AI Estimated Value'` (`_F.aiValue` at `:72`)
  /// and snake_case / camelCase aliases, filtering out sentinel strings per `:3346`.
  static String? extractValidAiValue(Map<String, dynamic> data) {
    final raw = data['AI Estimated Value'] ??
        data['ai_estimated_value'] ??
        data['ai_value'] ??
        data['aiValue'];
    if (raw == null) return null;
    final trimmed = raw.toString().trim();
    if (trimmed.isEmpty) return null;
    final lower = trimmed.toLowerCase();
    if (lower == 'pending' ||
        lower == 'valuation pending' ||
        lower == 'null' ||
        lower == 'none' ||
        lower == 'nan' ||
        trimmed == '—' ||
        trimmed == '-') {
      return null;
    }
    return trimmed;
  }

  /// Exact US origin allowlist matching `my_collection_screen.dart` (`usAllowList`).
  static const Set<String> _usAllowList = {
    'united states', 'usa', 'us', 'united states of america', 'u.s.', 'u.s.a.',
    'united states mint', 'puerto rico', 'guam', 'u.s. virgin islands', 'usvi',
    'american samoa', 'northern mariana islands', 'confederate states', 'csa', 'us philippines',
  };

  static const Set<String> _usDenoms = {
    'quarter dollar', 'quarter', 'dime', 'one cent', 'cent', 'penny',
    'lincoln cent', 'jefferson nickel', 'half dollar', 'dollar',
    'five dollars (half eagle)', 'half eagle', 'eagle', 'double eagle',
  };

  /// Reuses the exact US origin discriminator from `my_collection_screen.dart` (`_F.country`, `is_foreign`).
  /// Returns `false` when `is_foreign == true` or when a non-empty `Country`/`country` is not in `_usAllowList`.
  static bool isUsOrigin(Map<String, dynamic> data) {
    if (data['is_foreign'] == true) return false;
    if (data['is_foreign'] == false) return true;
    final countryClean = (data['Country'] ?? data['country'] ?? '').toString().toLowerCase().trim();
    if (_usAllowList.contains(countryClean)) return true;
    if (countryClean.isEmpty || countryClean == 'none') {
      final denomClean = (data['Denomination'] ?? data['denomination'] ?? '').toString().toLowerCase().trim();
      final isUSDenom = _usDenoms.contains(denomClean) ||
          denomClean.contains('quarter') ||
          denomClean.contains('dime') ||
          denomClean.contains('cent');
      return isUSDenom || denomClean.isEmpty;
    }
    return false;
  }

  /// Resolves face value in USD for canonical (`DenominationCanon`), colloquial,
  /// and historical US denominations (`Half Dime`, `Three Cent Nickel`).
  static double resolveFaceValue(String rawDenom) {
    final trimmed = rawDenom.trim();
    if (trimmed.isEmpty) return 0.0;

    // 1. Exact check against DenominationCanon constants
    switch (trimmed) {
      case DenominationCanon.cent:
        return 0.01;
      case DenominationCanon.fiveCents:
        return 0.05;
      case DenominationCanon.dime:
        return 0.10;
      case DenominationCanon.quarterDollar:
        return 0.25;
      case DenominationCanon.halfDollar:
        return 0.50;
      case DenominationCanon.dollar:
        return 1.00;
    }

    // 2. Delegate to MeltValueService.parseFaceValue (patched in MF-C3' for multi-word order)
    return MeltValueService.parseFaceValue(trimmed, qty: 1);
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    // v2.2 MF-SAG-C3: dark text #E0BC4A (#D4AF37 was 6.9956:1 on #1E2937); dark chip fill opaque #0D1520 (:3031)
    final chipTextColor = isDark ? const Color(0xFFE0BC4A) : const Color(0xFF856404);
    final chipBgColor = isDark ? const Color(0xFF0D1520) : const Color(0xFFFFF3CD);
    final chipBorderColor = isDark ? const Color(0xFFD4AF37).withAlpha(120) : const Color(0xFFFFEEBA);

    final valCpg = _parseNumber(data['cpgRetail']);
    final validAiStr = extractValidAiValue(data);
    final enrichmentStatus = data['enrichment_status']?.toString().toLowerCase().trim() ?? '';
    final rawDenom = (data['Denomination'] ?? data['denomination'] ?? '').toString();

    final fmt = intl.NumberFormat.currency(symbol: '\$');

    String displayValue;
    bool showPendingChip = false;

    if (valCpg > 0) {
      // 1. CPG Retail override takes top precedence and suppresses pending chip
      displayValue = fmt.format(valCpg);
      showPendingChip = false;
    } else if (validAiStr != null) {
      // 2. Valid AI Estimate present (supports range strings per :3347-3355)
      final rangeMatch = RegExp(r'^\$?(\d+(?:\.\d+)?)\s*[-–]\s*\$?(\d+(?:\.\d+)?)$').firstMatch(validAiStr);
      if (rangeMatch != null) {
        final v1 = double.tryParse(rangeMatch.group(1)!);
        final v2 = double.tryParse(rangeMatch.group(2)!);
        if (v1 != null && v2 != null) {
          displayValue = '\$${v1.toStringAsFixed(2)} - \$${v2.toStringAsFixed(2)}';
        } else {
          displayValue = validAiStr;
        }
      } else {
        final parsedAi = _parseNumber(validAiStr);
        displayValue = parsedAi > 0
            ? fmt.format(parsedAi)
            : (validAiStr.startsWith('\$') ? validAiStr : '\$$validAiStr');
      }
      showPendingChip = (enrichmentStatus == 'pending');
    } else {
      // 3. Fallback to face value (US-scoped per MF-3; closing B05N-8 & MF-C3')
      final faceValue = isUsOrigin(data) ? resolveFaceValue(rawDenom) : 0.0;
      displayValue = faceValue > 0 ? fmt.format(faceValue) : '—';
      showPendingChip = true;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        if (showPendingChip)
          Flexible(
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  displayValue,
                  style: TextStyle(
                    fontSize: 13,
                    fontWeight: FontWeight.bold,
                    color: chipTextColor,
                  ),
                ),
                const SizedBox(width: 6),
                Flexible(
                  child: Container(
                    key: const Key('valuation_pending_chip'), // v2.1 MF-SAG-C3
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: chipBgColor,
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: chipBorderColor),
                    ),
                    child: Text(
                      'Value pending AI estimate',
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontSize: 10,
                        color: chipTextColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ),
              ],
            ),
          )
        else
          Text(
            displayValue,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.bold,
              color: chipTextColor,
            ),
          ),
        if (condition.isNotEmpty)
          GradeBadgeWidget(gradeCode: condition),
      ],
    );
  }
}
```

#### 2. Required Imports & Call-Site Diff in `numista_mobile/lib/screens/my_collection_screen.dart` (MF-B3', MF-C1)
In `git show 4d17ca5e:numista_mobile/lib/screens/my_collection_screen.dart`, lines 1–3 and 40–45 read verbatim:
```dart
1: import 'dart:async';
2: import 'package:intl/intl.dart' as intl;
3: import '../utils/numista_error_helper.dart';
...
31: import '../services/melt_value_service.dart';
...
40: import '../services/set_expansion_helper.dart';
41: import '../services/set_grouping_service.dart';
42: import '../models/collection_row.dart';
43: import '../constants.dart';
44: import '../constants/denomination_canon.dart';
```
- **Import Usage Verification (`MF-B3'`):** `import 'package:intl/intl.dart' as intl;` (line 2) remains used by `_currencyFmt` (declared at `:248` as `static final _currencyFmt =`, used at `:3337` and `:3343`; note `:108` is `String? _selectedCoinId;`) and date formatting in `my_collection_screen.dart`. `import '../services/melt_value_service.dart';` (line 31) remains used by melt value computation in `my_collection_screen.dart` (`MeltValueService.compute` at `:3317` and `:3839`). Neither import becomes unused.
- **Exact Import Addition Diff (`my_collection_screen.dart:42–45`):**
```dart
<<<<
import '../models/collection_row.dart';
import '../constants.dart';
import '../constants/denomination_canon.dart';
====
import '../models/collection_row.dart';
import '../constants.dart';
import '../constants/denomination_canon.dart';
import '../widgets/collection_card_valuation_row.dart';
>>>>
```
- **Exact Valuation Variable & Row Diff (`my_collection_screen.dart:3015–3023` and `:3167–3192`):**
```dart
<<<<
            : (themeStartsYear ? label : '$yearMint $label').trim();

        final valCpg = _parseNumber(m['cpgRetail']);
        final finalVal = valCpg;
        
        final fmt = intl.NumberFormat.currency(symbol: '\$');
        final valueText = finalVal > 0 
            ? fmt.format(finalVal) 
            : (m[_F.aiValue]?.toString() ?? '—');
====
            : (themeStartsYear ? label : '$yearMint $label').trim();

        // Valuation precedence and pending chip encapsulated in CollectionCardValuationRow (NET-780b v2.0)
>>>>
```
```dart
<<<<
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      if (valueText == '—' || m['enrichment_status'] == 'pending')
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFFC9A227).withAlpha(25),
                            borderRadius: BorderRadius.circular(4),
                            border: Border.all(color: const Color(0xFFC9A227).withAlpha(120)),
                          ),
                          child: const Text('Valuation Pending', style: TextStyle(fontSize: 10, color: Color(0xFFC9A227), fontWeight: FontWeight.bold)),
                        )
                      else
                        Text(
                          valueText,
                          style: const TextStyle(
                            fontSize: 13,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFFC9A227),
                          ),
                        ),
                      if (condition.isNotEmpty)
                        GradeBadgeWidget(gradeCode: condition),
                    ],
                  ),
====
                  CollectionCardValuationRow(
                    data: m,
                    condition: condition,
                  ),
>>>>
```

---

### C. Denomination Word Boundary Patch in `canonical_mint_asset_service.dart` (MF-C5')
In `git show 4d17ca5e:numista_mobile/lib/services/canonical_mint_asset_service.dart`, lines 430–435 read verbatim (v2.1):
```dart
430:       // MF-1: cent and nickel, whole word or denomination field only. NEVER substring 'cent'.
431:       final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
432:           RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
433:       final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
434:           RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
435:       if (isCent && !isQuarter && !isHalf) {
```
(The 2026 guard is `:341 if (cleanYear == '2026') {`; dime handling is the earlier `.contains('dime')` return at `:342–345`. There is no `isDime` and no `y` in this method.)
Exact surgical replacement of lines **431–434 only** (`:435` stays as is). If the `<<<<` text does not match the file byte-for-byte, ABORT the step and commit nothing:
```dart
<<<<
      final isCent = RegExp(r'\b(1c|1¢|one cent|cent|penny)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b').hasMatch(cleanTitle);
      final isNickel = RegExp(r'\b(5c|5¢|five cents?|nickel)\b').hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b').hasMatch(cleanTitle);
====
      // MF-C5': (?!\w) fixes broken trailing \b on Unicode ¢; (?<![\d.]) prevents 15¢/25c/25 cent
      // from matching 1¢/5¢/cent while preserving '1 cent', '1¢', 'cent', '5¢', '5 cents', 'five cents'.
      final isCent = RegExp(r'(?<![\d.])(?:1c|1¢|1 cents?|one cent|penny)(?!\w)|(?:^|(?<![\d.])\s+)\bcent\b', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'\b(lincoln cent|one cent|penny)\b', caseSensitive: false).hasMatch(cleanTitle);
      final isNickel = RegExp(r'(?<![\d.])(?:5c|5¢|5 cents?|five cents?|nickel)(?!\w)', caseSensitive: false).hasMatch(cleanDenom) ||
          RegExp(r'\b(jefferson nickel|nickel|five cents?)\b', caseSensitive: false).hasMatch(cleanTitle);
>>>>
```

---

### D. Surgical Patch to `MeltValueService.parseFaceValue` (`lib/services/melt_value_service.dart:76–88`) (MF-C3')
In `git show 4d17ca5e:numista_mobile/lib/services/melt_value_service.dart`, lines 76–88 read verbatim:
```dart
76:     // 2. Sub-Dollar & Standard Silver/Base Denominations
77:     else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
78:     else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
79:     else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
80:     else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
81:     else if (s.contains('half dime')) { value = 0.05; }
82:     else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
83:     else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
84:     else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
85:     else if (s.contains('half cent')) { value = 0.005; }
86:     else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
87:     else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
```
Exact replacement at lines 76–88 so `half dime` precedes `dime`, `three cent` precedes `nickel`, and canonical word forms (`fifty cent`, `twenty-five cent`, `ten cent`, `five cent`) match before generic `'cent'`:
```dart
<<<<
    // 2. Sub-Dollar & Standard Silver/Base Denominations
    else if (s.contains('half dollar') || s.contains('50c') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('25c') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c')) { value = 0.20; }
    else if (s.contains('dime') || s.contains('10c') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('half dime')) { value = 0.05; }
    else if (s.contains('nickel') || s.contains('5c') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('three cent') || s.contains('3c')) { value = 0.03; }
    else if (s.contains('two cent') || s.contains('2c')) { value = 0.02; }
    else if (s.contains('half cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('cent') || s.contains('1c') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
====
    // 2. Sub-Dollar & Standard Silver/Base Denominations (MF-C3': multi-word & canonical forms first)
    else if (s.contains('half dollar') || s.contains('fifty cent') || s.contains('50c') || s.contains('50¢') || s.contains('50 cent') || s.contains(r'$0.50') || s.contains(r'$0.5')) { value = 0.50; }
    else if (s.contains('quarter dollar') || s.contains('quarter') || s.contains('twenty-five cent') || s.contains('twenty five cent') || s.contains('25c') || s.contains('25¢') || s.contains('25 cent') || s.contains(r'$0.25')) { value = 0.25; }
    else if (s.contains('twenty cent') || s.contains('20c') || s.contains('20¢') || s.contains('20 cent')) { value = 0.20; }
    else if (s.contains('half dime')) { value = 0.05; }
    else if (s.contains('dime') || s.contains('ten cent') || s.contains('10c') || s.contains('10¢') || s.contains('10 cent') || s.contains(r'$0.10') || s.contains(r'$0.1')) { value = 0.10; }
    else if (s.contains('three cent') || s.contains('3 cent') || s.contains('3c') || s.contains('3¢')) { value = 0.03; }
    else if (s.contains('nickel') || s.contains('five cent') || s.contains('5c') || s.contains('5¢') || s.contains('5 cent') || s.contains(r'$0.05')) { value = 0.05; }
    else if (s.contains('two cent') || s.contains('2 cent') || s.contains('2c') || s.contains('2¢')) { value = 0.02; }
    else if (s.contains('half cent')) { value = 0.005; }
    else if (s.contains('penny') || s.contains('one cent') || s.contains('cent') || s.contains('1c') || s.contains('1¢') || s.contains('1 cent') || s.contains(r'$0.01')) { value = 0.01; }
    else if (s.contains('dollar') || s.contains(r'$1')) { value = 1.00; }
>>>>
```

---

## 4. Execution Gates & Apply Ordering

### A. Pre-Flight Verification Against Code Pin `4d17ca5e` (MF-B2')
Before executing any file modifications on branch `p7-v8.9` (only after CoS $\ge 95$, SAG $\ge 95$, and Founder Eric's explicit typed YES):
```bash
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "p7-v8.9" ] || { echo "ABORT: HEAD is '$BR', not p7-v8.9"; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "ABORT: dirty tree"; exit 1; }
[ "$(git rev-parse origin/main)" = "9f04550a" ] || echo "WARN: check origin/main pin"
git diff --quiet 4d17ca5e HEAD -- numista_mobile/
```
- `origin/main` remains strictly locked at `9f04550a`. Stripe remains locked OFF.

### B. Kaggle & Google Inspector Deletions Boundary (MF-B1')
- NET-816 v1.11 is **PARKED**, and Catalog Chunk 1 (`9bbe20e4`) is scoped exclusively to 2 catalog items (`catalog_service.dart` / `catalog_browse_screen.dart`).
- NET-817's card and image changes (`:3017–3023`, `:3167–3192`, `:6356–6479`) have **zero overlap** with the inspector/Google-button lines (`:150–151`, `:3454`, `:3531–3548`, `:3820`, `:4387–4406`, `:5252–5278`, `:5549–5684`). By default, NET-817 leaves those lines untouched pending CoS re-homing to a dedicated inspector cleanup track. If CoS/Eric directs their inclusion at execution gate, all 7 verified spans in §2.A are removed atomically in Step 1 while preserving `_onSearchEbay` (`:4408–4426`) and verifying zero remaining references via `grep`.

### C. Stated Apply Ordering (MF-B3 — Closed, Preserved)
1. **Step 1 (Cards Plan NET-780b v2.3):**
   - Lands `canonicalYear` at line 77 and denomination regex fixes at lines 431–434 (`:435` untouched; apply by exact old text since inserting `canonicalYear` shifts later line numbers) of `numista_mobile/lib/services/canonical_mint_asset_service.dart`.
   - Lands face-value ordering fix at lines 76–88 of `numista_mobile/lib/services/melt_value_service.dart`.
   - Creates `numista_mobile/lib/widgets/collection_card_valuation_row.dart`.
   - Adds `import '../widgets/collection_card_valuation_row.dart';` at line 45 and wires `CollectionCardValuationRow` at lines 3017–3023 and 3167–3192 of `numista_mobile/lib/screens/my_collection_screen.dart`.
2. **Step 2 (Images Plan NET-780c v2.3):**
   - Creates `numista_mobile/lib/utils/owned_storage_url.dart`, `numista_mobile/lib/utils/collection_image_utils.dart`, and `numista_mobile/lib/widgets/collection_card_image.dart` (which calls `CanonicalMintAssetService.canonicalYear(data)` landed in Step 1).
   - Patches `hasUserUploadedPhotos` at line 39 of `numista_mobile/lib/services/canonical_mint_asset_service.dart` to also recognize URL-encoded `users%2f`.
   - Adds `import '../widgets/collection_card_image.dart';` at line 46 and delegates `_CollectionCardImage` (`:6356–6479`) in `numista_mobile/lib/screens/my_collection_screen.dart`.
   - Updates `img-src` in `numista_mobile/firebase.json:276`.

### D. Rollback Protocol
If any post-apply check or test fails:
```bash
#!/usr/bin/env bash
set -euo pipefail
CARDS_SHA="${CARDS_SHA:?set CARDS_SHA}"
IMAGES_SHA="${IMAGES_SHA:-}"        # empty if Images not applied
BR=$(git rev-parse --abbrev-ref HEAD)
[ "$BR" = "p7-v8.9" ] || { echo "ABORT: HEAD is '$BR', not p7-v8.9"; exit 1; }
git diff --quiet && git diff --cached --quiet || { echo "ABORT: dirty tree"; exit 1; }
for c in $IMAGES_SHA $CARDS_SHA; do
  git cat-file -e "$c^{commit}" && git merge-base --is-ancestor "$c" HEAD || { echo "ABORT: $c missing"; exit 1; }
done
# Images depends on Cards' canonicalYear helper: revert Images FIRST, then Cards (git revert only, no reset --hard)
if [ -n "$IMAGES_SHA" ]; then git revert --no-edit "$IMAGES_SHA" || { git revert --abort || true; exit 1; }; fi
git revert --no-edit "$CARDS_SHA" || { git revert --abort || true; exit 1; }
git push origin p7-v8.9            # only branch ever pushed; never main (locked 9f04550a)
```

---

## 5. Security, Rules & Standing Boundaries
- **No Argon:** Cycle has zero Argon reviews per Founder Eric's typed YES.
- **PLAN ONLY:** Zero code execution, zero deployments, zero Firestore writes without Founder Eric's explicit typed YES.
- **Alerts Only, Never Budget Caps:** Hard spending caps are permanently eliminated; billing alerts set at $20/mo.
- **No AJ PII:** Zero user emails or private credentials in plans, tests, or fixtures.
- **Nightly Stand-Down:** Standing 3:00 AM ET stand-down observed.

---

## 6. Real Automated Test Suites

### 6.1 `numista_mobile/test/widgets/my_collection_card_pricing_test.dart` (MF-C2', MF-C3', MF-C4, MF-C6' + Standalone `MeltValueService.parseFaceValue` Test)
```dart
import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/melt_value_service.dart';
import 'package:numista_ai/widgets/collection_card_valuation_row.dart';

double _luminance(int r, int g, int b) {
  double transform(int c) {
    final s = c / 255.0;
    return s <= 0.03928 ? s / 12.92 : pow((s + 0.055) / 1.055, 2.4).toDouble();
  }
  return 0.2126 * transform(r) + 0.7152 * transform(g) + 0.0722 * transform(b);
}

/// v2.2: source-over alpha composite of fg onto an opaque bg (for any translucent chip fill).
Color _over(Color fg, Color bg) {
  final a = fg.a;
  double mix(double f, double b) => f * a + b * (1 - a);
  return Color.from(alpha: 1.0, red: mix(fg.r, bg.r), green: mix(fg.g, bg.g), blue: mix(fg.b, bg.b));
}

int _ch(double v) => (v * 255).round(); // v2.1: Color.r/.g/.b (non-deprecated) on pin SDK ^3.11.3
double _contrastRatio(Color c1, Color c2) {
  final l1 = _luminance(_ch(c1.r), _ch(c1.g), _ch(c1.b));
  final l2 = _luminance(_ch(c2.r), _ch(c2.g), _ch(c2.b));
  final lighter = max(l1, l2);
  final darker = min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

void main() {
  group('CollectionCardValuationRow Production Widget Tests (MF-C2\', MF-C3\', MF-C4, MF-C6\')', () {
    test('Standalone MeltValueService.parseFaceValue table test (shared home_dashboard + cards parser)', () {
      expect(MeltValueService.parseFaceValue('Cent'), 0.01);
      expect(MeltValueService.parseFaceValue('Five Cents'), 0.05);
      expect(MeltValueService.parseFaceValue('Dime'), 0.10);
      expect(MeltValueService.parseFaceValue('Quarter Dollar'), 0.25);
      expect(MeltValueService.parseFaceValue('Half Dollar'), 0.50);
      expect(MeltValueService.parseFaceValue('Dollar'), 1.00);
      expect(MeltValueService.parseFaceValue('Half Dime'), 0.05);
      expect(MeltValueService.parseFaceValue('Three Cent Nickel'), 0.03);
      expect(MeltValueService.parseFaceValue('Set'), 0.0);
    });

    testWidgets('Case 1: CPG retail override displays retail without pending chip (even if enrichment_status is pending)', (tester) async {
      final data = {
        'cpgRetail': 12.50,
        'Denomination': 'Quarter Dollar',
        'enrichment_status': 'pending',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$12.50'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 2 (MF-C2\'): Real Firestore key "AI Estimated Value" displays formatted AI value when cpgRetail is 0', (tester) async {
      final data = {
        'cpgRetail': 0,
        'AI Estimated Value': '35.00',
        'Denomination': 'Half Dollar',
        'enrichment_status': 'completed',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$35.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsNothing);
    });

    testWidgets('Case 3 (MF-C2\'): Real Firestore key "AI Estimated Value" with enrichment_status == pending shows AI value AND pending chip', (tester) async {
      final data = {
        'cpgRetail': 0,
        'AI Estimated Value': '35.00',
        'Denomination': 'Half Dollar',
        'enrichment_status': 'pending',
      };

      await tester.pumpWidget(
        MaterialApp(
          theme: ThemeData.dark(),
          home: Scaffold(
            body: CollectionCardValuationRow(data: data),
          ),
        ),
      );

      expect(find.text('\$35.00'), findsOneWidget);
      expect(find.text('Value pending AI estimate'), findsOneWidget);
    });

    testWidgets('Case 4 (MF-C2\'): Sentinel AI values ("Pending", "null", "—") fall through to denomination face value + pending chip', (tester) async {
      for (final sentinel in const ['Pending', 'null', '—', '']) {
        final data = {
          'cpgRetail': 0,
          'AI Estimated Value': sentinel,
          'Denomination': 'Quarter Dollar',
        };

        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: Scaffold(
              body: CollectionCardValuationRow(data: data),
            ),
          ),
        );

        expect(find.text('\$0.25'), findsOneWidget, reason: 'Sentinel "$sentinel" must fall through to Quarter face value');
        expect(find.text('Value pending AI estimate'), findsOneWidget);
      }
    });

    testWidgets('Case 5 (MF-C3\'): Full canonical and historical denomination face-value table', (tester) async {
      final expectedTable = <String, String>{
        'Cent': '\$0.01',
        'Five Cents': '\$0.05',
        'Dime': '\$0.10',
        'Quarter Dollar': '\$0.25',
        'Half Dollar': '\$0.50',
        'Dollar': '\$1.00',
        'Half Dime': '\$0.05',
        'Three Cent Nickel': '\$0.03',
        'Set': '—',
      };

      for (final entry in expectedTable.entries) {
        final data = {
          'cpgRetail': 0.0,
          'Denomination': entry.key,
        };

        await tester.pumpWidget(
          MaterialApp(
            theme: ThemeData.dark(),
            home: Scaffold(
              body: CollectionCardValuationRow(data: data),
            ),
          ),
        );

        expect(
          find.text(entry.value),
          findsOneWidget,
          reason: 'Denomination "${entry.key}" must render "${entry.value}"',
        );
        expect(find.text('Value pending AI estimate'), findsOneWidget);
        expect(find.text('\$0.00'), findsNothing);
      }
    });

    testWidgets('Case 6 (MF-C6\', v2.2): mounts each cited surface and measures text vs PUMPED surface and PUMPED chip fill', (tester) async {
      // Cited surfaces: my_collection_screen.dart:211 _surface (dark 0xFF1E2937 / light Colors.white)
      // and :3031 virtual-child card colors (dark 0xFF0D1520 / light 0xFFF5F5F0).
      final cases = <(ThemeData, Color, double)>[
        (ThemeData.dark(), const Color(0xFF1E2937), 7.0),
        (ThemeData.dark(), const Color(0xFF0D1520), 7.0),
        (ThemeData.light(), const Color(0xFFFFFFFF), 4.5),
        (ThemeData.light(), const Color(0xFFF5F5F0), 4.5),
      ];
      final sampleData = {'cpgRetail': 0.0, 'Denomination': 'Five Cents'};
      for (final (theme, surface, min) in cases) {
        await tester.pumpWidget(MaterialApp(
          theme: theme,
          home: Scaffold(
            body: Container(
              key: const Key('udv_card_surface'),
              color: surface,
              child: CollectionCardValuationRow(data: sampleData),
            ),
          ),
        ));
        // Background actually rendered under the row (read from the pumped tree, not a local constant)
        final surfaceBox = tester.widget<Container>(find.byKey(const Key('udv_card_surface')));
        final renderedSurface = (surfaceBox.decoration as BoxDecoration?)?.color ?? surfaceBox.color!;
        expect(renderedSurface.a, 1.0, reason: 'card surface must be opaque for a valid ratio');

        final chipText = tester.widget<Text>(find.text('Value pending AI estimate'));
        final valText = tester.widget<Text>(find.text('\$0.05'));
        final textColor = chipText.style!.color!;
        expect(valText.style!.color, equals(textColor));

        final chip = tester.widget<Container>(find.byKey(const Key('valuation_pending_chip')));
        final chipFill = (chip.decoration! as BoxDecoration).color!;
        final effectiveChipBg = _over(chipFill, renderedSurface); // composited if translucent

        final label = '${theme.brightness} on ${renderedSurface.toARGB32().toRadixString(16)}';
        expect(_contrastRatio(textColor, renderedSurface), greaterThanOrEqualTo(min), reason: 'value text $label');
        expect(_contrastRatio(textColor, effectiveChipBg), greaterThanOrEqualTo(min), reason: 'chip text $label');
      }
    });

    testWidgets('Case 7 (v2.1 MF-SAG-C4): AI range strings with and without \$ format as \$a - \$b; non-numeric never \$0.00', (tester) async {
      for (final raw in ['12.00 - 15.00', '\$12.00 - \$15.00']) {
        await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
          data: {'cpgRetail': 0.0, 'AI Estimated Value': raw, 'Denomination': 'Quarter Dollar'}))));
        expect(find.text('\$12.00 - \$15.00'), findsOneWidget, reason: 'input "$raw"');
      }
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
        data: {'cpgRetail': 0.0, 'AI Estimated Value': 'about twelve', 'Denomination': 'Quarter Dollar'}))));
      expect(find.text('\$0.00'), findsNothing);
      expect(find.text('\$about twelve'), findsOneWidget);
    });

    testWidgets('Case 8 (v2.3 MF-3): Non-US row with "cent" denomination never renders USD face value', (tester) async {
      await tester.pumpWidget(MaterialApp(home: Scaffold(body: CollectionCardValuationRow(
        data: {'Country': 'Canada', 'Denomination': '1 Cent', 'cpgRetail': 0.0}))));
      expect(find.text('\$0.01'), findsNothing);
      expect(find.text('—'), findsOneWidget);
    });
  });
}
```

---

### 6.2 `numista_mobile/test/services/canonical_mint_asset_service_v2_0_test.dart` (MF-C5', MF-C7)
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:numista_ai/services/canonical_mint_asset_service.dart';

void main() {
  group('CanonicalMintAssetService v2.0 Enhancements (MF-C5\', MF-C7)', () {
    test('canonicalYear resolves explicit year fields and dual dates correctly', () {
      expect(CanonicalMintAssetService.canonicalYear({'year': '1958'}), '1958');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '2026.0'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'year': '', 'Year': '1964'}), '1964');
      expect(CanonicalMintAssetService.canonicalYear({'Year': '1776-2026'}), '2026');
      expect(CanonicalMintAssetService.canonicalYear({'title': '1921 Morgan Silver Dollar'}), '1921');
    });

    test('canonicalYear strictly ignores Personal Notes', () {
      final withNotes = {
        'title': 'Lincoln Cent',
        'personalNotes': 'Bought in 1999 from dealer',
        'notes': 'Inherited in 1985',
        'Personal Notes': '1999 estate lot',
      };
      expect(CanonicalMintAssetService.canonicalYear(withNotes), '');
    });

    test('MF-C5\': Denomination regex matches "1 cent", "1¢", "cent", "5¢", "5 cents", "five cents" with neutral title', () {
      for (final denom in const ['1 cent', '1¢', '1c', 'cent', 'one cent', 'penny']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': denom,
          'title': '2026 Coin', // Neutral title so cleanTitle cannot rescue cleanDenom
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(res, isNotNull, reason: 'Denomination "$denom" must resolve 2026 cent SKU');
        expect(res!.sku, '2026-CENT-P');
      }

      for (final denom in const ['5¢', '5c', '5 cents', '5 cent', 'five cents', 'five cent', 'nickel']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': denom,
          'title': '2026 Coin', // Neutral title so cleanTitle cannot rescue cleanDenom
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(res, isNotNull, reason: 'Denomination "$denom" must resolve 2026 nickel SKU');
        expect(res!.sku, '2026-NICKEL-P');
      }
    });

    test('MF-C5\': Denomination regex constructs without FormatException and rejects tokens reaching the new regex', () {
      // Explicit RegExp constructor check (ECMAScript lookbehind in Dart VM & JS)
      final centRe = RegExp(r'(?:^|\b)(?:1\s*cents?|1c|1¢(?!\w)|one\s+cent|(?<![\d.])cent|penny)\b', caseSensitive: false);
      final nickelRe = RegExp(r'(?:^|\b)(?:5\s*cents?|5c|5¢(?!\w)|five\s+cents?|(?<![\d.])nickel)\b', caseSensitive: false);
      expect(centRe.hasMatch('1 cent'), isTrue);
      expect(nickelRe.hasMatch('5 cents'), isTrue);
      expect(centRe.hasMatch('15¢'), isFalse);
      expect(centRe.hasMatch('15 cent'), isFalse);

      // Note: '25c' and '50c' are caught by earlier isQuarter/isHalf branches; '15¢', '15 cent', '35 cent', '100 cent' reach the new regex.
      for (final nonCentOrNickel in const ['15¢', '15 cent', '35 cent', '100 cent', '25 cent', '25c', '50 cent', '50c']) {
        final coin = {
          'Year': '2026',
          'mint_mark': 'P',
          'denomination': nonCentOrNickel,
          'title': '2026 Coin', // Neutral title
        };
        final res = CanonicalMintAssetService.resolveFromMap(coin);
        expect(
          res?.sku,
          isNot(anyOf('2026-CENT-P', '2026-NICKEL-P')),
          reason: 'Denomination "$nonCentOrNickel" must never match cent or nickel SKU',
        );
      }
    });
  });
}
```

---

## 7. Delivery & Sign-Off Requirements
- **Verification Command (Post-Approval Execution Only):**
  `flutter test test/widgets/my_collection_card_pricing_test.dart test/services/canonical_mint_asset_service_v2_0_test.dart test/services/canonical_mint_asset_service_test.dart`
- **Review Gate:** Requires independent score $\ge 95$ from Grok Bot CoS and Stand Alone Grok (SAG, grok-4.7) on **both** `FAILFIX_PLAN_NET-780b_CARDS_v2.0.md` and `FAILFIX_PLAN_NET-780c_IMAGES_v2.0.md` prior to Founder Eric's typed YES.
