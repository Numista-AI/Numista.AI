# ARGON (GEMINI 3.8) TECHNICAL & UX PLAN REVIEW: `PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` (`BATON_NET-806`)

- **Reviewer:** Argon — Gemini 3.8 Independent Technical & UX Auditor
- **Track / Baton:** `NET-798` / `BATON_NET-806` (Unified Coin Details View v1.1 + EGM Gate)
- **Target Plan Reviewed:** `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` (356 lines)
- **Companion EGM Audit Reviewed:** `docs/EGM_REVIEW_PLAN_UNIFIED-COIN-DETAILS-VIEW.md` (108 lines, `98 / 100 APPROVED FOR BUILD`)
- **Timestamp:** 2026-11-05 16:30 ET
- **Composite Score:** **98 / 100 (`PASS — 0 Blocking Plan Must-Fixes; 2 Non-Blocking Execution Safeguards EX-806-1 & EX-806-2 Logged`)**
- **Execution Posture:** **PLAN REVIEW ONLY** (`origin/main` locked at `9f04550a`, Stripe strictly OFF, zero code edits, zero deployments, zero Firestore writes/seeding)

---

## 1. Executive Verdict & Rubric Breakdown

`docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md` resolves all **7 blocking must-fixes** from Grok Bot CoS (`COS_SCORE_NET-798_UNIFIED-COIN-DETAILS-VIEW_20261105.md` — 86/100 FAIL) and Stand Alone Grok (`61/100 FAIL`) and faithfully implements Founder Eric's 5 Nov 2:44 PM ET typed `AMEND` (`AMEND_BATON_NET-806_CONGRESS-GOV-ONLY_LAWS-TAB_2026-11-05-1444.md`).

| Rubric Dimension | Weight | Score | Notes |
| :--- | :---: | :---: | :--- |
| **1. Must-Fix #1 (Storage Location PIN Service & Mutual Privacy Gate)** | 20 | **20 / 20** | Fictional `StorageLocationPinService` dropped (`§1` line 30, `§3.4` lines 181–185). Physical storage location is strictly hidden across all unified views until a dedicated PIN architecture gets Founder Eric's separate typed YES. Values (`"Show values"`) persist across `Previous`/`Next` until `Close` and never share a screen with storage location. |
| **2. Must-Fix #2 (All 5 Invocation Call Sites & Contrast Citations)** | 20 | **20 / 20** | All 5 call sites in `numista_mobile/lib/screens/my_collection_screen.dart` quoted verbatim and routed (`2736` table cell tap, `2761` & `2773` `CoinDetailScreen.show`, `3044` card tap preserving `3043` `setState`, and `3122` parent-set card container tap), plus `numista_mobile/lib/screens/coin_detail_screen.dart:59, 892-894, 918-922` light-mode contrast defect (`_kDark(context)` = `0xFFF4F4F2` with `Colors.white`). |
| **3. Must-Fix #3 & #4 (Public / Guest Mode Hide-List & CPG Retail Pricing)** | 20 | **19 / 20** | `§4.1` (lines 201–213) hard-suppresses purchase price, cost, date, invoice, retailer, item #, ref #, storage, `"Show values"` toggle, personal notes, and `Edit`/`Delete`/`Verify`/`Wishlist`. `§5` (lines 225–231) enforces CDN CPG retail (`cpgRetail`) only, zero wholesale, AI value labeled `"AI Estimate (Experimental)"`, and drops Live eBay (`my_collection_screen.dart:3856-3862`). Logged `EX-806-2` (-1 pt) for authenticated Tab 2 AI badge consistency. |
| **4. Must-Fix #5 (Congress.gov-Only Laws Tab per Eric Typed AMEND)** | 20 | **20 / 20** | `§6` (lines 234–260) permits outbound links **exclusively** to `https://www.congress.gov/bill/...` via plain `<a href>` text links (`target="_blank"`, `rel="noopener noreferrer"`), zero external images from Congress.gov, zero PCGS/NGC links (`[cert no. redacted]`), catalog legislation wins (`Source: Numista.AI catalog (checked)`), unchecked Congress.gov labeled `"From Congress.gov, not yet checked by us"`, US-only scope, `$0.00` hard cap / fail-closed. |
| **5. Must-Fix #6 & #7 (Feature Flag, Rollback, Code Freeze & Firestore Writes Gate)** | 20 | **19 / 20** | `§8` (lines 287–291) segregates all Firestore writes (`Edit`, `Wishlist`, `Delete`, research log) behind a separate typed YES. `§9` (lines 295–322) specifies `kUnifiedCoinDetailsEnabled`, preserves legacy views in the 10–16 Nov build, enforces preview channel + pre-26 Nov code freeze. Logged `EX-806-1` (-1 pt) for `git revert <feature-sha>` vs `HEAD...9f04550a`. |
| **TOTAL** | **100** | **98 / 100** | **PASS (`>= 95` Gate Met)** |

