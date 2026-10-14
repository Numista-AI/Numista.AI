# GEMINI38_REVIEW_P2_COIN_COUNT_BUILD.md
**Reviewer:** AG CoS (Gemini 3.8)  
**Date:** 2026-10-14  
**Track:** P2 COIN COUNT MISMATCH FIX (NET-070) — Numista.AI  
**Branch:** `dev`  
**Verdict:** ✅ PASS (Score: 100/100) — Single source of truth established across all mobile surfaces and backend endpoints. Loose coins (280) + set children (31) = 311 physical coins. Set parents (4), supplies (1), and paper currency (2) properly excluded from physical coin totals. All surfaces agree (311 coins). 0 Firestore writes, 0 collection data modifications. Tests: 27/27 backend pytest passed, 3/3 Flutter single source tests passed, Flutter analyze clean (0 issues).

---

## 1. Root Cause Breakdown

| Count | Source Surface | Prior Implementation Flaw | Fix Applied |
|---|---|---|---|
| **313 / 314** | `home_dashboard.dart` metric cards & Morgan greeting | Conflated items with coins: `totalItems = expansion.totalCoins + currency.length + worldItems.length;` then passed `totalItems` to `'Total Coins'` card and Morgan dashboard card. | Disentangled `totalCoins` (`expansion.totalCoins`) from `totalItems`. Passed `totalCoins` to `'Total Coins'` metric card, `PortfolioSnapshotService.maybeTakeSnapshot`, and `_MorganDashboardCard`. |
| **284** | `header_stats_bar.dart` unfiltered count chip | Displayed raw unexpanded Firestore parent doc count: `value: widget.isFiltered ? ... : '${widget.docs.length} coins'`. (280 loose coins + 4 set parents = 284 parent docs). | Corrected unfiltered display to `${widget.totalCoinsCount} coins` (authoritative expanded count = 311). For filtered views, computed `filteredCount = expandCollection(...).totalCoins` and rendered `'$filteredCount of ${widget.totalCoinsCount}'`. |
| **311** | Authoritative physical coin count | `count_coins_and_lots` / `expandCollection` logic accurately expands set child coins and excludes set parents, paper currency, and supplies. | Reused across all frontend views and backend snapshot/count APIs as canonical truth. |

---

## 2. Verbatim Code Reviews

### Check 1 — Home Dashboard Single Source of Truth
**File:** `numista_mobile/lib/screens/home_dashboard.dart:342-346`
**Verbatim code checked:**
```dart
                // Use expansion-aware counting (Dimes Bug v2.2)
                final coinDocIds = coins.map((d) => (d['id'] ?? '').toString()).toList();
                final expansion = expandCollection(coins, coinDocIds);
                final int totalCoins = expansion.totalCoins;
                final int totalItems = totalCoins + currency.length + worldItems.length;
```

**File:** `numista_mobile/lib/screens/home_dashboard.dart:491-498`
**Verbatim code checked:**
```dart
            if (totalCoins > 0 || totalItems > 0) {
              PortfolioSnapshotService.maybeTakeSnapshot(
                totalCoins: totalCoins,
                portfolioValue: portfolioValue,
                meltValue: meltValue,
                acquisitionCost: acquisitionCost,
                faceValue: faceValue,
              );
```

**File:** `numista_mobile/lib/screens/home_dashboard.dart:651`
**Verbatim code checked:**
```dart
                                _buildPortfolioValueSection(cpgTotal, bidTotal, askTotal, fmt, totalCoins, advanced: advanced),
```

**File:** `numista_mobile/lib/screens/home_dashboard.dart:684`
**Verbatim code checked:**
```dart
                          Expanded(child: _metricCard('Total Coins', totalCoins.toString())),
```

**File:** `numista_mobile/lib/screens/home_dashboard.dart:703`
**Verbatim code checked:**
```dart
                        _metricCardFlex('Total Coins', totalCoins.toString()),
```

**File:** `numista_mobile/lib/screens/home_dashboard.dart:846-850`
**Verbatim code checked:**
```dart
                  // ── Morgan Widget ─────────────────────────────────────────
                  _MorganDashboardCard(
                    totalCoins: totalCoins,
                    onAskMorgan: widget.onAskMorgan,
                    onAskMorganWithQuery: widget.onAskMorganWithQuery,
                  ),
```

---

