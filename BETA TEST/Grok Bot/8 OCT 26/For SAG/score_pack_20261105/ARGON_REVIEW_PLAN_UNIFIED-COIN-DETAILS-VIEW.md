# ARGON TECHNICAL REVIEW: Unified Coin Details View Plan & EGM Review (`NET-798`)

- **Reviewer:** Argon (`31035602-8cdd-403f-8b72-7280605f5100` — Independent Technical Reviewer / Gemini 3.8 Code & Data Auditor)
- **Author Reviewed:** Antigravity CoS v4 (`ba2bfdb2`)
- **Timestamp:** 2026-11-05 1:53 PM ET
- **Reference Baton:** [`BATON_NET-798_ARGON_REVIEW_UNIFIED-COIN-DETAILS-VIEW_2026-11-05-1305.md`](file:///c:/Users/ericd/Documents/MyVertexProject/BETA%20TEST/Grok%20Bot/8%20OCT%2026/BATONS/BATON_NET-798_ARGON_REVIEW_UNIFIED-COIN-DETAILS-VIEW_2026-11-05-1305.md)
- **Target Documents Audited in This Turn:**
  1. [`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md) (lines 1–255)
  2. [`docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md) (lines 1–108)
  3. [`1 NUMISTA.AI/UI UX DESIGN/2026-11-04/Unified Coin Details/Spec_Unified_Coin_Details_2026-11-04.md`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/UI%20UX%20DESIGN/2026-11-04/Unified%20Coin%20Details/Spec_Unified_Coin_Details_2026-11-04.md) (lines 1–60)
- **Codebase Files Verified in This Turn:**
  - [`numista_mobile/lib/screens/my_collection_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart) (lines 2734–2780, 3038–3048, 3445–3458, 3750–4050)
  - [`numista_mobile/lib/screens/coin_detail_screen.dart`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/coin_detail_screen.dart) (lines 756–768, 890–922)
- **Technical Score:** **97 / 100 (`PASS — 0 Blocking Must-Fixes; 3 Non-Blocking Implementation Safeguards UCD-1..UCD-3 Logged for 10–16 Nov Build`)**
- **Mode:** **REVIEW ONLY (`NO EXECUTE`)** — Zero source code changes, zero deploys, zero Firestore writes, Stripe OFF, `origin/main` locked at `9f04550a`.

---

## 1. Executive Summary & Scorecard

| Audit Dimension (`BATON_NET-798`) | Weight | Score | Verdict |
|---|---|---|---|
| **1. Faithfulness to UX Spec & Founder Eric's 3 Locked Decisions (`Spec:57-60`)** | 25 | **25 / 25** | **PASS** — Locked Decisions #1 (`10-16 Nov build`), #2 (`Show values` session persistence across `Previous`/`Next` until `Close`), and #3 (`Congress.gov` fallback labeled `"From Congress.gov, not yet checked by us"`, catalog wins) are all enforced 1:1. |
| **2. Unification of Cards & Table Invocations & Codebase Citation Accuracy** | 20 | **19 / 20** | **PASS** — Both Cards View (`my_collection_screen.dart:3042-3045`), Table Cell Tap (`line 2736`), and Table Info Icon (`lines 2750-2780`) route to `UnifiedCoinDetailScreen.show`. Minor safeguard (`UCD-1`) logged to ensure both `isVirtualChild` and `else` branches in `lines 2761-2773` are redirected. |
| **3. Header, Media, 6 Consolidated Tabs & WCAG AAA Accessibility Matrix** | 20 | **20 / 20** | **PASS** — Solid `#ffffff` header with `32px` bold `#0b1a2e` title (`17.5:1` AAA contrast), replacing legacy `_kDark(context)` + `Colors.white` (`coin_detail_screen.dart:892-920`); side-by-side `"Front"`/`"Back"` photos with coin outline fallback (zero folder icons); 6 tabs with custom `Wrap` on `<=390px`; `>=52px` buttons. |
| **4. Values vs. Physical Storage Mutual Privacy Gate (`Spec:14, 27`)** | 20 | **20 / 20** | **PASS** — Eliminates the legacy defect in `_showCoinInspectorDialog` (`my_collection_screen.dart:3850-3852, 3990-3996`) where `Est. Value`, `Melt Value`, `Cost`, and `Storage` appeared on the same screen. Enforces strict mutual exclusivity + PIN gate. |
| **5. EGM Review Gate Compliance (`AMEND_BATON_NET-798`) & Standing Locks** | 15 | **13 / 15** | **PASS** — `docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (`98/100 APPROVED FOR BUILD`) completed across all 5 lenses before Argon handoff, with all 3 nits folded in. Cross-track advisory (`UCD-3`) logged on external link policy alignment. |
| **TOTAL** | **100** | **97 / 100** | **PASS (Ready for Grok Bot CoS `95+` -> SAG -> Founder Eric Typed YES)** |

---

## 2. Task-by-Task Verbatim Audit (Rule 6a / `NET-767`)

### Task 1: Faithfulness to UX Spec & Founder Eric's 3 Locked Decisions (`PASS`)

- **UX Spec Reference ([`Spec_Unified_Coin_Details_2026-11-04.md:57-60`](file:///c:/Users/ericd/Documents/MyVertexProject/1%20NUMISTA.AI/UI%20UX%20DESIGN/2026-11-04/Unified%20Coin%20Details/Spec_Unified_Coin_Details_2026-11-04.md#L57-L60)):**
  ```markdown
  57: ## LOCKED DECISIONS (Eric, 4 Nov 2026, 7:32 PM ET, typed in Chief of Staff's chat)
  58: 1. SCOPE: build the unified details view in the 10-16 Nov build.
  59: 2. SHOW VALUES: once tapped, values stay showing as the user steps Previous/Next coin, until Close.
  60: 3. CONGRESS.GOV: show laws we haven't checked, labeled "not yet checked by us". Catalog legislation always wins when it exists.
  ```
- **Plan Verification ([`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md:10, 144-146, 191-192, 227-229`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md#L10-L229)):**
  ```markdown
  10: **Target Build:** 10–16 November 2026 Sprint Build (Locked Decision #1).  
  ...
  144: 3. **Session Persistence (Eric Locked Decision #2):**
  145:    - Once `"Show values"` is tapped, values remain visible as the user steps through `Previous coin` / `Next coin`.
  146:    - Values revert to hidden immediately upon modal `Close`.
  ...
  191: 1. **Tier 1 (Catalog Wins):** If the Numista.AI Catalog entry contains an authorized `legislation` field, it takes precedence. Rendered with footer: `Source: Numista.Ai catalog (checked)`.
  192: 2. **Tier 2 (Congress.gov Fallback):** If catalog legislation is missing or empty, query Congress.gov statutory index (e.g. Public Law 116-330 for 2026 Semiquincentennial items). Rendered with prominent disclaimer: `From Congress.gov, not yet checked by us`.
  ...
  227: | **2. Values Persistence** | Does "Show values" persist across Previous/Next? | **LOCKED DECISION #2 (Founder Eric):** Once tapped, values remain visible as the user steps through coins, until Close. |
  228: | **3. Congress.gov Status** | Show unverified Congress.gov laws? | **LOCKED DECISION #3 (Founder Eric):** Show laws we haven't checked, explicitly labeled *"not yet checked by us"*. |
  229: | **4. Build Timing** | Build in W2 or post-Black Friday? | **LOCKED DECISION #1 (Founder Eric):** Build in the 10–16 Nov sprint build. |
  ```
- **Audit Finding:** All 3 of Founder Eric's locked decisions from 4 Nov 2026 (7:32 PM ET) are faithfully incorporated into the architecture, state lifecycle, data resolution hierarchy, and sprint schedule.

---

### Task 2: Split Architecture Verification & Unification of Cards and Table (`PASS`)

- **Codebase Verification of Current Bifurcated Entry Points ([`numista_mobile/lib/screens/my_collection_screen.dart:2734-2780, 3041-3045, 3449-3454`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L2734-L3454)):**
  ```dart
  2734:             final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
  2735: 
  2736:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
  ...
  2750:                         _iconBtn(Icons.info_outline,
  2751:                           crw.isVirtualChild ? 'View Parent Set' : 'View Details', () {
  ...
  2754:                           if (crw.isVirtualChild) {
  ...
  2761:                             CoinDetailScreen.show(
  2762:                               context,
  2763:                               coin: coin,
  2764:                               spotPrices: _spotPrices,
  ...
  2771:                           } else {
  2772:                             final coin = CoinModel.fromMap(m, crw.id);
  2773:                             CoinDetailScreen.show(
  2774:                               context,
  2775:                               coin: coin,
  2776:                               spotPrices: _spotPrices,
  ...
  3041:           child: InkWell(
  3042:             onTap: () {
  3043:               setState(() => _selectedCoinId = effectiveId);
  3044:               _showCoinInspectorDialog(effectiveId, m);
  3045:             },
  ...
  3449:   void _showCoinInspectorDialog(String coinId, Map<String, dynamic> data) {
  3450:     setState(() {
  3451:       _selectedCoinId   = coinId;
  3452:       _vaultShowObverse = true;
  3453:     });
  3454:     _fetchInspectorSimilar(data);
  ```
- **Codebase Verification of Legacy Privacy Breach in Cards Inspector ([`numista_mobile/lib/screens/my_collection_screen.dart:3850-3852, 3989-3996`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/my_collection_screen.dart#L3850-L3996)):**
  ```dart
  3850:       Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
  3851:       SizedBox(width: 10),
  3852:       Expanded(child: _metricCard('Melt Value', meltStr, Color(0xFF34A853), Icons.blur_circular_outlined)),
  ...
  3989:       section('PURCHASE & STORAGE', [
  3990:         // Format cost as currency ($XX.XX)
  3991:         ['Cost',        _formatCost(data[_F.cost]?.toString())],
  ...
  3996:         ['Storage',     data[_F.storageLocation]?.toString()],
  ```
- **Audit Finding:** The plan (`PLAN_UNIFIED-COIN-DETAILS-VIEW.md:97-110, 242-243`) replaces both `_showCoinInspectorDialog` and `CoinDetailScreen.show` with a single unified launcher `UnifiedCoinDetailScreen.show(...)` accepting `coinList` and `currentIndex` for `Previous coin` / `Next coin` stepping.

---

### Task 3: Component Architecture, WCAG AAA Header & Privacy Gate (`PASS`)

- **Legacy Header Contrast Defect Verified ([`numista_mobile/lib/screens/coin_detail_screen.dart:892-894, 918-921`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/coin_detail_screen.dart#L892-L921)):**
  ```dart
  892:     return Container(
  893:       color: _kDark(context),
  894:       padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
  ...
  918:                   Text(title,
  919:                     style: const TextStyle(
  920:                       color: Colors.white, fontSize: 18,
  921:                       fontWeight: FontWeight.bold, height: 1.3),
  ```
- **Legacy 7-Tab Structure Verified ([`numista_mobile/lib/screens/coin_detail_screen.dart:758-766`](file:///c:/Users/ericd/Documents/MyVertexProject/numista_mobile/lib/screens/coin_detail_screen.dart#L758-L766)):**
  ```dart
  758:             tabs: const [
  759:               Tab(text: 'Details'),
  760:               Tab(text: 'Financials'),
  761:               Tab(text: 'Provenance'),
  762:               Tab(text: 'AI Insights'),
  763:               Tab(text: 'History'),
  764:               Tab(text: 'Legislation'),
  765:               Tab(text: 'Known Errors'),
  766:             ],
  ```
- **Unified Component & Contrast Matrix Verification ([`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md:112-160, 165-175, 204-213`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/PLAN_UNIFIED-COIN-DETAILS-VIEW.md#L112-L213)):**
  ```markdown
  112: ### 3.2 Header Component (`_UnifiedHeader`)
  113: - **Background:** Solid white (`#ffffff`).
  114: - **Coin Title:** 32px bold font in `#0b1a2e` (Deep Navy), providing a **17.5:1 contrast ratio (WCAG AAA)**.
  115: - **Subtitle:** 20px regular font in `#333333` (e.g. `San Francisco · 90% Silver · United States`).
  116: - **Navigation Controls:**
  117:   - `◀ Previous coin`: Outlined button, minimum height 52px, text + icon.
  118:   - `Next coin ▶`: Outlined button, minimum height 52px, text + icon.
  119:   - `✕ Close`: Text button with clear label "Close", minimum height 52px.
  ...
  174: *(Note on Tab Implementation & Wrapping: Standard Flutter `TabBar` does not natively wrap across multiple rows. On wide screens, tabs render in a single high-contrast row. On narrow mobile viewports (≤390px), tabs are implemented using a responsive custom `Wrap` containing `FilterChip`/`InkWell` controls with active state bound to the `TabController`, ensuring minimum 56px touch targets with 22px bold text without horizontal clipping).*
  ```
- **Audit Finding:** Every requirement from `Spec_Unified_Coin_Details_2026-11-04.md` is satisfied:
  1. **Header:** Solid `#ffffff` background, `32px` bold `#0b1a2e` title (`17.5:1` WCAG AAA), `20px` `#333333` subtitle (`12.6:1` WCAG AAA), and `>=52px` full-word buttons (`◀ Previous coin`, `Next coin ▶`, `✕ Close`).
  2. **Media & Morgan:** Side-by-side `"Front"` and `"Back"` photos, tap-to-enlarge lightbox, gold-outlined coin silhouette + `"Add a photo"` empty state (zero folder icons), and `"Ask Morgan about this coin"` owl tile (`#1d4f91` on `#ffffff`, `8.1:1` WCAG AAA).
  3. **Values & Storage Mutual Privacy Gate:** Values are hidden behind `"Show values"` by default; revealing values blanks/hides Storage Location; revealing Storage Location requires PIN entry (`StorageLocationPinService`) and immediately re-hides all dollar values.
  4. **6 Consolidated Tabs:** `Overview`, `Purchase & value`, `Morgan's notes`, `History`, `Laws`, and `Known errors` (`>=56px` height, `22px` bold, custom `Wrap` on `<=390px` viewports).
  5. **Bottom Action Bar (`_BottomActionBar`):** `Edit`, `Wishlist`, `Verify`, and `Delete` (with two-stage confirmation dialog), all `>=52px` tall with icon + English word label.

---

### Task 4: Audit of EGM Review Gate Compliance (`AMEND_BATON_NET-798` — `PASS`)

- **EGM Review Report Verified ([`docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md:8-24, 47-58`](file:///c:/Users/ericd/Documents/MyVertexProject/docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md#L8-L58)):**
  ```markdown
  8: **Status:** **PLAN AUDIT COMPLETE**  
  9: **Overall Score:** **98 / 100**  
  10: **Executive Verdict:** **APPROVED FOR BUILD** (with 3 Minor Pragmatic Advisories for the 10–16 Nov Sprint)
  ...
  16: | Auditing Lens Shortname | Focus Scope | Status | Score (/20) |
  17: |---|---|---|---|
  18: | `implementation_readiness` | Technical actionability, state persistence, Sprint build readiness | **completed** | 19 / 20 |
  19: | `design_critic` | Faithfulness to UX Spec & Founder Eric's Locked Decisions | **completed** | 20 / 20 |
  20: | `codebase_details` | Citation accuracy, legacy split deprecation, privacy gates | **completed** | 19 / 20 |
  21: | `accessibility_contrast` | WCAG AAA conformance (17.5:1 / 18.9:1), touch targets ≥52px | **completed** | 20 / 20 |
  22: | `defect_prevention` | Elimination of folder icons, 1.1:1 text, co-location privacy leak | **completed** | 20 / 20 |
  23: | **Total** | **Comprehensive Swarm Audit** | **ALL RUN** | **98 / 100** |
  ```
- **Audit Finding:** In full compliance with `AMEND_BATON_NET-798` (`9:50 AM ET 5 Nov 2026`), AG CoS v4 ran the EGM review gate after drafting the plan and before handing off to Argon, filed `docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` beside the plan, and incorporated all 3 EGM nits (custom `Wrap` tab bar for `<=390px`, dual citation of Cards `3042-3045` and Table `2736`, and dedicated Section 3.5 `_BottomActionBar`).

---

## 3. Non-Blocking Implementation Safeguards & Proactive No-Silo Observations (`RADIO_NET-790`)

Zero blocking plan defects exist. We log **3 non-blocking safeguards (`UCD-1`..`UCD-3`)** for the 10–16 Nov Sprint execution:

1. **`UCD-1` (Redirect Both `isVirtualChild` and `else` Branches of `CoinDetailScreen.show` in `my_collection_screen.dart:2754-2780`):**
   - In `my_collection_screen.dart:2750-2780`, `_iconBtn(Icons.info_outline, ...)` invokes `CoinDetailScreen.show` in **two** places: line `2761` (`if (crw.isVirtualChild)`) and line `2773` (`else` branch for standard rows). During Step 3 (`PLAN_UNIFIED-COIN-DETAILS-VIEW.md:242-243`), ensure **both** branches (plus line `2736` table cell tap and line `3044` card tap) route to `UnifiedCoinDetailScreen.show`.
2. **`UCD-2` (Minor Snippet Line-Number Precision in `my_collection_screen.dart:3042-3045`):**
   - In `PLAN_UNIFIED-COIN-DETAILS-VIEW.md:41-43`, the snippet omits `3043: setState(() => _selectedCoinId = effectiveId);` right above `3044: _showCoinInspectorDialog(effectiveId, m);`. When replacing `_showCoinInspectorDialog` in Step 3, preserve `_selectedCoinId` state synchronization so the selected card/row highlight updates as the user steps through `Previous coin` / `Next coin`.
3. **`UCD-3` (Proactive No-Silo Cross-Check: Congress.gov Button vs. Site-Wide No-External-Links Rule):**
   - In `Spec_Unified_Coin_Details_2026-11-04.md:32-33` and `PLAN_UNIFIED-COIN-DETAILS-VIEW.md:184, 186, 193`, the Laws tab includes a `"Read on Congress.gov"` button (`https://www.congress.gov/bill/...`). Meanwhile, in `BATON_NET-788` (`FAILFIX_PLAN_NET-777_CATALOG_v1.2.md`) and `my_collection_screen.dart:3938` (`CoinFacts`), outbound third-party links were restricted so users are never sent off-site. Before executing the 10–16 Nov build, confirm with Founder Eric whether statutory citations on the Laws tab should render strictly as plain-text Act Name + Public Law number + summary in-app, or whether Congress.gov is an approved statutory exception.

---

## 4. Standing Locks & Final Verdict

- **Standing Locks Verified:**
  - **PLAN ONLY / REVIEW ONLY:** Zero application source code modified.
  - **`origin/main` Lock:** Strictly untouched at `9f04550a`.
  - **Stripe Lock:** Strictly OFF.
  - **Firestore Lock:** Zero Firestore writes or seeding.
- **Final Verdict:** **97 / 100 (`PASS`)**. Handing off to **Grok Bot CoS (`95+`) -> Stand Alone Grok (`SAG`) -> Founder Eric typed YES**.