---

## 2. Rule 6(a) / `NET-767` Verbatim Code & Plan Verification (All Files Read via `read_file` in This Turn)

### 2.1 All 5 Call Sites in `numista_mobile/lib/screens/my_collection_screen.dart` — `PASS`
- **Verified in `numista_mobile/lib/screens/my_collection_screen.dart:2734-2736` & `2754-2776` (Call Sites 1, 2, 3):**
  ```dart
  2734:             final effectiveId = crw.isVirtualChild ? (crw.parentDocId ?? crw.id) : crw.id;
  2735: 
  2736:             void onTap() => _showCoinInspectorDialog(effectiveId, m);
  ...
  2754:                           if (crw.isVirtualChild) {
  2755:                             final parentDoc = _cachedCoinsDocs
  2756:                                 .where((d) => d.id == crw.parentDocId)
  2757:                                 .firstOrNull;
  2758:                             if (parentDoc == null) return; // parent missing — skip
  2759:                             final parentData = (parentDoc.data() as Map<String, dynamic>?) ?? {};
  2760:                             final coin = CoinModel.fromMap(parentData, parentDoc.id);
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
  ```
- **Verified in `numista_mobile/lib/screens/my_collection_screen.dart:3041-3045` & `3118-3124` (Call Sites 4 & 5):**
  ```dart
  3041:           child: InkWell(
  3042:             onTap: () {
  3043:               setState(() => _selectedCoinId = effectiveId);
  3044:               _showCoinInspectorDialog(effectiveId, m);
  3045:             },
  ...
  3118:                         onTap: () {
  3119:                           final parentId = m['parent_set_id'].toString();
  3120:                           final parentDoc = _cachedCoinsDocs.where((d) => d.id == parentId).firstOrNull;
  3121:                           if (parentDoc != null) {
  3122:                             _showCoinInspectorDialog(parentDoc.id, parentDoc.data());
  3123:                           }
  3124:                         },
  ```
- **Verified Legacy Privacy Co-Display & Live eBay Tile in `numista_mobile/lib/screens/my_collection_screen.dart:3850-3862` & `3989-3999`:**
  ```dart
  3850:       Expanded(child: _metricCard('Est. Value', data[_F.aiValue]?.toString() ?? '--', Color(0xFF1A73E8), Icons.attach_money)),
  ...
  3856:       Expanded(child: _metricCard(
  3857:           'Live eBay',
  3858:           _ebayPrices[_selectedCoinId] ?? 'Check >',
  3859:           Color(0xFFE53935),
  3860:           Icons.shopping_cart_outlined,
  3861:           onTap: () => _onSearchEbay(data),
  3862:       )),
  ...
  3989:       section('PURCHASE & STORAGE', [
  3990:         // Format cost as currency ($XX.XX)
  3991:         ['Cost',        _formatCost(data[_F.cost]?.toString())],
  ...
  3996:         ['Storage',     data[_F.storageLocation]?.toString()],
  ```

### 2.2 Light-Mode Contrast Defect in `numista_mobile/lib/screens/coin_detail_screen.dart` — `PASS`
- **Verified in `numista_mobile/lib/screens/coin_detail_screen.dart:59` & `892-922`:**
  ```dart
  59: Color _kDark(BuildContext c) => _isDarkCtx(c) ? const Color(0xFF0B1120) : const Color(0xFFF4F4F2);
  ...
  892:     return Container(
  893:       color: _kDark(context),
  894:       padding: const EdgeInsets.fromLTRB(20, 14, 12, 16),
  ...
  918:                   Text(title,
  919:                     style: const TextStyle(
  920:                       color: Colors.white, fontSize: 18,
  921:                       fontWeight: FontWeight.bold, height: 1.3),
  922:                   ),
  ```

### 2.3 Storage Location Suppression, Public Hide-List, CPG Retail & Congress.gov Laws Tab (`§3.4`, `§4.1`, `§5`, `§6.2`) — `PASS`
- **Verified in `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md:181-185` (`§3.4`):**
  ```markdown
  181: 4. **Physical Storage Location Security (Resolution of Must-Fix #1):**
  182:    - Fictional `StorageLocationPinService` is completely removed from the architecture.
  183:    - Physical storage location is **strictly suppressed** across all unified views.
  184:    - It will remain hidden and inaccessible until a formal storage PIN architecture, crypto model, and UI design are separately specified, reviewed, and approved via Founder Eric's typed YES.
  185:    - Under no circumstances will physical storage location and valuation figures ever share a viewport.
  ```
