# Numista.AI — Course of Action (COA)
**Date:** April 29, 2026 | **Session:** My Collection Review

---

## SECTION 1 — PCGS Coin Detail Issues
*(2025-W Silver Eagle w/ US Army Privy · 986403.70/53652580)*

---

### Issue 1.1 — PCGS Number vs Cert Number (+ Clickable Link)

**Current state:** The coin is stored with `PCGS Number: 986403` (coin-type catalog number). The cert `53652580` is in `Certification Number` but not shown as a tappable link anywhere.

**Primary COA:**
- Display both in the Coin Inspector:
  - `PCGS #: 986403` (coin type — label only, not tappable)
  - `Cert #: 53652580` (this slab — **tappable, opens in-app browser**)
- Use `url_launcher` (already imported): `launchUrl(Uri.parse('https://www.pcgs.com/cert/$certNo'), mode: LaunchMode.externalApplication)`
- Same treatment in the result card in `add_coins_hub.dart`
- URL table by grading service (from `pcgs_integration_notes.md`):
  - PCGS → `pcgs.com/cert/{certNo}`
  - NGC → `ngccoin.com/certlookup/{certNo}`
  - ANACS → `anacs.com/verify?cert={certNo}`
- **Files:** `my_collection_screen.dart` (inspector), `add_coins_hub.dart` (result card)