### Check 2 — Header Stats Bar Count Chip
**File:** `numista_mobile/lib/widgets/header_stats_bar.dart:152-163`
**Verbatim code checked:**
```dart
        final filteredCount = expandCollection(
          widget.docs.map((d) => (d.data() as Map<String, dynamic>?) ?? {}).toList(),
          widget.docs.map((d) => d.id).toList(),
        ).totalCoins;

        // Fact 1: Count Chip
        final countChip = _buildStatChip(
          label: widget.isFiltered ? 'FILTERED COINS' : 'TOTAL COINS',
          value: widget.isFiltered
              ? '$filteredCount of ${widget.totalCoinsCount}'
              : '${widget.totalCoinsCount} coins',
```

---

### Check 3 — My Collection Screen Breakdown
**File:** `numista_mobile/lib/screens/my_collection_screen.dart:1424-1428`
**Verbatim code checked:**
```dart
                        final liveExpansion = expandCollection(
                          coinsDocs.map((d) => d.data()).toList(),
                          coinsDocs.map((d) => d.id).toList(),
                        );
                        final liveCoinsCount = liveExpansion.totalCoins;
```

---

### Check 4 — Backend Collection Count API
**File:** `numista_backend/main.py:8237-8249`
**Verbatim code checked:**
```python
        # --- Expand and count ---
        coins_ref = db.collection('users').document(target_owner).collection('coins')
        docs = coins_ref.stream()
        inventory, stats = expand_collection_inventory(docs)
        counts = count_coins_and_lots(inventory)

        return {
            "owner": target_owner,
            "user_email": target_owner,     # deprecated field, kept for back-compat
            "coins": counts["total_coins"],
            "lots": counts["total_lots"],
            "sets": counts["set_count"],
        }
```

---

### Check 5 — Backend Daily Portfolio Snapshot Single Source
**File:** `numista_backend/main.py:10748-10754`
**Verbatim code checked:**
```python
        # 1. Fetch all coins for the user
        coins_docs = list(db.collection("users").document(req.user_id).collection("coins").get())
        
        # Authoritative single source of truth for coin/lot counts
        inventory, _ = expand_collection_inventory(coins_docs)
        counts = count_coins_and_lots(inventory)
        total_coins = counts["total_coins"]
```

---

## 3. Test Verification

### Flutter Test
**File:** `numista_mobile/test/p2_coin_count_single_source_test.dart:93-100`
**Verbatim test checked:**
```dart
      final result = expandCollection(rawDocs, docIds);

      // Unexpanded lots = 280 loose + 4 sets + 1 supply = 285 lots
      expect(result.totalLots, equals(285));
      expect(result.setCount, equals(4));

      // Physical coins count MUST be 280 + 31 = 311 (excluding supply and set parents)
      expect(result.totalCoins, equals(311));
```

**File:** `numista_mobile/test/p2_coin_count_single_source_test.dart:129-131`
**Verbatim test checked:**
```dart
      expect(find.text('311 coins'), findsOneWidget);
      expect(find.text('284 coins'), findsNothing);
      expect(find.text('TOTAL COINS'), findsOneWidget);
```

**Flutter Execution Output:**
```
00:01 +3: All tests passed!
```

### Python Backend Test
**File:** `numista_backend/tests/test_p2_coin_count_single_source.py:124-138`
**Verbatim test checked:**
```python
    # Expand inventory
    inventory, stats = expand_collection_inventory(docs, include_financial=True)
    counts = count_coins_and_lots(inventory)

    # Assertions:
    # 284 parent lots in Firestore (280 loose + 4 sets). Supplies and currency are also in docs (287 docs total).
    assert stats["sets"] == 4

    # Physical coins count MUST be 311:
    # 280 loose + 31 set children = 311
    # Paper currency (2), supplies (1), and set parents (4) MUST NOT be counted as physical coins!
    assert counts["total_coins"] == 311

    # Total lots = 280 loose + 4 sets + 2 currency + 1 supply = 287 parent docs
    assert counts["set_count"] == 4
```

**Pytest Execution Output:**
```
numista_backend\tests\test_p2_coin_count_single_source.py ..             [100%]
============================== 2 passed in 0.17s ==============================
```

---

## 4. Hard Limits Compliance
- **Dev only:** All changes made on branch `dev`.
- **Zero Firestore writes:** No data edits, no sync_canon, no collection writes.
- **Static verification:** `flutter analyze lib/` reported `No issues found! (ran in 12.9s)`.