- **Verified in `docs/PLAN_UNIFIED-COIN-DETAILS-VIEW_v1.1.md:225-231` (`§5`) & `251-260` (`§6.2`):**
  ```markdown
  227: 1. **Authorized Value Source:** Valuation metrics are sourced strictly and exclusively from **CDN CPG retail** (`cpgRetail`).
  228: 2. **No Wholesale Pricing:** Wholesale prices (e.g., dealer ask/bid or wholesale CDN sheets) are strictly excluded from display.
  229: 3. **AI Valuation Labeling:** AI-derived valuations must never be displayed as authoritative market prices or preferred over CDN CPG retail. If displayed, they must be explicitly labeled: `"AI Estimate (Experimental)"`.
  230: 4. **Live eBay Tile:** Dropped as a valuation price tile.
  ...
  251: ### 6.2 Implementation Rules for Laws Tab:
  252: 1. **Tier 1 (Catalog Wins):** If the Numista.AI Catalog entry contains an authorized `legislation` field, it takes precedence. Label: `Source: Numista.AI catalog (checked)`.
  253: 2. **Tier 2 (Congress.gov Fallback):** If catalog legislation is missing, query Congress.gov statutory index. Rendered with mandatory prominent disclaimer: `From Congress.gov, not yet checked by us`.
  254: 3. **Outbound Linking Rules:**
  255:    - Permitted **exclusively** to `https://www.congress.gov/bill/...`.
  256:    - Formatted strictly as plain `<a href>` text links with `target="_blank"` and `rel="noopener noreferrer"`.
  257:    - **Strictly Prohibited:** Zero outbound links to PCGS, NGC, Greysheet, or any third-party coin service. NGC/PCGS cert lookups render in-app plain text citations only (`[cert no. redacted]`).
  258:    - **Zero Hotlinked Images:** Zero images may be fetched or rendered from Congress.gov (text and plain links only).
  259: 4. **US-Only Scope:** Statutory legal records and Congress.gov queries apply strictly to coins, notes, and currency of current and former US states, territories, and possessions. Foreign coins bypass Congress.gov lookups entirely.
  260: 5. **Cost & Spend Hard Cap:** Congress.gov API calls run under a strict **$0.00 / capped budget**. Queries fail-closed (return empty state immediately on any API error, rate limit, or timeout). Zero paid API calls.
  ```

---

## 3. Non-Blocking Execution Safeguards (`EX-806-1` & `EX-806-2`)

1. **`EX-806-1` (To-Be-Created Files & Single-Commit Revert on `dev`):**
   - `numista_mobile/lib/config/feature_flags.dart` (`§9.1` line 298) and `numista_mobile/test/screens/unified_coin_detail_screen_test.dart` (`§10` line 328) are new files to be created during the 10–16 Nov sprint build.
   - In `§9.3` line 321 (`git revert --no-commit HEAD...9f04550a`), since `9f04550a` is the locked `origin/main` SHA, instant code rollback on `dev` should either toggle `kUnifiedCoinDetailsEnabled = false` (`§9.2` lines 309–314) or run `git revert <feature-commit-sha>` on `dev`.
2. **`EX-806-2` (Tab 2 Valuation Tile Labeling in Authenticated Mode):**
   - In authenticated user vault mode (`isPublicGuestMode: false`), ensure Tab 2 (`Purchase & value`, `§7` line 269) displays CDN CPG retail (`cpgRetail`) as the primary market valuation and only renders `data[_F.aiValue]` when explicitly labeled `"AI Estimate (Experimental)"` per `§5` line 229.

---

## 4. Proactive No-Silo Site & Product Observations (`RADIO_NET-790`)

1. **Alignment with `NET-808` (`Catalog v1.5`) & `NET-780b` (`Cards v1.2`):** The `isPublicGuestMode: true` sandbox (`§4.1`) and `[cert no. redacted]` plain-text certification rule (`§6.2` line 257) align seamlessly with the public catalog detail view (`NET-808`) and card-level NGC redaction (`NET-780b`), ensuring that when `UnifiedCoinDetailScreen` ships in the 10–16 Nov build, public catalog visitors and private vault owners share one WCAG AAA modal without leaking private fields.