**Alternate COA:** Show only the cert number (drop PCGS # from UI — it's an internal catalog ID most users don't recognize). Simpler, but loses traceability for dealers/power users.

ERIC NOTES: 

### Issue 1.2 — Year "2025-W" + Mint Mark "W" Redundant

**Root cause confirmed (`my_collection_screen.dart` line 222–226):**
```dart
String _yearMint(Map m) {
  final y  = m[_F.year]?.toString()...;
  final mm = m[_F.mintMark]?.toString() ?? '';
  return mm.isNotEmpty ? '$y-$mm' : y;  // appends mint to year
}
// Mint column ALSO reads mintMark → "W" shown twice
```

**Primary COA:**
- **Year cell** → raw year only (`2025`). Remove the `-$mm` suffix from `_yearMint()` (or stop using it in the Year cell).
- **Mint cell** → mint mark only (`W`).
- Visually compact the two columns: set their `columnSpacing` to ~4px (vs the default 14px for all other columns), and remove the internal cell border between them, so they read as `2025 W` — one visual unit, two sortable columns.
- **Files:** `my_collection_screen.dart` — `_yearMint()`, `_buildDataTable()` case `_F.year`, `_columns` widths

**Alternate COA:** Keep `_yearMint()` in the Year cell, and blank the Mint cell when mint is already embedded in Year. Simpler, but Mint column is no longer independently sortable.

---

### Issue 1.3 — Theme/Subject Blank (Should Be "U.S. Army")

**Current state:** `mapToFirestoreSchema()` does not write to `Theme/Subject`. The PCGS `Name` field contains `"Silver Eagle w/ U.S. Army Privy 250th Anniversary"` — the theme is there, just not extracted.

**Primary COA:**
- Add a `_parseTheme(String coinName)` helper in `pcgs_import_service.dart`:
  - Keyword lookup table: `"U.S. Army"`, `"Marines"`, `"Navy"`, `"Air Force"`, `"Coast Guard"`, `"Women's Suffrage"`, `"West Point"`, `"American Women"`, etc.
  - Write to `Theme/Subject` field in the schema map.
- **File:** `pcgs_import_service.dart` — `mapToFirestoreSchema()`

**Alternate COA:** Don't auto-parse. Show a one-tap "Enrich" prompt after import: *"We detected 'U.S. Army Privy' — set Theme/Subject to 'U.S. Army'?"* Zero false positives, but requires a user tap.

---

### Issue 1.4 — Melt Value Blank (Should Auto-Calculate)

**Known data available at import time:**
- PCGS returns `MetalContent: "99.93% Silver, .007% Copper"`
- All Silver Eagles = 1 troy oz (US Mint spec — safe to hardcode for this series)
- Silver spot price: already live from `/api/spot_prices` backend

**Formula:** `MeltValue = spotPrice × weightOz × purity`

**Primary COA:**
- In `mapToFirestoreSchema()`:
  1. Parse purity from `MetalContent`: `"99.93% Silver"` → `0.9993`
  2. Look up weight from series name: `"Silver Eagle"` → `1.0 oz` (hardcoded table for known US Mint series)
  3. Fetch current silver spot from `/api/spot_prices`
  4. Store result as `"~$32.15"` (tilde = spot-price-dependent approximation)
- Add `weightOz` to the Firestore schema so melt value can be recalculated later as spot prices change.
- **Files:** `pcgs_import_service.dart`, `my_collection_screen.dart` (display)

**Alternate COA:** Skip calculation at import time. Add a **"Recalculate Melt Values"** button on My Collection that batch-updates all coins where `Is Silver == true` and `weightOz` is known, using the current spot price. More maintainable; values stay current.

---

### Issue 1.5 — Missing Stock Images

**Current state:** PCGS API returns `ObverseImageURL` and `ReverseImageURL` stored as `image_url_obverse` / `image_url_reverse` in Firestore. Inspector has `Image.network()` calls but images may not display on localhost (PCGS CDN may block hotlinking or localhost origin).

**Primary COA:**
1. Open browser DevTools → Network tab → select the coin → check if image requests return 200 or 403.
2. **If 403 (CDN blocking):** At import time, proxy the download through the backend and upload to Firebase Storage. Store the Firebase Storage URL. Permanent fix.
3. **If 200 (just a field name mismatch):** Verify the inspector reads `image_url_obverse` (lowercase, with underscores) — confirm this matches what `mapToFirestoreSchema()` writes.
4. Fallback: Show generic coin silhouette until images load.
- **Files:** `pcgs_import_service.dart` (import), `my_collection_screen.dart` (inspector image widget)

**Alternate COA:** Use the `CoinFactsLink` URL (also returned by PCGS API) to open the PCGS CoinFacts page in a browser — user sees official images there without us needing to host them.

---

## SECTION 2 — My Collection Page Issues

---

### Issue 2.1 — Year/Mint Redundant *(same root cause as 1.2)*

See 1.2 above. The fix to `_yearMint()` and the compact column spacing applies identically to the collection table.

---

### Issue 2.2 — No Sticky/Frozen Header Row

**Current state:** `DataTable` is inside a vertical `SingleChildScrollView`. Header row scrolls away with the data.

**Primary COA:**
- Split into two `DataTable` widgets:
  - **Header-only table** (pinned outside the vertical scroll) — columns, no rows
  - **Data-only table** (inside vertical `SingleChildScrollView`) — rows, `headingRowHeight: 0` to hide its own header
  - Both linked to the same `_tableScrollCtrl` for horizontal sync
- This is the standard Flutter "freeze header" pattern for web data tables.
- **File:** `my_collection_screen.dart` — `_buildDataTable()`

**Alternate COA:** Adopt the `two_dimensional_scrollables` package (`TableView` widget) which has built-in sticky headers and sticky columns. More initial work but better long-term, especially if "freeze first column" is later requested.

---

### Issue 2.3 — Est. Value Discrepancy (~10% vs Homepage)

**Root cause:** My Collection stats sum `AI Estimated Value` across only the `_limit` docs shown (default 50). Homepage streams **all docs** with no limit. With >50 coins, the gap equals the value of the coins not in the current page.

**Primary COA:**
- Compute stats totals from a **separate, unlimited query** (or store the aggregate in a Firestore summary document updated on each write).
- Show a clarifying note: *"Showing 50 of N coins · totals reflect full collection"*
- **File:** `my_collection_screen.dart` — `_buildStatsRow()`, `build()` StreamBuilder query

**Alternate COA:** Remove the stats row from My Collection entirely. Single source of truth = Homepage dashboard. Eliminates the discrepancy by design.

---

### Issue 2.4 — Double Screen Refresh on Coin Selection

**Root cause:** `onSelectChanged` calls `setState()`. Then `_buildInspectorSection()` is called during that rebuild and triggers `addPostFrameCallback` → `_fetchInspectorSimilar()` → second `setState()`.

**Primary COA:**
- Move the `addPostFrameCallback` call out of `_buildInspectorSection` (which runs on every build) into `onSelectChanged` (runs only on user tap). Add a guard: skip if `_selectedCoinId` hasn't changed.
- **File:** `my_collection_screen.dart` — `_buildInspectorSection()`, `onSelectChanged`

**Alternate COA:** Debounce: wait 150ms after selection before triggering the similar-coin fetch. Rapid taps don't cascade.

---

### Issue 2.5 — "Silver" Column → Should Be "Precious Metal"

**Current state:** `_ColDef(_F.isSilver, '🥈 Silver', 52)` — boolean field.

**Primary COA:**
- Rename column header: `🪙 P.Metal`
- Change Firestore field from boolean `Is Silver` → string `Precious Metal` (values: `"Silver"`, `"Gold"`, `"Platinum"`, `"Palladium"`, `""`)
- Update `_isSilverSeries()` → `_detectPreciousMetal()` to return the metal string
- Migration script `migrate_precious_metal.py`: `Is Silver: true` → `Precious Metal: "Silver"`
- **Files:** `pcgs_import_service.dart`, `my_collection_screen.dart`, new `migrate_precious_metal.py`

**Alternate COA:** Keep boolean `Is Silver` for backward compat; add new `Precious Metal` text field alongside it. No migration; old data still works.

---

### Issue 2.6 — Cost Shows `3700.0` Instead of `$3,700.00`

**Root cause:** Cost stored as raw float in Firestore; cell renderer does `.toString()` with no formatting.

**Primary COA:**
- In the `case _F.cost:` renderer:
  ```dart
  final n = double.tryParse(raw.replaceAll(RegExp(r'[^\d.]'), ''));
  value = n != null ? NumberFormat.currency(symbol: '\$').format(n) : raw;
  ```
- Also fix at import: `mapToFirestoreSchema()` should store cost as formatted string `"$3,700.00"`, not raw float.
- **File:** `my_collection_screen.dart` — Cost case in `_buildDataTable()`

**Alternate COA:** Store cost as Firestore `number` (double) always; format at every display point. Cleaner for math/sorting but requires all display sites to format consistently.

---

### Issue 2.7 — Edit Button Inaccessible (Scrollbar Bounces Back)

**Root cause:** The `ConstrainedBox(minWidth: screenWidth - 128)` collapses the scroll range on wider viewports, causing the horizontal scroll to snap back. The Edit button (if it existed) would be in the rightmost `Actions` column.

**Primary COA:**
- **Move Actions column to the left** (column index 0) — always visible, no scrolling required. Standard UX for action tables.
- **Add Edit button**: pencil icon that opens `AddCoinManualForm` pre-populated with the selected coin's data.
- **Fix the scroll bounce**: replace `ConstrainedBox(minWidth: ...)` with an explicit computed `width` (same value already calculated for the top scroll strip).
- **File:** `my_collection_screen.dart` — `_buildDataTable()`, `_columns`, `Actions` DataCell

**Alternate COA:** Keep Actions on the right but make it sticky (always visible alongside a scrolling middle section). Requires a multi-`DataTable` layout — more complex.

---

### Issue 2.8 — Denomination Shows `1` or `5` Instead of `$1` or `$5`

**Root cause:** Some coins have `Denomination: "1"` (plain number string). `_faceValue()` and the cell renderer don't handle this.

**Primary COA:**
- Cell renderer: if denomination is a plain number with no `$`, prepend `$`:
  ```dart
  if (RegExp(r'^\d+(\.\d+)?$').hasMatch(value)) value = '\$$value';
  ```
- Fix `_faceValue()` to parse plain numbers: `double.tryParse(s.replaceAll('\$',''))` as a fallback
- Fix import: confirm PCGS API returns `"$1"` and it passes through `mapToFirestoreSchema()` correctly
- **Files:** `my_collection_screen.dart` — Denomination cell + `_faceValue()`, `pcgs_import_service.dart`

**Alternate COA:** One-time migration script to find all `Denomination` values matching `/^\d+$/` and reformat as `"$N"`.

---

## SECTION 3 — Homepage Issues

---

### Issue 3.1–3.4 — Reorder Sections + Recently Added → Last 5

**Current order** (code line ~220–420):
1. Dashboard metric cards
2. Live Spot Prices
3. Market Intel (news)
4. Release Notes
5. Recently Added

**Target order:**
1. Dashboard metric cards ← stays
2. Recently Added ← move up (last **5**, not 3)
3. Live Spot Prices ← move up (add "Last updated" timestamp + source)
4. System Updates & Release Notes ← move up
5. Market Intel ← move to bottom (+ fix news feed)

**Primary COA — Reorder:**
- Rearrange the `Column` children in `home_dashboard.dart`. Pure cosmetic swap, no logic changes.
- `take(3)` → `take(5)` for Recently Added
- Fix sort key: prefer `importedAt` → fallback `timestamp` → fallback `created_at`

**Primary COA — Spot price timestamp:**
- Add `DateTime? _pricesLastUpdated` to state; set in `_fetchSpotPrices()`
- Display: `Last updated: 29 APR 2026 @ 10:46 EST · Source: [API name from backend]`

**Primary COA — News feed fix:**
- Verify `/api/mint_news` endpoint on the backend (likely broken silently)
- **Proposed top 5 sources (for your approval before implementing):**
  1. **CoinWorld** — coinworld.com (RSS)
  2. **Numismatic News** — numismaticnews.net (RSS)
  3. **PCGS News** — news.pcgs.com (RSS)
  4. **NGC News** — ngccoin.com/news (RSS)
  5. **US Mint News** — usmint.gov/news (official RSS)
- **File:** `home_dashboard.dart`, `numista_backend/main.py`

**Alternate COA for news:** Use NewsAPI.org (free tier, <100 req/day) with query `"numismatics" OR "PCGS" OR "US Mint" OR "coin collecting"`. Faster to implement than scraping 5 RSS feeds.

---

### Issue 3.5 — Dashboard: Add "Profit" Box + Improve Card Typography

**Profit = Est. Portfolio Value − Acquisition Cost**

**Primary COA:**
- Add 5th metric card: `_metricCard('Profit', ...)` with green value if positive, red if negative
- On narrow screens: 2×2 grid + Profit as a full-width 5th card below
- **Typography improvements** (in `_metricCard()`):
  - Label: `fontSize 11 → 14`, add `FontWeight.w600`
  - Value: `fontSize 22 → 28`, keep `FontWeight.w800`
  - Padding: `vertical: 16 → 24`
  - Add colored top accent bar per card (blue=Coins, green=Portfolio, amber=Cost, silver=Melt, teal=Profit)
- **File:** `home_dashboard.dart` — `_metricCard()`, metric row `LayoutBuilder`

**Alternate COA for Profit:** Show as a sub-label under Portfolio Value: `$82,450  ↑ $4,230 gain`. No 5th box needed — saves horizontal space.

---

### Issue 3.6 — Face Value Wrong ($4.57 on $80K Portfolio)

**Root cause confirmed in code:** `_computeFaceValue()` returns `0.00` for any denomination it can't pattern-match. Coins stored as plain `"1"`, `"5"`, or `"0.25"` fall through all checks.

**Primary COA:**
1. Add numeric fallback at the end of `_computeFaceValue()`:
   ```dart
   final n = double.tryParse(s.replaceAll('\$', '').trim());
   if (n != null) return n;
   ```
2. Fix PCGS import to store `Denomination` as `"$1"` (with symbol)
3. Keep `_faceValue()` in `my_collection_screen.dart` in sync with `_computeFaceValue()` in `home_dashboard.dart` — they're duplicates and should be extracted to a shared utility
- **Files:** `home_dashboard.dart`, `my_collection_screen.dart` — both `_computeFaceValue`/`_faceValue`

**Alternate COA:** Store a numeric `faceValueAmount` field at import time; all math uses that field directly. No string parsing needed. More robust long-term.

---

## Priority Ranking

| Priority | Issue | Est. Time | Risk |
|---|---|---|---|
| 🔴 P1 | 2.7 — Edit button inaccessible + Move Actions left | 45 min | Low |
| 🔴 P1 | 3.6 — Face Value wrong (numeric fallback) | 30 min | Low |
| 🔴 P1 | 1.2/2.1 — Year + Mint redundant "W" | 30 min | Low |
| 🟠 P2 | 2.2 — Sticky frozen header row | 1 hr | Medium |
| 🟠 P2 | 2.3 — Est. Value discrepancy (limit vs all) | 45 min | Low |
| 🟠 P2 | 2.6 — Cost formatting `3700.0 → $3,700.00` | 20 min | Low |
| 🟠 P2 | 2.8 — Denomination `1 → $1` | 20 min | Low |
| 🟡 P3 | 1.1 — Cert # tappable link | 30 min | Low |
| 🟡 P3 | 1.4 — Melt Value auto-calculation | 1 hr | Medium |
| 🟡 P3 | 3.1–3.4 — Homepage reorder + last 5 + timestamp | 45 min | Low |
| 🟡 P3 | 3.5 — Profit box + card typography | 45 min | Low |
| 🔵 P4 | 2.4 — Double refresh fix | 30 min | Low |
| 🔵 P4 | 2.5 — Silver → Precious Metal (needs migration) | 1 hr | Medium |
| 🔵 P4 | 1.3 — Theme/Subject auto-parse | 45 min | Low |
| 🔵 P4 | 3.1b — Fix news feed (pending source approval) | 1–2 hr | Medium |
| ⚪ P5 | 1.5 — Stock images (CDN investigation first) | 1–2 hr | Medium |

**Estimated total:** ~10–12 hours across all priorities

---

*Generated: April 29, 2026 · Pending COA direction discussion*
